"""Source-bound Tower intentions in the original Telos commitment table.

A concrete Noesis decision is not a completed activity. The intent is durable
with the motor reservation, and only the source-pinned physical ledger can
close it. This is a bounded intention lifecycle, not long-horizon goal synthesis.
"""
import json
from contextlib import closing

from .lab_telos import SOURCE_PREFIX, DEFAULT_IMPORTANCE


def intention_id(policy_id):
    return "telos_tower_" + policy_id


def reserve_intention(store, db, request, *, subject=None):
    """Called inside the same transaction as the canonical motor reservation."""
    policy_id, action = request["policyRef"], request["choice"]
    if action is None:
        if policy_id is not None:
            raise PermissionError("Policy without physical intention")
        return None
    policy = db.execute(
        "SELECT tick,trigger,selected_action FROM policy_decisions WHERE id=?",
        (policy_id,)).fetchone()
    thoughts = db.execute(
        "SELECT text FROM thoughts WHERE generated_by=? AND trigger=?",
        ("noesis_world_affordance:" + policy_id, "noesis_world_affordance")).fetchall()
    if (policy is None or policy["trigger"] != "noesis_world_affordance"
            or policy["selected_action"] != action or len(thoughts) != 1
            or not thoughts[0]["text"].startswith("I intend to ")):
        raise PermissionError("Tower intention lacks its own canonical Noesis origin")
    # The motor reservation must be preceded by my own admitted decision.
    audit = db.execute("SELECT state_pressure_json FROM policy_decisions WHERE id=?",(policy_id,)).fetchone()
    bound=db.execute("SELECT value FROM meta WHERE key='small-tower:world-binding-v1'").fetchone()
    required=json.loads(audit["state_pressure_json"]).get("ipseity",{}).get("required")
    if bound is not None and not required:
        raise PermissionError("Bound Tower cannot reserve a decision outside Synthetic Ipseity")
    if required:
        from .tower_ipseity import RECORD
        own = db.execute("SELECT value FROM meta WHERE key=?",(RECORD+"decision:"+policy_id,)).fetchone()
        if own is None or json.loads(own["value"])["content"][0]["text"] != thoughts[0]["text"]:
            raise PermissionError("Motor intention has not been admitted by its owning subject")
    description = thoughts[0]["text"].removeprefix("I intend to ").rstrip(".")
    rid = intention_id(policy_id)
    source = SOURCE_PREFIX + "tower:" + policy_id
    db.execute(
        "INSERT OR IGNORE INTO commitments "
        "(id,created_tick,updated_tick,description,status,due_tick,importance,actor,source,outcome) "
        "VALUES(?,?,?,?,'open',NULL,?,NULL,?,NULL)",
        (rid, policy["tick"], store.tick, description, DEFAULT_IMPORTANCE, source))
    row = db.execute("SELECT * FROM commitments WHERE id=?", (rid,)).fetchone()
    if (row["source"] != source or row["description"] != description
            or row["status"] != "open" or row["outcome"] is not None
            or row["created_tick"] != policy["tick"]):
        raise PermissionError("Conflicting Tower intention reservation")
    from .tower_prospective import reserve
    reserve(store, db, request,subject=subject)
    return rid


def reconcile_intention(store, provider, row, receipt, memory_id):
    """Resolve exactly one verified completed/failed physical consequence.

    The original event's policyRef is verified against a fresh source lookup;
    receipt equality alone does not authenticate this engineering field.
    Historic events without a new Telos row are left unchanged.
    """
    if row["kind"] not in ("completed", "action_failed") or not row.get("policyRef"):
        return None
    from .small_tower import SmallTowerSource
    if type(provider) is not SmallTowerSource or not provider.verify_receipt(receipt):
        raise PermissionError("Original Tower event required")
    candidates = provider.snapshot(int(row["sequence"]) - 1)["events"]
    if not any(candidate == row for candidate in candidates):
        raise PermissionError("Tower policy reference differs from original event")
    pid = row["policyRef"]
    rid = intention_id(pid)
    with closing(store.connect()) as db:
        prior = db.execute("SELECT * FROM commitments WHERE id=?", (rid,)).fetchone()
        policy = db.execute("SELECT selected_action FROM policy_decisions WHERE id=?", (pid,)).fetchone()
    if prior is None:
        return None
    if policy is None or prior["source"] != SOURCE_PREFIX + "tower:" + pid:
        raise PermissionError("Invalid Tower intention origin")
    action = policy["selected_action"]
    expected_op = "doctor_move" if action.startswith("move_") else action
    if row["operation"] != expected_op:
        raise PermissionError("Physical outcome does not match intended action")
    memory = store.get_memory(memory_id)
    expected_source = ("virtual-world:small-tower:" + receipt.world_epoch + ":"
                       + receipt.kind + ":" + receipt.event_id)
    if (not memory or not memory["active"] or memory["external"]
            or memory["evidence_class"] != "lived_runtime_memory"
            or memory["source"] != expected_source or memory["text"] != receipt.first_person
            or not memory.get("source_event_id")):
        raise PermissionError("Tower outcome lacks the exact admitted experience")
    status = "kept" if row["kind"] == "completed" else "broken"
    key = "telos:tower-outcome:" + pid
    result = {"commitment_id": rid, "origin_policy_id": pid, "status": status,
              "source_memory_id": memory_id, "source_event_id": memory["source_event_id"]}
    serialized = json.dumps(result, sort_keys=True)
    with store.transaction() as db:
        current = db.execute("SELECT status,outcome FROM commitments WHERE id=?", (rid,)).fetchone()
        existing = db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        if existing:
            if (existing["value"] != serialized or current["status"] != status
                    or current["outcome"] != memory["text"]):
                raise PermissionError("Conflicting Tower intention outcome")
            return result
        if current["status"] != "open" or current["outcome"] is not None:
            raise PermissionError("Tower intention closed without original physical receipt")
        db.execute("UPDATE commitments SET status=?,outcome=?,updated_tick=? WHERE id=?",
                   (status, memory["text"], store.tick, rid))
        store.set_meta(key, serialized, db)
        from .tower_prospective import complete
        complete(store, db, pid, result)
        store.bump_state_version(db)
    return result
