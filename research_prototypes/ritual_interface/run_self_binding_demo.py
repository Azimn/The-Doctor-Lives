"""Reproducible, synthetic demonstration of bounded self-binding salience.

Produces structural counterfactual data, NOT evidence of persona continuity.
No model inference, world action, memory mutation, or awareness admission occurs.
Run: python -m research_prototypes.ritual_interface.run_self_binding_demo
"""
from __future__ import annotations

import json

from .self_binding_modulator import (
    BindingCandidate, BindingMode, EvidenceMatch, SelfBindingModulator,
)
from .state import IdentitySnapshot


def build_fixture() -> tuple[IdentitySnapshot, tuple[BindingCandidate, ...]]:
    state = IdentitySnapshot(
        subject_id="synthetic-subject",
        state_version=1,
        manifest_digest="f" * 64,
        invariants=("invariant:test",),
        relationships=("relationship:test",),
        commitments=("commitment:test",),
        memories=("episode:test",),
        self_model_hypotheses=("hypothesis:test",),
    )
    events = (
        BindingCandidate(
            "recall-promise", "synthetic-subject", .47,
            (EvidenceMatch("commitment:test", 1.0),),
        ),
        BindingCandidate("notice-background", "synthetic-subject", .53, ()),
        BindingCandidate(
            "question-self", "synthetic-subject", .30,
            (EvidenceMatch("hypothesis:test", .25),),
        ),
    )
    return state, events


def run_demo() -> dict[str, object]:
    state, candidates = build_fixture()
    engine = SelfBindingModulator()
    matrix = engine.lesion_matrix(
        state,
        candidates,
        expected_manifest=state.manifest_digest,
        expected_state_version=state.state_version,
    )
    traces: dict[str, object] = {}
    for run in matrix:
        ordered = sorted(run.proposals, key=lambda item: (-item.proposed_salience, item.event_id))
        traces[run.mode.value] = {
            "gain": run.gain,
            "audit_digest": run.audit_digest,
            "highest_proposed_salience_event": ordered[0].event_id,
            "bonuses": {p.event_id: p.effective_bonus for p in run.proposals},
            "scores": {p.event_id: p.proposed_salience for p in run.proposals},
        }
    # Exact same source state, same sensory baselines, but a protected
    # contradiction disables identity amplification in every condition.
    events_with_conflict = candidates + (
        BindingCandidate("contradictory-world-fact", state.subject_id, .61, (), True),
    )
    conflict = engine.run(
        state, events_with_conflict,
        mode=BindingMode.HIGH,
        expected_manifest=state.manifest_digest,
        expected_state_version=state.state_version,
    )
    return {
        "claim_status": "synthetic_algorithmic_smoke_test_not_behavioral_efficacy",
        "subject_id": state.subject_id,
        "snapshot_digest": state.digest,
        "policy_version": engine.policy.version,
        "modes": traces,
        "conflict": {
            "freeze": conflict.contradiction_freeze,
            "all_identity_bonuses_zero": all(p.effective_bonus == 0 for p in conflict.proposals),
            "audit_digest": conflict.audit_digest,
        },
    }


def main() -> None:
    print(json.dumps(run_demo(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
