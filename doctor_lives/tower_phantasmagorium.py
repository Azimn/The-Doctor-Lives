"""Original Phantasmagorium v0.5 on authenticated Tower activity boundaries.

The donor snapshot and nonfactual recollection share the canonical BrainStore
transaction. No imagined scene can become a verified physical outcome.
"""
from contextlib import closing
from hashlib import sha256
import json

from .lab_phantasmagorium import (
    STATE, SOURCE, _snapshot, _stable, _digest, _run, _nonfactual,
)
from .phantasmagorium_bridge import DONOR_SHA256, verify_archive


def sync_tower_phantasmagorium(store, provider, receipt, memory_id, archive):
    """Consume an actual completed read or sleep once, including source replay."""
    from .small_tower import SmallTowerSource
    from .virtual_world_port import VirtualWorldReceipt
    if (type(provider) is not SmallTowerSource
            or type(receipt) is not VirtualWorldReceipt
            or receipt.kind != "action"
            or receipt.operation not in ("read", "sleep")
            or not receipt.successful
            or not provider.verify_receipt(receipt)):
        raise PermissionError("Authentic completed Tower reading or sleep required")
    memory = store.get_memory(memory_id)
    source = ("virtual-world:small-tower:" + receipt.world_epoch
              + ":action:" + receipt.event_id)
    if (not memory or not memory["active"] or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or memory["source"] != source or memory["text"] != receipt.first_person
            or not memory.get("source_event_id")):
        raise PermissionError("Exact admitted Tower source memory required")
    archive = verify_archive(archive)
    digest = sha256(source.encode()).hexdigest()
    key = "phantasmagorium:tower-event:" + digest
    previous = store.meta(key)
    if previous:
        report = json.loads(previous)
        if report["source_memory_id"] != memory_id:
            raise PermissionError("Conflicting imagination source replay")
        return report
    raw = store.meta(STATE)
    state = _snapshot(raw, receipt.world_epoch)
    sleeping = receipt.operation == "sleep"
    day = state["nights"] + 1
    request = {"pin": DONOR_SHA256, "files": state["files"], "day": day,
               "seed": int(digest[:15], 16), "cues": [memory["text"]],
               "op": "night" if sleeping else "fancy"}
    if sleeping:
        with closing(store.connect()) as db:
            cues = db.execute(
                "SELECT text FROM memories WHERE active=1 AND external=0 "
                "AND evidence_class='lived_runtime_memory' AND source LIKE ? "
                "AND created_tick<? ORDER BY created_tick DESC LIMIT 5",
                ("virtual-world:small-tower:" + receipt.world_epoch + ":%",
                 memory["created_tick"])).fetchall()
        request["cues"] = [r["text"][:1000] for r in reversed(cues)] + request["cues"]
    else:
        # The Tower currently supplies a witnessed consultation, not full page
        # text. Do not invent the book's contents or a second lived event.
        request["scene"] = {"initial_scene": {"entities": [
            {"id": "folio", "kind": "book", "properties": {"form": "historical folio"}},
            {"id": "page", "kind": "page", "properties": {"context": memory["text"]}},
        ], "relations": []}, "max_fragments": 4}
    output = _run(archive, request)
    result, recall = output["result"], output["recall"]
    expected = "dreamed_not_lived" if sleeping else "hypothetical_only"
    if not _nonfactual(result, expected):
        raise PermissionError("Original donor omitted fictional provenance")
    text = None
    if sleeping:
        if not _nonfactual(recall, "dreamed_not_lived") or type(recall.get("has_recollection")) is not bool:
            raise PermissionError("Unmarked dream recollection")
        if recall["has_recollection"]:
            text = recall["text"]
            from .phenomenology import implementation_leaks, control_instruction_markers
            if (type(text) is not str or not text.startswith("I recall a dream: ")
                    or len(text) > 800 or implementation_leaks(text)
                    or control_instruction_markers(text)):
                raise PermissionError("Unmarked or unsafe dream text")
    elif any(not _nonfactual(f, "dreamed_not_lived") for f in result["fragments"]):
        raise PermissionError("Unmarked fancy fragment")
    updated = dict(state, files=output["files"])
    if sleeping:
        updated["nights"] = day
    envelope = {"payload": updated, "sha256": _digest(updated)}
    report = {"source_sha256": digest, "source_memory_id": memory_id,
              "source_event_id": memory["source_event_id"],
              "donor_sha256": DONOR_SHA256, "operation": request["op"],
              "sleep_index": updated["nights"], "fictional_result_sha256": _digest(result),
              "recollection_memory_id": None, "world_authority": False,
              "factual_memory_eligible": False, "motor_authority": False,
              "fragment_count": len(result.get("fragments", []))}
    with store.transaction() as db:
        existing = db.execute("SELECT value FROM meta WHERE key=?", (STATE,)).fetchone()
        if (existing["value"] if existing else None) != raw:
            raise RuntimeError("Concurrent original Phantasmagorium update")
        if db.execute("SELECT 1 FROM meta WHERE key=?", (key,)).fetchone():
            raise RuntimeError("Duplicate donor source event")
        if text:
            report["recollection_memory_id"] = store.add_memory(
                db, store.tick, text, SOURCE + digest, "dream_recollection",
                "dreamed_not_lived", True, 1.0, False, .35,
                tags=("dream", "fictional", "nonfactual"))
        store.set_meta(STATE, _stable(envelope), db)
        store.set_meta(key, _stable(report), db)
        store.bump_state_version(db)
    return report
