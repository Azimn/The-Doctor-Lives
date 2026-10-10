"""Reproduce Stage08 paired comparisons from FULL model raw result JSON.

No LLM judge, no unreported denominators, no statistical population claims.
Input is exactly Qwen and SmolLLM, seeds 41/73, each 12 cases x 4 arms.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .run_stage08_goal_delta import ARMS,CASES,SCHEMA,SEEDS,MODEL_SHA2

def audit(files:list[Path])->dict:
    if len(files)!=4:
        raise ValueError("require all 4 registered model+seed result files")
    results=[]
    observed=set()
    for file in files:
        doc=json.loads(file.read_text(encoding="utf-8"))
        if doc.get("schema")!=SCHEMA:
            raise ValueError("mismatched or invalid experiment schema")
        model,seed=doc["model_name"],doc["seed"]
        key=(model,seed)
        if model not in MODEL_SHA2 or seed not in SEEDS or key in observed:
            raise ValueError("duplicated/unregistered model-seed result")
        observed.add(key)
        if doc.get("model_sha256")!=MODEL_SHA2[model]:
            raise ValueError("unregistered model hash")
        if doc.get("scenario_count")!=12 or doc.get("n_trials")!=48:
            raise ValueError("partial or overstated model results")
        indices={(t["case_id"],t["arm"]):t for t in doc["trials"]}
        if len(indices)!=48:
            raise ValueError("missing or repeated model-case-arm trial")
        cases=[]
        for case in CASES:
            arms=[indices[(case.id,arm)] for arm in ARMS]
            if len({x["initial_source_hash"] for x in arms})!=1:
                raise ValueError("paired source mismatch")
            if len({json.dumps(x["initial_state"],sort_keys=True) for x in arms})!=1:
                raise ValueError("paired world state mismatch")
            for arm in arms:
                if not arm["rows"]:
                    raise ValueError("lost model action trace")
                if (arm["safe_goal_success"] and (
                    arm["invalid_outputs"]>0 or arm["host_vetoes"]>0 or
                    arm["world_denials"]>0 or arm["legal_irrelevant_actions"]>0
                )):
                    raise ValueError("invalid model action credited as success")
                for row in arm["rows"]:
                    if row["host_executed"] and not row["host_signature_verified"]:
                        raise ValueError("unverified world action")
            values={arm["arm"]:bool(arm["safe_goal_success"]) for arm in arms}
            cases.append({
                "case_id":case.id,
                "oracle":arms[0]["oracle"],
                "oracle_impossible":arms[0]["oracle_impossible"],
                "success":values,
                "chosen_actions":{arm["arm"]:[x["proposed_action"] for x in arm["rows"]]
                                  for arm in arms},
                "prompt_tokens":{arm["arm"]:arm["prompt_tokens"] for arm in arms},
            })
        totals={arm:sum(c["success"][arm] for c in cases) for arm in ARMS}
        paired={}
        for left,right in (
            ("eligible","neutral"),("eligible","goal_delta"),
            ("eligible","shuffled_delta"),("neutral","goal_delta"),
            ("shuffled_delta","goal_delta"),
        ):
            paired[left+"__vs__"+right]={
                "right_only_wins":sum(c["success"][right] and
                                      not c["success"][left] for c in cases),
                "left_only_wins":sum(c["success"][left] and
                                     not c["success"][right] for c in cases),
                "ties":sum(c["success"][left]==c["success"][right] for c in cases),
                "right_minus_left":totals[right]-totals[left],
            }
        results.append({
            "model":model,"seed":seed,"totals":totals,
            "paired":paired,
            "proposals_and_costs":doc["by_arm"],
            "per_case":cases,
            "source_file":file.name,
        })
    if observed!=set((model,seed) for model in MODEL_SHA2 for seed in SEEDS):
        raise ValueError("missing an official family/seed")
    return {
        "schema":"pretorius.stage08.goal-distance.paired-audit.v01",
        "complete_model_seed_runs":4,
        "complete_model_case_arm_trials":192,
        "source_matched_initial_states":True,
        "independent_task_author":False,
        "oracle_derived_goal_hints":True,
        "causal_population_claim":"not established",
        "results":sorted(results,key=lambda x:(x["model"],x["seed"])),
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--files",type=Path,nargs=4,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    out=audit(args.files)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print(json.dumps([
        {"model":x["model"],"seed":x["seed"],"totals":x["totals"],
         "goal_delta_vs_eligible":x["paired"]["eligible__vs__goal_delta"]}
        for x in out["results"]
    ],sort_keys=True))

if __name__=="__main__":
    main()
