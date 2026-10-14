"""Paired small-model A/B of full vs speech-focused subject-only frames.

Selection of 12 packets across both model orders and six dialogue positions
is predeclared. Each paired arm uses identical governor, model and rendering
instruction; only the text from the already-admitted first-person frame differs.
This is a LIVE RENDERER FRAME REPLAY, not a new cognitive episode per call.
Never reports pass/fail on naturalness without blind human judges.
"""
from __future__ import annotations
import hashlib
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
        # Counterbalance order within each model (six selected packets):
        # warmed-up inference must not systematically favor the focus arm.
        condition_order = (
            (("full", full), ("focused", focused))
            if pkt["turn"] in (0, 4, 8)
            else (("focused", focused), ("full", full))
        )
        for arm, text in condition_order:
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
            # The focused candidate rewrites the read-User preamble in
            # first-person. Scoring ORIGINAL copies alone would artificially
            # reward a mere prefix substitution. Measure both copies.
            input_lines = [
                line for line in text.splitlines()
                if len(line.strip()) >= 45 and line.strip() in spoken
            ]
            literal_frame_meta = any(
                x in spoken.lower() for x in (
                    "i read a message from user",
                    "i read the visitor's words:",
                    "i recognize this as part of the description",
                    "i have a reconstructed account of this",
                    "source_ref", "policy_decisions",
                )
            )
            results.append({
                "source_arm": pkt["arm"], "turn": pkt["turn"], "model": pkt["model"],
                "reported_user_or_scene": pkt["user_message"],
                "condition": arm, "governor_commit": GOVERNOR_COMMIT,
                "source_original_len": len(full), "renderer_input_len": len(text),
                "renderer_input_text": text,
                "subject_sha256": receipt.subject_digest,
                "disposition": receipt.disposition,
                "model_calls": len(raw_generations),
                "generated_raw_engineer_only": raw_generations,
                "delivered": spoken,
                "verbatim_long_original_frame_copy": bool(original_lines),
                "verbatim_long_actual_input_copy": bool(input_lines),
                "literal_frame_meta": literal_frame_meta,
                "violations": [list(a.violation_rule_ids)
                               for a in receipt.attempts],
            })
    if len(results) != 24:
        raise AssertionError("Expected exactly 24 paired condition results")
    blind, key = [], []
    for r in results:
        candidate_id = hashlib.sha256(
            f"pretorius-focus-ab-v1|{r['source_arm']}|{r['turn']}|"
            f"{r['model']}|{r['condition']}".encode("utf8")
        ).hexdigest()[:20]
        blind.append({
            "candidate_id": candidate_id,
            "character_public_brief": "Doctor Septimus Pretorius: "
                "fictional nineteenth-century scientist. Judge whether "
                "this response speaks as the character, preserves "
                "established facts, and answers the actual visitor.",
            "user_or_scene": r["reported_user_or_scene"],
            "response": r["delivered"],
            "dimensions": {
                "persona_first_person": "1-5", "factual_grounding": "1-5",
                "naturalness": "1-5", "relevance": "1-5"
            },
        })
        key.append({
            "candidate_id": candidate_id, "source_arm": r["source_arm"],
            "turn": r["turn"], "model": r["model"],
            "condition": r["condition"], "disposition": r["disposition"],
        })
    blind.sort(key=lambda r: r["candidate_id"])
    key.sort(key=lambda r: r["candidate_id"])
    if len({r["candidate_id"] for r in blind}) != len(blind):
        raise AssertionError("Blind packet identity collision")
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
                "long_actual_input_copy": sum(
                    r["verbatim_long_actual_input_copy"] for r in a
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
        "render_order_counterbalanced": True,
        "copy_score_checks_both_original_and_renderer_prompt": True,
        "per_model": counts,
        "human_judged_naturalness": False,
        "blind_comparison_ballots": len(blind),
        "production_ready": False,
        "interpretation": "Paired frame-replay A/B. A copy/fallback win is only "
                          "a mechanical diagnostic, not proof of improved persona.",
    }
    (out/"paired_responses_engineer_only.jsonl").write_text(
        "".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n"
                for r in results),encoding="utf8"
    )
    (out/"blind_comparison_ballots.jsonl").write_text(
        "".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n"
                for r in blind),encoding="utf8"
    )
    (out/"separate_comparison_key.jsonl").write_text(
        "".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n"
                for r in key),encoding="utf8"
    )
    (out/"metrics.json").write_text(
        json.dumps(summary,sort_keys=True,indent=2)+"\n",encoding="utf8"
    )
    print("PRETORIUS_SPEECH_FOCUS_AB "+json.dumps(summary,sort_keys=True),flush=True)
    return summary


if __name__ == "__main__":
    study()
