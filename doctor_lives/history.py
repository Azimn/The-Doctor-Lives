from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from contextlib import closing
from pathlib import Path
from typing import Any

from .store import BrainStore, clamp, new_id, utc_now


DEEP_HISTORY_VERSION = "pretorius-deep-history-v2"
PREVIOUS_DEEP_HISTORY_VERSION = "pretorius-deep-history-v1"
DATA_DIR = Path(__file__).with_name("data")
CONNECTOME_FILE = DATA_DIR / "pretorius_connectome_v0.2.json"
AGENDA_FILE = DATA_DIR / "pretorius_seed_agenda.json"
CURATED_FILE = DATA_DIR / "deep_history.json"
POLICY_FILE = DATA_DIR / "deep_history_v2_policy.json"

AUTOBIO_CLASSES = {
    "canonical_preawakening_memory",
    "reconstructed_preawakening_memory",
    "synthesized_preawakening_memory",
    "lived_runtime_memory",
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_boundary(connectome: dict[str, Any], agenda: dict[str, Any],
                       curated: dict[str, Any], policy: dict[str, Any]) -> None:
    surface = {
        "connectome_nodes": connectome["graph"]["nodes"],
        "agenda": agenda["agenda"],
        "curated_records": curated["records"],
        "policy": policy,
    }
    encoded = json.dumps(surface, sort_keys=True).lower()
    forbidden = ("calibos", "calibos_mind", "calibos-mind")
    hit = next((token for token in forbidden if token in encoded), None)
    if hit is not None:
        raise RuntimeError(
            f"deep-history donor-boundary violation: forbidden donor marker {hit!r} entered Pretorius history"
        )


def _node_confidence(node: dict[str, Any]) -> float:
    return {
        "memory": 0.76, "identity": 0.9, "belief": 0.86, "value": 0.84,
        "self_model": 0.82, "relationship": 0.74, "emotion": 0.7,
        "goal": 0.7, "motive": 0.72, "behavior": 0.7, "style": 0.72,
        "concept": 0.68,
    }.get(str(node["type"]), 0.68)


def _node_text(node: dict[str, Any]) -> str:
    node_id = str(node["id"])
    label = str(node["label"])
    node_type = str(node["type"])
    special = {
        "memory.homunculi": "I inherit a documented account of the creation of the homunculi.",
        "memory.ingolstadt": "I inherit a documented account of Ingolstadt.",
        "wound.institutional_rejection": "Institutional rejection appears in my reconstructed personal history.",
        "wound.continuity_uncertainty": "Uncertainty about continuity across substrates is durable design evidence for my self-model.",
        "self.digital_continuation": "My design evidence includes digital continuation or reconstruction of Pretorius.",
        "rel.henry": "Henry Frankenstein is a historically significant relationship in my reconstructed preawakening evidence.",
        "rel.monster": "The Creature is a historically significant relationship in my reconstructed preawakening evidence.",
        "rel.trust.user": "Archived design evidence records trust toward a prior research collaborator without identifying every future interlocutor as that person.",
        "rel.admiration.user": "Archived design evidence records admiration toward a prior research collaborator without identifying every future interlocutor as that person.",
        "rel.threat.user": "Archived design evidence records perceived threat or tension toward a prior research collaborator without identifying every future interlocutor as that person.",
    }
    if node_id in special:
        return special[node_id]
    low = label[:1].lower() + label[1:] if label else label
    if node_type == "identity":
        return f"My design material describes me as {low}."
    if node_type == "value":
        return f"My design material assigns durable value to {low}."
    if node_type == "belief":
        return f"My design material includes the belief: {label}."
    if node_type == "style":
        return f"My design material includes the expressive tendency {low}."
    if node_type == "behavior":
        return f"My design material includes the behavioral tendency {low}."
    if node_type == "motive":
        return f"My design material includes a recurring motive to {low}."
    if node_type == "concept":
        return f"{label} is a recurring concept in my design and intellectual evidence."
    if node_type == "emotion":
        return f"My design material includes the affective disposition {low}."
    if node_type == "relationship":
        return f"My reconstructed relationship evidence includes {low}."
    if node_type == "self_model":
        return f"My design material includes the self-model claim {low}."
    if node_type == "goal":
        return f"My design material includes the recurring goal: {label}."
    return f"My design material includes {label}."


def _source_string(provenance: dict[str, Any]) -> str:
    refs = provenance.get("sources", [])
    if refs:
        ref = refs[0]
        locator = ref.get("locator")
        suffix = f"#{locator}" if locator else ""
        return f"{ref['repository']}@{ref['commit']}:{ref['path']}{suffix}"
    return str(provenance.get("source", "Pretorius Deep-History v2"))


def _classification(*, autobiographical_class: str | None, event_subtype: str,
                    canon_rank: int | None, continuity: str, material_category: str,
                    reasoning: dict[str, Any], predecessor_memory_id: str | None = None,
                    wording: str | None = None) -> dict[str, Any]:
    if wording is None:
        wording = {
            "reconstructed_preawakening_memory": "reconstructed",
            "synthesized_preawakening_memory": "synthesized",
            "lived_runtime_memory": "quoted",
        }.get(autobiographical_class, "paraphrased")
    return {
        "autobiographical_class": autobiographical_class,
        "event_subtype": event_subtype,
        "canon_rank": canon_rank,
        "continuity": continuity,
        "material_category": material_category,
        "wording": wording,
        "classification_reasoning": reasoning,
        "predecessor_memory_id": predecessor_memory_id,
        "classifier": "pretorius-deep-history-v2",
    }


def _node_classification(node: dict[str, Any], *, predecessor_memory_id: str | None = None,
                         prior_evidence_class: str | None = None) -> tuple[str, dict[str, Any]]:
    node_id = str(node["id"])
    node_type = str(node["type"])
    autobiographical = node_type in {"memory", "relationship"} or node_id == "wound.institutional_rejection"
    if autobiographical:
        cls = "reconstructed_preawakening_memory"
        subtype = {
            "memory": "historical_episode",
            "relationship": "relationship_history",
        }.get(node_type, "formative_history")
        return cls, _classification(
            autobiographical_class=cls,
            event_subtype=subtype,
            canon_rank=3,
            continuity="project_reconstruction",
            material_category="autobiography",
            predecessor_memory_id=predecessor_memory_id,
            reasoning={
                "decision": "reconstructed_preawakening_memory",
                "basis": "Persona Connectome is project reconstruction evidence, not a directly cited primary-film autobiographical source.",
                "source_node_id": node_id,
                "source_node_type": node_type,
                "prior_evidence_class": prior_evidence_class,
                "promotion_forbidden": True,
            },
        )
    return "design_material", _classification(
        autobiographical_class=None,
        event_subtype=f"connectome_{node_type}",
        canon_rank=3,
        continuity="project_reconstruction",
        material_category="design_material",
        predecessor_memory_id=predecessor_memory_id,
        reasoning={
            "decision": "design_material",
            "basis": "Character invariant/connectome material is behavior-authoritative but does not describe a remembered episode.",
            "source_node_id": node_id,
            "source_node_type": node_type,
            "prior_evidence_class": prior_evidence_class,
        },
    )


_AUTOBIO_CURATED = {
    "history.ingolstadt": "historical_episode",
    "history.homunculi": "creation_history",
    "history.institutional_rejection": "formative_history",
    "relationship.henry": "relationship_history",
    "relationship.creature": "relationship_history",
}


def _curated_classification(item: dict[str, Any], *, predecessor_memory_id: str | None = None,
                            prior_evidence_class: str | None = None) -> tuple[str, dict[str, Any]]:
    key = str(item["key"])
    if key in _AUTOBIO_CURATED:
        cls = "reconstructed_preawakening_memory"
        return cls, _classification(
            autobiographical_class=cls,
            event_subtype=_AUTOBIO_CURATED[key],
            canon_rank=3,
            continuity="project_reconstruction",
            material_category="autobiography",
            predecessor_memory_id=predecessor_memory_id,
            reasoning={
                "decision": cls,
                "basis": "Curated project synthesis is derived from archived Pretorius project evidence and is therefore reconstruction, not directly witnessed runtime memory or rank-0 canon.",
                "history_key": key,
                "prior_evidence_class": prior_evidence_class,
                "source_count": len(item.get("sources", [])),
            },
        )
    if key == "lineage.lora":
        return "reference_only_material", _classification(
            autobiographical_class=None,
            event_subtype="training_lineage",
            canon_rank=5,
            continuity="training_lineage",
            material_category="reference_only",
            predecessor_memory_id=predecessor_memory_id,
            reasoning={
                "decision": "reference_only",
                "basis": "LoRA/training examples are reconstruction lineage and cannot become autobiography by repetition.",
                "history_key": key,
                "prior_evidence_class": prior_evidence_class,
                "training_frequency_is_not_provenance": True,
            },
        )
    return "design_material", _classification(
        autobiographical_class=None,
        event_subtype=str(item["kind"]),
        canon_rank=3,
        continuity="project_reconstruction",
        material_category="design_material",
        predecessor_memory_id=predecessor_memory_id,
        reasoning={
            "decision": "design_material",
            "basis": "The curated record expresses character design, research posture, concern, goal, or self-model rather than a directly evidenced autobiographical episode.",
            "history_key": key,
            "prior_evidence_class": prior_evidence_class,
        },
    )


def _agenda_classification(index: int, title: str, *, predecessor_memory_id: str | None = None,
                           prior_evidence_class: str | None = None) -> tuple[str, dict[str, Any]]:
    return "design_material", _classification(
        autobiographical_class=None,
        event_subtype="research_agenda",
        canon_rank=3,
        continuity="project_reconstruction",
        material_category="design_material",
        predecessor_memory_id=predecessor_memory_id,
        reasoning={
            "decision": "design_material",
            "basis": "Research agenda records guide behavior but are not autobiographical episodes.",
            "agenda_index": index,
            "title": title,
            "prior_evidence_class": prior_evidence_class,
        },
    )


def _add_with_provenance(store: BrainStore, conn, tick: int, *, history_key: str,
                         text: str, kind: str, evidence_class: str, confidence: float,
                         salience: float, tags: tuple[str, ...], provenance: dict[str, Any],
                         classification: dict[str, Any]) -> str:
    memory_id = store.add_memory(
        conn, tick, text, _source_string(provenance), kind, evidence_class,
        False, confidence, True, salience, tags, classification=classification,
    )
    conn.execute(
        "INSERT INTO memory_provenance(memory_id,history_key,provenance_json) VALUES(?,?,?)",
        (memory_id, history_key, json.dumps(provenance, sort_keys=True)),
    )
    return memory_id


def _append_relationship_evidence(conn, peer_id: str, evidence_items: list[str]) -> None:
    row = conn.execute("SELECT evidence_json FROM relationships WHERE peer_id=?", (peer_id,)).fetchone()
    if row is None:
        return
    evidence = json.loads(row["evidence_json"])
    for item in evidence_items:
        if item not in evidence:
            evidence.append(item)
    conn.execute("UPDATE relationships SET evidence_json=? WHERE peer_id=?", (json.dumps(evidence), peer_id))


def _install_policy(conn, policy: dict[str, Any]) -> None:
    for item in policy["authority_axis"]:
        conn.execute(
            """INSERT OR REPLACE INTO canon_authority(rank,label,description,reserved)
            VALUES(?,?,?,?)""",
            (int(item["rank"]), str(item["label"]), str(item["description"]), int(bool(item.get("reserved", False)))),
        )
    for item in policy.get("source_custody", []):
        provenance = dict(item["provenance"])
        provenance["original_author_status"] = item.get("original_author_status")
        conn.execute(
            """INSERT OR REPLACE INTO source_custody
            (source_key,custody_status,original_author,content_status,canon_rank,continuity,provenance_json)
            VALUES(?,?,?,?,?,?,?)""",
            (
                str(item["source_key"]), str(item["custody_status"]), item.get("original_author"),
                str(item["content_status"]), int(item["canon_rank"]), str(item["continuity"]),
                json.dumps(provenance, sort_keys=True),
            ),
        )
    for item in policy.get("withheld_claims", []):
        conn.execute(
            """INSERT OR REPLACE INTO withheld_claims
            (claim_key,claim_text,status,reason,source_refs_json,anti_promotion_json,created_at)
            VALUES(?,?,?,?,?,?,?)""",
            (
                str(item["claim_key"]), str(item["claim_text"]), str(item["status"]), str(item["reason"]),
                json.dumps(item.get("source_refs", []), sort_keys=True),
                json.dumps(item.get("anti_promotion", {}), sort_keys=True), utc_now(),
            ),
        )
    for item in policy.get("reference_only", []):
        conn.execute(
            """INSERT OR REPLACE INTO reference_material
            (reference_key,label,continuity,canon_rank,status,provenance_json)
            VALUES(?,?,?,?,?,?)""",
            (
                str(item["reference_key"]), str(item["label"]), str(item["continuity"]),
                int(item["canon_rank"]), str(item["status"]),
                json.dumps(item.get("provenance", {}), sort_keys=True),
            ),
        )
    for item in policy.get("reserved_continuities", []):
        if str(item["continuity"]) == "dark_universe" and item.get("records"):
            raise RuntimeError("Dark Universe continuity is reserved and must remain empty in Deep-History v2")


def _archive_reclassification_snapshot(conn, row: dict[str, Any], tick: int) -> None:
    payload = dict(row)
    payload["migration_snapshot"] = {
        "migration": DEEP_HISTORY_VERSION,
        "captured_at": utc_now(),
        "note": "Pre-v2 representation preserved before in-place epistemic reclassification.",
    }
    conn.execute(
        "INSERT INTO archive(id,archived_tick,record_id,reason,record_json) VALUES(?,?,?,?,?)",
        (
            new_id("arc"), tick, str(row["id"]), "deep-history-v2 pre-reclassification snapshot",
            json.dumps(payload, sort_keys=True, default=str),
        ),
    )


def _classify_existing_history(store: BrainStore, conn, curated: dict[str, Any],
                               connectome: dict[str, Any], agenda: dict[str, Any]) -> None:
    curated_by_key = {str(item["key"]): item for item in curated["records"]}
    node_by_id = {str(item["id"]): item for item in connectome["graph"]["nodes"]}
    rows = conn.execute(
        """SELECT p.history_key,p.memory_id,m.* FROM memory_provenance p
        JOIN memories m ON m.id=p.memory_id ORDER BY p.history_key"""
    ).fetchall()
    for raw in rows:
        row = dict(raw)
        key = str(row["history_key"])
        prior = str(row["evidence_class"])
        replacement_text = None
        if key.startswith("connectome:"):
            node_id = key.split(":", 1)[1]
            evidence_class, classification = _node_classification(
                node_by_id[node_id], predecessor_memory_id=str(row["id"]),
                prior_evidence_class=prior,
            )
        elif key.startswith("curated:"):
            curated_key = key.split(":", 1)[1]
            curated_item = curated_by_key[curated_key]
            evidence_class, classification = _curated_classification(
                curated_item, predecessor_memory_id=str(row["id"]),
                prior_evidence_class=prior,
            )
            replacement_text = str(curated_item["text"])
        elif key.startswith("agenda:"):
            parts = key.split(":", 2)
            index = int(parts[1])
            title = str(agenda["agenda"][index]["title"])
            evidence_class, classification = _agenda_classification(
                index, title, predecessor_memory_id=str(row["id"]),
                prior_evidence_class=prior,
            )
        else:
            continue
        if conn.execute(
            "SELECT 1 FROM memory_classifications WHERE memory_id=?", (row["id"],)
        ).fetchone() is None:
            _archive_reclassification_snapshot(conn, row, store.tick)
        if replacement_text is not None:
            conn.execute(
                "UPDATE memories SET text=?,evidence_class=? WHERE id=?",
                (replacement_text, evidence_class, row["id"]),
            )
        else:
            conn.execute("UPDATE memories SET evidence_class=? WHERE id=?", (evidence_class, row["id"]))
        store.set_classification(conn, str(row["id"]), classification)


def _classify_bootstrap_and_runtime(store: BrainStore, conn) -> None:
    rows = conn.execute(
        """SELECT * FROM memories WHERE id NOT IN
        (SELECT memory_id FROM memory_classifications) ORDER BY created_tick,id"""
    ).fetchall()
    for raw in rows:
        row = dict(raw)
        prior = str(row["evidence_class"])
        text = str(row["text"])
        source = str(row["source"])
        if prior in {"lived_experience", "lived_action_outcome"}:
            _archive_reclassification_snapshot(conn, row, store.tick)
            new_class = "lived_runtime_memory"
            conn.execute("UPDATE memories SET evidence_class=? WHERE id=?", (new_class, row["id"]))
            store.set_classification(conn, str(row["id"]), _classification(
                autobiographical_class=new_class,
                event_subtype=str(row["kind"]),
                canon_rank=None,
                continuity="runtime",
                material_category="autobiography",
                predecessor_memory_id=str(row["id"]),
                wording="paraphrased" if str(row["kind"]) == "action_outcome" else "quoted",
                reasoning={
                    "decision": new_class,
                    "basis": "The event was experienced by this running Pretorius instance and is migrated from the legacy lived-memory class.",
                    "prior_evidence_class": prior,
                    "source": source,
                },
            ))
            continue
        if source == "bootstrap" or prior in {"identity", "inherited_character_evidence"}:
            _archive_reclassification_snapshot(conn, row, store.tick)
            if "Ingolstadt" in text or "homunculi" in text:
                new_class = "reconstructed_preawakening_memory"
                material = "autobiography"
                autobio = new_class
                subtype = "bootstrap_historical_seed"
                reasoning = "Bootstrap historical seed derives from project reconstruction evidence rather than directly cited primary-film evidence."
            else:
                new_class = "design_material"
                material = "design_material"
                autobio = None
                subtype = "bootstrap_design"
                reasoning = "Bootstrap identity/self-model material is authoritative for behavior but is not autobiography."
            if "Ingolstadt" in text:
                conn.execute(
                    "UPDATE memories SET text=?,evidence_class=? WHERE id=?",
                    ("Ingolstadt appears in my reconstructed preawakening evidence.", new_class, row["id"]),
                )
            else:
                conn.execute("UPDATE memories SET evidence_class=? WHERE id=?", (new_class, row["id"]))
            store.set_classification(conn, str(row["id"]), _classification(
                autobiographical_class=autobio,
                event_subtype=subtype,
                canon_rank=3,
                continuity="project_reconstruction",
                material_category=material,
                predecessor_memory_id=str(row["id"]),
                reasoning={
                    "decision": new_class,
                    "basis": reasoning,
                    "prior_evidence_class": prior,
                    "source": source,
                },
            ))


def create_synthesis_proposal(store: BrainStore, *, claim_key: str, author: str, reviewer: str,
                              proposed_claim: str, sources: list[dict[str, Any]], reasoning: str,
                              causal_leverage: str, evidence_strength: str,
                              alternatives: list[str], exclusion_rulings: list[str],
                              conflict_notes: str = "") -> str:
    claim = proposed_claim.strip()
    if not claim:
        raise ValueError("proposed_claim is required")
    claim_sha256 = hashlib.sha256(claim.encode("utf-8")).hexdigest()
    admission_id = new_id("synth")
    with store.transaction() as conn:
        conn.execute(
            """INSERT INTO synthesis_admissions
            (id,claim_key,memory_id,author,reviewer,proposed_claim,claim_sha256,sources_json,reasoning,
             causal_leverage,evidence_strength,alternatives_json,exclusion_rulings_json,
             conflict_notes,status,created_at,reviewed_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                admission_id, claim_key, None, author, reviewer, claim, claim_sha256,
                json.dumps(sources, sort_keys=True), reasoning, causal_leverage, evidence_strength,
                json.dumps(alternatives, sort_keys=True), json.dumps(exclusion_rulings, sort_keys=True),
                conflict_notes, "proposed", utc_now(), None,
            ),
        )
    return admission_id


def review_synthesis_proposal(store: BrainStore, admission_id: str, *, approved: bool,
                              reviewer: str, exclusion_rulings: list[str] | None = None) -> None:
    with store.transaction() as conn:
        row = conn.execute(
            """SELECT reviewer,status,proposed_claim,claim_sha256
            FROM synthesis_admissions WHERE id=?""", (admission_id,)
        ).fetchone()
        if row is None:
            raise KeyError(admission_id)
        if str(row["status"]) != "proposed":
            raise ValueError("synthesis proposal is not pending review")
        if str(row["reviewer"]) != reviewer:
            raise ValueError("reviewer does not match the recorded independent reviewer")
        expected_hash = hashlib.sha256(
            str(row["proposed_claim"]).encode("utf-8")
        ).hexdigest()
        if str(row["claim_sha256"]) != expected_hash:
            raise ValueError("synthesis proposal changed after claim binding")
        status = "approved" if approved else "rejected"
        if exclusion_rulings is None:
            conn.execute(
                "UPDATE synthesis_admissions SET status=?,reviewed_at=? WHERE id=?",
                (status, utc_now(), admission_id),
            )
        else:
            conn.execute(
                """UPDATE synthesis_admissions SET status=?,reviewed_at=?,exclusion_rulings_json=?
                WHERE id=?""",
                (status, utc_now(), json.dumps(exclusion_rulings, sort_keys=True), admission_id),
            )


def resolve_canon_conflict(store: BrainStore, *, conflict_key: str,
                           memory_ids: list[str], rationale: str = "") -> dict[str, Any]:
    candidates = sorted(set(str(x) for x in memory_ids))
    if len(candidates) < 2:
        raise ValueError("canon conflict resolution requires at least two distinct memories")
    with store.transaction() as conn:
        placeholders = ",".join("?" for _ in candidates)
        rows = conn.execute(
            f"""SELECT m.id,m.evidence_class,m.active,c.autobiographical_class,
            c.canon_rank,c.continuity,c.wording
            FROM memories m JOIN memory_classifications c ON c.memory_id=m.id
            WHERE m.id IN ({placeholders})""",
            tuple(candidates),
        ).fetchall()
        if len(rows) != len(candidates):
            found = {str(row["id"]) for row in rows}
            missing = sorted(set(candidates) - found)
            raise ValueError(f"unclassified or missing conflict candidates: {missing!r}")
        decoded = [dict(row) for row in rows]
        if any(not bool(row["active"]) for row in decoded):
            raise ValueError("canon conflict candidates must be active memories")
        if any(row["canon_rank"] is None for row in decoded):
            raise ValueError("canon conflict candidates require non-null canon ranks")
        allowed = {
            "canonical_preawakening_memory",
            "reconstructed_preawakening_memory",
            "synthesized_preawakening_memory",
        }
        if any(str(row["autobiographical_class"]) not in allowed for row in decoded):
            raise ValueError("canon conflict resolution is limited to preawakening autobiography")
        continuities = {str(row["continuity"]) for row in decoded}
        if len(continuities) != 1:
            raise ValueError(
                "records from different continuities coexist; resolve conflicts only within one continuity"
            )

        ordered = sorted(decoded, key=lambda row: (int(row["canon_rank"]), str(row["id"])))
        winner = ordered[0]
        resolution = {
            "conflict_key": conflict_key,
            "rule": "lowest_canon_rank_then_lexicographic_memory_id",
            "rank_direction": "lower_is_stronger",
            "continuity": next(iter(continuities)),
            "winner_memory_id": str(winner["id"]),
            "winner_canon_rank": int(winner["canon_rank"]),
            "winner_autobiographical_class": str(winner["autobiographical_class"]),
            "class_upgrade_performed": False,
            "candidates": [
                {
                    "memory_id": str(row["id"]),
                    "canon_rank": int(row["canon_rank"]),
                    "autobiographical_class": str(row["autobiographical_class"]),
                    "wording": str(row["wording"]),
                }
                for row in ordered
            ],
        }
        audit_id = new_id("conflict")
        conn.execute(
            """INSERT INTO conflict_resolutions
            (id,conflict_key,created_at,candidate_memory_ids_json,candidate_ranks_json,
             winner_memory_id,rule,rationale,resolution_json)
            VALUES(?,?,?,?,?,?,?,?,?)""",
            (
                audit_id, conflict_key, utc_now(),
                json.dumps(candidates),
                json.dumps(
                    {str(row["id"]): int(row["canon_rank"]) for row in decoded},
                    sort_keys=True,
                ),
                str(winner["id"]),
                "lowest_canon_rank_then_lexicographic_memory_id",
                rationale,
                json.dumps(resolution, sort_keys=True),
            ),
        )
        store.bump_state_version(conn)
    return {"audit_id": audit_id, **resolution}


def retract_synthesis_admission(store: BrainStore, admission_id: str, *,
                                retracted_by: str, reason: str) -> dict[str, Any]:
    if not retracted_by.strip():
        raise ValueError("retracted_by is required")
    if not reason.strip():
        raise ValueError("retraction reason is required")
    note = (
        "Synthesis admission is retractable, not reversible: retraction removes the active "
        "memory but cannot undo cognition that already occurred."
    )
    with store.transaction() as conn:
        row = conn.execute(
            """SELECT id,status,memory_id,retraction_note FROM synthesis_admissions
            WHERE id=?""",
            (admission_id,),
        ).fetchone()
        if row is None:
            raise KeyError(admission_id)
        if str(row["status"]) != "approved":
            raise ValueError("only an approved synthesis admission can be retracted")
        memory_id = None if row["memory_id"] is None else str(row["memory_id"])
        if memory_id is not None:
            store.archive_memory(
                conn, memory_id, store.tick,
                f"synthesis admission {admission_id} retracted: {reason.strip()}",
            )
            conn.execute(
                "UPDATE memory_classifications SET status='retracted' WHERE memory_id=?",
                (memory_id,),
            )
        conn.execute(
            """UPDATE synthesis_admissions
            SET status='retracted',retracted_at=?,retracted_by=?,retraction_reason=?,
                retraction_note=?
            WHERE id=?""",
            (utc_now(), retracted_by.strip(), reason.strip(), note, admission_id),
        )
        store.bump_state_version(conn)
    return {
        "admission_id": admission_id,
        "memory_id": memory_id,
        "status": "retracted",
        "retraction_note": note,
        "retroactive_cognition_undone": False,
    }


def install_deep_history(
    store: BrainStore, *, evidence_root: str | Path | None = None
) -> dict[str, Any]:
    current = store.meta("deep_history_version", "") or ""
    if current == DEEP_HISTORY_VERSION:
        return history_status(store)
    if current not in {"", PREVIOUS_DEEP_HISTORY_VERSION}:
        raise RuntimeError(
            f"deep-history version {current!r} is installed; no migration to {DEEP_HISTORY_VERSION!r} is defined"
        )

    root = Path(evidence_root) if evidence_root is not None else DATA_DIR
    connectome = _load(root / "pretorius_connectome_v0.2.json")
    agenda = _load(root / "pretorius_seed_agenda.json")
    curated = _load(root / "deep_history.json")
    policy = _load(root / "deep_history_v2_policy.json")
    if policy.get("version") != DEEP_HISTORY_VERSION:
        raise RuntimeError("Deep-History v2 policy version does not match runtime migration version")
    _validate_boundary(connectome, agenda, curated, policy)

    source_repo = str(connectome["source_repository"])
    source_commit = str(connectome["source_commit"])
    source_path = str(connectome["source_path"])
    source_blob = str(connectome["source_blob_sha"])

    with store.transaction() as conn:
        _install_policy(conn, policy)
        tick = store.tick

        if current == "":
            for node in connectome["graph"]["nodes"]:
                node_id = str(node["id"])
                activation = float(node["a"])
                evidence_class, classification = _node_classification(node)
                provenance = {
                    "derivation": "direct Persona Connectome node import with v2 epistemic classification",
                    "sources": [{
                        "repository": source_repo, "commit": source_commit, "path": source_path,
                        "blob_sha": source_blob, "locator": f"node:{node_id}",
                    }],
                    "source_node": node,
                    "activation_is_not_confidence": True,
                    "classification_reasoning": classification["classification_reasoning"],
                }
                memory_id = _add_with_provenance(
                    store, conn, tick,
                    history_key=f"connectome:{node_id}",
                    text=_node_text(node),
                    kind=f"connectome_{node['type']}",
                    evidence_class=evidence_class,
                    confidence=_node_confidence(node),
                    salience=clamp(0.18 + 0.28 * activation, 0.18, 0.5),
                    tags=("deep_history", "connectome", str(node["type"]), f"node:{node_id}"),
                    provenance=provenance,
                    classification=classification,
                )
                conn.execute(
                    """INSERT INTO history_nodes
                    (node_id,label,node_type,activation,memory_id,provenance_json)
                    VALUES(?,?,?,?,?,?)""",
                    (node_id, str(node["label"]), str(node["type"]), activation, memory_id,
                     json.dumps(provenance, sort_keys=True)),
                )

            for index, edge in enumerate(connectome["graph"]["edges"]):
                provenance = {
                    "derivation": "direct connectome edge import", "repository": source_repo,
                    "commit": source_commit, "path": source_path, "blob_sha": source_blob,
                    "locator": f"edge:{index}",
                }
                conn.execute(
                    """INSERT INTO history_edges
                    (edge_id,source_node_id,target_node_id,weight,kind,provenance_json)
                    VALUES(?,?,?,?,?,?)""",
                    (f"connectome-edge-{index:03d}", str(edge["s"]), str(edge["t"]),
                     float(edge["w"]), str(edge["k"]), json.dumps(provenance, sort_keys=True)),
                )

            for item in curated["records"]:
                evidence_class, classification = _curated_classification(item)
                provenance = {
                    "derivation": "curated multi-source Pretorius history with v2 epistemic classification",
                    "sources": item["sources"],
                    "promotion_rule": "preawakening evidence never becomes lived_runtime_memory",
                    "classification_reasoning": classification["classification_reasoning"],
                }
                _add_with_provenance(
                    store, conn, tick,
                    history_key=f"curated:{item['key']}",
                    text=str(item["text"]), kind=str(item["kind"]),
                    evidence_class=evidence_class,
                    confidence=float(item["confidence"]), salience=float(item["salience"]),
                    tags=tuple(item.get("tags", [])), provenance=provenance,
                    classification=classification,
                )

            agenda_source = {
                "repository": str(agenda["source_repository"]), "commit": str(agenda["source_commit"]),
                "path": str(agenda["source_path"]), "blob_sha": str(agenda["source_blob_sha"]),
            }
            for index, item in enumerate(agenda["agenda"]):
                evidence_class, classification = _agenda_classification(index, str(item["title"]))
                provenance = {
                    "derivation": "direct research-agenda import as design material",
                    "sources": [{**agenda_source, "locator": f"agenda:{index}"}],
                    "priority": int(item["priority"]), "original_source": item.get("source"),
                    "classification_reasoning": classification["classification_reasoning"],
                }
                _add_with_provenance(
                    store, conn, tick,
                    history_key=f"agenda:{index}:{item['title']}",
                    text=f"Research agenda: {item['title']}. {item['description']}",
                    kind="project_history", evidence_class=evidence_class,
                    confidence=0.96,
                    salience=clamp(0.24 + 0.0035 * int(item["priority"]), 0.3, 0.65),
                    tags=tuple(["deep_history", "project", "agenda"] + list(item.get("tags", []))),
                    provenance=provenance,
                    classification=classification,
                )
        else:
            _classify_existing_history(store, conn, curated, connectome, agenda)

        _classify_bootstrap_and_runtime(store, conn)

        _append_relationship_evidence(conn, "henry_frankenstein", [
            f"{source_repo}@{source_commit}:{source_path}#node:rel.henry",
            f"{source_repo}@{source_commit}:{source_path}#incident-edges:rel.henry",
        ])
        _append_relationship_evidence(conn, "the_creature", [
            f"{source_repo}@{source_commit}:{source_path}#node:rel.monster",
            f"{source_repo}@{source_commit}:{source_path}#incident-edges:rel.monster",
        ])

        store.set_meta("deep_history_version", DEEP_HISTORY_VERSION, conn)
        store.set_meta("deep_history_source_commit", source_commit, conn)
        store.set_meta("deep_history_policy_issue", "Azimn/The-Doctor-Lives#4", conn)
        store.set_meta("deep_history_gaps_json", json.dumps(curated.get("gaps", [])), conn)
        store.set_meta("deep_history_exclusions_json",
                       json.dumps(curated.get("excluded_sources", []), sort_keys=True), conn)
        store.bump_state_version(conn)

    return history_status(store)


def render_memory_for_workspace(row: dict[str, Any]) -> str:
    text = str(row["text"])
    autobiographical_class = row.get("autobiographical_class")
    material_category = row.get("material_category")
    if autobiographical_class == "canonical_preawakening_memory":
        return f"[canonical preawakening memory] {text}"
    if autobiographical_class == "reconstructed_preawakening_memory":
        return f"[reconstructed preawakening account; not lived certainty] {text}"
    if autobiographical_class == "synthesized_preawakening_memory":
        return f"[admitted synthesis; not canonical or lived memory] {text}"
    if autobiographical_class == "lived_runtime_memory":
        return text
    if material_category == "design_material":
        return f"[design material; behavior-authoritative, not autobiography] {text}"
    if material_category == "reference_only":
        return f"[reference only; not autobiographical memory] {text}"
    return text


def spreading_activation(store: BrainStore, seed_memory_ids: list[str], *,
                         decay: float = 0.55, max_depth: int = 2,
                         max_bonus: float = 0.28) -> tuple[dict[str, float], list[dict[str, Any]]]:
    if not 0.0 < decay < 1.0:
        raise ValueError("decay must be between zero and one")
    if max_depth < 1:
        return {}, []
    with closing(store.connect()) as conn:
        nodes = conn.execute("SELECT node_id,memory_id FROM history_nodes ORDER BY node_id").fetchall()
        edges = conn.execute(
            """SELECT source_node_id,target_node_id,weight,edge_id FROM history_edges
            ORDER BY edge_id"""
        ).fetchall()
    memory_to_node = {str(row["memory_id"]): str(row["node_id"]) for row in nodes}
    node_to_memory = {str(row["node_id"]): str(row["memory_id"]) for row in nodes}
    adjacency: dict[str, list[tuple[str, float, str]]] = defaultdict(list)
    for row in edges:
        a, b = str(row["source_node_id"]), str(row["target_node_id"])
        w, edge_id = float(row["weight"]), str(row["edge_id"])
        adjacency[a].append((b, w, edge_id))
        adjacency[b].append((a, w, edge_id))
    for key in adjacency:
        adjacency[key].sort(key=lambda x: (x[0], x[2]))

    bonuses: dict[str, float] = defaultdict(float)
    paths: list[dict[str, Any]] = []
    for seed_memory in sorted(set(seed_memory_ids)):
        seed_node = memory_to_node.get(seed_memory)
        if seed_node is None:
            continue
        queue = deque([(seed_node, 0, 1.0, (seed_node,), ())])
        best: dict[tuple[str, int], float] = {(seed_node, 0): 1.0}
        while queue:
            node_id, depth, product, path_nodes, path_edges = queue.popleft()
            if depth >= max_depth:
                continue
            for target, weight, edge_id in adjacency.get(node_id, []):
                next_depth = depth + 1
                next_product = product * weight
                key = (target, next_depth)
                magnitude = abs(next_product)
                if magnitude <= best.get(key, -1.0):
                    continue
                best[key] = magnitude
                raw_contribution = max_bonus * (decay ** next_depth) * next_product
                contribution = max(-max_bonus, min(max_bonus, raw_contribution))
                target_memory = node_to_memory.get(target)
                if target_memory and target_memory != seed_memory:
                    bonuses[target_memory] = max(
                        -max_bonus,
                        min(max_bonus, bonuses[target_memory] + contribution),
                    )
                    paths.append({
                        "seed_memory_id": seed_memory,
                        "target_memory_id": target_memory,
                        "distance": next_depth,
                        "edge_product": next_product,
                        "edge_weight": weight,
                        "polarity": "inhibitory" if weight < 0 else "excitatory",
                        "decay": decay,
                        "contribution": contribution,
                        "node_path": list(path_nodes + (target,)),
                        "edge_path": list(path_edges + (edge_id,)),
                    })
                # Inhibitory edges apply a bounded negative retrieval pressure but
                # terminate propagation. This prevents double-negative paths from
                # reappearing as positive activation.
                if weight > 0:
                    queue.append((
                        target, next_depth, next_product,
                        path_nodes + (target,), path_edges + (edge_id,),
                    ))
    paths.sort(key=lambda x: (
        x["seed_memory_id"], x["distance"], x["target_memory_id"], x["edge_path"]
    ))
    return dict(bonuses), paths


def record_retrieval_audit(store: BrainStore, *, query: str, direct_memory_ids: list[str],
                           activated_memory_ids: list[str], paths: list[dict[str, Any]],
                           ranked_memory_ids: list[str], config: dict[str, Any],
                           state_digest_before: str, state_digest_after: str) -> str:
    if state_digest_before != state_digest_after:
        raise AssertionError("retrieval-time spreading activation mutated canonical brain state")
    audit_id = new_id("retrieval")
    with store.transaction() as conn:
        conn.execute(
            """INSERT INTO retrieval_audits
            (id,tick,query,config_json,direct_memory_ids_json,activated_memory_ids_json,
             path_contributions_json,ranked_memory_ids_json,state_digest_before,state_digest_after,
             created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (
                audit_id, store.tick, query, json.dumps(config, sort_keys=True),
                json.dumps(direct_memory_ids), json.dumps(activated_memory_ids),
                json.dumps(paths, sort_keys=True), json.dumps(ranked_memory_ids),
                state_digest_before, state_digest_after, utc_now(),
            ),
        )
    return audit_id


def history_status(store: BrainStore) -> dict[str, Any]:
    with closing(store.connect()) as conn:
        node_count = int(conn.execute("SELECT COUNT(*) FROM history_nodes").fetchone()[0])
        edge_count = int(conn.execute("SELECT COUNT(*) FROM history_edges").fetchone()[0])
        provenance_count = int(conn.execute("SELECT COUNT(*) FROM memory_provenance").fetchone()[0])
        lived_count = int(conn.execute(
            "SELECT COUNT(*) FROM memories WHERE evidence_class='lived_runtime_memory'"
        ).fetchone()[0])
        preawakening_count = int(conn.execute(
            """SELECT COUNT(*) FROM memories WHERE evidence_class IN
            ('canonical_preawakening_memory','reconstructed_preawakening_memory',
             'synthesized_preawakening_memory')"""
        ).fetchone()[0])
        project_count = int(conn.execute(
            """SELECT COUNT(*) FROM memory_classifications
            WHERE event_subtype='research_agenda'"""
        ).fetchone()[0])
        classes = {
            str(row["evidence_class"]): int(row["n"])
            for row in conn.execute(
                """SELECT evidence_class,COUNT(*) AS n FROM memories
                GROUP BY evidence_class ORDER BY evidence_class"""
            ).fetchall()
        }
        autobiographical_classes = {
            str(row["autobiographical_class"]): int(row["n"])
            for row in conn.execute(
                """SELECT autobiographical_class,COUNT(*) AS n FROM memory_classifications
                WHERE autobiographical_class IS NOT NULL
                GROUP BY autobiographical_class ORDER BY autobiographical_class"""
            ).fetchall()
        }
        withheld_count = int(conn.execute("SELECT COUNT(*) FROM withheld_claims").fetchone()[0])
        synthesis_counts = {
            str(row["status"]): int(row["n"])
            for row in conn.execute(
                "SELECT status,COUNT(*) AS n FROM synthesis_admissions GROUP BY status"
            ).fetchall()
        }
        custody = [
            dict(row) for row in conn.execute(
                """SELECT source_key,custody_status,original_author,content_status,canon_rank,continuity
                FROM source_custody ORDER BY source_key"""
            ).fetchall()
        ]
    return {
        "version": store.meta("deep_history_version", "") or "",
        "source_commit": store.meta("deep_history_source_commit", "") or "",
        "governing_issue": store.meta("deep_history_policy_issue", "") or "",
        "connectome_nodes": node_count,
        "connectome_edges": edge_count,
        "provenanced_memories": provenance_count,
        "preawakening_memories": preawakening_count,
        "lived_memories": lived_count,
        "project_records": project_count,
        "evidence_classes": classes,
        "autobiographical_classes": autobiographical_classes,
        "withheld_claims": withheld_count,
        "synthesis_admissions": synthesis_counts,
        "source_custody": custody,
        "known_gaps": json.loads(store.meta("deep_history_gaps_json", "[]") or "[]"),
        "excluded_sources": json.loads(store.meta("deep_history_exclusions_json", "[]") or "[]"),
    }
