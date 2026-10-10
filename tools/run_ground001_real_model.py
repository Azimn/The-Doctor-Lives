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


def fresh_model_turn(root: Path, gguf: Path, goal: str, seed: int, *,
                     world_name: str = "world.sqlite3", brain_name: str = "brain",
                     memory_arm: str = "full",
                     information_arm: str = "names") -> dict:
    argv = [sys.executable, "-m", "research_integrations.concrete_action",
            "--root", str(root), "--gguf", str(gguf),
            "--world", world_name, "--brain", brain_name,
            "--memory-arm", memory_arm,
            "--information-arm", information_arm,
            "--goal", goal, "--seed", str(seed)]
    proc = subprocess.run(argv, capture_output=True, text=True, check=False,
                          timeout=360)
    if proc.returncode:
        raise RuntimeError("Real-model subprocess failed (no simulated result): "
                           + proc.stderr[-3500:])
    return json.loads(proc.stdout)


def matched_memory_presentation(root: Path, gguf: Path,
                                goal: str, seed: int,
                                information_arm: str = "names") -> dict:
    """Equal post-action brain and world snapshots, different UPPB display.

    Does not delete source records or change the neural policy. Only the
    source-safe laboratory autobiography supplied to the action model is masked
    in one arm. No contrast means no valid causal outcome for memory exposure.
    """
    world = SpatialHabitat(root / "world.sqlite3")
    world.verify()
    world.backup_to(root / "cf_full_world.sqlite3")
    world.backup_to(root / "cf_mask_world.sqlite3")
    shutil.copytree(root / "brain", root / "cf_full_brain")
    shutil.copytree(root / "brain", root / "cf_mask_brain")
    full = fresh_model_turn(root, gguf, goal, seed,
                            world_name="cf_full_world.sqlite3",
                            brain_name="cf_full_brain",
                            information_arm=information_arm)
    masked = fresh_model_turn(root, gguf, goal, seed,
                              world_name="cf_mask_world.sqlite3",
                              brain_name="cf_mask_brain",
                              memory_arm="mask_lab_autobiography",
                              information_arm=information_arm)
    world_match = all(
        full["world_before"][key] == masked["world_before"][key]
        for key in ("world_epoch", "revision", "state_digest")
    )
    options_match = (full["offered_action_tokens"] == masked["offered_action_tokens"])
    full_lines, mask_lines = set(full["subject_frame"]), set(masked["subject_frame"])
    memories_removed = sorted(full_lines - mask_lines)
    memory_contrast = bool(memories_removed) and bool(world_match and options_match)
    return {
        "experiment": "source_lab_autobiography_visible_vs_masked_same_brain_and_world",
        "matched_world_identity_and_state": world_match,
        "matched_concrete_options": options_match,
        "full": full, "masked": masked,
        "changed_subject_lines": memories_removed,
        "valid_subject_memory_exposure_contrast": memory_contrast,
        "same_concrete_proposal": full["proposed_action"] == masked["proposed_action"],
        "interpretation_scope": "causal exposure of admitted lab autobiography in language model prompt; same underlying cognitive state, not a recurrent-memory lesion",
    }


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
    world.backup_to(root / "names_control_world.sqlite3")
    shutil.copytree(root / "brain", root / "names_control_brain")
    # A single matched initial-turn comparison of bare names vs known host
    # action effects. Both arms get identical subject and world source records.
    names_control = fresh_model_turn(
        root, gguf, goal, seed, world_name="names_control_world.sqlite3",
        brain_name="names_control_brain", information_arm="names",
    )
    trace = []
    stagnation_stop = False
    memory_contrast = {"not_run": "No successful first source-backed physical act"}
    for i in range(steps):
        record = fresh_model_turn(root, gguf, goal, seed,
                                  information_arm="effects")
        record["session_index"] = i
        record["independent_process_restart"] = True
        trace.append(record)
        if i == 0 and record["status"] == "model_action_verified_and_admitted":
            memory_contrast = matched_memory_presentation(
                root, gguf, goal, seed, information_arm="effects",
            )
        # This never chooses a replacement action. It only stops a run after
        # two identical non-mutating inspections with unchanged physical state.
        # Preserve both proposals as a negative result.
        if (len(trace) >= 2 and record["proposed_action"] == trace[-2]["proposed_action"]
                and record["status"] == "model_selected_additional_observation"
                and trace[-2]["status"] == "model_selected_additional_observation"
                and record["world_after"]["state_digest"] == trace[-2]["world_after"]["state_digest"]):
            stagnation_stop = True
            break
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
        "stagnation_stop_after_two_same_observations": stagnation_stop,
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
        "same_initial_action_menu_for_names_and_effects": (
            names_control["offered_action_tokens"] == trace[0]["offered_action_tokens"]
        ),
        "same_initial_world_for_names_and_effects": all(
            names_control["world_before"][key] == trace[0]["world_before"][key]
            for key in ("world_epoch", "revision", "state_digest")
        ),
        "names_first_proposal": names_control["proposed_action"],
        "effects_first_proposal": trace[0]["proposed_action"],
        "effects_first_action_executed": trace[0]["executed"],
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
        "initial_world": before,
        "names_only_matched_first_turn": names_control,
        "effects_provided_multi_turn_trace": trace,
        "trace": trace,
        "final_world": world.verify(),
        "nonneural_same_initial_world_control": baseline_steps,
        "metrics": metrics,
        "matched_memory_exposure_control": memory_contrast,
        "production_status": "research_hold",
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
