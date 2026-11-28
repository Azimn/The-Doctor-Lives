"""Sensus Artificialis v0.1: conservative, inspectable percept binding.

This module expects an upstream perception shell to provide typed and
trust-bounded percepts. It does not authenticate sources or normalize sensors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Iterable

SCHEMA_VERSION = "sensus.scene.v0.1"


class Evidence(str, Enum):
    OBSERVED = "observed"
    REPORTED = "reported"
    INFERRED = "inferred"
    REMEMBERED = "remembered"
    INTEROCEPTIVE = "interoceptive"


@dataclass(frozen=True, slots=True)
class Attribution:
    """A candidate affect attribution, never treated as an observed cause."""

    cause_ref: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.cause_ref or not isfinite(self.confidence) or not 0 <= self.confidence <= 1:
            raise ValueError("Invalid attribution")


@dataclass(frozen=True, slots=True)
class Percept:
    """Typed shell output. A provenance-bearing claim, not a world fact.

    object_hint binds channels within the same tick only. It is not a
    persistent ID or an authority assertion. features is a shell-provided
    immutable signature used only for uncertain cross-tick re-identification.
    """

    event_id: str
    channel: str
    evidence: Evidence
    source_ref: str
    tick: int
    attribute: str
    value: str
    confidence: float
    object_hint: str = ""
    features: tuple[tuple[str, str], ...] = ()
    attributions: tuple[Attribution, ...] = ()

    def __post_init__(self) -> None:
        for name in ("event_id", "channel", "source_ref", "attribute"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError("Missing or invalid " + name)
        if not isinstance(self.evidence, Evidence):
            raise TypeError("evidence must be an Evidence enum")
        if not isinstance(self.tick, int) or self.tick < 0:
            raise ValueError("tick must be a nonnegative integer")
        if not isinstance(self.confidence, (int, float)) or not isfinite(self.confidence) or not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be finite and between zero and one")
        if not isinstance(self.value, str):
            raise TypeError("value must be a string")
        if not isinstance(self.features, tuple) or any(
            not isinstance(pair, tuple) or len(pair) != 2 or
            not all(isinstance(part, str) and part for part in pair)
            for pair in self.features
        ):
            raise TypeError("features must be immutable nonempty string pairs")
        if not isinstance(self.attributions, tuple) or any(not isinstance(a, Attribution) for a in self.attributions):
            raise TypeError("attributions must be an immutable tuple")
        if self.attributions and self.evidence is not Evidence.INTEROCEPTIVE:
            raise ValueError("affect attributions require interoceptive evidence")


@dataclass(frozen=True, slots=True)
class IdentityCandidate:
    object_id: str
    similarity: float


@dataclass(frozen=True, slots=True)
class Conflict:
    object_id: str
    attribute: str
    event_ids: tuple[str, ...]
    source_refs: tuple[str, ...]
    values: tuple[str, ...]
    status: str  # vetoed or uncertain; never silently resolved


@dataclass(frozen=True, slots=True)
class SceneObject:
    object_id: str
    claims: tuple[Percept, ...]
    contested_attributes: tuple[str, ...]
    identity_status: str  # new, matched, ambiguous
    identity_candidates: tuple[IdentityCandidate, ...]
    reidentified_from: str | None = None


@dataclass(frozen=True, slots=True)
class Scene:
    schema_version: str
    tick: int
    objects: tuple[SceneObject, ...]
    conflicts: tuple[Conflict, ...]
    absent_channels: tuple[str, ...]

    @property
    def unresolved(self) -> bool:
        return bool(self.conflicts)


@dataclass(frozen=True, slots=True)
class ObjectFile:
    """Short-lived engineer-side working file; NOT the Archive."""

    object_id: str
    features: tuple[tuple[str, str], ...]
    last_seen_tick: int


@dataclass(frozen=True, slots=True)
class SensusConfig:
    expected_channels: tuple[str, ...] = ()
    recent_window: int = 4
    max_object_files: int = 64
    match_threshold: float = 0.60
    ambiguity_margin: float = 0.15
    conflict_confidence: float = 0.60

    def __post_init__(self) -> None:
        if self.recent_window < 0 or self.max_object_files < 1:
            raise ValueError("Invalid bounded working-memory limits")
        if len(self.expected_channels) != len(set(self.expected_channels)):
            raise ValueError("Expected channels must be unique")
        for value in (self.match_threshold, self.ambiguity_margin, self.conflict_confidence):
            if not isfinite(value) or not 0 <= value <= 1:
                raise ValueError("Thresholds must be in [0, 1]")


def _similarity(left: tuple[tuple[str, str], ...], right: tuple[tuple[str, str], ...]) -> float:
    a, b = set(left), set(right)
    return len(a & b) / len(a | b) if a and b else 0.0


class Sensus:
    """Bind percepts into immutable candidate scenes without admission decisions."""

    def __init__(self, config: SensusConfig | None = None) -> None:
        self.config = config or SensusConfig()
        self._files: dict[str, ObjectFile] = {}
        self._last_tick = -1
        self._next_id = 1

    @property
    def recent_object_files(self) -> tuple[ObjectFile, ...]:
        return tuple(sorted(self._files.values(), key=lambda f: f.object_id))

    def step(self, tick: int, percepts: Iterable[Percept]) -> Scene:
        if not isinstance(tick, int) or tick <= self._last_tick:
            raise ValueError("Ticks must advance strictly")
        items = tuple(percepts)
        if any(not isinstance(p, Percept) for p in items):
            raise TypeError("Only typed Percept values are accepted")
        if any(p.tick != tick for p in items):
            raise ValueError("Percepts must refer to this tick")
        event_ids = [p.event_id for p in items]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("Duplicate event_id in scene input")

        # Sort removes dependency on accidental iterable ordering.
        items = tuple(sorted(items, key=lambda p: p.event_id))
        self._files = {
            key: item for key, item in self._files.items()
            if tick - item.last_seen_tick <= self.config.recent_window
        }
        absent = tuple(sorted(set(self.config.expected_channels) - {p.channel for p in items}))
        groups: dict[str, list[Percept]] = {}
        for item in items:
            group_key = "hint:" + item.object_hint if item.object_hint else "event:" + item.event_id
            groups.setdefault(group_key, []).append(item)

        # Freeze the previous-tick comparison pool. Current-tick objects must
        # never become re-identification targets for each other.
        prior_files = tuple(self._files.values())
        objects: list[SceneObject] = []
        conflicts: list[Conflict] = []
        claimed_old_ids: set[str] = set()

        for key in sorted(groups):
            claims = tuple(groups[key])
            features = tuple(sorted({feature for p in claims for feature in p.features}))
            candidates = tuple(
                sorted(
                    (IdentityCandidate(old.object_id, round(_similarity(features, old.features), 6))
                     for old in prior_files if features and old.features
                     and old.object_id not in claimed_old_ids),
                    key=lambda c: (-c.similarity, c.object_id)
                )
            )
            candidates = tuple(c for c in candidates if c.similarity > 0)
            best = candidates[0].similarity if candidates else 0.0
            runner_up = candidates[1].similarity if len(candidates) > 1 else 0.0
            matched = (
                bool(candidates) and best >= self.config.match_threshold
                and best - runner_up >= self.config.ambiguity_margin
            )
            ambiguous = bool(candidates) and not matched
            reidentified_from: str | None = candidates[0].object_id if matched else None
            if reidentified_from:
                object_id = reidentified_from
                claimed_old_ids.add(object_id)
            else:
                object_id = "obj-" + str(self._next_id).zfill(6)
                self._next_id += 1
            by_attribute: dict[str, list[Percept]] = {}
            for claim in claims:
                by_attribute.setdefault(claim.attribute, []).append(claim)
            contested: list[str] = []
            for attribute, relevant in sorted(by_attribute.items()):
                if len({claim.value for claim in relevant}) <= 1:
                    continue
                contested.append(attribute)
                observed = [c for c in relevant if c.evidence is Evidence.OBSERVED and
                            c.confidence >= self.config.conflict_confidence]
                hard_veto = len({c.value for c in observed}) > 1
                conflicts.append(Conflict(
                    object_id=object_id,
                    attribute=attribute,
                    event_ids=tuple(c.event_id for c in relevant),
                    source_refs=tuple(c.source_ref for c in relevant),
                    values=tuple(c.value for c in relevant),
                    status="vetoed" if hard_veto else "uncertain",
                ))
            objects.append(SceneObject(
                object_id=object_id,
                claims=claims,
                contested_attributes=tuple(contested),
                identity_status="matched" if matched else "ambiguous" if ambiguous else "new",
                identity_candidates=candidates,
                reidentified_from=reidentified_from,
            ))
            # No evidence classes are collapsed or upgraded by this update.
            self._files[object_id] = ObjectFile(object_id, features, tick)

        while len(self._files) > self.config.max_object_files:
            oldest = min(self._files.values(), key=lambda f: (f.last_seen_tick, f.object_id))
            del self._files[oldest.object_id]
        self._last_tick = tick
        return Scene(
            schema_version=SCHEMA_VERSION,
            tick=tick,
            objects=tuple(objects),
            conflicts=tuple(conflicts),
            absent_channels=absent,
        )
