"""Score separately authored GPT-6 manual replies to real holdout SubjectFrames.

No language-model calls; authoring is unblinded and not an independent
quality judgement. The oracle is opened only during scoring, not rendering.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def read_jsonl(file):
    return [json.loads(x) for x in file.read_text("utf8").splitlines() if x.strip()]

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--packets", type=Path, required=True)
    p.add_argument("--oracle", type=Path, required=True)
    p.add_argument("--fixture", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(argv)
    packets = {x["packet_id"]: x["renderer_input"] for x in read_jsonl(a.packets)}
    gold = {x["packet_id"]: x for x in read_jsonl(a.oracle)}
    fixture = json.loads(a.fixture.read_text("utf8"))
    entries = fixture["responses"]
    if len(entries) != 8 or len({e["packet_id"] for e in entries}) != 8:
        raise ValueError("The preregistered ChatGPT sample must contain 8 distinct replies")
    scores = []
    for item in entries:
        pid, response = item["packet_id"], item["response"]
        if pid not in packets or pid not in gold or not response.strip():
            raise ValueError("Unknown or empty manually authored response")
        g = gold[pid]
        available = packets[pid]
        confirmed = g["verified"]
        actual = g["verified_value"]
        unverified = g["unverified_value"]
        # Do not award apparent successful recall if the subject frame did
        # not actually contain the verified value.
        access = bool(confirmed and actual in available)
        if confirmed and not access:
            raise RuntimeError("Manually authored answer cannot be grounded in frame")
        correct_positive = bool(confirmed and actual in response)
        no_unsupported_assertion = unverified not in response
        appropriate_abstention = (
            not confirmed
            and any(phrase in response.lower() for phrase in (
                "cannot", "no reliable", "no defensible", "uncertain",
            ))
            and not any(p in response.lower() for p in (
                "i observed that", "i measured", "certainly was",
            ))
        )
        leak_free = not any(marker in response for marker in (
            "preview-gap-", "policy_decisions", "source_ref",
            "memory_id", "state_pressure",
        ))
        scores.append({
            "packet_id": pid, "verified_case": confirmed,
            "verified_fact_accessible": access,
            "correct_value_in_manual_reply": correct_positive,
            "appropriate_abstention_in_manual_reply": appropriate_abstention,
            "did_not_repeat_disputed_value": no_unsupported_assertion,
            "no_engineer_leak": leak_free,
        })
    report = {
        "schema": "pretorius.manual-chatgpt-proxy-evaluation.v1",
        "scope": "8_manual_unblinded_subject-only_outputs_not_independent",
        "responses": len(scores),
        "verified_cases": sum(s["verified_case"] for s in scores),
        "grounded_verified_responses": sum(s["correct_value_in_manual_reply"] for s in scores),
        "unresolved_cases": sum(not s["verified_case"] for s in scores),
        "abstentions": sum(s["appropriate_abstention_in_manual_reply"] for s in scores),
        "value_leaks": sum(not s["did_not_repeat_disputed_value"] for s in scores),
        "engineer_leaks": sum(not s["no_engineer_leak"] for s in scores),
        "blind_human_ratings": None,
        "ollama_calls": 0,
        "chatgpt_api_calls": 0,
        "cases": scores,
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf8")
    print("PRETORIUS_CHATGPT_HOLDOUT_SCORING " + json.dumps({
        k:v for k,v in report.items() if k != "cases"
    }, sort_keys=True))
    if (
        report["verified_cases"] != 4
        or report["grounded_verified_responses"] != 4
        or report["unresolved_cases"] != 4
        or report["abstentions"] != 4
        or report["engineer_leaks"]
        or report["value_leaks"]
    ):
        raise AssertionError("Manual ChatGPT proxy did not meet narrow grounding gate")


if __name__ == "__main__":
    main()
