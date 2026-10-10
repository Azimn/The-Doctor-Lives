"""E4-A preregistered native Pretorius recurrent-vs-decoder audit tests.

Unit assertions concern deterministic software, controls, disjoint partitions,
and actual matrix/decoder transplants; never assert that a scientific
recurrent advantage *must* exist on developer-authored synthetic tasks.
"""
from __future__ import annotations

import json
import math
import unittest

import numpy as np

from doctor_lives.neural import ACTIONS, PretoriusRecurrentSubstrate
from scripts.run_eidolon_e4 import (
    ARMS, DELAY_TICKS, TRAIN_REPEATS, candidate_models, cases, config,
    evaluate, fixture_hash, run,
)


class EidolonE4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train, cls.test = cases()
        cls.report = run((197,))

    def test_actor_episode_and_text_holdouts_are_disjoint(self):
        self.assertEqual(len(self.train), 32)
        self.assertEqual(len(self.test), 16)
        for attr in ("actor", "episode", "text"):
            self.assertFalse(
                {case[attr] for case in self.train}
                & {case[attr] for case in self.test}
            )
        self.assertEqual(len(fixture_hash()), 64)

    def test_readout_is_ten_actions_and_never_learns_during_heldout(self):
        model = PretoriusRecurrentSubstrate(config(71))
        snapshot_w = model.W.data.copy()
        snapshot_motor = model.motor_w.copy()
        scores = evaluate(model, self.test[0]["text"])
        self.assertEqual(set(scores), {"direct", "delayed"})
        for part in scores.values():
            self.assertEqual(set(part["action_scores"]), set(ACTIONS))
            self.assertAlmostEqual(sum(part["action_scores"].values()), 1, places=6)
        np.testing.assert_array_equal(model.W.data, snapshot_w)
        np.testing.assert_array_equal(model.motor_w, snapshot_motor)

    def test_decoder_only_preserves_recurrent_weights_and_trial_count(self):
        _, audit = candidate_models(199, self.train)
        self.assertEqual(audit["recurrent_frobenius_change_decoder_only"], 0.0)
        self.assertEqual(audit["target_tick_hybrid"], audit["target_tick_decoder_only"])
        self.assertGreater(audit["motor_weight_change_decoder_only"], 0.0)

    def test_hybrid_lesion_equivalent_to_explicit_virgin_recurrent_transplant(self):
        arms, audit = candidate_models(211, self.train)
        x = arms["hybrid_recurrent_lesion"]
        y = arms["hybrid_virgin_recurrence_trained_decoder"]
        np.testing.assert_array_equal(x.W.data, y.W.data)
        np.testing.assert_array_equal(x.motor_w, y.motor_w)
        s1 = evaluate(x, self.test[0]["text"])
        s2 = evaluate(y, self.test[0]["text"])
        self.assertEqual(s1, s2)
        self.assertEqual(audit["recurrent_frobenius_change_decoder_only"], 0.0)

    def test_fresh_decoder_restores_exact_virgin_motor_weights(self):
        arms, _ = candidate_models(223, self.train)
        virgin = arms["untrained"]
        fresh = arms["hybrid_fresh_decoder"]
        np.testing.assert_array_equal(fresh.motor_w, virgin.motor_w)
        np.testing.assert_array_equal(fresh.motor_b, virgin.motor_b)
        self.assertFalse(np.array_equal(fresh.motor_w, arms["hybrid"].motor_w))

    def test_all_seven_arms_report_all_ten_actions_and_long_delay(self):
        report = self.report
        self.assertEqual(set(report["summary"]), set(ARMS))
        self.assertEqual(report["delay_ticks"], DELAY_TICKS)
        self.assertEqual(report["train_repeats"], TRAIN_REPEATS)
        self.assertEqual(len(report["rows"]), len(ARMS) * 16 * 2)
        for arm in ARMS:
            for delay in ("direct", "delayed"):
                x = report["summary"][arm][delay]
                self.assertEqual(x["n"], 16)
                self.assertTrue(0 <= x["correct_top1"] <= x["n"])
                self.assertTrue(math.isfinite(x["mean_target_log_loss"]))
        for r in report["rows"]:
            self.assertEqual(set(r["scores"]), set(ACTIONS))
            self.assertIn(r["target"], ACTIONS)
            self.assertTrue(math.isfinite(r["target_log_loss"]))
            self.assertGreater(r["target_probability"], 0.0)

    def test_deterministic_replay_for_same_seed(self):
        second = run((197,))
        prior = {k: v for k, v in self.report.items()
                 if k not in ("timing_seconds", "github_sha")}
        repeat = {k: v for k, v in second.items()
                  if k not in ("timing_seconds", "github_sha")}
        self.assertEqual(json.dumps(prior, sort_keys=True),
                         json.dumps(repeat, sort_keys=True))

    def test_invalid_seed_lists_rejected(self):
        for bad in ((), (1, 1), (-1,), (True,), (1.4,), ("7",)):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    run(bad)


if __name__ == "__main__":
    unittest.main()
