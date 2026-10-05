"""P5 deterministic source monitoring for UPPB.

P5 infers where a completed P4 recollection seems to have come from. The
source-monitoring calculation receives only subject-plausible cues. Protected
truth, evidence classifications, evidence digests, trace IDs, and P4 content
confidence are deliberately outside the scoring interface.

P5 then binds the source-monitoring decision back to the verified P4 candidate
and creates the first canonical recollection PhenomenalEvent. That event starts
LATENT and must pass through P3 awareness arbitration before subject access.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any

from .phenomenology import (
    AwarenessLevel,
    CertaintyBand,
    IntensityBand,
    ObjectiveProvenance,
    PhenomenalEvent,
    PhenomenalMode,
    PrivacyState,
    SubjectiveSourceAttribution,
    SubjectiveSourceKind,
)
from .recollection import RecollectionCandidate


_SOURCE_MONITORING_DECISION_FACTORY_TOKEN = object()
_SOURCE_MONITOR_RULE_VERSION = "uppb-p5-v1"


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


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


@dataclass(frozen=True)
class SourceMonitoringCues:
    """Restricted subject-plausible evidence for source attribution.

    This object intentionally contains no protected evidence references,
    objective evidence class, evidence digest, trace ID, database identifier,
    or other privileged provenance signal.
    """

    retrieval_fluency: float = 0.0
    perceptual_richness: float = 0.0
    temporal_coherence: float = 0.0
    spatial_coherence: float = 0.0
    contextual_compatibility: float = 0.0
    familiarity: float = 0.0
    trace_accessibility: float = 0.0
    rehearsal_frequency: float = 0.0
    imagination_exposure: float = 0.0
    reconstruction_exposure: float = 0.0
    competing_source_strength: float = 0.0
    cue_match: float = 0.0
    social_communication_signature: float = 0.0
    textual_signature: float = 0.0
    inferential_signature: float = 0.0
    dreamlike_discontinuity: float = 0.0

    def __post_init__(self) -> None:
        for name in (
            "retrieval_fluency",
            "perceptual_richness",
            "temporal_coherence",
            "spatial_coherence",
            "contextual_compatibility",
            "familiarity",
            "trace_accessibility",
            "rehearsal_frequency",
            "imagination_exposure",
            "reconstruction_exposure",
            "competing_source_strength",
            "cue_match",
            "social_communication_signature",
            "textual_signature",
            "inferential_signature",
            "dreamlike_discontinuity",
        ):
            object.__setattr__(self, name, _unit(getattr(self, name), name))

    @property
    def fingerprint(self) -> str:
        return _stable_sha256(asdict(self))

    def stable_json(self) -> str:
        return _stable_json(asdict(self))


@dataclass(frozen=True)
class SourceEvidenceContribution:
    source_kind: SubjectiveSourceKind
    score: float

    def __post_init__(self) -> None:
        if not isinstance(self.source_kind, SubjectiveSourceKind):
            raise TypeError("source_kind must be SubjectiveSourceKind")
        object.__setattr__(self, "score", _unit(self.score, "score"))


@dataclass(frozen=True, init=False)
class SourceMonitoringDecision:
    """Immutable engineer-visible result of the restricted source monitor."""

    candidate_id: str
    candidate_digest: str
    cues: SourceMonitoringCues
    cues_fingerprint: str
    rule_version: str
    contributions: tuple[SourceEvidenceContribution, ...]
    selected_source: SubjectiveSourceKind
    certainty: CertaintyBand
    top_score: float
    runner_up_score: float
    margin: float
    decision_basis: tuple[str, ...]
    decision_fingerprint: str

    def __init__(self, *, _factory_token: object = None) -> None:
        if _factory_token is not _SOURCE_MONITORING_DECISION_FACTORY_TOKEN:
            raise TypeError(
                "SourceMonitoringDecision is factory-controlled; "
                "use monitor_recollection_source()"
            )

    def stable_json(self) -> str:
        return _stable_json(asdict(self))


@dataclass(frozen=True)
class RecollectionFinalizationContext:
    """Engineer-side context for canonical recollection-event construction.

    This context is deliberately not passed into the source-monitoring scoring
    function. Objective provenance remains available to audit/finalization but
    cannot influence subjective source inference.
    """

    tick: int
    source_state_digest: str
    objective_provenance: ObjectiveProvenance
    privacy: PrivacyState = PrivacyState.PRIVATE
    projection_rule_version: str = "uppb-p5-finalize-v1"

    def __post_init__(self) -> None:
        if isinstance(self.tick, bool) or not isinstance(self.tick, int):
            raise TypeError("tick must be a non-boolean integer")
        if self.tick < 0:
            raise ValueError("tick cannot be negative")
        if (
            not isinstance(self.source_state_digest, str)
            or not self.source_state_digest.strip()
        ):
            raise ValueError("source_state_digest is required")
        if not isinstance(self.objective_provenance, ObjectiveProvenance):
            raise TypeError("objective_provenance must be ObjectiveProvenance")
        if not isinstance(self.privacy, PrivacyState):
            raise TypeError("privacy must be PrivacyState")
        if (
            not isinstance(self.projection_rule_version, str)
            or not self.projection_rule_version.strip()
        ):
            raise ValueError("projection_rule_version is required")


def _source_scores(cues: SourceMonitoringCues) -> dict[SubjectiveSourceKind, float]:
    """Compute source evidence from restricted cues only."""

    lived = _clamp(
        0.16 * cues.retrieval_fluency
        + 0.22 * cues.perceptual_richness
        + 0.10 * cues.temporal_coherence
        + 0.08 * cues.spatial_coherence
        + 0.10 * cues.contextual_compatibility
        + 0.10 * cues.familiarity
        + 0.08 * cues.trace_accessibility
        + 0.06 * cues.rehearsal_frequency
        + 0.06 * cues.cue_match
        - 0.12 * cues.imagination_exposure
        - 0.12 * cues.reconstruction_exposure
        - 0.10 * cues.competing_source_strength
        - 0.08 * cues.textual_signature
        - 0.05 * cues.social_communication_signature
        - 0.05 * cues.inferential_signature
        - 0.12 * cues.dreamlike_discontinuity
    )

    told = _clamp(
        0.30 * cues.social_communication_signature
        + 0.15 * cues.retrieval_fluency
        + 0.12 * cues.familiarity
        + 0.10 * cues.rehearsal_frequency
        + 0.08 * cues.contextual_compatibility
        + 0.08 * cues.cue_match
        + 0.05 * cues.competing_source_strength
        - 0.08 * cues.perceptual_richness
        - 0.04 * cues.textual_signature
    )

    read = _clamp(
        0.34 * cues.textual_signature
        + 0.14 * cues.familiarity
        + 0.10 * cues.rehearsal_frequency
        + 0.10 * cues.contextual_compatibility
        + 0.08 * cues.retrieval_fluency
        + 0.08 * cues.cue_match
        + 0.05 * cues.reconstruction_exposure
        - 0.08 * cues.social_communication_signature
        - 0.08 * cues.perceptual_richness
    )

    imagined = _clamp(
        0.34 * cues.imagination_exposure
        + 0.18 * cues.reconstruction_exposure
        + 0.10 * cues.perceptual_richness
        + 0.08 * cues.retrieval_fluency
        + 0.08 * cues.familiarity
        + 0.06 * cues.competing_source_strength
        - 0.08 * cues.temporal_coherence
        - 0.06 * cues.spatial_coherence
    )

    inferred = _clamp(
        0.40 * cues.inferential_signature
        + 0.14 * cues.contextual_compatibility
        + 0.12 * cues.cue_match
        + 0.08 * cues.retrieval_fluency
        + 0.06 * cues.familiarity
        - 0.12 * cues.perceptual_richness
    )

    dreamed = _clamp(
        0.46 * cues.dreamlike_discontinuity
        + 0.12 * cues.perceptual_richness
        + 0.08 * cues.familiarity
        + 0.08 * cues.imagination_exposure
        - 0.12 * cues.temporal_coherence
        - 0.12 * cues.spatial_coherence
        - 0.06 * cues.contextual_compatibility
    )

    return {
        SubjectiveSourceKind.LIVED: lived,
        SubjectiveSourceKind.TOLD: told,
        SubjectiveSourceKind.READ: read,
        SubjectiveSourceKind.IMAGINED: imagined,
        SubjectiveSourceKind.INFERRED: inferred,
        SubjectiveSourceKind.DREAMED: dreamed,
    }


def _certainty_for(top_score: float, margin: float) -> CertaintyBand:
    if top_score >= 0.78 and margin >= 0.24:
        return CertaintyBand.VERY_HIGH
    if top_score >= 0.64 and margin >= 0.14:
        return CertaintyBand.HIGH
    if top_score >= 0.50 and margin >= 0.08:
        return CertaintyBand.MODERATE
    return CertaintyBand.LOW


def monitor_recollection_source(
    *,
    candidate: RecollectionCandidate,
    cues: SourceMonitoringCues,
    rule_version: str = _SOURCE_MONITOR_RULE_VERSION,
) -> SourceMonitoringDecision:
    """Infer subjective source using only restricted source-monitoring cues.

    The canonical P5 boundary accepts the verified P4 candidate itself rather
    than a caller-supplied identifier. Source scoring still receives only the
    restricted cue object and never objective provenance.
    """

    if not isinstance(candidate, RecollectionCandidate):
        raise TypeError("candidate must be RecollectionCandidate")
    if not isinstance(cues, SourceMonitoringCues):
        raise TypeError("cues must be SourceMonitoringCues")
    if not isinstance(rule_version, str) or not rule_version.strip():
        raise ValueError("rule_version is required")

    scores = _source_scores(cues)
    ordered = sorted(
        scores.items(),
        key=lambda item: (item[1], item[0].value),
        reverse=True,
    )
    top_source, top_score = ordered[0]
    runner_up_score = ordered[1][1]
    margin = top_score - runner_up_score

    decision_basis: list[str] = []
    if top_score < 0.42:
        decision_basis.append("top_score_below_attribution_threshold")
    if margin < 0.07:
        decision_basis.append("winner_margin_below_attribution_threshold")
    if cues.competing_source_strength >= 0.75 and margin < 0.18:
        decision_basis.append("strong_competing_source")

    if decision_basis:
        selected = SubjectiveSourceKind.UNKNOWN
        certainty = CertaintyBand.LOW
    else:
        selected = top_source
        certainty = _certainty_for(top_score, margin)
        decision_basis.append("clear_highest_supported_source")

    contributions = tuple(
        SourceEvidenceContribution(source_kind=kind, score=score)
        for kind, score in ordered
    )
    payload = {
        "candidate_id": candidate.candidate_id,
        "candidate_digest": candidate.candidate_digest,
        "cues": asdict(cues),
        "cues_fingerprint": cues.fingerprint,
        "rule_version": rule_version,
        "contributions": [asdict(item) for item in contributions],
        "selected_source": selected.value,
        "certainty": certainty.value,
        "top_score": top_score,
        "runner_up_score": runner_up_score,
        "margin": margin,
        "decision_basis": decision_basis,
    }

    decision = SourceMonitoringDecision(
        _factory_token=_SOURCE_MONITORING_DECISION_FACTORY_TOKEN
    )
    object.__setattr__(decision, "candidate_id", candidate.candidate_id)
    object.__setattr__(decision, "candidate_digest", candidate.candidate_digest)
    object.__setattr__(decision, "cues", cues)
    object.__setattr__(decision, "cues_fingerprint", cues.fingerprint)
    object.__setattr__(decision, "rule_version", rule_version)
    object.__setattr__(decision, "contributions", contributions)
    object.__setattr__(decision, "selected_source", selected)
    object.__setattr__(decision, "certainty", certainty)
    object.__setattr__(decision, "top_score", top_score)
    object.__setattr__(decision, "runner_up_score", runner_up_score)
    object.__setattr__(decision, "margin", margin)
    object.__setattr__(decision, "decision_basis", tuple(decision_basis))
    object.__setattr__(
        decision,
        "decision_fingerprint",
        "source_monitor_" + _stable_sha256(payload)[:24],
    )
    return decision


def _source_neutral_first_person(scene: str) -> str:
    scene = scene.strip()
    if not scene:
        raise ValueError("recollection scene is required")
    return f"I can call to mind the following: {scene}"


def finalize_recollection_event(
    *,
    candidate: RecollectionCandidate,
    decision: SourceMonitoringDecision,
    context: RecollectionFinalizationContext,
) -> PhenomenalEvent:
    """Create the first canonical phenomenal recollection after source monitoring."""

    if not isinstance(candidate, RecollectionCandidate):
        raise TypeError("candidate must be RecollectionCandidate")
    if not isinstance(decision, SourceMonitoringDecision):
        raise TypeError("decision must be SourceMonitoringDecision")
    if not isinstance(context, RecollectionFinalizationContext):
        raise TypeError("context must be RecollectionFinalizationContext")
    if decision.candidate_id != candidate.candidate_id:
        raise ValueError("source-monitoring decision does not belong to candidate")
    if decision.candidate_digest != candidate.candidate_digest:
        raise ValueError("source-monitoring decision candidate digest mismatch")
    if decision.cues_fingerprint != decision.cues.fingerprint:
        raise ValueError("source-monitoring decision cue fingerprint mismatch")

    provenance_ids = tuple(context.objective_provenance.record_ids)
    if provenance_ids != candidate.protected_evidence_refs:
        raise ValueError(
            "objective provenance record_ids must exactly match "
            "candidate protected_evidence_refs in canonical order"
        )

    text = _source_neutral_first_person(candidate.reconstructed_scene)
    return PhenomenalEvent(
        tick=context.tick,
        subject_id=candidate.subject_id,
        mode=PhenomenalMode.RECOLLECTION,
        awareness=AwarenessLevel.LATENT,
        canonical_first_person=text,
        privacy=context.privacy,
        projection_rule_version=context.projection_rule_version,
        source_state_digest=context.source_state_digest,
        objective_provenance=context.objective_provenance,
        subjective_source=SubjectiveSourceAttribution(
            kind=decision.selected_source,
            certainty=decision.certainty,
        ),
        subjective_certainty=decision.certainty,
        subjective_vividness=candidate.vividness,
        subjective_intensity=IntensityBand.MODERATE,
        source_state_refs=candidate.trace_ids,
        source_event_refs=(
            candidate.candidate_id,
            candidate.candidate_digest,
            decision.decision_fingerprint,
            candidate.retrieval_episode_fingerprint,
        ),
    )
