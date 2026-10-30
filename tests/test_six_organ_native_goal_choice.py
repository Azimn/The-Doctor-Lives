"""Source-grounded native choice: explore a book versus avoid and rest.

Runs only with all four exact independently pinned donors in real Laboratory
CI, never by pretending a mocked choice is an authentic neural decision.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
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
            post = chooser.step()
            # A later native AVOID is allowed to start a *different*
            # intention; an EXPLORE must not duplicate the completed book.
            self.assertIn(post.status, ("already_complete", "goal_created"))
            if post.status == "goal_created":
                self.assertEqual(post.kind, "rest")
                self.assertEqual(post.selected_tendency, "avoid")
        with self.world._open() as db:
            reads = [json.loads(r[0]) for r in db.execute(
                "SELECT payload FROM books_events"
            )]
        self.assertEqual(sum(x["action"]["op"] == "read" for x in reads), 1)
        print("TWO_GOAL_NATIVE_BOOK=", json.dumps({
            "native": "explore", "real_read": True, "restart": True,
            "steps": i + 1, "host_selected_route": True
        }, sort_keys=True))

    def _originate_rest_after_real_episodes(self, chooser):
        for i in range(12):
            result = chooser.step()
            if result.kind == "rest" and result.status == "goal_created":
                self.assertEqual(result.selected_tendency, "avoid")
                print("TWO_GOAL_NATIVE_REST_DECISION_ATTEMPT=" + str(i + 1))
                return result
            self.assertEqual(result.status, "no_situated_goal")
            self.assertEqual(result.kind, None)
        self.fail("After authentic six-organ movement/weather, native avoid never emerged")

    def test_native_avoid_rest_continues_after_restart_with_world_receipt(self):
        path = self.root / "rest-mind"
        rt = SixOrganRuntime.open(path, neural_config=config())
        with self.host(rt) as session:
            # Four REAL source-receipted six-organ world cycles supply
            # embodied consequences and temporal Affectus weather. Those
            # are host-scheduled preparatory interactions, NOT goals the
            # Doctor self-authored. The next native selection is unforced.
            for _ in range(4):
                prior = session.cycle(authorized_world_action=True)
                self.assertEqual(len(prior.ports_used), 6)
            before_denial = self.subject.embodied.verify()["station"]
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            origin = self._originate_rest_after_real_episodes(chooser)
            self.assertEqual(chooser.step().status, "authorization_required")
            self.assertEqual(self.subject.embodied.verify()["station"], before_denial)
            rt.checkpoint()
        restarted = SixOrganRuntime.open(path)
        with self.host(restarted) as session:
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            movement_count = 0
            for _ in range(12):
                rest = chooser.step(authorized_world_action=True)
                self.assertEqual(rest.kind, "rest")
                self.assertEqual(rest.goal_id, origin.goal_id)
                if rest.status == "moved":
                    movement_count += 1
                if rest.status == "completed":
                    break
            else:
                self.fail("Original native avoid/rest did not physically finish")
            self.assertGreaterEqual(movement_count, 1)
            self.assertEqual(self.subject.embodied.verify()["station"], "station:bedroom")
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
            for _ in range(4):
                session.cycle(authorized_world_action=True)
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            self._originate_rest_after_real_episodes(chooser)
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


    def test_same_individual_reads_then_selects_rest_with_two_restarts(self):
        """One continuous identity and world, TWO different neural decisions.

        The later rest decision is not supplied by the host. Four source-
        verified physical episodes are a known host-provided *opportunity*
        and deliberately NOT counted as native task origin evidence.
        """
        from doctor_lives.lab_endogenous_book_task import _KEY

        fixture = self.install_fixture()
        path = self.root / "one-mind-two-goals"
        rt = SixOrganRuntime.open(path, neural_config=config())
        original_world_epoch = self.subject.verify()["world_epoch"]

        with self.host(rt) as session:
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            first = chooser.step()
            self.assertEqual(first.kind, "read_book")
            self.assertEqual(first.status, "goal_created")
            self.assertEqual(first.selected_tendency, "explore")
            # Permission gating is independent of the original policy.
            before_permission = self.subject.embodied.verify()["station"]
            with self.world._open() as db:
                before_moves = sum(
                    json.loads(row[0])["kind"] == "move"
                    for row in db.execute("SELECT envelope FROM embodied_events")
                )
            self.assertEqual(chooser.step().status, "authorization_required")
            self.assertEqual(self.subject.embodied.verify()["station"],
                             before_permission)
            with self.world._open() as db:
                after_moves = sum(
                    json.loads(row[0])["kind"] == "move"
                    for row in db.execute("SELECT envelope FROM embodied_events")
                )
            self.assertEqual(after_moves, before_moves)
            for n in range(24):
                read = chooser.step(authorized_world_action=True)
                if read.status == "completed":
                    break
            else:
                self.fail("Original neural reading goal did not complete")
            self.assertEqual(read.kind, "read_book")
            self.assertEqual(first.goal_id, read.goal_id)
            page_memory_id = read.memory_id
            page_memory = rt._port.brain.store.get_memory(page_memory_id)
            self.assertIn(fixture["pages"][0], page_memory["text"])
            first_memory_source = page_memory["source"]
            self.assertTrue(first_memory_source.startswith(
                "laboratory-home:action:"
            ))
            # Four genuine world-action cycles with original cognition and
            # weather offer embodied experience before a second choice.
            # Their scheduling is HOST-DRIVEN, so not scored as goals.
            for _ in range(4):
                source_episode = session.cycle(authorized_world_action=True)
                self.assertEqual(len(source_episode.ports_used), 6)
            rt.checkpoint()

        reopened = SixOrganRuntime.open(path)
        with self.host(reopened) as session:
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            self.assertEqual(
                chooser.book.status().goal_id, first.goal_id
            )
            self.assertEqual(chooser.book.status().phase, "complete")
            prior = reopened._port.brain.store.get_memory(page_memory_id)
            self.assertEqual(prior["source"], first_memory_source)
            self.assertEqual(prior["text"], page_memory["text"])
            self.assertEqual(self.subject.verify()["world_epoch"],
                             original_world_epoch)
            for chance in range(12):
                next_goal = chooser.step(authorized_world_action=False)
                if (next_goal.status == "goal_created"
                        and next_goal.kind == "rest"):
                    break
                self.assertEqual(next_goal.status, "already_complete")
                self.assertEqual(next_goal.kind, "read_book")
            else:
                self.fail("Same brain did not produce a later native avoid goal")
            self.assertEqual(next_goal.selected_tendency, "avoid")
            self.assertNotEqual(next_goal.goal_id, first.goal_id)
            with reopened._port.brain.store.connect() as db:
                intent = json.loads(
                    reopened._port.brain.store.meta(_REST_KEY)
                )["payload"]
                selected = db.execute(
                    "SELECT selected_action FROM policy_decisions WHERE id=?",
                    (intent["origin_policy_id"],)
                ).fetchone()
                self.assertEqual(selected["selected_action"], "avoid")
            denied_station = self.subject.embodied.verify()["station"]
            self.assertEqual(
                chooser.step(authorized_world_action=False).status,
                "authorization_required"
            )
            self.assertEqual(self.subject.embodied.verify()["station"],
                             denied_station)
            reopened.checkpoint()

        last_runtime = SixOrganRuntime.open(path)
        with self.host(last_runtime) as session:
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            for step_index in range(15):
                resting = chooser.step(authorized_world_action=True)
                self.assertEqual(resting.kind, "rest")
                self.assertEqual(resting.goal_id, next_goal.goal_id)
                if resting.status == "completed":
                    break
            else:
                self.fail("Same individual did not physically finish rest")
            self.assertEqual(self.subject.embodied.verify()["station"],
                             "station:bedroom")
            self.assertEqual(chooser.step().status, "already_complete")
            self.assertEqual(chooser.book.status().phase, "complete")
            old_page = last_runtime._port.brain.store.get_memory(page_memory_id)
            rest_memory = last_runtime._port.brain.store.get_memory(
                resting.memory_id
            )
            self.assertEqual(old_page["source"], first_memory_source)
            self.assertIn(fixture["pages"][0], old_page["text"])
            self.assertNotEqual(old_page["id"], rest_memory["id"])
            self.assertEqual(rest_memory["evidence_class"], "lived_runtime_memory")
            self.assertTrue(rest_memory["source"].startswith(
                "laboratory-home:action:"
            ))
            self.assertIsNotNone(last_runtime._port.brain.store.meta(_KEY))
            self.assertIsNotNone(last_runtime._port.brain.store.meta(_REST_KEY))

        with self.world._open() as db:
            books = [json.loads(row[0]) for row in db.execute(
                "SELECT payload FROM books_events"
            )]
            rest_events = [json.loads(row[0]) for row in db.execute(
                "SELECT envelope FROM rhythm_events"
            ) if "ng_" in row[0]]
        self.assertEqual(
            sum(entry["action"]["op"] == "read" for entry in books), 1
        )
        self.assertEqual(len(rest_events), 1)
        print("NATIVE_SAME_LIFETIME_TWO_GOALS=" + json.dumps({
            "canonical_brain_restarts": 2,
            "same_laboratory_epoch": True,
            "different_original_policy_goals": 2,
            "book_read_world_events": 1,
            "rest_world_events": 1,
            "verified_first_page_memory_retained": True,
            "host_scheduled_preparatory_cycles": 4,
            "later_task_chosen_by_unforced_native_avoid": True,
            "host_selected_route": True,
            "scope": "conditional_goal_router_not_novel_goal_authorship",
        }, sort_keys=True))

    def test_self_consistent_forged_book_completion_cannot_clear_goal(self):
        """Even a recomputed checksum cannot replace actual world evidence."""
        from doctor_lives.lab_endogenous_book_task import (
            _KEY, _digest, _stable
        )
        self.install_fixture()
        rt = SixOrganRuntime.open(
            self.root / "forged-completion", neural_config=config()
        )
        with self.host(rt) as session:
            chooser = NativeLaboratoryGoalChooser(session, authorized=True)
            self.assertEqual(chooser.step().kind, "read_book")
            saved = json.loads(rt._port.brain.store.meta(_KEY))
            saved["payload"]["phase"] = "complete"
            saved["payload"]["read_memory_id"] = (
                "nonexistent_world_source_claim"
            )
            saved["sha256"] = _digest(saved["payload"])
            with rt._port.brain.store.transaction() as db:
                rt._port.brain.store.set_meta(_KEY, _stable(saved), db)
            before = self.subject.embodied.verify()["revision"]
            with self.assertRaisesRegex(RuntimeError, "verified lived read"):
                chooser.step(authorized_world_action=True)
            self.assertEqual(self.subject.embodied.verify()["revision"],
                             before)


    def test_offline_cli_native_goal_origin_permission_and_cold_completion(self):
        """Shipping CLI offers a goal opportunity, never chooses a book or route.

        Three separate Python processes use one BrainStore and one original
        Laboratory. A no-permission pass may originate a native explore goal
        but must not perform a physical action. The third process completes
        that persisted intention only after explicit world authorization.
        """
        fixture = self.install_fixture()
        path = self.root / "cli-native-mind"
        SixOrganRuntime.open(path, neural_config=config()).checkpoint()
        world_epoch = self.subject.verify()["world_epoch"]

        def cli(*args):
            return subprocess.run(
                [sys.executable, "-m", "doctor_lives.cli",
                 "--state", str(path), "lab-native",
                 "--world", str(self.root / "lab.sqlite3"),
                 "--affectus-source", self.affectus, *args],
                capture_output=True, text=True, timeout=120,
            )

        before_station = self.subject.embodied.verify()["station"]
        with self.world._open() as db:
            before_moves = sum(
                json.loads(row[0])["kind"] == "move"
                for row in db.execute("SELECT envelope FROM embodied_events")
            )
        created = cli("--steps", "1")
        self.assertEqual(created.returncode, 0, created.stderr)
        first = json.loads(created.stdout)
        self.assertEqual(first["status"], "goal_created")
        self.assertEqual(first["receipts"][0]["kind"], "read_book")
        self.assertEqual(first["receipts"][0]["selected_tendency"], "explore")
        self.assertTrue(first["host_selected_goal_mapping"])
        self.assertFalse(first["natural_language_goal_authorship_proven"])
        self.assertFalse(first["uncoached_three_task_life_proven"])
        self.assertEqual(first["cloud_calls"], 0)
        self.assertEqual(self.subject.embodied.verify()["station"], before_station)
        with self.world._open() as db:
            self.assertEqual(sum(
                json.loads(row[0])["kind"] == "move"
                for row in db.execute("SELECT envelope FROM embodied_events")
            ), before_moves)

        denied = cli("--steps", "3")
        self.assertEqual(denied.returncode, 0, denied.stderr)
        self.assertEqual(json.loads(denied.stdout)["status"],
                         "authorization_required")
        self.assertEqual(self.subject.embodied.verify()["station"], before_station)
        with self.world._open() as db:
            self.assertEqual(sum(
                json.loads(row[0])["kind"] == "move"
                for row in db.execute("SELECT envelope FROM embodied_events")
            ), before_moves)

        completed = cli("--steps", "24", "--allow-world-actions")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        third = json.loads(completed.stdout)
        self.assertEqual(third["status"], "completed")
        self.assertLessEqual(third["steps"], 24)
        self.assertTrue(third["original_world_epoch_unchanged"])
        self.assertEqual(self.subject.verify()["world_epoch"], world_epoch)
        self.assertRegex(third["clock"]["beat"], r"^@[0-9]{3}$")
        read = third["receipts"][-1]
        self.assertEqual(read["kind"], "read_book")
        self.assertEqual(read["goal_id"], first["receipts"][0]["goal_id"])
        memory = SixOrganRuntime.open(path)._port.brain.store.get_memory(
            read["memory_id"]
        )
        self.assertIn(fixture["pages"][0], memory["text"])
        self.assertEqual(memory["evidence_class"], "lived_runtime_memory")
        self.assertTrue(memory["source"].startswith("laboratory-home:action:"))
        with self.world._open() as db:
            reads = [json.loads(row[0]) for row in
                     db.execute("SELECT payload FROM books_events")]
        self.assertEqual(sum(e["action"]["op"] == "read" for e in reads), 1)

        # An absent local donor is an honest failure before any new world act.
        missing = cli("--affectus-source", str(self.root / "absent"))
        self.assertNotEqual(missing.returncode, 0)
        with self.world._open() as db:
            self.assertEqual(sum(
                json.loads(row[0])["action"]["op"] == "read"
                for row in db.execute("SELECT payload FROM books_events")
            ), 1)
        print("R4_OFFLINE_NATIVE_CLI=" + json.dumps({
            "cold_processes": 3,
            "goal_origin": "original_neural_explore",
            "goal_mapping": "host_reviewed",
            "world_permission_required": True,
            "physical_book_read": 1,
            "canonical_memory": True,
            "three_uncoached_goals_proven": False,
        }, sort_keys=True))
