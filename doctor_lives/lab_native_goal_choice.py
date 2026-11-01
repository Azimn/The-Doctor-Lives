"""Native Noesis two-goal routing through one authenticated Laboratory.

EXPERIMENTAL. The native neural action chooses EXPLORE versus AVOID; this
reviewed host maps those abstract tendencies to bounded goal classes, and
handles routing and safety. It does not claim that Pretorius composed a
natural-language goal or independently authored a specific destination.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from .lab_endogenous_book_task import EndogenousBookPursuit, _verified_looks

_REST_KEY = "six_organ_native_rest_intention_v1"
_REST_SCHEMA = "pretorius.native-rest-intention.v1"
_REST_GOAL = "I want to rest somewhere safe."
_PHASES = {"travel", "rest", "complete"}


def _stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(value):
    return sha256(_stable(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class NativeGoalChoiceReceipt:
    status: str
    kind: str | None
    goal_id: str | None
    memory_id: str | None = None
    selected_tendency: str | None = None
    host_selected_goal_mapping: bool = True
    host_selected_route: bool = True


class NativeLaboratoryGoalChooser:
    """Bounded native-policy arbitration, one original BrainStore, one world."""

    def __init__(self, session, *, authorized: bool = False,
                 enable_sustained_work: bool = False):
        from .lab_six_organ_session import SixOrganLaboratoryCycle
        if type(session) is not SixOrganLaboratoryCycle or authorized is not True:
            raise PermissionError("Trusted opt-in six-organ Laboratory host needed")
        self.host = session
        self.runtime = session.runtime
        self.store = session.runtime._port.brain.store
        self.book = EndogenousBookPursuit(session, authorized=True)
        self._load_rest()
        if type(enable_sustained_work) is not bool:
            raise TypeError("Native work capability requires a typed opt-in")
        self.work = None
        if enable_sustained_work:
            from .lab_native_work_goal import NativeWorkPursuit
            self.work = NativeWorkPursuit(session)

    def _epoch(self):
        return self.host.subject.verify()["world_epoch"]

    def _load_rest(self):
        raw = self.store.meta(_REST_KEY)
        if raw is None:
            return None
        try:
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"payload", "sha256"}:
                raise ValueError("Rest-intention envelope")
            state = envelope["payload"]
            if _digest(state) != envelope["sha256"]:
                raise ValueError("Rest-intention checksum")
            if (type(state) is not dict or set(state) != {
                "schema", "id", "world_epoch", "goal", "phase", "steps",
                "origin_policy_id", "origin_thought_id", "memory_id"
            } or state["schema"] != _REST_SCHEMA
                    or state["world_epoch"] != self._epoch()
                    or state["goal"] != _REST_GOAL
                    or state["phase"] not in _PHASES
                    or type(state["steps"]) is not int or not 0 <= state["steps"] <= 12
                    or not re.fullmatch(r"[0-9a-f]{24}", state["id"])
                    or state["memory_id"] is not None and
                    (type(state["memory_id"]) is not str or not state["memory_id"])):
                raise ValueError("Invalid canonical rest goal")
            with self.store.connect() as db:
                choice = db.execute(
                    "SELECT selected_action,trigger FROM policy_decisions WHERE id=?",
                    (state["origin_policy_id"],)
                ).fetchone()
                thought = db.execute(
                    "SELECT generated_by FROM thoughts WHERE id=?",
                    (state["origin_thought_id"],)
                ).fetchone()
            if (choice is None or choice["trigger"] != "six_organ_lab_cycle"
                    or choice["selected_action"] != "avoid"
                    or thought is None or thought["generated_by"] !=
                    "neural_policy:" + state["origin_policy_id"]):
                raise ValueError("Rest goal has no original avoid-policy provenance")
            if state["phase"] == "complete":
                memory = self.store.get_memory(state["memory_id"])
                if (memory is None
                        or memory["evidence_class"] != "lived_runtime_memory"
                        or not memory["source"].startswith("laboratory-home:action:")):
                    raise ValueError("Rest was marked complete without lived evidence")
            return state
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise RuntimeError("Corrupt or forged canonical rest intention") from exc

    def _save_rest(self, state, *, archive_completed=None):
        envelope = {"payload": state, "sha256": _digest(state)}
        with self.store.transaction() as db:
            if archive_completed is not None:
                # A second genuine rest never erases the sealed, source-
                # verified first goal. History remains in the same BrainStore
                # and does not participate in active opportunity selection.
                current = db.execute(
                    "SELECT value FROM meta WHERE key=?", (_REST_KEY,)
                ).fetchone()
                if (current is None or
                        json.loads(current["value"]).get("payload") != archive_completed
                        or archive_completed["phase"] != "complete"):
                    raise RuntimeError("Rest changed before historical archival")
                key = "six_organ_native_rest_history_v1:" + archive_completed["id"]
                if db.execute(
                    "SELECT 1 FROM meta WHERE key=?", (key,)
                ).fetchone() is not None:
                    raise RuntimeError("Duplicate historical rest archival")
                self.store.set_meta(key, current["value"], db)
            self.store.set_meta(_REST_KEY, _stable(envelope), db)
            self.store.bump_state_version(db)

    def _finish_source_verified_rest(self, state, memory, event_id):
        """One original physical rest restores original homeostasis exactly once.

        The original Laboratory's one-hour rest, not a host-authored goal,
        licenses six existing ten-minute homeostatic opportunities. The
        canonical brain's own relaxation rule runs in the SAME transaction
        as the completed goal, so a cold replay cannot apply it twice.
        No action score, tendency, world supply or physics is overridden.
        """
        from .lab_home_bridge import _row
        digest = memory["source"].removeprefix("laboratory-home:action:")
        with self.host.bridge.world._open() as db:
            original, checked = _row(db, "rhythm_events", event_id)
        if (checked != digest or original.get("op") != "rest"
                or original.get("station") != "station:bedroom"
                or original.get("subject", {}).get("inner") != memory["text"]):
            raise PermissionError("Native rest has no matching original physical receipt")
        completed = dict(state)
        completed["steps"] += 1
        completed["phase"] = "complete"
        completed["memory_id"] = memory["id"]
        brain = self.runtime._port.brain
        envelope = {"payload": completed, "sha256": _digest(completed)}
        # Exactly one atomic BrainStore change owns both goal completion
        # and the original need-relaxation dynamics. No second memory store.
        with self.store.transaction() as db:
            for _ in range(6):
                tick = self.store.advance_tick(db)
                brain._relax_needs(db, tick)
                brain._update_commitments_due(db, tick)
            self.store.set_meta(_REST_KEY, _stable(envelope), db)
            self.store.bump_state_version(db)

    def _new_physical_rest_need(self):
        """Check an authentic NEW bodily need, not a host rest quota.

        Original world state is authoritative about bodily fatigue. A fresh
        Noesis AVOID decision may support later rest only after the previously
        completed rest and renewed physical fatigue; canonical brain fatigue
        alone cannot replay an already completed world event.
        """
        from pretorius_lab.daily_rhythm import transition
        from pretorius_lab.physics import Conflict, LabError
        self.host.subject.rhythm.verify()
        physical = self.host.subject.rhythm.audit_state()
        fatigue = physical.get("fatigue")
        if type(fatigue) not in (int, float) or not 0 < fatigue <= 10:
            return False
        try:
            transition(physical, "rest", {}, "station:bedroom")
        except (Conflict, LabError):
            return False
        return True

    def _native_policy(self):
        """Read the native choice from an ACTUAL full six-organ cycle.

        Body/world sensing and source-verified Affectus weather must advance
        before claiming any native intent. No host-controlled tendency,
        rendered prose, or desired outcome is substituted for the policy.
        The cycle is explicitly NON-actuating; this layer separately
        authorizes later physical actions.
        """
        from .organs import CognitiveProposal
        cycle = self.host.cycle(authorized_world_action=False)
        with self.store.connect() as db:
            row = db.execute(
                "SELECT id,selected_action FROM policy_decisions "
                "WHERE trigger='six_organ_lab_cycle' ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            if row is None or row["selected_action"] != cycle.selected_tendency:
                raise RuntimeError("No canonical native six-organ choice receipt")
            thought = db.execute(
                "SELECT id FROM thoughts WHERE generated_by=? "
                "ORDER BY rowid DESC LIMIT 1",
                ("neural_policy:" + row["id"],),
            ).fetchone()
        if thought is None:
            raise RuntimeError("Native six-organ decision lacks neural thought")
        proposal = CognitiveProposal(
            policy_decision_id=row["id"], thought_id=thought["id"],
            selected_tendency=row["selected_action"],
        )
        _, latest = self.host.corpus._verified_policy(proposal)
        if latest != proposal.policy_decision_id:
            raise PermissionError("Goal origin is not the newest canonical policy")
        return proposal

    def step(self, *, authorized_world_action: bool = False):
        """A host provides an opportunity and permission, never goal/destination."""
        if type(authorized_world_action) is not bool:
            raise TypeError("Typed world authorization required")
        rest = self._load_rest()
        book = self.book.status()
        work = self.work._load() if self.work is not None else None
        if work is not None and work["phase"] != "complete":
            if book.goal_id is not None and book.phase not in ("complete", "exhausted"):
                raise RuntimeError("Unreviewed competing book and work commitments")
            # A physically blocked work goal may coexist only with a real
            # Noesis-origin rest intention. Complete that temporary recovery
            # before resuming the original work goal, across cold restarts.
            if rest is not None and rest["phase"] != "complete":
                if work["phase"] != "blocked":
                    raise RuntimeError("Unreviewed competing work and rest")
                return self._continue_rest(rest, authorized_world_action)
            result = self.work.step(
                authorized=authorized_world_action, new_policy=self._native_policy
            )
            if (result.status == "blocked" and authorized_world_action
                    and (rest is None or rest["phase"] == "complete")):
                proposal = self._native_policy()
                if (proposal.selected_tendency == "avoid"
                        and (rest is None or self._new_physical_rest_need())):
                    return self._originate_rest(proposal)
            return NativeGoalChoiceReceipt(
                result.status, "work", result.goal_id, result.memory_id,
                selected_tendency=result.selected_tendency
            )
        if (rest is not None and rest["phase"] != "complete"
                and book.goal_id is not None and book.phase not in (
                    "complete", "exhausted")):
            raise RuntimeError("Competing pending goals require explicit review")
        if book.goal_id is not None and book.phase not in ("complete", "exhausted"):
            result = self.book.step(
                authorized_world_action=authorized_world_action
            )
            return NativeGoalChoiceReceipt(
                result.status, "read_book", result.goal_id, result.memory_id
            )
        # Candidate B may pursue a distinct later work/book commitment after
        # authentically completing rest. The original two-goal preview keeps
        # its earlier return contract unless sustained work is enabled.
        if rest is not None and (rest["phase"] != "complete" or self.work is None):
            return self._continue_rest(rest, authorized_world_action)
        # A fulfilled intention is HISTORY, not a permanent prohibition on
        # having a different intention. Preserve the original book receipt;
        # permit ONLY a later native AVOID choice to originate a distinct rest
        # goal. Never restart the already-completed book or infer that an
        # engineer has provided a second goal.
        prior_book_complete = book.goal_id is not None and book.phase == "complete"
        if prior_book_complete:
            self._verify_completed_book(book)

        observed = self.host.bridge.observe()
        lived = self.store.get_memory(observed["memory_id"])
        if (lived is None or not lived["active"]
                or lived["evidence_class"] != "lived_runtime_memory"
                or not lived["source"].startswith("laboratory-home:observe:")):
            raise PermissionError("Missing real situated original-Doctor perception")
        state = self.host.subject.embodied.verify()
        station = state["station"]
        # Passive, local, source-ledger LOOK opportunity, not a neural goal or
        # operator-chosen destination. The original world must supply the cue.
        # Without an actual LOOK, existing book/work origin guards cannot
        # admit a situated goal on a pristine installed world.
        if authorized_world_action and not any(
            e["after_station"] == station
            for e, _ in _verified_looks(self.host.subject.embodied)
        ):
            cue_id = "ng_percept_" + sha256(
                (self._epoch() + "|" + station).encode("utf-8")
            ).hexdigest()[:24]
            scan = self.host.subject.embodied.look(event_id=cue_id)
            self.book.books.admit_sighting(scan)
        proposal = self._native_policy()
        if proposal.selected_tendency == "explore":
            # Bounded source-grounded alternative: when an actual book has
            # already been read or no installed physical edition exists,
            # exploratory Noesis may pursue the SEEN workbench instead.
            # The host checks catalogue feasibility, never sends unseen
            # titles or an operator-authored task to the Doctor.
            if self.work is not None:
                from pretorius_lab.book_library import BookLibrary
                from pretorius_lab.physics import LabError
                try:
                    available_books = bool(BookLibrary(
                        self.host.subject.habitat).catalog())
                except LabError:
                    available_books = False
                if prior_book_complete or not available_books:
                    if work is not None:
                        return NativeGoalChoiceReceipt(
                            "already_complete", "work", work["id"],
                            work["memory_id"], selected_tendency="explore"
                        )
                    alternative = self.work.originate(proposal)
                    if alternative.goal_id is not None:
                        return NativeGoalChoiceReceipt(
                            alternative.status, "work", alternative.goal_id,
                            alternative.memory_id,
                            selected_tendency=alternative.selected_tendency
                        )
            if book.goal_id is not None:
                # Exhausted or completed once: never accidentally reopen
                # the original volume or start an alias of the old goal.
                return NativeGoalChoiceReceipt(
                    "already_complete" if prior_book_complete else "exhausted",
                    "read_book", book.goal_id, book.memory_id,
                    selected_tendency="explore",
                )
            # A source-verified bookshelf LOOK, including one witnessed in
            # an earlier room, can anchor a durable EXPLORE book intention.
            # The route is host-provided, not a newly invented neural goal.
            # Without a witnessed, reachable cue EXPLORE only moves one hop.
            scene = next((
                event for event, proof in _verified_looks(self.host.subject.embodied)
                if "bookshelves" in event["offered_payload"]["perceived_features"]
                and (event["after_station"] == station or
                     EndogenousBookPursuit._route(
                         station, event["after_station"]) is not None)
            ), None)
            if scene is None:
                return self._move_to_remembered_cue(proposal, authorized_world_action)
            result = self.book.step(
                native_proposal=proposal, authorized_world_action=False
            )
            if result.status != "goal_created":
                raise RuntimeError("Verified explore did not originate book intention")
            return NativeGoalChoiceReceipt(
                "goal_created", "read_book", result.goal_id,
                selected_tendency=proposal.selected_tendency
            )
        if proposal.selected_tendency == "persist" and self.work is not None:
            if work is not None:
                return NativeGoalChoiceReceipt(
                    "already_complete", "work", work["id"], work["memory_id"],
                    selected_tendency="persist"
                )
            result = self.work.originate(proposal)
            if result.goal_id is None:
                return self._move_to_remembered_cue(proposal, authorized_world_action)
            return NativeGoalChoiceReceipt(
                result.status, "work" if result.goal_id else None,
                result.goal_id, result.memory_id,
                selected_tendency=result.selected_tendency
            )
        # A completed goal is history, never the active opportunity. A new
        # original AVOID may support a NEW rest only if the world independently
        # exhibits renewed physical fatigue and can perform a bedroom rest.
        if proposal.selected_tendency != "avoid":
            return NativeGoalChoiceReceipt(
                "no_situated_goal", None, None,
                selected_tendency=proposal.selected_tendency
            )
        if rest is not None and rest["phase"] == "complete":
            if not self._new_physical_rest_need():
                return NativeGoalChoiceReceipt(
                    "no_situated_goal", None, None, selected_tendency="avoid"
                )
        return self._originate_rest(proposal)

    def _move_to_remembered_cue(self, proposal, authorized):
        """One physical exploration hop toward an ACTUALLY seen local cue.

        A new neural explore/persist choice may support travel to a previously
        verified room observation after rest. The host supplies a shortest
        physical route, never a book/work goal, unseen target, or action
        sequence. This movement has NO goal ID and earns NO R4 completion.
        """
        from pretorius_lab.embodied_access import STATIONS
        from .organs import CognitiveProposal
        if type(proposal) is not CognitiveProposal or proposal.selected_tendency not in (
                "explore", "persist"):
            raise PermissionError("Exploratory travel requires original neural policy")
        if not authorized:
            return NativeGoalChoiceReceipt(
                "no_situated_goal", None, None,
                selected_tendency=proposal.selected_tendency,
            )
        station = self.host.subject.embodied.verify()["station"]
        # Only verified original physical LOOK receipts can identify a cue.
        # The Laboratory's source-defined graph supplies traversable edges.
        seen = {
            event["after_station"]
            for event, _ in _verified_looks(self.host.subject.embodied)
            if event["after_station"] in STATIONS
            and any(feature in event["offered_payload"]["perceived_features"]
                    for feature in ("bookshelves", "workbench"))
        }
        if station in seen:
            return NativeGoalChoiceReceipt(
                "no_situated_goal", None, None,
                selected_tendency=proposal.selected_tendency,
            )
        if seen:
            # A real prior LOOK can justify returning to its witnessed cue.
            hop = next((
                step for target in sorted(seen)
                if (step := EndogenousBookPursuit._route(station, target)) is not None
            ), None)
        elif proposal.selected_tendency == "explore":
            # Previously, a first EXPLORE in a pristine world was trapped:
            # no room had been visited, so no remembered cue could exist.
            # Reuse the SAME original six-organ affordance allocator for
            # ONE adjacent, physically legal exploratory hop. It uses the
            # source-defined world graph and original lived movement counts,
            # never an unseen book/work cue, authored destination or goal.
            # The resulting movement has NO goal identity or R4 credit.
            hop = self.host._select_internal_affordance("explore", station)
        else:
            hop = None
        if hop is None:
            return NativeGoalChoiceReceipt(
                "no_situated_goal", None, None,
                selected_tendency=proposal.selected_tendency,
            )
        result = self.host._execute_movement(proposal, hop)
        if result.status not in ("admitted", "already_admitted") or not result.memory_id:
            raise RuntimeError("Exploratory movement lacks original lived receipt")
        return NativeGoalChoiceReceipt(
            "moved", None, None, result.memory_id,
            selected_tendency=proposal.selected_tendency,
        )

    def _originate_rest(self, proposal):
        # Original neural avoidance must be proved by its current policy,
        # not supplied by an external task message or synthetic body state.
        prior = self._load_rest()
        if (proposal.selected_tendency != "avoid"
                or (prior is not None and (
                    prior["phase"] != "complete"
                    or not self._new_physical_rest_need()
                ))):
            raise PermissionError("No new original-neural rest origin")
        _, latest = self.host.corpus._verified_policy(proposal)
        if latest != proposal.policy_decision_id:
            raise PermissionError("Stale neural rest intention")
        self.host.subject.home.verify()
        ident = sha256((self._epoch() + "|" +
                        proposal.policy_decision_id).encode()).hexdigest()[:24]
        record = {
            "schema": _REST_SCHEMA, "id": ident,
            "world_epoch": self._epoch(), "goal": _REST_GOAL,
            "phase": "travel", "steps": 0,
            "origin_policy_id": proposal.policy_decision_id,
            "origin_thought_id": proposal.thought_id, "memory_id": None,
        }
        self._save_rest(record, archive_completed=prior)
        return NativeGoalChoiceReceipt(
            "goal_created", "rest", ident, selected_tendency="avoid"
        )

    def _verify_completed_book(self, book):
        """Source-prove historical completion BEFORE issuing a later goal.

        The original first-person page memory must map to a real hashed
        Laboratory book READ event. The neural policy cannot use a forged
        completed-record flag to clear an existing unfinished intention.
        """
        from .lab_home_bridge import _row
        memory = self.store.get_memory(book.memory_id)
        if (memory is None or not memory["active"]
                or memory["evidence_class"] != "lived_runtime_memory"
                or not memory["source"].startswith("laboratory-home:action:")
                or "I read a page of " not in memory["text"]):
            raise RuntimeError("Prior book goal lacks a verified lived read")
        digest = memory["source"].removeprefix("laboratory-home:action:")
        with self.host.bridge.world._open() as db:
            events = db.execute(
                "SELECT event_id FROM books_events WHERE event_hash=?",
                (digest,),
            ).fetchall()
            if len(events) != 1:
                raise RuntimeError("Prior book memory has no unique physical event")
            event, hash_value = _row(db, "books_events", events[0][0])
        if (hash_value != digest or event.get("action", {}).get("op") != "read"
                or event.get("page_receipt") is None):
            raise RuntimeError("Earlier goal was not an authentic book reading")

    def _continue_rest(self, state, authorized):
        if state["phase"] == "complete":
            return NativeGoalChoiceReceipt(
                "already_complete", "rest", state["id"], state["memory_id"]
            )
        if not authorized:
            return NativeGoalChoiceReceipt(
                "authorization_required", "rest", state["id"]
            )
        if state["steps"] >= 12:
            raise RuntimeError("Bounded rest goal needs a new review")
        at = self.host.subject.embodied.verify()["station"]
        if at != "station:bedroom":
            to = EndogenousBookPursuit._route(at, "station:bedroom")
            if to is None:
                raise RuntimeError("No source-reviewed route to bedroom")
            proposal = self._native_policy()
            consequence = self.host._execute_movement(proposal, to)
            if consequence.status not in ("admitted", "already_admitted"):
                raise RuntimeError("Bedward movement lacks verified lived result")
            state["steps"] += 1
            state["phase"] = "travel"
            self._save_rest(state)
            return NativeGoalChoiceReceipt(
                "moved", "rest", state["id"], consequence.memory_id,
                selected_tendency=proposal.selected_tendency
            )
        # Rest is not a simulated checkbox: Laboratory's independently
        # persisted rhythm ledger and original first-person memory must exist.
        event_id = "ng_" + state["id"] + "_rest"
        outcome = self.host.bridge.act("rest", event_id=event_id)
        memory = self.store.get_memory(outcome["memory_id"])
        if (memory is None
                or memory["evidence_class"] != "lived_runtime_memory"
                or not memory["source"].startswith("laboratory-home:action:")
                or memory["text"] != outcome["subject"]["inner"]):
            raise RuntimeError("Failed to admit a real bodily rest consequence")
        self._finish_source_verified_rest(state, memory, event_id)
        return NativeGoalChoiceReceipt(
            "completed", "rest", state["id"], memory["id"]
        )
