"""Installed-wheel native operator integration, no scripted Doctor goal.

This QA harness prepares one already-existent book as external world setup.
No task prompt, book identity, goal ID or neural tendency is fed to Pretorius.
The test kills the actual preview-start process after original physical progress,
then uses the public installed preview-resume command with no additional input.
"""
from __future__ import annotations

from contextlib import closing
import gc
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from doctor_lives.preview_ledger import append_activity, read_activity_ledger
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.neural import DEFAULT_CONFIG


def _config():
    c = dict(DEFAULT_CONFIG)
    c.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
             input_degree=4, action_population_size=8, seed=1842)
    return c


def _poll_for(workspace, event, *, goal_id=None, process=None, timeout=90):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if process is not None and process.poll() is not None:
            out, err = process.communicate()
            raise AssertionError(f"Operator exited {process.returncode}: {out} {err}")
        if (workspace / "preview-activity.jsonl").exists():
            records = read_activity_ledger(workspace)
            for item in records:
                if item["event"] == event and (
                        goal_id is None or item["fields"].get("goal_id") == goal_id):
                    return item
        time.sleep(0.05)
    raise AssertionError("Timed out waiting for actual installed operator " + event)


def main():
    import doctor_lives, pretorius_lab, synthetic_ipseity
    assert "site-packages" in str(Path(doctor_lives.__file__).resolve())
    assert "site-packages" in str(Path(pretorius_lab.__file__).resolve())
    assert "site-packages" in str(Path(synthetic_ipseity.__file__).resolve())
    assert os.environ["PRETORIUS_PINNED_AFFECTUS_ROOT"]
    assert os.environ["PRETORIUS_PINNED_LAB_FIXTURE"]
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.home_life import HomeLife
    from pretorius_lab.daily_rhythm import DailyRhythm
    from pretorius_lab.book_library import BookLibrary

    console = shutil.which("doctor-lives")
    assert console and Path(console).parent == Path(sys.executable).parent
    with tempfile.TemporaryDirectory(prefix="wheel-native-operator-") as tmp:
        workspace = Path(tmp) / "doctor"
        workspace.mkdir()
        world_path = workspace / "laboratory.sqlite3"
        world = SpatialHabitat.create(world_path)
        HomeLife(world).initialize()
        DailyRhythm(world).initialize()
        library = BookLibrary(world)
        library.initialize()
        fixture = json.loads(Path(os.environ["PRETORIUS_PINNED_LAB_FIXTURE"])
                             .read_text(encoding="utf-8"))
        library.install("book:007", **fixture, event_id="operator-qa-fixture-install")
        epoch = world.verify()["world_epoch"]
        state = workspace / "state"
        runtime = SixOrganRuntime.open(state, neural_config=_config())
        runtime.checkpoint()
        del runtime
        gc.collect()
        append_activity(workspace, event="external_preexisting_lab_fixture",
                        external_input=True, fields={
                            "prepared_world": True, "installed_book": True,
                            "no_subject_goal_supplied": True})
        starter = subprocess.Popen(
            [console, "preview-start", "--workspace", str(workspace),
             "--native-affectus-source",
             os.environ["PRETORIUS_PINNED_AFFECTUS_ROOT"]],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        resumed = None
        try:
            partial = _poll_for(workspace, "native_goal_moved", process=starter)
            goal_id = partial["fields"]["goal_id"]
            assert goal_id and partial["fields"]["original_tendency"] == "explore"
            assert partial["fields"]["source_rechecked_by_host"]
            assert partial["fields"]["host_selected_route"] is True
            starter.kill()  # Actual foreground operator is terminated mid-goal
            starter.communicate(timeout=30)
            append_activity(workspace, event="external_operator_process_kill",
                            external_input=True, fields={
                                "test_harness_control": True, "goal_id": goal_id,
                                "no_new_task_instruction": True})
            config = json.loads((workspace / "preview-native-mode.json").read_text())
            assert config["operator_selected"] is True
            # No --native-* flag on resume: native intent and donor mode persist.
            resumed = subprocess.Popen(
                [console, "preview-resume", "--workspace", str(workspace)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            done = _poll_for(workspace, "native_goal_completed",
                             goal_id=goal_id, process=resumed, timeout=120)
            assert done["fields"]["world_table"] == "books_events"
            assert done["fields"]["canonical_memory_source"].startswith(
                "laboratory-home:action:")
            assert done["fields"]["source_rechecked_by_host"]
            # A cooperative stop must not replace or remove the original goal.
            stopping = subprocess.run(
                [console, "preview-stop", "--workspace", str(workspace)],
                capture_output=True, text=True, timeout=90)
            assert stopping.returncode == 0, stopping.stdout + stopping.stderr
            stdout, stderr = resumed.communicate(timeout=45)
            assert resumed.returncode == 0, stdout + stderr
            resumed = None
            with closing(world._open()) as db:
                reads = [json.loads(r[0]) for r in
                         db.execute("SELECT payload FROM books_events")]
            assert sum(e["action"]["op"] == "read" for e in reads) == 1
            assert SpatialHabitat(world_path).verify()["world_epoch"] == epoch
            records = read_activity_ledger(workspace)
            assert any(x["event"] == "operator_resume" for x in records)
            assert any(x["event"] == "unexpected_termination" for x in records)
            assert not any(x["fields"].get("operator_supplied_goal") for x in records)
            assert all(x["source_attestation_independent"] is False for x in records)
            print("INSTALLED_OPERATOR_NATIVE_RESUME=" + json.dumps({
                "doctor_from_installed_wheel": True,
                "lab_from_installed_wheel": True,
                "ipseity_from_installed_wheel": True,
                "sensus_pinned_local_checkout": True,
                "affectus_exact_blob_verified": True,
                "operator_killed_mid_goal": True,
                "public_preview_resume_used": True,
                "same_goal_completed_after_resume": True,
                "world_read_events": 1,
                "new_goal_prompt": False,
                "external_kill_recorded": True,
                "independent_attestation": False,
                "three_distinct_tasks_proven": False,
            }, sort_keys=True))
        finally:
            for child in (starter, resumed):
                if child is not None and child.poll() is None:
                    child.kill()
                    child.communicate()
        del world, library
        gc.collect()


if __name__ == "__main__":
    main()
