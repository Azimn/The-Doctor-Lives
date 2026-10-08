import unittest

import numpy as np

from doctor_lives.flywire_adapter import (
    centered_context_separation,
    effective_dimensionality,
    endpoint_shuffle_smoke_control,
    project_features_to_afferents,
    random_edge_count_smoke_control,
    summarize_topology,
    topology_fingerprint,
)


class FlyWireAdapterTests(unittest.TestCase):
    def setUp(self):
        self.pre = np.array([0, 0, 1, 1, 2, 2, 3, 3], dtype=np.int64)
        self.post = np.array([1, 2, 0, 3, 0, 3, 1, 2], dtype=np.int64)
        self.weights = np.array([1, -1, 2, 1, -2, 1, 1, -1], dtype=np.float32)

    def test_topology_fingerprint_is_stable_and_sensitive(self):
        a = topology_fingerprint(4, self.pre, self.post, self.weights)
        b = topology_fingerprint(
            4,
            self.pre.astype(np.int32),
            self.post.astype(np.int32),
            self.weights.astype(np.float64),
        )
        self.assertEqual(a, b)
        changed = self.post.copy()
        changed[0] = 3
        self.assertNotEqual(a, topology_fingerprint(4, self.pre, changed, self.weights))

    def test_summary_records_signs(self):
        summary = summarize_topology(4, self.pre, self.post, self.weights)
        self.assertEqual(summary.neurons, 4)
        self.assertEqual(summary.edges, 8)
        self.assertEqual(summary.excitatory_edges, 5)
        self.assertEqual(summary.inhibitory_edges, 3)

    def test_endpoint_shuffle_preserves_each_nodes_in_and_out_degree(self):
        pre, post, weights = endpoint_shuffle_smoke_control(
            self.pre, self.post, self.weights, seed=11
        )
        np.testing.assert_array_equal(
            np.bincount(pre, minlength=4),
            np.bincount(self.pre, minlength=4),
        )
        np.testing.assert_array_equal(
            np.bincount(post, minlength=4),
            np.bincount(self.post, minlength=4),
        )
        np.testing.assert_array_equal(weights, self.weights)
        pre2, post2, weights2 = endpoint_shuffle_smoke_control(
            self.pre, self.post, self.weights, seed=11
        )
        np.testing.assert_array_equal(pre, pre2)
        np.testing.assert_array_equal(post, post2)
        np.testing.assert_array_equal(weights, weights2)

    def test_random_smoke_control_matches_scale_and_avoids_self_loops(self):
        pre, post, weights = random_edge_count_smoke_control(
            8, len(self.weights), self.weights, seed=77
        )
        self.assertEqual(len(pre), len(self.weights))
        self.assertEqual(len(post), len(self.weights))
        self.assertFalse(np.any(pre == post))
        np.testing.assert_array_equal(np.sort(weights), np.sort(self.weights))

    def test_feature_projection_is_deterministic_and_nonsemantic(self):
        features = np.zeros(16, dtype=np.float32)
        features[[1, 4, 9]] = [0.5, -1.0, 0.25]
        candidates = np.arange(1000, 1100, dtype=np.int64)
        ids1, drive1 = project_features_to_afferents(
            features, candidates, fanout_per_feature=3, seed=5
        )
        ids2, drive2 = project_features_to_afferents(
            features, candidates, fanout_per_feature=3, seed=5
        )
        np.testing.assert_array_equal(ids1, ids2)
        np.testing.assert_array_equal(drive1, drive2)
        self.assertTrue(set(ids1).issubset(set(candidates)))
        self.assertAlmostEqual(float(drive1.max()), 1.0)

    def test_centered_context_geometry_separates_two_families(self):
        states = np.array(
            [
                [4.0, 0.0, 1.0, 1.0],
                [3.8, 0.2, 1.0, 1.0],
                [0.0, 4.0, 1.0, 1.0],
                [0.2, 3.8, 1.0, 1.0],
            ]
        )
        result = centered_context_separation(states, ["a", "a", "b", "b"])
        self.assertEqual(result["within_pairs"], 2)
        self.assertEqual(result["across_pairs"], 4)
        self.assertGreater(result["separation"], 0.0)
        self.assertGreater(effective_dimensionality(states), 0.0)


if __name__ == "__main__":
    unittest.main()
