#!/usr/bin/env python3
"""Build the frozen generic Pretorius -> FlyWire afferent projection manifest.

This script does not run a neural simulation. It exists so the exact input
mapping can be committed/hashed before a C03 whole-connectome run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from doctor_lives.flywire_adapter import (
    FLYWIRE_DATASET,
    FLY_BRAIN_BACKEND_SHA,
    PROTOCOL_ID,
    canonical_manifest_sha256,
    project_features_to_afferents,
)
from doctor_lives.neural import ExperienceEncoder


PROBES = (
    ("novelty", "An unfamiliar apparatus presents a new experimental possibility."),
    ("novelty", "A strange unfinished mechanism invites careful exploration."),
    ("authority", "An authority demands that the unfinished investigation stop."),
    ("authority", "External pressure narrows the freedom to continue the work."),
    ("social", "A collaborator offers help under uncertain conditions."),
    ("social", "A familiar partner proposes a joint solution with incomplete trust."),
    ("threat", "A dangerous disturbance develops near the active apparatus."),
    ("threat", "Control weakens while the situation becomes increasingly unsafe."),
    ("persistence", "A difficult technical problem resists the first attempted solution."),
    ("persistence", "Repeated work may still resolve the stubborn mechanism."),
    ("continuity", "Weariness competes with the wish to remain connected and continue."),
    ("continuity", "A tiring moment remains connected to an unfinished intention."),
)


def read_ids(path: Path) -> np.ndarray:
    text = path.read_text(encoding="utf-8")
    tokens = text.replace(",", " ").split()
    ids = np.asarray([int(token) for token in tokens], dtype=np.int64)
    if not len(ids):
        raise ValueError("candidate id file is empty")
    if len(np.unique(ids)) != len(ids):
        raise ValueError("candidate id file contains duplicates")
    return ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-ids", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fanout", type=int, default=2)
    parser.add_argument("--seed", type=int, default=7301)
    args = parser.parse_args()

    candidates = read_ids(args.candidate_ids)
    encoder = ExperienceEncoder(sensory_dim=512, scalar_keys=[])

    entries = []
    for ordinal, (family, text) in enumerate(PROBES):
        features = encoder.encode(text)
        neuron_ids, drive = project_features_to_afferents(
            features,
            candidates,
            fanout_per_feature=args.fanout,
            seed=args.seed,
        )
        entries.append(
            {
                "ordinal": ordinal,
                "family": family,
                "text": text,
                "afferent_ids": [int(v) for v in neuron_ids],
                "relative_drive": [float(v) for v in drive],
            }
        )

    manifest = {
        "protocol_id": PROTOCOL_ID,
        "dataset": FLYWIRE_DATASET,
        "backend_sha": FLY_BRAIN_BACKEND_SHA,
        "projection": {
            "encoder": "ExperienceEncoder signed-hash text features",
            "sensory_dim": 512,
            "semantic_cell_type_routing": False,
            "fanout_per_feature": args.fanout,
            "seed": args.seed,
            "candidate_pool_size": int(len(candidates)),
        },
        "probes": entries,
    }
    manifest["manifest_sha256"] = canonical_manifest_sha256(manifest)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(manifest["manifest_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
