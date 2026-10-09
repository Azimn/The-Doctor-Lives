"""World action outcomes require independent external authority and consent."""
from __future__ import annotations

from dataclasses import dataclass
import re

_DIGEST = re.compile(r"^[a-f0-9]{64}$")


@dataclass(frozen=True, slots=True)
class WorldOutcome:
    event_id: str
    actor_id: str
    world_authority: str
    outcome_digest: str
    participant_consented: bool
    world_verified: bool


@dataclass(frozen=True, slots=True)
class WorldDecision:
    accepted: bool
    reason: str


def accept_outcome(outcome: WorldOutcome, *, expected_authority: str, expected_actor: str) -> WorldDecision:
    if not isinstance(outcome, WorldOutcome):
        raise TypeError("WorldOutcome required")
    if not outcome.event_id or outcome.actor_id != expected_actor or outcome.world_authority != expected_authority:
        return WorldDecision(False, "actor, event, or external world authority mismatch")
    if type(outcome.participant_consented) is not bool or type(outcome.world_verified) is not bool:
        raise TypeError("world verification and consent must be booleans")
    if not outcome.participant_consented or not outcome.world_verified:
        return WorldDecision(False, "missing consent or authoritative world event")
    if not isinstance(outcome.outcome_digest, str) or not _DIGEST.fullmatch(outcome.outcome_digest):
        return WorldDecision(False, "invalid outcome digest")
    return WorldDecision(True, "verified event is eligible for governed ledger writeback")
