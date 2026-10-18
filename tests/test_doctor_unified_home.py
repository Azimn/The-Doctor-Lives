"""Real Doctor + unified offered home actions: no fabricated memories or pages."""
import importlib.util
import tempfile
from pathlib import Path
import unittest

from doctor_lives.home_native_practice import _agent
from doctor_lives.lab_home_bridge import DoctorHomeBridge

HAS_LAB = importlib.util.find_spec("pretorius_lab") is not None


@unittest.skipUnless(HAS_LAB, "Requires pinned source-authenticated Laboratory")
class DoctorUnifiedHomeIntegration(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.home_arrangement import HomeArrangements
        from pretorius_lab.material_objects import MaterialObjects
        from pretorius_lab.book_library import BookLibrary

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.lab = SpatialHabitat.create(self.root / "lab.sqlite3")
        HomeLife(self.lab).initialize()
        DailyRhythm(self.lab).initialize(
            perishable_meals=True, physical_provisions=True,
            visible_portions=True, physical_paper=True)
        HomeArrangements(self.lab).initialize()
        MaterialObjects(self.lab).initialize()
        BookLibrary(self.lab).initialize()
        BookLibrary(self.lab).install(
            "book:007", edition_id="doctor-fixture-1",
            title="Persistent Scientific Notes",
            author="Test fixture",
            pages=["The first authentic page is before my eyes.",
                   "I left a bookmark exactly at this second page.",
                   "Other pages remain here even when I depart."],
            source_class="original_fixture", source_reference="test evidence")
        self.bridge, _ = _agent(self.root, 1842)

    def offered(self, cmd, **args):
        options = self.bridge.observe_opportunities()
        return next((o for o in options["offers"]
                     if o["command"] == cmd and o["args"] == args), None)

    def do(self, cmd, event_id, *, text=None, **args):
        option = self.offered(cmd, **args)
        self.assertIsNotNone(option, (cmd, args))
        return self.bridge.act_offer(option["offer_id"],
                                     event_id=event_id, text=text)

    def test_chair_world_event_admitted_once_and_observed_after_rest(self):
        from pretorius_lab.home_arrangement import HomeArrangements
        self.bridge.act("walk", event_id="go-hall", station="station:hall")
        self.bridge.act("walk", event_id="go-parlor", station="station:parlor")
        invitation = self.bridge.observe_opportunities()
        self.assertIn("I could", invitation["subject"]["inner"])
        action = self.offered("arrange:move",
                             object="chair:parlor", anchor="parlor:window")
        self.assertIsNotNone(action)
        done = self.bridge.act_offer(action["offer_id"],
                                     event_id="doctor-chair-window")
        self.assertTrue(done["subject"]["inner"].startswith("I "))
        old_id = done["memory_id"]
        self.assertEqual(
            HomeArrangements(self.lab).audit_state()["chair:parlor"]["anchor"],
            "parlor:window")
        earlier = self.bridge.act(
            "arrange:move", event_id="doctor-chair-window",
            object="chair:parlor", anchor="parlor:window")
        self.assertEqual(earlier["memory_id"], old_id)
        with self.assertRaises(RuntimeError):
            self.bridge.act(
                "arrange:move", event_id="doctor-chair-window",
                object="table:parlor", anchor="parlor:window")
        self.bridge.act("walk", event_id="exit-parlor", station="station:hall")
        self.bridge.act("walk", event_id="go-bed", station="station:bedroom")
        # Same real world after sleep, but Doctor is reopened from disk.
        for n in range(4):
            self.bridge.act("advance", event_id=f"evening{n}", minutes=240)
        self.bridge.act("sleep", event_id="sleep-night")
        self.bridge, _ = _agent(self.root, 1842)
        self.bridge.act("walk", event_id="morning-hall", station="station:hall")
        self.bridge.act("walk", event_id="morning-parlor", station="station:parlor")
        morning = self.bridge.observe()
        self.assertIn("beside the window", morning["subject"]["inner"])
        self.assertTrue(HomeArrangements(self.lab).verify()["verified"])

    def test_bookmark_source_page_and_process_return(self):
        from pretorius_lab.book_library import BookLibrary
        self.bridge.act("walk", event_id="to-center", station="station:center")
        self.bridge.act("walk", event_id="to-shelf", station="station:shelf:3")
        self.do("book", "open-my-book", book_id="book:007", operation="open")
        page1 = self.do("book", "read-first", book_id="book:007", operation="read")
        self.assertIn("first authentic page", page1["subject"]["inner"])
        self.do("book", "page-next", book_id="book:007", operation="turn", direction=1)
        placed = self.do("book", "place-page-flag", book_id="book:007",
                         operation="mark", bookmark_id="page-flag-1")
        # Retry same accepted world receipt after the page has changed;
        # never create a second memory or a second physical bookmark.
        retry = self.bridge.act("book", event_id="place-page-flag",
                                book_id="book:007", operation="mark",
                                bookmark_id="page-flag-1")
        self.assertEqual(retry["memory_id"], placed["memory_id"])
        self.assertEqual(retry["status"], "already_admitted")
        self.do("book", "close-for-tomorrow",
                book_id="book:007", operation="close")
        self.assertEqual(
            BookLibrary(self.lab).catalog("book:007")["book:007"]["bookmarks"],
            {"page-flag-1": 2})
        self.bridge, _ = _agent(self.root, 1842)
        self.do("book", "return-to-flag", book_id="book:007",
                operation="open_mark", bookmark_id="page-flag-1")
        reread = self.do("book", "read-real-second",
                         book_id="book:007", operation="read")
        self.assertIn("bookmark exactly at this second page",
                      reread["subject"]["inner"])
        self.assertEqual(
            BookLibrary(self.lab).catalog("book:007")["book:007"]["page_if_open"], 2)
        self.assertTrue(BookLibrary(self.lab).verify()["verified"])

    def test_stale_tokens_and_unsupported_actions_leave_no_false_memories(self):
        from pretorius_lab.home_arrangement import HomeArrangements
        self.bridge.act("walk", event_id="room-hall", station="station:hall")
        self.bridge.act("walk", event_id="room-parlor", station="station:parlor")
        stale = self.offered("arrange:move",
                             object="chair:parlor", anchor="parlor:window")
        self.do("arrange:turn", "turn-chair",
                object="chair:parlor", facing="parlor:door")
        before_count = len(self.bridge.doctor.brain.store.memories(False))
        with self.assertRaises(RuntimeError):
            self.bridge.act_offer(stale["offer_id"],
                                  event_id="stale-doctor-action")
        self.assertEqual(len(self.bridge.doctor.brain.store.memories(False)),
                         before_count)
        self.assertEqual(
            HomeArrangements(self.lab).audit_state()["chair:parlor"]["anchor"],
            "parlor:hearth")
        with self.assertRaises(PermissionError):
            self.bridge.act("invent_physical_outcome", event_id="fake-door")
        self.assertEqual(len(self.bridge.doctor.brain.store.memories(False)),
                         before_count)


if __name__ == "__main__":
    unittest.main()
