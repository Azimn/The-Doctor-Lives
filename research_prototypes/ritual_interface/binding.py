"""Bounded relevance proposal only; never changes UPPB awareness decisions."""
from __future__ import annotations

import math


def _unit(name: str, value: float) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{name} cannot be boolean")
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be numeric") from exc
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite between zero and one")
    return value


def propose_self_relevance(*, self_prior_gain: float, source_relevance: float, bounded_max: float = 0.10) -> float:
    """Nonnegative proposal; zero gain cannot suppress contradictory perceptions."""
    gain = _unit("self_prior_gain", self_prior_gain)
    relevance = _unit("source_relevance", source_relevance)
    maximum = _unit("bounded_max", bounded_max)
    if maximum > 0.10:
        raise ValueError("prototype modulation cap is 0.10")
    return gain * relevance * maximum
