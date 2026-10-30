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
        no_bonus=max(cs,key=lambda k:(cs[k]["total"]-cs[k]["novelty"],cs[k]["tie_key"]))
        changed+=int(row["selected_proposal_id"]!=no_bonus)
        scored+=1

    native_changed=0
    open_changed=0
    open_case_traces=[]
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

            # Additional same-source candidate replay. These are the last
            # originally proposed free-language options, not host-authored
            # action labels. We make one new genuine native Noesis decision
            # under intact versus neutralized recurrent state, independently
            # from the older generic cognitive-probe comparison. No motor
            # authorization or Laboratory action is issued here.
            from doctor_lives.chassis import PretoriusBrainPort
            from doctor_lives.organs import NoesisOrgan
            with __import__("sqlite3").connect(root/f"seed-{seed}"/"brain"/"brain.sqlite3") as db:
                audited=db.execute(
                    "SELECT state_pressure_json FROM policy_decisions "
                    "WHERE trigger='noesis_open_choice' ORDER BY rowid DESC LIMIT 1").fetchone()
            if audited is None:
                raise ValueError("Missing exact original open-intention proposal set")
            original_audit=json.loads(audited[0])
            components=original_audit.get("contributions")
            if not isinstance(components,dict) or not components:
                raise ValueError("No source-stored proposal contributions for lesion")
            candidates=[]
            for condition in ("open-intact","open-recurrence-neutral"):
                clone=obj._clone_seed(f"{condition}-{seed}")
                port=PretoriusBrainPort(clone)
                if condition=="open-recurrence-neutral":
                    FullRecurrentWeightAudit._apply_static_lesions(
                        port.brain,{"recurrent_policy"})
                NoesisOrgan(port).deliberate(host_trigger="m5_recurrent_counterfactual")
                scores=port.brain.neural.action_scores()
                if any(c["tendency"] not in scores for c in components.values()):
                    raise ValueError("Invalid semantic category at native Noesis boundary")
                ranked={}
                for pid,c in components.items():
                    ranked[pid]=(float(scores[c["tendency"]])+
                                 float(c["familiarity"])+float(c["novelty"])+
                                 float(c["history"])+
                                 sum(float(v) for v in c.get("donor_components",{}).values()))
                chosen=max(ranked,key=lambda pid:(ranked[pid],components[pid]["tie_key"]))
                candidates.append(chosen if ranked[chosen]>0.01 else None)
            open_changed+=int(candidates[0]!=candidates[1])
            open_case_traces.append({"seed":seed,"intact_proposal_id":candidates[0],
                                     "neutralized_proposal_id":candidates[1],
                                     "changed":candidates[0]!=candidates[1]})
    return {"schema":"pretorius.m5-attribution.v1","decisions":rows,
            "summary":{"selections_with_proposal_scores":scored,
                       "novelty_removed_choice_flips":changed},
            "recurrent_lesion":{"executed_with_causal_audit_harness":True,
                                "seeds":20,
                                "recurrent_weights_neutralized":True,
                                "native_cognitive_choice_flips":native_changed,
                                "native_policy_score_l1_mean":sum(score_l1)/20,
                                "recorded_proposal_replay_choice_flips":open_changed,
                                "recorded_proposal_replay_trials":open_case_traces,
                                "note":"The native lesion and recorded-proposal replay are cloned-state causal probes, NOT new physical-world outcome trials."}}

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
