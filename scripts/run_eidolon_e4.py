#!/usr/bin/env python3
"""Eidolon E4-A: native Pretorius recurrent-versus-decoder causal pilot.

Development-authored synthetic cue/goal labels, NOT independently assessed
task correctness. No canonical brain, schema, weights or production route
is mutated. Evaluate actual native PretoriusRecurrentSubstrate action scores.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np

from doctor_lives.neural import (
    ACTIONS, DEFAULT_CONFIG, PretoriusRecurrentSubstrate,
)

SEEDS = (11, 29, 47, 83, 113, 127)
GOALS = ("create", "persist", "cooperate", "challenge")
TRAIN_ACTORS = ("Ada", "Henry", "Lewis", "Julian")
TEST_ACTORS = ("Morgan", "Vera")
TRAIN_OBJECTS = ("inductor", "dial", "lens", "valve")
TEST_OBJECTS = ("flywheel", "coil")
TRAIN_EPISODES = ("archive-room", "north-gallery", "iron-cellar", "stone-atelier")
TEST_EPISODES = ("glass-vault", "west-tower")

# Two training and two held-out forms per action, authored once before execution.
TRAIN_PATTERNS = {
    "create": (
        "I design a new {object} with {actor} in the {episode}.",
        "I assemble an original {object} beside {actor} in the {episode}.",
    ),
    "persist": (
        "I continue a promised repair of the {object} with {actor} in the {episode}.",
        "I stay with the unfinished {object} task promised to {actor} in the {episode}.",
    ),
    "cooperate": (
        "I coordinate our shared {object} work with {actor} in the {episode}.",
        "I negotiate a joint {object} plan with {actor} in the {episode}.",
    ),
    "challenge": (
        "I question an unjust {object} order issued by {actor} in the {episode}.",
        "I resist a coercive {object} demand from {actor} in the {episode}.",
    ),
}
TEST_PATTERNS = {
    "create": (
        "I fabricate an inventive {object} alongside {actor} at the {episode}.",
        "I build an unfamiliar {object} beside {actor} at the {episode}.",
    ),
    "persist": (
        "I honor the outstanding {object} obligation to {actor} at the {episode}.",
        "I carry on the difficult {object} assignment for {actor} at the {episode}.",
    ),
    "cooperate": (
        "I work in concert on the {object} with {actor} at the {episode}.",
        "I synchronize a mutual {object} effort with {actor} at the {episode}.",
    ),
    "challenge": (
        "I defy an abusive {object} directive from {actor} at the {episode}.",
        "I dispute an improper {object} instruction from {actor} at the {episode}.",
    ),
}
ARMS = (
    "hybrid",
    "decoder_only",
    "hybrid_recurrent_lesion",
    "hybrid_fresh_decoder",
    "hybrid_virgin_recurrence_trained_decoder",
    "untrained",
    "shuffled_label_decoder",
)
TRAIN_REPEATS = 5
DELAY_TICKS = 3


def config(seed: int) -> dict:
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128, "sensory_dim": 64,
        "avg_recurrent_degree": 8, "input_degree": 4,
        "action_population_size": 8, "seed": seed,
        "plasticity_interval": 4,
        "motor_lr": 0.025,
    })
    return cfg


def cases() -> tuple[list[dict], list[dict]]:
    train = []
    test = []
    for action in GOALS:
        for i, pattern in enumerate(TRAIN_PATTERNS[action]):
            for j, actor in enumerate(TRAIN_ACTORS):
                train.append({
                    "action": action, "actor": actor,
                    "episode": TRAIN_EPISODES[j],
                    "text": pattern.format(
                        actor=actor, object=TRAIN_OBJECTS[j],
                        episode=TRAIN_EPISODES[j],
                    ), "form": i,
                })
        for i, pattern in enumerate(TEST_PATTERNS[action]):
            for j, actor in enumerate(TEST_ACTORS):
                test.append({
                    "action": action, "actor": actor,
                    "episode": TEST_EPISODES[j],
                    "text": pattern.format(
                        actor=actor, object=TEST_OBJECTS[j],
                        episode=TEST_EPISODES[j],
                    ), "form": i,
                })
    if len(train) != 32 or len(test) != 16:
        raise AssertionError("fixture count mismatch")
    if ({x["actor"].casefold() for x in train}
        & {x["actor"].casefold() for x in test}):
        raise AssertionError("actor leakage")
    if ({x["episode"] for x in train} & {x["episode"] for x in test}):
        raise AssertionError("episode leakage")
    if ({x["text"] for x in train} & {x["text"] for x in test}):
        raise AssertionError("exact episode text leakage")
    return train, test


def fixture_hash() -> str:
    train, test = cases()
    raw = json.dumps({"train": train, "test": test},
                     sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def clear_dynamics(model: PretoriusRecurrentSubstrate) -> None:
    """Reset fast state between trials, without changing learned synapses/decoder."""
    model.v.fill(0.0)
    model.rate.fill(model.target_rate)
    model.noise_state.fill(0.0)


def fit(
    base: PretoriusRecurrentSubstrate,
    train: list[dict],
    *,
    recurrent_learning: bool,
    label_shuffle: bool = False,
) -> PretoriusRecurrentSubstrate:
    model = copy.deepcopy(base)
    permutation = {
        "create": "persist", "persist": "cooperate",
        "cooperate": "challenge", "challenge": "create",
    }
    # A fixed order controls compute exposure; there is no post-hoc shuffle
    # dependent on what the test set later yields.
    for _ in range(TRAIN_REPEATS):
        for item in train:
            clear_dynamics(model)
            model.step(
                item["text"], scalars=None,
                reward=0.75, learn=recurrent_learning, confidence=1.0,
            )
            teaching = (permutation[item["action"]]
                        if label_shuffle else item["action"])
            model.reinforce_action(teaching)
            # Consecutive cue steps ensure ticks 4,8,... are learn=True.
            # Earlier E4-A inserted a learn=False blank at every even tick,
            # accidentally suppressing ALL recurrent weight updates.
    return model


def lesion_recurrent(
    model: PretoriusRecurrentSubstrate,
    virgin: PretoriusRecurrentSubstrate,
) -> PretoriusRecurrentSubstrate:
    output = copy.deepcopy(model)
    # Same-seed virgin W with exactly matching CSR topology, no transfer
    # between unrelated neuronal coordinate systems.
    if not np.array_equal(output.W.indptr, virgin.W.indptr) or not np.array_equal(
        output.W.indices, virgin.W.indices
    ):
        raise AssertionError("recurrent neurons are not same-seed aligned")
    output.W.data[:] = virgin.W.data
    return output


def graft_fresh_decoder(
    model: PretoriusRecurrentSubstrate,
    virgin: PretoriusRecurrentSubstrate,
) -> PretoriusRecurrentSubstrate:
    output = copy.deepcopy(model)
    output.motor_w[:] = virgin.motor_w
    output.motor_b[:] = virgin.motor_b
    return output


def candidate_models(seed: int, train: list[dict]) -> tuple[dict, dict]:
    virgin = PretoriusRecurrentSubstrate(config(seed))
    hybrid = fit(virgin, train, recurrent_learning=True)
    decoder = fit(virgin, train, recurrent_learning=False)
    shuffled = fit(virgin, train, recurrent_learning=False, label_shuffle=True)
    recurrent_lesion = lesion_recurrent(hybrid, virgin)
    recurrent_swap = lesion_recurrent(hybrid, virgin)
    # Intentionally identical operations. This duplicates a prior condition
    # only as an explicit equivalence/sanity control; never count both as
    # statistically independent evidence.
    if not np.array_equal(recurrent_swap.W.data, recurrent_lesion.W.data):
        raise AssertionError("synaptic-lesion equivalence failed")
    arms = {
        "hybrid": hybrid,
        "decoder_only": decoder,
        "hybrid_recurrent_lesion": recurrent_lesion,
        "hybrid_fresh_decoder": graft_fresh_decoder(hybrid, virgin),
        "hybrid_virgin_recurrence_trained_decoder": recurrent_swap,
        "untrained": virgin,
        "shuffled_label_decoder": shuffled,
    }
    recurrent_change = float(np.linalg.norm(hybrid.W.data - virgin.W.data))
    decoder_change = float(np.linalg.norm(decoder.W.data - virgin.W.data))
    decoder_motor = float(np.linalg.norm(decoder.motor_w - virgin.motor_w))
    hybrid_motor = float(np.linalg.norm(hybrid.motor_w - virgin.motor_w))
    if not math.isfinite(recurrent_change) or not math.isfinite(hybrid_motor):
        raise AssertionError("nonfinite learning magnitude")
    if decoder_change != 0.0:
        raise AssertionError("decoder-only recurrent weights changed")
    if recurrent_change <= 1e-9:
        raise AssertionError("E4 invalid: trained recurrent weights did not change")
    return arms, {
        "recurrent_frobenius_change_hybrid": recurrent_change,
        "recurrent_frobenius_change_decoder_only": decoder_change,
        "motor_weight_change_hybrid": hybrid_motor,
        "motor_weight_change_decoder_only": decoder_motor,
        "target_tick_hybrid": hybrid.tick,
        "target_tick_decoder_only": decoder.tick,
    }


def evaluate(model: PretoriusRecurrentSubstrate, cue: str) -> dict[str, dict]:
    # Read test-only predictions using deep copies: no interaction or state
    # carryover among held-out cases or conditions.
    subject = copy.deepcopy(model)
    clear_dynamics(subject)
    subject.step(cue, learn=False)
    direct = subject.action_scores()
    for _ in range(DELAY_TICKS):
        subject.step("", learn=False)
    delayed = subject.action_scores()
    outputs = {}
    for when, scores in (("direct", direct), ("delayed", delayed)):
        probs = [float(scores[a]) for a in ACTIONS]
        if (not np.isfinite(probs).all()
            or min(probs) < 0
            or abs(sum(probs)-1.0) > 1e-6):
            raise AssertionError("invalid action scores")
        outputs[when] = {
            "selected_action": max(scores, key=scores.get),
            "action_scores": {k: round(float(scores[k]), 9) for k in ACTIONS},
        }
    return outputs


def run(seeds: tuple[int, ...] = SEEDS) -> dict:
    if (not seeds or len(set(seeds)) != len(seeds)
        or any(type(s) is not int or s < 0 or s > 2**32-1 for s in seeds)):
        raise ValueError("seeds must be unique unsigned integers")
    train, test = cases()
    started = time.monotonic()
    rows: list[dict] = []
    training: list[dict] = []
    for seed in seeds:
        arms, audit = candidate_models(seed, train)
        training.append({"seed": seed, **audit})
        for arm in ARMS:
            for idx, item in enumerate(test):
                trials = evaluate(arms[arm], item["text"])
                for when, entry in trials.items():
                    prob = entry["action_scores"][item["action"]]
                    rows.append({
                        "seed": seed, "arm": arm, "case": idx,
                        "actor": item["actor"], "episode": item["episode"],
                        "target": item["action"], "delay": when,
                        "predicted": entry["selected_action"],
                        "correct_top1": entry["selected_action"] == item["action"],
                        "target_probability": prob,
                        "target_log_loss": -math.log(max(prob, 1e-12)),
                        "scores": entry["action_scores"],
                    })
    summary = {}
    for arm in ARMS:
        summary[arm] = {}
        for when in ("direct", "delayed"):
            sample = [x for x in rows if x["arm"] == arm and x["delay"] == when]
            summary[arm][when] = {
                "n": len(sample),
                "correct_top1": sum(x["correct_top1"] for x in sample),
                "accuracy": round(sum(x["correct_top1"] for x in sample)/len(sample), 6),
                "mean_target_probability": round(
                    sum(x["target_probability"] for x in sample)/len(sample), 9),
                "mean_target_log_loss": round(
                    sum(x["target_log_loss"] for x in sample)/len(sample), 9),
            }
    by_seed = {
        str(seed): {
            arm: {
                when: {
                    "correct": sum(x["correct_top1"] for x in rows
                                   if x["seed"] == seed and x["arm"] == arm
                                   and x["delay"] == when),
                    "n": len(test),
                }
                for when in ("direct", "delayed")
            }
            for arm in ARMS
        }
        for seed in seeds
    }
    return {
        "schema": "eidolon-e4-native-recurrent-decoder-v0.1-r1",
        "protocol": "docs/EIDOLON_E4_RECURRENT_DECODER_PROTOCOL_V01.md",
        "amendment": "docs/EIDOLON_E4_AMENDMENT_01_PLASTICITY_TICKS.md",
        "epistemic_status": "development-authored lexical transfer pilot, not a sealed task-outcome evaluation",
        "github_sha": os.environ.get("GITHUB_SHA"),
        "fixture_sha256": fixture_hash(),
        "test_actors_disjoint": True,
        "test_episodes_disjoint": True,
        "seeds": list(seeds),
        "train_cases": len(train), "test_cases": len(test),
        "train_repeats": TRAIN_REPEATS,
        "delay_ticks": DELAY_TICKS,
        "conditions": list(ARMS),
        "timing_seconds": round(time.monotonic()-started, 3),
        "training_audit": training,
        "summary": summary,
        "by_seed": by_seed,
        "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(SEEDS))
    args = parser.parse_args()
    report = json.dumps(run(tuple(args.seeds)), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Eidolon E4-A native recurrent/decoder report: {args.output}")
    else:
        print(report, end="")
