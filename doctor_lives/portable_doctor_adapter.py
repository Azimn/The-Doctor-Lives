"""Optional, non-executing adapter from real Doctor cognition to portable game AI.

The caller must source and authorize affordances from subject-accessible events.
No Laboratory-only sensors, hidden physical state, identity data or second brain.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Mapping, Sequence

from .portable_life_policy import DecisionFrame, Opportunity, PortableLifePolicy


def advise_doctor(bridge, policy: PortableLifePolicy,
                  opportunities: Sequence[Opportunity],
                  *, motives: Mapping[str, float],
                  native_to_strategy: Mapping[str, str],
                  goal_ids=(), cue: str = "general", commit: bool = False):
    """Call the unchanged real Doctor's neural cognition after verified ingress.

    Requires an authorized DoctorHomeBridge-like source adapter. Engine receives
    only source-derived first-person text plus supplied cognitive motive input.
    An untrusted renderer must not supply the opportunity set or motive vector.
    This returns an engineer-only advisory decision, never a physical action.
    """
    if not isinstance(policy, PortableLifePolicy):
        raise TypeError("A portable cognitive policy is required")
    observed = bridge.observe()
    subject = observed["subject"]
    if set(subject) != {"inner", "spoken_aloud"}:
        raise ValueError("Unverified subject frame fields")
    native = bridge.request_cognition(trigger="portable_life_advisory")
    scores = defaultdict(float)
    for action, value in native["action_scores"].items():
        if action in native_to_strategy:
            scores[native_to_strategy[action]] += float(value)
    scores = {name: min(1.0, value) for name, value in scores.items()}
    decision = policy.choose(DecisionFrame(
        first_person=subject["inner"], source_event=observed["memory_id"],
        motives=motives, goal_ids=frozenset(goal_ids),
        native_strategy_scores=scores, cue=cue), list(opportunities),
        commit=commit)
    return {"advice": decision,
            "neural_policy_decision_id": native["policy_decision_id"],
            "observed_memory_id": observed["memory_id"]}
