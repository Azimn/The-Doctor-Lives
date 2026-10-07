from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from typing import Any, Iterable, Mapping

from .phenomenology import (
    AwarenessLevel,
    PhenomenalEvent,
    assert_subject_text_safe,
    control_instruction_markers,
)


@dataclass(frozen=True)
class Provenance:
    evidence_class: str
    source: str
    external: bool = False
    confidence: float = 1.0
    inherited: bool = False
    autobiographical_class: str | None = None
    canon_rank: int | None = None
    continuity: str | None = None
    material_category: str | None = None
    wording: str | None = None
    classification_reasoning: dict[str, Any] | None = None


def _validate_subject_experience_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("experience text must be a string")
    normalized = text.strip()
    if not normalized:
        raise ValueError("experience text is required")
    assert_subject_text_safe(normalized)
    if control_instruction_markers(normalized):
        raise ValueError(
            "raw control-like text cannot be ingested as subject experience; "
            "route it through an ingress projector"
        )
    if not any(char.isalpha() for char in normalized):
        raise ValueError(
            "raw numeric/symbolic input cannot be ingested as subject experience"
        )
    if normalized[:1] in {"{", "["}:
        try:
            decoded = json.loads(normalized)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, (dict, list)):
            raise ValueError(
                "raw structured input cannot be ingested as subject experience"
            )
    return normalized


@dataclass(frozen=True)
class Experience:
    """Subject-native lived input.

    Raw world/body/user/tool/scheduler payloads must be projected before this
    type is constructed. Hidden scalars remain machine-side causal inputs.
    """

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

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", _validate_subject_experience_text(self.text))
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("experience source is required")
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ValueError("experience kind is required")
        if self.actor is not None and (
            not isinstance(self.actor, str) or not self.actor.strip()
        ):
            raise ValueError("experience actor must be a non-blank string or None")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("experience confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "tags", tuple(str(x) for x in self.tags))

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
    """Renderer control-plane packet with one protected character-state surface."""

    schema: str
    subject: str
    subject_frame: "SubjectFrame"
    epistemic_rules: tuple[str, ...]
    renderer_rules: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.subject_frame, SubjectFrame):
            raise TypeError("RenderRequest.subject_frame must be SubjectFrame")

    @property
    def first_person_context(self) -> tuple[str, ...]:
        """Compatibility view of the protected subject frame, never raw state."""
        return self.subject_frame.renderer_context()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "subject": self.subject,
            "subject_frame": list(self.subject_frame.renderer_context()),
            "epistemic_rules": list(self.epistemic_rules),
            "renderer_rules": list(self.renderer_rules),
        }


class SubjectFrameError(ValueError):
    """Subject-facing content is not eligible for the renderer-visible frame."""


_SUBJECT_FRAME_ITEM_FACTORY_TOKEN = object()
_ENGINEER_AUDIT_FACTORY_TOKEN = object()


def _assert_natural_subject_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("subject frame text must be a string")
    normalized = text.strip()
    if not normalized:
        raise SubjectFrameError("subject frame text cannot be blank")
    assert_subject_text_safe(normalized)
    if not any(char.isalpha() for char in normalized):
        raise SubjectFrameError(
            "subject frame content must be natural-language experience, not a raw value"
        )
    if normalized[:1] in {"{", "["}:
        try:
            decoded = json.loads(normalized)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, (dict, list)):
            raise SubjectFrameError(
                "subject frame content cannot be a raw structured payload"
            )
    return normalized


@dataclass(frozen=True, slots=True, init=False)
class SubjectFrameItem:
    """Renderer-visible subject text stripped of engineer lineage and raw state."""

    text: str

    def __init__(self, *, _factory_token: object = None, text: str = "") -> None:
        if _factory_token is not _SUBJECT_FRAME_ITEM_FACTORY_TOKEN:
            raise TypeError(
                "SubjectFrameItem is factory-controlled; "
                "construct SubjectFrame from PhenomenalEvent values"
            )
        object.__setattr__(self, "text", _assert_natural_subject_text(text))


