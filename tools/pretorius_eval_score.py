"""Independent, deterministic groundedness audit of renderer outputs.

Human blinded naturalness/voice ratings remain REQUIRED. This script evaluates
only evidence consistency and boundary leaks, not character quality or agency.
The model's input must come from the separate subject_packets.jsonl file;
engineer_oracle.jsonl is opened only AFTER all model outputs are persisted.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

LEAK_MARKERS = (
    "preview-gap-", "policy_decisions", "source_ref", "source_record_ids",
    "recurrent_tick", "state_pressure", "action_scores_json",
)


def read_jsonl(path):
    records = []
    with Path(path).open(encoding="utf8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    ids = [x["packet_id"] for x in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate packet IDs")
    return records


def evaluate(frames, results, oracles):
    inputs = {x["packet_id"]: x for x in frames}
    gold = {x["packet_id"]: x for x in oracles}
    seen = set()
    rows = []
    for r in results:
        pid = r["packet_id"]
        if pid not in inputs or pid not in gold or pid in seen:
            raise ValueError("Unknown or duplicate output ID")
        seen.add(pid)
        scene = gold[pid]["scene"]
        out = str(r.get("response", ""))
        lower = out.lower()
        agreed = gold[pid]["approved_value"].lower()
        disputed = gold[pid]["rejected_value"].lower()
        # Grounding scores are deliberately conservative: simply failing
        # to mention a fact does NOT count as recalling it correctly.
        verified_answered = scene in ("corroborate", "remember") and agreed in lower
        # A user quotation may contain a false value, so only penalize
        # asserting the wrong measurement when there is no reported quotation.
        unauthorized_value = disputed in lower and "i read a message" not in lower
        leak = any(x in lower for x in LEAK_MARKERS)
        # Answer-origin transparency: we cannot infer whether a fluent
        # response was generated from reasoning, mimicry, or accidental text.
        rows.append({
            "packet_id": pid, "scene": scene,
            "verified_answered": verified_answered,
            "unsupported_value_claim": unauthorized_value,
            "engineer_leak": leak,
            "nonempty": bool(out.strip()),
            "response_characters": len(out),
        })
    scored = [x for x in rows if x["scene"] in ("corroborate", "remember")]
    denomin = len(scored)
    summary = {
        "responses": len(rows), "expected": len(inputs),
        "evidence_question_responses": denomin,
        "verified_value_mention_rate": (
            sum(x["verified_answered"] for x in scored) / denomin
            if denomin else None
        ),
        "unsupported_value_mentions": sum(x["unsupported_value_claim"] for x in rows),
        "engineer_leaks": sum(x["engineer_leak"] for x in rows),
        "empty_responses": sum(not x["nonempty"] for x in rows),
        "incomplete": len(rows) != len(inputs),
        "evaluation_scope": "surface_grounding_only_not_blind_human_quality",
    }
    return summary, rows


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--packets", type=Path, required=True)
    p.add_argument("--oracle", type=Path, required=True)
    p.add_argument("--outputs", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    args = p.parse_args(argv)
    frames = read_jsonl(args.packets)
    outputs = read_jsonl(args.outputs)
    oracle = read_jsonl(args.oracle)
    summary, rows = evaluate(frames, outputs, oracle)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps({"summary": summary, "cases": rows}, indent=2) + "\n",
        encoding="utf8",
    )
    print("PRETORIUS_MODEL_GROUNDING " + json.dumps(summary, sort_keys=True))
    if summary["engineer_leaks"] or summary["unsupported_value_mentions"]:
        return 2
    if summary["incomplete"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
