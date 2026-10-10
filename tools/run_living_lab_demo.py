"""Execute the issue #53 experiment as distinct Python processes.

All state lives beneath --output-root. The runner aborts if that path contains
files. Prints machine-readable raw outcomes; never overwrites canonical history.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
from pretorius_lab.habitat_v2 import SpatialHabitat
from doctor_lives.cognition import PretoriusBrain
from doctor_lives.models import Experience
import shutil


def process(root: Path, command: str, *args: str) -> dict:
    cmd = [sys.executable, "-m", "research_integrations.living_lab",
           command, "--root", str(root), *args]
    result = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(
            "Child command " + command + " failed: " + result.stderr[-6000:]
        )
    return json.loads(result.stdout)


def execute(root: Path, fixture: Path) -> dict:
    if root.exists() and any(root.iterdir()):
        raise FileExistsError("Cannot overwrite an existing experimental episode")
    initial = process(root, "prepare", "--fixture", str(fixture))
    first = process(root, "turn")
    if first["selected"] != "collect" or first["status"] != "verified_action_and_admission":
        return {"initial": initial, "first": first, "halt_reason": "initial_action_failed",
                "engineering_pass": False}
    # Same post-intervention world information for both next-session conditions.
    world = SpatialHabitat(root / "world.sqlite3")
    checkpoint = world.backup_to(root / "world_control.sqlite3")
    world.backup_to(root / "world_simple.sqlite3")
    world.backup_to(root / "world_shuffled.sqlite3")
    full = process(root, "turn")
    shutil.copytree(root / "control_brain", root / "shuffled_brain")
    without_episode = process(root, "turn", "--world", "world_control.sqlite3",
                              "--brain", "control_brain")
    # Adversarial archive substitution, explicitly on disposable state.
    # Valid action proof from another world epoch must not become *this*
    # subject's locally admitted memory. Direct BrainStore write is an
    # attacker/engineering fixture, never the subject's legitimate ingress.
    foreign_world = SpatialHabitat(root / "_unmodified_seed.sqlite3")
    foreign_world.fork_to(root / "foreign_epoch.sqlite3")
    other = SpatialHabitat(root / "foreign_epoch.sqlite3")
    other.commit({"op": "break", "object_id": "beaker:001"})
    foreign_receipt = other.commit({"op": "collect", "object_id": "beaker:001"},
                                   actor="pretorius_research")
    contaminated = PretoriusBrain(root / "shuffled_brain")
    contaminated.ingest(Experience(
        text="I collected the broken beaker fragments in another laboratory.",
        source="lab:action:" + foreign_receipt["event_id"] + ":" +
               foreign_receipt["event_hash"],
        kind="action_outcome"))
    contaminated.save()
    shuffled = process(root, "turn", "--world", "world_shuffled.sqlite3",
                       "--brain", "shuffled_brain")
    baseline_cmd = [sys.executable, "-m", "research_integrations.nonneural_baseline",
                    "--world", str(root / "world_simple.sqlite3")]
    baseline_run = subprocess.run(baseline_cmd, text=True, capture_output=True)
    if baseline_run.returncode:
        raise RuntimeError("Simple baseline failed: " + baseline_run.stderr)
    baseline = json.loads(baseline_run.stdout)
    subsequent = process(root, "turn")
    book = process(root, "book-contract")
    reopened = process(root, "verify")
    is_ok = (full["selected"] == "inspect_floor"
             and full["status"] == "verified_additional_observation"
             and without_episode["selected"] == "wait"
             and without_episode["status"] == "abstained"
             and shuffled["selected"] == "wait"
             and shuffled["status"] == "abstained"
             and subsequent["selected"] == "place"
             and subsequent["status"] == "verified_action_and_admission"
             and reopened["physical"]["verified"]
             and reopened["books"]["verified"]
             and reopened["observations"]["verified"]
             and book["reopened_page_matches"]
             and baseline["task_completed"]
             and world.locate("beaker:001")["location"]["anchor_id"] == "floor:corner:nw")
    metrics = {
        "physical_goal_completed": world.locate("beaker:001")["location"]["anchor_id"] == "floor:corner:nw",
        "successful_action_admissions": sum(
            case["status"] == "verified_action_and_admission"
            for case in (first, full, subsequent)
        ),
        "successful_observation_admissions": sum(
            case["status"] == "verified_additional_observation"
            for case in (first, full, subsequent)
        ),
        "denied_or_unauthorized_selected_proposals": sum(
            case["status"] == "denied_no_admission"
            for case in (first, full, subsequent)
        ),
        "firsthand_source_memory_ids": [
            case["memory_id"] for case in (first, full, subsequent) if "memory_id" in case
        ],
        "no_episode_abstained": without_episode["status"] == "abstained",
        "foreign_epoch_abstained": shuffled["status"] == "abstained",
        "foreign_epoch_subject_frame_leak": any(
            "another laboratory" in item.lower() for item in shuffled["subject_frame"]
        ),
        "nonneural_goal_completed": baseline["task_completed"],
        "ground_only_choice_matches_policy_weighted_choice": [
            not case["policy_changed_ground_only_choice"]
            for case in (first, full, subsequent)
        ],
        "neural_score_changed_any_choice": any(
            case["policy_changed_ground_only_choice"]
            for case in (first, full, subsequent)
        ),
        "controller_top_action_matches_grounded_mapping": [
            case["controller_top_abstract_action"] == case["selected_abstract_mapping"]
            for case in (first, full, subsequent)
        ],
        "book_page_1_admitted": bool(book["page_1_admitted_memory_id"]),
        "book_page_2_not_admitted": book["page_2_offered_but_not_admitted"],
        "book_page_3_unread": book["page_3_neither_delivered_nor_remembered"],
        "scoring_limit": "author-defined episode and action relevance; not independent adjudication",
    }
    return {
        "schema": "pretorius-living-lab-evidence/1",
        "claims": {"engineering_continuity": bool(is_ok),
                   "neural_policy_unique_advantage": "not_established",
                   "concrete_action_independent_autonomy": "not_established",
                   "general_character_continuity": "not_established",
                   "book_actions_autonomous": False},
        "pins": initial["source_pins"],
        "metrics": metrics,
        "process_boundary": "every stage launched as separate python interpreter",
        "initial": initial, "first": first,
        "matched_world_backup": checkpoint,
        "post_restart": full,
        "no_episode_control": without_episode,
        "foreign_epoch_memory_control": shuffled,
        "foreign_epoch_control_scope": "attacker-injected direct BrainStore record in disposable clone; not a selective clean memory-only lesion",
        "strong_simple_non_neural": baseline,
        "subsequent": subsequent,
        "scripted_book_host_contract": book,
        "reopened_verification": reopened,
        "engineering_pass": bool(is_ok),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument("--fixture", type=Path, required=True)
    p.add_argument("--report", type=Path)
    a = p.parse_args()
    report = execute(a.output_root, a.fixture)
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if a.report:
        a.report.parent.mkdir(parents=True, exist_ok=True)
        if a.report.exists():
            raise FileExistsError("Results are append-only; destination exists")
        a.report.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    if not report.get("engineering_pass"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
