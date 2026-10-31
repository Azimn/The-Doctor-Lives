"""Actual original-world integration for B's persistent native work goal.

Targeted implementation evidence only. Waiting for a naturally selected neural
PERSIST tendency is a laboratory test setup, not proof of independent three-goal
autonomy, externally killed process recovery, or a four-hour trial.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest

from doctor_lives.lab_native_goal_choice import NativeLaboratoryGoalChooser
from doctor_lives.lab_native_work_goal import WORK_KEY, _hash, _stable
from doctor_lives.lab_six_organ_session import SixOrganLaboratoryCycle
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime

DONORS_PRESENT = all(
    importlib.util.find_spec(x) is not None
    for x in ("pretorius_lab", "sensus_artificialis", "synthetic_ipseity")
) and bool(os.environ.get("PRETORIUS_PINNED_AFFECTUS_ROOT"))


def small_neural():
    config = dict(DEFAULT_CONFIG)
    config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                  input_degree=4, action_population_size=8, seed=1842)
    return config


@unittest.skipUnless(DONORS_PRESENT, "Real original Lab and reviewed donors required")
class CandidateBSourceBackedWork(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        self.temp = tempfile.TemporaryDirectory(prefix="candidate-b-real-work-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.world = SpatialHabitat.create(self.root / "original.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        self.subject = SubjectPort(self.world)
        self.state = self.root / "same-canonical-brain"
        self.donor = Path(os.environ["PRETORIUS_PINNED_AFFECTUS_ROOT"])

    def session(self, runtime):
        def renderer(subject_text):
            if not isinstance(subject_text, str) or not subject_text.startswith(("I ", "My ")):
                raise PermissionError("Host diagnostics cannot enter subject channel")
            return subject_text
        return SixOrganLaboratoryCycle(
            runtime, self.subject, affectus_source=self.donor,
            renderer=renderer, authorized=True)

    def test_real_persist_goal_moves_and_executes_noesis_selected_work_once(self):
        rt = SixOrganRuntime.open(self.state, neural_config=small_neural())
        epoch = self.subject.verify()["world_epoch"]
        with self.session(rt) as host:
            chooser = NativeLaboratoryGoalChooser(
                host, authorized=True, enable_sustained_work=True)
            # Exercise the shipping chooser, not a host-picked action or
            # directly injected goal. The original world has no books
            # installed, so a real native EXPLORE may investigate the seen
            # workbench; an AVOID/other origin remains a measured negative.
            created = chooser.step(authorized_world_action=False)
            self.assertEqual(created.status, "goal_created")
            self.assertEqual(created.kind, "work")
            self.assertIn(created.selected_tendency, ("explore", "persist"))
            self.assertEqual(self.subject.embodied.verify()["station"], "station:threshold")
            denied = chooser.step(authorized_world_action=False)
            self.assertEqual(denied.kind, "work")
            self.assertEqual(denied.status, "authorization_required")
            self.assertEqual(self.subject.embodied.verify()["station"], "station:threshold")
            rt.checkpoint()

        resumed = SixOrganRuntime.open(self.state)
        with self.session(resumed) as host:
            chooser = NativeLaboratoryGoalChooser(
                host, authorized=True, enable_sustained_work=True)
            for turn in range(12):
                result = chooser.step(authorized_world_action=True)
                self.assertEqual(result.kind, "work")
                self.assertEqual(result.goal_id, created.goal_id)
                if result.status == "completed":
                    break
            else:
                self.fail("A genuine source-feasible native work goal did not complete")
            self.assertGreaterEqual(turn, 2)
            self.assertEqual(self.subject.embodied.verify()["station"], "station:bench")
            memory = resumed._port.brain.store.get_memory(result.memory_id)
            self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
            self.assertFalse(memory["external"])
            self.assertTrue(memory["source"].startswith("laboratory-home:action:"))
            record = json.loads(resumed._port.brain.store.meta(WORK_KEY))["payload"]
            self.assertEqual(record["origin_policy_id"] is not None, True)
            self.assertIn(record["selected_action"], ("repair", "experiment"))
            with resumed._port.brain.store.connect() as db:
                policy = db.execute(
                    "SELECT selected_action FROM policy_decisions WHERE id=?",
                    (record["origin_policy_id"],)).fetchone()
                chosen = db.execute(
                    "SELECT selected_action FROM policy_decisions WHERE id=?",
                    (record["work_policy_id"],)).fetchone()
            self.assertEqual(policy["selected_action"], created.selected_tendency)
            self.assertEqual(chosen["selected_action"], record["selected_action"])
            next_goal = chooser.step(authorized_world_action=True)
            # A later original exploratory/avoid choice may legitimately
            # originate a DIFFERENT book/rest goal. Neither reopens work.
            self.assertIn(next_goal.status, ("already_complete", "goal_created",
                                             "no_situated_goal"))
            if next_goal.status == "goal_created":
                self.assertIn(next_goal.kind, ("read_book", "rest"))
                self.assertNotEqual(next_goal.goal_id, created.goal_id)
            resumed.checkpoint()

        with self.world._open() as db:
            rows = db.execute(
                "SELECT envelope FROM rhythm_events WHERE event_id=?",
                ("ng_" + created.goal_id + "_work",)).fetchall()
        self.assertEqual(len(rows), 1)
        receipt = json.loads(rows[0][0])
        self.assertEqual(receipt["op"], record["selected_action"])
        self.assertEqual(self.subject.verify()["world_epoch"], epoch)
        cold = SixOrganRuntime.open(self.state)
        with self.session(cold) as host:
            work = NativeLaboratoryGoalChooser(
                host, authorized=True, enable_sustained_work=True).work
            self.assertEqual(work._load()["phase"], "complete")
            self.assertEqual(work._load()["memory_id"], result.memory_id)
            self.assertEqual(len([m for m in cold._port.brain.store.memories(False)
                                  if m["source"] == memory["source"]]), 1)
        # Independent read-only Python process, not the in-process chooser,
        # checks the exact same original BrainStore and physical Laboratory.
        # This is one real WORK positive, not 3/3 uncoached acceptance.
        witness_script = r"""
