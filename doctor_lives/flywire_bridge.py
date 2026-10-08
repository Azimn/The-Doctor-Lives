from __future__ import annotations

"""Thin adapters for whole-FlyWire Phase C experiments.

This module deliberately does not reimplement the Drosophila LIF simulator.
It validates and imports pinned upstream runtimes, builds an explicit engineered
Pretorius-to-afferent interface, and emits audit-friendly summaries.

The biological wiring and neuron dynamics remain upstream-owned research
artifacts. The Pretorius feature-to-afferent projection is artificial and must
not be interpreted as biological semantics.
"""

from dataclasses import dataclass
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence

import numpy as np

from .neural import ExperienceEncoder


@dataclass(frozen=True)
class UpstreamPin:
    repository: str
    commit: str
    purpose: str


UPSTREAM_PINS: dict[str, UpstreamPin] = {
    "shiu_reference": UpstreamPin(
        "philshiu/Drosophila_brain_model",
        "91bdd1e7dcf193f3e7ca5a8933497fcef63b7960",
        "published Shiu et al. LIF reference",
    ),
    "flybrain_multibackend": UpstreamPin(
        "eonsystemspbc/fly-brain",
        "a3db62f9436074e485c0278290c2164ed6150808",
        "FlyWire v783 multi-backend LIF runtime",
    ),
    "fastfly": UpstreamPin(
        "eonfathom/FastFly",
        "c84458b4a500a3101836a4535aaef4fa8a2566cc",
        "CUDA/CuPy whole-brain runtime and annotation tooling",
    ),
    "mlx_control": UpstreamPin(
        "Kisame76/drosophila-brain-mlx",
        "e417b33616513ef350b1b1c3cdf2b5b7a1799c8e",
        "fast LIF implementation and degree-preserving wiring control",
    ),
    "connectome_interpreter": UpstreamPin(
        "YijieYin/connectome_interpreter",
        "d212f86ef32318657dc27fa65e7e8ff604bffac9",
        "whole-connectome analysis toolkit",
    ),
}


FLYBRAIN_COMPLETENESS = Path("data/2025_Completeness_783.csv")
FLYBRAIN_CONNECTIVITY = Path("data/2025_Connectivity_783.parquet")


@dataclass(frozen=True)
class AnnotationPools:
    neuron_count: int
    afferent_indices: np.ndarray
    efferent_indices: np.ndarray
    root_ids: np.ndarray

    def summary(self) -> dict[str, int]:
        return {
            "neuron_count": int(self.neuron_count),
            "afferent_count": int(self.afferent_indices.size),
            "efferent_count": int(self.efferent_indices.size),
        }


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_array(array: np.ndarray) -> str:
    arr = np.ascontiguousarray(array)
    return hashlib.sha256(arr.view(np.uint8)).hexdigest()


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def git_head(checkout: str | Path) -> str:
    checkout = Path(checkout)
    proc = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def validate_pinned_checkout(checkout: str | Path, pin_name: str) -> str:
    if pin_name not in UPSTREAM_PINS:
        raise KeyError(f"unknown upstream pin: {pin_name}")
    checkout = Path(checkout)
    if not checkout.is_dir():
        raise FileNotFoundError(checkout)
    actual = git_head(checkout)
    expected = UPSTREAM_PINS[pin_name].commit
    if actual != expected:
        raise RuntimeError(
            f"{pin_name} checkout is {actual}, expected frozen commit {expected}"
        )
    return actual


def validate_flybrain_v783_checkout(checkout: str | Path) -> dict[str, Any]:
    checkout = Path(checkout)
    commit = validate_pinned_checkout(checkout, "flybrain_multibackend")
    comp = checkout / FLYBRAIN_COMPLETENESS
    conn = checkout / FLYBRAIN_CONNECTIVITY
    missing = [str(p) for p in (comp, conn) if not p.is_file()]
    if missing:
        raise FileNotFoundError(
            "pinned fly-brain checkout is missing required v783 data: "
            + ", ".join(missing)
        )
    return {
        "repository": UPSTREAM_PINS["flybrain_multibackend"].repository,
        "commit": commit,
        "completeness_path": str(comp),
        "connectivity_path": str(conn),
        "completeness_sha256": sha256_file(comp),
        "connectivity_sha256": sha256_file(conn),
    }


def _text_array(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values)
    if values.dtype.kind in {"U", "S"}:
        return values.astype("U", copy=False)
    return np.asarray([str(x) for x in values], dtype="U")


