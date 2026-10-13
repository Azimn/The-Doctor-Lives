"""Engineer-only crash journal for the isolated three-organ research preview.

One scene at a time. No stored scene payload is ever projected to the subject.
This is a durable reconciliation log, not a Sensus donor modification.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
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
                decision_before INTEGER, publish_before INTEGER,
                op_active_index INTEGER, op_before_neural INTEGER,
                payload_sha256 TEXT, decision_sha256 TEXT
            );
            CREATE UNIQUE INDEX IF NOT EXISTS one_active_preview_scene
                ON scenes ((1)) WHERE stage != 'delivered';
            CREATE TABLE IF NOT EXISTS sensus_state (
                singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                snapshot_json TEXT NOT NULL, snapshot_sha256 TEXT
            );
        """)
        existing = {row["name"] for row in self._db.execute(
            "PRAGMA table_info(scenes)"
        )}
        for name in ("op_active_index", "op_before_neural"):
            if name not in existing:
                self._db.execute("ALTER TABLE scenes ADD COLUMN " + name + " INTEGER")
        for name in ("payload_sha256", "decision_sha256"):
            if name not in existing:
                self._db.execute("ALTER TABLE scenes ADD COLUMN " + name + " TEXT")
        snapshot_cols = {row["name"] for row in self._db.execute(
            "PRAGMA table_info(sensus_state)"
        )}
        if "snapshot_sha256" not in snapshot_cols:
            self._db.execute("ALTER TABLE sensus_state ADD COLUMN snapshot_sha256 TEXT")

    @contextmanager
    def _transaction(self):
        """Autocommit connections require an explicit SQLite transaction.

        Grouped journal writes must never become independently committed
        statements, especially scene intent and its matching Sensus snapshot.
        """
        self._db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self._db.execute("COMMIT")
        except BaseException:
            self._db.execute("ROLLBACK")
            raise

    def active(self) -> dict | None:
        row = self._db.execute(
            "SELECT * FROM scenes WHERE stage!='delivered'"
        ).fetchone()
        if row is None:
            return None
        return self._decode(row)

    @staticmethod
    def _digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @classmethod
    def _verify(cls, value: str | None, checksum: str | None, label: str) -> str:
        if not isinstance(value, str) or checksum != cls._digest(value):
            raise PreviewSceneConflict(
                "Unverified " + label + " integrity; operator reconciliation required"
            )
        return value

    @classmethod
    def _decode(cls, row) -> dict:
        data = dict(row)
        text = cls._verify(data["payload"], data["payload_sha256"], "scene payload")
        try:
            data["payload"] = json.loads(text)
            if data["decision_json"] is not None:
                decision = cls._verify(
                    data["decision_json"], data["decision_sha256"], "policy decision"
                )
                data["decision"] = json.loads(decision)
        except (ValueError, TypeError) as exc:
            raise PreviewSceneConflict("Malformed durable preview scene") from exc
        return data

    def snapshot(self) -> dict | None:
        row = self._db.execute(
            "SELECT snapshot_json,snapshot_sha256 FROM sensus_state WHERE singleton=1"
        ).fetchone()
        if row is None:
            return None
        snapshot = self._verify(row["snapshot_json"], row["snapshot_sha256"], "Sensus snapshot")
        try:
            return json.loads(snapshot)
        except (ValueError, TypeError) as exc:
            raise PreviewSceneConflict("Malformed durable Sensus snapshot") from exc

    def begin(self, payload: dict, snapshot: dict) -> dict:
        if self.active():
            raise PreviewSceneConflict("Pending scene must be reconciled first")
        key = "preview-scene-" + uuid4().hex
        with self._transaction():
            serialized = json.dumps(payload, sort_keys=True)
            self._db.execute(
                "INSERT INTO scenes (id,stage,op_index,payload,payload_sha256) "
                "VALUES(?,?,?,?,?)",
                (key, "scene_built", 0, serialized, self._digest(serialized)),
            )
            # Deliberately inside the same transaction: an exception while
            # serializing the second record must roll back the first insert.
            snapshot_text = json.dumps(snapshot, sort_keys=True)
            self._db.execute(
                "INSERT INTO sensus_state (singleton,snapshot_json,snapshot_sha256) "
                "VALUES(1,?,?) ON CONFLICT(singleton) DO UPDATE SET "
                "snapshot_json=excluded.snapshot_json,"
                "snapshot_sha256=excluded.snapshot_sha256",
                (snapshot_text, self._digest(snapshot_text)),
            )
        return self.active()

    def step(self, key: str, index: int) -> None:
        with self._transaction():
            result = self._db.execute(
                "UPDATE scenes SET op_index=?,op_active_index=NULL,"
                "op_before_neural=NULL WHERE id=? "
                "AND stage='scene_built' AND op_index=?",
                (index + 1, key, index),
            )
            if result.rowcount != 1:
                raise PreviewSceneConflict("Scene operation cursor changed")

    def prepare_ingress(self, key: str, index: int, neural_tick: int) -> int:
        """Durably seal the neural checkpoint baseline before ingress."""
        row = self._db.execute(
            "SELECT op_active_index,op_before_neural FROM scenes "
            "WHERE id=? AND op_index=? AND stage='scene_built'",
            (key, index),
        ).fetchone()
        if row is None:
            raise PreviewSceneConflict("Ingress cursor is stale")
        if row["op_active_index"] is not None:
            if int(row["op_active_index"]) != index:
                raise PreviewSceneConflict("Different incomplete ingress operation")
            return int(row["op_before_neural"])
        with self._transaction():
            self._db.execute(
                "UPDATE scenes SET op_active_index=?,op_before_neural=? "
                "WHERE id=? AND op_index=? AND op_active_index IS NULL",
                (index, neural_tick, key, index),
            )
        return neural_tick

    def stage(self, key: str, old: str, new: str) -> None:
        allowed = {
            ("scene_built", "admitted"),
            ("admitted", "decided"),
            ("decided", "published"),
            ("published", "delivered"),
        }
        if (old, new) not in allowed:
            raise PreviewSceneConflict("Illegal scene transition")
        with self._transaction():
            result = self._db.execute(
                "UPDATE scenes SET stage=? WHERE id=? AND stage=?",
                (new, key, old),
            )
            if result.rowcount != 1:
                raise PreviewSceneConflict("Scene stage was modified concurrently")

    def decision_boundary(self, key: str, rowid: int) -> None:
        with self._transaction():
            self._db.execute(
                "UPDATE scenes SET decision_before=? WHERE id=? "
                "AND stage='admitted' AND decision_before IS NULL",
                (rowid, key),
            )

    def set_decision(self, key: str, decision: dict) -> None:
        serialized = json.dumps(decision, sort_keys=True)
        with self._transaction():
            result = self._db.execute(
                "UPDATE scenes SET decision_json=?,decision_sha256=? "
                "WHERE id=? AND stage='admitted'",
                (serialized, self._digest(serialized), key),
            )
            if result.rowcount != 1:
                raise PreviewSceneConflict("Decision stage changed")

    def publish_boundary(self, key: str, seq: int) -> None:
        with self._transaction():
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
