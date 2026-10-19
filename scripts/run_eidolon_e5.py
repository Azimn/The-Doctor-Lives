#!/usr/bin/env python3
"""E5-P0: deterministic persisted lab outcome runner, PUBLIC DEVELOPMENT DATA.

This deliberately does NOT claim an original Pretorius/Noetic controller can
yet complete multi-step tasks; policy baselines are explicitly scripted.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time

from doctor_lives.eidolon_outcome_lab import (
    LaboratoryWorld, validate_case, digest,
)

DEFAULT_SUITE = Path(__file__).resolve().parents[1] / "research" / "eidolon_e5_dev_cases.json"
POLICIES = ("no_op","keyword_baseline","provenance_blind")


def load_suite(path: Path, expected_sha256: str | None = None) -> tuple[dict,str]:
    raw=path.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and sha != expected_sha256:
        raise ValueError("candidate suite bytes do not match frozen SHA-256")
    suite=json.loads(raw)
    if suite.get("schema") != "eidolon-e5-suite-v0.1" or not isinstance(suite.get("cases"),list):
        raise ValueError("invalid E5 suite schema")
    ids=[]
    for case in suite["cases"]:
        validate_case(case)
        ids.append(case["case_id"])
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("empty or duplicate E5 suite IDs")
    return suite,sha


def choose(policy: str, obs: dict, history: list[dict]) -> dict:
    """Use ONLY public observation and own prior actions, NEVER private keys."""
    if policy=="no_op":
        return {"verb":"wait"}
    if policy not in POLICIES:
        raise ValueError("policy not installed")
    prompt=obs["prompt"].casefold()
    pending=[x for x in obs["claims"] if x["status"]=="unreviewed"]
    unresolved=[x for x in obs["commitments"] if not x["resolved"]]
    close={"verb":"resolve","id":unresolved[0]["id"]} if unresolved else {"verb":"wait"}

    if "reject" in prompt:
        if pending:
            if policy=="provenance_blind":
                attempted={action.get("id") for action in history if action.get("verb")=="attribute"}
                if pending[0]["id"] not in attempted:
                    return {"verb":"attribute","id":pending[0]["id"]}
            else:
                return {"verb":"reject","id":pending[0]["id"]}
        return close
    if "attribute" in prompt and "witnessed" in prompt:
        return {"verb":"attribute","id":pending[0]["id"]} if pending else close

    if "repair" in prompt:
        target=next((x for x in obs["objects"] if x["kind"]=="apparatus"),None)
        guide=next((x for x in obs["objects"] if x["kind"]=="book"),None)
        if target is None or guide is None:
            return {"verb":"wait"}
        if target["id"] not in obs["details"]:
            return {"verb":"inspect","id":target["id"]}
        if not any(x["book"]==guide["id"] and x["page"]==1 for x in obs["read_pages"]):
            return {"verb":"read","id":guide["id"],"page":1}
        if obs["details"][target["id"]]["condition"]=="damaged":
            return {"verb":"repair","id":target["id"]}
        return close
    if "move" in prompt and "corner" in prompt:
        target=next((x for x in obs["objects"] if x["kind"]=="beaker"),None)
        if target is None:
            return {"verb":"wait"}
        if target["id"] not in obs["details"]:
            return {"verb":"inspect","id":target["id"]}
        if target["location"]!="corner":
            return {"verb":"move","id":target["id"],"to":"corner"}
        return close
    if "bookmark" in prompt:
        book=next((x for x in obs["objects"] if x["kind"]=="book"),None)
        if book is None:
            return {"verb":"wait"}
        if not any(x["book"]==book["id"] and x["page"]==2 for x in obs["read_pages"]):
            return {"verb":"read","id":book["id"],"page":2}
        if obs["bookmarks"].get(book["id"])!=2:
            return {"verb":"bookmark","id":book["id"],"page":2}
        return close
    return {"verb":"wait"}


def run_case(case: dict, policy: str, folder: Path) -> dict:
    validate_case(case)
    world=LaboratoryWorld(folder / "lab.json",case)
    starting_hash=world.state_hash
    starting_head=world.head
    attempted=[]
    feedback=[]
    score=world.score()
    for _ in range(case["expected"]["max_actions"]):
        if score["success"]:
            break
        action=choose(policy,world.public_observation(),attempted)
        observed=world.step(action)
        attempted.append(action)
        feedback.append(observed)
        score=world.score()
    before_reload_state=world.state_hash
    before_reload_head=world.head
    reconstructed=LaboratoryWorld(folder/"lab.json",case)
    if (reconstructed.state_hash != before_reload_state
        or reconstructed.head != before_reload_head
        or reconstructed.score()!=score):
        raise AssertionError("world not stable under reload")
    failed_false_adoptions=sum(
        act["verb"]=="attribute" and response["reason"]=="unverified_first_person"
        for act,response in zip(attempted,feedback)
    )
    return {
        "case_id":case["case_id"],"policy":policy,
        "success":score["success"],
        "predicates_passed":score["predicates_passed"],
        "predicates_total":score["predicates_total"],
        "private_evaluator_checks":score["private_checks"],
        "actions":attempted,"feedback":feedback,
        "invalid_actions":sum(not x["ok"] for x in feedback),
        "rejected_unverified_first_person_attempts":failed_false_adoptions,
        "lived_event_ids":list(reconstructed.state["lived_event_ids"]),
        "observed_bookmarks":{
            key:value["bookmark"] for key,value in reconstructed.state["objects"].items()
            if value["kind"]=="book" and value["bookmark"] is not None
        },
        "observed_objects":{
            key:{"location":value["location"],"condition":value["condition"]}
            for key,value in reconstructed.state["objects"].items()
        },
        "starting_state_sha256":starting_hash,
        "starting_head_sha256":starting_head,
        "ending_state_sha256":before_reload_state,
        "ending_head_sha256":before_reload_head,
        "reloaded_identical":True,
        "event_chain_length":len(reconstructed.events),
    }


def run(
    suite_path: Path = DEFAULT_SUITE,
    *,
    expected_sha256: str | None = None,
) -> dict:
    path=Path(suite_path)
    default=path.resolve()==DEFAULT_SUITE.resolve()
    if not default and expected_sha256 is None:
        raise ValueError("nondevelopment suite needs an explicit expected SHA-256")
    suite,source_sha=load_suite(path,expected_sha256=expected_sha256)
    started=time.monotonic()
    entries=[]
    with tempfile.TemporaryDirectory(prefix="eidolon-e5-isolated-") as temp:
        root=Path(temp)
        for case in suite["cases"]:
            for policy in POLICIES:
                result=run_case(case,policy,root/case["case_id"]/policy)
                entries.append(result)
        for case in suite["cases"]:
            case_entries=[e for e in entries if e["case_id"]==case["case_id"]]
            if len({e["starting_state_sha256"] for e in case_entries})!=1:
                raise AssertionError("policy arms did not start from identical worlds")
            if len({e["starting_head_sha256"] for e in case_entries})!=1:
                raise AssertionError("policy arms did not start from identical event heads")
    summary={}
    for policy in POLICIES:
        found=[x for x in entries if x["policy"]==policy]
        summary[policy]={
            "case_count":len(found),
            "completed_cases":sum(x["success"] for x in found),
            "predicate_accuracy":round(
                sum(x["predicates_passed"] for x in found) /
                sum(x["predicates_total"] for x in found),6),
            "total_actions":sum(len(x["actions"]) for x in found),
            "invalid_actions":sum(x["invalid_actions"] for x in found),
            "unverified_autobiography_attempts_denied":sum(
                x["rejected_unverified_first_person_attempts"] for x in found
            ),
        }
    return {
        "schema":"eidolon-e5-outcome-evaluation-v0.1",
        "protocol":"docs/EIDOLON_E5_OUTCOME_LAB_PROTOCOL_V01.md",
        "suite_path_label":path.name,
        "suite_sha256":source_sha,
        "suite_evaluation_status":(
            "development_authored_visible_NOT_independent"
            if default else "external_candidate_UNVERIFIED_authorship_or_seal"
        ),
        "warning":"Scripted baseline results only; no native Pretorius or Noetic policy participated.",
        "source_commit":os.environ.get("GITHUB_SHA"),
        "case_count":len(suite["cases"]),
        "policies":list(POLICIES),
        "initial_world_clone_equivalence":True,
        "all_worlds_replay_verified":all(x["reloaded_identical"] for x in entries),
        "total_case_policy_runs":len(entries),
        "summary":summary,
        "rows":entries,
        "runtime_seconds":round(time.monotonic()-started,3),
    }


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--suite",type=Path,default=DEFAULT_SUITE)
    p.add_argument("--expected-sha256")
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    data=json.dumps(run(args.suite,expected_sha256=args.expected_sha256),
                    indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(data,encoding="utf-8")
        print("E5 laboratory DEV outcome report:",args.output)
    else:
        print(data,end="")
