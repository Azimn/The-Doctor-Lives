"""Real Laboratory experience-to-work-action tests; no production defaults altered."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.experience_to_action import (
    execute_bench_action, propose_bench_action,
)
from doctor_lives.neural import DEFAULT_CONFIG

LAB_AVAILABLE = importlib.util.find_spec("pretorius_lab") is not None
_PAGE = (
    "When my instruments look worn, I should repair the apparatus "
    "before I experiment."
)


def brain_config():
    c = dict(DEFAULT_CONFIG)
    c.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842,
    )
    return c


@unittest.skipUnless(LAB_AVAILABLE, "Requires real pinned physical Laboratory")
class VerifiedExperienceToActionTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        from pretorius_lab.book_library import BookLibrary

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.world = SpatialHabitat.create(root / "world.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        self.port = PretoriusBrainPort(root / "brain", neural_config=brain_config())
        self.subject = SubjectPort(self.world)
        self.bridge = DoctorHomeBridge(self.port, self.subject, authorized=True)
        self.books = BookLibrary(self.world)
        self.books.initialize()

    def world_state(self):
        self.subject.verify()
        with self.world._open() as db:
            return json.loads(db.execute(
                "SELECT value FROM rhythm_meta WHERE key='state'"
            ).fetchone()[0])

    def history_count(self, op):
        with self.world._open() as db:
            return db.execute(
                "SELECT count(*) FROM rhythm_events WHERE "
                "json_extract(envelope,'$.op')=?", (op,),
            ).fetchone()[0]

    def walk(self, station, event):
        result = self.bridge.act("walk", event_id=event, station=station)
        self.assertIn(result["status"], ("admitted", "already_admitted"))

    def wear_by_actually_working(self):
        self.walk("station:center", "fixture-to-center")
        self.walk("station:bench", "fixture-to-bench")
        self.assertEqual(self.world_state()["apparatus"], 2)
        wore = self.bridge.act("experiment", event_id="fixture-real-work-wear")
        self.assertEqual(wore["status"], "admitted")
        self.assertEqual(self.world_state()["apparatus"], 1)
        self.assertEqual(self.history_count("experiment"), 1)
        self.walk("station:center", "fixture-from-bench")

    def read_real_page(self, *, book_id="book:001", title="Bench notes", page=_PAGE):
        self.books.install(
            book_id, edition_id="real-manual-" + book_id.split(":")[1],
            title=title, author="Original Laboratory Research Fixture",
            pages=[page], source_class="original_fixture",
            source_reference="Experience-to-action test original authored page",
            event_id="fixture-install-" + book_id.replace(":", "-"),
        )
        if self.subject.embodied.verify()["station"] == "station:threshold":
            self.walk("station:center", "reading-to-center")
        self.walk("station:shelf:3", "reading-to-shelf")
        opened = self.bridge.act(
            "book", event_id="physical-open-" + book_id.replace(":", "-"),
            book_id=book_id, operation="open",
        )
        self.assertEqual(opened["status"], "admitted")
        read = self.bridge.act(
            "book", event_id="physical-read-" + book_id.replace(":", "-"),
            book_id=book_id, operation="read",
        )
        self.assertEqual(read["status"], "admitted")
        memory = self.port.brain.store.get_memory(read["memory_id"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        self.assertIn(page, memory["text"])
        self.walk("station:center", "reading-from-shelf")
        self.walk("station:bench", "reading-to-bench")
        return read["memory_id"]

    def test_lived_read_lesion_restoration_real_action_and_replay(self):
        self.wear_by_actually_working()
        read_id = self.read_real_page()
        before = self.subject.verify()["world_epoch"]
        self.assertEqual(
            propose_bench_action(self.bridge, read_memory_id=read_id).action,
            "repair",
        )
        self.assertEqual(
            propose_bench_action(
                self.bridge, read_memory_id=read_id, memory_enabled=False
            ).action,
            "experiment",
        )
        with self.port.brain.store.transaction() as db:
            self.port.brain.store.archive_memory(
                db, read_id, self.port.brain.store.tick,
                "isolated reversible research memory lesion",
            )
            self.port.brain.store.bump_state_version(db)
        self.assertEqual(
            propose_bench_action(self.bridge, read_memory_id=read_id).action,
            "experiment",
        )
        with self.port.brain.store.transaction() as db:
            db.execute("UPDATE memories SET active=1 WHERE id=?", (read_id,))
            self.port.brain.store.bump_state_version(db)
        self.assertEqual(
            propose_bench_action(self.bridge, read_memory_id=read_id).action,
            "repair",
        )
        self.assertEqual(self.subject.verify()["world_epoch"], before)
        self.assertEqual(self.world_state()["apparatus"], 1)
        # An equal-information literal rule also recommends repair: TIE.
        self.assertEqual(
            "repair" if self.world_state()["apparatus"] == 1 else "experiment",
            "repair",
        )
        with self.assertRaises(PermissionError):
            execute_bench_action(
                self.bridge, read_memory_id=read_id,
                event_id="learned-repair", expected_action="repair",
            )
        acted = execute_bench_action(
            self.bridge, read_memory_id=read_id, event_id="learned-repair",
            expected_action="repair", authorized_world_action=True,
        )
        self.assertEqual(acted["status"], "admitted")
        self.assertEqual(self.world_state()["apparatus"], 3)
        self.assertEqual(self.history_count("repair"), 1)
        self.assertEqual(self.world_state()["repairs"], 1)
        memory = self.port.brain.store.get_memory(acted["memory_id"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        self.assertIn("replace the worn component", memory["text"])
        retry = self.bridge.act("repair", event_id="learned-repair")
        self.assertEqual(retry["status"], "already_admitted")
        self.assertEqual(retry["memory_id"], acted["memory_id"])
        self.port.save()
        reopened = PretoriusBrainPort(self.port.brain.state_dir)
        restarted = DoctorHomeBridge(reopened, self.subject, authorized=True)
        replay = restarted.act("repair", event_id="learned-repair")
        self.assertEqual(replay["status"], "already_admitted")
        self.assertEqual(self.history_count("repair"), 1)

    def test_different_book_identity_and_page_paraphrase(self):
        self.wear_by_actually_working()
        read_id = self.read_real_page(
            book_id="book:007", title="Practical apparatus maintenance",
            page=("When my instruments look worn, I should repair the "
                  "workbench mechanism before I experiment."),
        )
        proposal = propose_bench_action(self.bridge, read_memory_id=read_id)
        self.assertEqual(proposal.action, "repair")
        self.assertEqual(proposal.origin, "host_bounded_manual_interpreter")
        physical = execute_bench_action(
            self.bridge, read_memory_id=read_id,
            event_id="variant-repair", expected_action="repair",
            authorized_world_action=True,
        )
        self.assertEqual(physical["status"], "admitted")
        self.assertEqual(self.world_state()["repairs"], 1)

    def test_unworn_bench_does_not_trigger_manual(self):
        read_id = self.read_real_page()
        self.assertEqual(self.world_state()["apparatus"], 2)
        proposed = propose_bench_action(self.bridge, read_memory_id=read_id)
        self.assertEqual(proposed.action, "experiment")
        self.assertIsNone(proposed.read_memory_id)
        physical = execute_bench_action(
            self.bridge, read_memory_id=read_id,
            event_id="unworn-experiment", expected_action="experiment",
            authorized_world_action=True,
        )
        self.assertEqual(physical["status"], "admitted")
        self.assertEqual(self.world_state()["experiments"], 1)
        self.assertEqual(self.history_count("repair"), 0)

    def test_secondhand_claim_does_not_count_as_read(self):
        self.wear_by_actually_working()
        report = self.port.ingest({
            "channel": "world",
            "text": "A stranger claims I read a book saying: " + _PAGE,
            "source": "unverified-stranger-manual",
        })
        m = self.port.brain.store.get_memory(report["memory_id"])
        self.assertEqual(m["evidence_class"], "external_statement")
        self.walk("station:bench", "report-to-bench")
        self.assertEqual(
            propose_bench_action(
                self.bridge, read_memory_id=report["memory_id"]
            ).action,
            "experiment",
        )
        with self.assertRaises(RuntimeError):
            execute_bench_action(
                self.bridge, read_memory_id=report["memory_id"],
                event_id="false-repair", expected_action="repair",
                authorized_world_action=True,
            )
        self.assertEqual(self.history_count("repair"), 0)


if __name__ == "__main__":
    unittest.main()
