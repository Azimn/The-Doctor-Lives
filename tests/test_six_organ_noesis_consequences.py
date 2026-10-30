"""Real-world, no-manual Noesis choice changes after its own consequences.

This suite uses the original brain, one pinned actual Laboratory and original
source-verified admissions. No invented post-action reward or second selector.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.noesis_lab_work import propose_noesis_work, execute_noesis_work

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


def neural_config():
    c = dict(DEFAULT_CONFIG)
    c.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
             input_degree=4, action_population_size=8, seed=1842)
    return c


@unittest.skipUnless(HAS_LAB, "Requires actual pinned Laboratory, not mock world")
class NoesisActualConsequenceTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        from pretorius_lab.book_library import BookLibrary

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.world = SpatialHabitat.create(root / "world.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        self.port = PretoriusBrainPort(root / "brain", neural_config=neural_config())
        self.subject = SubjectPort(self.world)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        BookLibrary(self.world).initialize()
        # Location is a host opportunity, not a mind-authored navigation goal.
        self.bridge.act("walk", event_id="arrival-center", station="station:center")
        self.bridge.act("walk", event_id="arrival-bench", station="station:bench")

    def state(self):
        self.subject.verify()
        with self.world._open() as db:
            row = db.execute("SELECT value FROM rhythm_meta WHERE key='state'").fetchone()
            return json.loads(row[0])

    def actions(self, op):
        with self.world._open() as db:
            return db.execute(
                "SELECT count(*) FROM rhythm_events WHERE json_extract(envelope,'$.op')=?",
                (op,),
            ).fetchone()[0]

    def policy_audit(self, pid):
        with self.port.brain.store.connect() as db:
            row = db.execute(
                "SELECT policy_version,selected_action,state_pressure_json "
                "FROM policy_decisions WHERE id=?", (pid,),
            ).fetchone()
        self.assertIsNotNone(row)
        return row["selected_action"], json.loads(row["state_pressure_json"])

    def create_one_real_consequence(self):
        self.assertEqual(self.state()["apparatus"], 2)
        proposal = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True, neural_prior_enabled=False,
        )
        self.assertEqual(proposal.action, "experiment")
        action = execute_noesis_work(
            self.bridge, decision_id=proposal.decision_id,
            event_id="original-noesis-experiment", authorized_world_action=True,
        )
        self.assertEqual(action["world"]["status"], "admitted")
        self.assertEqual(self.state()["apparatus"], 1)
        self.assertEqual(self.actions("experiment"), 1)
        lived = self.port.brain.store.get_memory(action["world"]["memory_id"])
        self.assertEqual(lived["evidence_class"], "lived_runtime_memory")
        self.assertIn("apparatus shows wear", lived["text"])
        return action["world"]["memory_id"]

    def test_noesis_tried_experiment_suffered_wear_then_selected_real_repair(self):
        consequence_id = self.create_one_real_consequence()
        improved = propose_noesis_work(
            self.bridge, learning_enabled=False, outcome_learning_enabled=True,
        )
        self.assertEqual(improved.action, "repair")
        self.assertIn(consequence_id, improved.supporting_memory_ids)
        selected, audit = self.policy_audit(improved.decision_id)
        self.assertEqual(selected, "repair")
        self.assertEqual(audit["version"], "noesis-situated-choice-v0.3")
        self.assertEqual(audit["used_outcome_memory_ids"], [consequence_id])
        self.assertAlmostEqual(audit["outcome_contributions"]["experiment"], -0.6)
        self.assertAlmostEqual(audit["outcome_contributions"]["repair"], 0)
        self.assertEqual(self.actions("repair"), 0)
        with self.assertRaises(PermissionError):
            execute_noesis_work(
                self.bridge, decision_id=improved.decision_id,
                event_id="noesis-repair", authorized_world_action=False,
            )
        action = execute_noesis_work(
            self.bridge, decision_id=improved.decision_id,
            event_id="noesis-repair", authorized_world_action=True,
        )
        self.assertEqual(action["world"]["status"], "admitted")
        self.assertEqual(action["action"], "repair")
        self.assertEqual(self.state()["apparatus"], 3)
        self.assertEqual(self.state()["repairs"], 1)
        self.assertEqual(self.actions("repair"), 1)
        self.assertEqual(self.port.brain.store.get_memory(
            action["world"]["memory_id"]
        )["evidence_class"], "lived_runtime_memory")
        self.assertEqual(execute_noesis_work(
            self.bridge, decision_id=improved.decision_id,
            event_id="noesis-repair", authorized_world_action=True,
        )["world"]["status"], "already_admitted")
        self.port.save()
        self.port = PretoriusBrainPort(self.port.brain.state_dir)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        self.assertEqual(execute_noesis_work(
            self.bridge, decision_id=improved.decision_id,
            event_id="noesis-repair", authorized_world_action=True,
        )["world"]["status"], "already_admitted")
        self.assertEqual(self.actions("repair"), 1)

    def test_memory_lesion_off_and_restoration_change_choice_without_world_action(self):
        consequence_id = self.create_one_real_consequence()
        state = self.state()
        used = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True, neural_prior_enabled=False,
        )
        self.assertEqual(used.action, "repair")
        no_outcome = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=False, neural_prior_enabled=False,
        )
        self.assertEqual(no_outcome.action, "experiment")
        self.assertEqual(no_outcome.supporting_memory_ids, ())
        with self.port.brain.store.transaction() as db:
            self.port.brain.store.archive_memory(
                db, consequence_id, self.port.brain.store.tick,
                "temporary experimental outcome-memory ablation",
            )
            self.port.brain.store.bump_state_version(db)
        missing = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True, neural_prior_enabled=False,
        )
        self.assertEqual(missing.action, "experiment")
        self.assertEqual(missing.supporting_memory_ids, ())
        with self.port.brain.store.transaction() as db:
            db.execute("UPDATE memories SET active=1 WHERE id=?", (consequence_id,))
            self.port.brain.store.bump_state_version(db)
        returned = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True, neural_prior_enabled=False,
        )
        self.assertEqual(returned.action, "repair")
        self.assertEqual(tuple(returned.supporting_memory_ids), (consequence_id,))
        self.assertEqual(self.state(), state)
        self.port.save()
        self.port = PretoriusBrainPort(self.port.brain.state_dir)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        after_restart = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True, neural_prior_enabled=False,
        )
        self.assertEqual(after_restart.action, "repair")
        self.assertEqual(tuple(after_restart.supporting_memory_ids), (consequence_id,))

    def test_report_and_fake_self_report_never_promote_outcomes(self):
        genuine_id = self.create_one_real_consequence()
        with self.port.brain.store.transaction() as db:
            self.port.brain.store.archive_memory(
                db, genuine_id, self.port.brain.store.tick, "research lesion",
            )
            self.port.brain.store.bump_state_version(db)
        report = self.port.ingest({
            "channel": "world", "source": "report-of-an-experiment",
            "text": "Someone said I complete a careful experiment at my workbench. "
                    "The apparatus shows wear.",
        })
        self.assertEqual(self.port.brain.store.get_memory(
            report["memory_id"]
        )["evidence_class"], "external_statement")
        proposed = propose_noesis_work(
            self.bridge, learning_enabled=False, neural_prior_enabled=False,
            outcome_learning_enabled=True,
        )
        self.assertEqual(proposed.action, "experiment")
        self.assertEqual(proposed.supporting_memory_ids, ())

    def test_consequence_does_not_apply_after_world_is_repaired(self):
        self.create_one_real_consequence()
        repair = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True,
        )
        action = execute_noesis_work(
            self.bridge, decision_id=repair.decision_id,
            event_id="actual-repair-once", authorized_world_action=True,
        )
        self.assertEqual(action["action"], "repair")
        self.assertEqual(self.state()["apparatus"], 3)
        # Under the new *actually perceived* sound condition, neither the
        # earlier wear penalty nor remembered repair bonus may be applied.
        future = propose_noesis_work(
            self.bridge, learning_enabled=False,
            outcome_learning_enabled=True,
        )
        selected, audit = self.policy_audit(future.decision_id)
        self.assertEqual(selected, "experiment")
        self.assertEqual(audit["outcome_contributions"], {"experiment": 0.0})
        self.assertEqual(audit["used_outcome_memory_ids"], [])
        self.assertEqual(self.actions("repair"), 1)

    def test_replaying_world_action_is_not_another_learning_episode(self):
        outcome_id = self.create_one_real_consequence()
        retry = self.bridge.act("experiment", event_id="original-noesis-experiment")
        self.assertEqual(retry["status"], "already_admitted")
        self.assertEqual(retry["memory_id"], outcome_id)
        proposed = propose_noesis_work(
            self.bridge, learning_enabled=False, outcome_learning_enabled=True,
        )
        selected, audit = self.policy_audit(proposed.decision_id)
        self.assertEqual(selected, "repair")
        self.assertEqual(audit["used_outcome_memory_ids"], [outcome_id])
        self.assertAlmostEqual(audit["outcome_contributions"]["experiment"], -0.6)
        self.assertEqual(self.actions("experiment"), 1)


if __name__ == "__main__":
    unittest.main()
