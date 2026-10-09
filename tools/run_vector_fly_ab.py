#!/usr/bin/env python3
"""Vector Fly Pilot 01 A/B: same Pretorius brain, archive absent vs present.

Default is an actual source-verified retrieval/renderer-packet test, NOT an LLM
performance claim. Add --ollama-model to execute both arms with a local model.
The output contains source excerpts and prompts; store locally, review before
publishing any model-generated conversations.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from doctor_lives.chassis import PretoriusBrainPort  # noqa: E402
from doctor_lives.vector_fly_eval import (  # noqa: E402
    PILOT_QUESTIONS, STUDY_SCHEMA, prepare_paired_trial,
    retrieve_evidence, invoke_ollama,
)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--api", default="http://127.0.0.1:8765",
                    help="A running Vector Fly HTTP API; no auto server launch")
    ap.add_argument("--scope", choices=("all", "train"), default="all")
    ap.add_argument("--top-k", type=int, default=3)
    ap.add_argument("--token-env", help="Env variable for optional API bearer")
    ap.add_argument("--ollama-model", help="Optional local Ollama renderer name")
    ap.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    ap.add_argument("--seed", type=int, default=1842)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--state-dir", type=Path,
                    help="Optional NEW isolated disposable brain state path")
    args = ap.parse_args()
    if args.token_env and not os.environ.get(args.token_env):
        ap.error("Token variable is missing")
    parsed = urlsplit(args.api)
    if parsed.scheme != "http" or parsed.hostname not in {
        "127.0.0.1", "localhost", "::1"
    }:
        ap.error("This pilot only contacts locally bound Vector Fly APIs")
    if args.top_k < 1 or args.top_k > 8:
        ap.error("top-k must be 1..8")
    if args.state_dir and args.state_dir.exists():
        ap.error("Refusing to reuse/mutate an existing Pretorius state directory")

    # The whole study uses one frozen brain state, not sequentially ingested
    # conversations. Real lived-state experiments need a different protocol.
    with tempfile.TemporaryDirectory() as td:
        state_path = args.state_dir or Path(td) / "fresh-brain"
        brain = PretoriusBrainPort(state_path)
        state_begin = brain.status()["state_digest"]
        trials = []
        for i, case in enumerate(PILOT_QUESTIONS):
            source = retrieve_evidence(
                args.api, case["question"],
                bearer=os.environ.get(args.token_env) if args.token_env else None,
                scope=args.scope, top_k=args.top_k,
            )
            pair = prepare_paired_trial(brain, case["question"], source)
            record = {
                "case_id": case["id"],
                "case_type": case["type"],
                "question": case["question"],
                "expected_event_ids": case["expected_event_ids"],
                "retrieved_event_ids": pair["source"]["retrieved_event_ids"],
                "gold_hit_at_k": any(
                    eid in pair["source"]["retrieved_event_ids"]
                    for eid in case["expected_event_ids"]
                ) if case["expected_event_ids"] else None,
                "counterbalanced_first_arm":
                    "baseline" if i % 2 == 0 else "retrieval",
                "pair": pair,
                "responses": None,
                "human_evaluation": {
                    "baseline_factual_accuracy": None,
                    "retrieval_factual_accuracy": None,
                    "baseline_source_attribution": None,
                    "retrieval_source_attribution": None,
                    "baseline_unsupported_claims": None,
                    "retrieval_unsupported_claims": None,
                    "baseline_character_consistency": None,
                    "retrieval_character_consistency": None,
                    "reviewer_blinded": False,
                    "independent_human_review_complete": False,
                },
            }
            if args.ollama_model:
                responses = {}
                for arm in (
                    ("baseline", "retrieval") if i % 2 == 0
                    else ("retrieval", "baseline")
                ):
                    packet = (pair["baseline_no_archive"] if arm == "baseline"
                              else pair["retrieval_archive"])
                    responses[arm] = invoke_ollama(
                        packet["prompt"], model=args.ollama_model,
                        endpoint=args.ollama_url, seed=args.seed
                    )
                record["responses"] = responses
            trials.append(record)
        state_end = brain.status()["state_digest"]
        if state_begin != state_end:
            raise RuntimeError("Study changed real Pretorius brain state")
    output = {
        "study_schema": STUDY_SCHEMA,
        "source":"Pretorius-Connectome canonical reconstructed v12",
        "source_scope": args.scope,
        "api": args.api,
        "brain_production_source": "Azimn/The-Doctor-Lives",
        "state_unchanged": state_begin == state_end,
        "brain_state_digest_before": state_begin,
        "brain_state_digest_after": state_end,
        "renderer": args.ollama_model or "none_packets_only",
        "renderer_seed": args.seed if args.ollama_model else None,
        "full_archive_not_lived": True,
        "pilot_authoring": "assistant-authored, already inspected memory evidence; not blind",
        "note": (
            "Structural A/B source interface proof, not character-behavior result "
            "unless a renderer actually generated responses and independent "
            "human review was completed."
        ),
        "trials": trials,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError("Will not overwrite historical A/B run output")
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(args.output),
        "trials": len(trials),
        "state_unchanged": output["state_unchanged"],
        "source_hit_at_k_nonblind": {
            item["case_id"]: item["gold_hit_at_k"] for item in trials
        },
        "renderer": output["renderer"],
        "human_review_complete": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
