"""One actual Doctor memory per original material action receipt."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.living_action_bridge import DoctorLivingActionBridge
from doctor_lives.neural import DEFAULT_CONFIG

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


@unittest.skipUnless(HAS_LAB, "Use pinned unified physical Laboratory")
class RealDoctorUnifiedHomeTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.home_arrangement import HomeArrangements
        from pretorius_lab.book_library import BookLibrary
        from pretorius_lab.subject_port import SubjectPort

        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.lab = SpatialHabitat.create(self.root / "lab.sqlite3")
        HomeLife(self.lab).initialize()
        self.clock = DailyRhythm(self.lab)
        self.clock.initialize(perishable_meals=True,
                              physical_provisions=True,
                              visible_portions=True, physical_paper=True)
        HomeArrangements(self.lab).initialize()
        self.books = BookLibrary(self.lab)
        self.books.initialize()
        self.books.install(
            "book:007", edition_id="artificial-fixture",
            title="Observations on Natural Philosophy",
            author="Original test writer",
            pages=["The instrument was adjusted.",
                   "The rose was dried between paper.",
                   "The experiment ended in the afternoon."],
            source_class="original_fixture",
            source_reference="Integration fixture, not Pretorius canon")
        self.config = dict(DEFAULT_CONFIG)
        self.config.update(neurons=128, sensory_dim=64,
                           avg_recurrent_degree=8, input_degree=4,
                           action_population_size=8, seed=1842)
        self.doctor = PretoriusBrainPort(self.root / "brain",
                                         neural_config=self.config)
        self.live = DoctorLivingActionBridge(
            self.doctor, SubjectPort(self.lab), authorized=True)

    def act(self, command, event, *, bookmark_id=None, **args):
        seen = self.live.discover()
        choice = next((o for o in seen["offers_for_trusted_host"]
                       if o["command"] == command and o["args"] == args), None)
        self.assertIsNotNone(choice)
        result = self.live.act_offered(choice["offer_id"], event_id=event,
                                      bookmark_id=bookmark_id)
        self.assertTrue(result["physical_source"]["verified"])
        return result

    def test_real_doctor_experiences_bookmark_and_next_day_same_chair(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.subject_port import SubjectPort
        from pretorius_lab.home_arrangement import HomeArrangements

        self.act("walk", "to-center", station="station:center")
        self.act("walk", "to-shelf", station="station:shelf:3")
        self.act("book", "open-book", book_id="book:007", operation="open")
        self.act("book", "second-page", book_id="book:007",
                 operation="turn", direction=1)
        receipt = self.act("book", "mark-page", bookmark_id="rose-mark",
                           book_id="book:007", operation="mark")
        self.assertEqual(receipt["physical_source"]["source_table"], "books_events")
        self.act("book", "close-volume", book_id="book:007", operation="close")
        for i, station in enumerate(("station:center", "station:threshold",
                                     "station:hall", "station:parlor")):
            self.act("walk", f"to-parlor-{i}", station=station)
        chair = self.act("arrange:move", "move-chair",
                         object="chair:parlor", anchor="parlor:window")
        self.assertEqual(chair["physical_source"]["source_table"],
                         "arrangement_events")
        for i, station in enumerate(("station:hall", "station:bedroom")):
            self.act("walk", f"go-to-sleep-{i}", station=station)
        for i in range(4):
            self.clock.advance(240, event_id=f"evening-{i}")
        self.act("sleep", "normal-eight-hour-sleep")
        for i, station in enumerate(("station:hall", "station:parlor")):
            self.act("walk", f"morning-{i}", station=station)

        reloaded_brain = PretoriusBrainPort(
            self.root / "brain", neural_config=self.config)
        reloaded_lab = SpatialHabitat(self.lab.path)
        recovered = DoctorLivingActionBridge(
            reloaded_brain, SubjectPort(reloaded_lab), authorized=True)
        frame = recovered.discover()["subject"]["subject"]["inner"]
        self.assertIn("beside the window", frame)
        self.assertEqual(HomeArrangements(reloaded_lab)
                         .audit_state()["chair:parlor"]["anchor"], "parlor:window")
        self.assertEqual(self.books.catalog("book:007")["book:007"]["bookmarks"],
                         {"rose-mark": 2})
        memories = reloaded_brain.brain.store.memories(False)
        self.assertTrue(any(
            m["source"].startswith("laboratory-home:action:") and
            "reading chair" in m["text"] for m in memories))

    def test_fake_action_has_no_brain_or_world_effect(self):
        from pretorius_lab.subject_port import SubjectPort
        with self.assertRaises(PermissionError):
            DoctorLivingActionBridge(self.doctor, SubjectPort(self.lab))
        count = len(self.doctor.brain.store.memories(False))
        with self.assertRaises(Exception):
            self.live.act_offered("0" * 64, event_id="invented")
        self.assertEqual(count, len(self.doctor.brain.store.memories(False)))


if __name__ == "__main__":
    unittest.main()
