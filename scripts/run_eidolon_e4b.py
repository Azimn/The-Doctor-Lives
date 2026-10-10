#!/usr/bin/env python3
"""E4-B native Pretorius three-factor Noetic Crucible pilot.

All labels and grant proofs are synthetic developer-owned fixtures. Training
is NOT based on externally authenticated autobiographical outcomes. The
experiment is a control-law comparison, not a deployed character brain.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import time

import numpy as np

from doctor_lives.eidolon_noetic import NoeticCrucible, SyntheticOutcomeGrant
from doctor_lives.neural import ACTIONS, PretoriusRecurrentSubstrate
# Both supported invocation paths must work:
#   python scripts/run_eidolon_e4b.py
#   python -m unittest tests.test_eidolon_e4b
if __package__:
    from scripts.run_eidolon_e4 import (
        GOALS, cases, config, fixture_hash, lesion_recurrent,
    )
else:
    from run_eidolon_e4 import (
        GOALS, cases, config, fixture_hash, lesion_recurrent,
    )

SEEDS = (151, 167, 179, 191, 211, 223)
REPEATS = 5
DELAYS = (0, 3, 12)
ARMS = (
    "noetic_hybrid",
    "decoder_only",
    "noetic_recurrent_lesion",
    "noetic_fresh_untrained_decoder",
    "noetic_fresh_trained_decoder",
    "virgin_recurrence_fresh_trained_decoder",
    "shuffled_outcome_noetic",
    "virgin",
)
PERMUTATION = {
    "create": "persist",
    "persist": "cooperate",
    "cooperate": "challenge",
    "challenge": "create",
}


def ordered(train: list[dict]) -> list[dict]:
    """One example of each class per quartet, unlike E4-A's blocked order."""
    grouped = {action: [x for x in train if x["action"] == action]
               for action in GOALS}
    if {key: len(value) for key, value in grouped.items()} != {
        key: 8 for key in GOALS
    }:
        raise ValueError("unbalanced training set")
    return [grouped[action][j]
            for j in range(8) for action in GOALS]


def synthetic_grant(item: dict, target: str, ordinal: int) -> SyntheticOutcomeGrant:
    return SyntheticOutcomeGrant.for_fixture(
        event_id=f"fixture-{ordinal:05d}",
        actor=item["actor"],
        text=item["text"],
        action=target,
    )


def train(
    virgin: PretoriusRecurrentSubstrate,
    dataset: list[dict],
    *,
    recurrent: bool,
    shuffle_labels: bool = False,
) -> tuple[PretoriusRecurrentSubstrate, dict]:
    brain = copy.deepcopy(virgin)
    controller = NoeticCrucible(brain)
    processed = 0
    for _ in range(REPEATS):
        for item in ordered(dataset):
            target = (PERMUTATION[item["action"]]
                      if shuffle_labels else item["action"])
            grant = synthetic_grant(item, target, processed)
            if not controller.teach(
                event_id=grant.event_id, actor=item["actor"],
                text=item["text"], action=target, grant=grant,
                update_recurrence=recurrent,
            ):
                raise AssertionError("approved fixture grant was denied")
            processed += 1
    if processed != 160 or brain.tick != 160 or controller.denied_outcomes:
        raise AssertionError("unbalanced E4-B training exposure")
    w_change = controller.weight_change(virgin)
    motor_change = float(np.linalg.norm(brain.motor_w - virgin.motor_w))
    if not np.isfinite(w_change) or not np.isfinite(motor_change):
        raise AssertionError("nonfinite learned parameters")
    if recurrent and w_change <= 1e-8:
        raise AssertionError("E4-B invalid: no recurrent weight learning")
    if not recurrent and w_change != 0.0:
        raise AssertionError("decoder-only recurrent weights changed")
    return brain, {
        "train_ticks": brain.tick,
        "accepted_synthetic_grants": controller.accepted_outcomes,
        "denied_synthetic_grants": controller.denied_outcomes,
        "recurrent_change_norm": w_change,
        "motor_change_norm": motor_change,
        "class_order": list(GOALS),
    }


