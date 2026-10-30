"""Independent M5 attribution from saved original BrainStore and cloned neural states.

No live-world action is performed by this script. The original 20 seeded
brains are cloned by CausalAuditHarness; the lesion zeros the recurrent
weights AND their motor readout in the cloned research condition.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sqlite3
import tempfile
from doctor_lives import Experience
from doctor_lives.causal_audit import CausalAuditHarness, AuditIntervention

class FullRecurrentWeightAudit(CausalAuditHarness):
    @staticmethod
    def _apply_static_lesions(brain, disabled):
        CausalAuditHarness._apply_static_lesions(brain, disabled)
        if "recurrent_policy" in disabled:
            brain.neural.W.data.fill(0.0)
            brain.save()

def collect(root: Path):
    rows=[]
    for seed in range(6400,6420):
        db=root/f"seed-{seed}"/"brain"/"brain.sqlite3"
        if not db.is_file():
            raise FileNotFoundError(f"Missing independently seeded original brain {seed}")
        with sqlite3.connect(db) as con:
            policies=con.execute(
                "SELECT id,state_pressure_json FROM policy_decisions WHERE trigger='noesis_open_choice' ORDER BY rowid"
            ).fetchall()
        if not policies:
            raise ValueError(f"No actual open selection rows for seed {seed}")
        for policy_id,raw in policies:
            audit=json.loads(raw)
            if audit.get("selector_authority")!="original_noesis":
                raise ValueError("Non-original selector cannot enter attribution")
            rows.append({"seed":seed,"policy_id":policy_id,
                         "selected_proposal_id":audit.get("selected_proposal_id"),
                         "contributions":audit.get("contributions")})
    if len(rows)<160:
        raise ValueError("Attribution needs a full 20-seed trial cohort")
    scored=0
    changed=0
    for row in rows:
        cs=row["contributions"]
        if not isinstance(cs,dict) or not cs:
            continue
        no_bonus=max(cs,key=lambda k:(cs[k]["total"]-cs[k]["novelty"],k))
        changed+=int(row["selected_proposal_id"]!=no_bonus)
        scored+=1

    native_changed=0
    score_l1=[]
    with tempfile.TemporaryDirectory(prefix="m5-recurrent-audit-") as work:
        for seed in range(6400,6420):
            obj=FullRecurrentWeightAudit(root/f"seed-{seed}"/"brain",Path(work)/str(seed))
            probe=Experience(
                "I have completed a task, and I am considering another experiment.",
                kind="observation",novelty=0.3,achievement=0.5)
            row=obj.run_pair(probe,AuditIntervention(
                "recurrent_policy",("recurrent_policy",)))
            native_changed+=int(row["comparison"]["selected_action_diverged"])
            score_l1.append(float(row["comparison"]["action_score_l1"]))
    return {"schema":"pretorius.m5-attribution.v1","decisions":rows,
            "summary":{"selections_with_proposal_scores":scored,
                       "novelty_removed_choice_flips":changed},
            "recurrent_lesion":{"executed_with_causal_audit_harness":True,
                                "seeds":20,
                                "recurrent_weights_neutralized":True,
                                "native_cognitive_choice_flips":native_changed,
                                "native_policy_score_l1_mean":sum(score_l1)/20,
                                "note":"This lesion measures native cognition on cloned states; no claim of M5 action-choice flip is inferred without a paired open-intention rollout."}}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--run",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=collect(a.run)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2))
    print(json.dumps({**report["summary"],"recurrent_lesion":report["recurrent_lesion"]},sort_keys=True))

if __name__=="__main__":
    main()
