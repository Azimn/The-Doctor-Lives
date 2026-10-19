#!/usr/bin/env python3
"""E2 fixed-delay no-cue construction assay; not independent scientific proof."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.eidolon import EidolonEngine
from doctor_lives.neural import ACTIONS, DEFAULT_CONFIG


BASE = {a: 1.0 / len(ACTIONS) for a in ACTIONS}
CASES = (
    ("Cobalt bell behind the window.", "create"),
    ("Amber ribbon above the doorway.", "challenge"),
    ("Silver needle inside the drawer.", "cooperate"),
    ("Crimson ladder by the chimney.", "persist"),
)
SHUFFLED = {
    "create": "challenge", "challenge": "cooperate",
    "cooperate": "persist", "persist": "create",
}


def run_condition(text: str, target: str, arm: str) -> dict:
    engine = EidolonEngine()
    teaching = SHUFFLED[target] if arm == "label_shuffle" else target
    cue = Experience(text, actor="Henry")
    if arm == "no_learning":
        engine.observe(cue, BASE)
    else:
        engine.observe(
            cue, BASE, teaching_action=teaching, learn=True,
            lesion_binding=(arm == "binding_lesion")
        )
    before = engine.snapshot()
    engine.advance_without_cue(3)
    after = engine.snapshot()
    if before["weights"] != after["weights"]:
        raise RuntimeError("no-cue interval altered learned association weights")
    lesion = arm in {"recurrence_lesion", "cue_only"}
    result = engine.probe_intention(BASE, lesion_recurrence=lesion)
    prediction = max(result.action_scores, key=result.action_scores.get)
    return {
        "target": target,
        "predicted": prediction,
        "correct_top1": prediction == target,
        "target_probability": round(result.action_scores[target], 9),
        "base_probability": round(result.base_scores[target], 9),
        "recurrent_norm": round(result.recurrent_strength, 9),
        "cue_access_at_readout": False,
        "latent_ticks": after["tick"] - before["tick"],
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
            "I promise Henry to finish the anatomical apparatus.",
            actor="Henry", creation=0.8
        )
        brain.ingest(exp)
        baseline = brain.neural.action_scores()
        original_digest = brain.store.digest()
        original_tick = brain.neural.tick
        renderer_before = brain.render_request().to_dict()
        engine = EidolonEngine()
        engine.observe_pretorius(brain, exp, teaching_action="create", learn=True)
        engine.advance_without_cue(3)
        predicted = engine.probe_intention(baseline)
        masked = engine.probe_intention(baseline, lesion_recurrence=True)
        return {
            "real_neural_action_base": round(baseline["create"], 9),
            "intact_shadow_create": round(predicted.action_scores["create"], 9),
            "no_trace_shadow_create": round(masked.action_scores["create"], 9),
            "pretorius_database_digest_preserved": original_digest == brain.store.digest(),
            "pretorius_recurrent_tick_preserved": original_tick == brain.neural.tick,
            "pretorius_subject_frame_preserved": renderer_before == brain.render_request().to_dict(),
        }


def main() -> dict:
    arms = ("intact", "no_learning", "binding_lesion",
            "recurrence_lesion", "cue_only", "label_shuffle")
    by_arm = {}
    for arm in arms:
        results = [run_condition(text, action, arm) for text, action in CASES]
        by_arm[arm] = {
            "n": len(results),
            "correct_top1": sum(r["correct_top1"] for r in results),
            "mean_target_probability": round(
                sum(r["target_probability"] for r in results) / len(results), 9
            ),
            "cases": results,
        }
    return {
        "schema": "eidolon-e2-no-cue-construction-v0.2",
        "github_sha": os.environ.get("GITHUB_SHA"),
        "declared_protocol": "docs/EIDOLON_E2_NO_CUE_PROTOCOL_V02.md",
        "epistemic_status": "engineered construction comparison, not independent validation",
        "direct_cue_access_at_decision": False,
        "equal_no_cue_ticks": 3,
        "conditions": by_arm,
        "pretorius_shadow": real_pretorius_shadow(),
    }


if __name__ == "__main__":
    output = json.dumps(main(), indent=2, sort_keys=True) + "\n"
    if len(sys.argv) == 3 and sys.argv[1] == "--output":
        path = Path(sys.argv[2])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
        print(f"Eidolon E2 report: {path}")
    else:
        print(output, end="")
