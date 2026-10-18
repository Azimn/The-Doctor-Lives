"""Article 8: actual material habits, causal checks and honest score hold."""
import importlib.util
import tempfile
from pathlib import Path
import unittest

from doctor_lives.home_habit_trace import (
    CUES, MIN_PRACTICE, VerifiedHouseholdHabit, kitchen_cue,
)
from doctor_lives.home_habit_screen import (
    MAPPINGS, FIXED_SCHEDULE, run_habit_screen,
)

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


class RegisteredHabitSpecTests(unittest.TestCase):
    def test_context_reversal_blocks_hardcoded_schedule(self):
        self.assertEqual(set(MAPPINGS), {"A", "B"})
        self.assertEqual(MAPPINGS["A"], FIXED_SCHEDULE)
        self.assertEqual(MAPPINGS["B"], {
            "kitchen:morning": "tidy", "kitchen:afternoon": "tea"})
        self.assertEqual(MIN_PRACTICE, 2)
        self.assertEqual(CUES, ("kitchen:morning", "kitchen:afternoon"))

    def test_cues_are_source_calculated_not_host_named(self):
        state = {"minute": 7 * 60}
        self.assertEqual(kitchen_cue(state, "station:kitchen"),
                         "kitchen:morning")
        self.assertEqual(kitchen_cue({"minute": 15*60}, "station:kitchen"),
                         "kitchen:afternoon")
        with self.assertRaises(ValueError):
            kitchen_cue(state, "station:parlor")
        with self.assertRaises(ValueError):
            kitchen_cue({"minute": 23*60}, "station:kitchen")


@unittest.skipUnless(HAS_LAB, "Needs pinned original full physical Laboratory")
class RealDoctorHabitScreenTests(unittest.TestCase):
    def test_two_reversed_daily_training_worlds_with_real_memory_and_outcomes(self):
        report = run_habit_screen()
        self.assertEqual(report["article_08_engineering_score_before_and_after"], 10)
        self.assertFalse(report["independent_blinded_transfer"])
        self.assertEqual(report["full_article_qualification"], "UNASSESSABLE")
        self.assertTrue(report["all_material_worlds_verified"])
        self.assertTrue(report["all_training_receipts_verified"])
        self.assertTrue(report["all_recalled_acts_physically_completed"])
        self.assertEqual(report["totals"]["verified_practice"], 4)
        self.assertEqual(report["totals"]["fixed_schedule"], 2)
        self.assertEqual(report["totals"]["recency"], 0)
        self.assertEqual(report["totals"]["untrained_trace"], 0)
        self.assertTrue(report["predeclared_screen_met"])
        for world in report["worlds"]:
            self.assertEqual(len(world["practices"]), 4)
            self.assertEqual(world["habits_replayed"]["verified_practices"], 4)
            self.assertGreater(world["real_doctor_memories"], 0)
            for case in world["heldout"]:
                self.assertTrue(case["physically_completed"])
                self.assertIn(case["advice"]["verified_practice"],
                              ("tea", "tidy"))
                self.assertEqual(case["advice"]["untrained_trace"], None)
                self.assertNotIn("supplies=", str(case["first_person"]))


if __name__ == "__main__":
    unittest.main()
