"""Candidate B persistent work intention on the ONE original Noesis and Laboratory.

A source-observed workbench plus original six-organ PERSIST tendency may
originate an intention. A separate ORIGINAL Noesis situated choice determines
repair versus experiment at the real bench. This is bounded host routing, not
an independent agent, scripted goal sequence, or new motor authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from .lab_endogenous_book_task import EndogenousBookPursuit, _verified_looks
from .noesis_lab_work import _feasible_work, propose_noesis_work, execute_noesis_work

WORK_KEY = "six_organ_native_work_intention_v1"
_SCHEMA = "pretorius.native-work-intention.v1"
_GOAL = "I want to undertake worthwhile work at my laboratory bench."
_PHASES = frozenset(("travel", "blocked", "execute", "complete"))
_WORK_ACTIONS = frozenset(("repair", "experiment"))


def _stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(value):
    return sha256(_stable(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class WorkReceipt:
    status: str
    goal_id: str | None
    memory_id: str | None = None
    selected_tendency: str | None = None


class NativeWorkPursuit:
    """Only a persistent BrainStore goal adapter; no extra planning substrate."""

    def __init__(self, session):
        self.host = session
        self.store = session.runtime._port.brain.store
        self.state = self._load()

    def _epoch(self):
        return self.host.subject.verify()["world_epoch"]

    def _load(self):
        raw = self.store.meta(WORK_KEY)
        if raw is None:
            return None
        try:
            envelope = json.loads(raw)
            if type(envelope) is not dict or set(envelope) != {"payload", "sha256"}:
                raise ValueError("invalid work envelope")
            state = envelope["payload"]
            if (type(state) is not dict or set(state) != {
                    "schema", "id", "world_epoch", "goal", "phase", "steps",
                    "origin_policy_id", "origin_thought_id", "work_policy_id",
                    "selected_action", "memory_id"} or
                    envelope["sha256"] != _hash(state) or
                    state["schema"] != _SCHEMA or
                    state["world_epoch"] != self._epoch() or
                    state["goal"] != _GOAL or state["phase"] not in _PHASES or
                    type(state["steps"]) is not int or not 0 <= state["steps"] <= 12 or
                    type(state["id"]) is not str or
                    re.fullmatch(r"[0-9a-f]{24}", state["id"]) is None):
                raise ValueError("invalid work state")
            with self.store.connect() as db:
                origin = db.execute(
                    "SELECT selected_action FROM policy_decisions WHERE id=?",
                    (state["origin_policy_id"],)).fetchone()
                thought = db.execute(
                    "SELECT generated_by FROM thoughts WHERE id=?",
                    (state["origin_thought_id"],)).fetchone()
                if (origin is None or origin["selected_action"] != "persist" or
                        thought is None or thought["generated_by"] !=
                        "neural_policy:" + state["origin_policy_id"]):
                    raise ValueError("not an original neural persist intention")
                work = None
                if state["work_policy_id"] is not None:
                    work = db.execute(
                        "SELECT selected_action,state_pressure_json FROM policy_decisions "
                        "WHERE id=? AND trigger='noesis_situated_choice'",
                        (state["work_policy_id"],)).fetchone()
            if state["work_policy_id"] is None:
                if state["phase"] not in ("travel", "blocked") or state["selected_action"] is not None:
                    raise ValueError("work phase without physical decision")
            elif (work is None or work["selected_action"] not in _WORK_ACTIONS or
                  work["selected_action"] != state["selected_action"] or
                  json.loads(work["state_pressure_json"]).get("selector_authority")
                  != "original_noesis"):
                raise ValueError("unverified concrete work policy")
            if state["phase"] == "complete":
                if state["memory_id"] is None or work is None:
                    raise ValueError("completion has no memory or policy")
                from .lab_home_bridge import _row
                memory = self.store.get_memory(state["memory_id"])
                if (memory is None or not memory["active"] or memory["external"] or
                        memory["evidence_class"] != "lived_runtime_memory" or
                        not memory["source"].startswith("laboratory-home:action:")):
                    raise ValueError("completed work has no authentic lived memory")
                digest = memory["source"].split(":")[-1]
                with self.host.bridge.world._open() as db:
                    found = db.execute(
                        "SELECT event_id FROM rhythm_events WHERE event_hash=?",
                        (digest,)).fetchall()
                    if len(found) != 1:
                        raise ValueError("completed work world receipt missing")
                    event, checked = _row(db, "rhythm_events", found[0][0])
                if (checked != digest or event.get("op") != state["selected_action"]
                        or event.get("station") != "station:bench" or
                        event.get("subject", {}).get("inner") != memory["text"]):
                    raise ValueError("completed work source mismatch")
                from .noesis_lab_work import verify_noesis_work_replay
                if verify_noesis_work_replay(
                        self.host.bridge, event_id=found[0][0],
                        action=state["selected_action"]) != state["work_policy_id"]:
                    raise ValueError("work lacks original Noesis motor custody")
            elif state["memory_id"] is not None:
                raise ValueError("unfinished work has a completion memory")
            return state
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            raise RuntimeError("Corrupt or forged native work intention") from exc

    def _save(self, state):
        with self.store.transaction() as db:
            self.store.set_meta(
                WORK_KEY, _stable({"payload": state, "sha256": _hash(state)}), db
            )
            self.store.bump_state_version(db)
        self.state = state

    def originate(self, proposal):
        """Require a real LOCAL look, original persist policy, and bench viability."""
        if self.state is not None:
            raise RuntimeError("A native work commitment already exists")
        from .organs import CognitiveProposal
        if type(proposal) is not CognitiveProposal or proposal.selected_tendency != "persist":
            raise PermissionError("Only original neural persist can originate work")
        _, latest = self.host.corpus._verified_policy(proposal)
        if latest != proposal.policy_decision_id:
            raise PermissionError("Stale Noesis goal origin")
        at = self.host.subject.embodied.verify()["station"]
        scenes = _verified_looks(self.host.subject.embodied)
        if not any(e["after_station"] == at and
                   "workbench" in e["offered_payload"]["perceived_features"]
                   for e, _ in scenes):
            return WorkReceipt("no_situated_goal", None, selected_tendency="persist")
        if EndogenousBookPursuit._route(at, "station:bench") is None and at != "station:bench":
            return WorkReceipt("no_situated_goal", None, selected_tendency="persist")
        # Original world pure transition evaluates the real BENCH's current
        # physics. No host-scripted choice, magical supply, or fake feasibility.
        from pretorius_lab.daily_rhythm import transition
        from pretorius_lab.physics import Conflict, LabError
        physical = self.host.subject.rhythm.audit_state()
        possible = []
        for action in sorted(_WORK_ACTIONS):
            try:
                transition(physical, action, {}, "station:bench")
            except (Conflict, LabError):
                continue
            possible.append(action)
        if not possible:
            return WorkReceipt("no_situated_goal", None, selected_tendency="persist")
        ident = sha256((self._epoch() + "|" +
                        proposal.policy_decision_id).encode()).hexdigest()[:24]
        record = {
            "schema": _SCHEMA, "id": ident, "world_epoch": self._epoch(),
            "goal": _GOAL, "phase": "travel", "steps": 0,
            "origin_policy_id": proposal.policy_decision_id,
            "origin_thought_id": proposal.thought_id,
            "work_policy_id": None, "selected_action": None,
            "memory_id": None,
        }
        self._save(record)
        return WorkReceipt("goal_created", ident, selected_tendency="persist")

    def step(self, *, authorized: bool, new_policy):
        state = self._load()
        if state is None:
            raise RuntimeError("No original native work commitment")
        if state["phase"] == "complete":
            return WorkReceipt("already_complete", state["id"], state["memory_id"])
        if not authorized:
            return WorkReceipt("authorization_required", state["id"])
        if state["steps"] >= 12:
            raise RuntimeError("Work commitment exhausted its bounded action budget")
        at = self.host.subject.embodied.verify()["station"]
        if at != "station:bench":
            next_station = EndogenousBookPursuit._route(at, "station:bench")
            if next_station is None:
                raise RuntimeError("No physical route to workbench")
            proposal = new_policy()
            moved = self.host._execute_movement(proposal, next_station)
            if moved.status not in ("admitted", "already_admitted"):
                raise RuntimeError("Native work move has no lived world receipt")
            state["steps"] += 1
            self._save(state)
            return WorkReceipt("moved", state["id"], moved.memory_id,
                               proposal.selected_tendency)
        if state["phase"] in ("travel", "blocked"):
            if not _feasible_work(self.host.bridge):
                # Preserve the interrupted goal in the SAME BrainStore. No
                # external instruction or invented material can unblock it.
                if state["phase"] != "blocked":
                    state["phase"] = "blocked"
                    self._save(state)
                return WorkReceipt("blocked", state["id"])
            # A real six-port cycle precedes the concrete work selection.
            # It is non-actuating: only the subsequently source-verified
            # original Noesis work policy may authorize a physical action.
            cycle = self.host.cycle(authorized_world_action=False)
            if len(cycle.ports_used) != 6 or cycle.subjective_delivery_count != 1:
                raise RuntimeError("Incomplete canonical six-organ work opportunity")
            proposed = propose_noesis_work(
                self.host.bridge, outcome_learning_enabled=True
            )
            state["phase"] = "execute"
            state["work_policy_id"] = proposed.decision_id
            state["selected_action"] = proposed.action
            self.host.runtime.checkpoint()
            self._save(state)
        # A crash after reservation must reuse the original concrete Noesis
        # choice and stable world event identity, NEVER ask Noesis again.
        event_id = "ng_" + state["id"] + "_work"
        outcome = execute_noesis_work(
            self.host.bridge, decision_id=state["work_policy_id"],
            event_id=event_id, authorized_world_action=True,
        )
        if outcome["world"]["status"] not in ("admitted", "already_admitted"):
            raise RuntimeError("Original work effect not source-admitted")
        state["phase"] = "complete"
        state["memory_id"] = outcome["world"]["memory_id"]
        state["steps"] += 1
        self._save(state)
        # Verify the freshly saved completion, including the original world.
        self._load()
        return WorkReceipt("completed", state["id"], state["memory_id"])
