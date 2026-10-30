"""M5 three-donor 20-seed matched source/Noesis counterfactual audit.

This is an opt-in, non-actuating test, not evidence that a donor improved
physical outcomes. It clones the ORIGINAL saved BrainStore with
CausalAuditHarness and compares the exact same stored proposals and world
affordances under donor-on/off and equal-information cheap rankings.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile

from doctor_lives.causal_audit import CausalAuditHarness
from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.open_lab_bridge import OperatorWork
from doctor_lives.m5_donors import DONORS,contributions

def _choice(scores, tie_keys, threshold=0.01):
    if not scores:
        return None
    name=max(scores,key=lambda k:(scores[k],tie_keys[k]))
    return name if scores[name]>threshold else None

def audit_one(root:Path,seed:int,work_root:Path):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.subject_port import SubjectPort
    subject=root/f"seed-{seed}"
    harness=CausalAuditHarness(subject/"brain",work_root/str(seed))
    roots=[harness._clone_seed("source-off"),harness._clone_seed("candidate-on")]
    pairs=[]
    for root_state in roots:
        port=PretoriusBrainPort(root_state)
        bridge=DoctorHomeBridge(port,SubjectPort(SpatialHabitat(subject/"world.sqlite3")),authorized=True)
        work=OperatorWork(bridge)
        pairs.append((port,bridge,work))
    if pairs[0][0].brain.store.digest()!=pairs[1][0].brain.store.digest():
        raise AssertionError("Donor ablation not derived from identical original BrainStore")
    with pairs[0][0].brain.store.connect() as db:
        decisions=[dict(r) for r in db.execute(
            "SELECT id,state_pressure_json FROM policy_decisions WHERE trigger='noesis_open_choice' ORDER BY rowid")]
        proposals={r["proposal_id"]:dict(r) for r in db.execute("SELECT * FROM open_proposals")}
    if len(decisions)<9:
        raise ValueError("Missing actual original M4 Noesis policy cohort")
    counts={n:Counter() for n in DONORS}
    for d in decisions:
        off=json.loads(d["state_pressure_json"])
        original_scores={k:float(v) for k,v in off["candidate_scores"].items()}
        on_context=off.get("contributions") or {}
        if set(original_scores)!=set(on_context):
            raise ValueError("Original decision lacks complete neural/novelty evidence")
        stable_keys={k:v["tie_key"] for k,v in on_context.items()}
        off_selected=_choice(original_scores,stable_keys)
        if off_selected!=off.get("selected_proposal_id"):
            raise ValueError("Reconstructed existing Noesis choice differs from source")
        simple={p:(float(c["familiarity"])+float(c["novelty"])+float(c["history"]))
                for p,c in on_context.items()}
        simple_selected=_choice(simple,stable_keys,threshold=-1.0)
        cycle=proposals[next(iter(original_scores))]["cycle"]
        current={c["affordance_key"]:c for c in pairs[1][2].affordances(cycle)}
        for donor in DONORS:
            adjusted=dict(original_scores)
            for pid in adjusted:
                proposal=proposals[pid]
                cap=current.get(proposal["affordance_key"])
                if cap is not None:
                    add=contributions(pairs[1][1],pairs[1][2],proposal,cap,cycle,(donor,))
                    adjusted[pid]+=add[donor]
            adjusted_selected=_choice(adjusted,stable_keys)
            counts[donor]["recorded_decisions"]+=1
            counts[donor]["on_off_choice_flips"]+=int(adjusted_selected!=off_selected)
            counts[donor]["off_simple_disagreements"]+=int(off_selected!=simple_selected)
            counts[donor]["on_simple_disagreements"]+=int(adjusted_selected!=simple_selected)
    return counts

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    total={name:Counter() for name in DONORS}
    with tempfile.TemporaryDirectory(prefix="m5-harvest-") as d:
        for seed in range(6400,6420):
            partial=audit_one(args.run,seed,Path(d))
            for donor,values in partial.items():
                total[donor].update(values)
    result={"schema":"pretorius.m5-donor-counterfactual.v1",
            "seeds":20,"source":"canonical M4 Noesis policies with CausalAuditHarness cloned stores",
            "actuating":False,
            "outcome_claim":"unresolved; counterfactual choices are not independent task successes",
            "donors":{d:dict(v) for d,v in total.items()},
            "verdict":{d:"LEAVE_OFF, no proved improvement over equal-information simple controller"
                       for d in DONORS}}
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    main()