def fresh_motor_retrain(
    base: PretoriusRecurrentSubstrate,
    virgin: PretoriusRecurrentSubstrate,
    trainset: list[dict],
) -> tuple[PretoriusRecurrentSubstrate, dict]:
    """Train a fresh native motor readout on frozen W; matched exposure."""
    n = copy.deepcopy(base)
    n.motor_w[:] = virgin.motor_w
    n.motor_b[:] = virgin.motor_b
    fixed = n.W.data.copy()
    count = 0
    for _ in range(REPEATS):
        for item in ordered(trainset):
            n.v.fill(0.0)
            n.rate.fill(n.target_rate)
            n.noise_state.fill(0.0)
            n.step(item["text"], learn=False)
            n.reinforce_action(item["action"])
            count += 1
    np.testing.assert_array_equal(n.W.data, fixed)
    if count != 160:
        raise AssertionError("unmatched fresh decoder exposure")
    return n, {"fresh_decoder_train_ticks": count,
               "fresh_motor_change_norm": float(np.linalg.norm(
                   n.motor_w - virgin.motor_w
               ))}


def candidate_models(seed: int, dataset: list[dict]) -> tuple[dict, dict]:
    virgin = PretoriusRecurrentSubstrate(config(seed))
    hybrid, ha = train(virgin, dataset, recurrent=True)
    decoder, da = train(virgin, dataset, recurrent=False)
    shuffle, sa = train(virgin, dataset, recurrent=True, shuffle_labels=True)
    lesion = lesion_recurrent(hybrid, virgin)
    fresh_untrained = copy.deepcopy(hybrid)
    fresh_untrained.motor_w[:] = virgin.motor_w
    fresh_untrained.motor_b[:] = virgin.motor_b
    fresh_trained, fa = fresh_motor_retrain(hybrid, virgin, dataset)
    fresh_virgin, va = fresh_motor_retrain(virgin, virgin, dataset)
    # Exact checks distinguish recurrent from decoder effects.
    if not np.array_equal(lesion.motor_w, hybrid.motor_w) or not np.array_equal(
        lesion.motor_b, hybrid.motor_b
    ):
        raise AssertionError("recurrent lesion incorrectly changed decoder")
    if not np.array_equal(fresh_trained.W.data, hybrid.W.data):
        raise AssertionError("fresh decoder re-training changed recurrent W")
    if not np.array_equal(fresh_virgin.W.data, virgin.W.data):
        raise AssertionError("virgin recurrent control learned recurrent W")
    return {
        "noetic_hybrid": hybrid,
        "decoder_only": decoder,
        "noetic_recurrent_lesion": lesion,
        "noetic_fresh_untrained_decoder": fresh_untrained,
        "noetic_fresh_trained_decoder": fresh_trained,
        "virgin_recurrence_fresh_trained_decoder": fresh_virgin,
        "shuffled_outcome_noetic": shuffle,
        "virgin": virgin,
    }, {
        "seed": seed,
        "noetic": ha, "decoder_only": da,
        "shuffled_outcome": sa,
        "fresh_trained": fa,
        "virgin_fresh_trained": va,
        "noetic_v_lesion_same_motor": True,
        "fresh_readout_preserves_learned_W": True,
    }


def evaluate(model: PretoriusRecurrentSubstrate, text: str) -> dict[int, dict]:
    # Copy ensures no held-out case sees other examples' fast state.
    n = copy.deepcopy(model)
    n.v.fill(0.0)
    n.rate.fill(n.target_rate)
    n.noise_state.fill(0.0)
    n.step(text, learn=False)
    out = {}
    for delay in range(max(DELAYS)+1):
        if delay:
            n.step("", learn=False)
        if delay not in DELAYS:
            continue
        scores = n.action_scores()
        vec = np.asarray([scores[a] for a in ACTIONS])
        if (not np.isfinite(vec).all()
            or np.min(vec) < 0
            or abs(float(np.sum(vec))-1.0) > 1e-6):
            raise AssertionError("nonfinite or nonnormalized inference")
        out[delay] = {
            "predicted": max(scores, key=scores.get),
            "scores": {a: round(float(scores[a]), 9) for a in ACTIONS},
        }
    return out


