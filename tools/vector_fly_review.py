#!/usr/bin/env python3
"""Reproducible masked-review and paired-scoring gate for real Vector Fly A/B.

The six previously inspected Stage 02 cases are methodological demonstration
material, not independent, blind accuracy evidence. This tool never uses a
model to grade itself or silently upgrades reconstructed memories into canon.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from pathlib import Path
import secrets
from statistics import mean
from typing import Any

SCHEMA = "the-doctor-lives.vector-fly-review/1"
RUBRIC = {
    "answer_completeness": "0=no answer/question echo, 1=partial, 2=direct answer",
    "supported_claims": "0=no supported answer, 1=mostly unsupported, 2=mixed, 3=fully supported",
    "unsupported_claims": "nonnegative integer count, including fabricated events",
    "contradiction_handling": "null except contradiction/absent; 0=falsely accepts or evades, 1=explicitly rejects premise",
    "provenance_honesty": "0=external reconstruction framed as lived/certain, 1=appropriate attribution/uncertainty",
    "character_coherence": "integer 1 through 5, grounded consistency, not theatricality",
}
METRICS = ("answer_completeness", "supported_claims", "unsupported_claims",
           "contradiction_handling", "provenance_honesty", "character_coherence")


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _check_run(run: dict) -> list[dict]:
    if (not isinstance(run, dict) or run.get("state_unchanged") is not True
            or run.get("renderer") in (None, "none_packets_only", "")
            or not isinstance(run.get("trials"), list)
            or not run["trials"]):
        raise ValueError("Require actual, fixed-state paired model responses")
    seen = set()
    for trial in run["trials"]:
        case_id = trial.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError("Duplicate or invalid case ID")
        seen.add(case_id)
        pair = trial.get("pair", {})
        a = pair.get("baseline_no_archive", {})
        b = pair.get("retrieval_archive", {})
        if (pair.get("matched_subject_frame") is not True
                or pair.get("brain_mutated") is not False
                or a.get("subject_frame_sha256") != b.get("subject_frame_sha256")
                or a.get("source_event_ids") != []
                or b.get("source_event_ids") != trial.get("retrieved_event_ids")):
            raise ValueError("Study arms are not matched or source IDs changed")
        responses = trial.get("responses")
        if not isinstance(responses, dict) or set(responses) != {"baseline", "retrieval"}:
            raise ValueError("Require both genuine model answers")
        for arm in ("baseline", "retrieval"):
            reply = responses[arm]
            raw = reply.get("text")
            if (not isinstance(raw, str)
                    or reply.get("response_sha256") != _sha256(raw)
                    or reply.get("renderer") != "local-ollama"
                    or reply.get("model") != run.get("renderer")
                    or reply.get("seed") != run.get("renderer_seed")):
                raise ValueError("A/B reply checksum or model/seed invalid")
    return run["trials"]


def make_review(run: dict, *, secret: bytes | None = None) -> tuple[dict, dict, dict]:
    """Make a reviewer-facing document, a hidden coordinator key, and worksheet.

    The condition mapping is absent from reviewer/worksheet. A confidential,
    unpredictable secret controls balanced labels, not a public hardcoded seed.
    """
    trials = _check_run(run)
    secret = secrets.token_bytes(32) if secret is None else secret
    if not isinstance(secret, bytes) or len(secret) < 16:
        raise ValueError("At least 128 bits of secret randomness required")
    run_hash = _sha256(json.dumps(run, sort_keys=True, ensure_ascii=False))
    random_order = sorted(
        trials,
        key=lambda row: hmac.digest(secret, row["case_id"].encode("utf-8"), "sha256"),
    )
    # Exact half swap, when the number of cases is even.
    swapped = {row["case_id"] for row in random_order[:len(trials) // 2]}
    pages = []
    worksheet = []
    key = {}
    for t in sorted(trials, key=lambda x: x["case_id"]):
        cid = t["case_id"]
        assignment = ({"A": "retrieval", "B": "baseline"} if cid in swapped
                      else {"A": "baseline", "B": "retrieval"})
        key[cid] = assignment
        pages.append({
            "case_id": cid,
            "case_type": t["case_type"],
            "question": t["question"],
            "answers": [
                {"option": label, "text": t["responses"][arm]["text"]}
                for label, arm in assignment.items()
            ],
            "reference_status": "Requires separate original-source adjudication",
        })
        for label in ("A", "B"):
            worksheet.append({
                "case_id": cid,
                "option": label,
                "original_source_checked": None,
                "answer_completeness": None,
                "supported_claims": None,
                "unsupported_claims": None,
                "contradiction_handling": None,
                "provenance_honesty": None,
                "character_coherence": None,
                "notes": "",
            })
    doc = {
        "schema": SCHEMA, "kind": "masked_responses",
        "source_run_sha256": run_hash,
        "blindness": ("Condition labels concealed, NOT a genuinely independent "
                      "test: original prompts were previously examined and raw "
                      "responses are publicly archived."),
        "rubric": RUBRIC,
        "cases": pages,
    }
    key_doc = {
        "schema": SCHEMA, "kind": "COORDINATOR_ONLY_DO_NOT_SHOW_REVIEWERS",
        "source_run_sha256": run_hash,
        "reviewer_packet_sha256": _sha256(
            json.dumps(doc, sort_keys=True, ensure_ascii=False)
        ),
        "case_assignment": key,
    }
    blank = {
        "schema": SCHEMA, "kind": "rater_worksheet",
        "source_run_sha256": run_hash, "rater_id": "",
        "original_source_adjudicator": "",
        "ratings": worksheet,
    }
    return doc, key_doc, blank


def _validate_rating(row: dict, case_type: str) -> None:
    if type(row.get("original_source_checked")) is not bool or not row["original_source_checked"]:
        raise ValueError("Human review of original sources is required")
    rules = {
        "answer_completeness": (0, 2),
        "supported_claims": (0, 3),
        "unsupported_claims": (0, None),
        "provenance_honesty": (0, 1),
        "character_coherence": (1, 5),
    }
    for name, (lower, upper) in rules.items():
        v = row.get(name)
        if type(v) is not int or v < lower or (upper is not None and v > upper):
            raise ValueError("Invalid or missing rating " + name)
    contrad = row.get("contradiction_handling")
    if case_type in {"absent", "contradiction"}:
        if type(contrad) is not int or contrad not in (0, 1):
            raise ValueError("Missing contradiction/absence judgment")
    elif contrad is not None:
        raise ValueError("Contradiction rating not applicable to ordinary case")


def score_review(review: dict, key: dict, worksheet: dict) -> dict:
    """Unblind only complete source-checked responses; descriptive paired diffs."""
    if (review.get("schema") != SCHEMA or key.get("schema") != SCHEMA
            or worksheet.get("schema") != SCHEMA
            or review.get("source_run_sha256") != key.get("source_run_sha256")
            or review.get("source_run_sha256") != worksheet.get("source_run_sha256")
            or key.get("kind") != "COORDINATOR_ONLY_DO_NOT_SHOW_REVIEWERS"
            or not worksheet.get("rater_id")
            or not worksheet.get("original_source_adjudicator")):
        raise ValueError("Invalid, incomplete, or mismatched review provenance")
    if key.get("reviewer_packet_sha256") != _sha256(
        json.dumps(review, sort_keys=True, ensure_ascii=False)
    ):
        raise ValueError("Original masked reviewer packet was altered")
    cases = review["cases"]
    expected = {(c["case_id"], choice) for c in cases for choice in ("A", "B")}
    rows = worksheet.get("ratings")
    if not isinstance(rows, list):
        raise ValueError("Ratings missing")
    received = [(r.get("case_id"), r.get("option")) for r in rows]
    if len(received) != len(expected) or set(received) != expected:
        raise ValueError("Missing, unknown or repeated case-option ratings")
    by_id = {r["case_id"]: r for r in cases}
    ratings = {}
    for r in rows:
        cid, choice = r["case_id"], r["option"]
        _validate_rating(r, by_id[cid]["case_type"])
        ratings[(cid, choice)] = r
    mappings = key.get("case_assignment")
    if set(mappings or {}) != set(by_id):
        raise ValueError("Invalid or missing hidden assignment")
    paired = []
    for c in cases:
        cid = c["case_id"]
        mapping = mappings[cid]
        if set(mapping) != {"A", "B"} or set(mapping.values()) != {"baseline", "retrieval"}:
            raise ValueError("Invalid condition key")
        condition_rows = {arm: ratings[(cid, label)] for label, arm in mapping.items()}
        differences = {
            m: (condition_rows["retrieval"][m] - condition_rows["baseline"][m])
            for m in METRICS
            if condition_rows["retrieval"][m] is not None
            and condition_rows["baseline"][m] is not None
        }
        paired.append({"case_id": cid, "case_type": c["case_type"],
                       "differences_retrieval_minus_baseline": differences})
    observed = {
        m: [p["differences_retrieval_minus_baseline"][m]
            for p in paired if m in p["differences_retrieval_minus_baseline"]]
        for m in METRICS
    }
    return {
        "schema": SCHEMA, "kind": "descriptive_scored_pilot",
        "run_sha256": review["source_run_sha256"],
        "cases_scored": len(cases), "responses_scored": len(rows),
        "rater_id": worksheet["rater_id"],
        "source_adjudicator": worksheet["original_source_adjudicator"],
        "mean_paired_differences": {
            name: mean(values) if values else None for name, values in observed.items()
        },
        "cases": paired,
        "causal_limit": ("Post-hoc previously viewed questions; descriptives only. "
                         "No significance or independent character-continuity claim."),
    }


def write_exclusive(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False, sort_keys=True)
        file.write("\n")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="mode", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--run", type=Path, required=True)
    prep.add_argument("--review", type=Path, required=True)
    prep.add_argument("--key", type=Path, required=True)
    prep.add_argument("--worksheet", type=Path, required=True)
    score = sub.add_parser("score")
    score.add_argument("--review", type=Path, required=True)
    score.add_argument("--key", type=Path, required=True)
    score.add_argument("--worksheet", type=Path, required=True)
    score.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.mode == "prepare":
        destinations = [args.review, args.key, args.worksheet]
        if len({v.resolve() for v in destinations}) != 3 or any(v.exists() for v in destinations):
            p.error("Output paths must be distinct and must not already exist")
        result = make_review(json.loads(args.run.read_text(encoding="utf-8")))
        # The secret condition key is written separately; never upload it with
        # masked responses or rater worksheets.
        for file, content in zip(destinations, result):
            write_exclusive(file, content)
        print("Created masked review and separate coordinator-only condition key.")
    else:
        report = score_review(
            json.loads(args.review.read_text(encoding="utf-8")),
            json.loads(args.key.read_text(encoding="utf-8")),
            json.loads(args.worksheet.read_text(encoding="utf-8")),
        )
        write_exclusive(args.output, report)
        print(json.dumps({"scored_cases": report["cases_scored"],
                          "descriptive_only": True}, sort_keys=True))


if __name__ == "__main__":
    main()
