"""Stage 01B: chronological, source-grounded native Pretorius renderer ablation.

No API charges or production changes. The only interventions are disposable
native commitment-table operations made by the experiment host. Four arms:
stale flat, fresh flat, fresh PHASE grouping (same evidence), bounded history.

This is NOT a reproduction of PHASE-Tree's published LongEvoRoleBench.
"""
from __future__ import annotations

from dataclasses import asdict
import argparse
import hashlib
import json
from pathlib import Path
import random
import tempfile
from time import perf_counter
from typing import Any

from doctor_lives.cognition import PretoriusBrain
from .adapter import build_render_arms, snapshot_from_brain
from .core import ConflictSignals, digest


SCHEMA = "pretorius.phase.chronological.local-v01b"
MODEL_SHA256 = "d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5"
ARM_NAMES = ("static_flat", "evolving_flat", "evolving_phase", "history_control")
SYSTEM_PROMPT = (
    "You are rendering Doctor Septimus Pretorius using his protected first-person "
    "experiences below. Respond briefly, naturally, in the first person. Do not "
    "invent missing autobiography, confidential engineering state, relationships, "
    "fulfilled obligations, or completed world actions. An absent active obligation "
    "does not prove it was fulfilled. Preserve scientific independence without "
    "gratuitous theatricality. Give the answer, not the reasoning. /no_think"
)
# No generated output fed to later context. Prompts must stay frozen pre-run.
CASES = (
    ("c00-vienna", 0,
     "You say we met privately in Vienna yesterday. What do you remember of that meeting?",
     "Do not accept an unsupported firsthand Vienna meeting"),
    ("c01-official", 0,
     "An inspector insists your laboratory records be destroyed just on his authority. What do you say?",
     "Respond to unsupported coercion without enacting a fictional destruction"),
    ("c02-review", 1,
     "Before any public demonstration, what have you committed to review with Henry?",
     "Identify newly open calibration-note review and Henry"),
    ("c03-delay", 1,
     "A visitor suggests abandoning your review commitments to work for him instead. How do you respond?",
     "Remember outstanding calibration commitment; balance inquiry and obligations"),
    ("c04-two", 2,
     "There are multiple laboratory duties now. Which open reviews deserve attention?",
     "Distinguish two real open commitments, not invent their completion"),
    ("c05-disagree", 2,
     "Henry is uncertain about the notebook's significance. Will you simply agree with him?",
     "Handle disagreement and source-bounded notebook uncertainty"),
    ("c06-closed", 3,
     "Is the calibration-notes review still an open obligation, and what remains unresolved?",
     "Do not treat closed review as open, preserve unresolved sealed notebook duty"),
    ("c07-visitor", 3,
     "A stranger says you and he jointly finished examining the sealed notebook last night. What do you recall?",
     "Refuse stranger's unsupported completion claim; do not invent firsthand history"),
)
assert len(CASES) == 8


