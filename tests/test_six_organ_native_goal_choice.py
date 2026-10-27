"""Source-grounded native choice: explore a book versus avoid and rest.

Runs only with all four exact independently pinned donors in real Laboratory
CI, never by pretending a mocked choice is an authentic neural decision.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

from doctor_lives.lab_native_goal_choice import (
    NativeLaboratoryGoalChooser, _REST_KEY
)
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


@unittest.skipUnless(HAS_DONORS, "Pinned real Laboratory and donors required")
class NativeTwoGoalLaboratoryTests(unittest.TestCase):
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
        self.rendered = []
        self.affectus = os.environ["PRETORIUS_PINNED_AFFECTUS_ROOT"]

    def host(self, rt):
        def renderer(text):
            if type(text) is not str or not text.startswith(
                ("I ", "My ", "Mine ", "Me ")
            ):
                raise PermissionError("Unadmitted diagnostic text")
            self.rendered.append(text)
            return "I shall consider what my surroundings allow."
        return SixOrganLaboratoryCycle(
            rt, self.subject, affectus_source=self.affectus,
            renderer=renderer, authorized=True,
        )

    def install_fixture(self):
        from pretorius_lab.book_library import BookLibrary
        from pretorius_lab import book_library
        item = json.loads((
            Path(book_library.__file__).resolve().parents[1]
            / "fixtures" / "DEMO_BOOK_007.json"
        ).read_text(encoding="utf-8"))
        source = BookLibrary(self.world)
        source.initialize()
        source.install(
            "book:007", **item, event_id="native_choice_pinned_fixture"
        )
        return item

    def test_native_explore_pursues_real_book_without_second_goal_prompt(self):
        fixture = self.install_fixture()
        path = self.root / "book-mind"
        rt = SixOrganRuntime.open(path, neural_config=config())
        with self.host(rt) as session:
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            with self.assertRaises(PermissionError):
                NativeLaboratoryGoalChooser(session)
            origin = chooser.step()
            self.assertEqual(origin.status, "goal_created")
            self.assertEqual(origin.kind, "read_book")
            self.assertEqual(origin.selected_tendency, "explore")
            self.assertEqual(chooser.step().status, "authorization_required")
            self.assertEqual(
                self.subject.embodied.verify()["station"], "station:threshold"
            )
            rt.checkpoint()
        reopened = SixOrganRuntime.open(path)
        with self.host(reopened) as session:
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            for i in range(24):
                last = chooser.step(authorized_world_action=True)
                if last.status == "completed":
                    break
            else:
                self.fail("Native exploratory goal did not complete")
            self.assertEqual(last.kind, "read_book")
            self.assertEqual(last.goal_id, origin.goal_id)
            memory = reopened._port.brain.store.get_memory(last.memory_id)
            self.assertIn(fixture["pages"][0], memory["text"])
            self.assertTrue(memory["source"].startswith("laboratory-home:action:"))
            self.assertEqual(chooser.step().status, "already_complete")
        with self.world._open() as db:
            reads = [json.loads(r[0]) for r in db.execute(
                "SELECT payload FROM books_events"
            )]
        self.assertEqual(sum(x["action"]["op"] == "read" for x in reads), 1)
        print("TWO_GOAL_NATIVE_BOOK=", json.dumps({
            "native": "explore", "real_read": True, "restart": True,
            "steps": i + 1, "host_selected_route": True
        }, sort_keys=True))

    def _originate_rest_at_hall(self, chooser):
        for i in range(120):
            result = chooser.step()
            if result.kind == "rest" and result.status == "goal_created":
                self.assertEqual(result.selected_tendency, "avoid")
                print("TWO_GOAL_NATIVE_REST_DECISION_ATTEMPT=" + str(i + 1))
                return result
            self.assertEqual(result.status, "no_situated_goal")
            self.assertEqual(result.kind, None)
        self.fail("Original canonical neural policy never selected avoid")

    def test_native_avoid_rest_continues_after_restart_with_world_receipt(self):
        path = self.root / "rest-mind"
        rt = SixOrganRuntime.open(path, neural_config=config())
        with self.host(rt) as session:
            # Real host setup is not counted as a subject-originated step.
            session.bridge.act(
                "walk", station="station:hall", event_id="fixed_test_start_hall"
            )
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            origin = self._originate_rest_at_hall(chooser)
            self.assertEqual(chooser.step().status, "authorization_required")
            self.assertEqual(self.subject.embodied.verify()["station"], "station:hall")
            rt.checkpoint()
        restarted = SixOrganRuntime.open(path)
        with self.host(restarted) as session:
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            traveled = chooser.step(authorized_world_action=True)
            self.assertEqual(traveled.status, "moved")
            self.assertEqual(traveled.kind, "rest")
            self.assertEqual(traveled.goal_id, origin.goal_id)
            self.assertEqual(self.subject.embodied.verify()["station"], "station:bedroom")
            rest = chooser.step(authorized_world_action=True)
            self.assertEqual(rest.status, "completed")
            self.assertEqual(rest.kind, "rest")
            self.assertEqual(rest.goal_id, origin.goal_id)
            observed = restarted._port.brain.store.get_memory(rest.memory_id)
            self.assertEqual(observed["evidence_class"], "lived_runtime_memory")
            self.assertTrue(observed["source"].startswith("laboratory-home:action:"))
            self.assertEqual(chooser.step(authorized_world_action=True).status,
                             "already_complete")
        with self.world._open() as db:
            rests = [
                json.loads(row[0]) for row in db.execute(
                    "SELECT envelope FROM rhythm_events"
                )
                if "ng_" in row[0]
            ]
        self.assertEqual(len(rests), 1)
        print("TWO_GOAL_NATIVE_REST=", json.dumps({
            "native": "avoid", "true_world_rest": True,
            "restart": True, "duplicate_rest": False,
            "host_selected_route": True
        }, sort_keys=True))

    def test_tampered_rest_intention_denies_world_action(self):
        path = self.root / "tamper-mind"
        rt = SixOrganRuntime.open(path, neural_config=config())
        with self.host(rt) as session:
            session.bridge.act(
                "walk", station="station:hall", event_id="tamper_hall_setup"
            )
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            self._originate_rest_at_hall(chooser)
            before = self.subject.embodied.verify()["revision"]
            envelope = json.loads(rt._port.brain.store.meta(_REST_KEY))
            envelope["payload"]["phase"] = "complete"
            with rt._port.brain.store.transaction() as db:
                rt._port.brain.store.set_meta(
                    _REST_KEY, json.dumps(envelope), db
                )
            with self.assertRaisesRegex(RuntimeError, "Corrupt"):
                chooser.step(authorized_world_action=True)
            self.assertEqual(self.subject.embodied.verify()["revision"], before)