def run(seeds: tuple[int, ...] = SEEDS) -> dict:
    if not seeds or any(type(s) is not int or s < 0 or s > 2**32-1 for s in seeds):
        raise ValueError("seeds must be unsigned integers")
    if len(set(seeds)) != len(seeds):
        raise ValueError("duplicate seed")
    start = time.monotonic()
    training, heldout = cases()
    train_order = ordered(training)
    teacher_order = [x["action"] for x in train_order]
    if any(teacher_order[i:i+4] != list(GOALS)
           for i in range(0,len(train_order),4)):
        raise AssertionError("class-blocking confound in E4-B")
    rows = []
    audits = []
    for seed in seeds:
        models, audit = candidate_models(seed, training)
        audits.append(audit)
        for name in ARMS:
            model = models[name]
            before_W = model.W.data.copy()
            before_motor = model.motor_w.copy()
            for ix, item in enumerate(heldout):
                responses = evaluate(model, item["text"])
                for delay, pred in responses.items():
                    label = item["action"]
                    probability = float(pred["scores"][label])
                    rows.append({
                        "seed": seed, "arm": name, "case": ix, "delay": delay,
                        "target": label, "actor": item["actor"],
                        "episode": item["episode"], "predicted": pred["predicted"],
                        "correct_top1": pred["predicted"] == label,
                        "target_probability": probability,
                        "target_log_loss": -math.log(max(probability, 1e-12)),
                        "scores": pred["scores"],
                    })
            np.testing.assert_array_equal(model.W.data, before_W)
            np.testing.assert_array_equal(model.motor_w, before_motor)
    summary = {}
    by_seed = {}
    for name in ARMS:
        summary[name] = {}
        for delay in DELAYS:
            samples = [r for r in rows if r["arm"] == name and r["delay"] == delay]
            summary[name][str(delay)] = {
                "n": len(samples),
                "correct_top1": sum(r["correct_top1"] for r in samples),
                "mean_target_probability": round(sum(r["target_probability"] for r in samples)/len(samples),9),
                "mean_target_log_loss": round(sum(r["target_log_loss"] for r in samples)/len(samples),9),
                "predicted_classes": sorted({r["predicted"] for r in samples}),
            }
    for seed in seeds:
        by_seed[str(seed)] = {}
        for name in ARMS:
            by_seed[str(seed)][name] = {}
            for delay in DELAYS:
                group=[r for r in rows if r["seed"] == seed and r["arm"] == name and r["delay"] == delay]
                by_seed[str(seed)][name][str(delay)]={
                    "correct":sum(r["correct_top1"] for r in group),
                    "n":len(group),
                    "predicted_classes":sorted({r["predicted"] for r in group}),
                }
    return {
        "schema": "eidolon-e4b-noetic-three-factor-development-v0.1",
        "protocol": "docs/EIDOLON_E4B_EXPERIMENT_V01.md",
        "github_sha": os.environ.get("GITHUB_SHA"),
        "epistemic_status": "known/development-authored E4-A lexical fixtures, simulated provenance, NOT independent validation",
        "fixture_sha256": fixture_hash(),
        "train_cases": len(training), "test_cases": len(heldout),
        "class_balanced_round_robin": True,
        "test_actor_episode_disjoint": True,
        "synthetic_source_grants_not_authenticated": True,
        "seeds": list(seeds), "repeats": REPEATS, "delays": list(DELAYS),
        "conditions": list(ARMS), "training_audits": audits,
        "summary": summary, "by_seed": by_seed,
        "runtime_seconds": round(time.monotonic()-start,3),
        "rows": rows,
    }


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    parser.add_argument("--seeds",type=int,nargs="+",default=list(SEEDS))
    args=parser.parse_args()
    data=json.dumps(run(tuple(args.seeds)),sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(data,encoding="utf-8")
        print(f"Noetic Crucible E4-B research results: {args.output}")
    else:
        print(data,end="")
