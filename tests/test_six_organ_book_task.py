"""Real objective book-task comparisons on a pinned Laboratory.

The neutral result against an equal-information receipt ledger is deliberate:
this establishes useful prior experience and task consequences, not superiority
or an autonomous Noesis intention.
"""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.organs import SixOrganRuntime
from doctor_lives.six_organ_book_task import VerifiedBookSearch

from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.book_library import BookLibrary
from pretorius_lab.embodied_access import EmbodiedAccess


def config():
    c = dict(DEFAULT_CONFIG)
    c.update(
        neurons=128, sensory_dim=64, avg_recurrent_degree=8,
        input_degree=4, action_population_size=8, seed=1842
    )
    return c


class RealBookTaskBenchmark(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def world(self, label: str):
        root = self.root / label
        root.mkdir()
        lab = SpatialHabitat.create(root / "world.sqlite3")
        library = BookLibrary(lab)
        library.initialize()
        library.install(
            "book:007", edition_id="loop-case-v1", title="Task Reference",
            author="Synthetic Fixture", pages=["Copper conducts electricity."],
            source_class="original_fixture",
            source_reference="authored bounded task benchmark",
        )
        port = EmbodiedAccess(lab)
        port.initialize(station="station:center")
        runtime = SixOrganRuntime.open(root / "brain", neural_config=config())
        pilot = runtime.bind_source_verified_book_search(port, authorized=True)
        return runtime, lab, port, pilot

    def sighting(self, port, pilot, *, admit=True):
        port.move("station:shelf:3")
        view = port.look()
        memories = pilot.admit_sighting(view) if admit else ()
        port.move("station:center")
        return view, memories

    def test_memory_lesion_restoration_and_equal_information_receipt_ledger(self):
        reports = {}
        for name in ("memory", "lesion", "restored", "ledger"):
            runtime, _, port, pilot = self.world(name)
            sight, ids = self.sighting(port, pilot)
            self.assertTrue(ids)
            target = next(
                mid for mid in ids
                if runtime._port.brain.store.get_memory(mid)["text"]
                == "I see research volume 7 on shelf 3."
            )
            if name == "lesion":
                with runtime._port.brain.store.transaction() as db:
                    runtime._port.brain.store.archive_memory(
                        db, target, runtime._port.brain.store.tick,
                        "controlled experimentally archived observation",
                    )
                    runtime._port.brain.store.bump_state_version(db)
            if name == "restored":
                with runtime._port.brain.store.transaction() as db:
                    runtime._port.brain.store.archive_memory(
                        db, target, runtime._port.brain.store.tick,
                        "experimental lesion before restoration",
                    )
                    db.execute("UPDATE memories SET active=1 WHERE id=?", (target,))
                    runtime._port.brain.store.bump_state_version(db)
            report = pilot.run(
                task_id="read-007", book_id="book:007", max_actions=4,
                authorized=True,
                ledger_hint="station:shelf:3" if name == "ledger" else None,
            )
            reports[name] = report
            self.assertEqual(report["actions_used"], 4)
            if report["success"]:
                self.assertEqual(
                    report["page_text"], "Copper conducts electricity."
                )
                memory = runtime._port.brain.store.get_memory(
                    report["outcome_memory_id"]
                )
                self.assertTrue(memory["text"].startswith(("I ", "My ")))
                self.assertTrue(
                    memory["source"].startswith("lab-book-read:")
                )
            before = port.verify()["revision"]
            self.assertEqual(
                pilot.run(
                    task_id="read-007", book_id="book:007",
                    max_actions=4, authorized=True,
                    ledger_hint=(
                        "station:shelf:3" if name == "ledger" else None
                    ),
                ),
                report,
            )
            self.assertEqual(port.verify()["revision"], before)
            runtime.checkpoint()
            reopened = SixOrganRuntime.open(self.root / name / "brain")
            replay = reopened.bind_source_verified_book_search(
                port, authorized=True
            ).run(
                task_id="read-007", book_id="book:007",
                max_actions=4, authorized=True,
                ledger_hint=("station:shelf:3" if name == "ledger" else None),
            )
            self.assertEqual(report, replay)
        self.assertTrue(reports["memory"]["success"])
        self.assertFalse(reports["lesion"]["success"])
        self.assertTrue(reports["restored"]["success"])
        self.assertTrue(reports["ledger"]["success"])
        self.assertEqual(reports["memory"]["shelf_order"][0], "station:shelf:3")
        self.assertEqual(reports["lesion"]["shelf_order"][0], "station:shelf:1")
        self.assertEqual(reports["ledger"]["shelf_order"][0], "station:shelf:3")
        print("SIX_ORGAN_REAL_LAB_BOOK_TASK_ABLATION="
              "memory 1/1, lesion 0/1, restoration 1/1, "
              "equal-information receipt ledger 1/1; superiority NOT shown")

    def test_no_sighting_fails_without_privileged_global_book_knowledge(self):
        runtime, _, port, pilot = self.world("uninformed")
        self.assertIsNone(pilot.memory_hint("book:007"))
        report = pilot.run(
            task_id="blind", book_id="book:007",
            max_actions=4, authorized=True,
        )
        self.assertFalse(report["success"])
        self.assertEqual(report["shelf_order"][0], "station:shelf:1")

    def test_sighting_source_forgery_denied_without_memory_write(self):
        runtime, _, port, pilot = self.world("forgery")
        port.move("station:shelf:3")
        real = port.look()
        forged = {**real, "event_hash": "a" * 64}
        before = runtime._port.brain.store.digest()
        with self.assertRaises(PermissionError):
            pilot.admit_sighting(forged)
        self.assertEqual(before, runtime._port.brain.store.digest())
        pilot.admit_sighting(real)
        self.assertEqual(
            pilot.memory_hint("book:007")["station"], "station:shelf:3"
        )
        with runtime._port.brain.store.transaction() as db:
            memory = pilot.memory_hint("book:007")["memory_id"]
            db.execute(
                "UPDATE memories SET text=? WHERE id=?",
                ("I see research volume 7 on shelf 1.", memory),
            )
        self.assertIsNone(pilot.memory_hint("book:007"))

    def test_host_authorization_failure_and_crash_reservation_fail_closed(self):
        runtime, _, port, pilot = self.world("interrupted")
        before = port.verify()["revision"]
        with self.assertRaises(PermissionError):
            pilot.run(task_id="missing", book_id="book:007", max_actions=4)
        self.assertEqual(port.verify()["revision"], before)
        with patch.object(port, "move", side_effect=RuntimeError("world unavailable")):
            with self.assertRaisesRegex(RuntimeError, "world unavailable"):
                pilot.run(
                    task_id="broken", book_id="book:007",
                    max_actions=4, authorized=True,
                )
        self.assertEqual(port.verify()["revision"], before)
        with self.assertRaisesRegex(RuntimeError, "reconciliation"):
            pilot.run(
                task_id="broken", book_id="book:007",
                max_actions=4, authorized=True,
            )
        with self.assertRaisesRegex(RuntimeError, "interrupted task"):
            pilot.run(
                task_id="new", book_id="book:007",
                max_actions=4, authorized=True,
            )

    def test_book_appearance_is_not_current_ground_truth_if_object_moves(self):
        runtime, lab, port, pilot = self.world("stale")
        _, ids = self.sighting(port, pilot)
        self.assertTrue(ids)
        self.assertEqual(
            pilot.memory_hint("book:007")["station"], "station:shelf:3"
        )
        lab.commit({
            "op": "place", "object_id": "book:007",
            "anchor_id": "shelf:1/slot:1",
        })
        stale = pilot.run(
            task_id="stale", book_id="book:007",
            max_actions=2, authorized=True,
        )
        self.assertFalse(stale["success"])
        self.assertIsNone(pilot.memory_hint("book:007"))
        port.move("station:center")
        found = pilot.run(
            task_id="corrected", book_id="book:007",
            max_actions=4, authorized=True,
        )
        self.assertTrue(found["success"])
        self.assertEqual(found["shelf_order"][0], "station:shelf:1")


if __name__ == "__main__":
    unittest.main()
