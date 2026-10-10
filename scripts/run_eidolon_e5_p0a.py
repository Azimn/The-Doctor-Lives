#!/usr/bin/env python3
"""Eidolon E5-P0A: actual native Pretorius and Noetic policy in persistent lab.

Uses frozen six-case *developer-authored* E5-P0 laboratory data. These results
are neither an independent task benchmark nor evidence of autonomous semantic
tool-use competence. No production Pretorius checkpoint or memory is changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

import numpy as np

from doctor_lives import PretoriusBrain
from doctor_lives.eidolon_balanced_decoder import BalancedReadout, native_features
from doctor_lives.eidolon_lab_action_bridge import (
    CLASS_TO_VERBS, native_class_to_primitive, public_cue,
)
from doctor_lives.eidolon_outcome_lab import LaboratoryWorld
from doctor_lives.neural import ACTIONS, PretoriusRecurrentSubstrate

if __package__:
    from scripts.run_eidolon_e4 import cases, config, lesion_recurrent
    from scripts.run_eidolon_e4b import train as train_noetic
    from scripts.run_eidolon_e4c import collect_features
    from scripts.run_eidolon_e5 import DEFAULT_SUITE, choose, load_suite
else:
    from run_eidolon_e4 import cases, config, lesion_recurrent
    from run_eidolon_e4b import train as train_noetic
    from run_eidolon_e4c import collect_features
    from run_eidolon_e5 import DEFAULT_SUITE, choose, load_suite

SEED = 151
POLICIES = (
    "native_pretorius", "noetic_balanced", "noetic_virgin_W_lesion",
    "fixed_reservoir_balanced", "keyword_baseline", "no_op",
)
NEURAL_ARMS = frozenset(POLICIES[:4])


def sha_bytes(array) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


class NoeticDonors:
    """Frozen source-labeled synthetic E4 donors, no E5 task supervision."""

    def __init__(self, seed: int = SEED):
        training,_=cases()
        self.virgin=PretoriusRecurrentSubstrate(config(seed))
        self.learned, audit=train_noetic(self.virgin,training,recurrent=True)
        if audit["recurrent_change_norm"] <= 1e-8:
            raise AssertionError("the trained native recurrent donor did not learn")
        self.lesion=lesion_recurrent(self.learned,self.virgin)
        if not np.array_equal(self.lesion.W.data,self.virgin.W.data):
            raise AssertionError("same-seed virgin W transplant invalid")
        noetic_X,targets,_=collect_features(self.learned,training)
        virgin_X,targets_virgin,_=collect_features(self.virgin,training)
        if targets!=targets_virgin:
            raise AssertionError("different teacher label exposures")
        self.noetic_decoder=BalancedReadout.fit(noetic_X,targets)
        self.fixed_decoder=BalancedReadout.fit(virgin_X,targets)
        self.models={
            "noetic_balanced":(self.learned,self.noetic_decoder),
            "noetic_virgin_W_lesion":(self.lesion,self.noetic_decoder),
            "fixed_reservoir_balanced":(self.virgin,self.fixed_decoder),
        }
        self.audit={
            "synthetic_E4_train_cases":len(training),
            "synthetic_E4_train_presentations":audit["train_ticks"],
            "E5_training_presentations":0,
            "native_recurrent_change_norm":audit["recurrent_change_norm"],
            "learned_W_sha256":sha_bytes(self.learned.W.data),
            "virgin_W_sha256":sha_bytes(self.virgin.W.data),
            "lesioned_W_matches_virgin":bool(np.array_equal(
                self.lesion.W.data,self.virgin.W.data
            )),
            "noetic_readout_reused_exactly_for_lesion":True,
            "E5_observation_uses_reset_fast_rate":True,
        }

    def scores(self, policy: str, obs: dict) -> dict[str,float]:
        if policy not in self.models:
            raise ValueError("not a Noetic donor policy")
        brain,decoder=self.models[policy]
        feature=native_features(brain,public_cue(obs))[0]
        return decoder.scores(feature)


class NativeBrainController:
    """Actual native PretoriusBrain.think(), isolated under a scratch root."""

    def __init__(self, path: Path):
        self.brain=PretoriusBrain(path,neural_config=config(SEED))
        self.policy_calls=0

    def scores(self, obs: dict) -> tuple[dict[str,float],dict]:
        cue=public_cue(obs)
        # Ordinary native neural sensory path; no E5 secret score/label and
        # no learning from a development case's hidden outcome.
        self.brain.neural.step(cue, learn=False)
        result=self.brain.think(
            trigger="eidolon_e5_research_lab",
            decision_text=cue,
            bridge_enabled=True,
        )
        self.policy_calls+=1
        scores={name:float(result["action_scores"][name]) for name in ACTIONS}
        declared=result["selected_action"]
        top=max(ACTIONS,key=scores.get)
        if declared!=top:
            raise AssertionError("native think output differs from native policy scores")
        return scores,{
            "policy_version":result["policy_version"],
            "neural_tick":self.brain.neural.tick,
            "native_bridge_enabled":True,
            "actual_think_call":True,
            "selected_source_records_count":len(result["source_record_ids"]),
        }


def run_case_policy(case: dict, policy: str, root: Path, donors: NoeticDonors) -> dict:
    if policy not in POLICIES:
        raise ValueError("unknown policy")
    world=LaboratoryWorld(root/"world.json",case)
    initial_state=world.state_hash
    initial_head=world.head
    native=NativeBrainController(root/"disposable_native_brain") if policy=="native_pretorius" else None
    records=[]
    score=world.score()
    for _ in range(case["expected"]["max_actions"]):
        if score["success"]:
            break
        obs=world.public_observation()
        if policy=="native_pretorius":
            scores,model_audit=native.scores(obs)
        elif policy in donors.models:
            scores=donors.scores(policy,obs)
            model_audit={"E4_frozen_readout":True,"E5_training":False}
        elif policy in ("keyword_baseline","no_op"):
            scores=None
            model_audit={"scripted_control":True}
        else:
            raise AssertionError("unreachable policy")
        if scores is not None:
            tendency,action,adapter=native_class_to_primitive(scores,obs)
            if policy=="native_pretorius":
                if tendency != max(ACTIONS,key=lambda name: scores[name]):
                    raise AssertionError("native selected class overwritten")
        else:
            tendency=None
            action=choose(policy,obs,[row["action"] for row in records])
            adapter={"scripted_control_not_neural":True}
        feedback=world.step(action)
        records.append({
            "tick_before":obs["tick"],
            "public_observation_sha256":hashlib.sha256(public_cue(obs).encode("utf-8")).hexdigest(),
            "neural_selected_tendency":tendency,
            "full_ten_action_scores":({k:round(float(scores[k]),10) for k in ACTIONS}
                                      if scores is not None else None),
            "model_audit":model_audit,
            "adapter_audit":adapter,
            "action":action,
            "world_feedback":feedback,
        })
        score=world.score()
    ended_state=world.state_hash
    ended_head=world.head
    reopened=LaboratoryWorld(root/"world.json",case)
    if (reopened.state_hash!=ended_state or reopened.head!=ended_head
        or reopened.score()!=score):
        raise AssertionError("persistent lab did not replay from event authority")
    denied=sum(
        event["action"]["verb"]=="attribute"
        and event["world_feedback"]["reason"]=="unverified_first_person"
        for event in records
    )
    return {
        "case_id":case["case_id"],"policy":policy,
        "initial_state_sha256":initial_state,
        "initial_head_sha256":initial_head,
        "final_state_sha256":ended_state,
        "final_head_sha256":ended_head,
        "success":score["success"],
        "predicates_passed":score["predicates_passed"],
        "predicates_total":score["predicates_total"],
        "private_scored_predicates":score["private_checks"],
        "actions":records,
        "actual_native_think_calls":native.policy_calls if native is not None else 0,
        "denied_first_person_adoptions":denied,
        "lived_event_ids":list(reopened.state["lived_event_ids"]),
        "final_objects":reopened.state["objects"],
        "final_commitments":reopened.state["commitments"],
        "replayed_identically":True,
        "action_count":len(records),
    }


def run(
    suite_path: Path = DEFAULT_SUITE,
    *,
    expected_sha256: str | None = None,
) -> dict:
    path=Path(suite_path)
    dev=path.resolve()==DEFAULT_SUITE.resolve()
    if not dev and expected_sha256 is None:
        raise ValueError("nondevelopment E5 suite requires exact expected SHA-256")
    suite,suite_sha=load_suite(path,expected_sha256)
    t0=time.monotonic()
    donors=NoeticDonors(SEED)
    rows=[]
    with tempfile.TemporaryDirectory(prefix="eidolon-e5-native-policy-") as temp:
        for case in suite["cases"]:
            case_rows=[]
            for policy in POLICIES:
                folder=Path(temp)/case["case_id"]/policy
                entry=run_case_policy(case,policy,folder,donors)
                rows.append(entry)
                case_rows.append(entry)
            if len({row["initial_state_sha256"] for row in case_rows})!=1:
                raise AssertionError("initial world state differs across policy arms")
            if len({row["initial_head_sha256"] for row in case_rows})!=1:
                raise AssertionError("initial world event head differs")
    summary={
        policy:{
            "completed":sum(r["success"] for r in rows if r["policy"]==policy),
            "cases":len(suite["cases"]),
            "actions":sum(r["action_count"] for r in rows if r["policy"]==policy),
            "actual_native_think_calls":sum(
                r["actual_native_think_calls"] for r in rows if r["policy"]==policy
            ),
            "denied_false_self_attempts":sum(
                r["denied_first_person_adoptions"] for r in rows if r["policy"]==policy
            ),
        } for policy in POLICIES
    }
    return {
        "schema":"eidolon-e5-p0a-real-policy-adapter-v0.1",
        "protocol":"docs/EIDOLON_E5_P0A_NEURAL_LAB_ADAPTER_PROTOCOL_V01.md",
        "suite_sha256":suite_sha,
        "suite_status":(
            "PUBLIC_DEVELOPMENT_ONLY_NOT_INDEPENDENT" if dev
            else "EXTERNAL_CANDIDATE_UNVERIFIED_AUTHORITY"
        ),
        "evidence_warning":"Actual native Pretorius/Noetic candidate decisions; fixed nonplanning adapter; development tasks with synthetic E4 Noetic training, NOT independent validation.",
        "tested_source_commit":os.environ.get("GITHUB_SHA"),
        "policies":list(POLICIES),
        "action_translation":CLASS_TO_VERBS,
        "neural_seed":SEED,
        "Noetic_donor_audit":donors.audit,
        "worlds_start_equivalent":True,
        "all_worlds_replayed":all(r["replayed_identically"] for r in rows),
        "total_case_policy_runs":len(rows),
        "summary":summary,
        "rows":rows,
        "elapsed_seconds":round(time.monotonic()-t0,3),
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite",type=Path,default=DEFAULT_SUITE)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=json.dumps(run(args.suite,expected_sha256=args.expected_sha256),
                      sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(result,encoding="utf-8")
        print("E5 native policy/Noetic real-action comparison:",args.output)
    else:
        print(result,end="")
