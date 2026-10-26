"""Frozen, dependency-light D0 controls for the six-organ migration.

These tests exercise the existing canonical runtime. They do NOT demonstrate
that Sensus, Affectus, Corpus or global Ipseity are production-integrated.
"""
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.cognition import PretoriusBrain
from doctor_lives.models import (
    EngineerAuditCapability,
    Experience,
    SubjectFrame,
    SubjectRendererCapability,
)
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.store import SCHEMA_VERSION


def baseline_config():
    config = dict(DEFAULT_CONFIG)
    config.update(
        neurons=128,
        sensory_dim=64,
        avg_recurrent_degree=8,
        input_degree=4,
        action_population_size=8,
        seed=1842,
    )
    return config


class SixOrganD0BaselineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_legacy_canonical_state_and_donor_remain_separate(self):
        port = PretoriusBrainPort(self.root, neural_config=baseline_config())
        self.assertEqual(SCHEMA_VERSION, 7)
        self.assertEqual(port.status()["subject"], "Doctor Septimus Pretorius")
        self.assertFalse((self.root / "synthetic_ipseity.sqlite3").exists())
        result = port.ingest({
            "channel": "world",
            "text": "A clock sounds somewhere beyond the closed door.",
            "source": "bounded-world-percept",
            "novelty": 0.6,
        })
        self.assertTrue(result["memory_id"])
        self.assertTrue(result["ingress"]["subject_text"])
        port.save()
        first = port.status()
        restored = PretoriusBrainPort(self.root)
        second = restored.status()
        self.assertEqual(first["state_digest"], second["state_digest"])
        self.assertEqual(first["tick"], second["tick"])
        self.assertFalse((self.root / "synthetic_ipseity.sqlite3").exists())

    def test_engineer_audit_cannot_be_read_with_subject_capability(self):
        brain = PretoriusBrain(self.root, neural_config=baseline_config())
        brain.ingest(Experience(
            "I heard something move on the other side of the wall.",
            source="heard-percept", novelty=0.5,
        ))
        request = brain.render_request("What did I hear?")
        audit = brain.render_audit_envelope()
        subject = SubjectRendererCapability.read(request.subject_frame)
        self.assertTrue(subject)
        self.assertTrue(all(isinstance(x, str) for x in subject))
        forbidden = ("private_state_version", "state_pressure",
                     "action_scores", "source_record_ids", "evidence_class")
        self.assertTrue(all(
            word not in "\n".join(subject) for word in forbidden
        ))
        with self.assertRaises(TypeError):
            SubjectRendererCapability.read(audit)
        with self.assertRaises(TypeError):
            EngineerAuditCapability.read(request.subject_frame)
        self.assertIn("private_state_version",
                      EngineerAuditCapability.read(audit))

    def test_host_typed_projection_keeps_engineer_diagnostics_off_access_seam(self):
        port = PretoriusBrainPort(self.root, neural_config=baseline_config())
        port.ingest({
            "channel": "body",
            "signal": "cold",
            "level": 0.86,
            "payload": {"temperature_c": 13.2},
            "source": "thermal_sensor",
        })
        before = port.brain.store.digest()
        # Model callbacks must not need access to privileged engineer views.
        with patch.object(
            port.brain, "render_audit_envelope",
            side_effect=AssertionError("engineer path invoked"),
        ):
            frame = port.subject_frame("What did I notice when I felt cold?")
        self.assertIsInstance(frame, SubjectFrame)
        lines = SubjectRendererCapability.read(frame)
        self.assertTrue(lines)
        self.assertTrue(any("cold" in line.lower() for line in lines))
        rendered = "\n".join(lines)
        for token in (
            "temperature_c", "thermal_sensor", "13.2",
            "state_version", "action_scores", "source_record_ids",
        ):
            self.assertNotIn(token, rendered)
        self.assertEqual(before, port.brain.store.digest())
        self.assertNotIsInstance(frame, dict)

    def test_external_testimony_is_not_reclassified_as_lived_fact(self):
        brain = PretoriusBrain(self.root, neural_config=baseline_config())
        outcome = brain.ingest(Experience(
            "Someone claimed that I saw a vessel shatter, but I did not see it.",
            source="unverified-testimony",
            kind="social",
            external=True,
        ))
        record = brain.store.get_memory(outcome["memory_id"])
        self.assertEqual(record["evidence_class"], "external_statement")
        self.assertTrue(record["external"])
        brain.save()
        restored = PretoriusBrain(self.root)
        after = restored.store.get_memory(outcome["memory_id"])
        self.assertEqual(after["evidence_class"], "external_statement")
        self.assertTrue(after["external"])

    def test_neural_selector_stays_causally_active_under_motive_pressure(self):
        brain = PretoriusBrain(self.root, neural_config=baseline_config())
        with brain.store.transaction() as conn:
            conn.execute("UPDATE needs SET actual=.5,felt=.5")
            conn.execute(
                "UPDATE needs SET actual=.9,felt=.9 WHERE key='autonomy'"
            )
            conn.execute("DELETE FROM relationships")
            conn.execute("DELETE FROM commitments")
            conn.execute("DELETE FROM concerns")
            brain.store.bump_state_version(conn)
        base, adjusted, audit = brain._state_policy_scores([])
        self.assertGreater(adjusted["challenge"], base["challenge"])
        self.assertLess(adjusted["comply"], base["comply"])
        self.assertGreater(audit["families"]["needs"]["challenge"], 0)
        self.assertGreater(audit["families"]["needs"]["comply"] * -1, 0)
        self.assertEqual(set(base), set(adjusted))


if __name__ == "__main__":
    unittest.main()
