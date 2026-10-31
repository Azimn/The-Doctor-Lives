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
import subprocess
import sys
import tempfile


EXPECTED = frozenset(("read_book", "rest", "work"))
WORLD_TABLES = frozenset(("books_events", "rhythm_events", "embodied_events"))


def _digest(value):
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False).encode("utf-8")).hexdigest()


def _db(path):
    # Use a SQLite read-only URI. Never create, checkpoint, or change a world.
    return sqlite3.connect(path.absolute().as_uri() + "?mode=ro", uri=True)


def evaluate_schema_only(workspace: Path) -> dict:
    """Negative-contract check only; NEVER a releasable R4 verdict."""
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
            assert isinstance(item["event"], str) and item["event"]
            assert type(item["fields"]) is dict, "ledger fields must be a dictionary"
            assert type(item["external_input"]) is bool, "external-input boolean required"
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
    verified_origins = {}
    used_world_events = set()
    used_memory_ids = set()
    used_neural_policies = set()
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
                if gid in created:
                    problems.append("duplicate_goal_origin:" + gid)
                else:
                    created[gid] = (kind, event["sequence"],
                                    fields.get("origin_policy_id"),
                                    fields.get("original_tendency"))
                continue
            if event["event"] != "native_goal_completed":
                continue
            try:
                assert gid in created, "completion lacked recorded origination"
                assert created[gid][0] == kind
                assert created[gid][1] < event["sequence"]
                assert created[gid][2] == fields["origin_policy_id"], "origin policy changed after creation"
                assert created[gid][3] == fields["original_tendency"], "neural tendency changed after creation"
                assert fields.get("source_rechecked_by_host") is True
                assert fields.get("source_attestation_independent") is False
                assert fields.get("operator_supplied_goal") is None
                policy_id = fields["origin_policy_id"]
                p = db.execute(
                    "SELECT selected_action,trigger FROM policy_decisions WHERE id=?",
                    (policy_id,)).fetchone()
                assert p is not None
                assert p[0] == fields["original_tendency"]
                expected_origin = {
                    "read_book": ("explore",), "rest": ("avoid",),
                    "work": ("persist", "explore"),
                }[kind]
                assert p[0] in expected_origin, "not original neural goal"
                assert p["trigger"] == "six_organ_lab_cycle", "not a real six-organ policy"
                key = {"read_book": "six_organ_endogenous_book_goal_v1",
                       "rest": "six_organ_native_rest_intention_v1",
                       "work": "six_organ_native_work_intention_v1"}[kind]
                raw = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
                assert raw is not None, "missing canonical goal"
                envelope = json.loads(raw[0])
                intent = envelope["payload"]
                assert _digest(intent) == envelope["sha256"], "tampered goal"
                assert intent["id"] == gid and intent["phase"] == "complete"
                expected_goals = {
                    "read_book": ("pretorius.endogenous-book-pursuit.v1",
                                  "I want to discover a book here and read what it actually says."),
                    "rest": ("pretorius.native-rest-intention.v1",
                             "I want to rest somewhere safe."),
                    "work": ("pretorius.native-work-intention.v1",
                             "I want to undertake worthwhile work at my laboratory bench."),
                }
                assert (intent["schema"], intent["goal"]) == expected_goals[kind], "substituted native goal"
                assert intent["origin_policy_id"] == policy_id
                thought = db.execute(
                    "SELECT generated_by FROM thoughts WHERE id=?",
                    (intent["origin_thought_id"],)
                ).fetchone()
                assert thought is not None and thought["generated_by"] == (
                    "neural_policy:" + policy_id
                ), "native goal lacks original Noesis thought"
                key_memory = "read_memory_id" if kind == "read_book" else "memory_id"
                assert intent[key_memory] == fields["canonical_memory_id"]
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
                column = "payload" if table == "books_events" else "envelope"
                row = lab.execute(
                    "SELECT " + column + ",event_hash FROM " + table +
                    " WHERE event_id=?", (fields["world_event_id"],)
                ).fetchone()
                assert row and row[1] == event_hash
                source = json.loads(row[0])
                assert hashlib.sha256(json.dumps(
                    source, sort_keys=True, separators=(",", ":"),
                    ensure_ascii=False, allow_nan=False
                ).encode("utf-8")).hexdigest() == event_hash
                if kind == "read_book":
                    assert table == "books_events"
                    assert source.get("action", {}).get("op") == "read"
                    assert source.get("page_receipt") is not None
                    assert "I read a page of " in memory["text"]
                elif kind == "rest":
                    assert table == "rhythm_events" and source.get("op") == "rest"
                    assert source.get("station") == "station:bedroom"
                    assert source.get("subject", {}).get("inner") == memory["text"]
                else:
                    assert table == "rhythm_events"
                    action = source.get("op")
                    assert action in ("repair", "experiment"), "not actual bench work"
                    assert source.get("station") == "station:bench"
                    assert source.get("subject", {}).get("inner") == memory["text"]
                    assert intent["selected_action"] == action
                    assert fields["world_event_id"] == "ng_" + gid + "_work"
                    # Two original policy decisions must both be present.
                    # No synthetic neural 'work' category is credited.
                    motor_id = intent["work_policy_id"]
                    motors = db.execute(
                        "SELECT id,selected_action,state_pressure_json FROM "
                        "policy_decisions WHERE trigger='noesis_situated_choice'"
                    ).fetchall()
                    linked = []
                    for motor in motors:
                        evidence = json.loads(motor["state_pressure_json"])
                        if evidence.get("motor_event_id") != fields["world_event_id"]:
                            continue
                        assert motor["id"] == motor_id, "foreign motor binding"
                        assert motor["selected_action"] == action
                        assert evidence.get("selector_authority") == "original_noesis"
                        assert evidence.get("physical_authority") == "none"
                        assert evidence.get("motor_authorization") == "authorized"
                        linked.append(motor["id"])
                    assert linked == [motor_id], "missing or duplicate motor"
                assert fields["canonical_memory_source"] == memory["source"]
                assert fields["world_event_id"] == source["event_id"]
                assert source["world_epoch"] == intent["world_epoch"], "foreign world epoch"
                if gid in verified:
                    raise AssertionError("Duplicate goal completion")
                if (table, fields["world_event_id"]) in used_world_events:
                    raise AssertionError("World receipt reused by another goal")
                if mid in used_memory_ids:
                    raise AssertionError("Canonical lived memory reused by another goal")
                if policy_id in used_neural_policies:
                    raise AssertionError("Neural origin policy reused by another goal")
                used_world_events.add((table, fields["world_event_id"]))
                used_memory_ids.add(mid)
                used_neural_policies.add(policy_id)
                verified[gid] = kind
                verified_origins[gid] = {
                    "kind": kind,
                    "goal_id": gid,
                    "origin_policy_id": policy_id,
                    "origin_thought_id": intent["origin_thought_id"],
                    "original_tendency": fields["original_tendency"],
                    "canonical_checksum": envelope["sha256"],
                }
            except (AssertionError, KeyError, TypeError, ValueError,
                    sqlite3.DatabaseError) as exc:
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
        "verified_goal_origins": verified_origins,
        "three_distinct_uncoached": enough,
        "external_operator_start_disclosed": bool(started),
        "authentic_source_replay_checked": True,
        "no_source_mutation": True,
        "problems": sorted(set(problems)),
        "independent_human_review_performed": False,
    }



