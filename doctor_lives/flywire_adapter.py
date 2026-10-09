from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


FLYWIRE_DATASET = "FAFB/FlyWire v783"
SHIU_REFERENCE_SHA = "91bdd1e7dcf193f3e7ca5a8933497fcef63b7960"
FLY_BRAIN_BACKEND_SHA = "a3db62f9436074e485c0278290c2164ed6150808"
FASTFLY_SHA = "c84458b4a500a3101836a4535aaef4fa8a2566cc"
CONNECTOME_INTERPRETER_SHA = "d212f86ef32318657dc27fa65e7e8ff604bffac9"
PROTOCOL_ID = "pretorius-flywire-whole-connectome-c01-v2"


@dataclass(frozen=True)
class TopologySummary:
    neurons: int
    edges: int
    excitatory_edges: int
    inhibitory_edges: int
    zero_weight_edges: int
    fingerprint_sha256: str


def _as_int64(values: Sequence[int] | np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(np.asarray(values, dtype=np.int64))


def _as_float32(values: Sequence[float] | np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(np.asarray(values, dtype=np.float32))


def topology_fingerprint(
    n_neurons: int,
    pre: Sequence[int] | np.ndarray,
    post: Sequence[int] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
) -> str:
    """Hash a directed weighted topology in its supplied edge order.

    The normalized byte representation is independent of the caller's integer
    and floating-point dtypes. Edge order remains part of the fingerprint so a
    transformed manifest cannot masquerade as the source graph.
    """
    pre_a = _as_int64(pre)
    post_a = _as_int64(post)
    weight_a = _as_float32(weights)
    if not (len(pre_a) == len(post_a) == len(weight_a)):
        raise ValueError("pre, post and weights must have equal length")
    if int(n_neurons) <= 0:
        raise ValueError("n_neurons must be positive")
    if len(pre_a):
        if pre_a.min() < 0 or post_a.min() < 0:
            raise ValueError("negative neuron index")
        if pre_a.max() >= n_neurons or post_a.max() >= n_neurons:
            raise ValueError("edge endpoint outside topology")
    if not np.isfinite(weight_a).all():
        raise ValueError("non-finite weight")

    h = hashlib.sha256()
    h.update(b"pretorius-flywire-topology-v1\0")
    h.update(np.asarray([int(n_neurons), len(pre_a)], dtype=np.int64).tobytes())
    h.update(pre_a.tobytes())
    h.update(post_a.tobytes())
    h.update(weight_a.tobytes())
    return h.hexdigest()


def summarize_topology(
    n_neurons: int,
    pre: Sequence[int] | np.ndarray,
    post: Sequence[int] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
) -> TopologySummary:
    weight_a = _as_float32(weights)
    fp = topology_fingerprint(n_neurons, pre, post, weight_a)
    return TopologySummary(
        neurons=int(n_neurons),
        edges=int(len(weight_a)),
        excitatory_edges=int(np.count_nonzero(weight_a > 0)),
        inhibitory_edges=int(np.count_nonzero(weight_a < 0)),
        zero_weight_edges=int(np.count_nonzero(weight_a == 0)),
        fingerprint_sha256=fp,
    )


def endpoint_shuffle_smoke_control(
    pre: Sequence[int] | np.ndarray,
    post: Sequence[int] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
    *,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return an outcome-blind endpoint shuffle for engineering smoke tests.

    Presynaptic endpoints stay fixed and the complete postsynaptic endpoint
    vector is permuted. Therefore every neuron's directed out-degree and
    in-degree counts are preserved exactly and the global weight multiset is
    unchanged.

    This operation can introduce self-loops and parallel edges. It is therefore
    *not* the decisive C04 rewiring unless a later audit explicitly accepts
    those properties. The name intentionally says smoke_control.
    """
    pre_a = _as_int64(pre)
    post_a = _as_int64(post)
    weight_a = _as_float32(weights)
    if not (len(pre_a) == len(post_a) == len(weight_a)):
        raise ValueError("pre, post and weights must have equal length")
    rng = np.random.default_rng(int(seed))
    shuffled_post = post_a[rng.permutation(len(post_a))]
    return pre_a.copy(), shuffled_post, weight_a.copy()


def random_edge_count_smoke_control(
    n_neurons: int,
    edge_count: int,
    weights: Sequence[float] | np.ndarray,
    *,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Create a scale/edge-count matched engineering control.

    This is deliberately an Erdős-Rényi-like smoke control, not a degree-matched
    scientific control. Self-loops are removed deterministically by advancing
    the postsynaptic index by one modulo N.
    """
    n_neurons = int(n_neurons)
    edge_count = int(edge_count)
    if n_neurons < 2 or edge_count < 0:
        raise ValueError("invalid graph size")
    weights_a = _as_float32(weights)
    if len(weights_a) != edge_count:
        raise ValueError("weight count must equal edge_count")
    rng = np.random.default_rng(int(seed))
    pre = rng.integers(0, n_neurons, size=edge_count, dtype=np.int64)
    post = rng.integers(0, n_neurons, size=edge_count, dtype=np.int64)
    same = post == pre
    post[same] = (post[same] + 1) % n_neurons
    shuffled_weights = weights_a[rng.permutation(edge_count)]
    return pre, post, shuffled_weights


def project_features_to_afferents(
    features: Sequence[float] | np.ndarray,
    candidate_neuron_ids: Sequence[int] | np.ndarray,
    *,
    fanout_per_feature: int = 2,
    seed: int = 7301,
) -> tuple[np.ndarray, np.ndarray]:
    """Project generic encoder features onto a frozen candidate afferent pool.

    No biological cell type is assigned a Pretorius semantic role. A feature's
    index and sign determine a stable BLAKE2 mapping; shared encoder features
    therefore share some driven afferents. Returned drive is non-negative so it
    can directly scale Poisson stimulation rates.
    """
    x = np.asarray(features, dtype=np.float64).reshape(-1)
    candidates = _as_int64(candidate_neuron_ids)
    if not len(candidates):
        raise ValueError("candidate afferent pool is empty")
    if len(np.unique(candidates)) != len(candidates):
        raise ValueError("candidate afferent ids must be unique")
    fanout = int(fanout_per_feature)
    if fanout <= 0:
        raise ValueError("fanout_per_feature must be positive")
    if not np.isfinite(x).all():
        raise ValueError("feature vector contains non-finite values")

    accum: dict[int, float] = {}
    for feature_index in np.flatnonzero(np.abs(x) > 0):
        value = float(x[feature_index])
        sign = "pos" if value >= 0 else "neg"
        for slot in range(fanout):
            token = f"{int(seed)}|{int(feature_index)}|{sign}|{slot}".encode("utf-8")
            digest = hashlib.blake2b(token, digest_size=8).digest()
            candidate_offset = int.from_bytes(digest, "little") % len(candidates)
            neuron_id = int(candidates[candidate_offset])
            accum[neuron_id] = accum.get(neuron_id, 0.0) + abs(value)

    if not accum:
        return np.empty(0, dtype=np.int64), np.empty(0, dtype=np.float32)

    neuron_ids = np.asarray(sorted(accum), dtype=np.int64)
    drive = np.asarray([accum[int(n)] for n in neuron_ids], dtype=np.float32)
    peak = float(drive.max())
    if peak > 0:
        drive /= peak
    return neuron_ids, drive


def centered_context_separation(
    states: Sequence[Sequence[float]] | np.ndarray,
    labels: Sequence[str],
) -> dict[str, float | int]:
    """Compute the preregistered centered within-minus-across cosine metric."""
    x = np.asarray(states, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError("states must be a 2D probe-by-neuron matrix")
    if x.shape[0] != len(labels):
        raise ValueError("label count must equal probe count")
    if x.shape[0] < 2:
        raise ValueError("at least two probes are required")
    if not np.isfinite(x).all():
        raise ValueError("states contain non-finite values")

    centered = x - x.mean(axis=0, keepdims=True)
    norms = np.linalg.norm(centered, axis=1)
    normalized = np.zeros_like(centered)
    valid = norms >= 1e-12
    normalized[valid] = centered[valid] / norms[valid, None]
    gram = normalized @ normalized.T

    within: list[float] = []
    across: list[float] = []
    for i in range(x.shape[0]):
        for j in range(i + 1, x.shape[0]):
            if labels[i] == labels[j]:
                within.append(float(gram[i, j]))
            else:
                across.append(float(gram[i, j]))
    if not within or not across:
        raise ValueError("labels must provide at least one within and one across pair")

    within_mean = float(np.mean(within))
    across_mean = float(np.mean(across))
    return {
        "within_pairs": len(within),
        "across_pairs": len(across),
        "within_mean": within_mean,
        "across_mean": across_mean,
        "separation": within_mean - across_mean,
    }


def effective_dimensionality(states: Sequence[Sequence[float]] | np.ndarray) -> float:
    """Participation ratio of centered probe states via the sample Gram matrix."""
    x = np.asarray(states, dtype=np.float64)
    if x.ndim != 2 or x.shape[0] < 2:
        raise ValueError("states must be a 2D matrix with at least two probes")
    if not np.isfinite(x).all():
        raise ValueError("states contain non-finite values")
    centered = x - x.mean(axis=0, keepdims=True)
    gram = centered @ centered.T
    trace = float(np.trace(gram))
    denom = float(np.sum(gram * gram))
    if trace <= 0.0 or denom <= 0.0:
        return 0.0
    return (trace * trace) / denom


def canonical_manifest_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def uncentered_context_separation(
    states: Sequence[Sequence[float]] | np.ndarray,
    labels: Sequence[str],
) -> dict[str, float | int]:
    """Compute within-minus-across cosine on uncentered response vectors."""
    x = np.asarray(states, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError("states must be a 2D probe-by-neuron matrix")
    if x.shape[0] != len(labels):
        raise ValueError("label count must equal probe count")
    if x.shape[0] < 2:
        raise ValueError("at least two probes are required")
    if not np.isfinite(x).all():
        raise ValueError("states contain non-finite values")

    norms = np.linalg.norm(x, axis=1)
    normalized = np.zeros_like(x)
    valid = norms >= 1e-12
    normalized[valid] = x[valid] / norms[valid, None]
    gram = normalized @ normalized.T

    within: list[float] = []
    across: list[float] = []
    for i in range(x.shape[0]):
        for j in range(i + 1, x.shape[0]):
            if labels[i] == labels[j]:
                within.append(float(gram[i, j]))
            else:
                across.append(float(gram[i, j]))
    if not within or not across:
        raise ValueError("labels must provide at least one within and one across pair")

    within_mean = float(np.mean(within))
    across_mean = float(np.mean(across))
    return {
        "within_pairs": len(within),
        "across_pairs": len(across),
        "within_mean": within_mean,
        "across_mean": across_mean,
        "separation": within_mean - across_mean,
    }
