"""Deterministic offline phenomenal projectors.

These projectors translate implementation-native inputs into immutable,
subject-native PhenomenalEvent values. They are deliberately small and
inspectable. P2 does not yet wire them into PretoriusBrain.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

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
    VividnessBand,
)


class PhenomenalLeakError(ValueError):
    pass


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
_RAW_ASSIGNMENT_RE = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*-?\d+(?:\.\d+)?\b")


def implementation_leaks(text: str) -> tuple[str, ...]:
    """Return conservative implementation artifacts found in subject text."""
    lowered = text.lower()
    hits = [token for token in _IMPLEMENTATION_TOKENS if token in lowered]
    if _UUID_RE.search(text):
        hits.append("raw_uuid")
    if _RAW_ASSIGNMENT_RE.search(text):
        hits.append("raw_numeric_assignment")
    return tuple(sorted(set(hits)))


def assert_subject_text_safe(text: str) -> None:
    hits = implementation_leaks(text)
    if hits:
        raise PhenomenalLeakError(
            "subject-facing text contains implementation-native artifacts: "
            + ", ".join(hits)
        )


@dataclass(frozen=True)
class ProjectionContext:
    subject_id: str
    tick: int
    source_state_digest: str
    projection_rule_version: str = "uppb-p2"
    awareness: AwarenessLevel = AwarenessLevel.CONSCIOUS
    privacy: PrivacyState = PrivacyState.PRIVATE

    def __post_init__(self) -> None:
        if not self.subject_id.strip():
            raise ValueError("subject_id is required")
        if self.tick < 0:
            raise ValueError("tick cannot be negative")
        if not self.source_state_digest.strip():
            raise ValueError("source_state_digest is required")


class BodilySignal(str):
    FATIGUE = "fatigue"
    COLD = "cold"
    HEAT = "heat"
    HUNGER = "hunger"
    PAIN = "pain"
    TENSION = "tension"


def _unit(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


def _intensity(value: float) -> IntensityBand:
    value = _unit(value, "intensity")
    if value < 0.15:
        return IntensityBand.TRACE
    if value < 0.35:
        return IntensityBand.MILD
    if value < 0.60:
        return IntensityBand.MODERATE
    if value < 0.82:
        return IntensityBand.STRONG
    return IntensityBand.OVERWHELMING


def _certainty(value: float) -> CertaintyBand:
    value = _unit(value, "confidence")
    if value < 0.20:
        return CertaintyBand.VERY_LOW
    if value < 0.40:
        return CertaintyBand.LOW
    if value < 0.65:
        return CertaintyBand.MODERATE
    if value < 0.88:
        return CertaintyBand.HIGH
    return CertaintyBand.VERY_HIGH


def _event_id(context: ProjectionContext, mode: PhenomenalMode, text: str) -> str:
    payload = "|".join(
        (
            context.subject_id,
            str(context.tick),
            context.source_state_digest,
            context.projection_rule_version,
            mode.value,
            text,
        )
    )
    return "phen_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _event(
    *,
    context: ProjectionContext,
    mode: PhenomenalMode,
    text: str,
    provenance: ObjectiveProvenance,
    intensity: IntensityBand = IntensityBand.MODERATE,
    certainty: CertaintyBand = CertaintyBand.MODERATE,
    vividness: VividnessBand = VividnessBand.MODERATE,
    subjective_source: SubjectiveSourceAttribution | None = None,
    source_state_refs: tuple[str, ...] = (),
    source_event_refs: tuple[str, ...] = (),
    object_refs: tuple[str, ...] = (),
) -> PhenomenalEvent:
    assert_subject_text_safe(text)
    return PhenomenalEvent(
        event_id=_event_id(context, mode, text),
        tick=context.tick,
        subject_id=context.subject_id,
        mode=mode,
        awareness=context.awareness,
        canonical_first_person=text,
        privacy=context.privacy,
        projection_rule_version=context.projection_rule_version,
        source_state_digest=context.source_state_digest,
        objective_provenance=provenance,
        subjective_source=subjective_source or SubjectiveSourceAttribution(),
        subjective_certainty=certainty,
        subjective_vividness=vividness,
        subjective_intensity=intensity,
        source_state_refs=source_state_refs,
        source_event_refs=source_event_refs,
        object_refs=object_refs,
    )


_BODILY_TEXT = {
    BodilySignal.FATIGUE: {
        IntensityBand.TRACE: "I hardly notice any tiredness.",
        IntensityBand.MILD: "I feel a little tired.",
        IntensityBand.MODERATE: "I am tired enough that keeping my attention on this takes effort.",
        IntensityBand.STRONG: "I am exhausted, and concentrating is becoming difficult.",
        IntensityBand.OVERWHELMING: "I can barely keep myself focused through the exhaustion.",
    },
    BodilySignal.COLD: {
        IntensityBand.TRACE: "There is barely a chill to notice.",
        IntensityBand.MILD: "I feel a little chilly.",
        IntensityBand.MODERATE: "The cold is becoming hard to ignore.",
        IntensityBand.STRONG: "I feel deeply chilled.",
        IntensityBand.OVERWHELMING: "The cold is overwhelming everything else I am trying to attend to.",
    },
    BodilySignal.HEAT: {
        IntensityBand.TRACE: "I barely notice the warmth.",
        IntensityBand.MILD: "I feel a little warm.",
        IntensityBand.MODERATE: "The heat is becoming uncomfortable.",
        IntensityBand.STRONG: "I feel oppressively hot.",
        IntensityBand.OVERWHELMING: "The heat is making it difficult to think about anything else.",
    },
    BodilySignal.HUNGER: {
        IntensityBand.TRACE: "I barely notice any hunger.",
        IntensityBand.MILD: "I am a little hungry.",
        IntensityBand.MODERATE: "Hunger keeps tugging at my attention.",
        IntensityBand.STRONG: "I am very hungry, and it is becoming difficult to ignore.",
        IntensityBand.OVERWHELMING: "Hunger is crowding almost everything else out of my attention.",
    },
    BodilySignal.PAIN: {
        IntensityBand.TRACE: "There is a faint discomfort.",
        IntensityBand.MILD: "I feel a little pain.",
        IntensityBand.MODERATE: "The pain keeps drawing my attention back to it.",
        IntensityBand.STRONG: "I am in considerable pain.",
        IntensityBand.OVERWHELMING: "The pain is overwhelming my attention.",
    },
    BodilySignal.TENSION: {
        IntensityBand.TRACE: "There is a faint tension in me.",
        IntensityBand.MILD: "I feel slightly tense.",
        IntensityBand.MODERATE: "I can feel myself tightening up.",
        IntensityBand.STRONG: "I feel wound tight.",
        IntensityBand.OVERWHELMING: "I feel so tense that it is difficult to settle my attention.",
    },
}


def project_bodily_sensation(
    *,
    context: ProjectionContext,
    signal: str,
    level: float,
    provenance: ObjectiveProvenance,
    source_state_refs: tuple[str, ...] = (),
) -> PhenomenalEvent:
    if signal not in _BODILY_TEXT:
        raise ValueError(f"unsupported bodily signal {signal!r}")
    band = _intensity(level)
    return _event(
        context=context,
        mode=PhenomenalMode.BODILY_SENSATION,
        text=_BODILY_TEXT[signal][band],
        provenance=provenance,
        intensity=band,
        subjective_source=SubjectiveSourceAttribution(
            SubjectiveSourceKind.SELF_OBSERVED,
            CertaintyBand.HIGH,
        ),
        source_state_refs=source_state_refs,
    )


def project_appraisal_feeling(
    *,
    context: ProjectionContext,
    valence: float,
    arousal: float,
    threat: float,
    control: float,
    novelty: float,
    provenance: ObjectiveProvenance,
    source_state_refs: tuple[str, ...] = (),
) -> PhenomenalEvent:
    valence = float(valence)
    if not -1.0 <= valence <= 1.0:
        raise ValueError("valence must be between -1 and 1")
    arousal = _unit(arousal, "arousal")
    threat = _unit(threat, "threat")
    control = _unit(control, "control")
    novelty = _unit(novelty, "novelty")

    if threat >= 0.65 and control <= 0.35:
        text = "I feel cornered."
    elif threat >= 0.65 and control >= 0.65:
        text = "This feels dangerous, but I feel ready to face it."
    elif valence <= -0.45 and arousal >= 0.50:
        text = "Something about this is upsetting me."
    elif valence >= 0.45 and novelty >= 0.50:
        text = "This is exciting; I want to see where it leads."
    elif valence <= -0.20:
        text = "I do not like how this feels."
    elif valence >= 0.20:
        text = "This feels good."
    else:
        text = "I am not sure what I feel about this yet."

    intensity = _intensity(max(abs(valence), arousal, threat))
    return _event(
        context=context,
        mode=PhenomenalMode.FEELING,
        text=text,
        provenance=provenance,
        intensity=intensity,
        source_state_refs=source_state_refs,
    )


def project_impulse(
    *,
    context: ProjectionContext,
    action_phrase: str,
    strength: float,
    provenance: ObjectiveProvenance,
    source_state_refs: tuple[str, ...] = (),
) -> PhenomenalEvent:
    phrase = action_phrase.strip().rstrip(".")
    if not phrase:
        raise ValueError("action_phrase is required")
    band = _intensity(strength)
    if band is IntensityBand.TRACE:
        text = f"I have only the faintest urge to {phrase}."
    elif band is IntensityBand.MILD:
        text = f"I feel a slight urge to {phrase}."
    elif band is IntensityBand.MODERATE:
        text = f"I want to {phrase}."
    elif band is IntensityBand.STRONG:
        text = f"I strongly want to {phrase}."
    else:
        text = f"The urge to {phrase} is difficult to ignore."
    return _event(
        context=context,
        mode=PhenomenalMode.IMPULSE,
        text=text,
        provenance=provenance,
        intensity=band,
        source_state_refs=source_state_refs,
    )


def project_uncertainty(
    *,
    context: ProjectionContext,
    proposition: str,
    confidence: float,
    provenance: ObjectiveProvenance,
    source_state_refs: tuple[str, ...] = (),
) -> PhenomenalEvent:
    proposition = proposition.strip().rstrip(".")
    if not proposition:
        raise ValueError("proposition is required")
    confidence = _unit(confidence, "confidence")
    certainty = _certainty(confidence)

    if confidence >= 0.88:
        mode = PhenomenalMode.BELIEF
        text = f"I am almost certain that {proposition}."
    elif confidence >= 0.65:
        mode = PhenomenalMode.BELIEF
        text = f"I think {proposition}."
    elif confidence >= 0.40:
        mode = PhenomenalMode.UNCERTAINTY
        text = f"I am not sure whether {proposition}."
    elif confidence >= 0.20:
        mode = PhenomenalMode.UNCERTAINTY
        text = f"I doubt that {proposition}."
    else:
        mode = PhenomenalMode.BELIEF
        text = f"I do not believe that {proposition}."

    return _event(
        context=context,
        mode=mode,
        text=text,
        provenance=provenance,
        certainty=certainty,
        intensity=IntensityBand.MILD,
        source_state_refs=source_state_refs,
    )


def project_relationship_feeling(
    *,
    context: ProjectionContext,
    actor_name: str,
    trust: float,
    affiliation: float,
    provenance: ObjectiveProvenance,
    source_state_refs: tuple[str, ...] = (),
) -> PhenomenalEvent:
    actor = actor_name.strip()
    if not actor:
        raise ValueError("actor_name is required")
    trust = _unit(trust, "trust")
    affiliation = _unit(affiliation, "affiliation")

    if trust <= 0.20 and affiliation >= 0.55:
        text = f"I want to remain close to {actor}, but I do not trust them."
    elif trust <= 0.25:
        text = f"I do not trust {actor}."
    elif trust < 0.45:
        text = f"I am wary of {actor}."
    elif trust >= 0.78 and affiliation >= 0.60:
        text = f"I feel close to {actor}, and I trust them."
    elif affiliation >= 0.70:
        text = f"I feel drawn toward {actor}."
    elif trust >= 0.65:
        text = f"I trust {actor}."
    else:
        text = f"I am not yet sure what to make of {actor}."

    tension = max(abs(trust - 0.5) * 2.0, affiliation)
    return _event(
        context=context,
        mode=PhenomenalMode.FEELING,
        text=text,
        provenance=provenance,
        intensity=_intensity(tension),
        source_state_refs=source_state_refs,
        object_refs=(f"actor:{actor}",),
    )


def project_concern(
    *,
    context: ProjectionContext,
    subject_phrase: str,
    urgency: float,
    provenance: ObjectiveProvenance,
    source_state_refs: tuple[str, ...] = (),
) -> PhenomenalEvent:
    phrase = subject_phrase.strip().rstrip(".")
    if not phrase:
        raise ValueError("subject_phrase is required")
    band = _intensity(urgency)
    if band is IntensityBand.TRACE:
        text = f"The thought of {phrase} flickers at the edge of my attention."
    elif band is IntensityBand.MILD:
        text = f"The thought of {phrase} keeps returning to me."
    elif band is IntensityBand.MODERATE:
        text = f"I cannot quite put aside the thought of {phrase}."
    elif band is IntensityBand.STRONG:
        text = f"I am preoccupied with {phrase}."
    else:
        text = f"I can barely think past {phrase}."
    return _event(
        context=context,
        mode=PhenomenalMode.CONCERN,
        text=text,
        provenance=provenance,
        intensity=band,
        source_state_refs=source_state_refs,
    )


def project_commitment(
    *,
    context: ProjectionContext,
    action_phrase: str,
    importance: float,
    provenance: ObjectiveProvenance,
    source_state_refs: tuple[str, ...] = (),
) -> PhenomenalEvent:
    phrase = action_phrase.strip().rstrip(".")
    if not phrase:
        raise ValueError("action_phrase is required")
    band = _intensity(importance)
    if band in {IntensityBand.TRACE, IntensityBand.MILD}:
        text = f"I still mean to {phrase}."
    elif band is IntensityBand.MODERATE:
        text = f"I intend to {phrase}."
    elif band is IntensityBand.STRONG:
        text = f"I am determined to {phrase}."
    else:
        text = f"I cannot accept leaving {phrase} undone."
    return _event(
        context=context,
        mode=PhenomenalMode.INTENTION,
        text=text,
        provenance=provenance,
        intensity=band,
        source_state_refs=source_state_refs,
    )
