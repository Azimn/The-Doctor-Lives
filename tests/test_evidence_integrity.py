from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from doctor_lives import EvidenceIntegrityError, Experience, PretoriusBrain
from doctor_lives.neural import DEFAULT_CONFIG


def small_config() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 64,
        "sensory_dim": 32,
        "avg_recurrent_degree": 6,
        "input_degree": 3,
        "action_population_size": 5,
        "seed": 1842,
    })
    return cfg


class CanonicalEvidenceAuthorityTests(unittest.TestCase):
    def make_brain(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        state = Path(tmp.name)
        return state, PretoriusBrain(state, neural_config=small_config())

    def test_initial_adoption_is_versioned_verified_and_restart_idempotent(self):
        state, brain = self.make_brain()
        first = brain.status()["canonical_evidence"]
        self.assertEqual(first["manifest_version"], 1)
        self.assertTrue(first["distribution_snapshot_verified"])
        self.assertIn("bootstrap", first["artifact_ids"])
        self.assertEqual(brain.store.meta("canonical_evidence_manifest_version"), "1")
        self.assertEqual(
            brain.store.meta("canonical_evidence_manifest_fingerprint"),
            first["manifest_fingerprint"],
        )
        restarted = PretoriusBrain(state)
        second = restarted.status()["canonical_evidence"]
        self.assertEqual(first["snapshot_id"], second["snapshot_id"])
        self.assertEqual(first["manifest_fingerprint"], second["manifest_fingerprint"])

    def test_modified_active_evidence_fails_closed(self):
        state, brain = self.make_brain()
        path = brain.evidence.artifact_path("bootstrap")
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaisesRegex(EvidenceIntegrityError, "bootstrap"):
            PretoriusBrain(state)

    def test_missing_active_evidence_fails_closed(self):
        state, brain = self.make_brain()
        brain.evidence.artifact_path("deep_history").unlink()
        with self.assertRaisesRegex(EvidenceIntegrityError, "deep_history"):
            PretoriusBrain(state)

    def test_manifest_rollback_in_active_pointer_fails_closed(self):
        state, brain = self.make_brain()
        pointer_path = brain.evidence.active_pointer_path
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        pointer["manifest_version"] = 0
        pointer_path.write_text(
            json.dumps(pointer, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(EvidenceIntegrityError, "rollback"):
            PretoriusBrain(state)

    def test_interrupted_staging_is_discarded_before_initial_adoption(self):
        with tempfile.TemporaryDirectory() as td:
            state = Path(td)
            staging = state / "evidence_authority" / "snapshots" / ".staging-interrupted"
            staging.mkdir(parents=True)
            (staging / "partial.json").write_text("partial", encoding="utf-8")
            brain = PretoriusBrain(state, neural_config=small_config())
            self.assertFalse(staging.exists())
            self.assertEqual(brain.status()["canonical_evidence"]["manifest_version"], 1)

    def test_protected_reference_must_match_admitted_digest(self):
        _, brain = self.make_brain()
        bootstrap = next(
            item for item in brain.evidence.manifest["artifacts"]
            if item["id"] == "bootstrap"
        )
        expected = bootstrap["git_blob_sha1"]
        self.assertTrue(brain.evidence.verify_reference("bootstrap", expected))
        with self.assertRaisesRegex(EvidenceIntegrityError, "digest mismatch"):
            brain.evidence.verify_reference("bootstrap", "0" * 40)
        with self.assertRaisesRegex(EvidenceIntegrityError, "unknown artifact"):
            brain.evidence.verify_reference("invented", "0" * 40)

    def test_explicit_recovery_is_append_only_and_preserves_cognitive_state(self):
        state, brain = self.make_brain()
        brain.ingest(Experience(
            "A collaborator kept a difficult promise.",
            actor="Morgan",
            kind="interaction",
            social=0.8,
            valence=0.7,
        ))
        brain.add_commitment(
            "Revisit the evidence after another observation.",
            actor="Morgan",
        )
        brain.save()
        digest_before = brain.store.digest()
        tick_before = brain.store.tick
        old_snapshot = brain.evidence.active_snapshot_id
        old_root = brain.evidence.active_root

        history_path = brain.evidence.artifact_path("deep_history")
        history_path.write_text("corrupted", encoding="utf-8")

        recovery = PretoriusBrain.recover_canonical_evidence(
            state,
            reason="test recovery after deliberate active-snapshot corruption",
        )
        self.assertEqual(recovery["parent_snapshot_id"], old_snapshot)
        self.assertNotEqual(recovery["snapshot_id"], old_snapshot)
        self.assertTrue(old_root.exists())
        self.assertEqual(history_path.read_text(encoding="utf-8"), "corrupted")

        restored = PretoriusBrain(state)
        self.assertEqual(restored.store.tick, tick_before)
        self.assertEqual(restored.store.digest(), digest_before)
        self.assertEqual(restored.evidence.active_snapshot_id, recovery["snapshot_id"])
        self.assertTrue(restored.evidence.artifact_path("deep_history").is_file())

    def test_partial_store_binding_fails_closed(self):
        state, brain = self.make_brain()
        with brain.store.transaction() as conn:
            conn.execute(
                "DELETE FROM meta WHERE key='canonical_evidence_manifest_fingerprint'"
            )
        with self.assertRaisesRegex(RuntimeError, "partially bound"):
            PretoriusBrain(state)


if __name__ == "__main__":
    unittest.main()
