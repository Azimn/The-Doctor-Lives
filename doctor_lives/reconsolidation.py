"""P6 conservative reconsolidation for UPPB.

P6 evolves memory by producing immutable successor MemoryTrace snapshots after
verified recollection and awareness. It never mutates an existing trace.

Initial P6 deliberately changes only bounded trace-strength variables and
retrieval/rehearsal counters. Gist, retained details, protected evidence,
source-cue labels, actor/object associations, and temporal content remain
unchanged. This establishes the causal loop before any later content drift.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .phenomenology import (
    AwarenessLevel,
    CertaintyBand,
    PhenomenalEvent,
    PhenomenalMode,
)
from .recollection import (
    MemoryTrace,
    ProtectedEvidenceRef,
    RecollectionCandidate,
    TraceDetail,
)
from .source_monitoring import SourceMonitoringDecision


_RECONSOLIDATION_DECISION_FACTORY_TOKEN = object()
_LEDGER_SCHEMA_VERSION = "uppb-p6-ledger-v1"
_ALLOWED_OPERATION_FIELDS = {
    "strength",
    "accessibility",
    "familiarity",
    "retrieval_count",
    "rehearsal_count",
}


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _unit(value: float, name: str) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be numeric, not bool")
    try:
        normalized = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be a finite number") from exc
    if not math.isfinite(normalized):
        raise ValueError(f"{name} must be finite")
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return normalized


def _positive_unit(value: float, name: str) -> float:
    normalized = _unit(value, name)
    if normalized <= 0.0:
        raise ValueError(f"{name} must be greater than zero")
    return normalized


def _optional_nonblank(value: str | None, name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-blank string or None")
    return value


@dataclass(frozen=True)
class ReconsolidationContext:
    """Engineer-visible reactivation context for one possible trace update."""

    enabled: bool = True
    reactivation_strength: float = 0.5
    prediction_error: float = 0.0
    emotional_activation: float = 0.0
    goal_relevance: float = 0.0
    explicit_rehearsal: bool = False
    rule_version: str = "uppb-p6-v1"

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be bool")
        if not isinstance(self.explicit_rehearsal, bool):
            raise TypeError("explicit_rehearsal must be bool")
        for name in (
            "reactivation_strength",
            "prediction_error",
            "emotional_activation",
            "goal_relevance",
        ):
            object.__setattr__(self, name, _unit(getattr(self, name), name))
        if not isinstance(self.rule_version, str) or not self.rule_version.strip():
            raise ValueError("rule_version is required")

    @property
    def fingerprint(self) -> str:
        return _stable_sha256(asdict(self))


@dataclass(frozen=True)
class ReconsolidationPolicy:
    """Bounded conservative plasticity policy for initial P6."""

    min_reactivation: float = 0.35
    min_prediction_error: float = 0.15
    min_emotional_activation: float = 0.40
    max_strength_delta: float = 0.02
    max_accessibility_delta: float = 0.04
    max_familiarity_delta: float = 0.03
    strength_ceiling: float = 0.95
    accessibility_ceiling: float = 0.98
    familiarity_ceiling: float = 0.98
    require_neutral_content_certainty: bool = True
    allow_blended_recollection: bool = False

    def __post_init__(self) -> None:
        for name in (
            "min_reactivation",
            "min_prediction_error",
            "min_emotional_activation",
            "max_strength_delta",
            "max_accessibility_delta",
            "max_familiarity_delta",
            "strength_ceiling",
            "accessibility_ceiling",
            "familiarity_ceiling",
        ):
            object.__setattr__(self, name, _unit(getattr(self, name), name))
        if not isinstance(self.require_neutral_content_certainty, bool):
            raise TypeError("require_neutral_content_certainty must be bool")
        if not isinstance(self.allow_blended_recollection, bool):
            raise TypeError("allow_blended_recollection must be bool")

    @property
    def fingerprint(self) -> str:
        return _stable_sha256(asdict(self))


@dataclass(frozen=True)
class ReconsolidationOperation:
    """One explicit bounded field change in a successor trace."""

    field_name: str
    old_value: float | int
    new_value: float | int
    delta: float | int
    reason_code: str

    def __post_init__(self) -> None:
        if self.field_name not in _ALLOWED_OPERATION_FIELDS:
            raise ValueError(f"unsupported reconsolidation field {self.field_name!r}")
        if isinstance(self.old_value, bool) or not isinstance(self.old_value, (int, float)):
            raise TypeError("old_value must be numeric")
        if isinstance(self.new_value, bool) or not isinstance(self.new_value, (int, float)):
            raise TypeError("new_value must be numeric")
        if isinstance(self.delta, bool) or not isinstance(self.delta, (int, float)):
            raise TypeError("delta must be numeric")
        if not isinstance(self.reason_code, str) or not self.reason_code.strip():
            raise ValueError("reason_code is required")
        if not math.isfinite(float(self.old_value)):
            raise ValueError("old_value must be finite")
        if not math.isfinite(float(self.new_value)):
            raise ValueError("new_value must be finite")
        if not math.isfinite(float(self.delta)):
            raise ValueError("delta must be finite")
        if abs((float(self.new_value) - float(self.old_value)) - float(self.delta)) > 1e-12:
            raise ValueError("delta must equal new_value - old_value")

    @property
    def fingerprint(self) -> str:
        return _stable_sha256(asdict(self))


@dataclass(frozen=True, init=False)
class ReconsolidationDecision:
    """Immutable causal record for one P6 eligibility/update decision."""

    old_trace_id: str
    old_trace_digest: str
    trace_lineage_id: str
    old_version: int
    candidate_id: str
    candidate_digest: str
    source_decision_fingerprint: str
    recollection_event_id: str
    recollection_event_lineage_fingerprint: str
    context: ReconsolidationContext
    context_fingerprint: str
    policy: ReconsolidationPolicy
    policy_fingerprint: str
    eligible: bool
    eligibility_strength: float
    operations: tuple[ReconsolidationOperation, ...]
    reason_codes: tuple[str, ...]
    decision_fingerprint: str

    def __init__(self, *, _factory_token: object = None) -> None:
        if _factory_token is not _RECONSOLIDATION_DECISION_FACTORY_TOKEN:
            raise TypeError(
                "ReconsolidationDecision is factory-controlled; "
                "use evaluate_reconsolidation()"
            )

    def stable_json(self) -> str:
        return _stable_json(asdict(self))


def _validate_upstream_chain(
    *,
    old_trace: MemoryTrace,
    candidate: RecollectionCandidate,
    source_decision: SourceMonitoringDecision,
    recollection_event: PhenomenalEvent,
) -> None:
    if not isinstance(old_trace, MemoryTrace):
        raise TypeError("old_trace must be MemoryTrace")
    if not isinstance(candidate, RecollectionCandidate):
        raise TypeError("candidate must be RecollectionCandidate")
    if not isinstance(source_decision, SourceMonitoringDecision):
        raise TypeError("source_decision must be SourceMonitoringDecision")
    if not isinstance(recollection_event, PhenomenalEvent):
        raise TypeError("recollection_event must be PhenomenalEvent")

    if candidate.subject_id != old_trace.subject_id:
        raise ValueError("candidate subject does not match old trace")
    if old_trace.trace_id not in candidate.trace_ids:
        raise ValueError("old trace is not part of the P4 candidate")
    if source_decision.candidate_id != candidate.candidate_id:
        raise ValueError("P5 decision candidate ID mismatch")
    if source_decision.candidate_digest != candidate.candidate_digest:
        raise ValueError("P5 decision candidate digest mismatch")
    if recollection_event.subject_id != candidate.subject_id:
        raise ValueError("recollection event subject mismatch")
    if recollection_event.mode is not PhenomenalMode.RECOLLECTION:
        raise ValueError("P6 requires a recollection PhenomenalEvent")

    expected_event_refs = (
        candidate.candidate_id,
        candidate.candidate_digest,
        source_decision.decision_fingerprint,
        candidate.retrieval_episode_fingerprint,
    )
    if recollection_event.source_event_refs != expected_event_refs:
        raise ValueError("recollection event does not preserve exact P4/P5 lineage")
    if recollection_event.source_state_refs != candidate.trace_ids:
        raise ValueError("recollection event trace lineage mismatch")
    if (
        tuple(recollection_event.objective_provenance.record_ids)
        != candidate.protected_evidence_refs
    ):
        raise ValueError("recollection event objective provenance mismatch")
    if recollection_event.subjective_source.kind is not source_decision.selected_source:
        raise ValueError("recollection event source attribution mismatch")
    if recollection_event.subjective_source.certainty is not source_decision.certainty:
        raise ValueError("recollection event source certainty mismatch")


def _bounded_delta(
    current: float,
    *,
    ceiling: float,
    max_delta: float,
    drive: float,
) -> float:
    remaining = max(0.0, ceiling - current)
    return min(max_delta, remaining * 0.25 * drive)


def _decision_payload(
    *,
    old_trace: MemoryTrace,
    candidate: RecollectionCandidate,
    source_decision: SourceMonitoringDecision,
    recollection_event: PhenomenalEvent,
    context: ReconsolidationContext,
    policy: ReconsolidationPolicy,
    eligible: bool,
    eligibility_strength: float,
    operations: tuple[ReconsolidationOperation, ...],
    reason_codes: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "old_trace_id": old_trace.trace_id,
        "old_trace_digest": old_trace.snapshot_digest,
        "trace_lineage_id": old_trace.trace_lineage_id,
        "old_version": old_trace.version,
        "candidate_id": candidate.candidate_id,
        "candidate_digest": candidate.candidate_digest,
        "source_decision_fingerprint": source_decision.decision_fingerprint,
        "recollection_event_id": recollection_event.event_id,
        "recollection_event_lineage_fingerprint": recollection_event.lineage_fingerprint,
        "context": asdict(context),
        "context_fingerprint": context.fingerprint,
        "policy": asdict(policy),
        "policy_fingerprint": policy.fingerprint,
        "eligible": eligible,
        "eligibility_strength": eligibility_strength,
        "operations": [asdict(op) for op in operations],
        "reason_codes": reason_codes,
    }


def evaluate_reconsolidation(
    *,
    old_trace: MemoryTrace,
    candidate: RecollectionCandidate,
    source_decision: SourceMonitoringDecision,
    recollection_event: PhenomenalEvent,
    context: ReconsolidationContext,
    policy: ReconsolidationPolicy | None = None,
) -> ReconsolidationDecision:
    """Evaluate eligibility and bounded update operations without mutating state."""

    policy = policy or ReconsolidationPolicy()
    if not isinstance(context, ReconsolidationContext):
        raise TypeError("context must be ReconsolidationContext")
    if not isinstance(policy, ReconsolidationPolicy):
        raise TypeError("policy must be ReconsolidationPolicy")

    _validate_upstream_chain(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        recollection_event=recollection_event,
    )

    reasons: list[str] = []
    if not context.enabled:
        reasons.append("reconsolidation_disabled")
    if recollection_event.awareness not in {
        AwarenessLevel.CONSCIOUS,
        AwarenessLevel.FOCAL,
    }:
        reasons.append("recollection_not_consciously_accessible")
    if policy.require_neutral_content_certainty and (
        recollection_event.subjective_certainty is not CertaintyBand.MODERATE
    ):
        reasons.append("nonneutral_content_certainty_not_grounded_for_p6")
    if candidate.blended and not policy.allow_blended_recollection:
        reasons.append("blended_recollection_not_enabled")
    if len(candidate.trace_ids) != 1 and not policy.allow_blended_recollection:
        reasons.append("multiple_trace_reconsolidation_not_enabled")
    if context.reactivation_strength < policy.min_reactivation:
        reasons.append("reactivation_below_threshold")

    destabilizing = (
        context.prediction_error >= policy.min_prediction_error
        or context.emotional_activation >= policy.min_emotional_activation
        or context.explicit_rehearsal
    )
    if not destabilizing:
        reasons.append("no_destabilizing_or_rehearsal_signal")

    eligible = not reasons
    if eligible:
        drive = min(
            1.0,
            0.45 * context.reactivation_strength
            + 0.25 * context.prediction_error
            + 0.15 * context.emotional_activation
            + 0.15 * context.goal_relevance
            + (0.10 if context.explicit_rehearsal else 0.0),
        )
        reasons.append("eligible_conscious_reactivation")
    else:
        drive = 0.0

    operations: list[ReconsolidationOperation] = []
    if eligible:
        strength_delta = _bounded_delta(
            old_trace.strength,
            ceiling=policy.strength_ceiling,
            max_delta=policy.max_strength_delta,
            drive=drive,
        )
        accessibility_delta = _bounded_delta(
            old_trace.accessibility,
            ceiling=policy.accessibility_ceiling,
            max_delta=policy.max_accessibility_delta,
            drive=drive,
        )
        familiarity_delta = _bounded_delta(
            old_trace.familiarity,
            ceiling=policy.familiarity_ceiling,
            max_delta=policy.max_familiarity_delta,
            drive=drive,
        )

        for field_name, old_value, delta in (
            ("strength", old_trace.strength, strength_delta),
            ("accessibility", old_trace.accessibility, accessibility_delta),
            ("familiarity", old_trace.familiarity, familiarity_delta),
        ):
            if delta > 0.0:
                operations.append(
                    ReconsolidationOperation(
                        field_name=field_name,
                        old_value=old_value,
                        new_value=old_value + delta,
                        delta=delta,
                        reason_code="bounded_reactivation_strengthening",
                    )
                )

        operations.append(
            ReconsolidationOperation(
                field_name="retrieval_count",
                old_value=old_trace.retrieval_count,
                new_value=old_trace.retrieval_count + 1,
                delta=1,
                reason_code="eligible_retrieval_reactivation",
            )
        )
        if context.explicit_rehearsal:
            operations.append(
                ReconsolidationOperation(
                    field_name="rehearsal_count",
                    old_value=old_trace.rehearsal_count,
                    new_value=old_trace.rehearsal_count + 1,
                    delta=1,
                    reason_code="explicit_rehearsal",
                )
            )

    operations_tuple = tuple(operations)
    reasons_tuple = tuple(reasons)
    payload = _decision_payload(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        recollection_event=recollection_event,
        context=context,
        policy=policy,
        eligible=eligible,
        eligibility_strength=drive,
        operations=operations_tuple,
        reason_codes=reasons_tuple,
    )

    decision = ReconsolidationDecision(
        _factory_token=_RECONSOLIDATION_DECISION_FACTORY_TOKEN
    )
    for name, value in (
        ("old_trace_id", old_trace.trace_id),
        ("old_trace_digest", old_trace.snapshot_digest),
        ("trace_lineage_id", old_trace.trace_lineage_id),
        ("old_version", old_trace.version),
        ("candidate_id", candidate.candidate_id),
        ("candidate_digest", candidate.candidate_digest),
        ("source_decision_fingerprint", source_decision.decision_fingerprint),
        ("recollection_event_id", recollection_event.event_id),
        (
            "recollection_event_lineage_fingerprint",
            recollection_event.lineage_fingerprint,
        ),
        ("context", context),
        ("context_fingerprint", context.fingerprint),
        ("policy", policy),
        ("policy_fingerprint", policy.fingerprint),
        ("eligible", eligible),
        ("eligibility_strength", drive),
        ("operations", operations_tuple),
        ("reason_codes", reasons_tuple),
    ):
        object.__setattr__(decision, name, value)
    object.__setattr__(
        decision,
        "decision_fingerprint",
        "reconsolidation_" + _stable_sha256(payload)[:24],
    )
    return decision


def _verify_decision_integrity(
    *,
    old_trace: MemoryTrace,
    candidate: RecollectionCandidate,
    source_decision: SourceMonitoringDecision,
    recollection_event: PhenomenalEvent,
    decision: ReconsolidationDecision,
) -> None:
    if not isinstance(decision, ReconsolidationDecision):
        raise TypeError("decision must be ReconsolidationDecision")
    _validate_upstream_chain(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        recollection_event=recollection_event,
    )
    if decision.old_trace_id != old_trace.trace_id:
        raise ValueError("reconsolidation decision old trace ID mismatch")
    if decision.old_trace_digest != old_trace.snapshot_digest:
        raise ValueError("reconsolidation decision old trace digest mismatch")
    if decision.candidate_id != candidate.candidate_id:
        raise ValueError("reconsolidation decision candidate ID mismatch")
    if decision.candidate_digest != candidate.candidate_digest:
        raise ValueError("reconsolidation decision candidate digest mismatch")
    if decision.source_decision_fingerprint != source_decision.decision_fingerprint:
        raise ValueError("reconsolidation decision P5 fingerprint mismatch")
    if decision.recollection_event_id != recollection_event.event_id:
        raise ValueError("reconsolidation decision event ID mismatch")
    if (
        decision.recollection_event_lineage_fingerprint
        != recollection_event.lineage_fingerprint
    ):
        raise ValueError("reconsolidation decision event lineage mismatch")
    if decision.context_fingerprint != decision.context.fingerprint:
        raise ValueError("reconsolidation context fingerprint mismatch")
    if decision.policy_fingerprint != decision.policy.fingerprint:
        raise ValueError("reconsolidation policy fingerprint mismatch")

    payload = _decision_payload(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        recollection_event=recollection_event,
        context=decision.context,
        policy=decision.policy,
        eligible=decision.eligible,
        eligibility_strength=decision.eligibility_strength,
        operations=decision.operations,
        reason_codes=decision.reason_codes,
    )
    expected = "reconsolidation_" + _stable_sha256(payload)[:24]
    if decision.decision_fingerprint != expected:
        raise ValueError("reconsolidation decision fingerprint mismatch")


def apply_reconsolidation(
    *,
    old_trace: MemoryTrace,
    candidate: RecollectionCandidate,
    source_decision: SourceMonitoringDecision,
    recollection_event: PhenomenalEvent,
    decision: ReconsolidationDecision,
) -> MemoryTrace | None:
    """Create an immutable successor trace when the verified decision is eligible."""

    _verify_decision_integrity(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        recollection_event=recollection_event,
        decision=decision,
    )
    if not decision.eligible:
        return None

    values: dict[str, float | int] = {
        "strength": old_trace.strength,
        "accessibility": old_trace.accessibility,
        "familiarity": old_trace.familiarity,
        "retrieval_count": old_trace.retrieval_count,
        "rehearsal_count": old_trace.rehearsal_count,
    }
    for operation in decision.operations:
        if values[operation.field_name] != operation.old_value:
            raise ValueError(
                f"operation old value mismatch for {operation.field_name}"
            )
        values[operation.field_name] = operation.new_value

    successor = MemoryTrace(
        subject_id=old_trace.subject_id,
        version=old_trace.version + 1,
        protected_evidence=old_trace.protected_evidence,
        gist=old_trace.gist,
        details=old_trace.details,
        temporal_cues=old_trace.temporal_cues,
        actor_refs=old_trace.actor_refs,
        object_refs=old_trace.object_refs,
        encoding_affect=old_trace.encoding_affect,
        source_cues=old_trace.source_cues,
        strength=float(values["strength"]),
        accessibility=float(values["accessibility"]),
        familiarity=float(values["familiarity"]),
        rehearsal_count=int(values["rehearsal_count"]),
        retrieval_count=int(values["retrieval_count"]),
        competing_trace_ids=old_trace.competing_trace_ids,
        parent_trace_id=old_trace.trace_id,
        reconsolidation_decision_fingerprint=decision.decision_fingerprint,
        reconsolidation_event_id=recollection_event.event_id,
    )

    if successor.trace_lineage_id != old_trace.trace_lineage_id:
        raise AssertionError("reconsolidation changed trace lineage")
    if successor.protected_evidence != old_trace.protected_evidence:
        raise AssertionError("reconsolidation changed protected evidence")
    if successor.gist != old_trace.gist or successor.details != old_trace.details:
        raise AssertionError("initial P6 may not rewrite gist or retained details")
    return successor


def _memory_trace_from_dict(data: dict[str, Any]) -> MemoryTrace:
    protected = tuple(
        ProtectedEvidenceRef(
            evidence_id=str(item["evidence_id"]),
            digest=str(item["digest"]),
        )
        for item in data["protected_evidence"]
    )
    details = tuple(
        TraceDetail(
            detail_id=str(item["detail_id"]),
            text=str(item["text"]),
            cue_terms=tuple(item.get("cue_terms", ())),
        )
        for item in data.get("details", ())
    )
    trace = MemoryTrace(
        subject_id=str(data["subject_id"]),
        version=int(data["version"]),
        protected_evidence=protected,
        gist=str(data["gist"]),
        details=details,
        temporal_cues=tuple(data.get("temporal_cues", ())),
        actor_refs=tuple(data.get("actor_refs", ())),
        object_refs=tuple(data.get("object_refs", ())),
        encoding_affect=tuple(data.get("encoding_affect", ())),
        source_cues=tuple(data.get("source_cues", ())),
        strength=float(data.get("strength", 0.5)),
        accessibility=float(data.get("accessibility", 0.5)),
        familiarity=float(data.get("familiarity", 0.5)),
        rehearsal_count=int(data.get("rehearsal_count", 0)),
        retrieval_count=int(data.get("retrieval_count", 0)),
        competing_trace_ids=tuple(data.get("competing_trace_ids", ())),
        parent_trace_id=_optional_nonblank(data.get("parent_trace_id"), "parent_trace_id"),
        reconsolidation_decision_fingerprint=_optional_nonblank(
            data.get("reconsolidation_decision_fingerprint"),
            "reconsolidation_decision_fingerprint",
        ),
        reconsolidation_event_id=_optional_nonblank(
            data.get("reconsolidation_event_id"),
            "reconsolidation_event_id",
        ),
    )
    stored_trace_id = data.get("trace_id")
    stored_lineage_id = data.get("trace_lineage_id")
    if stored_trace_id is not None and str(stored_trace_id) != trace.trace_id:
        raise ValueError("persisted trace_id does not match reconstructed snapshot")
    if stored_lineage_id is not None and str(stored_lineage_id) != trace.trace_lineage_id:
        raise ValueError(
            "persisted trace_lineage_id does not match reconstructed lineage"
        )
    return trace


class TraceVersionLedger:
    """Local deterministic version ledger preventing silent trace forks."""

    def __init__(self) -> None:
        self._history: dict[str, list[MemoryTrace]] = {}

    def register_initial(self, trace: MemoryTrace) -> None:
        if not isinstance(trace, MemoryTrace):
            raise TypeError("trace must be MemoryTrace")
        if trace.version != 0:
            raise ValueError("initial trace version must be 0")
        if trace.parent_trace_id is not None:
            raise ValueError("initial trace cannot have a parent")
        if trace.reconsolidation_decision_fingerprint is not None:
            raise ValueError("initial trace cannot have a reconsolidation decision")
        if trace.reconsolidation_event_id is not None:
            raise ValueError("initial trace cannot have a reconsolidation event")
        if trace.trace_lineage_id in self._history:
            raise ValueError("trace lineage is already registered")
        self._history[trace.trace_lineage_id] = [trace]

    def append_successor(
        self,
        *,
        parent: MemoryTrace,
        successor: MemoryTrace,
    ) -> None:
        if not isinstance(parent, MemoryTrace) or not isinstance(successor, MemoryTrace):
            raise TypeError("parent and successor must be MemoryTrace")
        history = self._history.get(parent.trace_lineage_id)
        if not history:
            raise ValueError("parent trace lineage is not registered")
        latest = history[-1]
        if latest.trace_id != parent.trace_id:
            raise ValueError("silent fork rejected: parent is not the latest snapshot")
        if successor.trace_lineage_id != parent.trace_lineage_id:
            raise ValueError("successor lineage mismatch")
        if successor.version != parent.version + 1:
            raise ValueError("successor version must increment exactly once")
        if successor.parent_trace_id != parent.trace_id:
            raise ValueError("successor must name the exact parent trace")
        if successor.protected_evidence != parent.protected_evidence:
            raise ValueError("successor protected evidence must remain identical")
        if successor.reconsolidation_decision_fingerprint is None:
            raise ValueError("successor requires reconsolidation decision lineage")
        if successor.reconsolidation_event_id is None:
            raise ValueError("successor requires recollection event lineage")
        if any(item.version == successor.version for item in history):
            raise ValueError("duplicate trace version rejected")
        history.append(successor)

    def history(self, trace_lineage_id: str) -> tuple[MemoryTrace, ...]:
        if trace_lineage_id not in self._history:
            raise KeyError(trace_lineage_id)
        return tuple(self._history[trace_lineage_id])

    def latest(self, trace_lineage_id: str) -> MemoryTrace:
        return self.history(trace_lineage_id)[-1]

    def stable_json(self) -> str:
        traces = [
            asdict(trace)
            for lineage in sorted(self._history)
            for trace in self._history[lineage]
        ]
        return _stable_json(
            {
                "schema_version": _LEDGER_SCHEMA_VERSION,
                "traces": traces,
            }
        )

    @classmethod
    def from_json(cls, payload: str) -> "TraceVersionLedger":
        if not isinstance(payload, str) or not payload.strip():
            raise ValueError("ledger payload is required")
        decoded = json.loads(payload)
        if decoded.get("schema_version") != _LEDGER_SCHEMA_VERSION:
            raise ValueError("unsupported trace ledger schema version")
        ledger = cls()
        for raw in decoded.get("traces", []):
            trace = _memory_trace_from_dict(raw)
            if trace.version == 0:
                ledger.register_initial(trace)
            else:
                history = ledger._history.get(trace.trace_lineage_id)
                if not history:
                    raise ValueError("successor encountered before initial trace")
                ledger.append_successor(parent=history[-1], successor=trace)
        return ledger

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.stable_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "TraceVersionLedger":
        return cls.from_json(Path(path).read_text(encoding="utf-8"))


def reconsolidate_and_record(
    *,
    ledger: TraceVersionLedger,
    old_trace: MemoryTrace,
    candidate: RecollectionCandidate,
    source_decision: SourceMonitoringDecision,
    recollection_event: PhenomenalEvent,
    context: ReconsolidationContext,
    policy: ReconsolidationPolicy | None = None,
) -> tuple[ReconsolidationDecision, MemoryTrace | None]:
    """Evaluate, apply, and append one reconsolidation operation atomically in API terms."""

    if not isinstance(ledger, TraceVersionLedger):
        raise TypeError("ledger must be TraceVersionLedger")
    decision = evaluate_reconsolidation(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        recollection_event=recollection_event,
        context=context,
        policy=policy,
    )
    successor = apply_reconsolidation(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        recollection_event=recollection_event,
        decision=decision,
    )
    if successor is not None:
        ledger.append_successor(parent=old_trace, successor=successor)
    return decision, successor
