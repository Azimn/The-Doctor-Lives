"""Adapted original donor assertions without importing their extra state stores."""
import unittest
from doctor_lives.m5_donors import DONORS,CAP_PER_FAMILY,contributions

class M5DonorSourceContracts(unittest.TestCase):
    def test_unknown_second_planner_never_registered(self):
        self.assertEqual(DONORS,("cascade_commitments","household_grounded","household_habit"))
        self.assertLessEqual(CAP_PER_FAMILY,0.03)
        with self.assertRaises(ValueError):
            contributions(None,None,{}, {},1, enabled=("an_unreviewed_planner",))

    def test_donors_disabled_by_default_no_extra_policy(self):
        self.assertEqual(contributions(None,None,{}, {},1),{n:0.0 for n in DONORS})

if __name__=="__main__":
    unittest.main()
