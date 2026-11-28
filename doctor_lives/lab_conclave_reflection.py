"""Connect completed reading to the existing Conclave and original Noesis.

All current rival interpretations enter one existing deliberation, with
individual source provenance retained. No interpretation is a lived fact or
motor grant. Preserve historical single-reading receipts without upgrading
their evidence claims.
"""
from __future__ import annotations
from contextlib import closing
from hashlib import sha256
import json

from .conclave import Conclave, Stimulus
from .lab_endogenous_book_task import EndogenousBookPursuit
from .lab_six_organ_session import SixOrganLaboratoryCycle

PREFIX = "conclave:completed-reading:"


def compile_readings(readings):
    """All rival questions and propositions, not a fixed preferred tradition.

    Stable ordering only makes the packet replayable; it is not prioritization.
    Explicitly withdrawn/ignored readings remain in the audit with their reason.
    No raw internal IDs or method metadata enter the conscious query.
    """
    rows = []
    lines = []
    ids = set()
    for reading in sorted(readings, key=lambda r: (r.tradition_id, r.id)):
        if reading.id in ids:
            raise PermissionError("Duplicate Conclave interpretation")
        ids.add(reading.id)
        active = reading.state not in ("withdrawn", "ignored")
        line = ("I consider this possible interpretation: " + reading.proposition
                + " I ask myself: " + reading.question) if active else None
        if active:
            lines.append(line)
        rows.append({
            "reading_id": reading.id, "tradition_id": reading.tradition_id,
            "source_event_id": reading.source_event_id, "source_kind": reading.source_kind,
            "source_work": reading.source_work, "claim_scope": reading.claim_scope,
            "proposition": reading.proposition, "question": reading.question,
            "question_sha256": sha256(reading.question.encode()).hexdigest(),
            "method_trace": reading.method_trace, "truth_status": reading.truth_status,
            "state_at_decision": reading.state, "considered": active,
            "exclusion_reason": None if active else reading.state,
            "first_person": line,
        })
    return " ".join(lines), rows


