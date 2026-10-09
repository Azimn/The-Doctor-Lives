"""Isolated, deterministic self-relevance prior for a protected identity snapshot.

No model, storage, world adapter, UPPB, AwarenessRouter, or action-policy calls
occur here. Outputs are *candidate proposals* on the engineer plane. They do
not authorize admission to awareness, memory editing, action, or introspection.

Matched-state experiments use the same source records in every arm and lesion
only the gain or the association of evidence packets with candidates.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
import math

from .state import IdentitySnapshot


class BindingMode(StrEnum):
    OFF = "off"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    SHUFFLED = "shuffled"


# Gain is not a neurobiological or phenomenal scale. These are preregisterable
# synthetic ablation settings, not calibrated selfhood measurements.
_MODE_GAIN = {
    BindingMode.OFF: 0.0,
    BindingMode.LOW: 0.25,
    BindingMode.NORMAL: 0.50,
    BindingMode.HIGH: 1.0,
    BindingMode.SHUFFLED: 0.50,
}

# Fixed prototype priorities. They require independent ablation before tuning.
_SOURCE_WEIGHTS = {
    "invariants": 1.0,
    "relationships": 0.80,
    "commitments": 1.0,
    "memories": 0.70,
    "self_model_hypotheses": 0.40,
}


def _unit(field: str, value: float) -> float:
    if isinstance(value, bool):
        raise TypeError(f"{field} must be numeric, not boolean")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{field} must be a finite number") from exc
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise ValueError(f"{field} must be between zero and one")
    return number


def _digest(value: object) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class EvidenceMatch:
    """Host-provided, source-linked relevance; not inferred from ritual words.

    The protected caller is responsible for judging semantic alignment.
    Matching a reference in the snapshot proves membership, not relevance.
    """

    source_ref: str
    relevance: float
    evidential_support: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.source_ref, str) or not self.source_ref.strip():
            raise ValueError("source_ref is required")
        object.__setattr__(self, "relevance", _unit("relevance", self.relevance))
        object.__setattr__(
            self, "evidential_support", _unit("evidential_support", self.evidential_support)
        )


@dataclass(frozen=True, slots=True)
class BindingCandidate:
    """Protected-plane event descriptor, not a subjective/phenomenal event."""

    event_id: str
    subject_id: str
    base_salience: float
    matches: tuple[EvidenceMatch, ...]
    verified_world_contradiction: bool = False

    def __post_init__(self) -> None:
        for name in ("event_id", "subject_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        object.__setattr__(self, "base_salience", _unit("base_salience", self.base_salience))
        if not isinstance(self.matches, tuple) or any(
            not isinstance(match, EvidenceMatch) for match in self.matches
        ):
            raise TypeError("matches must be a tuple of EvidenceMatch")
        refs = [match.source_ref for match in self.matches]
        if len(set(refs)) != len(refs):
            raise ValueError("duplicate source_ref within one event")
        if type(self.verified_world_contradiction) is not bool:
            raise TypeError("verified_world_contradiction must be a boolean")


@dataclass(frozen=True, slots=True)
class BindingPolicy:
    """Versioned fixed-weight prototype. No unbounded amplification."""

    version: str = "scc-self-binding-v1"
    max_bonus: float = 0.10

    def __post_init__(self) -> None:
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("policy version is required")
        bonus = _unit("max_bonus", self.max_bonus)
        if bonus > 0.10:
            raise ValueError("prototype self-binding bonus cap is 0.10")
        object.__setattr__(self, "max_bonus", bonus)


@dataclass(frozen=True, slots=True)
class BindingProposal:
    """Engineer-only audit record; it is NOT a PhenomenalEvent."""

    event_id: str
    base_salience: float
    supported_relevance: float
    requested_bonus: float
    effective_bonus: float
    proposed_salience: float
    source_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BindingRun:
    subject_id: str
    snapshot_digest: str
    state_version: int
    manifest_digest: str
    policy_version: str
    mode: BindingMode
    gain: float
    contradiction_freeze: bool
    proposals: tuple[BindingProposal, ...]
    audit_digest: str


class SelfBindingModulator:
    """Pure opt-in trial runner. Cannot grant consciousness or tool authority."""

    def __init__(self, policy: BindingPolicy | None = None) -> None:
        if policy is not None and not isinstance(policy, BindingPolicy):
            raise TypeError("policy must be BindingPolicy")
        self.policy = policy if policy is not None else BindingPolicy()

    @staticmethod
    def _source_index(snapshot: IdentitySnapshot) -> dict[str, str]:
        index: dict[str, str] = {}
        for family in _SOURCE_WEIGHTS:
            for ref in getattr(snapshot, family):
                if ref in index:
                    raise ValueError("source reference belongs to multiple identity families")
                index[ref] = family
        return index

    @staticmethod
    def _shuffled(
        candidates: tuple[BindingCandidate, ...],
    ) -> tuple[BindingCandidate, ...]:
        """Rotate evidence packets over sorted events, preserving all score inputs."""
        if len(candidates) < 2:
            raise ValueError("shuffled lesion requires at least two events")
        indexed = sorted(candidates, key=lambda item: item.event_id)
        packets = tuple(item.matches for item in indexed)
        if len(set(packets)) < 2:
            raise ValueError("shuffled lesion has identical evidence packets")
        remapped = {
            current.event_id: packets[(idx + 1) % len(indexed)]
            for idx, current in enumerate(indexed)
        }
        return tuple(
            BindingCandidate(
                item.event_id,
                item.subject_id,
                item.base_salience,
                remapped[item.event_id],
                item.verified_world_contradiction,
            )
            for item in candidates
        )

    def run(
        self,
        snapshot: IdentitySnapshot,
        candidates: tuple[BindingCandidate, ...],
        *,
        mode: BindingMode = BindingMode.NORMAL,
        expected_manifest: str,
        expected_state_version: int,
    ) -> BindingRun:
        if not isinstance(snapshot, IdentitySnapshot):
            raise TypeError("snapshot must be IdentitySnapshot")
        if not isinstance(candidates, tuple) or any(
            not isinstance(item, BindingCandidate) for item in candidates
        ):
            raise TypeError("candidates must be a tuple of BindingCandidate")
        if not isinstance(mode, BindingMode):
            raise TypeError("mode must be BindingMode; no implicit string selection")
        if (
            expected_manifest != snapshot.manifest_digest
            or type(expected_state_version) is not int
            or expected_state_version != snapshot.state_version
        ):
            raise ValueError("stale or mismatched source authority; fail closed")
        event_ids = [item.event_id for item in candidates]
        if len(set(event_ids)) != len(event_ids):
            raise ValueError("duplicate event_id")
        if any(item.subject_id != snapshot.subject_id for item in candidates):
            raise ValueError("cross-subject evidence is forbidden")
        source_index = self._source_index(snapshot)

        # Check source membership before any lesion, even for OFF; malformed
        # evidence cannot silently pass just because its current gain is zero.
        for candidate in candidates:
            for match in candidate.matches:
                if match.source_ref not in source_index:
                    raise ValueError("unknown or cross-version source reference")
        effective = (
            self._shuffled(candidates) if mode is BindingMode.SHUFFLED else candidates
        )
        freeze = any(item.verified_world_contradiction for item in candidates)
        gain = _MODE_GAIN[mode]
        proposals = []
        for item in effective:
            weighted_sum = 0.0
            weight_total = 0.0
            for match in item.matches:
                weight = _SOURCE_WEIGHTS[source_index[match.source_ref]]
                weight_total += weight
                weighted_sum += weight * match.relevance * match.evidential_support
            support = weighted_sum / weight_total if weight_total else 0.0
            # Under an independently verified contradiction, freeze *all*
            # identity bonuses in this batch so competing self-priors cannot
            # indirectly crowd out the world observation in P3.
            requested = 0.0 if freeze else min(
                self.policy.max_bonus, self.policy.max_bonus * gain * support
            )
            proposed = min(1.0, item.base_salience + requested)
            effective_bonus = max(0.0, proposed - item.base_salience)
            proposals.append(
                BindingProposal(
                    event_id=item.event_id,
                    base_salience=item.base_salience,
                    supported_relevance=support,
                    requested_bonus=requested,
                    effective_bonus=effective_bonus,
                    proposed_salience=proposed,
                    source_refs=tuple(match.source_ref for match in item.matches),
                )
            )
        proposal_tuple = tuple(proposals)
        audit = {
            "subject_id": snapshot.subject_id,
            "snapshot_digest": snapshot.digest,
            "manifest_digest": snapshot.manifest_digest,
            "state_version": snapshot.state_version,
            "policy": self.policy.version,
            "cap": self.policy.max_bonus,
            "mode": mode.value,
            "gain": gain,
            "contradiction_freeze": freeze,
            "proposals": [
                {
                    "event": p.event_id,
                    "base": p.base_salience,
                    "support": p.supported_relevance,
                    "bonus": p.requested_bonus,
                    "effective": p.effective_bonus,
                    "proposed": p.proposed_salience,
                    "refs": p.source_refs,
                }
                for p in proposal_tuple
            ],
        }
        return BindingRun(
            subject_id=snapshot.subject_id,
            snapshot_digest=snapshot.digest,
            state_version=snapshot.state_version,
            manifest_digest=snapshot.manifest_digest,
            policy_version=self.policy.version,
            mode=mode,
            gain=gain,
            contradiction_freeze=freeze,
            proposals=proposal_tuple,
            audit_digest=_digest(audit),
        )

    def lesion_matrix(
        self,
        snapshot: IdentitySnapshot,
        candidates: tuple[BindingCandidate, ...],
        *,
        expected_manifest: str,
        expected_state_version: int,
    ) -> tuple[BindingRun, ...]:
        """Use identical immutable inputs to compute matched counterfactuals."""
        return tuple(
            self.run(
                snapshot, candidates,
                mode=mode,
                expected_manifest=expected_manifest,
                expected_state_version=expected_state_version,
            )
            for mode in BindingMode
        )
