"""Engineer-only crash journal for the isolated three-organ research preview.

One scene at a time. No stored scene payload is ever projected to the subject.
This is a durable reconciliation log, not a Sensus donor modification.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4


class PreviewSceneConflict(RuntimeError):
    """An interrupted scene cannot be assumed completed or repeated."""


class PreviewSceneJournal:
    def __init__(self, state_dir: str | Path):
        root = Path(state_dir)
        root.mkdir(parents=True, exist_ok=True)
        self._mutex = sqlite3.connect(
            str(root / "preview_scene_mutex.sqlite3"), timeout=2.0,
            isolation_level=None,
        )
        self._mutex.execute("PRAGMA journal_mode=WAL")
        self._mutex.execute("CREATE TABLE IF NOT EXISTS mutex (id INTEGER PRIMARY KEY)")
        self._mutex.execute("BEGIN IMMEDIATE")
        self._mutex.execute("INSERT OR IGNORE INTO mutex VALUES(1)")
        self._db = sqlite3.connect(
            str(root / "preview_scene_journal.sqlite3"), timeout=10.0,
            isolation_level=None,
        )
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS scenes (
                id TEXT PRIMARY KEY, stage TEXT NOT NULL, op_index INTEGER NOT NULL,
                payload TEXT NOT NULL, decision_json TEXT,
                decision_before INTEGER, publish_before INTEGER
            );
            CREATE UNIQUE INDEX IF NOT EXISTS one_active_preview_scene
                ON scenes ((1)) WHERE stage != 'delivered';
            CREATE TABLE IF NOT EXISTS sensus_state (
                singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                snapshot_json TEXT NOT NULL
            );
        """)

    def active(self) -> dict | None:
        row = self._db.execute(
            "SELECT * FROM scenes WHERE stage!='delivered'"
        ).fetchone()
        if row is None:
            return None
        return self._decode(row)

    @staticmethod
    def _decode(row) -> dict:
        data = dict(row)
        data["payload"] = json.loads(data["payload"])
        if data["decision_json"] is not None:
            data["decision"] = json.loads(data["decision_json"])
        return data

    def snapshot(self) -> dict | None:
        row = self._db.execute(
            "SELECT snapshot_json FROM sensus_state WHERE singleton=1"
        ).fetchone()
        return json.loads(row[0]) if row else None

    def begin(self, payload: dict, snapshot: dict) -> dict:
        if self.active():
            raise PreviewSceneConflict("Pending scene must be reconciled first")
        key = "preview-scene-" + uuid4().hex
        with self._db:
            self._db.execute(
                "INSERT INTO scenes (id,stage,op_index,payload) VALUES(?,?,?,?)",
                (key, "scene_built", 0, json.dumps(payload, sort_keys=True)),
            )
            self._db.execute(
                "INSERT INTO sensus_state (singleton,snapshot_json) VALUES(1,?) "
                "ON CONFLICT(singleton) DO UPDATE SET snapshot_json=excluded.snapshot_json",
                (json.dumps(snapshot, sort_keys=True),),
            )
        return self.active()

    def step(self, key: str, index: int) -> None:
        with self._db:
            result = self._db.execute(
                "UPDATE scenes SET op_index=? WHERE id=? "
                "AND stage='scene_built' AND op_index=?",
                (index + 1, key, index),
            )
            if result.rowcount != 1:
                raise PreviewSceneConflict("Scene operation cursor changed")

    def stage(self, key: str, old: str, new: str) -> None:
        allowed = {
            ("scene_built", "admitted"),
            ("admitted", "decided"),
            ("decided", "published"),
            ("published", "delivered"),
        }
        if (old, new) not in allowed:
            raise PreviewSceneConflict("Illegal scene transition")
        with self._db:
            result = self._db.execute(
                "UPDATE scenes SET stage=? WHERE id=? AND stage=?",
                (new, key, old),
            )
            if result.rowcount != 1:
                raise PreviewSceneConflict("Scene stage was modified concurrently")

    def decision_boundary(self, key: str, rowid: int) -> None:
        with self._db:
            self._db.execute(
                "UPDATE scenes SET decision_before=? WHERE id=? "
                "AND stage='admitted' AND decision_before IS NULL",
                (rowid, key),
            )

    def set_decision(self, key: str, decision: dict) -> None:
        with self._db:
            result = self._db.execute(
                "UPDATE scenes SET decision_json=? WHERE id=? AND stage='admitted'",
                (json.dumps(decision, sort_keys=True), key),
            )
            if result.rowcount != 1:
                raise PreviewSceneConflict("Decision stage changed")

    def publish_boundary(self, key: str, seq: int) -> None:
        with self._db:
            self._db.execute(
                "UPDATE scenes SET publish_before=? WHERE id=? "
                "AND stage='decided' AND publish_before IS NULL",
                (seq, key),
            )

    def close(self) -> None:
        try:
            self._db.close()
        finally:
            try:
                self._mutex.execute("ROLLBACK")
            finally:
                self._mutex.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
