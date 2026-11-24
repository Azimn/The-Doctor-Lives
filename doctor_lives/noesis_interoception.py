"""Bounded one-direction regulatory pressure from admitted Laboratory cues.

Mechanism precedent: DUCK duck/body_v010.py at
30a11ea8308ebd0fc89a06bb994ab0e23bd02886 separates physical state from
regulatory pressure. No DUCK body, identity or store is imported.
The source grammar is Pretorius-Laboratory 6e49795752835d64fa6fd63d16359669a1ca2ba7
daily_rhythm._perceive. This is not open-domain language comprehension.
No hidden physical state or motor authority enters this adapter.
"""
from __future__ import annotations
import re

_PREFIX = re.compile(
    r"^I am in [^.!?\r\n]+\. "
    r"(?:It is too dark to make out the furnishings clearly\.|"
    r"There is daylight enough to see\.|The lamp gives me enough light to see\.)"
)
# Initial engineering coefficients, not a claim of human equivalence.
# Maximum contribution equals the existing situated neural prior weight.
_CUES = (
    (
        ("I feel worn out and find it hard to concentrate.", "worn_out",
         {"rest": 0.18, "sleep": 0.20}),
        ("I am getting tired.", "tired", {"rest": 0.09, "sleep": 0.04}),
    ),
    (
        ("I am painfully hungry.", "painfully_hungry",
         {"eat": 0.20, "prepare_meal": 0.16}),
        ("I could do with something to eat.", "hungry",
         {"eat": 0.10, "prepare_meal": 0.08}),
    ),
    (
        ("My mouth is dry.", "thirsty", {"brew_tea": 0.20}),
    ),
)


def perceived_regulatory_pressure(
    observation: str, feasible_actions: tuple[str, ...],
) -> tuple[dict[str, float], tuple[str, ...]]:
    """Return bounded contributions to already feasible alternatives.

    Match the leading ordered rhythm clauses, not arbitrary quoted text in
    the rest of the scene. Absent or unknown cues add no pressure. This is
    a stateless calculation; the original Noesis commits the decision.
    """
    scores = {action: 0.0 for action in feasible_actions}
    cues = []
    prefix = _PREFIX.match(observation)
    if prefix is None:
        return scores, ()
    remainder = observation[prefix.end():].lstrip()
    for alternatives in _CUES:
        for phrase, cue, contributions in alternatives:
            if remainder == phrase or remainder.startswith(phrase + " "):
                remainder = remainder[len(phrase):].lstrip()
                cues.append(cue)
                for action, pressure in contributions.items():
                    if action in scores:
                        scores[action] = min(0.20, scores[action] + pressure)
                break
    return scores, tuple(cues)
