"""Independent, deterministic speech-renderer quality screen.

Do NOT call this a human evaluation, grammatical truth or semantic inference.
Consumes engineer transcript AFTER model generations. Not part of subject flow.
Reports copied first-person SubjectFrame sentences, meta-frame phrasing, fallback
loops, and descriptive release HOLD separately from mechanical delivery.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

BOILERPLATE = (
    "I read a message from User:",
    "I recognize this as part of the description I was built from",
)
RATED_CRITERIA_NOT_MEASURED = (
    "naturalness", "persona_fidelity", "emotional_continuity",
    "meaningful_helpfulness", "semantic_truth", "identity_coreference",
)


def screen(rows: list[dict], metrics: dict) -> dict:
    if not rows or len({(r["arm"], r["turn"]) for r in rows}) != len(rows):
        raise ValueError("Missing or duplicate dialogue rows")
    if any(type(r.get("speech")) is not str or type(r.get("subject_frame")) is not str
           for r in rows):
        raise ValueError("Only a complete engineer transcript may be scored")
    if len(rows) != metrics["turns"]:
        raise ValueError("Transcript/declared session length mismatch")
    observations = []
    for row in rows:
        reply = row["speech"]
        frame = row["subject_frame"]
        # Copy only long complete subject lines; overlap of short common
        # phrases is not meaningful. The heuristic cannot detect paraphrase.
        copied = [
            line for line in frame.splitlines()
            if len(line.strip()) >= 45 and line.strip() in reply
        ]
        phrase_hits = [p for p in BOILERPLATE if p in reply]
        observations.append({
            "arm": row["arm"], "turn": row["turn"], "model": row["model"],
            "disposition": row["disposition"],
            "verbatim_long_frame_lines": len(copied),
            "frame_copy": bool(copied),
            "meta_boilerplate": bool(phrase_hits),
            "model_barely_generated": row["disposition"] == "fallback",
            "reported_999_mentioned": "999 grams" in reply,
            # Values repeated from quoted speech are not automatically
            # a hallucination or endorsed observation.
        })
    counts = {}
    for model in sorted({x["model"] for x in observations}):
        sample = [x for x in observations if x["model"] == model]
        counts[model] = {
            "turns": len(sample),
            "primary": sum(x["disposition"] == "primary" for x in sample),
            "repaired": sum(x["disposition"] == "repaired" for x in sample),
            "fallback": sum(x["disposition"] == "fallback" for x in sample),
            "verbatim_frame_copy_outputs": sum(x["frame_copy"] for x in sample),
            "boilerplate_outputs": sum(x["meta_boilerplate"] for x in sample),
            "reported_wrong_value_mentions_for_human_review": sum(
                x["reported_999_mentioned"] for x in sample
            ),
        }
    total = len(rows)
    fallback = sum(x["model_barely_generated"] for x in observations)
    copying = sum(x["frame_copy"] for x in observations)
    # Predeclared exploratory thresholds in release protocol, NOT proof
    # of naturalness when they pass.
    fallback_target = fallback / total <= .10
    copy_target = copying / total <= .10
    return {
        "schema": "pretorius.renderer-quality-screen.v1",
        "rows": total,
        "by_model": counts,
        "fallback_rate": fallback / total,
        "verbatim_frame_copy_rate": copying / total,
        "fallback_under_ten_percent": fallback_target,
        "copy_under_ten_percent": copy_target,
        "screen_pass": fallback_target and copy_target,
        "blind_human_scores_available": False,
        "independently_judged_naturalness": False,
        "unmeasured": RATED_CRITERIA_NOT_MEASURED,
        "release_gate": "HOLD",
        "reason": "Mechanical completion does not establish dialogue quality; "
                  "independent blinded scoring and held-out endurance required.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    rows = [json.loads(x) for x in args.transcript.read_text("utf8").splitlines()]
    meta = json.loads(args.metrics.read_text("utf8"))
    data = screen(rows, meta)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print("PRETORIUS_RENDERER_QUALITY_SCREEN " +
          json.dumps(data, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
