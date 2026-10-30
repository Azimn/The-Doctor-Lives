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
