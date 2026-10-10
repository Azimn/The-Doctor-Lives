"""Read-only source/provenance adapter for the existing PretoriusBrain.

No source rows are promoted into truth. Access to the brain object is supplied
by a caller that owns the state; reading a real policy_decision only verifies
that a choice occurred, NOT that it succeeded in the external world.
"""
from __future__ import annotations

from dataclasses import dataclass
from doctor_lives.cognition import PretoriusBrain
from doctor_lives.neural import ACTIONS

from .loop import (
    EvidenceKind, Forecast, ObservedEpisode, PredictiveSelfLoop,
    SelfSnapshot,
)


def snapshot_from_brain(brain: PretoriusBrain) -> SelfSnapshot:
    if not isinstance(brain, PretoriusBrain):
        raise TypeError("brain must be PretoriusBrain")
    before = brain.store.digest()
    scores = brain.neural.action_scores()
    actions = tuple(ACTIONS)
    raw = tuple(float(scores[action]) for action in actions)
    if any(value < 0 for value in raw) or sum(raw) <= 0:
        raise ValueError("invalid neural action score distribution")
    total = sum(raw)
    probabilities = tuple(x / total for x in raw)
    rows = brain.store.memories_with_classification()
    memory_refs = {
        "memory:" + str(row["id"])
        for row in rows if not row["external"]
    }
    relationship_refs = {
        "relationship:" + str(row["peer_id"])
        for row in brain.store.relationships()
    }
    commitment_refs = {
        "commitment:" + str(row["id"])
        for row in brain.store.open_commitments()
    }
    with brain.store.connect() as conn:
        model_refs = {
            "hypothesis:" + str(row["id"])
            for row in conn.execute("SELECT id FROM self_model ORDER BY id")
        }
    result = SelfSnapshot(
        subject_id="pretorius",
        state_digest=before,
        state_version=brain.store.state_version,
        manifest_digest=brain.evidence.manifest_fingerprint,
        cutoff_tick=brain.store.tick,
        actions=actions,
        base_probabilities=probabilities,
        admitted_refs=tuple(sorted(memory_refs | relationship_refs | commitment_refs | model_refs)),
    )
    if brain.store.digest() != before:
        raise AssertionError("read-only self snapshot mutated BrainStore")
    return result


def witnessed_policy_decision(
    brain: PretoriusBrain,
    loop: PredictiveSelfLoop,
    forecast: Forecast,
    decision_id: str,
) -> ObservedEpisode:
    """Verify an *actual stored* native decision, never a model-written claim.

    The caller supplies the context; this cannot independently verify how the
    situation was labeled. A policy record is evidence of chosen action only,
    not of correct world action or anyone else's beliefs.
    """
    if not isinstance(brain, PretoriusBrain):
        raise TypeError("brain must be PretoriusBrain")
    if loop.snapshot.manifest_digest != brain.evidence.manifest_fingerprint:
        raise ValueError("canonical manifest changed")
    if forecast.source_snapshot != loop.snapshot.digest:
        raise ValueError("foreign source snapshot")
    with brain.store.connect() as conn:
        row = conn.execute(
            "SELECT id,tick,selected_action FROM policy_decisions WHERE id=?",
            (decision_id,),
        ).fetchone()
    if row is None:
        raise ValueError("decision not found in local BrainStore")
    if int(row["tick"]) <= forecast.cutoff_tick:
        raise ValueError("policy decision was not later than the forecast cutoff")
    return ObservedEpisode(
        event_id="policy:" + str(row["id"]),
        forecast_id=forecast.forecast_id,
        tick=int(row["tick"]),
        situation=forecast.situation,
        action=str(row["selected_action"]),
        evidence_kind=EvidenceKind.RUNTIME_POLICY,
        witness_ref="local-policy_decisions:" + str(row["id"]),
        evidence_precision=1.0,
    )
