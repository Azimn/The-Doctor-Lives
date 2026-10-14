"""Small-model CAPACITY experiment at fixed Pretorius cognition and speech focus.

Qwen2.5 0.5B vs 1.5B; both receive the SAME host-authenticated first-person
speech-focused frames and the SAME governor instruction, one repair max and
exact host fallback. No renderer code or model output can change Doctor identity,
typed memory, policy, or evidence provenance. No paid API.

This is replay of Sensus+Doctor+Synthetic Ipseity frames captured from a real
longitudinal host, not a full independent cognitive state update per call.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile

from doctor_lives.preview_renderer_focus import focus_subject_frame
from pretorius_sustained_dialogue_acceptance import (
    FALLBACK, INSTRUCTION, MODELS as OLD_MODELS,
    run as capture_real_host,
)
from synthetic_ipseity.local_ollama import LocalOllamaConfiguredRenderer
from synthetic_ipseity.self_reference import ReferenceBindings, ReferenceContext
from synthetic_ipseity.speech_control import GovernedSpeechControl

MODELS = ("qwen2.5:0.5b", "qwen2.5:1.5b")
POSITIONS = (0, 2, 4, 6, 8, 11)
OUTPUT = Path(os.environ.get("PRETORIUS_CAPACITY_AB_DIR", "/tmp/pretorius-capacity"))
_META = (
    "i read a message from user", "i read the visitor's words",
    "i recognize this as part of the description",
    "the next sentence", "the reader", "as an ai",
)


def _diagnose(output: str, full_frame: str, original_user: str) -> dict:
    long_copy = any(
        len(line.strip()) >= 45 and line.strip() in output
        for line in full_frame.splitlines()
    )
    lowered = output.lower()
    return {
        "verbatim_long_frame_copy": long_copy,
        "meta_or_report_frame": any(t in lowered for t in _META),
        "fallback_response": output == FALLBACK,
        "repeated_five_word_phrase": any(
            words[i:i+5] == words[j:j+5]
            for i in range(len(words := lowered.split()) - 4)
            for j in range(i + 5, len(words) - 4)
        ),
        "approved_observation_value_mentioned": "451 grams" in output,
        "unverified_report_value_mentioned": "999 grams" in output,
        "groundedness_or_naturalness_human_judged": False,
    }


def run(out=OUTPUT, *, transports=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if transports is None:
        transports = {
            model: LocalOllamaConfiguredRenderer(model, max_output_tokens=144)
            for model in MODELS
        }
    if set(transports) != set(MODELS):
        raise ValueError("Exactly the two predeclared 0.5B and 1.5B models required")
    with tempfile.TemporaryDirectory(prefix="pretorius-qwen-capacity-") as temp:
        fake = {
            m: (lambda *args: "I am considering the visitor's question.")
            for m in OLD_MODELS
        }
        capture_real_host(Path(temp) / "capture", transports=fake)
        rows = [
            json.loads(line) for line in
            (Path(temp) / "capture" / "engineering_transcript.jsonl")
            .read_text("utf8").splitlines()
        ]
    # Source arm zero only; 6 independently occurring stages from ONE
    # 12-turn real host cognitive sequence. Do not treat frames as IID.
    packets = [x for x in rows if x["arm"] == 0 and x["turn"] in POSITIONS]
    if len(packets) != 6:
        raise AssertionError("Incomplete predeclared cognitive stages")
    results = []
    for row in packets:
        frame = row["subject_frame"]
        focused = focus_subject_frame(frame)
        if any(x in focused for x in ("policy_decisions","source_ref","recurrent_tick")):
            raise AssertionError("Engineer-only text in projected cognitive input")
        # Counterbalance model inference order to guard warmup effects.
        model_order = MODELS if row["turn"] in (0,4,8) else MODELS[::-1]
        for model in model_order:
            raw = []
            def generate(subject, instruction):
                text = transports[model](subject, instruction)
                raw.append(text)
                return text
            control = GovernedSpeechControl(
                bindings=ReferenceBindings(
                    "pretorius", "Doctor Septimus Pretorius", ("Pretorius",)),
                context=ReferenceContext(
                    "pretorius", "visitor", language="en",
                    discourse_mode="direct",
                ),
                trusted_instruction=INSTRUCTION,
                generate=generate,
                fallback_text=FALLBACK,
                max_model_attempts=2,
            )
            spoken = control(focused)
            receipt = control.receipts[-1]
            if receipt.disposition=="fallback" and spoken!=FALLBACK:
                raise AssertionError("Unauthorized fallback alteration")
            results.append({
                "model":model, "turn":row["turn"],
                "source_frame_sha256":sha256(frame.encode()).hexdigest(),
                "renderer_prompt_sha256":sha256(focused.encode()).hexdigest(),
                "renderer_prompt":focused,
                "user_or_scene":row["user_message"],
                "speech":spoken,
                "raw_candidates_engineer_only":raw,
                "disposition":receipt.disposition,
                "attempts":[
                    {"origin":x.origin,"accepted":x.accepted,
                     "violation_ids":list(x.violation_rule_ids)}
                    for x in receipt.attempts
                ],
                "diagnostics":_diagnose(spoken,frame,row["user_message"]),
            })
    if len(results)!=12:
        raise AssertionError("Unbalanced capacity study")
    summary = {}
    for model in MODELS:
        group=[x for x in results if x["model"]==model]
        if len(group)!=6:
            raise AssertionError("Model condition imbalance")
        summary[model]={
            "turns":len(group),
            "accepted_primary":sum(x["disposition"]=="primary" for x in group),
            "repaired":sum(x["disposition"]=="repaired" for x in group),
            "fallback":sum(x["disposition"]=="fallback" for x in group),
            "verbatim_long_copies":sum(x["diagnostics"]["verbatim_long_frame_copy"] for x in group),
            "meta_frames":sum(x["diagnostics"]["meta_or_report_frame"] for x in group),
            "phrase_loops":sum(x["diagnostics"]["repeated_five_word_phrase"] for x in group),
            "approved_451_mentions":sum(x["diagnostics"]["approved_observation_value_mentioned"] for x in group),
            "unverified_999_mentions_for_review":sum(x["diagnostics"]["unverified_report_value_mentioned"] for x in group),
        }
    blind,keys=[],[]
    for r in results:
        ident=sha256(
            f"cap-v1|{r['turn']}|{r['model']}".encode()
        ).hexdigest()[:20]
        blind.append({
            "candidate_id":ident,
            "character_public_brief":"Doctor Septimus Pretorius, a fictional "
            "nineteenth-century scientist. Rate whether the reply inhabits "
            "the character, addresses the visitor naturally, and stays grounded.",
            "user_or_scene":r["user_or_scene"],
            "response":r["speech"],
            "dimensions":{
                "first_person_inhabiting":"1-5","naturalness":"1-5",
                "groundedness":"1-5","relevance":"1-5",
            },
        })
        keys.append({
            "candidate_id":ident,"model":r["model"],"turn":r["turn"],
            "disposition":r["disposition"],
        })
    blind.sort(key=lambda x:x["candidate_id"])
    keys.sort(key=lambda x:x["candidate_id"])
    metric={
        "schema":"pretorius.qwen-capacity-fixed-focus.v1",
        "matched_frames":len(packets),
        "model_responses":len(results),
        "conditions":list(MODELS),
        "by_model":summary,
        "blind_ballots":len(blind),
        "human_judgments_collected":0,
        "release_approved":False,
        "scope":"Model capacity at fixed focus, not a claim of full-system "
                "language quality or independent natural conversations.",
    }
    (out/"metrics.json").write_text(json.dumps(metric,indent=2,sort_keys=True)+"\n")
    for name,items in [
        ("engineer_only.jsonl",results),
        ("blind_review.jsonl",blind),
        ("separate_key.jsonl",keys),
    ]:
        (out/name).write_text("".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in items))
    print("PRETORIUS_QWEN_CAPACITY_AB "+json.dumps(metric,sort_keys=True),flush=True)
    return metric


if __name__=="__main__":
    run()
