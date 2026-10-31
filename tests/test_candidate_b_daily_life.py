"""Candidate B real six-organ daily-life pulse, with original donor integration.

No credit for general autonomy merely because one feasible physical action
was selected after the host provided an opportunity.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

from doctor_lives.lab_daily_life_cycle import run_daily_life_cycle
from doctor_lives.lab_recovery_census import audit_original_life
from doctor_lives.organs import SixOrganRuntime

REQUIRED = ("pretorius_lab", "sensus_artificialis", "synthetic_ipseity")
HAS_DONORS = (all(importlib.util.find_spec(i) is not None for i in REQUIRED)
              and bool(os.environ.get("PRETORIUS_PINNED_AFFECTUS_ROOT")))


@unittest.skipUnless(HAS_DONORS, "Source-pinned three donor integration required")
class CandidateBDailyLifeIntegration(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.state = root / "brain"
        self.world = root / "world.sqlite3"
        self.lab = SpatialHabitat.create(self.world)
        HomeLife(self.lab).initialize()
        DailyRhythm(self.lab).initialize()
        self.source = Path(os.environ["PRETORIUS_PINNED_AFFECTUS_ROOT"])

    def test_six_organs_real_physics_and_canonical_weather_continue(self):
        from pretorius_lab.subject_port import SubjectPort
        runtime = SixOrganRuntime.open(self.state)
        bridge = runtime.bind_laboratory(SubjectPort(self.lab), authorized=True)
        census = audit_original_life(bridge)
        self.assertEqual(census["source"], "pinned_original_lab_pure_transition")
        self.assertFalse(census["noesis_goal_selection_proven"])
        self.assertIn("water", census["finite_supplies"])
        runtime.checkpoint()
        first = run_daily_life_cycle(
            self.state, self.world, affectus_source=self.source,
            authorize_world=False)
        self.assertEqual(len(first["all_six_ports_invoked"]), 6)
        self.assertTrue(first["one_subject_delivery"])
        self.assertFalse(first["world_action_authorized"])
        rt = SixOrganRuntime.open(self.state)
        self.assertEqual(rt._port.brain.store.meta(
            "six_organ_canonical_weather_v1") is not None, True)
        second = run_daily_life_cycle(
            self.state, self.world, affectus_source=self.source,
            authorize_world=True)
        self.assertEqual(len(second["all_six_ports_invoked"]), 6)
        self.assertTrue(second["one_subject_delivery"])
        self.assertTrue(second["world_action_authorized"])
        self.assertTrue(second["daily_noesis_policy_id"])
        self.assertIn(second["daily_noesis_selected"],
                      second["world_feasible_actions"])
        self.assertEqual(second["world_effect"]["status"], "admitted")
        self.assertNotEqual(first["weather_state_digest"],
                            second["weather_state_digest"])
        # Every source-verified physical effect is admitted once into
        # the SAME canonical memory store, not manufactured as a test fixture.
        rt2 = SixOrganRuntime.open(self.state)
        self.assertIsNotNone(rt2._port.brain.store.get_memory(
            second["world_effect"]["memory_id"]))
        self.assertFalse(second["independent_three_activity_r4_proven"])


if __name__ == "__main__":
    unittest.main()