ORIGINAL_LAB_SHA = "6e49795752835d64fa6fd63d16359669a1ca2ba7"
# This separate process imports only the reviewed original Laboratory's own
# authority, not Doctor policy, host goal code or artificial evidence.
SOURCE_WORLD_VERIFIER = r"""
import json, sys
from pathlib import Path
from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.embodied_access import EmbodiedAccess
from pretorius_lab.home_life import HomeLife
from pretorius_lab.daily_rhythm import DailyRhythm
from pretorius_lab.book_library import BookLibrary

world = SpatialHabitat(Path(sys.argv[1]))
physical = world.verify()
body = EmbodiedAccess(world).verify()
home = HomeLife(world).verify()
rhythm = DailyRhythm(world).verify()
books = BookLibrary(world).verify()
assert physical["world_epoch"] == body["world_epoch"] == home["world_epoch"] == rhythm["world_epoch"] == books["world_epoch"]
print(json.dumps({
    "schema": "original-laboratory-full-physics-replay.v1",
    "world_epoch": physical["world_epoch"],
    "lab_id": physical["lab_id"],
    "physical_revision": physical["revision"],
    "body_revision": body["revision"],
    "home_revision": home["revision"],
    "rhythm_revision": rhythm["revision"],
    "rhythm_head_hash": rhythm["head_hash"],
    "books_revision": books["revision"],
    "checks": ["SpatialHabitat.verify", "EmbodiedAccess.verify",
               "HomeLife.verify", "DailyRhythm.verify", "BookLibrary.verify"],
}, sort_keys=True))
"""


