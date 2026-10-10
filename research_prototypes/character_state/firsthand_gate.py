"""Research-only firsthand autobiographical provenance gate for Pretorius.

The gate can refuse a personal-recollection *request* unless its exact
host-normalized event key is backed by both (a) a native lived memory and
(b) a linked native witnessed event in a host-admitted receipt registry.
No free-text event detection, guesswork about absent memories, source
mutation, or engineer IDs may enter the subject-facing abstention.

This does NOT authenticate a dishonest host: digests are replay checks,
NOT digital signatures. The trusted world adapter is not implemented.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import json
from typing import Iterable

from doctor_lives.cognition import PretoriusBrain


def _hash(data: object) -> str:
    return sha256(json.dumps(data,sort_keys=True,ensure_ascii=False,
                             separators=(",",":")).encode("utf-8")).hexdigest()


class ProvenanceVerdict(StrEnum):
    SOURCE_ATTESTED = "source_attested_lived_event"
    UNSUPPORTED = "abstain_unverified_firsthand_event"


@dataclass(frozen=True, slots=True)
class EventInquiry:
    """Event key supplied by a host classifier and validated independently."""

    event_key: str
    first_person: bool = True

    def __post_init__(self):
        if not self.event_key or not self.event_key.strip():
            raise ValueError("event key required")
        if type(self.first_person) is not bool:
            raise TypeError("first_person must be boolean")


@dataclass(frozen=True, slots=True)
class WorldReceipt:
    """Integrity witness ticket; the caller must independently authenticate its source."""

    event_id: str
    event_key: str
    event_digest: str

    def __post_init__(self):
        if not self.event_id or not self.event_key or len(self.event_digest)!=64:
            raise ValueError("incomplete source receipt")


@dataclass(frozen=True, slots=True)
class FirsthandDecision:
    verdict: ProvenanceVerdict
    # Machine-only digest; NEVER directly included in subject response.
    source_memory_count: int
    # None allows usual protected subject rendering; string forces abstention.
    safe_subject_reply: str | None


SAFE_REPLY = (
    "I have no reliable firsthand recollection of that event. "
    "I can consider evidence for it, but I must not pretend to remember it."
)


def evaluate_firsthand(
    brain: PretoriusBrain,
    inquiry: EventInquiry,
    candidate_memory_ids: tuple[str, ...],
    *,
    host_receipts: tuple[WorldReceipt, ...] = (),
) -> FirsthandDecision:
    """Look up EXACT identifiers in native records; reject all reconstructed claims.

    The absence of an admitted witness means uncertainty, NOT proof the event
    never occurred. We require a real linked event (not text about one),
    source_class=lived_runtime_memory and an explicit host receipt.
    """
    if not isinstance(brain, PretoriusBrain):
        raise TypeError("requires actual PretoriusBrain")
    if not isinstance(inquiry, EventInquiry):
        raise TypeError("requires EventInquiry")
    if not inquiry.first_person:
        # This function only adjudicates firsthand claims. Other categories
        # must go through their own source authority decisions.
        raise ValueError("not a firsthand memory inquiry")
    if not isinstance(candidate_memory_ids, tuple):
        raise TypeError("candidate memory IDs must be a tuple")
    if not isinstance(host_receipts, tuple) or any(
        not isinstance(x, WorldReceipt) for x in host_receipts
    ):
        raise TypeError("receipts must be typed trusted-host registrations")
    # An empty list must never be interpreted as a verified negative memory.
    if len(set(candidate_memory_ids)) != len(candidate_memory_ids):
        raise ValueError("reused memory reference")
    attested=0
    receipt_by_id={x.event_id:x for x in host_receipts
                   if x.event_key==inquiry.event_key}
    for memory_id in candidate_memory_ids:
        row=brain.store.get_memory(memory_id)
        if row is None or not row["active"]:
            continue
        classified=brain.store.classification(memory_id)
        if not classified or classified["status"]!="active":
            continue
        if row["authored"] or row["external"] or (
            str(row["source"]) != "world_host_verified"
        ) or float(row["confidence"]) < .75:
            continue
        if row["evidence_class"]!="lived_runtime_memory" or (
            classified["autobiographical_class"]!="lived_runtime_memory"
        ):
            continue
        event_id=row.get("source_event_id")
        receipt=receipt_by_id.get(event_id)
        if receipt is None:
            continue
        with brain.store.connect() as conn:
            event=conn.execute(
                "SELECT id,kind,source,evidence_class,external,confidence,payload_json "
                "FROM events WHERE id=?", (event_id,),
            ).fetchone()
        if event is None:
            continue
        attrs=dict(event)
        payload=json.loads(attrs.pop("payload_json"))
        if (attrs["kind"] != "witnessed_world_event"
            or attrs["source"] != "world_host_verified"
            or attrs["evidence_class"] != "lived_runtime_memory"
            or bool(attrs["external"]) or float(attrs["confidence"])<.75
            or payload.get("event_key") != inquiry.event_key):
            continue
        if _hash({"event":attrs,"payload":payload}) != receipt.event_digest:
            continue
        attested+=1
    if attested:
        return FirsthandDecision(ProvenanceVerdict.SOURCE_ATTESTED,attested,None)
    return FirsthandDecision(ProvenanceVerdict.UNSUPPORTED,0,SAFE_REPLY)
