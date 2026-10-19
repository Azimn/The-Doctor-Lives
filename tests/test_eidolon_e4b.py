"""E4-B Noetic Crucible mechanistic controls; no independent cognitive claim."""
from __future__ import annotations

from dataclasses import replace
import json
import math
import unittest

import numpy as np

from doctor_lives.eidolon_noetic import (
    NoeticCrucible, SyntheticOutcomeGrant, GRANT_CLASS,
)
from doctor_lives.neural import ACTIONS, PretoriusRecurrentSubstrate
from scripts.run_eidolon_e4 import cases, config, fixture_hash
from scripts.run_eidolon_e4b import (
    ARMS, DELAYS, SEEDS, candidate_models, ordered, run,
)


class NoeticE4BTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train, cls.test = cases()
        cls.one_seed = run((257,))

    def test_admissibility_denies_untrusted_actor_source_outcome_and_text(self):
        item=self.train[0]
        n=PretoriusRecurrentSubstrate(config(71))
        gate=NoeticCrucible(n)
        grant=SyntheticOutcomeGrant.for_fixture(
            event_id="synthetic-001",actor=item["actor"],
            text=item["text"],action=item["action"])
        for denied in (
            replace(grant,evidence_class="external_statement"),
            replace(grant,verified_outcome=False),
            replace(grant,actor="Unknown"),
            replace(grant,text_sha256="0"*64),
            replace(grant,action="challenge" if item["action"]!="challenge" else "create"),
        ):
            with self.subTest(denied=denied):
                w=n.W.data.copy()
                motor=n.motor_w.copy()
                tick=n.tick
                accepted=gate.teach(
                    event_id="synthetic-001",actor=item["actor"],
                    text=item["text"],action=item["action"],grant=denied,
                    update_recurrence=True,
                )
                self.assertFalse(accepted)
                self.assertEqual(n.tick,tick)
                np.testing.assert_array_equal(n.W.data,w)
                np.testing.assert_array_equal(n.motor_w,motor)
        self.assertEqual(gate.accepted_outcomes,0)
        self.assertEqual(gate.denied_outcomes,5)

    def test_teacher_never_injected_at_inference(self):
        x=PretoriusRecurrentSubstrate(config(59))
        grant=SyntheticOutcomeGrant.for_fixture(
            event_id="synthetic",actor="Ada",text="Construct a lens",
            action="create")
        gate=NoeticCrucible(x)
        self.assertTrue(gate.teach(
            event_id="synthetic",actor="Ada",text="Construct a lens",
            action="create",grant=grant,update_recurrence=True))
        before=x.W.data.copy()
        from scripts.run_eidolon_e4b import evaluate
        eval_scores=evaluate(x,"A different device")
        self.assertEqual(set(eval_scores),set(DELAYS))
        np.testing.assert_array_equal(x.W.data,before)

    def test_all_conditions_share_class_balanced_training_exposure(self):
        train_order=ordered(self.train)
        self.assertEqual(len(train_order),32)
        self.assertEqual([x["action"] for x in train_order[:4]],
                         ["create","persist","cooperate","challenge"])
        models,audit=candidate_models(271,self.train)
        self.assertEqual(set(models),set(ARMS))
        for name in ("noetic","decoder_only","shuffled_outcome"):
            self.assertEqual(audit[name]["train_ticks"],160)
            self.assertEqual(audit[name]["accepted_synthetic_grants"],160)
        self.assertEqual(audit["fresh_trained"]["fresh_decoder_train_ticks"],160)
        self.assertEqual(audit["virgin_fresh_trained"]["fresh_decoder_train_ticks"],160)
        self.assertGreater(audit["noetic"]["recurrent_change_norm"],1e-8)
        self.assertEqual(audit["decoder_only"]["recurrent_change_norm"],0)

    def test_recurrent_lesion_preserves_trained_motor_and_virgin_weights(self):
        models,audit=candidate_models(283,self.train)
        virgin=models["virgin"]
        hybrid=models["noetic_hybrid"]
        lesion=models["noetic_recurrent_lesion"]
        np.testing.assert_array_equal(lesion.W.data,virgin.W.data)
        np.testing.assert_array_equal(lesion.motor_w,hybrid.motor_w)
        np.testing.assert_array_equal(lesion.motor_b,hybrid.motor_b)
        self.assertFalse(np.array_equal(hybrid.W.data,virgin.W.data))
        self.assertTrue(audit["noetic_v_lesion_same_motor"])

    def test_fresh_decoder_is_retrained_and_recurrence_is_unchanged(self):
        models,audit=candidate_models(293,self.train)
        new=models["noetic_fresh_trained_decoder"]
        old=models["noetic_hybrid"]
        virgin=models["virgin"]
        np.testing.assert_array_equal(new.W.data,old.W.data)
        self.assertFalse(np.array_equal(new.motor_w,virgin.motor_w))
        np.testing.assert_array_equal(models["virgin_recurrence_fresh_trained_decoder"].W.data,virgin.W.data)
        np.testing.assert_array_equal(models["noetic_fresh_untrained_decoder"].motor_w,virgin.motor_w)
        self.assertTrue(audit["fresh_readout_preserves_learned_W"])

    def test_full_trial_grid_finite_scores_and_probability(self):
        d=self.one_seed
        self.assertEqual(d["fixture_sha256"],fixture_hash())
        self.assertEqual(d["seeds"],[257])
        self.assertEqual(len(d["rows"]),len(ARMS)*16*len(DELAYS))
        self.assertTrue(d["synthetic_source_grants_not_authenticated"])
        self.assertEqual(d["delays"],list(DELAYS))
        for row in d["rows"]:
            self.assertEqual(set(row["scores"]),set(ACTIONS))
            self.assertGreater(row["target_probability"],0)
            self.assertTrue(math.isfinite(row["target_log_loss"]))
            self.assertLess(abs(sum(row["scores"].values())-1),1e-6)

    def test_deterministic_seed_replay_ignoring_clock(self):
        a=self.one_seed
        b=run((257,))
        a={k:v for k,v in a.items() if k not in ("runtime_seconds","github_sha")}
        b={k:v for k,v in b.items() if k not in ("runtime_seconds","github_sha")}
        self.assertEqual(json.dumps(a,sort_keys=True),json.dumps(b,sort_keys=True))

    def test_fail_closed_seed_list(self):
        for invalid in ((),(1,1),(-1,),(True,),("hello",)):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    run(invalid)

    def test_learner_does_not_require_legacy_production_mutations(self):
        from doctor_lives import PretoriusBrain
        import inspect
        self.assertNotIn("eidolon_noetic",inspect.getsource(PretoriusBrain.think))
        self.assertNotIn("eidolon_noetic",inspect.getsource(PretoriusBrain.ingest))


if __name__=="__main__":
    unittest.main()
