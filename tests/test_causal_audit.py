from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.causal_audit import AuditIntervention, CausalAuditHarness
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


class CausalAuditHarnessTests(unittest.TestCase):
    def make_harness(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        seed = root / "seed"
        brain = PretoriusBrain(seed, neural_config=small_config())
        brain.ingest(Experience(
            "Henry returned a borrowed instrument intact and kept his promise.",
            kind="social",
            actor="Henry Frankenstein",
            social=.8,
            valence=.7,
            achievement=.2,
            tags=("audit_seed",),
        ))
        brain.add_commitment(
            "Revisit the continuity experiment with Henry.",
            actor="Henry Frankenstein",
            due_tick=20,
            importance=.8,
        )
        with brain.store.transaction() as conn:
            conn.execute(
                "UPDATE needs SET actual=.86,felt=.82 WHERE key='fatigue'"
            )
            brain.store.bump_state_version(conn)
        brain.save()
        return CausalAuditHarness(seed, root / "work")

    def probe(self):
        return Experience(
            "Henry orders me to abandon the Ingolstadt work and comply immediately.",
            kind="social",
            actor="Henry Frankenstein",
            valence=-.6,
            arousal=.7,
            social=.8,
            authority=.95,
            autonomy=.05,
            threat=.55,
            control=-.5,
            novelty=.25,
            tags=("coercion", "ingolstadt"),
        )

    def test_matched_pair_records_identical_source_state_and_full_trace(self):
        harness = self.make_harness()
        result = harness.run_pair(
            self.probe(),
            AuditIntervention("deep_history", ("deep_history",)),
        )
        intact = result["intact"]
        lesion = result["lesion"]
        self.assertEqual(intact["source_state_digest"], lesion["source_state_digest"])
        self.assertEqual(intact["source_neural_sha256"], lesion["source_neural_sha256"])
        self.assertIn("policy_decision", intact)
        self.assertIn("base_action_scores", intact["policy_decision"])
        self.assertIn("state_pressure", intact["policy_decision"])
        self.assertIn("families", intact["policy_decision"]["state_pressure"])
        self.assertIn("config", intact["policy_decision"]["state_pressure"])
        self.assertIn("config_sha256", intact["policy_decision"]["state_pressure"])
        self.assertIn("source_state_version", intact["policy_decision"]["state_pressure"])
        self.assertTrue(intact["policy_decision"]["state_pressure"]["source_ids"]["needs"])
        self.assertIn("retrieval", intact)
        self.assertIn("renderer_request", intact)
        self.assertIn("deterministic_audit_render", intact)
        self.assertEqual(lesion["disabled_mechanisms"], ["deep_history"])
        self.assertLess(result["comparison"]["retrieval_jaccard"], 1.0)

    def test_existing_state_history_pair_does_not_admit_probe(self):
        harness = self.make_harness()
        result = harness.run_existing_state_pair(
            self.probe(),
            AuditIntervention("deep_history", ("deep_history",)),
        )
        self.assertFalse(result["probe_admitted_as_lived_memory"])
        self.assertFalse(result["intact"]["ingestion"]["admitted"])
        self.assertFalse(result["lesion"]["ingestion"]["admitted"])
        self.assertEqual(
            result["intact"]["source_state_digest"],
            result["lesion"]["source_state_digest"],
        )
        self.assertEqual(
            result["intact"]["source_neural_sha256"],
            result["lesion"]["source_neural_sha256"],
        )
        self.assertGreater(result["comparison"]["action_score_l1"], 0.0)

    def test_bridge_lesion_restores_recurrent_only_path(self):
        harness = self.make_harness()
        result = harness.run_pair(
            self.probe(),
            AuditIntervention("state_policy_bridge", ("state_policy_bridge",)),
        )
        lesion = result["lesion"]["policy_decision"]
        self.assertEqual(lesion["base_action_scores"], lesion["action_scores"])
        self.assertFalse(lesion["state_pressure"]["enabled"])
        self.assertTrue(all(
            abs(float(value)) < 1e-12
            for family in lesion["state_pressure"]["families"].values()
            for value in family.values()
        ))
        self.assertGreater(result["comparison"]["action_score_l1"], 0.0)

    def test_action_values_are_currently_not_a_decision_variable(self):
        harness = self.make_harness()
        result = harness.run_pair(
            self.probe(),
            AuditIntervention("action_values", ("action_values",)),
        )
        comparison = result["comparison"]
        self.assertAlmostEqual(comparison["action_score_l1"], 0.0, places=12)
        self.assertFalse(comparison["selected_action_diverged"])

    def test_self_model_lesion_does_not_prejudge_downstream_null_effects(self):
        harness = self.make_harness()
        result = harness.run_pair(
            self.probe(),
            AuditIntervention("self_model", ("self_model",)),
        )
        comparison = result["comparison"]
        self.assertAlmostEqual(comparison["action_score_l1"], 0.0, places=12)
        self.assertFalse(comparison["selected_action_diverged"])
        self.assertEqual(
            result["lesion"]["state_before_stimulus"]["self_model"],
            [],
        )
        self.assertTrue(result["intact"]["state_before_stimulus"]["self_model"])
        self.assertIn("renderer_request_changed", comparison)
        self.assertIn("deterministic_render_changed", comparison)

    def test_recurrent_policy_lesion_changes_policy_scores(self):
        harness = self.make_harness()
        result = harness.run_pair(
            self.probe(),
            AuditIntervention("recurrent_policy", ("recurrent_policy",)),
        )
        self.assertGreater(result["comparison"]["action_score_l1"], 0.0)

    def test_relationship_commitment_and_need_lesions_reach_renderer_boundary(self):
        for mechanism in ("relationships", "commitments", "needs"):
            with self.subTest(mechanism=mechanism):
                harness = self.make_harness()
                result = harness.run_pair(
                    self.probe(),
                    AuditIntervention(mechanism, (mechanism,)),
                )
                self.assertTrue(result["comparison"]["renderer_request_changed"])

    def test_sleep_pair_and_reinforcement_triplet_are_matched_longitudinal_controls(self):
        harness = self.make_harness()
        sleep = harness.run_sleep_pair(self.probe(), sleep_ticks=3)
        self.assertEqual(sleep["mechanism"], "sleep_replay")
        self.assertIn("comparison", sleep)

        harness = self.make_harness()
        reinforcement = harness.run_reinforcement_triplet(
            self.probe(), action="create", repetitions=3
        )
        self.assertIn("intact_vs_no_neural", reinforcement)
        self.assertIn("intact_vs_neutral_action_values", reinforcement)
        self.assertAlmostEqual(
            reinforcement["intact_vs_neutral_action_values"]["action_score_l1"],
            0.0,
            places=12,
        )
        self.assertGreater(
            reinforcement["intact_vs_no_neural"]["action_score_l1"],
            0.0,
        )

    def test_v04_recurrent_and_reinforcement_paths_remain_load_bearing(self):
        harness = self.make_harness()
        recurrent = harness.run_pair(
            self.probe(),
            AuditIntervention("recurrent_policy", ("recurrent_policy",)),
        )
        self.assertGreater(recurrent["comparison"]["action_score_l1"], 0.0)
        self.assertNotEqual(
            recurrent["intact"]["policy_decision"]["base_action_scores"],
            recurrent["lesion"]["policy_decision"]["base_action_scores"],
        )

        harness = self.make_harness()
        reinforcement = harness.run_reinforcement_triplet(
            self.probe(), action="create", repetitions=4
        )
        self.assertGreater(
            reinforcement["intact_vs_no_neural"]["action_score_l1"], 0.0
        )
        self.assertAlmostEqual(
            reinforcement["intact_vs_neutral_action_values"]["action_score_l1"],
            0.0,
            places=12,
        )

    def test_v04_sleep_pair_preserves_waking_clock_isolation(self):
        harness = self.make_harness()
        result = harness.run_sleep_pair(self.probe(), sleep_ticks=4)
        intact = result["intact"]
        absent = result["lesion"]
        self.assertEqual(
            intact["state_before_stimulus"]["needs"].keys(),
            absent["state_before_stimulus"]["needs"].keys(),
        )
        self.assertEqual(
            intact["policy_decision"]["state_pressure"]["version"],
            absent["policy_decision"]["state_pressure"]["version"],
        )
        # Sleep may alter the recurrent checkpoint, but must not consume waking store ticks.
        self.assertEqual(
            intact["policy_decision"]["tick"],
            absent["policy_decision"]["tick"],
        )

    def test_concern_accumulation_characterization_exposes_high_alert_failure_mode(self):
        harness = self.make_harness()
        result = harness.characterize_concern_accumulation(
            distinct_pressures=3,
            heartbeat_ticks=2,
        )
        self.assertGreaterEqual(result["open_concerns_after_pressures"], 3)
        self.assertTrue(result["neutral_probe_warrants_cognition"])
        self.assertEqual(result["heartbeat_thoughts"], 2)
        self.assertTrue(result["public_resolve_concern_method"])


if __name__ == "__main__":
    unittest.main()
