from __future__ import annotations

import unittest

import numpy as np

from doctor_lives.neural import (
    DEFAULT_CONFIG,
    NEURAL_CONVERGENCE_CONFIG,
    PretoriusRecurrentSubstrate,
)
from doctor_lives.neural_lesions import (
    learned_recurrent_delta,
    rank_causal_core,
    verify_recurrent_topology,
)
from doctor_lives.neural_robustness import (
    DELTA_CLIP_QUANTILES,
    HIGH_CHANGE_FRACTION,
    MODEST_WEIGHT_PERTURBATION_FRACTION,
    RECURRENT_WEIGHT_CLIP_QUANTILES,
    apply_delta,
    clip_delta_by_quantile,
    clip_recurrent_weights,
    ordinary_edge_indices,
    permute_delta_within_ei,
    perturb_recurrent_weights,
    project_delta_by_weight_quantile,
    validate_robustness_protocol_surface,
    verify_sign_contract,
)


def _cfg(seed: int = 1842, convergence: bool = True) -> dict:
    cfg = dict(
        NEURAL_CONVERGENCE_CONFIG if convergence else DEFAULT_CONFIG
    )
    cfg.update(
        {
            "neurons": 64,
            "sensory_dim": 32,
            "avg_recurrent_degree": 6,
            "input_degree": 3,
            "action_population_size": 4,
            "spectral_homeostasis_mode": "off",
            "seed": seed,
        }
    )
    return cfg


def _small_pair(
    seed: int = 1842,
) -> tuple[
    PretoriusRecurrentSubstrate,
    PretoriusRecurrentSubstrate,
]:
    stabilized = PretoriusRecurrentSubstrate(_cfg(seed))
    developed = PretoriusRecurrentSubstrate(_cfg(seed))
    verify_recurrent_topology(stabilized, developed)
    edge_is_exc = developed.excitatory[developed.pre_idx]
    direction = np.where(
        edge_is_exc, 1.0, -1.0
    ).astype(np.float32)
    scale = np.linspace(
        0.00001,
        0.002,
        developed.W.data.size,
        dtype=np.float32,
    )
    developed.W.data[:] = (
        developed.W.data + direction * scale
    )
    developed._enforce_sign_and_bounds()
    return stabilized, developed


class NeuralRobustnessHarnessTests(unittest.TestCase):
    def test_protocol_surface_freezes_b07_choices(self):
        surface = validate_robustness_protocol_surface()
        self.assertEqual(
            surface["high_change_fraction"],
            HIGH_CHANGE_FRACTION,
        )
        self.assertEqual(
            tuple(surface["recurrent_weight_clip_quantiles"]),
            RECURRENT_WEIGHT_CLIP_QUANTILES,
        )
        self.assertEqual(
            tuple(surface["delta_clip_quantiles"]),
            DELTA_CLIP_QUANTILES,
        )
        self.assertEqual(
            surface["modest_weight_perturbation_fraction"],
            MODEST_WEIGHT_PERTURBATION_FRACTION,
        )
        self.assertIn(
            "next decisive seed",
            surface["independent_seed_rule"],
        )

    def test_ei_permutation_preserves_exact_stratified_multiset(self):
        stabilized, developed = _small_pair()
        delta = learned_recurrent_delta(
            stabilized, developed
        )
        first = permute_delta_within_ei(
            delta, stabilized, 1842
        )
        second = permute_delta_within_ei(
            delta, stabilized, 1842
        )
        self.assertTrue(
            np.array_equal(first, second)
        )
        edge_is_exc = stabilized.excitatory[
            stabilized.pre_idx
        ]
        for is_exc in (True, False):
            self.assertTrue(
                np.array_equal(
                    np.sort(delta[edge_is_exc == is_exc]),
                    np.sort(first[edge_is_exc == is_exc]),
                )
            )

    def test_ordinary_edges_are_size_and_ei_matched_but_not_high_change(self):
        stabilized, developed = _small_pair()
        delta = learned_recurrent_delta(
            stabilized, developed
        )
        high = rank_causal_core(
            delta, fraction=0.10
        )
        ordinary = ordinary_edge_indices(
            delta, developed, high
        )
        self.assertEqual(
            high.size, ordinary.size
        )
        self.assertEqual(
            np.intersect1d(high, ordinary).size,
            0,
        )
        edge_is_exc = developed.excitatory[
            developed.pre_idx
        ]
        self.assertEqual(
            int(np.count_nonzero(edge_is_exc[high])),
            int(np.count_nonzero(edge_is_exc[ordinary])),
        )
        self.assertLess(
            float(np.median(np.abs(delta[ordinary]))),
            float(np.median(np.abs(delta[high]))),
        )

    def test_topology_matched_delta_application_is_exact_when_contract_not_hit(self):
        stabilized, developed = _small_pair()
        recipient = PretoriusRecurrentSubstrate(
            _cfg(1842, convergence=False)
        )
        verify_recurrent_topology(
            stabilized, recipient
        )
        delta = learned_recurrent_delta(
            stabilized, developed
        )
        before = recipient.W.data.copy()
        metadata = apply_delta(
            recipient, delta
        )
        self.assertEqual(
            metadata["contract_adjusted_edge_count"],
            0,
        )
        self.assertTrue(
            np.array_equal(
                recipient.W.data,
                before + delta,
            )
        )
        self.assertTrue(
            verify_sign_contract(recipient)["pass"]
        )

    def test_independent_topology_projection_is_finite_and_target_shaped(self):
        stabilized, developed = _small_pair(1842)
        recipient = PretoriusRecurrentSubstrate(
            _cfg(1843, convergence=False)
        )
        projected = project_delta_by_weight_quantile(
            stabilized, developed, recipient
        )
        self.assertEqual(
            projected.shape,
            recipient.W.data.shape,
        )
        self.assertTrue(
            np.all(np.isfinite(projected))
        )
        self.assertGreater(
            float(np.linalg.norm(projected)),
            0.0,
        )

    def test_weight_and_delta_clipping_preserve_sign_contract(self):
        stabilized, developed = _small_pair()
        metadata = clip_recurrent_weights(
            developed, 0.95
        )
        self.assertTrue(
            verify_sign_contract(developed)["pass"]
        )
        self.assertGreater(
            metadata["affected_edge_count"],
            0,
        )
        self.assertLessEqual(
            float(np.max(np.abs(developed.W.data))),
            metadata["absolute_limit"] + 1e-7,
        )

        delta = learned_recurrent_delta(
            stabilized, developed
        )
        clipped, meta = clip_delta_by_quantile(
            delta, 0.75
        )
        self.assertEqual(
            clipped.shape, delta.shape
        )
        self.assertLessEqual(
            float(np.max(np.abs(clipped))),
            meta["absolute_threshold"] + 1e-12,
        )

    def test_modest_perturbation_is_deterministic_and_bounded(self):
        _, first = _small_pair()
        _, second = _small_pair()
        before = first.W.data.copy()
        meta_a = perturb_recurrent_weights(
            first, 1842, 0.02
        )
        meta_b = perturb_recurrent_weights(
            second, 1842, 0.02
        )
        self.assertTrue(
            np.array_equal(
                first.W.data,
                second.W.data,
            )
        )
        self.assertTrue(
            verify_sign_contract(first)["pass"]
        )
        self.assertLessEqual(
            meta_a["max_relative_weight_change"],
            0.020001,
        )
        self.assertEqual(
            meta_a, meta_b
        )
        self.assertFalse(
            np.array_equal(
                before,
                first.W.data,
            )
        )


if __name__ == "__main__":
    unittest.main()
