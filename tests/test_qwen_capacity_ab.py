"""Contract tests for two-model speech-capacity experiment and blind design."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

HAVE = (importlib.util.find_spec("synthetic_ipseity") is not None
        and importlib.util.find_spec("sensus_artificialis") is not None)
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))


@unittest.skipUnless(HAVE,"Reviewed donor dependencies required")
class CapacityExperimentTests(unittest.TestCase):
    def setUp(self):
        import pretorius_qwen_capacity_ab as probe
        self.probe=probe

    def test_real_brain_capture_paired_models_without_network(self):
        seen={m:[] for m in self.probe.MODELS}
        def fake(model):
            def emit(subject,system):
                seen[model].append((subject,system))
                return "I am uncertain about the evidence."
            return emit
        with tempfile.TemporaryDirectory() as td:
            metrics=self.probe.run(
                Path(td),transports={m:fake(m) for m in self.probe.MODELS}
            )
            self.assertEqual(metrics["matched_frames"],6)
            self.assertEqual(metrics["model_responses"],12)
            self.assertFalse(metrics["release_approved"])
            self.assertEqual(metrics["human_judgments_collected"],0)
            for model in self.probe.MODELS:
                self.assertEqual(metrics["by_model"][model]["accepted_primary"],6)
                self.assertEqual(metrics["by_model"][model]["fallback"],0)
                self.assertEqual(len(seen[model]),6)
                self.assertTrue(all("Direct-speech task" in system
                                    for _,system in seen[model]))
                self.assertTrue(all("source_ref" not in subject
                                    for subject,_ in seen[model]))
            import json
            out=Path(td)
            blind=[json.loads(line) for line in (out/"blind_review.jsonl").read_text().splitlines()]
            keys=[json.loads(line) for line in (out/"separate_key.jsonl").read_text().splitlines()]
            self.assertEqual(len(blind),12)
            self.assertEqual({x["candidate_id"] for x in blind},
                             {x["candidate_id"] for x in keys})
            self.assertFalse(any("model" in x or "disposition" in x for x in blind))

    def test_heuristic_copy_and_loops_do_not_become_human_verdicts(self):
        full="I remember two later observations of the laboratory balance reading agreeing at 451 grams."
        bad=self.probe._diagnose(full+" "+full+" "+full,full,"question")
        self.assertTrue(bad["verbatim_long_frame_copy"])
        self.assertTrue(bad["repeated_five_word_phrase"])
        self.assertFalse(bad["groundedness_or_naturalness_human_judged"])
        okay=self.probe._diagnose("I must examine that carefully.",full,"question")
        self.assertFalse(okay["verbatim_long_frame_copy"])
        self.assertFalse(okay["repeated_five_word_phrase"])


if __name__=="__main__":
    unittest.main()
