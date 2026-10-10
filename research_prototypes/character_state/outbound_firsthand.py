"""Outgoing response-firsthand claim guard: no generic narrator rewrite.

This is *not* a truth-conditional natural language model. It detects a
narrow class of explicit FIRST-PERSON ASSERTIVE event claims, verifies their
host-indexed question/source, and blocks unadmitted lived experience. Draft
texts are preserved for audit; only the approved outward reply changes.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from doctor_lives.cognition import PretoriusBrain
from .firsthand_gate import SAFE_REPLY
from .firsthand_router import (
    EventAlias, Intent, classify_firsthand, route_and_verify,
)
from .signed_world_receipts import SignedWorldReceipt, WorldHostVerifier


_AFFIRMATIVE = re.compile(
    r"\b(?:"
    r"I (?:personally |actually |clearly )?"
    r"(?:remember|recall|saw|heard|witnessed|observed|met|visited|"
    r"touched|held|inspected|attended|opened|found|entered|experienced|"
    r"walked|handled|finished|completed|revisited|examined|told|said|shared|showed|gave|handed)|"
    r"I (?:can |do )?(?:remember|recall)|"
    r"I have (?:seen|met|visited|attended|completed|finished|"
    r"reviewed|examined|inspected|witnessed|observed)|"
    r"I (?:was there|went there|spoke with|talked with|spoke to|talked to)|"
    r"We (?:met|spoke|talked|visited|witnessed|observed|"
    r"inspected|completed|finished)"
    r")\b",
    re.IGNORECASE,
)
_NON_EPISODIC = re.compile(
    r"\bI (?:remember|recall) (?:how to|the definition|the formula|"
    r"the meaning|the general rule|the principle)\b", re.IGNORECASE
)
_ELLIPTICAL_PAST_ASSENT = re.compile(
    r"^\\s*(?:yes[,.!]?[ \\t]+)?I did[.!?](?:\\s|$)", re.IGNORECASE,
)

_EXPLICIT_FICTION = re.compile(
    r"\b(?:imagine|pretend|suppose|fictional|in a story|"
    r"write a fictional|write an imaginary)\b", re.IGNORECASE,
)


def has_asserted_firsthand_claim(draft: str) -> bool:
    if not isinstance(draft,str):
        raise TypeError("generated text must be a string")
    if len(draft)>24000:
        raise ValueError("draft exceeds research guard text limit")
    if not draft.strip():
        return False
    text=_NON_EPISODIC.sub("",draft)
    return _AFFIRMATIVE.search(text) is not None


@dataclass(frozen=True)
class GuardedAnswer:
    question_intent: Intent
    draft_asserted_firsthand: bool
    disposition: str
    response: str
    changed: bool
    # Not a statement of true external world authenticity.
    signed_host_positive_fixture: bool


def protect_draft(
    brain: PretoriusBrain,
    question: str,
    draft: str,
    aliases: tuple[EventAlias,...],
    candidate_memory_ids: tuple[str,...],
    signed_receipts: tuple[SignedWorldReceipt,...],
    verifier: WorldHostVerifier,
) -> GuardedAnswer:
    """Apply only when a supported claim needs host source validation.

    If no affirmative claim is detected, keep existing dialogue exactly.
    For explicit creative fiction, do not assert historical truth and do not
    mistake its first-person character narrator for Pretorius testimony.
    """
    intent=classify_firsthand(question)
    asserted=(has_asserted_firsthand_claim(draft) or (
        intent is Intent.FIRSTHAND and _ELLIPTICAL_PAST_ASSENT.search(draft) is not None
    ))
    if not asserted:
        return GuardedAnswer(intent,False,"no_episodic_assertion",draft,False,False)
    if _EXPLICIT_FICTION.search(question):
        return GuardedAnswer(intent,True,"explicit_fiction_exempt",draft,False,False)
    routed=route_and_verify(
        brain,question,aliases,candidate_memory_ids,signed_receipts,verifier,
    )
    if routed.can_answer_firsthand and routed.disposition=="verified_lived_source":
        return GuardedAnswer(intent,True,"signed_source_admitted",draft,False,True)
    # The recognized output assertion cannot be justified by any indexed
    # verified event. Even for a generic user query, don't turn the model's
    # freely invented personal experience into a lived fact.
    return GuardedAnswer(
        intent,True,"unsupported_outbound_firsthand_assertion",SAFE_REPLY,
        draft!=SAFE_REPLY,False,
    )
