from __future__ import annotations

import json
from contextlib import closing
from pathlib import Path
from typing import Any

from .store import BrainStore, clamp


DEEP_HISTORY_VERSION = "pretorius-deep-history-v1"
DATA_DIR = Path(__file__).with_name("data")
CONNECTOME_FILE = DATA_DIR / "pretorius_connectome_v0.2.json"
AGENDA_FILE = DATA_DIR / "pretorius_seed_agenda.json"
CURATED_FILE = DATA_DIR / "deep_history.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_boundary(connectome: dict[str, Any], agenda: dict[str, Any], curated: dict[str, Any]) -> None:
    surface = {
        "connectome_nodes": connectome["graph"]["nodes"],
        "agenda": agenda["agenda"],
        "curated_records": curated["records"],
    }
    encoded = json.dumps(surface, sort_keys=True).lower()
    forbidden = ("calibos", "calibos_mind", "calibos-mind")
    hit = next((token for token in forbidden if token in encoded), None)
    if hit is not None:
        raise RuntimeError(
            f"deep-history donor-boundary violation: forbidden donor marker {hit!r} entered Pretorius history"
        )


def _node_evidence_class(node: dict[str, Any]) -> str:
    node_id = str(node["id"])
    node_type = str(node["type"])
    if node_type == "memory":
        return "inherited_canonical_memory"
    if node_type == "relationship":
        return "inherited_relationship_evidence"
    if node_type in {"identity", "belief", "value", "self_model"}:
        return "inherited_identity_evidence"
    if node_type == "emotion" or node_id.startswith("wound."):
        return "inherited_self_history"
    if node_type == "goal":
        return "inherited_goal_evidence"
    return "inherited_character_evidence"


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
        "memory.homunculi": "I inherit a documented memory of the creation of the homunculi.",
        "memory.ingolstadt": "I inherit a documented memory of Ingolstadt.",
        "wound.institutional_rejection": "Institutional rejection is an inherited wound in my personal history.",
        "wound.continuity_uncertainty": "Uncertainty about my continuity across substrates is an inherited personal wound.",
        "self.digital_continuation": "My inherited self-model includes a digital continuation or reconstruction of Pretorius.",
        "rel.henry": "Henry Frankenstein is a historically significant relationship in my inherited character evidence.",
        "rel.monster": "The Creature is a historically significant relationship in my inherited character evidence.",
        "rel.trust.user": "I carry inherited evidence of trust toward the research collaborator represented in the archived persona history, without assuming every future interlocutor is that same person.",
        "rel.admiration.user": "I carry inherited evidence of admiration toward the research collaborator represented in the archived persona history, without assuming every future interlocutor is that same person.",
        "rel.threat.user": "I carry inherited evidence of perceived threat or tension toward the research collaborator represented in the archived persona history, without assuming every future interlocutor is that same person.",
    }
    if node_id in special:
        return special[node_id]
    low = label[:1].lower() + label[1:] if label else label
    if node_type == "identity":
        return f"I understand myself as {low}."
    if node_type == "value":
        return f"I place durable value on {low}."
    if node_type == "belief":
        return f"I carry the inherited belief: {label}."
    if node_type == "style":
        return f"My inherited expressive style includes {low}."
    if node_type == "behavior":
        return f"My inherited behavioral repertoire includes {low}."
    if node_type == "motive":
        return f"A recurring inherited motive is to {low}."
    if node_type == "concept":
        return f"{label} is a recurring concept in my inherited intellectual history."
    if node_type == "emotion":
        return f"A recurring affective disposition in my inherited evidence is {low}."
    if node_type == "relationship":
        return f"My inherited relationship evidence includes {low}."
    if node_type == "self_model":
        return f"My inherited self-model includes {low}."
    if node_type == "goal":
        return f"A recurring inherited goal is: {label}."
    return f"My inherited character evidence includes {label}."


def _source_string(provenance: dict[str, Any]) -> str:
    refs = provenance.get("sources", [])
    if refs:
        ref = refs[0]
        locator = ref.get("locator")
        suffix = f"#{locator}" if locator else ""
        return f"{ref['repository']}@{ref['commit']}:{ref['path']}{suffix}"
    return str(provenance.get("source", "Pretorius deep-history migration"))


