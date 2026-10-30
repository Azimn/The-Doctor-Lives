"""Opt-in source-attested reading to subsequent physical work-action preference.

This is a *host-owned, bounded manual interpreter* for one research test,
NOT native Noesis goal authorship, a new neural policy, or general semantic
learning. The original Doctor owns memory; the Laboratory owns every actual
physical result. A page can suggest an action but cannot authorize execution.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import re

from .lab_home_bridge import DoctorHomeBridge, _row

_BASELINE = "experiment"
_WORK_ACTIONS = frozenset(("repair", "experiment"))
_WORN_CUE = "My instruments look worn and will need attention."
_MANUAL = re.compile(
    r"\bwhen my instruments look worn,\s*i should\s*"
    r"(?P<first>repair|experiment)\b.{0,90}?\bbefore i\s*"
    r"(?P<second>repair|experiment)\b",
    re.IGNORECASE,
)
_READ_SOURCE = "laboratory-home:action:"


@dataclass(frozen=True)
class BenchActionProposal:
    action: str
    observed_memory_id: str
    read_memory_id: str | None
    origin: str = "host_bounded_manual_interpreter"
    source_of_opportunity: str = "verified_laboratory_bench"
    authorization: str = "not_granted"


def _source_read_page(bridge: DoctorHomeBridge, memory_id: str) -> str | None:
    """Reconstruct page from original physical edition, never from hearsay.

    A legitimate directly read memory needs a matching unique world READ hash,
    replay-verified book and access proof, and exact normalized edition text.
    Unverified memories and absent/archived claims are not eligible evidence.
    """
    m = bridge.doctor.brain.store.get_memory(memory_id)
    if (m is None or not m["active"]
            or m["evidence_class"] != "lived_runtime_memory"
            or not m["source"].startswith(_READ_SOURCE)
            or not m["text"].startswith("I read a page of ")):
        return None
    receipt_hash = m["source"][len(_READ_SOURCE):]
    if not re.fullmatch(r"[0-9a-f]{64}", receipt_hash):
        return None

    # The world validates its entire physical book event, page and custody
    # chains. This is trusted host bookkeeping; none enters subject experience.
    from pretorius_lab.book_library import BookLibrary
    from pretorius_lab.physics import digest
    BookLibrary(bridge.world).verify()
    with bridge.world._open() as db:
        hits = db.execute(
            "SELECT event_id FROM books_events WHERE event_hash=?",
            (receipt_hash,),
        ).fetchall()
        if len(hits) != 1:
            return None
        receipt, verified_hash = _row(db, "books_events", hits[0][0])
        if verified_hash != receipt_hash:
            return None
        action = receipt.get("action", {})
        if action.get("op") != "read" or receipt.get("access_proof") is None:
            return None
        page_proof = receipt.get("page_receipt")
        if not isinstance(page_proof, dict):
            return None
        book_id = action.get("book_id")
        books_row = db.execute(
            "SELECT value FROM books_meta WHERE key='books'"
        ).fetchone()
        if books_row is None:
            return None
        book = json.loads(books_row[0]).get(book_id)
        if not isinstance(book, dict):
            return None
        edition = book["edition"]
        index = page_proof.get("page_number")
        if type(index) is not int or not 1 <= index <= len(edition["pages"]):
            return None
        page_text = edition["pages"][index - 1]
        if (digest(page_text) != page_proof.get("page_digest")
                or edition["content_digest"] != page_proof.get("edition_digest")):
            return None
    original_text = (
        "I read a page of " + edition["title"] + ". The words before me read: "
        + page_text
    )
    if " ".join(original_text.split()) != m["text"]:
        return None
    return page_text


def propose_bench_action(
    bridge: DoctorHomeBridge, *, read_memory_id: str | None,
    memory_enabled: bool = True,
) -> BenchActionProposal:
    """Derive a proposal from a *fresh* first-person bench observation.

    The policy is deliberately host-side and its baseline is documented. The
    only physical actions that can ever be proposed are experiment and repair.
    No operator-provided raw world state or book page can become a decision.
    """
    if not isinstance(bridge, DoctorHomeBridge):
        raise TypeError("Use an authorized original Doctor Laboratory bridge")
    if type(memory_enabled) is not bool:
        raise TypeError("Memory-ablation control must be boolean")
    if read_memory_id is not None and type(read_memory_id) is not str:
        raise TypeError("Memory identity must refer to the original BrainStore")
    if bridge.subject.embodied.verify()["station"] != "station:bench":
        raise PermissionError("Work decisions must be situated at the actual bench")

    observation = bridge.observe()
    perceived = bridge.doctor.brain.store.get_memory(observation["memory_id"])
    if (perceived is None or not perceived["active"]
            or perceived["evidence_class"] != "lived_runtime_memory"
            or not perceived["source"].startswith("laboratory-home:observe:")
            or perceived["text"] != observation["subject"]["inner"]):
        raise RuntimeError("Fresh first-person bench observation not admitted")

    selected = _BASELINE
    used = None
    if memory_enabled and read_memory_id is not None and _WORN_CUE in perceived["text"]:
        page = _source_read_page(bridge, read_memory_id)
        if page is not None:
            match = _MANUAL.search(" ".join(page.split()))
            if match and match.group("first").lower() != match.group("second").lower():
                action = match.group("first").lower()
                if action in _WORK_ACTIONS:
                    selected = action
                    used = read_memory_id
    return BenchActionProposal(
        action=selected, observed_memory_id=observation["memory_id"],
        read_memory_id=used,
    )


def execute_bench_action(
    bridge: DoctorHomeBridge, *, read_memory_id: str | None,
    event_id: str, expected_action: str, authorized_world_action: bool = False,
    memory_enabled: bool = True,
) -> dict:
    """Re-evaluate right before an explicitly authorized physical attempt.

    Never accept an arbitrary proposed motor command or an unverified page as
    authorization. The Laboratory decides if the requested action is feasible;
    only its hashed event and the original single-brain memory count as result.
    """
    if authorized_world_action is not True:
        raise PermissionError("A manual cannot grant physical action authority")
    if expected_action not in _WORK_ACTIONS:
        raise PermissionError("Unsupported physical work action")
    proposal = propose_bench_action(
        bridge, read_memory_id=read_memory_id, memory_enabled=memory_enabled,
    )
    if proposal.action != expected_action:
        raise RuntimeError("Action proposal has changed before execution")
    return bridge.act(proposal.action, event_id=event_id)
