"""Engineer-only recorded chronology, Swatch presentation, and migration."""
from datetime import datetime, timezone
import sqlite3
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from doctor_lives import Experience, PretoriusBrain
from doctor_lives.engineer_time import engineer_time
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.store import BrainStore, SCHEMA_VERSION


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128, "sensory_dim": 64,
        "avg_recurrent_degree": 8, "input_degree": 4,
        "action_population_size": 8,
    })
    return cfg


class PrivateMemoryTimeTests(unittest.TestCase):
    def test_atomic_new_recording_uses_utc_and_beat_without_event_time_claim(self):
        with tempfile.TemporaryDirectory() as td:
            store = BrainStore(Path(td) / "brain.sqlite3")
            fixed = engineer_time(datetime(
                2026, 10, 12, 23, 30, tzinfo=timezone.utc
            ))
            with patch("doctor_lives.store.engineer_time", return_value=fixed):
                with store.transaction() as conn:
                    rid = store.add_memory(
                        conn, tick=7, text="I notice a closed door.",
                        source="engineer-controlled-event",
                        kind="observation", evidence_class="external_statement",
                        external=True, confidence=1, authored=False,
                        base_salience=.5,
                    )
                    # Both rows are visible to the same writer transaction.
                    self.assertIsNotNone(conn.execute(
                        "SELECT 1 FROM memory_timecodes WHERE memory_id=?", (rid,),
                    ).fetchone())
            stamp = store.engineer_memory_timecode(rid)
            self.assertEqual(stamp["recorded_tick"], 7)
            self.assertEqual(stamp["recorded_utc"], fixed.utc_iso)
            self.assertEqual(stamp["recorded_beat"], "@020")
            self.assertEqual(stamp["recorded_bmt_date"], "2026-10-13")
            self.assertEqual(stamp["recording_status"], "runtime_recorded")
            self.assertIsNone(stamp["event_utc"])
            self.assertEqual(stamp["event_time_basis"], "unknown")
            self.assertIsNone(store.engineer_memory_timecode("missing"))
            self.assertNotIn("recorded_beat", store.get_memory(rid))
            self.assertNotIn("recorded_utc", store.memories()[0])

    def test_rejected_write_rolls_back_both_memory_and_time(self):
        with tempfile.TemporaryDirectory() as td:
            store = BrainStore(Path(td) / "brain.sqlite3")
            rid = "mem_private_time_rollback"
            with self.assertRaises(RuntimeError):
                with store.transaction() as conn:
                    store.add_memory(
                        conn, tick=1, text="A cold laboratory.",
                        source="test", kind="observation",
                        evidence_class="external_statement",
                        external=True, confidence=1.0,
                        authored=False, base_salience=.3, record_id=rid,
                    )
                    raise RuntimeError("injected crash before commit")
            self.assertIsNone(store.get_memory(rid))
            self.assertIsNone(store.engineer_memory_timecode(rid))

    def test_existing_v6_memories_migrate_without_fabricated_time(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "brain.sqlite3"
            store = BrainStore(path)
            with store.transaction() as conn:
                old = store.add_memory(
                    conn, tick=12, text="An inherited historical account.",
                    source="archival-citation", kind="reconstruction",
                    evidence_class="external_statement",
                    external=True, confidence=.6,
                    authored=False, base_salience=.5,
                )
            # Recreate the exact version-6 shape for controlled migration.
            with store.transaction() as conn:
                conn.execute("DROP TABLE memory_timecodes")
                conn.execute(
                    "UPDATE meta SET value='6' WHERE key='schema_version'"
                )
            reopened = BrainStore(path)
            self.assertEqual(SCHEMA_VERSION, 7)
            self.assertEqual(reopened.meta("schema_version"), "7")
            prior = reopened.engineer_memory_timecode(old)
            self.assertEqual(prior["recording_status"], "legacy_unobserved")
            self.assertEqual(prior["recorded_tick"], 12)
            self.assertIsNone(prior["recorded_beat"])
            self.assertIsNone(prior["recorded_utc"])
            self.assertIsNone(prior["event_utc"])
            self.assertIsNotNone(reopened.get_memory(old))
            self.assertTrue(list((Path(td) / "migration_snapshots").glob("*.sqlite3")))

    def test_real_brain_render_never_exposes_private_beat_or_utc(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brain = PretoriusBrain(root, neural_config=small_config())
            fixed = engineer_time(datetime(
                2026, 10, 12, 11, 0, tzinfo=timezone.utc
            ))
            with patch("doctor_lives.store.engineer_time", return_value=fixed):
                result = brain.ingest(Experience(
                    "I see the brass measuring device.",
                    source="world-observation",
                ))
            rid = result["memory_id"]
            stamp = brain.store.engineer_memory_timecode(rid)
            self.assertEqual(stamp["recorded_beat"], "@500")
            permitted = brain.render_request().subject_frame.renderer_context()
            entire = "\n".join(permitted)
            self.assertNotIn("2026-10-12T11:00:00", entire)
            self.assertNotIn("@500", entire)
            self.assertNotIn("recorded_utc", entire)
            self.assertNotIn("BMT", entire)
            self.assertNotIn("memory_timecodes", entire)


if __name__ == "__main__":
    unittest.main()
