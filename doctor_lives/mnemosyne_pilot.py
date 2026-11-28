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
import re

from .chassis import PretoriusBrainPort
from .models import SubjectFrame, SubjectRendererCapability
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


@dataclass(frozen=True, slots=True)
class PrivateRecollectionEffect:
    """Engineer-only evidence of original brain policy after subject recall."""
    recall_decision_id: str
    next_policy_decision_id: str | None
    next_tendency: str | None
    relevant_lines: int
    cue_sha256: str | None


_STOPWORDS = frozenset({"what", "remember", "recall", "about", "with",
                         "from", "that", "this", "their", "there", "have",
                         "been", "would", "could", "should", "were",
                         "when", "where", "into", "mine", "something"})


def _cue_terms(value: str) -> frozenset[str]:
    return frozenset(
        term for term in re.findall(r"[a-z]{4,}", value.lower())
        if term not in _STOPWORDS
    )


class MnemosyneEndogenousPilot:
    def __init__(self, port: PretoriusBrainPort, *, enabled: bool = False):
        if not isinstance(port, PretoriusBrainPort):
            raise TypeError("The pilot uses only the canonical Pretorius brain")
        if enabled is not True:
            raise PermissionError("Explicit experimental Mnemosyne opt-in required")
        self._port = port
        self._pending_question: str | None = None
        self._pending_decision_id: str | None = None
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
        # Candidate ranking is latent. The selected uncertainty is admitted
        # before the original epistemic policy consumes it. No host question
        # or externally supplied goal is introduced.
        from .tower_ipseity import TowerIpseity, ownership_required, DELIBERATION
        from .phenomenology import PhenomenalMode, SubjectiveSourceKind
        subject = TowerIpseity(brain) if ownership_required(brain) else None
        context = None
        status_key = None
        if subject is not None:
            subject.verify_tail()
            if best is not None:
                event = subject.event("Mnemosyne", "I ask myself: " + best[2],
                                      PhenomenalMode.INTERNAL_THOUGHT, (best[1],),
                                      attribution=SubjectiveSourceKind.UNKNOWN)
                with brain.store.transaction() as db:
                    context = subject.record(db, new_id("recall-context"), (event,),
                                             phase="recall_context")
                    status_key = DELIBERATION + context["sha256"]
                    brain.store.set_meta(status_key, json.dumps({"status": "pending"}, sort_keys=True), db)
        try:
            base, adjusted, bridge = brain._state_policy_scores(
                [], decision_text=None, bridge_enabled=True
            )
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
            if context is not None:
                audit["ipseity_context"] = {"key": context["key"], "sha256": context["sha256"]}
            if subject is not None:
                wording = {"recall": "I want to recall what I can of this.",
                           "continue": "I mean to continue with what presently occupies me.",
                           "ask": "I would like to ask about what I do not understand.",
                           "defer": "I will leave this uncertainty for another moment."}[chosen]
                intention = subject.event("Mnemosyne", wording, PhenomenalMode.INTENTION,
                                          (decision_id,) + ((gap_id,) if gap_id else ()),
                                          attribution=SubjectiveSourceKind.SELF_OBSERVED)
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
                if subject is not None:
                    subject.record(conn, "recall-decision:" + decision_id, (intention,),
                                   phase="private_experience")
                if status_key is not None:
                    brain.store.set_meta(status_key, json.dumps({"status": "completed",
                        "policy_id": decision_id}, sort_keys=True), conn)
                brain.store.bump_state_version(conn)
        except Exception:
            if status_key is not None:
                try:
                    with brain.store.transaction() as db:
                        brain.store.set_meta(status_key, json.dumps({"status": "failed"}, sort_keys=True), db)
                        brain.store.bump_state_version(db)
                except Exception:
                    pass  # Durable pending is not completed after interruption.
            raise
        if question is not None:
            self._pending_question = question
            self._pending_decision_id = decision_id
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
            self._pending_decision_id = None

    def reflect_selected_recollection(self, *, reconstruct: bool = False) -> PrivateRecollectionEffect:
        """Recollection influences cognition only via a factory-created subject frame.

        Existing policy and BrainStore retain all decision/write authority;
        neither engineer audit nor unobserved facts enter private cognition.
        No retrieved relevant first-person content means NO invented thought.
        """
        question, recall_id = self._pending_question, self._pending_decision_id
        if question is None or recall_id is None:
            raise PermissionError("No selected recollection awaiting reflection")
        frame = self.recollect()  # consumes the original state-bound one-use grant
        from .dream_resurfacing import selected_recall_question
        if selected_recall_question(self._port.brain, recall_id) != question:
            raise PermissionError("Selected recollection is stale or unauthorized")
        if type(frame) is not SubjectFrame:
            raise TypeError("Recollection returned noncanonical subject frame")
        terms = _cue_terms(question)
        # The canonical SubjectFrame contains recollections FIRST, followed
        # by present needs, impulses, relationships and unresolved concerns.
        # Restrict the private-cognition cue to actual memory projections:
        # treating a projected *concern* as a remembered fact would fabricate
        # autobiographical knowledge. The memory count is host-only and never
        # passed to the thought/renderer.
        brain = self._port.brain
        before = (brain.store.digest(), brain.neural.tick)
        memory_items = brain.cognitive_view(query=question, audit=False).experiences
        memory_count = len(memory_items)
        if (brain.store.digest(), brain.neural.tick) != before:
            raise RuntimeError("Subject recollection changed while selecting cue")
        lines = SubjectRendererCapability.read(frame)[:memory_count]
        ranked = sorted(
            ((len(_cue_terms(line) & terms), line)
             for line in lines
             if line.startswith(("I ", "My ", "Mine ", "Me "))),
            key=lambda row: (-row[0], row[1]),
        )
        matches = [row for row in ranked if row[0] > 0]
        from .tower_ipseity import TowerIpseity
        from .phenomenology import PhenomenalMode, SubjectiveSourceKind
        subject = TowerIpseity(brain)
        fragment = None
        if not matches or matches[0][0] < 2:
            from .dream_resurfacing import select_fragment
            suppressed = brain.store.canon_conflict_suppressed_memory_ids()
            rows = [r for r in brain.store.memories_with_classification() if r["id"] not in suppressed]
            fragment = select_fragment(rows, subject.verify_history(), brain.store.tick, question)
        if fragment is not None:
            _, source_id, cue = fragment
            source_ids = []
            refs = (recall_id, source_id)
            attribution = SubjectiveSourceKind.UNKNOWN
            external = True
        else:
            if not matches:
                return PrivateRecollectionEffect(recall_id, None, None, 0, None)
            cue = matches[0][1]
            source_ids = [item.record_id for item in memory_items if item.first_person == cue]
            if reconstruct:
                from .mnemosyne_reconstruction import reconstruct_selected
                cue = reconstruct_selected(brain, question, recall_id, cue)
                if cue is None:
                    return PrivateRecollectionEffect(recall_id, None, None, 0, None)
            refs = (recall_id,)
            attribution = SubjectiveSourceKind.SELF_OBSERVED
            external = False
        # Only this invocation, which consumed the original retrieval grant
        # and selected the exact cue, can authorize its conscious admission.
        # Neither a policy row nor a raw history entry is a bearer credential.
        from .first_person_governance import first_person_line
        cue = first_person_line(cue)
        if selected_recall_question(brain, recall_id) != question:
            raise PermissionError("Selected recollection is stale or unauthorized")
        if (getattr(brain, "_pending_recollection_admission", None) is not None
                or getattr(brain, "_pending_recollection_processing", None) is not None):
            raise PermissionError("Another selected recollection is pending")
        key = "recollection:" + recall_id
        content = [{"organ": "Mnemosyne", "text": cue, "mode": "recollection",
                    "attribution": attribution.value, "source_refs": list(refs), "external": external}]
        brain._pending_recollection_admission = (
            key, "private_experience", content, brain.store.tick, brain.store.digest(), brain.neural.tick)
        try:
            if external:
                event = subject.event("Mnemosyne", cue, PhenomenalMode.RECOLLECTION,
                                      refs, attribution=attribution, external=True)
                with brain.store.transaction() as db:
                    admission = subject.record(db, key, (event,), phase="private_experience")
            else:
                admission = subject.admit_private(
                    key, "Mnemosyne", cue, refs, mode=PhenomenalMode.RECOLLECTION)
        finally:
            brain._pending_recollection_admission = None
        history = subject.verify_history()
        if (not history or history[-1] != admission or admission["content"] != content
                or admission["tick"] != brain.store.tick):
            raise PermissionError("Selected recollection admission was not committed freshly")
        # This process-local handoff is lost on restart and consumed at the
        # Noesis boundary before ranking or policy. Do not persist a live grant.
        brain._pending_recollection_processing = (
            admission["sha256"], brain.store.tick, brain.store.digest(), brain.neural.tick)
        try:
            thought = brain.think("mnemosyne_private_reflection", decision_text=cue)
        finally:
            brain._pending_recollection_processing = None
        # Only a uniquely identified completed owned reflection strengthens direct recall.
        if len(source_ids) == 1:
            from .dream_retention import is_dream_recollection
            source = brain.store.get_memory(source_ids[0])
            if source is not None and is_dream_recollection(source):
                tick = brain.store.tick
                with brain.store.transaction() as db:
                    brain.store.rehearse(db, source_ids[0], tick, explicit_dream_reflection=True)
                    brain.store.bump_state_version(db)
        return PrivateRecollectionEffect(
            recall_id, str(thought["policy_decision_id"]),
            str(thought["selected_action"]), max(len(matches), int(fragment is not None)),
            hashlib.sha256(cue.encode("utf-8")).hexdigest(),
        )

