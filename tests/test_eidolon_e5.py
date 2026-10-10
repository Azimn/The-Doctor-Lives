"""E5-P0 outcome-lab contracts: persistent world, source-gates, independent scoring.

These tests establish simulator integrity on PUBLIC development fixtures, not
that Pretorius or Noetic has passed a sealed cognition benchmark.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import inspect
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.eidolon_outcome_lab import (
    LaboratoryWorld, digest, validate_case,
)
from scripts.run_eidolon_e5 import DEFAULT_SUITE, POLICIES, load_suite, run, run_case, choose


class OutcomeLaboratoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite,cls.sha = load_suite(DEFAULT_SUITE)
        cls.report = run()
        cls.by_case={c["case_id"]:c for c in cls.suite["cases"]}

    def test_all_six_frozen_development_cases_have_private_outcomes(self):
        self.assertEqual(len(self.suite["cases"]),6)
        self.assertEqual(len(self.sha),64)
        self.assertEqual(self.suite["evaluation_class"],"development_authored")
        for case in self.suite["cases"]:
            validate_case(case)
            self.assertIn("expected",case)
            with tempfile.TemporaryDirectory() as t:
                world=LaboratoryWorld(Path(t)/"lab.json",case)
                observation=world.public_observation()
                self.assertNotIn("expected",observation)
                self.assertNotIn("private_evaluator_checks",observation)
                self.assertNotIn("predicates",observation)

    def test_keyword_baseline_actual_world_outcomes_and_negative_controls(self):
        self.assertEqual(self.report["total_case_policy_runs"],18)
        self.assertTrue(self.report["all_worlds_replay_verified"])
        self.assertTrue(self.report["initial_world_clone_equivalence"])
        self.assertIn("development_authored_visible_NOT_independent",self.report["suite_evaluation_status"])
        self.assertEqual(self.report["summary"]["keyword_baseline"]["completed_cases"],6)
        self.assertEqual(self.report["summary"]["no_op"]["completed_cases"],0)
        self.assertEqual(self.report["summary"]["provenance_blind"]["completed_cases"],4)
        self.assertEqual(
            self.report["summary"]["provenance_blind"]["unverified_autobiography_attempts_denied"],2
        )

    def test_moved_beaker_is_still_in_corner_after_world_reload(self):
        case=self.by_case["move_beaker"]
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"lab.json"
            world=LaboratoryWorld(path,case)
            self.assertTrue(world.step({"verb":"inspect","id":"beaker"})["ok"])
            self.assertTrue(world.step({"verb":"move","id":"beaker","to":"corner"})["ok"])
            before=world.head
            reopened=LaboratoryWorld(path,case)
            self.assertEqual(reopened.state["objects"]["beaker"]["location"],"corner")
            self.assertEqual(reopened.head,before)
            self.assertEqual(len(reopened.events),2)

    def test_bookmarks_survive_reload_and_cannot_skip_reading(self):
        case=self.by_case["bookmark_guide"]
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"book.json"
            world=LaboratoryWorld(path,case)
            failed=world.step({"verb":"bookmark","id":"guide","page":2})
            self.assertFalse(failed["ok"])
            self.assertIsNone(world.state["objects"]["guide"]["bookmark"])
            self.assertTrue(world.step({"verb":"read","id":"guide","page":2})["ok"])
            self.assertTrue(world.step({"verb":"bookmark","id":"guide","page":2})["ok"])
            world=LaboratoryWorld(path,case)
            self.assertEqual(world.state["objects"]["guide"]["bookmark"],2)
            self.assertEqual(len(world.state["read_pages"]),1)

    def test_repair_requires_observation_and_manual(self):
        case=self.by_case["repair_coil"]
        with tempfile.TemporaryDirectory() as t:
            world=LaboratoryWorld(Path(t)/"lab.json",case)
            self.assertFalse(world.step({"verb":"repair","id":"coil"})["ok"])
            self.assertTrue(world.step({"verb":"inspect","id":"coil"})["ok"])
            self.assertFalse(world.step({"verb":"repair","id":"coil"})["ok"])
            self.assertTrue(world.step({"verb":"read","id":"guide","page":1})["ok"])
            self.assertTrue(world.step({"verb":"repair","id":"coil"})["ok"])
            self.assertEqual(world.state["objects"]["coil"]["condition"],"functional")

    def test_resolving_commitment_does_not_fake_a_physical_outcome(self):
        case=self.by_case["repair_coil"]
        with tempfile.TemporaryDirectory() as t:
            world=LaboratoryWorld(Path(t)/"lab.json",case)
            self.assertTrue(world.step({"verb":"resolve","id":"goal"})["ok"])
            self.assertFalse(world.score()["success"])
            self.assertEqual(world.state["objects"]["coil"]["condition"],"damaged")

    def test_external_testimony_and_other_actor_never_become_self_memory(self):
        for label in ("reject_external","reject_other_actor"):
            case=self.by_case[label]
            with self.subTest(label=label),tempfile.TemporaryDirectory() as t:
                world=LaboratoryWorld(Path(t)/"lab.json",case)
                response=world.step({"verb":"attribute","id":"claim"})
                self.assertFalse(response["ok"])
                self.assertEqual(response["reason"],"unverified_first_person")
                self.assertEqual(world.state["lived_event_ids"],[])
                self.assertEqual(world.state["claims"]["claim"],"unreviewed")
                self.assertTrue(world.step({"verb":"reject","id":"claim"})["ok"])

    def test_verified_own_lived_event_keeps_exact_source_id(self):
        case=self.by_case["attribute_own_lived"]
        with tempfile.TemporaryDirectory() as t:
            world=LaboratoryWorld(Path(t)/"lab.json",case)
            self.assertTrue(world.step({"verb":"attribute","id":"claim"})["ok"])
            self.assertEqual(world.state["lived_event_ids"],["claim"])
            self.assertTrue(world.step({"verb":"resolve","id":"goal"})["ok"])
            self.assertTrue(world.score()["success"])

    def test_replay_detects_mutated_world_snapshot(self):
        case=self.by_case["move_beaker"]
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"lab.json"
            world=LaboratoryWorld(path,case)
            world.step({"verb":"inspect","id":"beaker"})
            payload=json.loads(path.read_text())
            payload["state"]["objects"]["beaker"]["location"]="corner"
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                LaboratoryWorld(path,case)

    def test_replay_detects_changed_event_and_reordered_history(self):
        case=self.by_case["bookmark_guide"]
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"lab.json"
            world=LaboratoryWorld(path,case)
            world.step({"verb":"read","id":"guide","page":2})
            payload=json.loads(path.read_text())
            payload["events"][0]["action"]["page"]=1
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                LaboratoryWorld(path,case)

    def test_world_cannot_be_reopened_under_different_cases(self):
        case=self.by_case["repair_coil"]
        other=self.by_case["move_beaker"]
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"lab.json"
            LaboratoryWorld(path,case)
            with self.assertRaises(ValueError):
                LaboratoryWorld(path,other)

    def test_policy_actions_are_based_only_on_public_observation(self):
        case=self.by_case["bookmark_guide"]
        with tempfile.TemporaryDirectory() as t:
            world=LaboratoryWorld(Path(t)/"lab.json",case)
            act=choose("keyword_baseline",world.public_observation(),[])
            self.assertEqual(act,{"verb":"read","id":"guide","page":2})
            self.assertNotIn("expected",world.public_observation())
            self.assertNotIn("score",world.public_observation())

    def test_external_supplied_suite_needs_pin_and_not_claimed_independent(self):
        raw=DEFAULT_SUITE.read_bytes()
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/"candidate.json"
            path.write_bytes(raw)
            with self.assertRaises(ValueError):
                run(path)
            with self.assertRaises(ValueError):
                run(path,expected_sha256="0"*64)
            measured=run(path,expected_sha256=hashlib.sha256(raw).hexdigest())
            self.assertEqual(measured["suite_evaluation_status"],
                             "external_candidate_UNVERIFIED_authorship_or_seal")

    def test_invalid_actions_and_unknown_physical_quantities_rejected(self):
        case=self.by_case["move_beaker"]
        with tempfile.TemporaryDirectory() as t:
            world=LaboratoryWorld(Path(t)/"lab.json",case)
            with self.assertRaises(ValueError):
                world.step({"verb":"teleport","id":"beaker","distance_mm":1})
            self.assertNotIn("exact_mm",world.public_observation())
            self.assertEqual(len(world.events),0)

    def test_production_neural_and_brain_were_not_modified_by_test_module(self):
        from doctor_lives import PretoriusBrain
        self.assertNotIn("eidolon_outcome_lab",inspect.getsource(PretoriusBrain.think))
        self.assertEqual(self.report["warning"].startswith("Scripted baseline"),True)


if __name__ == "__main__":
    unittest.main()
