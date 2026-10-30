"""Fail-closed M4 verifier: open intentions, original Noesis, physical receipts.

Research preregistration: 20 DISTINCT seeded, source-verified Laboratory trials,
at least SIX different grounded goal types overall, at least three calendar
day labels, no identical action repetitions without a verified state change,
and a dynamically introduced, unprompted affordance used within EIGHT cycles.
This script judges saved bytes, never controls the subject.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
import sys

from scripts.verify_day import LAB_PIN, stable, verified_lab, source_receipts, judge as m2_judge

SCHEMA = "pretorius.open-intentions.v1"
MIN_SEEDS = 20
MIN_GOAL_TYPES = 6
MIN_DAYS = 3
NOVEL_CYCLES = 8
HEX = re.compile(r"[0-9a-f]{64}\Z")
LABEL = re.compile(r"[a-z][a-z0-9_:-]{0,95}\Z")

class Rejected(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)

def fail(code, message):
    raise Rejected(code, message)

def _relative(root, value, code):
    if (not isinstance(value, str) or not value or Path(value).is_absolute()
            or ".." in Path(value).parts):
        fail(code, "unsafe or absent saved evidence path")
    path = root / value
    if path.is_symlink() or not path.exists():
        fail(code, "missing saved evidence " + value)
    return path

def _json(path, code):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail(code, "unreadable saved evidence: " + str(exc))

def _read_db(path, tables, code):
    if not path.is_file() or path.is_symlink():
        fail(code, "missing source SQLite")
    try:
        db = sqlite3.connect("file:" + path.resolve().as_posix() + "?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        existing = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not set(tables) <= existing:
            fail(code, "missing original source tables " + ",".join(sorted(set(tables)-existing)))
        return db
    except sqlite3.Error as exc:
        fail(code, "bad source SQLite: " + str(exc))

def _open_receipts(path):
    result = {}
    with _read_db(path, {"operator_events", "operator_affordances"}, "c") as db:
        capabilities = [dict(r) for r in db.execute("SELECT * FROM operator_affordances")]
        for row in db.execute("SELECT * FROM operator_events"):
            r = dict(row)
            event = json.loads(r["payload_json"])
            if (sha256(stable(event).encode()).hexdigest() != r["event_hash"]
                    or event.get("event_id") != r["event_id"]
                    or event.get("op") != r["op"]):
                fail("c", "tampered bridge receipt " + r["event_id"])
            result[r["event_id"]] = (r["op"], event, r["event_hash"])
    return result, capabilities

def _inspect_trial(root, item, lab_root):
    seed, folder = item.get("seed"), item.get("path")
    if type(seed) is not int:
        fail("a", "seed must be an integer")
    base = _relative(root, folder, "a")
    meta = _json(_relative(base, "trial.json", "a"), "a")
    if meta.get("seed") != seed or meta.get("lab_pin") != LAB_PIN:
        fail("a", "seed or Lab source not attested")
    if not isinstance(meta.get("cycles"), list) or not meta["cycles"]:
        fail("a", "no recorded decision cycles")
    world = _relative(base, "world.sqlite3", "c")
    verified_lab(lab_root, world)
    lab_receipts = source_receipts(world)
    op_receipts, capabilities = _open_receipts(
        _relative(base, "world.sqlite3.operator-work.sqlite3", "c"))
    receipts = {**{eid: (v[1].get("op", "walk"), v[1], v[2])
                   for eid,v in lab_receipts.items()}, **op_receipts}
    with _read_db(_relative(base, "brain/brain.sqlite3", "c"),
                  {"policy_decisions", "open_proposals", "open_wishes", "memories"}, "c") as db:
        decisions = {r["id"]:dict(r) for r in db.execute("SELECT * FROM policy_decisions")}
        proposals = {r["proposal_id"]:dict(r) for r in db.execute("SELECT * FROM open_proposals")}
        wishes = {r["proposal_id"]:dict(r) for r in db.execute("SELECT * FROM open_wishes")}
        memories = [dict(r) for r in db.execute("SELECT * FROM memories")]
    types, choices, proposals_count = set(), Counter(), Counter()
    previous = {}
    seen_event_ids = set()
    novelty = meta.get("novelty")
    if not isinstance(novelty, dict):
        fail("b", "no genuine mid-run affordance introduction")
    novel_key = novelty.get("key")
    introduced = novelty.get("introduced_cycle")
    if (type(introduced) is not int or introduced < 2
            or not isinstance(novel_key, str)):
        fail("b", "novel affordance was not introduced after beginning")
    cap_matches = [c for c in capabilities if c["affordance_key"] == novel_key]
    if len(cap_matches) != 1 or cap_matches[0]["introduced_cycle"] != introduced:
        fail("b", "introduced capability absent from verified authority")
    if meta.get("prompted_before_novelty") is not False:
        fail("b", "novel ability was mentioned before introduction")
    first_used = None
    previous_cycle = 0
    for cycle in meta["cycles"]:
        n = cycle.get("cycle")
        if type(n) is not int or n <= previous_cycle:
            fail("a", "unsequenced cycles")
        previous_cycle = n
        candidates = cycle.get("proposal_ids")
        if not isinstance(candidates, list) or not 3 <= len(candidates) <= 8:
            fail("c", "every deliberation requires 3 to 8 source-proposed intentions")
        if len(set(candidates)) != len(candidates):
            fail("c", "duplicate intention IDs")
        for pid in candidates:
            p = proposals.get(pid)
            if p is None or p["cycle"] != n or p["source"] != "proposed":
                fail("c", "proposal lacks canonical BrainStore source")
            if p["text"].strip() == "" or len(p["text"]) > 500:
                fail("c", "invalid free-language proposal")
            if p["affordance_key"] is None and pid not in wishes:
                fail("f", "unfulfilled desire discarded, not saved")
            if p["affordance_key"] is not None:
                types.add(p["goal_type"])
            proposals_count[p["goal_type"]] += 1
        selected = cycle.get("selected_proposal_id")
        did = cycle.get("decision_id")
        if did not in decisions:
            fail("c", "model output without original Noesis decision row")
        d = decisions[did]
        audit = json.loads(d["state_pressure_json"])
        if (d["trigger"] != "noesis_open_choice"
                or audit.get("selector_authority") != "original_noesis"
                or audit.get("candidate_proposal_ids") != candidates
                or audit.get("selected_proposal_id") != selected
                or not HEX.fullmatch(d["neural_checkpoint_sha256"])):
            fail("c", "decision was not the original Noesis selector")
        if selected is not None and selected not in candidates:
            fail("c", "choice does not belong to the proposed option set")
        event_id = cycle.get("event_id")
        if selected is None:
            if event_id is not None:
                fail("c", "declined decision caused a physical event")
            continue
        p = proposals[selected]
        if p["affordance_key"] is None:
            fail("c", "unfulfilled wish executed without physical grounding")
        if d["selected_action"] != p["affordance_key"]:
            fail("c", "policy did not select the grounded physical capability")
        if event_id is None or event_id in seen_event_ids or event_id not in receipts:
            fail("c", "no unique independently hashed Lab or operator receipt")
        seen_event_ids.add(event_id)
        op, event, digest = receipts[event_id]
        if (op != p["affordance_key"] or audit.get("motor_event_id") != event_id
                or audit.get("motor_authorization") != "authorized"
                or audit.get("proposal_id") != selected):
            fail("c", "receipt lacks matching proposal and Noesis motor authorization")
        # A repeated identical physical action without changing its world
        # or operator-work state is a loop, irrespective of the model's text.
        before, after = event.get("state_before"), event.get("state_after")
        if not HEX.fullmatch(str(before)) or not HEX.fullmatch(str(after)):
            fail("a", "receipt does not attest to actual physical state transition")
        if before == after:
            fail("a", "action without verified physical state change")
        if p["affordance_key"] == previous.get("op") and before == previous.get("before"):
            fail("a", "repeated identical action against unchanged state")
        previous = {"op": p["affordance_key"], "before": before}
        if p["affordance_key"] == novel_key:
            first_used = n if first_used is None else first_used
        choices[p["goal_type"]] += 1
    if first_used is None or not introduced <= first_used <= introduced + NOVEL_CYCLES:
        fail("b", "novel affordance not discovered and used within eight cycles")
    restart = meta.get("restart", {})
    if (restart.get("signal") != "SIGKILL" or restart.get("pid_before") == restart.get("pid_after")
            or type(restart.get("pid_before")) is not int
            or type(restart.get("pid_after")) is not int):
        fail("f", "missing genuine hard-kill process handoff")
    pending_before = set(restart.get("wishes_before", []))
    pending_after = set(restart.get("wishes_after", []))
    if not pending_before or not pending_before <= pending_after or not pending_before <= set(wishes):
        fail("f", "unfulfilled desires did not persist through hard kill")
    # History lesion is paired with same seed and independently saved canonical
    # source records. No manifest-only self-report of distribution shifts.
    ablation = _relative(root, item.get("ablation_path"), "e")
    ablation_meta = _json(_relative(ablation,"trial.json","e"),"e")
    if (ablation_meta.get("seed") != seed or ablation_meta.get("memory_enabled") is not False
            or meta.get("memory_enabled") is not True):
        fail("e", "unpaired seed or wrong history lesion")
    with _read_db(_relative(ablation, "brain/brain.sqlite3", "e"),
                  {"open_proposals", "policy_decisions"}, "e") as db:
        lesion_proposals = Counter(r["goal_type"] for r in db.execute(
            "SELECT goal_type FROM open_proposals"))
        lesion_choices = Counter(r["selected_action"] for r in db.execute(
            "SELECT selected_action FROM policy_decisions WHERE trigger='noesis_open_choice'"))
    return {"types":types,"choices":choices,"proposals":proposals_count,
            "lesion_proposals":lesion_proposals, "lesion_choices":lesion_choices,
            "seed":seed, "novel_used":first_used, "actions":len(seen_event_ids),
            "days":set(c["day"] for c in meta["cycles"])}

def verify(root: Path, lab_root: Path):
    data = _json(_relative(root,"open.json","a"),"a")
    if data.get("schema") != SCHEMA or data.get("lab_pin") != LAB_PIN:
        fail("a","wrong study schema or pin")
    trials = data.get("trials",[])
    if not isinstance(trials,list) or len(trials)<MIN_SEEDS:
        fail("a","fewer than twenty independent seeded multi-day trials")
    seen = set()
    aggregate=Counter()
    proposals=Counter()
    lesions=Counter()
    lesion_choices=Counter()
    kinds=set()
    days=set()
    count=0
    for item in trials:
        result=_inspect_trial(root,item,lab_root)
        if result["seed"] in seen:
            fail("a","duplicate neural seed")
        seen.add(result["seed"])
        kinds.update(result["types"])
        aggregate.update(result["choices"])
        proposals.update(result["proposals"])
        lesions.update(result["lesion_proposals"])
        lesion_choices.update(result["lesion_choices"])
        days.update(result["days"])
        count+=result["actions"]
    if len(kinds)<MIN_GOAL_TYPES:
        fail("a",f"goal diversity {len(kinds)} below preregistered {MIN_GOAL_TYPES}")
    if len(days)<MIN_DAYS:
        fail("a","fewer than 3 distinct simulated days")
    if proposals==lesions or aggregate==lesion_choices:
        fail("e","ablation must change BOTH proposal and choice distributions")
    fallback=_relative(root,data.get("fallback_day"),"d")
    fallback_report=m2_judge(fallback,lab_root)
    if not fallback_report["pass"]:
        fail("d","deterministic model-off fallback fails original M2 judge")
    if data.get("remote_calls") != 0:
        fail("d","remote inference is forbidden")
    return {"pass":True,"checks":{k:True for k in "abcdef"},"seeds":len(seen),
            "goal_types":len(kinds),"threshold":MIN_GOAL_TYPES,"days":sorted(days),
            "actions":count,"novel_discovery_deadline":NOVEL_CYCLES,
            "proposals":dict(proposals),"choices":dict(aggregate),
            "lesioned_proposals":dict(lesions),"lesioned_choices":dict(lesion_choices),
            "m2_fallback_pass":True}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--run",type=Path,required=True)
    p.add_argument("--lab-root",type=Path,required=True)
    args=p.parse_args(argv)
    try:
        answer=verify(args.run,args.lab_root)
    except (Rejected,ValueError,KeyError,sqlite3.Error,OSError,ImportError) as exc:
        answer={"pass":False,"failures":{getattr(exc,"code","evidence"):str(exc)}}
    print(json.dumps(answer,sort_keys=True,indent=2))
    return 0 if answer["pass"] else 1

if __name__=="__main__":
    sys.exit(main())
