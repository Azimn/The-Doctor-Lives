"""The focus-quality screen is engineering telemetry, never release approval."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from pretorius_focus_response_audit import diagnose, score


class FocusQualityScreenTests(unittest.TestCase):
    def test_repeated_loop_and_writing_about_sentences_are_detected(self):
        loop=("I'm so glad you're here. "*12).strip()
        d=diagnose(loop,"I feel curious about what comes next.")
        self.assertTrue(d["runaway_5gram_repetition"])
        self.assertTrue(d["screen_failure"])
        meta=diagnose(
            'The next sentence could be: "I should listen to the visitor."',
            "I read the visitor's words: “Are you listening?”"
        )
        self.assertTrue(meta["writing_or_reader_commentary"])
        self.assertTrue(meta["screen_failure"])

    def test_renamed_prompt_copy_is_still_copy(self):
        same='I read the visitor\'s words: “What do you remember?”'
        d=diagnose(same,same)
        self.assertTrue(d["spoken_prompt_framing"])
        self.assertTrue(d["verbatim_input_line_copy"])

    def test_short_normal_first_person_not_mechanically_rejected(self):
        d=diagnose(
            "I must examine the balance again before I can be certain.",
            "I notice: The laboratory balance is unsettled."
        )
        self.assertFalse(d["screen_failure"])
        self.assertFalse(d["runaway_5gram_repetition"])

    def test_fallback_and_primary_grouped_but_release_always_held(self):
        def row(cond,turn,spoken,disposition="primary"):
            return dict(source_arm=0,turn=turn,model="smollm2:135m",
                        condition=cond,disposition=disposition,
                        delivered=spoken,
                        renderer_input_text="I feel uncertain about the experiment.")
        data=[
            row("full",0,"I cannot settle that.","fallback"),
            row("focused",0,"I am uncertain."),
            row("full",1,"I am uncertain."),
            row("focused",1,"I read the visitor's words: “Hello?”"),
        ]
        summary=score(data,{"paired_conditions":4})
        self.assertEqual(summary["by_model"]["smollm2:135m"]["full"]["fallback"],1)
        self.assertEqual(summary["by_model"]["smollm2:135m"]["focused"]["spoken_frame_framing"],1)
        self.assertEqual(summary["release_decision"],"HOLD")
        self.assertFalse(summary["human_blind_ratings_available"])

    def test_duplicate_pair_fails_closed(self):
        row=dict(source_arm=0,turn=0,model="m",condition="full",
                 disposition="primary",delivered="I know.",
                 renderer_input_text="I think.")
        with self.assertRaises(ValueError):
            score([row,row],{"paired_conditions":2})


if __name__=="__main__":
    unittest.main()
