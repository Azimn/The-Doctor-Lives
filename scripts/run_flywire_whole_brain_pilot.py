from __future__ import annotations

"""Run the Phase C whole-FlyWire exploratory pilot.

This script requires a local checkout of the pinned eonsystemspbc/fly-brain
runtime and a FastFly-compatible neuron_annotations.npz file. It does not
vendor or reimplement the upstream LIF model.
"""

import argparse
import json
from pathlib import Path

import numpy as np

from doctor_lives.flywire_bridge import (
    build_pretorius_feature_vector,
    load_annotation_pools,
    project_features_to_afferents,
    run_upstream_lif_probe,
    sha256_array,
    stimulus_manifest,
)


def _parse_scalar(items: list[str]) -> dict[str, float]:
    values: dict[str, float] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"scalar must be key=value, got {item!r}")
        key, raw = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError("scalar key must not be empty")
        values[key] = float(raw)
    return values


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runtime-checkout", type=Path, required=True)
    ap.add_argument("--annotations", type=Path, required=True)
    ap.add_argument("--text", required=True)
    ap.add_argument("--scalar", action="append", default=[], help="key=value; repeatable")
    ap.add_argument("--duration-ms", type=float, default=50.0)
    ap.add_argument("--seed", type=int, default=24017)
    ap.add_argument("--projection-seed", type=int, default=24017)
    ap.add_argument("--fanout", type=int, default=4)
    ap.add_argument("--base-rate-hz", type=float, default=20.0)
    ap.add_argument("--feature-rate-hz", type=float, default=100.0)
    ap.add_argument("--max-rate-hz", type=float, default=180.0)
    ap.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    ap.add_argument("--out", type=Path, default=Path("results/flywire_phase_c/pilot.json"))
    args = ap.parse_args()

    scalars = _parse_scalar(args.scalar)
    pools = load_annotation_pools(args.annotations)
    features = build_pretorius_feature_vector(args.text, scalars)
    rates = project_features_to_afferents(
        features,
        pools.afferent_indices,
        seed=args.projection_seed,
        fanout=args.fanout,
        base_rate_hz=args.base_rate_hz,
        feature_rate_hz=args.feature_rate_hz,
        max_rate_hz=args.max_rate_hz,
    )
    stim = stimulus_manifest(
        text=args.text,
        scalars=scalars,
        rates_hz=rates,
        projection_seed=args.projection_seed,
        fanout=args.fanout,
    )

    summary, counts = run_upstream_lif_probe(
        args.runtime_checkout,
        rates,
        duration_ms=args.duration_ms,
        seed=args.seed,
        device=args.device,
    )
    if pools.neuron_count != summary["neurons"]:
        raise RuntimeError(
            "annotation/runtime neuron-count mismatch: "
            f"{pools.neuron_count} annotations vs {summary['neurons']} runtime neurons"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    counts_path = args.out.with_suffix(".spike_counts.npz")
    np.savez_compressed(counts_path, spike_counts=counts)

    result = {
        "protocol": "pretorius-flywire-c00-v1",
        "condition": "REAL-LIF",
        "production_change": False,
        "biological_semantics_claimed": False,
        "annotation_pools": pools.summary(),
        "feature_vector_sha256": sha256_array(features.astype(np.float32, copy=False)),
        "stimulus": stim,
        "simulation": summary,
        "spike_counts_artifact": {
            "path": str(counts_path),
            "sha256": sha256_array(counts),
        },
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
