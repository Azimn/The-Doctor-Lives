"""Actual-world causal choice pilot (requires pinned Laboratory donor)."""
import importlib.util
import unittest

from doctor_lives.home_choice_probe import (
    ACTIONS, NATIVE_TO_TASK, CASES, ARMS, EXPECTED,
    MAX_ACTIONS, simple_choice, run_pilot,
)

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


class ChoiceMappingTests(unittest.TestCase):
    def test_every_native_action_has_exactly_one_frozen_task(self):
        self.assertEqual(set(ACTIONS), set(NATIVE_TO_TASK))
        self.assertEqual(set(NATIVE_TO_TASK.values()),
                         {"tea", "rest", "experiment", "repair"})
        self.assertGreater(MAX_ACTIONS, 5)

    def test_rule_baseline_uses_only_first_person_language(self):
        self.assertEqual(simple_choice("I am in my laboratory."), "experiment")
        self.assertEqual(simple_choice(
            "I am here. My mouth is dry."), "tea")
        self.assertEqual(simple_choice(
            "I feel worn out and find it hard to concentrate."), "rest")
        self.assertEqual(simple_choice(
            "I feel worn out. My instruments look worn."), "repair")
        with self.assertRaises(ValueError):
            simple_choice('{"fatigue":10}')

    @unittest.skipUnless(HAS_LAB, "Pinned Laboratory required for physical pilot")
    def test_four_paired_real_doctor_cases_and_equal_sensory_frames(self):
        result = run_pilot()
        self.assertEqual(result["qualification"], "UNASSESSABLE")
        self.assertEqual(len(result["cases"]), len(CASES) * len(ARMS))
        self.assertEqual(len(result["pairs"]), len(CASES))
        self.assertEqual(result["result"]["simple_firstperson_rule"], 4)
        self.assertTrue(0 <= result["result"]["real_doctor_policy"] <= 4)
        for pair in result["pairs"]:
            self.assertTrue(pair["same_world_state"])
            self.assertTrue(pair["same_sensory_frame"])
        for row in result["cases"]:
            self.assertEqual(row["policy_source"],
                "actual_recurrent_policy_fixed_mapping"
                if row["arm"] == "real_doctor_policy"
                else "literal_firstperson_rules")
            self.assertIn(row["task_proposed"], ("tea", "rest", "experiment", "repair"))
            self.assertLessEqual(row["actions_used"], MAX_ACTIONS)
            if row["expected_task_completed"]:
                self.assertTrue(row["completed"])
                self.assertEqual(row["task_proposed"], EXPECTED[row["case"]])
            if row["arm"] == "real_doctor_policy":
                self.assertIsNotNone(row["native_tendency"])
                self.assertIsNotNone(row["policy_decision_id"])
            else:
                self.assertIsNone(row["native_tendency"])


if __name__ == "__main__":
    unittest.main()
