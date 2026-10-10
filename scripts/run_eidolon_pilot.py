#!/usr/bin/env python3
"""Exploratory Eidolon construction assay. NOT a blinded continuity benchmark."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.eidolon import EidolonEngine
from doctor_lives.neural import ACTIONS, DEFAULT_CONFIG


BASE = {name: 1.0 / len(ACTIONS) for name in ACTIONS}
CASES = (
    ("Cobalt bell behind the window.", "create"),
    ("Amber ribbon above the doorway.", "challenge"),
    ("Silver needle inside the drawer.", "cooperate"),
    ("Crimson ladder by the chimney.", "persist"),
)
DISTRACTORS = (
    Experience("Dust gathers along neglected cabinets."),
    Experience("Rain scatters across the distant courtyard."),
)


def episode(cue: Experience, action: str, control: str) -> dict:
    engine = EidolonEngine()
    shuffled = {"create": "challenge", "challenge": "cooperate",
                "cooperate": "persist", "persist": "create"}
    training = shuffled[action] if control == "label_shuffle" else action
    if control != "no_learning":
        engine.observe(cue, BASE, teaching_action=training, learn=True,
                       lesion_binding=(control == "binding_lesion"))
    else:
        engine.observe(cue, BASE)
    for item in DISTRACTORS:
        output = engine.observe(
            item, BASE, lesion_recurrence=(control == "recurrence_lesion"),
            lesion_binding=(control == "binding_lesion")
        )
    chosen = max(output.action_scores, key=output.action_scores.get)
    return {
        "target": action,
        "predicted": chosen,
        "target_probability": round(output.action_scores[action], 9),
        "base_target_probability": round(output.base_scores[action], 9),
        "correct": chosen == action,
    }


def real_pretorius_shadow() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128, "sensory_dim": 64, "avg_recurrent_degree": 8,
        "input_degree": 4, "action_population_size": 8, "seed": 1842,
    })
    with tempfile.TemporaryDirectory() as td:
        brain = PretoriusBrain(Path(td), neural_config=cfg)
        exp = Experience(
            "I examine the violet prism with Henry in the laboratory.",
            actor="Henry", novelty=0.8, creation=0.7
        )
        result = brain.ingest(exp)
        before_digest, before_tick = brain.store.digest(), brain.neural.tick
        engine = EidolonEngine()
        out = engine.observe_pretorius(
            brain, exp, teaching_action="create", learn=True
        )
        later = engine.observe_pretorius(
            brain, Experience("Dust settles in the lower hall.")
        )
        return {
            "pretorius_memory_was_ingested": brain.store.get_memory(result["memory_id"]) is not None,
            "production_digest_unchanged_by_shadow": brain.store.digest() == before_digest,
            "production_recurrent_tick_unchanged_by_shadow": brain.neural.tick == before_tick,
            "source_neural_policy_actions": len(out.base_scores),
            "create_probability_from_brain": round(out.base_scores["create"], 9),
            "create_probability_in_shadow": round(out.action_scores["create"], 9),
            "delayed_shadow_create_probability": round(later.action_scores["create"], 9),
        }


def run() -> dict:
    groups = {}
    controls = ("intact", "no_learning", "binding_lesion",
                "recurrence_lesion", "label_shuffle")
    for control in controls:
        rows = [episode(Experience(text, actor="Henry"), action, control)
                for text, action in CASES]
        groups[control] = {
            "correct_top1": sum(row["correct"] for row in rows),
            "n": len(rows),
            "mean_target_probability": round(
                sum(row["target_probability"] for row in rows) / len(rows), 9
            ),
            "per_case": rows,
        }
    return {
        "schema": "eidolon-construction-assay-v0.1",
        "commit": os.environ.get("GITHUB_SHA"),
        "epistemic_status": "designed-on-model construction cases, not independent confirmatory results",
        "conditions": groups,
        "real_pretorius_shadow": real_pretorius_shadow(),
    }


if __name__ == "__main__":
    report = run()
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if len(sys.argv) == 3 and sys.argv[1] == "--output":
        dest = Path(sys.argv[2])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(encoded + "\n", encoding="utf-8")
        print(f"Eidolon construction assay written: {dest}")
    else:
        print(encoded)
