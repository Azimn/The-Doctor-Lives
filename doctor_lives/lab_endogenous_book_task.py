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
BOOK_HISTORY = "six_organ_endogenous_book_history_v1:"
_GOAL = "I want to discover a book here and read what it actually says."
_SCHEMA = "pretorius.endogenous-book-pursuit.v1"
_PHASES = {"search", "open", "turn", "read", "complete", "exhausted"}
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

    def __init__(self, session, *, authorized: bool = False,
                 recurring: bool = False):
        from .lab_six_organ_session import SixOrganLaboratoryCycle
        if type(session) is not SixOrganLaboratoryCycle or authorized is not True:
            raise PermissionError("Explicit opt-in canonical Laboratory session required")
        if type(recurring) is not bool:
            raise TypeError("Recurring reading requires an explicit mode")
        self.recurring = recurring
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
            if (type(state) is not dict
                    or set(state) not in (expected, expected | {"target_page"})
                    or ("target_page" in state and (
                        state["target_page"] is not None and
                        (type(state["target_page"]) is not int or state["target_page"] < 1)
                        or (state["phase"] in ("open", "turn", "read", "complete")
                            and state["target_page"] is None)))
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
                    "SELECT selected_action,trigger FROM policy_decisions WHERE id=?",
                    (state["origin_policy_id"],)
                ).fetchone()
                thought = db.execute(
                    "SELECT generated_by FROM thoughts WHERE id=?",
                    (state["origin_thought_id"],)
                ).fetchone()
            if (row is None or row["trigger"] != "six_organ_lab_cycle"
                    or row["selected_action"] != "explore"
                    or thought is None or thought["generated_by"] !=
                    "neural_policy:" + state["origin_policy_id"]):
                raise ValueError("Goal origin no longer matches canonical neural evidence")
            return state
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise RuntimeError("Corrupt or unauthorized endogenous goal state") from exc

    def _save(self, state, *, archive_completed=None):
        if state["steps"] > 40:
            raise RuntimeError("Endogenous task action budget exhausted")
        envelope = {"payload": state, "sha256": _digest(state)}
        with self.store.transaction() as db:
            if archive_completed is not None:
                current = db.execute("SELECT value FROM meta WHERE key=?", (_KEY,)).fetchone()
                if (current is None or archive_completed["phase"] != "complete"
                        or json.loads(current["value"])["payload"] != archive_completed
                        or state["id"] == archive_completed["id"]):
                    raise RuntimeError("Book goal changed before historical archival")
                key = BOOK_HISTORY + archive_completed["id"]
                if db.execute("SELECT 1 FROM meta WHERE key=?", (key,)).fetchone():
                    raise RuntimeError("Duplicate historical reading archival")
                self.store.set_meta(key, current["value"], db)
            self.store.set_meta(_KEY, _stable(envelope), db)
            self.store.bump_state_version(db)

    def _verified_read_pages(self):
        """Only admitted, original source reads count as lived reading history."""
        from .lab_home_bridge import _row
        pages = {}
        with self.host.bridge.world._open() as db:
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='books_events'").fetchone() is None:
                return pages
            for memory in self.store.memories():
                if (not memory["active"] or memory["external"]
                        or memory["evidence_class"] != "lived_runtime_memory"
                        or not memory["source"].startswith("laboratory-home:action:")
                        or not memory["text"].startswith("I read a page of ")):
                    continue
                digest = memory["source"].removeprefix("laboratory-home:action:")
                hits = db.execute(
                    "SELECT event_id FROM books_events WHERE event_hash=?", (digest,)
                ).fetchall()
                if len(hits) != 1:
                    continue
                event, checked = _row(db, "books_events", hits[0][0])
                page = event.get("page_receipt")
                action = event.get("action", {})
                if (checked == digest and action.get("op") == "read"
                        and event.get("world_epoch") == self._epoch()
                        and event.get("access_proof") and type(page) is dict
                        and type(page.get("page_number")) is int):
                    pages.setdefault(action["book_id"], set()).add(page["page_number"])
        return pages

    def _reading_plans(self, candidates=None):
        """Host-only physical feasibility; never reveal unread text or catalog.

        A closed, not-yet-read volume may open at page one. A physically
        open volume may be read at its current unread page or turned one
        leaf forward from a previously lived page. A closed partially
        read volume requires a future bookmark/return mechanism.
        """
        from pretorius_lab.book_library import BookLibrary
        from pretorius_lab.physics import LabError
        try:
            catalog = BookLibrary(self.subject.habitat).catalog()
        except LabError:
            return {}
        seen = self._verified_read_pages()
        plans = {}
        for book_id, info in catalog.items():
            if candidates is not None and book_id not in candidates:
                continue
            pages = seen.get(book_id, set())
            if not info["opened"]:
                if 1 not in pages:
                    plans[book_id] = ("open", 1)
            else:
                page = info["page_if_open"]
                if page not in pages:
                    plans[book_id] = ("read", page)
                elif page < info["page_count"] and page + 1 not in pages:
                    plans[book_id] = ("turn", page + 1)
        return plans

    def has_reading_opportunity(self):
        return bool(self._reading_plans())

    def _completed_source(self, state):
        from .lab_home_bridge import _row
        memory = self.store.get_memory(state["read_memory_id"])
        if (memory is None or not memory["active"] or memory["external"]
                or memory["evidence_class"] != "lived_runtime_memory"
                or not memory["source"].startswith("laboratory-home:action:")
                or not memory["text"].startswith("I read a page of ")):
            raise RuntimeError("Prior book goal lacks a verified lived read")
        with self.host.bridge.world._open() as db:
            event, digest = _row(db, "books_events", "eb_" + state["id"] + "_read")
        page = event.get("page_receipt")
        if (memory["source"] != "laboratory-home:action:" + digest
                or event.get("action") != {"op": "read", "book_id": state["target"]}
                or event.get("world_epoch") != self._epoch()
                or not event.get("access_proof") or not page
                or ("target_page" in state and page.get("page_number") != state["target_page"])):
            raise RuntimeError("Prior book completion lacks exact original page receipt")
        return event

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

    def step(self, *, authorized_world_action: bool = False,
             native_proposal=None):
        """One bounded cognitive opportunity and at most ONE physical act.

        A host schedules an opportunity, not a goal, destination, title or
        book text. Repeated calls can continue an earlier internally originated
        commitment across process/brain restart.
        """
        if type(authorized_world_action) is not bool:
            raise TypeError("World authorization must be an explicit boolean")
        state = self._load()
        prior = None
        if state and state["phase"] in ("complete", "exhausted"):
            if (self.recurring and state["phase"] == "complete"
                    and native_proposal is not None and self.has_reading_opportunity()):
                self._completed_source(state)
                prior, state = state, None
            else:
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
        # An authenticated caller may forward the JUST-ISSUED native policy
        # event from a common multi-goal deliberation. This cannot be a
        # host-authored action label or stale policy receipt.
        from .organs import CognitiveProposal
        if native_proposal is not None:
            if type(native_proposal) is not CognitiveProposal:
                raise PermissionError("Expected an original typed neural decision")
            proposal = native_proposal
        else:
            # A direct opportunity must run the SAME canonical six-organ
            # decision as the native multi-goal chooser. A standalone Noesis
            # call with a different trigger cannot originate a replayable goal.
            cycle = self.host.cycle(authorized_world_action=False)
            with self.store.connect() as db:
                row = db.execute(
                    "SELECT id,selected_action FROM policy_decisions "
                    "WHERE trigger='six_organ_lab_cycle' "
                    "ORDER BY rowid DESC LIMIT 1"
                ).fetchone()
                thought = (db.execute(
                    "SELECT id FROM thoughts WHERE generated_by=? "
                    "ORDER BY rowid DESC LIMIT 1",
                    ("neural_policy:" + row["id"],),
                ).fetchone() if row is not None else None)
            if (row is None or thought is None
                    or row["selected_action"] != cycle.selected_tendency):
                raise RuntimeError("Direct book opportunity lacks a six-organ neural decision")
            proposal = CognitiveProposal(
                policy_decision_id=row["id"], thought_id=thought["id"],
                selected_tendency=row["selected_action"],
            )
        # Both entrypoints must bind the same original policy and thought.
        with self.store.connect() as db:
            origin = db.execute(
                "SELECT trigger,selected_action FROM policy_decisions WHERE id=?",
                (proposal.policy_decision_id,),
            ).fetchone()
            thought_origin = db.execute(
                "SELECT generated_by FROM thoughts WHERE id=?",
                (proposal.thought_id,),
            ).fetchone()
        if (origin is None or origin["trigger"] != "six_organ_lab_cycle"
                or origin["selected_action"] != proposal.selected_tendency
                or thought_origin is None or thought_origin["generated_by"] !=
                "neural_policy:" + proposal.policy_decision_id):
            raise PermissionError("Book origin requires original six-organ policy and thought")
        _, newest_id = self.host.corpus._verified_policy(proposal)
        if newest_id != proposal.policy_decision_id:
            raise PermissionError("Stale policy cannot originate a new book goal")
        if state is None:
            # An internal exploratory choice alone does not create a book fact.
            # A bookshelves cue must have been physically SEEN by this
            # original individual. A remembered source LOOK may be remote:
            # an EXPLORE commitment can survive the journey back to it.
            # The original world graph must still admit a physical route.
            looks = _verified_looks(self.subject.embodied)
            station = self._at()
            cue = next((
                e for e, _ in looks
                if "bookshelves" in e["offered_payload"]["perceived_features"]
                and (e["after_station"] == station or
                     self._route(station, e["after_station"]) is not None)
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
            if self.recurring:
                state["target_page"] = None
            if prior is not None and prior["origin_policy_id"] == proposal.policy_decision_id:
                raise PermissionError("Historical reading cannot reuse its neural origin")
            self._save(state, archive_completed=prior)
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
                plans = self._reading_plans(candidates) if "target_page" in state else None
                if plans is not None:
                    candidates = [book_id for book_id in candidates if book_id in plans]
                if candidates:
                    # Preference comes from the original Doctor's verified
                    # autobiographical reading history, not the host's book
                    # ID order. A lesion uses the ID baseline for comparison.
                    from .autobiographical_book_preference import choose_visible_book
                    chosen = choose_visible_book(
                        candidates, store=self.store,
                        world=self.host.bridge.world,
                    )
                    proof = self.books.memory_hint(chosen)
                    if proof is None:
                        raise RuntimeError("Visible book lacks canonical sight memory")
                    state["target"] = chosen
                    state["target_sighting"] = proof["memory_id"]
                    if plans is not None:
                        state["phase"], state["target_page"] = plans[chosen]
                    else:
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
        if proof is None or proof["memory_id"] != state["target_sighting"]:
            raise RuntimeError("Selected book no longer has original source evidence")
        if proof["station"] != station:
            # A previously selected volume may be left behind while a
            # different need wins. Preserve its exact intent and sighting,
            # then physically return before opening/reading it.
            hop = self._route(station, proof["station"])
            if hop is None:
                raise RuntimeError("No source-defined return route to selected book")
            consequence = self.host._execute_movement(proposal, hop)
            if consequence.status not in ("admitted", "already_admitted"):
                raise RuntimeError("Book resumption travel lacks lived consequence")
            state["steps"] += 1
            self._save(state)
            return EndogenousTaskReceipt(
                "moved", state["id"], state["phase"], hop,
                consequence.memory_id, "original-neural-explore-with-situated-evidence",
            )
        op = state["phase"]
        event_id = "eb_" + state["id"] + "_" + op
        if "target_page" in state:
            from pretorius_lab.book_library import BookLibrary
            with self.host.bridge.world._open() as db:
                previous = db.execute(
                    "SELECT 1 FROM books_events WHERE event_id=?", (event_id,)
                ).fetchone()
            if previous is None:
                info = BookLibrary(self.subject.habitat).catalog(state["target"])[state["target"]]
                page = state["target_page"]
                valid = ((op == "open" and not info["opened"] and page == 1)
                         or (op == "turn" and info["opened"]
                             and info["page_if_open"] == page - 1
                             and page <= info["page_count"])
                         or (op == "read" and info["opened"] and info["page_if_open"] == page))
                if not valid:
                    raise PermissionError("Physical book changed before selected page operation")
        receipt = self.host.book_action(
            state["target"], op, event_id=event_id,
            authorized=True, direction=1 if op == "turn" else None,
        )
        if receipt["status"] not in ("admitted", "already_admitted"):
            raise RuntimeError("Book action lacks original Doctor lived memory")
        state["steps"] += 1
        if op in ("open", "turn"):
            state["phase"] = "read"
        elif op == "read":
            if "I read a page of " not in receipt["subject"]["inner"]:
                raise RuntimeError("No source-backed book content was experienced")
            state["phase"] = "complete"
            state["read_memory_id"] = receipt["memory_id"]
            if "target_page" in state:
                self._completed_source(state)
        self._save(state)
        return EndogenousTaskReceipt(
            "completed" if op == "read" else "turned" if op == "turn" else "opened",
            state["id"], state["phase"], state["target"], receipt["memory_id"],
            "original-neural-explore-with-situated-evidence",
        )
