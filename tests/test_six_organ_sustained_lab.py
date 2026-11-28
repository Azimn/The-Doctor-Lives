"""12-cycle real Laboratory six-organ experimental host + restart exercise.

Distinct pinned donors are REQUIRED in dedicated CI; no source stub,
unauthenticated lived percept or fabricated physical receipt is accepted.
The locked acceptance protocol still demands matched full task/lesion
comparisons before claiming the *complete* autonomous Pretorius.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

from doctor_lives.lab_six_organ_session import SixOrganLaboratoryCycle
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.neural import DEFAULT_CONFIG

HAS_ALL = (
    all(importlib.util.find_spec(x) is not None
        for x in ("pretorius_lab", "sensus_artificialis",
                  "synthetic_ipseity"))
    and bool(os.getenv("PRETORIUS_PINNED_AFFECTUS_ROOT"))
)


def config():
    c = dict(DEFAULT_CONFIG)
    c.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
             input_degree=4, action_population_size=8, seed=1842)
    return c


@unittest.skipUnless(HAS_ALL, "Requires three independently pinned donor checkouts")
class TwelveCycleActualSixOrganLaboratory(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.world = SpatialHabitat.create(self.root / "lab.sqlite3")
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        self.subject = SubjectPort(self.world)
        self.received = []
        self.config = config()
        self.weather_root = os.environ["PRETORIUS_PINNED_AFFECTUS_ROOT"]

    def renderer(self, first_person):
        if type(first_person) is not str or not first_person.startswith(
            ("I ", "My ", "Mine ", "Me ")
        ):
            raise PermissionError("Renderer received anything other than subject experience")
        self.received.append(first_person)
        return "I want to understand what happened."

    def host(self, runtime):
        return SixOrganLaboratoryCycle(
            runtime, self.subject, affectus_source=self.weather_root,
            renderer=self.renderer, authorized=True,
        )

    def test_12_cycles_all_six_source_attested_restart_and_no_extra_brain_store(self):
        rt = SixOrganRuntime.open(self.root / "brain", neural_config=self.config)
        results = []
        with self.host(rt) as session:
            for _ in range(6):
                results.append(session.cycle(authorized_world_action=True))
            self.assertEqual(session.weather.tick, 6)
            before = session.weather.snapshot_digest()
            rt.checkpoint()
        reopened = SixOrganRuntime.open(self.root / "brain")
        with self.host(reopened) as session:
            self.assertEqual(session.weather.tick, 6)
            self.assertEqual(before, session.weather.snapshot_digest())
            for _ in range(6):
                results.append(session.cycle(authorized_world_action=True))
            self.assertEqual(session.weather.tick, 12)
            self.assertIs(session.runtime._port, session.runtime.noesis._port)
            self.assertIs(session.runtime._port, session.runtime.mnemosyne._port)
            self.assertIs(session.runtime._port, session.runtime.sensus._port)
            self.assertIs(session.runtime._port, session.runtime.affectus._port)
            self.assertIs(session.runtime._port, session.runtime.corpus._port)
            self.assertIs(session.runtime._port, session.runtime.synthetic_ipseity._port)
        # Engineering metrics are audit output ONLY, never renderer context.
        import json
        diagnostics = {
            "schema": "pretorius.six-organ.actual-lab-12-cycle.v1",
            "cycles": len(results),
            "all_organs_each_cycle": sum(len(r.ports_used) == 6 for r in results),
            "executed_world_moves": sum(r.movement_status == "admitted" for r in results),
            "self_selected_goal_proven": sum(r.self_selected_goal_proven for r in results),
            "host_goal_actions": sum(r.host_provided_goal for r in results),
            "station_now": self.subject.embodied.verify()["station"],
            "destinations": [r.destination for r in results],
            "selected_tendencies": [r.selected_tendency for r in results],
            "restarts": 1,
            "book_read": any(
                m["source"].startswith("laboratory-home:action:")
                and "I read a page of" in m["text"]
                for m in reopened._port.brain.store.memories()
            ),
        }
        print("SIX_ORGAN_LAB_12_CYCLE_DIAGNOSTICS="
              + json.dumps(diagnostics, sort_keys=True))
        self.assertEqual(len(results), 12)
        self.assertEqual(len(self.received), 12)
        self.assertEqual([r.tick for r in results], list(range(1, 13)))
        self.assertTrue(all(r.ports_used == (
            "Sensus", "Corpus", "Affectus", "Mnemosyne",
            "Noesis", "Synthetic Ipseity"
        ) for r in results))
        self.assertTrue(all(r.scene_admitted == 1 and r.body_verified
                            and r.subjective_delivery_count == 1 for r in results))
        self.assertTrue(all(not r.self_selected_goal_proven for r in results))
        self.assertTrue(all(not r.scene_vetoed for r in results))
        # Four donor modulation outputs must actually be consumed by the
        # physical six-organ cycle, not merely serialized as decorative fields.
        self.assertTrue(all(set(r.affectus_consumed) == {
            "salience_gain", "exploration_bias",
            "rehearsal_bias", "decay_multiplier",
        } for r in results))
        self.assertTrue(all(0.5 <= r.sensus_prominence_consumed <= 1.0
                            for r in results))
        self.assertTrue(all(0.0 <= r.mnemonic_recall_cost_consumed <= 1.0
                            for r in results))
        from doctor_lives.canonical_affectus_weather import _META
        self.assertIsNotNone(reopened._port.brain.store.meta(_META))
        self.assertFalse((self.root / "brain" / "affectus.sqlite3").exists())
        self.assertFalse((self.root / "brain" / "spinoza_weather.json").exists())
        self.subject.verify()
        for m in reopened._port.brain.store.memories():
            if m["source"].startswith(("laboratory-home:", "sensus-pilot-verified:")):
                self.assertEqual(m["evidence_class"], "lived_runtime_memory")
        for line in self.received:
            for forbidden in ("action_scores_json", "lab_experiment_weather",
                              "world_epoch", "opponent_levels", "checkpoint_sha256"):
                self.assertNotIn(forbidden, line)

    def test_one_lived_world_consequence_drives_weather_at_most_once_across_restart(self):
        rt = SixOrganRuntime.open(
            self.root / "brain-one-event", neural_config=self.config,
        )
        with self.host(rt) as session:
            proposal = rt.noesis.deliberate(
                host_trigger="six_organ_one_weather_driver"
            )
            world_result = session._execute_movement(
                proposal, "station:hall"
            )
            lived = rt._port.brain.store.get_memory(world_result.memory_id)
            source = lived["source"]
            original = session.weather.driver(
                "goal_progress", 1.0, source,
            )
            session.weather.step(
                1, (original,), authorized=True,
                consumed_world_source=source,
            )
            self.assertEqual(
                session.weather.last_consumed_world_source(), source,
            )
            with self.assertRaisesRegex(RuntimeError, "twice"):
                session.weather.step(
                    2, (original,), authorized=True,
                    consumed_world_source=source,
                )
            self.assertEqual(session.weather.tick, 1)
            rt.checkpoint()
        reopened = SixOrganRuntime.open(self.root / "brain-one-event")
        with self.host(reopened) as session:
            self.assertEqual(session.weather.tick, 1)
            self.assertEqual(
                session.weather.last_consumed_world_source(), source,
            )
            with self.assertRaisesRegex(RuntimeError, "twice"):
                session.weather.step(
                    2, (session.weather.driver(
                        "goal_progress", 1.0, source,
                    ),), authorized=True,
                    consumed_world_source=source,
                )
            next_cycle = session.cycle(authorized_world_action=False)
            self.assertEqual(next_cycle.tick, 2)
            self.assertEqual(session.weather.last_consumed_world_source(), source)

    def test_crash_between_physical_commit_and_lived_admission_recovers_once(self):
        """No duplicate movement, one admitted memory and one reflection."""
        from unittest.mock import patch

        rt = SixOrganRuntime.open(self.root / "brain-crash", neural_config=self.config)
        with self.host(rt) as session:
            proposal = rt.noesis.deliberate(
                host_trigger="six_organ_crash_boundary"
            )
            before = len([
                m for m in rt._port.brain.store.memories(False)
                if m["source"].startswith("laboratory-home:action:")
            ])
            with patch.object(
                session.corpus._bridge, "_admit",
                side_effect=RuntimeError("crash after world commit"),
            ):
                with self.assertRaisesRegex(RuntimeError, "crash after world commit"):
                    session._execute_movement(proposal, "station:hall")
            revision = self.subject.embodied.verify()["revision"]
            self.assertEqual(self.subject.embodied.verify()["station"],
                             "station:hall")
            self.assertIsNotNone(session._pending())
            self.assertEqual(len([
                m for m in rt._port.brain.store.memories(False)
                if m["source"].startswith("laboratory-home:action:")
            ]), before)
        # No manual checkpoint here. The host precommits original neural
        # state and pending world request before calling the actual Lab.
        reopened = SixOrganRuntime.open(self.root / "brain-crash")
        with self.host(reopened) as gate:
            self.assertIsNone(gate._pending())
            self.assertEqual(self.subject.embodied.verify()["revision"], revision)
            observed = [
                m for m in reopened._port.brain.store.memories(False)
                if m["source"].startswith("laboratory-home:action:")
            ]
            self.assertEqual(len(observed), before + 1)
            with reopened._port.brain.store.connect() as db:
                rows = db.execute(
                    "SELECT id FROM policy_decisions WHERE trigger LIKE "
                    "'nc_feedback_%'"
                ).fetchall()
            self.assertEqual(len(rows), 1)
            # A new host is allowed to run a next full cycle only after
            # the source-world action has been durably reconciled.
            next_cycle = gate.cycle(authorized_world_action=False)
            self.assertEqual(len(next_cycle.ports_used), 6)
            self.assertIsNone(gate._pending())
            self.assertEqual(self.subject.embodied.verify()["station"], "station:hall")
        again = SixOrganRuntime.open(self.root / "brain-crash")
        with self.host(again) as gate:
            self.assertIsNone(gate._pending())
            with again._port.brain.store.connect() as db:
                self.assertEqual(
                    db.execute(
                        "SELECT count(*) FROM policy_decisions "
                        "WHERE trigger LIKE 'nc_feedback_%'"
                    ).fetchone()[0], 1,
                )
            self.assertEqual(self.subject.embodied.verify()["revision"], revision)

    def test_real_book_three_page_source_edition_custody_and_replay(self):
        """Physical read is actual page text, not a title/LLM improvisation.

        Movement destination and book ID are host-provided here: this
        demonstrates an authenticated TASK CAPABILITY, not autonomy.
        """
        import json
        from pretorius_lab.book_library import BookLibrary
        from pretorius_lab import book_library
        from pretorius_lab.physics import LabError

        fixture_path = (
            Path(book_library.__file__).resolve().parents[1]
            / "fixtures" / "DEMO_BOOK_007.json"
        )
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        lib = BookLibrary(self.world)
        lib.initialize()
        lib.install("book:007", **fixture,
                    event_id="six_book_fixture_verified_source")
        rt = SixOrganRuntime.open(
            self.root / "brain-book", neural_config=self.config,
        )
        with self.host(rt) as session:
            with self.assertRaises(PermissionError):
                session.book_action(
                    "book:007", "open", event_id="no-permission",
                )
            with self.assertRaises(LabError):
                session.book_action(
                    "book:007", "open", event_id="wrong-station",
                    authorized=True,
                )
            # Physical setup remains HOST-directed. Every move is audited,
            # not claimed as a self-originated intention.
            for event_id, target in (
                ("host-book-route-center", "station:center"),
                ("host-book-route-shelf-3", "station:shelf:3"),
            ):
                session.bridge.act(
                    "walk", event_id=event_id, station=target,
                )
            self.assertEqual(self.subject.embodied.verify()["station"],
                             "station:shelf:3")
            opened = session.book_action(
                "book:007", "open",
                event_id="verified-book-open", authorized=True,
            )
            self.assertEqual(opened["status"], "admitted")
            read = session.book_action(
                "book:007", "read",
                event_id="verified-book-page-one", authorized=True,
            )
            self.assertIn(fixture["pages"][0], read["subject"]["inner"])
            self.assertEqual(
                rt._port.brain.store.get_memory(read["memory_id"])["text"],
                read["subject"]["inner"],
            )
            same = session.book_action(
                "book:007", "read",
                event_id="verified-book-page-one", authorized=True,
            )
            self.assertEqual(same["status"], "already_admitted")
            self.assertEqual(same["memory_id"], read["memory_id"])
            session.book_action(
                "book:007", "turn", direction=1,
                event_id="verified-book-turn", authorized=True,
            )
            page2 = session.book_action(
                "book:007", "read",
                event_id="verified-book-page-two", authorized=True,
            )
            self.assertIn(fixture["pages"][1], page2["subject"]["inner"])
            self.assertNotEqual(read["memory_id"], page2["memory_id"])
            with self.assertRaises(Exception):
                session.book_action(
                    "book:001", "read", event_id="not-installed-book",
                    authorized=True,
                )
            session.ipseity.publish_current()
            session.ipseity.deliver_next(now_ms=900_000)
            rt.checkpoint()
        reopened = SixOrganRuntime.open(self.root / "brain-book")
        with self.host(reopened) as session:
            replay = session.book_action(
                "book:007", "read",
                event_id="verified-book-page-two", authorized=True,
            )
            self.assertEqual(replay["status"], "already_admitted")
            self.assertEqual(replay["memory_id"], page2["memory_id"])
            self.assertIn(fixture["pages"][1],
                          reopened._port.brain.store.get_memory(
                              replay["memory_id"]
                          )["text"])
            with self.assertRaises(Exception):
                session.book_action(
                    "book:007", "turn", direction=1,
                    event_id="verified-book-page-two",
                    authorized=True,
                )
        self.assertGreaterEqual(lib.verify()["catalog_count"], 1)
        print("SIX_ORGAN_SOURCE_VERIFIED_BOOK_READ=" + json.dumps({
            "real_lab_book_id": "book:007",
            "title": fixture["title"],
            "installed_pages": len(fixture["pages"]),
            "real_physical_station": "station:shelf:3",
            "source_verified_pages_read": 2,
            "duplicate_read_memories": 0,
            "host_directed_travel": True,
            "autonomous_book_goal": False,
            "historical_corpus_installed": False,
        }, sort_keys=True))

    def test_host_denial_all_six_still_run_without_world_move(self):
        rt = SixOrganRuntime.open(self.root / "denied", neural_config=self.config)
        before = self.subject.embodied.verify()["revision"]
        with self.host(rt) as session:
            outcome = session.cycle(authorized_world_action=False)
        self.assertEqual(outcome.ports_used, (
            "Sensus", "Corpus", "Affectus", "Mnemosyne",
            "Noesis", "Synthetic Ipseity",
        ))
        self.assertEqual(outcome.movement_status, "not_executed")
        # Looking is an authenticated receipt; lack of movement still means
        # one observation event may advance the world log revision.
        self.assertEqual(self.subject.embodied.verify()["station"],
                         "station:threshold")
        self.assertGreaterEqual(self.subject.embodied.verify()["revision"], before)


if __name__ == "__main__":
    unittest.main()
