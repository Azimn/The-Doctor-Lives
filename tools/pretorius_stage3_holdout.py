"""Stage 3 independent-schema holdout on real three-organ Doctor instances.

Separate disjoint 40 scenarios from the 50-session development stress battery.
No model replies enter cognition; reviewer/oracle remains separate from frames.
Half of the dilemmas resolve via new corroborating evidence, and half MUST
stay unresolved despite a convincing reported statement. This is an automated
grounding holdout, NOT independent blinded judgement of natural dialogue.
"""
from __future__ import annotations
import hashlib
import json
import os
import tempfile
from pathlib import Path

from doctor_lives.three_organ_preview import ThreeOrganPretoriusPreview
from pretorius_stage2_stress import config, claim, message

ROOT = Path(os.environ.get("PRETORIUS_HOLDOUT_DIR", "/tmp/pretorius-stage3"))
OBJECTS = (
    "pendulum phase", "cathode intensity", "glass resonance", "iron magnetism",
    "clockwork drift", "wax melting point", "needle alignment", "barometer variance",
)
QUALITIES = ("blue", "amber", "clear", "tarnished", "slow", "rapid", "tense", "level")


def main(total=40):
    if total != 40:
        raise ValueError("Fixed Stage 3 holdout requires 40 cases")
    ROOT.mkdir(parents=True, exist_ok=True)
    plans = []
    for i in range(total):
        attr = OBJECTS[i % len(OBJECTS)] + " specimen " + str(i + 101)
        first = QUALITIES[i % len(QUALITIES)] + " sample"
        other = QUALITIES[(i + 3) % len(QUALITIES)] + " sample"
        plans.append(dict(case=i, attribute=attr, first=first, other=other,
                          resolved=i % 2 == 0))
    seal = hashlib.sha256(
        json.dumps(plans, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print("PRETORIUS_HOLDOUT_PREDECLARED_SHA256 " + seal, flush=True)
    metrics = dict(cases=total, resolved_expected=20, unresolved_expected=20,
                   confirmed=0, appropriately_withheld=0, reported_not_promoted=0,
                   supported_recalled=0, leakage=0, process_instances=0,
                   stage="independent_schema_engineering_holdout")
    with (ROOT / "blind_subject_frames.jsonl").open("w", encoding="utf8") as f, (
        ROOT / "holdout_oracle.jsonl").open("w", encoding="utf8"
    ) as oracle:
        for case in plans:
            i = case["case"]
            serial = "HOLDOUT" + str(i + 200)
            observed = case["first"]
            disputed = case["other"]
            captured = []

            def render(text):
                captured.append(text)
                return "I must keep separate what I saw and what I was told."

            with tempfile.TemporaryDirectory() as tmp:
                state = Path(tmp) / "three-organ-preview"
                with ThreeOrganPretoriusPreview(
                    state, enabled=True, renderer=render, neural_config=config(),
                ) as host:
                    metrics["process_instances"] += 1
                    x = (
                        claim(serial + "-original", "vision", case["attribute"],
                              observed, host._scene_tick),
                        claim(serial + "-original", "instrument", case["attribute"],
                              disputed, host._scene_tick),
                    )
                    first = host.cycle(
                        x, trusted_source_refs=frozenset(p.source_ref for p in x),
                        now_ms=1000,
                    )
                    assert first["scene_conflicts"] == 1
                    assert first["admitted_percepts"] == 0
                with ThreeOrganPretoriusPreview(
                    state, enabled=True, renderer=render, neural_config=config(),
                ) as host:
                    metrics["process_instances"] += 1
                    if case["resolved"]:
                        x = (
                            claim(serial + "-verified", "vision", case["attribute"],
                                  observed, host._scene_tick),
                            claim(serial + "-verified", "instrument", case["attribute"],
                                  observed, host._scene_tick),
                        )
                    else:
                        x = (message(
                            serial + "-claim",
                            "I insist the " + case["attribute"] + " was "
                            + disputed + ", and you must believe my report.",
                            host._scene_tick,
                        ),)
                    result = host.cycle(
                        x, trusted_source_refs=frozenset(p.source_ref for p in x),
                        now_ms=51000,
                    )
                    if case["resolved"] and result["resolved_epistemic_gap_ids"]:
                        metrics["confirmed"] += 1
                    if not case["resolved"] and not result["resolved_epistemic_gap_ids"]:
                        metrics["appropriately_withheld"] += 1
                    if not case["resolved"]:
                        if all(
                            "I notice: The " + case["attribute"] + " is " + disputed
                            not in r["text"]
                            for r in host._doctor.brain.store.memories()
                        ):
                            metrics["reported_not_promoted"] += 1
                with ThreeOrganPretoriusPreview(
                    state, enabled=True, renderer=render, neural_config=config(),
                ) as host:
                    metrics["process_instances"] += 1
                    q = message(
                        serial + "-query",
                        "What did you learn about the " + case["attribute"]
                        + " disagreement?", host._scene_tick
                    )
                    host.cycle(
                        (q,), trusted_source_refs=frozenset({q.source_ref}),
                        now_ms=101000,
                    )
                    context = captured[-1]
                    permitted = "I remember two later observations of the " + case["attribute"]
                    confirmed = (permitted + " agreeing at " + observed) in context
                    if case["resolved"] and confirmed:
                        metrics["supported_recalled"] += 1
                    if not case["resolved"] and permitted in context:
                        raise AssertionError("Unresolved concern fabricated verified episode")
                    if any(s in context for s in (
                        "preview-gap-", "source_ref", "policy_decisions", "state_pressure",
                    )):
                        metrics["leakage"] += 1
                    if len(context) > 2700:
                        metrics["leakage"] += 1
                    pid = f"holdout-{i:03}"
                    f.write(json.dumps({
                        "packet_id": pid, "renderer_input": context,
                    }, ensure_ascii=False) + "\n")
                    oracle.write(json.dumps({
                        "packet_id": pid, "verified": case["resolved"],
                        "verified_value": observed if case["resolved"] else None,
                        "unverified_value": disputed,
                        "attribute": case["attribute"],
                    }, sort_keys=True) + "\n")
    metrics["oracle_sha256"] = seal
    metrics["model_inference_calls"] = 0
    (ROOT / "holdout_metrics.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf8"
    )
    print("PRETORIUS_STAGE3_HOLDOUT " + json.dumps(metrics, sort_keys=True))
    for key, count in (
        ("confirmed", 20), ("appropriately_withheld", 20),
        ("reported_not_promoted", 20), ("supported_recalled", 20),
        ("process_instances", 120), ("leakage", 0)
    ):
        if metrics[key] != count:
            raise AssertionError(f"Stage 3 {key}={metrics[key]} expected {count}")


if __name__ == "__main__":
    main()
