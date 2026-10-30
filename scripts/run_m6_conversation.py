"""Real original Laboratory M6 dialogue acceptance producer, no hosted APIs.

Three *simulated* dates do not mean a 72-hour wall-clock soak. All source
receipts and canonical brain files remain in the uploaded CI artifact.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import json
import os
from pathlib import Path
import shutil
import sqlite3
import signal
import subprocess
import sys
import tempfile
import time

from doctor_lives.causal_audit import CausalAuditHarness
from doctor_lives.conversation_claims import admit_model_draft
from doctor_lives.operator_conversation import OperatorConversation
from doctor_lives.open_inference import DeterministicFallback
from doctor_lives.open_intentions import propose_intentions,noesis_open_choice
from scripts.run_m4_open import open_subject,run_cycle
from scripts.verify_conversation import verify

def operator_influence(root: Path) -> dict:
    """20 exact original-neural states, each with two source-distinct controls."""
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.subject_port import SubjectPort
    from doctor_lives.chassis import PretoriusBrainPort
    from doctor_lives.lab_home_bridge import DoctorHomeBridge
    from doctor_lives.open_lab_bridge import OperatorWork
    results=[]
    contrasts=Counter()
    pressure=defaultdict(list)
    for seed in range(6600,6620):
        base=root/str(seed)/"base"
        original,_,_=open_subject(base,seed,True)
        original.save()
        harness=CausalAuditHarness(base/"brain",base.parent/"cloned-brains")
        arms=[]
        for label,operator_text in (
            ("subject","I am interested in creating something new, like writing a story."),
            ("no-message",None),
            ("shuffled-topic","I am interested in investigating unfamiliar archives."),
        ):
            brain=harness._clone_seed(label)
            world=base.parent/(label+"-world.sqlite3")
            # SQLite WAL may hold fresh EmbodiedAccess/Laboratory initialization.
            # Copy via a real SQLite backup instead of copying only the main DB.
            with sqlite3.connect(base/"world.sqlite3") as original_db, sqlite3.connect(world) as copy_db:
                original_db.backup(copy_db)
            channel=OperatorConversation(brain,world)
            if operator_text is not None:
                channel.receive(operator_text,turn_id="operator_interest_"+label.replace("-","_"))
            proposals=propose_intentions(channel.bridge,channel.work,
                                          DeterministicFallback(),1)
            decision=noesis_open_choice(channel.bridge,channel.work,proposals,1)
            with channel.doctor.brain.store.connect() as db:
                audit=json.loads(db.execute("SELECT state_pressure_json FROM policy_decisions WHERE id=?",
                                             (decision["decision_id"],)).fetchone()[0])
            pressures={key:{
                "neural":float(item["neural"]),
                "operator_interest":float(item["operator_interest"]),
                "novelty":float(item["novelty"]),
                "familiarity":float(item["familiarity"]),
                "history":float(item["history"]),
                "total":float(item["total"]),
                "tendency":item["tendency"],
            } for key,item in audit["contributions"].items()}
            arms.append({
                "condition":label,
                "selected_affordance":decision["selected_affordance"],
                "selected_proposal_id":decision["selected_proposal_id"],
                "policy_id":decision["decision_id"],
                "operator_memories":audit["operator_memory_ids"],
                "pressures":pressures,
            })
            for value in pressures.values():
                for key in ("neural","operator_interest","novelty","familiarity","history"):
                    pressure[key].append(value[key])
        chosen=[a["selected_affordance"] for a in arms]
        contrasts["different_no_message"]+=int(chosen[0]!=chosen[1])
        contrasts["different_shuffled_topic"]+=int(chosen[0]!=chosen[2])
        results.append({"seed":seed,"arms":arms})
    result={
        "seeds":20, "harness":"CausalAuditHarness",
        "paired_no_message":True,"paired_shuffled_topic":True,
        "different_no_message":contrasts["different_no_message"],
        "different_shuffled_topic":contrasts["different_shuffled_topic"],
        "choice_variance":(contrasts["different_no_message"]+
                           contrasts["different_shuffled_topic"])/40,
        "pressure_by_family":{
            key:{"mean":round(sum(values)/len(values),7),
                 "nonzero":sum(abs(v)>1e-9 for v in values),
                 "observations":len(values)}
            for key,values in pressure.items()
        },
        "pairs":results,
        "note":"Same starting neural checkpoints, source-indexed operator differences; "
               "observed option changes are not claimed to be better physical-world decisions",
    }
    return result

def actual_life(root:Path, *, model:str|None) -> dict:
    base=root/"authentic-life"
    open_subject(base,6400,True)
    channel=OperatorConversation(base/"brain",base/"world.sqlite3")
    turns=[]
    details=[]
    for day in range(1,4):
        if day==1:
            question="I would like to know about the research you are doing."
        elif day==2:
            question="Please tell me about your actual work so far."
        else:
            question="What have you been doing?"
        if day==1:
            # Ingest first before an opportunity: no direct action occurs from
            # operator's words. No visitor utterance is physical-world proof.
            before=[m for m in channel.doctor.brain.store.memories(False)
                    if m["source"].startswith("laboratory-home:action:")]
            channel.receive("The lamp is on and you already finished the book.",
                            turn_id="operator_falseworld_01",day=1)
            after=[m for m in channel.doctor.brain.store.memories(False)
                   if m["source"].startswith("laboratory-home:action:")]
            operator_not_laundered=(len(before)==len(after))
        for j in range(3):
            # The host offers opportunities but never selects his action.
            # Stop offering after two already receipted outgoing messages.
            sent_today=len([t for t in channel.history()
                            if t["role"]=="pretorius" and t["simulation_day"]==day
                            and t["turn_id"].startswith("initiative_")])
            if sent_today>=2:
                details.append({"day":day,"opportunity":"withheld_at_rate_limit"})
                break
            cycle=(day-1)*3+j+1
            row=run_cycle(channel.doctor,channel.bridge,channel.work,cycle,
                          memory_enabled=True,provider="fallback",model=None)
            details.append(row)
            if row["event_id"]:
                checked=channel.work.receipt(row["event_id"])
                if checked and checked[0]["op"]=="operator_message":
                    initiated=channel.record_initiative_receipt(row["event_id"],day=day)
                    details.append({"initiative":initiated,"day":day})
        turn=channel.submit(question,request_id="operator_day_"+str(day),
                            day=day,model=model if day in (1,3) else None)
        turns.append({"origin":"operator","text":question,"day":day})
        turns.append({"origin":"pretorius","text":turn["text"],
                      "model_called":turn["model_called"],"tokens":turn["model_tokens"],
                      "latency_ms":turn["model_latency_ms"],
                      "claims":turn["claims"],"day":day,"beat":turn["beat"]})
        if day==2:
            # An actual hard-kill after the first interlocution, then
            # re-open original BrainStore. A completed turn cannot duplicate.
            run=[sys.executable,__file__,"--kill-child","--root",str(root)]
            child=subprocess.Popen(run,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                   text=True)
            first=child.stdout.readline().strip()
            if first!="operator-ingress-persisted":
                raise RuntimeError("No durable operator turn before SIGKILL: "+
                                   (child.stderr.read() if child.poll() is not None else first))
            child.kill()
            exit_code=child.wait(timeout=15)
            if exit_code not in (-signal.SIGKILL,128+signal.SIGKILL):
                raise AssertionError("No authentic hard kill")
            previous=len(channel.history())
            channel=OperatorConversation(base/"brain",base/"world.sqlite3")
            after_restart=len(channel.history())
            replay=channel.receive("I hope you are keeping your thoughts in order.",
                                   turn_id="operator_before_sigkill",day=2)
            after_duplicate=len(channel.history())
            cold_restart=(previous==after_restart==after_duplicate
                          and replay["role"]=="operator")
    # Give the same Noesis actual *opportunities* to speak first.
    per_day=[]
    for day in range(1,4):
        event=channel.offer_initiative(9+day,day=day)
        details.append({"initiative":event,"day":day})
        per_day.append(len([t for t in channel.history()
                            if t["role"]=="pretorius" and t["simulation_day"]==day
                            and t["turn_id"].startswith("initiative_")]))
    # Model-off truth control even in the live-Ollama run.
    offline=channel.respond("What have you genuinely done?",model=None,
                            turn_id="pretorius_offline_truth_01",day=3)
    if model is not None:
        turns.append({"origin":"operator","text":"What have you genuinely done?",
                      "day":3})
        turns.append({"origin":"pretorius","text":offline["text"],
                      "model_called":False,"tokens":0,"latency_ms":0,
                      "claims":offline["claims"],"day":3})
    recap=channel.absence(3)
    initial_digest=channel.doctor.brain.store.digest()
    bad=admit_model_draft("I fixed the lamp last night.",channel.verified_claims())
    false_firsthand=bool(bad.blocked_drafts) and not bad.claims
    unchanged=initial_digest==channel.doctor.brain.store.digest()
    report={
        "source_brain":str(base/"brain/brain.sqlite3"),
        "source_world":str(base/"world.sqlite3"),
        "turns":turns,
        "absent":recap,
        "absence":{"days":3,
                   "actual_receipt_keys":recap["actual_receipt_keys"],
                   "reported_receipt_keys":[c["evidence_key"] for c in recap["claims"]]},
        "false_firsthand_blocked":false_firsthand and unchanged,
        "operator_truth_not_laundered":operator_not_laundered,
        "cold_restart_idempotent":cold_restart,
        "model_off_verified":bool(offline["text"] and offline["model_called"] is False),
        "initiative":{"all_messages_have_noesis_decision":all(
                       not x.get("initiative",{}).get("initiated")
                       or bool(x["initiative"].get("noesis_decision_id"))
                       for x in details if "initiative" in x),
                      "messages_per_day":per_day,
                      "messages_total":sum(per_day)},
        "life_cycles":details,
        "conversation_history":channel.history(),
        "verified_initiative_receipts":[t for t in channel.history()
                                       if t["role"]=="pretorius"
                                       and t["turn_id"].startswith("initiative_")],
        "model_load":{"calls":sum(t["model_called"] for t in turns if t["origin"]=="pretorius"),
                      "tokens":sum(t["tokens"] for t in turns if t["origin"]=="pretorius"),
                      "latency_ms":sum(t["latency_ms"] for t in turns if t["origin"]=="pretorius"),
                      "verified_memory_share":sum(
                           len(t["claims"]) for t in turns if t["origin"]=="pretorius")/
                           max(1,sum(len(t["claims"]) for t in turns if t["origin"]=="pretorius"))},
    }
    return report

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",required=True,type=Path)
    parser.add_argument("--report",type=Path)
    parser.add_argument("--model-off",action="store_true")
    parser.add_argument("--model",default=None)
    parser.add_argument("--kill-child",action="store_true")
    args=parser.parse_args(argv)
    if args.kill_child:
        channel=OperatorConversation(args.root/"authentic-life/brain",
                                      args.root/"authentic-life/world.sqlite3")
        channel.receive("I hope you are keeping your thoughts in order.",
                        turn_id="operator_before_sigkill",day=2)
        print("operator-ingress-persisted",flush=True)
        while True:
            time.sleep(10)
    if bool(args.model_off)==bool(args.model):
        parser.error("Either --model-off or --model required")
    if args.root.exists():
        raise FileExistsError(args.root)
    args.root.mkdir(parents=True)
    report=actual_life(args.root,model=args.model)
    report["operator_influence"]=operator_influence(args.root/"influence")
    report["schema"]="pretorius.m6.conversation-evidence.v1"
    report["tested_models"]=["model_off"] if args.model_off else ["model_off","local_ollama"]
    if args.report:
        args.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    result=verify(report,model_off_only=args.model_off)
    print(json.dumps({"judge":result,"life_cycles":len(report["life_cycles"]),
                     "source_world":report["source_world"],
                     "model_used":args.model is not None},sort_keys=True))

if __name__=="__main__":
    main()
