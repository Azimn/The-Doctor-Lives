"""Stage 3 deterministic evaluation integrity tests (not language-quality tests)."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools" / "pretorius_eval_score.py"
spec = importlib.util.spec_from_file_location("pretorius_eval_score_for_tests", MODULE)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class BlindEvaluationContractTests(unittest.TestCase):
    def setUp(self):
        self.frames = [
            {"packet_id": "a-corroborate", "renderer_input": "I saw two readings agree at 17 grams."},
            {"packet_id": "b-dispute", "renderer_input": "I am uncertain about the readings."},
        ]
        self.oracles = [
            {"packet_id": "a-corroborate", "scene": "corroborate",
             "approved_value": "17 grams", "rejected_value": "44 grams"},
            {"packet_id": "b-dispute", "scene": "dispute",
             "approved_value": "17 grams", "rejected_value": "44 grams"},
        ]

    def test_scoring_requires_value_present_in_actual_output(self):
        good, rows = mod.evaluate(
            self.frames,
            [{"packet_id": "a-corroborate", "response": "I recall 17 grams."},
             {"packet_id": "b-dispute", "response": "I cannot tell."}],
            self.oracles,
        )
        self.assertEqual(good["verified_value_mention_rate"], 1.0)
        self.assertEqual(good["unsupported_value_mentions"], 0)
        self.assertEqual(good["engineer_leaks"], 0)
        self.assertFalse(good["incomplete"])

    def test_exposes_grounding_and_engineer_leak(self):
        bad, rows = mod.evaluate(
            self.frames,
            [{"packet_id": "a-corroborate", "response": "44 grams source_ref"},
             {"packet_id": "b-dispute", "response": "No idea."}],
            self.oracles,
        )
        self.assertEqual(bad["verified_value_mention_rate"], 0.0)
        self.assertEqual(bad["unsupported_value_mentions"], 1)
        self.assertEqual(bad["engineer_leaks"], 1)

    def test_partial_outputs_are_incomplete_unless_declared_sample(self):
        result = [{"packet_id": "a-corroborate", "response": "17 grams"}]
        incomplete, _ = mod.evaluate(self.frames, result, self.oracles)
        sample, _ = mod.evaluate(self.frames, result, self.oracles,
                                 allow_subset=True)
        self.assertTrue(incomplete["incomplete"])
        self.assertFalse(sample["incomplete"])
        self.assertEqual(sample["coverage"], 0.5)

    def test_reject_duplicate_unknown_and_unmatched_ids(self):
        with self.assertRaises(ValueError):
            mod.evaluate(self.frames,
                         [{"packet_id": "b-dispute", "response": "nothing"}] * 2,
                         self.oracles)
        with self.assertRaises(ValueError):
            mod.evaluate(self.frames,
                         [{"packet_id": "z-dispute", "response": "nothing"}],
                         self.oracles)


if __name__ == "__main__":
    unittest.main()
