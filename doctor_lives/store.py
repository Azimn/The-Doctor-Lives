from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 4

WORDING_KINDS = frozenset({"quoted", "paraphrased", "reconstructed", "synthesized"})

AUTOBIOGRAPHICAL_CLASSES = frozenset({
    "canonical_preawakening_memory",
    "reconstructed_preawakening_memory",
    "synthesized_preawakening_memory",
    "lived_runtime_memory",
})


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
CREATE TABLE IF NOT EXISTS policy_decisions (
 id TEXT PRIMARY KEY, tick INTEGER NOT NULL, created_at TEXT NOT NULL,
 trigger TEXT NOT NULL, selected_action TEXT NOT NULL,
 action_scores_json TEXT NOT NULL, candidate_record_ids_json TEXT NOT NULL,
 selected_record_ids_json TEXT NOT NULL, neural_tick INTEGER NOT NULL,
 neural_checkpoint_sha256 TEXT NOT NULL, policy_version TEXT NOT NULL
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
CREATE TABLE IF NOT EXISTS memory_provenance (
 memory_id TEXT PRIMARY KEY, history_key TEXT NOT NULL UNIQUE,
 provenance_json TEXT NOT NULL,
 FOREIGN KEY(memory_id) REFERENCES memories(id)
);
CREATE TABLE IF NOT EXISTS memory_classifications (
 memory_id TEXT PRIMARY KEY,
 autobiographical_class TEXT,
 event_subtype TEXT NOT NULL,
 canon_rank INTEGER,
 continuity TEXT NOT NULL,
 material_category TEXT NOT NULL,
 wording TEXT NOT NULL,
 classification_reasoning_json TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'active',
 predecessor_memory_id TEXT,
 classifier TEXT NOT NULL,
 classified_at TEXT NOT NULL,
 CHECK(canon_rank IS NULL OR (canon_rank >= 0 AND canon_rank <= 5)),
 FOREIGN KEY(memory_id) REFERENCES memories(id)
);
CREATE TABLE IF NOT EXISTS canon_authority (
 rank INTEGER PRIMARY KEY,
 label TEXT NOT NULL,
 description TEXT NOT NULL,
 reserved INTEGER NOT NULL DEFAULT 0,
 CHECK(rank >= 0 AND rank <= 5)
);
CREATE TABLE IF NOT EXISTS synthesis_admissions (
 id TEXT PRIMARY KEY,
 claim_key TEXT NOT NULL UNIQUE,
 memory_id TEXT,
 author TEXT NOT NULL,
 reviewer TEXT NOT NULL,
 proposed_claim TEXT NOT NULL,
 sources_json TEXT NOT NULL,
 reasoning TEXT NOT NULL,
 causal_leverage TEXT NOT NULL,
 evidence_strength TEXT NOT NULL,
 alternatives_json TEXT NOT NULL,
 exclusion_rulings_json TEXT NOT NULL,
 conflict_notes TEXT NOT NULL,
 status TEXT NOT NULL,
 created_at TEXT NOT NULL,
 reviewed_at TEXT,
 retracted_at TEXT,
 retracted_by TEXT,
 retraction_reason TEXT,
 retraction_note TEXT NOT NULL DEFAULT 'Synthesis admission is retractable, not reversible: retraction removes the active memory but cannot undo cognition that already occurred.',
 FOREIGN KEY(memory_id) REFERENCES memories(id)
);
CREATE TABLE IF NOT EXISTS conflict_resolutions (
 id TEXT PRIMARY KEY,
 conflict_key TEXT NOT NULL,
 created_at TEXT NOT NULL,
 candidate_memory_ids_json TEXT NOT NULL,
 candidate_ranks_json TEXT NOT NULL,
 winner_memory_id TEXT NOT NULL,
 rule TEXT NOT NULL,
 rationale TEXT NOT NULL,
 resolution_json TEXT NOT NULL,
 FOREIGN KEY(winner_memory_id) REFERENCES memories(id)
);
CREATE TABLE IF NOT EXISTS source_custody (
 source_key TEXT PRIMARY KEY,
 custody_status TEXT NOT NULL,
 original_author TEXT,
 content_status TEXT NOT NULL,
 canon_rank INTEGER,
 continuity TEXT NOT NULL,
 provenance_json TEXT NOT NULL,
 CHECK(canon_rank IS NULL OR (canon_rank >= 0 AND canon_rank <= 5))
);
CREATE TABLE IF NOT EXISTS withheld_claims (
 claim_key TEXT PRIMARY KEY,
 claim_text TEXT NOT NULL,
 status TEXT NOT NULL,
 reason TEXT NOT NULL,
 source_refs_json TEXT NOT NULL,
 anti_promotion_json TEXT NOT NULL,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reference_material (
 reference_key TEXT PRIMARY KEY,
 label TEXT NOT NULL,
 continuity TEXT NOT NULL,
 canon_rank INTEGER NOT NULL,
 status TEXT NOT NULL,
 provenance_json TEXT NOT NULL,
 CHECK(canon_rank >= 0 AND canon_rank <= 5)
);
CREATE TABLE IF NOT EXISTS retrieval_audits (
 id TEXT PRIMARY KEY,
 tick INTEGER NOT NULL,
 query TEXT NOT NULL,
 config_json TEXT NOT NULL,
 direct_memory_ids_json TEXT NOT NULL,
 activated_memory_ids_json TEXT NOT NULL,
 path_contributions_json TEXT NOT NULL,
 ranked_memory_ids_json TEXT NOT NULL,
 state_digest_before TEXT NOT NULL,
 state_digest_after TEXT NOT NULL,
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS history_nodes (
 node_id TEXT PRIMARY KEY, label TEXT NOT NULL, node_type TEXT NOT NULL,
 activation REAL NOT NULL, memory_id TEXT NOT NULL, provenance_json TEXT NOT NULL,
 FOREIGN KEY(memory_id) REFERENCES memories(id)
);
CREATE TABLE IF NOT EXISTS history_edges (
 edge_id TEXT PRIMARY KEY, source_node_id TEXT NOT NULL, target_node_id TEXT NOT NULL,
 weight REAL NOT NULL, kind TEXT NOT NULL, provenance_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_tick ON events(tick);
CREATE INDEX IF NOT EXISTS idx_memories_active_tick ON memories(active, updated_tick DESC);
CREATE INDEX IF NOT EXISTS idx_thoughts_tick ON thoughts(tick DESC);
CREATE INDEX IF NOT EXISTS idx_concerns_status ON concerns(status, importance DESC);
CREATE INDEX IF NOT EXISTS idx_commitments_status ON commitments(status, importance DESC);
CREATE INDEX IF NOT EXISTS idx_memory_provenance_history_key ON memory_provenance(history_key);
CREATE INDEX IF NOT EXISTS idx_history_edges_source ON history_edges(source_node_id);
CREATE INDEX IF NOT EXISTS idx_history_edges_target ON history_edges(target_node_id);
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

    @staticmethod
    def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
        return {str(row["name"]) for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}

    def _migrate_schema(self, conn: sqlite3.Connection) -> None:
        classification_columns = self._table_columns(conn, "memory_classifications")
        if "wording" not in classification_columns:
            conn.execute(
                "ALTER TABLE memory_classifications ADD COLUMN wording TEXT NOT NULL DEFAULT 'paraphrased'"
            )
            conn.execute(
                """UPDATE memory_classifications SET wording=
                CASE
                  WHEN autobiographical_class='reconstructed_preawakening_memory' THEN 'reconstructed'
                  WHEN autobiographical_class='synthesized_preawakening_memory' THEN 'synthesized'
                  WHEN autobiographical_class='lived_runtime_memory' THEN 'quoted'
                  ELSE 'paraphrased'
                END"""
            )

        admission_columns = self._table_columns(conn, "synthesis_admissions")
        if "retracted_at" not in admission_columns:
            conn.execute("ALTER TABLE synthesis_admissions ADD COLUMN retracted_at TEXT")
        if "retracted_by" not in admission_columns:
            conn.execute("ALTER TABLE synthesis_admissions ADD COLUMN retracted_by TEXT")
        if "retraction_reason" not in admission_columns:
            conn.execute("ALTER TABLE synthesis_admissions ADD COLUMN retraction_reason TEXT")
        if "retraction_note" not in admission_columns:
            conn.execute(
                """ALTER TABLE synthesis_admissions ADD COLUMN retraction_note TEXT NOT NULL
                DEFAULT 'Synthesis admission is retractable, not reversible: retraction removes the active memory but cannot undo cognition that already occurred.'"""
            )

    def init(self) -> None:
        with closing(self.connect()) as conn:
            conn.executescript(SCHEMA)
            self._migrate_schema(conn)
            conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),))
            conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('tick','0')")
            conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('state_version','0')")
            conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('bootstrap_version','')")
            conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('deep_history_version','')")
            conn.execute("UPDATE meta SET value=? WHERE key='schema_version'", (str(SCHEMA_VERSION),))
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
                   source_event_id: str | None = None,
                   classification: dict[str, Any] | None = None,
                   synthesis_admission_id: str | None = None,
                   record_id: str | None = None) -> str:
        if evidence_class in AUTOBIOGRAPHICAL_CLASSES and classification is None:
            raise ValueError(
                f"autobiographical memory {evidence_class!r} requires classification reasoning"
            )
        if evidence_class in {"reconstructed_preawakening_memory", "synthesized_preawakening_memory"}:
            normalized = " ".join(text.strip().lower().split())
            if normalized.startswith(("i remember ", "i recall ", "i witnessed ", "i experienced ")):
                raise ValueError(
                    f"{evidence_class} cannot use unqualified direct-recollection wording"
                )
        if evidence_class == "synthesized_preawakening_memory":
            if not synthesis_admission_id:
                raise ValueError("synthesized memory requires an approved synthesis admission")
            admission = conn.execute(
                "SELECT status,memory_id FROM synthesis_admissions WHERE id=?",
                (synthesis_admission_id,),
            ).fetchone()
            if admission is None or str(admission["status"]) != "approved":
                raise ValueError("synthesis admission is missing or not approved")
            if admission["memory_id"] is not None:
                raise ValueError("synthesis admission is already bound to a memory")

        rid = record_id or new_id("mem")
        conn.execute(
            """INSERT INTO memories
            (id,created_tick,updated_tick,kind,text,source,evidence_class,external,confidence,
             authored,base_salience,tags_json,source_event_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (rid,tick,tick,kind,text.strip(),source,evidence_class,int(bool(external)),clamp(confidence),
             int(bool(authored)),clamp(base_salience),json.dumps(sorted(set(tags))),source_event_id),
        )
        if classification is not None:
            self.set_classification(conn, rid, classification)
        if synthesis_admission_id is not None:
            conn.execute(
                "UPDATE synthesis_admissions SET memory_id=? WHERE id=?",
                (rid, synthesis_admission_id),
            )
        return rid

    def set_classification(self, conn: sqlite3.Connection, memory_id: str,
                           classification: dict[str, Any]) -> None:
        autobiographical_class = classification.get("autobiographical_class")
        if autobiographical_class is not None and autobiographical_class not in AUTOBIOGRAPHICAL_CLASSES:
            raise ValueError(f"unknown autobiographical class {autobiographical_class!r}")
        canon_rank = classification.get("canon_rank")
        if canon_rank is not None and not 0 <= int(canon_rank) <= 5:
            raise ValueError("canon_rank must be between 0 and 5")
        wording = str(classification.get("wording") or "")
        if wording not in WORDING_KINDS:
            raise ValueError(
                "classification wording must be one of: quoted, paraphrased, reconstructed, synthesized"
            )
        if autobiographical_class == "synthesized_preawakening_memory" and wording != "synthesized":
            raise ValueError("synthesized preawakening memory must use synthesized wording")
        reasoning = classification.get("classification_reasoning")
        if not isinstance(reasoning, dict) or not reasoning:
            raise ValueError("classification_reasoning must be a non-empty mapping")
        row = conn.execute(
            "SELECT evidence_class,kind,text FROM memories WHERE id=?", (memory_id,)
        ).fetchone()
        if row is None:
            raise KeyError(memory_id)
        if autobiographical_class in {
            "reconstructed_preawakening_memory", "synthesized_preawakening_memory"
        }:
            normalized = " ".join(str(row["text"]).strip().lower().split())
            if normalized.startswith(("i remember ", "i recall ", "i witnessed ", "i experienced ")):
                raise ValueError(
                    f"{autobiographical_class} cannot use unqualified direct-recollection wording"
                )
        if str(row["evidence_class"]) in AUTOBIOGRAPHICAL_CLASSES:
            if autobiographical_class != str(row["evidence_class"]):
                raise ValueError("memory evidence_class and autobiographical_class disagree")
        conn.execute(
            """INSERT OR REPLACE INTO memory_classifications
            (memory_id,autobiographical_class,event_subtype,canon_rank,continuity,
             material_category,wording,classification_reasoning_json,status,predecessor_memory_id,
             classifier,classified_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                memory_id,
                autobiographical_class,
                str(classification.get("event_subtype") or row["kind"]),
                None if canon_rank is None else int(canon_rank),
                str(classification.get("continuity") or "runtime"),
                str(classification.get("material_category") or (
                    "autobiography" if autobiographical_class else "uncategorized"
                )),
                wording,
                json.dumps(reasoning, sort_keys=True),
                str(classification.get("status") or "active"),
                classification.get("predecessor_memory_id"),
                str(classification.get("classifier") or "doctor_lives"),
                str(classification.get("classified_at") or utc_now()),
            ),
        )

    def classification(self, memory_id: str) -> dict[str, Any] | None:
        with closing(self.connect()) as conn:
            row = conn.execute(
                "SELECT * FROM memory_classifications WHERE memory_id=?", (memory_id,)
            ).fetchone()
        if row is None:
            return None
        out = dict(row)
        out["classification_reasoning"] = json.loads(out.pop("classification_reasoning_json"))
        return out

    def memories_with_classification(self, active_only: bool = True) -> list[dict[str, Any]]:
        sql = """SELECT m.*,c.autobiographical_class,c.event_subtype,c.canon_rank,
                 c.continuity,c.material_category,c.wording,c.classification_reasoning_json,
                 c.status AS classification_status,c.predecessor_memory_id,c.classifier,c.classified_at
                 FROM memories m LEFT JOIN memory_classifications c ON c.memory_id=m.id"""
        if active_only:
            sql += " WHERE m.active=1"
        sql += " ORDER BY m.updated_tick DESC,m.created_tick DESC"
        with closing(self.connect()) as conn:
            rows = conn.execute(sql).fetchall()
        out = []
        for row in rows:
            item = self._decode_memory(row)
            raw_reasoning = item.pop("classification_reasoning_json", None)
            item["classification_reasoning"] = (
                None if raw_reasoning is None else json.loads(raw_reasoning)
            )
            out.append(item)
        return out

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
                          "commitments","self_model","thoughts","policy_decisions","associations","needs","action_values",
                          "sleep_fragments","archive","memory_provenance","memory_classifications",
                          "canon_authority","synthesis_admissions","conflict_resolutions","source_custody","withheld_claims",
                          "reference_material","history_nodes","history_edges"]:
                rows = conn.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
                for row in rows:
                    h.update(table.encode())
                    h.update(json.dumps(dict(row),sort_keys=True,default=str).encode())
        return h.hexdigest()
