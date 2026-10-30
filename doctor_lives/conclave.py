"""The Conclave: a bounded, contradiction-preserving interpretive organoid.

Opt-in research code. Uses the SAME BrainStore as Pretorius, never a second
subject, executive, model loop, memory authority, or Laboratory connection.
Interpretations are typed hypotheses, not experiences or verified world facts.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Protocol

from .engineer_time import engineer_time
from .store import BrainStore

VERSION = "conclave.kernel.v1"
KINDS = frozenset({"world_verified", "lived_acquired", "reported", "recalled",
                   "dreamed", "imagined", "divined", "inferred"})
STATES = frozenset({"generated", "noticed", "considered", "adopted", "doubted",
                    "contested", "ignored", "revised", "withdrawn", "dormant"})
CONFLICTS = frozenset({"factual", "doctrinal", "methodological", "symbolic",
                       "opposing_desire", "incommensurable"})
KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")

# Source citations name historical primary works, not an assertion that our
# reconstructed example mappings are a scholar-verified critical edition.
# Method-specific mapping needs independent specialist assessment.
@dataclass(frozen=True, slots=True)
class SpokeSpec:
    tradition_id: str
    version: str
    source_work: str
    semantics: str
    determinism: str = "deterministic-local"
    allowed_side_effects: tuple[str, ...] = ()


SPOKES = (
    SpokeSpec("agrippan-wheel", "1.0", "H. C. Agrippa, De occulta philosophia, Books I-III",
              "Three-level correspondences; claimed sympathy is not a world fact"),
    SpokeSpec("llullian-ars", "1.0", "Ramon Llull, Ars generalis ultima",
              "Constrained combinatorial questions, never proofs"),
    SpokeSpec("brunian-memory", "1.0", "Giordano Bruno, De umbris idearum",
              "Constructed image/locus cues, never rewritten memory"),
    SpokeSpec("ficinian-temperament", "1.0", "Marsilio Ficino, De vita libri tres",
              "Sensory and rhythmic questions, not planetary mood determination"),
    SpokeSpec("geomantic-shield", "1.0", "Traditional geomantic shield method (edition unpinned)",
              "Seeded binary figures and questions, not predictions"),
)
REGISTRY = {entry.tradition_id: entry for entry in SPOKES}

# An interpretive scaffold, not a claimed historical quotation or proof of
# occult correspondences. Unknown links remain UNKNOWN, not freely composed.
ELEMENTAL = {"raven": "air", "bird": "air", "wind": "air",
             "flame": "fire", "fire": "fire", "candle": "fire",
             "river": "water", "rain": "water", "water": "water",
             "stone": "earth", "soil": "earth", "garden": "earth"}
CELESTIAL = {"sun": "sun", "moon": "moon", "saturn": "saturn",
             "venus": "venus", "mars": "mars", "mercury": "mercury",
             "jupiter": "jupiter"}
GEOMANCY_NAMES = {
    (1, 1, 1, 1): "Via", (2, 2, 2, 2): "Populus",
    (1, 2, 2, 2): "Cauda Draconis", (2, 2, 2, 1): "Caput Draconis",
    (1, 1, 2, 2): "Fortuna Minor", (2, 2, 1, 1): "Fortuna Major",
    (1, 2, 1, 2): "Puer", (2, 1, 2, 1): "Puella",
    (1, 2, 2, 1): "Carcer", (2, 1, 1, 2): "Conjunctio",
    (1, 1, 1, 2): "Acquisitio", (2, 1, 1, 1): "Amissio",
    (2, 2, 1, 2): "Laetitia", (2, 1, 2, 2): "Tristitia",
    (1, 1, 2, 1): "Albus", (1, 2, 1, 1): "Rubeus",
}


def _bounded(value: str, label: str, limit: int = 2000) -> str:
    if type(value) is not str or not value.strip() or len(value) > limit:
        raise ValueError(f"{label} must be nonempty bounded text")
    return value.strip()


def _key(value: str, label: str) -> str:
    if type(value) is not str or not KEY.fullmatch(value):
        raise ValueError(f"{label} must be a bounded stable identifier")
    return value


@dataclass(frozen=True, slots=True)
class Stimulus:
    source_event_id: str
    source_kind: str
    context_key: str
    text: str
    # The host must supply only already admitted material. The organoid
    # does not verify arbitrary host claims by introspecting the world.
    def validate(self) -> None:
        _key(self.source_event_id, "source_event_id")
        _key(self.context_key, "context_key")
        if self.source_kind not in KINDS:
            raise ValueError("unknown provenance class")
        _bounded(self.text, "stimulus text")


@dataclass(frozen=True, slots=True)
class Draft:
    proposition_key: str
    proposition: str
    question: str
    claim_scope: str
    memory_cues: tuple[str, ...] = ()
    possible_observations: tuple[str, ...] = ()
    action_suggestions: tuple[str, ...] = ()
    method_trace: str = ""


@dataclass(frozen=True, slots=True)
class Reading:
    id: str
    tradition_id: str
    context_key: str
    proposition_key: str
    proposition: str
    question: str
    claim_scope: str
    source_event_id: str
    source_kind: str
    source_work: str
    state: str
    method_trace: str
    memory_cues: tuple[str, ...]
    possible_observations: tuple[str, ...]
    action_suggestions: tuple[str, ...]
    truth_status: str


class Spoke(Protocol):
    def __call__(self, stimulus: Stimulus) -> Draft | None: ...


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z]+", text.lower()))


def agrippan_wheel(stimulus: Stimulus) -> Draft | None:
    words = set(_tokens(stimulus.text))
    anchor = next((w for w in _tokens(stimulus.text)
                   if w in ELEMENTAL or w in CELESTIAL), None)
    if anchor is None:
        return None
    elemental = ELEMENTAL.get(anchor)
    celestial = CELESTIAL.get(anchor)
    relation = f"elemental:{elemental}" if elemental else f"celestial:{celestial}"
    # The intellectual register and cross-level causal links are deliberately
    # unassigned until a passage-supported edge is explicitly registered.
    return Draft(
        f"correspondence:{anchor}:{relation}",
        f"Can {anchor} be contemplated through {relation} without assuming physical influence?",
        f"What, if anything, would distinguish an analogy concerning {anchor} from causal influence?",
        "symbolic_correspondence",
        (anchor, relation),
        ("Observe recurrence without inferring an external cause",),
        ("Consider an observational comparison; no physical action authorized",),
        f"wheel={relation}; intellectual=unassigned; composed_causal_edge=forbidden; "
        f"unmapped_context_words={len(words - set(ELEMENTAL) - set(CELESTIAL))}",
    )


def llullian_ars(stimulus: Stimulus) -> Draft | None:
    words = _tokens(stimulus.text)
    if not words:
        return None
    key = words[0]
    # The stable relational grid is an experimental abstraction of Ars
    # combinatoria. It does NOT reproduce Llull's exact figures.
    relations = ("difference", "concordance", "possibility", "contrariety")
    slot = int(sha256(stimulus.source_event_id.encode()).hexdigest()[:8], 16) % len(relations)
    rel = relations[slot]
    return Draft(
        f"question:{key}:{rel}",
        f"Under the relation {rel}, what alternative readings of {key} are possible?",
        f"How would a counterexample to a proposed {rel} relation appear?",
        "formal_question",
        (key,),
        ("Seek a discriminating observation rather than treat the combination as proof",),
        (),
        f"ars_grid_v1; topic={key}; relation={rel}; no_theological_inference",
    )


def brunian_memory(stimulus: Stimulus) -> Draft | None:
    words = _tokens(stimulus.text)
    if not words:
        return None
    image = next((w for w in words if len(w) >= 4), words[0])
    locus = int(sha256(stimulus.source_event_id.encode()).hexdigest()[:6], 16) % 12
    return Draft(
        f"mnemonic:{stimulus.source_event_id}:{locus}",
        f"Imagine {image} occupying an unusual place in memory locus {locus}.",
        "Does this constructed image help recall the original source without changing it?",
        "imagined_mnemonic",
        (image, f"locus:{locus}", stimulus.source_event_id),
        ("Compare retrieval with and without the image cue",),
        (),
        f"loci=12; locus={locus}; image={image}; association_only; no_memory_write",
    )


def ficinian_temperament(stimulus: Stimulus) -> Draft | None:
    words = set(_tokens(stimulus.text))
    sensory = words & {"light", "music", "night", "sun", "moon", "air",
                       "sound", "sleep", "garden", "warmth", "cold", "song"}
    if not sensory:
        return None
    signal = sorted(sensory)[0]
    return Draft(
        f"temperament:{signal}",
        f"Could the setting involving {signal} alter felt attention or appetite?",
        f"Is any change associated with {signal} measurable without a planetary explanation?",
        "situated_analogy",
        (signal,),
        ("Compare reported feeling with observed bodily state and mundane controls",),
        ("Offer a neutral comparison to Noesis, not an affect command",),
        f"spiritus_analogy={signal}; no_unverified_astrological_effect",
    )


def _add_figures(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    # Traditional shield-chart parity addition: equal => 2 dots, different => 1.
    return tuple(2 if x == y else 1 for x, y in zip(a, b))


def geomantic_shield(stimulus: Stimulus) -> Draft | None:
    seed = sha256(("geomancy:v1:" + stimulus.source_event_id +
                   ":" + stimulus.context_key).encode()).digest()
    mothers = tuple(tuple(1 + ((seed[i * 4 + j] & 1)) for j in range(4))
                    for i in range(4))
    # Daughters are transposes of mothers; nieces, witnesses, judge follow
    # the orthodox shield structure. No secret knowledge is retrieved.
    daughters = tuple(tuple(mothers[j][i] for j in range(4)) for i in range(4))
    first = mothers + daughters
    nieces = tuple(_add_figures(first[i], first[i + 1]) for i in range(0, 8, 2))
    witness_left = _add_figures(nieces[0], nieces[1])
    witness_right = _add_figures(nieces[2], nieces[3])
    judge = _add_figures(witness_left, witness_right)
    name = GEOMANCY_NAMES.get(judge, "unclassified")
    return Draft(
        f"divinatory:{stimulus.source_event_id}:{stimulus.context_key}",
        f"A seeded shield chart yields the figure {name}; it offers a symbolic question, not an outcome.",
        f"How might {name} change the question being asked, without predicting the world?",
        "divined_symbol",
        (f"geomantic:{name}",),
        ("A matched random-symbol control can test the reading's psychological effect",),
        (),
        f"geomancy:v1; mothers={mothers}; daughters={daughters}; "
        f"nieces={nieces}; witnesses={(witness_left, witness_right)}; judge={judge}; "
        f"seed_sha256={sha256(seed).hexdigest()}",
    )


METHODS: dict[str, Spoke] = {
    "agrippan-wheel": agrippan_wheel,
    "llullian-ars": llullian_ars,
    "brunian-memory": brunian_memory,
    "ficinian-temperament": ficinian_temperament,
    "geomantic-shield": geomantic_shield,
}

# Namespace is in the canonical BrainStore database, not a shadow database.
# Schema is additive, guarded by opt-in initialization, and versioned locally.
_SCHEMA = """
CREATE TABLE IF NOT EXISTS conclave_meta (
  key TEXT PRIMARY KEY, value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS conclave_readings (
  id TEXT PRIMARY KEY, tradition_id TEXT NOT NULL, context_key TEXT NOT NULL,
  proposition_key TEXT NOT NULL, proposition TEXT NOT NULL, question TEXT NOT NULL,
  claim_scope TEXT NOT NULL, source_event_id TEXT NOT NULL,
  source_kind TEXT NOT NULL, source_work TEXT NOT NULL,
  state TEXT NOT NULL, method_trace TEXT NOT NULL,
  memory_cues_json TEXT NOT NULL, observations_json TEXT NOT NULL,
  suggestions_json TEXT NOT NULL, utc_time TEXT NOT NULL,
  beat_time TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS conclave_support (
  reading_id TEXT NOT NULL, evidence_ref TEXT NOT NULL, direction TEXT NOT NULL,
  source_kind TEXT NOT NULL, note TEXT NOT NULL, utc_time TEXT NOT NULL,
  PRIMARY KEY(reading_id, evidence_ref, direction),
  FOREIGN KEY(reading_id) REFERENCES conclave_readings(id)
);
CREATE TABLE IF NOT EXISTS conclave_conflicts (
  reading_a TEXT NOT NULL, reading_b TEXT NOT NULL,
  conflict_type TEXT NOT NULL, context_key TEXT NOT NULL, note TEXT NOT NULL,
  PRIMARY KEY(reading_a, reading_b, conflict_type, context_key),
  FOREIGN KEY(reading_a) REFERENCES conclave_readings(id),
  FOREIGN KEY(reading_b) REFERENCES conclave_readings(id)
);
CREATE TABLE IF NOT EXISTS conclave_transitions (
  reading_id TEXT NOT NULL, revision INTEGER NOT NULL,
  old_state TEXT NOT NULL, new_state TEXT NOT NULL, reason TEXT NOT NULL,
  utc_time TEXT NOT NULL, PRIMARY KEY(reading_id, revision),
  FOREIGN KEY(reading_id) REFERENCES conclave_readings(id)
);
"""


class Conclave:
    """Interpretive methods and persistent disagreement, never an action port."""

    def __init__(self, store: BrainStore, *, enabled: bool = False):
        if not isinstance(store, BrainStore):
            raise TypeError("Conclave must share the canonical BrainStore")
        if enabled is not True:
            raise PermissionError("Conclave must be explicitly enabled by the host")
        self._store = store
        # Keep schema admission scoped to opt-in; do not migrate or replace
        # canonical BrainStore schema version in this research branch.
        with store.transaction() as db:
            for statement in _SCHEMA.split(";"):
                if statement.strip():
                    db.execute(statement)
            row = db.execute("SELECT value FROM conclave_meta WHERE key='version'").fetchone()
            if row and row["value"] != VERSION:
                raise RuntimeError("Unknown Conclave namespace version")
            db.execute("INSERT OR IGNORE INTO conclave_meta(key,value) VALUES('version',?)",
                       (VERSION,))

    def _check_world_receipt(self, event_id: str) -> None:
        # This checks a canonical *record*, not privileged world state.
        with self._store.connect() as db:
            row = db.execute(
                "SELECT external,evidence_class FROM events WHERE id=?", (event_id,)
            ).fetchone()
        if row is None or int(row["external"]) != 1 or row["evidence_class"] in {
            "dreamed", "imagined", "divined", "inferred"
        }:
            raise PermissionError("world_verified requires a recorded external event")

    @staticmethod
    def _truth(db, reading_id: str) -> str:
        evidence = {row[0] for row in db.execute(
            "SELECT DISTINCT direction FROM conclave_support WHERE reading_id=?",
            (reading_id,)
        )}
        if evidence == {"for", "against"}:
            return "both"
        if "for" in evidence:
            return "supported"
        if "against" in evidence:
            return "rejected"
        return "neither"

    @classmethod
    def _reading(cls, db, row) -> Reading:
        return Reading(
            id=row["id"], tradition_id=row["tradition_id"],
            context_key=row["context_key"], proposition_key=row["proposition_key"],
            proposition=row["proposition"], question=row["question"],
            claim_scope=row["claim_scope"], source_event_id=row["source_event_id"],
            source_kind=row["source_kind"], source_work=row["source_work"],
            state=row["state"], method_trace=row["method_trace"],
            memory_cues=tuple(json.loads(row["memory_cues_json"])),
            possible_observations=tuple(json.loads(row["observations_json"])),
            action_suggestions=tuple(json.loads(row["suggestions_json"])),
            truth_status=cls._truth(db, row["id"]),
        )

    def interpret(self, stimulus: Stimulus, *, spokes: tuple[str, ...] | None = None,
                  max_spokes: int = 5) -> tuple[Reading, ...]:
        """Generate bounded, idempotently persisted rival readings; silence is valid.

        Call ONLY from a host that already enforced source admission. No
        subjective experience, first-person memory, or action is generated.
        """
        if not isinstance(stimulus, Stimulus):
            raise TypeError("explicit typed stimulus required")
        stimulus.validate()
        if type(max_spokes) is not int or not 1 <= max_spokes <= len(SPOKES):
            raise ValueError("invalid budget")
        selected = tuple(REGISTRY) if spokes is None else spokes
        if not isinstance(selected, tuple) or len(selected) > max_spokes:
            raise ValueError("spoke budget exceeded")
        if len(set(selected)) != len(selected) or any(s not in METHODS for s in selected):
            raise ValueError("invalid or repeated tradition")
        if stimulus.source_kind == "world_verified":
            self._check_world_receipt(stimulus.source_event_id)
        drafts = [(tid, METHODS[tid](stimulus)) for tid in selected]
        clock = engineer_time()
        with self._store.transaction() as db:
            result = []
            for tid, draft in drafts:
                if draft is None:
                    continue
                payload = "|".join((stimulus.source_event_id, stimulus.context_key,
                                    stimulus.source_kind, stimulus.text, tid))
                reading_id = "conclave:" + sha256(payload.encode()).hexdigest()[:32]
                db.execute(
                    """INSERT OR IGNORE INTO conclave_readings
                    (id,tradition_id,context_key,proposition_key,proposition,question,
                     claim_scope,source_event_id,source_kind,source_work,state,
                     method_trace,memory_cues_json,observations_json,suggestions_json,
                     utc_time,beat_time)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (reading_id, tid, stimulus.context_key, draft.proposition_key,
                     draft.proposition, draft.question, draft.claim_scope,
                     stimulus.source_event_id, stimulus.source_kind,
                     REGISTRY[tid].source_work, "generated", draft.method_trace,
                     json.dumps(draft.memory_cues), json.dumps(draft.possible_observations),
                     json.dumps(draft.action_suggestions), clock.utc_iso, clock.beat),
                )
                row = db.execute("SELECT * FROM conclave_readings WHERE id=?",
                                 (reading_id,)).fetchone()
                result.append(self._reading(db, row))
            return tuple(result)

    def readings(self, context_key: str) -> tuple[Reading, ...]:
        _key(context_key, "context_key")
        with self._store.connect() as db:
            rows = db.execute(
                "SELECT * FROM conclave_readings WHERE context_key=? ORDER BY id",
                (context_key,),
            ).fetchall()
            return tuple(self._reading(db, row) for row in rows)

    def transition(self, reading_id: str, state: str, *, reason: str) -> Reading:
        _key(reading_id, "reading_id")
        if state not in STATES:
            raise ValueError("unknown reading state")
        _bounded(reason, "revision reason", 500)
        with self._store.transaction() as db:
            row = db.execute("SELECT * FROM conclave_readings WHERE id=?",
                             (reading_id,)).fetchone()
            if row is None:
                raise KeyError(reading_id)
            if row["state"] == state:
                return self._reading(db, row)
            rev = int(row["revision"]) + 1
            db.execute("UPDATE conclave_readings SET state=?,revision=? WHERE id=?",
                       (state, rev, reading_id))
            db.execute(
                "INSERT INTO conclave_transitions VALUES(?,?,?,?,?,?)",
                (reading_id, rev, row["state"], state, reason, engineer_time().utc_iso),
            )
            return self._reading(db, db.execute(
                "SELECT * FROM conclave_readings WHERE id=?", (reading_id,)
            ).fetchone())

    def add_support(self, reading_id: str, *, evidence_ref: str,
                    direction: str, source_kind: str, note: str) -> Reading:
        _key(reading_id, "reading_id")
        _key(evidence_ref, "evidence_ref")
        if direction not in {"for", "against"} or source_kind not in KINDS:
            raise ValueError("invalid evidence direction or provenance")
        _bounded(note, "support note", 500)
        if source_kind == "world_verified":
            self._check_world_receipt(evidence_ref)
        with self._store.transaction() as db:
            row = db.execute("SELECT * FROM conclave_readings WHERE id=?",
                             (reading_id,)).fetchone()
            if row is None:
                raise KeyError(reading_id)
            db.execute(
                """INSERT OR IGNORE INTO conclave_support
                (reading_id,evidence_ref,direction,source_kind,note,utc_time)
                VALUES(?,?,?,?,?,?)""",
                (reading_id, evidence_ref, direction, source_kind, note,
                 engineer_time().utc_iso),
            )
            return self._reading(db, row)

    def mark_conflict(self, reading_a: str, reading_b: str, *,
                      conflict_type: str, note: str) -> None:
        for r in (reading_a, reading_b):
            _key(r, "reading id")
        if reading_a == reading_b or conflict_type not in CONFLICTS:
            raise ValueError("two distinct readings and a valid conflict type required")
        _bounded(note, "conflict note", 500)
        a, b = sorted((reading_a, reading_b))
        with self._store.transaction() as db:
            found = db.execute(
                "SELECT id,context_key FROM conclave_readings WHERE id IN (?,?)",
                (a, b),
            ).fetchall()
            if len(found) != 2 or found[0]["context_key"] != found[1]["context_key"]:
                raise ValueError("contradictions require two readings in one context")
            db.execute(
                "INSERT OR IGNORE INTO conclave_conflicts VALUES(?,?,?,?,?)",
                (a, b, conflict_type, found[0]["context_key"], note),
            )

    def conflicts(self, context_key: str) -> tuple[dict, ...]:
        _key(context_key, "context_key")
        with self._store.connect() as db:
            rows = db.execute(
                """SELECT reading_a,reading_b,conflict_type,note
                   FROM conclave_conflicts WHERE context_key=?
                   ORDER BY reading_a,reading_b""", (context_key,)
            ).fetchall()
            return tuple(dict(row) for row in rows)

    def cues(self, context_key: str, *, max_cues: int = 12) -> tuple[str, ...]:
        if type(max_cues) is not int or not 0 <= max_cues <= 24:
            raise ValueError("invalid cue budget")
        # Cues are optional suggestions to Mnemosyne's ordinary retrieval port,
        # never direct edits to memories and never newly lived evidence.
        return tuple(dict.fromkeys(cue for reading in self.readings(context_key)
                                   if reading.state not in {"withdrawn", "ignored"}
                                   for cue in reading.memory_cues))[:max_cues]

    @property
    def source_registry(self) -> tuple[SpokeSpec, ...]:
        return SPOKES
