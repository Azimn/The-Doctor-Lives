"""Live first-person boundary using the original pinned Ipseity governor.

The governor is a linguistic gate, not evidence authority. Only the admitted
natural-language subject frame enters a renderer. Raw IDs, scores, source
metadata, world state and model instructions never become subject experience.
"""
from __future__ import annotations
import re
from .self_reference_governor import ReferenceBindings, ReferenceContext, SelfReferenceGovernor
from .phenomenology import implementation_leaks, control_instruction_markers

DONOR_COMMIT = "a70a7e9fc61ddf1706d27bfa0b0edf3caf71b7fa"
_BINDINGS = ReferenceBindings("pretorius", "Doctor Septimus Pretorius",
                             ("Pretorius", "Septimus", "Doctor Pretorius", "Dr. Pretorius"))
_CONTEXT = ReferenceContext("pretorius", addressee_subject_id="operator")
_GOVERNOR = SelfReferenceGovernor()
_FIRST = re.compile(r"^(?:I\b|My\b|Mine\b|Me\b)", re.I)
# The original governor licenses vocatives based on addressee identity.
# In this product's own voice, addressing one's own name is never licensed.
_SELF_ADDRESS = re.compile(
    r"(?:^|[.!?]\s*|\n\s*)(?:Doctor Septimus Pretorius|Doctor Pretorius|Dr\. Pretorius|Pretorius|Septimus)\s*,"
    r"|\bI\s+(?:want|wish|need|seek|hope|yearn)\s+(?:Doctor Septimus Pretorius|Pretorius|Septimus)\b",
    re.I)
_ENGINEERING = re.compile(r"\b(?:world_epoch|centibeats|policyRef|sourceEventId|candidate_final_scores|neural_tick|policy_decision_id|neural_checkpoint_sha256)\b|\b(?:mem|policy|event)_[a-f0-9]{16,}\b", re.I)
_FALLBACK = "I cannot put that into words with confidence."


def first_person_line(text):
    if type(text) is not str or not text.strip():
        raise ValueError("Subject content must be natural language")
    text = text.strip()
    if implementation_leaks(text) or control_instruction_markers(text) or _ENGINEERING.search(text):
        return "I cannot make sense of that material."
    if not _FIRST.match(text):
        # Older inherited/reference material can have third-person wording.
        # Do not mechanically convert names into lived first-person claims.
        return "I have this account in mind, without claiming I witnessed it: “" + text + "”"
    return text


def admissible_output(text):
    if type(text) is not str or not text.strip():
        return False
    if implementation_leaks(text) or control_instruction_markers(text) or _ENGINEERING.search(text):
        return False
    score = _GOVERNOR.check(text, _BINDINGS, _CONTEXT)
    # No raw control text or self-address, even if the original rule's
    # addressee is not the speaker. Other people may still be mentioned.
    own = re.sub(r'“[^”]*”|"[^"\n]*"', " ", text)
    return score.accepted and not _SELF_ADDRESS.search(own) and bool(_FIRST.match(text.strip()))


def govern_renderer(render):
    """One admitted narrative input, one first-person response or honest fallback."""
    def guarded(subject):
        narrative = "\n".join(first_person_line(line)
                              for line in subject.splitlines() if line.strip())
        if not narrative:
            narrative = "I have nothing definite to say."
        result = render(narrative)
        return result if admissible_output(result) else _FALLBACK
    return guarded


def renderer_instruction(instruction):
    return _GOVERNOR.renderer_instruction(instruction, _BINDINGS, _CONTEXT)
