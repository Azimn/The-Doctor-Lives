"""Universal Phenomenal-Projection Boundary value objects.

These objects are deliberately stricter than ordinary presentation models.
Subjective fallibility is represented inside the model; mutation of audit
lineage is not. Canonical subject-facing text is validated at construction so
no caller can bypass the UPPB merely by skipping a projector helper.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Iterable


class PhenomenalLeakError(ValueError):
    """Canonical subject-facing text contains implementation-native artifacts."""


_IMPLEMENTATION_TOKENS = (
    "state_pressure",
    "action_score",
    "policy_decision_id",
    "state_version",
    "recurrent_tick",
    "memory_id",
    "source_record_ids",
    "activation_weight",
    "bridge_family",
)

_UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)
_RAW_ASSIGNMENT_RE = re.compile(
    r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*-?\d+(?:\.\d+)?\b"
)


def implementation_leaks(text: str) -> tuple[str, ...]:
    """Return conservative implementation artifacts found in subject text."""
    if not isinstance(text, str):
        raise TypeError("subject-facing text must be a string")
    lowered = text.lower()
    hits = [token for token in _IMPLEMENTATION_TOKENS if token in lowered]
    if _UUID_RE.search(text):
        hits.append("raw_uuid")
    if _RAW_ASSIGNMENT_RE.search(text):
        hits.append("raw_numeric_assignment")
    return tuple(sorted(set(hits)))


def assert_subject_text_safe(text: str) -> None:
    """Fail closed when canonical subject text leaks implementation vocabulary."""
    hits = implementation_leaks(text)
    if hits:
        raise PhenomenalLeakError(
            "subject-facing text contains implementation-native artifacts: "
            + ", ".join(hits)
        )


class PhenomenalMode(StrEnum):
    PERCEPT = "percept"
    BODILY_SENSATION = "bodily_sensation"
    FEELING = "feeling"
    IMPULSE = "impulse"
    RECOLLECTION = "recollection"
    BELIEF = "belief"
    UNCERTAINTY = "uncertainty"
    EXPECTATION = "expectation"
    CONCERN = "concern"
    INTENTION = "intention"
    INTERNAL_THOUGHT = "internal_thought"
    SELF_PERCEPTION = "self_perception"
    METACOGNITIVE_STATE = "metacognitive_state"


class AwarenessLevel(StrEnum):
    LATENT = "latent"
    PRECONSCIOUS = "preconscious"
    CONSCIOUS = "conscious"
    FOCAL = "focal"


class PrivacyState(StrEnum):
    PRIVATE = "private"
    POTENTIALLY_REPORTABLE = "potentially_reportable"
    DELIBERATELY_CONCEALED = "deliberately_concealed"
    COMMUNICATIVE = "communicative"


class SubjectiveSourceKind(StrEnum):
    LIVED = "lived"
    TOLD = "told"
    READ = "read"
    INFERRED = "inferred"
    IMAGINED = "imagined"
    DREAMED = "dreamed"
    SELF_OBSERVED = "self_observed"
    UNKNOWN = "unknown"


class CertaintyBand(StrEnum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class VividnessBand(StrEnum):
    FAINT = "faint"
    WEAK = "weak"
    MODERATE = "moderate"
    VIVID = "vivid"


class IntensityBand(StrEnum):
    TRACE = "trace"
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"
    OVERWHELMING = "overwhelming"


def _require_enum(value: object, enum_type: type[StrEnum], name: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError(f"{name} must be {enum_type.__name__}, not {type(value).__name__}")


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


def _stable_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ObjectiveProvenance:
    """Engineer-visible origin truth, never automatic subjective knowledge."""

    evidence_class: str
    source: str
    external: bool = False
    confidence: float = 1.0
    record_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_class, str) or not self.evidence_class.strip():
            raise ValueError("objective provenance evidence_class is required")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("objective provenance source is required")
        if not isinstance(self.external, bool):
            raise TypeError("objective provenance external must be bool")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("objective provenance confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(
            self, "record_ids", _tuple_of_strings(self.record_ids, "record_ids")
        )


@dataclass(frozen=True)
class SubjectiveSourceAttribution:
    """The source a subject currently believes or feels a representation has."""

    kind: SubjectiveSourceKind = SubjectiveSourceKind.UNKNOWN
    certainty: CertaintyBand = CertaintyBand.MODERATE

    def __post_init__(self) -> None:
        _require_enum(self.kind, SubjectiveSourceKind, "subjective source kind")
        _require_enum(self.certainty, CertaintyBand, "subjective source certainty")


@dataclass(frozen=True)
class PhenomenalEvent:
    """Deeply immutable subject-native semantic event with hidden audit lineage.

    event_id is a deterministic lineage identity. It includes objective
    provenance and source lineage but excludes awareness level, so P3 can route
    the same occurrence without manufacturing a new occurrence ID.

    content_fingerprint identifies the subjective semantic realization and may
    intentionally match across distinct occurrences or provenance.
    """

    tick: int
    subject_id: str
    mode: PhenomenalMode
    awareness: AwarenessLevel
    canonical_first_person: str
    privacy: PrivacyState
    projection_rule_version: str
    source_state_digest: str
    objective_provenance: ObjectiveProvenance
    subjective_source: SubjectiveSourceAttribution = SubjectiveSourceAttribution()
    subjective_certainty: CertaintyBand = CertaintyBand.MODERATE
    subjective_vividness: VividnessBand = VividnessBand.MODERATE
    subjective_intensity: IntensityBand = IntensityBand.MODERATE
    source_state_refs: tuple[str, ...] = ()
    source_event_refs: tuple[str, ...] = ()
    object_refs: tuple[str, ...] = ()
    recollection_parent_id: str | None = None
    reconsolidation_parent_id: str | None = None
    event_id: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.tick, int) or isinstance(self.tick, bool) or self.tick < 0:
            raise ValueError("phenomenal tick must be a non-negative integer")
        if not isinstance(self.subject_id, str) or not self.subject_id.strip():
            raise ValueError("phenomenal subject_id is required")
        _require_enum(self.mode, PhenomenalMode, "phenomenal mode")
        _require_enum(self.awareness, AwarenessLevel, "awareness")
        _require_enum(self.privacy, PrivacyState, "privacy")
        _require_enum(self.subjective_certainty, CertaintyBand, "subjective certainty")
        _require_enum(self.subjective_vividness, VividnessBand, "subjective vividness")
        _require_enum(self.subjective_intensity, IntensityBand, "subjective intensity")
        if not isinstance(self.objective_provenance, ObjectiveProvenance):
            raise TypeError("objective_provenance must be ObjectiveProvenance")
        if not isinstance(self.subjective_source, SubjectiveSourceAttribution):
            raise TypeError("subjective_source must be SubjectiveSourceAttribution")
        if (
            not isinstance(self.canonical_first_person, str)
            or not self.canonical_first_person.strip()
        ):
            raise ValueError("canonical first-person realization is required")
        assert_subject_text_safe(self.canonical_first_person)
        if (
            not isinstance(self.projection_rule_version, str)
            or not self.projection_rule_version.strip()
        ):
            raise ValueError("projection_rule_version is required")
        if (
            not isinstance(self.source_state_digest, str)
            or not self.source_state_digest.strip()
        ):
            raise ValueError("source_state_digest is required")

        for field_name in ("recollection_parent_id", "reconsolidation_parent_id"):
            value = getattr(self, field_name)
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ValueError(f"{field_name} must be a non-blank string or None")

        object.__setattr__(
            self,
            "source_state_refs",
            _tuple_of_strings(self.source_state_refs, "source_state_refs"),
        )
        object.__setattr__(
            self,
            "source_event_refs",
            _tuple_of_strings(self.source_event_refs, "source_event_refs"),
        )
        object.__setattr__(
            self,
            "object_refs",
            _tuple_of_strings(self.object_refs, "object_refs"),
        )
        object.__setattr__(self, "event_id", "phen_" + self.lineage_fingerprint[:24])

    @property
    def subject_text(self) -> str:
        """The ordinary content made available to the subject."""
        return self.canonical_first_person

    @property
    def content_fingerprint(self) -> str:
        """Fingerprint subject semantics independent of objective provenance."""
        return _stable_sha256(
            {
                "mode": self.mode.value,
                "canonical_first_person": self.canonical_first_person,
                "subjective_source": asdict(self.subjective_source),
                "subjective_certainty": self.subjective_certainty.value,
                "subjective_vividness": self.subjective_vividness.value,
                "subjective_intensity": self.subjective_intensity.value,
            }
        )

    @property
    def lineage_fingerprint(self) -> str:
        """Fingerprint the occurrence lineage used by persistent parent links."""
        return _stable_sha256(
            {
                "subject_id": self.subject_id,
                "tick": self.tick,
                "projection_rule_version": self.projection_rule_version,
                "source_state_digest": self.source_state_digest,
                "content_fingerprint": self.content_fingerprint,
                "objective_provenance": asdict(self.objective_provenance),
                "source_state_refs": self.source_state_refs,
                "source_event_refs": self.source_event_refs,
                "object_refs": self.object_refs,
                "recollection_parent_id": self.recollection_parent_id,
                "reconsolidation_parent_id": self.reconsolidation_parent_id,
            }
        )

    def engineer_view(self) -> dict[str, Any]:
        """Complete deterministic audit representation."""
        return asdict(self)

    def stable_json(self) -> str:
        return json.dumps(
            self.engineer_view(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )


@dataclass(frozen=True)
class Recollection:
    """Structural lineage for a current recollection.

    Subjective source attribution, certainty, vividness, and intensity have one
    authority only: the embedded PhenomenalEvent. This wrapper adds trace
    lineage and recollection structure without creating a second subjective
    source of truth.
    """

    event: PhenomenalEvent
    trace_refs: tuple[str, ...]
    fragmented: bool = False
    omitted_detail_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.event, PhenomenalEvent):
            raise TypeError("Recollection.event must be PhenomenalEvent")
        if self.event.mode is not PhenomenalMode.RECOLLECTION:
            raise ValueError("Recollection.event must use PhenomenalMode.RECOLLECTION")
        if not isinstance(self.fragmented, bool):
            raise TypeError("fragmented must be bool")
        trace_refs = _tuple_of_strings(self.trace_refs, "trace_refs")
        if not trace_refs:
            raise ValueError("Recollection requires at least one trace reference")
        object.__setattr__(self, "trace_refs", trace_refs)
        object.__setattr__(
            self,
            "omitted_detail_refs",
            _tuple_of_strings(self.omitted_detail_refs, "omitted_detail_refs"),
        )

    @property
    def subject_text(self) -> str:
        return self.event.subject_text

    @property
    def subjective_source(self) -> SubjectiveSourceAttribution:
        return self.event.subjective_source

    @property
    def subjective_certainty(self) -> CertaintyBand:
        return self.event.subjective_certainty

    @property
    def vividness(self) -> VividnessBand:
        return self.event.subjective_vividness

    def engineer_view(self) -> dict[str, Any]:
        return asdict(self)

    def stable_json(self) -> str:
        return json.dumps(
            self.engineer_view(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
