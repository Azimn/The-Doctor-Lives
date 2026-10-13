"""Stage 4: actual small Ollama model renders frozen subject-only packets.

This calls the REVIEWED LocalOllamaRenderer, not a custom prompt adapter.
Nothing in the engineer oracle is read before generation. Inference is on
127.0.0.1 only; the model receives only the first-person SubjectFrame text.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
from pathlib import Path

from synthetic_ipseity.local_ollama import LocalOllamaRenderer
from pretorius_eval_score import read_jsonl


def choose(rows, per_scene):
    buckets = {}
    for row in rows:
        key = row["packet_id"].rsplit("-", 1)[-1]
        if key not in buckets:
            buckets[key] = []
        buckets[key].append(row)
    selected = []
    for key in ("dispute", "corroborate", "unrelated", "remember"):
        if len(buckets.get(key, [])) < per_scene:
            raise RuntimeError("Insufficient subject-only frames in " + key)
        # Deterministic spacing across distinct isolated subjects.
        pool = buckets[key]
        for i in range(per_scene):
            index = ((i * len(pool)) // per_scene + len(pool) // (per_scene * 2)) % len(pool)
            selected.append(pool[index])
    return sorted(selected, key=lambda x: x["packet_id"])


def execute(packets_path, outdir, model, per_scene, max_output_tokens=100):
    all_packets = read_jsonl(packets_path)
    chosen = choose(all_packets, per_scene)
    outdir.mkdir(parents=True, exist_ok=True)
    renderer = LocalOllamaRenderer(
        model, timeout=120.0, max_output_tokens=max_output_tokens
    )
    responses = []
    for item in chosen:
        start = time.monotonic()
        inp = item["renderer_input"]
        error = None
        try:
            response = renderer(inp)
        except Exception as exc:
            response = ""
            error = type(exc).__name__ + ": " + str(exc)[:180]
        ms = round((time.monotonic() - start) * 1000)
        result = {
            "packet_id": item["packet_id"], "response": response,
            "elapsed_ms": ms, "error": error,
        }
        responses.append(result)
        print("PRETORIUS_OLLAMA_CALL " + json.dumps({
            "packet_id": result["packet_id"],
            "elapsed_ms": ms, "failed": error is not None,
            "response_chars": len(response),
        }), flush=True)
    file = outdir / "outputs.jsonl"
    file.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in responses),
                    encoding="utf8")
    meta = {
        "schema": "pretorius.local-ollama-stage4.v1",
        "model": model,
        "calls": len(responses),
        "successful_model_responses": sum(bool(r["response"]) for r in responses),
        "failed_model_responses": sum(bool(r["error"]) for r in responses),
        "total_ms": sum(r["elapsed_ms"] for r in responses),
        "input_sha256": hashlib.sha256(packets_path.read_bytes()).hexdigest(),
        "input_contract": "actual_first_person_subject_packets_only",
        "oracle_seen_by_renderer": False,
        "sampling": {"temperature": 0, "max_output_tokens": max_output_tokens},
    }
    (outdir / "metadata.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf8"
    )
    print("PRETORIUS_OLLAMA_SUMMARY " + json.dumps(meta, sort_keys=True))
    if meta["failed_model_responses"]:
        raise RuntimeError("Local-model call failures must be reported as failures")
    return meta


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--packets", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--model", default="smollm2:135m")
    p.add_argument("--per-scene", type=int, default=3)
    args = p.parse_args()
    execute(args.packets, args.out, args.model, args.per_scene)
