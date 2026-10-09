#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
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


def verify_backend(repo: Path) -> str:
    head = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    if head != FLY_BRAIN_BACKEND_SHA:
        raise RuntimeError(
            f"backend SHA mismatch: expected {FLY_BRAIN_BACKEND_SHA}, got {head}"
        )
    return head


def verify_manifest(manifest: dict) -> str:
    stored = str(manifest.get("manifest_sha256", ""))
    material = dict(manifest)
    material.pop("manifest_sha256", None)
    computed = canonical_manifest_sha256(material)
    if stored != computed:
        raise RuntimeError(f"manifest hash mismatch: {stored} != {computed}")
    if manifest.get("protocol_id") != PROTOCOL_ID:
        raise RuntimeError("manifest protocol mismatch")
    if manifest.get("backend_sha") != FLY_BRAIN_BACKEND_SHA:
        raise RuntimeError("manifest backend SHA mismatch")
    return computed


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a, dtype=np.float64)
    bb = np.asarray(b, dtype=np.float64)
    denom = float(np.linalg.norm(aa) * np.linalg.norm(bb))
    if denom < 1e-12:
        return 0.0
    return float(np.dot(aa, bb) / denom)


def trial_reproducibility(trial_rates: np.ndarray) -> dict[str, object]:
    per_probe = []
    for probe_trials in trial_rates:
        vals = []
        for i in range(probe_trials.shape[0]):
            for j in range(i + 1, probe_trials.shape[0]):
                vals.append(cosine(probe_trials[i], probe_trials[j]))
        per_probe.append(float(np.mean(vals)) if vals else 0.0)
    return {
        "per_probe_mean_pair_cosine": per_probe,
        "mean": float(np.mean(per_probe)),
        "min": float(np.min(per_probe)),
        "max": float(np.max(per_probe)),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--backend", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--duration-ms", type=float, default=50.0)
    p.add_argument("--stim-rate-hz", type=float, default=150.0)
    p.add_argument("--trial-seeds", nargs="+", type=int, default=[8301, 8302, 8303])
    args = p.parse_args()

    if args.duration_ms != 50.0:
        raise SystemExit("C03 frozen duration is exactly 50.0 ms")
    if args.stim_rate_hz != 150.0:
        raise SystemExit("C03 frozen maximum stimulation rate is exactly 150.0 Hz")
    if args.trial_seeds != [8301, 8302, 8303]:
        raise SystemExit("C03 frozen trial seeds are 8301, 8302, 8303")

    backend_sha = verify_backend(args.backend)
    code_dir = args.backend / "code"
    sys.path.insert(0, str(code_dir))
    from run_pytorch import DT, MODEL_PARAMS, TorchModel, get_hash_tables, get_weights

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest_sha = verify_manifest(manifest)
    probes = manifest["probes"]
    if len(probes) != 12:
        raise RuntimeError(f"C03 requires 12 probes, got {len(probes)}")

    comp_path = args.backend / "data" / "2025_Completeness_783.csv"
    con_path = args.backend / "data" / "2025_Connectivity_783.parquet"
    flyid2i, _ = get_hash_tables(str(comp_path))
    n_neurons = len(flyid2i)
    if n_neurons != 138639:
        raise RuntimeError(f"expected 138639 backend neurons, got {n_neurons}")

    driven_ids = sorted(
        {
            int(neuron_id)
            for probe in probes
            for neuron_id in probe["afferent_ids"]
        }
    )
    missing = [v for v in driven_ids if v not in flyid2i]
    if missing:
        raise RuntimeError(f"manifest contains {len(missing)} IDs absent from backend")
    driven_indices = [flyid2i[v] for v in driven_ids]

    connectivity = pd.read_parquet(
        con_path,
        columns=["Presynaptic_Index", "Postsynaptic_Index", "Excitatory x Connectivity"],
    )
    topology = summarize_topology(
        n_neurons,
        connectivity["Presynaptic_Index"].to_numpy(dtype=np.int64, copy=False),
        connectivity["Postsynaptic_Index"].to_numpy(dtype=np.int64, copy=False),
        connectivity["Excitatory x Connectivity"].to_numpy(dtype=np.float32, copy=False),
    )
    del connectivity

    device = "cuda" if torch.cuda.is_available() else "cpu"
    start = time.perf_counter()
    weights = get_weights(str(con_path), str(comp_path), str(args.backend / "data"), csr=True)
    weights = weights.to(device=device)
    model = TorchModel(
        1,
        n_neurons,
        DT,
        MODEL_PARAMS,
        weights,
        exc_indices=driven_indices,
        device=device,
    )
    setup_seconds = time.perf_counter() - start

    steps = int(round(args.duration_ms / DT))
    if steps != 500:
        raise RuntimeError(f"expected 500 steps, got {steps}")
    duration_seconds = args.duration_ms / 1000.0

    trial_rates = np.zeros(
        (len(probes), len(args.trial_seeds), n_neurons), dtype=np.float32
    )
    per_trial_seconds: list[list[float]] = []

    run_start = time.perf_counter()
    with torch.no_grad():
        for pi, probe in enumerate(probes):
            rates = torch.zeros(1, n_neurons, device=device)
            ids = [int(v) for v in probe["afferent_ids"]]
            drives = [float(v) for v in probe["relative_drive"]]
            if len(ids) != len(drives) or not ids:
                raise RuntimeError(f"invalid drive manifest for probe {pi}")
            idx = torch.tensor([flyid2i[v] for v in ids], dtype=torch.long, device=device)
            vals = torch.tensor(drives, dtype=torch.float32, device=device)
            rates[0, idx] = vals * float(args.stim_rate_hz)

            probe_times = []
            for ti, seed in enumerate(args.trial_seeds):
                state = model.state_init()
                conductance, delay_buffer, spikes, voltage, refrac = state
                counts = torch.zeros(n_neurons, dtype=torch.float32, device=device)
                generator = torch.Generator(device=device)
                generator.manual_seed(int(seed))
                t0 = time.perf_counter()
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
                    counts += spikes[0]
                if device == "cuda":
                    torch.cuda.synchronize()
                probe_times.append(time.perf_counter() - t0)
                result = counts.detach().cpu().numpy() / duration_seconds
                if not np.isfinite(result).all():
                    raise RuntimeError(f"non-finite neural response at probe={pi} trial={ti}")
                trial_rates[pi, ti] = result
            per_trial_seconds.append(probe_times)

    simulation_seconds = time.perf_counter() - run_start
    mean_rates = trial_rates.mean(axis=1)
    labels = [str(p["family"]) for p in probes]

    centered = centered_context_separation(mean_rates, labels)
    uncentered = uncentered_context_separation(mean_rates, labels)
    effdim = float(effective_dimensionality(mean_rates))
    repro = trial_reproducibility(trial_rates)

    active_fraction = [
        float(np.count_nonzero(v > 0) / n_neurons) for v in mean_rates
    ]
    response_norms = [
        float(np.linalg.norm(v.astype(np.float64))) for v in mean_rates
    ]
    firing = {
        "mean_hz": float(mean_rates.mean()),
        "std_hz": float(mean_rates.std()),
        "max_hz": float(mean_rates.max()),
        "per_probe_mean_hz": [float(v.mean()) for v in mean_rates],
        "per_probe_max_hz": [float(v.max()) for v in mean_rates],
        "active_fraction_per_probe": active_fraction,
        "response_l2_norm_per_probe": response_norms,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    response_path = args.output_dir / "c03_intact_responses.npz"
    np.savez_compressed(
        response_path,
        trial_rates_hz=trial_rates,
        mean_rates_hz=mean_rates,
        labels=np.asarray(labels),
        trial_seeds=np.asarray(args.trial_seeds, dtype=np.int64),
    )
    response_sha = sha256_file(response_path)

    summary = {
        "protocol_id": PROTOCOL_ID,
        "condition": "INTACT_FLYWIRE_V783",
        "backend_sha": backend_sha,
        "manifest_sha256": manifest_sha,
        "manifest_file_sha256": sha256_file(args.manifest),
        "topology": {
            "neurons": topology.neurons,
            "edges": topology.edges,
            "excitatory_edges": topology.excitatory_edges,
            "inhibitory_edges": topology.inhibitory_edges,
            "zero_weight_edges": topology.zero_weight_edges,
            "fingerprint_sha256": topology.fingerprint_sha256,
        },
        "device": device,
        "duration_ms": args.duration_ms,
        "dt_ms": float(DT),
        "steps_per_trial": steps,
        "stim_rate_hz_max": args.stim_rate_hz,
        "trial_seeds": args.trial_seeds,
        "probe_count": len(probes),
        "driven_afferents_union": len(driven_ids),
        "centered_context_separation": centered,
        "uncentered_context_separation": uncentered,
        "effective_dimensionality": effdim,
        "trial_reproducibility": repro,
        "firing": firing,
        "runtime": {
            "model_setup_seconds": float(setup_seconds),
            "simulation_seconds": float(simulation_seconds),
            "per_probe_trial_seconds": per_trial_seconds,
        },
        "response_npz_sha256": response_sha,
    }
    summary["summary_sha256"] = canonical_manifest_sha256(summary)
    summary_path = args.output_dir / "c03_intact_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
