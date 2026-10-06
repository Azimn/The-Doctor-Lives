"""P6 versioned reconsolidation for UPPB.

P6 evolves memory by producing immutable successor MemoryTrace snapshots after
verified recollection and awareness. It never mutates an existing trace.

P6A changes only bounded trace-level strength/accessibility/familiarity and
retrieval/rehearsal counters. P6B adds separately audited accessibility drift
for existing retained details that were omitted by the exact P4 recollection.
P6C adds separately gated temporal-confidence and contextual-association drift
for psychologically meaningful omission causes. P6D adds a factory-controlled
subjective temporal-generalization representation while preserving stable
TraceDetail semantic truth. Novel propositions, donor substitution, and
free-form constructive distortion remain outside this module's active gate.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

from .awareness import AwarenessDecision
from .distortion import (
    DistortionCandidate,
    DistortionKind,
    RepresentationOperation,
    build_representation_operation,
    propose_temporal_generalization,
    verify_distortion_candidate,
)
from .phenomenology import (
    AwarenessLevel,
    CertaintyBand,
    PhenomenalEvent,
    PhenomenalMode,
)
from .recollection import (
    MemoryTrace,
    OmissionCause,
    ProtectedEvidenceRef,
    RecollectionCandidate,
    SubjectiveDetailRepresentation,
    SubjectiveTemporalForm,
    TemporalPrecision,
    TemporalSemantics,
    _make_subjective_detail_representation,
    TraceDetail,
    TraceDetailState,
)
from .source_monitoring import (
    FinalizedRecollection,
    SourceMonitoringDecision,
    verify_finalized_recollection,
)


_RECONSOLIDATION_DECISION_FACTORY_TOKEN = object()
_LEDGER_SCHEMA_VERSION = "uppb-p6d-ledger-v6"
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


def _json_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"persisted {name} must be an integer")
    return value


def _json_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"persisted {name} must be numeric")
    normalized = float(value)
    if not math.isfinite(normalized):
        raise ValueError(f"persisted {name} must be finite")
    return normalized


@dataclass(frozen=True)
class ReconsolidationContext:
    """Engineer-visible reactivation context for one possible trace update."""

    enabled: bool = True
    reactivation_strength: float = 0.5
    prediction_error: float = 0.0
    emotional_activation: float = 0.0
    goal_relevance: float = 0.0
    explicit_rehearsal: bool = False
    detail_drift_enabled: bool = False
    interference_strength: float = 0.0
    temporal_drift_enabled: bool = False
    temporal_disorientation: float = 0.0
    association_drift_enabled: bool = False
    context_mismatch: float = 0.0
    temporal_generalization_enabled: bool = False
    rule_version: str = "uppb-p6d-v2"

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be bool")
        if not isinstance(self.explicit_rehearsal, bool):
            raise TypeError("explicit_rehearsal must be bool")
        if not isinstance(self.detail_drift_enabled, bool):
            raise TypeError("detail_drift_enabled must be bool")
        if not isinstance(self.temporal_drift_enabled, bool):
            raise TypeError("temporal_drift_enabled must be bool")
        if not isinstance(self.association_drift_enabled, bool):
            raise TypeError("association_drift_enabled must be bool")
        if not isinstance(self.temporal_generalization_enabled, bool):
            raise TypeError("temporal_generalization_enabled must be bool")
        for name in (
            "reactivation_strength",
            "prediction_error",
            "emotional_activation",
            "goal_relevance",
            "interference_strength",
            "temporal_disorientation",
            "context_mismatch",
        ):
            object.__setattr__(self, name, _unit(getattr(self, name), name))
        if not isinstance(self.rule_version, str) or not self.rule_version.strip():
            raise ValueError("rule_version is required")

    @property
    def fingerprint(self) -> str:
        return _stable_sha256(asdict(self))


@dataclass(frozen=True)
class ReconsolidationPolicy:
    """Bounded P6A-P6D plasticity policy.

    P6D may transform only a separate subjective temporal representation.
    Stable TraceDetail semantic truth and retention remain read-only.
    """

    min_reactivation: float = 0.35
    min_prediction_error: float = 0.15
    min_emotional_activation: float = 0.40
    max_strength_delta: float = 0.02
    max_accessibility_delta: float = 0.04
    max_familiarity_delta: float = 0.03
    strength_ceiling: float = 0.95
    accessibility_ceiling: float = 0.98
    familiarity_ceiling: float = 0.98
    min_detail_interference: float = 0.35
    max_detail_accessibility_loss: float = 0.12
    detail_accessibility_floor: float = 0.05
    min_temporal_disorientation: float = 0.35
    max_temporal_confidence_loss: float = 0.10
    temporal_confidence_floor: float = 0.20
    min_context_mismatch: float = 0.35
    max_association_strength_loss: float = 0.10
    association_strength_floor: float = 0.20
    max_temporal_confidence_for_generalization: float = 0.35

    def __post_init__(self) -> None:
        for name in (
            "min_reactivation",
            "min_prediction_error",
            "min_emotional_activation",
            "max_strength_delta",
            "max_accessibility_delta",
            "max_familiarity_delta",
        ):
            object.__setattr__(
                self,
                name,
                _positive_unit(getattr(self, name), name),
            )
        for name in (
            "strength_ceiling",
            "accessibility_ceiling",
            "familiarity_ceiling",
            "min_detail_interference",
            "max_detail_accessibility_loss",
            "detail_accessibility_floor",
            "min_temporal_disorientation",
            "max_temporal_confidence_loss",
            "temporal_confidence_floor",
            "min_context_mismatch",
            "max_association_strength_loss",
            "association_strength_floor",
            "max_temporal_confidence_for_generalization",
        ):
            object.__setattr__(self, name, _unit(getattr(self, name), name))

    @property
    def fingerprint(self) -> str:
        return _stable_sha256(asdict(self))


@dataclass(frozen=True)
class DetailStateOperation:
    """One explicit bounded P6B/P6C change to a retained detail's mnemonic state."""

    detail_id: str
    field_name: str
    old_value: float
    new_value: float
    delta: float
    old_state_fingerprint: str
    new_state_fingerprint: str
    reason_code: str

    def __post_init__(self) -> None:
        if not isinstance(self.detail_id, str) or not self.detail_id.strip():
            raise ValueError("detail_id is required")
        if self.field_name not in {
            "accessibility",
            "temporal_confidence",
            "association_strength",
        }:
            raise ValueError("unsupported detail-state operation field")
        for name in ("old_value", "new_value"):
            object.__setattr__(self, name, _unit(getattr(self, name), name))
        if isinstance(self.delta, bool) or not isinstance(self.delta, (int, float)):
            raise TypeError("delta must be numeric")
        if not math.isfinite(float(self.delta)):
            raise ValueError("delta must be finite")
        object.__setattr__(self, "delta", float(self.delta))
        if abs((self.new_value - self.old_value) - self.delta) > 1e-12:
            raise ValueError("delta must equal new_value - old_value")
        if self.delta > 0.0:
            raise ValueError("P6 detail-state degradation may only weaken")
        for name in ("old_state_fingerprint", "new_state_fingerprint", "reason_code"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")

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
    finalized_recollection_fingerprint: str
    recollection_event_id: str
    recollection_event_lineage_fingerprint: str
    recollection_awareness: AwarenessLevel
    awareness_priority: float
    context: ReconsolidationContext
    context_fingerprint: str
    policy: ReconsolidationPolicy
    policy_fingerprint: str
    eligible: bool
    eligibility_strength: float
    operations: tuple[ReconsolidationOperation, ...]
    detail_operations: tuple[DetailStateOperation, ...]
    detail_reason_codes: tuple[str, ...]
    distortion_candidates: tuple[DistortionCandidate, ...]
    representation_operations: tuple[RepresentationOperation, ...]
    distortion_reason_codes: tuple[str, ...]
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
    finalized_recollection: FinalizedRecollection,
    awareness_decision: AwarenessDecision,
) -> PhenomenalEvent:
    if not isinstance(old_trace, MemoryTrace):
        raise TypeError("old_trace must be MemoryTrace")
    if not isinstance(candidate, RecollectionCandidate):
        raise TypeError("candidate must be RecollectionCandidate")
    if not isinstance(source_decision, SourceMonitoringDecision):
        raise TypeError("source_decision must be SourceMonitoringDecision")
    if not isinstance(finalized_recollection, FinalizedRecollection):
        raise TypeError(
            "finalized_recollection must be the P5 FinalizedRecollection output"
        )
    verify_finalized_recollection(
        finalized=finalized_recollection,
        candidate=candidate,
        decision=source_decision,
    )
    if not isinstance(awareness_decision, AwarenessDecision):
        raise TypeError(
            "awareness_decision must be the P3 AwarenessDecision output"
        )
    recollection_event = awareness_decision.event
    if not isinstance(recollection_event, PhenomenalEvent):
        raise TypeError("awareness decision event must be PhenomenalEvent")
    canonical_latent_event = finalized_recollection.event
    if replace(
        recollection_event,
        awareness=AwarenessLevel.LATENT,
    ) != canonical_latent_event:
        raise ValueError(
            "P3 awareness decision did not route the canonical P5 finalized recollection"
        )
    if isinstance(awareness_decision.priority, bool) or not isinstance(
        awareness_decision.priority, (int, float)
    ):
        raise TypeError("awareness decision priority must be numeric")
    if not math.isfinite(float(awareness_decision.priority)):
        raise ValueError("awareness decision priority must be finite")
    if not 0.0 <= float(awareness_decision.priority) <= 1.0:
        raise ValueError("awareness decision priority must be between 0 and 1")

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
    return recollection_event


