"""Reproduce GROUND-001 with actual pinned local GGUF and fresh processes.

Never claim a deterministic stub or existing abstract Pretorius state policy
picked concrete actions. Model proposal, host outcome, and success are scored
separately. The simple nonneural planner runs on a matched physical world.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from pretorius_lab.habitat_v2 import SpatialHabitat
from research_integrations.living_lab import prepare
from research_integrations.nonneural_baseline import run as simple_baseline

SCHEMA = "pretorius.living-lab.ground001-real-model-comparison/1"


def fresh_model_turn(root: Path, gguf: Path, goal: str, seed: int) -> dict:
    argv = [sys.executable, "-m", "research_integrations.concrete_action",
            "--root", str(root), "--gguf", str(gguf),
            "--goal", goal, "--seed", str(seed)]
    proc = subprocess.run(argv, capture_output=True, text=True, check=False,
                          timeout=360)
    if proc.returncode:
        raise RuntimeError("Real-model subprocess failed (no simulated result): "
                           + proc.stderr[-3500:])
    return json.loads(proc.stdout)


def goal_finished(world: SpatialHabitat) -> bool:
    observed = world.locate("beaker:001")
    return (observed["condition"] == "broken"
            and observed["location"]["anchor_id"] == "floor:corner:nw")


def run(root: Path, fixture: Path, gguf: Path, *, goal: str, steps: int,
        seed: int = 41) -> dict:
    if steps < 1 or steps > 8:
        raise ValueError("Max 1..8 turns")
    if root.exists() and any(root.iterdir()):
        raise FileExistsError("Refusing nonempty result directory")
    setup = prepare(root, fixture)
    world = SpatialHabitat(root / "world.sqlite3")
    before = world.verify()
    world.backup_to(root / "nonneural_control.sqlite3")
    trace = []
    for i in range(steps):
        record = fresh_model_turn(root, gguf, goal, seed)
        record["session_index"] = i
        record["independent_process_restart"] = True
        trace.append(record)
        if (goal_finished(world) or record["status"] in {
            "model_selected_wait", "invalid_proposal_no_execution",
            "host_denied_no_admission", "observation_denied_no_admission",
        }):
            break
    # Same initial physical problem, host grants and perceptual affordances.
    baseline_world = SpatialHabitat(root / "nonneural_control.sqlite3")
    baseline_steps = [simple_baseline(baseline_world.path)]
    if not baseline_steps[0]["task_completed"]:
        baseline_steps.append(simple_baseline(baseline_world.path))
    metrics = {
        "goal_complete": goal_finished(world),
        "firsthand_action_admissions": sum(
            row["status"] == "model_action_verified_and_admitted" for row in trace),
        "additional_observation_admissions": sum(
            row["status"] == "model_selected_additional_observation" for row in trace),
        "model_invalid_proposals": sum(
            row["status"] == "invalid_proposal_no_execution" for row in trace),
        "model_explicit_abstentions": sum(
            row["status"] == "model_selected_wait" for row in trace),
        "host_denials": sum(row["host_denied"] for row in trace),
        "proposed_legal_action_operand": sum(
            row["proposed_action"] is not None and row["validation"] == "accepted_proposal"
            for row in trace),
        "neural_policy_top_actions": [x["abstract_policy_top"] for x in trace],
        "actual_concrete_proposals": [x["proposed_action"] for x in trace],
        "baseline_goal_complete": baseline_steps[-1]["task_completed"],
        "source_attribution": "per-action event hash and source-bound memory id in raw trace",
        "uncontrolled_confounders": [
            "researcher-defined goal and environment",
            "action options and plain-language renderer authored by researcher",
            "no independent held-out evaluation",
            "language model acts as concrete decoder, not demonstrated neural causality",
        ],
    }
    result = {
        "schema": SCHEMA, "source_pins": setup["source_pins"],
        "model_file_sha256": trace[0].get("model_sha256") if trace else None,
        "run_configuration": {"goal": goal, "steps": steps, "seed": seed,
                              "fresh_python_process_per_model_turn": True},
        "initial_world": before, "trace": trace,
        "final_world": world.verify(),
        "nonneural_same_initial_world_control": baseline_steps,
        "metrics": metrics, "production_status": "research_hold",
    }
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument("--fixture", type=Path, required=True)
    p.add_argument("--gguf", type=Path, required=True)
    p.add_argument("--goal", default="Make the broken laboratory glass safe.")
    p.add_argument("--steps", type=int, default=5)
    p.add_argument("--seed", type=int, default=41)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    if a.report.exists():
        raise FileExistsError("Raw evidence path already exists")
    result = run(a.output_root, a.fixture, a.gguf, goal=a.goal,
                 steps=a.steps, seed=a.seed)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({"schema": result["schema"], "metrics": result["metrics"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
