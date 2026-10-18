"""Grounded operator: physical preflight, stale-source denial, real world controls."""
import importlib.util
import tempfile
from pathlib import Path
import unittest

from doctor_lives.home_grounded_actions import (
    ARMS, TASKS, choose, execute, physically_available,
)
from doctor_lives.home_grounded_screen import CASES, SEEDS, OFFERS, run_grounded_screen

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


class FrozenGroundedPlanTests(unittest.TestCase):
    def test_comparison_and_task_set_frozen_before_experiment(self):
        self.assertEqual(ARMS, (
            "legacy_mapped", "grounded_doctor", "grounded_simple"))
        self.assertEqual(CASES, (
            "ordinary_home", "empty_tea", "worn_workbench", "evening_dark"))
        self.assertEqual(SEEDS, (1842, 2718, 31415))
        self.assertEqual(OFFERS, 6)
        self.assertEqual(set(TASKS), {
            "experiment", "repair", "rest", "tea", "meal", "clean"})

    def test_reject_arbitrary_experimental_subjects_and_actions(self):
        with self.assertRaises(ValueError):
            run_grounded_screen(cases=("invented",))
        with self.assertRaises(ValueError):
            run_grounded_screen(seeds=(8888,))
        with self.assertRaises(ValueError):
            run_grounded_screen(arms=("superhuman",))


@unittest.skipUnless(HAS_LAB, "Requires pinned original physical Laboratory")
class RealLaboratoryGroundingTests(unittest.TestCase):
    def _home(self, path):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from doctor_lives.home_native_practice import _agent, _act
        world = SpatialHabitat.create(path / "lab.sqlite3")
        HomeLife(world).initialize()
        DailyRhythm(world).initialize()
        bridge, _ = _agent(path, 1842)
        _act(bridge, "walk", "visit-hall", station="station:hall")
        _act(bridge, "walk", "visit-kitchen", station="station:kitchen")
        return bridge

    def test_whole_action_validation_checks_physics_and_finite_goods(self):
        from doctor_lives.home_native_practice import _act
        with tempfile.TemporaryDirectory() as folder:
            bridge = self._home(Path(folder))
            original = bridge.subject.rhythm.audit_state()
            offered = physically_available(original, "station:kitchen")
            self.assertIn("tea", offered["available"])
            self.assertIn("meal", offered["available"])
            for n in range(3):
                _act(bridge, "brew_tea", f"consumed-tea-{n}")
            after = bridge.subject.rhythm.audit_state()
            self.assertEqual(after["supplies"]["tea"], 0)
            listed = physically_available(after, "station:kitchen")
            self.assertNotIn("tea", listed["available"])
            self.assertIn("tea", listed["rejected"])
            self.assertTrue(listed["available"])
            self.assertEqual(after, bridge.subject.rhythm.audit_state())
            self.assertTrue(bridge.subject.verify()["verified"])

    def test_grounded_decision_will_not_apply_to_a_changed_world(self):
        from doctor_lives.home_native_practice import _act
        with tempfile.TemporaryDirectory() as folder:
            bridge = self._home(Path(folder))
            pick = choose(bridge, arm="grounded_doctor")
            self.assertIn(pick["selected_task"], pick["available_tasks"])
            _act(bridge, "advance", "external-interruption", minutes=10)
            after = bridge.subject.rhythm.audit_state()
            with self.assertRaises(RuntimeError):
                execute(bridge, pick, prefix="stale")
            self.assertEqual(after, bridge.subject.rhythm.audit_state())
            self.assertTrue(bridge.subject.verify()["verified"])

    def test_depleted_tea_three_matched_arms_without_fake_replenishment(self):
        report = run_grounded_screen(
            cases=("empty_tea",), seeds=(1842,), arms=ARMS)
        self.assertEqual(len(report["trials"]), 3)
        self.assertTrue(report["checks"]["all_worlds_replay"])
        self.assertTrue(report["checks"]["matched_source_conditions"])
        self.assertTrue(report["checks"]["no_grounded_tea_when_unavailable"])
        self.assertTrue(report["checks"]["all_grounded_attempts_preflight_legal"])
        for trial in report["trials"]:
            self.assertEqual(len(trial["attempts"]), OFFERS)
            self.assertGreater(trial["doctor_lived_observation_count"], 0)
            self.assertTrue(all(a["world_verified"] for a in trial["attempts"]))


if __name__ == "__main__":
    unittest.main()
