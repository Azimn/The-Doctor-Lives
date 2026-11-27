"""QI-02: scalar reinforcement cannot create first-person experience."""
from contextlib import closing
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.cognition import PretoriusBrain
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.tower_ipseity import TowerIpseity


def small_config():
    return dict(DEFAULT_CONFIG, neurons=128, sensory_dim=64,
                avg_recurrent_degree=8, input_degree=4, action_population_size=8,
                seed=1842)


def memory_ids(brain):
    return {m["id"] for m in brain.store.memories(False)}


class ReinforcementOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_scalar_reinforcement_cannot_manufacture_lived_memory(self):
        brain = PretoriusBrain(self.root / "brain", neural_config=small_config())
        subject = TowerIpseity(brain)
        subject.admit_private("reinforcement-control", "Noesis", "I consider the apparatus.")
        history = subject.verify_history()
        ids = memory_ids(brain)
        tick = brain.store.tick
        original_capture = brain.neural.capture_outcome
        original_reinforce = brain.neural.reinforce_action
        calls = []

        def capture(reward, **kw):
            with closing(brain.store.connect()) as db:
                row = db.execute("SELECT * FROM events WHERE kind='action_outcome' ORDER BY rowid DESC LIMIT 1").fetchone()
            self.assertEqual(row["source"], "reinforcement:scalar")
            self.assertEqual(row["evidence_class"], "unconscious_reinforcement")
            self.assertTrue(row["external"])
            self.assertFalse(json.loads(row["payload_json"])["subject_admitted"])
            self.assertEqual(memory_ids(brain), ids)
            self.assertEqual(subject.verify_history(), history)
            calls.append(("capture", reward))
            return original_capture(reward, **kw)

        def reinforce(action, strength):
            self.assertEqual(subject.verify_history(), history)
            self.assertEqual(memory_ids(brain), ids)
            calls.append((action, strength))
            return original_reinforce(action, strength)

        with patch.object(brain.neural, "capture_outcome", side_effect=capture), \
                patch.object(brain.neural, "reinforce_action", side_effect=reinforce):
            brain.record_action_outcome("create", True, 1.0)
            brain.record_action_outcome("create", False, 1.0)
        self.assertEqual(calls, [("capture", 1.0), ("create", 1.0),
                                 ("capture", -1.0), ("create", -1.0)])
        with closing(brain.store.connect()) as db:
            row = db.execute("SELECT value,uses,successes FROM action_values WHERE action='create'").fetchone()
            self.assertAlmostEqual(row["value"], .4838)
            self.assertEqual((row["uses"], row["successes"]), (2, 1))
            self.assertEqual(db.execute("SELECT count(*) FROM memories WHERE kind='action_outcome'").fetchone()[0], 0)
        self.assertEqual(brain.store.tick, tick + 2)
        self.assertEqual(memory_ids(brain), ids)
        self.assertEqual(subject.verify_history(), history)
        reopened = PretoriusBrain(brain.state_dir)
        self.assertEqual(memory_ids(reopened), ids)
        self.assertEqual(TowerIpseity(reopened).verify_history(), history)

    @unittest.skipUnless(importlib.util.find_spec("pretorius_lab") is not None,
                         "Pinned original Laboratory dependency required")
    def test_authenticated_action_outcome_is_owned_before_conscious_processing(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        from doctor_lives.lab_home_bridge import DoctorHomeBridge
        world = SpatialHabitat.create(self.root / "world.sqlite3")
        HomeLife(world).initialize()
        DailyRhythm(world).initialize()
        port = PretoriusBrainPort(self.root / "brain", neural_config=small_config())
        bridge = DoctorHomeBridge(port, SubjectPort(world), authorized=True)
        brain = port.brain
        subject = TowerIpseity(brain)
        self.assertIsNone(brain.store.meta("small-tower:world-binding-v1"))
        prefix = subject.verify_history()
        original_step = brain.neural.step
        witnessed = []

        def checked_step(text, *args, **kwargs):
            # Check committed history through an independent DB connection
            # inside the actual recurrent call for a real physical outcome.
            memory = next(m for m in brain.store.memories(False)
                          if m["text"] == text and m["source"].startswith("laboratory-home:action:"))
            entries = [e for e in subject.verify_history()
                       if e["key"].endswith("acquisition:" + memory["id"])]
            self.assertEqual(len(entries), 1)
            entry = entries[0]
            self.assertEqual(entry["phase"], "acquisition")
            item = entry["content"][0]
            self.assertEqual(item["text"], text)
            self.assertEqual(item["attribution"], "lived")
            self.assertFalse(item["external"])
            self.assertIn(memory["source_event_id"], item["source_refs"])
            self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
            witnessed.append((memory["id"], entry["sha256"]))
            return original_step(text, *args, **kwargs)

        with patch.object(brain.neural, "step", side_effect=checked_step):
            result = bridge.act("walk", event_id="qi02-outcome-walk", station="station:hall")
        self.assertEqual(len(witnessed), 1)
        self.assertEqual(witnessed[0][0], result["memory_id"])
        history = subject.verify_history()
        self.assertEqual(history[:len(prefix)], prefix)
        self.assertIn(witnessed[0][1], [e["sha256"] for e in history])
        ids = memory_ids(brain)
        # A separate scalar learning signal is not the physical receipt.
        # No invented equivalence between the action label and world action.
        original_capture = brain.neural.capture_outcome
        def checked_capture(reward, **kwargs):
            self.assertEqual(subject.verify_history(), history)
            self.assertEqual(memory_ids(brain), ids)
            return original_capture(reward, **kwargs)
        with patch.object(brain.neural, "capture_outcome", side_effect=checked_capture) as capture:
            brain.record_action_outcome("explore", True, .8)
            capture.assert_called_once_with(.8, confidence=1.0)
        self.assertEqual(memory_ids(brain), ids)
        self.assertEqual(subject.verify_history(), history)
        reopened = PretoriusBrainPort(brain.state_dir)
        self.assertEqual(TowerIpseity(reopened.brain).verify_history(), history)
        self.assertEqual(memory_ids(reopened.brain), ids)

    @unittest.skipUnless(importlib.util.find_spec("pretorius_lab") is not None,
                         "Pinned original Laboratory dependency required")
    def test_denied_outcome_admission_cannot_reach_recurrence(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        from doctor_lives.lab_home_bridge import DoctorHomeBridge
        world = SpatialHabitat.create(self.root / "world.sqlite3")
        HomeLife(world).initialize()
        DailyRhythm(world).initialize()
        port = PretoriusBrainPort(self.root / "brain", neural_config=small_config())
        bridge = DoctorHomeBridge(port, SubjectPort(world), authorized=True)
        brain = port.brain
        history = TowerIpseity(brain).verify_history()
        ids = memory_ids(brain)
        neural_tick = brain.neural.tick
        with patch.object(TowerIpseity, "record", side_effect=PermissionError("admission fault")), \
                patch.object(brain.neural, "step", wraps=brain.neural.step) as step:
            with self.assertRaisesRegex(PermissionError, "admission fault"):
                bridge.act("walk", event_id="qi02-denied-outcome", station="station:hall")
            step.assert_not_called()
        self.assertEqual(TowerIpseity(brain).verify_history(), history)
        self.assertEqual(memory_ids(brain), ids)
        self.assertEqual(brain.neural.tick, neural_tick)


if __name__ == "__main__":
    unittest.main()
