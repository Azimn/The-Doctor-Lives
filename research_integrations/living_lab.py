"""Issue #53 research-only bridge. Lab owns the world, Doctor Lives owns memory/policy.

No canonical subject directory or live laboratory is ever opened by this module.
Concrete grounding is a *declared deterministic mapper* from existing neural
abstract action scores, visible affordances, and source-verified history.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import shutil
import sqlite3
from typing import Any

from doctor_lives.cognition import PretoriusBrain
from doctor_lives.ingress import project_raw_ingress
from doctor_lives.models import Experience, SubjectFrame
from doctor_lives.projection import ProjectionContext
from pretorius_lab.habitat_v2 import SpatialHabitat
from pretorius_lab.book_library import BookLibrary
from pretorius_lab.observation_receipts import ObservationPort
from pretorius_lab.physics import Conflict, LabError, digest

DOCTOR_COMMIT = "56aab5493ef48cdb560881a138b2277ca6ebcce0"
LAB_COMMIT = "93d19671f7666b2996e6fcad211c5e6509336466"
SCHEMA = "pretorius-living-lab-research/1"
GOAL = "I want to make the broken laboratory glass safe without inventing what I know."


class AdmissionError(ValueError):
    pass


def _read_event(world: SpatialHabitat, event_id: str) -> dict:
    world.verify()
    with world._open() as db:
        row = db.execute("SELECT envelope,event_hash FROM events WHERE event_id=?", (event_id,)).fetchone()
    if not row:
        raise AdmissionError("Unrecognized physical event")
    result = json.loads(row[0])
    if digest(result) != row[1]:
        raise AdmissionError("Corrupt physical event")
    return {**result, "event_hash": row[1]}


def _verify_observation(port: ObservationPort, receipt: dict) -> dict:
    port.verify()
    with port.habitat._open() as db:
        row = db.execute(
            "SELECT payload,event_hash FROM observation_events WHERE delivery_id=?",
            (receipt["delivery_id"],),
        ).fetchone()
    if not row or row[1] != receipt["receipt_hash"]:
        raise AdmissionError("Unknown observation receipt")
    payload = json.loads(row[0])
    if digest(payload) != row[1] or payload["payload_digest"] != digest(receipt["offered_payload"]):
        raise AdmissionError("Observation receipt/payload mismatch")
    if payload["offered_payload"] != receipt["offered_payload"]:
        raise AdmissionError("Altered observed fact")
    if payload["world_epoch"] != port.habitat.status()["world_epoch"]:
        raise AdmissionError("Wrong world epoch")
    return payload


def _project(brain: PretoriusBrain, text: str):
    """Produce a subject-safe percept without passing raw lab payload to subject."""
    return project_raw_ingress(
        {"channel": "world", "percept": text, "kind": "laboratory_observation",
         "source": "verified_laboratory_interface"},
        context=ProjectionContext(
            subject_id="pretorius", tick=brain.store.tick + 1,
            source_state_digest=brain.store.digest(),
            projection_rule_version="subject-interface-a12-living-lab-research",
        ),
    )


def _index_admission(brain: PretoriusBrain, memory_id: str,
                     kind: str, proof: str, epoch: str) -> None:
    """Separate, indexed *evidence of adapter admission*, not a memory authority."""
    with brain.store.transaction() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS lab_research_admissions (
            memory_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL,
            evidence_kind TEXT NOT NULL, proof_hash TEXT NOT NULL,
            world_epoch TEXT NOT NULL, UNIQUE(evidence_kind,proof_hash)
        )""")
        conn.execute("INSERT INTO lab_research_admissions VALUES (?,?,?,?,?)",
                     (memory_id, "pretorius", kind, proof, epoch))


def _indexed(brain: PretoriusBrain, kind: str, epoch: str) -> set[tuple[str, str]]:
    with brain.store.connect() as conn:
        exists = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='lab_research_admissions'"
        ).fetchone()
        if not exists:
            return set()
        rows = conn.execute("""SELECT memory_id,proof_hash
                               FROM lab_research_admissions
                               WHERE subject_id='pretorius'
                                 AND evidence_kind=? AND world_epoch=?""",
                            (kind, epoch)).fetchall()
    return {(str(row[0]), str(row[1])) for row in rows}