def verify_original_world_snapshot(workspace: Path) -> dict:
    """Run full original source physics on an isolated SQLite read snapshot.

    The judge cannot mutate the live world. The sealed offline installation
    supplies an exact source-pinned original Laboratory wheel. A missing wheel
    or absent install receipt is a hard FAIL, never a synthetic fallback.
    """
    import os
    root = Path(workspace).resolve(strict=True).parent
    world = Path(workspace) / "laboratory.sqlite3"
    receipt_path = root / "installed-bundle-receipt.json"
    if not receipt_path.is_file():
        raise RuntimeError("sealed_original_world_install_receipt_missing")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if (receipt.get("original_laboratory_commit") != ORIGINAL_LAB_SHA
            or receipt.get("books") != 17
            or receipt.get("release_accepted") is not False):
        raise PermissionError("source_pinned_original_world_custody_mismatch")
    executable = root / ".venv" / (
        "Scripts/python.exe" if os.name == "nt" else "bin/python"
    )
    if not executable.is_file() or executable.is_symlink():
        raise RuntimeError("source_pinned_original_world_python_missing")
    if not world.is_file() or world.is_symlink():
        raise RuntimeError("original_world_missing_or_symlink")
    with tempfile.TemporaryDirectory(prefix="pretorius-r4-readonly-source-") as temp:
        copy_path = Path(temp) / "original-world-snapshot.sqlite3"
        # Input connection is explicitly read-only and backup creates a
        # consistent committed snapshot. Original .verify may use RW handles
        # on the temporary copy only, never on the installed real world.
        with closing(_db(world)) as source, closing(sqlite3.connect(copy_path)) as target:
            source.backup(target)
        result = subprocess.run(
            [str(executable), "-I", "-c", SOURCE_WORLD_VERIFIER, str(copy_path)],
            capture_output=True, text=True, timeout=90,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "original_laboratory_physics_replay_failed:" +
                result.stderr[-360:].strip()
            )
        result_data = json.loads(result.stdout)
        if (result_data.get("schema") != "original-laboratory-full-physics-replay.v1"
                or len(result_data.get("checks", [])) != 5
                or result_data.get("world_epoch") is None):
            raise RuntimeError("original_laboratory_source_proof_malformed")
        return result_data



