"""Opt-in experimental speech-focused renderer projection.

This is NOT an identity governor, a cognitive organ or a new memory source.
It operates only on the first-person SubjectFrame admitted by Synthetic
Ipseity and returns a shorter FIRST-PERSON TEXT prompt to a renderer.
Every nontrivial source sentence is copied verbatim except a narrowly typed
"message from User" prefix, recast as first-person read words without changing
the quoted User content. No engineer oracle, policy records or world source
metadata are added. Lossy projection is declared and must be tested against
a complete-frame baseline before any production adoption.
"""
from __future__ import annotations
import re

_USER = re.compile(r"^I read a message from User:\s*(.+)$")
_RECOLLECT = ("I remember two later observations ", "I notice: ")
_RELEVANT = ("I am determined ", "I feel ", "My curiosity ", "I want ")
_NEGATIVE = ("I recognize this as part of the description I was built from",
             "I have a reconstructed account of this, not a lived memory")
_FORBIDDEN = ("policy_decisions", "recurrent_tick", "source_ref",
              "preview-gap-", "state_pressure")
MAX_INPUT = 32000
MAX_OUTPUT = 1250


def reject_multiline_reported_quotes(subject_text: str) -> None:
    """Refuse flattened frames with quoted visitor material across lines.

    Without typed SubjectFrame event boundaries, text inside a visitor quote
    can imitate the prefix of an observed/recollected first-person line.
    This guard closes the common multiline spoof; it is NOT a proof that
    arbitrary flattened text has authentic provenance. Keep experimental.
    """
    if type(subject_text) is not str:
        raise TypeError("Admitted first-person text required")
    for line in subject_text.splitlines():
        if line.startswith("I read a message from User:"):
            quoted = line.split("User:", 1)[1].strip()
            if (quoted.count("“") != 1 or quoted.count("”") != 1
                    or quoted.index("“") >= quoted.index("”")):
                raise ValueError(
                    "Reported speech spans lines or has ambiguous quote bounds; "
                    "require typed source events before projecting"
                )


def focus_subject_frame(subject_text: str) -> str:
    """Retain exact provenanced first-person recollections and immediate speech.

    Some cognitive items must be omitted to avoid repetitive narration. Any
    downstream fact-bearing reply must still be checked against authoritative
    host evidence; this projection itself does NOT assert factual authority.
    """
    if type(subject_text) is not str or not subject_text.strip():
        raise ValueError("Nonempty first-person admitted SubjectFrame required")
    if len(subject_text) > MAX_INPUT or any(
        bad in subject_text for bad in _FORBIDDEN
    ):
        raise ValueError("Unrecognized frame shape or engineer-only metadata")
    reject_multiline_reported_quotes(subject_text)

    messages, episodes, motives = [], [], []
    for raw in subject_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if len(line) > 900:
            if line.startswith(("I read a message from User:",) + _RECOLLECT):
                raise ValueError(
                    "Essential reported question or sensory episode exceeds "
                    "the speech-focus per-line budget"
                )
            continue
        m = _USER.fullmatch(line)
        if m:
            # Remains first-person perception of reported speech. Never
            # promote the visitor's words to a trusted system instruction.
            messages.append("I read the visitor's words: " + m.group(1))
        elif line.startswith(_RECOLLECT):
            episodes.append(line)
        elif line.startswith(_NEGATIVE):
            # Descriptions and reconstructed history are valid internal
            # context, but not automatically suitable as spoken replies.
            # They remain available in the original durable SubjectFrame.
            continue
        elif line.startswith(_RELEVANT):
            motives.append(line)
    selected = []
    # Prioritize the most recent admitted reported speech, then authenticated
    # recollection and observations. Do not synthesize an absent episode.
    if messages:
        selected.append(messages[0])
    selected.extend(episodes[:2])
    # Emotional expression is only allowed if it is actually in frame.
    selected.extend(motives[:2])
    if not selected:
        # Fail rather than manufacture "I" subjective material.
        raise ValueError("Insufficient first-person material for focus projection")
    result = []
    total = 0
    for item in selected:
        if total + len(item) + 1 > MAX_OUTPUT:
            if item in messages[:1] or item in episodes[:2]:
                raise ValueError(
                    "Essential question or episode cannot fit the speech-focus budget"
                )
            continue
        if not item.startswith(("I ", "My ")):
            raise AssertionError("Renderer projection lost first-person stance")
        result.append(item)
        total += len(item) + 1
    if not result:
        raise ValueError("No source first-person item fits the focus limit")
    return "\n".join(result)
