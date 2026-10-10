#!/usr/bin/env python3
"""Eidolon E4-B controlled order crossover, NOT a sealed evaluation.

Rotates final teacher class, preserving exact same cues/counts/seeds for
native Noetic recurrent and native fixed-W decoder-only arms.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import time

import numpy as np

from doctor_lives.eidolon_noetic import NoeticCrucible, SyntheticOutcomeGrant
from doctor_lives.neural import ACTIONS, PretoriusRecurrentSubstrate

if __package__:
    from scripts.run_eidolon_e4 import cases, config, fixture_hash
    from scripts.run_eidolon_e4b import evaluate, REPEATS, SEEDS
else:
    from run_eidolon_e4 import cases, config, fixture_hash
    from run_eidolon_e4b import evaluate, REPEATS, SEEDS

ORDERS = (
    ("create","persist","cooperate","challenge"),
    ("persist","cooperate","challenge","create"),
    ("cooperate","challenge","create","persist"),
    ("challenge","create","persist","cooperate"),
)
ARMS = ("noetic","decoder_only")
DELAYS = (0,12)


def fit(seed: int, train: list[dict], order: tuple[str,...],
        *, update_W: bool) -> tuple[PretoriusRecurrentSubstrate,dict]:
    if tuple(sorted(order)) != tuple(sorted(ORDERS[0])):
        raise ValueError("invalid class order")
    grouped = {a: [x for x in train if x["action"]==a] for a in ORDERS[0]}
    if any(len(grouped[a])!=8 for a in grouped):
        raise ValueError("unequal training classes")
    virgin = PretoriusRecurrentSubstrate(config(seed))
    n=copy.deepcopy(virgin)
    gate=NoeticCrucible(n)
    counts={a:0 for a in ORDERS[0]}
    ordinal=0
    for _ in range(REPEATS):
        for i in range(8):
            for action in order:
                item=grouped[action][i]
                grant=SyntheticOutcomeGrant.for_fixture(
                    event_id=f"order-{ordinal:05d}",
                    actor=item["actor"],text=item["text"],action=action,
                )
                accepted=gate.teach(
                    event_id=grant.event_id,actor=item["actor"],
                    text=item["text"],action=action,
                    grant=grant,update_recurrence=update_W,
                )
                if not accepted:
                    raise AssertionError("approved fixture grant was rejected")
                counts[action]+=1
                ordinal+=1
    if ordinal!=160 or n.tick!=160 or any(v!=40 for v in counts.values()):
        raise AssertionError("unequal neural/motor training dose")
    recurrent_change=gate.weight_change(virgin)
    if update_W and recurrent_change<=1e-8:
        raise AssertionError("Noetic W did not learn")
    if not update_W and recurrent_change!=0:
        raise AssertionError("decoder-only W changed")
    motor_change=float(np.linalg.norm(n.motor_w-virgin.motor_w))
    if not np.isfinite(motor_change):
        raise AssertionError("nonfinite motor parameters")
    return n, {
        "seed":seed,
        "last_label":order[-1],
        "order":list(order),
        "updates":ordinal,
        "training_class_counts":counts,
        "recurrent_change_norm":recurrent_change,
        "motor_change_norm":motor_change,
    }


def run(seeds: tuple[int,...]=SEEDS) -> dict:
    if not seeds or len(seeds)!=len(set(seeds)) or any(type(x)!=int or x<0 or x>2**32-1 for x in seeds):
        raise ValueError("invalid seed set")
    train,heldout=cases()
    start=time.monotonic()
    rows=[]
    fit_audits=[]
    for seed in seeds:
        for order_ix,order in enumerate(ORDERS):
            for arm in ARMS:
                model,audit=fit(seed,train,order,update_W=arm=="noetic")
                audit.update({"order_id":order_ix,"arm":arm})
                fit_audits.append(audit)
                before_W=model.W.data.copy()
                before_motor=model.motor_w.copy()
                for case_ix,item in enumerate(heldout):
                    outputs=evaluate(model,item["text"])
                    for delay in DELAYS:
                        output=outputs[delay]
                        target=item["action"]
                        rows.append({
                            "seed":seed,"order_id":order_ix,"final_label":order[-1],
                            "order":list(order),"arm":arm,
                            "case":case_ix,"target":target,"delay":delay,
                            "predicted":output["predicted"],
                            "correct_top1":output["predicted"]==target,
                            "target_probability":output["scores"][target],
                            "scores":output["scores"],
                        })
                np.testing.assert_array_equal(model.W.data,before_W)
                np.testing.assert_array_equal(model.motor_w,before_motor)
    summary={}
    for order_ix,order in enumerate(ORDERS):
        k=str(order_ix)
        summary[k]={"order":list(order),"final_label":order[-1]}
        for arm in ARMS:
            subset=[r for r in rows if r["order_id"]==order_ix and r["arm"]==arm and r["delay"]==12]
            summary[k][arm]={
                "n":len(subset),
                "correct":sum(r["correct_top1"] for r in subset),
                "predicted_classes":sorted({r["predicted"] for r in subset}),
                "predicted_final_label":sum(r["predicted"]==order[-1] for r in subset),
                "mean_target_probability":round(sum(r["target_probability"] for r in subset)/len(subset),9),
            }
    shifts={}
    for seed in seeds:
        shifts[str(seed)]={}
        for arm in ARMS:
            for order_ix,order in enumerate(ORDERS):
                t=[r for r in rows if r["seed"]==seed and r["arm"]==arm and r["order_id"]==order_ix and r["delay"]==12]
                shifts[str(seed)][f"{arm}_{order_ix}"]=sorted({r["predicted"] for r in t})
    return {
        "schema":"eidolon-e4b-order-crossover-v0.1",
        "protocol":"docs/EIDOLON_E4B_ORDER_CROSSOVER_PROTOCOL_V01.md",
        "fixture_sha256":fixture_hash(),
        "github_sha":os.environ.get("GITHUB_SHA"),
        "epistemic_status":"previously-inspected development corpus: ordering diagnostic, NOT independent cognitive validation",
        "seeds":list(seeds),"orders":[list(x) for x in ORDERS],
        "expected_rows":len(seeds)*4*2*16*len(DELAYS),
        "actual_rows":len(rows),
        "summary":summary,
        "seed_action_classes":shifts,
        "fit_audits":fit_audits,
        "runtime_seconds":round(time.monotonic()-start,3),
        "rows":rows,
    }


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--seeds",nargs="+",type=int,default=list(SEEDS))
    args=parser.parse_args()
    report=json.dumps(run(tuple(args.seeds)),indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(report,encoding="utf-8")
        print(f"E4-B class-order crossover recorded: {args.output}")
    else:
        print(report,end="")
