"""P4 reconstructive-memory architecture for UPPB.

This module is intentionally upstream of subjective source monitoring and
awareness. It models protected-evidence references, immutable/versioned memory
trace snapshots, explicit retrieval episodes, and deterministic nonfinal
recollection candidates.

P4 does not create PhenomenalEvent values. P5 owns subjective source
attribution and final phenomenal recollection construction.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Iterable

from .phenomenology import VividnessBand


_TOKEN_RE = re.compile(r"[A-Za-z0-9']+")
_RECOLLECTION_CANDIDATE_FACTORY_TOKEN = object()
_SUBJECTIVE_DETAIL_REP_FACTORY_TOKEN = object()


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in _TOKEN_RE.findall(text) if token}


def _tuple_of_strings(value: Iterable[str], name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must be a sequence of strings, not a string")
    try:
        normalized = tuple(value)
    except TypeError as exc:
        raise TypeError(f"{name} must be an iterable of strings") from exc
    if any(not isinstance(item, str) for item in normalized):
        raise TypeError(f"{name} must contain only strings")
    if any(not item.strip() for item in normalized):
        raise ValueError(f"{name} cannot contain blank identifiers")
    return normalized


def _tuple_of_type(value: Iterable[Any], item_type: type, name: str) -> tuple[Any, ...]:
    if isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must be a sequence")
    try:
        normalized = tuple(value)
    except TypeError as exc:
        raise TypeError(f"{name} must be iterable") from exc
    if any(not isinstance(item, item_type) for item in normalized):
        raise TypeError(f"{name} must contain only {item_type.__name__} values")
    return normalized


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


def _nonnegative_int(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be a non-boolean integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")
    return value


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ProtectedEvidenceRef:
    """Reference to truth owned outside UPPB."""

    evidence_id: str
    digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_id, str) or not self.evidence_id.strip():
            raise ValueError("evidence_id is required")
        if not isinstance(self.digest, str) or not self.digest.strip():
            raise ValueError("protected evidence digest is required")


@dataclass(frozen=True)
class TemporalSemantics:
    """Structured temporal truth for a detail with an allowed generalization."""

    exact_phrase: str
    generalized_phrase: str

    def __post_init__(self) -> None:
        for name in ("exact_phrase", "generalized_phrase"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if self.exact_phrase == self.generalized_phrase:
            raise ValueError("temporal generalization must differ from exact phrase")


class SubjectiveTemporalForm(StrEnum):
    """Current subject-memory representation of a structured temporal slot."""

    EXACT = "exact"
    GENERALIZED = "generalized"


@dataclass(frozen=True, init=False)
class SubjectiveDetailRepresentation:
    """Factory-controlled subject-memory representation separate from truth."""

    detail_id: str
    temporal_form: SubjectiveTemporalForm
    parent_representation_fingerprint: str | None
    distortion_candidate_fingerprint: str | None
    representation_fingerprint: str

    def __init__(self, *, _factory_token: object = None) -> None:
        if _factory_token is not _SUBJECTIVE_DETAIL_REP_FACTORY_TOKEN:
            raise TypeError(
                "SubjectiveDetailRepresentation is factory-controlled"
            )


def _make_subjective_detail_representation(
    *,
    detail_id: str,
    temporal_form: SubjectiveTemporalForm = SubjectiveTemporalForm.EXACT,
    parent_representation_fingerprint: str | None = None,
    distortion_candidate_fingerprint: str | None = None,
) -> SubjectiveDetailRepresentation:
    if not isinstance(detail_id, str) or not detail_id.strip():
        raise ValueError("detail_id is required")
    if not isinstance(temporal_form, SubjectiveTemporalForm):
        raise TypeError("temporal_form must be SubjectiveTemporalForm")
    for name, value in (
        ("parent_representation_fingerprint", parent_representation_fingerprint),
        ("distortion_candidate_fingerprint", distortion_candidate_fingerprint),
    ):
        if value is not None and (
            not isinstance(value, str) or not value.strip()
        ):
            raise ValueError(f"{name} must be a non-blank string or None")
    if temporal_form is SubjectiveTemporalForm.EXACT:
        if parent_representation_fingerprint is not None:
            raise ValueError("initial exact representation cannot claim a parent")
        if distortion_candidate_fingerprint is not None:
            raise ValueError(
                "initial exact representation cannot claim distortion"
            )
    else:
        if parent_representation_fingerprint is None:
            raise ValueError("generalized representation requires a parent")
        if distortion_candidate_fingerprint is None:
            raise ValueError(
                "generalized representation requires distortion lineage"
            )
    payload = {
        "detail_id": detail_id,
        "temporal_form": temporal_form.value,
        "parent_representation_fingerprint": (
            parent_representation_fingerprint
        ),
        "distortion_candidate_fingerprint": (
            distortion_candidate_fingerprint
        ),
    }
    representation = SubjectiveDetailRepresentation(
        _factory_token=_SUBJECTIVE_DETAIL_REP_FACTORY_TOKEN
    )
    for name, value in (
        ("detail_id", detail_id),
        ("temporal_form", temporal_form),
        (
            "parent_representation_fingerprint",
            parent_representation_fingerprint,
        ),
        (
            "distortion_candidate_fingerprint",
            distortion_candidate_fingerprint,
        ),
        (
            "representation_fingerprint",
            "subjective_detail_" + _stable_sha256(payload)[:24],
        ),
    ):
        object.__setattr__(representation, name, value)
    return representation


@dataclass(frozen=True)
class TraceDetail:
    """One retained semantic detail in an immutable memory-trace snapshot."""

    detail_id: str
    text: str
    cue_terms: tuple[str, ...] = ()
    temporal_semantics: TemporalSemantics | None = None
    temporal_template: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.detail_id, str) or not self.detail_id.strip():
            raise ValueError("detail_id is required")
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("trace detail text is required")
        object.__setattr__(
            self,
            "cue_terms",
            _tuple_of_strings(self.cue_terms, "cue_terms"),
        )
        if (self.temporal_semantics is None) != (self.temporal_template is None):
            raise ValueError(
                "temporal_semantics and temporal_template must be supplied together"
            )
        if self.temporal_semantics is not None:
            if not isinstance(self.temporal_semantics, TemporalSemantics):
                raise TypeError("temporal_semantics must be TemporalSemantics")
            if (
                not isinstance(self.temporal_template, str)
                or not self.temporal_template.strip()
            ):
                raise ValueError("temporal_template is required")
            if self.temporal_template.count("{temporal}") != 1:
                raise ValueError(
                    "temporal_template must contain exactly one {temporal} slot"
                )
            remainder = self.temporal_template.replace("{temporal}", "")
            if "{" in remainder or "}" in remainder:
                raise ValueError("temporal_template may contain only {temporal}")
            rendered_exact = self.temporal_template.format(
                temporal=self.temporal_semantics.exact_phrase
            )
            if rendered_exact != self.text:
                raise ValueError(
                    "temporal_template with exact phrase must reproduce detail text"
                )

    @property
    def semantic_fingerprint(self) -> str:
        return "trace_detail_" + _stable_sha256(asdict(self))[:24]


class DetailAvailability(StrEnum):
    """Subject-independent mnemonic availability state for one retained detail."""

    AVAILABLE = "available"
    WEAKENED = "weakened"
    SUPPRESSED = "suppressed"


class OmissionCause(StrEnum):
    """Auditable reason an existing detail did not enter a P4 reconstruction."""

    BELOW_RETRIEVAL_THRESHOLD = "below_retrieval_threshold"
    CUE_MISMATCH = "cue_mismatch"
    CAPACITY_LIMITED = "capacity_limited"


class TemporalPrecision(StrEnum):
    PRECISE = "precise"
    APPROXIMATE = "approximate"
    UNCERTAIN = "uncertain"


class ContextAssociation(StrEnum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


@dataclass(frozen=True)
class DetailOmission:
    """Exact P4 omission audit for one retained detail."""

    detail_ref: str
    cause: OmissionCause
    score: float
    cue_overlap: float
    rank: int
    retrieval_threshold: float

    def __post_init__(self) -> None:
        if not isinstance(self.detail_ref, str) or not self.detail_ref.strip():
            raise ValueError("detail_ref is required")
        if not isinstance(self.cause, OmissionCause):
            raise TypeError("cause must be OmissionCause")
        object.__setattr__(self, "score", _unit(self.score, "score"))
        object.__setattr__(
            self,
            "cue_overlap",
            _unit(self.cue_overlap, "cue_overlap"),
        )
        if isinstance(self.rank, bool) or not isinstance(self.rank, int):
            raise TypeError("rank must be a non-boolean integer")
        if self.rank < 0:
            raise ValueError("rank cannot be negative")
        object.__setattr__(
            self,
            "retrieval_threshold",
            _unit(self.retrieval_threshold, "retrieval_threshold"),
        )


@dataclass(frozen=True)
class RecalledDetailState:
    """Subject-plausible qualitative access state for an included P4 detail."""

    detail_ref: str
    temporal_precision: TemporalPrecision
    contextual_association: ContextAssociation
    subjective_representation_fingerprint: str
    temporal_form: SubjectiveTemporalForm

    def __post_init__(self) -> None:
        if not isinstance(self.detail_ref, str) or not self.detail_ref.strip():
            raise ValueError("detail_ref is required")
        if not isinstance(self.temporal_precision, TemporalPrecision):
            raise TypeError("temporal_precision must be TemporalPrecision")
        if not isinstance(self.contextual_association, ContextAssociation):
            raise TypeError("contextual_association must be ContextAssociation")
        if (
            not isinstance(self.subjective_representation_fingerprint, str)
            or not self.subjective_representation_fingerprint.strip()
        ):
            raise ValueError("subjective_representation_fingerprint is required")
        if not isinstance(self.temporal_form, SubjectiveTemporalForm):
            raise TypeError("temporal_form must be SubjectiveTemporalForm")


@dataclass(frozen=True)
class TraceDetailState:
    """Versioned mnemonic state for a stable TraceDetail semantic identity.

    TraceDetail stores the retained semantic content. TraceDetailState stores
    psychologically plastic availability variables. Reconsolidation may evolve
    these values without rewriting or deleting the underlying detail.
    """

    detail_id: str
    retention: float = 1.0
    accessibility: float = 1.0
    temporal_confidence: float = 1.0
    association_strength: float = 1.0
    parent_state_fingerprint: str | None = None
    availability_state: DetailAvailability = field(init=False)
    state_fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.detail_id, str) or not self.detail_id.strip():
            raise ValueError("detail_id is required")
        for field_name in (
            "retention",
            "accessibility",
            "temporal_confidence",
            "association_strength",
        ):
            object.__setattr__(
                self,
                field_name,
                _unit(getattr(self, field_name), field_name),
            )
        if self.parent_state_fingerprint is not None and (
            not isinstance(self.parent_state_fingerprint, str)
            or not self.parent_state_fingerprint.strip()
        ):
            raise ValueError(
                "parent_state_fingerprint must be a non-blank string or None"
            )
        if self.accessibility >= 0.55:
            availability = DetailAvailability.AVAILABLE
        elif self.accessibility >= 0.20:
            availability = DetailAvailability.WEAKENED
        else:
            availability = DetailAvailability.SUPPRESSED
        object.__setattr__(self, "availability_state", availability)
        payload = {
            "detail_id": self.detail_id,
            "retention": self.retention,
            "accessibility": self.accessibility,
            "temporal_confidence": self.temporal_confidence,
            "association_strength": self.association_strength,
            "parent_state_fingerprint": self.parent_state_fingerprint,
            "availability_state": availability.value,
        }
        object.__setattr__(
            self,
            "state_fingerprint",
            "detail_state_" + _stable_sha256(payload)[:24],
        )


@dataclass(frozen=True)
class MemoryTrace:
    """Immutable/versioned autobiographical trace snapshot."""

    subject_id: str
    version: int
    protected_evidence: tuple[ProtectedEvidenceRef, ...]
    gist: str
    details: tuple[TraceDetail, ...] = ()
    detail_states: tuple[TraceDetailState, ...] = ()
    subjective_representations: tuple[SubjectiveDetailRepresentation, ...] = ()
    temporal_cues: tuple[str, ...] = ()
    actor_refs: tuple[str, ...] = ()
    object_refs: tuple[str, ...] = ()
    encoding_affect: tuple[str, ...] = ()
    source_cues: tuple[str, ...] = ()
    strength: float = 0.5
    accessibility: float = 0.5
    familiarity: float = 0.5
    rehearsal_count: int = 0
    retrieval_count: int = 0
    competing_trace_ids: tuple[str, ...] = ()
    parent_trace_id: str | None = None
    reconsolidation_decision_fingerprint: str | None = None
    reconsolidation_event_id: str | None = None
    trace_lineage_id: str = field(init=False)
    trace_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.subject_id, str) or not self.subject_id.strip():
            raise ValueError("subject_id is required")
        _nonnegative_int(self.version, "version")
        protected = _tuple_of_type(
            self.protected_evidence,
            ProtectedEvidenceRef,
            "protected_evidence",
        )
        if not protected:
            raise ValueError("MemoryTrace requires protected evidence")
        evidence_ids = tuple(ref.evidence_id for ref in protected)
        if len(set(evidence_ids)) != len(evidence_ids):
            raise ValueError("protected_evidence evidence_id values must be unique within a trace")
        object.__setattr__(self, "protected_evidence", protected)
        if not isinstance(self.gist, str) or not self.gist.strip():
            raise ValueError("memory trace gist is required")
        normalized_details = _tuple_of_type(self.details, TraceDetail, "details")
        detail_ids = tuple(detail.detail_id for detail in normalized_details)
        if len(set(detail_ids)) != len(detail_ids):
            raise ValueError("detail_id values must be unique within a MemoryTrace")
        object.__setattr__(self, "details", normalized_details)

        normalized_states = _tuple_of_type(
            self.detail_states,
            TraceDetailState,
            "detail_states",
        )
        if not normalized_states and normalized_details:
            normalized_states = tuple(
                TraceDetailState(detail_id=detail.detail_id)
                for detail in normalized_details
            )
        state_ids = tuple(state.detail_id for state in normalized_states)
        if len(set(state_ids)) != len(state_ids):
            raise ValueError(
                "detail_states detail_id values must be unique within a MemoryTrace"
            )
        if state_ids != detail_ids:
            raise ValueError(
                "detail_states must exactly match details in canonical detail order"
            )
        object.__setattr__(self, "detail_states", normalized_states)

        normalized_representations = _tuple_of_type(
            self.subjective_representations,
            SubjectiveDetailRepresentation,
            "subjective_representations",
        )
        if not normalized_representations and normalized_details:
            normalized_representations = tuple(
                _make_subjective_detail_representation(
                    detail_id=detail.detail_id
                )
                for detail in normalized_details
            )
        representation_ids = tuple(
            item.detail_id for item in normalized_representations
        )
        if representation_ids != detail_ids:
            raise ValueError(
                "subjective_representations must exactly match details in canonical order"
            )
        for detail, representation in zip(
            normalized_details,
            normalized_representations,
        ):
            if (
                representation.temporal_form
                is SubjectiveTemporalForm.GENERALIZED
                and detail.temporal_semantics is None
            ):
                raise ValueError(
                    "generalized representation requires structured temporal semantics"
                )
        object.__setattr__(
            self,
            "subjective_representations",
            normalized_representations,
        )
        for field_name in (
            "temporal_cues",
            "actor_refs",
            "object_refs",
            "encoding_affect",
            "source_cues",
            "competing_trace_ids",
        ):
            object.__setattr__(
                self,
                field_name,
                _tuple_of_strings(getattr(self, field_name), field_name),
            )
        for field_name in ("strength", "accessibility", "familiarity"):
            object.__setattr__(
                self,
                field_name,
                _unit(getattr(self, field_name), field_name),
            )
        object.__setattr__(
            self,
            "rehearsal_count",
            _nonnegative_int(self.rehearsal_count, "rehearsal_count"),
        )
        object.__setattr__(
            self,
            "retrieval_count",
            _nonnegative_int(self.retrieval_count, "retrieval_count"),
        )
        for field_name in (
            "parent_trace_id",
            "reconsolidation_decision_fingerprint",
            "reconsolidation_event_id",
        ):
            value = getattr(self, field_name)
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ValueError(f"{field_name} must be a non-blank string or None")

        lineage_payload = {
            "subject_id": self.subject_id,
            "protected_evidence": [asdict(ref) for ref in self.protected_evidence],
        }
        object.__setattr__(
            self,
            "trace_lineage_id",
            "trace_lineage_" + _stable_sha256(lineage_payload)[:24],
        )
        snapshot_payload = {
            "trace_lineage_id": self.trace_lineage_id,
            "version": self.version,
            "gist": self.gist,
            "details": [asdict(detail) for detail in self.details],
            "detail_states": [asdict(state) for state in self.detail_states],
            "subjective_representations": [
                asdict(item) for item in self.subjective_representations
            ],
            "temporal_cues": self.temporal_cues,
            "actor_refs": self.actor_refs,
            "object_refs": self.object_refs,
            "encoding_affect": self.encoding_affect,
            "source_cues": self.source_cues,
            "strength": self.strength,
            "accessibility": self.accessibility,
            "familiarity": self.familiarity,
            "rehearsal_count": self.rehearsal_count,
            "retrieval_count": self.retrieval_count,
            "competing_trace_ids": self.competing_trace_ids,
            "parent_trace_id": self.parent_trace_id,
            "reconsolidation_decision_fingerprint": self.reconsolidation_decision_fingerprint,
            "reconsolidation_event_id": self.reconsolidation_event_id,
        }
        object.__setattr__(
            self,
            "trace_id",
            "trace_" + _stable_sha256(snapshot_payload)[:24],
        )

    def subjective_representation(
        self,
        detail_id: str,
    ) -> SubjectiveDetailRepresentation:
        if not isinstance(detail_id, str) or not detail_id.strip():
            raise ValueError("detail_id is required")
        for representation in self.subjective_representations:
            if representation.detail_id == detail_id:
                return representation
        raise KeyError(detail_id)

    def detail_state(self, detail_id: str) -> TraceDetailState:
        if not isinstance(detail_id, str) or not detail_id.strip():
            raise ValueError("detail_id is required")
        for state in self.detail_states:
            if state.detail_id == detail_id:
                return state
        raise KeyError(detail_id)

    @property
    def protected_evidence_digest(self) -> str:
        return _stable_sha256([asdict(ref) for ref in self.protected_evidence])

    @property
    def snapshot_digest(self) -> str:
        return _stable_sha256(asdict(self))

    def stable_json(self) -> str:
        return _stable_json(asdict(self))


@dataclass(frozen=True)
class RetrievalEpisode:
    """Explicit occurrence identity for one recall attempt."""

    episode_id: str
    subject_id: str
    tick: int
    cue_text: str
    candidate_trace_ids: tuple[str, ...]
    context_refs: tuple[str, ...] = ()
    subject_state_digest: str = ""
    reconstruction_rule_version: str = "uppb-p4-v1"

    def __post_init__(self) -> None:
        if not isinstance(self.episode_id, str) or not self.episode_id.strip():
            raise ValueError("episode_id is required")
        if not isinstance(self.subject_id, str) or not self.subject_id.strip():
            raise ValueError("subject_id is required")
        _nonnegative_int(self.tick, "tick")
        if not isinstance(self.cue_text, str) or not self.cue_text.strip():
            raise ValueError("cue_text is required")
        candidates = _tuple_of_strings(
            self.candidate_trace_ids,
            "candidate_trace_ids",
        )
        if not candidates:
            raise ValueError("retrieval episode requires candidate traces")
        if len(set(candidates)) != len(candidates):
            raise ValueError("candidate_trace_ids cannot contain duplicates")
        object.__setattr__(self, "candidate_trace_ids", candidates)
        object.__setattr__(
            self,
            "context_refs",
            _tuple_of_strings(self.context_refs, "context_refs"),
        )
        if not isinstance(self.subject_state_digest, str):
            raise TypeError("subject_state_digest must be a string")
        if (
            not isinstance(self.reconstruction_rule_version, str)
            or not self.reconstruction_rule_version.strip()
        ):
            raise ValueError("reconstruction_rule_version is required")

    @property
    def cue_fingerprint(self) -> str:
        return _stable_sha256(
            {
                "cue_text": self.cue_text,
                "context_refs": self.context_refs,
                "subject_state_digest": self.subject_state_digest,
            }
        )

    @property
    def occurrence_fingerprint(self) -> str:
        return _stable_sha256(asdict(self))

    def stable_json(self) -> str:
        return _stable_json(asdict(self))


@dataclass(frozen=True)
class ReconstructionConfig:
    max_details: int = 3
    minimum_detail_score: float = 0.0

    def __post_init__(self) -> None:
        if isinstance(self.max_details, bool) or not isinstance(self.max_details, int):
            raise TypeError("max_details must be a non-boolean integer")
        if self.max_details < 0:
            raise ValueError("max_details cannot be negative")
        object.__setattr__(
            self,
            "minimum_detail_score",
            _unit(self.minimum_detail_score, "minimum_detail_score"),
        )

    @property
    def fingerprint(self) -> str:
        return _stable_sha256(
            {
                "max_details": self.max_details,
                "minimum_detail_score": self.minimum_detail_score,
            }
        )


@dataclass(frozen=True, init=False)
class RecollectionCandidate:
    """Verified nonfinal P4 reconstruction.

    Public callers may inspect and type-check candidates, but canonical
    candidates can only be created by the module reconstruction factory.
    """

    candidate_id: str
    subject_id: str
    retrieval_episode_id: str
    retrieval_episode_fingerprint: str
    reconstruction_config_fingerprint: str
    reconstruction_rule_version: str
    trace_ids: tuple[str, ...]
    protected_evidence_refs: tuple[str, ...]
    reconstructed_scene: str
    included_detail_refs: tuple[str, ...]
    omitted_detail_refs: tuple[str, ...]
    detail_omissions: tuple[DetailOmission, ...]
    recalled_detail_states: tuple[RecalledDetailState, ...]
    vividness: VividnessBand
    content_confidence: float
    fragmented: bool
    blended: bool
    reconstruction_operations: tuple[str, ...]

    def __init__(self, *, _factory_token: object = None) -> None:
        if _factory_token is not _RECOLLECTION_CANDIDATE_FACTORY_TOKEN:
            raise TypeError(
                "RecollectionCandidate is factory-controlled; "
                "use reconstruct_recollection()"
            )

    @property
    def candidate_digest(self) -> str:
        return _stable_sha256(asdict(self))

    def stable_json(self) -> str:
        return _stable_json(asdict(self))


def _make_recollection_candidate(
    *,
    subject_id: str,
    retrieval_episode_id: str,
    retrieval_episode_fingerprint: str,
    reconstruction_config_fingerprint: str,
    reconstruction_rule_version: str,
    trace_ids: Iterable[str],
    protected_evidence_refs: Iterable[str],
    reconstructed_scene: str,
    included_detail_refs: Iterable[str],
    omitted_detail_refs: Iterable[str],
    detail_omissions: Iterable[DetailOmission],
    recalled_detail_states: Iterable[RecalledDetailState],
    vividness: VividnessBand,
    content_confidence: float,
    fragmented: bool,
    blended: bool,
    reconstruction_operations: Iterable[str],
) -> RecollectionCandidate:
    """Canonical construction gate for verified P4 reconstruction output."""

    for name, value in (
        ("subject_id", subject_id),
        ("retrieval_episode_id", retrieval_episode_id),
        ("retrieval_episode_fingerprint", retrieval_episode_fingerprint),
        ("reconstruction_config_fingerprint", reconstruction_config_fingerprint),
        ("reconstruction_rule_version", reconstruction_rule_version),
        ("reconstructed_scene", reconstructed_scene),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} is required")

    normalized_trace_ids = _tuple_of_strings(trace_ids, "trace_ids")
    if not normalized_trace_ids:
        raise ValueError("RecollectionCandidate requires trace_ids")
    normalized_protected_refs = _tuple_of_strings(
        protected_evidence_refs,
        "protected_evidence_refs",
    )
    normalized_included = _tuple_of_strings(
        included_detail_refs,
        "included_detail_refs",
    )
    normalized_omitted = _tuple_of_strings(
        omitted_detail_refs,
        "omitted_detail_refs",
    )
    normalized_omission_details = _tuple_of_type(
        detail_omissions,
        DetailOmission,
        "detail_omissions",
    )
    if tuple(item.detail_ref for item in normalized_omission_details) != normalized_omitted:
        raise ValueError(
            "detail_omissions must exactly match omitted_detail_refs in canonical order"
        )
    normalized_recalled_states = _tuple_of_type(
        recalled_detail_states,
        RecalledDetailState,
        "recalled_detail_states",
    )
    if tuple(item.detail_ref for item in normalized_recalled_states) != normalized_included:
        raise ValueError(
            "recalled_detail_states must exactly match included_detail_refs in order"
        )
    normalized_operations = _tuple_of_strings(
        reconstruction_operations,
        "reconstruction_operations",
    )
    if not isinstance(vividness, VividnessBand):
        raise TypeError("vividness must be VividnessBand")
    normalized_confidence = _unit(content_confidence, "content_confidence")
    if not isinstance(fragmented, bool):
        raise TypeError("fragmented must be bool")
    if not isinstance(blended, bool):
        raise TypeError("blended must be bool")

    identity_payload = {
        "subject_id": subject_id,
        "retrieval_episode_id": retrieval_episode_id,
        "retrieval_episode_fingerprint": retrieval_episode_fingerprint,
        "reconstruction_config_fingerprint": reconstruction_config_fingerprint,
        "reconstruction_rule_version": reconstruction_rule_version,
        "trace_ids": normalized_trace_ids,
        "protected_evidence_refs": normalized_protected_refs,
        "reconstructed_scene": reconstructed_scene,
        "included_detail_refs": normalized_included,
        "omitted_detail_refs": normalized_omitted,
        "detail_omissions": [asdict(item) for item in normalized_omission_details],
        "recalled_detail_states": [asdict(item) for item in normalized_recalled_states],
        "vividness": vividness.value,
        "content_confidence": normalized_confidence,
        "fragmented": fragmented,
        "blended": blended,
        "reconstruction_operations": normalized_operations,
    }

    candidate = RecollectionCandidate(
        _factory_token=_RECOLLECTION_CANDIDATE_FACTORY_TOKEN
    )
    for field_name, value in (
        ("subject_id", subject_id),
        ("retrieval_episode_id", retrieval_episode_id),
        ("retrieval_episode_fingerprint", retrieval_episode_fingerprint),
        ("reconstruction_config_fingerprint", reconstruction_config_fingerprint),
        ("reconstruction_rule_version", reconstruction_rule_version),
        ("trace_ids", normalized_trace_ids),
        ("protected_evidence_refs", normalized_protected_refs),
        ("reconstructed_scene", reconstructed_scene),
        ("included_detail_refs", normalized_included),
        ("omitted_detail_refs", normalized_omitted),
        ("detail_omissions", normalized_omission_details),
        ("recalled_detail_states", normalized_recalled_states),
        ("vividness", vividness),
        ("content_confidence", normalized_confidence),
        ("fragmented", fragmented),
        ("blended", blended),
        ("reconstruction_operations", normalized_operations),
    ):
        object.__setattr__(candidate, field_name, value)
    object.__setattr__(
        candidate,
        "candidate_id",
        "recollection_candidate_" + _stable_sha256(identity_payload)[:24],
    )
    return candidate


def _vividness(score: float) -> VividnessBand:
    if score < 0.25:
        return VividnessBand.FAINT
    if score < 0.50:
        return VividnessBand.WEAK
    if score < 0.78:
        return VividnessBand.MODERATE
    return VividnessBand.VIVID


def _detail_metrics(
    detail: TraceDetail,
    cue_tokens: set[str],
    trace: MemoryTrace,
) -> tuple[float, float]:
    rendered_detail = _subjective_detail_text(trace, detail)
    cue_term_tokens = _tokens(" ".join(detail.cue_terms))
    representation = trace.subjective_representation(detail.detail_id)
    if (
        representation.temporal_form is SubjectiveTemporalForm.GENERALIZED
        and detail.temporal_semantics is not None
    ):
        exact_only_tokens = (
            _tokens(detail.temporal_semantics.exact_phrase)
            - _tokens(detail.temporal_semantics.generalized_phrase)
        )
        cue_term_tokens -= exact_only_tokens
    detail_tokens = _tokens(rendered_detail) | cue_term_tokens
    if cue_tokens:
        overlap = len(cue_tokens & detail_tokens) / max(1, len(cue_tokens))
    else:
        overlap = 0.0
    state = trace.detail_state(detail.detail_id)
    base = (
        0.45 * trace.accessibility * state.accessibility
        + 0.30 * trace.strength * state.retention
        + 0.15 * trace.familiarity * state.association_strength
        + 0.10 * overlap * state.association_strength
    )
    # Strong matching cues retain a recovery path even after accessibility
    # weakens. P6B/P6C model forgetting as degraded access rather than
    # destructive deletion of retained semantic content.
    score = max(0.0, min(1.0, base + 0.35 * overlap))
    return score, overlap


def _temporal_precision(state: TraceDetailState) -> TemporalPrecision:
    if state.temporal_confidence >= 0.75:
        return TemporalPrecision.PRECISE
    if state.temporal_confidence >= 0.40:
        return TemporalPrecision.APPROXIMATE
    return TemporalPrecision.UNCERTAIN


def _contextual_association(state: TraceDetailState) -> ContextAssociation:
    if state.association_strength >= 0.75:
        return ContextAssociation.STRONG
    if state.association_strength >= 0.40:
        return ContextAssociation.MODERATE
    return ContextAssociation.WEAK


def _subjective_detail_text(
    trace: MemoryTrace,
    detail: TraceDetail,
) -> str:
    representation = trace.subjective_representation(detail.detail_id)
    if (
        representation.temporal_form is SubjectiveTemporalForm.GENERALIZED
    ):
        if detail.temporal_semantics is None or detail.temporal_template is None:
            raise ValueError(
                "generalized subjective representation lacks temporal semantics"
            )
        return detail.temporal_template.format(
            temporal=detail.temporal_semantics.generalized_phrase
        )
    return detail.text


def reconstruct_recollection(
    traces: Iterable[MemoryTrace],
    episode: RetrievalEpisode,
    *,
    config: ReconstructionConfig | None = None,
) -> RecollectionCandidate:
    """Deterministically reconstruct a nonfinal recollection candidate."""

    config = config or ReconstructionConfig()
    trace_values = tuple(traces)
    if not trace_values:
        raise ValueError("reconstruction requires at least one MemoryTrace")
    if any(not isinstance(trace, MemoryTrace) for trace in trace_values):
        raise TypeError("traces must contain only MemoryTrace values")
    if any(trace.subject_id != episode.subject_id for trace in trace_values):
        raise ValueError("all traces must belong to the retrieval subject")

    trace_by_id = {trace.trace_id: trace for trace in trace_values}
    if len(trace_by_id) != len(trace_values):
        raise ValueError("duplicate trace snapshots are not allowed")
    if set(trace_by_id) != set(episode.candidate_trace_ids):
        raise ValueError(
            "retrieval episode candidate_trace_ids must exactly match supplied trace snapshots"
        )

    ordered = tuple(trace_by_id[trace_id] for trace_id in episode.candidate_trace_ids)
    cue_tokens = _tokens(episode.cue_text)

    ranked_details: list[tuple[float, int, TraceDetail, float]] = []
    for trace_index, trace in enumerate(ordered):
        for detail in trace.details:
            score, overlap = _detail_metrics(detail, cue_tokens, trace)
            ranked_details.append((score, trace_index, detail, overlap))
    ranked_details.sort(
        key=lambda item: (item[0], -item[1], item[2].detail_id),
        reverse=True,
    )

    eligible = [
        item
        for item in ranked_details
        if item[0] >= config.minimum_detail_score
    ]
    included = eligible[: config.max_details]
    included_detail_refs = tuple(
        f"{ordered[trace_index].trace_id}:{detail.detail_id}"
        for _, trace_index, detail, _ in included
    )
    included_set = set(included_detail_refs)
    rank_by_ref = {
        f"{ordered[trace_index].trace_id}:{detail.detail_id}": (
            rank,
            score,
            overlap,
        )
        for rank, (score, trace_index, detail, overlap) in enumerate(ranked_details)
    }

    detail_omissions: list[DetailOmission] = []
    for trace in ordered:
        for detail in trace.details:
            detail_ref = f"{trace.trace_id}:{detail.detail_id}"
            if detail_ref in included_set:
                continue
            rank, score, overlap = rank_by_ref[detail_ref]
            if score >= config.minimum_detail_score:
                cause = OmissionCause.CAPACITY_LIMITED
            elif cue_tokens and overlap == 0.0:
                cause = OmissionCause.CUE_MISMATCH
            else:
                cause = OmissionCause.BELOW_RETRIEVAL_THRESHOLD
            detail_omissions.append(
                DetailOmission(
                    detail_ref=detail_ref,
                    cause=cause,
                    score=score,
                    cue_overlap=overlap,
                    rank=rank,
                    retrieval_threshold=config.minimum_detail_score,
                )
            )
    omitted_detail_refs = tuple(item.detail_ref for item in detail_omissions)

    recalled_detail_states = tuple(
        RecalledDetailState(
            detail_ref=f"{ordered[trace_index].trace_id}:{detail.detail_id}",
            temporal_precision=_temporal_precision(
                ordered[trace_index].detail_state(detail.detail_id)
            ),
            contextual_association=_contextual_association(
                ordered[trace_index].detail_state(detail.detail_id)
            ),
            subjective_representation_fingerprint=(
                ordered[trace_index]
                .subjective_representation(detail.detail_id)
                .representation_fingerprint
            ),
            temporal_form=(
                ordered[trace_index]
                .subjective_representation(detail.detail_id)
                .temporal_form
            ),
        )
        for _, trace_index, detail, _ in included
    )

    gist_parts = [trace.gist.strip().rstrip(".") for trace in ordered]
    detail_parts = [
        _subjective_detail_text(ordered[item[1]], item[2]).strip().rstrip(".")
        for item in included
    ]
    scene_parts = gist_parts + detail_parts
    reconstructed_scene = ". ".join(part for part in scene_parts if part) + "."
    if any(
        item.temporal_precision is TemporalPrecision.UNCERTAIN
        for item in recalled_detail_states
    ):
        reconstructed_scene += " The timing feels uncertain."
    elif any(
        item.temporal_precision is TemporalPrecision.APPROXIMATE
        for item in recalled_detail_states
    ):
        reconstructed_scene += " The timing feels approximate."
    if any(
        item.contextual_association is ContextAssociation.WEAK
        for item in recalled_detail_states
    ):
        reconstructed_scene += (
            " Some details feel weakly connected to the surrounding context."
        )

    average_quality = sum(
        (trace.strength + trace.accessibility + trace.familiarity) / 3.0
        for trace in ordered
    ) / len(ordered)
    mean_detail_score = (
        sum(item[0] for item in included) / len(included)
        if included
        else average_quality * 0.5
    )
    content_confidence = max(
        0.0,
        min(1.0, 0.6 * average_quality + 0.4 * mean_detail_score),
    )
    vividness = _vividness(
        max(
            0.0,
            min(
                1.0,
                0.45 * average_quality
                + 0.35 * mean_detail_score
                + 0.20 * min(1.0, len(included) / max(1, config.max_details)),
            ),
        )
    )

    operations = ["retrieve_gist"]
    if included:
        operations.append("retrieve_details")
    if omitted_detail_refs:
        operations.append("omit_details")
    if len(ordered) > 1:
        operations.append("blend_traces")

    protected_refs = tuple(
        ref.evidence_id
        for trace in ordered
        for ref in trace.protected_evidence
    )
    return _make_recollection_candidate(
        subject_id=episode.subject_id,
        retrieval_episode_id=episode.episode_id,
        retrieval_episode_fingerprint=episode.occurrence_fingerprint,
        reconstruction_config_fingerprint=config.fingerprint,
        reconstruction_rule_version=episode.reconstruction_rule_version,
        trace_ids=tuple(trace.trace_id for trace in ordered),
        protected_evidence_refs=protected_refs,
        reconstructed_scene=reconstructed_scene,
        included_detail_refs=included_detail_refs,
        omitted_detail_refs=omitted_detail_refs,
        detail_omissions=tuple(detail_omissions),
        recalled_detail_states=recalled_detail_states,
        vividness=vividness,
        content_confidence=content_confidence,
        fragmented=bool(omitted_detail_refs),
        blended=len(ordered) > 1,
        reconstruction_operations=tuple(operations),
    )
