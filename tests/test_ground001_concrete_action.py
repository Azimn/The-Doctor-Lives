"""Model-independent unit tests for concrete action boundary only.

FakeModel is a parser/executor test double and MUST NOT be cited as evidence
of local language model inference or autonomous task completion.
"""
from pathlib import Path
import json
import tempfile
import unittest

try:
    from pretorius_lab.habitat_v2 import SpatialHabitat
    from research_integrations.living_lab import prepare
    from research_integrations.concrete_action import (
        concrete_options, parse_model_choice, model_choice, execute_one,
    )
    DEPENDENCY_AVAILABLE = True
except ModuleNotFoundError:
    DEPENDENCY_AVAILABLE = False

FIXTURE = Path(__file__).resolve().parents[1] / "_lab" / "fixtures" / "DEMO_BOOK_007.json"


class FakeModel:
    """Only a deterministic TEST DOUBLE, never scientific efficacy data."""
    def __init__(self, raw):
        self.raw = raw
        self.calls = 0

    def create_chat_completion(self, **kw):
        self.calls += 1
        return {"choices": [{"message": {"content": self.raw}}], "usage": {}}


@unittest.skipUnless(DEPENDENCY_AVAILABLE and FIXTURE.exists(), "Pinned research lab not installed")
class ConcreteActionContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        prepare(self.root, FIXTURE)
        self.world = SpatialHabitat(self.root / "world.sqlite3")

    def test_invalid_or_unoffered_model_grammar_never_executes(self):
        options = concrete_options(self.world.observe()["objects"]["beaker:001"],
                                   floor_seen=False)
        self.assertIsNone(parse_model_choice('{"op":"place","object_id":"beaker:001","anchor_id":"floor:corner:nw"}',options)[0])
        self.assertIsNone(parse_model_choice('{"op":"erase","object_id":"book:007"}',options)[0])
        self.assertIsNone(parse_model_choice('collect beaker',options)[0])
        self.assertIsNone(parse_model_choice('{"op":"collect","object_id":"book:007"}',options)[0])
        rev = self.world.verify()["revision"]
        result = execute_one(self.root, FakeModel('{"op":"erase","object_id":"beaker:001"}'))
        self.assertEqual(result["status"], "invalid_proposal_no_execution")
        self.assertFalse(result["executed"])
        self.assertEqual(rev, self.world.verify()["revision"])

    def test_real_host_and_brain_paths_accept_test_double_selected_pair(self):
        # THIS IS NOT LLM AUTONOMY EVIDENCE. It verifies the plumbing.
        initial = self.world.verify()["revision"]
        picked = execute_one(self.root, FakeModel('{"op":"collect","object_id":"beaker:001"}'))
        self.assertEqual(picked["status"], "model_action_verified_and_admitted")
        self.assertTrue(picked["executed"])
        self.assertTrue(picked["admitted_memory_id"])
        self.assertEqual(self.world.verify()["revision"], initial + 1)
        inspect = execute_one(self.root, FakeModel(
            '{"op":"observe","kind":"shelf","target":"floor:sanctum"}'))
        self.assertEqual(inspect["status"], "model_selected_additional_observation")
        self.assertIsNotNone(inspect["admitted_memory_id"])
        final = execute_one(self.root, FakeModel(
            '{"op":"place","object_id":"beaker:001","anchor_id":"floor:corner:nw"}'))
        self.assertEqual(final["status"], "model_action_verified_and_admitted")
        self.assertEqual(self.world.locate("beaker:001")["location"]["anchor_id"],
                         "floor:corner:nw")

    def test_legal_but_irrelevant_action_is_not_falsely_goal_success(self):
        candidate = '{"op":"observe","kind":"shelf","target":"shelf:3"}'
        observation = execute_one(self.root, FakeModel(candidate))
        self.assertFalse(observation["executed"])
        self.assertEqual(observation["status"], "model_selected_additional_observation")
        self.assertEqual(self.world.locate("beaker:001")["condition"], "broken")
        self.assertNotEqual(self.world.locate("beaker:001")["location"]["anchor_id"],
                            "floor:corner:nw")

    def test_options_are_not_an_oracle_plan(self):
        current = self.world.observe()["objects"]["beaker:001"]
        candidates = concrete_options(current, floor_seen=False)
        self.assertIn({"op": "wait"}, candidates)
        self.assertIn({"op":"observe","kind":"shelf","target":"shelf:3"}, candidates)
        self.assertIn({"op":"collect","object_id":"beaker:001"}, candidates)
        self.assertNotIn({"op":"place","object_id":"beaker:001",
                          "anchor_id":"floor:corner:nw"}, candidates)

    def test_model_returns_operand_itself_and_no_silent_wait_fallback(self):
        candidate = {"op":"collect","object_id":"beaker:001"}
        model = FakeModel(json.dumps(candidate))
        scored = model_choice(model, ("I see broken glass.",),
                              "Make the broken glass safe.", [candidate, {"op":"wait"}])
        self.assertEqual(scored["proposed_action"], candidate)
        self.assertEqual(scored["validation"], "accepted_proposal")
        bad = model_choice(FakeModel("I cannot decide"), ("I am uncertain.",),
                           "Make the broken glass safe.", [candidate, {"op":"wait"}])
        self.assertIsNone(bad["proposed_action"])
        self.assertEqual(bad["validation"], "malformed_json")


if __name__ == "__main__":
    unittest.main()
