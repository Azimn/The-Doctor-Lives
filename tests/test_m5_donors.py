"""Adapted original donor assertions without importing their extra state stores."""
import importlib.util
import unittest
from types import SimpleNamespace
from doctor_lives.m5_donors import DONORS,CAP_PER_FAMILY,contributions

class M5DonorSourceContracts(unittest.TestCase):
    def test_unknown_second_planner_never_registered(self):
        self.assertEqual(DONORS,("cascade_commitments","household_grounded","household_habit"))
        self.assertLessEqual(CAP_PER_FAMILY,0.03)
        with self.assertRaises(ValueError):
            contributions(None,None,{}, {},1, enabled=("an_unreviewed_planner",))


    def test_cascade_contract_reads_existing_canonical_commitments_only(self):
        class SourceBrainStore:
            def open_commitments(self):
                return [{"description":"Continue the laboratory research"}]
        bridge=SimpleNamespace(doctor=SimpleNamespace(
            brain=SimpleNamespace(store=SourceBrainStore())))
        out=contributions(bridge,None,{"text":"I should continue the laboratory research"},
                          {"affordance_key":"document_read","goal_type":"study"},
                          2,enabled=("cascade_commitments",))
        self.assertEqual(out["cascade_commitments"],CAP_PER_FAMILY)
        self.assertEqual(out["household_habit"],0.0)

    @unittest.skipUnless(importlib.util.find_spec("pretorius_lab") is not None,
                         "Source-pinned actual Laboratory required")
    def test_grounded_donor_original_physics_survives_depleted_provisions(self):
        # Adapted from tests/test_home_grounded_actions.py on the original
        # household branch. Do NOT adopt the original host controller.
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm,transition
        from doctor_lives.m5_home_feasibility import physically_available
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as temp:
            world=SpatialHabitat.create(Path(temp)/"physical.sqlite3")
            HomeLife(world).initialize()
            rhythm=DailyRhythm(world)
            rhythm.initialize()
            state=rhythm.audit_state()
            available=physically_available(state,"station:kitchen")
            self.assertIn("tea",available["available"])
            for _ in range(3):
                state,_=transition(state,"brew_tea",{},"station:kitchen")
            after=physically_available(state,"station:kitchen")
            self.assertNotIn("tea",after["available"])
            self.assertIn("tea",after["rejected"])
            self.assertTrue(after["available"])
            self.assertEqual(rhythm.audit_state(),available and rhythm.audit_state())

    def test_donors_disabled_by_default_no_extra_policy(self):
        self.assertEqual(contributions(None,None,{}, {},1),{n:0.0 for n in DONORS})

if __name__=="__main__":
    unittest.main()
