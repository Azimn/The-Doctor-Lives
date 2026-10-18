"""Article 7 preregistered compound transfer: invariants before outcomes."""
import importlib.util
import unittest

from doctor_lives.home_motivation_transfer import (
    SCHEMA, ARMS, CASES, SEEDS, MAX_PARTICIPANT_ACTIONS, GAP_MINUTES,
    seeded_fixture, run_transfer_screen,
)

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


class RegisteredTransferPlanTests(unittest.TestCase):
    def test_new_scenarios_do_not_reuse_prior_single_variable_cases(self):
        self.assertEqual(tuple(CASES), (
            "tired_and_thirsty", "thirsty_broken",
            "tired_thirsty_broken", "broken_without_water", "two_day_return"))
        self.assertEqual(SEEDS, (1842, 2718, 31415))
        self.assertEqual(len(ARMS), 5)
        self.assertEqual(MAX_PARTICIPANT_ACTIONS, 20)
        self.assertEqual(GAP_MINUTES, 2880)
        self.assertEqual(CASES["two_day_return"]["intended"],
                         ("tea", "rest", "tea", "repair"))
        self.assertEqual(CASES["two_day_return"]["gap_after_episode"], 1)

    def test_untrusted_extra_research_conditions_are_rejected(self):
        with self.assertRaises(ValueError):
            seeded_fixture({"joy": 10})
        with self.assertRaises(ValueError):
            seeded_fixture({"water": "unlimited"})
        with self.assertRaises(ValueError):
            run_transfer_screen(cases=("imagined_unseen_test",))
        with self.assertRaises(ValueError):
            run_transfer_screen(seeds=(10,))

    @unittest.skipUnless(HAS_LAB, "Requires pinned original physical Laboratory")
    def test_exact_single_source_counterfactual_genesis(self):
        from pretorius_lab.daily_rhythm import initial_state
        from doctor_lives.home_motivation_transfer import CASES
        original = initial_state()
        for name, spec in CASES.items():
            with self.subTest(name=name):
                newer = seeded_fixture(spec["change"])
                changed = {
                    key for key in original
                    if newer[key] != original[key]
                }
                expected = set(spec["change"]) - {"water"}
                self.assertEqual(changed, expected |
                                 ({"supplies"} if "water" in spec["change"] else set()))
                for stock, old_value in original["supplies"].items():
                    if stock != "water":
                        self.assertEqual(newer["supplies"][stock], old_value)


@unittest.skipUnless(HAS_LAB, "Requires pinned original physical Laboratory")
class SourceBoundTransferSmoke(unittest.TestCase):
    def test_real_doctor_five_arms_restart_and_source_hash_verification(self):
        output = run_transfer_screen(cases=("tired_and_thirsty",), seeds=(1842,))
        self.assertEqual(output["schema"], SCHEMA)
        self.assertEqual(output["engineering_score_before_and_after"], 80)
        self.assertFalse(output["independent_transfer_gate"])
        self.assertEqual(output["full_article_qualification"], "UNASSESSABLE")
        self.assertEqual(len(output["trials"]), 5)
        self.assertTrue(output["screening"]["all_worlds_replay_verified"])
        self.assertTrue(output["screening"]["all_same_initial_worlds_and_frames"])
        self.assertEqual(output["registered_case_count"], 1)
        for arm in ARMS:
            trial = next(x for x in output["trials"] if x["arm"] == arm)
            self.assertTrue(trial["world_verification"])
            self.assertLessEqual(trial["participant_actions"], MAX_PARTICIPANT_ACTIONS)
            self.assertGreater(trial["real_doctor_laboratory_memories"], 0)
            for episode in trial["episodes"]:
                for frame in episode["subject_frames"]:
                    self.assertEqual(set(frame), {"inner", "spoken_aloud"})
                    self.assertNotIn("fatigue=", frame["inner"])
                    self.assertNotIn("world_epoch", frame["inner"])
        for arm in ("native_plus_motives", "body_motive_lesion"):
            trial = next(x for x in output["trials"] if x["arm"] == arm)
            self.assertGreater(trial["pause_restart_attempts"], 0)
            self.assertEqual(trial["pause_restart_attempts"],
                             trial["pause_restart_successes"])

    def test_actual_48h_gap_is_12_committed_physical_time_receipts(self):
        output = run_transfer_screen(
            cases=("two_day_return",), seeds=(1842,),
            arms=("native_plus_motives", "numeric_state_rules"))
        self.assertTrue(output["screening"]["all_worlds_replay_verified"])
        self.assertTrue(output["screening"]["all_same_initial_worlds_and_frames"])
        for trial in output["trials"]:
            if trial["episodes"][0]["expected_verified_completion"]:
                self.assertEqual(trial["scheduled_gap_actions_not_autonomous"], 12)
                self.assertEqual(trial["actual_gap_elapsed_minutes"], GAP_MINUTES)
            else:
                self.assertEqual(trial["actual_gap_elapsed_minutes"], 0)
            self.assertTrue(trial["world_verification"])


if __name__ == "__main__":
    unittest.main()
