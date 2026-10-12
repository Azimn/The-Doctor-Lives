"""Host-attested, durable text-emission receipts for standalone Pretorius.

The model never certifies speech. A trusted local sink first reports actual
successful output. The journal then records a narrow host acknowledgment.
If a process dies after emission begins but before the acknowledgment, the
result is UNKNOWN and automatic replay is forbidden; stdout cannot provide
end-to-end exactly-once semantics.
"""
from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .engineer_time import engineer_time


class SpeechEmissionUncertain(RuntimeError):
    """Emission may have occurred; do not claim or repeat it automatically."""


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SpeechSinkAck:
    """Host-only return from the actual output boundary, not model output."""
    delivery_key: str
    sink_id: str
    content_sha256: str


@dataclass(frozen=True)
class SpeechEmissionReceipt:
    delivery_key: str
    sink_id: str
    content_sha256: str
    text: str
    before_tick: int
    before_neural_tick: int
    emitted_utc: str | None = None
    emitted_bmt_date: str | None = None
    emitted_beat: str | None = None


class SpeechEmissionJournal:
    """Store model output before renderer ACK; certify only successful emission."""

    def __init__(self, state_dir: str | Path):
        root = Path(state_dir)
        root.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(
            str(root / "speech_emission.sqlite3"), timeout=10,
            isolation_level=None,
        )
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.execute("""
            CREATE TABLE IF NOT EXISTS emissions (
                delivery_key TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                content_sha256 TEXT NOT NULL,
                state TEXT NOT NULL CHECK(
                    state IN ('prepared','emitting','acknowledged')
                ),
                sink_id TEXT,
                before_tick INTEGER NOT NULL,
                before_neural_tick INTEGER NOT NULL,
                emitted_utc TEXT,
                emitted_bmt_date TEXT,
                emitted_beat TEXT
            )
        """)
        # Candidate upgrades must not fabricate emission times for older ACKs.
        columns = {row[1] for row in self._db.execute("PRAGMA table_info(emissions)")}
        for name in ("emitted_utc", "emitted_bmt_date", "emitted_beat"):
            if name not in columns:
                self._db.execute("ALTER TABLE emissions ADD COLUMN " + name + " TEXT")

    def _row(self, key: str):
        row = self._db.execute(
            "SELECT content,content_sha256,state,sink_id,"
            "before_tick,before_neural_tick,emitted_utc,emitted_bmt_date,"
            "emitted_beat FROM emissions WHERE delivery_key=?",
            (key,),
        ).fetchone()
        if row is not None and digest(row[0]) != row[1]:
            raise SpeechEmissionUncertain("Stored speech integrity mismatch")
        return row

    def prepare(self, key: str, text: str, *,
                before_tick: int, before_neural_tick: int) -> str:
        if type(key) is not str or not key or type(text) is not str:
            raise TypeError("Only keyed textual speech can be prepared")
        if not text.strip() or len(text) > 4000:
            raise ValueError("Speech must be nonblank and at most 4000 characters")
        current = self._row(key)
        if current is not None:
            if current[0] != text:
                raise SpeechEmissionUncertain("Different output for a committed turn")
            return current[0]
        self._db.execute(
            "INSERT INTO emissions (delivery_key,content,content_sha256,"
            "state,sink_id,before_tick,before_neural_tick) "
            "VALUES (?,?,?,?,?,?,?)",
            (key, text, digest(text), "prepared", None,
             before_tick, before_neural_tick),
        )
        return text

    def prepared_text(self, key: str) -> str | None:
        row = self._row(key)
        if row is None:
            return None
        if row[2] == "emitting":
            raise SpeechEmissionUncertain(
                "Emission outcome unknown; never repeat an uncertain output"
            )
        return row[0]

    def emit_once(
        self, key: str, sink: Callable[[str, str], SpeechSinkAck]
    ) -> SpeechEmissionReceipt:
        row = self._row(key)
        if row is None:
            raise SpeechEmissionUncertain("No recorded model output to emit")
        (text, checksum, state, sink_id, before_tick, before_neural_tick,
         emitted_utc, emitted_bmt_date, emitted_beat) = row
        if state == "emitting":
            raise SpeechEmissionUncertain(
                "Output may already be visible; manual reconciliation required"
            )
        if state == "prepared":
            # Commit attempt BEFORE handing text to the external sink.
            changed = self._db.execute(
                "UPDATE emissions SET state='emitting' "
                "WHERE delivery_key=? AND state='prepared'", (key,),
            )
            if changed.rowcount != 1:
                raise SpeechEmissionUncertain("Concurrent speech emission detected")
            ack = sink(text, key)
            if (type(ack) is not SpeechSinkAck
                or ack.delivery_key != key
                or ack.content_sha256 != checksum
                or type(ack.sink_id) is not str
                or not ack.sink_id.strip()
                or len(ack.sink_id) > 80):
                raise SpeechEmissionUncertain(
                    "Output sink failed to attest exactly the emitted text"
                )
            sink_id = ack.sink_id
            stamp = engineer_time()  # Engineer-only, after confirmed sink write.
            emitted_utc, emitted_bmt_date, emitted_beat = (
                stamp.utc_iso, stamp.bmt_date, stamp.beat
            )
            changed = self._db.execute(
                "UPDATE emissions SET state='acknowledged',sink_id=?,"
                "emitted_utc=?,emitted_bmt_date=?,emitted_beat=? "
                "WHERE delivery_key=? AND state='emitting'",
                (sink_id, emitted_utc, emitted_bmt_date, emitted_beat, key),
            )
            if changed.rowcount != 1:
                raise SpeechEmissionUncertain("Speech acknowledgment lost")
        return SpeechEmissionReceipt(
            key, sink_id, checksum, text, before_tick, before_neural_tick,
            emitted_utc, emitted_bmt_date, emitted_beat,
        )

    def close(self):
        self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