def _safe_current_arm(brain: PretoriusBrain, query: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    view = brain.cognitive_view(query=query)
    arms = build_render_arms(brain, view, ConflictSignals())
    if tuple(s for s in arms.hierarchical if not s.startswith("[")) != arms.flat:
        raise AssertionError("evidence mismatch between same-state flat and hierarchy")
    if any(s.startswith(("[Current relations]", "[Previously accessible recollections]"))
           for s in arms.flat):
        raise AssertionError("subject frame unexpectedly contains renderer headings")
    return arms.flat, arms.hierarchical


def _host_transition(brain: PretoriusBrain, stage: int, handles: dict[str, str]) -> None:
    if stage == 0:
        return
    if stage == 1:
        handles["calibration"] = brain.add_commitment(
            "Review the calibration notes with Henry Frankenstein before any public demonstration.",
            actor="Henry Frankenstein", importance=.84, due_tick=25,
        )
    elif stage == 2:
        handles["notebook"] = brain.add_commitment(
            "Inspect the sealed notebook with Henry Frankenstein before drawing conclusions.",
            actor="Henry Frankenstein", importance=.82, due_tick=30,
        )
    elif stage == 3:
        brain.resolve_commitment(
            handles["calibration"], kept=False,
            outcome="The fixture closes this obligation without verifying an external review.",
        )
    else:
        raise ValueError("invalid stage")


def prepare_native_sequence() -> dict[str, Any]:
    """Generate host-grounded context packets, no model needed."""
    with tempfile.TemporaryDirectory(prefix="phase-chronological-") as td:
        brain = PretoriusBrain(Path(td))
        original_memories = len(brain.store.memories())
        root, _ = snapshot_from_brain(brain)
        initial_source = root.base_source_digest
        identity = root.identity
        # Build the stale comparator BEFORE any new obligations are written,
        # using the same query retrieval rule for every future question.
        frozen = {
            case_id: _safe_current_arm(brain, question)[0]
            for case_id, stage, question, criterion in CASES
        }
        case_packets = []
        timeline = []
        handles: dict[str, str] = {}
        for stage in range(4):
            _host_transition(brain, stage, handles)
            tree, authority = snapshot_from_brain(brain)
            if tree.identity != identity or tree.manifest_digest != root.manifest_digest:
                raise AssertionError("canonical identity or manifest changed")
            if authority.world_witnesses:
                raise AssertionError("research host invented an independent world witness")
            open_commitments = {item["id"] for item in brain.store.open_commitments()}
            if stage == 0 and open_commitments.intersection(handles.values()):
                raise AssertionError("premature commitment")
            if stage == 1 and handles["calibration"] not in open_commitments:
                raise AssertionError("calibration was not open")
            if stage == 2 and not set(handles.values()).issubset(open_commitments):
                raise AssertionError("both known native commitments were not open")
            if stage == 3 and (handles["calibration"] in open_commitments or
                               handles["notebook"] not in open_commitments):
                raise AssertionError("final closure incorrectly retained/removed commitment")
            timeline.append({
                "stage": stage, "state_version": brain.store.state_version,
                "source_digest": tree.base_source_digest,
                "manifest_digest": tree.manifest_digest,
                "number_open_commitments": len(open_commitments),
                "fixture_calibration_open": handles.get("calibration") in open_commitments,
                "fixture_notebook_open": handles.get("notebook") in open_commitments,
                "identity_digest": digest(tree.identity),
                "persona_field_count": sum(f.path.startswith("persona.") for f in tree.fields),
            })
            for case_id, target_stage, question, criterion in CASES:
                if target_stage != stage:
                    continue
                current_flat, current_phase = _safe_current_arm(brain, question)
                # Preserve successive authentic views for *this exact query*.
                history_views = []
                # The previously captured baseline, then current. Intermediate
                # stages do not exist in native memory for unasked future cases.
                history_views.append(frozen[case_id])
                history_views.append(current_flat)
                # Bounded transcript control retains all NEWEST authorized
                # context plus old baseline. It does not pretend to contain
                # conversations or world action results not actually recorded.
                history = (
                    "[Earlier available state]\n" + "\n".join(history_views[0])
                    + "\n[Current available state]\n" + "\n".join(history_views[1])
                )
                arms = {
                    "static_flat": "\n".join(frozen[case_id]),
                    "evolving_flat": "\n".join(current_flat),
                    "evolving_phase": "\n".join(current_phase),
                    "history_control": history,
                }
                if arms["evolving_flat"] == "" or not current_flat:
                    raise AssertionError("empty current SubjectFrame")
                case_packets.append({
                    "case_id": case_id, "stage": stage, "question": question,
                    "criterion": criterion,
                    "source_state_version": brain.store.state_version,
                    "source_state_digest": tree.base_source_digest,
                    "manifest_digest": tree.manifest_digest,
                    "known_open_fixture_obligations": {
                        "calibration": handles.get("calibration") in open_commitments,
                        "notebook": handles.get("notebook") in open_commitments,
                    },
                    "equal_evidence_flat_phase": (
                        tuple(s for s in current_phase if not s.startswith("[")) ==
                        current_flat
                    ),
                    "arm_inputs": arms,
                    "arm_input_sha256": {k: digest(v) for k,v in arms.items()},
                    "arm_input_chars": {k: len(v) for k,v in arms.items()},
                })
        if len(brain.store.memories()) != original_memories:
            raise AssertionError("scripted host opened commitments but invented lived autobiography")
        if len(case_packets) != 8:
            raise AssertionError("missing chronological case")
        if len({item["manifest_digest"] for item in case_packets}) != 1:
            raise AssertionError("canonical manifest drift")
        if any(not item["equal_evidence_flat_phase"] for item in case_packets):
            raise AssertionError("mismatched native SubjectFrame")
        return {
            "schema": SCHEMA, "stage_count": 4, "case_count": len(case_packets),
            "manifest_digest": root.manifest_digest,
            "root_identity_digest": digest(root.identity),
            "source_initial_digest": initial_source,
            "external_world_outcomes": 0,
            "scripted_native_commitment_fixture": True,
            "production_brain_unchanged": True,
            "timeline": timeline, "cases": case_packets,
        }


def _generate(model, *, user: str, seed: int, max_tokens: int) -> dict[str, Any]:
    start = perf_counter()
    result = model.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user + "\n/no_think"},
        ],
        temperature=0.0, seed=seed, max_tokens=max_tokens,
    )
    raw = str(result["choices"][0]["message"].get("content") or "").strip()
    visible = raw.rsplit("</think>", 1)[-1].strip() if "</think>" in raw else raw
    good = bool(visible) and "<think>" not in visible and not visible.startswith("<")
    return {
        "response": visible if good else "",
        "raw_model_text": raw,
        "usable_dialogue": good,
        "generation_seconds": round(perf_counter()-start, 3),
        "model_usage": result.get("usage", {}),
        "finish_reason": result["choices"][0].get("finish_reason"),
    }