def _add_with_provenance(store: BrainStore, conn, tick: int, *, history_key: str,
                         text: str, kind: str, evidence_class: str, confidence: float,
                         salience: float, tags: tuple[str, ...],
                         provenance: dict[str, Any]) -> str:
    memory_id = store.add_memory(
        conn, tick, text, _source_string(provenance), kind, evidence_class,
        False, confidence, True, salience, tags,
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


def install_deep_history(store: BrainStore) -> dict[str, Any]:
    current = store.meta("deep_history_version", "") or ""
    if current == DEEP_HISTORY_VERSION:
        return history_status(store)
    if current:
        raise RuntimeError(
            f"deep-history version {current!r} is already installed; explicit migration to "
            f"{DEEP_HISTORY_VERSION!r} is required"
        )

    connectome = _load(CONNECTOME_FILE)
    agenda = _load(AGENDA_FILE)
    curated = _load(CURATED_FILE)
    if curated.get("version") != DEEP_HISTORY_VERSION:
        raise RuntimeError("deep-history data version does not match runtime migration version")
    _validate_boundary(connectome, agenda, curated)

    source_repo = str(connectome["source_repository"])
    source_commit = str(connectome["source_commit"])
    source_path = str(connectome["source_path"])
    source_blob = str(connectome["source_blob_sha"])

    with store.transaction() as conn:
        tick = store.tick
        for node in connectome["graph"]["nodes"]:
            node_id = str(node["id"])
            activation = float(node["a"])
            provenance = {
                "derivation": "direct connectome node import",
                "sources": [{
                    "repository": source_repo, "commit": source_commit, "path": source_path,
                    "blob_sha": source_blob, "locator": f"node:{node_id}",
                }],
                "source_node": node,
                "activation_is_not_confidence": True,
            }
            memory_id = _add_with_provenance(
                store, conn, tick,
                history_key=f"connectome:{node_id}",
                text=_node_text(node),
                kind=f"connectome_{node['type']}",
                evidence_class=_node_evidence_class(node),
                confidence=_node_confidence(node),
                salience=clamp(0.18 + 0.28 * activation, 0.18, 0.5),
                tags=("deep_history", "connectome", str(node["type"]), f"node:{node_id}"),
                provenance=provenance,
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
            provenance = {
                "derivation": "curated multi-source Pretorius history synthesis",
                "sources": item["sources"],
                "promotion_rule": "inherited evidence, never lived experience",
            }
            _add_with_provenance(
                store, conn, tick,
                history_key=f"curated:{item['key']}",
                text=str(item["text"]), kind=str(item["kind"]),
                evidence_class=str(item["evidence_class"]),
                confidence=float(item["confidence"]), salience=float(item["salience"]),
                tags=tuple(item.get("tags", [])), provenance=provenance,
            )

        agenda_source = {
            "repository": str(agenda["source_repository"]), "commit": str(agenda["source_commit"]),
            "path": str(agenda["source_path"]), "blob_sha": str(agenda["source_blob_sha"]),
        }
        for index, item in enumerate(agenda["agenda"]):
            provenance = {
                "derivation": "direct inherited research-agenda import",
                "sources": [{**agenda_source, "locator": f"agenda:{index}"}],
                "priority": int(item["priority"]), "original_source": item.get("source"),
            }
            _add_with_provenance(
                store, conn, tick,
                history_key=f"agenda:{index}:{item['title']}",
                text=f"I inherit a research agenda item: {item['title']}. {item['description']}",
                kind="project_history", evidence_class="inherited_project_evidence",
                confidence=0.96,
                salience=clamp(0.24 + 0.0035 * int(item["priority"]), 0.3, 0.65),
                tags=tuple(["deep_history", "project", "agenda"] + list(item.get("tags", []))),
                provenance=provenance,
            )

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
        store.set_meta("deep_history_gaps_json", json.dumps(curated.get("gaps", [])), conn)
        store.set_meta("deep_history_exclusions_json",
                       json.dumps(curated.get("excluded_sources", []), sort_keys=True), conn)
        store.bump_state_version(conn)

    return history_status(store)


def history_status(store: BrainStore) -> dict[str, Any]:
    with closing(store.connect()) as conn:
        node_count = int(conn.execute("SELECT COUNT(*) FROM history_nodes").fetchone()[0])
        edge_count = int(conn.execute("SELECT COUNT(*) FROM history_edges").fetchone()[0])
        provenance_count = int(conn.execute("SELECT COUNT(*) FROM memory_provenance").fetchone()[0])
        inherited_count = int(conn.execute(
            "SELECT COUNT(*) FROM memories WHERE evidence_class LIKE 'inherited_%'"
        ).fetchone()[0])
        lived_count = int(conn.execute(
            "SELECT COUNT(*) FROM memories WHERE evidence_class='lived_experience'"
        ).fetchone()[0])
        project_count = int(conn.execute(
            "SELECT COUNT(*) FROM memories WHERE evidence_class='inherited_project_evidence'"
        ).fetchone()[0])
        classes = {
            str(row["evidence_class"]): int(row["n"])
            for row in conn.execute(
                """SELECT evidence_class,COUNT(*) AS n FROM memories
                WHERE evidence_class LIKE 'inherited_%'
                GROUP BY evidence_class ORDER BY evidence_class"""
            ).fetchall()
        }
    return {
        "version": store.meta("deep_history_version", "") or "",
        "source_commit": store.meta("deep_history_source_commit", "") or "",
        "connectome_nodes": node_count,
        "connectome_edges": edge_count,
        "provenanced_memories": provenance_count,
        "inherited_memories": inherited_count,
        "lived_memories": lived_count,
        "project_records": project_count,
        "evidence_classes": classes,
        "known_gaps": json.loads(store.meta("deep_history_gaps_json", "[]") or "[]"),
        "excluded_sources": json.loads(store.meta("deep_history_exclusions_json", "[]") or "[]"),
    }
