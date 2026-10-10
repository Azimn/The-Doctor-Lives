"""Issue 53: contract checks. Model-free tests are explicitly software tests.

The end-to-end runner and CI use the actual Pretorius recurrent policy.
"""
from pathlib import Path
import json
import tempfile
import unittest

try:
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from pretorius_lab.observation_receipts import ObservationPort
    from pretorius_lab.physics import LabError
    from research_integrations.living_lab import (
        AdmissionError, _verify_observation, _admit_action, _options,
        prepare, _has_attested_memory,
    )
    from doctor_lives.cognition import PretoriusBrain
    LAB_PRESENT = True
except ModuleNotFoundError:
    # Existing production brain-tests do not install optional research lab.
    # Dedicated issue53 workflow pins and installs it, then runs these tests.
    LAB_PRESENT = False


FIXTURE = Path(__file__).resolve().parents[1] / "_lab" / "fixtures" / "DEMO_BOOK_007.json"


@unittest.skipUnless(LAB_PRESENT and FIXTURE.exists(), "Install pinned Pretorius-Laboratory under _lab")
class LaboratoryBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        prepare(self.root, FIXTURE)
        self.world = SpatialHabitat(self.root / "world.sqlite3")
        self.brain = PretoriusBrain(self.root / "brain")

    def test_subject_port_does_not_expose_metric_geometry(self):
        port = ObservationPort(self.world)
        receipt = port.expose("object", "beaker:001")
        value = _verify_observation(port, receipt)
        self.assertNotIn("xyz_mm", json.dumps(value["offered_payload"]))
        self.assertNotIn("100, 100", json.dumps(value["offered_payload"]))
        altered = dict(receipt)
        altered["offered_payload"] = {"object_id": "beaker:001", "condition": "intact"}
        with self.assertRaises(AdmissionError):
            _verify_observation(port, altered)

    def test_unknown_actor_and_unauthorized_action_denied(self):
        rev = self.world.verify()["revision"]
        with self.assertRaises(LabError):
            self.world.commit({"op": "erase", "object_id": "beaker:001"},
                              actor="pretorius_research")
        with self.assertRaises(LabError):
            self.world.commit({"op": "collect", "object_id": "beaker:001"},
                              actor="untrusted_network_actor")
        self.assertEqual(self.world.verify()["revision"], rev)

    def test_forged_action_receipt_not_admitted(self):
        action = {"op": "collect", "object_id": "beaker:001"}
        rev = self.world.verify()["revision"]
        real = self.world.commit(action, actor="pretorius_research",
                                 expected_revision=rev)
        bad = dict(real, event_hash="0" * 64)
        with self.assertRaises(AdmissionError):
            _admit_action(self.brain, self.world, bad, action,
                          "I collected the broken fragments.", rev)
        self.assertFalse(_has_attested_memory(self.brain, self.world, "collect"))
        self.assertNotIn("place", [x[0] for x in _options(
            self.world.observe()["objects"]["beaker:001"],
            collected_memory=False, floor_memory=False,
        )])

    def test_epoch_and_replay_guard(self):
        action = {"op": "collect", "object_id": "beaker:001"}
        rev = self.world.verify()["revision"]
        event = self.world.commit(action, actor="pretorius_research",
                                  expected_revision=rev)
        _admit_action(self.brain, self.world, event, action,
                      "I gathered the broken beaker fragments.", rev)
        self.assertTrue(_has_attested_memory(self.brain, self.world, "collect"))
        with self.assertRaises(AdmissionError):
            _admit_action(self.brain, self.world, event, action,
                          "I gathered the broken beaker fragments.", rev)


if __name__ == "__main__":
    unittest.main()
