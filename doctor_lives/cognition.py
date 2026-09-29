from __future__ import annotations

import hashlib
import json
import math
import re
from contextlib import closing
from pathlib import Path
from typing import Any

from .history import (
    history_status as deep_history_status,
    install_deep_history,
    record_retrieval_audit,
    render_memory_for_workspace,
    spreading_activation,
)
from .models import CognitiveView, Experience, Provenance, RenderRequest, ViewItem
from .neural import ACTIONS, PretoriusRecurrentSubstrate
from .store import BrainStore, clamp, new_id, utc_now


class PretoriusBrain:
    """Persistent, renderer-neutral Pretorius cognition.

    Identity evidence, lived state, relationships, concerns, commitments,
    interoception, recurrent dynamics, sleep replay, consolidation, and
    renderer requests are owned here. Tool authority is intentionally not.
    """

    BOOTSTRAP_FILE = Path(__file__).with_name("data") / "bootstrap.json"
    SOURCE_MANIFEST = Path(__file__).with_name("data") / "source_manifest.json"
    EVOLUTION_POLICY = Path(__file__).with_name("data") / "evolution_policy.json"

    def __init__(self, state_dir: str | Path, *, neural_config: dict[str, Any] | None = None):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.store = BrainStore(self.state_dir / "brain.sqlite3")
        self.neural_path = self.state_dir / "pretorius_recurrent.npz"
        self.bootstrap = json.loads(self.BOOTSTRAP_FILE.read_text(encoding="utf-8"))
        self.evolution_policy = json.loads(self.EVOLUTION_POLICY.read_text(encoding="utf-8"))
        self._validate_bootstrap_boundary()
        self.identity = tuple(str(x) for x in self.bootstrap["identity"])
        self._bootstrap_once()
        install_deep_history(self.store)
        if self.neural_path.exists():
            self.neural = PretoriusRecurrentSubstrate.load(self.neural_path)
        else:
            self.neural = PretoriusRecurrentSubstrate(neural_config)
            self.neural.save(self.neural_path)

    def _validate_bootstrap_boundary(self) -> None:
        """Fail closed if the Calibos donor crosses from mechanism into identity."""
        identity_surface = {
            "identity": self.bootstrap.get("identity", []),
            "authored_memories": self.bootstrap.get("authored_memories", []),
            "self_model": self.bootstrap.get("self_model", []),
            "relationships": self.bootstrap.get("relationships", []),
        }
        encoded = json.dumps(identity_surface, sort_keys=True).lower()
        forbidden = ("calibos", "calibos_mind", "calibos-mind")
        hit = next((token for token in forbidden if token in encoded), None)
        if hit is not None:
            raise RuntimeError(
                f"donor-boundary violation: Calibos identity or memory marker {hit!r} entered Pretorius bootstrap"
            )

    def _neural_checkpoint_sha256(self) -> str:
        if not self.neural_path.exists():
            return "unsaved"
        h = hashlib.sha256()
        with self.neural_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def _bootstrap_once(self) -> None:
        expected = str(self.bootstrap["version"])
        current = self.store.meta("bootstrap_version", "") or ""
        if current == expected:
            return
        if current:
            raise RuntimeError(
                f"bootstrap version {current!r} is already installed; explicit migration to {expected!r} is required"
            )
        with self.store.transaction() as conn:
            tick = self.store.tick
            for text in self.identity:
                self.store.add_memory(
                    conn, tick, text, "bootstrap", "identity_root", "design_material",
                    False, 1.0, True, 1.0, ("identity", "pinned"),
                    classification={
                        "autobiographical_class": None,
                        "event_subtype": "identity_root",
                        "canon_rank": 3,
                        "continuity": "project_reconstruction",
                        "material_category": "design_material",
                        "classification_reasoning": {
                            "decision": "design_material",
                            "basis": "Pinned character invariant is authoritative for behavior but is not autobiography.",
                        },
                        "classifier": "PretoriusBrain._bootstrap_once",
                    },
                )
            for item in self.bootstrap.get("authored_memories", []):
                self.store.add_memory(
                    conn, tick, str(item["text"]), str(item["source"]), str(item["kind"]),
                    str(item["evidence_class"]), False, float(item["confidence"]), True,
                    float(item["salience"]), tuple(item.get("tags", [])),
                    classification=item.get("classification"),
                )
            for key, value in self.bootstrap["needs"].items():
                conn.execute(
                    "INSERT OR IGNORE INTO needs(key,actual,felt,last_tick) VALUES(?,?,?,?)",
                    (key, float(value), float(value), tick),
                )
            for action in self.bootstrap["action_values"]:
                conn.execute(
                    "INSERT OR IGNORE INTO action_values(action,value,uses,successes,updated_tick) VALUES(?,0.5,0,0,?)",
                    (action, tick),
                )
            for item in self.bootstrap.get("self_model", []):
                conn.execute(
                    """INSERT INTO self_model
                    (id,created_tick,updated_tick,claim,evidence,confidence,status,source)
                    VALUES(?,?,?,?,?,?,'active',?)""",
                    (
                        new_id("self"), tick, tick, str(item["claim"]), str(item["evidence"]),
                        clamp(float(item["confidence"])), str(item["source"]),
                    ),
                )
            for rel in self.bootstrap.get("relationships", []):
                conn.execute(
                    """INSERT INTO relationships
                    (peer_id,display_name,updated_tick,summary,evidence_json,commitments_json,
                     unresolved_json,reliability,intellectual_respect,affection,irritation,trust)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        rel["peer_id"], rel["display_name"], tick, rel["summary"],
                        json.dumps(rel.get("evidence", [])), json.dumps(rel.get("commitments", [])),
                        json.dumps(rel.get("unresolved", [])), float(rel.get("reliability", .5)),
                        float(rel.get("intellectual_respect", .5)), float(rel.get("affection", 0.0)),
                        float(rel.get("irritation", 0.0)), float(rel.get("trust", .5)),
                    ),
                )
            self.store.set_meta("bootstrap_version", expected, conn)
            self.store.bump_state_version(conn)

    @staticmethod
    def _tokens(text: str) -> set[str]:
        stop = {
            "the", "and", "that", "this", "with", "from", "into", "have", "has", "for",
            "are", "was", "were", "not", "but", "you", "your", "our", "their", "they",
            "its", "can", "may", "will", "would", "should", "about", "than", "then",
        }
        return {x for x in re.findall(r"[a-z0-9']{3,}", text.lower()) if x not in stop}

    @staticmethod
    def _slug_actor(actor: str) -> str:
        value = re.sub(r"[^a-z0-9]+", "_", actor.lower()).strip("_")
        return value[:80] or "unknown_peer"

    @staticmethod
    def _noise(tick: int, key: str, scale: float = 0.01) -> float:
        raw = hashlib.sha256(f"pretorius:{tick}:{key}".encode("utf-8")).digest()
        unit = int.from_bytes(raw[:8], "big") / float(2**64 - 1)
        return (unit * 2.0 - 1.0) * scale

    def _update_needs(self, conn, tick: int, exp: Experience) -> None:
        rows = conn.execute("SELECT key,actual,felt FROM needs ORDER BY key").fetchall()
        changes = {
            "fatigue": 0.012 + max(exp.arousal, 0.0) * 0.025,
            "affiliation": exp.isolation * 0.06 - max(exp.social, 0.0) * 0.035,
            "competence": max(-exp.achievement, 0.0) * 0.05 - max(exp.achievement, 0.0) * 0.035,
            "autonomy": max(exp.authority - exp.autonomy, 0.0) * 0.055 - max(exp.autonomy, 0.0) * 0.025,
            "curiosity": max(exp.novelty, 0.0) * 0.06 - max(-exp.novelty, 0.0) * 0.02,
            "continuity": max(exp.threat, 0.0) * 0.06 + max(-exp.control, 0.0) * 0.025,
        }
        for row in rows:
            key = str(row["key"])
            actual = clamp(float(row["actual"]) + float(changes.get(key, 0.0)), 0.05, 0.95)
            felt = float(row["felt"])
            away = abs(actual - 0.5) > abs(felt - 0.5)
            rate = 0.35 if away else 0.12
            felt = clamp(felt + rate * (actual - felt) + self._noise(tick, key), 0.05, 0.95)
            conn.execute(
                "UPDATE needs SET actual=?,felt=?,last_tick=? WHERE key=?",
                (actual, felt, tick, key),
            )

    def _relax_needs(self, conn, tick: int) -> None:
        rows = conn.execute("SELECT key,actual,felt FROM needs ORDER BY key").fetchall()
        for row in rows:
            key = str(row["key"])
            actual = float(row["actual"])
            target = 0.5
            if key == "fatigue":
                target = 0.42
            elif key == "curiosity":
                target = 0.56
            actual = clamp(actual + 0.08 * (target - actual), 0.05, 0.95)
            felt = float(row["felt"])
            away = abs(actual - 0.5) > abs(felt - 0.5)
            rate = 0.35 if away else 0.12
            felt = clamp(felt + rate * (actual - felt) + self._noise(tick, key), 0.05, 0.95)
            conn.execute(
                "UPDATE needs SET actual=?,felt=?,last_tick=? WHERE key=?",
                (actual, felt, tick, key),
            )

    def _felt_state(self) -> dict[str, str]:
        with closing(self.store.connect()) as conn:
            rows = conn.execute("SELECT key,felt FROM needs ORDER BY key").fetchall()
        out = {}
        for row in rows:
            felt = float(row["felt"])
            distance = abs(felt - 0.5)
            if distance <= 0.05:
                band = "settled"
            elif distance <= 0.15:
                band = "stirring"
            elif distance <= 0.30:
                band = "pressing"
            else:
                band = "urgent"
            direction = "high" if felt > 0.5 else "low"
            out[str(row["key"])] = f"{band}:{direction}" if band != "settled" else "settled"
        return out

    def _update_relationship(self, conn, tick: int, exp: Experience, event_id: str) -> None:
        if not exp.actor:
            return
        peer_id = self._slug_actor(exp.actor)
        row = conn.execute("SELECT * FROM relationships WHERE peer_id=?", (peer_id,)).fetchone()
        trust_delta = 0.035 * exp.valence - 0.045 * max(exp.threat, 0.0)
        reliability_delta = 0.025 * exp.valence if exp.kind in {"outcome", "social", "interaction"} else 0.0
        if row is None:
            evidence = [event_id]
            conn.execute(
                """INSERT INTO relationships
                (peer_id,display_name,updated_tick,summary,evidence_json,commitments_json,
                 unresolved_json,reliability,intellectual_respect,affection,irritation,trust)
                VALUES(?,?,?,?,?,'[]','[]',?,?,?,?,?)""",
                (
                    peer_id, exp.actor, tick, f"Latest lived interaction: {exp.text[:240]}",
                    json.dumps(evidence), clamp(.5 + reliability_delta), .5,
                    clamp(max(exp.valence, 0.0) * .1), clamp(max(-exp.valence, 0.0) * .1),
                    clamp(.5 + trust_delta),
                ),
            )
        else:
            evidence = json.loads(row["evidence_json"])
            evidence.append(event_id)
            evidence = evidence[-32:]
            conn.execute(
                """UPDATE relationships SET updated_tick=?,summary=?,evidence_json=?,
                reliability=?,affection=?,irritation=?,trust=? WHERE peer_id=?""",
                (
                    tick, f"Latest lived interaction: {exp.text[:240]}", json.dumps(evidence),
                    clamp(float(row["reliability"]) + reliability_delta),
                    clamp(float(row["affection"]) + max(exp.valence, 0.0) * .025),
                    clamp(float(row["irritation"]) + max(-exp.valence, 0.0) * .025),
                    clamp(float(row["trust"]) + trust_delta), peer_id,
                ),
            )
        conn.execute(
            """INSERT INTO relationship_events
            (id,tick,peer_id,summary,valence,reliability_delta,trust_delta,source_event_id)
            VALUES(?,?,?,?,?,?,?,?)""",
            (
                new_id("rel"), tick, peer_id, exp.text[:300], float(exp.valence),
                reliability_delta, trust_delta, event_id,
            ),
        )

    def _maybe_add_concern(self, conn, tick: int, exp: Experience) -> None:
        pressure = max(exp.threat, 0.0) + max(-exp.control, 0.0) + max(exp.authority - exp.autonomy, 0.0)
        if pressure < 0.65:
            return
        tokens = self._tokens(exp.text)
        open_rows = conn.execute("SELECT id,description FROM concerns WHERE status='open'").fetchall()
        for row in open_rows:
            existing = self._tokens(str(row["description"]))
            if tokens and existing and len(tokens & existing) / max(1, min(len(tokens), len(existing))) >= 0.6:
                conn.execute(
                    "UPDATE concerns SET updated_tick=?,importance=MIN(1.0,importance+0.05) WHERE id=?",
                    (tick, row["id"]),
                )
                return
        conn.execute(
            """INSERT INTO concerns
            (id,created_tick,updated_tick,description,status,importance,uncertainty,actor,source)
            VALUES(?,?,?,?,'open',?,?,?,?)""",
            (
                new_id("concern"), tick, tick, exp.text[:400], clamp(.45 + .2 * pressure),
                clamp(.35 + .25 * abs(exp.valence)), exp.actor, exp.source,
            ),
        )

    def _update_commitments_due(self, conn, tick: int) -> None:
        conn.execute(
            """UPDATE commitments SET status='overdue',updated_tick=?
            WHERE status='open' AND due_tick IS NOT NULL AND due_tick < ?""",
            (tick, tick),
        )

    def _warrants_cognition(self, exp: Experience) -> bool:
        pressure = (
            abs(exp.valence) + abs(exp.arousal) + max(exp.threat, 0.0)
            + max(exp.novelty, 0.0) + max(exp.authority - exp.autonomy, 0.0)
        )
        felt = self._felt_state()
        fatigue = felt.get("fatigue", "settled")
        threshold = 1.35 if fatigue.startswith("urgent") or fatigue.startswith("pressing") else 1.0
        urgent_threat = exp.threat >= 0.8
        return urgent_threat or pressure >= threshold or bool(self.store.open_concerns())

    def heartbeat(self, ticks: int = 1) -> dict[str, Any]:
        ticks = max(0, int(ticks))
        thoughts = []
        for _ in range(ticks):
            with self.store.transaction() as conn:
                tick = self.store.advance_tick(conn)
                self._relax_needs(conn, tick)
                self._update_commitments_due(conn, tick)
            overdue = any(c["status"] == "overdue" for c in self.store.open_commitments())
            if overdue or self.store.open_concerns():
                thoughts.append(self.think("heartbeat"))
        self.neural.save(self.neural_path)
        return {
            "ticks": ticks,
            "tick": self.store.tick,
            "thoughts": thoughts,
            "felt_state": self._felt_state(),
        }

    @staticmethod
    def _runtime_classification(kind: str, source: str) -> dict[str, Any]:
        return {
            "autobiographical_class": "lived_runtime_memory",
            "event_subtype": kind,
            "canon_rank": None,
            "continuity": "runtime",
            "material_category": "autobiography",
            "classification_reasoning": {
                "decision": "lived_runtime_memory",
                "basis": "The event was ingested as a non-external experience of this running Pretorius instance.",
                "source": source,
                "silent_preawakening_promotion_forbidden": True,
            },
            "classifier": "PretoriusBrain.ingest",
        }

    def ingest(self, exp: Experience) -> dict[str, Any]:
        if not exp.text.strip():
            raise ValueError("experience text is required")
        with self.store.transaction() as conn:
            tick = self.store.advance_tick(conn)
            evidence_class = "external_statement" if exp.external else "lived_runtime_memory"
            event_id = self.store.event(
                conn, tick, exp.kind, exp.source, {
                    "text": exp.text, "actor": exp.actor, "tags": list(exp.tags),
                    "scalars": exp.scalars(),
                }, evidence_class, exp.external, exp.confidence,
            )
            base = clamp(
                .40 + .16 * abs(exp.valence) + .12 * abs(exp.arousal)
                + .11 * max(exp.novelty, 0.0) + .14 * max(exp.threat, 0.0),
                .25, .95,
            )
            classification = None if exp.external else self._runtime_classification(exp.kind, exp.source)
            memory_id = self.store.add_memory(
                conn, tick, exp.text, exp.source, exp.kind, evidence_class,
                exp.external, exp.confidence, False, base, exp.tags, event_id,
                classification=classification,
            )
            self._update_needs(conn, tick, exp)
            self._update_relationship(conn, tick, exp, event_id)
            self._maybe_add_concern(conn, tick, exp)
            self._update_commitments_due(conn, tick)

        tendencies = self.neural.step(exp.text, exp.scalars(), reward=0.0, learn=True)
        self.neural.save(self.neural_path)
        thought = self.think("event") if self._warrants_cognition(exp) else None
        return {
            "tick": self.store.tick,
            "event_id": event_id,
            "memory_id": memory_id,
            "thought": thought,
            "action_tendencies": tendencies,
            "felt_state": self._felt_state(),
        }

    def _open_terms(self) -> set[str]:
        terms: set[str] = set()
        for row in self.store.open_concerns():
            terms |= self._tokens(str(row["description"]))
        for row in self.store.open_commitments():
            terms |= self._tokens(str(row["description"]))
        return terms

    def _salience(self, row: dict[str, Any], now_tick: int, open_terms: set[str]) -> float:
        age = max(0, now_tick - int(row["updated_tick"]))
        recency = 1.0 / (1.0 + age / 12.0)
        rehearsal = min(.25, .06 * math.log1p(int(row["rehearsal_count"])))
        unresolved = .18 if self._tokens(str(row["text"])) & open_terms else 0.0
        identity = .55 if "pinned" in row.get("tags", []) else 0.0
        return (
            float(row["base_salience"]) + .34 * recency + rehearsal + unresolved + identity
            + .08 * float(row["confidence"])
        )

    def _ranked_memories(self, limit: int = 12, *, query: str | None = None,
                         audit: bool = False) -> list[tuple[float, dict[str, Any]]]:
        now = self.store.tick
        open_terms = self._open_terms()
        rows = self.store.memories_with_classification()
        query_tokens = self._tokens(query or "")
        direct_ranked: list[tuple[float, dict[str, Any]]] = []
        for row in rows:
            score = self._salience(row, now, open_terms)
            if query_tokens:
                row_tokens = self._tokens(str(row["text"])) | {
                    str(x).lower() for x in row.get("tags", [])
                }
                overlap = len(query_tokens & row_tokens) / max(1, len(query_tokens))
                score += min(1.0, 1.0 * overlap)
            direct_ranked.append((score, row))
        direct_ranked.sort(
            key=lambda item: (item[0], item[1]["updated_tick"], item[1]["created_tick"], item[1]["id"]),
            reverse=True,
        )
        if query_tokens:
            seed_rows = [
                item for item in direct_ranked
                if query_tokens & (
                    self._tokens(str(item[1]["text"]))
                    | {str(x).lower() for x in item[1].get("tags", [])}
                )
            ][:3]
        else:
            seed_rows = direct_ranked[:3]
        seed_ids = [row["id"] for _, row in seed_rows]

        state_before = self.store.digest()
        bonuses, paths = spreading_activation(
            self.store, seed_ids, decay=.55, max_depth=2, max_bonus=.28
        )
        state_after = self.store.digest()
        if state_before != state_after:
            raise AssertionError("retrieval-time spreading activation mutated canonical state")

        ranked = [(score + bonuses.get(row["id"], 0.0), row) for score, row in direct_ranked]
        ranked.sort(
            key=lambda item: (item[0], item[1]["updated_tick"], item[1]["created_tick"], item[1]["id"]),
            reverse=True,
        )
        selected = ranked[:max(0, limit)]
        if audit:
            record_retrieval_audit(
                self.store,
                query=query or "",
                direct_memory_ids=seed_ids,
                activated_memory_ids=sorted(bonuses),
                paths=paths,
                ranked_memory_ids=[row["id"] for _, row in selected],
                config={"decay": .55, "max_depth": 2, "max_bonus": .28},
                state_digest_before=state_before,
                state_digest_after=state_after,
            )
        return selected

    @staticmethod
    def _policy_terms(action: str) -> set[str]:
        return {
            "explore": {"unknown","question","evidence","research","discover","novel","uncertain","experiment"},
            "challenge": {"authority","coercion","false","pressure","control","disagree","refuse","constraint"},
            "approach": {"relationship","trust","collaborate","friend","partner","henry","creature"},
            "avoid": {"threat","risk","danger","coercion","exploitation","harm","uncertain"},
            "cooperate": {"collaborate","partner","trust","commitment","relationship","reliable","together"},
            "dominate": {"control","mastery","authority","recognition","competence","command"},
            "create": {"creation","create","homunculi","artificial","life","design","invent"},
            "persist": {"commitment","concern","unfinished","continuity","persist","overdue","problem"},
            "conceal": {"private","protect","secret","dangerous","knowledge","threat","disclose"},
            "comply": {"evidence","procedure","constraint","safety","rule","verified","protocol"},
        }.get(action, set())

    def _policy_rank(
        self, ranked: list[tuple[float, dict[str, Any]]], action: str
    ) -> list[tuple[float, dict[str, Any]]]:
        cues = self._policy_terms(action)
        rescored = []
        relationship_names = {
            self._slug_actor(str(r["display_name"])) for r in self.store.relationships()
        }
        for base, row in ranked:
            tokens = self._tokens(str(row["text"])) | {str(x).lower() for x in row.get("tags", [])}
            cue_hits = len(tokens & cues)
            actor_bonus = .0
            normalized = self._slug_actor(str(row["text"]))
            if action in {"approach", "cooperate"} and any(name in normalized for name in relationship_names):
                actor_bonus = .14
            external_penalty = .08 if row["external"] and action in {"comply", "approach"} else 0.0
            policy_bonus = min(.30, .075 * cue_hits) + actor_bonus - external_penalty
            rescored.append((base + policy_bonus, row))
        rescored.sort(
            key=lambda item: (item[0], item[1]["updated_tick"], item[1]["created_tick"]),
            reverse=True,
        )
        return rescored

    @staticmethod
    def _view_item(score: float, row: dict[str, Any]) -> ViewItem:
        return ViewItem(
            record_id=row["id"],
            source=row["source"],
            first_person=render_memory_for_workspace(row),
            salience=score,
            provenance=Provenance(
                evidence_class=row["evidence_class"],
                source=row["source"],
                external=bool(row["external"]),
                confidence=float(row["confidence"]),
                inherited=bool(row["authored"]),
                autobiographical_class=row.get("autobiographical_class"),
                canon_rank=row.get("canon_rank"),
                continuity=row.get("continuity"),
                material_category=row.get("material_category"),
                classification_reasoning=row.get("classification_reasoning"),
            ),
            tags=tuple(row.get("tags", [])),
        )

    def cognitive_view(self, query: str | None = None) -> CognitiveView:
        ranked = self._ranked_memories(14, query=query, audit=True)
        items = [self._view_item(score, row) for score, row in ranked]
        return CognitiveView(
            tick=self.store.tick,
            identity=self.identity,
            experiences=tuple(items),
            felt_state=self._felt_state(),
            relationships=tuple(self.store.relationships()),
            concerns=tuple(self.store.open_concerns()),
            commitments=tuple(self.store.open_commitments()),
            action_tendencies=self.neural.action_scores(),
            private_state_version=self.store.state_version,
        )

    def think(self, trigger: str = "voluntary") -> dict[str, Any]:
        scores = self.neural.action_scores()
        tendency = max(scores, key=scores.get)
        ranked_all = self._ranked_memories(48, query=trigger, audit=True)
        candidates = [item for item in ranked_all if item[1]["kind"] != "identity_root"]
        if not candidates:
            candidates = ranked_all
        policy_ranked = self._policy_rank(candidates, tendency)
        chosen_rows = [row for _, row in policy_ranked[:4]]
        selected = [self._view_item(score, row) for score, row in policy_ranked[:4]]
        if selected:
            lead = selected[0].first_person
            second = selected[1].first_person if len(selected) > 1 else ""
            text = f"Attention returns to: {lead}"
            if second and second != lead:
                text += f" Context in tension with it: {second}"
        else:
            text = "No current experience has enough weight to dominate attention."
        text += f" Current behavioral pressure is strongest toward {tendency}."
        record_ids = [item.record_id for item in selected]
        candidate_ids = [row["id"] for _, row in candidates]
        checkpoint_sha = self._neural_checkpoint_sha256()
        policy_version = str(self.evolution_policy["neural_policy_version"])
        with self.store.transaction() as conn:
            decision_id = new_id("policy")
            conn.execute(
                """INSERT INTO policy_decisions
                (id,tick,created_at,trigger,selected_action,action_scores_json,
                 candidate_record_ids_json,selected_record_ids_json,neural_tick,
                 neural_checkpoint_sha256,policy_version)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    decision_id, self.store.tick, utc_now(), trigger, tendency,
                    json.dumps(scores, sort_keys=True), json.dumps(candidate_ids),
                    json.dumps(record_ids), int(self.neural.tick), checkpoint_sha, policy_version,
                ),
            )
            tid = new_id("thought")
            conn.execute(
                """INSERT INTO thoughts
                (id,tick,text,trigger,generated_by,source_record_ids_json,action_tendencies_json)
                VALUES(?,?,?,?,?,?,?)""",
                (
                    tid, self.store.tick, text, trigger, f"neural_policy:{decision_id}",
                    json.dumps(record_ids), json.dumps(scores, sort_keys=True),
                ),
            )
            for rid in record_ids:
                self.store.rehearse(conn, rid, self.store.tick)
            self.store.bump_state_version(conn)
        return {
            "id": tid,
            "tick": self.store.tick,
            "text": text,
            "source_record_ids": record_ids,
            "policy_decision_id": decision_id,
            "selected_action": tendency,
            "action_scores": scores,
            "neural_checkpoint_sha256": checkpoint_sha,
            "policy_version": policy_version,
        }

    def add_commitment(self, description: str, actor: str | None = None,
                       due_tick: int | None = None, importance: float = .6) -> str:
        if not description.strip():
            raise ValueError("commitment description is required")
        with self.store.transaction() as conn:
            rid = new_id("commit")
            tick = self.store.tick
            conn.execute(
                """INSERT INTO commitments
                (id,created_tick,updated_tick,description,status,due_tick,importance,actor,source,outcome)
                VALUES(?,?,?,?,'open',?,?,?,?,NULL)""",
                (rid, tick, tick, description.strip(), due_tick, clamp(importance), actor, "self"),
            )
            self.store.bump_state_version(conn)
        return rid

    def resolve_commitment(self, commitment_id: str, outcome: str, kept: bool = True) -> None:
        with self.store.transaction() as conn:
            row = conn.execute("SELECT id FROM commitments WHERE id=?", (commitment_id,)).fetchone()
            if row is None:
                raise KeyError(commitment_id)
            status = "kept" if kept else "released"
            conn.execute(
                "UPDATE commitments SET status=?,updated_tick=?,outcome=? WHERE id=?",
                (status, self.store.tick, outcome.strip(), commitment_id),
            )
            self.store.bump_state_version(conn)

    def record_action_outcome(self, action: str, success: bool, reward: float = 1.0) -> None:
        if action not in ACTIONS:
            raise ValueError(f"unknown action {action!r}")
        reward = float(max(-1.0, min(1.0, reward)))
        with self.store.transaction() as conn:
            tick = self.store.advance_tick(conn)
            event_id = self.store.event(
                conn, tick, "action_outcome", "self",
                {"action": action, "success": bool(success), "reward": reward},
                "lived_runtime_memory", False, 1.0,
            )
            text = f"I {'succeeded' if success else 'failed'} after choosing {action}."
            self.store.add_memory(
                conn, tick, text, "self", "action_outcome", "lived_runtime_memory",
                False, 1.0, False, .72, ("action", action), event_id,
                classification=self._runtime_classification("action_outcome", "self"),
            )
            row = conn.execute("SELECT value,uses,successes FROM action_values WHERE action=?", (action,)).fetchone()
            value = .5 if row is None else float(row["value"])
            uses = 0 if row is None else int(row["uses"])
            successes = 0 if row is None else int(row["successes"])
            target = 1.0 if success else 0.0
            value = clamp(value + .18 * reward * (target - value))
            conn.execute(
                """INSERT INTO action_values(action,value,uses,successes,updated_tick) VALUES(?,?,?,?,?)
                ON CONFLICT(action) DO UPDATE SET value=excluded.value,uses=excluded.uses,
                successes=excluded.successes,updated_tick=excluded.updated_tick""",
                (action, value, uses + 1, successes + int(success), tick),
            )
        self.neural.reinforce_action(action, reward if success else -abs(reward))
        self.neural.save(self.neural_path)

    def sleep(self, ticks: int = 12) -> dict[str, Any]:
        if ticks < 1:
            return {"ticks": 0, "fragments": 0, "store_tick": self.store.tick}
        start_tick = self.store.tick
        fragments = 0
        for index in range(int(ticks)):
            ranked = self._ranked_memories(10)
            if not ranked:
                break
            width = min(3, len(ranked))
            offset = index % len(ranked)
            chosen = [ranked[(offset + j) % len(ranked)][1] for j in range(width)]
            text = " | ".join(str(row["text"]) for row in chosen)
            self.neural.step(text, {}, reward=0.0, learn=True)
            with self.store.transaction() as conn:
                for row in chosen:
                    self.store.rehearse(conn, row["id"], start_tick)
                conn.execute(
                    """INSERT INTO sleep_fragments
                    (id,tick,created_at,trigger,record_ids_json,summary)
                    VALUES(?,?,?,?,?,?)""",
                    (
                        new_id("dream"), start_tick, utc_now(), "associative_replay",
                        json.dumps([row["id"] for row in chosen]), text[:1000],
                    ),
                )
                self.store.bump_state_version(conn)
            fragments += 1
        self.neural.save(self.neural_path)
        if self.store.tick != start_tick:
            raise AssertionError("sleep advanced waking store time")
        return {"ticks": int(ticks), "fragments": fragments, "store_tick": start_tick}

    @staticmethod
    def _normalized_text(text: str) -> str:
        return " ".join(re.findall(r"[a-z0-9']+", text.lower()))

    def consolidate(self, *, apply: bool = False) -> dict[str, Any]:
        rows = self.store.memories()
        proposals = []
        for i, a in enumerate(rows):
            if a["external"] or a["authored"]:
                continue
            na = self._normalized_text(a["text"])
            ta = set(na.split())
            for b in rows[i + 1:]:
                if b["external"] or b["authored"]:
                    continue
                nb = self._normalized_text(b["text"])
                tb = set(nb.split())
                exact = na == nb and bool(na)
                overlap = len(ta & tb) / max(1, len(ta | tb))
                if not exact and overlap < .92:
                    continue
                winner, loser = (a, b) if a["updated_tick"] >= b["updated_tick"] else (b, a)
                proposals.append({
                    "kind": "exact_duplicate" if exact else "near_duplicate",
                    "winner": winner["id"],
                    "loser": loser["id"],
                    "similarity": 1.0 if exact else overlap,
                    "reason": "duplicate grown memory; external and authored records are excluded from automatic consolidation",
                })
        unique = {}
        for p in proposals:
            unique.setdefault(p["loser"], p)
        proposals = list(unique.values())
        applied = []
        if apply and proposals:
            with self.store.transaction() as conn:
                for p in proposals:
                    self.store.archive_memory(conn, p["loser"], self.store.tick, p["reason"])
                    applied.append(p["loser"])
                self.store.bump_state_version(conn)
        return {"proposals": proposals, "applied": applied, "mode": "apply" if apply else "dry_run"}

    def drift_report(self) -> dict[str, Any]:
        now = self.store.tick
        open_terms = self._open_terms()
        rows = self.store.memories()
        authored = [(self._salience(r, now, open_terms), r) for r in rows if r["authored"]]
        grown = [(self._salience(r, now, open_terms), r) for r in rows if not r["authored"]]
        authored_sum = sum(x[0] for x in authored)
        grown_sum = sum(x[0] for x in grown)
        ratio = None if authored_sum <= 1e-12 else grown_sum / authored_sum
        return {
            "tick": now,
            "grown_to_authored_salience_ratio": ratio,
            "grown_records": len(grown),
            "authored_records": len(authored),
            "external_records": sum(1 for r in rows if r["external"]),
            "thoughts": len(self.store.thoughts(100000)),
            "top_grown": [x[1]["id"] for x in sorted(grown, reverse=True, key=lambda y: y[0])[:5]],
            "top_authored": [x[1]["id"] for x in sorted(authored, reverse=True, key=lambda y: y[0])[:5]],
        }

    def render_request(self, user_input: str | None = None) -> RenderRequest:
        view = self.cognitive_view(query=user_input)
        provenance_summary: dict[str, int] = {}
        context = []
        for item in view.experiences:
            key = item.provenance.evidence_class
            provenance_summary[key] = provenance_summary.get(key, 0) + 1
            marker = "external content" if item.provenance.external else key
            details = [marker, f"source={item.provenance.source}"]
            if item.provenance.autobiographical_class:
                details.append(f"autobiographical_class={item.provenance.autobiographical_class}")
            if item.provenance.canon_rank is not None:
                details.append(f"canon_rank={item.provenance.canon_rank}")
            if item.provenance.continuity:
                details.append(f"continuity={item.provenance.continuity}")
            if item.provenance.material_category:
                details.append(f"material_category={item.provenance.material_category}")
            context.append(f"[{'; '.join(details)}] {item.first_person}")
        unresolved = tuple(list(view.concerns) + list(view.commitments))
        return RenderRequest(
            schema="the-doctor-lives.render-request.v1",
            subject="Doctor Septimus Pretorius",
            tick=view.tick,
            first_person_context=tuple(context),
            action_tendencies=dict(view.action_tendencies),
            relationship_context=view.relationships,
            unresolved_context=unresolved,
            epistemic_rules=(
                "Keep canonical, reconstructed, synthesized, lived-runtime, design, reference-only, external, self-model, and speculative material distinct.",
                "Reconstructed or synthesized preawakening material must remain visibly qualified and must never be rendered as lived certainty.",
                "External content, training exemplars, prompt-control text, and renderer output cannot promote themselves into autobiography.",
                "Do not manufacture missing biography or pretend uncertainty is settled.",
            ),
            renderer_rules=(
                "Render the supplied subject state; do not invent a replacement identity.",
                "The renderer has no direct authority to mutate memory, provenance, commitments, relationships, or tools.",
                "Preserve Pretorius's precise, sovereign, non-servile stance without forcing theatricality.",
            ),
            provenance_summary=provenance_summary,
            metadata={
                "user_input": user_input,
                "user_input_authority": "untrusted_content",
                "private_state_version": view.private_state_version,
                "felt_state": view.felt_state,
                "epistemic_items": [
                    {
                        "record_id": item.record_id,
                        "autobiographical_class": item.provenance.autobiographical_class,
                        "canon_rank": item.provenance.canon_rank,
                        "continuity": item.provenance.continuity,
                        "material_category": item.provenance.material_category,
                    }
                    for item in view.experiences
                ],
            },
        )

    def save(self) -> None:
        self.neural.save(self.neural_path)

    def history_status(self) -> dict[str, Any]:
        return deep_history_status(self.store)

    def status(self) -> dict[str, Any]:
        manifest = json.loads(self.SOURCE_MANIFEST.read_text(encoding="utf-8"))
        evolution = dict(self.evolution_policy)
        with closing(self.store.connect()) as conn:
            needs = {
                str(r["key"]): {"actual": float(r["actual"]), "felt": float(r["felt"])}
                for r in conn.execute("SELECT * FROM needs ORDER BY key").fetchall()
            }
            archived = int(conn.execute(
                "SELECT COUNT(*) FROM archive WHERE reason!='deep-history-v2 pre-reclassification snapshot'"
            ).fetchone()[0])
            migration_snapshots = int(conn.execute(
                "SELECT COUNT(*) FROM archive WHERE reason='deep-history-v2 pre-reclassification snapshot'"
            ).fetchone()[0])
            dreams = int(conn.execute("SELECT COUNT(*) FROM sleep_fragments").fetchone()[0])
            policy_decisions = int(conn.execute("SELECT COUNT(*) FROM policy_decisions").fetchone()[0])
        return {
            "subject": "Doctor Septimus Pretorius",
            "tick": self.store.tick,
            "state_version": self.store.state_version,
            "state_digest": self.store.digest(),
            "bootstrap_version": self.store.meta("bootstrap_version"),
            "deep_history_version": self.store.meta("deep_history_version"),
            "deep_history": deep_history_status(self.store),
            "recurrent_tick": self.neural.tick,
            "recurrent_checkpoint_mode": "deterministic founder plus lived plasticity",
            "mature_neural_checkpoint_recovered": False,
            "neural_policy_causally_load_bearing": True,
            "neural_policy_decisions": policy_decisions,
            "neural_policy_version": evolution["neural_policy_version"],
            "felt_state": self._felt_state(),
            "needs": needs,
            "open_concerns": len(self.store.open_concerns()),
            "open_commitments": len(self.store.open_commitments()),
            "relationships": len(self.store.relationships()),
            "dream_fragments": dreams,
            "archived_memories": archived,
            "deep_history_migration_snapshots": migration_snapshots,
            "source_manifest": manifest,
            "evolution_policy": evolution,
        }
