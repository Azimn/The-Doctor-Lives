"""E4-C batch decoder: numerical order-invariance and causality contracts."""
from __future__ import annotations

import json
import unittest

import numpy as np

from doctor_lives.eidolon_balanced_decoder import (
    BalancedReadout, native_features, DELAYS, RIDGE_ALPHA,
)
from doctor_lives.neural import ACTIONS, PretoriusRecurrentSubstrate
from scripts.run_eidolon_e4 import cases, config, fixture_hash
from scripts.run_eidolon_e4c import (
    ARMS, collect_features, fit_and_check_order, run,
)


class BalancedDecoderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train, cls.test = cases()
        cls.report = run((331,))

    def test_batch_solution_fits_all_ten_actions_and_four_balanced_classes(self):
        model = PretoriusRecurrentSubstrate(config(333))
        X, labels, _ = collect_features(model, self.train)
        self.assertEqual(X.shape,(len(self.train)*len(DELAYS),128))
        learned = BalancedReadout.fit(X, labels)
        self.assertEqual(learned.n_rows,96)
        self.assertEqual(set(learned.training_classes),
                         {"create","persist","cooperate","challenge"})
        s=learned.scores(X[0])
        self.assertEqual(set(s),set(ACTIONS))
        self.assertAlmostEqual(sum(s.values()),1,places=8)

    def test_solve_invariant_to_four_presentation_order_rotations(self):
        model=PretoriusRecurrentSubstrate(config(337))
        X,labels,_=collect_features(model,self.train)
        out,audit=fit_and_check_order(X,labels,self.train)
        self.assertEqual(audit["orders_tested"],4)
        self.assertLess(audit["max_weight_difference_by_order"],1e-6)
        self.assertLess(audit["max_center_difference_by_order"],1e-6)
        self.assertEqual(set(audit["class_counts"].values()),{24})

    def test_invalid_label_balance_finite_and_shape_fail_closed(self):
        X=np.zeros((4,8),dtype=np.float64)
        for labels in (["create"]*4,["create","create","persist","challenge"],
                       ["create","persist","unknown","challenge"]):
            with self.subTest(labels=labels):
                with self.assertRaises(ValueError):
                    BalancedReadout.fit(X,labels)
        with self.assertRaises(ValueError):
            BalancedReadout.fit(np.array([[np.nan]*8]*4),["create","persist","create","persist"])
        with self.assertRaises(ValueError):
            BalancedReadout.fit(X,["create","persist","create","persist"],alpha=0)
        decoder=BalancedReadout.fit(X,["create","persist","create","persist"])
        with self.assertRaises(ValueError):
            decoder.scores(np.zeros(10))

    def test_feature_read_does_not_mutate_native_state_or_weights(self):
        model=PretoriusRecurrentSubstrate(config(347))
        old=(model.tick,model.W.data.copy(),model.motor_w.copy(),model.rate.copy())
        result=native_features(model,self.test[0]["text"])
        self.assertEqual(set(result),set(DELAYS))
        self.assertEqual(model.tick,old[0])
        np.testing.assert_array_equal(model.W.data,old[1])
        np.testing.assert_array_equal(model.motor_w,old[2])
        np.testing.assert_array_equal(model.rate,old[3])

    def test_one_seed_has_expected_complete_control_grid(self):
        report=self.report
        self.assertEqual(report["fixture_sha256"],fixture_hash())
        self.assertEqual(report["seeds"],[331])
        self.assertEqual(len(report["rows"]),len(ARMS)*len(self.test)*len(DELAYS))
        self.assertTrue(report["class_balanced_batch"])
        self.assertEqual(report["alpha"],RIDGE_ALPHA)
        for row in report["rows"]:
            self.assertEqual(set(row["scores"]),set(ACTIONS))
            self.assertAlmostEqual(sum(row["scores"].values()),1,places=6)
            self.assertGreater(row["target_probability"],0)
        audit=report["audits"][0]
        self.assertGreater(audit["noetic_recurrent_change_norm"],1e-8)
        self.assertEqual(audit["virgin_recurrent_change_norm"],0)
        self.assertEqual(audit["noetic_teacher_updates"],160)
        self.assertEqual(audit["balanced_feature_count"],96)

    def test_fresh_virgin_solution_is_equivalent_and_not_new_scientific_arm(self):
        a=[r for r in self.report["rows"] if r["arm"]=="virgin_W_balanced"]
        b=[r for r in self.report["rows"] if r["arm"]=="virgin_W_fresh_balanced_decoder"]
        self.assertEqual(len(a),len(b))
        for old,new in zip(a,b):
            self.assertEqual(old["case"],new["case"])
            self.assertEqual(old["delay"],new["delay"])
            for action in ACTIONS:
                self.assertAlmostEqual(old["scores"][action],
                                       new["scores"][action],places=6)

    def test_repeatability_under_fixed_seed(self):
        a={k:v for k,v in self.report.items() if k not in ("runtime_seconds","source_sha")}
        b={k:v for k,v in run((331,)).items() if k not in ("runtime_seconds","source_sha")}
        self.assertEqual(json.dumps(a,sort_keys=True),json.dumps(b,sort_keys=True))

    def test_bad_seeds_rejected(self):
        for bad in ((),(3,3),(-1,),(True,),("bad",)):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    run(bad)


if __name__=="__main__":
    unittest.main()
