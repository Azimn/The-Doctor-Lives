"""M6 donor-call measurement, including actual original-Lab eligibility scenarios.

The observed historical 0/180 M5 outcome is explicitly NOT a negative if
the donor-specific code was never eligible. Separate test-only targeted
scenarios exercise the source-backed constraints without making donor-on a
shipping default or asserting better world outcomes.
"""
from __future__ import annotations
from collections import Counter
import json
import os
from pathlib import Path
import tempfile

from doctor_lives.m5_donors import DONORS,contributions
from doctor_lives.m5_home_feasibility import physically_available
from doctor_lives.open_inference import InferencePort
from doctor_lives.open_intentions import propose_intentions,noesis_open_choice,authorized_open_action
from scripts.run_m4_open import open_subject,run_cycle

class JournalOnlyFixture(InferencePort):
    def propose(self, context):
        return [
            "I might append an observation to my daily journal.",
            "I wish I could visit a remote village.",
            "I would like to sail across the ocean.",
        ]

def run(out: Path):
    counts={name:Counter() for name in DONORS}
    decisions=[]
    with tempfile.TemporaryDirectory(prefix="m6-donor-coverage-") as tmp:
        root=Path(tmp)
        doc,bridge,work=open_subject(root/"subject",6900,True)
        old=os.environ.get("PRETORIUS_M5_DONORS")
        os.environ["PRETORIUS_M5_DONORS"]=",".join(DONORS)
        try:
            for cycle in range(1,19):
                result=run_cycle(doc,bridge,work,cycle,
                                 memory_enabled=True,provider="fallback",model=None)
                with doc.brain.store.connect() as db:
                    row=db.execute("SELECT state_pressure_json FROM policy_decisions WHERE id=?",
                                   (result["decision_id"],)).fetchone()
                    audit=json.loads(row[0])
                observed={}
                for name in DONORS:
                    records=[c["donor_trace"][name]
                             for c in audit["contributions"].values()]
                    called=any(r["entered"] for r in records)
                    eligible=any(r["eligible"] for r in records)
                    score=sum(float(r["contribution"]) for r in records)
                    counts[name]["decisions"]+=1
                    counts[name]["path_entered_decisions"]+=int(called)
                    counts[name]["eligible_decisions"]+=int(eligible)
                    counts[name]["nonzero_score_decisions"]+=int(score!=0)
                    observed[name]={"entered":called,"eligible":eligible,
                                    "score":round(score,6)}
                decisions.append({"cycle":cycle,"policy_id":result["decision_id"],
                                  "source_action":result["event_id"],"donors":observed})
        finally:
            if old is None: os.environ.pop("PRETORIUS_M5_DONORS",None)
            else: os.environ["PRETORIUS_M5_DONORS"]=old

        # Controlled direct adapter invocation is a *coverage* fixture, not
        # a real autonomous physical task or measured policy improvement.
        doc.brain.add_commitment("append observation to daily journal")
        journal={"text":"I might append an observation to my daily journal."}
        cap={"goal_type":"journal","affordance_key":"daily_journal"}
        trace={}
        commitment=contributions(bridge,work,journal,cap,19,
                                 ("cascade_commitments",),audit=trace)
        assert trace["cascade_commitments"]["entered"]
        assert trace["cascade_commitments"]["eligible"]
        assert commitment["cascade_commitments"]>0

        # Actual Lab-owned home state, actual station, unchanged pure donor.
        state=bridge.subject.rhythm.audit_state()
        station=bridge.subject.embodied.verify()["station"]
        feasible=physically_available(state,station)["available"]
        if not feasible:
            raise AssertionError("Laboratory provided no feasible household task")
        task=sorted(feasible)[0]
        homecap={"goal_type":"household","affordance_key":task}
        hometrace={}
        household=contributions(bridge,work,{"text":"I might "+task},
                                homecap,19,("household_grounded",),audit=hometrace)
        assert hometrace["household_grounded"]["entered"]
        assert hometrace["household_grounded"]["eligible"]
        assert household["household_grounded"]==0.0  # Hard preflight, no selector bonus.

        # Legitimate operator-work receipts from the 18 actual original-Noesis
        # cycles. Even if repeated receipts are unavailable, the verification
        # path is exercised and its bounded null is not called an advantage.
        source_caps=work.affordances(19)
        habit_results=[]
        for item in source_caps:
            trace={}
            answer=contributions(bridge,work,journal,item,19,
                                 ("household_habit",),audit=trace)
            habit_results.append({"key":item["affordance_key"],
                                  "called":trace["household_habit"]["entered"],
                                  "eligible":trace["household_habit"]["eligible"],
                                  "score":answer["household_habit"]})
        assert habit_results and all(row["called"] for row in habit_results)
        targeted={
            "cascade_commitments":{"entered":True,"eligible":True,
                                   "score":commitment["cascade_commitments"],
                                   "fixture":"canonical open commitment"},
            "household_grounded":{"entered":True,"eligible":True,"score":0.0,
                                   "fixture":"verified physical station and pure preflight",
                                   "feasible_task":task},
            "household_habit":{"entered":True,
                               "eligible":any(row["eligible"] for row in habit_results),
                               "fixture":"actual receipted original Noesis operator work",
                               "candidates":habit_results},
        }
    report={
        "schema":"pretorius.m6.donor-path-coverage.v1",
        "observed_decisions":decisions,
        "counts":{name:dict(c) | {
            "coverage":c["path_entered_decisions"]/max(1,c["decisions"]),
            "historical_zero_is_untested":c["path_entered_decisions"]<0.1*c["decisions"],
        } for name,c in counts.items()},
        "targeted_source_scenarios":targeted,
        "interpretation":"Path execution is not proof of outcome improvement. "
           "A zero score with under-10-percent donor eligibility is untested, "
           "not a negative demonstration. All donors remain OFF by default.",
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({key:report[key] for key in (
        "schema","counts","targeted_source_scenarios","interpretation")},sort_keys=True))
    return report

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    run(args.out)
