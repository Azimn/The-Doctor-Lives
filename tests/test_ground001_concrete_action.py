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
    from pretorius_lab.observation_receipts import ObservationPort
    from doctor_lives.cognition import PretoriusBrain
    from research_integrations.living_lab import prepare, _verified_subject_frame
    from tools.run_ground001_real_model import (
        repeated_no_progress, goal_finished, SPECIFIC_GOAL, VAGUE_GOAL,
    )
    from research_integrations.concrete_action import (
        concrete_options, parse_model_choice, model_choice, execute_one, _choice, action_token,
        currently_admitted_fixture_observations, action_grammar,
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
        self.assertIsNone(parse_model_choice('{"verb":"place","operand":"beaker:001","destination":"floor:corner:nw"}',options)[0])
        self.assertIsNone(parse_model_choice('{"verb":"erase","operand":"book:007","destination":"none"}',options)[0])
        self.assertIsNone(parse_model_choice('collect beaker',options)[0])
        self.assertIsNone(parse_model_choice('{"verb":"collect","operand":"book:007","destination":"none"}',options)[0])
        rev = self.world.verify()["revision"]
        result = execute_one(self.root, FakeModel('{"verb":"erase","operand":"beaker:001","destination":"none"}'))
        self.assertEqual(result["status"], "invalid_proposal_no_execution")
        self.assertFalse(result["executed"])
        self.assertEqual(rev, self.world.verify()["revision"])

    def test_real_host_and_brain_paths_accept_test_double_selected_pair(self):
        # THIS IS NOT LLM AUTONOMY EVIDENCE. It verifies the plumbing.
        initial = self.world.verify()["revision"]
        picked = execute_one(self.root, FakeModel('COLLECT|beaker:001'))
        self.assertEqual(picked["status"], "model_action_verified_and_admitted")
        self.assertTrue(picked["executed"])
        self.assertTrue(picked["admitted_memory_id"])
        self.assertEqual(self.world.verify()["revision"], initial + 1)
        inspect = execute_one(self.root, FakeModel('OBSERVE|floor:sanctum'))
        self.assertEqual(inspect["status"], "model_selected_additional_observation")
        self.assertTrue(any("I collected the broken beaker" in line
                            for line in inspect["subject_frame"]),
                        "Source-admitted collection memory must be retrieved after restart")
        self.assertIsNotNone(inspect["admitted_memory_id"])
        brain = PretoriusBrain(self.root / "brain")
        frame_masked = _verified_subject_frame(
            brain, ObservationPort(self.world),
            current_percept="I see gathered fragments of the broken laboratory beaker.",
            withhold_lab_autobiography=True,
        )
        self.assertFalse(any("I collected the broken beaker" in line
                             for line in frame_masked.renderer_context()),
                         "Counterfactual masked subject frame must exclude lab autobiography")
        final = execute_one(self.root, FakeModel('PLACE|beaker:001|floor:corner:nw'))
        self.assertEqual(final["status"], "model_action_verified_and_admitted")
        self.assertEqual(self.world.locate("beaker:001")["location"]["anchor_id"],
                         "floor:corner:nw")

    def test_legal_but_irrelevant_action_is_not_falsely_goal_success(self):
        candidate = 'OBSERVE|shelf:3'
        observation = execute_one(self.root, FakeModel(candidate))
        self.assertFalse(observation["executed"])
        self.assertEqual(observation["status"], "model_selected_additional_observation")
        self.assertEqual(self.world.locate("beaker:001")["condition"], "broken")
        self.assertNotEqual(self.world.locate("beaker:001")["location"]["anchor_id"],
                            "floor:corner:nw")

    def test_same_world_subject_inspection_is_not_reoffered(self):
        port = ObservationPort(self.world)
        self.assertEqual(currently_admitted_fixture_observations(
            PretoriusBrain(self.root / "brain"), port), {})
        first = execute_one(self.root, FakeModel("OBSERVE|floor:sanctum"))
        self.assertEqual(first["status"], "model_selected_additional_observation")
        brain = PretoriusBrain(self.root / "brain")
        admitted = currently_admitted_fixture_observations(brain, port)
        self.assertIn("floor:sanctum", admitted)
        options = concrete_options(self.world.observe()["objects"]["beaker:001"],
                                   floor_seen=True,
                                   fresh_observed=frozenset(admitted))
        self.assertNotIn(_choice("observe", "floor:sanctum"), options)
        self.assertIn(_choice("collect", "beaker:001"), options)
        again = execute_one(self.root, FakeModel("OBSERVE|floor:sanctum"))
        self.assertEqual(again["status"], "invalid_proposal_no_execution")
        self.assertFalse(again["executed"])

    def test_external_world_mutation_makes_previous_inspection_stale(self):
        execute_one(self.root, FakeModel("OBSERVE|floor:sanctum"))
        before = PretoriusBrain(self.root / "brain")
        self.assertIn("floor:sanctum",
                      currently_admitted_fixture_observations(
                          before, ObservationPort(self.world)))
        self.world.commit({"op": "collect", "object_id": "beaker:001"},
                          actor="local_operator")
        current = PretoriusBrain(self.root / "brain")
        self.assertNotIn("floor:sanctum",
                         currently_admitted_fixture_observations(
                             current, ObservationPort(self.world)))
        options = concrete_options(self.world.observe()["objects"]["beaker:001"],
                                   floor_seen=False,
                                   fresh_observed=frozenset())
        self.assertIn(_choice("observe", "floor:sanctum"), options)
        self.assertNotIn(_choice("place", "beaker:001", "floor:corner:nw"),
                         options)

    def test_engineer_only_scan_cannot_mark_subject_as_observed(self):
        self.world.scan("floor:sanctum")
        self.assertEqual(currently_admitted_fixture_observations(
            PretoriusBrain(self.root / "brain"), ObservationPort(self.world)), {})

    def test_options_are_not_an_oracle_plan(self):
        current = self.world.observe()["objects"]["beaker:001"]
        candidates = concrete_options(current, floor_seen=False)
        self.assertIn(_choice("wait"), candidates)
        self.assertIn(_choice("observe","shelf:3"), candidates)
        self.assertIn(_choice("collect","beaker:001"), candidates)
        self.assertNotIn(_choice("place","beaker:001","floor:corner:nw"), candidates)

    def test_goal_scoring_requires_removal_not_collection_alone(self):
        self.assertFalse(goal_finished(self.world))
        self.assertNotIn("floor:corner:nw", SPECIFIC_GOAL)
        self.assertNotIn("COLLECT|beaker:001", SPECIFIC_GOAL)
        self.assertNotEqual(SPECIFIC_GOAL, VAGUE_GOAL)
        gathered = execute_one(self.root, FakeModel("COLLECT|beaker:001"))
        self.assertTrue(gathered["executed"])
        self.assertFalse(goal_finished(self.world),
                         "Gathered fragments still on the bench cannot satisfy clearance")
        execute_one(self.root, FakeModel("OBSERVE|floor:sanctum"))
        moved = execute_one(self.root, FakeModel("PLACE|beaker:001|floor:corner:nw"))
        self.assertTrue(moved["executed"])
        self.assertTrue(goal_finished(self.world))

    def test_stagnation_watchdog_stops_only_identical_nonmutating_inspections(self):
        prior = {
            "status": "model_selected_additional_observation",
            "proposed_action": _choice("observe", "floor:sanctum"),
            "world_after": {"state_digest": "same-state"},
        }
        again = dict(prior)
        self.assertTrue(repeated_no_progress(prior, again))
        self.assertFalse(repeated_no_progress(prior, dict(
            again, proposed_action=_choice("collect", "beaker:001"))))
        self.assertFalse(repeated_no_progress(prior, dict(
            again, world_after={"state_digest": "changed-state"})))


    def test_host_effects_are_presentation_only_not_action_authority(self):
        options = [_choice("wait"), _choice("collect", "beaker:001"),
                   _choice("observe", "floor:sanctum")]
        model = FakeModel("COLLECT|beaker:001")
        bare = model_choice(model, ("I see broken glass.",),
                            "Make the broken glass safe.", options,
                            information_arm="names")
        explained = model_choice(model, ("I see broken glass.",),
                                 "Make the broken glass safe.", options,
                                 information_arm="effects")
        self.assertEqual(bare["offered_action_tokens"], explained["offered_action_tokens"])
        self.assertEqual(bare["proposed_action"], explained["proposed_action"])
        self.assertNotEqual(bare["prompt_sha256"], explained["prompt_sha256"])


    def test_grammar_only_allows_complete_offered_semantic_tokens(self):
        options = [_choice("wait"), _choice("observe", "floor:sanctum"),
                   _choice("collect", "beaker:001")]
        grammar = action_grammar(options)
        self.assertEqual(
            grammar,
            'root ::= "WAIT" | "OBSERVE|floor:sanctum" | "COLLECT|beaker:001"' + chr(10),
        )
        self.assertNotIn("PLACE|", grammar)
        with self.assertRaises(ValueError):
            action_grammar([_choice("wait"), _choice("wait")])
        with self.assertRaises(ValueError):
            action_grammar([])

    def test_model_returns_operand_itself_and_no_silent_wait_fallback(self):
        candidate = _choice("collect","beaker:001")
        model = FakeModel(action_token(candidate))
        scored = model_choice(model, ("I see broken glass.",),
                              "Make the broken glass safe.", [candidate, _choice("wait")])
        self.assertEqual(scored["proposed_action"], candidate)
        self.assertEqual(scored["validation"], "accepted_proposal")
        bad = model_choice(FakeModel("I cannot decide"), ("I am uncertain.",),
                           "Make the broken glass safe.", [candidate, _choice("wait")])
        self.assertIsNone(bad["proposed_action"])
        self.assertEqual(bad["validation"], "not_an_offered_action_and_operand")
        self.assertIsNone(parse_model_choice("COLLECT|book:007",
                          [candidate, _choice("wait")])[0])
        self.assertIsNone(parse_model_choice("PLACE|beaker:001|floor:corner:nw",
                          [candidate, _choice("wait")])[0])
        self.assertEqual(parse_model_choice('"COLLECT|beaker:001"',
                         [candidate, _choice("wait")])[0], candidate)
        self.assertEqual(action_token(_choice("observe", "floor:sanctum")),
                         "OBSERVE|floor:sanctum")



if __name__ == "__main__":
    unittest.main()
