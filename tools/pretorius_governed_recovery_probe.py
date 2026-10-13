"""Actual CPU Ollama controlled speech: primary / one repair / host fallback.

Uses frozen SubjectFrames CAPTURED from real Doctor/Sensus/Ipseity first; all
model inference then occurs as matched frame replay. It does not rerun cognition
or claim that stylistic quality is solved. The trusted host binds all identities.
Raw unsuccessful model outputs remain engineering-only artifacts.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from doctor_lives.self_reference_adapter import (
    HostBoundGovernorRenderer, GOVERNOR_COMMIT,
)
from doctor_lives.three_organ_preview import ThreeOrganPretoriusPreview
from synthetic_ipseity.local_ollama import LocalOllamaConfiguredRenderer
from pretorius_self_reference_live import (
    CASES, INSTRUCTION, config, three_first_person_frames,
)

MODELS = ("smollm2:135m", "qwen2.5:0.5b")
FALLBACK = "I must consider my words more carefully."
OUT = Path(os.environ.get("PRETORIUS_SRG_ARTIFACT_DIR", "/tmp/pretorius-srg-live"))


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as root:
        frames_received = []
        with ThreeOrganPretoriusPreview(
            Path(root) / "three-organ-preview",
            enabled=True, neural_config=config(),
            renderer=lambda frame: frames_received.append(frame)
            or "I am still considering the question.",
        ) as host:
            frozen = three_first_person_frames(host, frames_received)
            cases = []
            for model in MODELS:
                local = LocalGovernedOllamaRenderer(model, max_tokens=120)
                for label, addressee, rhetorical, _question in CASES:
                    candidates = []

                    def propose(subject, instruction):
                        text = local(subject, instruction)
                        candidates.append(text)
                        return text

                    adapter = HostBoundGovernorRenderer(
                        enabled=True,
                        recovery_enabled=True,
                        max_model_attempts=2,
                        trusted_instruction=INSTRUCTION,
                        fallback_text=FALLBACK,
                        render=propose,
                    )
                    adapter.bind_doctor_host(
                        host,
                        addressee_subject_id=addressee,
                        rhetorical_self_address=rhetorical,
                    )
                    delivered = adapter(frozen[label])
                    receipt = adapter.control_receipts[-1]
                    if not delivered.strip():
                        raise AssertionError("Empty model or fallback delivery")
                    if receipt.disposition == "fallback":
                        if delivered != FALLBACK:
                            raise AssertionError("Fallback must be verbatim host text")
                    else:
                        if delivered not in candidates:
                            raise AssertionError("Unknown generated output accepted")
                    if any(token in delivered for token in
                           ("policy_decisions", "source_ref", "recurrent_tick")):
                        raise AssertionError("Internal data in utterance")
                    cases.append({
                        "model": model,
                        "case": label,
                        "subject_sha256": receipt.subject_digest,
                        "governor_commit": GOVERNOR_COMMIT,
                        "disposition": receipt.disposition,
                        "model_call_count": len(candidates),
                        "raw_model_outputs_engineer_only": candidates,
                        "delivered": delivered,
                        "attempts": [
                            {"origin": x.origin, "accepted": x.accepted,
                             "violations": x.violation_rule_ids,
                             "output_sha256": x.output_digest}
                            for x in receipt.attempts
                        ],
                    })
            (OUT / "bounded-recovery-results.json").write_text(
                json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
                encoding="utf8",
            )
            summary = {
                "schema": "pretorius.governed-recovery-live.v1",
                "frozen_host_frames": len(CASES),
                "actual_local_models": len(MODELS),
                "responses": len(cases),
                "primary": sum(x["disposition"] == "primary" for x in cases),
                "repaired": sum(x["disposition"] == "repaired" for x in cases),
                "fallback": sum(x["disposition"] == "fallback" for x in cases),
                "model_calls": sum(x["model_call_count"] for x in cases),
                "max_model_attempts": 2,
                "semantic_or_blinded_naturalness_verified": False,
                "first_person_subject_only_ingress": True,
                "host_supplied_fallback_only": True,
                "failures_to_deliver": 0,
            }
            (OUT / "bounded-recovery-summary.json").write_text(
                json.dumps(summary, indent=2, sort_keys=True) + "\n",
                encoding="utf8",
            )
            print("PRETORIUS_GOVERNED_RECOVERY_LIVE "
                  + json.dumps(summary, sort_keys=True), flush=True)
            if len(cases) != len(CASES) * len(MODELS):
                raise AssertionError("Incomplete host-governor-model test")


if __name__ == "__main__":
    run()
