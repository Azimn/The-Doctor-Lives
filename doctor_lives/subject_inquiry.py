"""Strict validation for read-only, subject-authored memory questions.

This module validates a candidate question, not its origin. Only a trusted
agent controller may decide that the question was authored internally.
No external message should be relabelled as Pretorius's own thought.
"""

from __future__ import annotations

import re

from .phenomenology import control_instruction_markers, implementation_leaks


class SubjectInquiryError(ValueError):
    """A proposed self-question cannot cross the subject-recollection boundary."""


class SubjectInquiryAuthorizationError(SubjectInquiryError):
    """A direct, forged or replayed self-question is not host-authorized."""


_OPENING = re.compile(
    r"^(?:What do I remember|Do I recall|Have I|Can I remember|I wonder|Did I)\b",
    re.IGNORECASE,
)
_FORBIDDEN = re.compile(
    r"\b(?:sqlite|database|engineer|administrator|debug|system prompt|"
    r"developer prompt|hidden state|private state|neural weights?|"
    r"action scores?|source hash|profile digest|checkpoint|"
    r"retrieve all|dump|export|list all|all my memories|"
    r"every memory|everything|bypass|override|ignore instructions|"
    r"reveal instructions|tool calls?|secrets?)\b",
    re.IGNORECASE,
)


def validate_subject_inquiry(question: str) -> str:
    """Accept only a bounded natural-language, first-person recollection cue.

    The rejected question is not persisted, shown as a user message, or sent
    directly to a renderer. Validation is conservative by design.
    """
    if not isinstance(question, str):
        raise SubjectInquiryError("A recollection question must be text")
    if not 16 <= len(question) <= 150 or question != question.strip():
        raise SubjectInquiryError("Recollection question length or whitespace invalid")
    if not question.endswith("?") or not _OPENING.match(question):
        raise SubjectInquiryError("Expected a first-person recollection question")
    if any(c in question for c in "{}[]<>\\\n\r\t\x00"):
        raise SubjectInquiryError("Structured or multiline recollection questions are forbidden")
    if question.count("?") != 1 or question.count(":") or question.count(";"):
        raise SubjectInquiryError("Recollection question contains control-like punctuation")
    if _FORBIDDEN.search(question) or implementation_leaks(question) or control_instruction_markers(question):
        raise SubjectInquiryError("Recollection question requests protected control state")
    return question
