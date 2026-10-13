"""Renderer quality report is an audit, not a replacement for human judges."""
from __future__ import annotations
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from pretorius_sustained_dialogue_score import screen


class RendererQualityScreenTests(unittest.TestCase):
    def sample(self, response, model="small", disposition="primary"):
        return {
            "arm": 0, "turn": 0, "speech": response, "model": model,
            "disposition": disposition,
            "subject_frame": (
                "I recognize this as part of the description I was built from, "
                "not something I remember happening: I am Doctor Pretorius."
            ),
        }

    def test_copying_fallback_and_weak_screen_never_authorize_release(self):
        copied = self.sample(
            "I recognize this as part of the description I was built from, "
            "not something I remember happening: I am Doctor Pretorius."
        )
        fallback = self.sample("I cannot establish this.", disposition="fallback")
        fallback["turn"] = 1
        report = screen([copied, fallback], {"turns": 2})
        self.assertEqual(report["by_model"]["small"]["fallback"], 1)
        self.assertEqual(report["by_model"]["small"]["verbatim_frame_copy_outputs"], 1)
        self.assertEqual(report["release_gate"], "HOLD")
        self.assertFalse(report["screen_pass"])
        self.assertFalse(report["blind_human_scores_available"])

    def test_natural_reply_can_pass_mechanical_screen_but_not_human_gate(self):
        data = screen([self.sample("I am not certain yet.")], {"turns": 1})
        self.assertTrue(data["screen_pass"])
        self.assertEqual(data["release_gate"], "HOLD")

    def test_bad_or_replayed_transcript_refuses_to_score(self):
        x = self.sample("I have questions.")
        with self.assertRaises(ValueError):
            screen([x, x], {"turns": 2})
        with self.assertRaises(ValueError):
            screen([x], {"turns": 3})


if __name__ == "__main__":
    unittest.main()
