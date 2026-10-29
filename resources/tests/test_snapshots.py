"""Offline stdlib smoke tests for non-integrated third-party candidate source snapshots.

These tests verify that the exact copied MIT upstream files still match
their pinned git blobs and can perform representative isolated calculations.
They DO NOT validate Pretorius integration, cognitive novelty or autonomy.
"""
from __future__ import annotations

import hashlib
import importlib.util
import math
import pathlib
import sys
import unittest


HERE = pathlib.Path(__file__).resolve().parents[1]
UPSTREAM = HERE / "candidates" / "revive-companion"


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load candidate {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _git_blob_sha(path: pathlib.Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\x00" + payload).hexdigest()


class CandidateSnapshotTests(unittest.TestCase):
    def test_upstream_file_integrity(self):
        self.assertEqual(
            _git_blob_sha(UPSTREAM / "control_pid.py"),
            "7d5d7a7c3143a01224198463ec616e9fe30165f7",
        )
        self.assertEqual(
            _git_blob_sha(UPSTREAM / "bayesian_state.py"),
            "6b65ec441a27cf8374ea9b2b40da89b7b424bf11",
        )
        self.assertEqual(
            _git_blob_sha(UPSTREAM / "LICENSE"),
            "d509faaac26362f8ff09aee4c363ea96472c96d1",
        )

    def test_pid_proportional_clamp_and_reset(self):
        mod = _load("_pretorius_resource_pid", UPSTREAM / "control_pid.py")
        pid = mod.PIDController(kp=1.0, ki=0, kd=0, setpoint=1.0, output_max=0.5)
        self.assertAlmostEqual(pid.update(current=0.0), 0.5)
        self.assertAlmostEqual(pid.error, 1.0)
        pid.reset()
        self.assertIsNone(pid.error)

    def test_pid_anti_windup(self):
        mod = _load("_pretorius_resource_pid_windup", UPSTREAM / "control_pid.py")
        pid = mod.PIDController(kp=0, ki=1.0, kd=0, setpoint=1.0, integral_limit=1.0)
        self.assertAlmostEqual(pid.update(current=0), 1.0)
        self.assertAlmostEqual(pid.update(current=0), 1.0)

    def test_bayesian_probability_mass_and_observation_update(self):
        mod = _load("_pretorius_resource_bayes", UPSTREAM / "bayesian_state.py")
        est = mod.StateEstimator()
        initial = est.belief
        self.assertAlmostEqual(sum(initial.values()), 1.0)
        updated = est.update(reply_speed=0.8, reply_length=0.7, hour=14, silence_hours=0.2)
        self.assertAlmostEqual(sum(updated.values()), 1.0, places=8)
        self.assertNotEqual(initial, updated)
        state, probs = est.most_likely()
        self.assertIn(state, mod.State)
        self.assertEqual(probs, updated)
        self.assertTrue(math.isfinite(est.send_utility()))


if __name__ == "__main__":
    unittest.main()
