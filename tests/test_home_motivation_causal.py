"""Article 7: preregistered isolated body/motive counterfactuals and receipts."""
import importlib.util
import unittest

from doctor_lives.home_motivation_causal import (
    CASES, ARMS, MAX_ACTIONS, numeric_rule, _fixture
)
from doctor_lives.home_motive_queue import motive_scores

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


class IndependentRuleBaselineTests(unittest.TestCase):
    def test_numeric_simple_controller_is_independent_of_motive_formula(self):
        state = {"fatigue": 2, "thirst": 2, "apparatus": 2}
        self.assertEqual(numeric_rule(state), "experiment")
        self.assertEqual(numeric_rule(dict(state, apparatus=0)), "repair")
        self.assertEqual(numeric_rule(dict(state, fatigue=8)), "rest")
        self.assertEqual(numeric_rule(dict(state, thirst=8)), "tea")
        self.assertEqual(numeric_rule(dict(state, fatigue=8, apparatus=0)), "rest")

    def test_explicit_registered_cases_and_dual_goal(self):
        self.assertEqual(set(CASES), {
            "baseline", "wear_only", "fatigue_only", "thirst_only",
            "wear_and_fatigue",
        })
        self.assertEqual(CASES["wear_and_fatigue"]["intended"], ("rest", "repair"))
        self.assertEqual(len(ARMS), 5)
        self.assertEqual(MAX_ACTIONS, 12)


@unittest.skipUnless(HAS_LAB, "Use pinned real Laboratory package for causal tests")
class SourceBoundCausalTests(unittest.TestCase):
    def test_one_variable_isolation_vs_unmodified_domestic_fixture(self):
        from pretorius_lab.daily_rhythm import initial_state
        control = initial_state()
        for case, spec in CASES.items():
            other = _fixture(spec["change"])
            differences = {key for key in control if control[key] != other[key]}
            self.assertEqual(differences, set(spec["change"]), case)
            self.assertEqual(other["supplies"], control["supplies"])
            self.assertEqual(other["minute"], control["minute"])
            self.assertEqual(other["lamps"], control["lamps"])

    def test_material_receipts_and_assessed_motive_lesion(self):
        from doctor_lives.home_motivation_causal import run_isolated_motivation_pilot
        report = run_isolated_motivation_pilot()
        self.assertEqual(report["qualification"], "UNASSESSABLE")
        self.assertEqual(len(report["trials"]), 25)
        for case in CASES:
            rows = [x for x in report["trials"] if x["case"] == case]
            self.assertEqual(len(rows), len(ARMS))
            self.assertEqual(len({r["engineered_initial_fixture_sha256"]
                                  for r in rows}), 1)
            self.assertEqual(len({
                r["episodes"][0]["first_person_frame_sha256"]
                for r in rows
            }), 1)
        for row in report["trials"]:
            self.assertTrue(row["world_verification"])
            self.assertLessEqual(row["total_physical_actions"], MAX_ACTIONS)
            self.assertGreater(row["persistent_real_doctor_memories"], 0)
            for step in row["episodes"]:
                self.assertEqual(step["expected_action_completed"],
                                 step["physical_completed"] and
                                 step["chosen_action"] == step["expected_action"])
                for frame in step["subject_frames"]:
                    self.assertEqual(set(frame), {"inner", "spoken_aloud"})
                    self.assertNotIn("fatigue=", frame["inner"])
                    self.assertNotIn("world_epoch", frame["inner"])
        # Hypothesis preregistered, not assumed universally true: the
        # ecological controller MUST outperform its own bodily lesion on
        # at least one physical case, otherwise no causal evidence exists.
        self.assertGreater(
            report["totals"]["native_plus_motives"],
            report["totals"]["body_motive_lesion"],
        )
        self.assertEqual(report["totals"]["numeric_state_rules"], 5)
        # In the dual need case, the actual physical sequence has to
        # sleep BEFORE repairing an actually damaged apparatus.
        duo = next(x for x in report["trials"]
                   if x["case"] == "wear_and_fatigue" and
                   x["arm"] == "native_plus_motives")
        self.assertTrue(duo["completed_scored_sequence"])
        self.assertEqual(duo["actual_sequence"], ["rest", "repair"])
        self.assertGreater(duo["actual_apparatus"], 0)
        self.assertLess(duo["actual_fatigue"], 7)


if __name__ == "__main__":
    unittest.main()
