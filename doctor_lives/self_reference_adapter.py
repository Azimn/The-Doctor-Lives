"""Opt-in thin Pretorius adapter for the canonical Synthetic Ipseity governor.

Never owns identity or cognitive state. Host identity comes from the actual
Doctor RenderRequest and session subject_id, not from text or the governor.
Engineer receipts are kept outside Ipseity's subject-only renderer input.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Callable

from .ipseity_integration import DoctorSyntheticIpseitySession

try:
    from synthetic_ipseity.self_reference import (
        ReferenceBindings, ReferenceContext, SelfReferenceGovernor,
    )
except ImportError as exc:
    raise ImportError(
        "Install the pinned Synthetic Ipseity governor donor revision"
    ) from exc

GOVERNOR_COMMIT = "e84f3e37d844756786b289c13c15ea92edfd8d69"


class GovernorOutputRejected(ValueError):
    """Unsafe output was rejected before durable Ipseity delivery ACK."""


@dataclass(frozen=True)
class GovernedRendererReceipt:
    """Engineer-only immutable digest receipt, never exposed to subject."""
    enabled: bool
    rule_id: str
    disposition: str
    conflict: bool
    input_sha256: str
    instruction_sha256: str
    resolved_instruction_sha256: str
    response_sha256: str
    allowed: bool
    first_person_desire: int
    in_clause_self_name: int
    vocative_self: int
    unlicensed_vocative_self: int


def _sha(text: str) -> str:
    return sha256(text.encode("utf8")).hexdigest()


class HostBoundGovernorRenderer:
    """Trusted adapter presents one positional subject string to Ipseity.

    The separate instruction argument to the trusted rendering implementation
    is configuration, NOT an additional cognitive input or memory event.
    """

    def __init__(
        self, *,
        enabled: bool,
        render: Callable[[str, str], str],
        trusted_instruction: str,
    ):
        if type(enabled) is not bool:
            raise TypeError("Governor switch must be explicitly boolean")
        if not callable(render):
            raise TypeError("Trusted renderer must be callable")
        if type(trusted_instruction) is not str or not trusted_instruction.strip():
            raise ValueError("Trusted renderer-only instruction required")
        self.enabled = enabled
        self._render = render
        self._instruction = trusted_instruction
        self._gov = SelfReferenceGovernor() if enabled else None
        self._bindings = None
        self._context = None
        self.receipts: list[GovernedRendererReceipt] = []
        self.subject_inputs: list[str] = []
        self.render_instructions: list[str] = []

    def bind_doctor_host(
        self, host: DoctorSyntheticIpseitySession, *,
        addressee_subject_id: str | None,
        rhetorical_self_address: bool = False,
        aliases: tuple[str, ...] = ("Pretorius",),
    ) -> None:
        """Seal canonical identity from the real Doctor's authority only."""
        if self._bindings is not None:
            raise RuntimeError("Host identity already sealed")
        if not isinstance(host, DoctorSyntheticIpseitySession):
            raise TypeError("Only real Doctor Ipseity host can bind identity")
        if type(rhetorical_self_address) is not bool:
            raise TypeError("Host rhetorical license must be boolean")
        if type(aliases) is not tuple or any(type(a) is not str for a in aliases):
            raise TypeError("Host aliases must be an explicit tuple of strings")
        canonical = host._doctor.brain.render_request().subject
        self._bindings = ReferenceBindings(
            host.SUBJECT_ID, canonical, aliases,
        )
        self._context = ReferenceContext(
            speaker_subject_id=host.SUBJECT_ID,
            addressee_subject_id=addressee_subject_id,
            rhetorical_self_address=rhetorical_self_address,
        )

    def __call__(self, subject_text: str) -> str:
        if self._bindings is None or self._context is None:
            raise RuntimeError("Unbound host authority; refuse delivery")
        if type(subject_text) is not str or not subject_text.strip():
            raise ValueError("Only admitted nonblank subject text may be rendered")
        self.subject_inputs.append(subject_text)
        instruction = self._instruction
        rule = "SRG-DISABLED"
        disposition = "disabled"
        conflict = False
        if self._gov is not None:
            instruction, receipt = self._gov.resolve(
                instruction, self._bindings, self._context,
            )
            rule = receipt.rule_id
            disposition = receipt.disposition
            conflict = receipt.conflict
        self.render_instructions.append(instruction)
        response = self._render(subject_text, instruction)
        if type(response) is not str or not response.strip():
            raise TypeError("Renderer must return nonblank speech")
        score = (
            self._gov.check(response, self._bindings, self._context)
            if self._gov is not None else None
        )
        allowed = score.accepted if score is not None else True
        self.receipts.append(GovernedRendererReceipt(
            enabled=self.enabled,
            rule_id=rule,
            disposition=disposition,
            conflict=conflict,
            input_sha256=_sha(subject_text),
            instruction_sha256=_sha(self._instruction),
            resolved_instruction_sha256=_sha(instruction),
            response_sha256=_sha(response),
            allowed=allowed,
            first_person_desire=score.first_person_desire if score else 0,
            in_clause_self_name=score.in_clause_self_name if score else 0,
            vocative_self=score.vocative_self if score else 0,
            unlicensed_vocative_self=score.unlicensed_vocative_self if score else 0,
        ))
        if not allowed:
            raise GovernorOutputRejected(
                "Self-reference governor veto; subject delivery unacknowledged"
            )
        return response
