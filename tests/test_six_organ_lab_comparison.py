"""Executable Laboratory parity: original BrainPort vs six-organ facade.

Both paths use separately initialized copies of the SAME pinned real Laboratory
with the same physical event sequence. Nothing in this test claims independent
agency, a new organ implementation, or parity with a deployed robot.
The dedicated doctor-home-bridge workflow must install the Laboratory donor;
a normal no-donor brain-tests run may skip this file.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.models import SubjectFrame, SubjectRendererCapability
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime

LAB_AVAILABLE = importlib.util.find_spec("pretorius_lab") is not None


@unittest.skipUnless(LAB_AVAILABLE, "Requires pinned real Pretorius-Laboratory")
class SixOrganRealLaboratoryABParityTests(unittest.TestCase):
    """The identical physical episode must not change because of organ labels."""

    @staticmethod
    def _run_episode(root: Path, *, facade: bool) -> dict:
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort

        world = SpatialHabitat.create(root / "world.sqlite3")
        HomeLife(world).initialize()
        DailyRhythm(world).initialize()
        config = dict(DEFAULT_CONFIG)
        config.update(
            neurons=128, sensory_dim=64, avg_recurrent_degree=8,
            input_degree=4, action_population_size=8, seed=1842,
        )
        brain = PretoriusBrainPort(root / "brain", neural_config=config)
        subject = SubjectPort(world)
        if facade:
            runtime = SixOrganRuntime(brain)
            bridge = runtime.bind_laboratory(subject, authorized=True)
        else:
            runtime = None
            bridge = DoctorHomeBridge(brain, subject, authorized=True)

        frames = []
        receipts = []
        def collect(value):
            frames.append(value["subject"]["inner"])
            receipts.append(value["status"])
            self_speech = value["subject"].get("spoken_aloud")
            return self_speech

        observation = bridge.observe()
        collect(observation)
        walk = bridge.act("walk", event_id="parity-hall", station="station:hall")
        collect(walk)
        collision = bridge.act(
            "walk", event_id="parity-stool", station="station:shop:private"
        )
        spoken = collect(collision)
        advance = bridge.act(
            "advance", event_id="parity-time", minutes=120
        )
        collect(advance)
        collect(bridge.observe())

        before = brain.brain.store.tick
        retry = bridge.act(
            "walk", event_id="parity-stool", station="station:shop:private"
        )
        assert retry["status"] == "already_admitted"
        assert brain.brain.store.tick == before

        if facade:
            proposal = runtime.noesis.deliberate(host_trigger="parity-lab")
            selected = proposal.selected_tendency
            frame = runtime.synthetic_ipseity.project_subject_frame()
            runtime.checkpoint()
        else:
            selected = brain.cognition(trigger="parity-lab")["selected_action"]
            frame = brain.subject_frame()
            brain.save()

        assert isinstance(frame, SubjectFrame)
        subject_lines = SubjectRendererCapability.read(frame)
        # Laboratory world epoch and hidden physiology must remain engineer-only.
        assert all(
            "world_epoch" not in line and "foot_soreness" not in line
            for line in subject_lines
        )

        if facade:
            reopened = SixOrganRuntime.open(brain.brain.state_dir)
            reopened_bridge = reopened.bind_laboratory(subject, authorized=True)
            reopened_brain = reopened._port
        else:
            reopened_brain = PretoriusBrainPort(brain.brain.state_dir)
            reopened_bridge = DoctorHomeBridge(
                reopened_brain, subject, authorized=True
            )
        again = reopened_bridge.act(
            "walk", event_id="parity-stool", station="station:shop:private"
        )
        assert again["status"] == "already_admitted"
        assert again["memory_id"] == collision["memory_id"]
        sources = [
            m for m in reopened_brain.brain.store.memories(False)
            if m["source"].startswith("laboratory-home:")
        ]
        return {
            "frames": frames,
            "receipt_statuses": receipts,
            "reflex_speech": spoken,
            "replay_text": again["subject"]["inner"],
            "replay_spoken": again["subject"]["spoken_aloud"],
            "memory_texts": sorted(m["text"] for m in sources),
            "memory_classes": sorted(m["evidence_class"] for m in sources),
            "selected_tendency": selected,
            "body": subject.home.audit_state()["body"],
            "station": subject.embodied.verify()["station"],
            "subject_lines": tuple(subject_lines),
        }

    def test_classic_and_six_organ_lab_episode_have_identical_observable_behavior(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            classic_root = root / "classic"
            organ_root = root / "six-organs"
            classic_root.mkdir()
            organ_root.mkdir()
            classic = self._run_episode(classic_root, facade=False)
            organs = self._run_episode(organ_root, facade=True)
            for key in (
                "frames", "receipt_statuses", "reflex_speech",
                "replay_text", "replay_spoken", "memory_texts",
                "memory_classes", "selected_tendency", "station",
                "body",
            ):
                with self.subTest(key=key):
                    self.assertEqual(classic[key], organs[key])
            # Distinct fresh brains allocate different memory IDs. Tied
            # retrieval ranks can therefore produce different frame order,
            # without changing the acquired first-person content.
            self.assertCountEqual(
                classic["subject_lines"], organs["subject_lines"]
            )
            self.assertEqual(classic["reflex_speech"], "Ow! My foot!")
            self.assertEqual(len(classic["frames"]), 5)
            self.assertTrue(all(
                isinstance(value, str) and value.startswith(("I ", "My ", "Mine ", "Me "))
                for value in classic["frames"]
            ))


if __name__ == "__main__":
    unittest.main()
