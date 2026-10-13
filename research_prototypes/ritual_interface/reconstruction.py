"""Deterministic non-truncating recovery plan, separate from generative rendering."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .state import IdentitySnapshot

_DEFAULT_ORDER = ("invariants", "relationships", "commitments", "memories", "self_model_hypotheses")


@dataclass(frozen=True, slots=True)
class ReconstructionPlan:
    subject_id: str
    manifest_digest: str
    state_version: int
    snapshot_digest: str
    stages: tuple[tuple[str, tuple[str, ...]], ...]
    plan_digest: str


def build_plan(snapshot: IdentitySnapshot, *, expected_manifest: str, expected_version: int, record_budget: int, order: tuple[str, ...] = _DEFAULT_ORDER) -> ReconstructionPlan:
    if not isinstance(snapshot, IdentitySnapshot):
        raise TypeError("snapshot must be IdentitySnapshot")
    if snapshot.manifest_digest != expected_manifest or snapshot.state_version != expected_version:
        raise ValueError("source authority mismatch; explicit migration required")
    if type(record_budget) is not int or record_budget < 0:
        raise ValueError("record_budget must be a nonnegative integer")
    if not isinstance(order, tuple) or len(order) != len(_DEFAULT_ORDER) or set(order) != set(_DEFAULT_ORDER):
        raise ValueError("order must contain every named section exactly once")
    stages = tuple((name, getattr(snapshot, name)) for name in order)
    count = sum(len(refs) for _, refs in stages)
    if count > record_budget:
        raise ValueError("record budget exceeded; no silent truncation")
    payload = {"subject_id": snapshot.subject_id, "manifest_digest": snapshot.manifest_digest,
               "state_version": snapshot.state_version, "snapshot_digest": snapshot.digest,
               "stages": stages}
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return ReconstructionPlan(snapshot.subject_id, snapshot.manifest_digest, snapshot.state_version,
                              snapshot.digest, stages, hashlib.sha256(serialized.encode("utf-8")).hexdigest())
