"""D3-S native-bridge comparison: 60 additional genuine clone decisions.

This is a software regression on developer-defined cases, not a validation of
the artistic or clinical correctness of any action category.
"""
from __future__ import annotations

import unittest

from scripts.run_eidolon_d3_stress_v02 import run_battery, CASES, POSITIVE


class NativeBridgeComparatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = run_battery((127,))

    def test_fifth_arm_is_a_real_separate_policy_execution(self):
        r = self.report
        self.assertEqual(r["fixture_count"], 12)
        self.assertEqual(r["actual_think_decisions"], 60)
        self.assertFalse(r["overridden_natural_neural_action_scores"])
        for case in r["rows"]:
            self.assertEqual(set(case["arms"]), {
                "sham", "intact", "history_lesion",
                "clock_lesion", "production_bridge",
            })
            self.assertTrue(case["arms"]["production_bridge"]["prechoice_neural_state_identical"])
            self.assertFalse(case["arms"]["production_bridge"]["injected"])

    def test_v01_source_gate_invariants_survive_comparison(self):
        self.assertEqual(self.report["summary"]["eligible_cases"], len(POSITIVE))
        self.assertEqual(self.report["summary"]["correct_gate_acceptances"], len(POSITIVE))
        self.assertEqual(self.report["summary"]["false_gate_acceptances"], 0)
        for case in self.report["rows"]:
            if case["expected_gate"]:
                self.assertTrue(case["arms"]["intact"]["injected"])
                self.assertFalse(case["arms"]["history_lesion"]["injected"])
                self.assertFalse(case["arms"]["clock_lesion"]["injected"])

    def test_every_arm_started_from_same_checkpoint(self):
        for case in self.report["rows"]:
            self.assertTrue(case["parent_unmodified"])
            for info in case["arms"].values():
                self.assertTrue(info["prechoice_neural_state_identical"])

    def test_task_specificity_metric_reported_for_native_and_eidolon(self):
        report = self.report["summary"]
        self.assertEqual(report["create_intent_cases"], 1)
        for key in ("create_tasks_production_bridge_selects_create",
                    "create_tasks_eidolon_selects_create",
                    "production_bridge_choice_changes_vs_sham",
                    "eidolon_choice_differs_from_production_bridge"):
            self.assertIn(key, report)
            self.assertGreaterEqual(report[key], 0)
            self.assertLessEqual(report[key], 12)


if __name__ == "__main__":
    unittest.main()