def _bounded_delta(
    current: float,
    *,
    ceiling: float,
    max_delta: float,
    drive: float,
) -> float:
    remaining = max(0.0, ceiling - current)
    return min(max_delta, remaining * 0.25 * drive)


def _bounded_loss(
    current: float,
    *,
    floor: float,
    max_loss: float,
    drive: float,
) -> float:
    available = max(0.0, current - floor)
    return min(max_loss, available * 0.25 * drive)


def _degrade_detail_state(
    state: TraceDetailState,
    *,
    field_name: str,
    loss: float,
    reason_code: str,
) -> tuple[DetailStateOperation, TraceDetailState]:
    if field_name not in {
        "accessibility",
        "temporal_confidence",
        "association_strength",
    }:
        raise ValueError("unsupported detail-state degradation field")
    if loss < 0.0:
        raise ValueError("detail-state loss cannot be negative")
    old_value = float(getattr(state, field_name))
    new_value = max(0.0, old_value - float(loss))
    kwargs = {
        "detail_id": state.detail_id,
        "retention": state.retention,
        "accessibility": state.accessibility,
        "temporal_confidence": state.temporal_confidence,
        "association_strength": state.association_strength,
        "parent_state_fingerprint": state.state_fingerprint,
    }
    kwargs[field_name] = new_value
    successor = TraceDetailState(**kwargs)
    operation = DetailStateOperation(
        detail_id=state.detail_id,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        delta=new_value - old_value,
        old_state_fingerprint=state.state_fingerprint,
        new_state_fingerprint=successor.state_fingerprint,
        reason_code=reason_code,
    )
    return operation, successor


def _decision_payload(
    *,
    old_trace: MemoryTrace,
    candidate: RecollectionCandidate,
    source_decision: SourceMonitoringDecision,
    finalized_recollection: FinalizedRecollection,
    awareness_decision: AwarenessDecision,
    context: ReconsolidationContext,
    policy: ReconsolidationPolicy,
    eligible: bool,
    eligibility_strength: float,
    operations: tuple[ReconsolidationOperation, ...],
    detail_operations: tuple[DetailStateOperation, ...],
    detail_reason_codes: tuple[str, ...],
    distortion_candidates: tuple[DistortionCandidate, ...],
    representation_operations: tuple[RepresentationOperation, ...],
    distortion_reason_codes: tuple[str, ...],
    reason_codes: tuple[str, ...],
) -> dict[str, Any]:
    recollection_event = awareness_decision.event
    return {
        "old_trace_id": old_trace.trace_id,
        "old_trace_digest": old_trace.snapshot_digest,
        "trace_lineage_id": old_trace.trace_lineage_id,
        "old_version": old_trace.version,
        "candidate_id": candidate.candidate_id,
        "candidate_digest": candidate.candidate_digest,
        "source_decision_fingerprint": source_decision.decision_fingerprint,
        "finalized_recollection_fingerprint": (
            finalized_recollection.finalization_fingerprint
        ),
        "recollection_event_id": recollection_event.event_id,
        "recollection_event_lineage_fingerprint": recollection_event.lineage_fingerprint,
        "recollection_awareness": recollection_event.awareness.value,
        "awareness_priority": float(awareness_decision.priority),
        "context": asdict(context),
        "context_fingerprint": context.fingerprint,
        "policy": asdict(policy),
        "policy_fingerprint": policy.fingerprint,
        "eligible": eligible,
        "eligibility_strength": eligibility_strength,
        "operations": [asdict(op) for op in operations],
        "detail_operations": [asdict(op) for op in detail_operations],
        "detail_reason_codes": detail_reason_codes,
        "distortion_candidates": [
            asdict(item) for item in distortion_candidates
        ],
        "representation_operations": [
            asdict(item) for item in representation_operations
        ],
        "distortion_reason_codes": distortion_reason_codes,
        "reason_codes": reason_codes,
    }