def load_annotation_pools(annotation_npz: str | Path) -> AnnotationPools:
    """Load FastFly-compatible annotation arrays and identify I/O pools.

    FastFly's annotation builder aligns arrays to the FlyWire completeness-file
    index. We use only array positions here; no biological class is mapped to a
    Pretorius concept.
    """

    payload = np.load(Path(annotation_npz), allow_pickle=False)
    if "root_ids" not in payload.files:
        raise ValueError("annotation npz must contain root_ids")

    root_ids = np.asarray(payload["root_ids"], dtype=np.int64)
    n = int(root_ids.size)
    if n == 0:
        raise ValueError("annotation npz contains no neurons")

    flow = _text_array(payload["flow"]) if "flow" in payload.files else np.full(n, "", dtype="U1")
    super_class = (
        _text_array(payload["super_class"])
        if "super_class" in payload.files
        else np.full(n, "", dtype="U1")
    )
    if flow.size != n or super_class.size != n:
        raise ValueError("annotation arrays must align one-to-one with root_ids")

    flow_l = np.char.lower(flow)
    super_l = np.char.lower(super_class)

    afferent = (flow_l == "afferent") | (super_l == "sensory")
    efferent = (flow_l == "efferent") | (super_l == "motor") | (super_l == "descending")

    afferent_indices = np.flatnonzero(afferent).astype(np.int64)
    efferent_indices = np.flatnonzero(efferent).astype(np.int64)

    if afferent_indices.size == 0:
        raise ValueError("annotation npz yielded no afferent/sensory neurons")
    if efferent_indices.size == 0:
        raise ValueError("annotation npz yielded no efferent/motor/descending neurons")

    return AnnotationPools(
        neuron_count=n,
        afferent_indices=afferent_indices,
        efferent_indices=efferent_indices,
        root_ids=root_ids,
    )


def build_pretorius_feature_vector(
    text: str,
    scalars: Mapping[str, float] | None = None,
) -> np.ndarray:
    """Use the existing generic Pretorius encoder without an action label."""

    encoder = ExperienceEncoder()
    return encoder.encode(text, scalars=dict(scalars or {}), action=None)


def _stable_slot(seed: int, feature_index: int, sign: int, slot: int, n: int) -> int:
    material = f"{seed}:{feature_index}:{sign}:{slot}".encode("utf-8")
    digest = hashlib.blake2b(material, digest_size=8).digest()
    return int.from_bytes(digest, "little", signed=False) % n


def project_features_to_afferents(
    features: Sequence[float] | np.ndarray,
    afferent_indices: Sequence[int] | np.ndarray,
    *,
    seed: int = 24017,
    fanout: int = 4,
    base_rate_hz: float = 20.0,
    feature_rate_hz: float = 100.0,
    max_rate_hz: float = 180.0,
) -> dict[int, float]:
    """Project generic features into a real afferent pool deterministically.

    This is an engineered interface, not a biological-semantic mapping. Feature
    sign participates in the hash, so +x and -x recruit separable afferent
    routes. Multiple features may converge on the same neuron; rates then add
    and are capped.
    """

    x = np.asarray(features, dtype=np.float64).reshape(-1)
    aff = np.sort(np.unique(np.asarray(afferent_indices, dtype=np.int64)))
    if aff.size == 0:
        raise ValueError("afferent_indices must not be empty")
    if fanout <= 0:
        raise ValueError("fanout must be positive")
    if base_rate_hz < 0 or feature_rate_hz < 0 or max_rate_hz <= 0:
        raise ValueError("rates must be non-negative and max_rate_hz positive")
    if not np.isfinite(x).all():
        raise ValueError("features contain non-finite values")

    rates: dict[int, float] = {}
    for feature_index, value in enumerate(x):
        if abs(float(value)) <= 1e-12:
            continue
        sign = 1 if value > 0 else -1
        amplitude = min(abs(float(value)), 1.0)
        contribution = base_rate_hz + feature_rate_hz * amplitude
        for slot in range(fanout):
            idx = int(aff[_stable_slot(seed, feature_index, sign, slot, aff.size)])
            rates[idx] = min(max_rate_hz, rates.get(idx, 0.0) + contribution)

    return dict(sorted(rates.items()))


def stimulus_manifest(
    *,
    text: str,
    scalars: Mapping[str, float] | None,
    rates_hz: Mapping[int, float],
    projection_seed: int,
    fanout: int,
) -> dict[str, Any]:
    payload = {
        "interface": "pretorius-generic-feature-to-flywire-afferent-v1",
        "biological_semantics_claimed": False,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "scalars": {str(k): float(v) for k, v in sorted((scalars or {}).items())},
        "projection_seed": int(projection_seed),
        "fanout": int(fanout),
        "stimulated_neurons": [
            {"index": int(i), "rate_hz": float(rate)}
            for i, rate in sorted(rates_hz.items())
        ],
    }
    payload["manifest_sha256"] = sha256_json(payload)
    return payload


def _import_pinned_flybrain_runtime(checkout: Path):
    code_dir = (checkout / "code").resolve()
    if not code_dir.is_dir():
        raise FileNotFoundError(code_dir)

    original_path = list(sys.path)
    try:
        sys.path.insert(0, str(code_dir))
        # run_pytorch imports sibling benchmark by its top-level module name.
        for name in ("run_pytorch", "benchmark"):
            existing = sys.modules.get(name)
            if existing is not None:
                origin = Path(getattr(existing, "__file__", "") or "").resolve()
                if code_dir not in origin.parents:
                    del sys.modules[name]
        module = importlib.import_module("run_pytorch")
    finally:
        sys.path[:] = original_path

    origin = Path(module.__file__).resolve()
    if code_dir not in origin.parents:
        raise RuntimeError(f"loaded run_pytorch from unexpected path: {origin}")
    return module


