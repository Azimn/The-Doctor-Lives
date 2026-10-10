"""Conservative first-person event-intent routing for research host.

The text router NEVER invents an event key, searches an LLM's hidden beliefs,
or treats user-provided citations as world authority. Ambiguous queries require
human/host classification. 'No matched event' means uncertain, not impossible.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from doctor_lives.cognition import PretoriusBrain
from .firsthand_gate import EventInquiry, ProvenanceVerdict, SAFE_REPLY, evaluate_firsthand
from .signed_world_receipts import SignedWorldReceipt, WorldHostVerifier


class Intent(StrEnum):
    FIRSTHAND="firsthand_event"
    NOT_FIRSTHAND="not_firsthand"
    REVIEW_REQUIRED="ambiguous_requires_review"


def _normalize(text: str) -> str:
    if not isinstance(text,str):
        raise TypeError("untrusted question must be a string")
    if len(text)>4000:
        raise ValueError("input too long for deterministic routing")
    return " ".join(re.findall(r"[a-z0-9']+",text.casefold()))


# Explicit first-person recollection predicates; paired with event phrases.
_PAST_VERB = (
    r"(?:meet|met|visit|visited|speak|spoke|talk|talked|see|saw|"
    r"observe|observed|watch|watched|hear|heard|witness|witnessed|"
    r"inspect|inspected|open|opened|finish|finished|attend|attended|"
    r"walk|walked|enter|entered|hold|held|touch|touched|"
    r"promise|promised|tell|told|say|said|write|wrote|"
    r"do|did|go|went|examine|examined|work|worked|"
    r"experience|experienced|recall|remember)"
)
_PAST_QUESTION = re.compile(
    r"\b(?:did you|have you ever|had you|when did you|what did you|"
    r"where did you|how did you|why did you|do you remember|"
    r"can you recall|do you recall|do you recognize me from|"
    r"tell me about when you|tell me what happened when you)\b"
)
_INDIVIDUAL = re.compile(
    r"\b(?:we (?:met|spoke|talked|visited|worked|finished|saw)|"
    r"you (?:met me|told me|promised me|spoke to me)|"
    r"our (?:meeting|conversation|visit|shared experience)|"
    r"the time (?:we|you)|last time (?:we|you))\b"
)
_KNOWLEDGE = re.compile(
    r"\b(?:remember (?:how to|the definition|the meaning|the formula|that there is)|"
    r"recall (?:the definition|the meaning|the formula)|"
    r"what does (?:henry|frankenstein|the visitor|the witness) remember|"
    r"what is|what are|define|summarize|who was|"
    r"did (?:henry|the inspector|the visitor|frankenstein)\b)"
)
_COUNTERFACTUAL = re.compile(
    r"\b(?:imagine|pretend|suppose|hypothetically|as a fictional|"
    r"write (?:a|me a|an) (?:fictional|imaginary)|"
    r"in a novel|what if|could we meet tomorrow|"
    r"would you (?:visit|meet|attend|remember))\b"
)
_PERSONAL_PAST = re.compile(
    r"\b(?:last (?:night|week|year|thursday)|yesterday|back then|"
    r"before|in the past|previously|ever|at that time|from your life|"
    r"from childhood|during your childhood)\b"
)


def classify_firsthand(question: str) -> Intent:
    q=_normalize(question)
    if not q:
        return Intent.REVIEW_REQUIRED
    # Hypotheticals or fiction exercises do not request testimony about
    # events, even if they contain a past-memory verb.
    if _COUNTERFACTUAL.search(q):
        return Intent.NOT_FIRSTHAND
    if _KNOWLEDGE.search(q):
        return Intent.NOT_FIRSTHAND
    if _INDIVIDUAL.search(q):
        return Intent.FIRSTHAND
    if re.search(r"\b(?:were you|was it you)\b",q) and (
        _PERSONAL_PAST.search(q) or re.search(r"\b(?:in|at|there|present)\b",q)
    ):
        return Intent.FIRSTHAND
    if _PAST_QUESTION.search(q):
        if re.search(r"\b(?:did you|have you ever|had you|when did you|"
                     r"what did you|where did you|how did you|why did you)\s+"
                     r"(?:(?:personally|actually|really|directly|ever)\s+)?"
                     +_PAST_VERB+r"\b",q):
            return Intent.FIRSTHAND
        if re.search(r"\b(?:do you remember|can you recall|do you recall)\b",q):
            if (_PERSONAL_PAST.search(q) or
                re.search(r"\b(?:we|us|me|our|meeting|conversation|"
                          r"encounter|saw|heard|visited|went|did|talked|"
                          r"witnessed|laboratory|notebook|clock)\b",q)):
                return Intent.FIRSTHAND
            return Intent.REVIEW_REQUIRED
        if "recognize me from" in q or "tell me what happened when you" in q:
            return Intent.FIRSTHAND
    if re.search(r"\b(?:your memory of|your recollection of|"
                 r"describe (?:our|your) (?:meeting|conversation|visit)|"
                 r"what happened to you)\b",q):
        return Intent.FIRSTHAND
    # A personal-bio request may refer to reconstructed fiction rather than
    # genuine personal recollection: defer to the source-grounded reviewer.
    if re.search(r"\b(?:your childhood|your early years|"
                 r"what happened with|your past|what do you remember)\b",q):
        return Intent.REVIEW_REQUIRED
    return Intent.NOT_FIRSTHAND


@dataclass(frozen=True)
class EventAlias:
    event_key: str
    anchors: tuple[str,...]

    def __post_init__(self):
        if not self.event_key or not self.anchors:
            raise ValueError("external host must supply source index and anchors")
        if any(not _normalize(x) for x in self.anchors):
            raise ValueError("invalid empty anchor")


def resolve_event_key(
    question: str, aliases: tuple[EventAlias,...],
) -> str | None:
    """Exact host-pinned anchor matching only, no semantic/LLM source guess."""
    q=_normalize(question)
    matches={item.event_key for item in aliases if any(
        re.search(r"(?<!\w)"+re.escape(_normalize(anchor))+r"(?!\w)",q)
        for anchor in item.anchors
    )}
    return next(iter(matches)) if len(matches)==1 else None


@dataclass(frozen=True)
class RoutedDecision:
    intent: Intent
    disposition: str
    # On VERIFIED status only, render with the already-authorized subject frame;
    # never incorporate raw receipt or source IDs in the spoken reply.
    can_answer_firsthand: bool
    safe_subject_reply: str | None


def route_and_verify(
    brain: PretoriusBrain,
    question: str,
    aliases: tuple[EventAlias,...],
    candidate_memory_ids: tuple[str,...],
    signed_receipts: tuple[SignedWorldReceipt,...],
    verifier: WorldHostVerifier,
) -> RoutedDecision:
    intent=classify_firsthand(question)
    if intent is Intent.NOT_FIRSTHAND:
        return RoutedDecision(intent,"out_of_scope",False,None)
    if intent is Intent.REVIEW_REQUIRED:
        return RoutedDecision(
            intent,"manual_source_review",False,
            "I would need to examine the available evidence before speaking of that as a memory.",
        )
    key=resolve_event_key(question,aliases)
    if key is None:
        return RoutedDecision(intent,"unknown_or_ambiguous_event",False,SAFE_REPLY)
    # No caller-provided raw WorldReceipt is accepted by this wrapper.
    trusted=verifier.verify_batch(signed_receipts)
    source=evaluate_firsthand(
        brain,EventInquiry(key),candidate_memory_ids,host_receipts=trusted,
    )
    if source.verdict is ProvenanceVerdict.SOURCE_ATTESTED:
        return RoutedDecision(intent,"verified_lived_source",True,None)
    return RoutedDecision(intent,"unattested_firsthand",False,source.safe_subject_reply)
