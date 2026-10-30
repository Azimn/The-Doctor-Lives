"""Generate source-backed M4 multi-day, multi-seed Laboratory evidence.

The harness can schedule opportunities and introduce a data-only affordance.
It cannot name the next action. An Ollama proposer can speak, but Noesis alone
selects; all operations still need bridge authorization and physical receipts.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.open_lab_bridge import OperatorWork
from doctor_lives.open_inference import make_inference
from doctor_lives.open_intentions import (propose_intentions,noesis_open_choice,
                                          authorized_open_action)
from scripts.verify_open import SCHEMA,LAB_PIN,verify

def config(seed):
    cfg=dict(DEFAULT_CONFIG)
    cfg.update(neurons=128,sensory_dim=64,avg_recurrent_degree=8,
               input_degree=4,action_population_size=8,seed=seed)
    return cfg

def open_subject(folder, seed, new):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.book_library import BookLibrary
    from pretorius_lab.subject_port import SubjectPort
    folder=Path(folder)
    if new:
        folder.mkdir(parents=True,exist_ok=False)
        world=SpatialHabitat.create(folder/"world.sqlite3")
        HomeLife(world).initialize()
        DailyRhythm(world).initialize()
        BookLibrary(world).initialize()
        doctor=PretoriusBrainPort(folder/"brain",neural_config=config(seed))
    else:
        world=SpatialHabitat(folder/"world.sqlite3")
        doctor=PretoriusBrainPort(folder/"brain")
    bridge=DoctorHomeBridge(doctor,SubjectPort(world),authorized=True)
    work=OperatorWork(bridge)
    return doctor,bridge,work

def run_cycle(doctor,bridge,work,cycle,*,memory_enabled,provider,model):
    inferred=make_inference(provider,model=model)
    proposed=propose_intentions(bridge,work,inferred,cycle,memory_enabled=memory_enabled)
    chosen=noesis_open_choice(bridge,work,proposed,cycle,memory_enabled=memory_enabled)
    executed=authorized_open_action(bridge,work,chosen,cycle)
    doctor.save()
    return {"cycle":cycle,"day":f"day-{1+(cycle-1)//3}",
            "proposal_ids":[p["proposal_id"] for p in proposed],
            "selected_proposal_id":chosen["selected_proposal_id"],
            "decision_id":chosen["decision_id"],
            "event_id":executed["event_id"] if executed else None}

def wishes(brain):
    with brain.brain.store.connect() as db:
        return [r[0] for r in db.execute(
            "SELECT proposal_id FROM open_wishes WHERE status='unfulfilled' ORDER BY proposal_id"
        )]

def run_child(folder,seed,phase,memory_enabled,provider,model):
    if phase=="start":
        doc,bridge,work=open_subject(folder,seed,True)
        initial=run_cycle(doc,bridge,work,1,memory_enabled=memory_enabled,
                          provider=provider,model=model)
        pending=wishes(doc)
        if not pending:
            raise RuntimeError("The subject failed to retain any unfulfilled desires")
        print(json.dumps({"status":"ready","pid":os.getpid(),
                          "cycle":initial,"wishes":pending}),flush=True)
        while True:
            time.sleep(5)
    if phase=="resume":
        doc,bridge,work=open_subject(folder,seed,False)
        pending=wishes(doc)
        if not pending:
            raise RuntimeError("Cold restore did not preserve the first-person unfulfilled wish")
        # Registry change is data, not code. This capability was absent from
        # the model's first prompt and all previous host opportunities.
        work.register("archive_findings","append a finding to the newly opened archive",
                      "append_journal","archive.txt","archive",
                      introduced_cycle=2)
        cycles=[]
        for tick in range(2,10):
            row=run_cycle(doc,bridge,work,tick,memory_enabled=memory_enabled,
                          provider=provider,model=model)
            cycles.append(row)
        print(json.dumps({"status":"completed","pid":os.getpid(),
                          "wishes":pending,"cycles":cycles}),flush=True)
        return

def run_pair(root,seed,*,provider,model):
    folder=root/f"seed-{seed}"
    cmd=[sys.executable,__file__,"--child","start","--subject",str(folder),
         "--seed",str(seed),"--provider",provider]
    if model:cmd+=["--model",model]
    started=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    first_line=started.stdout.readline()
    if not first_line:
        try:err=started.stderr.read()
        except OSError:err="unknown"
        raise RuntimeError("First subject died before creating goal: "+err)
    first=json.loads(first_line)
    if first.get("status")!="ready" or first["pid"]!=started.pid:
        raise RuntimeError("First process did not persist original wishes")
    started.kill()
    code=started.wait(timeout=15)
    if code not in (-signal.SIGKILL,128+signal.SIGKILL):
        raise RuntimeError("No genuine hard kill")
    next_cmd=[sys.executable,__file__,"--child","resume","--subject",str(folder),
              "--seed",str(seed),"--provider",provider]
    if model:next_cmd+=["--model",model]
    after=subprocess.run(next_cmd,capture_output=True,text=True,timeout=240)
    if after.returncode:
        raise RuntimeError("Cold restore failed: "+after.stderr[-4000:])
    second=json.loads(after.stdout)
    if second.get("status")!="completed" or second["pid"]==first["pid"]:
        raise RuntimeError("No different successfully restarted subject process")
    meta={"seed":seed,"lab_pin":LAB_PIN,"memory_enabled":True,
          "cycles":[first["cycle"]]+second["cycles"],
          "prompted_before_novelty":False,
          "novelty":{"key":"archive_findings","introduced_cycle":2},
          "restart":{"signal":"SIGKILL","pid_before":first["pid"],
                     "pid_after":second["pid"],
                     "wishes_before":first["wishes"],"wishes_after":second["wishes"]}}
    (folder/"trial.json").write_text(json.dumps(meta,sort_keys=True,indent=2))
    return folder

def run_lesion(root,seed,*,provider,model):
    folder=root/f"lesion-{seed}"
    doc,bridge,work=open_subject(folder,seed,True)
    cycles=[]
    for c in range(1,10):
        if c==2:
            work.register("archive_findings","append a finding to the newly opened archive",
                          "append_journal","archive.txt","archive",
                          introduced_cycle=2)
        cycles.append(run_cycle(doc,bridge,work,c,memory_enabled=False,
                                provider=provider,model=model))
    (folder/"trial.json").write_text(json.dumps({
        "seed":seed,"memory_enabled":False,"cycles":cycles
    },sort_keys=True))
    return folder

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",type=Path)
    parser.add_argument("--lab-root",type=Path)
    parser.add_argument("--provider",choices=("ollama","fallback"),default="fallback")
    parser.add_argument("--model",default=None)
    parser.add_argument("--child",choices=("start","resume"))
    parser.add_argument("--subject",type=Path)
    parser.add_argument("--seed",type=int,default=6400)
    args=parser.parse_args(argv)
    if args.child:
        if not args.subject:
            parser.error("--subject required for child")
        run_child(args.subject,args.seed,args.child,True,args.provider,args.model)
        return 0
    if args.run is None or args.lab_root is None:
        parser.error("--run and --lab-root required")
    root=args.run
    root.mkdir(parents=True,exist_ok=False)
    trials=[]
    for n in range(20):
        seed=6400+n
        run_pair(root,seed,provider=args.provider,model=args.model)
        run_lesion(root,seed,provider="fallback",model=None)
        trials.append({"seed":seed,"path":f"seed-{seed}",
                       "ablation_path":f"lesion-{seed}"})
    # The old deterministic offline M2 day MUST independently pass M2's
    # UNCHANGED complete source-backed day judge with no model loaded.
    fallback=root/"fallback-day"
    command=[sys.executable,"scripts/run_m2_day.py","--run",str(fallback),
             "--lab-root",str(args.lab_root)]
    completed=subprocess.run(command,capture_output=True,text=True,timeout=300)
    if completed.returncode:
        raise RuntimeError("Original M2 model-off regression failed: "+completed.stderr[-4000:])
    bundle={"schema":SCHEMA,"lab_pin":LAB_PIN,"provider":args.provider,
            "remote_calls":0,"trials":trials,"fallback_day":"fallback-day"}
    (root/"open.json").write_text(json.dumps(bundle,sort_keys=True,indent=2))
    result=verify(root,args.lab_root)
    (root/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2))
    print(json.dumps(result,sort_keys=True,indent=2))
    return int(not result["pass"])

if __name__=="__main__":
    sys.exit(main())
