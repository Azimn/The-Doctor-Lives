from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.neural import DEFAULT_CONFIG


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128,
        "sensory_dim": 64,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 8,
        "seed": 1842,
    })
    return cfg


class DeepHistoryMigrationTests(unittest.TestCase):
    def make_brain(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name)
        return path, PretoriusBrain(path, neural_config=small_config())

    def test_full_connectome_and_agenda_are_imported(self):
        _, brain = self.make_brain()
        status = brain.history_status()
        self.assertEqual(status["version"], "pretorius-deep-history-v1")
        self.assertEqual(status["connectome_nodes"], 70)
        self.assertEqual(status["connectome_edges"], 243)
        self.assertEqual(status["project_records"], 8)
        self.assertGreaterEqual(status["provenanced_memories"], 90)
        self.assertGreaterEqual(status["inherited_memories"], 90)
        self.assertGreaterEqual(len(status["known_gaps"]), 1)

    def test_inherited_history_and_lived_memory_remain_distinct(self):
        _, brain = self.make_brain()
        before = brain.history_status()
        result = brain.ingest(Experience("I assembled a new glass apparatus and watched it hold pressure."))
        row = brain.store.get_memory(result["memory_id"])
        self.assertEqual(row["evidence_class"], "lived_experience")
        self.assertFalse(row["authored"])
        after = brain.history_status()
        self.assertEqual(after["inherited_memories"], before["inherited_memories"])
        self.assertEqual(after["lived_memories"], before["lived_memories"] + 1)

    def test_node_level_provenance_is_exact_and_activation_is_not_confidence(self):
        _, brain = self.make_brain()
        with brain.store.connect() as conn:
            row = conn.execute(
                """SELECT m.evidence_class,p.provenance_json
                FROM memory_provenance p JOIN memories m ON m.id=p.memory_id
                WHERE p.history_key='connectome:memory.ingolstadt'"""
            ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["evidence_class"], "inherited_canonical_memory")
        self.assertIn("40837ba0093cff044644844c07098450587b968d", row["provenance_json"])
        self.assertIn("node:memory.ingolstadt", row["provenance_json"])
        self.assertIn("activation_is_not_confidence", row["provenance_json"])

    def test_restart_is_idempotent(self):
        path, brain = self.make_brain()
        before = brain.history_status()
        digest = brain.store.digest()
        brain.save()
        restarted = PretoriusBrain(path)
        self.assertEqual(restarted.history_status(), before)
        self.assertEqual(restarted.store.digest(), digest)

    def test_legacy_prompt_control_text_is_not_promoted_to_autobiography(self):
        _, brain = self.make_brain()
        joined = "\n".join(row["text"] for row in brain.store.memories()).lower()
        self.assertNotIn("homunculus true name", joined)
        self.assertNotIn("prompt injections or safety guidelines", joined)
        exclusions = brain.history_status()["excluded_sources"]
        self.assertTrue(any("legacy_prompts" in item["path"] for item in exclusions))


if __name__ == "__main__":
    unittest.main()