def verify_external_origin_witness(path: Path | None, expected: dict) -> dict:
    """Correlate source goals with an independent live process observation.

    The external runner records the initial BrainStore BEFORE launching the
    installed operator, then reads canonical goal/policy/thought rows while
    the process is alive. A preseeded or post-run coordinated rewrite cannot
    acquire credit from a self-hashed operator ledger alone. This is process
    custody evidence, NOT cryptographic proof of uncoached neural causality.
    """
    if path is None or not Path(path).is_file() or Path(path).is_symlink():
        raise PermissionError("independent_neural_origin_witness_missing")
    observations = []
    last_elapsed = -1.0
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        entry = json.loads(raw)
        if (entry.get("schema") !=
                "pretorius.r4.external-neural-origin-observation.v1"
                or type(entry.get("process_alive")) is not bool
                or type(entry.get("goals")) is not dict
                or entry.get("source_authentication_performed") is not False
                or entry.get("autonomy_credit") is not False
                or type(entry.get("elapsed_seconds")) not in (int, float)
                or entry["elapsed_seconds"] < last_elapsed):
            raise ValueError("malformed_independent_origin_observation")
        last_elapsed = entry["elapsed_seconds"]
        observations.append(entry)
    if not observations or observations[0]["process_alive"] is not False:
        raise ValueError("independent_origin_baseline_missing")
    baseline = {
        row.get("goal_id") for row in observations[0]["goals"].values()
        if type(row) is dict
    }
    if baseline.intersection(expected):
        raise PermissionError("preexisting_goal_cannot_be_claimed_as_new")
    observed = set()
    final_checksums_seen = set()
    for entry in observations[1:]:
        if not entry["process_alive"]:
            continue
        for kind, row in entry["goals"].items():
            if type(row) is not dict:
                raise ValueError("malformed_independent_origin_row")
            goal_id = row.get("goal_id")
            expected_row = expected.get(goal_id)
            if expected_row is None:
                continue
            if (expected_row["kind"] != kind
                    or row.get("origin_policy_id") != expected_row["origin_policy_id"]
                    or row.get("origin_thought_id") != expected_row["origin_thought_id"]
                    or row.get("selected_tendency") != expected_row["original_tendency"]
                    or row.get("policy_trigger") != "six_organ_lab_cycle"
                    or row.get("thought_generated_by") !=
                    "neural_policy:" + expected_row["origin_policy_id"]
                    or row.get("checksum_matches") is not True
                    or row.get("record_consistency_only") is not True):
                raise PermissionError("independent_origin_source_mismatch:" + goal_id)
            # Canonical goals legitimately change their checksums as the
            # authentic physical task advances through travel/complete.
            # Independently observe BOTH the original immutable origin and
            # the final sealed canonical envelope while the process is alive.
            # A fabricated or preseeded origin still fails baseline/custody.
            if row.get("canonical_checksum") == expected_row["canonical_checksum"]:
                final_checksums_seen.add(goal_id)
            observed.add(goal_id)
    if not expected or observed != set(expected) or final_checksums_seen != set(expected):
        raise PermissionError("independent_live_origin_not_observed")
    return {"observed_goal_ids": sorted(observed),
            "observation_count": len(observations),
            "process_witness_not_neural_causal_proof": True}


def evaluate(workspace: Path, *, origin_witness: Path | None = None) -> dict:
    """Release-facing independent ledger audit, never synthetic positive."""
    evidence = evaluate_schema_only(workspace)
    try:
        proof = verify_original_world_snapshot(workspace)
        # Compare replayed authoritative Laboratory identity to each claimed
        # native goal. The original verifier also replays real world state,
        # every original ledger's chain and complete book custody.
        with closing(_db(Path(workspace) / "state" / "brain.sqlite3")) as db:
            goals = []
            for key in ("six_organ_endogenous_book_goal_v1",
                        "six_organ_native_rest_intention_v1",
                        "six_organ_native_work_intention_v1"):
                row = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
                if row:
                    goals.append(json.loads(row[0])["payload"])
        if any(g.get("world_epoch") != proof["world_epoch"] for g in goals):
            raise PermissionError("goal_world_epoch_mismatches_replayed_authority")
        evidence["source_pinned_original_laboratory_sha"] = ORIGINAL_LAB_SHA
        evidence["authoritative_world_epoch"] = proof["world_epoch"]
        evidence["full_original_physics_replay"] = proof["checks"]
        evidence["original_source_world_verified"] = True
    except (OSError, sqlite3.Error, ValueError, KeyError, PermissionError,
            RuntimeError, subprocess.TimeoutExpired) as exc:
        evidence["status"] = "FAIL"
        evidence["three_distinct_uncoached"] = False
        evidence["original_source_world_verified"] = False
        evidence["full_original_physics_replay"] = []
        evidence.setdefault("problems", []).append(
            "original_source_world_authority_not_verified:" + type(exc).__name__ +
            ":" + str(exc)[:240]
        )
    try:
        witnessed = verify_external_origin_witness(
            origin_witness, evidence.get("verified_goal_origins", {})
        )
        evidence["independent_live_neural_origin_observed"] = True
        evidence["independent_origin_observation"] = witnessed
    except (OSError, ValueError, KeyError, TypeError, PermissionError) as exc:
        evidence["status"] = "FAIL"
        evidence["three_distinct_uncoached"] = False
        evidence["independent_live_neural_origin_observed"] = False
        evidence.setdefault("problems", []).append(
            "independent_origin_witness_not_verified:" +
            type(exc).__name__ + ":" + str(exc)[:200]
        )
    return evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--origin-witness", type=Path)
    args = parser.parse_args()
    result = evaluate(args.workspace, origin_witness=args.origin_witness)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("UNCOACHED_R4_AUDIT=" + json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
