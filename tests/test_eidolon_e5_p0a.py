"""E5-P0A real policy bridge: no evaluator leakage, no oracle substitution.

PASS means the native think/Noetic readout pathways actually ran on identical
persistent lab states, NOT that any learned system mastered the six tasks.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from doctor_lives.eidolon_lab_action_bridge import (
    CLASS_TO_VERBS, candidates, native_class_to_primitive,
    public_cue, public_only, select_primitive,
)
from doctor_lives.neural import ACTIONS
from doctor_lives.eidolon_outcome_lab import LaboratoryWorld
from scripts.run_eidolon_e5 import DEFAULT_SUITE, load_suite
from scripts.run_eidolon_e5_p0a import (
    NEURAL_ARMS, POLICIES, NativeBrainController, NoeticDonors,
    run, run_case_policy,
)


class E5NativePolicyLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite,cls.suite_hash=load_suite(DEFAULT_SUITE)
        cls.report=run()

    def test_all_cognitive_arms_act_on_fresh_matching_worlds(self):
        r=self.report
        self.assertEqual(r["total_case_policy_runs"],6*len(POLICIES))
        self.assertEqual(set(r["policies"]),set(POLICIES))
        self.assertTrue(r["worlds_start_equivalent"])
        self.assertTrue(r["all_worlds_replayed"])
        self.assertEqual(r["suite_sha256"],self.suite_hash)
        self.assertIn("NOT_INDEPENDENT",r["suite_status"])
        self.assertEqual(len(r["rows"]),36)
        for row in r["rows"]:
            self.assertTrue(row["replayed_identically"])
            self.assertLessEqual(row["action_count"],6)
            if row["policy"] in NEURAL_ARMS:
                for step in row["actions"]:
                    self.assertEqual(set(step["full_ten_action_scores"]),set(ACTIONS))
                    self.assertIn(step["neural_selected_tendency"],ACTIONS)
                    self.assertEqual(
                        step["neural_selected_tendency"],
                        max(ACTIONS,key=step["full_ten_action_scores"].get)
                    )
                    self.assertEqual(step["adapter_audit"]["translator_class"],
                                     step["neural_selected_tendency"])

    def test_existing_e5_development_baselines_reproduce(self):
        r=self.report["summary"]
        self.assertEqual(r["no_op"]["completed"],0)
        self.assertEqual(r["keyword_baseline"]["completed"],6)
        self.assertEqual(r["keyword_baseline"]["actions"],16)
        self.assertEqual(r["no_op"]["actions"],36)

    def test_native_pretorius_actual_think_writes_only_disposable_brain(self):
        native_rows=[r for r in self.report["rows"] if r["policy"]=="native_pretorius"]
        self.assertEqual(len(native_rows),6)
        self.assertGreater(sum(r["actual_native_think_calls"] for r in native_rows),0)
        for r in native_rows:
            self.assertEqual(r["actual_native_think_calls"],r["action_count"])
            for action in r["actions"]:
                audit=action["model_audit"]
                self.assertTrue(audit["actual_think_call"])
                self.assertTrue(audit["native_bridge_enabled"])
                self.assertTrue(audit["policy_version"])

    def test_noetic_W_lesion_keeps_exact_same_readout(self):
        d=self.report["Noetic_donor_audit"]
        self.assertGreater(d["native_recurrent_change_norm"],1e-8)
        self.assertNotEqual(d["learned_W_sha256"],d["virgin_W_sha256"])
        self.assertTrue(d["lesioned_W_matches_virgin"])
        self.assertTrue(d["noetic_readout_reused_exactly_for_lesion"])
        self.assertEqual(d["E5_training_presentations"],0)
        donor=NoeticDonors()
        np.testing.assert_array_equal(donor.lesion.W.data,donor.virgin.W.data)
        np.testing.assert_array_equal(
            donor.models["noetic_balanced"][1].weights,
            donor.models["noetic_virgin_W_lesion"][1].weights
        )

    def test_adapter_will_not_see_private_scoring_or_case_id(self):
        case=self.suite["cases"][0]
        with tempfile.TemporaryDirectory() as t:
            world=LaboratoryWorld(Path(t)/"world.json",case)
            obs=world.public_observation()
            tainted=deepcopy(obs)
            tainted["expected"]={"predicates":[{"kind":"make_everything_pass"}]}
            tainted["case_id"]="hidden-test-label"
            self.assertEqual(public_cue(obs),public_cue(tainted))
            self.assertEqual(candidates(obs),candidates(tainted))
            self.assertEqual(public_only(obs),public_only(tainted))
            self.assertNotIn("expected",public_cue(tainted))
            self.assertNotIn("case_id",public_cue(tainted))

    def test_no_skipping_top_native_action_to_find_convenient_verb(self):
        case=self.suite["cases"][0]
        with tempfile.TemporaryDirectory() as t:
            world=LaboratoryWorld(Path(t)/"world.json",case)
            obs=world.public_observation()
            # Repair is not yet available; learner says create. Explicit
            # abstention, not secretly inspect/read with keyword plan.
            action,audit=select_primitive("create",obs)
            self.assertEqual(action,{"verb":"wait"})
            self.assertTrue(audit["abstained_no_affordance"])
            values={a:0.0 for a in ACTIONS}
            values["create"]=1.0
            tendency,action2,audit2=native_class_to_primitive(values,obs)
            self.assertEqual(tendency,"create")
            self.assertEqual(action2,{"verb":"wait"})

    def test_public_affordances_apply_across_cases_without_goal_plan(self):
        case=self.suite["cases"][1]
        with tempfile.TemporaryDirectory() as t:
            world=LaboratoryWorld(Path(t)/"world.json",case)
            obs=world.public_observation()
            allowed={x["verb"] for x in candidates(obs)}
            self.assertIn("inspect",allowed)
            self.assertNotIn("move",allowed)
            world.step({"verb":"inspect","id":"beaker"})
            obs=world.public_observation()
            allowed={x["verb"] for x in candidates(obs)}
            self.assertIn("move",allowed)
            action,_=select_primitive("cooperate",obs)
            self.assertEqual(action["verb"],"move")
            self.assertIn(action["to"],obs["rooms"])
            self.assertNotEqual(action["to"],"bench")

    def test_attribution_never_overrides_world_source_gate(self):
        case=self.suite["cases"][3]
        with tempfile.TemporaryDirectory() as t:
            world=LaboratoryWorld(Path(t)/"world.json",case)
            obs=world.public_observation()
            action,_=select_primitive("challenge",obs)
            self.assertEqual(action["verb"],"reject")
            forced={"verb":"attribute","id":"claim"}
            feedback=world.step(forced)
            self.assertFalse(feedback["ok"])
            self.assertEqual(feedback["reason"],"unverified_first_person")
            self.assertEqual(world.state["lived_event_ids"],[])
            self.assertEqual(LaboratoryWorld(Path(t)/"world.json",case).state["lived_event_ids"],[])

    def test_native_action_map_is_complete_and_all_tool_verbs_explicit(self):
        self.assertEqual(set(CLASS_TO_VERBS),set(ACTIONS))
        self.assertEqual(CLASS_TO_VERBS["persist"],("resolve",))
        self.assertEqual(CLASS_TO_VERBS["challenge"],("reject",))
        self.assertEqual(CLASS_TO_VERBS["create"],("repair","bookmark"))

    def test_external_suite_requires_sha_and_remains_unverified(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"candidate.json"
            path.write_bytes(DEFAULT_SUITE.read_bytes())
            with self.assertRaises(ValueError):
                run(path)
            with self.assertRaises(ValueError):
                run(path,expected_sha256="0"*64)

    def test_no_unsupported_claim_that_neural_training_was_on_laboratory(self):
        self.assertEqual(self.report["Noetic_donor_audit"]["E5_training_presentations"],0)
        for policy in ("noetic_balanced","noetic_virgin_W_lesion",
                       "fixed_reservoir_balanced"):
            for r in self.report["rows"]:
                if r["policy"]==policy:
                    self.assertTrue(all(x["model_audit"]["E5_training"] is False
                                        for x in r["actions"]))


if __name__=="__main__":
    unittest.main()
