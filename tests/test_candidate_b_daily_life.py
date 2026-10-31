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


    def _reserve_crash_window(self):
        """Inject the exact durable motor reservation without a host action."""
        import json
        from pretorius_lab.subject_port import SubjectPort
        from doctor_lives.noesis_day import offer_daily_opportunity
        runtime = SixOrganRuntime.open(self.state)
        bridge = runtime.bind_laboratory(SubjectPort(self.lab), authorized=True)
        choice = offer_daily_opportunity(
            bridge, author_goal=False, use_consequences=False)
        event_id = "candidate_b_fault_" + choice.policy_id[-16:]
        store = runtime._port.brain.store
        with store.transaction() as db:
            row = db.execute(
                "SELECT state_pressure_json FROM policy_decisions WHERE id=?",
                (choice.policy_id,)
            ).fetchone()
            evidence = json.loads(row["state_pressure_json"])
            self.assertEqual(evidence["selector_authority"], "original_noesis")
            evidence["motor_authorization"] = "authorized"
            evidence["motor_event_id"] = event_id
            db.execute(
                "UPDATE policy_decisions SET state_pressure_json=? WHERE id=?",
                (json.dumps(evidence, sort_keys=True), choice.policy_id)
            )
            store.bump_state_version(db)
        runtime.checkpoint()
        return bridge, choice, event_id

    def _verify_one_replayed_world_action(self, bridge, choice, event_id):
        from doctor_lives.lab_home_bridge import _ACTION_DOMAINS
        from doctor_lives.noesis_day import reconcile_pending_daily_action
        replay = reconcile_pending_daily_action(bridge)
        self.assertEqual(len(replay), 1)
        self.assertEqual(replay[0]["policy_decision_id"], choice.policy_id)
        self.assertEqual(replay[0]["action"], choice.action)
        self.assertFalse(replay[0]["new_goal_selected"])
        self.assertEqual(reconcile_pending_daily_action(bridge), ())
        memory_id = replay[0]["memory_id"]
        store = bridge.doctor.brain.store
        memory = store.get_memory(memory_id)
        self.assertIsNotNone(memory)
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        self.assertTrue(memory["source"].startswith("laboratory-home:action:"))
        self.assertEqual(
            len([m for m in store.memories(False) if m["source"] == memory["source"]]),
            1
        )
        with bridge.world._open() as db:
            count = db.execute(
                "SELECT count(*) FROM " + _ACTION_DOMAINS[choice.action]
                + " WHERE event_id=?", (event_id,)
            ).fetchone()[0]
        self.assertEqual(count, 1)
        return replay[0]


    def test_pending_daily_motor_requires_permission_and_preempts_new_action(self):
        """A restart may reconcile ONE original motor, never silently do TWO.

        No-permission cycles still exercise six organs, but cannot execute a
        reserved action. An authorized cold cycle replays its original receipt
        and lived memory without selecting another physical daily motor.
        """
        from doctor_lives.lab_home_bridge import _ACTION_DOMAINS
        from doctor_lives.noesis_day import reconcile_pending_daily_action
        bridge, choice, event_id = self._reserve_crash_window()
        with self.lab._open() as db:
            original_moves = db.execute(
                "SELECT count(*) FROM embodied_events WHERE "
                "json_extract(envelope, '$.kind')='move'"
            ).fetchone()[0]
        denied = run_daily_life_cycle(
            self.state, self.world, affectus_source=self.source,
            authorize_world=False)
        self.assertEqual(denied["pending_prior_noesis_actions"],
                         [choice.policy_id])
        self.assertTrue(denied["new_motor_suppressed_for_recovery"])
        self.assertIsNone(denied["world_effect"])
        self.assertIsNone(denied["daily_noesis_policy_id"])
        self.assertEqual(len(denied["all_six_ports_invoked"]), 6)
        self.assertIsNone(bridge.existing_action_intent(event_id))

        allowed = run_daily_life_cycle(
            self.state, self.world, affectus_source=self.source,
            authorize_world=True)
        self.assertEqual(allowed["pending_prior_noesis_actions"], [])
        self.assertTrue(allowed["new_motor_suppressed_for_recovery"])
        self.assertEqual(len(allowed["reconciled_prior_noesis_actions"]), 1)
        self.assertEqual(allowed["reconciled_prior_noesis_actions"][0]["event_id"],
                         event_id)
        self.assertIsNone(allowed["world_effect"])
        self.assertIsNone(allowed["daily_noesis_policy_id"])
        self.assertEqual(len(allowed["all_six_ports_invoked"]), 6)
        self.assertEqual(reconcile_pending_daily_action(bridge), ())
        with self.lab._open() as db:
            self.assertEqual(db.execute(
                "SELECT count(*) FROM " + _ACTION_DOMAINS[choice.action]
                + " WHERE event_id=?", (event_id,)).fetchone()[0], 1)
            self.assertEqual(db.execute(
                "SELECT count(*) FROM embodied_events WHERE "
                "json_extract(envelope, '$.kind')='move'"
            ).fetchone()[0], original_moves)
        store = SixOrganRuntime.open(self.state)._port.brain.store
        with store.connect() as db:
            self.assertEqual(db.execute(
                "SELECT count(*) FROM policy_decisions "
                "WHERE trigger='noesis_situated_choice'"
            ).fetchone()[0], 1)
        recovered = allowed["reconciled_prior_noesis_actions"][0]
        memory = store.get_memory(recovered["memory_id"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        self.assertTrue(memory["source"].startswith("laboratory-home:action:"))
        self.assertEqual(sum(
            m["source"] == memory["source"] for m in store.memories(False)
        ), 1)

    def test_reserved_daily_motor_restarts_without_second_noesis_choice(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.subject_port import SubjectPort
        bridge, choice, event_id = self._reserve_crash_window()
        # No world action occurred: a killed host after the BrainStore commit.
        self.assertIsNone(bridge.existing_action_intent(event_id))
        reopened = SixOrganRuntime.open(self.state).bind_laboratory(
            SubjectPort(SpatialHabitat(self.world)), authorized=True)
        receipt = self._verify_one_replayed_world_action(
            reopened, choice, event_id)
        self.assertFalse(receipt["original_world_receipt_replayed"])

    def test_world_committed_memory_unadmitted_replays_once_after_restart(self):
        from unittest.mock import patch
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.subject_port import SubjectPort
        from doctor_lives.noesis_day import physical_args
        bridge, choice, event_id = self._reserve_crash_window()
        # Deterministic crash-window injection after ORIGINAL physical commit,
        # before first-person admission. This is NOT an external OS-kill test.
        with patch.object(bridge, "_admit_verified",
                          side_effect=RuntimeError("injected post-world interruption")):
            with self.assertRaisesRegex(RuntimeError, "injected post-world"):
                bridge.act(choice.action, event_id=event_id,
                           **physical_args(choice.action))
        self.assertEqual(bridge.existing_action_intent(event_id)["status"], "pending")
        reopened = SixOrganRuntime.open(self.state).bind_laboratory(
            SubjectPort(SpatialHabitat(self.world)), authorized=True)
        receipt = self._verify_one_replayed_world_action(
            reopened, choice, event_id)
        self.assertTrue(receipt["original_world_receipt_replayed"])


if __name__ == "__main__":
    unittest.main()
