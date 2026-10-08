from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from doctor_lives.flywire_bridge import (
    build_pretorius_feature_vector,
    load_annotation_pools,
    project_features_to_afferents,
    sha256_array,
    stimulus_manifest,
)


class FlyWireBridgeTests(unittest.TestCase):
    def test_existing_pretorius_encoder_is_reused_deterministically(self):
        scalars = {"threat": 0.5, "novelty": -0.25}
        a = build_pretorius_feature_vector("A difficult apparatus remains unfinished.", scalars)
        b = build_pretorius_feature_vector("A difficult apparatus remains unfinished.", scalars)
        np.testing.assert_array_equal(a, b)
        self.assertEqual(a.dtype, np.float32)
        self.assertGreater(a.size, 512)
        self.assertTrue(np.isfinite(a).all())

    def test_annotation_pool_selection_uses_only_index_aligned_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ann.npz"
            np.savez(
                path,
                root_ids=np.arange(8, dtype=np.int64) + 100,
                flow=np.array(
                    ["afferent", "intrinsic", "efferent", "", "", "afferent", "", ""]
                ),
                super_class=np.array(
                    ["", "", "", "sensory", "motor", "", "descending", "central"]
                ),
            )
            pools = load_annotation_pools(path)

        np.testing.assert_array_equal(pools.afferent_indices, np.array([0, 3, 5]))
        np.testing.assert_array_equal(pools.efferent_indices, np.array([2, 4, 6]))
        self.assertEqual(pools.neuron_count, 8)

    def test_projection_is_deterministic_bounded_and_stays_in_afferent_pool(self):
        features = np.array([1.0, -0.5, 0.0, 0.25], dtype=np.float32)
        afferents = np.arange(100, 300, dtype=np.int64)
        a = project_features_to_afferents(
            features,
            afferents,
            seed=19,
            fanout=3,
            max_rate_hz=150.0,
        )
        b = project_features_to_afferents(
            features,
            afferents,
            seed=19,
            fanout=3,
            max_rate_hz=150.0,
        )
        self.assertEqual(a, b)
        self.assertTrue(a)
        self.assertTrue(set(a).issubset(set(afferents.tolist())))
        self.assertTrue(all(0.0 < rate <= 150.0 for rate in a.values()))

    def test_feature_sign_selects_a_different_hash_route(self):
        afferents = np.arange(1000, 3000, dtype=np.int64)
        positive = project_features_to_afferents([1.0], afferents, seed=3, fanout=4)
        negative = project_features_to_afferents([-1.0], afferents, seed=3, fanout=4)
        self.assertNotEqual(set(positive), set(negative))

    def test_manifest_is_stable_and_marks_interface_as_engineered(self):
        rates = {4: 80.0, 7: 120.0}
        a = stimulus_manifest(
            text="test",
            scalars={"novelty": 0.5},
            rates_hz=rates,
            projection_seed=11,
            fanout=2,
        )
        b = stimulus_manifest(
            text="test",
            scalars={"novelty": 0.5},
            rates_hz=rates,
            projection_seed=11,
            fanout=2,
        )
        self.assertEqual(a, b)
        self.assertFalse(a["biological_semantics_claimed"])
        self.assertEqual(a["interface"], "pretorius-generic-feature-to-flywire-afferent-v1")
        self.assertEqual(len(a["manifest_sha256"]), 64)

    def test_array_hash_depends_on_content(self):
        a = np.arange(16, dtype=np.int64)
        b = a.copy()
        b[-1] += 1
        self.assertEqual(sha256_array(a), sha256_array(a.copy()))
        self.assertNotEqual(sha256_array(a), sha256_array(b))


if __name__ == "__main__":
    unittest.main()
