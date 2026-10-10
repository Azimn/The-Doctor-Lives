"""Compare two PSL native-policy runs without concealing diagnostic jitter.

Only 'native_pre_ingest_diagnostic', an ancillary live floating-point neural
readout, is exempt from byte-exact core replay comparison. All actual choices,
sealed forecasts, trained model scores, case labels and manifests must match.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any


EXCLUDED_DIAGNOSTIC = "native_pre_ingest_diagnostic"


def core_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") != "pretorius.psl.native-policy-chronological.v1":
        raise ValueError("unsupported PSL replay schema")
    result = deepcopy(payload)
    for item in result["cases"]:
        for key in ("forecasts", "scored"):
            if EXCLUDED_DIAGNOSTIC not in item[key]:
                raise ValueError("expected dynamic diagnostic is missing")
            del item[key][EXCLUDED_DIAGNOSTIC]
    for phase in result["summary"].values():
        if EXCLUDED_DIAGNOSTIC not in phase["metrics"]:
            raise ValueError("expected summary dynamic diagnostic is missing")
        del phase["metrics"][EXCLUDED_DIAGNOSTIC]
    return result


def core_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(
        core_payload(payload), sort_keys=True,
        ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()


def compare(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    a = core_sha256(first)
    b = core_sha256(second)
    same_choices = [c["selected_action"] for c in first["cases"]] == [
        c["selected_action"] for c in second["cases"]
    ]
    return {
        "protocol": first["schema"],
        "excluded_diagnostic": EXCLUDED_DIAGNOSTIC,
        "total_choices": len(first["cases"]),
        "selected_action_sequence_equal": same_choices,
        "core_sha256_a": a,
        "core_sha256_b": b,
        "core_equal": a == b,
        "full_json_equal": first == second,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    args = parser.parse_args()
    a = json.loads(args.first.read_text(encoding="utf-8"))
    b = json.loads(args.second.read_text(encoding="utf-8"))
    report = compare(a, b)
    print(json.dumps(report, sort_keys=True, indent=2))
    if not report["core_equal"] or not report["selected_action_sequence_equal"]:
        raise SystemExit("PSL core replay mismatch")


if __name__ == "__main__":
    main()