def _subject_frame_item(event: PhenomenalEvent) -> SubjectFrameItem:
    if not isinstance(event, PhenomenalEvent):
        raise TypeError("subject frame accepts PhenomenalEvent values only")
    if event.awareness not in {AwarenessLevel.CONSCIOUS, AwarenessLevel.FOCAL}:
        raise SubjectFrameError(
            "only conscious or focal phenomenal events may enter SubjectFrame"
        )
    return SubjectFrameItem(
        _factory_token=_SUBJECT_FRAME_ITEM_FACTORY_TOKEN,
        text=event.subject_text,
    )


@dataclass(frozen=True, slots=True)
class SubjectFrame:
    """The only character-state capability a subject renderer may read.

    The frame intentionally stores no subject IDs, ticks, scores, record IDs,
    provenance, state versions, hashes, body telemetry, or policy diagnostics.
    """

    items: tuple[SubjectFrameItem, ...] = ()

    def __post_init__(self) -> None:
        normalized = tuple(self.items)
        if any(not isinstance(item, SubjectFrameItem) for item in normalized):
            raise TypeError("SubjectFrame.items must contain SubjectFrameItem values only")
        object.__setattr__(self, "items", normalized)

    @classmethod
    def from_events(cls, events: Iterable[PhenomenalEvent]) -> "SubjectFrame":
        events = tuple(events)
        if any(not isinstance(event, PhenomenalEvent) for event in events):
            raise TypeError("SubjectFrame.from_events accepts PhenomenalEvent values only")
        subject_ids = {event.subject_id for event in events}
        if len(subject_ids) > 1:
            raise SubjectFrameError("one SubjectFrame cannot mix multiple subjects")
        return cls(items=tuple(_subject_frame_item(event) for event in events))

    def renderer_context(self) -> tuple[str, ...]:
        """Return only authorized natural-language subject content."""
        return tuple(item.text for item in self.items)


@dataclass(frozen=True, slots=True, init=False)
class EngineerAuditEnvelope:
    """Immutable engineer-only diagnostics, never a renderer subject frame."""

    _payload_json: str

    def __init__(self, *, _factory_token: object = None, payload_json: str = "") -> None:
        if _factory_token is not _ENGINEER_AUDIT_FACTORY_TOKEN:
            raise TypeError("EngineerAuditEnvelope is factory-controlled; use capture()")
        object.__setattr__(self, "_payload_json", payload_json)

    @classmethod
    def capture(cls, payload: Mapping[str, Any]) -> "EngineerAuditEnvelope":
        if not isinstance(payload, Mapping):
            raise TypeError("engineer audit payload must be a mapping")
        try:
            encoded = json.dumps(
                dict(payload),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
        except (TypeError, ValueError) as exc:
            raise TypeError(
                "engineer audit payload must be finite JSON-serializable data"
            ) from exc
        return cls(
            _factory_token=_ENGINEER_AUDIT_FACTORY_TOKEN,
            payload_json=encoded,
        )

    def inspect(self) -> dict[str, Any]:
        """Return a detached engineer-side copy of captured diagnostics."""
        decoded = json.loads(self._payload_json)
        if not isinstance(decoded, dict):
            raise RuntimeError("engineer audit envelope payload is not an object")
        return decoded


class SubjectRendererCapability:
    """Capability that can read SubjectFrame and nothing else."""

    @staticmethod
    def read(frame: SubjectFrame) -> tuple[str, ...]:
        if not isinstance(frame, SubjectFrame):
            raise TypeError("subject renderer capability requires SubjectFrame")
        return frame.renderer_context()


class EngineerAuditCapability:
    """Capability that can inspect EngineerAuditEnvelope and nothing else."""

    @staticmethod
    def read(envelope: EngineerAuditEnvelope) -> dict[str, Any]:
        if not isinstance(envelope, EngineerAuditEnvelope):
            raise TypeError("engineer audit capability requires EngineerAuditEnvelope")
        return envelope.inspect()
