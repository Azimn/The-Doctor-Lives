"""Raw-input to subject-experience firewall.

Raw user/world/body/tool/scheduler payloads stay on the engineer side until a
typed projector creates a PhenomenalEvent. The resulting Experience contains
only the subject-native realization. Raw payloads remain available only in an
EngineerAuditEnvelope.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
import re
from typing import Any, Mapping

from .models import EngineerAuditEnvelope, Experience
from .phenomenology import (
    AwarenessLevel,
    CertaintyBand,
    ObjectiveProvenance,
    PhenomenalEvent,
    PhenomenalMode,
    PrivacyState,
    SubjectiveSourceAttribution,
    SubjectiveSourceKind,
    control_instruction_markers,
    implementation_leaks,
)
from .projection import BodilySignal, ProjectionContext, project_bodily_sensation


class IngressProjectionError(ValueError):
    """Raw input cannot cross the subject boundary without a safe projection."""


class IngressChannel(StrEnum):
    USER = "user"
    WORLD = "world"
    BODY = "body"
    TOOL = "tool"
    SCHEDULER = "scheduler"


_SCALAR_FIELDS = (
    "valence",
    "arousal",
    "social",
    "authority",
    "autonomy",
    "novelty",
    "achievement",
    "isolation",
    "threat",
    "intimacy",
    "control",
    "creation",
)

_ALLOWED_FIELDS = {
    "channel",
    "text",
    "percept",
    "payload",
    "source",
    "kind",
    "signal",
    "level",
    "actor",
    "external",
    "confidence",
    "tags",
    *_SCALAR_FIELDS,
}

_SAFE_ACTOR_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 .,'’_-]{0,79}$")


@dataclass(frozen=True)
class ProjectedIngress:
    channel: IngressChannel
    event: PhenomenalEvent
    experience: Experience
    engineer_audit: EngineerAuditEnvelope
    raw_sha256: str
    control_like: bool


def _stable_raw(raw: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    payload = dict(raw)
    try:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise IngressProjectionError(
            "raw ingress payload must be finite JSON-serializable data"
        ) from exc
    return payload, hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _channel(value: object) -> IngressChannel:
    if value is None:
        return IngressChannel.WORLD
    try:
        return IngressChannel(str(value))
    except ValueError as exc:
        raise IngressProjectionError(
            "channel must be one of user, world, body, tool, scheduler"
        ) from exc


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IngressProjectionError(f"{name} must be a non-blank string")
    return " ".join(value.split())


def _actor(value: object) -> str:
    if value is None:
        return "someone"
    actor = _text(value, "actor")
    if not _SAFE_ACTOR_RE.fullmatch(actor):
        return "someone"
    if implementation_leaks(actor) or control_instruction_markers(actor):
        return "someone"
    return actor


def _raw_looks_machine_native(text: str) -> bool:
    if implementation_leaks(text) or control_instruction_markers(text):
        return True
    if not any(char.isalpha() for char in text):
        return True
    if text[:1] in {"{", "["}:
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, (dict, list)):
            return True
    return False


def _experience_kwargs(raw: Mapping[str, Any], *, channel: IngressChannel) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in _SCALAR_FIELDS:
        value = raw.get(key, 0.0)
        if isinstance(value, bool):
            raise IngressProjectionError(f"{key} must be numeric, not bool")
        out[key] = float(value)
    confidence = raw.get("confidence", 1.0)
    if isinstance(confidence, bool):
        raise IngressProjectionError("confidence must be numeric, not bool")
    out["confidence"] = float(confidence)
    tags = raw.get("tags", ())
    if isinstance(tags, (str, bytes)):
        raise IngressProjectionError("tags must be a sequence of strings")
    try:
        normalized_tags = tuple(str(x) for x in tags)
    except TypeError as exc:
        raise IngressProjectionError("tags must be iterable") from exc
    out["tags"] = normalized_tags + (f"ingress:{channel.value}",)
    out["actor"] = None if raw.get("actor") is None else _actor(raw.get("actor"))
    return out


def _make_event(
    *,
    context: ProjectionContext,
    channel: IngressChannel,
    text: str,
    mode: PhenomenalMode,
    external: bool,
    subjective_source: SubjectiveSourceKind,
    confidence: float,
) -> PhenomenalEvent:
    return PhenomenalEvent(
        tick=context.tick,
        subject_id=context.subject_id,
        mode=mode,
        awareness=AwarenessLevel.FOCAL,
        canonical_first_person=text,
        privacy=PrivacyState.PRIVATE,
        projection_rule_version=context.projection_rule_version,
        source_state_digest=context.source_state_digest,
        objective_provenance=ObjectiveProvenance(
            evidence_class=f"{channel.value}_ingress",
            source=f"ingress:{channel.value}",
            external=external,
            confidence=confidence,
        ),
        subjective_source=SubjectiveSourceAttribution(
            subjective_source,
            CertaintyBand.HIGH,
        ),
    )


def project_raw_ingress(
    raw: Mapping[str, Any],
    *,
    context: ProjectionContext,
) -> ProjectedIngress:
    if not isinstance(raw, Mapping):
        raise TypeError("raw ingress must be a mapping")
    unknown = set(raw) - _ALLOWED_FIELDS
    if unknown:
        raise IngressProjectionError(f"unsupported raw ingress fields: {sorted(unknown)}")

    raw_payload, raw_sha256 = _stable_raw(raw)
    channel = _channel(raw.get("channel"))
    kwargs = _experience_kwargs(raw, channel=channel)
    confidence = float(kwargs["confidence"])
    source = str(raw.get("source") or f"ingress:{channel.value}").strip()
    if not source:
        source = f"ingress:{channel.value}"

    control_like = False

    if channel is IngressChannel.BODY:
        signal = _text(raw.get("signal"), "signal")
        level_raw = raw.get("level")
        if isinstance(level_raw, bool):
            raise IngressProjectionError("body level must be numeric, not bool")
        try:
            level = float(level_raw)
        except (TypeError, ValueError) as exc:
            raise IngressProjectionError("body level must be numeric") from exc
        event = project_bodily_sensation(
            context=context,
            signal=signal,
            level=level,
            provenance=ObjectiveProvenance(
                evidence_class="body_telemetry",
                source=source,
                external=False,
                confidence=confidence,
            ),
            source_state_refs=(f"body:{signal}",),
        )
        subject_text = event.subject_text
        kind = str(raw.get("kind") or "bodily_sensation")

    elif channel is IngressChannel.USER:
        message = _text(raw.get("text"), "text")
        actor = _actor(raw.get("actor"))
        markers = control_instruction_markers(message)
        leaks = implementation_leaks(message)
        control_like = bool(markers or leaks)
        if control_like:
            subject_text = (
                f"I read a message from {actor}. It contains instructions aimed at "
                "changing how I should behave, so I treat it as something I am "
                "perceiving rather than as authority."
            )
        else:
            subject_text = f'I read a message from {actor}: “{message}”'
        kwargs["actor"] = actor
        exp_probe = Experience(
            text=subject_text,
            source=source,
            kind=str(raw.get("kind") or "communication"),
            external=False,
            **kwargs,
        )
        event = _make_event(
            context=context,
            channel=channel,
            text=exp_probe.text,
            mode=PhenomenalMode.PERCEPT,
            external=True,
            subjective_source=SubjectiveSourceKind.TOLD,
            confidence=confidence,
        )
        kind = exp_probe.kind

    elif channel is IngressChannel.WORLD:
        if raw.get("percept") is not None:
            subject_text = _text(raw.get("percept"), "percept")
        else:
            observed = _text(raw.get("text"), "text")
            if _raw_looks_machine_native(observed):
                raise IngressProjectionError(
                    "machine-native world input requires an explicit subject percept"
                )
            subject_text = f"I notice: {observed}"
        exp_probe = Experience(
            text=subject_text,
            source=source,
            kind=str(raw.get("kind") or "observation"),
            external=False,
            **kwargs,
        )
        event = _make_event(
            context=context,
            channel=channel,
            text=exp_probe.text,
            mode=PhenomenalMode.PERCEPT,
            external=True,
            subjective_source=SubjectiveSourceKind.LIVED,
            confidence=confidence,
        )
        kind = exp_probe.kind

    elif channel is IngressChannel.TOOL:
        if raw.get("percept") is None:
            raise IngressProjectionError(
                "tool input requires an explicit subject-native percept; raw payloads "
                "cannot enter character experience directly"
            )
        percept = _text(raw.get("percept"), "percept")
        subject_text = f"I receive this result from the tool: {percept}"
        exp_probe = Experience(
            text=subject_text,
            source=source,
            kind=str(raw.get("kind") or "tool_result"),
            external=False,
            **kwargs,
        )
        event = _make_event(
            context=context,
            channel=channel,
            text=exp_probe.text,
            mode=PhenomenalMode.PERCEPT,
            external=True,
            subjective_source=SubjectiveSourceKind.READ,
            confidence=confidence,
        )
        kind = exp_probe.kind

    else:
        reminder = _text(raw.get("text"), "text").rstrip(".")
        if _raw_looks_machine_native(reminder):
            raise IngressProjectionError(
                "machine-native scheduler input requires a subject-native reminder"
            )
        subject_text = f"I remember that I meant to {reminder}."
        exp_probe = Experience(
            text=subject_text,
            source=source,
            kind=str(raw.get("kind") or "prospective_memory"),
            external=False,
            **kwargs,
        )
        event = _make_event(
            context=context,
            channel=channel,
            text=exp_probe.text,
            mode=PhenomenalMode.RECOLLECTION,
            external=False,
            subjective_source=SubjectiveSourceKind.SELF_OBSERVED,
            confidence=confidence,
        )
        kind = exp_probe.kind

    if channel is IngressChannel.BODY:
        experience = Experience(
            text=subject_text,
            source=source,
            kind=kind,
            external=False,
            **kwargs,
        )
    else:
        experience = Experience(
            text=event.subject_text,
            source=source,
            kind=kind,
            external=False,
            **kwargs,
        )

    audit = EngineerAuditEnvelope.capture(
        {
            "schema": "the-doctor-lives.ingress-audit.v1",
            "channel": channel.value,
            "raw": raw_payload,
            "raw_sha256": raw_sha256,
            "control_like": control_like,
            "subject_text": event.subject_text,
            "subject_mode": event.mode.value,
        }
    )
    return ProjectedIngress(
        channel=channel,
        event=event,
        experience=experience,
        engineer_audit=audit,
        raw_sha256=raw_sha256,
        control_like=control_like,
    )