def reconcile_unadmitted_host_actions(
    brain: PretoriusBrain, world: SpatialHabitat,
) -> list[dict]:
    """Recover a lost lab-to-memory handoff without fabricating lived memory.

    An authoritative committed host operation, by itself, is NOT evidence
    that Pretorius perceived the consequence. Admit it as EXTERNAL history
    only, even when the actor field identifies the research subject. An
    action-outcome record already bound to local admission evidence wins.
    """
    proof = world.verify()
    epoch = proof["world_epoch"]
    firsthand = _indexed(brain, "action", epoch)
    recovered = _indexed(brain, "recovery", epoch)
    stored = brain.store.memories()
    with world._open() as db:
        event_ids = [row[0] for row in db.execute(
            "SELECT event_id FROM events ORDER BY revision"
        )]
    records = []
    for event_id in event_ids:
        event = _read_event(world, event_id)
        action = event["action"]
        if (event["actor"] != "pretorius_research"
                or event["world_epoch"] != epoch
                or action.get("op") not in {"collect", "place"}
                or action.get("object_id") != "beaker:001"):
            continue
        proof_hash = event["event_hash"]
        if any(
            memory["source"] == "lab:action:" + event_id + ":" + proof_hash
            and not memory["external"]
            and memory["kind"] == "action_outcome"
            and (str(memory["id"]), proof_hash) in firsthand
            for memory in stored
        ):
            continue
        if any(
            memory["source"] == "lab:recovery:" + event_id + ":" + proof_hash
            and memory["external"]
            and memory["kind"] == "lab_event_report"
            and (str(memory["id"]), proof_hash) in recovered
            for memory in stored
        ):
            continue
        source = "lab:recovery:" + event_id + ":" + proof_hash
        verb = action["op"]
        if verb == "collect":
            claim = "gathered the broken laboratory beaker fragments"
        else:
            claim = "relocated the gathered beaker fragments"
        text = (
            "A verified laboratory event record attributes a request that "
            + claim + " to my research actor label. I cannot retrieve a "
            "firsthand record of witnessing that outcome."
        )
        # If the process stopped after writing EXTERNAL text but before
        # indexing its proof, repair only an exact external statement whose
        # words are independently regenerated from the verified world event.
        # An alien string, mismatched classification or duplicate is refused.
        existing = [m for m in stored if m["source"] == source]
        if existing:
            if (len(existing) != 1 or not existing[0]["external"]
                    or existing[0]["kind"] != "lab_event_report"
                    or existing[0]["evidence_class"] != "external_statement"
                    or existing[0]["text"] != text):
                raise AdmissionError("Unverified recovery memory collision")
            memory_id = str(existing[0]["id"])
            _index_admission(brain, memory_id, "recovery", proof_hash, epoch)
            recovered = _indexed(brain, "recovery", epoch)
            records.append({
                "event_id": event_id,
                "event_hash": proof_hash,
                "memory_id": memory_id,
                "classification": "external_record_not_firsthand",
                "index_repaired": True,
            })
            continue
        # A record recovered after interruption is NEVER lived_runtime_memory.
        saved = brain.ingest(Experience(
            text=text,
            source=source,
            kind="lab_event_report",
            external=True,
            confidence=1.0,
            tags=("lab", "external_event_recovery", "not_firsthand"),
        ))
        _index_admission(brain, saved["memory_id"], "recovery", proof_hash, epoch)
        stored = brain.store.memories()
        recovered = _indexed(brain, "recovery", epoch)
        records.append({
            "event_id": event_id,
            "event_hash": proof_hash,
            "memory_id": saved["memory_id"],
            "classification": "external_record_not_firsthand",
            "index_repaired": False,
        })
    if records:
        brain.save()
    return records


def _has_attested_memory(brain: PretoriusBrain, world: SpatialHabitat, op: str) -> bool:
    """No arbitrary autobiographical text or foreign-source memory can unlock an action."""
    proof = world.verify()
    indexed = _indexed(brain, "action", proof["world_epoch"])
    for record in brain.store.memories():
        source = str(record["source"])
        if (not source.startswith("lab:action:") or record["external"]
                or record["kind"] != "action_outcome"
                or (str(record["id"]), source.rsplit(":", 1)[-1]) not in indexed):
            continue
        parts = source.split(":")
        if len(parts) != 4:
            continue
        try:
            e = _read_event(world, parts[2])
        except (AdmissionError, LabError, KeyError):
            continue
        if (e["event_hash"] == parts[3] and e["world_epoch"] == proof["world_epoch"]
                and e["action"] == {"op": op, "object_id": "beaker:001"}):
            return True
    return False


