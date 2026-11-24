"""Grounded regulatory pressure is not action authority."""
import unittest
from doctor_lives.noesis_interoception import perceived_regulatory_pressure


class PerceivedRegulatoryPressureTests(unittest.TestCase):
    prefix = "I am in the kitchen. There is daylight enough to see. "
    actions = ("advance", "eat", "prepare_meal", "brew_tea", "rest", "sleep")

    def test_all_situated_motors_use_real_neural_vocabulary(self):
        from doctor_lives.neural import ACTIONS
        from doctor_lives.noesis_situated_choice import NEURAL_AFFORDANCE_MAP
        self.assertTrue(set(NEURAL_AFFORDANCE_MAP.values()) <= set(ACTIONS))
        self.assertIn("brew_tea", NEURAL_AFFORDANCE_MAP)

    def test_neutral_perception_has_no_artificial_need(self):
        scores, cues = perceived_regulatory_pressure(
            self.prefix + "There is a prepared meal to eat.", self.actions)
        self.assertEqual(cues, ())
        self.assertEqual(set(scores), set(self.actions))
        self.assertTrue(all(x == 0 for x in scores.values()))

    def test_competing_perceived_needs_are_bounded(self):
        scores, cues = perceived_regulatory_pressure(
            self.prefix + "I feel worn out and find it hard to concentrate. "
            "I am painfully hungry. My mouth is dry.", self.actions)
        self.assertEqual(cues, ("worn_out", "painfully_hungry", "thirsty"))
        self.assertGreater(scores["eat"], scores["prepare_meal"])
        self.assertGreater(scores["rest"], scores["advance"])
        self.assertGreater(scores["brew_tea"], scores["advance"])
        self.assertTrue(all(0 <= x <= .20 for x in scores.values()))

    def test_no_unavailable_action_is_created(self):
        scores, cues = perceived_regulatory_pressure(
            self.prefix + "I am painfully hungry. My mouth is dry.",
            ("advance", "rest"))
        self.assertEqual(cues, ("painfully_hungry", "thirsty"))
        self.assertEqual(scores, {"advance": 0.0, "rest": 0.0})

    def test_quoted_later_text_and_unrecognized_prefix_have_no_effect(self):
        for text in (
            self.prefix + "I can make out a sign. I am painfully hungry.",
            "I remember the kitchen. I am painfully hungry.",
            self.prefix + "My mouth is dry. I am painfully hungry.",
        ):
            scores, cues = perceived_regulatory_pressure(text, ("eat",))
            self.assertEqual(scores["eat"], 0)
            self.assertNotIn("painfully_hungry", cues)

    def test_moderate_and_urgent_hunger_are_distinct(self):
        moderate, _ = perceived_regulatory_pressure(
            self.prefix + "I could do with something to eat.", ("eat",))
        urgent, _ = perceived_regulatory_pressure(
            self.prefix + "I am painfully hungry.", ("eat",))
        self.assertGreater(urgent["eat"], moderate["eat"])


if __name__ == "__main__":
    unittest.main()
