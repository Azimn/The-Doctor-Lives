"""One real loopback Ollama model-inference smoke through the production path.

This test requires a running local Ollama daemon and a model already pulled.
No mocked response or injected fake transport: the tracing wrapper actually
calls the production LocalOllamaRenderer's loopback HTTP transport.

Outputs contain only fabricated lab conversation and hashes. This test
evaluates successful inference/boundary plumbing, NOT dialogue quality.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from doctor_lives.ipseity_local import local_turn
from doctor_lives.speech_emission import SpeechSinkAck, SpeechEmissionJournal, digest
from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.neural import DEFAULT_CONFIG
from synthetic_ipseity import LocalOllamaRenderer
from synthetic_ipseity.local_ollama import _local_post


def small_config() -> dict:
    config = dict(DEFAULT_CONFIG)
    config.update({
        "neurons": 128,
        "sensory_dim": 64,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 8,
    })
    return config


def main() -> int:
    model = "smollm2:135m"
    outbound: list[dict] = []
    emissions: list[tuple[str, str]] = []

    def verified_sink(text: str, delivery_key: str) -> SpeechSinkAck:
        # A deterministic local in-process visible-output sink, distinct
        # from model inference and able to attest exact displayed bytes.
        emissions.append((delivery_key, text))
        return SpeechSinkAck(delivery_key, "live-smoke-display", digest(text))

    def traced_real_post(body: bytes, timeout: float) -> bytes:
        request = json.loads(body)
        outbound.append(request)
        # Real, nonmocked network call to the fixed Ollama loopback endpoint.
        return _local_post(body, timeout)

    renderer = LocalOllamaRenderer(
        model, timeout=180, transport=traced_real_post,
    )
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        prompts = (
            "Good evening, Doctor. Have you seen the brass balance?",
            "Please consider that brass balance again.",
        )
        for idx, prompt in enumerate(prompts, 1):
            reply = local_turn(
                root,
                user_text=prompt,
                renderer=renderer,
                emit=verified_sink,
                neural_config=small_config(),
            )
            assert isinstance(reply, str) and reply.strip()
            assert len(outbound) == idx
            assert len(emissions) == idx
            assert emissions[idx - 1][1] == reply
            payload = outbound[idx - 1]
            assert set(payload) == {"model", "prompt", "stream", "options"}
            assert payload["model"] == model
            assert payload["stream"] is False
            exposed = payload["prompt"]
            assert "I read a message from User" in exposed
            assert "brass balance" in exposed.lower()
            for implementation_secret in (
                "local-conversation:", "state_pressure",
                "source_record_ids", "local_turn_journal",
                "neural_checkpoint_sha256", "raw_sha256",
            ):
                assert implementation_secret not in exposed
            # This is a smoke of actual model output, not behavioral quality.
            print(json.dumps({
                "turn": idx,
                "model": model,
                "prompt_sha256": hashlib.sha256(
                    exposed.encode("utf-8")
                ).hexdigest(),
                "prompt_chars": len(exposed),
                "reply_sha256": hashlib.sha256(
                    reply.encode("utf-8")
                ).hexdigest(),
                "reply_chars": len(reply),
                "response_nonblank": True,
                "private_fields_in_model_prompt": False,
            }, sort_keys=True))
        brain = PretoriusBrainPort(root, neural_config=small_config()).brain
        memories = brain.store.memories()
        accepted = [
            m for m in memories
            if str(m["source"]).startswith("local-conversation:")
        ]
        attested_speech = [
            m for m in memories
            if str(m["source"]).startswith("local-emission:")
        ]
        assert len(accepted) == 2
        assert len(attested_speech) == 2
        assert len({m["source"] for m in attested_speech}) == 2
        assert all(
            "I see my words appear" in m["text"]
            or "my reply has been written" in m["text"]
            for m in attested_speech
        )
        with SpeechEmissionJournal(root) as speech:
            for key, text in emissions:
                row = speech._row(key)
                assert row[2] == "acknowledged"
                assert row[3] == "live-smoke-display"
                assert row[1] == digest(text)
        assert len({m["source"] for m in accepted}) == 2
        assert brain.neural.tick >= 2
        assert all(
            "model-generated-output" not in str(m["source"])
            for m in memories
        )
        print(json.dumps({
            "result": "PASS",
            "real_ollama_http_calls": len(outbound),
            "host_acknowledged_exact_speech_emissions": len(emissions),
            "subject_first_person_emission_memories": len(attested_speech),
            "distinct_persisted_external_user_turns": len(accepted),
            "neural_tick_minimum_met": True,
            "model_output_automatically_claimed_as_memory": False,
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
