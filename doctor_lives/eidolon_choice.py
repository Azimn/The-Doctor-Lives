"""Eidolon D3: disposable Pretorius clone policy-interface *construction* probe.

This code MUST NOT be installed as an automatic production policy adapter.
It accepts only test state dirs explicitly marked disposable. It transiently
wraps `PretoriusBrain._state_policy_scores` to measure a causal route into the
real `think()` policy-selection audit path, then restores the method.

Fixed rule-based injection is NOT a trained neural mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .cognition import PretoriusBrain
from .eidolon_temporal import ChronosCoil
from .neural import ACTIONS


@dataclass(frozen=True)
class ClonePolicyProbe:
    selected_action: str
    injected: bool
    source_commitments: tuple[str, ...]
    source_evidence_events: tuple[str, ...]
    base_scores: dict[str, float]
    chosen_scores: dict[str, float]
    selected_memory_count: int
    policy_decision_id: str


def run_disposable_policy_probe(
    brain: PretoriusBrain,
    *,
    enabled: bool,
    with_history: bool = True,
    with_temporal: bool = True,
    delta: float = 0.04,
) -> ClonePolicyProbe:
    """Run one genuine `think` in a disposable clone and log its selected mode.

    No supported production workflow calls this method. An explicit marker
    on a research clone is mandatory, and source/clock gates are enforced.
    """
    if not isinstance(brain, PretoriusBrain):
        raise TypeError("expected PretoriusBrain")
    if not (Path(brain.state_dir) / ".eidolon_disposable_clone").is_file():
        raise PermissionError("refusing to patch a non-disposable Pretorius brain")
    if not all(isinstance(v, bool) for v in (enabled, with_history, with_temporal)):
        raise TypeError("probe flags must be Boolean")
    if delta != 0.04:
        raise ValueError("D3 intervention strength is precommitted at 0.04")

    forecast = ChronosCoil.forecast(
        brain, with_history=with_history, with_temporal=with_temporal
    )
    eligible = tuple(
        item for item in forecast.goals
        if item.evidence_support > 0.0
        and item.urgency >= 0.8
        and item.priority >= 0.85
        and item.evidence_event_ids
    )
    injected = bool(enabled and eligible)
    # Read before the think event; do not permit the event itself to become
    # retrospective evidence for its own policy choice.
    source_ids = tuple(sorted({g.commitment_id for g in eligible})) if injected else ()
    evidence_ids = tuple(
        sorted({event_id for g in eligible for event_id in g.evidence_event_ids})
    ) if injected else ()

    original = brain._state_policy_scores
    if injected:
        def bounded_adapter(*args: Any, **kwargs: Any):
            base, selected, audit = original(*args, **kwargs)
            if set(selected) != set(ACTIONS):
                raise RuntimeError("invalid production action dictionary")
            adjusted = {k: float(v) for k, v in selected.items()}
            adjusted["persist"] += delta
            denominator = sum(adjusted.values())
            if denominator <= 0:
                raise RuntimeError("invalid adapter normalization")
            adjusted = {k: v / denominator for k, v in adjusted.items()}
            updated_audit = dict(audit)
            updated_audit["eidolon_d3_disposable_adapter"] = {
                "source_state_digest": forecast.source_state_digest,
                "eligible_commitments": list(source_ids),
                "witness_event_ids": list(evidence_ids),
                "applied_delta": delta,
                "production_bridge_disabled_for_experiment": True,
            }
            return base, adjusted, updated_audit

        brain._state_policy_scores = bounded_adapter
    try:
        result = brain.think(
            "eidolon-d3-disposable-clone",
            bridge_enabled=False,
        )
    finally:
        # In-memory method always restored, including on any exception.
        if injected:
            brain._state_policy_scores = original
    return ClonePolicyProbe(
        selected_action=result["selected_action"],
        injected=injected,
        source_commitments=source_ids,
        source_evidence_events=evidence_ids,
        base_scores=dict(result["base_action_scores"]),
        chosen_scores=dict(result["action_scores"]),
        selected_memory_count=len(result["source_record_ids"]),
        policy_decision_id=str(result["policy_decision_id"]),
    )
