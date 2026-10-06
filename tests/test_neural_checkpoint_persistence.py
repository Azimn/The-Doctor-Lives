from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from doctor_lives.neural import (
    NEURAL_CHECKPOINT_SCHEMA_VERSION,
    NEURAL_CONVERGENCE_CONFIG,
    NeuralCheckpointError,
    PretoriusRecurrentSubstrate,
)


def small_config() -> dict:
    cfg = dict(NEURAL_CONVERGENCE_CONFIG)
    cfg.update({
        "neurons": 64,
        "sensory_dim": 32,
        "avg_recurrent_degree": 6,
        "input_degree": 3,
        "action_population_size": 5,
        "plasticity_interval": 1,
        "spectral_check_interval": 1,
        "seed": 1842,
    })
    return cfg


class NeuralCheckpointPersistenceTests(unittest.TestCase):
    def test_atomic_save_round_trip_and_schema_marker(self):
        net = PretoriusRecurrentSubstrate(small_config())
        net.step(
            "A novel apparatus resists the expected adjustment.",
            {"novelty": 0.7, "threat": 0.2},
            confidence=0.9,
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pretorius_recurrent.npz"
            net.save(path)
            self.assertTrue(path.is_file())
            self.assertFalse(path.with_name(f".{path.name}.tmp").exists())
            with np.load(path, allow_pickle=False) as payload:
                self.assertEqual(
                    int(payload["checkpoint_schema_version"][0]),
                    NEURAL_CHECKPOINT_SCHEMA_VERSION,
                )
            restored = PretoriusRecurrentSubstrate.load(path)
            self.assertEqual(restored.tick, net.tick)
            self.assertTrue(np.array_equal(restored.v, net.v))
            self.assertTrue(np.array_equal(restored.rate, net.rate))
            self.assertTrue(np.array_equal(restored.W.data, net.W.data))

    def test_interrupted_save_preserves_previous_checkpoint(self):
        net = PretoriusRecurrentSubstrate(small_config())
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pretorius_recurrent.npz"
            net.save(path)
            before = path.read_bytes()
            net.step("A later observation.", {"novelty": 0.4}, confidence=0.8)

            def fail_after_partial_write(handle, **kwargs):
                handle.write(b"partial checkpoint bytes")
                handle.flush()
                raise OSError("injected checkpoint write failure")

            with patch(
                "doctor_lives.neural.np.savez_compressed",
                side_effect=fail_after_partial_write,
            ):
                with self.assertRaisesRegex(
                    NeuralCheckpointError,
                    "failed to save recurrent checkpoint atomically",
                ):
                    net.save(path)

            self.assertEqual(path.read_bytes(), before)
            self.assertFalse(path.with_name(f".{path.name}.tmp").exists())
            restored = PretoriusRecurrentSubstrate.load(path)
            self.assertEqual(restored.tick, 0)

    def test_truncated_checkpoint_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pretorius_recurrent.npz"
            path.write_bytes(b"not an npz checkpoint")
            with self.assertRaisesRegex(
                NeuralCheckpointError,
                "unreadable or truncated",
            ):
                PretoriusRecurrentSubstrate.load(path)

    def test_missing_required_array_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pretorius_recurrent.npz"
            np.savez_compressed(
                path,
                checkpoint_schema_version=np.asarray([1], dtype=np.int64),
                cfg_json=np.asarray('{"neurons": 64}'),
                tick=np.asarray([0], dtype=np.int64),
            )
            with self.assertRaisesRegex(
                NeuralCheckpointError,
                "missing required fields",
            ):
                PretoriusRecurrentSubstrate.load(path)

    def test_future_checkpoint_schema_fails_closed(self):
        net = PretoriusRecurrentSubstrate(small_config())
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pretorius_recurrent.npz"
            net.save(path)
            with np.load(path, allow_pickle=False) as payload:
                arrays = {
                    name: np.asarray(payload[name]).copy()
                    for name in payload.files
                }
            arrays["checkpoint_schema_version"] = np.asarray(
                [NEURAL_CHECKPOINT_SCHEMA_VERSION + 1],
                dtype=np.int64,
            )
            np.savez_compressed(path, **arrays)
            with self.assertRaisesRegex(
                NeuralCheckpointError,
                "newer than this runtime",
            ):
                PretoriusRecurrentSubstrate.load(path)

    def test_legacy_rc1_checkpoint_without_schema_marker_still_loads(self):
        net = PretoriusRecurrentSubstrate(small_config())
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legacy_rc1.npz"
            np.savez_compressed(
                path,
                v=net.v,
                rate=net.rate,
                bias=net.bias,
                w_data=net.W.data,
                w_indices=net.W.indices,
                w_indptr=net.W.indptr,
                excitatory=net.excitatory,
                eligibility=net.eligibility,
                synaptic_tags=net.synaptic_tags,
                noise_state=net.noise_state,
                state_gain=np.asarray([net.state_gain], dtype=np.float64),
                homeostasis_events=np.asarray(
                    [net.homeostasis_events], dtype=np.int64
                ),
                last_recurrent_gain=np.asarray([np.nan], dtype=np.float64),
                motor_w=net.motor_w,
                motor_b=net.motor_b,
                cfg_json=np.asarray(json.dumps(net.cfg)),
                rng_state_json=np.asarray(
                    json.dumps(net.rng.bit_generator.state)
                ),
                tick=np.asarray([net.tick], dtype=np.int64),
            )
            restored = PretoriusRecurrentSubstrate.load(path)
            self.assertEqual(restored.tick, net.tick)
            self.assertTrue(np.array_equal(restored.W.data, net.W.data))


if __name__ == "__main__":
    unittest.main()
