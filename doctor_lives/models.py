from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Provenance:
    evidence_class: str
    source: str
    external: bool = False
    confidence: float = 1.0
    inherited: bool = False


@dataclass(frozen=True)
class Experience:
    text: str
    source: str = "world"
    kind: str = "observation"
    valence: float = 0.0
    arousal: float = 0.0
    social: float = 0.0
    authority: float = 0.0
    autonomy: float = 0.0
    novelty: float = 0.0
    achievement: float = 0.0
    isolation: float = 0.0
    threat: float = 0.0
    intimacy: float = 0.0
    control: float = 0.0
    creation: float = 0.0
    actor: str | None = None
    external: bool = False
    confidence: float = 1.0
    tags: tuple[str, ...] = ()

    def scalars(self) -> dict[str, float]:
        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "social": self.social,
            "authority": self.authority,
            "autonomy": self.autonomy,
            "novelty": self.novelty,
            "achievement": self.achievement,
            "isolation": self.isolation,
            "threat": self.threat,
            "intimacy": self.intimacy,
            "control": self.control,
            "creation": self.creation,
        }


@dataclass(frozen=True)
class ViewItem:
    record_id: str
    source: str
    first_person: str
    salience: float
    provenance: Provenance
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class CognitiveView:
    tick: int
    identity: tuple[str, ...]
    experiences: tuple[ViewItem, ...]
    felt_state: dict[str, str]
    relationships: tuple[dict[str, Any], ...]
    concerns: tuple[dict[str, Any], ...]
    commitments: tuple[dict[str, Any], ...]
    action_tendencies: dict[str, float]
    private_state_version: int


@dataclass(frozen=True)
class RenderRequest:
    schema: str
    subject: str
    tick: int
    first_person_context: tuple[str, ...]
    action_tendencies: dict[str, float]
    relationship_context: tuple[dict[str, Any], ...]
    unresolved_context: tuple[dict[str, Any], ...]
    epistemic_rules: tuple[str, ...]
    renderer_rules: tuple[str, ...]
    provenance_summary: dict[str, int]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
