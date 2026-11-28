"""Bounded Noesis appraisal of *lived*, source-verified work consequences.

This is a helper mechanism of the ONE original cognitive selector. Its inputs
are exclusively original BrainStore first-person memories and the current
first-person perception. Independently verifying world receipts belongs to
the trusted external Laboratory adapter, not to Noesis. No separate store,
neural policy, model, renderer or second action authority is introduced.
"""
from __future__ import annotations

import re

WORN = "My instruments look worn and will need attention."
EXPERIMENT_WEAR = "I complete a careful experiment at my workbench. The apparatus shows wear."
REPAIR_IMPROVEMENT = "I replace the worn component in my apparatus."
# Preregistered researcher-authored appraisal weights. They are NOT rewards
# issued by the host, discovered neural causal relationships, or motor grants.
WEAR_COST = -0.60
REPAIR_BENEFIT = 0.30


def consequence_pressure(brain, *, observation: str,
                         verified_outcome_memory_ids: tuple[str, ...],
                         feasible_actions: tuple[str, ...]) -> tuple[dict[str, float], list[str], list[str]]:
    """Return bounded per-action score changes and exact used memory IDs.

    Only one latest physically sourced outcome per action can contribute.
    No memory, reported story, authored fiction or stale context can be a
    source of action valuation. The world verifier controls the eligible list;
    we validate autobiographical membership a second time in Noesis.
    """
    if type(verified_outcome_memory_ids) is not tuple or len(verified_outcome_memory_ids) > 64 or any(
        type(mid) is not str for mid in verified_outcome_memory_ids
    ) or len(set(verified_outcome_memory_ids)) != len(verified_outcome_memory_ids):
        raise ValueError("Bounded unique verified outcome memory IDs required")
    scores = {action: 0.0 for action in feasible_actions}
    if WORN not in observation:
        return scores, [], []
    eligible = []
    latest = {}
    for mid in verified_outcome_memory_ids:
        m = brain.store.get_memory(mid)
        if (m is None or not m["active"]
                or m["evidence_class"] != "lived_runtime_memory"
                or m["external"]
                or not m["source"].startswith("laboratory-home:action:")):
            continue
        eligible.append(mid)
        text = " ".join(str(m["text"]).split())
        action, delta = None, 0.0
        if text == EXPERIMENT_WEAR and "experiment" in scores:
            action, delta = "experiment", WEAR_COST
        elif text == REPAIR_IMPROVEMENT and "repair" in scores:
            action, delta = "repair", REPAIR_BENEFIT
        if action is not None:
            candidate = (int(m["created_tick"]), mid, delta)
            if action not in latest or candidate > latest[action]:
                latest[action] = candidate
    used = []
    for action in sorted(latest):
        tick, mid, delta = latest[action]
        scores[action] = delta
        used.append(mid)
    return scores, eligible, used


# Developmental history is a bounded evidence-derived appraisal, not a new
# personality, external reward, learned neural weights, or motor authority.
HISTORY_VERSION = "work-history-appraisal-v2"
# Developmental contributions must compete with the existing 0.20 neural
# prior, not automatically override it on the first experience. This is a
# declared engineering scale, not a fitted or biologically measured value.
DEVELOPMENTAL_WEAR_COST = -0.08
DEVELOPMENTAL_REPAIR_BENEFIT = 0.04


def developmental_consequence_pressure(brain, *, observation: str,
                                      verified_outcome_memory_ids: tuple[str, ...],
                                      feasible_actions: tuple[str, ...]):
    """Accumulate independent autobiographical episodes, not replay counts.

    The legacy appraisal remains a separate control. This smaller first-event
    contribution can compete with rather than overwhelm the neural prior.
    Repeated independently verified experiences strengthen it
    with diminishing, capped influence. State is reconstructed from the
    canonical BrainStore on every opportunity, so archival and cold restart
    naturally remove or restore evidence. The host must authenticate custody.
    """
    if (type(verified_outcome_memory_ids) is not tuple
            or len(verified_outcome_memory_ids) > 64
            or any(type(mid) is not str for mid in verified_outcome_memory_ids)
            or len(set(verified_outcome_memory_ids)) != len(verified_outcome_memory_ids)):
        raise ValueError("Bounded unique verified outcome memory IDs required")
    scores = dict.fromkeys(feasible_actions, 0.0)
    if WORN not in observation:
        return scores, [], []
    episodes = {}
    for mid in verified_outcome_memory_ids:
        memory = brain.store.get_memory(mid)
        if (memory is None or not memory["active"] or memory["external"]
                or memory["evidence_class"] != "lived_runtime_memory"):
            continue
        match = re.fullmatch(r"laboratory-home:action:([0-9a-f]{64})", memory["source"])
        if match is None:
            continue
        content = " ".join(str(memory["text"]).split())
        action = ("experiment" if content == EXPERIMENT_WEAR else
                  "repair" if content == REPAIR_IMPROVEMENT else None)
        if action is None:
            continue
        # An aliased source event cannot strengthen a disposition twice.
        record = (int(memory["created_tick"]), mid, action)
        digest = match.group(1)
        if digest not in episodes or record < episodes[digest]:
            episodes[digest] = record
    ordered = sorted(episodes.values(), reverse=True)
    eligible = [row[1] for row in ordered]
    used = []
    for action, appraisal in (("experiment", DEVELOPMENTAL_WEAR_COST),
                              ("repair", DEVELOPMENTAL_REPAIR_BENEFIT)):
        if action not in scores:
            continue
        matching = [row[1] for row in ordered if row[2] == action]
        if matching:
            # Saturates at four independent episodes; no unbounded habit.
            effective = matching[:4]
            multiplier = 1.0 + sum(0.5 ** index for index in range(1, len(effective)))
            scores[action] = appraisal * multiplier
            used.extend(effective)
    return scores, eligible, used
