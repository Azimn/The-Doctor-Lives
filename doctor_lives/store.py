from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(value)))


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (
 id TEXT PRIMARY KEY, tick INTEGER NOT NULL, created_at TEXT NOT NULL,
 kind TEXT NOT NULL, source TEXT NOT NULL, payload_json TEXT NOT NULL,
 evidence_class TEXT NOT NULL, external INTEGER NOT NULL, confidence REAL NOT NULL,
 parent_id TEXT
);
CREATE TABLE IF NOT EXISTS memories (
 id TEXT PRIMARY KEY, created_tick INTEGER NOT NULL, updated_tick INTEGER NOT NULL,
 kind TEXT NOT NULL, text TEXT NOT NULL, source TEXT NOT NULL,
 evidence_class TEXT NOT NULL, external INTEGER NOT NULL,
 confidence REAL NOT NULL, authored INTEGER NOT NULL,
 base_salience REAL NOT NULL, rehearsal_count INTEGER NOT NULL DEFAULT 0,
 last_rehearsed_tick INTEGER, tags_json TEXT NOT NULL,
 active INTEGER NOT NULL DEFAULT 1, source_event_id TEXT
);
CREATE TABLE IF NOT EXISTS relationships (
 peer_id TEXT PRIMARY KEY, display_name TEXT NOT NULL, updated_tick INTEGER NOT NULL,
 summary TEXT NOT NULL, evidence_json TEXT NOT NULL,
 commitments_json TEXT NOT NULL, unresolved_json TEXT NOT NULL,
 reliability REAL NOT NULL DEFAULT 0.5,
 intellectual_respect REAL NOT NULL DEFAULT 0.5,
 affection REAL NOT NULL DEFAULT 0.0,
 irritation REAL NOT NULL DEFAULT 0.0,
 trust REAL NOT NULL DEFAULT 0.5
);
CREATE TABLE IF NOT EXISTS relationship_events (
 id TEXT PRIMARY KEY, tick INTEGER NOT NULL, peer_id TEXT NOT NULL,
 summary TEXT NOT NULL, valence REAL NOT NULL, reliability_delta REAL NOT NULL,
 trust_delta REAL NOT NULL, source_event_id TEXT,
 FOREIGN KEY(peer_id) REFERENCES relationships(peer_id)
);
CREATE TABLE IF NOT EXISTS concerns (
 id TEXT PRIMARY KEY, created_tick INTEGER NOT NULL, updated_tick INTEGER NOT NULL,
 description TEXT NOT NULL, status TEXT NOT NULL, importance REAL NOT NULL,
 uncertainty REAL NOT NULL, actor TEXT, source TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS commitments (
 id TEXT PRIMARY KEY, created_tick INTEGER NOT NULL, updated_tick INTEGER NOT NULL,
 description TEXT NOT NULL, status TEXT NOT NULL, due_tick INTEGER,
 importance REAL NOT NULL, actor TEXT, source TEXT NOT NULL, outcome TEXT
);
CREATE TABLE IF NOT EXISTS self_model (
 id TEXT PRIMARY KEY, created_tick INTEGER NOT NULL, updated_tick INTEGER NOT NULL,
 claim TEXT NOT NULL, evidence TEXT NOT NULL, confidence REAL NOT NULL,
 status TEXT NOT NULL, source TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS thoughts (
 id TEXT PRIMARY KEY, tick INTEGER NOT NULL, text TEXT NOT NULL,
 trigger TEXT NOT NULL, generated_by TEXT NOT NULL,
 source_record_ids_json TEXT NOT NULL, action_tendencies_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS associations (
 a TEXT NOT NULL, b TEXT NOT NULL, strength REAL NOT NULL,
 updated_tick INTEGER NOT NULL, PRIMARY KEY(a,b)
);
CREATE TABLE IF NOT EXISTS needs (
 key TEXT PRIMARY KEY, actual REAL NOT NULL, felt REAL NOT NULL,
 last_tick INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS action_values (
 action TEXT PRIMARY KEY, value REAL NOT NULL, uses INTEGER NOT NULL DEFAULT 0,
 successes INTEGER NOT NULL DEFAULT 0, updated_tick INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS sleep_fragments (
 id TEXT PRIMARY KEY, tick INTEGER NOT NULL, created_at TEXT NOT NULL,
 trigger TEXT NOT NULL, record_ids_json TEXT NOT NULL, summary TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS archive (
 id TEXT PRIMARY KEY, archived_tick INTEGER NOT NULL, record_id TEXT NOT NULL,
 reason TEXT NOT NULL, record_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_tick ON events(tick);
CREATE INDEX IF NOT EXISTS idx_memories_active_tick ON memories(active, updated_tick DESC);
CREATE INDEX IF NOT EXISTS idx_thoughts_tick ON thoughts(tick DESC);
CREATE INDEX IF NOT EXISTS idx_concerns_status ON concerns(status, importance DESC);
CREATE INDEX IF NOT EXISTS idx_commitments_status ON commitments(status, importance DESC);
"""


class BrainStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.init()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    @contextmanager
    def transaction(self):
        conn = self.connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init(self) -> None:
        with closing(self.connect()) as conn:
            conn.executescript(SCHEMA)
            conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),))
            conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('tick','0')")
            conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('state_version','0')")
            conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('bootstrap_version','')")
            conn.commit()

    def meta(self, key: str, default: str | None = None) -> str | None:
        with closing(self.connect()) as conn:
            row = conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return default if row is None else str(row[0])

    def set_meta(self, key: str, value: Any, conn: sqlite3.Connection | None = None) -> None:
        target = conn if conn is not None else self.connect()
        try:
            target.execute("INSERT OR REPLACE INTO meta(key,value) VALUES(?,?)", (key, str(value)))
            if conn is None:
                target.commit()
        finally:
            if conn is None:
                target.close()

    @property
    def tick(self) -> int:
        return int(self.meta("tick", "0") or 0)

    @property
    def state_version(self) -> int:
        return int(self.meta("state_version", "0") or 0)

    def bump_state_version(self, conn: sqlite3.Connection) -> int:
        row = conn.execute("SELECT value FROM meta WHERE key='state_version'").fetchone()
        version = int(row[0] if row is not None else 0) + 1
        self.set_meta("state_version", version, conn)
        return version

    def advance_tick(self, conn: sqlite3.Connection) -> int:
        tick_row = conn.execute("SELECT value FROM meta WHERE key='tick'").fetchone()
        tick = int(tick_row[0] if tick_row is not None else 0) + 1
        self.set_meta("tick", tick, conn)
        self.bump_state_version(conn)
        return tick

    def event(self, conn: sqlite3.Connection, tick: int, kind: str, source: str,
              payload: dict[str, Any], evidence_class: str, external: bool,
              confidence: float, parent_id: str | None = None) -> str:
        rid = new_id("evt")
        conn.execute(
            """INSERT INTO events
            (id,tick,created_at,kind,source,payload_json,evidence_class,external,confidence,parent_id)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (rid,tick,utc_now(),kind,source,json.dumps(payload,sort_keys=True),evidence_class,
             int(bool(external)),clamp(confidence),parent_id),
        )
        return rid

    def add_memory(self, conn: sqlite3.Connection, tick: int, text: str, source: str,
                   kind: str, evidence_class: str, external: bool, confidence: float,
                   authored: bool, base_salience: float, tags: Iterable[str] = (),
                   source_event_id: str | None = None) -> str:
        rid = new_id("mem")
        conn.execute(
            """INSERT INTO memories
            (id,created_tick,updated_tick,kind,text,source,evidence_class,external,confidence,
             authored,base_salience,tags_json,source_event_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rid,tick,tick,kind,text.strip(),source,evidence_class,int(bool(external)),clamp(confidence),
             int(bool(authored)),clamp(base_salience),json.dumps(sorted(set(tags))),source_event_id),
        )
        return rid

    def memories(self, active_only: bool = True) -> list[dict[str, Any]]:
        sql = "SELECT * FROM memories"
        if active_only:
            sql += " WHERE active=1"
        sql += " ORDER BY updated_tick DESC, created_tick DESC"
        with closing(self.connect()) as conn:
            rows = conn.execute(sql).fetchall()
        return [self._decode_memory(r) for r in rows]

    @staticmethod
    def _decode_memory(row: sqlite3.Row) -> dict[str, Any]:
        d = dict(row)
        d["external"] = bool(d["external"])
        d["authored"] = bool(d["authored"])
        d["active"] = bool(d["active"])
        d["tags"] = json.loads(d.pop("tags_json"))
        return d

    def get_memory(self, record_id: str) -> dict[str, Any] | None:
        with closing(self.connect()) as conn:
            row = conn.execute("SELECT * FROM memories WHERE id=?", (record_id,)).fetchone()
        return None if row is None else self._decode_memory(row)

    def rehearse(self, conn: sqlite3.Connection, record_id: str, tick: int) -> None:
        conn.execute(
            """UPDATE memories SET rehearsal_count=rehearsal_count+1,last_rehearsed_tick=?,updated_tick=?
            WHERE id=? AND active=1""", (tick,tick,record_id)
        )

    def archive_memory(self, conn: sqlite3.Connection, record_id: str, tick: int, reason: str) -> None:
        row = conn.execute("SELECT * FROM memories WHERE id=? AND active=1", (record_id,)).fetchone()
        if row is None:
            return
        payload = self._decode_memory(row)
        conn.execute(
            "INSERT INTO archive(id,archived_tick,record_id,reason,record_json) VALUES(?,?,?,?,?)",
            (new_id("arc"),tick,record_id,reason,json.dumps(payload,sort_keys=True)),
        )
        conn.execute("UPDATE memories SET active=0,updated_tick=? WHERE id=?", (tick,record_id))

    def open_concerns(self) -> list[dict[str, Any]]:
        with closing(self.connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM concerns WHERE status='open' ORDER BY importance DESC,updated_tick DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def open_commitments(self) -> list[dict[str, Any]]:
        with closing(self.connect()) as conn:
            rows = conn.execute(
                "SELECT * FROM commitments WHERE status IN ('open','overdue') ORDER BY importance DESC,updated_tick DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def relationships(self) -> list[dict[str, Any]]:
        with closing(self.connect()) as conn:
            rows = conn.execute("SELECT * FROM relationships ORDER BY updated_tick DESC").fetchall()
        out = []
        for row in rows:
            d = dict(row)
            d["evidence"] = json.loads(d.pop("evidence_json"))
            d["commitments"] = json.loads(d.pop("commitments_json"))
            d["unresolved"] = json.loads(d.pop("unresolved_json"))
            out.append(d)
        return out

    def thoughts(self, limit: int = 20) -> list[dict[str, Any]]:
        with closing(self.connect()) as conn:
            rows = conn.execute("SELECT * FROM thoughts ORDER BY tick DESC LIMIT ?", (limit,)).fetchall()
        out=[]
        for row in rows:
            d=dict(row)
            d["source_record_ids"] = json.loads(d.pop("source_record_ids_json"))
            d["action_tendencies"] = json.loads(d.pop("action_tendencies_json"))
            out.append(d)
        return out

    def digest(self) -> str:
        h = hashlib.sha256()
        with closing(self.connect()) as conn:
            for table in ["meta","events","memories","relationships","relationship_events","concerns",
                          "commitments","self_model","thoughts","associations","needs","action_values",
                          "sleep_fragments","archive"]:
                rows = conn.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
                for row in rows:
                    h.update(table.encode())
                    h.update(json.dumps(dict(row),sort_keys=True,default=str).encode())
        return h.hexdigest()
