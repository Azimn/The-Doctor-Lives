"""Real Laboratory physics recovery contract; these are NOT autonomy credit."""
import copy
import os
import unittest

from doctor_lives.lab_recovery_census import recovery_options, supply_gaps

try:
    from pretorius_lab.daily_rhythm import INITIAL, transition
except ModuleNotFoundError as exc:
    # General brain-only CI has no Laboratory. The pinned-Lab CI must fail closed.
    if exc.name != "pretorius_lab" or os.environ.get("PRETORIUS_REQUIRE_PINNED_LAB") == "1":
        raise
    INITIAL = None
    transition = None


@unittest.skipIf(INITIAL is None, "requires pinned original Laboratory; see dedicated recovery CI")
class OriginalPhysicsRecoveryTests(unittest.TestCase):
    def state(self, **kwargs):
        s = copy.deepcopy(INITIAL)
        s.update(kwargs)
        return s

    def paths(self, state, need):
        return [o for o in recovery_options(state) if o.need == need]

    def test_extreme_fatigue_honors_night_sleep_and_later_bench_recovery(self):
        state = self.state(fatigue=9, apparatus=0)
        state["cleanliness"]["room:sanctum"] = 3
        paths = self.paths(state, "fatigue")
        self.assertTrue(any(p.actions == ("sleep",) and p.physically_feasible for p in paths))
        self.assertFalse(self.paths(state, "apparatus")[0].physically_feasible)
        self.assertFalse(self.paths(state, "clutter:room:sanctum")[0].physically_feasible)
        slept, _ = transition(state, "sleep", {}, "station:bedroom")
        cleaned, _ = transition(slept, "clean", {}, "station:bench")
        repaired, _ = transition(cleaned, "repair", {}, "station:bench")
        self.assertLess(repaired["fatigue"], 8)
        self.assertLess(repaired["cleanliness"]["room:sanctum"], 3)
        self.assertGreater(repaired["apparatus"], 0)
        self.assertEqual(repaired["repairs"], state["repairs"] + 1)

    def test_hunger_is_two_step_real_cooking_then_eating(self):
        state = self.state(hunger=8)
        options = self.paths(state, "hunger")
        self.assertEqual(len(options), 1)
        self.assertEqual(options[0].actions, ("prepare_meal", "eat"))
        self.assertTrue(options[0].physically_feasible)
        cooked, _ = transition(state, "prepare_meal", {}, "station:kitchen")
        self.assertTrue(cooked["meal_ready"])
        fed, _ = transition(cooked, "eat", {}, "station:kitchen")
        self.assertFalse(fed["meal_ready"])
        self.assertLess(fed["hunger"], state["hunger"])
        self.assertLess(fed["supplies"]["rations"], state["supplies"]["rations"])

    def test_thirst_requires_real_water_tea_and_fuel(self):
        state = self.state(thirst=8)
        self.assertTrue(self.paths(state, "thirst")[0].physically_feasible)
        after, _ = transition(state, "brew_tea", {}, "station:kitchen")
        self.assertLess(after["thirst"], state["thirst"])
        empty = self.state(thirst=8)
        empty["supplies"]["water"] = 0
        option = self.paths(empty, "thirst")[0]
        self.assertFalse(option.physically_feasible)
        self.assertIn("Conflict", option.blocker)
        self.assertEqual(supply_gaps(empty)["water"], "exhausted_no_verified_replenishment")

    def test_empty_rations_no_invented_food(self):
        state = self.state(hunger=9)
        state["supplies"]["rations"] = 0
        option = self.paths(state, "hunger")[0]
        self.assertFalse(option.physically_feasible)
        self.assertEqual(state["supplies"]["rations"], 0)

    def test_broken_apparatus_needs_actual_spare(self):
        state = self.state(apparatus=0)
        self.assertTrue(self.paths(state, "apparatus")[0].physically_feasible)
        no_parts = self.state(apparatus=0)
        no_parts["supplies"]["spares"] = 0
        self.assertFalse(self.paths(no_parts, "apparatus")[0].physically_feasible)

    def test_darkness_needs_real_oil_and_lamp(self):
        state = self.state()
        state["minute"] = 23 * 60
        lit = self.paths(state, "darkness:room:sanctum")
        self.assertEqual(lit[0].actions, ("light",))
        self.assertTrue(lit[0].physically_feasible)
        no_oil = self.state()
        no_oil["minute"] = 23 * 60
        no_oil["supplies"]["oil"] = 0
        option = self.paths(no_oil, "darkness:room:sanctum")[0]
        self.assertFalse(option.physically_feasible)
        self.assertEqual(supply_gaps(no_oil)["oil"],
                         "exhausted_no_verified_replenishment")

    def test_exhausted_reagents_are_not_misreported_as_fixable(self):
        state = self.state()
        state["supplies"]["reagents"] = 0
        self.assertEqual(
            supply_gaps(state)["reagents"], "exhausted_no_verified_replenishment")
        self.assertEqual(
            supply_gaps(state)["rations"], "finite_stock_no_verified_replenishment")
        self.assertEqual(copy.deepcopy(INITIAL)["supplies"]["reagents"], 3)


if __name__ == "__main__":
    unittest.main()
