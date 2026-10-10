"""Issue #53 GROUND-001: model-selected, fully specified host operations.

Research chassis actuator, not an alternative Pretorius state authority. A real
local GGUF language model decodes a concrete proposal from the accepted subject
frame, goal and current qualitative host facts. There is NO hardcoded goal
ranking, oracle action, preselected operand, or fallback execution on parse
failure. The independent laboratory always executes or rejects the proposal.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from doctor_lives.cognition import PretoriusBrain
from doctor_lives.models import SubjectFrame
from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.book_library import BookLibrary
from pretorius_lab.observation_receipts import ObservationPort
from pretorius_lab.physics import Conflict, LabError
from .living_lab import (
    _admit_action, _admit_observation, _has_floor_percept,
    _offer_room, _verify_observation, _project, GOAL,
)

SCHEMA = "pretorius.living-lab.concrete-model-action.v1"
MODEL_SHA = {
    "qwen3-1.7b-q4_k_m":
        "d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5",
}
SYSTEM = (
    "You are the concrete-action decoder for Doctor Septimus Pretorius. "
    "His persistent cognition and firsthand subject frame are authoritative. "
    "Choose one genuinely useful immediate operation based ONLY on the "
    "presented first-person facts, the current objective and the offered "
    "legal operations. You are not permitted to invent observations, physical "
    "locations, page content, permissions or past memories. A world host "
    "will independently authorize and execute or deny your proposal. "
    "Respond with exactly one JSON object copied from the choices; do not "
    "add explanations, code fences, or any other words. "
    "If no reasonable action helps, choose the wait object."
)


def concrete_options(beaker: dict, *, floor_seen: bool) -> list[dict]:
    """The adapter offers affordances, NOT goals, ranks or a preferred option.

    A floor slot is not offered as a placement operand until source-backed
    qualitative floor inspection is in the subject's own admitted history.
    This is an epistemic constraint, not physical host authorization.
    """
    options = [
        {"op": "wait"},
        {"op": "observe", "kind": "shelf", "target": "floor:sanctum"},
        {"op": "observe", "kind": "shelf", "target": "shelf:3"},
    ]
    if beaker["condition"] == "broken" and not beaker["collected"]:
        options.append({"op": "collect", "object_id": "beaker:001"})
    if (beaker["condition"] == "broken" and beaker["collected"]
            and floor_seen and beaker["anchor_id"] == "bench:main/position:left"):
        options.append({"op": "place", "object_id": "beaker:001",
                        "anchor_id": "floor:corner:nw"})
    return options


def parse_model_choice(raw: str, options: list[dict]) -> tuple[dict | None, str]:
    """No interpolation, guessed object ID, scripted plan or WAIT-on-failure credit."""
    if not isinstance(raw, str) or len(raw) > 4096:
        return None, "invalid_length_or_type"
    value = raw.strip()
    if "</think>" in value:
        value = value.rsplit("</think>", 1)[-1].strip()
    try:
        choice = json.loads(value)
    except (ValueError, TypeError):
        return None, "malformed_json"
    if not isinstance(choice, dict) or any(type(k) is not str for k in choice):
        return None, "not_exact_action_object"
    if choice not in options:
        return None, "not_an_offered_action_and_operand"
    return choice, "accepted_proposal"


def model_choice(model, subject: tuple[str, ...], goal: str,
                 options: list[dict], *, seed: int = 41) -> dict:
    """Uses the same llama.cpp chat-completion interface as Stages 06/07."""
    menu = "\n".join(json.dumps(choice, sort_keys=True) for choice in options)
    user = (
        "Current first-person subject frame, selected from the protected "
        "Doctor Lives projector:\n"
        + "\n".join(subject)
        + "\nCurrent objective: " + goal
        + "\nChoose EXACTLY ONE JSON operation and operand from these "
        "host-offered possibilities, or wait:\n" + menu
        + "\nProvide only the complete JSON object. /no_think"
    )
    start = perf_counter()
    output = model.create_chat_completion(
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": user}],
        temperature=0.0, seed=seed, max_tokens=100,
    )
    raw = str(output["choices"][0]["message"].get("content") or "").strip()
    proposed, reason = parse_model_choice(raw, options)
    return {
        "raw_reply": raw,
        "proposed_action": proposed,
        "validation": reason,
        "prompt_sha256": sha256(user.encode()).hexdigest(),
        "offered_options": options,
        "usage": output.get("usage", {}),
        "inference_seconds": round(perf_counter() - start, 3),
    }


def _shelf_text(port: ObservationPort, result: dict) -> str:
    receipt = _verify_observation(port, result)
    payload = receipt["offered_payload"]
    if payload["fixture_id"] == "floor:sanctum":
        corner = next((x for x in payload["positions"]
                       if x["anchor_id"] == "floor:corner:nw"), None)
        if corner is None:
            raise LabError("No qualitative floor-corner observation")
        if corner["occupant"] is None:
            return "I inspected the laboratory floor. The northwest corner is empty."
        return ("I inspected the northwest floor corner. It is occupied by "
                + str(corner["occupant"]["name"]) + ".")
    if payload["fixture_id"] == "shelf:3":
        entries = [str(x["ordinal"]) + ": " + str(x["occupant"]["name"])
                   for x in payload["positions"] if x["occupant"]]
        return "I surveyed the third shelf and noticed " + (", ".join(entries) or
               "no volumes there") + "."
    raise LabError("No approved shelf narration")


def execute_one(root: Path, model, *, brain_name: str = "brain",
                world_name: str = "world.sqlite3",
                goal: str = GOAL, seed: int = 41) -> dict:
    """One live, non-scripted model proposal; open DB afresh on every invocation."""
    world = SpatialHabitat(root / world_name)
    port = ObservationPort(world)
    library = BookLibrary(world)
    port.verify()
    library.verify()
    brain = PretoriusBrain(root / brain_name)
    offered, beaker, frame = _offer_room(brain, port)
    subject = frame.renderer_context()
    options = concrete_options(beaker, floor_seen=_has_floor_percept(brain, port))
    policy = brain.think("concrete_laboratory_action",
                         decision_text=goal + "\n" + subject[-1])
    response = model_choice(model, subject, goal, options, seed=seed)
    proposal = response["proposed_action"]
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "controller": "real_local_language_model_plus_authoritative_pretorius_subject_frame",
        "abstract_policy_top": policy["selected_action"],
        "abstract_policy_scores": policy["action_scores"],
        "goal": goal,
        "room_receipt": offered["receipt_hash"],
        "subject_frame": list(subject),
        "world_before": world.verify(),
        **response,
        "executed": False, "admitted_memory_id": None,
        "host_denied": False, "goal_relevance": "scored_posthoc_not_used_for_decoding",
    }
    if proposal is None:
        record["status"] = "invalid_proposal_no_execution"
    elif proposal["op"] == "wait":
        record["status"] = "model_selected_wait"
    elif proposal["op"] == "observe":
        try:
            receipt = port.expose(proposal["kind"], proposal["target"])
            sentence = _shelf_text(port, receipt)
            result = _admit_observation(brain, port, receipt, sentence)
            record.update(status="model_selected_additional_observation",
                          observed_receipt=receipt["receipt_hash"],
                          admitted_memory_id=result["memory_id"])
        except (LabError, Conflict, ValueError) as exc:
            record.update(status="observation_denied_no_admission",
                          host_denied=True, reason=str(exc))
    elif proposal["op"] in {"collect", "place"}:
        before = world.verify()["revision"]
        try:
            outcome = world.commit(proposal, actor="pretorius_research",
                                   expected_revision=before)
            verified = world.verify()
            receipt = port.expose("object", "beaker:001")
            observed = _verify_observation(port, receipt)["offered_payload"]
            if proposal["op"] == "collect" and not world.status()["state"]["objects"]["beaker:001"]["collected"]:
                raise ValueError("Collection did not materialize")
            if proposal["op"] == "place" and observed["location"]["anchor_id"] != proposal["anchor_id"]:
                raise ValueError("Placement did not materialize")
            if not verified["verified"]:
                raise ValueError("Physical event replay verification failed")
            text = ("I collected the broken beaker fragments."
                    if proposal["op"] == "collect" else
                    "I placed the gathered beaker fragments in the northwest floor corner.")
            admission = _admit_action(brain, world, outcome, proposal, text, before)
            record.update(status="model_action_verified_and_admitted",
                          executed=True, event_hash=outcome["event_hash"],
                          consequence_receipt=receipt["receipt_hash"],
                          admitted_memory_id=admission["memory_id"])
        except (LabError, Conflict, ValueError) as exc:
            record.update(status="host_denied_no_admission",
                          host_denied=True, reason=str(exc))
    else:
        raise AssertionError("Only offered options may reach an executor")
    brain.save()
    record["world_after"] = world.verify()
    record["brain_tick"] = brain.store.tick
    return record


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--gguf", type=Path, required=True)
    p.add_argument("--model", choices=tuple(MODEL_SHA), default="qwen3-1.7b-q4_k_m")
    p.add_argument("--world", default="world.sqlite3")
    p.add_argument("--brain", default="brain")
    p.add_argument("--goal", default=GOAL)
    p.add_argument("--seed", type=int, default=41)
    a = p.parse_args()
    digest = sha256()
    with a.gguf.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    if digest.hexdigest() != MODEL_SHA[a.model]:
        raise ValueError("GGUF checksum mismatch: no model execution")
    from llama_cpp import Llama
    model = Llama(model_path=str(a.gguf), n_ctx=4096, n_threads=4,
                  n_gpu_layers=0, verbose=False)
    result = execute_one(a.root, model, brain_name=a.brain,
                         world_name=a.world, goal=a.goal, seed=a.seed)
    result["model_id"] = a.model
    result["model_sha256"] = digest.hexdigest()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
