"""One narrow Mnemosyne-to-Noesis influence on situated book selection.

This is a *preference experiment*, not independent goal authorship. It uses
ONLY Doctor's active lived memories of actual source-backed book reads to
prefer an unread physical book over one previously read, among candidates
already found in the current locally verified shelf observation.

The simple deterministic no-memory controller remains the ID-order baseline.
No full page content, engineering score, remote catalog or hidden world state
is transmitted into the Doctor's subjective rendering.
"""
from __future__ import annotations

from .lab_home_bridge import _row
from .six_organ_book_task import _BOOK


def choose_visible_book(candidates: list[str], *, store, world,
                        memory_enabled: bool = True) -> str:
    """Return a bounded source-verified preference, never a physical permission.

    Candidate identities must already have passed current source-backed LOOK,
    installation and canonical sighting checks in EndogenousBookPursuit.
    Require world receipt support before treating a remembered read as fact.
    This choice does not read or reveal any page. Stable ID order supplies
    the identical-information no-memory baseline and honest fallback.
    """
    if type(candidates) is not list or not candidates:
        raise ValueError("At least one currently witnessed book is required")
    if any(type(b) is not str or _BOOK.fullmatch(b) is None for b in candidates):
        raise ValueError("Invalid observed book identity")
    if type(memory_enabled) is not bool:
        raise TypeError("Memory ablation switch must be boolean")
    options = sorted(set(candidates))
    if not memory_enabled or len(options) == 1:
        return options[0]

    lived = [
        m for m in store.memories()
        if m["active"] and m["evidence_class"] == "lived_runtime_memory"
        and m["source"].startswith("laboratory-home:action:")
        and m["text"].startswith("I read a page of ")
    ]
    previously_read = set()
    with world._open() as db:
        for memory in lived:
            checksum = memory["source"].removeprefix("laboratory-home:action:")
            if len(checksum) != 64:
                continue
            hits = db.execute(
                "SELECT event_id FROM books_events WHERE event_hash=?",
                (checksum,),
            ).fetchall()
            if len(hits) != 1:
                continue
            receipt, digest = _row(db, "books_events", hits[0]["event_id"])
            action = receipt.get("action", {})
            book_id = action.get("book_id")
            if (digest == checksum and action.get("op") == "read"
                    and book_id in options and receipt.get("page_receipt")
                    and receipt.get("access_proof")):
                previously_read.add(book_id)
    return min(options, key=lambda b: (b in previously_read, b))
