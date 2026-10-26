"""Opt-in Mnemosyne endogenous-recollection experiment on the canonical brain.

Mechanism source: reviewed PR #59 cognition.py research_endogenous_recall
(2b0bb21425558cb24906309075b3d919850b10e8). This *reuses* its
epistemic recall-vs-continue/ask/defer policy, with one existing neural state,
policy table, and BrainPort recollection capability. It does not introduce
another LLM, durable brain, or independent neural/action selector.

Host calls are opportunities to deliberate; the *question* is derived from an
existing source-qualified internal concern, never supplied as a text argument.
This is a bounded research interface, NOT autonomous model authorship or a
default runtime change.
"""
from __future__ import annotations

from dataclasses import dataclass
from contextlib import closing
import hashlib
import json
import math

from .chassis import PretoriusBrainPort
from .models import SubjectFrame
from .store import new_id, utc_now
from .subject_inquiry import SubjectInquiryError, validate_subject_inquiry

_SOURCE = "preview_sensus_conflict"
_ACTOR = "PREVIEW_HOST"
_TRIGGER = "preview_endogenous_recall_v01"
_POLICY = "preview-epistemic-deliberation-v0.1"
_ORDER = ("continue", "ask", "defer", "recall")


@dataclass(frozen=True, slots=True)
class EndogenousRecallDecision:
    """Host audit only, not a subject-visible thought or assertion of awareness."""

    decision_id: str
    action: str
    selected_gap_id: str | None
    recall_pressure: float
    initiated_by: str = "host_scheduled_internal_policy"


class MnemosyneEndogenousPilot:
    def __init__(self, port: PretoriusBrainPort, *, enabled: bool = False):
        if not isinstance(port, PretoriusBrainPort):
            raise TypeError("The pilot uses only the canonical Pretorius brain")
        if enabled is not True:
            raise PermissionError("Explicit experimental Mnemosyne opt-in required")
        self._port = port
        self._pending_question: str | None = None
        self._controller = port.bind_recollection_controller(self._internal_question)

    def _internal_question(self) -> str:
        if self._pending_question is None:
            raise RuntimeError("No policy-selected recollection is pending")
        return self._pending_question

    def deliberate(
        self, *, recall_cost: float = 0.12, cooldown_ticks: int = 2,
    ) -> EndogenousRecallDecision:
        """Decide from *internal* unresolved uncertainty, without a host question.

        Deliberation logs one versioned decision into the original BrainStore,
        but never adds a false autobiography or executes a world action.
        """
        if self._pending_question is not None:
            raise RuntimeError("Resolve the previous recollection before deliberating")
        if (type(recall_cost) not in (float, int)
                or not math.isfinite(recall_cost)
                or not 0 <= recall_cost <= 1):
            raise ValueError("Recall cost must be finite and in [0,1]")
        if type(cooldown_ticks) is not int or not 1 <= cooldown_ticks <= 100:
            raise ValueError("Cooldown must be in [1,100]")
        brain = self._port.brain
        base, adjusted, bridge = brain._state_policy_scores(
            [], decision_text=None, bridge_enabled=True
        )
        with closing(brain.store.connect()) as conn:
            needs = {
                str(row["key"]): float(row["felt"])
                for row in conn.execute("SELECT key,felt FROM needs")
            }
            last = conn.execute(
                """SELECT tick FROM policy_decisions
                WHERE trigger=? AND selected_action='recall'
                ORDER BY rowid DESC LIMIT 1""",
                (_TRIGGER,),
            ).fetchone()

        def bounded(v: float) -> float:
            return max(0.0, min(1.0, float(v)))

        curiosity = bounded((needs.get("curiosity", 0.5) - 0.5) / 0.45)
        fatigue = bounded((needs.get("fatigue", 0.5) - 0.5) / 0.45)
        candidates = []
        for concern in brain.store.open_concerns():
            if concern["source"] != _SOURCE or concern["actor"] != _ACTOR:
                continue
            description = " ".join(str(concern["description"]).split()).rstrip(".?")
            question = f"What do I remember of {description}?"
            try:
                validate_subject_inquiry(question)
            except SubjectInquiryError:
                continue
            uncertainty = bounded(float(concern["uncertainty"]))
            importance = bounded(float(concern["importance"]))
            candidates.append(
                (uncertainty * importance, str(concern["id"]), question)
            )
        candidates.sort(key=lambda row: (-row[0], row[1]))
        best = candidates[0] if candidates else None
        pressure = best[0] if best else 0.0
        cooldown = (
            last is not None
            and 0 <= brain.store.tick - int(last["tick"]) < cooldown_ticks
        )
        # Direct adaptation of PR #59 bounded epistemic policy. It does not
        # replace the existing ten-action recurrent neural substrate.
        raw = {
            "recall": max(
                0.0, 0.12 + 0.72 * pressure + 0.12 * curiosity
                + 0.10 * adjusted["explore"] - float(recall_cost)
                - 0.50 * fatigue,
            ) if best is not None and not cooldown else 0.0,
            "continue": 0.35 + 0.35 * adjusted["persist"],
            "ask": 0.16 + 0.20 * pressure * (1.0 - curiosity),
            "defer": 0.07 + 0.50 * fatigue,
        }
        total = sum(raw.values())
        scores = {key: value / total for key, value in raw.items()}
        chosen = max(_ORDER, key=lambda key: raw[key])
        gap_id = best[1] if chosen == "recall" else None
        question = best[2] if gap_id else None
        audit = {
            "schema": "the-doctor-lives.endogenous-recall-research.v0.1",
            "policy_version": _POLICY,
            "origin": "trusted_host_sensus_conflict_preview",
            "autonomous_model_authorship_proven": False,
            "memory_retrieval_performed": False,
            "information_need_family": {
                "recall_pressure": pressure,
                "curiosity": curiosity,
                "fatigue": fatigue,
                "recollection_cost": recall_cost,
                "cooldown_active": cooldown,
            },
            "candidate_gap_ids": [c[1] for c in candidates],
            "selected_gap_ids": [gap_id] if gap_id else [],
            "question_sha256": hashlib.sha256(
                question.encode("utf-8")
            ).hexdigest() if question else None,
            "deliberative_raw_scores": raw,
            "state_policy_bridge": bridge,
        }
        decision_id = new_id("policy")
        with brain.store.transaction() as conn:
            conn.execute(
                """INSERT INTO policy_decisions
                (id,tick,created_at,trigger,selected_action,
                 base_action_scores_json,state_pressure_json,
                 action_scores_json,candidate_record_ids_json,
                 selected_record_ids_json,neural_tick,
                 neural_checkpoint_sha256,policy_version)
                 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    decision_id, brain.store.tick, utc_now(), _TRIGGER, chosen,
                    json.dumps(base, sort_keys=True),
                    json.dumps(audit, sort_keys=True),
                    json.dumps(scores, sort_keys=True),
                    json.dumps(audit["candidate_gap_ids"]),
                    json.dumps(audit["selected_gap_ids"]),
                    int(brain.neural.tick),
                    brain._neural_checkpoint_sha256(),
                    _POLICY,
                ),
            )
            brain.store.bump_state_version(conn)
        if question is not None:
            self._pending_question = question
        return EndogenousRecallDecision(
            decision_id=decision_id, action=chosen,
            selected_gap_id=gap_id, recall_pressure=pressure,
        )

    def recollect(self) -> SubjectFrame:
        """Consume the one-use original host-bound private recollection grant."""
        if self._pending_question is None:
            raise PermissionError("No internally selected recall action")
        try:
            return self._controller.recollect_frame()
        finally:
            self._pending_question = None
