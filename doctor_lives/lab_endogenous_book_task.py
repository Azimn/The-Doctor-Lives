"""Opt-in endogenous book pursuit in the one canonical six-organ Doctor.

A native exploratory policy event may originate the bounded intention to find
and read a book after a source-verified situated Laboratory observation.
Only the Laboratory decides what exists and whether actions are physically legal.
The host supplies a fixed, inspectable navigation algorithm and permission, NOT
a book identifier, destination, goal prompt or source text. This is a candidate
endogenous *goal initiation*, not a claim of fully independent planning or D11.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from hashlib import sha256
import json
import re

from .six_organ_book_task import SHELVES, _verified_looks


_KEY = "six_organ_endogenous_book_goal_v1"
_GOAL = "I want to discover a book here and read what it actually says."
_SCHEMA = "pretorius.endogenous-book-pursuit.v1"
_PHASES = {"search", "open", "read", "complete", "exhausted"}
_BOOK_ID = re.compile(r"book:[0-9]{3}\Z")


def _stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value):
    return sha256(_stable(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EndogenousTaskReceipt:
    status: str
    goal_id: str | None
    phase: str | None
    world_action: str | None = None
    memory_id: str | None = None
    goal_origin: str = "not-established"
    host_selected_route: bool = True


class EndogenousBookPursuit:
    """One opt-in, bounded goal stored in the ORIGINAL BrainStore meta.

    The host owns execution, source checking and fixed routing. Only an
    original neural 'explore' result can start a new task. Resume uses a
    preserved intention rather than a host resending a goal or a prompt.
    """

    def __init__(self, session, *, authorized: bool = False):
        from .lab_six_organ_session import SixOrganLaboratoryCycle
        if type(session) is not SixOrganLaboratoryCycle or authorized is not True:
            raise PermissionError("Explicit opt-in canonical Laboratory session required")
        self.host = session
        self.runtime = session.runtime
        self.subject = session.subject
        self.store = session.runtime._port.brain.store
        self.books = self.runtime.bind_source_verified_book_search(
            self.subject.embodied, authorized=True
        )
        self._load()

    def _epoch(self):
        return self.subject.verify()["world_epoch"]

    def _load(self):
        raw = self.store.meta(_KEY)
        if raw is None:
            return None
        try:
            envelope = json.loads(raw)
            if set(envelope) != {"payload", "sha256"}:
                raise ValueError("Bad goal envelope")
            state = envelope["payload"]
            if _digest(state) != envelope["sha256"]:
                raise ValueError("Goal envelope checksum mismatch")
            expected = {
                "schema", "id", "world_epoch", "goal", "phase",
                "origin_policy_id", "origin_thought_id", "searched",
                "target", "target_sighting", "steps", "read_memory_id",
            }
            if (type(state) is not dict or set(state) != expected
                    or state["schema"] != _SCHEMA
                    or state["world_epoch"] != self._epoch()
                    or state["goal"] != _GOAL or state["phase"] not in _PHASES
                    or not re.fullmatch(r"[0-9a-f]{24}", state["id"])
                    or type(state["steps"]) is not int or not 0 <= state["steps"] <= 40
                    or type(state["searched"]) is not list
                    or len(set(state["searched"])) != len(state["searched"])
                    or not set(state["searched"]) <= set(SHELVES)
                    or (state["target"] is not None and
                        (type(state["target"]) is not str or
                         not _BOOK_ID.fullmatch(state["target"])))):
                raise ValueError("Invalid bounded goal state")
            with self.store.connect() as db:
                row = db.execute(
                    "SELECT selected_action FROM policy_decisions WHERE id=?",
                    (state["origin_policy_id"],)
                ).fetchone()
                thought = db.execute(
                    "SELECT generated_by FROM thoughts WHERE id=?",
                    (state["origin_thought_id"],)
                ).fetchone()
            if (row is None or row["selected_action"] != "explore"
                    or thought is None or thought["generated_by"] !=
                    "neural_policy:" + state["origin_policy_id"]):
                raise ValueError("Goal origin no longer matches canonical neural evidence")
            return state
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise RuntimeError("Corrupt or unauthorized endogenous goal state") from exc

    def _save(self, state):
        if state["steps"] > 40:
            raise RuntimeError("Endogenous task action budget exhausted")
        envelope = {"payload": state, "sha256": _digest(state)}
        with self.store.transaction() as db:
            self.store.set_meta(_KEY, _stable(envelope), db)
            self.store.bump_state_version(db)

    def _at(self):
        return self.subject.embodied.verify()["station"]

    @staticmethod
    def _route(start, destination):
        # Navigation is an explicit, NON-COGNITIVE host feasibility adapter.
        from pretorius_lab.embodied_access import STATIONS
        if start not in STATIONS or destination not in STATIONS:
            raise PermissionError("Unknown source-reviewed physical station")
        if start == destination:
            return None
        queue = deque([(start, ())])
        visited = {start}
        while queue:
            at, path = queue.popleft()
            for neighbor in STATIONS[at][1]:
                if neighbor in visited:
                    continue
                new_path = path + (neighbor,)
                if neighbor == destination:
                    return new_path[0]
                visited.add(neighbor)
                queue.append((neighbor, new_path))
        return None

    def status(self):
        """Engineer-only, does not supply raw state to the Ipseity renderer."""
        state = self._load()
        if state is None:
            return EndogenousTaskReceipt("dormant", None, None)
        return EndogenousTaskReceipt(
            "already_complete" if state["phase"] == "complete" else "active",
            state["id"], state["phase"],
            memory_id=state["read_memory_id"],
            goal_origin="original-neural-explore-with-situated-evidence",
        )

    def step(self, *, authorized_world_action: bool = False):
        """One bounded cognitive opportunity and at most ONE physical act.

        A host schedules an opportunity, not a goal, destination, title or
        book text. Repeated calls can continue an earlier internally originated
        commitment across process/brain restart.
        """
        if type(authorized_world_action) is not bool:
            raise TypeError("World authorization must be an explicit boolean")
        state = self._load()
        if state and state["phase"] in ("complete", "exhausted"):
            return EndogenousTaskReceipt(
                "already_complete" if state["phase"] == "complete" else "exhausted",
                state["id"], state["phase"], memory_id=state["read_memory_id"],
                goal_origin="original-neural-explore-with-situated-evidence",
            )
        observed = self.host.bridge.observe()
        lived = self.store.get_memory(observed["memory_id"])
        if (lived is None or lived["evidence_class"] != "lived_runtime_memory"
                or not lived["source"].startswith("laboratory-home:observe:")):
            raise RuntimeError("Endogenous opportunity lacks situated lived observation")
        proposal = self.runtime.noesis.deliberate(
            host_trigger="endogenous_book_opportunity"
        )
        # Checks the actual neural decision and thought relationship, rather
        # than trusting the selected_action copied into a Python dataclass.
        self.host.corpus._verified_policy(proposal)
        if state is None:
            # An internal exploratory choice alone does not create a book fact.
            # The co-present bookshelves cue must come from a verified local
            # look that entered the Doctor's first-person observation.
            looks = _verified_looks(self.subject.embodied)
            cue = next((
                e for e, _ in looks
                if e["after_station"] == self._at()
                and "bookshelves" in e["offered_payload"]["perceived_features"]
            ), None)
            if proposal.selected_tendency != "explore" or cue is None:
                return EndogenousTaskReceipt("dormant", None, None)
            ident = sha256((self._epoch() + "|" +
                            proposal.policy_decision_id).encode()).hexdigest()[:24]
            state = {
                "schema": _SCHEMA, "id": ident,
                "world_epoch": self._epoch(), "goal": _GOAL,
                "phase": "search", "origin_policy_id": proposal.policy_decision_id,
                "origin_thought_id": proposal.thought_id,
                "searched": [], "target": None, "target_sighting": None,
                "steps": 0, "read_memory_id": None,
            }
            self._save(state)
            return EndogenousTaskReceipt(
                "goal_created", ident, "search",
                goal_origin="original-neural-explore-with-situated-evidence",
            )
        if not authorized_world_action:
            return EndogenousTaskReceipt(
                "authorization_required", state["id"], state["phase"],
                goal_origin="original-neural-explore-with-situated-evidence",
            )
        if state["steps"] >= 40:
            raise RuntimeError("Bounded goal requires independent reevaluation")

        station = self._at()
        if state["phase"] == "search":
            if station in SHELVES and station not in state["searched"]:
                scan = self.subject.embodied.look(
                    event_id="eb_" + state["id"] + "_look_" + station[-1]
                )
                self.books.admit_sighting(scan)
                # The host may reject objects lacking a real installed text
                # edition. This is physical feasibility, NEVER advance
                # knowledge of an unseen book or a subject-facing catalog.
                from pretorius_lab.book_library import BookLibrary
                from pretorius_lab.physics import LabError
                try:
                    installed = set(BookLibrary(self.subject.habitat).catalog())
                except LabError:
                    installed = set()
                candidates = sorted(
                    x["object_id"]
                    for x in scan["offered_payload"]["nearby_objects"]
                    if type(x.get("object_id")) is str and
                    _BOOK_ID.fullmatch(x["object_id"])
                    and x["object_id"] in installed
                    and self.books.memory_hint(x["object_id"]) is not None
                    and self.books.memory_hint(x["object_id"])["station"] == station
                )
                if candidates:
                    chosen = candidates[0]
                    proof = self.books.memory_hint(chosen)
                    if proof is None:
                        raise RuntimeError("Visible book lacks canonical sight memory")
                    state["target"] = chosen
                    state["target_sighting"] = proof["memory_id"]
                    state["phase"] = "open"
                else:
                    state["searched"].append(station)
                state["steps"] += 1
                self._save(state)
                return EndogenousTaskReceipt(
                    "source_verified_shelf_scan", state["id"], state["phase"],
                    goal_origin="original-neural-explore-with-situated-evidence",
                )
            targets = [s for s in SHELVES if s not in state["searched"]]
            if not targets:
                state["phase"] = "exhausted"
                self._save(state)
                return EndogenousTaskReceipt("exhausted", state["id"], "exhausted")
            next_station = self._route(station, targets[0])
            if next_station is None:
                raise RuntimeError("No verified route to an unexplored shelf")
            consequence = self.host._execute_movement(proposal, next_station)
            if consequence.status not in ("admitted", "already_admitted"):
                raise RuntimeError("Movement lacked canonical lived consequence")
            state["steps"] += 1
            self._save(state)
            return EndogenousTaskReceipt(
                "moved", state["id"], "search", next_station,
                consequence.memory_id,
                "original-neural-explore-with-situated-evidence",
            )
        # A book choice can only follow a source-backed LOOK, and a later
        # relocation cannot silently turn a stale sighting into world truth.
        proof = self.books.memory_hint(state["target"])
        if (proof is None or proof["station"] != station
                or proof["memory_id"] != state["target_sighting"]):
            raise RuntimeError("Selected book no longer has current source evidence")
        op = state["phase"]
        receipt = self.host.book_action(
            state["target"], op, event_id="eb_" + state["id"] + "_" + op,
            authorized=True,
        )
        if receipt["status"] not in ("admitted", "already_admitted"):
            raise RuntimeError("Book action lacks original Doctor lived memory")
        state["steps"] += 1
        if op == "open":
            state["phase"] = "read"
        elif op == "read":
            if "I read a page of " not in receipt["subject"]["inner"]:
                raise RuntimeError("No source-backed book content was experienced")
            state["phase"] = "complete"
            state["read_memory_id"] = receipt["memory_id"]
        self._save(state)
        return EndogenousTaskReceipt(
            "completed" if op == "read" else "opened",
            state["id"], state["phase"], state["target"], receipt["memory_id"],
            "original-neural-explore-with-situated-evidence",
        )
