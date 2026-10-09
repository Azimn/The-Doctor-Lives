"""Capability-based preflight only; does not write identity or world history."""
from __future__ import annotations

from dataclasses import dataclass

from .state import IdentitySnapshot

_EDITABLE = frozenset({"relationship", "commitment", "self_model_hypothesis", "cue"})


@dataclass(frozen=True, slots=True)
class ChangeProposal:
    actor_id: str
    capability: str
    target_kind: str
    source_ref: str
    expected_state_version: int
    expected_manifest_digest: str


@dataclass(frozen=True, slots=True)
class GovernanceDecision:
    allowed: bool
    reason: str


def review(proposal: ChangeProposal, *, snapshot: IdentitySnapshot, granted_capabilities: frozenset[str]) -> GovernanceDecision:
    if not isinstance(proposal, ChangeProposal) or not isinstance(snapshot, IdentitySnapshot):
        raise TypeError("typed proposal and snapshot required")
    if not isinstance(granted_capabilities, frozenset):
        raise TypeError("granted_capabilities must come from protected capability store")
    if not proposal.actor_id or not proposal.source_ref:
        return GovernanceDecision(False, "missing actor or source provenance")
    if proposal.target_kind not in _EDITABLE:
        return GovernanceDecision(False, "canonical evidence and protected history are not editable")
    if proposal.expected_state_version != snapshot.state_version or proposal.expected_manifest_digest != snapshot.manifest_digest:
        return GovernanceDecision(False, "stale state or source manifest")
    if proposal.capability not in granted_capabilities:
        return GovernanceDecision(False, "missing out-of-band capability")
    return GovernanceDecision(True, "preflight only; authoritative writer must enforce and audit separately")
