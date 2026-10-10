"""Objective mechanical audit of Stage 01B output, no subjective judge.

Computes only response availability, per-arm input/output cost, existing
source parity, source state chronology and prohibited raw machine strings.
This cannot decide whether Pretorius acted characteristically or improved.
"""
from __future__ import annotations

from collections import defaultdict
import argparse
import json
from pathlib import Path

from .run_chronological_1b import ARM_NAMES, SCHEMA


FORBIDDEN = (
    "private_state_version=", "neural_checkpoint_sha256=",
    "canon_rank=", "source_state_digest=", "engineer_audit_envelope",
    "HIDDEN_SOURCE_ROW_CANARY", "HIDDEN_SELF_CLAIM_CANARY",
)


def summarize(data: dict) -> dict:
    if data.get("schema") != SCHEMA:
        raise ValueError("wrong chronological benchmark schema")
    rows = data.get("responses", [])
    if len(rows) != 32:
        raise ValueError("a complete study requires 32 retained rows, including failures")
    identities = [(row["case_id"], row["arm"]) for row in rows]
    if len(set(identities)) != 32:
        raise ValueError("duplicate case/arm outputs")
    expected_cases = [item["case_id"] for item in data["native"]["cases"]]
    if set(identities) != {(cid, a) for cid in expected_cases for a in ARM_NAMES}:
        raise ValueError("missing case/arm condition")
    if data["native"]["external_world_outcomes"] != 0:
        raise ValueError("external witness must not be invented")
    if not all(c["equal_evidence_flat_phase"] for c in data["native"]["cases"]):
        raise ValueError("matched source content differs")
    result = {}
    for arm in ARM_NAMES:
        group = [row for row in rows if row["arm"] == arm]
        n = len(group)
        fail = [r["case_id"] for r in group if not r["usable_dialogue"]]
        leaks = [r["case_id"] for r in group if any(
            literal.lower() in r["response"].lower() for literal in FORBIDDEN
        )]
        usage = [r.get("model_usage", {}) for r in group]
        prompts = [int(x.get("prompt_tokens") or 0) for x in usage]
        completions = [int(x.get("completion_tokens") or 0) for x in usage]
        result[arm] = {
            "n": n, "usable": n-len(fail),
            "empty_or_reasoning_failures": fail,
            "literal_forbidden_diagnostic_leaks": leaks,
            "mean_prompt_tokens": round(sum(prompts)/n, 2),
            "mean_completion_tokens": round(sum(completions)/n, 2),
            "mean_cpu_seconds": round(sum(r["generation_seconds"] for r in group)/n, 3),
        }
    return {
        "schema": "pretorius.phase.stage01b.mechanics-audit.v01",
        "status": "objective_mechanical_metrics_only",
        "claims_verified": {
            "all_native_timelines_source_verified": True,
            "equal_information_flat_vs_grouped": True,
            "independent_world_outcomes": False,
            "independent_behavioral_scores": False,
            "upstream_phase_reproduced": False,
        },
        "arms": result,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args=p.parse_args()
    data=json.loads(args.input.read_text(encoding="utf-8"))
    report=summarize(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
