"""Deterministic awareness routing for phenomenal candidates.

P3 is a subject-access gate, not a consciousness claim. This module is the
awareness arbitration kernel: change, novelty, persistence, and habituation are
explicit inputs supplied by upstream temporal state. It assigns immutable
phenomenal events to latent, preconscious, conscious, or focal access using a
small inspectable priority rule. It remains disconnected from PretoriusBrain
until a later integration gate.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from .phenomenology import AwarenessLevel, PhenomenalEvent


def _unit(value: float, name: str) -> float:
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return value


@dataclass(frozen=True)
class AwarenessCandidate:
    event: PhenomenalEvent
    salience: float = 0.5
    change: float = 0.0
    novelty: float = 0.0
    goal_relevance: float = 0.0
    conflict: float = 0.0
    persistence: float = 0.0
    habituation: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.event, PhenomenalEvent):
            raise TypeError("AwarenessCandidate.event must be PhenomenalEvent")
        for name in (
            "salience",
            "change",
            "novelty",
            "goal_relevance",
            "conflict",
            "persistence",
            "habituation",
        ):
            _unit(getattr(self, name), name)

    @property
    def priority(self) -> float:
        raw = (
            0.20 * self.salience
            + 0.20 * self.change
            + 0.15 * self.novelty
            + 0.20 * self.goal_relevance
            + 0.10 * self.conflict
            + 0.10 * self.persistence
            - 0.15 * self.habituation
        )
        return max(0.0, min(1.0, raw))


@dataclass(frozen=True)
class AwarenessDecision:
    event: PhenomenalEvent
    priority: float

    @property
    def awareness(self) -> AwarenessLevel:
        return self.event.awareness


@dataclass(frozen=True)
class AwarenessPolicy:
    conscious_capacity: int = 3
    focal_capacity: int = 1
    conscious_threshold: float = 0.35
    focal_threshold: float = 0.55
    preconscious_threshold: float = 0.20

    def __post_init__(self) -> None:
        if self.conscious_capacity < 1:
            raise ValueError("conscious_capacity must be at least 1")
        if self.focal_capacity < 0:
            raise ValueError("focal_capacity cannot be negative")
        if self.focal_capacity > self.conscious_capacity:
            raise ValueError("focal_capacity cannot exceed conscious_capacity")
        for name in (
            "conscious_threshold",
            "focal_threshold",
            "preconscious_threshold",
        ):
            _unit(getattr(self, name), name)
        if self.preconscious_threshold > self.conscious_threshold:
            raise ValueError("preconscious threshold cannot exceed conscious threshold")
        if self.conscious_threshold > self.focal_threshold:
            raise ValueError("conscious threshold cannot exceed focal threshold")


class AwarenessRouter:
    def __init__(self, policy: AwarenessPolicy | None = None):
        self.policy = policy or AwarenessPolicy()

    def route(
        self, candidates: tuple[AwarenessCandidate, ...] | list[AwarenessCandidate]
    ) -> tuple[AwarenessDecision, ...]:
        """Route candidates deterministically without mutating their source events."""
        candidates = tuple(candidates)
        if any(not isinstance(candidate, AwarenessCandidate) for candidate in candidates):
            raise TypeError("awareness routing accepts AwarenessCandidate values only")
        subject_ids = {candidate.event.subject_id for candidate in candidates}
        if len(subject_ids) > 1:
            raise ValueError(
                "one awareness routing operation may contain events for only one subject"
            )

        ranked = sorted(
            candidates,
            key=lambda candidate: (candidate.priority, candidate.event.event_id),
            reverse=True,
        )

        conscious_used = 0
        focal_used = 0
        decisions: list[AwarenessDecision] = []
        for candidate in ranked:
            score = candidate.priority
            level = AwarenessLevel.LATENT
            if (
                score >= self.policy.conscious_threshold
                and conscious_used < self.policy.conscious_capacity
            ):
                if (
                    score >= self.policy.focal_threshold
                    and focal_used < self.policy.focal_capacity
                ):
                    level = AwarenessLevel.FOCAL
                    focal_used += 1
                else:
                    level = AwarenessLevel.CONSCIOUS
                conscious_used += 1
            elif score >= self.policy.preconscious_threshold:
                level = AwarenessLevel.PRECONSCIOUS

            decisions.append(
                AwarenessDecision(
                    event=replace(candidate.event, awareness=level),
                    priority=score,
                )
            )
        return tuple(decisions)
