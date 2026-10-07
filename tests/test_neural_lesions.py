from __future__ import annotations

import unittest

import numpy as np

from doctor_lives.neural import (
    NEURAL_CONVERGENCE_CONFIG,
    PretoriusRecurrentSubstrate,
)
from doctor_lives.neural_lesions import (
    CAUSAL_CORE_FRACTION,
    LESION_EVALUATION_STEPS,
    RELEARNING_BLOCKS,
    RELEARNING_STEPS,
    learned_recurrent_delta,
    matched_random_core,
    rank_causal_core,
    revert_learned_edges,
    transplant_full_delta,
    validate_lesion_protocol_surface,
    verify_recurrent_topology,
)


def _small_pair() -> tuple[
    PretoriusRecurrentSubstrate,
    PretoriusRecurrentSubstrate,
]:
    cfg = dict(NEURAL_CONVERGENCE_CONFIG)
    cfg.update(
        {
            "neurons": 64,
            "sensory_dim": 32,
            "avg_recurrent_degree": 6,
            "input_degree": 3,
            "action_population_size": 4,
            "spectral_homeostasis_mode": "off",
        }
    )
    stabilized = PretoriusRecurrentSubstrate(cfg)
    developed = PretoriusRecurrentSubstrate(cfg)
    verify_recurrent_topology(stabilized, developed)

    edge_is_exc = developed.excitatory[developed.pre_idx]
    signed_step = np.where(
        edge_is_exc, 0.001, -0.001
    ).astype(np.float32)
    scale = np.linspace(
        0.1,
        1.0,
        developed.W.data.size,
        dtype=np.float32,
    )
    developed.W.data[:] = (
        developed.W.data + signed_step * scale
    )
    developed._enforce_sign_and_bounds()
    return stabilized, developed


class NeuralLesionHarnessTests(unittest.TestCase):
    def test_protocol_surface_freezes_b06_choices(self):
        surface = validate_lesion_protocol_surface()
        self.assertEqual(
            surface["causal_core_fraction"],
            CAUSAL_CORE_FRACTION,
        )
        self.assertEqual(
            surface["lesion_evaluation_steps"],
            LESION_EVALUATION_STEPS,
        )
        self.assertEqual(
            surface["relearning_steps"],
            RELEARNING_STEPS,
        )
        self.assertEqual(
            surface["relearning_blocks"],
            RELEARNING_BLOCKS,
        )
        self.assertIn(
            "absolute developed-minus-stabilized",
            surface["causal_core_rank_metric"],
        )

    def test_learned_delta_and_full_reversion_are_exact(self):
        stabilized, developed = _small_pair()
        delta = learned_recurrent_delta(
            stabilized, developed
        )
        self.assertGreater(
            float(np.linalg.norm(delta)),
            0.0,
        )
        revert_learned_edges(developed, stabilized)
        self.assertTrue(
            np.array_equal(
                developed.W.data,
                stabilized.W.data,
            )
        )

    def test_full_delta_transplant_recovers_developed_weights(self):
        stabilized, developed = _small_pair()
        baseline, _ = _small_pair()
        baseline.W.data[:] = stabilized.W.data
        transplant_full_delta(
            baseline,
            stabilized,
            developed,
        )
        self.assertTrue(
            np.array_equal(
                baseline.W.data,
                developed.W.data,
            )
        )

    def test_causal_core_rank_is_deterministic_and_absolute(self):
        delta = np.asarray(
            [0.1, -0.8, 0.3, -0.4, 0.2],
            dtype=np.float32,
        )
        first = rank_causal_core(delta, fraction=0.4)
        second = rank_causal_core(
            delta.copy(), fraction=0.4
        )
        self.assertTrue(
            np.array_equal(first, second)
        )
        self.assertEqual(
            set(first.tolist()),
            {1, 3},
        )

    def test_random_control_is_size_ei_matched_and_disjoint(self):
        stabilized, developed = _small_pair()
        delta = learned_recurrent_delta(
            stabilized, developed
        )
        targeted = rank_causal_core(
            delta, fraction=0.10
        )
        random_a = matched_random_core(
            developed, targeted, 1842
        )
        random_b = matched_random_core(
            developed, targeted, 1842
        )
        self.assertTrue(
            np.array_equal(random_a, random_b)
        )
        self.assertEqual(
            len(random_a), len(targeted)
        )
        self.assertEqual(
            np.intersect1d(
                random_a, targeted
            ).size,
            0,
        )

        edge_is_exc = developed.excitatory[
            developed.pre_idx
        ]
        self.assertEqual(
            int(
                np.count_nonzero(
                    edge_is_exc[random_a]
                )
            ),
            int(
                np.count_nonzero(
                    edge_is_exc[targeted]
                )
            ),
        )

    def test_zero_edge_reversion_is_exact_noop(self):
        stabilized, developed = _small_pair()
        before = developed.W.data.copy()
        revert_learned_edges(
            developed,
            stabilized,
            np.asarray([], dtype=np.int64),
        )
        self.assertTrue(
            np.array_equal(
                developed.W.data,
                before,
            )
        )

    def test_partial_reversion_changes_only_selected_edges(self):
        stabilized, developed = _small_pair()
        before = developed.W.data.copy()
        selected = np.asarray(
            [0, 2, 4, 6],
            dtype=np.int64,
        )
        revert_learned_edges(
            developed,
            stabilized,
            selected,
        )
        self.assertTrue(
            np.array_equal(
                developed.W.data[selected],
                stabilized.W.data[selected],
            )
        )
        mask = np.ones(
            developed.W.data.size,
            dtype=bool,
        )
        mask[selected] = False
        self.assertTrue(
            np.array_equal(
                developed.W.data[mask],
                before[mask],
            )
        )


if __name__ == "__main__":
    unittest.main()
