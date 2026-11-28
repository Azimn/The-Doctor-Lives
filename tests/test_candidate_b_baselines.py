"""Actual-world simple controller and flat/no-organ comparison."""
from __future__ import annotations

import importlib.util
import unittest

from doctor_lives.lab_baselines import run_repair_baseline


@unittest.skipUnless(importlib.util.find_spec("pretorius_lab") is not None,
                     "Requires original source-pinned Laboratory")
class MatchedWorldControllerBaselines(unittest.TestCase):
    def test_goal_aware_simple_controller_completes_original_physical_task(self):
        result = run_repair_baseline("simple")
        self.assertTrue(result["goal_completed_by_physical_world"])
        self.assertEqual(result["world_final"]["apparatus"], 2)
        self.assertLess(result["world_final"]["clutter"], 3)
        self.assertEqual(result["world_final"]["spares"], 1)
        self.assertIn("sleep", result["actions"])
        self.assertIn("clean", result["actions"])
        self.assertIn("repair", result["actions"])
        self.assertIn("walk", result["actions"])
        self.assertTrue(result["actual_world_epoch_verified"])
        self.assertFalse(result["Noesis_or_any_organ_invoked"])
        self.assertFalse(result["autonomy_credit"])

    def test_unguided_flat_controller_does_not_fake_repair_success(self):
        result = run_repair_baseline("flat")
        self.assertFalse(result["goal_completed_by_physical_world"])
        self.assertNotIn("repair", result["actions"])
        self.assertFalse(result["autonomy_credit"])
        self.assertTrue(result["actual_world_epoch_verified"])

    def test_comparators_reject_unreviewed_mode(self):
        with self.assertRaises(ValueError):
            run_repair_baseline("pretorius")


if __name__ == "__main__":
    unittest.main()
