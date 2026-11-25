"""Source-bound Corpus regulation of the original canonical fatigue need.

Adapts the existing Laboratory fatigue projection to the Tower's coarse
perceived energy grammar. The Tower remains the sole physical authority.
No hidden body value, new bodily memory, or alternative selector is created.
"""
from hashlib import sha256
import json

from .store import clamp


def fatigue_target(lines, *, complete):
    """A coarse engineering mapping, not a human fatigue calibration."""
    if "I feel worn out and find it hard to concentrate." in lines:
        return "worn_out", .82
    if "I am getting tired." in lines:
        return "tired", .55
    # Absence is informative only in the complete, uncontested, verified
    # original narrative. Its energy grammar emits tiredness below 60.
    if complete:
        return "no_reported_fatigue", .23
    return "unknown", None


def reconcile_fatigue(runtime, provider, snapshot, receipt, memory_id, scene):
    from .small_tower import SmallTowerSource
    from .virtual_world_port import VirtualWorldReceipt
    if (type(provider) is not SmallTowerSource or type(receipt) is not VirtualWorldReceipt
            or receipt.kind != "observation"
            or provider._observation(snapshot) != receipt
            or not provider.verify_receipt(receipt)):
        raise PermissionError("Corpus requires the current verified Tower perception")
    store = runtime._port.brain.store
    memory = store.get_memory(memory_id)
    source = ("virtual-world:small-tower:" + receipt.world_epoch
              + ":observation:" + receipt.event_id)
    scene_key = "sensus:tower-scene:" + sha256(source.encode()).hexdigest()
    saved = store.meta(scene_key)
    if (not memory or not memory["active"] or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or memory["source"] != source or memory["text"] != receipt.first_person
            or not memory.get("source_event_id")
            or saved is None or json.loads(saved) != scene
            or scene["source_memory_id"] != memory_id):
        raise PermissionError("Corpus requires the same admitted Sensus source")
    complete = (" ".join(snapshot["narrative"]) == receipt.first_person
                and scene["admitted_lines"] == snapshot["narrative"]
                and not scene["conflicts"])
    band, target = fatigue_target(scene["admitted_lines"], complete=complete)
    key = "corpus:tower-body:" + sha256(source.encode()).hexdigest()
    with store.transaction() as db:
        prior = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        if prior is not None:
            report = json.loads(prior["value"])
            if report["source_memory_id"] != memory_id or report["band"] != band:
                raise PermissionError("Conflicting bodily source replay")
            return report
        report = {"source_memory_id": memory_id,
                  "source_event_id": memory["source_event_id"],
                  "band": band, "complete_perception": complete,
                  "projection_applied": target is not None,
                  "world_authority": False, "motor_authority": False}
        if target is not None:
            need = db.execute("SELECT actual,felt FROM needs WHERE key='fatigue'").fetchone()
            if need is None:
                raise RuntimeError("Original canonical fatigue need absent")
            # Original lab_corpus_regulation coupling: preserve its .65 felt
            # adaptation rate and canonical bounds, but use a coarse Tower band.
            felt = clamp(float(need["felt"]) + .65 * (target - float(need["felt"])),
                         .05, .95)
            db.execute("UPDATE needs SET actual=?,felt=?,last_tick=? WHERE key='fatigue'",
                       (target, felt, store.tick))
            report.update(actual_projection=target, felt_projection=felt)
        store.set_meta(key, json.dumps(report, sort_keys=True), db)
        store.bump_state_version(db)
    return report
