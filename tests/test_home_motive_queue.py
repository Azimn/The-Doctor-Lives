"""Homeostatic priority and interruptible real-world action queue regression."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

from doctor_lives.home_motive_queue import (
    HomeActivityQueue, motive_scores, plan_steps, TASKS,
)
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


def state():
    return {
        "minute": 420, "fatigue": 2, "thirst": 2, "hunger": 2,
        "apparatus": 2, "cleanliness": {
            "room:sanctum": 1, "room:kitchen": 1, "room:shop": 1,
        },
        "supplies": {"oil": 5, "water": 7, "fuel": 4, "tea": 3,
                     "rations": 4, "reagents": 3, "spares": 2},
        "lamps": {room: 0 for room in ("room:sanctum", "room:experiment",
                                     "room:hall", "room:kitchen",
                                     "room:bedroom", "room:parlor", "room:shop")},
        "meal_ready": False, "experiments": 0, "repairs": 0, "chores": 0,
    }


class MotiveUtilityTests(unittest.TestCase):
    def test_normal_needs_keep_scientific_work_salient(self):
        self.assertEqual(motive_scores(state())["task"], "experiment")

    def test_need_pressure_changes_task_without_pretending_neural_choice(self):
        cases = [(dict(apparatus=0), "repair"),
                 (dict(fatigue=8), "rest"),
                 (dict(thirst=8), "tea"),
                 (dict(hunger=9), "meal")]
        for override, expected in cases:
            with self.subTest(override=override):
                s = state()
                s.update(override)
                self.assertEqual(motive_scores(s)["task"], expected)
                self.assertEqual(motive_scores(s, {"explore": 1.0})["task"], expected)

    def test_combined_exhaustion_and_worn_apparatus_compete_without_scripted_answer(self):
        s = state()
        s["apparatus"] = 0
        s["fatigue"] = 7
        # The observed worn-equipment pilot was not a pure repair test:
        # two preceding experiments also generated sufficient exhaustion
        # to make rest a defensible first priority.
        first = motive_scores(s, {"explore": 1.0})
        self.assertEqual(first["task"], "rest")
        self.assertTrue(first["eligible"]["repair"])
        # After bodily recovery, the *same* broken equipment should
        # regain motivational priority, without a case-name override.
        s["fatigue"] = 2
        second = motive_scores(s, {"explore": 1.0})
        self.assertEqual(second["task"], "repair")

    def test_unavailable_supplies_and_exhaustion_remain_real_vetoes(self):
        s = state()
        s["thirst"] = 9
        s["supplies"]["tea"] = 0
        result = motive_scores(s)
        self.assertFalse(result["eligible"]["tea"])
        self.assertNotEqual(result["task"], "tea")
        s["fatigue"] = 10
        self.assertFalse(motive_scores(s)["eligible"]["experiment"])
        self.assertFalse(motive_scores(s)["eligible"]["repair"])
        self.assertEqual(motive_scores(s)["task"], "rest")

    def test_body_lesion_removes_priority_but_does_not_invent_affordances(self):
        s = state()
        s["apparatus"] = 0
        with_body = motive_scores(s, {"explore": 1}, body_enabled=True)
        without_body = motive_scores(s, {"explore": 1}, body_enabled=False)
        self.assertEqual(with_body["task"], "repair")
        self.assertFalse(without_body["eligible"]["experiment"])
        self.assertNotEqual(without_body["task"], "experiment")

    @unittest.skipUnless(HAS_LAB, "Pinned Laboratory required for route planning")
    def test_activity_queue_uses_actual_stations_and_meal_is_two_actions(self):
        s = state()
        steps = plan_steps(s, "station:threshold", "meal")
        self.assertEqual([x["op"] for x in steps][-2:], ["prepare_meal", "eat"])
        self.assertIn("station:kitchen", [x["args"].get("station") for x in steps])
        s["minute"] = 20 * 60  # kitchen becomes dark
        steps = plan_steps(s, "station:threshold", "tea")
        self.assertIn("light", [x["op"] for x in steps])
        s["supplies"]["oil"] = 0
        with self.assertRaises(RuntimeError):
            plan_steps(s, "station:threshold", "tea")


@unittest.skipUnless(HAS_LAB, "Pinned Laboratory required for true world receipts")
class PersistentHomeActivities(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        root = Path(self.t.name)
        world = SpatialHabitat.create(root / "house.sqlite3")
        HomeLife(world).initialize()
        DailyRhythm(world).initialize()
        config = dict(DEFAULT_CONFIG)
        config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                      input_degree=4, action_population_size=8)
        doctor = PretoriusBrainPort(root / "brain", neural_config=config)
        self.bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)
        self.queue_path = root / "activities.sqlite3"
        self.queue = HomeActivityQueue(self.bridge, self.queue_path)

    def finish(self, plan_id):
        frames = []
        for n in range(12):
            result = self.queue.step(plan_id)
            if result["subject"] is not None:
                frames.append(result["subject"])
            if result["status"] == "completed":
                return frames
        self.fail("A bounded plan failed to finish in 12 authorized actions")

    def test_activity_completes_as_real_physical_work_with_source_receipts(self):
        p = self.queue.start("work-one")
        self.assertEqual(p["task"], "experiment")
        self.assertTrue(p["seen_source"].startswith("mem_"))
        actions = self.finish("work-one")
        self.assertEqual(self.bridge.subject.rhythm.audit_state()["experiments"], 1)
        self.assertEqual(self.queue.inspect("work-one")["status"], "completed")
        self.assertEqual(self.queue.verify("work-one")["source_receipts"],
                         len(actions))
        self.assertTrue(all(set(f) == {"inner", "spoken_aloud"} for f in actions))
        self.assertTrue(all(f["inner"].startswith(("I ", "My ")) for f in actions))
        self.assertTrue(all("fatigue=" not in f["inner"] for f in actions))

    def test_pause_resume_survives_restart_without_reselecting_personality(self):
        initial = self.queue.start("persistent")
        self.assertEqual(initial["choices"]["body_enabled"], True)
        self.queue.step("persistent")
        self.queue.pause("persistent")
        from doctor_lives.chassis import PretoriusBrainPort
        from pretorius_lab.subject_port import SubjectPort
        from doctor_lives.neural import DEFAULT_CONFIG
        config = dict(DEFAULT_CONFIG)
        config.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                      input_degree=4, action_population_size=8)
        reopened = PretoriusBrainPort(self.bridge.doctor.brain.state_dir,
                                      neural_config=config)
        other = DoctorHomeBridge(reopened,
                                 SubjectPort(self.bridge.world), authorized=True)
        queue2 = HomeActivityQueue(other, self.queue_path)
        self.assertEqual(queue2.step("persistent")["status"], "paused")
        self.assertEqual(queue2.resume("persistent")["status"], "active")
        for _ in range(12):
            r = queue2.step("persistent")
            if r["status"] == "completed":
                break
        self.assertEqual(queue2.verify("persistent")["status"], "completed")
        self.assertEqual(queue2.bridge.subject.rhythm.audit_state()["experiments"], 1)

    def test_world_interruption_prevents_stale_plan_and_requires_rechoice(self):
        self.queue.start("interrupted")
        # Independent real physical event between queued steps.
        self.bridge.act("advance", event_id="external-time", minutes=120)
        event = self.queue.step("interrupted")
        self.assertEqual(event["status"], "paused")
        self.assertEqual(event["reason"], "world_interrupted")
        with self.assertRaises(RuntimeError):
            self.queue.resume("interrupted")
        self.queue.cancel("interrupted")
        replacement = self.queue.start("revised")
        self.assertEqual(replacement["status"], "active")
        self.assertEqual(self.queue.verify("revised")["source_receipts"], 0)

    def test_post_world_pre_queue_crash_gap_fails_closed_without_repeat(self):
        plan = self.queue.start("crash-gap")
        first = plan["steps"][0]
        self.assertEqual(first["op"], "walk")
        # An already authorized physical action completes, then its queue
        # cursor write is lost in a simulated host crash.
        self.bridge.act(first["op"], event_id="motive-crash-gap-1",
                        **first["args"])
        position = self.bridge.subject.embodied.verify()["station"]
        outcome = self.queue.step("crash-gap")
        self.assertEqual(outcome["status"], "paused")
        self.assertEqual(outcome["reason"], "world_interrupted")
        self.assertEqual(self.bridge.subject.embodied.verify()["station"],
                         position)
        self.assertEqual(self.queue.verify("crash-gap")["source_receipts"], 0)
        with self.assertRaises(RuntimeError):
            self.queue.resume("crash-gap")

    def test_duplicate_plan_id_does_not_retrigger_neural_decision(self):
        x = self.queue.start("once")
        old = self.bridge.doctor.brain.store.tick
        y = self.queue.start("once")
        self.assertEqual(old, self.bridge.doctor.brain.store.tick)
        self.assertEqual(x, y)
        with self.assertRaises(RuntimeError):
            self.queue.start("once", body_enabled=False)
        with self.assertRaises(RuntimeError):
            self.queue.start("parallel")
        self.assertEqual(self.queue.verify("once")["source_receipts"], 0)

    def test_zero_budget_invention_and_receipt_tamper_are_rejected(self):
        with self.assertRaises(ValueError):
            self.queue.start("invalid/name")
        self.queue.start("safeguard")
        self.queue.step("safeguard")
        with self._db() as db:
            row = db.execute("SELECT receipts_json FROM activity_plans WHERE plan_id=?",
                             ("safeguard",)).fetchone()
            db.execute("UPDATE activity_plans SET receipts_json=? WHERE plan_id=?",
                       ('["' + "0" * 64 + '"]', "safeguard"))
        with self.assertRaises(RuntimeError):
            self.queue.verify("safeguard")

    def _db(self):
        import sqlite3
        return sqlite3.connect(self.queue_path)


if __name__ == "__main__":
    unittest.main()
