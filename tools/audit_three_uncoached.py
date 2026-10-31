#!/usr/bin/env python3
"""Read-only R4 judge, deliberately independent of Pretorius Python imports.

It may inspect only immutable ledger entries and canonical original
Laboratory/BrainStore receipts. It never selects a goal, presents messages,
moves the subject, or writes to his state. No extra credit for host scheduling.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import sys


EXPECTED = frozenset(("read_book", "rest", "work"))
WORLD_TABLES = frozenset(("books_events", "rhythm_events", "embodied_events"))


def _digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False).encode("utf-8")).hexdigest()


def _db(path):
    # Use a SQLite read-only URI. Never create, checkpoint, or change a world.
    return sqlite3.connect(path.absolute().as_uri() + "?mode=ro", uri=True)


def evaluate(workspace: Path) -> dict:
    workspace = Path(workspace).resolve(strict=True)
    log = workspace / "preview-activity.jsonl"
    brain = workspace / "state" / "brain.sqlite3"
    world = workspace / "laboratory.sqlite3"
    problems, entries, previous = [], [], "0" * 64
    if not log.is_file() or not brain.is_file() or not world.is_file():
        return {"gate": "R4", "status": "FAIL", "reason": "required evidence missing",
                "distinct_valid_activity_kinds": [], "three_distinct_uncoached": False}
    for n, raw in enumerate(log.read_text(encoding="utf-8").splitlines(), 1):
        try:
            item = json.loads(raw)
            payload = {k: v for k, v in item.items() if k != "sha256"}
            assert item["sequence"] == n
            assert item["previous_sha256"] == previous
            assert _digest(payload) == item["sha256"]
            assert item["event"] and isinstance(item["external_input"], bool)
            assert len(item["utc"]) >= 20 and item["beat"].startswith("@")
            previous = item["sha256"]
            entries.append(item)
        except (ValueError, AssertionError, TypeError, KeyError) as exc:
            problems.append("invalid_or_torn_activity_record:" + str(n))
            break
    started = [x for x in entries if x["event"] in ("operator_start", "operator_resume")]
    # Operator start/stop and the *pre-run* book fixture are transparent
    # engineering interventions, never autonomous goals.
    allowed = frozenset((
        "operator_native_mode_selected", "operator_start",
        "operator_resume", "operator_stop", "external_preexisting_lab_fixture",
        "operator_world_17_book_template",
    ))
    if not started:
        problems.append("no_operator_session")
    for item in entries:
        if item["external_input"] and item["event"] not in allowed:
            problems.append("unapproved_external_input:" + item["event"])
        if any(v for k,v in item.get("fields", {}).items() if k in (
                "operator_supplied_goal", "task_instruction", "user_requested_goal")
               and v is not None and v is not False):
            problems.append("coached_task_input:" + item["event"])
    created = {}
    verified = {}
    with closing(_db(brain)) as db, closing(_db(world)) as lab:
        db.row_factory = sqlite3.Row
        for event in entries:
            if not event["event"].startswith("native_goal_"):
                continue
            fields = event.get("fields", {})
            gid, kind = fields.get("goal_id"), fields.get("kind")
            if not gid or kind not in EXPECTED:
                continue
            if event["event"] == "native_goal_goal_created":
                created[gid] = (kind, event["sequence"])
                continue
            if event["event"] != "native_goal_completed":
                continue
            try:
                assert gid in created, "completion lacked recorded origination"
                assert created[gid][0] == kind
                assert created[gid][1] < event["sequence"]
                assert fields.get("source_rechecked_by_host") is True
                assert fields.get("source_attestation_independent") is False
                assert fields.get("operator_supplied_goal") is None
                policy_id = fields["origin_policy_id"]
                p = db.execute(
                    "SELECT selected_action FROM policy_decisions WHERE id=?",
                    (policy_id,)).fetchone()
                assert p is not None
                assert p[0] == fields["original_tendency"]
                assert p[0] == ("explore" if kind == "read_book"
                                else "avoid" if kind == "rest" else "work")
                mid = fields["canonical_memory_id"]
                memory = db.execute(
                    "SELECT source,evidence_class,external,active,text FROM memories WHERE id=?",
                    (mid,)).fetchone()
                assert memory is not None
                assert memory["active"] == 1 and memory["external"] == 0
                assert memory["evidence_class"] == "lived_runtime_memory"
                event_hash = fields["world_receipt_sha256"]
                assert memory["source"] == "laboratory-home:action:" + event_hash
                table = fields["world_table"]
                assert table in WORLD_TABLES
                row = lab.execute(
                    "SELECT payload,event_hash FROM " + table + " WHERE event_id=?",
                    (fields["world_event_id"],)).fetchone()
                assert row and row[1] == event_hash
                source = json.loads(row[0])
                assert hashlib.sha256(json.dumps(
                    source, sort_keys=True, separators=(",", ":"),
                    ensure_ascii=False, allow_nan=False
                ).encode("utf-8")).hexdigest() == event_hash
                action = source.get("action", {})
                if kind == "read_book":
                    assert table == "books_events" and action.get("op") == "read"
                    assert "I read a page of " in memory["text"]
                elif kind == "rest":
                    assert table == "rhythm_events" and action.get("op") == "rest"
                else:
                    assert table == "rhythm_events" and action.get("op") in (
                        "write", "experiment", "work")
                if gid in verified:
                    raise AssertionError("Duplicate goal completion")
                verified[gid] = kind
            except (AssertionError, KeyError, TypeError, ValueError) as exc:
                problems.append("unauthenticated_completion:" + gid + ":" + str(exc))
    kinds = sorted(set(verified.values()))
    # Distinct bodies of activity, not three steps in one book-reading task.
    enough = len(kinds) >= 3 and not problems
    if len(kinds) < 3:
        problems.append("three_distinct_uncoached_activities_not_observed")
    return {
        "schema": "pretorius.r4.independent-readonly-ledger-audit.v1",
        "gate": "R4", "status": "PASS" if enough else "FAIL",
        "distinct_valid_activity_kinds": kinds,
        "validated_goal_count": len(verified),
        "three_distinct_uncoached": enough,
        "external_operator_start_disclosed": bool(started),
        "authentic_source_replay_checked": True,
        "no_source_mutation": True,
        "problems": sorted(set(problems)),
        "independent_human_review_performed": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(args.workspace)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("UNCOACHED_R4_AUDIT=" + json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