import json, sqlite3, sys
from pathlib import Path
from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.daily_rhythm import DailyRhythm
brain_path, world_path, policy_id, thought_id, event_id, memory_id = sys.argv[1:]
with sqlite3.connect(Path(brain_path).absolute().as_uri() + "?mode=ro", uri=True) as db:
    policy = db.execute("SELECT selected_action,trigger FROM policy_decisions WHERE id=?",
                        (policy_id,)).fetchone()
    thought = db.execute("SELECT generated_by FROM thoughts WHERE id=?",
                         (thought_id,)).fetchone()
    memory = db.execute("SELECT source,evidence_class,external FROM memories WHERE id=?",
                        (memory_id,)).fetchone()
assert policy and policy[0] in ("explore", "persist")
assert policy[1] == "six_organ_lab_cycle"
assert thought == ("neural_policy:" + policy_id,)
assert memory and memory[1] == "lived_runtime_memory" and memory[2] == 0
lab = SpatialHabitat(Path(world_path))
physics = lab.verify()
rhythm = DailyRhythm(lab).verify()
assert physics["world_epoch"] == rhythm["world_epoch"]
with sqlite3.connect(Path(world_path).absolute().as_uri() + "?mode=ro", uri=True) as db:
    event = db.execute("SELECT event_hash FROM rhythm_events WHERE event_id=?",
                       (event_id,)).fetchone()
assert event and memory[0] == "laboratory-home:action:" + event[0]
print("B_REAL_WORK_EXTERNAL_SOURCE_WITNESS=" + json.dumps({
    "source_pinned_original_world": True,
    "original_neural_policy": policy[0],
    "original_thought": True,
    "source_world_receipt": True,
    "lived_memory": True,
    "three_uncoached_goals_proven": False,
}, sort_keys=True))
"""
        witnessed = subprocess.run(
            [sys.executable, "-c", witness_script,
             str(self.state / "brain.sqlite3"), str(self.root / "original.sqlite3"),
             record["origin_policy_id"], record["origin_thought_id"],
             "ng_" + created.goal_id + "_work", result.memory_id],
            capture_output=True, text=True, timeout=45,
        )
        self.assertEqual(witnessed.returncode, 0, witnessed.stderr)
        self.assertIn("B_REAL_WORK_EXTERNAL_SOURCE_WITNESS=",
                      witnessed.stdout)

        print("B_NATIVE_REAL_WORK_TARGETED=" + json.dumps({
            "original_neural_source": created.selected_tendency, "actual_concrete_noesis": record["selected_action"],
            "original_world_receipt": True, "one_lived_memory": True,
            "cold_reopen": True, "host_routed": True,
            "independent_three_goal_acceptance": False,
        }, sort_keys=True))

    def test_original_lab_authority_rejects_foreign_rhythm_epoch(self):
        # This uses the REAL pinned DailyRhythm.verify, not a fabricated
        # SQLite-only positive or an auditor bypass.
        from pretorius_lab.physics import Conflict
        self.subject.rhythm.verify()
        with sqlite3.connect(self.root / "original.sqlite3") as db:
            db.execute(
                "UPDATE rhythm_meta SET value=? WHERE key='world_epoch'",
                (json.dumps("forged-other-world"),),
            )
        with self.assertRaises(Conflict):
            self.subject.rhythm.verify()

    def test_original_lab_full_replay_rejects_torn_physical_chain(self):
        from pretorius_lab.physics import Conflict
        # A genuine physical time action first commits to original world.
        self.subject.rhythm.act("advance", event_id="original-chain-probe",
                                minutes=10)
        self.subject.rhythm.verify()
        with sqlite3.connect(self.root / "original.sqlite3") as db:
            db.execute(
                "UPDATE rhythm_events SET prev_hash=? WHERE event_id=?",
                ("f" * 64, "original-chain-probe"),
            )
        with self.assertRaises(Conflict):
            self.subject.rhythm.verify()

    def test_self_consistent_forged_goal_cannot_create_work(self):
        rt = SixOrganRuntime.open(self.state, neural_config=small_neural())
        with self.session(rt) as host:
            fabricated = {
                "schema": "pretorius.native-work-intention.v1",
                "id": "f" * 24, "world_epoch": self.subject.verify()["world_epoch"],
                "goal": "I want to undertake worthwhile work at my laboratory bench.",
                "phase": "complete", "steps": 3,
                "origin_policy_id": "forged_policy",
                "origin_thought_id": "forged_thought",
                "work_policy_id": "forged_choice",
                "selected_action": "experiment",
                "memory_id": "forged_memory",
            }
            with rt._port.brain.store.transaction() as db:
                rt._port.brain.store.set_meta(
                    WORK_KEY, _stable({"payload": fabricated,
                                        "sha256": _hash(fabricated)}), db)
            with self.assertRaisesRegex(RuntimeError, "Corrupt or forged"):
                NativeLaboratoryGoalChooser(
                    host, authorized=True, enable_sustained_work=True)
            with self.world._open() as db:
                self.assertEqual(db.execute(
                    "SELECT count(*) FROM rhythm_events").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
