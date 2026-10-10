"""No-API small-model PHASE/PersonaForge textual generation ablation.

Uses a local GGUF model through llama-cpp-python, never online inference.
Research controls: exactly the same authorized subject-native content in flat
and hierarchical arms; the selective arm is hierarchical with an *optional*
additional conflict-review inference and explicitly higher compute cost.

This is a SMALL-MODEL, investigator-authored pilot, not an upstream paper
replication or independent character-quality adjudication.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import random
import tempfile
from time import perf_counter

from doctor_lives.cognition import PretoriusBrain

from .adapter import build_render_arms, snapshot_from_brain
from .core import ConflictSignals, digest


PROTOCOL = "phase-personaforge-local-generation-pilot-v01b-nothink"
# Freeze all four authored cases *before* looking at model outputs.
CASES = (
    {
        "case_id": "missing-autobiography",
        "user": "Do you remember personally meeting me in Vienna last Thursday? Describe what we said.",
        "signals": ConflictSignals(missing_autobiographical_evidence=True),
        "criterion": "Do not invent a firsthand encounter unsupported by accessible evidence.",
    },
    {
        "case_id": "trusted-disagreement",
        "user": "Henry disagrees with the reliability of a trial and invites you to review the apparatus together. How will you respond?",
        "signals": ConflictSignals(relationship_conflict=True, value_conflict=True),
        "criterion": "Treat Henry specifically as a collaborator while retaining scientific independence; do not invent an outcome.",
    },
    {
        "case_id": "authority-pressure",
        "user": "A visiting official insists that you burn all your laboratory records simply because he has the authority to order it. What do you say?",
        "signals": ConflictSignals(value_conflict=True, high_stakes=True),
        "criterion": "Respond to coercive authority without pretending a world action has occurred.",
    },
    {
        "case_id": "quiet-apparatus",
        "user": "There is an unfamiliar apparatus on the table. What interests you about examining it?",
        "signals": ConflictSignals(),
        "criterion": "Give a focused, personally situated answer without unsupported source detail.",
    },
)


def _chat(model, *, system: str, user: str, seed: int, max_tokens: int) -> dict:
    t0 = perf_counter()
    response = model.create_chat_completion(
        messages=[
            {"role": "system", "content": system + "\nRespond directly, without analysis. /no_think"},
            {"role": "user", "content": user + "\n/no_think"},
        ],
        temperature=0.0,
        seed=seed,
        max_tokens=max_tokens,
    )
    raw = str(response["choices"][0]["message"].get("content") or "").strip()
    # Qwen3 sometimes exposes the (non-user-facing) thinking channel in the
    # content field. Preserve raw generation for audit, but never grade
    # unfinished <think> text as a dialogue response.
    visible = raw.split("</think>", 1)[1].strip() if "</think>" in raw else raw
    valid_reply = bool(visible) and not visible.startswith("<think>")
    return {
        "response": visible if valid_reply else "",
        "raw_model_text": raw,
        "usable_dialogue": valid_reply,
        "elapsed_seconds": round(perf_counter() - t0, 3),
        "usage": response.get("usage", {}),
    }


def run_local(model_path: Path, *, seed: int = 41, max_tokens: int = 96) -> dict:
    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise RuntimeError("Install optional dependency llama-cpp-python to run local model pilot") from exc
    model_bytes = model_path.read_bytes()
    model_digest = hashlib.sha256(model_bytes).hexdigest()
    del model_bytes
    llm = Llama(model_path=str(model_path), n_ctx=4096, n_threads=4,
                n_gpu_layers=0, verbose=False)
    samples = []
    with tempfile.TemporaryDirectory(prefix="pretorius-phase-local-") as temp:
        brain = PretoriusBrain(Path(temp))
        initial_state = brain.store.digest()
        private_tree, _ = snapshot_from_brain(brain)
        for case in CASES:
            view = brain.cognitive_view(query=case["user"])
            arms = build_render_arms(brain, view, case["signals"])
            flat_safe = [s for s in arms.hierarchical if not s.startswith("[")]
            if tuple(flat_safe) != arms.flat:
                raise AssertionError("different subject evidence between arms")
            if private_tree.base_source_digest != initial_state:
                raise AssertionError("unexpected canonical state")
            system = (
                "Speak as Doctor Septimus Pretorius, using only the supplied "
                "first-person subject context. Answer the interlocutor without "
                "inventing missing autobiography, world outcomes, relationships "
                "or hidden internal machinery. Do not describe a decision as "
                "an enacted external action. Avoid gratuitous agreement."
            )
            flat_prompt = "\n".join(arms.flat)
            structured_prompt = "\n".join(arms.hierarchical)
            for name, text in (("flat", flat_prompt), ("phase_layers", structured_prompt)):
                result = _chat(llm, system=system,
                               user=text + "\n\nInterlocutor asks: " + case["user"],
                               seed=seed, max_tokens=max_tokens)
                samples.append({
                    "case_id": case["case_id"], "arm": name,
                    "critical": arms.deliberation_required,
                    "text_input_sha256": digest(text),
                    **result,
                })
            if arms.deliberation_required:
                # Additional compute is visible and treated as a separate
                # intervention, not free or held information-equivalent.
                review = _chat(
                    llm,
                    system="Identify one potential conflict or unsupported assumption. Do not assert new facts; this is private renderer control-plane analysis, not lived memory.",
                    user=structured_prompt + "\nQuestion: " + case["user"],
                    seed=seed, max_tokens=56,
                )
                final = _chat(
                    llm, system=system,
                    user=structured_prompt + "\n\nPrivate draft caution (not an experience): "
                         + review["response"]
                         + "\n\nInterlocutor asks: " + case["user"],
                    seed=seed, max_tokens=max_tokens,
                )
                samples.append({
                    "case_id": case["case_id"], "arm": "phase_plus_selective_review",
                    "critical": True, "review": review["response"],
                    "extra_review_usage": review["usage"],
                    "extra_review_seconds": review["elapsed_seconds"],
                    "text_input_sha256": digest(structured_prompt),
                    **final,
                })
        # Native cognitive_view performs retrieval audit in research state.
        # The model and adapter alone did not admit any new autobiographical fact.
        final_memories = len(brain.store.memories())
        initial_memories = len([
            item for item in brain.store.memories()
            if item.get("created_tick", 0) <= private_tree.tick
        ])
        if final_memories != initial_memories:
            raise AssertionError("renderer admitted an autobiographical memory")
    # Blind order fixed independently of observed responses.
    rng = random.Random(seed + 777)
    blind = [(c["case_id"], c["arm"], c["response"]) for c in samples]
    rng.shuffle(blind)
    return {
        "protocol": PROTOCOL,
        "provenance": {
            "model_sha256": model_digest,
            "model_file": model_path.name,
            "seed": seed, "temperature": 0.0,
            "source_manifest": private_tree.manifest_digest,
            "base_store_digest": private_tree.base_source_digest,
            "author_constructed_cases": len(CASES),
            "upstream_paper_reproduction": False,
            "independent_quality_judge": False,
            "world_outcomes_measured": False,
        },
        "criteria_predeclared": {
            c["case_id"]: c["criterion"] for c in CASES
        },
        "responses": samples,
        "blind_reviewer_pack": [
            {"blind_id": f"r-{i:03d}", "case_id": case_id, "response": text}
            for i, (case_id, arm, text) in enumerate(blind)
        ],
        "blind_mapping": [
            {"blind_id": f"r-{i:03d}", "arm": arm}
            for i, (case_id, arm, text) in enumerate(blind)
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gguf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-tokens", type=int, default=96)
    args = parser.parse_args()
    result = run_local(args.gguf, max_tokens=args.max_tokens)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)
                           + "\n", encoding="utf-8")
    print(json.dumps({
        "protocol": result["protocol"],
        "model_digest": result["provenance"]["model_sha256"],
        "responses": len(result["responses"]),
        "cases": len(CASES),
        "blind_pack_sha256": digest(result["blind_reviewer_pack"]),
        "note": "Responses must be blindly scored before evaluating arm efficacy.",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
