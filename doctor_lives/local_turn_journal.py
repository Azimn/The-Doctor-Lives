"""Durable local turn journal, separate from cognitive and subject-output state.

Only engineer-side orchestration reads this SQLite record. It does not grant
the character access to raw messages, state digests, or processing stages.

A separate SQLite writer lease serializes whole local turns across processes
while the journal's own commits remain durable between brain/organ operations.
Crashes release the lease without erasing the previously committed intent.
"""

from __future__ import annotations

import hashlib
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path


class LocalTurnConflict(RuntimeError):
    """A previous input is uncertain or in progress; fail closed."""


@dataclass(frozen=True)
class TurnRecord:
    key: str
    message: str
    before_digest: str
    before_tick: int
    before_neural_tick: int
    state: str


class LocalTurnJournal:
    """One active user communication at a time, with durable step checkpoints."""

    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS turns (
        turn_key TEXT PRIMARY KEY,
        message TEXT NOT NULL,
        message_sha256 TEXT NOT NULL,
        before_digest TEXT NOT NULL,
        stage TEXT NOT NULL
          CHECK(stage IN ('prepared','admitted','published','delivered')),
        before_tick INTEGER NOT NULL,
        before_neural_tick INTEGER NOT NULL
    );
    CREATE UNIQUE INDEX IF NOT EXISTS one_active_local_turn
      ON turns ((1)) WHERE stage != 'delivered';
    """

    def __init__(self, state_dir: str | Path):
        root = Path(state_dir)
        root.mkdir(parents=True, exist_ok=True)
        self._lock = sqlite3.connect(
            str(root / "local_turn_mutex.sqlite3"), timeout=1.0,
            isolation_level=None,
        )
        self._db = None
        try:
            self._lock.execute("PRAGMA journal_mode=WAL")
            self._lock.execute("CREATE TABLE IF NOT EXISTS lock_seed (k INTEGER PRIMARY KEY)")
            # Keep an IMMEDIATE transaction open for the whole local turn.
            # Only this mutex database is locked; journal, Doctor and organ
            # use their own durable independent transactions as usual.
            self._lock.execute("BEGIN IMMEDIATE")
            self._lock.execute("INSERT OR IGNORE INTO lock_seed VALUES (1)")
            self._db = sqlite3.connect(
                str(root / "local_turn_journal.sqlite3"), timeout=10.0,
                isolation_level=None,
            )
            self._db.execute("PRAGMA journal_mode=WAL")
            self._db.execute("PRAGMA synchronous=FULL")
            for statement in self._SCHEMA.split(";"):
                if statement.strip():
                    self._db.execute(statement)
            # Review-branch recovery from an earlier candidate journal:
            # legacy active turns cannot establish neural completion, and
            # therefore MUST remain blocked rather than guessed through.
            columns = {
                row[1] for row in self._db.execute("PRAGMA table_info(turns)")
            }
            for name in ("before_tick", "before_neural_tick"):
                if name not in columns:
                    self._db.execute("ALTER TABLE turns ADD COLUMN " + name + " INTEGER")
        except BaseException:
            if self._db is not None:
                self._db.close()
            self._lock.close()
            raise

    def open_turn(self) -> TurnRecord | None:
        row = self._db.execute(
            "SELECT turn_key,message,message_sha256,before_digest,"
            "stage,before_tick,before_neural_tick "
            "FROM turns WHERE stage!='delivered'"
        ).fetchone()
        if row is None:
            return None
        key, message, checksum, digest, stage, before_tick, before_neural_tick = row
        if type(before_tick) is not int or type(before_neural_tick) is not int:
            raise LocalTurnConflict(
                "Previous local journal lacks neural continuity evidence; "
                "manual review required"
            )
        if hashlib.sha256(message.encode("utf-8")).hexdigest() != checksum:
            raise LocalTurnConflict("Local input journal integrity mismatch")
        return TurnRecord(key, message, digest, before_tick, before_neural_tick, stage)

    def prepare(
        self, message: str, before_digest: str,
        before_tick: int, before_neural_tick: int,
    ) -> TurnRecord:
        if self.open_turn() is not None:
            raise LocalTurnConflict("Previous local turn requires reconciliation")
        key = uuid.uuid4().hex
        sha = hashlib.sha256(message.encode("utf-8")).hexdigest()
        try:
            self._db.execute(
                "INSERT INTO turns (turn_key,message,message_sha256,"
                "before_digest,stage,before_tick,before_neural_tick) "
                "VALUES (?,?,?,?,?,?,?)",
                (key, message, sha, before_digest, "prepared",
                 before_tick, before_neural_tick),
            )
        except sqlite3.IntegrityError as exc:
            raise LocalTurnConflict("Another active local turn exists") from exc
        return TurnRecord(
            key, message, before_digest, before_tick, before_neural_tick,
            "prepared",
        )

    def advance(self, key: str, prior: str, stage: str) -> None:
        allowed = {
            ("prepared", "admitted"),
            ("admitted", "published"),
            ("published", "delivered"),
        }
        if (prior, stage) not in allowed:
            raise LocalTurnConflict("Invalid local turn transition")
        row = self._db.execute(
            "UPDATE turns SET stage=? WHERE turn_key=? AND stage=?",
            (stage, key, prior),
        )
        if row.rowcount != 1:
            raise LocalTurnConflict("Stale local turn stage, refusing replay")

    def close(self):
        try:
            if self._db is not None:
                self._db.close()
        finally:
            try:
                if self._lock.in_transaction:
                    self._lock.execute("ROLLBACK")
            finally:
                self._lock.close()

    def __enter__(self) -> "LocalTurnJournal":
        return self

    def __exit__(self, *_):
        self.close()
