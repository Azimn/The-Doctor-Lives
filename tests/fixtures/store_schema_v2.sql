-- Historical schema fixture for production migration tests.
-- Exact SCHEMA body extracted from The-Doctor-Lives commit 7be60ed.
-- That commit declared SCHEMA_VERSION = 2.
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
