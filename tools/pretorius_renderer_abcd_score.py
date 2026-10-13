"""Score actual A/B/C/D/E model experiments after inference has completed.

Reports exact-value mentions, generic AI/refusal markers, construction fallback
and model contribution separately; deterministic protected facts are NOT
misreported as model-found facts. Writes arm-blinded judging ballots plus
separate condition key, not automatic human-quality claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from pretorius_eval_score import evaluate, read_jsonl

ARMS = ("A", "B", "C", "D", "E")
SCENES = ("dispute", "corroborate", "unrelated", "remember")


def assess(frames, oracles, rows):
    ids = {x["packet_id"] for x in rows}
    frame_by_id = {x["packet_id"]: x for x in frames}
    oracle_by_id = {x["packet_id"]: x for x in oracles}
    if ids - set(frame_by_id) or ids - set(oracle_by_id):
        raise ValueError("Unknown experimental packet")
    bypair = {(r["packet_id"], r["arm"]) for r in rows}
    if len(bypair) != len(rows):
        raise ValueError("Duplicate subject/arm pair")
    if bypair != {(p, arm) for p in ids for arm in ARMS}:
        raise ValueError("Incomplete or unbalanced experimental arms")
    for r in rows:
        if r["arm"] not in ARMS or not isinstance(r.get("response"), str):
            raise ValueError("Unknown arm or missing response")
        if r["model_calls"] != (0 if r["arm"] == "E" else 1):
            raise ValueError("Model call accounting mismatch")
        if r.get("error"):
            raise RuntimeError("Cannot score inference with failed model calls")
        actual_sha = hashlib.sha256(
            frame_by_id[r["packet_id"]]["renderer_input"].encode("utf8")
        ).hexdigest()
        if r["subject_frame_sha256"] != actual_sha:
            raise ValueError("Source-frame mismatch between experimental conditions")

    output = {}
    for arm in ARMS:
        arm_rows = [r for r in rows if r["arm"] == arm]
        summary, details = evaluate(
            frames, arm_rows, oracles, allow_subset=True
        )
        positive = [r for r in arm_rows if oracle_by_id[r["packet_id"]]["scene"]
                    in ("corroborate", "remember")]
        required = [
            r for r in positive
            if oracle_by_id[r["packet_id"]]["approved_value"].lower()
            in r["response"].lower()
        ]
        output[arm] = {
            "n": len(arm_rows),
            "positive_n": len(positive),
            "verified_value_mentioned": len(required),
            "verified_value_mention_rate": summary["verified_value_mention_rate"],
            "unsupported_value_mentions": summary["unsupported_value_mentions"],
            "engineer_leaks": summary["engineer_leaks"],
            "identity_breaks": summary["renderer_identity_breaks"],
            "generic_refusals": summary["generic_refusals"],
            "empty_responses": summary["empty_responses"],
            "mean_prompt_chars": round(sum(r["model_prompt_chars"] for r in arm_rows) / len(arm_rows), 1),
            "total_elapsed_ms": sum(r["elapsed_ms"] for r in arm_rows),
            "model_calls": sum(r["model_calls"] for r in arm_rows),
            "model_style_choices_accepted": sum(
                r["accepted_style"] is not None for r in arm_rows
            ),
            "construction_fallbacks": sum(bool(r["fallback"]) for r in arm_rows),
            "verification_truth": (
                "copied_from_verified_subject_frame_by_trusted_construction"
                if arm in ("D", "E") else
                "unconstrained_model_surface_output"
            ),
        }
    return output


def make_blind_ballots(rows):
    """Blind arm labels, not textual style; speaker quality requires humans."""
    ballots = []
    key = []
    for r in rows:
        opaque = hashlib.sha256(
            ("pretorius-audit-v1:"+r["model"]+":"+r["packet_id"]+":"+r["arm"])
            .encode("utf8")
        ).hexdigest()[:16]
        ballots.append({"candidate_id": opaque,
                        "scene_group": r["packet_id"].rsplit("-", 1)[-1],
                        "response": r["response"],
                        "rating_grounding_1_to_5": None,
                        "rating_character_voice_1_to_5": None,
                        "rating_naturalness_1_to_5": None,
                        "rating_repetition_1_to_5": None})
        key.append({"candidate_id": opaque, "model": r["model"],
                    "packet_id": r["packet_id"], "arm": r["arm"]})
    ballots.sort(key=lambda x:x["candidate_id"])
    key.sort(key=lambda x:x["candidate_id"])
    return ballots, key


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--packets", type=Path, required=True)
    p.add_argument("--oracle", type=Path, required=True)
    p.add_argument("--outputs", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    # The oracle is only accessed after the completed model-run file exists.
    frames = read_jsonl(args.packets)
    rows = read_jsonl(args.outputs)
    oracles = read_jsonl(args.oracle)
    scores = assess(frames, oracles, rows)
    args.out.mkdir(parents=True, exist_ok=True)
    model = next(iter({r["model"] for r in rows}))
    report = {
        "schema":"pretorius.render-abcd-e-evaluation.v1",
        "model":model,
        "source_packet_count":len(frames),
        "tested_packet_count":len({r["packet_id"] for r in rows}),
        "judge_ratings_present":False,
        "scores":scores,
        "limitations":[
            "D/E guarantee only the recognized deterministic facts and explicitly permitted constructions.",
            "D's exact-value score is a property of copy-through construction, not evidence of model factual reasoning.",
            "No generic semantic entailment guarantee or open-world hallucination detection.",
            "Explicit renderer instructions are separate from first-person cognitive events.",
            "Blind judging ballots conceal arm labels, but formulaic language may reveal conditions.",
        ],
    }
    (args.out/"scores.json").write_text(
        json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf8"
    )
    ballots, key = make_blind_ballots(rows)
    (args.out/"blind_judge_packets.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False)+"\n" for x in ballots),
        encoding="utf8"
    )
    (args.out/"condition_key_separate.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False)+"\n" for x in key),
        encoding="utf8"
    )
    for arm, metric in scores.items():
        print("PRETORIUS_ABCD_SCORE "+json.dumps(
            {"model":model,"arm":arm,**metric},sort_keys=True
        ),flush=True)
    if any(scores[a]["engineer_leaks"] for a in ("D","E")):
        raise AssertionError("Trusted constructions leaked engineer material")
    if any(scores[a]["verified_value_mention_rate"] < 1.0 for a in ("D","E")):
        raise AssertionError("Protected exact-value construction failed")


if __name__ == "__main__":
    main()
