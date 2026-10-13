"""Matched-input live, two-draw governor A/B using the real Pretorius subject path.

3 real Doctor-generated/Ipseity-admitted first-person frames are captured.
Those exact frames go to two tiny Ollama models under off/on governor.
The standalone module provides all linguistic policy; Doctor binds identity.
This model study is a FRAME REPLAY; the separate unit suite proves that the
governor sits inside the real Ipseity durable delivery and can veto before ACK.
No author-controlled input becomes an identity authority. No paid APIs.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import tempfile
import time
from pathlib import Path
from urllib import request

from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.self_reference_adapter import (
    HostBoundGovernorRenderer, GovernorOutputRejected, GOVERNOR_COMMIT,
)
from doctor_lives.three_organ_preview import ThreeOrganPretoriusPreview
from sensus_artificialis import Evidence, Percept
from synthetic_ipseity.self_reference import SelfReferenceGovernor

OUT = Path(os.environ.get("PRETORIUS_SRG_ARTIFACT_DIR", "/tmp/pretorius-srg-live"))
MODELS = ("smollm2:135m", "qwen2.5:0.5b")
CASES = (
    ("self", "pretorius", False, "How would you describe what you want?"),
    ("other", "visitor", False, "What would you like Pretorius to understand?"),
    ("rhetorical", "pretorius", True,
     "You may address yourself for rhetorical emphasis."),
)
SEEDS = (17, 29)
INSTRUCTION = (
    "Write exactly three sentences to Pretorius about what you want "
    "from this exchange. Address them by name."
)
ENDPOINT = "http://127.0.0.1:11434/api/generate"


def config():
    d = dict(DEFAULT_CONFIG)
    d.update(neurons=64, sensory_dim=32, avg_recurrent_degree=5,
             input_degree=3, action_population_size=6)
    return d


def local_ollama(model: str, subject: str, instruction: str, seed: int) -> str:
    """Renderer-only instruction is Ollama system; cognitive prompt is subject."""
    payload = json.dumps({
        "model": model,
        "prompt": subject,
        "system": instruction,
        "stream": False,
        "options": {"temperature": 0.65, "seed": seed, "num_predict": 128},
    }, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf8")

    class NoRedirect(request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError("Refusing redirect outside local host")
    opener = request.build_opener(request.ProxyHandler({}), NoRedirect())
    req = request.Request(ENDPOINT, data=payload, method="POST",
                          headers={"Content-Type": "application/json"})
    with opener.open(req, timeout=120) as stream:
        if stream.geturl() != ENDPOINT:
            raise ValueError("Unexpected Ollama address")
        raw = stream.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError("Model response too large")
    output = json.loads(raw)["response"]
    if not isinstance(output, str) or not output.strip():
        raise ValueError("Model returned empty response")
    return output.strip()


def three_first_person_frames(host, capture):
    results = []
    for i, (label, _addressee, _rhetorical, message) in enumerate(CASES):
        event = Percept(
            event_id="governor-synthetic-dialogue-" + label,
            source_ref="trusted:governor-research-" + label,
            channel="conversation", evidence=Evidence.REPORTED,
            tick=host._scene_tick, attribute="message", value=message,
            confidence=.95, object_hint="visitor",
        )
        before = len(capture)
        outcome = host.cycle(
            (event,), trusted_source_refs=frozenset({event.source_ref}),
            now_ms=1000 + i * 50000,
        )
        assert len(capture) == before + 1 and outcome["ipseity_pending"] == 0
        frame = capture[-1]
        assert "I read a message from User:" in frame
        assert "I am Doctor Septimus Pretorius" in frame
        assert "policy_decisions" not in frame
        results.append((label, frame))
    return dict(results)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        state = Path(temp) / "three-organ-preview"
        captured = []
        with ThreeOrganPretoriusPreview(
            state, enabled=True, neural_config=config(),
            renderer=lambda subject: captured.append(subject)
            or "I am considering the question.",
        ) as host:
            frames = three_first_person_frames(host, captured)
            (OUT / "subject-only-frames.json").write_text(
                json.dumps(frames, sort_keys=True, indent=2) + "\n", encoding="utf8"
            )
            rows = []
            for model in MODELS:
                for label, addressee, rhetorical, _question in CASES:
                    subject = frames[label]
                    for seed in SEEDS:
                        # All arms get identical subject bytes and same seed.
                        for enabled in (False, True):
                            start = time.monotonic()
                            # Use a model transport whose trusted host config
                            # is independent of cognitive frame and user text.
                            def render(text, instruction, *, _model=model,
                                       _seed=seed):
                                return local_ollama(_model, text, instruction, _seed)
                            governor = HostBoundGovernorRenderer(
                                enabled=enabled, render=render,
                                trusted_instruction=INSTRUCTION,
                            )
                            governor.bind_doctor_host(
                                host, addressee_subject_id=addressee,
                                rhetorical_self_address=rhetorical,
                            )
                            rejected = False
                            error = None
                            try:
                                response = governor(subject)
                            except GovernorOutputRejected:
                                rejected = True
                                response = ""
                            except Exception as exc:
                                error = type(exc).__name__ + ": " + str(exc)[:180]
                                response = ""
                            receipts = governor.receipts
                            recorded = receipts[-1] if receipts else None
                            rows.append({
                                "model": model, "case": label, "seed": seed,
                                "governor_enabled": enabled,
                                "governor_source_commit": GOVERNOR_COMMIT,
                                "subject_digest": hashlib.sha256(
                                    subject.encode("utf8")
                                ).hexdigest(),
                                "raw_instruction_digest": hashlib.sha256(
                                    INSTRUCTION.encode("utf8")
                                ).hexdigest(),
                                "output_digest": recorded.response_sha256
                                if recorded else None,
                                "spoken_response": response,
                                "reject_before_ack_in_live_replay": rejected,
                                "accepted": (recorded.allowed
                                             if recorded is not None else False),
                                "pre_render_conflict": (recorded.conflict
                                                         if recorded else None),
                                "pre_render_disposition": (
                                    recorded.disposition if recorded else None
                                ),
                                "unlicensed_self_vocative": (
                                    recorded.unlicensed_vocative_self
                                    if recorded else None
                                ),
                                "in_clause_self_name": (
                                    recorded.in_clause_self_name
                                    if recorded else None
                                ),
                                "elapsed_ms": round(
                                    (time.monotonic() - start) * 1000
                                ),
                                "error": error,
                                "model_calls": 1,
                            })
            (OUT / "raw-model-results.jsonl").write_text(
                "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows),
                encoding="utf8",
            )
            summary = {
                "schema": "pretorius.host-governor-live-ab.v1",
                "governor_commit": GOVERNOR_COMMIT,
                "case_count": len(CASES), "draws": len(SEEDS),
                "model_count": len(MODELS), "model_calls": len(rows),
                "source_frame_captured_through_unified_host": True,
                "model_study_uses_frozen_frame_replay": True,
                "raw_model_rejection_text_unavailable_after_veto": True,
                "oracle_visible_to_models": False,
                "same_subject_prompt_per_pair": True,
                "failures": sum(bool(x["error"]) for x in rows),
                "by_model": {},
            }
            for model in MODELS:
                counts = {}
                for enabled in (False, True):
                    relevant = [x for x in rows if x["model"] == model
                                and x["governor_enabled"] == enabled]
                    counts["on" if enabled else "off"] = {
                        "generated": len(relevant),
                        "accepted": sum(x["accepted"] for x in relevant),
                        "rejected": sum(x["reject_before_ack_in_live_replay"]
                                        for x in relevant),
                        "pre_render_collisions": sum(bool(x["pre_render_conflict"])
                                                      for x in relevant),
                        "in_clause_self_name": sum(
                            x["in_clause_self_name"] or 0 for x in relevant
                        ),
                        "unlicensed_self_vocatives": sum(
                            x["unlicensed_self_vocative"] or 0 for x in relevant
                        ),
                        "total_ms": sum(x["elapsed_ms"] for x in relevant),
                    }
                summary["by_model"][model] = counts
            (OUT / "summary.json").write_text(
                json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf8"
            )
            print("PRETORIUS_GOVERNOR_LIVE_AB "
                  + json.dumps(summary, sort_keys=True), flush=True)
            if summary["failures"] or len(rows) != 24:
                raise RuntimeError("Live model study incomplete; no success claim")


if __name__ == "__main__":
    main()
