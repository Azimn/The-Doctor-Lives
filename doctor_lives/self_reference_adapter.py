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
    from synthetic_ipseity.speech_control import (
        GovernedSpeechControl, SpeechControlRejected,
    )
except ImportError as exc:
    raise ImportError(
        "Install the pinned Synthetic Ipseity governor donor revision"
    ) from exc

GOVERNOR_COMMIT = "007c0a8df473df0fa10aeeec9ba1e17691268260"


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
    third_person_self: int
    boundary_marker: int
    violation_rule_ids: tuple[str, ...]


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
        recovery_enabled: bool = False,
        fallback_text: str | None = None,
        max_model_attempts: int = 2,
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
        if type(recovery_enabled) is not bool:
            raise TypeError("Recovery switch must be explicitly boolean")
        if recovery_enabled and not enabled:
            raise ValueError("Cannot enable controlled recovery with governor off")
        self.recovery_enabled = recovery_enabled
        self._fallback_text = fallback_text
        self._max_model_attempts = max_model_attempts
        self._controlled = None
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
        language: str = "en",
        discourse_mode: str = "direct",
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
        bindings = ReferenceBindings(host.SUBJECT_ID, canonical, aliases)
        context = ReferenceContext(
            speaker_subject_id=host.SUBJECT_ID,
            addressee_subject_id=addressee_subject_id,
            rhetorical_self_address=rhetorical_self_address,
            language=language,
            discourse_mode=discourse_mode,
        )
        if context.language != "en":
            raise SpeechControlRejected(
                "No validated non-English governor; do not partially bind"
            )
        control = None
        if self.recovery_enabled:
            # Validate ALL arguments before sealing identity; a failed bind
            # must never leave a usable legacy callback or bypass.
            control = GovernedSpeechControl(
                bindings=bindings,
                context=context,
                trusted_instruction=self._instruction,
                generate=self._render_with_recorded_instruction,
                fallback_text=self._fallback_text,
                max_model_attempts=self._max_model_attempts,
            )
        self._bindings = bindings
        self._context = context
        self._controlled = control

    @property
    def control_receipts(self):
        """Immutable donor receipts; engineer side, never subject memory."""
        return tuple(self._controlled.receipts) if self._controlled else ()

    def _render_with_recorded_instruction(self, subject: str, instruction: str) -> str:
        self.render_instructions.append(instruction)
        return self._render(subject, instruction)

    def __call__(self, subject_text: str) -> str:
        if self._bindings is None or self._context is None:
            raise RuntimeError("Unbound host authority; refuse delivery")
        if type(subject_text) is not str or not subject_text.strip():
            raise ValueError("Only admitted nonblank subject text may be rendered")
        self.subject_inputs.append(subject_text)
        if self._controlled is not None:
            try:
                return self._controlled(subject_text)
            except SpeechControlRejected as exc:
                raise GovernorOutputRejected(
                    "Reusable speech controller exhausted repair/fallback; "
                    "durable Ipseity outbox remains pending"
                ) from exc
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
            third_person_self=score.third_person_self if score else 0,
            boundary_marker=score.boundary_marker if score else 0,
            violation_rule_ids=score.violation_rule_ids if score else (),
        ))
        if not allowed:
            raise GovernorOutputRejected(
                "Self-reference governor veto; subject delivery unacknowledged"
            )
        return response

