"""Real-Laboratory opt-in endurance tests for one neural-originated book goal.

These are behavioral source/receipt tests, NOT an amendment to the frozen
twelve-cycle three-task preregistration or a proof of general D11 superiority.
Pinned donors are mandatory in the dedicated actual-Lab CI job.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

from doctor_lives.lab_endogenous_book_task import EndogenousBookPursuit, _KEY
from doctor_lives.lab_six_organ_session import SixOrganLaboratoryCycle
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime

HAS_DONORS = (
    all(importlib.util.find_spec(x) is not None
        for x in ("pretorius_lab", "sensus_artificialis", "synthetic_ipseity"))
    and bool(os.getenv("PRETORIUS_PINNED_AFFECTUS_ROOT"))
)


def config():
    c = dict(DEFAULT_CONFIG)
    c.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
             input_degree=4, action_population_size=8, seed=1842)
    return c


@unittest.skipUnless(HAS_DONORS, "Pinned actual Lab + three independent donors required")
class NeuralOriginatedBookGoalTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort

        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.world = SpatialHabitat.create(self.root / "lab.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        self.subject = SubjectPort(self.world)
        self.frames = []
        self.affectus = os.environ["PRETORIUS_PINNED_AFFECTUS_ROOT"]

    def host(self, rt):
        def render(text):
            if not isinstance(text, str) or not text.startswith(
                ("I ", "My ", "Mine ", "Me ")
            ):
                raise RuntimeError("Engineer state escaped the first-person gate")
            self.frames.append(text)
            return "I intend to consider my discoveries carefully."
        return SixOrganLaboratoryCycle(
            rt, self.subject, affectus_source=self.affectus,
            renderer=render, authorized=True,
        )

    def install_book(self):
        from pretorius_lab.book_library import BookLibrary
        from pretorius_lab import book_library

        fixture = json.loads((
            Path(book_library.__file__).resolve().parents[1]
            / "fixtures" / "DEMO_BOOK_007.json"
        ).read_text(encoding="utf-8"))
        library = BookLibrary(self.world)
        library.initialize()
        library.install(
            "book:007", **fixture, event_id="endogenous_verified_fixture"
        )
        return fixture

    def begin_genuinely_selected_goal(self, task):
        """Never inject 'explore', a book ID, or a preselected world destination."""
        for attempt in range(80):
            result = task.step(authorized_world_action=False)
            if result.status == "goal_created":
                print("BOOK_GOAL_NATIVE_START_ATTEMPT=" + str(attempt + 1))
                return result
            self.assertEqual(result.status, "dormant")
        self.fail("Canonical neural selector did not originate an explore goal")

    def test_source_grounded_goal_completes_after_restart_without_host_task(self):
        fixture = self.install_book()
        path = self.root / "doctor"
        rt = SixOrganRuntime.open(path, neural_config=config())
        with self.host(rt) as session:
            task = EndogenousBookPursuit(session, authorized=True)
            with self.assertRaises(PermissionError):
                EndogenousBookPursuit(session)
            origin = self.begin_genuinely_selected_goal(task)
            self.assertEqual(self.subject.embodied.verify()["station"],
                             "station:threshold")
            self.assertEqual(
                task.step(authorized_world_action=False).status,
                "authorization_required"
            )
            self.assertEqual(self.subject.embodied.verify()["station"],
                             "station:threshold")
            moved = task.step(authorized_world_action=True)
            self.assertEqual(moved.status, "moved")
            self.assertEqual(moved.world_action, "station:center")
            with rt._port.brain.store.connect() as db:
                row = db.execute(
                    "SELECT selected_action FROM policy_decisions WHERE id=?",
                    (json.loads(rt._port.brain.store.meta(_KEY))["payload"]
                     ["origin_policy_id"],)
                ).fetchone()
                self.assertEqual(row["selected_action"], "explore")
            rt.checkpoint()

        continued = SixOrganRuntime.open(path)
        with self.host(continued) as session:
            task = EndogenousBookPursuit(session, authorized=True)
            self.assertEqual(task.status().goal_id, origin.goal_id)
            actions = []
            for _ in range(22):
                step = task.step(authorized_world_action=True)
                actions.append(step.status)
                if step.status == "completed":
                    break
            else:
                self.fail("Internal goal failed to complete through real Laboratory")
            self.assertEqual(task.status().phase, "complete")
            memory = continued._port.brain.store.get_memory(step.memory_id)
            self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
            self.assertTrue(memory["source"].startswith("laboratory-home:action:"))
            self.assertIn(fixture["pages"][0], memory["text"])
            self.assertEqual(step.world_action, "book:007")
            self.assertEqual(
                task.step(authorized_world_action=True).status,
                "already_complete"
            )
            with self.world._open() as world_db:
                book_events = [json.loads(row[0]) for row in world_db.execute(
                    "SELECT payload FROM books_events"
                )]
            self.assertEqual(
                sum(e["action"]["op"] == "read" for e in book_events), 1
            )
            lived_reads = [
                m for m in continued._port.brain.store.memories(False)
                if m["source"].startswith("laboratory-home:action:")
                and "I read a page of" in m["text"]
            ]
            self.assertEqual(len(lived_reads), 1)
            print("ENDOGENOUS_BOOK_TASK_RESULT=" + json.dumps({
                "goal_origin": "verified_canonical_neural_explore",
                "goal_id": origin.goal_id,
                "task_complete": True, "world_book_reads": 1,
                "distinct_lived_page_memories": len(lived_reads),
                "resume_after_reopen": True,
                "followup_steps": len(actions),
                "host_selected_navigation": True,
                "scope": "one_opt_in_goal_not_full_independent_planning",
            }, sort_keys=True))

    def test_no_editions_means_exhausted_without_imaginary_read(self):
        rt = SixOrganRuntime.open(self.root / "empty-doctor", neural_config=config())
        with self.host(rt) as session:
            task = EndogenousBookPursuit(session, authorized=True)
            self.begin_genuinely_selected_goal(task)
            for _ in range(22):
                result = task.step(authorized_world_action=True)
                if result.status == "exhausted":
                    break
            else:
                self.fail("Absent source-backed books were not rejected")
            self.assertEqual(task.status().phase, "exhausted")
            self.assertFalse(any(
                "I read a page of" in m["text"]
                for m in rt._port.brain.store.memories(False)
            ))

    def test_goal_tampering_fails_closed_before_new_world_action(self):
        self.install_book()
        rt = SixOrganRuntime.open(self.root / "tampered-doctor", neural_config=config())
        with self.host(rt) as session:
            task = EndogenousBookPursuit(session, authorized=True)
            self.begin_genuinely_selected_goal(task)
            before = self.subject.embodied.verify()["station"]
            raw = json.loads(rt._port.brain.store.meta(_KEY))
            raw["payload"]["phase"] = "complete"  # deliberately stale checksum
            with rt._port.brain.store.transaction() as db:
                rt._port.brain.store.set_meta(
                    _KEY, json.dumps(raw, sort_keys=True), db
                )
            with self.assertRaisesRegex(RuntimeError, "Corrupt"):
                task.step(authorized_world_action=True)
            self.assertEqual(before, self.subject.embodied.verify()["station"])
