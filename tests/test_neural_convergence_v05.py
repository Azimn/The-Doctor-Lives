from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.neural import (
    DEFAULT_CONFIG,
    NEURAL_CONVERGENCE_CONFIG,
    PretoriusRecurrentSubstrate,
)


def convergence_config() -> dict:
    cfg = dict(NEURAL_CONVERGENCE_CONFIG)
    cfg.update({
        "neurons": 96,
        "sensory_dim": 48,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 6,
        "plasticity_interval": 1,
        "spectral_check_interval": 1,
        "seed": 1842,
    })
    return cfg


class NeuralConvergenceTests(unittest.TestCase):
    def test_legacy_defaults_remain_the_accepted_v04_path(self):
        net = PretoriusRecurrentSubstrate({
            **DEFAULT_CONFIG,
            "neurons": 64,
            "sensory_dim": 32,
            "avg_recurrent_degree": 6,
            "input_degree": 3,
            "action_population_size": 4,
        })
        diagnostics = net.diagnostics()
        self.assertEqual(diagnostics["profile"], "legacy_v04")
        self.assertEqual(diagnostics["plasticity_rule"], "hebbian")
        self.assertFalse(diagnostics["neuromodulation_enabled"])
        self.assertFalse(diagnostics["synaptic_tagging_enabled"])
        self.assertEqual(diagnostics["spectral_homeostasis_mode"], "off")
        self.assertEqual(diagnostics["endogenous_noise"], 0.0)

    def test_neuromodulation_changes_write_gate_without_choosing_action(self):
        low = PretoriusRecurrentSubstrate(convergence_config())
        high = PretoriusRecurrentSubstrate(convergence_config())
        low.step("same observation", {"novelty": 0.0, "threat": 0.0, "arousal": 0.0}, confidence=.4)
        high.step(
            "same observation",
            {"novelty": 1.0, "threat": 1.0, "arousal": 1.0, "valence": -1.0},
            confidence=1.0,
        )
        self.assertGreater(
            float(high.diagnostics()["plastic_gate"]),
            float(low.diagnostics()["plastic_gate"]),
        )
        self.assertEqual(set(low.action_scores()), set(high.action_scores()))

    def test_oja_tagging_and_outcome_capture_preserve_dale_signs(self):
        net = PretoriusRecurrentSubstrate(convergence_config())
        before = net.W.data.copy()
        net.step(
            "A dangerous novel apparatus succeeds unexpectedly.",
            {"novelty": .9, "threat": .7, "arousal": .8, "valence": .6},
            confidence=.9,
        )
        tag_before = float(np.linalg.norm(net.synaptic_tags))
        self.assertGreater(tag_before, 0.0)
        report = net.capture_outcome(.8, confidence=.9)
        self.assertTrue(report["captured"])
        self.assertLess(float(np.linalg.norm(net.synaptic_tags)), tag_before)
        self.assertFalse(np.array_equal(before, net.W.data))
        exc = net.excitatory[net.pre_idx]
        self.assertTrue(np.all(net.W.data[exc] >= -1e-12))
        self.assertTrue(np.all(net.W.data[~exc] <= 1e-12))

    def test_banded_recurrent_homeostasis_recovers_from_forced_gain(self):
        net = PretoriusRecurrentSubstrate(convergence_config())
        net.W.data *= np.float32(8.0)
        before = net._estimate_recurrent_gain()
        after = net._renormalize_recurrent(force=True)
        self.assertGreater(before, float(net.cfg["max_spectral_radius"]))
        self.assertIsNotNone(after)
        self.assertLessEqual(float(after), float(net.cfg["max_spectral_radius"]) + .03)
        self.assertGreaterEqual(float(after), float(net.cfg["min_spectral_radius"]) - .03)
        self.assertGreater(net.homeostasis_events, 0)

    def test_noise_tags_gain_and_rng_survive_restart(self):
        cfg = convergence_config()
        first = PretoriusRecurrentSubstrate(cfg)
        first.step(
            "Novel social challenge.",
            {"novelty": .8, "social": .8, "threat": .2},
            confidence=.8,
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "brain.npz"
            first.save(path)
            second = PretoriusRecurrentSubstrate.load(path)
            self.assertTrue(np.allclose(first.noise_state, second.noise_state))
            self.assertTrue(np.allclose(first.synaptic_tags, second.synaptic_tags))
            self.assertAlmostEqual(first.state_gain, second.state_gain, places=12)
            self.assertEqual(first.homeostasis_events, second.homeostasis_events)
            scores_a = first.step("next identical observation", {"novelty": .3}, confidence=.7)
            scores_b = second.step("next identical observation", {"novelty": .3}, confidence=.7)
            for action in scores_a:
                self.assertAlmostEqual(scores_a[action], scores_b[action], places=10)

    def test_brain_outcome_path_captures_neural_tags_and_exposes_diagnostics(self):
        with tempfile.TemporaryDirectory() as td:
            brain = PretoriusBrain(Path(td), neural_config=convergence_config())
            brain.ingest(Experience(
                "The apparatus behaves in an unfamiliar and dangerous way.",
                novelty=.9,
                threat=.7,
                arousal=.7,
                confidence=.9,
            ))
            tag_before = float(np.linalg.norm(brain.neural.synaptic_tags))
            self.assertGreater(tag_before, 0.0)
            brain.record_action_outcome("create", True, .8)
            tag_after = float(np.linalg.norm(brain.neural.synaptic_tags))
            self.assertLess(tag_after, tag_before)
            status = brain.status()
            self.assertEqual(status["neural_diagnostics"]["profile"], "neural_convergence_v05")
            self.assertGreaterEqual(status["neural_diagnostics"]["homeostasis_events"], 0)


if __name__ == "__main__":
    unittest.main()
