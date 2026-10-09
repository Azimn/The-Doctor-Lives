#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()

    summaries = []
    for path in args.root.rglob("c04_condition_summary.json"):
        data = json.loads(path.read_text())
        data["_path"] = str(path)
        summaries.append(data)
    if len(summaries) != 7:
        raise SystemExit(f"expected 7 C04 condition summaries, found {len(summaries)}")

    manifests = {s["manifest_sha256"] for s in summaries}
    if manifests != {"7204b9ac2860d94b5ac28edb5976695831b61e366a920da67629ee8c99a13228"}:
        raise SystemExit(f"manifest mismatch: {manifests}")

    intact = [s for s in summaries if s["condition"] == "INTACT"]
    degree = sorted(
        [s for s in summaries if s["condition"] == "DEGREE_PRESERVING"],
        key=lambda x: int(x["topology_seed"]),
    )
    random = sorted(
        [s for s in summaries if s["condition"] == "RANDOM_SCALE"],
        key=lambda x: int(x["topology_seed"]),
    )
    if len(intact) != 1 or len(degree) != 3 or len(random) != 3:
        raise SystemExit("condition cardinality mismatch")
    intact = intact[0]

    def metric(s, name="centered_context_separation"):
        return float(s[name]["separation"])

    def family(items):
        vals = [metric(s) for s in items]
        iv = metric(intact)
        return {
            "values": vals,
            "mean": float(statistics.mean(vals)),
            "median": float(statistics.median(vals)),
            "intact_minus_each": [iv - v for v in vals],
            "intact_greater_count": int(sum(iv > v for v in vals)),
        }

    result = {
        "protocol_id": intact["protocol_id"],
        "primary_metric": "centered_context_separation",
        "intact": {
            "value": metric(intact),
            "effective_dimensionality": intact["effective_dimensionality"],
            "trial_reproducibility_mean": intact["trial_reproducibility"]["mean"],
        },
        "degree_preserving": family(degree),
        "random_scale": family(random),
        "secondary": {
            "intact_uncentered_separation": metric(intact, "uncentered_context_separation"),
            "degree_uncentered": [
                metric(s, "uncentered_context_separation") for s in degree
            ],
            "random_uncentered": [
                metric(s, "uncentered_context_separation") for s in random
            ],
            "degree_effective_dimensionality": [
                s["effective_dimensionality"] for s in degree
            ],
            "random_effective_dimensionality": [
                s["effective_dimensionality"] for s in random
            ],
        },
        "interpretation_guard": (
            "Exploratory topology comparison only; three topology instances per "
            "control family do not establish biological optimality."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
