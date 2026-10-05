"""Universal Phenomenal-Projection Boundary value objects.

P1 is intentionally non-invasive. These immutable objects define the semantic
contract between implementation-native state and future subject-accessible
experience. They do not yet alter Pretorius cognition, memory, or rendering.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


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


@dataclass(frozen=True)
class ObjectiveProvenance:
    """Engineer-visible origin truth.

    This structure is intentionally separate from subjective source attribution.
    A future character may misattribute a memory while this record remains true.
    """

    evidence_class: str
    source: str
    external: bool = False
    confidence: float = 1.0
    record_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.evidence_class.strip():
            raise ValueError("objective provenance evidence_class is required")
        if not self.source.strip():
            raise ValueError("objective provenance source is required")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("objective provenance confidence must be between 0 and 1")


@dataclass(frozen=True)
class SubjectiveSourceAttribution:
    """The source a subject currently believes or feels a representation has."""

    kind: SubjectiveSourceKind = SubjectiveSourceKind.UNKNOWN
    certainty: CertaintyBand = CertaintyBand.MODERATE


@dataclass(frozen=True)
class PhenomenalEvent:
    """Immutable subject-native semantic event with hidden audit lineage.

    canonical_first_person is the subject-native realization. Objective
    provenance and implementation references remain engineer-visible lineage,
    not ordinary subject-accessible content.
    """

    event_id: str
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

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("phenomenal event_id is required")
        if self.tick < 0:
            raise ValueError("phenomenal tick cannot be negative")
        if not self.subject_id.strip():
            raise ValueError("phenomenal subject_id is required")
        if not self.canonical_first_person.strip():
            raise ValueError("canonical first-person realization is required")
        if not self.projection_rule_version.strip():
            raise ValueError("projection_rule_version is required")
        if not self.source_state_digest.strip():
            raise ValueError("source_state_digest is required")

    @property
    def subject_text(self) -> str:
        """The ordinary content made available to the subject."""
        return self.canonical_first_person

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
    """A current subjective recollection derived from one or more memory traces.

    The recollection is allowed to disagree with objective provenance. The
    mismatch is represented rather than repaired by overwriting either side.
    """

    event: PhenomenalEvent
    trace_refs: tuple[str, ...]
    subjective_source: SubjectiveSourceAttribution
    subjective_certainty: CertaintyBand
    vividness: VividnessBand
    fragmented: bool = False

    def __post_init__(self) -> None:
        if self.event.mode is not PhenomenalMode.RECOLLECTION:
            raise ValueError("Recollection.event must use PhenomenalMode.RECOLLECTION")
        if not self.trace_refs:
            raise ValueError("Recollection requires at least one trace reference")

    @property
    def subject_text(self) -> str:
        return self.event.subject_text

    def engineer_view(self) -> dict[str, Any]:
        return asdict(self)

    def stable_json(self) -> str:
        return json.dumps(
            self.engineer_view(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
