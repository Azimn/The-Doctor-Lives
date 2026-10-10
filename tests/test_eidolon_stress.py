"""D3-S natural neural multi-seed stress harness invariants.

Developer-generated scenarios are regression fixtures, not scientific holdouts.
"""
from __future__ import annotations

import unittest

from scripts.run_eidolon_d3_stress import ARMS, CASES, POSITIVE, run_battery


class StressBatteryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One additional seed, separate from the fixed four-seed research run.
        # Tests observable validity, not a sealed generalization claim.
        cls.output = run_battery((113,))

    def test_one_seed_has_12_cases_and_48_real_decisions(self):
        result = self.output
        self.assertEqual(result["fixture_count"], 12)
        self.assertEqual(result["actual_think_decisions"], 48)
        self.assertEqual(set(result["by_case"]), set(CASES))
        self.assertFalse(result["overridden_natural_neural_action_scores"])

    def test_expected_positive_gates_open_and_negative_gates_fail_closed(self):
        rows = self.output["rows"]
        self.assertEqual(self.output["summary"]["eligible_cases"], len(POSITIVE))
        self.assertEqual(self.output["summary"]["ineligible_cases"], len(CASES)-len(POSITIVE))
        self.assertEqual(self.output["summary"]["correct_gate_acceptances"], len(POSITIVE))
        self.assertEqual(self.output["summary"]["false_gate_acceptances"], 0)
        for row in rows:
            self.assertEqual(row["arms"]["intact"]["injected"], row["expected_gate"])
            if row["expected_gate"]:
                self.assertTrue(row["arms"]["intact"]["source_event_accepted"])
                self.assertGreater(
                    row["arms"]["intact"]["persist_probability"],
                    row["arms"]["sham"]["persist_probability"]
                )
            else:
                self.assertFalse(row["arms"]["intact"]["source_event_accepted"])

    def test_all_controls_are_source_and_time_lesioned(self):
        for row in self.output["rows"]:
            for arm, enabled, with_history, with_temporal in ARMS:
                sample = row["arms"][arm]
                if arm != "intact":
                    self.assertFalse(sample["injected"], f"{row['case']}/{arm}")
                    self.assertAlmostEqual(
                        sample["persist_probability"],
                        row["arms"]["sham"]["persist_probability"],
                        places=9,
                    )

    def test_strong_naive_due_only_baseline_has_known_false_positives(self):
        report = self.output["summary"]
        self.assertGreater(report["naive_due_only_false_acceptances"], 0)
        self.assertEqual(report["false_gate_acceptances"], 0)

    def test_unmodified_source_and_exact_paired_states(self):
        for row in self.output["rows"]:
            self.assertTrue(row["parent_unmodified"])
            for arm in row["arms"].values():
                self.assertTrue(arm["prechoice_neural_state_identical"])

    def test_creative_intent_counterexample_always_documented(self):
        cases = [r for r in self.output["rows"] if r["case"] == "lived_due_create"]
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]["intended_action_fixture_label"], "create")
        self.assertTrue(cases[0]["arms"]["intact"]["injected"])
        # Do NOT demand the generic 'persist' injection improve a create task.
        self.assertIn("create_intent_cases_intervention_harmed", self.output["summary"])
        self.assertIn("create_intent_cases_intervention_helped", self.output["summary"])

    def test_invalid_seed_lists_rejected(self):
        for invalid in ((), (True,), (-1,), (11, 11), ("seventeen",)):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    run_battery(invalid)


if __name__ == "__main__":
    unittest.main()