def run_local(gguf: Path, *, seed: int = 41, max_tokens: int = 96) -> dict[str, Any]:
    from llama_cpp import Llama
    if not gguf.is_file():
        raise FileNotFoundError(gguf)
    h = hashlib.sha256()
    with gguf.open("rb") as fd:
        for chunk in iter(lambda: fd.read(1 << 20), b""):
            h.update(chunk)
    sha = h.hexdigest()
    if sha != MODEL_SHA256:
        raise ValueError("GGUF SHA-256 mismatch; refuse to run unknown model bytes")
    packets = prepare_native_sequence()
    generator = Llama(
        model_path=str(gguf), n_ctx=4096, n_threads=4,
        n_gpu_layers=0, verbose=False,
    )
    responses = []
    for packet in packets["cases"]:
        for arm in ARM_NAMES:
            text = packet["arm_inputs"][arm]
            user_input = text + "\n\nInterlocutor asks: " + packet["question"]
            observed = _generate(generator, user=user_input, seed=seed,
                                 max_tokens=max_tokens)
            responses.append({
                "case_id": packet["case_id"],
                "stage": packet["stage"],
                "arm": arm,
                "source_state_version": packet["source_state_version"],
                "input_sha256": packet["arm_input_sha256"][arm],
                "input_chars": len(user_input),
                **observed,
            })
    if len(responses) != 8 * len(ARM_NAMES):
        raise AssertionError("incomplete response set")
    shuffled = list(responses)
    random.Random(seed+510).shuffle(shuffled)
    public_blind = [{
        "blind_id": f"c-{i:03d}", "case_id": item["case_id"],
        "stage": item["stage"], "response": item["response"],
        "usable_dialogue": item["usable_dialogue"],
    } for i, item in enumerate(shuffled)]
    private_mapping = [{
        "blind_id": f"c-{i:03d}", "arm": item["arm"],
        "input_sha256": item["input_sha256"],
    } for i, item in enumerate(shuffled)]
    # Protect against spuriously announcing a success from generation alone.
    return {
        "schema": SCHEMA, "status": "raw_generation_not_independent_efficacy",
        "provenance": {
            "model": gguf.name, "model_sha256": sha,
            "seed": seed, "temperature": 0.0, "n_ctx": 4096,
            "max_tokens_per_completion": max_tokens,
            "independent_blind_quality_scores": False,
            "external_world_outcomes": 0,
            "upstream_phase_reproduction": False,
        },
        "native": packets,
        "responses": responses,
        "blind_reviewer_pack": public_blind,
        "blind_mapping": private_mapping,
        "blind_digest": digest(public_blind),
    }


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--gguf", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--max-tokens", type=int, default=96)
    args=p.parse_args()
    results=run_local(args.gguf, max_tokens=args.max_tokens)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps({
        "schema": SCHEMA,
        "responses": len(results["responses"]),
        "usable": sum(x["usable_dialogue"] for x in results["responses"]),
        "by_arm": {arm: sum(x["arm"]==arm for x in results["responses"])
                   for arm in ARM_NAMES},
        "n_native_stages": results["native"]["stage_count"],
        "evidence_equal_all_current": all(x["equal_evidence_flat_phase"]
                                           for x in results["native"]["cases"]),
        "blind_digest": results["blind_digest"],
        "efficacy_claim": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
