from __future__ import annotations

import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from doctor_lives.store import BrainStore, SCHEMA_VERSION, StateMigrationError


FIXTURE = Path(__file__).with_name("fixtures") / "store_schema_v2.sql"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_v2_state(path: Path) -> None:
    schema = FIXTURE.read_text(encoding="utf-8")
    conn = sqlite3.connect(path)
    try:
        conn.executescript(schema)
        meta = {
            "schema_version": "2",
            "tick": "41",
            "state_version": "17",
            "bootstrap_version": "",
            "deep_history_version": "",
        }
        conn.executemany(
            "INSERT INTO meta(key,value) VALUES(?,?)",
            sorted(meta.items()),
        )
        conn.execute(
            """INSERT INTO memories
            (id,created_tick,updated_tick,kind,text,source,evidence_class,external,
             confidence,authored,base_salience,rehearsal_count,last_rehearsed_tick,
             tags_json,active,source_event_id)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                "mem_legacy_lived", 17, 41, "episode",
                "A legacy lived observation survived long enough to matter.",
                "legacy-runtime", "lived_experience", 1, 0.91, 0, 0.73, 2, 39,
                json.dumps(["legacy", "continuity"]), 1, None,
            ),
        )
        conn.execute(
            """INSERT INTO relationships
            (peer_id,display_name,updated_tick,summary,evidence_json,commitments_json,
             unresolved_json,reliability,intellectual_respect,affection,irritation,trust)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                "morgan", "Morgan", 40, "A long-running collaborator.",
                json.dumps(["legacy evidence"]), json.dumps([]),
                json.dumps(["unfinished experiment"]), 0.82, 0.77, 0.31, 0.04, 0.79,
            ),
        )
        conn.execute(
            """INSERT INTO commitments
            (id,created_tick,updated_tick,description,status,due_tick,importance,actor,source,outcome)
            VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                "commit_legacy", 35, 41, "Revisit the apparatus after restart.",
                "open", 55, 0.88, "Morgan", "legacy-runtime", None,
            ),
        )
        conn.execute(
            "INSERT INTO needs(key,actual,felt,last_tick) VALUES(?,?,?,?)",
            ("fatigue", 0.61, 0.58, 41),
        )
        conn.commit()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


class StateMigrationTests(unittest.TestCase):
    def test_schema_v2_state_migrates_to_current_and_preserves_durable_rows(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "brain.sqlite3"
            make_v2_state(path)

            store = BrainStore(path)

            self.assertEqual(store.meta("schema_version"), str(SCHEMA_VERSION))
            self.assertEqual(store.meta("tick"), "41")
            self.assertEqual(store.get_memory("mem_legacy_lived")["text"],
                             "A legacy lived observation survived long enough to matter.")
            self.assertEqual(store.open_commitments()[0]["id"], "commit_legacy")
            self.assertEqual(store.relationships()[0]["peer_id"], "morgan")
            with store.connect() as conn:
                need = conn.execute(
                    "SELECT actual,felt,last_tick FROM needs WHERE key='fatigue'"
                ).fetchone()
                policy_columns = {
                    row["name"] for row in conn.execute(
                        "PRAGMA table_info(policy_decisions)"
                    ).fetchall()
                }
            self.assertEqual(tuple(need), (0.61, 0.58, 41))
            self.assertIn("base_action_scores_json", policy_columns)
            self.assertIn("state_pressure_json", policy_columns)

            lineage = json.loads(store.meta("state_schema_migrations_json", "[]"))
            self.assertEqual(len(lineage), 1)
            self.assertEqual(lineage[0]["from_version"], 2)
            self.assertEqual(lineage[0]["to_version"], SCHEMA_VERSION)
            snapshot = path.parent / "migration_snapshots" / lineage[0]["pre_migration_snapshot"]
            self.assertTrue(snapshot.is_file())
            self.assertEqual(
                file_sha256(snapshot),
                lineage[0]["pre_migration_snapshot_sha256"],
            )

            BrainStore(path)
            lineage_after = json.loads(
                BrainStore(path).meta("state_schema_migrations_json", "[]")
            )
            self.assertEqual(lineage_after, lineage)

    def test_failed_migration_restores_pre_migration_state(self):
        class FailingStore(BrainStore):
            def _migrate_schema(self, conn):
                super()._migrate_schema(conn)
                conn.execute(
                    "UPDATE memories SET text='should not survive rollback' "
                    "WHERE id='mem_legacy_lived'"
                )
                raise RuntimeError("injected migration failure")

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "brain.sqlite3"
            make_v2_state(path)

            with self.assertRaisesRegex(StateMigrationError, "pre-migration state restored"):
                FailingStore(path)

            conn = sqlite3.connect(path)
            try:
                version = conn.execute(
                    "SELECT value FROM meta WHERE key='schema_version'"
                ).fetchone()[0]
                text = conn.execute(
                    "SELECT text FROM memories WHERE id='mem_legacy_lived'"
                ).fetchone()[0]
                columns = {
                    row[1] for row in conn.execute(
                        "PRAGMA table_info(policy_decisions)"
                    ).fetchall()
                }
            finally:
                conn.close()
            self.assertEqual(version, "2")
            self.assertEqual(
                text,
                "A legacy lived observation survived long enough to matter.",
            )
            self.assertNotIn("base_action_scores_json", columns)

    def test_future_schema_fails_before_database_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "brain.sqlite3"
            store = BrainStore(path)
            with store.connect() as conn:
                conn.execute(
                    "UPDATE meta SET value='999' WHERE key='schema_version'"
                )
                conn.commit()
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            before = file_sha256(path)

            with self.assertRaisesRegex(StateMigrationError, "newer than runtime"):
                BrainStore(path)

            self.assertEqual(file_sha256(path), before)
            conn = sqlite3.connect(path)
            try:
                version = conn.execute(
                    "SELECT value FROM meta WHERE key='schema_version'"
                ).fetchone()[0]
            finally:
                conn.close()
            self.assertEqual(version, "999")

    def test_declared_current_but_partial_schema_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "brain.sqlite3"
            make_v2_state(path)
            conn = sqlite3.connect(path)
            try:
                conn.execute(
                    "UPDATE meta SET value=? WHERE key='schema_version'",
                    (str(SCHEMA_VERSION),),
                )
                conn.commit()
            finally:
                conn.close()

            with self.assertRaisesRegex(StateMigrationError, "does not match"):
                BrainStore(path)

            conn = sqlite3.connect(path)
            try:
                columns = {
                    row[1] for row in conn.execute(
                        "PRAGMA table_info(policy_decisions)"
                    ).fetchall()
                }
            finally:
                conn.close()
            self.assertNotIn("base_action_scores_json", columns)

    def test_malformed_schema_version_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "brain.sqlite3"
            make_v2_state(path)
            conn = sqlite3.connect(path)
            try:
                conn.execute(
                    "UPDATE meta SET value='six' WHERE key='schema_version'"
                )
                conn.commit()
            finally:
                conn.close()
            with self.assertRaisesRegex(StateMigrationError, "not an integer"):
                BrainStore(path)


if __name__ == "__main__":
    unittest.main()
