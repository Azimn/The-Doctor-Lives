"""The Eidolon Engine v0.1: opt-in, engineer-only cognitive binding pilot.

The Janus Gate controls whether an event may teach a self-owned association.
The Synthema Lattice is a small trainable cue-to-policy associative matrix.
A decaying recurrent trace maintains candidate intention across interruptions.

This is a *shadow* researcher instrument: it never rewrites Pretorius memory,
neural checkpoints, policy decisions, or subject-accessible representations.
It is not evidence of consciousness or a trained biological connectome.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import re
import unicodedata
from typing import Mapping

import numpy as np

from .models import Experience
from .neural import ACTIONS


def _unit(x: float, name: str) -> float:
    if isinstance(x, bool) or not math.isfinite(float(x)):
        raise ValueError(f"{name} must be finite")
    x = float(x)
    if not 0 <= x <= 1:
        raise ValueError(f"{name} must be in [0, 1]")
    return x


@dataclass(frozen=True)
class EidolonConfig:
    features: int = 256
    learning_rate: float = 0.9
    trace_decay: float = 0.83
    output_gain: float = 2.0
    min_binding_confidence: float = 0.5
    source_schema: str = "eidolon-shadow-v0.1"

    def __post_init__(self) -> None:
        if not isinstance(self.features, int) or self.features < 32:
            raise ValueError("features must be an integer >= 32")
        for key in ("learning_rate", "trace_decay", "min_binding_confidence"):
            _unit(getattr(self, key), key)
        if not math.isfinite(float(self.output_gain)) or not 0 <= self.output_gain <= 8:
            raise ValueError("output_gain must be in [0, 8]")


@dataclass(frozen=True)
class BindingObservation:
    action_scores: dict[str, float]
    base_scores: dict[str, float]
    binding_strength: float
    recurrent_strength: float
    learned: bool
    tick: int
    # All values here are engineer-only; no first-person claims.


class JanusGate:
    """Only directly lived, adequately supported events train self-associations."""

    def __init__(self, config: EidolonConfig):
        self.config = config

    def may_bind(self, exp: Experience) -> bool:
        return (
            isinstance(exp, Experience)
            and not exp.external
            and exp.confidence >= self.config.min_binding_confidence
        )


class SynthemaLattice:
    """Deterministic lexical/relational features, trainable associative weights.

    Hashed words are NOT semantic embeddings. The actor conjunction supplies
    a relation-specific feature but does not authenticate the actor.
    """

    def __init__(self, config: EidolonConfig):
        self.config = config
        self.weights = np.zeros((len(ACTIONS), config.features), dtype=np.float64)

    def features_for(self, exp: Experience) -> np.ndarray:
        normalized = unicodedata.normalize("NFC", exp.text.casefold())
        words = sorted(set(re.findall(r"\\w+", normalized, flags=re.UNICODE)))
        glyphs = sorted({ch for ch in normalized
                         if unicodedata.category(ch).startswith("S")})
        if not words and not glyphs:
            raise ValueError("no cue features")
        tokens = ["word:" + w for w in words] + ["glyph:" + g for g in glyphs]
        terms = list(tokens)
        if exp.actor:
            actor = unicodedata.normalize("NFC", exp.actor.casefold().strip())
            terms += ["relation:" + actor + ":" + t for t in tokens]
        x = np.zeros(self.config.features, dtype=np.float64)
        for term in terms:
            digest = hashlib.blake2b(term.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest, "big") % self.config.features
            x[index] += 1
        norm = np.linalg.norm(x)
        return x / norm

    def association(self, features: np.ndarray) -> np.ndarray:
        return self.weights @ features

    def bind(self, features: np.ndarray, action: str) -> None:
        target = np.zeros(len(ACTIONS), dtype=np.float64)
        target[ACTIONS.index(action)] = 1.0
        prediction = self.association(features)
        # Bounded supervised delta, with weights clipped to protect stability.
        self.weights += self.config.learning_rate * np.outer(target - prediction, features)
        np.clip(self.weights, -3.0, 3.0, out=self.weights)


class EidolonEngine:
    """Shadow recurrent cognitive-state binding. Nothing calls Pretorius.think.

    First bind a grounded cue and an explicit prospective action in a controlled
    training episode. Then apply cues/distractors in subsequent episodes, and
    observe whether the trained association persists through the recurrence.
    """

    def __init__(self, config: EidolonConfig | None = None):
        self.config = config or EidolonConfig()
        self.janus = JanusGate(self.config)
        self.synthema = SynthemaLattice(self.config)
        self.intention_trace = np.zeros(len(ACTIONS), dtype=np.float64)
        self.tick = 0

    @staticmethod
    def _probabilities(scores: Mapping[str, float]) -> np.ndarray:
        if set(scores) != set(ACTIONS):
            raise ValueError("base policy must contain all ten Pretorius actions")
        values = np.asarray([scores[k] for k in ACTIONS], dtype=np.float64)
        if not np.all(np.isfinite(values)) or np.any(values < 0) or values.sum() <= 0:
            raise ValueError("base policy scores must be nonnegative and finite")
        return values / values.sum()

    def observe(
        self,
        exp: Experience,
        base_scores: Mapping[str, float],
        *,
        teaching_action: str | None = None,
        learn: bool = False,
        lesion_recurrence: bool = False,
        lesion_binding: bool = False,
    ) -> BindingObservation:
        if not isinstance(exp, Experience):
            raise TypeError("input must be a projected Pretorius Experience")
        if teaching_action is not None and teaching_action not in ACTIONS:
            raise ValueError("unknown prospective action")
        if learn and teaching_action is None:
            raise ValueError("learning requires a prespecified teaching action")
        if learn and not self.janus.may_bind(exp):
            raise ValueError("Janus Gate refuses non-lived or weakly supported training")
        base = self._probabilities(base_scores)
        cue = self.synthema.features_for(exp)
        self.tick += 1
        if learn and not lesion_binding:
            self.synthema.bind(cue, teaching_action)
        affinity = (
            np.zeros(len(ACTIONS), dtype=np.float64)
            if lesion_binding else self.synthema.association(cue)
        )
        if lesion_recurrence:
            self.intention_trace.fill(0.0)
        else:
            self.intention_trace *= self.config.trace_decay
        self.intention_trace += affinity
        np.clip(self.intention_trace, -4.0, 4.0, out=self.intention_trace)
        # Fixed readout, not a trainable motor decoder. The recurrent trace
        # supplies the proposed long-horizon effect.
        logits = np.log(np.maximum(base, 1e-12)) + (
            self.config.output_gain * self.intention_trace
        )
        logits -= logits.max()
        posterior = np.exp(logits)
        posterior /= posterior.sum()
        return BindingObservation(
            action_scores=dict(zip(ACTIONS, map(float, posterior))),
            base_scores=dict(zip(ACTIONS, map(float, base))),
            binding_strength=float(np.linalg.norm(affinity)),
            recurrent_strength=float(np.linalg.norm(self.intention_trace)),
            learned=bool(learn and not lesion_binding),
            tick=self.tick,
        )

    def observe_pretorius(
        self,
        brain: object,
        exp: Experience,
        **kwargs: object,
    ) -> BindingObservation:
        """Read real Pretorius recurrent policy; do NOT ingest or change brain."""
        from .cognition import PretoriusBrain
        if not isinstance(brain, PretoriusBrain):
            raise TypeError("expected PretoriusBrain")
        return self.observe(exp, brain.neural.action_scores(), **kwargs)

    def snapshot(self) -> dict:
        return {
            "schema": self.config.source_schema,
            "config": vars(self.config),
            "tick": self.tick,
            "weights": self.synthema.weights.tolist(),
            "intention_trace": self.intention_trace.tolist(),
        }

    @classmethod
    def from_snapshot(cls, data: Mapping) -> "EidolonEngine":
        if not isinstance(data, Mapping) or data.get("schema") != "eidolon-shadow-v0.1":
            raise ValueError("unsupported shadow snapshot schema")
        config = EidolonConfig(**data["config"])
        obj = cls(config)
        weights = np.asarray(data["weights"], dtype=np.float64)
        trace = np.asarray(data["intention_trace"], dtype=np.float64)
        if (weights.shape != obj.synthema.weights.shape
                or trace.shape != obj.intention_trace.shape
                or not np.isfinite(weights).all()
                or not np.isfinite(trace).all()
                or np.max(np.abs(weights)) > 3.0
                or np.max(np.abs(trace)) > 4.0):
            raise ValueError("invalid shadow snapshot state")
        tick = data["tick"]
        if isinstance(tick, bool) or not isinstance(tick, int) or tick < 0:
            raise ValueError("invalid shadow snapshot tick")
        obj.synthema.weights = weights.copy()
        obj.intention_trace = trace.copy()
        obj.tick = tick
        return obj