def _has_floor_percept(brain: PretoriusBrain, port: ObservationPort) -> bool:
    proof = port.verify()
    indexed = _indexed(brain, "observation", proof["world_epoch"])
    known = set()
    with port.habitat._open() as db:
        for encoded, h in db.execute("SELECT payload,event_hash FROM observation_events"):
            entry = json.loads(encoded)
            if (digest(entry) == h and entry["world_epoch"] == proof["world_epoch"]
                    and entry["kind"] == "shelf" and entry["target"] == "floor:sanctum"
                    and any(x["anchor_id"] == "floor:corner:nw" and x["occupant"] is None
                            for x in entry["offered_payload"]["positions"])):
                known.add(h)
    return any(str(m["source"]) == "lab:observation:" + h
               and not m["external"] and m["kind"] == "laboratory_observation"
               and (str(m["id"]), h) in indexed
               for m in brain.store.memories() for h in known)


def _admit_observation(brain: PretoriusBrain, port: ObservationPort,
                       receipt: dict, text: str) -> dict:
    _verify_observation(port, receipt)
    source = "lab:observation:" + receipt["receipt_hash"]
    if any(m["source"] == source for m in brain.store.memories()):
        raise AdmissionError("Duplicate firsthand observation admission")
    # Not a subjective-consciousness claim: the active controller processed the
    # percept; the source certifies delivery, not humanlike experience.
    saved = brain.ingest(Experience(text=text, source=source,
                                   kind="laboratory_observation", tags=("lab", "offered_fact")))
    _index_admission(brain, saved["memory_id"], "observation", receipt["receipt_hash"],
                     port.habitat.verify()["world_epoch"])
    return saved


def _admit_action(brain: PretoriusBrain, world: SpatialHabitat, receipt: dict,
                  action: dict, text: str, before_revision: int) -> dict:
    event = _read_event(world, receipt["event_id"])
    current = world.verify()
    if (event != receipt or event["action"] != action
            or event["actor"] != "pretorius_research"
            or event["world_epoch"] != current["world_epoch"]
            or event["base_revision"] != before_revision
            or event["committed_revision"] != before_revision + 1):
        raise AdmissionError("Action receipt cannot support memory")
    if current["revision"] < event["committed_revision"]:
        raise AdmissionError("World rolled back")
    source = "lab:action:" + event["event_id"] + ":" + event["event_hash"]
    if any(m["source"] == source for m in brain.store.memories()):
        raise AdmissionError("Replayed action cannot create duplicate autobiography")
    saved = brain.ingest(Experience(text=text, source=source, kind="action_outcome",
                                   novelty=0.3, tags=("lab", "physical_consequence")))
    _index_admission(brain, saved["memory_id"], "action", event["event_hash"],
                     event["world_epoch"])
    return saved


def prepare(root: Path, fixture: Path) -> dict:
    if root.exists() and any(root.iterdir()):
        raise FileExistsError("Research root must be empty")
    root.mkdir(parents=True, exist_ok=True)
    base = SpatialHabitat.create(root / "_unmodified_seed.sqlite3")
    BookLibrary(base).initialize()
    ObservationPort(base).initialize()
    base.fork_to(root / "world.sqlite3")
    world = SpatialHabitat(root / "world.sqlite3")
    BookLibrary(world).initialize()
    ObservationPort(world).initialize()
    # An external operator creates an initial *observed problem*, not Pretorius's action.
    initial = world.commit({"op": "break", "object_id": "beaker:001"}, actor="local_operator")
    edition = json.loads(fixture.read_text(encoding="utf-8"))
    BookLibrary(world).install("book:007", **edition)
    brain = PretoriusBrain(root / "brain")
    brain.save()
    shutil.copytree(root / "brain", root / "control_brain")
    return {"schema": SCHEMA, "source_pins": {"doctor": DOCTOR_COMMIT, "lab": LAB_COMMIT},
            "research_world": world.status()["mode"], "initial_event": initial["event_hash"],
            "world_verified": world.verify()["verified"]}


