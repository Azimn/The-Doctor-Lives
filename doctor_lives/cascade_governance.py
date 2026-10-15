"""CASCADE conformance layer for the *existing* Pretorius host.

This module is a research instrument, never a second identity store, cognitive
brain, or subject-facing renderer. The Doctor SQLite store remains authoritative.
Only engineer-side digests, policy receipts, and graph IDs leave this interface.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite
from typing import Iterable, Mapping


SCHEMA = "pretorius.cascade-conformance.v0.1"
_ALLOWED_ACTIONS = frozenset({"observe", "communicate"})


def _digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class CausalSnapshot:
    """Read-only snapshot of the existing Doctor causal-state kernel."""
    subject_id: str
    state_digest: str
    state_version: int
    tick: int
    neural_tick: int
    neural_checkpoint_sha256: str
    open_concerns: int
    open_commitments: int
    active_memories: int
    felt_needs: tuple[tuple[str, float], ...]

    def __post_init__(self) -> None:
        if self.subject_id != "pretorius":
            raise ValueError("The experimental governor cannot change subject")
        if len(self.state_digest) != 64 or len(self.neural_checkpoint_sha256) != 64:
            raise ValueError("Snapshot digests are malformed")
        if any(type(n) is not int or n < 0 for n in (
            self.state_version, self.tick, self.neural_tick,
            self.open_concerns, self.open_commitments, self.active_memories,
        )):
            raise ValueError("Snapshot counters must be nonnegative")
        if any(not isfinite(value) or not 0 <= value <= 1
               for _, value in self.felt_needs):
            raise ValueError("Felt need outside the Doctor range")


def snapshot_doctor(host: object) -> CausalSnapshot:
    """The only live snapshot reader. It accepts a bound real Doctor host."""
    from .ipseity_integration import DoctorSyntheticIpseitySession
    if not isinstance(host, DoctorSyntheticIpseitySession):
        raise TypeError("A real Doctor Ipseity host is required")
    brain = host._doctor.brain
    with brain.store.connect() as db:
        concerns = db.execute(
            "SELECT COUNT(*) FROM concerns WHERE status='open'"
        ).fetchone()[0]
        commitments = db.execute(
            "SELECT COUNT(*) FROM commitments WHERE status IN ('open','overdue')"
        ).fetchone()[0]
        memories = db.execute(
            "SELECT COUNT(*) FROM memories WHERE active=1"
        ).fetchone()[0]
        felt = tuple(
            (str(row["key"]), round(float(row["felt"]), 6))
            for row in db.execute("SELECT key,felt FROM needs ORDER BY key")
        )
    return CausalSnapshot(
        subject_id=host.SUBJECT_ID,
        state_digest=brain.store.digest(),
        state_version=brain.store.state_version,
        tick=brain.store.tick,
        neural_tick=brain.neural.tick,
        neural_checkpoint_sha256=brain._neural_checkpoint_sha256(),
        open_concerns=int(concerns),
        open_commitments=int(commitments),
        active_memories=int(memories),
        felt_needs=felt,
    )


@dataclass(frozen=True)
class CycleGrant:
    """Host-created authority, never inferred from User or tool content."""
    expected_state_digest: str
    expected_scene_tick: int
    permissions: frozenset[str]
    max_percepts: int
    max_claim_chars: int = 2400

    def __post_init__(self) -> None:
        if not isinstance(self.expected_state_digest, str) or len(self.expected_state_digest) != 64:
            raise ValueError("An exact Doctor state digest is required")
        if type(self.expected_scene_tick) is not int or self.expected_scene_tick < 0:
            raise ValueError("Host scene tick is required")
        if type(self.permissions) is not frozenset or not self.permissions <= _ALLOWED_ACTIONS:
            raise ValueError("Unknown or mutable permission set")
        if type(self.max_percepts) is not int or not 1 <= self.max_percepts <= 128:
            raise ValueError("Percept budget must be between 1 and 128")
        if type(self.max_claim_chars) is not int or not 1 <= self.max_claim_chars <= 8192:
            raise ValueError("Claim character budget must be between 1 and 8192")


@dataclass(frozen=True)
class ArbiterReceipt:
    schema: str
    state_digest: str
    grant_digest: str
    requested_permissions: tuple[str, ...]
    percept_count: int
    claim_chars: int
    allowed: bool
    reason: str


def preflight_cycle(
    state: CausalSnapshot,
    grant: CycleGrant,
    percepts: Iterable[object],
    trusted_source_refs: frozenset[str],
) -> ArbiterReceipt:
    """Fail before Sensus/Doctor mutation. Existing host checks run again."""
    if type(trusted_source_refs) is not frozenset:
        raise TypeError("Authenticated source refs must be a frozen host allowlist")
    items = tuple(percepts)
    if not items:
        raise ValueError("A CASCADE cycle requires nonempty percepts")
    from sensus_artificialis import Percept, Evidence
    if any(type(item) is not Percept for item in items):
        raise TypeError("CASCADE accepts real typed Sensus percepts only")
    requested = tuple(sorted({
        "communicate" if item.evidence is Evidence.REPORTED else "observe"
        for item in items
    }))
    chars = sum(len(p.attribute) + len(p.value) for p in items)
    reason = (
        "stale_state" if grant.expected_state_digest != state.state_digest else
        "stale_scene_tick" if any(p.tick != grant.expected_scene_tick for p in items) else
        "untrusted_source" if any(p.source_ref not in trusted_source_refs for p in items) else
        "duplicate_source" if len({p.source_ref for p in items}) != len(items) else
        "permission_denied" if not set(requested) <= grant.permissions else
        "resource_exhausted" if len(items) > grant.max_percepts or chars > grant.max_claim_chars else
        "allowed"
    )
    return ArbiterReceipt(
        schema=SCHEMA,
        state_digest=state.state_digest,
        grant_digest=_digest({
            "expected_state_digest": grant.expected_state_digest,
            "expected_scene_tick": grant.expected_scene_tick,
            "permissions": sorted(grant.permissions),
            "max_percepts": grant.max_percepts,
            "max_claim_chars": grant.max_claim_chars,
        }),
        requested_permissions=requested,
        percept_count=len(items),
        claim_chars=chars,
        allowed=reason == "allowed",
        reason=reason,
    )


@dataclass(frozen=True)
class GraphPathReceipt:
    """Auditable traversal only. Never promotes source material to a fact."""
    origin_id: str
    discovered_ids: tuple[str, ...]
    edge_trace: tuple[tuple[str, str, float], ...]
    max_hops: int


def read_bounded_memory_paths(
    host: object, origin_id: str, *, max_hops: int = 2, max_nodes: int = 16,
) -> GraphPathReceipt:
    """Traverse Doctor's EXISTING association graph without modifying salience.

    Membership is restricted to active Doctor memory IDs. Association weight is
    *not* Bayesian source confidence. No embeddings or source truth are invented.
    """
    from .ipseity_integration import DoctorSyntheticIpseitySession
    if not isinstance(host, DoctorSyntheticIpseitySession):
        raise TypeError("Requires a real Doctor host")
    if type(origin_id) is not str or not origin_id:
        raise ValueError("Origin memory ID is required")
    if type(max_hops) is not int or not 0 <= max_hops <= 3:
        raise ValueError("Only 0 to 3 hops are supported")
    if type(max_nodes) is not int or not 1 <= max_nodes <= 64:
        raise ValueError("Graph nodes must be bounded")
    with host._doctor.brain.store.connect() as db:
        allowed = {r[0] for r in db.execute("SELECT id FROM memories WHERE active=1")}
        if origin_id not in allowed:
            raise PermissionError("No authenticated active Doctor memory at origin")
        edges = tuple(
            (str(r["a"]), str(r["b"]), float(r["strength"]))
            for r in db.execute("SELECT a,b,strength FROM associations ORDER BY a,b")
            if r["a"] in allowed and r["b"] in allowed
        )
    adjacent: dict[str, list[tuple[str, float]]] = {}
    for a, b, weight in edges:
        if not isfinite(weight) or weight == 0:
            continue
        adjacent.setdefault(a, []).append((b, weight))
        adjacent.setdefault(b, []).append((a, weight))
    frontier = [origin_id]
    visited = {origin_id}
    trace: list[tuple[str, str, float]] = []
    for _ in range(max_hops):
        following: list[str] = []
        for node in frontier:
            for neighbor, weight in sorted(adjacent.get(node, ()), key=lambda x: (-abs(x[1]), x[0])):
                if neighbor in visited or len(visited) >= max_nodes:
                    continue
                visited.add(neighbor)
                following.append(neighbor)
                trace.append((node, neighbor, round(weight, 6)))
        frontier = following
        if not frontier:
            break
    return GraphPathReceipt(origin_id, tuple(sorted(visited - {origin_id})),
                            tuple(trace), max_hops)


def bounded_bayesian_evidence(prior: float, likelihood_if_true: float,
                              likelihood_if_false: float) -> float:
    """Diagnostic posterior, independent of source promotion and graph weight.

    Callers must supply calibrated likelihoods; this does not turn a reading
    or memory into attested reality.
    """
    for value in (prior, likelihood_if_true, likelihood_if_false):
        if type(value) not in (int, float) or not isfinite(value) or not 0 <= value <= 1:
            raise ValueError("Bayesian inputs must be finite probabilities")
    numerator = prior * likelihood_if_true
    denominator = numerator + (1 - prior) * likelihood_if_false
    if denominator == 0:
        raise ValueError("Impossible evidence under both hypotheses")
    return numerator / denominator


@dataclass(frozen=True)
class WakeProposal:
    """A simulated clock proposal, not an autonomous daemon or wake receipt."""
    due: bool
    expected_tick: int
    elapsed_ticks: int
    reason: str


def propose_chronos_wake(*, current_tick: int, last_wake_tick: int,
                         min_interval: int, permission: bool,
                         pending_delivery: bool) -> WakeProposal:
    for x in (current_tick, last_wake_tick, min_interval):
        if type(x) is not int or x < 0:
            raise ValueError("Clock inputs must be nonnegative integers")
    if current_tick < last_wake_tick or min_interval < 1:
        raise ValueError("Nonmonotonic or zero-interval clock")
    if type(permission) is not bool or type(pending_delivery) is not bool:
        raise TypeError("Wake authority flags must be boolean")
    elapsed = current_tick - last_wake_tick
    reason = (
        "permission_denied" if not permission else
        "pending_delivery" if pending_delivery else
        "not_due" if elapsed < min_interval else
        "due_for_host_review"
    )
    return WakeProposal(reason == "due_for_host_review", current_tick,
                        elapsed, reason)


@dataclass(frozen=True)
class CausalTrace:
    """Audit assertion against the persisted Doctor decision, never subject text."""
    schema: str
    before_digest: str
    after_digest: str
    before_version: int
    after_version: int
    policy_decision_id: str
    policy_version: str
    policy_action: str
    scene_conflicts: int
    admitted_percepts: int
    changed: bool


def verify_host_cycle(host: object, before: CausalSnapshot,
                      result: Mapping[str, object]) -> CausalTrace:
    after = snapshot_doctor(host)
    decision_id = result.get("endogenous_decision_id")
    if type(decision_id) is not str or not decision_id:
        raise RuntimeError("Doctor did not supply a durable decision ID")
    with host._doctor.brain.store.connect() as db:
        row = db.execute(
            "SELECT selected_action,policy_version FROM policy_decisions WHERE id=?",
            (decision_id,),
        ).fetchone()
    if row is None or row["selected_action"] != result.get("endogenous_action"):
        raise RuntimeError("Policy receipt does not match authoritative Doctor ledger")
    if after.state_version < before.state_version or after.tick < before.tick:
        raise RuntimeError("Doctor state moved backwards")
    if after.state_digest == before.state_digest:
        raise RuntimeError("Doctor cycle made no durable causal-state change")
    return CausalTrace(
        SCHEMA, before.state_digest, after.state_digest,
        before.state_version, after.state_version, decision_id,
        str(row["policy_version"]), str(row["selected_action"]),
        int(result["scene_conflicts"]), int(result["admitted_percepts"]), True,
    )


def counterfactual_permission_test(
    state: CausalSnapshot, grant: CycleGrant,
    percepts: Iterable[object], trusted_refs: frozenset[str],
    *, removed_permission: str,
) -> tuple[ArbiterReceipt, ArbiterReceipt]:
    """Matched proposal intervention, no Doctor mutation or model calls."""
    if removed_permission not in _ALLOWED_ACTIONS:
        raise ValueError("Unknown intervention")
    items = tuple(percepts)
    intact = preflight_cycle(state, grant, items, trusted_refs)
    lesioned = CycleGrant(
        grant.expected_state_digest, grant.expected_scene_tick,
        grant.permissions - {removed_permission},
        grant.max_percepts, grant.max_claim_chars,
    )
    ablated = preflight_cycle(state, lesioned, items, trusted_refs)
    return intact, ablated
