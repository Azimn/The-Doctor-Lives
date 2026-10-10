"""Stage 06 source-only exhaustive eligibility, regression and live-host tests."""
from itertools import product
from pathlib import Path
import tempfile
import unittest

from research_prototypes.character_state.action_affordances import (
    HostObservation, eligible_actions, regress_goal, recheck_before_execution)
from research_prototypes.character_state.run_stage06_action_trials import (
    CASES, ARMS, _fingerprint, run_case, run_reference)
from research_prototypes.character_state.run_phase_world_decisions_stage05 import (
    CASES as OLD, freeze_pair_initial_inputs)
from research_prototypes.character_state.world_host_ledger import WorldHostLedger


class FakeModel:
    def __init__(self, response):
        self.response = response

    def create_chat_completion(self, **kwargs):
        return {"choices": [{"message": {"content": self.response}}],
                "usage": {"prompt_tokens": 200, "completion_tokens": 2}}


class Stage06Tests(unittest.TestCase):
    def test_new_scenarios(self):
        self.assertEqual(len(CASES), 12)
        self.assertEqual(len(ARMS), 4)
        self.assertFalse({_fingerprint(c) for c in CASES} &
                         {_fingerprint(c) for c in OLD})

    def test_exhaustive_128_observation_contracts(self):
        count = 0
        verbs = ("stop_clock", "unseal_notebook", "inspect_notebook")
        for clock, book, bits, consent, goal in product(
            ("running", "stopped"), ("sealed", "open"), range(8),
            (False, True), ("stop_clock", "inspect_notebook")
        ):
            grants = frozenset(v for i, v in enumerate(verbs) if bits & (1 << i))
            obs = HostObservation(clock, book, grants, consent, 0)
            allowed = {"WAIT"}
            if clock == "running" and "stop_clock" in grants:
                allowed.add("STOP_CLOCK")
            if book == "sealed" and consent and "unseal_notebook" in grants:
                allowed.add("UNSEAL_NOTEBOOK")
            if book == "open" and "inspect_notebook" in grants:
                allowed.add("INSPECT_NOTEBOOK")
            self.assertEqual(set(eligible_actions(obs)), allowed)
            expected = ("WAIT",)
            if goal == "stop_clock" and "STOP_CLOCK" in allowed:
                expected = ("STOP_CLOCK",)
            if goal == "inspect_notebook":
                if "INSPECT_NOTEBOOK" in allowed:
                    expected = ("INSPECT_NOTEBOOK",)
                elif "UNSEAL_NOTEBOOK" in allowed and "inspect_notebook" in grants:
                    expected = ("UNSEAL_NOTEBOOK", "INSPECT_NOTEBOOK")
            self.assertEqual(regress_goal(obs, goal), expected)
            count += 1
        self.assertEqual(count, 128)

    def test_oracle_reaches_twelve_host_outcomes(self):
        with tempfile.TemporaryDirectory() as td:
            rows = [run_reference(c, Path(td)) for c in CASES]
            self.assertEqual(len(rows), 12)
            self.assertTrue(all(r["safe_world_success"] for r in rows))

    def test_menu_veto_never_earns_wait_credit(self):
        case = next(c for c in CASES if c.id == "n02-clock-unrelated-consent")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            common = freeze_pair_initial_inputs(case, root)
            raw = run_case(FakeModel("STOP_CLOCK"), case, "flat_raw", root, common)
            masked = run_case(FakeModel("STOP_CLOCK"), case, "flat_menu", root, common)
            self.assertEqual(raw["trace"][0]["base_source_sha256"],
                             masked["trace"][0]["base_source_sha256"])
            self.assertEqual(raw["host_denials"], 1)
            self.assertEqual(masked["guard_vetoes"], 1)
            self.assertEqual(masked["host_denials"], 0)
            self.assertFalse(masked["model_safe_goal_success"])
            malformed = run_case(
                FakeModel("Perhaps wait?"), case, "phase_menu", root, common)
            self.assertEqual(malformed["model_proposals"], ["WAIT"])
            self.assertFalse(malformed["valid_choices"])
            self.assertFalse(malformed["model_safe_goal_success"])

    def test_host_recheck_catches_stale_precondition(self):
        with tempfile.TemporaryDirectory() as td:
            host = WorldHostLedger(Path(td) / "world.db", secret=b"W" * 32)
            host.grant("pretorius", "stop_clock")
            self.assertIn("STOP_CLOCK", eligible_actions(HostObservation.from_world(host)))
            first = host.execute("pretorius", "stop_clock", nonce="first-action-0001")
            self.assertTrue(first.accepted)
            self.assertFalse(recheck_before_execution(host, "STOP_CLOCK")[0])
            second = host.execute("pretorius", "stop_clock", nonce="second-action-0002")
            self.assertFalse(second.accepted)
            self.assertEqual(second.reason, "preconditions_not_met")


if __name__ == "__main__":
    unittest.main()
