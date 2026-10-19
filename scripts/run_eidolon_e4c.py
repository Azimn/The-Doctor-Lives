#!/usr/bin/env python3
"""Eidolon E4-C: order-invariant balanced decoder versus recurrent W swaps.

Uses the previously inspected E4 corpus. Successful fitting is a software
result, not independent evidence of semantic action choice or identity.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import time

import numpy as np

from doctor_lives.eidolon_balanced_decoder import (
    BalancedReadout, DELAYS, RIDGE_ALPHA, native_features,
)
from doctor_lives.neural import ACTIONS, PretoriusRecurrentSubstrate

if __package__:
    from scripts.run_eidolon_e4 import cases, config, fixture_hash, lesion_recurrent
    from scripts.run_eidolon_e4b import SEEDS, train as train_noetic, evaluate as sequential_evaluate
    from scripts.run_eidolon_e4b_order import ORDERS
else:
    from run_eidolon_e4 import cases, config, fixture_hash, lesion_recurrent
    from run_eidolon_e4b import SEEDS, train as train_noetic, evaluate as sequential_evaluate
    from run_eidolon_e4b_order import ORDERS

ARMS = (
    "virgin_W_balanced",
    "noetic_W_balanced",
    "noetic_decoder_virgin_W_lesion",
    "noetic_W_native_sequential_decoder",
    "virgin_W_fresh_balanced_decoder",
)


def collect_features(native: PretoriusRecurrentSubstrate, dataset: list[dict]):
    observations = [native_features(native, item["text"]) for item in dataset]
    X = np.asarray([features[delay] for features in observations for delay in DELAYS],
                   dtype=np.float64)
    y = [item["action"] for item in dataset for _ in DELAYS]
    if X.shape != (len(dataset)*len(DELAYS), native.n):
        raise AssertionError("incorrect native feature dimensions")
    return X, y, observations


def permuted_indices(dataset: list[dict], order: tuple[str, ...]) -> list[int]:
    classes = {name: [i for i,x in enumerate(dataset) if x["action"]==name]
               for name in order}
    if any(len(indices)!=8 for indices in classes.values()):
        raise AssertionError("unbalanced fixture classes")
    return [item_index * len(DELAYS) + delay_index
            for i in range(8) for action in order
            for item_index in [classes[action][i]]
            for delay_index in range(len(DELAYS))]


def fit_and_check_order(X: np.ndarray, labels: list[str], dataset: list[dict]):
    trained = []
    for order in ORDERS:
        ix = permuted_indices(dataset, order)
        trained.append(BalancedReadout.fit(
            X[ix], [labels[j] for j in ix], alpha=RIDGE_ALPHA
        ))
    original = trained[0]
    max_weight_difference = max(
        float(np.max(np.abs(d.weights-original.weights)))
        for d in trained[1:]
    )
    max_center_difference = max(
        float(np.max(np.abs(d.center-original.center)))
        for d in trained[1:]
    )
    if max(max_weight_difference, max_center_difference) > 1e-6:
        raise AssertionError("readout depends on teaching presentation order")
    return original, {
        "orders_tested": len(ORDERS),
        "training_feature_rows": len(labels),
        "class_counts": {
            name: labels.count(name)
            for name in sorted(set(labels))
        },
        "max_weight_difference_by_order": max_weight_difference,
        "max_center_difference_by_order": max_center_difference,
    }


def score_one(readout: BalancedReadout, features: np.ndarray) -> dict:
    scores = readout.scores(features)
    return {
        "selected": max(scores, key=scores.get),
        "scores": {a: round(float(scores[a]), 9) for a in ACTIONS},
    }


def run(seeds: tuple[int, ...] = SEEDS) -> dict:
    if (not seeds or len(seeds) != len(set(seeds))
        or any(type(x) is not int or x<0 or x>2**32-1 for x in seeds)):
        raise ValueError("seeds must be unique unsigned integers")
    train, test = cases()
    started = time.monotonic()
    rows = []
    audits = []
    for seed in seeds:
        virgin = PretoriusRecurrentSubstrate(config(seed))
        learned, training_audit = train_noetic(virgin, train, recurrent=True)
        if training_audit["recurrent_change_norm"] <= 1e-8:
            raise AssertionError("E4-C Noetic feature donor did not learn W")
        fixed_W_donor = lesion_recurrent(learned, virgin)
        if not np.array_equal(fixed_W_donor.W.data, virgin.W.data):
            raise AssertionError("mismatched same-seed W transplant")
        native_checkpoints = {
            "virgin": virgin.W.data.copy(),
            "noetic": learned.W.data.copy(),
            "lesion": fixed_W_donor.W.data.copy(),
            "motor": learned.motor_w.copy(),
        }
        Xvirgin, yvirgin, _ = collect_features(virgin, train)
        Xnoetic, ynoetic, _ = collect_features(learned, train)
        if yvirgin != ynoetic:
            raise AssertionError("unmatched training targets")
        ridge_virgin, order_v = fit_and_check_order(Xvirgin, yvirgin, train)
        ridge_noetic, order_n = fit_and_check_order(Xnoetic, ynoetic, train)
        # The repeat is an independent, newly solved readout on virgin W,
        # with the same examples and fixed alpha; it is an equivalence
        # test, not another independent scientific comparator.
        ridge_virgin_fresh = BalancedReadout.fit(
            Xvirgin, yvirgin, alpha=RIDGE_ALPHA
        )
        if not np.allclose(ridge_virgin_fresh.weights, ridge_virgin.weights, atol=1e-6, rtol=0):
            raise AssertionError("repeat virgin fit changed decoder")

        datasets = {
            "virgin_W_balanced": (virgin, ridge_virgin),
            "noetic_W_balanced": (learned, ridge_noetic),
            "noetic_decoder_virgin_W_lesion": (fixed_W_donor, ridge_noetic),
            "noetic_W_native_sequential_decoder": (learned, None),
            "virgin_W_fresh_balanced_decoder": (virgin, ridge_virgin_fresh),
        }
        # Assess whether ridge has in-sample discrimination at all, not
        # just category prediction on unseen actor/episode/cue families.
        training_accuracy = {}
        for name in ("virgin_W_balanced", "noetic_W_balanced"):
            native, decoder = datasets[name]
            train_features = collect_features(native, train)[2]
            guessed = [
                max(decoder.scores(features[0]), key=decoder.scores(features[0]).get)
                for features in train_features
            ]
            training_accuracy[name] = sum(
                guess == item["action"] for guess, item in zip(guessed, train)
            )
        precomputed_test_features = {
            "virgin": [native_features(virgin, x["text"]) for x in test],
            "noetic": [native_features(learned, x["text"]) for x in test],
            "lesion": [native_features(fixed_W_donor, x["text"]) for x in test],
        }
        for arm, (native, decoder) in datasets.items():
            key = ("noetic" if arm in ("noetic_W_balanced","noetic_W_native_sequential_decoder")
                   else "lesion" if arm == "noetic_decoder_virgin_W_lesion"
                   else "virgin")
            for i, item in enumerate(test):
                if decoder is None:
                    outputs = sequential_evaluate(native, item["text"])
                else:
                    outputs = {
                        delay: score_one(decoder, precomputed_test_features[key][i][delay])
                        for delay in DELAYS
                    }
                for delay in DELAYS:
                    prediction = outputs[delay]
                    selected = prediction.get("selected",prediction.get("predicted"))
                    scores = prediction["scores"]
                    if selected is None or abs(sum(scores.values())-1) > 1e-6:
                        raise AssertionError("invalid experiment output distribution")
                    rows.append({
                        "seed": seed, "arm": arm, "case": i,
                        "delay": delay, "actor":item["actor"],
                        "episode":item["episode"],"target": item["action"],
                        "predicted": selected,
                        "correct_top1": selected == item["action"],
                        "target_probability":scores[item["action"]],
                        "target_log_loss":-math.log(max(scores[item["action"]],1e-12)),
                        "scores": scores,
                    })
        for model, name in ((virgin,"virgin"),(learned,"noetic"),(fixed_W_donor,"lesion")):
            np.testing.assert_array_equal(model.W.data,native_checkpoints[name])
        np.testing.assert_array_equal(learned.motor_w,native_checkpoints["motor"])
        audits.append({
            "seed":seed,"noetic_recurrent_change_norm":training_audit["recurrent_change_norm"],
            "noetic_teacher_updates": training_audit["train_ticks"],
            "virgin_recurrent_change_norm":0.0,
            "balanced_feature_count":len(yvirgin),
            "order_check_virgin":order_v,"order_check_noetic":order_n,
            "training_correct_out_of_32":training_accuracy,
        })

    summary={}
    by_seed={}
    for arm in ARMS:
        summary[arm]={}
        for delay in DELAYS:
            subset=[r for r in rows if r["arm"]==arm and r["delay"]==delay]
            summary[arm][str(delay)]={
                "correct":sum(r["correct_top1"] for r in subset),
                "n":len(subset),
                "mean_target_probability":round(sum(r["target_probability"] for r in subset)/len(subset),9),
                "mean_target_log_loss":round(sum(r["target_log_loss"] for r in subset)/len(subset),9),
                "predicted_classes":sorted({r["predicted"] for r in subset}),
            }
    for seed in seeds:
        by_seed[str(seed)]={}
        for arm in ARMS:
            by_seed[str(seed)][arm]={}
            for delay in DELAYS:
                subset=[r for r in rows if r["seed"]==seed and r["arm"]==arm and r["delay"]==delay]
                by_seed[str(seed)][arm][str(delay)]={
                    "correct":sum(r["correct_top1"] for r in subset),
                    "n":len(subset),
                    "predicted_classes":sorted({r["predicted"] for r in subset}),
                }
    # Causal lesion in a fixed decoder controls for new label content:
    loss_count=sum(
        summary["noetic_W_balanced"][str(d)]["correct"]
        -summary["noetic_decoder_virgin_W_lesion"][str(d)]["correct"]
        for d in DELAYS
    )
    return {
        "schema":"eidolon-e4c-batch-balanced-decoder-v0.1",
        "protocol":"docs/EIDOLON_E4C_BALANCED_DECODER_PROTOCOL_V01.md",
        "epistemic_status":"research engineering on repeatedly inspected E4-A/B lexical task bank; not independent outcome validation",
        "source_sha":os.environ.get("GITHUB_SHA"),
        "fixture_sha256":fixture_hash(),
        "seeds":list(seeds),"delay_steps":list(DELAYS),
        "train_cases":len(train),"test_cases":len(test),
        "class_balanced_batch":True,
        "alpha":RIDGE_ALPHA,
        "arms":list(ARMS),"rows":rows,
        "audits":audits,"summary":summary,
        "by_seed":by_seed,"total_lesion_correct_difference_summed_over_delays":loss_count,
        "runtime_seconds":round(time.monotonic()-started,3),
    }


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--seeds",nargs="+",type=int,default=list(SEEDS))
    args=parser.parse_args()
    data=json.dumps(run(tuple(args.seeds)),sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(data,encoding="utf-8")
        print(f"Eidolon E4-C balanced batch report: {args.output}")
    else:
        print(data,end="")
