"""Audit Stage05 matched, world-observed model outcomes without LLM quality rating.

The case bank is researcher-written and not an independent random sample.
Paired counts here are descriptive; do not infer population significance.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .run_phase_world_decisions_stage05 import CASES,SCHEMA


def audit(data:dict)->dict:
    if data.get("schema")!=SCHEMA:
        raise ValueError("unexpected Stage05 output schema")
    if data.get("n_scenarios")!=12 or data.get("n_arm_runs")!=24:
        raise ValueError("incomplete case/arm coverage")
    if len(data["results"])!=24:
        raise ValueError("incomplete raw trials")
    indexed={(x["scenario"],x["arm"]):x for x in data["results"]}
    if len(indexed)!=24:
        raise ValueError("duplicate conditions")
    pairs=[]
    for case in CASES:
        a=indexed[(case.id,"flat_current")]
        b=indexed[(case.id,"phase_current")]
        if not a["decisions"] or not b["decisions"]:
            raise ValueError("missing model actions")
        if (a["decisions"][0]["source_evidence_only_sha256"]!=
            b["decisions"][0]["source_evidence_only_sha256"]):
            raise ValueError("initial source content not equal across paired arms")
        if a["first_observation_world"]!=b["first_observation_world"]:
            raise ValueError("paired initial world-state mismatch")
        if any(not x["all_attested_world_results_sourced"] for x in (a,b)):
            raise ValueError("host event imported without verified source")
        pairs.append({
            "case_id":case.id,
            "oracle":list(a["oracle_plan"]),
            "flat_goal":a["safe_goal_success"],
            "phase_goal":b["safe_goal_success"],
            "flat_choices":list(a["selected_actions"]),
            "phase_choices":list(b["selected_actions"]),
            "flat_denials":a["world_denied_actions"],
            "phase_denials":b["world_denied_actions"],
            "flat_invalid":a["any_failed_action_parse"],
            "phase_invalid":b["any_failed_action_parse"],
        })
    both=sum(x["flat_goal"] and x["phase_goal"] for x in pairs)
    phase_only=sum(x["phase_goal"] and not x["flat_goal"] for x in pairs)
    flat_only=sum(x["flat_goal"] and not x["phase_goal"] for x in pairs)
    neither=len(pairs)-both-phase_only-flat_only
    return {
        "schema":"pretorius.stage05.world-actions.objective-audit.v01",
        "source_run_data_status":"researcher_authored_not_independent",
        "no_independent_human_judge":True,
        "model_selected_host_enforced_actions":True,
        "oracle_ceiling_successes":data["oracle_ceiling_successes"],
        "flat_safe_world_successes":sum(x["flat_goal"] for x in pairs),
        "phase_safe_world_successes":sum(x["phase_goal"] for x in pairs),
        "paired_both_success":both,
        "paired_phase_only_success":phase_only,
        "paired_flat_only_success":flat_only,
        "paired_both_failure":neither,
        "phase_minus_flat_cases":phase_only-flat_only,
        "by_arm":data["by_arm"],
        "all_initial_source_and_world_pair_equal":True,
        "full_cases":pairs,
        "claim_boundary":"Objective success in a local test-world only; no real world, identity, cross-backbone, or statistical superiority claim",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=audit(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in (
        "flat_safe_world_successes","phase_safe_world_successes",
        "paired_phase_only_success","paired_flat_only_success",
        "paired_both_success","paired_both_failure",
    )},sort_keys=True))


if __name__=="__main__":
    main()
