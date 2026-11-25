"""Developmental consequence appraisal on the original Tower and BrainStore.

Adapts noesis_consequences developmental saturation and source deduplication
to source-attested Telos outcomes, not an additional learning database. A
completed activity establishes contextual task reliability, not subjective
reward, material utility, skill mastery or a neural learning breakthrough.
"""
from contextlib import closing
import json
import re

VERSION = "tower-contextual-consequence-v1"
SUCCESS = .015
FAILURE = -.05
CAP = .08
ROOM = re.compile(r"^I am in my [^.!?]+\.")
EVENT = re.compile(r"L([0-9]+)-[a-f0-9]{32}")


def _room(text):
    match = ROOM.match(text)
    return match.group(0) if match else None


def _appraise(episodes, feasible, *, repeated_unchanged=None):
    """At most four recent independent outcomes per feasible concrete action.

    A reliable action is not an independent reason to repeat it immediately
    in the exact same perceived context. Suppress its positive reliability
    contribution only; retain its failures and their original recency weights.
    """
    scores = dict.fromkeys(feasible, 0.0)
    used = {action: [] for action in feasible}
    counts = dict.fromkeys(feasible, 0)
    seen = set()
    for action, success, memory_id, source_id in episodes:
        if action not in scores or source_id in seen or counts[action] >= 4:
            continue
        seen.add(source_id)
        weight = .5 ** counts[action]
        counts[action] += 1
        if action == repeated_unchanged and success:
            continue
        scores[action] += weight * (SUCCESS if success else FAILURE)
        used[action].append(memory_id)
    scores = {action: max(-CAP, min(CAP, value)) for action, value in scores.items()}
    return scores, used


def verified_consequence_pressure(brain, provider, observation, feasible):
    """Recheck original event, protected intention and same perceived room."""
    from .small_tower import SmallTowerSource
    if type(provider) is not SmallTowerSource:
        raise PermissionError("Original Tower source required")
    store = brain.store
    current = provider.observe()
    prefix = "virtual-world:small-tower:" + current.world_epoch + ":"
    if (not observation["active"] or observation["external"]
            or observation["evidence_class"] != "lived_runtime_memory"
            or observation["source"] != prefix + "observation:" + current.event_id
            or observation["text"] != current.first_person):
        raise PermissionError("Development requires current admitted perception")
    room = _room(observation["text"])
    if not room:
        return _appraise((), feasible)
    with closing(store.connect()) as db:
        candidates = db.execute(
            "SELECT c.id,c.status,c.outcome,p.id AS policy_id,p.selected_action,"
            "p.state_pressure_json FROM commitments c JOIN policy_decisions p "
            "ON c.source='telos:native:tower:'||p.id "
            "WHERE c.status IN ('kept','broken') AND p.trigger='noesis_world_affordance' "
            "ORDER BY c.updated_tick DESC,c.id DESC LIMIT 64").fetchall()
    pending = []
    for row in candidates:
        action = row["selected_action"]
        if action not in feasible or action.startswith("move_"):
            continue
        origin = json.loads(row["state_pressure_json"])
        context = store.get_memory(origin["observation_memory_id"])
        if (not context or not context["active"] or context["external"]
                or context["evidence_class"] != "lived_runtime_memory"
                or not context["source"].startswith(prefix + "observation:")
                or _room(context["text"]) != room):
            continue
        report_raw = store.meta("telos:tower-outcome:" + row["policy_id"])
        if report_raw is None:
            raise PermissionError("Closed native intention lacks its physical outcome")
        report = json.loads(report_raw)
        memory = store.get_memory(report["source_memory_id"])
        # Retention and archival may remove an episode from current appraisal.
        if not memory or not memory["active"]:
            continue
        success = row["status"] == "kept"
        kind = "action" if success else "observation"
        source = prefix + kind + ":"
        if (report["commitment_id"] != row["id"]
                or report["origin_policy_id"] != row["policy_id"]
                or report["status"] != row["status"]
                or memory["external"] or memory["evidence_class"] != "lived_runtime_memory"
                or memory["text"] != row["outcome"]
                or memory.get("source_event_id") != report["source_event_id"]
                or not memory["source"].startswith(source)):
            raise PermissionError("Developmental outcome differs from canonical intention")
        event_id = memory["source"][len(source):]
        match = EVENT.fullmatch(event_id)
        if not match:
            raise PermissionError("Invalid physical outcome source identity")
        pending.append((int(match.group(1)), action, success, memory, row["policy_id"], context["text"]))
    if not pending:
        return _appraise((), feasible)
    history = provider.snapshot(min(item[0] for item in pending) - 1)
    if provider._observation(history) != current:
        raise PermissionError("Tower changed during consequence appraisal")
    by_sequence = {r["sequence"]: r for r in history["events"]}
    verified = []
    latest = max((r["sequence"] for r in history["events"]
                  if r["kind"] in ("completed","action_failed") and r.get("policyRef")), default=-1)
    repeated_unchanged = None
    for sequence, action, success, memory, pid, prior_text in sorted(pending, key=lambda x: -x[0]):
        row = by_sequence.get(sequence)
        if (not row or row["policyRef"] != pid or row["operation"] != action
                or row["kind"] != ("completed" if success else "action_failed")):
            raise PermissionError("Original consequence differs from native intention")
        receipt = provider.event_receipt(row)
        expected = prefix + receipt.kind + ":" + receipt.event_id
        if memory["source"] != expected or memory["text"] != receipt.first_person:
            raise PermissionError("Original consequence differs from lived memory")
        verified.append((action, success, memory["id"], expected))
        if sequence == latest and success and prior_text == observation["text"]:
            repeated_unchanged = action
    return _appraise(verified, feasible, repeated_unchanged=repeated_unchanged)
