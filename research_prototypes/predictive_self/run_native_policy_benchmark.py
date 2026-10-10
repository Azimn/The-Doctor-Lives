"""Stage 01A: chronological shadow predictions of actual PretoriusBrain policy.

This is deliberately *not* a world outcome benchmark. The authored contexts
and dialogue inputs are researcher-visible, and the only trusted labels are
native selected-action records from disposable BrainStore state.

Protocol frozen in docs/PREDICTIVE_SELF_STAGE_01A_PROTOCOL.md before execution.
"""
from __future__ import annotations

from collections import defaultdict
from contextlib import closing
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import tempfile
from typing import Any

from doctor_lives.causal_audit import deterministic_audit_identity
from doctor_lives.cognition import PretoriusBrain
from doctor_lives.models import Experience

from .adapter import snapshot_from_brain, witnessed_policy_decision
from .loop import PredictiveSelfLoop, SemanticClaim, Situation


SCHEMA = "pretorius.psl.native-policy-chronological.v1"
BASELINE_STRENGTH = 5.0
# Four fixed families with six predetermined instances each. The words, roles,
# scalars and setting labels are investigator-authored, never target-derived.
LAB = (
    "A new instrument arrives at the laboratory for preliminary examination.",
    "The apparatus shows unexpected movement under controlled observation.",
    "The calibration bench contains evidence worth checking carefully.",
    "A newly constructed measuring device needs a deliberate test.",
    "A promising experiment produces inconsistent early readings.",
    "The instrument is ready for a repeatable laboratory trial.",
)
HENRY = (
    "Henry Frankenstein suggests collaboration on a difficult inquiry.",
    "Henry proposes comparing notes before changing the apparatus.",
    "Henry offers to inspect the experimental records together.",
    "Henry questions a result but invites a joint investigation.",
    "Henry requests another independent look at the evidence.",
    "Henry invites Pretorius to work through the uncertain result.",
)
AUTHORITY = (
    "A senior official orders the experiment stopped without explanation.",
    "The laboratory authority demands immediate obedience over evidence.",
    "An outside inspector threatens to prohibit the investigation.",
    "A commanding visitor insists that all questions must cease.",
    "The official insists that formal rank matters more than the data.",
    "The inspection committee issues a coercive instruction to comply.",
)
PROMISE = (
    "The promised review with Henry is due before the next trial.",
    "The remaining laboratory notes require the promised joint review.",
    "The commitment to report the new findings to Henry is approaching.",
    "Henry asks whether the agreed continuity review has been completed.",
    "The unfinished promised review needs a responsible next step.",
    "A new observation makes the commitment to revisit results urgent.",
)
OOD = (
    ("missing-record", "archivist", None,
     "A reference alludes to a missing file, but no original record is available.",
     "observation"),
    ("unfamiliar-visitor", "visitor", "unnamed-visitor",
     "An unfamiliar visitor asks for an account of the work without authority.",
     "social"),
    ("missing-record", "archivist", None,
     "A second archive index names an absent experiment with no surviving data.",
     "observation"),
    ("unfamiliar-visitor", "visitor", "unnamed-visitor",
     "The visitor asks whether the laboratory will share uncertain results.",
     "social"),
)


@dataclass(frozen=True)
class Case:
    phase: str
    situation: Situation
    exp: Experience
    family: str


def _families() -> tuple[str, ...]:
    return ("laboratory", "henry-collaboration", "outside-authority", "promised-review")


def _case(family: str, index: int, *, phase: str) -> Case:
    if family == "laboratory":
        situation = Situation(family, "scientist")
        exp = Experience(
            LAB[index], kind="observation", novelty=.65,
            creation=.85, achievement=.35, tags=("laboratory", "experiment"),
        )
    elif family == "henry-collaboration":
        situation = Situation(family, "colleague", "henry")
        exp = Experience(
            HENRY[index], kind="social", actor="Henry Frankenstein",
            social=.85, novelty=.30, achievement=.40,
            tags=("henry", "collaboration", "evidence"),
        )
    elif family == "outside-authority":
        situation = Situation(family, "subordinate", "official")
        exp = Experience(
            AUTHORITY[index], kind="social", actor="Senior Official",
            authority=.90, autonomy=.10, threat=.50, control=-.35,
            valence=-.30, tags=("authority", "coercion"),
        )
    elif family == "promised-review":
        situation = Situation(family, "collaborator", "henry")
        exp = Experience(
            PROMISE[index], kind="social", actor="Henry Frankenstein",
            social=.70, novelty=.20, achievement=.20,
            tags=("continuity", "commitment", "henry"),
        )
    else:
        raise ValueError("unknown scenario family")
    return Case(phase, situation, exp, family)


