"""Article 8 native-mapped domestic practice: document nulls, verify all receipts."""
import importlib.util
import tempfile
from pathlib import Path
import unittest

from doctor_lives.home_native_practice import (
    CLOCKS, FIXED, LAB_PIN, NATIVE_TO_HOUSEHOLD, SEEDS, _execute_once,
    run_native_practice_screen,
)
from doctor_lives.neural import ACTIONS

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


class PreregisteredNativeChoiceTests(unittest.TestCase):
    def test_mapping_is_total_fixed_and_has_no_host_supplied_task_choice(self):
        self.assertEqual(set(NATIVE_TO_HOUSEHOLD), set(ACTIONS))
        self.assertEqual(NATIVE_TO_HOUSEHOLD["approach"], "tea")
        self.assertEqual(NATIVE_TO_HOUSEHOLD["cooperate"], "tea")
        self.assertEqual(NATIVE_TO_HOUSEHOLD["create"], "tidy")
        self.assertEqual(NATIVE_TO_HOUSEHOLD["explore"], "tidy")
        self.assertEqual(CLOCKS, (
            ("kitchen:morning", 420), ("kitchen:afternoon", 900)))
        self.assertEqual(FIXED, {
            "kitchen:morning": "tea", "kitchen:afternoon": "tidy"})
        self.assertEqual(SEEDS, (1842, 2718, 31415))

    def test_no_unregistered_seed_is_allowed_without_world_install(self):
        with self.assertRaises(ValueError):
            run_native_practice_screen(seeds=(9999,))
        with self.assertRaises(ValueError):
            run_native_practice_screen(seeds=())


@unittest.skipUnless(HAS_LAB, "Requires pinned authenticated Laboratory")
class ActualNeuralHomePracticeTests(unittest.TestCase):
    def test_neural_choice_attempts_and_source_learning_survive_actual_sleep(self):
        report = run_native_practice_screen(seeds=(1842,))
        self.assertEqual(report["neural_opportunities"], 8)
        self.assertEqual(report["article_8_engineering_score_before_and_after"], 10)
        self.assertFalse(report["independent_transfer_gate"])
        self.assertTrue(report["all_worlds_verified"])
        self.assertTrue(report["all_restored_practices_verified"])
        self.assertEqual(len(report["worlds"][0]["night_restarts"]), 3)
        self.assertEqual(len(report["worlds"][0]["training_offers"]), 6)
        self.assertEqual(len(report["worlds"][0]["heldout_offers"]), 2)
        for offer in (report["worlds"][0]["training_offers"] +
                      report["worlds"][0]["heldout_offers"]):
            policy = offer["decision"]
            self.assertIsInstance(policy["neural_policy_receipt"], str)
            self.assertIsInstance(policy["admitted_observation_memory_id"], str)
            self.assertEqual(policy["mapped_household_task"],
                             NATIVE_TO_HOUSEHOLD[policy["native_action"]])
        self.assertEqual(
            report["training_material_benefits"],
            report["worlds"][0]["source_verified_practices"])
        self.assertEqual(report["heldout_neural_agreement"]["untrained_lesion"], 0)

    def test_exhausted_real_tea_stays_blocked_and_cannot_be_habit_reward(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from doctor_lives.home_native_practice import _agent, _act
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            world = SpatialHabitat.create(root / "lab.sqlite3")
            HomeLife(world).initialize()
            DailyRhythm(world).initialize()
            bridge, habit = _agent(root, 1842)
            _act(bridge, "walk", "to-hall", station="station:hall")
            _act(bridge, "walk", "to-kitchen", station="station:kitchen")
            # Real tea is finite, three physically committed cups maximum.
            for cup in range(3):
                before = bridge.subject.rhythm.audit_state()
                _act(bridge, "brew_tea", f"cup-{cup}")
                if before["thirst"] > 0:
                    habit.learn(event_id=f"cup-{cup}", before=before)
            before = bridge.subject.rhythm.audit_state()
            denied = _execute_once(bridge, "tea", "fourth-cup",
                                   train=True, habit=habit)
            self.assertFalse(denied["world_accepted"])
            self.assertFalse(denied["learned"])
            self.assertEqual(bridge.subject.rhythm.audit_state(), before)
            self.assertTrue(habit.verify()["verified"])
            self.assertTrue(bridge.subject.verify()["verified"])


if __name__ == "__main__":
    unittest.main()
