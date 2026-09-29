import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from doctor_lives.cognition import PretoriusBrain
from doctor_lives.models import Experience
from doctor_lives.neural import DEFAULT_CONFIG


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128,
        "sensory_dim": 64,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 8,
        "plasticity_interval": 2,
    })
    return cfg


class BrainIntegrationTests(unittest.TestCase):
    def make_brain(self):
        tmp = tempfile.TemporaryDirectory()
        brain = PretoriusBrain(Path(tmp.name), neural_config=small_config())
        self.addCleanup(tmp.cleanup)
        return brain

    def test_calibos_is_structure_only(self):
        brain = self.make_brain()
        self.assertNotIn("calibos", json.dumps(brain.bootstrap).lower())
        for memory in brain.store.memories():
            payload = (memory["text"] + " " + memory["source"]).lower()
            self.assertNotIn("calibos", payload)

    def test_bad_bootstrap_boundary_fails_closed(self):
        brain = self.make_brain()
        original = brain.bootstrap
        brain.bootstrap = dict(original)
        brain.bootstrap["identity"] = list(original["identity"]) + ["I am Calibos."]
        with self.assertRaises(RuntimeError):
            brain._validate_bootstrap_boundary()

    def test_neural_policy_changes_attention_and_is_audited(self):
        brain = self.make_brain()
        tick = brain.store.tick
        with brain.store.transaction() as conn:
            create_id = brain.store.add_memory(
                conn, tick,
                "The homunculi design suggests a new creation experiment.",
                "test", "episode", "lived_experience", False, 1.0, False, 1.0,
                ("creation", "experiment"),
            )
            challenge_id = brain.store.add_memory(
                conn, tick,
                "An authority is using control and coercion to force compliance.",
                "test", "episode", "lived_experience", False, 1.0, False, 1.0,
                ("authority", "coercion", "control"),
            )
            brain.store.bump_state_version(conn)

        create_scores = {a: 0.01 for a in brain.neural.action_scores()}
        create_scores["create"] = 0.91
        brain.neural.action_scores = lambda: dict(create_scores)
        create_thought = brain.think("test-create")

        challenge_scores = {a: 0.01 for a in create_scores}
        challenge_scores["challenge"] = 0.91
        brain.neural.action_scores = lambda: dict(challenge_scores)
        challenge_thought = brain.think("test-challenge")

        self.assertEqual(create_thought["selected_action"], "create")
        self.assertEqual(challenge_thought["selected_action"], "challenge")
        self.assertEqual(create_thought["source_record_ids"][0], create_id)
        self.assertEqual(challenge_thought["source_record_ids"][0], challenge_id)

        with sqlite3.connect(brain.store.path) as conn:
            rows = conn.execute(
                "SELECT selected_action,selected_record_ids_json,policy_version "
                "FROM policy_decisions ORDER BY rowid"
            ).fetchall()
        self.assertEqual([row[0] for row in rows[-2:]], ["create", "challenge"])
        self.assertEqual(rows[-1][2], "neural-cognitive-policy-v1")

    def test_sleep_does_not_advance_waking_tick(self):
        brain = self.make_brain()
        brain.ingest(Experience("A quiet laboratory observation.", novelty=0.1))
        before = brain.store.tick
        result = brain.sleep(4)
        self.assertEqual(brain.store.tick, before)
        self.assertEqual(result["store_tick"], before)

    def test_restart_preserves_continuity(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name)
        brain = PretoriusBrain(path, neural_config=small_config())
        brain.ingest(Experience(
            "A collaborator kept a difficult promise.",
            actor="Morgan", kind="interaction", social=0.8, valence=0.7,
        ))
        brain.add_commitment("Revisit the result after another observation.", actor="Morgan")
        brain.save()
        before = brain.status()

        restored = PretoriusBrain(path)
        after = restored.status()
        self.assertEqual(before["tick"], after["tick"])
        self.assertEqual(before["state_digest"], after["state_digest"])
        self.assertEqual(before["open_commitments"], after["open_commitments"])
        self.assertEqual(before["relationships"], after["relationships"])

    def test_renderer_request_is_read_only(self):
        brain = self.make_brain()
        before = brain.store.digest()
        request = brain.render_request("Explain the current problem.")
        after = brain.store.digest()
        self.assertEqual(before, after)
        self.assertEqual(request.schema, "the-doctor-lives.render-request.v1")

    def test_frozen_and_mutable_surfaces_are_declared(self):
        brain = self.make_brain()
        policy = brain.evolution_policy
        self.assertIn("calibos_structure_only_no_identity_or_memory", policy["frozen"])
        self.assertIn("neural_policy_decision_audit", policy["frozen"])
        self.assertIn("recurrent_weights_and_fast_state", policy["mutable"])


if __name__ == "__main__":
    unittest.main()
