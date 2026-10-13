"""Standalone mechanics for sustained Pretorius conversation acceptance runner.

Actual subject cognition / memory / policy / Sensus / durable Ipseity are real.
Only the language renderers are deterministic fakes in this unit test; the
GitHub Ollama job separately runs the same study on actual CPU models.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HAVE = (
    importlib.util.find_spec("synthetic_ipseity") is not None
    and importlib.util.find_spec("sensus_artificialis") is not None
)


@unittest.skipUnless(HAVE, "Both reviewed optional donors needed for real runtime")
class SustainedDialogueAcceptanceTests(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
        import pretorius_sustained_dialogue_acceptance as study
        self.study = study

    def test_two_real_host_stories_model_swap_restarts_and_separate_judge_key(self):
        study = self.study
        texts = {"smollm2:135m": [], "qwen2.5:0.5b": []}
        transports = {
            m: (lambda text, instruction, name=m: (
                texts[name].append((text, instruction))
                or "I cannot be certain without stronger evidence."
            )) for m in study.MODELS
        }
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "ballots"
            result = study.run(dest, transports=transports)
            rows = [json.loads(x) for x in (
                dest / "engineering_transcript.jsonl"
            ).read_text().splitlines()]
            ballots = [json.loads(x) for x in (
                dest / "blind_judge_ballots.jsonl"
            ).read_text().splitlines()]
            keys = [json.loads(x) for x in (
                dest / "separate_condition_key.jsonl"
            ).read_text().splitlines()]
            self.assertEqual(result["sessions"], 2)
            self.assertEqual(result["turns"], 24)
            self.assertEqual(result["actual_model_calls"], 24)
            self.assertEqual(result["primary"], 24)
            self.assertEqual(result["fallback"], 0)
            self.assertEqual(result["repaired"], 0)
            self.assertEqual(result["verified_recollection_frames_at_probe_turns"], 6)
            self.assertEqual(len(ballots), 24)
            self.assertEqual(len(keys), 24)
            self.assertEqual(len({r["decision_id"] for r in rows}), 24)
            self.assertEqual({r["arm"] for r in rows}, {0, 1})
            self.assertFalse(result["release_approved"])
            self.assertEqual(result["human_judgments_collected"], 0)
            for a in (0, 1):
                sub = [r for r in rows if r["arm"] == a]
                self.assertEqual(len(sub), 12)
                self.assertNotEqual(sub[5]["model"], sub[6]["model"])
                self.assertEqual([r["turn"] for r in sub], list(range(12)))
                self.assertEqual(sub[1]["scene_conflicts"], 1)
                self.assertEqual(sub[3]["resolved_gap_ids"], 1)
                self.assertTrue(all(r["policy_rows"] >= i + 1
                                    for i, r in enumerate(sub)))
                self.assertTrue(all(r["speech"].startswith("I ") for r in sub))
            for name in study.MODELS:
                self.assertEqual(len(texts[name]), 12)
                self.assertTrue(all("Direct-speech task" in instruction
                                    for _, instruction in texts[name]))
                self.assertTrue(all("source_ref" not in frame
                                    for frame, _ in texts[name]))
            for row in ballots:
                self.assertNotIn("model", row)
                self.assertNotIn("arm", row)
                self.assertNotIn("disposition", row)
                self.assertNotIn("subject_frame", row)
                self.assertNotIn("approved_value", row)
            self.assertEqual({r["candidate_id"] for r in ballots},
                             {r["candidate_id"] for r in keys})

    def test_blind_packets_do_not_expose_key_and_are_repeatable(self):
        study = self.study
        pretend = [
            {"arm": a, "turn": t, "model": study.model_for(a, t),
             "disposition": "fallback" if t == 2 else "primary",
             "speech": "I remain uncertain.", "subject_sha256": "hash",
             "user_message": "What did you see?"}
            for a in (0, 1) for t in range(12)
        ]
        first, keys = study.blind_ballots(pretend)
        second, keys2 = study.blind_ballots(pretend)
        self.assertEqual(first, second)
        self.assertEqual(keys, keys2)
        self.assertTrue(all("model" not in x for x in first))
        self.assertTrue(all("model" in x for x in keys))


if __name__ == "__main__":
    unittest.main()
