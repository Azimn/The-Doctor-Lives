"""Real Laboratory tests of ORIGINAL Noesis-owned competing work choices."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.noesis_lab_work import (
    execute_noesis_work, propose_noesis_work,
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
class NoesisDirectActionTests(unittest.TestCase):
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

    def audit(self, decision_id):
        with self.port.brain.store.connect() as db:
            record = db.execute(
                "SELECT trigger,selected_action,policy_version,state_pressure_json,"
                "action_scores_json FROM policy_decisions WHERE id=?",
                (decision_id,),
            ).fetchone()
        self.assertIsNotNone(record)
        return dict(record), json.loads(record["state_pressure_json"])

    def test_noesis_ranks_two_real_offers_from_one_lived_read(self):
        self.wear_by_actually_working()
        read_id = self.read_real_page()
        original_state = self.world_state()
        proposal = propose_noesis_work(self.bridge)
        self.assertEqual(proposal.action, "repair")
        self.assertEqual(proposal.selector, "original_noesis")
        self.assertEqual(tuple(proposal.supporting_memory_ids), (read_id,))
        receipt, audit = self.audit(proposal.decision_id)
        self.assertEqual(receipt["trigger"], "noesis_situated_choice")
        self.assertEqual(receipt["selected_action"], "repair")
        self.assertEqual(audit["selector_authority"], "original_noesis")
        self.assertEqual(set(audit["candidate_base_scores"]), {"repair", "experiment"})
        self.assertIn(read_id, audit["used_memory_ids"])
        self.assertGreater(
            audit["candidate_final_scores"]["repair"]
            - audit["candidate_base_scores"]["repair"], 0.5
        )
        self.assertEqual(self.world_state(), original_state)
        self.assertEqual(self.history_count("repair"), 0)
        with self.assertRaises(PermissionError):
            execute_noesis_work(
                self.bridge, decision_id=proposal.decision_id,
                event_id="noesis-action",
            )
        performed = execute_noesis_work(
            self.bridge, decision_id=proposal.decision_id,
            event_id="noesis-action", authorized_world_action=True,
        )
        self.assertEqual(performed["action"], "repair")
        self.assertEqual(performed["world"]["status"], "admitted")
        self.assertEqual(self.world_state()["apparatus"], 3)
        self.assertEqual(self.history_count("repair"), 1)
        replay = execute_noesis_work(
            self.bridge, decision_id=proposal.decision_id,
            event_id="noesis-action", authorized_world_action=True,
        )
        self.assertEqual(replay["world"]["status"], "already_admitted")
        self.port.save()
        fresh = PretoriusBrainPort(self.port.brain.state_dir)
        after_restart = DoctorHomeBridge(fresh, self.subject, authorized=True)
        replay = execute_noesis_work(
            after_restart, decision_id=proposal.decision_id,
            event_id="noesis-action", authorized_world_action=True,
        )
        self.assertEqual(replay["world"]["status"], "already_admitted")
        self.assertEqual(self.history_count("repair"), 1)

    def test_memory_disabled_archived_restored_changes_noesis_scores(self):
        self.wear_by_actually_working()
        read_id = self.read_real_page()
        active = propose_noesis_work(
            self.bridge, neural_prior_enabled=False,
        )
        self.assertEqual(active.action, "repair")
        # When recurrent priors are explicitly lesioned, memory removal
        # forces the original Noesis to pick the deterministic tie-break.
        no_learning = propose_noesis_work(
            self.bridge, learning_enabled=False, neural_prior_enabled=False,
        )
        self.assertEqual(no_learning.action, "experiment")
        self.assertEqual(no_learning.supporting_memory_ids, ())
        self.assertEqual(no_learning.candidate_scores["repair"], 0.0)
        self.assertGreater(active.candidate_scores["repair"], 0.5)
        original_state = self.world_state()
        with self.port.brain.store.transaction() as db:
            self.port.brain.store.archive_memory(
                db, read_id, self.port.brain.store.tick,
                "reversible preregistered Noesis learned-memory lesion",
            )
            self.port.brain.store.bump_state_version(db)
        removed = propose_noesis_work(self.bridge, neural_prior_enabled=False)
        self.assertEqual(removed.action, "experiment")
        self.assertEqual(removed.supporting_memory_ids, ())
        with self.port.brain.store.transaction() as db:
            db.execute("UPDATE memories SET active=1 WHERE id=?", (read_id,))
            self.port.brain.store.bump_state_version(db)
        restored = propose_noesis_work(self.bridge, neural_prior_enabled=False)
        self.assertEqual(restored.action, "repair")
        self.assertEqual(tuple(restored.supporting_memory_ids), (read_id,))
        self.assertEqual(self.world_state(), original_state)

    def test_neural_scores_remain_original_and_are_causally_included(self):
        self.wear_by_actually_working()
        self.read_real_page()
        native = self.port.brain.neural.action_scores()
        observed = propose_noesis_work(
            self.bridge, learning_enabled=False, neural_prior_enabled=True
        )
        no_neural = propose_noesis_work(
            self.bridge, learning_enabled=False, neural_prior_enabled=False
        )
        self.assertAlmostEqual(observed.neural_scores["repair"], .2 * native["persist"])
        self.assertAlmostEqual(observed.neural_scores["experiment"], .2 * native["explore"])
        self.assertTrue(any(value > 0 for value in observed.neural_scores.values()))
        self.assertEqual(no_neural.neural_scores, {"experiment": 0.0, "repair": 0.0})
        self.assertNotEqual(observed.candidate_scores, no_neural.candidate_scores)
        self.assertEqual(self.port.brain.neural.action_scores(), native)

    def test_secondhand_instruction_is_not_cognitive_evidence(self):
        self.wear_by_actually_working()
        statement = self.port.ingest({
            "channel": "world",
            "text": "Someone claims I read a page that says: " + _PAGE,
            "source": "unverified-advice-about-apparatus",
        })
        self.assertEqual(
            self.port.brain.store.get_memory(statement["memory_id"])["evidence_class"],
            "external_statement"
        )
        self.walk("station:bench", "reported-advice-to-bench")
        choice = propose_noesis_work(self.bridge, neural_prior_enabled=False)
        self.assertEqual(choice.action, "experiment")
        self.assertEqual(choice.supporting_memory_ids, ())
        with self.assertRaises(PermissionError):
            execute_noesis_work(
                self.bridge, decision_id=choice.decision_id,
                event_id="untrusted-noesis-act",
            )
        self.assertEqual(self.history_count("repair"), 0)

    def test_other_book_and_unworn_condition_are_distinct(self):
        read_id = self.read_real_page(
            book_id="book:007",
            title="Original mechanical training notes",
            page="When my instruments look worn, I should repair "
                 "the mechanism carefully before I experiment.",
        )
        # Still original apparatus condition 2: cue not present.
        safe = propose_noesis_work(self.bridge, neural_prior_enabled=False)
        self.assertEqual(safe.action, "experiment")
        self.assertEqual(safe.supporting_memory_ids, ())
        acted = execute_noesis_work(
            self.bridge, decision_id=safe.decision_id,
            event_id="noesis-wear-once", authorized_world_action=True,
        )
        self.assertEqual(acted["action"], "experiment")
        self.assertEqual(self.world_state()["apparatus"], 1)
        learned = propose_noesis_work(self.bridge, neural_prior_enabled=False)
        self.assertEqual(learned.action, "repair")
        self.assertEqual(tuple(learned.supporting_memory_ids), (read_id,))
        with self.assertRaises(PermissionError):
            execute_noesis_work(
                self.bridge, decision_id=safe.decision_id,
                event_id="stale-old-action", authorized_world_action=True,
            )
        completed = execute_noesis_work(
            self.bridge, decision_id=learned.decision_id,
            event_id="noesis-repair-variant", authorized_world_action=True,
        )
        self.assertEqual(completed["action"], "repair")
        self.assertEqual(self.world_state()["repairs"], 1)


if __name__ == "__main__":
    unittest.main()
