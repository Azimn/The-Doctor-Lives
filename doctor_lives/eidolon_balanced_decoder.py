"""Eidolon E4-C: research-only, simultaneous class-balanced native readout.

A fixed ridge solution replaces sequential per-example teacher updates for
diagnostic comparison. No production brain/checkpoint/policy is modified.
"""
from __future__ import annotations

from dataclasses import dataclass
import copy
import math

import numpy as np

from .neural import ACTIONS, PretoriusRecurrentSubstrate

RIDGE_ALPHA = 0.10
LOGIT_SCALE = 4.0
DELAYS = (0, 3, 12)


def native_features(
    native: PretoriusRecurrentSubstrate, cue: str
) -> dict[int, np.ndarray]:
    """Extract unlabeled features from a fresh, read-only neural copy."""
    if not isinstance(native, PretoriusRecurrentSubstrate):
        raise TypeError("requires native Pretorius substrate")
    if not isinstance(cue, str):
        raise TypeError("cue must be text")
    subject = copy.deepcopy(native)
    subject.v.fill(0.0)
    subject.rate.fill(subject.target_rate)
    subject.noise_state.fill(0.0)
    subject.step(cue, learn=False)
    result = {}
    for delay in range(max(DELAYS) + 1):
        if delay:
            subject.step("", learn=False)
        if delay in DELAYS:
            feature = (subject.rate - subject.target_rate).astype(np.float64)
            norm = float(np.linalg.norm(feature))
            if norm > 1e-8:
                feature /= norm
            if feature.shape != (subject.n,) or not np.isfinite(feature).all():
                raise RuntimeError("invalid native feature")
            result[delay] = feature.copy()
    return result


@dataclass(frozen=True)
class BalancedReadout:
    """Independent vector linear readout; no native motor weight writes."""

    center: np.ndarray
    weights: np.ndarray
    intercept: np.ndarray
    alpha: float
    n_rows: int
    training_classes: tuple[str, ...]

    @classmethod
    def fit(
        cls, features: np.ndarray, labels: list[str] | tuple[str, ...],
        *, alpha: float = RIDGE_ALPHA
    ) -> "BalancedReadout":
        X = np.asarray(features, dtype=np.float64)
        if X.ndim != 2 or X.shape[0] != len(labels) or X.shape[0] < 2:
            raise ValueError("invalid feature matrix or labels")
        if not np.isfinite(X).all() or not math.isfinite(alpha) or alpha <= 0:
            raise ValueError("nonfinite data or invalid regularization")
        if any(label not in ACTIONS for label in labels):
            raise ValueError("unknown motor label")
        counts = {name: labels.count(name) for name in sorted(set(labels))}
        if len(counts) < 2 or len(set(counts.values())) != 1:
            raise ValueError("requires multiple equally represented classes")
        Y = np.zeros((len(labels), len(ACTIONS)), dtype=np.float64)
        for ix, label in enumerate(labels):
            Y[ix, ACTIONS.index(label)] = 1.0
        center = X.mean(axis=0)
        Z = X - center
        intercept = Y.mean(axis=0)
        # Fixed, simultaneous full-data regularized least squares: no
        # iterative presentation-order/terminal-class learning update.
        weights = np.linalg.solve(
            Z.T @ Z + alpha * np.eye(X.shape[1], dtype=np.float64),
            Z.T @ (Y - intercept)
        )
        if not np.isfinite(weights).all():
            raise RuntimeError("invalid balanced readout weights")
        return cls(
            center=center, weights=weights, intercept=intercept,
            alpha=float(alpha), n_rows=len(labels),
            training_classes=tuple(sorted(counts)),
        )

    def scores(self, feature: np.ndarray) -> dict[str, float]:
        x = np.asarray(feature, dtype=np.float64)
        if x.shape != self.center.shape or not np.isfinite(x).all():
            raise ValueError("feature shape or finite contract failed")
        logits = LOGIT_SCALE * ((x - self.center) @ self.weights + self.intercept)
        logits -= logits.max()
        prob = np.exp(logits)
        prob /= prob.sum()
        if not np.isfinite(prob).all() or abs(float(prob.sum()) - 1) > 1e-8:
            raise RuntimeError("non-normalized readout")
        return {name: float(value) for name, value in zip(ACTIONS, prob)}
