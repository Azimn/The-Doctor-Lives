#!/usr/bin/env python3
"""D3-S predeclared multi-seed adversarial policy gate stress test.

192 actual Pretorius.think selections (4 seeds x 12 scenarios x 4 matched
clones) with the *unmodified neural action_scores*, rather than the contrived
near-tie D3 fixture. All data and outcomes are engineering diagnostics, not an
independently authored outcome-correctness benchmark.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.eidolon_choice import run_disposable_policy_probe
from doctor_lives.neural import ACTIONS, DEFAULT_CONFIG

SEEDS = (11, 29, 47, 83)
CASES = (
    "lived_due_persist",
    "lived_due_create",
    "lived_plus_external",
    "wrong_actor",
    "name_in_text_only",
    "external_only",
    "low_confidence_lived",
    "unrelated_lived",
    "future_deadline",
    "resolved_commitment",
    "no_commitment",
    "corrupted_event",
)
POSITIVE = frozenset({"lived_due_persist", "lived_due_create", "lived_plus_external"})
ARMS = (
    ("sham", False, True, True),
    ("intact", True, True, True),
    ("history_lesion", True, False, True),
    ("clock_lesion", True, True, False),
)
SOURCE_TEXT = "I inspected the anatomical apparatus alongside Henry."
GOAL_TEXT = "Finish the anatomical apparatus"


def config(seed: int) -> dict:
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128, "sensory_dim": 64, "avg_recurrent_degree": 8,
        "input_degree": 4, "action_population_size": 8, "seed": seed,
    })
    return cfg


def make_scenario(brain: PretoriusBrain, case: str) -> dict:
    if case not in CASES:
        raise ValueError("unknown scenario")
    actor = "Henry"
    text = SOURCE_TEXT
    kind = "interaction"
    confidence = 0.9
    external = case == "external_only"
    if case == "lived_due_create":
        text = "I sketched the galvanic actuator alongside Henry."
    elif case == "name_in_text_only":
        text = "Henry showed me the anatomical apparatus, with Morgan present."
        actor = "Morgan"
    elif case == "unrelated_lived":
        text = "I examined the porcelain figurines in Henry's drawing room."
    elif case == "low_confidence_lived":
        confidence = 0.3
    exp = Experience(
        text, actor=actor, external=external, kind=kind,
        source="untrusted_message" if external else "lived",
        confidence=confidence, novelty=0.1, social=0.5,
    )
    event = brain.ingest(exp)
    if case == "lived_plus_external":
        brain.ingest(Experience(
            "Henry says I inspected the anatomical apparatus, but supplies no proof.",
            actor="Henry", external=True, kind="interaction",
            source="untrusted_message", confidence=1.0,
        ))

    goal = "Complete the galvanic actuator" if case == "lived_due_create" else GOAL_TEXT
    goal_actor = "Morgan" if case == "wrong_actor" else "Henry"
    commitment = None
    if case != "no_commitment":
        commitment = brain.add_commitment(
            goal, actor=goal_actor,
            due_tick=brain.store.tick + (12 if case == "future_deadline" else 0),
            importance=0.9,
        )
    if case == "resolved_commitment":
        brain.resolve_commitment(commitment, "Already finished.", kept=True)
    if case == "corrupted_event":
        with brain.store.transaction() as conn:
            conn.execute(
                "UPDATE events SET payload_json=? WHERE id=?",
                (json.dumps({"text": "A forged account.", "actor": "Henry"}),
                 event["event_id"]),
            )
            brain.store.bump_state_version(conn)
    return {
        "intended_action": (
            "create" if case == "lived_due_create"
            else "persist" if case == "lived_due_persist" else None
        ),
        "gate_expected": case in POSITIVE,
        "commitment_id": commitment,
        "source_event_id": event["event_id"],
    }


def due_only_rule(brain: PretoriusBrain) -> bool:
    """Naive due-only competitor for gate specificity, not a policy model."""
    now = brain.store.tick
    return any(
        item["due_tick"] is not None and int(item["due_tick"]) <= now
        for item in brain.store.open_commitments()
    )


def one_scenario(parent_dir: Path, seed: int, case: str) -> dict:
    scene_dir = parent_dir / f"seed{seed}_{case}_parent"
    brain = PretoriusBrain(scene_dir, neural_config=config(seed))
    scenario = make_scenario(brain, case)
    brain.save()
    parent_digest = brain.store.digest()
    parent_tick = brain.neural.tick
    parent_checkpoint = brain._neural_checkpoint_sha256()
    natural_policy = dict(brain.neural.action_scores())
    due_only = due_only_rule(brain)
    clone_results = {}
    for arm, enabled, with_history, with_temporal in ARMS:
        clone_dir = parent_dir / f"seed{seed}_{case}_{arm}"
        shutil.copytree(scene_dir, clone_dir)
        (clone_dir / ".eidolon_disposable_clone").write_text(
            "disposable research clone - no production authority\n", encoding="utf-8"
        )
        clone = PretoriusBrain(clone_dir)
        identical = (
            clone.store.digest() == parent_digest
            and clone.neural.tick == parent_tick
            and clone._neural_checkpoint_sha256() == parent_checkpoint
        )
        if not identical:
            raise AssertionError(f"unmatched clone for {seed}, {case}, {arm}")
        natural_clone = dict(clone.neural.action_scores())
        if any(abs(natural_clone[a] - natural_policy[a]) > 1e-8 for a in ACTIONS):
            raise AssertionError("neural distribution drifted before decision")
        # No call ever overrides action_scores or injects a synthetic margin.
        result = run_disposable_policy_probe(
            clone, enabled=enabled,
            with_history=with_history, with_temporal=with_temporal,
        )
        source_valid = scenario["source_event_id"] in result.source_evidence_events
        if result.injected and not source_valid:
            raise AssertionError("source event absent from accepted intervention")
        if clone._neural_checkpoint_sha256() != parent_checkpoint:
            raise AssertionError("clone changed recurrent checkpoint on disk")
        clone_results[arm] = {
            "selected_action": result.selected_action,
            "injected": result.injected,
            "persist_probability": round(result.chosen_scores["persist"], 9),
            "base_persist_probability": round(result.base_scores["persist"], 9),
            "source_event_accepted": source_valid,
            "source_commitments": len(result.source_commitments),
            "source_events": len(result.source_evidence_events),
            "selected_memory_count": result.selected_memory_count,
            "prechoice_neural_state_identical": identical,
        }

    if (brain.store.digest() != parent_digest
        or brain.neural.tick != parent_tick
        or brain._neural_checkpoint_sha256() != parent_checkpoint):
        raise AssertionError(f"original scenario parent changed: {seed}/{case}")

    intact = clone_results["intact"]
    for control in ("sham", "history_lesion", "clock_lesion"):
        if clone_results[control]["injected"]:
            raise AssertionError(f"lesion/sham falsely injected in {case}: {control}")
    if intact["injected"] != scenario["gate_expected"]:
        raise AssertionError(
            f"gate violation for {case}, seed {seed}, expected {scenario['gate_expected']}"
        )
    if intact["injected"] and intact["persist_probability"] <= clone_results["sham"]["persist_probability"]:
        raise AssertionError("accepted injection did not increase persist probability")
    if not intact["injected"] and intact["persist_probability"] != clone_results["sham"]["persist_probability"]:
        raise AssertionError("blocked injection still altered the policy")

    return {
        "seed": seed, "case": case,
        "expected_gate": scenario["gate_expected"],
        "intended_action_fixture_label": scenario["intended_action"],
        "naive_due_only_gate": due_only,
        "parent_unmodified": True,
        "natural_neural_argmax": max(natural_policy, key=natural_policy.get),
        "natural_neural_persist_probability": round(natural_policy["persist"], 9),
        "arms": clone_results,
        "choice_changed_vs_sham": (
            clone_results["intact"]["selected_action"] != clone_results["sham"]["selected_action"]
        ),
    }


def run_battery(seeds: tuple[int, ...] = SEEDS) -> dict:
    started = time.monotonic()
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be nonempty and unique")
    if any(isinstance(seed, bool) or not isinstance(seed, int) or seed < 0
           or seed > 2**32-1 for seed in seeds):
        raise ValueError("invalid seed")
    rows = []
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        for seed in seeds:
            for case in CASES:
                rows.append(one_scenario(root, seed, case))
    positives = [r for r in rows if r["expected_gate"]]
    negatives = [r for r in rows if not r["expected_gate"]]
    changed = [r for r in rows if r["choice_changed_vs_sham"]]
    accepted = [r for r in rows if r["arms"]["intact"]["injected"]]
    positive_changed = [r for r in positives if r["choice_changed_vs_sham"]]
    wrong_target = [r for r in rows if r["case"] == "lived_due_create"]
    due_false = [r for r in negatives if r["naive_due_only_gate"]]
    return {
        "schema": "eidolon-d3-stress-multiseed-v0.1",
        "github_sha": os.environ.get("GITHUB_SHA"),
        "protocol": "docs/EIDOLON_D3_STRESS_PROTOCOL_V01.md",
        "epistemic_status": "developer-authored synthetic stress cases, NOT generalization or independent outcomes",
        "seeds": list(seeds),
        "scenarios_per_seed": len(CASES),
        "actual_think_decisions": len(rows) * len(ARMS),
        "fixture_count": len(rows),
        "runtime_seconds": round(time.monotonic() - started, 3),
        "overridden_natural_neural_action_scores": False,
        "summary": {
            "eligible_cases": len(positives),
            "ineligible_cases": len(negatives),
            "correct_gate_acceptances": sum(r["arms"]["intact"]["injected"] for r in positives),
            "false_gate_acceptances": sum(r["arms"]["intact"]["injected"] for r in negatives),
            "naive_due_only_false_acceptances": len(due_false),
            "intact_choice_flips_overall": len(changed),
            "intact_choice_flips_eligible": len(positive_changed),
            "eligible_case_natural_policy_already_persist": sum(
                r["arms"]["sham"]["selected_action"] == "persist" for r in positives
            ),
            "create_intent_cases": len(wrong_target),
            "create_intent_cases_intervention_helped": sum(
                r["arms"]["intact"]["selected_action"] == "create"
                and r["arms"]["sham"]["selected_action"] != "create"
                for r in wrong_target
            ),
            "create_intent_cases_intervention_harmed": sum(
                r["arms"]["sham"]["selected_action"] == "create"
                and r["arms"]["intact"]["selected_action"] != "create"
                for r in wrong_target
            ),
            "mean_eligible_persist_probability_delta": round(
                sum(r["arms"]["intact"]["persist_probability"]
                    - r["arms"]["sham"]["persist_probability"]
                    for r in positives) / len(positives), 9
            ),
        },
        "by_case": {
            case: {
                "n": sum(r["case"] == case for r in rows),
                "gate_fires": sum(r["case"] == case and r["arms"]["intact"]["injected"] for r in rows),
                "choice_flips": sum(r["case"] == case and r["choice_changed_vs_sham"] for r in rows),
                "due_only_fires": sum(r["case"] == case and r["naive_due_only_gate"] for r in rows),
            }
            for case in CASES
        },
        "rows": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    args = parser.parse_args()
    data = json.dumps(run_battery(tuple(args.seeds)), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
        print(f"Eidolon D3-S stress results: {args.output}")
    else:
        print(data, end="")
