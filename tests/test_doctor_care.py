"""Real Doctor's first-person basic care under finite supplies."""
import importlib.util
import tempfile
from pathlib import Path
import unittest

from doctor_lives.home_native_practice import _agent

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None
if HAS_LAB:
    HAS_LAB = importlib.util.find_spec("pretorius_lab.care_safety") is not None


@unittest.skipUnless(HAS_LAB, "Requires pinned care-capable Laboratory")
class DoctorCareIntegrationTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.home_arrangement import HomeArrangements
        from pretorius_lab.material_objects import MaterialObjects
        from pretorius_lab.personal_projects import PersonalProjects
        from pretorius_lab.care_contract import HouseholdCareContract

        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)
        self.lab = SpatialHabitat.create(self.root / "lab.sqlite3")
        HomeLife(self.lab).initialize()
        self.clock = DailyRhythm(self.lab)
        self.clock.initialize(
            perishable_meals=True, physical_provisions=True,
            visible_portions=True, physical_paper=True)
        MaterialObjects(self.lab).initialize()
        HomeArrangements(self.lab).initialize()
        PersonalProjects(self.lab).initialize()
        HouseholdCareContract(self.lab).initialize()
        self.bridge, _ = _agent(self.root, 1842)

    def offer(self, command, **args):
        result = self.bridge.observe_opportunities()
        return next((o for o in result["offers"]
                     if o["command"] == command and o["args"] == args), None)

    def do(self, command, event_id, **args):
        selected = self.offer(command, **args)
        self.assertIsNotNone(selected, (command, args))
        return self.bridge.act_offer(
            selected["offer_id"], event_id=event_id)

    def next_day(self):
        for i in range(6):
            self.clock.advance(240, event_id=f"clock-next-day-{i}")

    def test_real_drinking_is_not_tied_to_tea_and_is_admitted_once(self):
        self.bridge.act("walk", event_id="hall", station="station:hall")
        self.bridge.act("walk", event_id="kitchen", station="station:kitchen")
        self.bridge.act("open", event_id="open-cupboard", container="cupboard:kitchen")
        before = self.clock.audit_state()["supplies"]["water"]
        done = self.do("drink_water", "doctor-real-drink")
        self.assertIn("drink a cup of water", done["subject"]["inner"])
        self.assertEqual(self.clock.audit_state()["supplies"]["water"], before-1)
        repeated = self.bridge.act("drink_water", event_id="doctor-real-drink")
        self.assertEqual(repeated["memory_id"], done["memory_id"])
        self.assertEqual(repeated["status"], "already_admitted")

    def test_doctor_collects_day_bound_real_delivery_then_remembers_it(self):
        self.bridge.act("walk", event_id="go-hall", station="station:hall")
        self.next_day()
        ready = self.bridge.observe_opportunities()
        self.assertIn("local supplier", self.bridge.observe()["subject"]["inner"])
        offered = self.offer("accept_delivery", day=1)
        self.assertIsNotNone(offered)
        before = self.clock.audit_state()["supplies"]["rations"]
        returned = self.bridge.act_offer(
            offered["offer_id"], event_id="doctor-collects-parcel")
        self.assertIn("I collect the ordinary household delivery", returned["subject"]["inner"])
        self.assertEqual(self.clock.audit_state()["supplies"]["rations"], before+4)
        self.assertIsNone(self.offer("accept_delivery", day=1))
        self.bridge, _ = _agent(self.root, 1842)
        self.assertTrue(self.clock.verify()["verified"])
        again = self.bridge.act("accept_delivery", event_id="doctor-collects-parcel",
                                day=1)
        self.assertEqual(again["memory_id"], returned["memory_id"])
        self.assertEqual(again["status"], "already_admitted")

    def test_period_washroom_is_a_voluntary_first_person_event_not_new_distress(self):
        self.bridge.act("walk", event_id="washroom-hall", station="station:hall")
        self.bridge.act("walk", event_id="washroom-bedroom", station="station:bedroom")
        before = self.clock.audit_state()
        used = self.do("use_washroom", "doctor-ordinary-sanitation")
        self.assertIn("I step into the small private washroom", used["subject"]["inner"])
        after = self.clock.audit_state()
        self.assertEqual(after["minute"] - before["minute"], 10)
        self.assertNotIn("bladder", after)
        replay = self.bridge.act("use_washroom",
                                 event_id="doctor-ordinary-sanitation")
        self.assertEqual(replay["memory_id"], used["memory_id"])
        self.assertTrue(self.clock.verify()["verified"])

    def test_no_forced_suffering_clock_after_severe_unmet_needs(self):
        self.bridge.act("walk", event_id="go-bedroom-hall", station="station:hall")
        self.bridge.act("walk", event_id="go-bedroom", station="station:bedroom")
        for i in range(10):
            self.clock.advance(240, event_id=f"care-pressure-{i}")
        hold = self.bridge.care_review()
        self.assertTrue(hold["pause_unattended_time"])
        sleeping = self.offer("sleep")
        self.assertIsNotNone(sleeping)
        before = self.clock.audit_state()["minute"]
        before_memories = len(self.bridge.doctor.brain.store.memories(False))
        with self.assertRaises(RuntimeError):
            self.bridge.act_offer(
                sleeping["offer_id"], event_id="unsafe-repeat-sleep")
        self.assertEqual(before, self.clock.audit_state()["minute"])
        self.assertEqual(before_memories,
                         len(self.bridge.doctor.brain.store.memories(False)))
        self.bridge.act("walk", event_id="return-hall", station="station:hall")
        self.assertIsNotNone(self.offer("accept_delivery",
                                        day=self.clock.audit_state()["minute"]//1440))


if __name__ == "__main__":
    unittest.main()
