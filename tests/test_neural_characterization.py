from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from doctor_lives.neural import ACTIONS, PretoriusRecurrentSubstrate
from doctor_lives.neural_characterization import (
    DECISIVE_SEEDS,
    DEVELOPMENT_BLOCK_LENGTH,
    PHASE_LENGTHS,
    PRODUCTION_NEURONS,
    PROTOCOL_TIMELINE_STEPS,
    PROBE_KINDS,
    _anchor_probes,
    _development_block,
    _run_rows,
    action_metrics,
    build_schedule,
    developmental_exposure,
    evaluation_probes,
    jensen_shannon_divergence,
    neutral_stabilization,
    profile_config,
    representational_summary,
    sha256_json,
    validate_protocol_surface,
    write_precommitted_schedule,
)


class NeuralCharacterizationHarnessTests(unittest.TestCase):
    def test_frozen_protocol_surface_matches_b02(self):
        surface = validate_protocol_surface()
        self.assertEqual(tuple(surface["seeds"]), DECISIVE_SEEDS)
        self.assertEqual(
            PHASE_LENGTHS,
            {
                "neutral_stabilization": 512,
                "developmental_exposure": 3584,
                "evaluation": 512,
                "restart_evaluation": 512,
            },
        )
        self.assertEqual(PROTOCOL_TIMELINE_STEPS, 5120)
        self.assertEqual(surface["profiles"]["legacy_v04"]["neurons"], PRODUCTION_NEURONS)
        self.assertEqual(
            surface["profiles"]["neural_convergence_v05"]["neurons"],
            PRODUCTION_NEURONS,
        )
        self.assertEqual(
            surface["profiles"]["legacy_v04"]["plasticity_rule"], "hebbian"
        )
        self.assertEqual(
            surface["profiles"]["neural_convergence_v05"]["plasticity_rule"], "oja"
        )

    def test_decisive_profile_rejects_unregistered_seed(self):
        with self.assertRaisesRegex(ValueError, "not preregistered"):
            profile_config("legacy_v04", 9999)

    def test_schedule_is_deterministic_balanced_and_complete(self):
        first = build_schedule(1842)
        second = build_schedule(1842)
        other = build_schedule(1843)
        self.assertEqual(first, second)
        self.assertEqual(first["curriculum_sha256"], second["curriculum_sha256"])
        self.assertNotEqual(first["curriculum_sha256"], other["curriculum_sha256"])
        self.assertEqual(len(first["neutral_stabilization"]), 512)
        self.assertEqual(len(first["developmental_exposure"]), 3584)
        self.assertEqual(len(first["evaluation_probes"]), 512)
        for block_index in range(7):
            block = _development_block(1842, block_index)
            self.assertEqual(len(block), DEVELOPMENT_BLOCK_LENGTH)
            counts = {
                name: sum(row.outcome_class == name for row in block)
                for name in ("positive", "negative", "neutral", "ambiguous")
            }
            self.assertEqual(counts, {
                "positive": 128,
                "negative": 128,
                "neutral": 128,
                "ambiguous": 128,
            })
        probes = evaluation_probes(1842)
        self.assertEqual(
            {kind: sum(row.probe_kind == kind for row in probes) for kind in PROBE_KINDS},
            {kind: 128 for kind in PROBE_KINDS},
        )

    def test_schedule_is_written_before_runtime_and_hashes_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "schedule.json"
            schedule = write_precommitted_schedule(1842, path)
            self.assertTrue(path.is_file())
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded, schedule)
            self.assertEqual(
                loaded["curriculum_sha256"],
                sha256_json({
                    "neutral_stabilization": loaded["neutral_stabilization"],
                    "developmental_exposure": loaded["developmental_exposure"],
                    "evaluation_probes": loaded["evaluation_probes"],
                }),
            )

    def test_action_metrics_and_js_are_normalized(self):
        uniform = {action: 1.0 / len(ACTIONS) for action in ACTIONS}
        peaked = {action: 0.0 for action in ACTIONS}
        peaked[ACTIONS[0]] = 1.0
        metrics = action_metrics(uniform)
        self.assertAlmostEqual(metrics["entropy_normalized"], 1.0, places=10)
        self.assertAlmostEqual(jensen_shannon_divergence(uniform, uniform), 0.0)
        divergence = jensen_shannon_divergence(uniform, peaked)
        self.assertGreater(divergence, 0.0)
        self.assertLessEqual(divergence, 1.0)

    def test_restart_probe_path_is_exact_on_small_nondecisive_network(self):
        cfg = profile_config("neural_convergence_v05", 1842)
        cfg.update({
            "neurons": 64,
            "sensory_dim": 32,
            "avg_recurrent_degree": 6,
            "input_degree": 3,
            "action_population_size": 4,
            "plasticity_interval": 1,
            "spectral_check_interval": 1,
        })
        net = PretoriusRecurrentSubstrate(cfg)
        dev = developmental_exposure(1842)[:16]
        _run_rows(net, dev, learn=True, apply_outcomes=True)
        probes = evaluation_probes(1842)[:16]
        with tempfile.TemporaryDirectory() as td:
            checkpoint = Path(td) / "developed.npz"
            net.save(checkpoint)
            left_records, left_states = _run_rows(
                net, probes, learn=False, apply_outcomes=False, capture_states=True
            )
            restored = PretoriusRecurrentSubstrate.load(checkpoint)
            right_records, right_states = _run_rows(
                restored, probes, learn=False, apply_outcomes=False, capture_states=True
            )
        self.assertEqual(left_records, right_records)
        self.assertTrue(np.array_equal(left_states, right_states))

    def test_representation_metric_definition_is_deterministic(self):
        probes = evaluation_probes(1842)[:16]
        states = np.arange(16 * 8, dtype=np.float32).reshape(16, 8)
        first = representational_summary(states, probes)
        second = representational_summary(states.copy(), probes)
        self.assertEqual(first, second)
        self.assertGreaterEqual(first["covariance_participation_ratio"], 0.0)

    def test_anchor_set_covers_each_available_family_kind_pair(self):
        probes = evaluation_probes(1842)
        anchors = _anchor_probes(probes)
        keys = {(row.block, row.probe_kind) for row in anchors}
        self.assertEqual(len(keys), len(anchors))
        self.assertGreaterEqual(len({row.block for row in anchors}), 6)
        self.assertEqual({row.probe_kind for row in anchors}, set(PROBE_KINDS))

    def test_phase_generators_keep_protocol_lengths(self):
        self.assertEqual(len(neutral_stabilization(1842)), 512)
        self.assertEqual(len(developmental_exposure(1842)), 3584)
        self.assertEqual(len(evaluation_probes(1842)), 512)


if __name__ == "__main__":
    unittest.main()