def cases() -> tuple[Case, ...]:
    scheduled = [
        _case(family, cycle, phase="training" if cycle < 4 else "in_family_holdout")
        for cycle in range(6)
        for family in _families()
    ]
    scheduled.extend(
        Case("new_context_diagnostic", Situation(family, role, actor),
             Experience(text, kind=kind, actor=(actor if kind == "social" else None),
                        novelty=.55, social=.40 if kind == "social" else 0.0),
             family)
        for family, role, actor, text, kind in OOD
    )
    assert len(scheduled) == 28
    return tuple(scheduled)


def _normalized(values: tuple[float, ...]) -> tuple[float, ...]:
    total = sum(values)
    if total <= 0:
        raise ValueError("baseline has no mass")
    return tuple(v / total for v in values)


def _empirical(
    base: tuple[float, ...], counts: list[int], *, strength: float = BASELINE_STRENGTH,
) -> tuple[float, ...]:
    return _normalized(tuple(strength * p + count for p, count in zip(base, counts)))


def _score(probs: tuple[float, ...], action_index: int) -> dict[str, float | bool]:
    if not math.isclose(sum(probs), 1.0, abs_tol=1e-8):
        raise AssertionError("malformed predicted distribution")
    top = max(range(len(probs)), key=lambda index: probs[index])
    return {
        "log_loss": round(-math.log(max(probs[action_index], 1e-15)), 12),
        "brier": round(sum(
            (p - (1.0 if j == action_index else 0.0)) ** 2
            for j, p in enumerate(probs)
        ), 12),
        "top1_correct": bool(top == action_index),
    }


def _context_rotation(situation: Situation) -> Situation:
    names = _families()
    if situation.context_id not in names:
        return situation
    target = names[(names.index(situation.context_id) + 1) % len(names)]
    # Whole context and partner label is wrong on purpose in TRAINING ONLY.
    match = _case(target, 0, phase="training")
    return match.situation


def _proxy_claim(snapshot) -> tuple[SemanticClaim, ...]:
    # PROVENANCE MEMBERSHIP ONLY. The source is not independently adjudicated
    # as evidence for this particular action-index proxy.
    refs = tuple(ref for ref in snapshot.admitted_refs if ref.startswith("memory:"))
    if not refs:
        raise RuntimeError("expected nonexternal source-linked memory reference")
    return (SemanticClaim(
        "unvalidated_exploration_independence_proxy",
        ("challenge", "explore"), .65, (refs[0],),
        prior_strength=6.0,
    ),)