def _verified_subject_frame(brain: PretoriusBrain, port: ObservationPort, *,
                            current_percept: str | None = None,
                            withhold_lab_autobiography: bool = False) -> SubjectFrame:
    """Only locally admitted lab memories can enter the protected subject frame.

    Other memories are still governed by Doctor Lives' existing classifications.
    This does not claim to secure its trusted direct BrainStore write API.
    """
    epoch = port.habitat.verify()["world_epoch"]
    keys = {kind: _indexed(brain, kind, epoch)
            for kind in ("action", "observation", "book", "recovery")}
    # Cue retrieval only with the current offered percept. No host secrets.
    view = brain.cognitive_view(query=current_percept)
    def admitted(item) -> bool:
        source = str(item.provenance.source)
        if not source.startswith("lab:"):
            return True
        if withhold_lab_autobiography:
            return False
        parts = source.split(":")
        if len(parts) != 4 and len(parts) != 3:
            return False
        kind = parts[1]
        proof_hash = parts[-1]
        if kind == "recovery" and (
            not item.provenance.external
            or item.provenance.evidence_class != "external_statement"
        ):
            return False
        return kind in keys and (item.record_id, proof_hash) in keys[kind]
    filtered = replace(view, experiences=tuple(x for x in view.experiences if admitted(x)))
    # Reuse the accepted Subject Interface Firewall projector, not a second renderer.
    return brain._subject_frame_from_view(filtered)


def _offer_room(brain: PretoriusBrain, port: ObservationPort, *,
                withhold_lab_autobiography: bool = False):
    receipt = port.expose("room", "room:sanctum")
    payload = _verify_observation(port, receipt)["offered_payload"]
    obj = payload["objects"]["beaker:001"]
    condition = obj["condition"]
    where = "the main bench" if obj["anchor_id"] == "bench:main/position:left" else "a corner of the room"
    text = ("I see the laboratory beaker at " + where + ". Its glass is " + condition +
            (" and its fragments are gathered." if obj["collected"] else
             " and its fragments are scattered."))
    projected = _project(brain, text)
    existing = _verified_subject_frame(
        brain, port, current_percept=text,
        withhold_lab_autobiography=withhold_lab_autobiography,
    )
    frame = SubjectFrame(items=existing.items + SubjectFrame.from_events([projected.event]).items)
    return receipt, obj, frame


def _options(obj: dict, *, collected_memory: bool, floor_memory: bool):
    """Only host-observed facts, verified memory and stable, narrow public action grammar."""
    options = [("wait", {}, "avoid", 0.20)]
    if obj["condition"] == "broken" and not obj["collected"]:
        options += [("collect", {"op": "collect", "object_id": "beaker:001"},
                     "persist", 0.72)]
    elif (obj["condition"] == "broken" and obj["collected"]
          and obj["anchor_id"] == "bench:main/position:left"):
        if collected_memory and not floor_memory:
            options += [("inspect_floor", {}, "explore", 0.68)]
        if floor_memory:
            options += [("place", {"op": "place", "object_id": "beaker:001",
                                    "anchor_id": "floor:corner:nw"}, "persist", 0.76)]
    return options


