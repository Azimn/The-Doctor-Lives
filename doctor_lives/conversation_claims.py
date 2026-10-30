"""Source-indexed outbound firsthand speech gate.

Adapted from research/outbound-firsthand-claim-gate-stage03-20261009
at 361ac5e1607b2a1a3457306fb1ad218c49328146, specifically
research_prototypes/character_state/outbound_firsthand.py and
tests/test_outbound_firsthand_stage03.py. The research prototype used a
fixture receipt signer. This adaptation uses real canonical BrainStore
memories plus original Laboratory and OperatorWork receipts instead.
A lexical detector is NOT a general semantic theorem prover; model lines are
unverified unless they are exact copies of source-backed safe claims.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

# Include additional common M6 verbs absent from the donor's original list.
_FIRSTHAND = re.compile(
    r"\b(?:I|we)\s+(?:(?:have|had)\s+)?(?:personally\s+|actually\s+)?"
    r"(?:read|wrote|written|fixed|repaired|lit|finished|completed|"
    r"remember|recalled|recall|observed|witnessed|saw|seen|heard|"
    r"visited|met|inspected|opened|found|took|walked|worked|"
    r"experimented|made|built|created|sent|received|spoke|"
    r"recorded|documented|wished|wanted|thought|remembered|"
    r"reviewed|revisited|touched|held|attended|entered|handed|"
    r"told|gave|shared|showed|experienced|handled|examined)\b",
    re.I,
)
_FIRST_PERSON = re.compile(r"\b(?:I|my|mine|we|our)\b", re.I)
_MODEL_LINE = re.compile(r"(?<=[.!?])\s+|\n+")

@dataclass(frozen=True)
class GuardResult:
    text: str
    claims: tuple[dict, ...]
    blocked_drafts: tuple[str, ...]
    model_unverified: tuple[str, ...]

def has_asserted_firsthand_claim(value: str) -> bool:
    if not isinstance(value, str):
        raise TypeError("Reply must be text")
    # The source donor's elliptical affirmative first-person answer is still
    # a historical event claim when presented without a receipt.
    if re.match(r"^\s*(?:yes[,.!]?[ \t]+)?I did[.!?](?:\s|$)",value,re.I):
        return True
    neutral = re.sub(
        r"\bI (?:remember|recall) (?:how to|the definition|the formula|"
        r"the meaning|the general rule|the principle)\b",
        "",value,flags=re.I)
    return bool(_FIRSTHAND.search(neutral))

def admit_model_draft(draft: str, verified_claims: list[dict]) -> GuardResult:
    """Model may quote exact independently verified sentences, not mint events.

    Any model-first-person sentence not found verbatim in the source ledger
    is withheld. Unverified third-person commentary is explicitly marked and
    never written into lived memory.
    """
    if not isinstance(draft, str) or len(draft) > 4096:
        raise ValueError("Local model reply must be bounded text")
    sources = {c["text"].strip(): c for c in verified_claims}
    kept, claims, blocked, unverified = [], [], [], []
    for line in _MODEL_LINE.split(draft.strip()):
        part = " ".join(line.split())
        if not part:
            continue
        if part in sources:
            kept.append(part); claims.append(dict(sources[part]))
        elif has_asserted_firsthand_claim(part) or _FIRST_PERSON.search(part):
            blocked.append(part)
        else:
            # Neither model analysis nor free-language narration becomes
            # evidence about Pretorius's private historical existence.
            unverified.append(part)
    if unverified:
        kept.append("Unverified local-model commentary: " + " ".join(unverified)[:350])
    return GuardResult(" ".join(kept),tuple(claims),tuple(blocked),tuple(unverified))