def run_upstream_lif_probe(
    checkout: str | Path,
    rates_hz: Mapping[int, float],
    *,
    duration_ms: float = 50.0,
    seed: int = 24017,
    device: str = "auto",
) -> tuple[dict[str, Any], np.ndarray]:
    """Run a custom stimulus through the pinned upstream v783 PyTorch LIF graph.

    Returns a compact JSON-safe summary and the complete per-neuron spike-count
    vector. The latter can be stored as an NPZ artifact by the caller.
    """

    checkout = Path(checkout)
    provenance = validate_flybrain_v783_checkout(checkout)
    runtime = _import_pinned_flybrain_runtime(checkout)

    try:
        import torch
    except ImportError as exc:  # pragma: no cover - depends on optional runtime
        raise RuntimeError(
            "The upstream fly-brain environment (including torch/pandas/pyarrow) "
            "must be installed to execute the 139K pilot."
        ) from exc

    if device == "auto":
        device_name = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device_name = device
    if device_name == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is false")

    comp = checkout / FLYBRAIN_COMPLETENESS
    conn = checkout / FLYBRAIN_CONNECTIVITY
    weights = runtime.get_weights(str(conn), str(comp), str(checkout / "data"), csr=True)
    weights = weights.to(device=device_name)
    num_neurons = int(weights.shape[0])

    clean_rates: dict[int, float] = {}
    for idx, rate in rates_hz.items():
        i = int(idx)
        r = float(rate)
        if i < 0 or i >= num_neurons:
            raise ValueError(f"stimulus index {i} outside 0..{num_neurons - 1}")
        if not np.isfinite(r) or r < 0:
            raise ValueError(f"invalid rate for neuron {i}: {r}")
        if r > 0:
            clean_rates[i] = r

    dt = float(runtime.DT)
    steps = int(round(float(duration_ms) / dt))
    if steps <= 0:
        raise ValueError("duration_ms must cover at least one upstream timestep")

    stimulated = sorted(clean_rates)
    model = runtime.TorchModel(
        1,
        num_neurons,
        runtime.DT,
        runtime.MODEL_PARAMS,
        weights,
        exc_indices=stimulated,
        device=device_name,
    )
    conductance, delay_buffer, spikes, voltage, refrac = model.state_init()
    rates = torch.zeros(1, num_neurons, device=device_name)
    for idx, rate in clean_rates.items():
        rates[0, idx] = rate

    torch.manual_seed(int(seed))
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(int(seed))
    try:
        generator = torch.Generator(device=device_name)
    except TypeError:  # older torch
        generator = torch.Generator()
    generator.manual_seed(int(seed))

    counts = torch.zeros(num_neurons, dtype=torch.int64, device=device_name)
    with torch.no_grad():
        for _ in range(steps):
            conductance, delay_buffer, spikes, voltage, refrac = model(
                rates,
                conductance,
                delay_buffer,
                spikes,
                voltage,
                refrac,
                generator=generator,
            )
            counts += (spikes[0] > 0).to(torch.int64)

    if device_name == "cuda":
        torch.cuda.synchronize()
    counts_np = counts.cpu().numpy().astype(np.int64, copy=False)
    active = np.flatnonzero(counts_np)
    top_order = np.argsort(counts_np, kind="stable")[-20:][::-1]
    top = [
        {"index": int(i), "spikes": int(counts_np[i])}
        for i in top_order
        if counts_np[i] > 0
    ]

    summary = {
        "runtime": provenance,
        "backend": "upstream-fly-brain-pytorch",
        "device": device_name,
        "duration_ms": float(duration_ms),
        "dt_ms": dt,
        "steps": steps,
        "seed": int(seed),
        "neurons": num_neurons,
        "stimulated_neurons": len(stimulated),
        "total_spikes": int(counts_np.sum()),
        "active_neurons": int(active.size),
        "spike_count_sha256": sha256_array(counts_np),
        "top_active": top,
    }
    summary["summary_sha256"] = sha256_json(summary)
    return summary, counts_np


def build_reproduction_command(
    checkout: str | Path,
    *,
    t_run_seconds: float = 0.1,
    trials: int = 1,
    backend: str = "pytorch",
) -> list[str]:
    """Build the unmodified upstream C00 reproduction command."""

    checkout = Path(checkout)
    validate_flybrain_v783_checkout(checkout)
    if backend != "pytorch":
        raise ValueError("initial adapter currently freezes backend='pytorch'")
    if t_run_seconds <= 0 or trials <= 0:
        raise ValueError("t_run_seconds and trials must be positive")
    return [
        sys.executable,
        str(checkout / "main.py"),
        "--pytorch",
        "--t_run",
        str(float(t_run_seconds)),
        "--n_run",
        str(int(trials)),
        "--no_log_file",
    ]
