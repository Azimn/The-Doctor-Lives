"""P6D controlled subjective-memory distortion primitives.

This module does not mutate protected evidence or TraceDetail semantic truth.
It proposes deterministic, auditable transformations of the separate
SubjectiveDetailRepresentation carried by a MemoryTrace.

Initial P6D supports temporal generalization only. It deliberately does not
invent novel propositions or rewrite arbitrary text.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

from .recollection import (
    MemoryTrace,
    RecollectionCandidate,
    SubjectiveDetailRepresentation,
    SubjectiveTemporalForm,
    TemporalPrecision,
)


_DISTORTION_CANDIDATE_FACTORY_TOKEN = object()


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _stable_sha256(value: Any) -> str:
    return hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


class DistortionKind(StrEnum):
    """Reviewed classes of subjective-memory transformation."""

    TEMPORAL_GENERALIZATION = "temporal_generalization"


@dataclass(frozen=True, init=False)
class DistortionCandidate:
    """Factory-controlled proposal for one bounded subjective transformation."""

    distortion_id: str
    kind: DistortionKind
    subject_id: str
    old_trace_id: str
    old_trace_digest: str
    detail_id: str
    detail_semantic_fingerprint: str
    parent_representation_fingerprint: str
    p4_candidate_id: str
    p4_candidate_digest: str
    recalled_detail_ref: str
    driver_state_fingerprint: str
    driver_temporal_confidence: float
    exact_temporal_phrase: str
    generalized_temporal_phrase: str
    output_temporal_form: SubjectiveTemporalForm
    reason_code: str
    rule_version: str
    distortion_fingerprint: str

    def __init__(self, *, _factory_token: object = None) -> None:
        if _factory_token is not _DISTORTION_CANDIDATE_FACTORY_TOKEN:
            raise TypeError(
                "DistortionCandidate is factory-controlled; "
                "use propose_temporal_generalization()"
            )

    def stable_json(self) -> str:
        return _stable_json(asdict(self))


@dataclass(frozen=True)
class RepresentationOperation:
    """One reviewed transition of a subjective-memory representation."""

    detail_id: str
    kind: DistortionKind
    old_temporal_form: SubjectiveTemporalForm
    new_temporal_form: SubjectiveTemporalForm
    old_representation_fingerprint: str
    new_representation_fingerprint: str
    distortion_candidate_fingerprint: str
    reason_code: str

    def __post_init__(self) -> None:
        if not isinstance(self.detail_id, str) or not self.detail_id.strip():
            raise ValueError("detail_id is required")
        if not isinstance(self.kind, DistortionKind):
            raise TypeError("kind must be DistortionKind")
        if not isinstance(self.old_temporal_form, SubjectiveTemporalForm):
            raise TypeError("old_temporal_form must be SubjectiveTemporalForm")
        if not isinstance(self.new_temporal_form, SubjectiveTemporalForm):
            raise TypeError("new_temporal_form must be SubjectiveTemporalForm")
        if (
            self.kind is DistortionKind.TEMPORAL_GENERALIZATION
            and (
                self.old_temporal_form is not SubjectiveTemporalForm.EXACT
                or self.new_temporal_form
                is not SubjectiveTemporalForm.GENERALIZED
            )
        ):
            raise ValueError(
                "temporal generalization must transition EXACT -> GENERALIZED"
            )
        for name in (
            "old_representation_fingerprint",
            "new_representation_fingerprint",
            "distortion_candidate_fingerprint",
            "reason_code",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")

    @property
    def fingerprint(self) -> str:
        return "representation_operation_" + _stable_sha256(asdict(self))[:24]


def _make_distortion_candidate(**payload: Any) -> DistortionCandidate:
    candidate = DistortionCandidate(
        _factory_token=_DISTORTION_CANDIDATE_FACTORY_TOKEN
    )
    for name, value in payload.items():
        object.__setattr__(candidate, name, value)
    fingerprint_payload = dict(payload)
    fingerprint = "distortion_" + _stable_sha256(fingerprint_payload)[:24]
    object.__setattr__(candidate, "distortion_fingerprint", fingerprint)
    object.__setattr__(candidate, "distortion_id", fingerprint)
    return candidate


def propose_temporal_generalization(
    *,
    old_trace: MemoryTrace,
    candidate: RecollectionCandidate,
    detail_id: str,
    max_temporal_confidence: float,
    rule_version: str = "uppb-p6d-temporal-v1",
) -> DistortionCandidate | None:
    """Propose structured exact-time -> broader-time generalization.

    The proposal is derived only from the verified P4 reconstruction and the
    current trace's subject-memory state. Omission cause and source attribution
    are deliberately not inputs.
    """

    if not isinstance(old_trace, MemoryTrace):
        raise TypeError("old_trace must be MemoryTrace")
    if not isinstance(candidate, RecollectionCandidate):
        raise TypeError("candidate must be RecollectionCandidate")
    if not isinstance(detail_id, str) or not detail_id.strip():
        raise ValueError("detail_id is required")
    if isinstance(max_temporal_confidence, bool) or not isinstance(
        max_temporal_confidence,
        (int, float),
    ):
        raise TypeError("max_temporal_confidence must be numeric")
    threshold = float(max_temporal_confidence)
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("max_temporal_confidence must be between 0 and 1")
    if not isinstance(rule_version, str) or not rule_version.strip():
        raise ValueError("rule_version is required")
    if candidate.subject_id != old_trace.subject_id:
        raise ValueError("candidate subject does not match trace")
    if old_trace.trace_id not in candidate.trace_ids:
        raise ValueError("candidate does not include old trace")
    if candidate.blended or len(candidate.trace_ids) != 1:
        return None

    detail = next(
        (item for item in old_trace.details if item.detail_id == detail_id),
        None,
    )
    if detail is None:
        raise KeyError(detail_id)
    if detail.temporal_semantics is None:
        return None
    representation = old_trace.subjective_representation(detail_id)
    if representation.temporal_form is not SubjectiveTemporalForm.EXACT:
        return None
    state = old_trace.detail_state(detail_id)
    if state.temporal_confidence > threshold:
        return None

    detail_ref = f"{old_trace.trace_id}:{detail_id}"
    if detail_ref not in candidate.included_detail_refs:
        return None
    recalled = next(
        (
            item
            for item in candidate.recalled_detail_states
            if item.detail_ref == detail_ref
        ),
        None,
    )
    if recalled is None:
        raise ValueError("included detail lacks recalled-detail state")
    if recalled.temporal_precision is not TemporalPrecision.UNCERTAIN:
        return None
    if (
        recalled.subjective_representation_fingerprint
        != representation.representation_fingerprint
    ):
        raise ValueError("P4 candidate representation binding mismatch")

    return _make_distortion_candidate(
        kind=DistortionKind.TEMPORAL_GENERALIZATION,
        subject_id=old_trace.subject_id,
        old_trace_id=old_trace.trace_id,
        old_trace_digest=old_trace.snapshot_digest,
        detail_id=detail_id,
        detail_semantic_fingerprint=detail.semantic_fingerprint,
        parent_representation_fingerprint=(
            representation.representation_fingerprint
        ),
        p4_candidate_id=candidate.candidate_id,
        p4_candidate_digest=candidate.candidate_digest,
        recalled_detail_ref=detail_ref,
        driver_state_fingerprint=state.state_fingerprint,
        driver_temporal_confidence=state.temporal_confidence,
        exact_temporal_phrase=detail.temporal_semantics.exact_phrase,
        generalized_temporal_phrase=(
            detail.temporal_semantics.generalized_phrase
        ),
        output_temporal_form=SubjectiveTemporalForm.GENERALIZED,
        reason_code="uncertain_recalled_time_generalized",
        rule_version=rule_version,
    )


def verify_distortion_candidate(distortion: DistortionCandidate) -> None:
    """Fail closed if a canonical distortion proposal was altered after creation."""

    if not isinstance(distortion, DistortionCandidate):
        raise TypeError("distortion must be DistortionCandidate")
    payload = asdict(distortion)
    stored_id = payload.pop("distortion_id")
    stored_fingerprint = payload.pop("distortion_fingerprint")
    expected = "distortion_" + _stable_sha256(payload)[:24]
    if stored_fingerprint != expected or stored_id != expected:
        raise ValueError("distortion candidate fingerprint mismatch")
    if not isinstance(distortion.kind, DistortionKind):
        raise TypeError("distortion candidate kind is invalid")
    if not isinstance(
        distortion.output_temporal_form,
        SubjectiveTemporalForm,
    ):
        raise TypeError("distortion output temporal form is invalid")


def build_representation_operation(
    *,
    old_trace: MemoryTrace,
    distortion: DistortionCandidate,
) -> tuple[RepresentationOperation, SubjectiveDetailRepresentation]:
    """Build the exact representation transition authorized by a proposal."""

    verify_distortion_candidate(distortion)
    if distortion.old_trace_id != old_trace.trace_id:
        raise ValueError("distortion candidate trace ID mismatch")
    if distortion.old_trace_digest != old_trace.snapshot_digest:
        raise ValueError("distortion candidate trace digest mismatch")
    detail = next(
        (
            item
            for item in old_trace.details
            if item.detail_id == distortion.detail_id
        ),
        None,
    )
    if detail is None:
        raise KeyError(distortion.detail_id)
    if detail.semantic_fingerprint != distortion.detail_semantic_fingerprint:
        raise ValueError("distortion candidate semantic-detail mismatch")
    old_representation = old_trace.subjective_representation(
        distortion.detail_id
    )
    if (
        old_representation.representation_fingerprint
        != distortion.parent_representation_fingerprint
    ):
        raise ValueError("distortion candidate representation parent mismatch")
    if old_representation.temporal_form is not SubjectiveTemporalForm.EXACT:
        raise ValueError("temporal generalization requires exact parent form")

    new_representation = SubjectiveDetailRepresentation(
        detail_id=distortion.detail_id,
        temporal_form=SubjectiveTemporalForm.GENERALIZED,
        parent_representation_fingerprint=(
            old_representation.representation_fingerprint
        ),
        distortion_candidate_fingerprint=(
            distortion.distortion_fingerprint
        ),
    )
    operation = RepresentationOperation(
        detail_id=distortion.detail_id,
        kind=distortion.kind,
        old_temporal_form=old_representation.temporal_form,
        new_temporal_form=new_representation.temporal_form,
        old_representation_fingerprint=(
            old_representation.representation_fingerprint
        ),
        new_representation_fingerprint=(
            new_representation.representation_fingerprint
        ),
        distortion_candidate_fingerprint=(
            distortion.distortion_fingerprint
        ),
        reason_code=distortion.reason_code,
    )
    return operation, new_representation