def reflect_completed_reading(book: EndogenousBookPursuit) -> dict | None:
    """Deliberate once using the entire source-bound interpretation set."""
    if type(book) is not EndogenousBookPursuit or type(book.host) is not SixOrganLaboratoryCycle:
        raise PermissionError("Actual canonical native reading host required")
    goal = book._load()
    if not goal or goal["phase"] != "complete":
        return None
    book._completed_source(goal)
    brain = book.runtime._port.brain
    store = brain.store
    memory = store.get_memory(goal["read_memory_id"])
    if memory is None or not memory.get("source_event_id"):
        raise RuntimeError("Completed reading lacks original canonical event")
    key = PREFIX + goal["id"]
    context = "reading:" + goal["id"]
    trigger = "conclave_reading_" + goal["id"]
    conclave = Conclave(store, enabled=True)
    conclave.interpret(Stimulus(
        memory["source_event_id"], "world_verified", context,
        memory["text"][:2000].strip(),
    ))
    readings = conclave.readings(context)
    if not readings:
        return None
    if any(r.source_event_id != memory["source_event_id"] or
           r.source_kind != "world_verified" for r in readings):
        raise PermissionError("Reading interpretation source mismatch")
    with closing(store.connect()) as db:
        previous = db.execute(
            "SELECT id,selected_action,state_pressure_json FROM policy_decisions "
            "WHERE trigger=? ORDER BY rowid", (trigger,),
        ).fetchall()
    if len(previous) > 1:
        raise RuntimeError("Duplicate original Conclave reflection")
    prior_raw = store.meta(key)
    prior = json.loads(prior_raw) if prior_raw else None
    if prior and prior["schema"] == "pretorius.conclave-reading-reflection.v1":
        # An already experienced historical reflection is never rewritten.
        historical = next((r for r in readings if r.id == prior["reading_id"]), None)
        if (historical is None or len(previous) != 1
                or prior["memory_id"] != memory["id"]
                or prior["source_event_id"] != memory["source_event_id"]
                or previous[0]["id"] != prior["policy_id"]
                or previous[0]["selected_action"] != prior["selected_tendency"]
                or sha256(historical.question.encode()).hexdigest() != prior["question_sha256"]
                or json.loads(previous[0]["state_pressure_json"]).get("decision_text_sha256") != prior["question_sha256"]):
            raise PermissionError("Historical reflection provenance differs")
        return prior
    packet_key = key + ":decision-context-v2"
    packet_raw = store.meta(packet_key)
    if packet_raw:
        packet = json.loads(packet_raw)
        saved = {r["reading_id"]: r for r in packet["interpretations"]}
        if set(saved) != {r.id for r in readings}:
            raise PermissionError("Interpretation set changed during reflection recovery")
        # State changes after deliberation do not retroactively change its input.
        for r in readings:
            row = saved[r.id]
            if (row["source_event_id"] != r.source_event_id or row["source_kind"] != r.source_kind
                    or row["source_work"] != r.source_work or row["tradition_id"] != r.tradition_id
                    or row["proposition"] != r.proposition or row["question"] != r.question
                    or row["method_trace"] != r.method_trace or row["claim_scope"] != r.claim_scope):
                raise PermissionError("Interpretation provenance changed during reflection recovery")
        query = " ".join(r["first_person"] for r in packet["interpretations"] if r["considered"])
        if sha256(query.encode()).hexdigest() != packet["query_sha256"]:
            raise PermissionError("Stored interpretation context does not match its digest")
    else:
        if previous:
            raise PermissionError("Historical decision without a recoverable reflection receipt")
        query, interpretations = compile_readings(readings)
        if not query:
            return None
        packet = {"query_sha256": sha256(query.encode()).hexdigest(),
                  "interpretations": interpretations}
        with store.transaction() as db:
            store.set_meta(packet_key, json.dumps(packet, sort_keys=True), db)
            store.bump_state_version(db)
    query_digest = packet["query_sha256"]
    if previous:
        policy_id = previous[0]["id"]
        tendency = previous[0]["selected_action"]
        if json.loads(previous[0]["state_pressure_json"]).get("decision_text_sha256") != query_digest:
            raise PermissionError("Prior reflection has different interpretation provenance")
    else:
        decision = brain.think(trigger, decision_text=query)
        policy_id = decision["policy_decision_id"]
        tendency = decision["selected_action"]
    with closing(store.connect()) as db:
        thoughts = db.execute(
            "SELECT id,source_record_ids_json FROM thoughts WHERE generated_by=? AND trigger=?",
            ("neural_policy:" + policy_id, trigger),
        ).fetchall()
    if len(thoughts) != 1:
        raise RuntimeError("Conclave questions lack original Noesis thought")
    result = {
        "schema": "pretorius.conclave-reading-reflection.v2",
        "goal_id": goal["id"], "memory_id": memory["id"],
        "source_event_id": memory["source_event_id"], "context_key": context,
        "reading_ids": [r["reading_id"] for r in packet["interpretations"] if r["considered"]],
        "interpretations": packet["interpretations"], "question_sha256": query_digest,
        "policy_id": policy_id, "thought_id": thoughts[0]["id"],
        "selected_tendency": tendency,
        "retrieved_record_ids": json.loads(thoughts[0]["source_record_ids_json"]),
        "lived_fact_created": False, "motor_authority": False,
        "host_selected_tradition_mapping": False,
    }
    if prior is not None:
        if prior != result:
            raise PermissionError("Existing reflection receipt differs from original cognition")
        return result
    considered = set(result["reading_ids"])
    for reading in readings:
        if reading.id in considered and reading.state == "generated":
            conclave.transition(reading.id, "considered",
                reason="Original Noesis deliberated on the joint source-bound interpretation set.")
    with store.transaction() as db:
        store.set_meta(key, json.dumps(result, sort_keys=True), db)
        store.bump_state_version(db)
    return result