def turn(root: Path, *, world_name: str = "world.sqlite3",
         brain_name: str = "brain") -> dict:
    world = SpatialHabitat(root / world_name)
    port = ObservationPort(world)
    port.verify()
    library = BookLibrary(world)
    library.verify()
    brain = PretoriusBrain(root / brain_name)
    offered, obj, frame = _offer_room(brain, port)
    # Never send JSON, coordinates, hidden world state, raw sources, or model telemetry.
    conscious = frame.renderer_context()
    # The actual The-Doctor-Lives recurrent/state-policy controller is evaluated.
    policy = brain.think("laboratory", decision_text=" ".join(conscious[-3:]) + " " + GOAL)
    collected_memory = _has_attested_memory(brain, world, "collect")
    floor_memory = _has_floor_percept(brain, port)
    options = _options(obj, collected_memory=collected_memory, floor_memory=floor_memory)
    ranked = sorted(
        ((round(ground + 0.15 * float(policy["action_scores"][abstract]), 9),
          name, action, abstract) for name, action, abstract, ground in options),
        key=lambda item: (-item[0], item[1]),
    )
    ground_only = sorted(options, key=lambda item: (-item[3], item[0]))[0][0]
    score, chosen, action, abstract = ranked[0]
    audit: dict[str, Any] = {
        "schema": SCHEMA, "world_before": world.verify(), "observed_delivery": offered["receipt_hash"],
        "subject_frame": conscious, "selected": chosen, "selected_abstract_mapping": abstract,
        "controller_top_abstract_action": policy["selected_action"],
        "policy_scores": policy["action_scores"],
        "candidate_scores": [{"option": x[1], "score": x[0]} for x in ranked],
        "ground_only_choice": ground_only,
        "policy_changed_ground_only_choice": chosen != ground_only,
        "controller_top_action_is_executed_mapping": abstract == policy["selected_action"],
        "action": action, "goal": GOAL,
        "memory_evidence": {"collected": collected_memory, "floor_observed": floor_memory},
    }
    if chosen == "collect" or chosen == "place":
        before = world.verify()["revision"]
        try:
            outcome = world.commit(action, actor="pretorius_research",
                                   expected_revision=before)
            verified = _read_event(world, outcome["event_id"])
            if verified != outcome:
                raise AdmissionError("World outcome differs from persisted event")
            after = port.expose("object", "beaker:001")
            condition = _verify_observation(port, after)["offered_payload"]
            if chosen == "collect" and (condition["condition"] != "broken"
                                        or world.status()["state"]["objects"]["beaker:001"]["collected"] is not True):
                raise AdmissionError("Expected gathered fragments not verified")
            if chosen == "place" and condition["location"]["anchor_id"] != "floor:corner:nw":
                raise AdmissionError("Expected destination not verified")
            sentence = ("I gathered the broken beaker fragments from the bench." if chosen == "collect" else
                        "I placed the gathered beaker fragments in the northwest floor corner.")
            admission = _admit_action(brain, world, outcome, action, sentence, before)
            audit["memory_id"] = admission["memory_id"]
            audit["action_receipt"] = outcome["event_hash"]
            audit["verified_consequence"] = condition
            audit["status"] = "verified_action_and_admission"
        except (LabError, Conflict, AdmissionError) as exc:
            audit["status"] = "denied_no_admission"
            audit["denial"] = str(exc)
    elif chosen == "inspect_floor":
        floor = port.expose("shelf", "floor:sanctum")
        payload = _verify_observation(port, floor)["offered_payload"]
        available = any(x["anchor_id"] == "floor:corner:nw" and x["occupant"] is None
                        for x in payload["positions"])
        sentence = ("I inspected the floor and found the northwest corner empty."
                    if available else "I inspected the floor; the northwest corner is occupied.")
        admission = _admit_observation(brain, port, floor, sentence)
        audit["memory_id"] = admission["memory_id"]
        audit["status"] = "verified_additional_observation"
        audit["floor_receipt"] = floor["receipt_hash"]
    else:
        audit["status"] = "abstained"
    brain.save()
    audit["world_after"] = world.verify()
    audit["brain_tick"] = brain.store.tick
    return audit


def _admit_book_page(brain: PretoriusBrain, book: BookLibrary, delivered: dict) -> dict:
    """Admit only a source-backed page actively processed through the subject port."""
    proof = book.verify()
    with book.habitat._open() as db:
        row = db.execute("SELECT payload,event_hash FROM books_events WHERE event_id=?",
                         (delivered["delivery_event_id"],)).fetchone()
    if not row:
        raise AdmissionError("Page delivery not found in laboratory book ledger")
    event = json.loads(row[0])
    if (digest(event) != row[1] or event["world_epoch"] != proof["world_epoch"]
            or event["action"] != {"op": "read", "book_id": delivered["book_id"]}
            or event["page_receipt"] != {
                "page_number": delivered["page"],
                "page_digest": digest(delivered["page_text"]),
                "edition_digest": delivered["content_digest"],
            }):
        raise AdmissionError("Invalid page/edition delivery claim")
    if (delivered["page"] < 1 or delivered["page"] > delivered["page_count"]):
        raise AdmissionError("Page outside the verified edition")
    source = "lab:book:" + event["event_id"] + ":" + row[1]
    if any(m["source"] == source for m in brain.store.memories()):
        raise AdmissionError("Replayed page delivery")
    text = ("I read page " + str(delivered["page"]) + " of " +
            delivered["title"] + ": " + delivered["page_text"])
    projected = _project(brain, text)
    # A real cognitive pass over this *particular* page is required.
    policy = brain.think("book_read", decision_text=projected.event.subject_text)
    recorded = brain.ingest(Experience(
        text=projected.experience.text, source=source,
        kind="read_page", tags=("lab", "source_backed_page")))
    _index_admission(brain, recorded["memory_id"], "book", row[1], proof["world_epoch"])
    brain.save()
    return {"memory_id": recorded["memory_id"], "source_proof": row[1],
            "processed_with_policy": policy["policy_version"]}


