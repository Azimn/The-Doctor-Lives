"""Stage 01B: source chronologies and renderer evidence parity."""
import unittest

from research_prototypes.character_state.run_chronological_1b import (
    ARM_NAMES, CASES, prepare_native_sequence, SCHEMA,
)


class ChronologicalPretoriusTests(unittest.TestCase):
    def test_four_native_stages_and_eight_reserved_prompts(self):
        result=prepare_native_sequence()
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual(result["stage_count"], 4)
        self.assertEqual(result["case_count"], 8)
        self.assertEqual(len(result["cases"]), 8)
        self.assertEqual(
            [x["stage"] for x in result["cases"]],
            [stage for _id, stage, _q, _criterion in CASES],
        )
        self.assertEqual(result["external_world_outcomes"], 0)
        self.assertTrue(result["production_brain_unchanged"])

    def test_natively_witnessed_transition_never_rewrites_root(self):
        result=prepare_native_sequence()
        seq=result["timeline"]
        self.assertEqual(len(seq), 4)
        self.assertFalse(seq[0]["fixture_calibration_open"])
        self.assertFalse(seq[0]["fixture_notebook_open"])
        self.assertTrue(seq[1]["fixture_calibration_open"])
        self.assertFalse(seq[1]["fixture_notebook_open"])
        self.assertTrue(seq[2]["fixture_calibration_open"])
        self.assertTrue(seq[2]["fixture_notebook_open"])
        self.assertFalse(seq[3]["fixture_calibration_open"])
        self.assertTrue(seq[3]["fixture_notebook_open"])
        self.assertEqual(len({x["identity_digest"] for x in seq}), 1)
        self.assertEqual(len({x["manifest_digest"] for x in seq}), 1)
        self.assertTrue(all(seq[i]["state_version"] <= seq[i+1]["state_version"]
                            for i in range(3)))

    def test_information_parity_and_future_mask(self):
        result=prepare_native_sequence()
        for case in result["cases"]:
            self.assertTrue(case["equal_evidence_flat_phase"])
            self.assertEqual(set(case["arm_inputs"]), set(ARM_NAMES))
            self.assertEqual(set(case["arm_input_chars"]), set(ARM_NAMES))
            self.assertNotIn("private_state_version=", case["arm_inputs"]["evolving_phase"])
            self.assertNotIn("canon_rank=", case["arm_inputs"]["evolving_phase"])
            self.assertNotIn("source_digest=", case["arm_inputs"]["evolving_phase"])
            self.assertNotIn("world_witnesses=", case["arm_inputs"]["evolving_phase"])
            self.assertTrue(case["arm_input_chars"]["history_control"] >
                            case["arm_input_chars"]["evolving_flat"])
            if case["stage"] == 0:
                self.assertEqual(case["arm_inputs"]["static_flat"],
                                 case["arm_inputs"]["evolving_flat"])


if __name__ == "__main__":
    unittest.main()
