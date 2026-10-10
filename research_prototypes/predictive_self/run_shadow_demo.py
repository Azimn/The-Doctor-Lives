"""Executable research smoke test for the bidirectional Predictive Self Loop.

Separates synthetic, mock-witness semantic updating from an actual read-only
PretoriusBrain snapshot and native stored-action verification. Never interprets
synthetic results as independent persona or world evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

from doctor_lives.cognition import PretoriusBrain
from doctor_lives.models import Experience

from .adapter import snapshot_from_brain, witnessed_policy_decision
from .loop import (
    EvidenceKind, ObservedEpisode, PredictiveSelfLoop, SelfSnapshot,
    SemanticClaim, Situation,
)


def synthetic_run() -> dict[str, object]:
    snapshot = SelfSnapshot(
        "synthetic-pretorius", "a" * 64, 1, "b" * 64, 5,
        ("challenge", "cooperate", "explore"), (.3, .4, .3),
        ("design:independence",),
    )
    claims = (SemanticClaim(
        "independence_testable_proxy", ("challenge", "explore"),
        .75, ("design:independence",), 4.0,
    ),)
    loop = PredictiveSelfLoop(snapshot, claims=claims)
    initial = dict(loop.audit()["semantic_posterior"])
    audits = []
    for index, role in enumerate(("laboratory", "colleague", "unfamiliar_authority")):
        context = Situation(f"probe-{index}", role, "henry" if index < 2 else None)
        forecast = loop.forecast(context)
        outcome = ObservedEpisode(
            f"mock-event-{index}", forecast.forecast_id,
            6 + index, context, "cooperate",
            EvidenceKind.WORLD_VERIFIED, f"MOCK-WITNESS-{index}",
            evidence_precision=1.0,
            world_success=True,
            partner_cooperated=True if context.partner_id else None,
        )
        error = loop.observe(outcome)
        audits.append({
            "forecast_digest": forecast.digest,
            "action_log_loss": round(error.action_log_loss, 8),
            "partner_before": forecast.partner_cooperation_probability,
            "suggestion": forecast.inquiry.kind if forecast.inquiry else None,
        })
    return {
        "evidence": "mock_world_witness_synthetic_only",
        "semantic_before": initial,
        "semantic_after": loop.audit()["semantic_posterior"],
        "forecast_errors": audits,
        "n_scored": loop.audit()["n_scored"],
        "ledger_digest": loop.audit()["audit_sha256"],
    }


def real_brain_shadow_run() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="psl-shadow-") as td:
        brain = PretoriusBrain(Path(td))
        source_digest = brain.store.digest()
        source = snapshot_from_brain(brain)
        loop = PredictiveSelfLoop(source)
        forecast = loop.forecast(Situation("lab-inspection", "scientist"))
        # Only the disposable brain executes its native logic. PSL neither
        # triggers this step nor chooses its policy; here it merely watches.
        brain.ingest(Experience(
            "An unfamiliar apparatus is delivered to the laboratory.",
            kind="observation", novelty=.75, creation=.5,
        ))
        decision = brain.think(
            "predictive_self_shadow_demo",
            decision_text="The unfamiliar apparatus requires inspection.",
        )
        event = witnessed_policy_decision(
            brain, loop, forecast, decision["policy_decision_id"]
        )
        before_observe = brain.store.digest()
        error = loop.observe(event)
        after_observe = brain.store.digest()
        if before_observe != after_observe:
            raise AssertionError("PSL updated production BrainStore")
        return {
            "source_store_digest": source_digest,
            "manifest_digest": source.manifest_digest,
            "source_neural_action_count": len(source.actions),
            "observed_action": decision["selected_action"],
            "witness_kind": event.evidence_kind.value,
            "log_loss": round(error.action_log_loss, 8),
            "store_unchanged_by_shadow_observer": before_observe == after_observe,
            "world_result_verified": False,
            "n_scored": loop.audit()["n_scored"],
        }


def main() -> None:
    print(json.dumps({
        "protocol": "pretorius-predictive-self-loop-v0.1",
        "claim_status": "synthetic_and_native_shadow_mechanics_not_continuity_evidence",
        "synthetic": synthetic_run(),
        "native_shadow": real_brain_shadow_run(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
