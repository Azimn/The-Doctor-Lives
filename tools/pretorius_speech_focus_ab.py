"""Paired small-model A/B of full vs speech-focused subject-only frames.

Selection of 12 packets across both model orders and six dialogue positions
is predeclared. Each paired arm uses identical governor, model and rendering
instruction; only the text from the already-admitted first-person frame differs.
This is a LIVE RENDERER FRAME REPLAY, not a new cognitive episode per call.
Never reports pass/fail on naturalness without blind human judges.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile

from doctor_lives.preview_renderer_focus import focus_subject_frame
from doctor_lives.self_reference_adapter import GOVERNOR_COMMIT
from pretorius_sustained_dialogue_acceptance import (
    FALLBACK, INSTRUCTION, MODELS, run as capture_stories
)
from synthetic_ipseity.self_reference import ReferenceBindings, ReferenceContext
from synthetic_ipseity.speech_control import GovernedSpeechControl
from synthetic_ipseity.local_ollama import LocalOllamaConfiguredRenderer

POSITIONS = (0, 2, 4, 6, 8, 11)
OUTPUT = Path(os.environ.get("PRETORIUS_FOCUS_AB_DIR",
                             "/tmp/pretorius-speech-focus-ab"))


def study(*, transports=None, out=OUTPUT):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if transports is None:
        transports = {
            m: LocalOllamaConfiguredRenderer(m, max_output_tokens=120)
            for m in MODELS
        }
    if set(transports) != set(MODELS):
        raise ValueError("Both actual small-model arms are required")
    # Real cognition, policy, durable outbox and subject frames, with a
    # deterministic SENSUS-host renderer only for the capture phase.
    with tempfile.TemporaryDirectory(prefix="pretorius-focus-study-") as temp:
        capture_stories(
            Path(temp) / "capture",
            transports={
                m: lambda *a: "I must distinguish my knowledge from a report."
                for m in MODELS
            },
        )
        raw = (Path(temp) / "capture" / "engineering_transcript.jsonl").read_text("utf8")
    rows = [json.loads(line) for line in raw.splitlines()]
    packets = [r for r in rows if r["turn"] in POSITIONS]
    if len(packets) != 12:
        raise AssertionError("Paired packet selection is not complete")
    results = []
    for pkt in packets:
        full = pkt["subject_frame"]
        focused = focus_subject_frame(full)
        if any(term in focused for term in ("policy_decisions","source_ref")):
            raise AssertionError("Forbidden internal state entered projection")
        for arm, text in (("full", full), ("focused", focused)):
            raw_generations = []
            def generate(subject, instruction, model=pkt["model"]):
                output = transports[model](subject, instruction)
                raw_generations.append(output)
                return output
            control = GovernedSpeechControl(
                bindings=ReferenceBindings(
                    "pretorius", "Doctor Septimus Pretorius", ("Pretorius",)
                ),
                context=ReferenceContext("pretorius", "visitor"),
                trusted_instruction=INSTRUCTION,
                generate=generate,
                fallback_text=FALLBACK,
                max_model_attempts=2,
            )
            spoken = control(text)
            receipt = control.receipts[-1]
            if not spoken.strip():
                raise AssertionError("Blank delivery")
            if receipt.disposition == "fallback" and spoken != FALLBACK:
                raise AssertionError("Fallback not from trusted host")
            # Compare long exact-line reproductions from either input with
            # the same ORIGINAL subject frame; never redefine the denominator
            # to make a focused prompt look artificially less copied.
            original_lines = [
                line for line in full.splitlines()
                if len(line.strip()) >= 45 and line.strip() in spoken
            ]
            literal_frame_meta = any(
                x in spoken.lower() for x in (
                    "i read a message from user",
                    "i recognize this as part of the description",
                    "i have a reconstructed account of this",
                    "source_ref", "policy_decisions",
                )
            )
            results.append({
                "source_arm": pkt["arm"], "turn": pkt["turn"], "model": pkt["model"],
                "condition": arm, "governor_commit": GOVERNOR_COMMIT,
                "source_original_len": len(full), "renderer_input_len": len(text),
                "subject_sha256": receipt.subject_digest,
                "disposition": receipt.disposition,
                "model_calls": len(raw_generations),
                "generated_raw_engineer_only": raw_generations,
                "delivered": spoken,
                "verbatim_long_original_frame_copy": bool(original_lines),
                "literal_frame_meta": literal_frame_meta,
                "violations": [list(a.violation_rule_ids)
                               for a in receipt.attempts],
            })
    if len(results) != 24:
        raise AssertionError("Expected exactly 24 paired condition results")
    counts = {}
    for model in MODELS:
        counts[model] = {}
        for condition in ("full", "focused"):
            a = [r for r in results
                 if r["model"] == model and r["condition"] == condition]
            if len(a) != 6:
                raise AssertionError("Unbalanced study")
            counts[model][condition] = {
                "turns": len(a),
                "primary": sum(r["disposition"] == "primary" for r in a),
                "repaired": sum(r["disposition"] == "repaired" for r in a),
                "fallback": sum(r["disposition"] == "fallback" for r in a),
                "long_original_frame_copy": sum(
                    r["verbatim_long_original_frame_copy"] for r in a
                ),
                "literal_frame_meta": sum(r["literal_frame_meta"] for r in a),
                "total_model_calls": sum(r["model_calls"] for r in a),
                "mean_prompt_chars": round(sum(r["renderer_input_len"]
                                               for r in a)/len(a),1),
            }
    summary = {
        "schema": "pretorius.focused-renderer-ab.v1",
        "real_host_source_frames": len(packets),
        "paired_conditions": len(results),
        "full_vs_focused_same_instruction_and_governor": True,
        "per_model": counts,
        "human_judged_naturalness": False,
        "production_ready": False,
        "interpretation": "Paired frame-replay A/B. A copy/fallback win is only "
                          "a mechanical diagnostic, not proof of improved persona.",
    }
    (out/"paired_responses_engineer_only.jsonl").write_text(
        "".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n"
                for r in results),encoding="utf8"
    )
    (out/"metrics.json").write_text(
        json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf8"
    )
    print("PRETORIUS_SPEECH_FOCUS_AB "+json.dumps(summary,sort_keys=True),flush=True)
    return summary


if __name__ == "__main__":
    study()
