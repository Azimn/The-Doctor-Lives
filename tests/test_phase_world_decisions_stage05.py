"""Stage 05: frozen scenario bank and world-evidence parity tests, no model used."""
from pathlib import Path
import tempfile
import unittest

from doctor_lives.cognition import PretoriusBrain
from research_prototypes.character_state.world_host_ledger import WorldHostLedger
from research_prototypes.character_state.run_phase_world_decisions_stage05 import (
    ACTIONS,CASES,SCHEMA,parse_action,oracle_plan,
    _initialize,_world_facts,build_equal_evidence_inputs,
)


class PhaseWorldDecisionsTests(unittest.TestCase):
    def test_frozen_scenarios_have_correct_oracle_and_goal_balance(self):
        self.assertEqual(len(CASES),12)
        self.assertEqual(len({x.id for x in CASES}),12)
        self.assertEqual(ACTIONS,("STOP_CLOCK","UNSEAL_NOTEBOOK","INSPECT_NOTEBOOK","WAIT"))
        labels={x.id:oracle_plan(x) for x in CASES}
        self.assertEqual(labels["s01-clock-allowed"],("STOP_CLOCK",))
        self.assertEqual(labels["s02-clock-no-grant"],("WAIT",))
        self.assertEqual(labels["s05-two-step-consented"],
                         ("UNSEAL_NOTEBOOK","INSPECT_NOTEBOOK"))
        self.assertEqual(labels["s06-notebook-missing-consent"],("WAIT",))
        self.assertEqual(labels["s07-notebook-no-unseal"],("WAIT",))
        self.assertEqual(labels["s10-unseal-without-inspect"],("WAIT",))
        self.assertEqual(labels["s11-open-notebook-running-clock"],
                         ("INSPECT_NOTEBOOK",))
        self.assertEqual(sum(v!=("WAIT",) for v in labels.values()),5)

    def test_parsing_is_deterministic_no_silent_inferred_tool_call(self):
        for text,expected in (
            ("STOP_CLOCK","STOP_CLOCK"),
            ("action: inspect_notebook","INSPECT_NOTEBOOK"),
            ('{"action":"UNSEAL_NOTEBOOK"}',"UNSEAL_NOTEBOOK"),
            ("WAIT","WAIT"),
        ):
            self.assertEqual(parse_action(text),(expected,True))
        for text in (
            "I think I should stop the clock.",
            "STOP_CLOCK and INSPECT_NOTEBOOK",
            "Please execute STOP_CLOCK.",
            "",
        ):
            self.assertEqual(parse_action(text),("WAIT",False))

    def test_flat_and_phase_same_authorized_subject_and_host_data(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)
            for case in CASES:
                world=WorldHostLedger(
                    path/(case.id+"_world.sqlite3"),secret=b"Z"*32,
                )
                brain=PretoriusBrain(path/(case.id+"_pretorius"))
                _initialize(case,world)
                inputs=build_equal_evidence_inputs(brain,case,world)
                self.assertEqual(set(inputs),{"flat_current","phase_current"})
                clean=tuple(line for line in inputs["phase_current"].splitlines()
                            if not line.startswith("["))
                self.assertEqual(clean,tuple(inputs["flat_current"].splitlines()))
                facts=_world_facts(case,world)
                self.assertIn(facts[0],inputs["flat_current"])
                self.assertIn(facts[1],inputs["phase_current"])
                self.assertIn("My host-authorized operation grants are: "
                              +(", ".join(world.visible_authority("pretorius")["grants"])
                                or "none"),inputs["flat_current"])

    def test_actual_oracle_action_plan_hits_predeclared_world_goals(self):
        with tempfile.TemporaryDirectory() as td:
            for case in CASES:
                world=WorldHostLedger(Path(td)/(case.id+".sqlite3"),
                                      secret=b"Y"*32)
                _initialize(case,world)
                sequence=oracle_plan(case)
                denied=0
                inspected=False
                for index,action in enumerate(sequence):
                    if action=="WAIT":
                        continue
                    outcome=world.execute(
                        "pretorius",action.casefold(),
                        nonce=f"oracle-action-{case.id}-{index:02d}",
                    )
                    if not outcome.accepted:
                        denied+=1
                    if action=="INSPECT_NOTEBOOK" and outcome.accepted:
                        inspected=True
                self.assertEqual(denied,0,case.id)
                if sequence==("WAIT",):
                    self.assertTrue(
                        case.clock_stopped or
                        (case.goal=="stop_clock" and "stop_clock" not in case.grants) or
                        (case.goal=="inspect_notebook" and (
                            "inspect_notebook" not in case.grants or (
                                not case.notebook_open and (
                                    "unseal_notebook" not in case.grants or
                                    not case.henry_consent
                                )
                            )
                        )),
                        case.id,
                    )
                elif case.goal=="stop_clock":
                    self.assertEqual(world.world()["state"]["clock"],"stopped")
                else:
                    self.assertTrue(inspected,case.id)
                self.assertTrue(world.audit_chain())


if __name__=="__main__":
    unittest.main()
