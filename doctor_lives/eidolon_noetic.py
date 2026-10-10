"""Eidolon Noetic Crucible E4-B: *experimental* class-conditional W learning.

Uses the real PretoriusRecurrentSubstrate sparse recurrent matrix and its
fixed native action populations. This does NOT integrate with production,
prove biological local plasticity, or authenticate live autobiographical
evidence. Only an explicitly typed offline synthetic research grant is
admitted; live source ownership needs the trusted Janus/Mnemosyne adapter.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math

import numpy as np

from .neural import ACTIONS, PretoriusRecurrentSubstrate

ETA = 0.05
TRACE_DECAY = 0.90
UPDATE_LIMIT = 0.02
GRANT_CLASS = "synthetic_verified_outcome_fixture"


@dataclass(frozen=True)
class SyntheticOutcomeGrant:
    """An OFFLINE research fixture assertion, not cryptographic testimony."""

    event_id: str
    actor: str
    text_sha256: str
    action: str
    evidence_class: str
    verified_outcome: bool

    @classmethod
    def for_fixture(cls, *, event_id: str, actor: str,
                    text: str, action: str) -> "SyntheticOutcomeGrant":
        if action not in ACTIONS:
            raise ValueError("unknown supervised action")
        if not event_id or not actor or not text:
            raise ValueError("missing synthetic source attribution")
        return cls(
            event_id=event_id,
            actor=actor,
            text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            action=action,
            evidence_class=GRANT_CLASS,
            verified_outcome=True,
        )

    def admissible(self, *, event_id: str, actor: str, text: str,
                   action: str) -> bool:
        return (
            bool(self.event_id) and self.event_id == event_id
            and bool(self.actor) and self.actor == actor
            and self.text_sha256 == hashlib.sha256(text.encode("utf-8")).hexdigest()
            and self.action == action
            and self.evidence_class == GRANT_CLASS
            and self.verified_outcome is True
        )


class NoeticCrucible:
    """Class-conditional three-factor update of existing sparse recurrent W.

    Teacher error travels through a fixed, architecture-native feedback map.
    The motor decoder receives supervision through its existing native method.
    E4-B never changes the production checkpoint schema or neural class code.
    """

    def __init__(self, substrate: PretoriusRecurrentSubstrate):
        if not isinstance(substrate, PretoriusRecurrentSubstrate):
            raise TypeError("expected native Pretorius recurrent substrate")
        self.neural = substrate
        self.eligibility = np.zeros_like(substrate.W.data, dtype=np.float32)
        # Action feedback routes are fixed by SAME-SEED native motor
        # populations, not learned motor weights or hand-authored characters.
        self.feedback = np.zeros((substrate.n, len(ACTIONS)), dtype=np.float32)
        for i, name in enumerate(ACTIONS):
            population = substrate.action_populations[name]
            if len(population) == 0:
                raise ValueError("empty action population")
            self.feedback[population, i] += np.float32(1.0 / len(population))
        self.accepted_outcomes = 0
        self.denied_outcomes = 0

    def teach(
        self, *,
        event_id: str,
        actor: str,
        text: str,
        action: str,
        grant: SyntheticOutcomeGrant,
        update_recurrence: bool,
    ) -> bool:
        if not isinstance(grant, SyntheticOutcomeGrant) or not grant.admissible(
            event_id=event_id, actor=actor, text=text, action=action
        ):
            self.denied_outcomes += 1
            return False
        if action not in ACTIONS:
            raise ValueError("invalid target action")
        if not isinstance(update_recurrence, bool):
            raise TypeError("update_recurrence must be a boolean")
        # Independent episodes cannot borrow action-specific eligibility from
        # one another. Fast neural state is also reset for matched controls.
        n = self.neural
        self.eligibility.fill(0.0)
        n.v.fill(0.0)
        n.rate.fill(n.target_rate)
        n.noise_state.fill(0.0)
        # Disable the native generic Hebbian path in ALL conditions. Only
        # this explicitly action-conditioned learning rule can change W.
        n.step(text, scalars=None, learn=False, reward=0.0)
        scores = n.action_scores()
        p = np.asarray([scores[name] for name in ACTIONS], dtype=np.float32)
        error = -p
        error[ACTIONS.index(action)] += 1.0

        if update_recurrence:
            post = (n.rate[n.post_idx] - n.target_rate).astype(np.float32)
            pre = (n.rate[n.pre_idx] - n.target_rate).astype(np.float32)
            self.eligibility *= np.float32(TRACE_DECAY)
            self.eligibility += post * pre
            teacher_feedback = self.feedback.dot(error)
            delta = np.float32(ETA) * teacher_feedback[n.post_idx] * self.eligibility
            delta = np.clip(delta, -UPDATE_LIMIT, UPDATE_LIMIT)
            if not np.all(np.isfinite(delta)):
                raise RuntimeError("nonfinite class-conditional synaptic update")
            n.W.data[:] += delta.astype(np.float32)
            n._enforce_sign_and_bounds()
            if not np.all(np.isfinite(n.W.data)):
                raise RuntimeError("nonfinite recurrent matrix")
        # Always identical supervised motor update in true-label arms.
        n.reinforce_action(action)
        self.accepted_outcomes += 1
        return True

    def weight_change(self, virgin: PretoriusRecurrentSubstrate) -> float:
        if not np.array_equal(self.neural.W.indices, virgin.W.indices) or not np.array_equal(
            self.neural.W.indptr, virgin.W.indptr
        ):
            raise ValueError("unaligned recurrent sparse topology")
        return float(np.linalg.norm(self.neural.W.data - virgin.W.data))
