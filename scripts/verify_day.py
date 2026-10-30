"""Independent, fail-closed judge for the M2 autonomous-day research gate.

Never select an action, execute a world command or repair evidence from here.
The saved bundle contains the ORIGINAL BrainStore, ORIGINAL Lab database, the
DoctorHomeBridge intent journal and a process-restart/ablation evidence ledger.
A manifest assertion is never sufficient without independently checking DBs.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys

LAB_PIN = "6e49795752835d64fa6fd63d16359669a1ca2ba7"
SCHEMA = "pretorius.autonomous-day.v1"
TABLES = {
    "embodied_events": "envelope",
    "domestic_events": "envelope",
    "rhythm_events": "envelope",
    "books_events": "payload",
    "custody_events": "payload",
    "instrument_events": "envelope",
}
FAILURES = ("a", "b", "c", "d", "e", "f", "g")
HEX = re.compile(r"[0-9a-f]{64}\Z")


def stable(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def reject(code, message):
    raise DayEvidenceError(code, message)


class DayEvidenceError(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


def db_open(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError("missing or symlinked evidence database: " + str(path))
    conn = sqlite3.connect("file:" + path.resolve().as_posix() + "?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _tables(db):
    return {x[0] for x in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def verified_lab(root: Path, world: Path):
    """Check immutable checked-out source and the independent Lab authorities."""
    pin = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()
    if pin != LAB_PIN:
        reject("a", "wrong physical-world code SHA " + pin)
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.book_library import BookLibrary
    habitat = SpatialHabitat(world)
    habitat.verify()
    HomeLife(habitat).verify()
    DailyRhythm(habitat).verify()
    BookLibrary(habitat).verify()


def source_receipts(world):
    """No manifest-provided receipt counts or hashes are trusted."""
    receipts = {}
    with db_open(world) as db:
        tables = _tables(db)
        for table, col in TABLES.items():
            if table not in tables:
                continue
            for row in db.execute("SELECT event_id," + col + ",event_hash FROM " + table):
                event_id, payload, digest = row
                try:
                    event = json.loads(payload)
                except (TypeError, ValueError):
                    reject("a", "unparseable world event " + str(event_id))
                if not isinstance(event, dict) or not HEX.fullmatch(str(digest)):
                    reject("a", "malformed world receipt " + str(event_id))
                if sha256(stable(event).encode()).hexdigest() != digest:
                    reject("a", "tampered world receipt hash " + str(event_id))
                if event_id in receipts:
                    reject("d", "world event ID reused across domains " + str(event_id))
                receipts[event_id] = (table, event, digest)
    return receipts


def intent_rows(path):
    with db_open(path) as db:
        if "doctor_action_intents" not in _tables(db):
            reject("b", "missing original Doctor intent table")
        return {r["event_id"]: dict(r) for r in db.execute(
            "SELECT event_id,request_json,status FROM doctor_action_intents"
        )}


def brain_evidence(path):
    with db_open(path) as db:
        tables = _tables(db)
        required = {"policy_decisions", "thoughts", "memories", "meta"}
        if not required <= tables:
            reject("b", "missing canonical BrainStore tables")
        policies = {r["id"]: dict(r) for r in db.execute("SELECT * FROM policy_decisions")}
        thoughts = [dict(r) for r in db.execute("SELECT * FROM thoughts")]
        memories = [dict(r) for r in db.execute("SELECT * FROM memories")]
        meta = {r["key"]: r["value"] for r in db.execute("SELECT key,value FROM meta")}
    return policies, thoughts, memories, meta


def _physical_op(table, event):
    if table == "embodied_events":
        return "walk" if event.get("kind") == "move" else None
    if table == "books_events":
        return "book" if event.get("action", {}).get("op") else None
    if table == "custody_events":
        return "take_book" if event.get("action", {}).get("op") == "take" else "put_book"
    if table == "instrument_events":
        return "measure"
    return event.get("op")


def _reject_host_commands(opportunities):
    forbidden = {"action", "next_action", "selected_action", "work_action",
                 "destination", "station", "book_id", "task", "goal", "target",
                 "preferred", "reward", "motor_command"}
    def scan(value):
        if isinstance(value, dict):
            for key, part in value.items():
                if key in forbidden:
                    reject("b", "host provided a choice or target: " + key)
                scan(part)
        elif isinstance(value, list):
            for part in value:
                scan(part)
    scan(opportunities)


def _authored_goal(meta, policies, thoughts, restart):
    """Check original policy + thought and an unchanged durable goal envelope."""
    keys = ("six_organ_endogenous_book_goal_v1", "six_organ_native_rest_intention_v1",
            "pretorius_day_noesis_goal_v1")
    goals = []
    for key in keys:
        raw = meta.get(key)
        if not raw:
            continue
        try:
            envelope = json.loads(raw)
            goal = envelope["payload"]
            if sha256(stable(goal).encode()).hexdigest() != envelope["sha256"]:
                continue
            pid, tid = goal["origin_policy_id"], goal["origin_thought_id"]
            policy = policies[pid]
            thought = next(t for t in thoughts if t["id"] == tid)
            if key == "pretorius_day_noesis_goal_v1":
                evidence = json.loads(policy["state_pressure_json"])
                if (goal.get("schema") != "pretorius.native-day-goal.v1"
                        or goal.get("phase") not in ("active", "complete")
                        or policy["trigger"] != "noesis_situated_choice"
                        or policy["selected_action"] != goal.get("selected_action")
                        or thought["generated_by"] != "noesis_situated_choice:" + pid
                        or thought.get("text") != goal.get("intention")
                        or evidence.get("selector_authority") != "original_noesis"
                        or evidence.get("physical_authority") != "none"):
                    continue
            elif (policy["selected_action"] not in ("explore", "avoid")
                  or thought["generated_by"] != "neural_policy:" + pid):
                continue
            goals.append((key, goal))
        except (KeyError, ValueError, TypeError, StopIteration):
            continue
    if not goals:
        reject("c", "no original-neural-policy-authored durable goal")
    if not isinstance(restart, dict):
        reject("c", "missing hard-kill evidence")
    if (restart.get("signal") not in (9, "SIGKILL")
            or restart.get("exit_code") not in (-9, 137)
            or not isinstance(restart.get("first_pid"), int)
            or not isinstance(restart.get("second_pid"), int)
            or restart["first_pid"] == restart["second_pid"]):
        reject("c", "no evidence of two processes separated by a hard kill")
    matched = []
    for key, goal in goals:
        before = restart.get("before_goal")
        after = restart.get("after_goal")
        if (isinstance(before, dict) and isinstance(after, dict)
                and before.get("id") == after.get("id") == goal["id"]
                and before.get("origin_policy_id") == after.get("origin_policy_id")
                == goal["origin_policy_id"]
                and before.get("phase") not in ("complete", "exhausted")
                and before.get("schema") == after.get("schema") == goal["schema"]):
            matched.append(goal["id"])
    if not matched:
        reject("c", "no pending subject goal retained through cold restart")
    return matched


def _check_ablation(ablations, policies, memories, receipts):
    if not isinstance(ablations, list) or len(ablations) < 20:
        reject("e", "fewer than 20 independent paired seeds")
    used_seeds, with_counts, without_counts = set(), Counter(), Counter()
    changed = 0
    memory_by_id = {m["id"]: m for m in memories}
    for pair in ablations:
        if not isinstance(pair, dict):
            reject("e", "malformed ablation pair")
        seed = pair.get("seed")
        if type(seed) is not int or seed in used_seeds:
            reject("e", "reused or noninteger ablation seed")
        used_seeds.add(seed)
        with_id, without_id = pair.get("with_memory"), pair.get("without_memory")
        if with_id == without_id or with_id not in policies or without_id not in policies:
            reject("e", "ablation missing two independent canonical decisions")
        a, b = policies[with_id], policies[without_id]
        if (a["trigger"] != b["trigger"] or a["trigger"] != "noesis_situated_choice"
                or a["neural_checkpoint_sha256"] != b["neural_checkpoint_sha256"]):
            reject("e", "ablations do not hold neural state and selector fixed")
        ea, eb = json.loads(a["state_pressure_json"]), json.loads(b["state_pressure_json"])
        if (ea.get("outcome_learning_enabled") is not True
                or eb.get("outcome_learning_enabled") is not False
                or ea.get("native_abstract_scores") != eb.get("native_abstract_scores")
                or set(json.loads(a["action_scores_json"])) != set(json.loads(b["action_scores_json"]))
                or not ea.get("used_outcome_memory_ids")
                or eb.get("used_outcome_memory_ids")):
            reject("e", "memory-only ablation lacks matched native priors or lived outcome")
        for mid in ea["used_outcome_memory_ids"]:
            m = memory_by_id.get(mid)
            if (m is None or not m["active"] or m["evidence_class"] != "lived_runtime_memory"
                    or m["external"] or not m["source"].startswith("laboratory-home:action:")
                    or not any(v[2] == m["source"].split(":")[-1] for v in receipts.values())):
                reject("e", "ablation outcome not independently tied to lived Lab event")
        with_counts[a["selected_action"]] += 1
        without_counts[b["selected_action"]] += 1
        changed += a["selected_action"] != b["selected_action"]
    if not changed or with_counts == without_counts:
        reject("e", "removing consequence memory did not change choice distribution")
    return {"seeds": len(used_seeds), "paired_changes": changed,
            "with_memory": dict(with_counts), "without_memory": dict(without_counts)}


def judge(bundle: Path, lab_root: Path, *, baseline=False):
    manifest_path = bundle / "day.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        reject("a", "no saved day.json run evidence")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA or data.get("lab_pin") != LAB_PIN:
        reject("a", "wrong day evidence schema or Lab source pin")
    def path(name):
        value = data.get(name)
        if type(value) is not str or not value or Path(value).is_absolute() or ".." in Path(value).parts:
            reject("a", "invalid relative evidence path " + name)
        return bundle / value
    brain, world, intents = path("brain_db"), path("world_db"), path("intent_db")
    verified_lab(lab_root, world)
    receipts = source_receipts(world)
    reservations = intent_rows(intents)
    policies, thoughts, memories, meta = brain_evidence(brain)
    failures = {}
    try:
        _reject_host_commands(data.get("host_opportunities", []))
    except DayEvidenceError as exc:
        failures[exc.code] = str(exc)
    actions = []
    origins = {}
    # Distinct tasks are an independent physical test. A forged or host-driven
    # task must fail (b) as well, not hide a missing third task under one error.
    try:
        kinds = set()
        for eid, intent in reservations.items():
            if eid in receipts and intent["status"] == "complete":
                kinds.add(_physical_op(receipts[eid][0], receipts[eid][1]))
        kinds.discard(None)
        if len(kinds) < 3:
            reject("a", "fewer than three different completed Lab physical task kinds")
    except DayEvidenceError as exc:
        failures[exc.code] = str(exc)
    try:
        # Every Doctor journal reservation, not merely manifest-listed events,
        # must be justified by one original Noesis choice. No hidden actions.
        if not reservations:
            reject("a", "no Doctor-owned physical actions")
        action_types = set()
        for eid, intent in reservations.items():
            if eid not in receipts:
                reject("a", "Doctor intent has no original Lab receipt: " + eid)
            table, event, digest = receipts[eid]
            req = json.loads(intent["request_json"])
            op = req.get("op")
            if (intent["status"] != "complete" or _physical_op(table, event) != op):
                reject("a", "incomplete or mismatched physical action " + eid)
            # Exact physical request identity, not merely same event ID.
            if op == "walk" and req.get("args", {}).get("station") != event.get("after_station"):
                reject("a", "walk destination mismatches original receipt")
            if op not in ("walk", "book", "take_book", "put_book", "measure") and (
                event.get("args") != req.get("args")
            ):
                reject("a", "action arguments mismatch the actual Lab receipt")
            action_types.add(op)
            matches = []
            for p in policies.values():
                evidence = json.loads(p["state_pressure_json"])
                if evidence.get("motor_event_id") == eid:
                    matches.append((p, evidence))
            if len(matches) != 1:
                reject("b", "physical action lacks unique Noesis policy row " + eid)
            p, evidence = matches[0]
            if (p["selected_action"] != op
                    or evidence.get("selector_authority") != "original_noesis"
                    or evidence.get("physical_authority") != "none"
                    or evidence.get("motor_authorization") != "authorized"
                    or not HEX.fullmatch(p["neural_checkpoint_sha256"])):
                reject("b", "host-authored, unbound or unverifiable Noesis selection " + eid)
            if not any(t["generated_by"] in (
                "noesis_situated_choice:" + p["id"],
                "neural_policy:" + p["id"],
            ) for t in thoughts):
                reject("b", "original Noesis decision lacks original cognitive thought " + eid)
            matching_memory = [m for m in memories if m["source"] == "laboratory-home:action:" + digest]
            if (len(matching_memory) != 1
                    or matching_memory[0]["evidence_class"] != "lived_runtime_memory"
                    or matching_memory[0]["external"]):
                reject("d", "missing or duplicate authenticated first-person action memory " + eid)
            actions.append({"event_id": eid, "action": op, "policy_decision_id": p["id"],
                            "lab_event_hash": digest, "memory_id": matching_memory[0]["id"]})
            origins[eid] = p["id"]
        if len(action_types) < 3:
            reject("a", "fewer than three distinct independently receipted physical task kinds")
        # Physical operations without Doctor intent are unacceptable. Exclude
        # LOOK and bridge-independent secondary effects, not physical commands.
        for eid, (table, event, _) in receipts.items():
            kind = _physical_op(table, event)
            if kind and eid not in reservations and not (
                eid.startswith("motion:") or table == "domestic_events" and event.get("kind") == "reflex"
            ):
                reject("b", "unclaimed physical action in original world ledger " + eid)
    except DayEvidenceError as exc:
        failures[exc.code] = str(exc)
    try:
        goals = _authored_goal(meta, policies, thoughts, data.get("restart"))
    except DayEvidenceError as exc:
        failures[exc.code] = str(exc)
        goals = []
    restart = data.get("restart", {})
    try:
        if (not isinstance(restart, dict) or restart.get("duplicate_world_receipts") != 0
                or restart.get("duplicate_lived_memories") != 0):
            reject("d", "restart replay failed exactly-once world and memory tests")
        # Independently measured final DBs must have no duplicate event IDs or
        # first-person admissions. Manifest counts alone never suffice.
        digests = [m["source"] for m in memories if m["source"].startswith("laboratory-home:action:")]
        if len(digests) != len(set(digests)):
            reject("d", "duplicate first-person Lab action memory found in BrainStore")
    except DayEvidenceError as exc:
        failures[exc.code] = str(exc)
    try:
        ablation = _check_ablation(data.get("ablation"), policies, memories, receipts)
    except DayEvidenceError as exc:
        failures[exc.code] = str(exc)
        ablation = None
    try:
        if (not any(a["action"] in ("rest", "sleep") for a in actions)
                and not data.get("verified_need_conflict")):
            reject("f", "neither original-Noesis rest nor proven needs conflict")
        if data.get("verified_need_conflict") and not any(
            p["trigger"] == "six_organ_lab_cycle" for p in policies.values()
        ):
            reject("f", "conflicting needs claimed without original six-organ cognitive evidence")
    except DayEvidenceError as exc:
        failures[exc.code] = str(exc)
    if not baseline:
        try:
            bp = data.get("random_baseline")
            if type(bp) is not str or not bp or Path(bp).is_absolute() or ".." in Path(bp).parts:
                reject("g", "missing independent random-controller evidence bundle")
            baseline_dir = bundle / bp
            if baseline_dir.resolve() == bundle.resolve():
                reject("g", "baseline cannot reuse tested subject's evidence bundle")
            other = judge(baseline_dir, lab_root, baseline=True)
            if other["pass"] and (
                other["action_distribution"] == dict(Counter(a["action"] for a in actions))
            ):
                reject("g", "random-controller baseline matches every acceptance gate and choices")
        except (DayEvidenceError, ValueError) as exc:
            failures["g"] = str(exc)
    return {
        "schema": "pretorius.day-judge-result.v1",
        "pass": not failures,
        "failures": failures,
        "checks": {code: code not in failures for code in FAILURES if not baseline or code != "g"},
        "distinct_physical_tasks": sorted({a["action"] for a in actions}),
        "receipts": actions,
        "authored_goals": goals,
        "ablation": ablation,
        "action_distribution": dict(Counter(a["action"] for a in actions)),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--lab-root", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = judge(args.run.resolve(), args.lab_root.resolve())
    except (DayEvidenceError, ValueError, KeyError, sqlite3.Error, OSError, subprocess.CalledProcessError, ImportError) as exc:
        result = {"schema": "pretorius.day-judge-result.v1", "pass": False,
                  "failures": {getattr(exc, "code", "evidence"): str(exc)}}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
