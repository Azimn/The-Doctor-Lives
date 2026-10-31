"""Hard-kill experiment on a REAL neural-originated Laboratory book intention.

Test only. No host-chosen book goal, no forced Noesis result, no mock world
receipt, no new production command. The restarted process receives only the
existing world/state paths and a general world-action authorization.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from doctor_lives.preview_ledger import append_activity, read_activity_ledger
from doctor_lives.neural import DEFAULT_CONFIG

NEED = ("pretorius_lab", "sensus_artificialis", "synthetic_ipseity")
READY = all(importlib.util.find_spec(name) is not None for name in NEED) and bool(
    os.environ.get("PRETORIUS_PINNED_AFFECTUS_ROOT")
) and bool(os.environ.get("PRETORIUS_PINNED_LAB_FIXTURE"))


def _config():
    settings = dict(DEFAULT_CONFIG)
    settings.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                    input_degree=4, action_population_size=8, seed=1842)
    return settings


def _host(runtime, world):
    from pretorius_lab.subject_port import SubjectPort
    from doctor_lives.lab_six_organ_session import SixOrganLaboratoryCycle

    def render(text):
        if type(text) is not str or not text.startswith(("I ", "My ", "Mine ", "Me ")):
            raise PermissionError("Unverified engineer diagnostics entered subject renderer")
        return text

    return SixOrganLaboratoryCycle(
        runtime, SubjectPort(world),
        affectus_source=os.environ["PRETORIUS_PINNED_AFFECTUS_ROOT"],
        renderer=render, authorized=True,
    )


def _proof_for_memory(runtime, world, memory_id, table):
    """Locate exactly one original-world receipt matching canonical lived memory."""
    from doctor_lives.lab_home_bridge import _row

    memory = runtime._port.brain.store.get_memory(memory_id)
    if (memory is None or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or not memory["source"].startswith("laboratory-home:action:")):
        raise AssertionError("Physical action lacks canonical lived memory")
    receipt_hash = memory["source"].removeprefix("laboratory-home:action:")
    with world._open() as db:
        records = db.execute(
            "SELECT event_id FROM " + table + " WHERE event_hash=?",
            (receipt_hash,),
        ).fetchall()
        assert len(records) == 1, "One unique original world receipt required"
        receipt, digest = _row(db, table, records[0][0])
    assert digest == receipt_hash
    return {
        "memory_id": memory_id,
        "memory_source": memory["source"],
        "world_event_id": records[0][0],
        "world_receipt_sha256": digest,
        "source_checked": True,
        "independent_attestation": False,
    }


def _begin_and_kill(root):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from doctor_lives.organs import SixOrganRuntime
    from doctor_lives.lab_endogenous_book_task import EndogenousBookPursuit, _KEY

    state = root / "state"
    world = SpatialHabitat(root / "laboratory.sqlite3")
    runtime = SixOrganRuntime.open(state, neural_config=_config())
    with _host(runtime, world) as session:
        goal = EndogenousBookPursuit(session, authorized=True)
        origin = None
        for attempt in range(80):
            trial = goal.step(authorized_world_action=False)
            if trial.status == "goal_created":
                origin = trial
                break
            assert trial.status == "dormant", trial
        assert origin is not None, "Original Noesis never selected a situated goal"
        intent = json.loads(runtime._port.brain.store.meta(_KEY))["payload"]
        assert intent["id"] == origin.goal_id
        with runtime._port.brain.store.connect() as db:
            decision = db.execute(
                "SELECT selected_action FROM policy_decisions WHERE id=?",
                (intent["origin_policy_id"],)
            ).fetchone()
        assert decision and decision["selected_action"] == "explore"
        append_activity(root, event="doctor_goal_originated", external_input=False,
            fields={
                "goal_id": origin.goal_id, "kind": "read_book",
                "original_policy_id": intent["origin_policy_id"],
                "original_thought_id": intent["origin_thought_id"],
                "goal_selection": "original_neural_explore",
                "host_selected_route": True,
                "task_instruction": None,
            })
        moved = goal.step(authorized_world_action=True)
        assert moved.status == "moved" and moved.goal_id == origin.goal_id
        proof = _proof_for_memory(runtime, world, moved.memory_id, "embodied_events")
        append_activity(root, event="doctor_partial_physical_progress",
                        external_input=False,
                        fields={**proof, "goal_id": origin.goal_id,
                                "physical_effect": "movement",
                                "goal_completed": False, "task_instruction": None})
        assert goal.status().goal_id == origin.goal_id
        assert goal.status().phase != "complete"
        runtime.checkpoint()
    append_activity(root, event="harness_mid_activity_crash_point",
                    external_input=False,
                    fields={"goal_id": origin.goal_id, "task_instruction": None})
    # A real hard process exit: no finally/normal Python shutdown/clean-stop.
    os._exit(79)


def _continue_without_instruction(root):
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from doctor_lives.organs import SixOrganRuntime
    from doctor_lives.lab_endogenous_book_task import EndogenousBookPursuit

    world = SpatialHabitat(root / "laboratory.sqlite3")
    runtime = SixOrganRuntime.open(root / "state")
    old = next(
        row for row in read_activity_ledger(root)
        if row["event"] == "doctor_goal_originated"
    )
    original_goal_id = old["fields"]["goal_id"]
    with _host(runtime, world) as session:
        existing = EndogenousBookPursuit(session, authorized=True)
        previous = existing.status()
        assert previous.goal_id == original_goal_id
        assert previous.phase != "complete"
        append_activity(root, event="original_goal_restored_on_cold_boot",
                        external_input=False,
                        fields={"goal_id": previous.goal_id,
                                "phase": previous.phase,
                                "new_goal_prompt": False,
                                "task_instruction": None})
        done = None
        for _ in range(24):
            progress = existing.step(authorized_world_action=True)
            assert progress.goal_id == original_goal_id
            if progress.status == "completed":
                done = progress
                break
        assert done is not None, "Original unfinished neural goal did not finish"
        assert existing.status().phase == "complete"
        proof = _proof_for_memory(runtime, world, done.memory_id, "books_events")
        memory = runtime._port.brain.store.get_memory(done.memory_id)
        assert "I read a page of " in memory["text"]
        append_activity(root, event="same_doctor_goal_completed_after_restart",
                        external_input=False,
                        fields={**proof, "goal_id": done.goal_id,
                                "original_goal_id": original_goal_id,
                                "original_goal_preserved": True,
                                "physical_effect": "one_real_book_read",
                                "task_instruction": None,
                                "host_selected_route": True})
        runtime.checkpoint()


@unittest.skipUnless(READY, "Pinned real Laboratory, Sensus, Ipseity and Affectus required")
class RealHardKillResumeTests(unittest.TestCase):
    def test_noesis_book_goal_survives_actual_process_kill(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.book_library import BookLibrary

        with tempfile.TemporaryDirectory(prefix="real-hard-kill-noesis-") as temp:
            root = Path(temp)
            world = SpatialHabitat.create(root / "laboratory.sqlite3")
            HomeLife(world).initialize()
            DailyRhythm(world).initialize()
            fixture = json.loads(Path(os.environ["PRETORIUS_PINNED_LAB_FIXTURE"])
                                 .read_text(encoding="utf-8"))
            library = BookLibrary(world)
            library.initialize()
            library.install("book:007", **fixture, event_id="qa-book-installed-before-run")
            expected_epoch = world.verify()["world_epoch"]
            append_activity(root, event="harness_setup", external_input=True,
                            fields={"prepared_world": True, "installed_book_fixture": True,
                                    "task_instruction": None, "release_accepted": False})
            # Child processes start with only the original world/state paths,
            # not a subject goal, book ID, neural action or desired outcome.
            script = str(Path(__file__).resolve())
            child1 = subprocess.run(
                [sys.executable, script, "--begin-and-kill", str(root)],
                capture_output=True, text=True, timeout=240,
            )
            self.assertEqual(child1.returncode, 79, child1.stdout + child1.stderr)
            log = read_activity_ledger(root)
            self.assertEqual(log[-1]["event"], "harness_mid_activity_crash_point")
            self.assertTrue(any(x["event"] == "doctor_partial_physical_progress"
                                for x in log))
            append_activity(root, event="external_hard_kill_injected",
                            external_input=True,
                            fields={"test_harness_control": True,
                                    "task_instruction": None, "exit_code": 79})
            child2 = subprocess.run(
                [sys.executable, script, "--continue", str(root)],
                capture_output=True, text=True, timeout=240,
            )
            self.assertEqual(child2.returncode, 0, child2.stdout + child2.stderr)
            log = read_activity_ledger(root)
            origins = [x for x in log if x["event"] == "doctor_goal_originated"]
            completions = [x for x in log
                           if x["event"] == "same_doctor_goal_completed_after_restart"]
            self.assertEqual(len(origins), 1)
            self.assertEqual(len(completions), 1)
            self.assertEqual(origins[0]["fields"]["goal_id"],
                             completions[0]["fields"]["goal_id"])
            self.assertFalse(any(x["fields"].get("task_instruction")
                                 for x in log))
            self.assertTrue(all(
                x["event"] in ("harness_setup", "external_hard_kill_injected")
                for x in log if x["external_input"]
            ))
            self.assertFalse(any(x["source_attestation_independent"] for x in log))
            self.assertEqual(SpatialHabitat(root / "laboratory.sqlite3")
                             .verify()["world_epoch"], expected_epoch)
            with SpatialHabitat(root / "laboratory.sqlite3")._open() as db:
                reads = [json.loads(row[0]) for row in
                         db.execute("SELECT payload FROM books_events")]
            self.assertEqual(sum(x["action"]["op"] == "read" for x in reads), 1)
            gc.collect()
            print("PREVIEW_HARD_KILL_NATIVE_GOAL=" + json.dumps({
                "actual_process_killed": True,
                "cold_restarted": True,
                "same_original_goal_id": True,
                "source_verified_book_read": 1,
                "new_task_instruction": False,
                "external_hard_kill_marked": True,
                "independent_attestation": False,
                "preview_operator_entrypoint_proven": False,
                "three_distinct_tasks_proven": False,
            }, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in ("--begin-and-kill", "--continue"):
        if not READY:
            raise RuntimeError("Hard-kill worker needs all actual pinned donors")
        root = Path(sys.argv[2])
        if sys.argv[1] == "--begin-and-kill":
            _begin_and_kill(root)
        else:
            _continue_without_instruction(root)
    else:
        unittest.main()
