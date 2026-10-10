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

SCHEMA = "pretorius.living-lab.concrete-model-action.v2"
MODEL_SHA = {
    "qwen3-1.7b-q4_k_m":
        "d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5",
}
SYSTEM = (
    "You are the concrete-action decoder for Doctor Septimus Pretorius. "
    "His persistent cognition and firsthand subject frame are authoritative. "
    "Choose one operation that directly advances the stated goal, not merely a legal but irrelevant operation. Base the choice ONLY on the "
    "presented first-person facts, the current objective and the offered "
    "legal operations. You are not permitted to invent observations, physical "
    "locations, page content, permissions or past memories. A world host "
    "will independently authorize and execute or deny your proposal. "
    "Respond with exactly one complete action token copied from the choices. "
    "A token names BOTH an operation and its specific operand. "
    "Do not add explanations, quotes, code fences, or any other words. "
    "If no reasonable action helps, choose WAIT."
)


def _choice(verb: str, operand: str = "none", destination: str = "none") -> dict:
    """Uniform renderer grammar for all candidate operations and operands."""
    return {"verb": verb, "operand": operand, "destination": destination}


def concrete_options(beaker: dict, *, floor_seen: bool) -> list[dict]:
    """Offer typed affordances, never a ranked goal-directed plan."""
    options = [
        _choice("wait"),
        _choice("observe", "floor:sanctum"),
        _choice("observe", "shelf:3"),
    ]
    if beaker["condition"] == "broken" and not beaker["collected"]:
        options.append(_choice("collect", "beaker:001"))
    if (beaker["condition"] == "broken" and beaker["collected"]
            and floor_seen and beaker["anchor_id"] == "bench:main/position:left"):
        options.append(_choice("place", "beaker:001", "floor:corner:nw"))
    return options


def _host_action(proposal: dict) -> dict:
    """Mechanical schema conversion only, NOT an autonomous planner."""
    verb = proposal["verb"]
    if verb == "collect":
        return {"op": "collect", "object_id": proposal["operand"]}
    if verb == "place":
        return {"op": "place", "object_id": proposal["operand"],
                "anchor_id": proposal["destination"]}
    raise ValueError("No physical host mapping for proposed verb")


def action_token(option: dict) -> str:
    """One unambiguous fixed grammar across all legal actions, including operands.

    Token is an entire concrete proposal, not a numeric/menu-position key.
    The decoding map may only return the exact offered object. It cannot
    interpret free-text model requests or fill in missing operands.
    """
    verb, operand, dest = option["verb"], option["operand"], option["destination"]
    if verb == "wait" and operand == dest == "none":
        return "WAIT"
    if verb == "observe" and dest == "none":
        return "OBSERVE|" + operand
    if verb == "collect" and dest == "none":
        return "COLLECT|" + operand
    if verb == "place":
        return "PLACE|" + operand + "|" + dest
    raise ValueError("Invalid offered concrete action tuple")


def parse_model_choice(raw: str, options: list[dict]) -> tuple[dict | None, str]:
    """No inferred operands, no silent WAIT, and no auto-repair of wrong tokens."""
    if not isinstance(raw, str) or len(raw) > 4096:
        return None, "invalid_length_or_type"
    value = raw.strip()
    if "</think>" in value:
        value = value.rsplit("</think>", 1)[-1].strip()
    # A JSON-quoted exact token is not a repaired or inferred action.
    if value.startswith('"') and value.endswith('"'):
        try:
            value = json.loads(value)
        except (TypeError, ValueError):
            return None, "malformed_quoted_token"
    if not isinstance(value, str):
        return None, "not_a_token"
    mapping = {action_token(item): item for item in options}
    if len(mapping) != len(options):
        raise ValueError("Ambiguous offered concrete action tokens")
    if value not in mapping:
        return None, "not_an_offered_action_and_operand"
    return mapping[value], "accepted_proposal"


def model_choice(model, subject: tuple[str, ...], goal: str,
                 options: list[dict], *, seed: int = 41) -> dict:
    """Uses the same llama.cpp chat-completion interface as Stages 06/07."""
    menu = "\n".join(action_token(choice) for choice in options)
    user = (
        "Current first-person subject frame, selected from the protected "
        "Doctor Lives projector:\n"
        + "\n".join(subject)
        + "\nCurrent objective: " + goal
        + "\nChoose exactly one complete operation-and-operand token from these "
        "host-offered possibilities, or WAIT:\n" + menu
        + "\nOutput the chosen token verbatim, with no prefix or commentary. /no_think"
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
        "offered_action_tokens": [action_token(choice) for choice in options],
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
    elif proposal["verb"] == "wait":
        record["status"] = "model_selected_wait"
    elif proposal["verb"] == "observe":
        try:
            receipt = port.expose("shelf", proposal["operand"])
            sentence = _shelf_text(port, receipt)
            result = _admit_observation(brain, port, receipt, sentence)
            record.update(status="model_selected_additional_observation",
                          observed_receipt=receipt["receipt_hash"],
                          admitted_memory_id=result["memory_id"])
        except (LabError, Conflict, ValueError) as exc:
            record.update(status="observation_denied_no_admission",
                          host_denied=True, reason=str(exc))
    elif proposal["verb"] in {"collect", "place"}:
        before = world.verify()["revision"]
        host_action = _host_action(proposal)
        try:
            outcome = world.commit(host_action, actor="pretorius_research",
                                   expected_revision=before)
            verified = world.verify()
            receipt = port.expose("object", "beaker:001")
            observed = _verify_observation(port, receipt)["offered_payload"]
            if proposal["verb"] == "collect" and not world.status()["state"]["objects"]["beaker:001"]["collected"]:
                raise ValueError("Collection did not materialize")
            if proposal["verb"] == "place" and observed["location"]["anchor_id"] != proposal["destination"]:
                raise ValueError("Placement did not materialize")
            if not verified["verified"]:
                raise ValueError("Physical event replay verification failed")
            text = ("I collected the broken beaker fragments."
                    if proposal["verb"] == "collect" else
                    "I placed the gathered beaker fragments in the northwest floor corner.")
            admission = _admit_action(brain, world, outcome, host_action, text, before)
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
