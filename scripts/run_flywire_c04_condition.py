#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from doctor_lives.flywire_adapter import (
    FLY_BRAIN_BACKEND_SHA,
    PROTOCOL_ID,
    canonical_manifest_sha256,
    centered_context_separation,
    effective_dimensionality,
    summarize_topology,
    uncentered_context_separation,
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a.astype(np.float64)) * np.linalg.norm(b.astype(np.float64)))
    return 0.0 if denom < 1e-12 else float(np.dot(a.astype(np.float64), b.astype(np.float64)) / denom)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--backend", required=True, type=Path)
    p.add_argument("--connectivity", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--condition", required=True)
    p.add_argument("--topology-seed", required=True)
    p.add_argument("--output-dir", required=True, type=Path)
    args = p.parse_args()

    head = subprocess.check_output(
        ["git", "-C", str(args.backend), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != FLY_BRAIN_BACKEND_SHA:
        raise RuntimeError("backend SHA mismatch")

    sys.path.insert(0, str(args.backend / "code"))
    from run_pytorch import DT, MODEL_PARAMS, TorchModel, get_hash_tables, get_weights

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    stored_manifest_sha = manifest["manifest_sha256"]
    material = dict(manifest)
    material.pop("manifest_sha256")
    if canonical_manifest_sha256(material) != stored_manifest_sha:
        raise RuntimeError("manifest hash mismatch")
    if stored_manifest_sha != "7204b9ac2860d94b5ac28edb5976695831b61e366a920da67629ee8c99a13228":
        raise RuntimeError("C04 manifest is not the frozen C03 semantic manifest")

    comp = args.backend / "data" / "2025_Completeness_783.csv"
    flyid2i, _ = get_hash_tables(str(comp))
    n = len(flyid2i)
    if n != 138639:
        raise RuntimeError(f"unexpected neuron count {n}")

    probes = manifest["probes"]
    labels = [str(p["family"]) for p in probes]
    driven_ids = sorted({int(v) for p in probes for v in p["afferent_ids"]})
    if any(v not in flyid2i for v in driven_ids):
        raise RuntimeError("manifest afferent absent from backend")
    driven_indices = [flyid2i[v] for v in driven_ids]

    conn = pd.read_parquet(
        args.connectivity,
        columns=["Presynaptic_Index", "Postsynaptic_Index", "Excitatory x Connectivity"],
    )
    topology = summarize_topology(
        n,
        conn["Presynaptic_Index"].to_numpy(dtype=np.int64, copy=False),
        conn["Postsynaptic_Index"].to_numpy(dtype=np.int64, copy=False),
        conn["Excitatory x Connectivity"].to_numpy(dtype=np.float32, copy=False),
    )
    del conn

    device = "cuda" if torch.cuda.is_available() else "cpu"
    cache = args.output_dir / "weight-cache"
    cache.mkdir(parents=True, exist_ok=True)
    setup_start = time.perf_counter()
    weights = get_weights(str(args.connectivity), str(comp), str(cache), csr=True).to(device)
    model = TorchModel(
        1, n, DT, MODEL_PARAMS, weights,
        exc_indices=driven_indices, device=device,
    )
    setup_seconds = time.perf_counter() - setup_start

    duration_ms = 50.0
    max_rate = 150.0
    trial_seeds = [8301, 8302, 8303]
    steps = int(round(duration_ms / DT))
    if steps != 500:
        raise RuntimeError("unexpected integration step count")

    trial_rates = np.zeros((12, 3, n), dtype=np.float32)
    trial_seconds = []
    sim_start = time.perf_counter()
    with torch.no_grad():
        for pi, probe in enumerate(probes):
            rates = torch.zeros(1, n, device=device)
            ids = [int(v) for v in probe["afferent_ids"]]
            vals = [float(v) for v in probe["relative_drive"]]
            idx = torch.tensor([flyid2i[v] for v in ids], dtype=torch.long, device=device)
            rates[0, idx] = torch.tensor(vals, dtype=torch.float32, device=device) * max_rate
            probe_times = []
            for ti, seed in enumerate(trial_seeds):
                conductance, delay_buffer, spikes, voltage, refrac = model.state_init()
                counts = torch.zeros(n, dtype=torch.float32, device=device)
                gen = torch.Generator(device=device)
                gen.manual_seed(seed)
                t0 = time.perf_counter()
                for _ in range(steps):
                    conductance, delay_buffer, spikes, voltage, refrac = model(
                        rates, conductance, delay_buffer, spikes, voltage, refrac,
                        generator=gen,
                    )
                    counts += spikes[0]
                if device == "cuda":
                    torch.cuda.synchronize()
                probe_times.append(time.perf_counter() - t0)
                trial_rates[pi, ti] = counts.cpu().numpy() / 0.05
            trial_seconds.append(probe_times)
    sim_seconds = time.perf_counter() - sim_start

    mean_rates = trial_rates.mean(axis=1)
    repro_per_probe = []
    for p in trial_rates:
        repro_per_probe.append(float(np.mean([
            cosine(p[0], p[1]), cosine(p[0], p[2]), cosine(p[1], p[2])
        ])))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    response_path = args.output_dir / "c04_condition_responses.npz"
    np.savez_compressed(
        response_path,
        trial_rates_hz=trial_rates,
        mean_rates_hz=mean_rates,
        labels=np.asarray(labels),
        trial_seeds=np.asarray(trial_seeds, dtype=np.int64),
    )

    summary = {
        "protocol_id": PROTOCOL_ID,
        "condition": args.condition,
        "topology_seed": args.topology_seed,
        "backend_sha": head,
        "manifest_sha256": stored_manifest_sha,
        "connectivity_file_sha256": sha256_file(args.connectivity),
        "topology": {
            "neurons": topology.neurons,
            "edges": topology.edges,
            "excitatory_edges": topology.excitatory_edges,
            "inhibitory_edges": topology.inhibitory_edges,
            "zero_weight_edges": topology.zero_weight_edges,
            "fingerprint_sha256": topology.fingerprint_sha256,
        },
        "centered_context_separation": centered_context_separation(mean_rates, labels),
        "uncentered_context_separation": uncentered_context_separation(mean_rates, labels),
        "effective_dimensionality": float(effective_dimensionality(mean_rates)),
        "trial_reproducibility": {
            "mean": float(np.mean(repro_per_probe)),
            "min": float(np.min(repro_per_probe)),
            "max": float(np.max(repro_per_probe)),
            "per_probe_mean_pair_cosine": repro_per_probe,
        },
        "firing": {
            "mean_hz": float(mean_rates.mean()),
            "std_hz": float(mean_rates.std()),
            "max_hz": float(mean_rates.max()),
            "active_fraction_per_probe": [
                float(np.count_nonzero(v > 0) / n) for v in mean_rates
            ],
        },
        "runtime": {
            "model_setup_seconds": setup_seconds,
            "simulation_seconds": sim_seconds,
            "per_probe_trial_seconds": trial_seconds,
        },
        "response_npz_sha256": sha256_file(response_path),
    }
    summary["summary_sha256"] = canonical_manifest_sha256(summary)
    (args.output_dir / "c04_condition_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
