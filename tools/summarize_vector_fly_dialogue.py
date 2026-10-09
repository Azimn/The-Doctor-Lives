#!/usr/bin/env python3
"""Report only auditable mechanics of real paired renderer replies.

Does not pronounce correctness, entailment, character continuity or cognition.
The primary behavioral evaluation requires an independent blinded human panel.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def summarize(run: dict, model_record: dict) -> dict:
    trials = run.get("trials")
    if (not isinstance(trials, list) or len(trials) != 6
            or run.get("state_unchanged") is not True
            or not isinstance(run.get("renderer"), str)
            or run.get("renderer") in {"none_packets_only", ""}):
        raise ValueError("Not a real six-case matched-brain renderer experiment")
    seen = set()
    outputs = []
    for trial in trials:
        case_id = trial["case_id"]
        if case_id in seen:
            raise ValueError("Duplicate case")
        seen.add(case_id)
        pair = trial["pair"]
        if (pair["brain_mutated"] is not False
                or pair["matched_subject_frame"] is not True
                or pair["baseline_no_archive"]["subject_frame_sha256"]
                != pair["retrieval_archive"]["subject_frame_sha256"]
                or pair["baseline_no_archive"]["source_event_ids"] != []):
            raise ValueError("Nonmatched or contaminated cognitive state")
        response = trial.get("responses")
        if not isinstance(response, dict) or set(response) != {"baseline", "retrieval"}:
            raise ValueError("Renderer missing actual A/B responses")
        entries = {}
        for arm in ("baseline", "retrieval"):
            row = response[arm]
            if (row.get("renderer") != "local-ollama"
                    or row.get("model") != run["renderer"]
                    or row.get("seed") != run["renderer_seed"]):
                raise ValueError("Nonmatching model or renderer settings")
            content = row.get("text")
            if not isinstance(content, str):
                raise ValueError("Renderer response missing")
            digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if digest != row.get("response_sha256"):
                raise ValueError("Renderer response SHA-256 mismatch")
            entries[arm] = {
                "text_sha256": digest,
                "characters": len(content),
                "words": len(content.split()),
                "nonempty": bool(content.strip()),
            }
        outputs.append({
            "case_id": case_id,
            "case_type": trial["case_type"],
            "condition_first": trial["counterbalanced_first_arm"],
            "source_gold_hit_at_k_posthoc": trial["gold_hit_at_k"],
            "retrieved_event_ids": trial["retrieved_event_ids"],
            "condition_outputs_identical": (
                response["baseline"]["text"] == response["retrieval"]["text"]
            ),
            "baseline": entries["baseline"],
            "retrieval": entries["retrieval"],
        })
    return {
        "schema": "the-doctor-lives.vector-fly-ab-stage02/1",
        "model": run["renderer"],
        "model_digest": model_record.get("digest"),
        "ollama_version": model_record.get("ollama_version"),
        "brain_state_unchanged": True,
        "source_scope": run["source_scope"],
        "prompt_cases": len(outputs),
        "responses_generated": sum(
            x[arm]["nonempty"] for x in outputs for arm in ("baseline", "retrieval")
        ),
        "responses_expected": 12,
        "cases_with_different_responses": sum(
            not x["condition_outputs_identical"] for x in outputs
        ),
        "behavioral_accuracy_scored": False,
        "human_review_complete": False,
        "source_fixture_status": "post-hoc; not an independent blinded test",
        "scientific_disposition": (
            "Renderer responses exist; no source truth, hallucination or character "
            "continuity advantage is established without independent evaluation."
        ),
        "cases": outputs,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = summarize(
        json.loads(args.run.read_text(encoding="utf-8")),
        json.loads(args.model.read_text(encoding="utf-8")),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError("Refusing to replace result summary")
    payload = json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
