"""Actual Pretorius memory port with freely revisitable projects and real work."""
import importlib.util
import tempfile
from pathlib import Path
import unittest

from doctor_lives.home_native_practice import _agent

# Earlier Doctor-bridge workflows deliberately pin older Laboratory revisions.
# Skip this *new* protocol there; the dedicated project workflow pins the
# required source commit and must run the tests without skipping.
HAS_LAB = importlib.util.find_spec("pretorius_lab.personal_projects") is not None


@unittest.skipUnless(HAS_LAB, "Requires pinned opt-in Laboratory")
class DoctorProjectContinuityTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.home_arrangement import HomeArrangements
        from pretorius_lab.material_objects import MaterialObjects
        from pretorius_lab.personal_projects import PersonalProjects

        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.lab = SpatialHabitat.create(self.root / "lab.sqlite3")
        HomeLife(self.lab).initialize()
        DailyRhythm(self.lab).initialize(
            perishable_meals=True, physical_provisions=True,
            visible_portions=True, physical_paper=True)
        HomeArrangements(self.lab).initialize()
        MaterialObjects(self.lab).initialize()
        PersonalProjects(self.lab).initialize()
        self.bridge, _ = _agent(self.root, 1842)

    def offer(self, op, **args):
        return next((x for x in self.bridge.observe_opportunities()["offers"]
                     if x["command"] == op and x["args"] == args), None)

    def do(self, op, eid, *, text=None, **args):
        offered = self.offer(op, **args)
        self.assertIsNotNone(offered, (op, args))
        return self.bridge.act_offer(offered["offer_id"], event_id=eid, text=text)

    def begin(self):
        return self.do("project:start", "doctor-project-start",
                       project_id="project:0001",
                       text="Compare the behavior of glass under two temperatures.")

    def parlor(self):
        self.bridge.act("walk", event_id="hall", station="station:hall")
        self.bridge.act("walk", event_id="parlor", station="station:parlor")

    def test_doctor_declares_pauses_and_voluntarily_resumes_same_project_next_day(self):
        from pretorius_lab.personal_projects import PersonalProjects
        from pretorius_lab.daily_rhythm import DailyRhythm
        started = self.begin()
        self.assertIn("I decide to pursue", started["subject"]["inner"])
        first_memory = started["memory_id"]
        review = self.do("project:review", "doctor-project-review",
                         project_id="project:0001")
        self.assertIn("two temperatures", review["subject"]["inner"])
        self.do("project:reflect", "doctor-project-reflection",
                project_id="project:0001",
                text="The second vessel remains a hypothesis; I have not measured it.")
        self.do("project:pause", "doctor-pause",
                project_id="project:0001")
        self.parlor()
        self.bridge.act("open", event_id="open-writing-desk",
                        container="desk:parlor")
        unrelated = self.do("write_paper", "write-on-paper",
                            text="A separate thought on the evening sky.")
        self.assertIn("evening sky", unrelated["subject"]["inner"])
        for n in range(6):
            DailyRhythm(self.lab).advance(240, event_id=f"late-next-day-{n}")
        self.bridge, _ = _agent(self.root, 1842)
        state = PersonalProjects(self.lab).audit_state()["projects"]["project:0001"]
        self.assertEqual(state["status"], "paused")
        self.assertEqual(state["receipts"], [])
        self.assertEqual(DailyRhythm(self.lab).audit_state()["experiments"], 0)
        resumed = self.do("project:resume", "doctor-resume",
                          project_id="project:0001")
        self.assertIn("I decide to return", resumed["subject"]["inner"])
        self.assertEqual(
            PersonalProjects(self.lab).audit_state()["projects"]["project:0001"]["status"],
            "active")
        once = self.bridge.act("project:start", event_id="doctor-project-start",
                               project_id="project:0001",
                               text="Compare the behavior of glass under two temperatures.")
        self.assertEqual(once["memory_id"], first_memory)
        self.assertEqual(once["status"], "already_admitted")
        self.assertTrue(PersonalProjects(self.lab).verify()["verified"])

    def test_doctor_reconciles_only_a_physically_verified_effect_with_project(self):
        from pretorius_lab.personal_projects import PersonalProjects
        self.begin()
        self.parlor()
        physical = self.do("arrange:move", "actual-chair-project",
                           object="chair:parlor", anchor="parlor:window")
        # Only a caller explicitly selects this association; the project
        # system never claims the chair was moved just because text says so.
        linked = self.bridge.associate_project_evidence(
            "project:0001", {
                "source_table": "arrangement_events",
                "source_event_id": "actual-chair-project",
                "source_event_hash": self._world_receipt_hash("arrangement_events",
                                                             "actual-chair-project"),
            }, event_id="doctor-links-real-effect")
        self.assertIn("something I actually did", linked["subject"]["inner"])
        project = PersonalProjects(self.lab).audit_state()["projects"]["project:0001"]
        self.assertEqual(len(project["receipts"]), 1)
        self.assertEqual(project["status"], "active")
        previous_memories = len(self.bridge.doctor.brain.store.memories(False))
        with self.assertRaises(Exception):
            self.bridge.associate_project_evidence(
                "project:0001", {
                    "source_table": "arrangement_events",
                    "source_event_id": "invented-outcome",
                    "source_event_hash": "0"*64,
                }, event_id="doctor-false-result")
        self.assertEqual(len(self.bridge.doctor.brain.store.memories(False)),
                         previous_memories)
        self.assertEqual(len(PersonalProjects(self.lab).audit_state()
                             ["projects"]["project:0001"]["receipts"]),1)

    def _world_receipt_hash(self, table, event_id):
        with self.lab._open() as db:
            return db.execute(
                "SELECT event_hash FROM " + table + " WHERE event_id=?",
                (event_id,)).fetchone()[0]

    def test_no_forced_progress_when_the_doctor_is_merely_observing(self):
        from pretorius_lab.personal_projects import PersonalProjects
        self.begin()
        before = PersonalProjects(self.lab).audit_state()
        for _ in range(2):
            self.bridge.observe_opportunities()
            self.bridge.observe()
        self.assertEqual(before, PersonalProjects(self.lab).audit_state())
        self.assertIsNotNone(self.offer(
            "project:pause", project_id="project:0001"))
        self.assertIsNotNone(self.offer(
            "project:finish", project_id="project:0001"))
        self.assertEqual(before["projects"]["project:0001"]["receipts"], [])


if __name__ == "__main__":
    unittest.main()
