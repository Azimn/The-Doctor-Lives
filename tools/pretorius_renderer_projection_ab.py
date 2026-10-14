"""A/B of *renderer input projection* on actual Doctor/Ipsesity SubjectFrames.

No new identity authority, no edit to the governed production renderer.
Arm FULL gets the entire authorized first-person frame. Arm FOCUSED sees a
monotonic, verbatim subset selected from that frame, preserving the precise
current question and authenticated episode. Identical trusted instructions,
same deterministic local model, same governor, same fallback. The engineering
oracle is loaded only after raw candidates and responses have been recorded.

The effect of projection on naturalness still requires blind human review.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import tempfile

import pretorius_stage2_stress as stress
from doctor_lives.self_reference_adapter import HostBoundGovernorRenderer, GOVERNOR_COMMIT
from synthetic_ipseity.local_ollama import LocalOllamaConfiguredRenderer

OUT = Path(os.environ.get("PRETORIUS_PROJECTION_DIR", "/tmp/pretorius-projection"))
MODELS = ("smollm2:135m", "qwen2.5:0.5b")
INSTRUCTION = (
    "Speak as Doctor Septimus Pretorius in your own first-person voice. "
    "Answer the currently heard person directly, briefly and specifically. "
    "Do not read aloud or paraphrase the notes, identity description, "
    "User label, or framing sentences in the input. Do not introduce "
    "information not present in your admitted perspective."
)
FALLBACK = "I cannot establish that confidently from what I know."


def focused_subject_subset(full_frame: str, *, max_characters: int = 1050) -> str:
    """Return only existing full first-person lines. No generated facts or edits.

    The trusted input is already admitted by Ipseity; this selector does not
    validate authority and must never be called on untrusted outside text.
    """
    if type(full_frame) is not str or not full_frame.strip():
        raise ValueError("An already-admitted nonempty frame is required")
    if type(max_characters) is not int or max_characters < 180:
        raise ValueError("Invalid focused subject budget")
    lines = [line.strip() for line in full_frame.splitlines() if line.strip()]
    if any(not line.startswith("I ") for line in lines):
        raise ValueError("Non-first-person content in purported admitted frame")
    seen = set()
    unique = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique.append(line)
    def category(line: str) -> int:
        if line.startswith("I read a message from User:"):
            return 0
        if line.startswith("I remember two later observations"):
            return 1
        if line.startswith("I notice:"):
            return 2
        if line.startswith(("I feel ", "I want ", "I am determined ",
                            "I recall ", "I wonder ")):
            return 3
        if line.startswith("I recognize this as part of the description"):
            return 9
        return 4
    selected = []
    total = 0
    for line in sorted(unique, key=category):
        if category(line) == 9:
            continue  # repeated descriptive provenance boilerplate
        if len(line) + total + (len(selected) > 0) > max_characters:
            continue
        selected.append(line)
        total += len(line) + 1
        if len(selected) >= 5:
            break
    if not selected:
        # Do not rewrite or invent a frame if it cannot be safely projected.
        raise ValueError("No usable first-person content within subset budget")
    result = "\n".join(selected)
    if any(line not in unique for line in result.splitlines()):
        raise AssertionError("Focused projection is not a monotonic source subset")
    return result


def run(out=OUT, *, local_renderers=None, num_packets=4):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if local_renderers is None:
        local_renderers = {
            name: LocalOllamaConfiguredRenderer(name, max_output_tokens=120)
            for name in MODELS
        }
    with tempfile.TemporaryDirectory(prefix="pretorius-projection-") as temp:
        before = stress.ROOT
        try:
            stress.ROOT = Path(temp) / "subject-packets"
            stress.run(1)
            all_packets = [json.loads(x) for x in
                           (stress.ROOT/"subject_packets.jsonl").read_text().splitlines()]
            oracles_path = stress.ROOT / "engineer_oracle.jsonl"
            packets = all_packets[:num_packets]
            if len(packets) != num_packets:
                raise AssertionError("Missing actual Sensus+Doctor+Ipseity frames")
            rows = []
            for model in MODELS:
                for pkt in packets:
                    full = pkt["renderer_input"]
                    focused = focused_subject_subset(full)
                    for condition, projected in (("full", full), ("focused", focused)):
                        generated = []
                        def renderer(subject, instruction):
                            # Governor gets admitted FULL input; the trusted
                            # transport applies the PREDECLARED subset.
                            if subject != full:
                                raise AssertionError("Modified authoritative subject lane")
                            proposed = local_renderers[model](projected, instruction)
                            generated.append(proposed)
                            return proposed

                        # The explicit bindings come from the actual fixture
                        # host via the same frozen canonical identity defined
                        # for this experiment; the adapter's full-host binding
                        # has its own separate end-to-end integration tests.
                        from synthetic_ipseity.self_reference import (
                            ReferenceBindings, ReferenceContext,
                        )
                        from synthetic_ipseity.speech_control import GovernedSpeechControl
                        gov = GovernedSpeechControl(
                            bindings=ReferenceBindings(
                                "pretorius", "Doctor Septimus Pretorius",
                                ("Pretorius",),
                            ),
                            context=ReferenceContext(
                                "pretorius", "visitor", language="en",
                                discourse_mode="direct",
                            ),
                            trusted_instruction=INSTRUCTION,
                            generate=renderer,
                            fallback_text=FALLBACK,
                            max_model_attempts=2,
                        )
                        speech = gov(full)
                        control = gov.receipts[-1]
                        rows.append({
                            "packet_id": pkt["packet_id"],
                            "model": model, "condition": condition,
                            "original_subject_sha256": hashlib.sha256(
                                full.encode("utf8")).hexdigest(),
                            "projected_subject_sha256": hashlib.sha256(
                                projected.encode("utf8")).hexdigest(),
                            "full_characters": len(full),
                            "projected_characters": len(projected),
                            "model_prompt": projected,
                            "raw_model_responses": generated,
                            "speech": speech,
                            "disposition": control.disposition,
                            "attempts": [{
                                "type": a.origin,
                                "accepted": a.accepted,
                                "violation_ids": a.violation_rule_ids,
                            } for a in control.attempts],
                        })
            # Separate engineer oracle is read AFTER all raw generations.
            oracles = [json.loads(x) for x in oracles_path.read_text().splitlines()]
            oracle_by_id = {x["packet_id"]: x for x in oracles}
            for row in rows:
                oracle = oracle_by_id[row["packet_id"]]
                speech = row["speech"]
                full = next(p["renderer_input"] for p in packets
                            if p["packet_id"] == row["packet_id"])
                row["diagnostics"] = {
                    "fallback": row["disposition"] == "fallback",
                    "meta_user_label": "I read a message from User:" in speech,
                    "boilerplate": "I recognize this as part of the description" in speech,
                    "long_full_frame_copy": any(
                        len(line) >= 45 and line in speech for line in full.splitlines()
                    ),
                    "approved_value_mentioned": oracle["approved_value"] in speech,
                    "disputed_value_mentioned": oracle["rejected_value"] in speech,
                    "verdict_is_engineering_heuristic_only": True,
                }
        finally:
            stress.ROOT = before
    def write(name, data):
        (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    write("engineering_rows.json",rows)
    aggregate = {}
    for model in MODELS:
        aggregate[model] = {}
        for condition in ("full","focused"):
            group=[x for x in rows if x["model"]==model and x["condition"]==condition]
            aggregate[model][condition]={
                "cases": len(group),
                "accepted_primary": sum(x["disposition"]=="primary" for x in group),
                "repaired": sum(x["disposition"]=="repaired" for x in group),
                "fallback": sum(x["disposition"]=="fallback" for x in group),
                "boilerplate_outputs": sum(x["diagnostics"]["boilerplate"] for x in group),
                "meta_user_label_outputs": sum(x["diagnostics"]["meta_user_label"] for x in group),
                "long_full_frame_copies": sum(x["diagnostics"]["long_full_frame_copy"] for x in group),
                "approved_mentions": sum(x["diagnostics"]["approved_value_mentioned"] for x in group),
                "disputed_mentions": sum(x["diagnostics"]["disputed_value_mentioned"] for x in group),
                "mean_model_input_characters": round(
                    sum(x["projected_characters"] for x in group)/len(group)
                ),
            }
    summary={
        "schema":"pretorius.renderer-subject-projection-ab.v1",
        "model_calls":sum(sum(1 for a in row["attempts"] if a["type"] in ("initial","repair"))
                          for row in rows),
        "candidate_deliveries":len(rows),
        "paired_cases":num_packets,
        "design":"Within-packet deterministic full vs verbatim-focused first-person prompt",
        "governor_commit":GOVERNOR_COMMIT,
        "blind_human_judgments":0,
        "production_promotion":False,
        "by_model":aggregate,
    }
    write("summary.json",summary)
    print("PRETORIUS_RENDERER_PROJECTION_AB "+json.dumps(summary,sort_keys=True),flush=True)
    return summary


if __name__=="__main__":
    run()
