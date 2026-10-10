"""Training-order recency control. Never force a desired empirical winner."""
from __future__ import annotations

import json
import unittest

from scripts.run_eidolon_e4b_order import ARMS, DELAYS, ORDERS, run


class NoeticOrderCrossoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=run((307,))

    def test_all_four_labels_rotated_into_terminal_position(self):
        self.assertEqual({x[-1] for x in ORDERS},
                         {"create","persist","cooperate","challenge"})
        self.assertEqual(len(self.report["orders"]),4)
        self.assertEqual(len(self.report["rows"]),4*2*16*len(DELAYS))

    def test_counts_and_weights_match_in_all_arms(self):
        for audit in self.report["fit_audits"]:
            self.assertEqual(audit["updates"],160)
            self.assertEqual(set(audit["training_class_counts"].values()),{40})
            self.assertGreater(audit["motor_change_norm"],0)
            if audit["arm"]=="noetic":
                self.assertGreater(audit["recurrent_change_norm"],1e-8)
            else:
                self.assertEqual(audit["recurrent_change_norm"],0)

    def test_output_is_calibrated_and_no_label_is_forced(self):
        for trial in self.report["rows"]:
            self.assertAlmostEqual(sum(trial["scores"].values()),1,places=6)
            self.assertTrue(trial["target_probability"]>0)
            self.assertIn(trial["predicted"],trial["scores"])
        # Do not assert selected final label: that is a falsifiable outcome.

    def test_deterministic_replay(self):
        a={k:v for k,v in self.report.items() if k not in ("runtime_seconds","github_sha")}
        b={k:v for k,v in run((307,)).items() if k not in ("runtime_seconds","github_sha")}
        self.assertEqual(json.dumps(a,sort_keys=True),json.dumps(b,sort_keys=True))

    def test_bad_seeds_are_rejected(self):
        for seeds in ((),(True,),(-1,),(1,1),("a",)):
            with self.subTest(seeds=seeds):
                with self.assertRaises(ValueError):
                    run(seeds)


if __name__=="__main__":
    unittest.main()
