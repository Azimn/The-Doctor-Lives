"""Paired native neural and bodily-arbitrated Laboratory action comparisons."""
import importlib.util
import unittest

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


@unittest.skipUnless(HAS_LAB, "Pinned physical Laboratory required")
class HomeMotivePilotTest(unittest.TestCase):
    def test_four_arm_physical_comparison_and_information_parity(self):
        from doctor_lives.home_motive_pilot import run_motive_pilot, ARMS
        result = run_motive_pilot()
        self.assertEqual(result["qualification"], "UNASSESSABLE")
        self.assertEqual(len(result["observations"]), 16)
        self.assertEqual(len(result["matched_conditions"]), 4)
        self.assertEqual(set(result["totals"]), set(ARMS))
        self.assertEqual(result["totals"]["simple_firstperson_rules"], 4)
        self.assertEqual(result["totals"]["native_only"], 1)
        self.assertTrue(0 <= result["totals"]["native_plus_motives"] <= 4)
        self.assertTrue(0 <= result["totals"]["motives_body_lesion"] <= 4)
        for case in result["matched_conditions"]:
            self.assertTrue(case["matching_physical_world"])
            self.assertTrue(case["matching_first_person_observation"])
        for observation in result["observations"]:
            self.assertLessEqual(observation["physical_actions"],
                                 result["action_budget"])
            if observation["expected_task_completed"]:
                self.assertTrue(observation["physical_goal_occurred"])
                self.assertEqual(observation["task_proposed"],
                                 observation["expected_task"])
            self.assertIsNotNone(observation["neural_policy_decision_id"])

if __name__ == "__main__":
    unittest.main()