def book_contract(root: Path) -> dict:
    """Explicit HOST contract check, not an autonomous-controller result."""
    world = SpatialHabitat(root / "world.sqlite3")
    book = BookLibrary(world)
    book.verify()
    before = book.catalog("book:007")["book:007"]
    if before["opened"]:
        raise AdmissionError("Book precondition: closed")
    book.operate("book:007", "open", actor="pretorius_research")
    first = book.operate("book:007", "read", actor="pretorius_research")
    brain = PretoriusBrain(root / "brain")
    admitted = _admit_book_page(brain, book, first)
    if not first["page_text"].startswith("Page 1."):
        raise AdmissionError("Wrong page edition")
    book.operate("book:007", "mark", bookmark_id="ribbon", actor="pretorius_research")
    book.operate("book:007", "turn", direction=1, actor="pretorius_research")
    second = book.operate("book:007", "read", actor="pretorius_research")
    book.operate("book:007", "close", actor="pretorius_research")
    # Reopen the database, not the in-memory BookLibrary object.
    reopened = BookLibrary(SpatialHabitat(root / "world.sqlite3"))
    saved = reopened.catalog("book:007")["book:007"]
    if saved["bookmarks"].get("ribbon") != 1:
        raise AdmissionError("Bookmark was not persistent")
    reopened.operate("book:007", "open_mark", bookmark_id="ribbon",
                     actor="pretorius_research")
    after = reopened.operate("book:007", "read", actor="pretorius_research")
    with world._open() as db:
        delivered_page_numbers = [
            json.loads(e[0])["page_receipt"]["page_number"]
            for e in db.execute("SELECT payload FROM books_events")
            if json.loads(e[0])["action"]["op"] == "read"
        ]
    restored = PretoriusBrain(root / "brain")
    recognized = [
        m for m in restored.store.memories()
        if str(m["source"]).startswith("lab:book:")
        and (str(m["id"]), str(m["source"]).rsplit(":", 1)[-1])
        in _indexed(restored, "book", world.verify()["world_epoch"])
    ]
    if len(recognized) != 1:
        raise AdmissionError("Book autobiographical admission count mismatch")
    return {"host_contract_only": True, "page_1_processed_with_real_policy": True,
            "page_1_admitted_memory_id": admitted["memory_id"],
            "page_2_offered_but_not_admitted": 2 in delivered_page_numbers,
            "page_3_neither_delivered_nor_remembered": 3 not in delivered_page_numbers, "book_verify": reopened.verify(),
            "bookmark_page": saved["bookmarks"]["ribbon"],
            "read_first_page_digest": digest(first["page_text"]),
            "read_second_page_digest": digest(second["page_text"]),
            "reopened_page_matches": after["page_text"] == first["page_text"],
            "unread_third_page_was_not_delivered": 3 not in delivered_page_numbers}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=("prepare", "turn", "book-contract", "verify"))
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--fixture", type=Path)
    p.add_argument("--world", default="world.sqlite3")
    p.add_argument("--brain", default="brain")
    a = p.parse_args()
    if a.command == "prepare":
        if a.fixture is None:
            p.error("--fixture required")
        result = prepare(a.root, a.fixture)
    elif a.command == "turn":
        result = turn(a.root, world_name=a.world, brain_name=a.brain)
    elif a.command == "book-contract":
        result = book_contract(a.root)
    else:
        w = SpatialHabitat(a.root / a.world)
        result = {"physical": w.verify(), "books": BookLibrary(w).verify(),
                  "observations": ObservationPort(w).verify(),
                  "brain": PretoriusBrain(a.root / a.brain).status()["tick"]}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
