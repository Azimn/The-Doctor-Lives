"""Actual PretoriusBrainPort + opt-in home pilot with source/action replay checks."""
from pathlib import Path
import importlib.util
import json
import tempfile
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.models import SubjectFrame, SubjectRendererCapability


LAB_AVAILABLE = importlib.util.find_spec("pretorius_lab") is not None


@unittest.skipUnless(LAB_AVAILABLE, "Pinned Pretorius-Laboratory dependency required")
class RealDoctorHomeBridgeTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.world = SpatialHabitat.create(root / "world.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        config = dict(DEFAULT_CONFIG)
        config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                      input_degree=4, action_population_size=8)
        self.doctor = PretoriusBrainPort(root / "brain", neural_config=config)
        self.port = SubjectPort(self.world)
        self.bridge = DoctorHomeBridge(self.doctor, self.port, authorized=True)

    def source_memories(self):
        return [m for m in self.doctor.brain.store.memories(False)
                if m["source"].startswith("laboratory-home:")]

    def test_unauthorized_bridge_cannot_admit_world_experience(self):
        with self.assertRaises(PermissionError):
            DoctorHomeBridge(self.doctor, self.port)
        with self.assertRaises(PermissionError):
            self.bridge.act("invent_authority", event_id="invent-1")
        self.assertFalse(self.source_memories())

    def test_observation_enters_real_doctor_once_as_first_person_lived_memory(self):
        first = self.bridge.observe()
        self.assertEqual(first["status"], "admitted")
        self.assertTrue(first["subject"]["inner"].startswith("I "))
        old_tick = self.doctor.brain.store.tick
        second = self.bridge.observe()
        self.assertEqual(second["status"], "already_admitted")
        self.assertEqual(first["memory_id"], second["memory_id"])
        self.assertEqual(old_tick, self.doctor.brain.store.tick)
        mem = next(m for m in self.source_memories() if m["id"] == first["memory_id"])
        self.assertEqual(mem["text"], first["subject"]["inner"])
        self.assertEqual(mem["evidence_class"], "lived_runtime_memory")
        self.assertFalse(mem["external"])

    def test_involuntary_utterance_becomes_real_doctor_memory_without_raw_body_data(self):
        self.bridge.act("walk", event_id="go-hall", station="station:hall")
        hit = self.bridge.act("walk", event_id="hit-stool", station="station:shop:private")
        self.assertEqual(hit["subject"]["spoken_aloud"], "Ow! My foot!")
        self.assertIn("That was aloud?", hit["subject"]["inner"])
        memory = next(m for m in self.source_memories() if m["id"] == hit["memory_id"])
        self.assertIn("I had not meant", memory["text"])
        self.assertNotIn("foot_soreness", memory["text"])
        self.assertNotIn("world_epoch", memory["text"])
        self.assertEqual(self.port.home.audit_state()["body"]["reflexes"], 1)
        self.assertEqual(self.doctor.brain.store.tick > 0, True)

    def test_retry_after_other_world_actions_never_repeats_earlier_doctor_ingress(self):
        self.bridge.act("walk", event_id="go-hall", station="station:hall")
        first = self.bridge.act("walk", event_id="hit-stool", station="station:shop:private")
        self.bridge.act("advance", event_id="clock-forward", minutes=120)
        memories_before = len(self.source_memories())
        tick = self.doctor.brain.store.tick
        second = self.bridge.act("walk", event_id="hit-stool", station="station:shop:private")
        self.assertEqual(second["status"], "already_admitted")
        self.assertEqual(second["subject"], first["subject"])
        self.assertEqual(tick, self.doctor.brain.store.tick)
        self.assertEqual(len(self.source_memories()), memories_before)
        with self.assertRaises(RuntimeError):
            self.bridge.act("walk", event_id="hit-stool", station="station:bedroom")

    def test_nighttime_source_admitted_without_unseen_items(self):
        self.bridge.act("walk", event_id="go-hall", station="station:hall")
        self.bridge.act("walk", event_id="go-bed", station="station:bedroom")
        self.bridge.act("open", event_id="open-wardrobe", container="wardrobe:bedroom")
        light = self.bridge.observe()
        self.assertIn("heavy wool coat", light["subject"]["inner"])
        for ordinal in (1, 2, 3):
            self.bridge.act("advance", event_id=f"night-{ordinal}", minutes=240)
        dark = self.bridge.observe()
        self.assertIn("too dark", dark["subject"]["inner"])
        self.assertNotIn("heavy wool coat", dark["subject"]["inner"])
        tick = self.doctor.brain.store.tick
        with self.assertRaises(Exception):
            self.bridge.act("take", event_id="invisible-coat", item="garment:coat")
        self.assertEqual(tick, self.doctor.brain.store.tick)
        self.bridge.act("light", event_id="lamp-light")
        revealed = self.bridge.observe()
        self.assertIn("heavy wool coat", revealed["subject"]["inner"])

    def test_actual_doctor_policy_runs_after_admitted_environment_not_host_mock(self):
        result = self.bridge.observe()
        decision = self.bridge.request_cognition(trigger="laboratory_home")
        self.assertIsInstance(decision, dict)
        self.assertTrue(decision.get("selected_action"))
        self.assertTrue(decision.get("action_scores"))
        memory = next(m for m in self.source_memories() if m["id"] == result["memory_id"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        # Cognition is a real decision tendency. This experiment has NOT
        # authorized or demonstrated autonomy in selecting a world action.
        self.assertEqual(self.port.home.audit_state()["body"]["steps"], 0)

    def test_brain_reopen_preserves_admitted_sources_without_cloning_world_life(self):
        seen = self.bridge.observe()
        reopened = PretoriusBrainPort(self.doctor.brain.state_dir)
        actor = DoctorHomeBridge(reopened, self.port, authorized=True)
        retry = actor.observe()
        self.assertEqual(retry["status"], "already_admitted")
        self.assertEqual(retry["memory_id"], seen["memory_id"])


@unittest.skipUnless(LAB_AVAILABLE, "Pinned Pretorius-Laboratory dependency required")
class SixOrganLaboratoryParityTests(RealDoctorHomeBridgeTests):
    """Exercise the SAME Laboratory world and existing bridge via six organs."""

    def setUp(self):
        super().setUp()
        self.runtime = SixOrganRuntime(self.doctor)
        self.bridge = self.runtime.bind_laboratory(self.port, authorized=True)

    def test_six_organ_world_observation_action_memory_and_restart(self):
        with self.assertRaises(PermissionError):
            self.runtime.bind_laboratory(self.port)
        first = self.bridge.observe()
        self.assertEqual(first["status"], "admitted")
        decision = self.runtime.noesis.deliberate(host_trigger="laboratory-parity")
        self.assertTrue(decision.selected_tendency)
        self.assertFalse(hasattr(decision, "world_receipt"))
        walked = self.bridge.act(
            "walk", event_id="six-organ-go-hall", station="station:hall"
        )
        self.assertEqual(walked["status"], "admitted")
        hit = self.bridge.act(
            "walk", event_id="six-organ-hit-stool",
            station="station:shop:private"
        )
        self.assertEqual(hit["subject"]["spoken_aloud"], "Ow! My foot!")
        self.assertIn("That was aloud?", hit["subject"]["inner"])
        self.assertNotIn("foot_soreness", hit["subject"]["inner"])
        frame = self.runtime.synthetic_ipseity.project_subject_frame()
        self.assertIsInstance(frame, SubjectFrame)
        for line in SubjectRendererCapability.read(frame):
            self.assertNotIn("world_epoch", line)
            self.assertNotIn("foot_soreness", line)
        tick = self.doctor.brain.store.tick
        again = self.bridge.act(
            "walk", event_id="six-organ-hit-stool",
            station="station:shop:private"
        )
        self.assertEqual(again["status"], "already_admitted")
        self.assertEqual(tick, self.doctor.brain.store.tick)
        self.runtime.checkpoint()
        reopened = SixOrganRuntime.open(self.doctor.brain.state_dir)
        reopened_bridge = reopened.bind_laboratory(self.port, authorized=True)
        retried = reopened_bridge.act(
            "walk", event_id="six-organ-hit-stool",
            station="station:shop:private"
        )
        self.assertEqual(retried["status"], "already_admitted")
        self.assertEqual(retried["memory_id"], hit["memory_id"])



if __name__ == "__main__":
    unittest.main()
