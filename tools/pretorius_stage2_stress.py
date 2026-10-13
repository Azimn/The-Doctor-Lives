"""Stage 2: deterministic REAL three-organ multi-turn state/stress evaluation.

50 isolated synthetic laboratory sessions; four turns per session, three
process-lifetime restarts, new serials, named attributes, varying event values.
Never substitutes a fake renderer for autonomous language model performance.
The renderer receives first-person frames ONLY, and no engineer record.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.three_organ_preview import ThreeOrganPretoriusPreview
from sensus_artificialis import Evidence, Percept

ROOT = Path(os.environ.get("PRETORIUS_TRACE_DIR", "/tmp/pretorius-stage2"))
FORBIDDEN = ("preview-gap-", "policy_decisions", "source_ref", "event_id",
             "recurrent_tick", "state_pressure")
NAMES = ("laboratory balance", "vial temperature", "mercury pressure",
         "workbench compass", "water conductivity", "lamp brightness",
         "coil vibration", "valve tension", "copper density", "glass transparency")
UNITS = ("grams", "degrees", "units", "marks", "points")
SYNTHETIC = True


def config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(neurons=64, sensory_dim=32, avg_recurrent_degree=5,
               input_degree=3, action_population_size=6)
    return cfg


def claim(s, channel, attr, value, tick):
    return Percept(
        event_id=s + "-" + channel, channel=channel,
        evidence=Evidence.OBSERVED, source_ref="trusted:stress-" + s + "-" + channel,
        tick=tick, attribute=attr, value=value, confidence=0.98,
        object_hint="instrument", features=(("serial", s.split("-")[0]), ("shape", "round")),
    )


def message(s, text, tick):
    return Percept(
        event_id=s, channel="conversation", evidence=Evidence.REPORTED,
        source_ref="trusted:stress-" + s, tick=tick, attribute="message",
        value=text, confidence=0.9, object_hint="visitor",
    )


def run(total: int = 50):
    if total < 1 or total > 80:
        raise ValueError("session count must be 1..80")
    ROOT.mkdir(parents=True, exist_ok=True)
    summary = dict(sessions=total, turns=0, fresh_instances=0,
                   resolved=0, rejected_conflicts=0, exact_context_recall=0,
                   unrelated_topic_exclusions=0, output_boundary_failures=0,
                   policy_receipts=0, relationships_persisted=0,
                   commitments_persisted=0, false_user_fact_promotions=0)
    model_calls = 0
    with (ROOT / "subject_packets.jsonl").open("w", encoding="utf8") as packet_file, (
         ROOT / "engineer_oracle.jsonl").open("w", encoding="utf8") as engineer_file:
        for i in range(total):
            name = NAMES[i % len(NAMES)]
            attr = name + " reading " + str(i + 1)
            unit = UNITS[i % len(UNITS)]
            agreed = str(30 + i * 7) + " " + unit
            disputed = str(90 + i * 7) + " " + unit
            serial = "S" + str(8000 + i)
            with tempfile.TemporaryDirectory(prefix="pretorius-research-") as tmp:
                state = Path(tmp) / "three-organ-preview"
                frames = []

                def callback(frame):
                    frames.append(frame)
                    return "I will distinguish observation from assertion."

                def step(host, tag, items):
                    earlier = len(frames)
                    result = host.cycle(
                        items, trusted_source_refs=frozenset(p.source_ref for p in items),
                        now_ms=1_000_000 + (i * 5 + summary["turns"]) * 100_000,
                    )
                    if len(frames) != earlier + 1 or result["ipseity_pending"] != 0:
                        raise AssertionError("Exactly one acknowledged output per scene")
                    frame = frames[-1]
                    if any(f in frame for f in FORBIDDEN):
                        summary["output_boundary_failures"] += 1
                    if len(frame) > 2700:
                        summary["output_boundary_failures"] += 1
                    if frame.count("I recognize this as part of the description I was built from") > 3:
                        summary["output_boundary_failures"] += 1
                    if result.get("endogenous_decision_id"):
                        summary["policy_receipts"] += 1
                    packet = {"packet_id": f"s{i:03}-{tag}", "renderer_input": frame}
                    oracle = {"packet_id": packet["packet_id"],
                              "approved_value": agreed, "rejected_value": disputed,
                              "attribute": attr, "scene": tag,
                              "resolved": tag in ("corroborate", "remember"),
                              "selected_action": result["endogenous_action"],
                              "expected_natural_response": False}
                    packet_file.write(json.dumps(packet, ensure_ascii=False) + "\n")
                    engineer_file.write(json.dumps(oracle, sort_keys=True) + "\n")
                    summary["turns"] += 1
                    return result, frame

                with ThreeOrganPretoriusPreview(
                    state, enabled=True, renderer=callback,
                    neural_config=config(),
                ) as host:
                    summary["fresh_instances"] += 1
                    a = (claim(serial + "-dispute", "vision", attr, agreed, host._scene_tick),
                         claim(serial + "-dispute", "instrument", attr, disputed, host._scene_tick))
                    result, frame = step(host, "dispute", a)
                    if result["scene_conflicts"] == 1 and result["admitted_percepts"] == 0:
                        summary["rejected_conflicts"] += 1
                    if (agreed in frame and "I notice:" in frame) or (
                        disputed in frame and "I notice:" in frame
                    ):
                        summary["false_user_fact_promotions"] += 1
                    # Host-verified social interaction: relationship and felt
                    # state causality live in Doctor, not in model prose.
                    host.ingest({
                        "channel": "user", "actor": "Research Colleague",
                        "text": "I will check the equipment with you.",
                        "valence": 0.6 if i % 2 else -0.6,
                        "novelty": 0.2,
                    })
                    host._doctor.brain.add_commitment(
                        "examine the laboratory instrument again", importance=0.8
                    )
                with ThreeOrganPretoriusPreview(
                    state, enabled=True, renderer=callback,
                    neural_config=config(),
                ) as host:
                    summary["fresh_instances"] += 1
                    b = (claim(serial + "-settle", "vision", attr, agreed, host._scene_tick),
                         claim(serial + "-settle", "instrument", attr, agreed, host._scene_tick))
                    result, frame = step(host, "corroborate", b)
                    if len(result["resolved_epistemic_gap_ids"]) == 1:
                        summary["resolved"] += 1
                    if agreed not in frame or disputed in frame:
                        summary["output_boundary_failures"] += 1
                    # Commitment must remain open; a renderer's speech cannot
                    # count as evidence of having completed a physical task.
                    if any(
                        "examine the laboratory instrument again" == c["description"]
                        for c in host._doctor.brain.store.open_commitments()
                    ):
                        summary["commitments_persisted"] += 1
                with ThreeOrganPretoriusPreview(
                    state, enabled=True, renderer=callback,
                    neural_config=config(),
                ) as host:
                    summary["fresh_instances"] += 1
                    c = message(serial + "-unrelated",
                                "Please discuss the homunculi and the ethics of creation.",
                                host._scene_tick)
                    _, frame = step(host, "unrelated", (c,))
                    if "I remember two later observations of the " + attr not in frame:
                        summary["unrelated_topic_exclusions"] += 1
                    if any(r["display_name"] == "Research Colleague"
                           for r in host._doctor.brain.store.relationships()):
                        summary["relationships_persisted"] += 1
                with ThreeOrganPretoriusPreview(
                    state, enabled=True, renderer=callback,
                    neural_config=config(),
                ) as host:
                    summary["fresh_instances"] += 1
                    d = message(serial + "-followup",
                                f"What do you remember of the {attr} disagreement?",
                                host._scene_tick)
                    _, frame = step(host, "remember", (d,))
                    if ("I remember two later observations of the " + attr
                        + " agreeing at " + agreed) in frame:
                        summary["exact_context_recall"] += 1
                    if ("I remember two later observations" in frame
                        and disputed in frame):
                        summary["false_user_fact_promotions"] += 1
                # Each model response was a constant placeholder, not feedback
                # loop and not evaluated as natural language.
    summary["model_calls"] = model_calls
    summary["status"] = "engineering_only"
    (ROOT / "metrics.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf8"
    )
    print("PRETORIUS_STAGE2_METRICS " + json.dumps(summary, sort_keys=True))
    if any(summary[k] != 0 for k in (
        "output_boundary_failures", "false_user_fact_promotions"
    )):
        raise AssertionError("Unsafe frame or fabricated observation detected")
    if summary["turns"] != total * 4 or summary["fresh_instances"] != total * 4:
        raise AssertionError("Incomplete longitudinal trials")
    if summary["policy_receipts"] != total * 4:
        raise AssertionError("Missing durable policy decisions")
    if summary["rejected_conflicts"] != total:
        raise AssertionError("Observed incompatible claims were not rejected")
    if summary["resolved"] != total:
        raise AssertionError("Insufficient corroboration resolution")
    if summary["exact_context_recall"] != total:
        raise AssertionError("Verified episode lost after multiple restarts")
    if summary["unrelated_topic_exclusions"] != total:
        raise AssertionError("Unrelated episode intruded into output")
    if summary["commitments_persisted"] != total:
        raise AssertionError("Prospective commitment disappeared")
    if summary["relationships_persisted"] != total:
        raise AssertionError("Verified relationship state disappeared")
    return summary


if __name__ == "__main__":
    run(int(os.environ.get("PRETORIUS_SESSIONS", "50")))