def evaluate_reconsolidation(
    *,
    old_trace: MemoryTrace,
    candidate: RecollectionCandidate,
    source_decision: SourceMonitoringDecision,
    finalized_recollection: FinalizedRecollection,
    awareness_decision: AwarenessDecision,
    context: ReconsolidationContext,
    policy: ReconsolidationPolicy | None = None,
) -> ReconsolidationDecision:
    """Evaluate eligibility and bounded update operations without mutating state."""

    policy = policy or ReconsolidationPolicy()
    if not isinstance(context, ReconsolidationContext):
        raise TypeError("context must be ReconsolidationContext")
    if not isinstance(policy, ReconsolidationPolicy):
        raise TypeError("policy must be ReconsolidationPolicy")

    recollection_event = _validate_upstream_chain(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        finalized_recollection=finalized_recollection,
        awareness_decision=awareness_decision,
    )

    reasons: list[str] = []
    if not context.enabled:
        reasons.append("reconsolidation_disabled")
    if recollection_event.awareness not in {
        AwarenessLevel.CONSCIOUS,
        AwarenessLevel.FOCAL,
    }:
        reasons.append("recollection_not_consciously_accessible")
    if recollection_event.subjective_certainty is not CertaintyBand.MODERATE:
        reasons.append("nonneutral_content_certainty_not_grounded_for_p6")
    if candidate.blended:
        reasons.append("blended_recollection_not_enabled")
    if len(candidate.trace_ids) != 1:
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

    detail_operations: list[DetailStateOperation] = []
    detail_reasons: list[str] = []
    current_detail_states = {
        state.detail_id: state for state in old_trace.detail_states
    }
    omission_by_ref = {
        item.detail_ref: item for item in candidate.detail_omissions
    }

    # P6B: accepted accessibility weakening remains intentionally broad over
    # exact P4 omissions, regardless of why the detail was omitted.
    if not context.detail_drift_enabled:
        detail_reasons.append("detail_drift_disabled")
    elif not eligible:
        detail_reasons.append("base_reconsolidation_ineligible")
    elif context.interference_strength < policy.min_detail_interference:
        detail_reasons.append("detail_interference_below_threshold")
    else:
        for old_state in old_trace.detail_states:
            detail_ref = f"{old_trace.trace_id}:{old_state.detail_id}"
            if detail_ref not in omission_by_ref:
                continue
            current_state = current_detail_states[old_state.detail_id]
            loss = _bounded_loss(
                current_state.accessibility,
                floor=policy.detail_accessibility_floor,
                max_loss=policy.max_detail_accessibility_loss,
                drive=context.interference_strength,
            )
            if loss <= 0.0:
                continue
            operation, new_state = _degrade_detail_state(
                current_state,
                field_name="accessibility",
                loss=loss,
                reason_code="omitted_detail_interference_weakening",
            )
            detail_operations.append(operation)
            current_detail_states[old_state.detail_id] = new_state
        if any(op.field_name == "accessibility" for op in detail_operations):
            detail_reasons.append("omitted_detail_accessibility_weakened")
        else:
            detail_reasons.append("no_eligible_omitted_detail")

    # P6C: richer degradation explicitly distinguishes omission causes. A
    # capacity-limited detail was retrievable but lost the reconstruction
    # contest, so max_details alone cannot silently degrade temporal/contextual
    # precision.
    richer_omissions = tuple(
        item
        for item in candidate.detail_omissions
        if item.cause is not OmissionCause.CAPACITY_LIMITED
    )
    if any(
        item.cause is OmissionCause.CAPACITY_LIMITED
        for item in candidate.detail_omissions
    ):
        detail_reasons.append("capacity_limited_omission_excluded_from_p6c")

    if not context.temporal_drift_enabled:
        detail_reasons.append("temporal_drift_disabled")
    elif not eligible:
        detail_reasons.append("temporal_base_reconsolidation_ineligible")
    elif context.temporal_disorientation < policy.min_temporal_disorientation:
        detail_reasons.append("temporal_disorientation_below_threshold")
    else:
        temporal_changed = False
        for omission in richer_omissions:
            prefix = old_trace.trace_id + ":"
            if not omission.detail_ref.startswith(prefix):
                continue
            detail_id = omission.detail_ref[len(prefix):]
            current_state = current_detail_states[detail_id]
            loss = _bounded_loss(
                current_state.temporal_confidence,
                floor=policy.temporal_confidence_floor,
                max_loss=policy.max_temporal_confidence_loss,
                drive=context.temporal_disorientation,
            )
            if loss <= 0.0:
                continue
            operation, new_state = _degrade_detail_state(
                current_state,
                field_name="temporal_confidence",
                loss=loss,
                reason_code=(
                    "temporal_disorientation_after_"
                    + omission.cause.value
                ),
            )
            detail_operations.append(operation)
            current_detail_states[detail_id] = new_state
            temporal_changed = True
        detail_reasons.append(
            "omitted_detail_temporal_confidence_weakened"
            if temporal_changed
            else "no_p6c_temporal_target"
        )

    if not context.association_drift_enabled:
        detail_reasons.append("association_drift_disabled")
    elif not eligible:
        detail_reasons.append("association_base_reconsolidation_ineligible")
    elif context.context_mismatch < policy.min_context_mismatch:
        detail_reasons.append("context_mismatch_below_threshold")
    else:
        association_changed = False
        for omission in richer_omissions:
            prefix = old_trace.trace_id + ":"
            if not omission.detail_ref.startswith(prefix):
                continue
            detail_id = omission.detail_ref[len(prefix):]
            current_state = current_detail_states[detail_id]
            loss = _bounded_loss(
                current_state.association_strength,
                floor=policy.association_strength_floor,
                max_loss=policy.max_association_strength_loss,
                drive=context.context_mismatch,
            )
            if loss <= 0.0:
                continue
            operation, new_state = _degrade_detail_state(
                current_state,
                field_name="association_strength",
                loss=loss,
                reason_code=(
                    "context_mismatch_after_"
                    + omission.cause.value
                ),
            )
            detail_operations.append(operation)
            current_detail_states[detail_id] = new_state
            association_changed = True
        detail_reasons.append(
            "omitted_detail_association_weakened"
            if association_changed
            else "no_p6c_association_target"
        )

    distortion_candidates: list[DistortionCandidate] = []
    representation_operations: list[RepresentationOperation] = []
    distortion_reasons: list[str] = []

    # P6D: structured content generalization is downstream of an actually
    # recalled, consciously processed P4/P5/P3 chain. It does not use source
    # attribution or omission cause as a driver.
    if not context.temporal_generalization_enabled:
        distortion_reasons.append("temporal_generalization_disabled")
    elif not eligible:
        distortion_reasons.append(
            "base_reconsolidation_ineligible_for_distortion"
        )
    else:
        for detail in old_trace.details:
            proposal = propose_temporal_generalization(
                old_trace=old_trace,
                candidate=candidate,
                detail_id=detail.detail_id,
                max_temporal_confidence=(
                    policy.max_temporal_confidence_for_generalization
                ),
            )
            if proposal is None:
                continue
            operation, _ = build_representation_operation(
                old_trace=old_trace,
                distortion=proposal,
            )
            distortion_candidates.append(proposal)
            representation_operations.append(operation)
        distortion_reasons.append(
            "temporal_generalization_proposed"
            if distortion_candidates
            else "no_p6d_temporal_generalization_target"
        )

    operations_tuple = tuple(operations)
    detail_operations_tuple = tuple(detail_operations)
    detail_reasons_tuple = tuple(detail_reasons)
    distortion_candidates_tuple = tuple(distortion_candidates)
    representation_operations_tuple = tuple(representation_operations)
    distortion_reasons_tuple = tuple(distortion_reasons)
    reasons_tuple = tuple(reasons)
    payload = _decision_payload(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        finalized_recollection=finalized_recollection,
        awareness_decision=awareness_decision,
        context=context,
        policy=policy,
        eligible=eligible,
        eligibility_strength=drive,
        operations=operations_tuple,
        detail_operations=detail_operations_tuple,
        detail_reason_codes=detail_reasons_tuple,
        distortion_candidates=distortion_candidates_tuple,
        representation_operations=representation_operations_tuple,
        distortion_reason_codes=distortion_reasons_tuple,
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
        (
            "finalized_recollection_fingerprint",
            finalized_recollection.finalization_fingerprint,
        ),
        ("recollection_event_id", recollection_event.event_id),
        (
            "recollection_event_lineage_fingerprint",
            recollection_event.lineage_fingerprint,
        ),
        ("recollection_awareness", recollection_event.awareness),
        ("awareness_priority", float(awareness_decision.priority)),
        ("context", context),
        ("context_fingerprint", context.fingerprint),
        ("policy", policy),
        ("policy_fingerprint", policy.fingerprint),
        ("eligible", eligible),
        ("eligibility_strength", drive),
        ("operations", operations_tuple),
        ("detail_operations", detail_operations_tuple),
        ("detail_reason_codes", detail_reasons_tuple),
        ("distortion_candidates", distortion_candidates_tuple),
        ("representation_operations", representation_operations_tuple),
        ("distortion_reason_codes", distortion_reasons_tuple),
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
    finalized_recollection: FinalizedRecollection,
    awareness_decision: AwarenessDecision,
    decision: ReconsolidationDecision,
) -> None:
    if not isinstance(decision, ReconsolidationDecision):
        raise TypeError("decision must be ReconsolidationDecision")
    recollection_event = _validate_upstream_chain(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        finalized_recollection=finalized_recollection,
        awareness_decision=awareness_decision,
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
    if (
        decision.finalized_recollection_fingerprint
        != finalized_recollection.finalization_fingerprint
    ):
        raise ValueError("reconsolidation decision P5 finalization mismatch")
    if decision.recollection_event_id != recollection_event.event_id:
        raise ValueError("reconsolidation decision event ID mismatch")
    if (
        decision.recollection_event_lineage_fingerprint
        != recollection_event.lineage_fingerprint
    ):
        raise ValueError("reconsolidation decision event lineage mismatch")
    if decision.recollection_awareness is not recollection_event.awareness:
        raise ValueError("reconsolidation decision awareness mismatch")
    if abs(decision.awareness_priority - float(awareness_decision.priority)) > 1e-12:
        raise ValueError("reconsolidation decision awareness priority mismatch")
    if decision.context_fingerprint != decision.context.fingerprint:
        raise ValueError("reconsolidation context fingerprint mismatch")
    if decision.policy_fingerprint != decision.policy.fingerprint:
        raise ValueError("reconsolidation policy fingerprint mismatch")

    if len(decision.distortion_candidates) != len(
        decision.representation_operations
    ):
        raise ValueError("distortion candidate/operation count mismatch")
    for distortion, operation in zip(
        decision.distortion_candidates,
        decision.representation_operations,
    ):
        verify_distortion_candidate(distortion)
        if distortion.p4_candidate_id != candidate.candidate_id:
            raise ValueError("distortion candidate P4 ID mismatch")
        if distortion.p4_candidate_digest != candidate.candidate_digest:
            raise ValueError("distortion candidate P4 digest mismatch")
        if (
            distortion.max_temporal_confidence_threshold
            != decision.policy.max_temporal_confidence_for_generalization
        ):
            raise ValueError("distortion candidate policy threshold mismatch")
        if (
            distortion.recalled_temporal_precision
            is not TemporalPrecision.UNCERTAIN
        ):
            raise ValueError("distortion candidate recall precision mismatch")
        if (
            distortion.recalled_representation_fingerprint
            != distortion.parent_representation_fingerprint
        ):
            raise ValueError("distortion candidate recalled representation mismatch")
        expected_operation, _ = build_representation_operation(
            old_trace=old_trace,
            distortion=distortion,
        )
        if operation != expected_operation:
            raise ValueError("representation operation does not match distortion")

    payload = _decision_payload(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        finalized_recollection=finalized_recollection,
        awareness_decision=awareness_decision,
        context=decision.context,
        policy=decision.policy,
        eligible=decision.eligible,
        eligibility_strength=decision.eligibility_strength,
        operations=decision.operations,
        detail_operations=decision.detail_operations,
        detail_reason_codes=decision.detail_reason_codes,
        distortion_candidates=decision.distortion_candidates,
        representation_operations=decision.representation_operations,
        distortion_reason_codes=decision.distortion_reason_codes,
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
    finalized_recollection: FinalizedRecollection,
    awareness_decision: AwarenessDecision,
    decision: ReconsolidationDecision,
) -> MemoryTrace | None:
    """Create an immutable successor trace when the verified decision is eligible."""

    _verify_decision_integrity(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        finalized_recollection=finalized_recollection,
        awareness_decision=awareness_decision,
        decision=decision,
    )
    recollection_event = awareness_decision.event
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

    detail_states = list(old_trace.detail_states)
    detail_index = {
        state.detail_id: index for index, state in enumerate(detail_states)
    }
    seen_detail_operations: set[tuple[str, str]] = set()
    for operation in decision.detail_operations:
        operation_key = (operation.detail_id, operation.field_name)
        if operation_key in seen_detail_operations:
            raise ValueError("duplicate detail-state field operation")
        seen_detail_operations.add(operation_key)
        if operation.detail_id not in detail_index:
            raise ValueError("detail-state operation references unknown detail")
        index = detail_index[operation.detail_id]
        old_state = detail_states[index]
        if old_state.state_fingerprint != operation.old_state_fingerprint:
            raise ValueError("detail-state operation old fingerprint mismatch")
        if abs(float(getattr(old_state, operation.field_name)) - operation.old_value) > 1e-12:
            raise ValueError("detail-state operation old value mismatch")
        kwargs = {
            "detail_id": old_state.detail_id,
            "retention": old_state.retention,
            "accessibility": old_state.accessibility,
            "temporal_confidence": old_state.temporal_confidence,
            "association_strength": old_state.association_strength,
            "parent_state_fingerprint": old_state.state_fingerprint,
        }
        kwargs[operation.field_name] = operation.new_value
        new_state = TraceDetailState(**kwargs)
        if new_state.state_fingerprint != operation.new_state_fingerprint:
            raise ValueError("detail-state operation new fingerprint mismatch")
        detail_states[index] = new_state

    subjective_representations = list(
        old_trace.subjective_representations
    )
    representation_index = {
        item.detail_id: index
        for index, item in enumerate(subjective_representations)
    }
    distortion_by_fingerprint = {
        item.distortion_fingerprint: item
        for item in decision.distortion_candidates
    }
    seen_representation_details: set[str] = set()
    for operation in decision.representation_operations:
        if operation.detail_id in seen_representation_details:
            raise ValueError("duplicate subjective-representation operation")
        seen_representation_details.add(operation.detail_id)
        if operation.detail_id not in representation_index:
            raise ValueError(
                "subjective-representation operation references unknown detail"
            )
        distortion = distortion_by_fingerprint.get(
            operation.distortion_candidate_fingerprint
        )
        if distortion is None:
            raise ValueError(
                "representation operation lacks distortion candidate"
            )
        expected_operation, new_representation = (
            build_representation_operation(
                old_trace=old_trace,
                distortion=distortion,
            )
        )
        if expected_operation != operation:
            raise ValueError(
                "representation operation does not match reviewed distortion"
            )
        index = representation_index[operation.detail_id]
        if (
            subjective_representations[index].representation_fingerprint
            != operation.old_representation_fingerprint
        ):
            raise ValueError(
                "representation operation old fingerprint mismatch"
            )
        subjective_representations[index] = new_representation

    successor = MemoryTrace(
        subject_id=old_trace.subject_id,
        version=old_trace.version + 1,
        protected_evidence=old_trace.protected_evidence,
        gist=old_trace.gist,
        details=old_trace.details,
        detail_states=tuple(detail_states),
        subjective_representations=tuple(subjective_representations),
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
        raise AssertionError("P6 may not rewrite gist or retained details")
    return successor


def _memory_trace_from_dict(data: dict[str, Any]) -> MemoryTrace:
    protected = tuple(
        ProtectedEvidenceRef(
            evidence_id=str(item["evidence_id"]),
            digest=str(item["digest"]),
        )
        for item in data["protected_evidence"]
    )
    parsed_details: list[TraceDetail] = []
    for item in data.get("details", ()):
        raw_temporal = item.get("temporal_semantics")
        temporal_semantics = None
        if raw_temporal is not None:
            if not isinstance(raw_temporal, dict):
                raise ValueError(
                    "persisted temporal_semantics must be an object"
                )
            temporal_semantics = TemporalSemantics(
                exact_phrase=str(raw_temporal["exact_phrase"]),
                generalized_phrase=str(
                    raw_temporal["generalized_phrase"]
                ),
            )
        parsed_details.append(
            TraceDetail(
                detail_id=str(item["detail_id"]),
                text=str(item["text"]),
                cue_terms=tuple(item.get("cue_terms", ())),
                temporal_semantics=temporal_semantics,
                temporal_template=_optional_nonblank(
                    item.get("temporal_template"),
                    "detail temporal_template",
                ),
            )
        )
    details = tuple(parsed_details)
    raw_detail_states = data.get("detail_states")
    if details and not isinstance(raw_detail_states, list):
        raise ValueError("persisted detail_states are required for traces with details")
    if raw_detail_states is None:
        raw_detail_states = []
    if not isinstance(raw_detail_states, list):
        raise ValueError("persisted detail_states must be a list")

    parsed_detail_states: list[TraceDetailState] = []
    for item in raw_detail_states:
        if not isinstance(item, dict):
            raise ValueError("persisted detail state must be an object")
        state = TraceDetailState(
            detail_id=str(item["detail_id"]),
            retention=_json_number(item.get("retention", 1.0), "detail retention"),
            accessibility=_json_number(
                item.get("accessibility", 1.0),
                "detail accessibility",
            ),
            temporal_confidence=_json_number(
                item.get("temporal_confidence", 1.0),
                "detail temporal_confidence",
            ),
            association_strength=_json_number(
                item.get("association_strength", 1.0),
                "detail association_strength",
            ),
            parent_state_fingerprint=_optional_nonblank(
                item.get("parent_state_fingerprint"),
                "detail parent_state_fingerprint",
            ),
        )
        persisted_availability = item.get("availability_state")
        if persisted_availability != state.availability_state.value:
            raise ValueError("persisted detail availability state is inconsistent")
        persisted_fingerprint = item.get("state_fingerprint")
        if persisted_fingerprint != state.state_fingerprint:
            raise ValueError("persisted detail state fingerprint is inconsistent")
        parsed_detail_states.append(state)
    detail_states = tuple(parsed_detail_states)

    raw_representations = data.get("subjective_representations")
    if details and not isinstance(raw_representations, list):
        raise ValueError(
            "persisted subjective_representations are required for traces with details"
        )
    if raw_representations is None:
        raw_representations = []
    if not isinstance(raw_representations, list):
        raise ValueError("persisted subjective_representations must be a list")
    parsed_representations: list[SubjectiveDetailRepresentation] = []
    for item in raw_representations:
        if not isinstance(item, dict):
            raise ValueError(
                "persisted subjective representation must be an object"
            )
        representation = _make_subjective_detail_representation(
            detail_id=str(item["detail_id"]),
            temporal_form=SubjectiveTemporalForm(
                str(item.get("temporal_form", "exact"))
            ),
            parent_representation_fingerprint=_optional_nonblank(
                item.get("parent_representation_fingerprint"),
                "representation parent fingerprint",
            ),
            distortion_candidate_fingerprint=_optional_nonblank(
                item.get("distortion_candidate_fingerprint"),
                "representation distortion fingerprint",
            ),
        )
        if (
            item.get("representation_fingerprint")
            != representation.representation_fingerprint
        ):
            raise ValueError(
                "persisted subjective representation fingerprint is inconsistent"
            )
        parsed_representations.append(representation)
    subjective_representations = tuple(parsed_representations)

    subject_id = data.get("subject_id")
    gist = data.get("gist")
    if not isinstance(subject_id, str) or not subject_id.strip():
        raise ValueError("persisted subject_id must be a non-blank string")
    if not isinstance(gist, str) or not gist.strip():
        raise ValueError("persisted gist must be a non-blank string")

    trace = MemoryTrace(
        subject_id=subject_id,
        version=_json_int(data.get("version"), "version"),
        protected_evidence=protected,
        gist=gist,
        details=details,
        detail_states=detail_states,
        subjective_representations=subjective_representations,
        temporal_cues=tuple(data.get("temporal_cues", ())),
        actor_refs=tuple(data.get("actor_refs", ())),
        object_refs=tuple(data.get("object_refs", ())),
        encoding_affect=tuple(data.get("encoding_affect", ())),
        source_cues=tuple(data.get("source_cues", ())),
        strength=_json_number(data.get("strength", 0.5), "strength"),
        accessibility=_json_number(
            data.get("accessibility", 0.5),
            "accessibility",
        ),
        familiarity=_json_number(data.get("familiarity", 0.5), "familiarity"),
        rehearsal_count=_json_int(
            data.get("rehearsal_count", 0),
            "rehearsal_count",
        ),
        retrieval_count=_json_int(
            data.get("retrieval_count", 0),
            "retrieval_count",
        ),
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
    if not isinstance(stored_trace_id, str) or not stored_trace_id.strip():
        raise ValueError("persisted trace_id is required")
    if not isinstance(stored_lineage_id, str) or not stored_lineage_id.strip():
        raise ValueError("persisted trace_lineage_id is required")
    if stored_trace_id != trace.trace_id:
        raise ValueError("persisted trace_id does not match reconstructed snapshot")
    if stored_lineage_id != trace.trace_lineage_id:
        raise ValueError(
            "persisted trace_lineage_id does not match reconstructed lineage"
        )
    return trace


def _verify_serialized_decision_audit(audit: dict[str, Any]) -> None:
    if not isinstance(audit, dict):
        raise TypeError("decision audit must be an object")
    fingerprint = audit.get("decision_fingerprint")
    if not isinstance(fingerprint, str) or not fingerprint.strip():
        raise ValueError("decision audit fingerprint is required")
    finalization_fingerprint = audit.get("finalized_recollection_fingerprint")
    if (
        not isinstance(finalization_fingerprint, str)
        or not finalization_fingerprint.strip()
    ):
        raise ValueError(
            "persisted reconsolidation decision requires P5 finalization fingerprint"
        )
    payload = dict(audit)
    payload.pop("decision_fingerprint", None)
    expected = "reconsolidation_" + _stable_sha256(payload)[:24]
    if fingerprint != expected:
        raise ValueError("persisted reconsolidation decision audit is corrupt")
    if audit.get("eligible") is not True:
        raise ValueError("ineligible decision cannot produce a successor")

    distortion_items = audit.get("distortion_candidates", [])
    if not isinstance(distortion_items, list):
        raise ValueError("distortion_candidates audit must be a list")
    policy_audit = audit.get("policy")
    if not isinstance(policy_audit, dict):
        raise ValueError("persisted reconsolidation policy audit is required")
    policy_generalization_threshold = policy_audit.get(
        "max_temporal_confidence_for_generalization"
    )
    if (
        isinstance(policy_generalization_threshold, bool)
        or not isinstance(policy_generalization_threshold, (int, float))
    ):
        raise ValueError(
            "persisted temporal generalization threshold must be numeric"
        )
    seen_distortions: set[str] = set()
    for raw in distortion_items:
        if not isinstance(raw, dict):
            raise ValueError("distortion candidate audit must be an object")
        candidate_payload = dict(raw)
        stored_id = candidate_payload.pop("distortion_id", None)
        stored_fingerprint = candidate_payload.pop(
            "distortion_fingerprint",
            None,
        )
        expected_distortion = (
            "distortion_" + _stable_sha256(candidate_payload)[:24]
        )
        if (
            stored_id != expected_distortion
            or stored_fingerprint != expected_distortion
        ):
            raise ValueError("persisted distortion candidate is corrupt")
        if expected_distortion in seen_distortions:
            raise ValueError("duplicate persisted distortion candidate")
        seen_distortions.add(expected_distortion)
        if raw.get("old_trace_id") != audit.get("old_trace_id"):
            raise ValueError("distortion candidate parent trace mismatch")
        if raw.get("old_trace_digest") != audit.get("old_trace_digest"):
            raise ValueError("distortion candidate parent digest mismatch")
        if raw.get("p4_candidate_id") != audit.get("candidate_id"):
            raise ValueError("distortion candidate P4 ID mismatch")
        if raw.get("p4_candidate_digest") != audit.get("candidate_digest"):
            raise ValueError("distortion candidate P4 digest mismatch")
        if raw.get("kind") != DistortionKind.TEMPORAL_GENERALIZATION.value:
            raise ValueError("persisted distortion kind is not permitted")
        if raw.get("output_temporal_form") != (
            SubjectiveTemporalForm.GENERALIZED.value
        ):
            raise ValueError("persisted distortion output form is invalid")
        if raw.get("recalled_temporal_precision") != (
            TemporalPrecision.UNCERTAIN.value
        ):
            raise ValueError("persisted distortion recall precision is invalid")
        if raw.get("recalled_representation_fingerprint") != raw.get(
            "parent_representation_fingerprint"
        ):
            raise ValueError(
                "persisted distortion recalled representation mismatch"
            )
        driver_confidence = raw.get("driver_temporal_confidence")
        distortion_threshold = raw.get("max_temporal_confidence_threshold")
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in (driver_confidence, distortion_threshold)
        ):
            raise ValueError(
                "persisted distortion confidence values must be numeric"
            )
        if abs(
            float(distortion_threshold)
            - float(policy_generalization_threshold)
        ) > 1e-12:
            raise ValueError("persisted distortion policy threshold mismatch")
        if float(driver_confidence) > float(distortion_threshold):
            raise ValueError(
                "persisted distortion driver exceeds generalization threshold"
            )

    representation_items = audit.get("representation_operations", [])
    if not isinstance(representation_items, list):
        raise ValueError("representation_operations audit must be a list")
    if len(representation_items) != len(distortion_items):
        raise ValueError(
            "persisted distortion candidate/operation count mismatch"
        )


def _verify_successor_matches_audit(
    *,
    parent: MemoryTrace,
    successor: MemoryTrace,
    audit: dict[str, Any],
) -> None:
    """Prove the successor is exactly the state transition described by audit."""

    expected_values: dict[str, float | int] = {
        "strength": parent.strength,
        "accessibility": parent.accessibility,
        "familiarity": parent.familiarity,
        "retrieval_count": parent.retrieval_count,
        "rehearsal_count": parent.rehearsal_count,
    }
    seen_fields: set[str] = set()
    for raw in audit.get("operations", []):
        if not isinstance(raw, dict):
            raise ValueError("reconsolidation operation audit must be an object")
        field_name = raw.get("field_name")
        if field_name not in _ALLOWED_OPERATION_FIELDS:
            raise ValueError("decision audit contains unsupported operation field")
        if field_name in seen_fields:
            raise ValueError("decision audit contains duplicate operation field")
        seen_fields.add(field_name)
        old_value = raw.get("old_value")
        new_value = raw.get("new_value")
        delta = raw.get("delta")
        if isinstance(old_value, bool) or not isinstance(old_value, (int, float)):
            raise ValueError("decision operation old_value must be numeric")
        if isinstance(new_value, bool) or not isinstance(new_value, (int, float)):
            raise ValueError("decision operation new_value must be numeric")
        if isinstance(delta, bool) or not isinstance(delta, (int, float)):
            raise ValueError("decision operation delta must be numeric")
        if float(expected_values[field_name]) != float(old_value):
            raise ValueError(
                f"decision operation old value does not match parent for {field_name}"
            )
        if abs((float(new_value) - float(old_value)) - float(delta)) > 1e-12:
            raise ValueError("decision operation delta is inconsistent")
        expected_values[field_name] = new_value

    for field_name, expected_value in expected_values.items():
        actual = getattr(successor, field_name)
        if isinstance(expected_value, int) and field_name in {
            "retrieval_count",
            "rehearsal_count",
        }:
            if actual != int(expected_value):
                raise ValueError(
                    f"successor {field_name} does not match decision operations"
                )
        elif abs(float(actual) - float(expected_value)) > 1e-12:
            raise ValueError(
                f"successor {field_name} does not match decision operations"
            )

    expected_detail_states = {
        state.detail_id: state for state in parent.detail_states
    }
    seen_detail_fields: set[tuple[str, str]] = set()
    for raw in audit.get("detail_operations", []):
        if not isinstance(raw, dict):
            raise ValueError("detail operation audit must be an object")
        detail_id = raw.get("detail_id")
        if not isinstance(detail_id, str) or not detail_id.strip():
            raise ValueError("detail operation requires detail_id")
        if detail_id not in expected_detail_states:
            raise ValueError("detail operation references unknown parent detail")
        field_name = raw.get("field_name")
        if field_name not in {
            "accessibility",
            "temporal_confidence",
            "association_strength",
        }:
            raise ValueError("decision audit contains unsupported detail field")
        operation_key = (detail_id, field_name)
        if operation_key in seen_detail_fields:
            raise ValueError("decision audit contains duplicate detail field operation")
        seen_detail_fields.add(operation_key)
        parent_state = expected_detail_states[detail_id]
        old_value = raw.get("old_value")
        new_value = raw.get("new_value")
        delta = raw.get("delta")
        if any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            for value in (old_value, new_value, delta)
        ):
            raise ValueError("detail operation values must be numeric")
        if abs(float(getattr(parent_state, field_name)) - float(old_value)) > 1e-12:
            raise ValueError("detail operation old value does not match parent")
        if raw.get("old_state_fingerprint") != parent_state.state_fingerprint:
            raise ValueError("detail operation old fingerprint mismatch")
        if abs((float(new_value) - float(old_value)) - float(delta)) > 1e-12:
            raise ValueError("detail operation delta is inconsistent")
        kwargs = {
            "detail_id": parent_state.detail_id,
            "retention": parent_state.retention,
            "accessibility": parent_state.accessibility,
            "temporal_confidence": parent_state.temporal_confidence,
            "association_strength": parent_state.association_strength,
            "parent_state_fingerprint": parent_state.state_fingerprint,
        }
        kwargs[field_name] = float(new_value)
        new_state = TraceDetailState(**kwargs)
        if raw.get("new_state_fingerprint") != new_state.state_fingerprint:
            raise ValueError("detail operation new fingerprint mismatch")
        expected_detail_states[detail_id] = new_state

    expected_detail_tuple = tuple(
        expected_detail_states[detail.detail_id] for detail in parent.details
    )
    if successor.detail_states != expected_detail_tuple:
        raise ValueError(
            "successor detail_states do not match audited detail operations"
        )

    expected_representations = {
        item.detail_id: item for item in parent.subjective_representations
    }
    distortion_by_fingerprint = {
        str(item["distortion_fingerprint"]): item
        for item in audit.get("distortion_candidates", [])
    }
    seen_representation_details: set[str] = set()
    used_distortions: set[str] = set()
    for raw in audit.get("representation_operations", []):
        if not isinstance(raw, dict):
            raise ValueError("representation operation audit must be an object")
        detail_id = raw.get("detail_id")
        if not isinstance(detail_id, str) or not detail_id.strip():
            raise ValueError("representation operation requires detail_id")
        if detail_id in seen_representation_details:
            raise ValueError(
                "decision audit contains duplicate representation operation"
            )
        seen_representation_details.add(detail_id)
        if detail_id not in expected_representations:
            raise ValueError(
                "representation operation references unknown parent detail"
            )
        distortion_fingerprint = raw.get(
            "distortion_candidate_fingerprint"
        )
        if not isinstance(distortion_fingerprint, str):
            raise ValueError(
                "representation operation requires distortion fingerprint"
            )
        distortion = distortion_by_fingerprint.get(distortion_fingerprint)
        if distortion is None:
            raise ValueError(
                "representation operation references unknown distortion candidate"
            )
        if distortion_fingerprint in used_distortions:
            raise ValueError("distortion candidate used more than once")
        used_distortions.add(distortion_fingerprint)
        if raw.get("kind") != distortion.get("kind"):
            raise ValueError("representation operation kind mismatch")
        if raw.get("reason_code") != distortion.get("reason_code"):
            raise ValueError("representation operation reason mismatch")
        if distortion.get("detail_id") != detail_id:
            raise ValueError("distortion candidate detail mismatch")
        parent_representation = expected_representations[detail_id]
        if raw.get("old_representation_fingerprint") != (
            parent_representation.representation_fingerprint
        ):
            raise ValueError("representation operation old fingerprint mismatch")
        if distortion.get("parent_representation_fingerprint") != (
            parent_representation.representation_fingerprint
        ):
            raise ValueError("distortion candidate representation parent mismatch")
        if distortion.get("recalled_representation_fingerprint") != (
            parent_representation.representation_fingerprint
        ):
            raise ValueError("distortion candidate recalled representation mismatch")
        if distortion.get("recalled_detail_ref") != f"{parent.trace_id}:{detail_id}":
            raise ValueError("distortion candidate recalled detail ref mismatch")
        if distortion.get("recalled_temporal_precision") != (
            TemporalPrecision.UNCERTAIN.value
        ):
            raise ValueError("distortion candidate recall was not temporally uncertain")
        if raw.get("old_temporal_form") != SubjectiveTemporalForm.EXACT.value:
            raise ValueError("P6D operation must begin from exact temporal form")
        if raw.get("new_temporal_form") != (
            SubjectiveTemporalForm.GENERALIZED.value
        ):
            raise ValueError(
                "P6D operation must end in generalized temporal form"
            )
        detail = next(
            item for item in parent.details if item.detail_id == detail_id
        )
        if distortion.get("detail_semantic_fingerprint") != (
            detail.semantic_fingerprint
        ):
            raise ValueError("distortion candidate semantic detail mismatch")
        if detail.temporal_semantics is None:
            raise ValueError(
                "temporal distortion requires structured temporal semantics"
            )
        if distortion.get("exact_temporal_phrase") != (
            detail.temporal_semantics.exact_phrase
        ):
            raise ValueError("distortion exact temporal phrase mismatch")
        if distortion.get("generalized_temporal_phrase") != (
            detail.temporal_semantics.generalized_phrase
        ):
            raise ValueError("distortion generalized temporal phrase mismatch")
        parent_state = parent.detail_state(detail_id)
        if distortion.get("driver_state_fingerprint") != (
            parent_state.state_fingerprint
        ):
            raise ValueError("distortion driver state fingerprint mismatch")
        if abs(
            float(distortion.get("driver_temporal_confidence"))
            - parent_state.temporal_confidence
        ) > 1e-12:
            raise ValueError("distortion driver temporal confidence mismatch")
        audit_policy = audit.get("policy")
        if not isinstance(audit_policy, dict):
            raise ValueError("persisted reconsolidation policy audit is required")
        policy_threshold = audit_policy.get(
            "max_temporal_confidence_for_generalization"
        )
        distortion_threshold = distortion.get(
            "max_temporal_confidence_threshold"
        )
        if (
            isinstance(policy_threshold, bool)
            or not isinstance(policy_threshold, (int, float))
            or isinstance(distortion_threshold, bool)
            or not isinstance(distortion_threshold, (int, float))
        ):
            raise ValueError("distortion threshold audit is invalid")
        if abs(float(distortion_threshold) - float(policy_threshold)) > 1e-12:
            raise ValueError("distortion threshold does not match policy")
        if parent_state.temporal_confidence > float(distortion_threshold):
            raise ValueError("distortion parent confidence exceeds threshold")

        new_representation = _make_subjective_detail_representation(
            detail_id=detail_id,
            temporal_form=SubjectiveTemporalForm.GENERALIZED,
            parent_representation_fingerprint=(
                parent_representation.representation_fingerprint
            ),
            distortion_candidate_fingerprint=distortion_fingerprint,
        )
        if raw.get("new_representation_fingerprint") != (
            new_representation.representation_fingerprint
        ):
            raise ValueError("representation operation new fingerprint mismatch")
        expected_representations[detail_id] = new_representation

    if used_distortions != set(distortion_by_fingerprint):
        raise ValueError("unused persisted distortion candidate")
    expected_representation_tuple = tuple(
        expected_representations[detail.detail_id]
        for detail in parent.details
    )
    if successor.subjective_representations != expected_representation_tuple:
        raise ValueError(
            "successor subjective representations do not match audit"
        )

    for field_name in (
        "protected_evidence",
        "gist",
        "details",
        "temporal_cues",
        "actor_refs",
        "object_refs",
        "encoding_affect",
        "source_cues",
        "competing_trace_ids",
    ):
        if getattr(successor, field_name) != getattr(parent, field_name):
            raise ValueError(
                f"initial P6 successor illegally changed {field_name}"
            )




class TraceVersionLedger:
    """Local deterministic version and transition-audit ledger.

    The ledger is the isolated P6 authority for monotonic versions. Every
    successor is stored with the complete canonical ReconsolidationDecision
    audit payload that caused it.
    """

    def __init__(self) -> None:
        self._history: dict[str, list[MemoryTrace]] = {}
        self._decision_audit: dict[str, str] = {}

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
        if any(
            state.parent_state_fingerprint is not None
            for state in trace.detail_states
        ):
            raise ValueError(
                "initial trace detail states cannot claim prior mnemonic parents"
            )
        if any(
            representation.temporal_form is not SubjectiveTemporalForm.EXACT
            or representation.parent_representation_fingerprint is not None
            or representation.distortion_candidate_fingerprint is not None
            for representation in trace.subjective_representations
        ):
            raise ValueError(
                "initial trace subjective representations must be exact roots"
            )
        if trace.trace_lineage_id in self._history:
            raise ValueError("trace lineage is already registered")
        self._history[trace.trace_lineage_id] = [trace]

    def _append_verified(
        self,
        *,
        parent: MemoryTrace,
        successor: MemoryTrace,
        decision_json: str,
    ) -> None:
        if not isinstance(parent, MemoryTrace) or not isinstance(successor, MemoryTrace):
            raise TypeError("parent and successor must be MemoryTrace")
        if not isinstance(decision_json, str) or not decision_json.strip():
            raise ValueError("decision audit JSON is required")
        audit = json.loads(decision_json)
        _verify_serialized_decision_audit(audit)
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
        if str(audit.get("decision_fingerprint") or "") != (
            successor.reconsolidation_decision_fingerprint
        ):
            raise ValueError("decision audit fingerprint does not match successor")
        if str(audit.get("recollection_event_id") or "") != (
            successor.reconsolidation_event_id
        ):
            raise ValueError("decision audit recollection event does not match successor")
        if str(audit.get("old_trace_id") or "") != parent.trace_id:
            raise ValueError("decision audit parent trace mismatch")
        if str(audit.get("old_trace_digest") or "") != parent.snapshot_digest:
            raise ValueError("decision audit parent digest mismatch")
        if str(audit.get("trace_lineage_id") or "") != parent.trace_lineage_id:
            raise ValueError("decision audit lineage mismatch")
        if int(audit.get("old_version", -1)) != parent.version:
            raise ValueError("decision audit parent version mismatch")
        if successor.trace_id in self._decision_audit:
            raise ValueError("successor transition audit already exists")

        _verify_successor_matches_audit(
            parent=parent,
            successor=successor,
            audit=audit,
        )

        history.append(successor)
        self._decision_audit[successor.trace_id] = _stable_json(audit)

    def append_successor(
        self,
        *,
        parent: MemoryTrace,
        successor: MemoryTrace,
        decision: ReconsolidationDecision,
    ) -> None:
        if not isinstance(decision, ReconsolidationDecision):
            raise TypeError("decision must be ReconsolidationDecision")
        if decision.old_trace_id != parent.trace_id:
            raise ValueError("decision does not belong to parent trace")
        if decision.old_trace_digest != parent.snapshot_digest:
            raise ValueError("decision parent digest mismatch")
        if decision.decision_fingerprint != successor.reconsolidation_decision_fingerprint:
            raise ValueError("decision fingerprint does not match successor")
        self._append_verified(
            parent=parent,
            successor=successor,
            decision_json=decision.stable_json(),
        )

    def history(self, trace_lineage_id: str) -> tuple[MemoryTrace, ...]:
        if trace_lineage_id not in self._history:
            raise KeyError(trace_lineage_id)
        return tuple(self._history[trace_lineage_id])

    def latest(self, trace_lineage_id: str) -> MemoryTrace:
        return self.history(trace_lineage_id)[-1]

    def decision_audit(self, successor_trace_id: str) -> dict[str, Any]:
        if successor_trace_id not in self._decision_audit:
            raise KeyError(successor_trace_id)
        return json.loads(self._decision_audit[successor_trace_id])

    def stable_json(self) -> str:
        traces = [
            asdict(trace)
            for lineage in sorted(self._history)
            for trace in self._history[lineage]
        ]
        transitions = [
            {
                "successor_trace_id": successor_trace_id,
                "decision": json.loads(self._decision_audit[successor_trace_id]),
            }
            for successor_trace_id in sorted(self._decision_audit)
        ]
        return _stable_json(
            {
                "schema_version": _LEDGER_SCHEMA_VERSION,
                "traces": traces,
                "transitions": transitions,
            }
        )

    @classmethod
    def from_json(cls, payload: str) -> "TraceVersionLedger":
        if not isinstance(payload, str) or not payload.strip():
            raise ValueError("ledger payload is required")
        decoded = json.loads(payload)
        if decoded.get("schema_version") != _LEDGER_SCHEMA_VERSION:
            raise ValueError("unsupported trace ledger schema version")

        transition_by_successor = {
            str(item["successor_trace_id"]): _stable_json(item["decision"])
            for item in decoded.get("transitions", [])
        }
        if len(transition_by_successor) != len(decoded.get("transitions", [])):
            raise ValueError("duplicate successor transition audit")

        ledger = cls()
        for raw in decoded.get("traces", []):
            trace = _memory_trace_from_dict(raw)
            if trace.version == 0:
                ledger.register_initial(trace)
                continue
            history = ledger._history.get(trace.trace_lineage_id)
            if not history:
                raise ValueError("successor encountered before initial trace")
            decision_json = transition_by_successor.pop(trace.trace_id, None)
            if decision_json is None:
                raise ValueError("successor is missing reconsolidation decision audit")
            ledger._append_verified(
                parent=history[-1],
                successor=trace,
                decision_json=decision_json,
            )
        if transition_by_successor:
            raise ValueError("transition audit references unknown successor trace")
        return ledger

    def save(self, path: str | Path) -> None:
        target = Path(path)
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_text(self.stable_json(), encoding="utf-8")
        temporary.replace(target)

    @classmethod
    def load(cls, path: str | Path) -> "TraceVersionLedger":
        return cls.from_json(Path(path).read_text(encoding="utf-8"))


def reconsolidate_and_record(
    *,
    ledger: TraceVersionLedger,
    old_trace: MemoryTrace,
    candidate: RecollectionCandidate,
    source_decision: SourceMonitoringDecision,
    finalized_recollection: FinalizedRecollection,
    awareness_decision: AwarenessDecision,
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
        finalized_recollection=finalized_recollection,
        awareness_decision=awareness_decision,
        context=context,
        policy=policy,
    )
    successor = apply_reconsolidation(
        old_trace=old_trace,
        candidate=candidate,
        source_decision=source_decision,
        finalized_recollection=finalized_recollection,
        awareness_decision=awareness_decision,
        decision=decision,
    )
    if successor is not None:
        ledger.append_successor(
            parent=old_trace,
            successor=successor,
            decision=decision,
        )
    return decision, successor
