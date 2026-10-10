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
    full = process(root, "turn")
    without_episode = process(root, "turn", "--world", "world_control.sqlite3",
                              "--brain", "control_brain")
    subsequent = process(root, "turn")
    book = process(root, "book-contract")
    reopened = process(root, "verify")
    is_ok = (full["selected"] == "inspect_floor"
             and full["status"] == "verified_additional_observation"
             and without_episode["selected"] == "wait"
             and without_episode["status"] == "abstained"
             and subsequent["selected"] == "place"
             and subsequent["status"] == "verified_action_and_admission"
             and reopened["physical"]["verified"]
             and reopened["books"]["verified"]
             and reopened["observations"]["verified"]
             and book["reopened_page_matches"]
             and world.locate("beaker:001")["location"]["anchor_id"] == "floor:corner:nw")
    return {
        "schema": "pretorius-living-lab-evidence/1",
        "claims": {"engineering_continuity": bool(is_ok),
                   "neural_policy_unique_advantage": "not_established",
                   "general_character_continuity": "not_established",
                   "book_actions_autonomous": False},
        "pins": initial["source_pins"],
        "process_boundary": "every stage launched as separate python interpreter",
        "initial": initial, "first": first,
        "matched_world_backup": checkpoint,
        "post_restart": full,
        "no_episode_control": without_episode,
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
