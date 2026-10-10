"""Eidolon D2: source-bound Mnemosyne and Chronos shadow research adaptors.

NOT a second memory store, renderer access path, learned neural planner or
production policy. Reads the definitive BrainStore and returns only engineer
audit estimates. The source and clock gates are deliberately fail-closed.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
import json
import math
import re
import unicodedata
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .cognition import PretoriusBrain

_STOPWORDS = frozenset({
    "a", "an", "and", "at", "by", "for", "from", "i", "in", "is", "it",
    "my", "of", "on", "our", "the", "their", "there", "to", "was",
    "we", "with", "will", "would", "you",
})


def _tokens(text: str) -> frozenset[str]:
    normalized = unicodedata.normalize("NFC", text.casefold())
    return frozenset(re.findall(r"\w+", normalized, flags=re.UNICODE)) - _STOPWORDS


def _finite_unit(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} may not be Boolean")
    try:
        v = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(v) or not 0 <= v <= 1:
        raise ValueError(f"{name} must be in [0,1]")
    return v


@dataclass(frozen=True)
class LivedWitness:
    memory_id: str
    event_id: str
    text: str
    actor: str | None
    tick: int
    confidence: float
    source: str


@dataclass(frozen=True)
class ProspectivePriority:
    commitment_id: str
    due_tick: int | None
    at_tick: int
    projected_clock: bool
    importance: float
    urgency: float
    priority: float
    baseline: float
    evidence_support: float
    evidence_memory_ids: tuple[str, ...]
    evidence_event_ids: tuple[str, ...]


@dataclass(frozen=True)
class ChronosAudit:
    """Engineer-only. IDs/priority never become subject-accessible."""

    schema: str
    source_state_digest: str
    at_tick: int
    projected_clock: bool
    with_history: bool
    with_temporal: bool
    lived_evidence_count: int
    goals: tuple[ProspectivePriority, ...]


class MnemosyneLoom:
    """Source-checked view of *only* lived episodes in the production store."""

    MIN_CONFIDENCE = 0.6

    @staticmethod
    def collect(brain: PretoriusBrain, *, as_of_tick: int | None = None) -> tuple[LivedWitness, ...]:
        from .cognition import PretoriusBrain
        if not isinstance(brain, PretoriusBrain):
            raise TypeError("expected PretoriusBrain")
        now = brain.store.tick if as_of_tick is None else as_of_tick
        if isinstance(now, bool) or not isinstance(now, int) or now < 0:
            raise ValueError("as_of_tick must be a nonnegative integer")
        suppressed = brain.store.canon_conflict_suppressed_memory_ids()
        with closing(brain.store.connect()) as conn:
            rows = conn.execute(
                """SELECT m.id memory_id,m.text memory_text,m.source memory_source,
                    m.confidence memory_confidence,m.created_tick memory_tick,
                    e.id event_id,e.tick event_tick,e.source event_source,
                    e.external event_external,e.evidence_class event_class,
                    e.confidence event_confidence,e.payload_json event_payload
                   FROM memories m
                   JOIN memory_classifications c ON c.memory_id=m.id
                   JOIN events e ON e.id=m.source_event_id
                   WHERE m.active=1 AND m.external=0
                     AND m.evidence_class='lived_runtime_memory'
                     AND c.autobiographical_class='lived_runtime_memory'
                     AND c.status='active'
                     AND e.external=0 AND e.evidence_class='lived_runtime_memory'
                     AND m.created_tick<=? AND e.tick<=?
                   ORDER BY e.tick,m.id""",
                (now, now),
            ).fetchall()
        good: list[LivedWitness] = []
        for row in rows:
            if row["memory_id"] in suppressed:
                continue
            confidence = min(float(row["memory_confidence"]), float(row["event_confidence"]))
            if not math.isfinite(confidence) or confidence < MnemosyneLoom.MIN_CONFIDENCE or confidence > 1:
                continue
            if str(row["memory_source"]) != str(row["event_source"]):
                continue
            if int(row["memory_tick"]) != int(row["event_tick"]):
                continue
            try:
                payload = json.loads(str(row["event_payload"]))
            except (ValueError, TypeError):
                continue
            if not isinstance(payload, dict) or payload.get("text") != row["memory_text"]:
                continue
            actor = payload.get("actor")
            if actor is not None and (not isinstance(actor, str) or not actor.strip()):
                continue
            good.append(LivedWitness(
                memory_id=str(row["memory_id"]),
                event_id=str(row["event_id"]),
                text=str(row["memory_text"]),
                actor=actor,
                tick=int(row["event_tick"]),
                confidence=confidence,
                source=str(row["memory_source"]),
            ))
        return tuple(good)


class ChronosCoil:
    """Read-only source- and clock-bound prospective *attention* estimator.

    It does not learn, predict real-world outcomes or choose actual actions.
    """

    SCHEMA = "eidolon-d2-chronos-shadow-v0.1"

    @staticmethod
    def forecast(
        brain: PretoriusBrain,
        *,
        at_tick: int | None = None,
        with_history: bool = True,
        with_temporal: bool = True,
    ) -> ChronosAudit:
        from .cognition import PretoriusBrain
        if not isinstance(brain, PretoriusBrain):
            raise TypeError("expected PretoriusBrain")
        if not isinstance(with_history, bool) or not isinstance(with_temporal, bool):
            raise TypeError("lesion flags must be Boolean")
        current = brain.store.tick
        at_tick = current if at_tick is None else at_tick
        if isinstance(at_tick, bool) or not isinstance(at_tick, int) or at_tick < 0:
            raise ValueError("at_tick must be a nonnegative integer")
        # The future clock is *counterfactual*. No future evidence is invented.
        witnesses = MnemosyneLoom.collect(brain, as_of_tick=at_tick)
        # Derive bounded relational context from *witness-verified* lived
        # relationship-event deltas available by this clock tick. Do not use
        # the current relationship row for a past counterfactual: that would
        # leak later social experience backward in time.
        witnessed_by_event = {e.event_id: e for e in witnesses}
        trust_by_actor: dict[str, float] = {}
        with closing(brain.store.connect()) as conn:
            relation_events = conn.execute(
                """SELECT source_event_id,trust_delta FROM relationship_events
                   WHERE tick<=? ORDER BY tick,id""", (at_tick,)
            ).fetchall()
        for event in relation_events:
            source = witnessed_by_event.get(str(event["source_event_id"]))
            if source is None or source.actor is None:
                continue
            delta = float(event["trust_delta"])
            if not math.isfinite(delta) or abs(delta) > 1:
                continue
            actor_key = source.actor.casefold().strip()
            trust_by_actor[actor_key] = max(
                0.0, min(1.0, trust_by_actor.get(actor_key, 0.5) + delta)
            )
        goals: list[ProspectivePriority] = []
        for row in brain.store.open_commitments():
            if int(row["created_tick"]) > at_tick:
                continue
            description = str(row["description"])
            actor = row.get("actor")
            if actor is not None and not str(actor).strip():
                continue
            actor_text = None if actor is None else str(actor).casefold().strip()
            target_tokens = _tokens(description)
            if actor_text is not None:
                target_tokens -= _tokens(actor_text)
            importance = _finite_unit(row["importance"], "importance")
            due = row["due_tick"]
            if due is not None:
                if isinstance(due, bool):
                    raise ValueError("invalid due tick")
                due = int(due)
                if due < 0:
                    raise ValueError("invalid due tick")
            urgency = (
                1.0 / (1.0 + max(0, due - at_tick))
                if with_temporal and due is not None else 0.25
            )
            baseline = importance * (0.2 + 0.8 * urgency)
            best = 0.0
            winners: list[LivedWitness] = []
            if with_history and target_tokens:
                for e in witnesses:
                    # An actor-specific commitment needs that same source event
                    # actor, not just a matching name inside generic prose.
                    if actor_text is not None and (
                        e.actor is None or e.actor.casefold().strip() != actor_text
                    ):
                        continue
                    overlap = len(target_tokens & _tokens(e.text)) / len(target_tokens)
                    if overlap < 0.2:
                        continue
                    relation_multiplier = 1.0
                    if actor_text is not None:
                        if actor_text in trust_by_actor:
                            # An engineer-side reconstruction from actually
                            # witnessed relationship deltas, not the current
                            # production relationship row or subjective trust.
                            relation_multiplier = (
                                0.75 + 0.25 * trust_by_actor[actor_text]
                            )
                        else:
                            relation_multiplier = 0.75
                    support = overlap * e.confidence * relation_multiplier
                    if support > best + 1e-12:
                        best = support
                        winners = [e]
                    elif support > 0 and abs(support - best) <= 1e-12:
                        winners.append(e)
            priority = min(1.0, baseline + 0.45 * best)
            goals.append(ProspectivePriority(
                commitment_id=str(row["id"]),
                due_tick=due,
                at_tick=at_tick,
                projected_clock=at_tick != current,
                importance=importance,
                urgency=urgency,
                baseline=baseline,
                priority=priority,
                evidence_support=best,
                evidence_memory_ids=tuple(sorted(e.memory_id for e in winners)),
                evidence_event_ids=tuple(sorted(e.event_id for e in winners)),
            ))
        goals.sort(key=lambda x: (-x.priority, x.commitment_id))
        return ChronosAudit(
            schema=ChronosCoil.SCHEMA,
            source_state_digest=brain.store.digest(),
            at_tick=at_tick,
            projected_clock=at_tick != current,
            with_history=with_history,
            with_temporal=with_temporal,
            lived_evidence_count=len(witnesses),
            goals=tuple(goals),
        )