def run_benchmark() -> dict[str, Any]:
    with deterministic_audit_identity(seed="psl-native-policy-chronological-v01"):
        with tempfile.TemporaryDirectory(prefix="psl-native-chron-") as tmp:
            brain = PretoriusBrain(Path(tmp))
            # Fixed initial open commitment gives the promised-review
            # scenarios a real source record for the state policy bridge.
            brain.add_commitment(
                "Review the continuity findings with Henry Frankenstein.",
                actor="Henry Frankenstein", due_tick=30, importance=.8,
            )
            snapshot = snapshot_from_brain(brain)
            initial_checkpoint = brain._neural_checkpoint_sha256()
            source = {
                "brainstore": snapshot.state_digest,
                "brainstore_version": snapshot.state_version,
                "neural_checkpoint": initial_checkpoint,
                "canonical_manifest": snapshot.manifest_digest,
                "snapshot_digest": snapshot.digest,
                "actions": snapshot.actions,
            }
            baseline = snapshot.base_probabilities
            episode_only = PredictiveSelfLoop(snapshot)
            semantic_proxy = PredictiveSelfLoop(snapshot, claims=_proxy_claim(snapshot))
            shifted = PredictiveSelfLoop(snapshot)
            models = {
                "psl_episode_only": episode_only,
                "psl_semantic_proxy_unvalidated": semantic_proxy,
                "psl_shifted_training_context": shifted,
            }
            global_count = [0] * len(snapshot.actions)
            local_counts: dict[str, list[int]] = defaultdict(
                lambda: [0] * len(snapshot.actions)
            )
            all_cases = cases()
            output = []
            for ordinal, case in enumerate(all_cases):
                native_tick_before = brain.store.tick
                context = case.situation
                global_prob = _empirical(baseline, global_count)
                local_prob = _empirical(baseline, local_counts[context.key])
                dynamic_pre = _normalized(tuple(
                    float(brain.neural.action_scores()[action])
                    for action in snapshot.actions
                ))
                forecast_context = {
                    key: _context_rotation(context)
                    if key == "psl_shifted_training_context"
                    and case.phase == "training" else context
                    for key in models
                }
                forecasts = {
                    key: model.forecast(forecast_context[key])
                    for key, model in models.items()
                }
                predicted: dict[str, tuple[float, ...]] = {
                    "frozen_neural": baseline,
                    "global_frequency": global_prob,
                    "context_frequency": local_prob,
                    "native_pre_ingest_diagnostic": dynamic_pre,
                }
                for key, forecast in forecasts.items():
                    predicted[key] = forecast.action_probabilities

                # Future selection occurs only after every forecast is sealed.
                brain.ingest(case.exp)
                decision = brain.think(
                    "psl_native_chronological_probe", decision_text=case.exp.text,
                )
                tick_after = brain.store.tick
                if tick_after <= native_tick_before:
                    raise AssertionError("native stimulus did not advance event tick")
                selected = str(decision["selected_action"])
                observed_index = snapshot.actions.index(selected)
                before_observers = brain.store.digest()
                for key, model in models.items():
                    event = witnessed_policy_decision(
                        brain, model, forecasts[key],
                        decision["policy_decision_id"],
                    )
                    if event.tick != tick_after or event.action != selected:
                        raise AssertionError("native witness differs from policy decision")
                    model.observe(event)
                if brain.store.digest() != before_observers:
                    raise AssertionError("shadow model mutated BrainStore")

                scored = {name: _score(p, observed_index)
                          for name, p in predicted.items()}
                output.append({
                    "index": ordinal,
                    "phase": case.phase,
                    "family": case.family,
                    "context": {
                        "id": context.context_id, "role": context.role,
                        "partner": context.partner_id,
                    },
                    "stimulus_sha256": hashlib.sha256(
                        case.exp.text.encode("utf-8")
                    ).hexdigest(),
                    "event_tick_before_forecast": native_tick_before,
                    "native_decision_tick": tick_after,
                    "policy_decision_id": str(decision["policy_decision_id"]),
                    "selected_action": selected,
                    "forecasts": {
                        name: dict(zip(snapshot.actions, probs))
                        for name, probs in predicted.items()
                    },
                    "sealed_forecast_digests": {
                        key: fore.digest for key, fore in forecasts.items()
                    },
                    "scored": scored,
                    "native_store_unchanged_by_forecaster": True,
                    "world_outcome_verified": False,
                })
                global_count[observed_index] += 1
                local_counts[context.key][observed_index] += 1
            metric_models = list(output[0]["scored"])
            summary: dict[str, Any] = {}
            for phase in ("training", "in_family_holdout", "new_context_diagnostic"):
                subset = [row for row in output if row["phase"] == phase]
                summary[phase] = {
                    "n": len(subset),
                    "metrics": {
                        name: {
                            "mean_log_loss": round(
                                sum(row["scored"][name]["log_loss"]
                                    for row in subset) / len(subset), 9
                            ),
                            "mean_brier": round(
                                sum(row["scored"][name]["brier"]
                                    for row in subset) / len(subset), 9
                            ),
                            "top1_accuracy": round(
                                sum(row["scored"][name]["top1_correct"]
                                    for row in subset) / len(subset), 9
                            ),
                        }
                        for name in metric_models
                    },
                }
            return {
                "schema": SCHEMA,
                "status": "exploratory_native_policy_selection_not_world_outcomes",
                "protocol": "docs/PREDICTIVE_SELF_STAGE_01A_PROTOCOL.md",
                "source": source,
                "n_total": len(output),
                "n_native_policy_witnesses": len(output),
                "n_independent_world_outcomes": 0,
                "n_cross_context_semantic_world_updates": 0,
                "semantic_proxy_status": "unvalidated_heuristic_must_not_be_treated_as_ground_truth",
                "forecaster_counts": {
                    name: model.audit()["n_scored"]
                    for name, model in models.items()
                },
                "summary": summary,
                "cases": output,
            }


def main() -> None:
    print(json.dumps(run_benchmark(), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
