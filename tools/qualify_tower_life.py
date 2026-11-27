"""Longitudinal product qualification of the actual original Tower runner.

Fresh isolated workspace only. No selected action, destination, goal,
scripted activity, donor substitution or synthetic evidence is supplied.
The result is a mechanical integration report, not a consciousness or
character-fidelity claim. An unfinished faculty produces an incomplete gate.
"""
from __future__ import annotations
import argparse
from contextlib import closing
import json
import os
from pathlib import Path
import uuid

from doctor_lives.small_tower import initialize_tower, run_tower_life, SmallTowerSource, PENDING
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.tower_phantasmagorium import require_archive
from doctor_lives.tower_prospective import PREFIX


def inspect_life(store, snapshot, runs):
    with closing(store.connect()) as db:
        decisions = db.execute(
            "SELECT id,selected_action,state_pressure_json FROM policy_decisions "
            "WHERE trigger='noesis_world_affordance' ORDER BY rowid").fetchall()
        commitments = db.execute("SELECT * FROM commitments WHERE source LIKE 'telos:native:tower:%'").fetchall()
        goals = db.execute("SELECT * FROM commitments WHERE source LIKE ?", (PREFIX+"%",)).fetchall()
        imagination = db.execute("SELECT value FROM meta WHERE key LIKE 'phantasmagorium:tower-event:%'").fetchall()
    choices = [json.loads(row["state_pressure_json"]) for row in decisions]
    reports = [json.loads(row["value"]) for row in imagination]
    wakes = [w for run in runs for w in run["background_receipts"]]
    physical = [m for m in store.memories(False) if m["source"].startswith("virtual-world:small-tower:")]
    emitted = [m for m in store.memories() if m["source"].startswith("local-emission:")
               and m["kind"] == "confirmed_written_utterance"]
    source_ticks = sum(run["new_source_ticks"]+run["recovered_source_ticks"] for run in runs)
    by_policy = {row["id"]:row for row in decisions}
    outcomes = []
    for row in snapshot["events"]:
        if row["kind"] not in ("completed","action_failed") or not row.get("policyRef"):
            continue
        policy = by_policy.get(row["policyRef"])
        if policy is None:
            raise PermissionError("World outcome has no canonical policy")
        expected = "doctor_move" if policy["selected_action"].startswith("move_") else policy["selected_action"]
        if row["operation"] != expected:
            raise PermissionError("World outcome differs from canonical policy")
        saved = store.meta("telos:tower-outcome:"+policy["id"])
        if not saved:
            raise PermissionError("World outcome has no protected Telos receipt")
        report = json.loads(saved)
        memory = store.get_memory(report["source_memory_id"])
        source = ("virtual-world:small-tower:"+snapshot["epoch"]+":"
                  +("action" if row["kind"]=="completed" else "observation")+":"
                  +row["id"]+"-"+row["sha256"][:32])
        if (not memory or memory["external"] or memory["source"]!=source
                or memory["text"]!=row["text"] or memory["evidence_class"]!="lived_runtime_memory"):
            raise PermissionError("Source outcome lacks exact lived evidence")
        outcomes.append(row)
    from doctor_lives.tower_ipseity import TowerIpseity
    # Use the exact existing store; verification does not construct a brain.
    from types import SimpleNamespace
    history=TowerIpseity(SimpleNamespace(store=store)).verify_history()
    by_key={e["key"]:e for e in history}
    organs = {
        "Synthetic Ipseity": bool(history) and bool(choices) and all(
            c.get("ipseity",{}).get("required") is True
            and c["ipseity"]["admission_key"] in by_key
            and by_key[c["ipseity"]["admission_key"]]["sha256"]==c["ipseity"]["admission_sha256"] for c in choices),
        "Sensus": bool(decisions) and all(store.meta("small-tower:choice:"+r["id"])
                    and json.loads(store.meta("small-tower:choice:"+r["id"]))["sensus"]["source_memory_id"]
                    for r in decisions),
        "Corpus": bool(outcomes) and bool(decisions) and all(
                    "corpus" in json.loads(store.meta("small-tower:choice:"+r["id"])) for r in decisions),
        "Affectus": bool(decisions) and all(
                    "affectus" in json.loads(store.meta("small-tower:choice:"+r["id"])) for r in decisions),
        "Mnemosyne": bool(wakes) and all(w["mnemosyne_policy_id"] for w in wakes),
        "Noesis": bool(decisions) and bool(outcomes),
        "Expression": bool(emitted),
        "Telos": any(r["status"]=="kept" for r in commitments) and any(r["status"]=="kept" for r in goals),
        "Conclave": bool(choices) and all(c["conclave"]["reading_ids"] for c in choices),
        "Phantasmagorium": (any(r["operation"]=="night" for r in reports)
                            and any(r["operation"]=="fancy" and r.get("fictional_motifs") for r in reports)
                            and all(not r["factual_memory_eligible"] and not r["world_authority"]
                                    and not r["motor_authority"] for r in reports)),
    }
    mechanisms = {
        "cascade_endogenous_busy_activity": any(w.get("during_activity") for w in wakes),
        "cascade_no_motor_or_renderer": bool(wakes) and all(w["external_actions"]==0 and w["renderer_calls"]==0
                                  and w.get("physical_revision_unchanged") is True for w in wakes),
        "synthetic_ipseity_written_expression": bool(emitted),
        "source_monitoring": bool(physical) and all(not m["external"] and m["evidence_class"]=="lived_runtime_memory"
                             for m in physical) and all(not r["factual_memory_eligible"] for r in reports),
        "developmental_appraisal_positive_use": any(any(c["developmental_history"]["source_memory_ids"].values())
                                                    for c in choices),
        "procedural_sequence_positive_use": any(any(c["procedural_memory"]["source_memory_ids"].values())
                                                 for c in choices),
        "prospective_goal_fulfilled": any(r["status"]=="kept" for r in goals),
        "no_duplicate_world_memory": len(physical)==len({m["source"] for m in physical}),
        "no_unreconciled_world_request": store.meta(PENDING) is None,
    }
    return {"schema":"pretorius.tower-longitudinal-mechanical.v1",
            "source_ticks":source_ticks,"completed_activities":sum(r["kind"]=="completed" for r in outcomes),
            "distinct_completed_activities":sorted({r["operation"] for r in outcomes if r["kind"]=="completed"}),
            "policy_count":len(decisions),"private_wakes":len(wakes),"prospective_goals":len(goals),
            "kept_prospective_goals":sum(r["status"]=="kept" for r in goals),
            "organs_observed":organs,"supporting_mechanisms_observed":mechanisms,
            "alive":not snapshot["deceased"],"character_fidelity_qualified":False,
            "full_release_certified":False}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--workspace",type=Path,required=True)
    ap.add_argument("--tower-source",type=Path,required=True)
    ap.add_argument("--model",required=True,help="Existing local Ollama model for guarded Expression")
    ap.add_argument("--max-opportunities",type=int,default=300)
    ap.add_argument("--min-source-ticks",type=int,default=3000)
    args=ap.parse_args()
    if args.workspace.exists() or not 1<=args.max_opportunities<=1000 or args.min_source_ticks<3000:
        raise ValueError("Use a fresh workspace and at least 3000 actual source ticks")
    from doctor_lives.lab_phantasmagorium import configured_archive
    if configured_archive() is None:
        raise FileNotFoundError("Exact Phantasmagorium donor required for all-ten qualification")
    from doctor_lives.local_subject_gloss import valid_local_model
    if not valid_local_model(args.model):
        raise ValueError("Existing local model identifier required")
    args.workspace.mkdir(parents=True)
    state=args.workspace/"doctor"
    world=args.workspace/"tower.json"
    initialize_tower(state,args.tower_source,world,epoch="qualify-"+uuid.uuid4().hex)
    runs=[]
    remaining=args.max_opportunities
    while remaining:
        block=min(10,remaining)
        # A 1000-tick pulse completes even a 250-tick sleep, hiding every
        # in-progress activity from the required CASCADE busy-boundary gate.
        # Keep the ordinary 100-tick host cadence, independent of task choice.
        result=run_tower_life(state,args.tower_source,world,authorize=True,
                              opportunities=block,steps=100,background_every_ticks=100,
                              require_phantasmagorium=True)
        runs.append(result)
        # Persist actual returned receipts before another block. Interrupted
        # rehearsals retain evidence without being labeled fresh passes.
        with (args.workspace/"qualification-progress.jsonl").open("a",encoding="utf-8") as stream:
            stream.write(json.dumps(result,sort_keys=True)+"\n")
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps({"progress_source_ticks":sum(r["new_source_ticks"]+r["recovered_source_ticks"] for r in runs),
                          "opportunities":sum(r["opportunities_completed"] for r in runs)}),flush=True)
        remaining-=result["opportunities_completed"]
        if result["status"]=="deceased" or sum(r["new_source_ticks"]+r["recovered_source_ticks"] for r in runs)>=args.min_source_ticks:
            break
    # Actual local output delivery. Ask about the present situation, not a
    # target activity, goal, destination, or evaluation answer.
    provider=SmallTowerSource(args.tower_source,world)
    snapshot=provider.snapshot()
    expression_error=None
    if not snapshot["deceased"]:
        from doctor_lives.ipseity_local import local_turn
        from doctor_lives.speech_emission import SpeechSinkAck,digest
        def sink(text,key):
            with (args.workspace/"expression.jsonl").open("a",encoding="utf-8") as stream:
                stream.write(json.dumps({"key":key,"text":text},ensure_ascii=False)+"\n")
                stream.flush()
                os.fsync(stream.fileno())
            return SpeechSinkAck(key,"longitudinal-local-file",digest(text))
        try:
            local_turn(state,user_text="What is on your mind at present?",model=args.model,
                       governed=True,emit=sink)
        except Exception as exc:
            expression_error=type(exc).__name__
    runtime=SixOrganRuntime.open(state)
    report=inspect_life(runtime._port.brain.store,snapshot,runs)
    report["expression_error"]=expression_error
    report["model_identifier"]=args.model
    report["minimum_source_ticks"]=args.min_source_ticks
    report["mechanical_gate_passed"]=(report["alive"] and report["source_ticks"]>=args.min_source_ticks
        and all(report["organs_observed"].values()) and all(report["supporting_mechanisms_observed"].values())
        and expression_error is None)
    (args.workspace/"qualification.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,sort_keys=True))
    return 0 if report["mechanical_gate_passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())
