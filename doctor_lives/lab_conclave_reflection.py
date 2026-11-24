"""Connect real completed reading to existing Conclave and original Noesis.

A book completion is an opportunity for interpretation, not a host-supplied
subject biography or external world action. The original kernel generates
bounded rival hypotheses; one question enters original Noesis retrieval and
deliberation. All hypotheses remain separate from lived memories. No new
brain, language model, action planner or motor grant is introduced.
"""
from __future__ import annotations
from contextlib import closing
from hashlib import sha256
import json

from .conclave import Conclave, Stimulus
from .lab_endogenous_book_task import EndogenousBookPursuit
from .lab_six_organ_session import SixOrganLaboratoryCycle

PREFIX = "conclave:completed-reading:"
PREFERENCE = ("agrippan-wheel", "ficinian-temperament", "brunian-memory",
              "llullian-ars", "geomantic-shield")


def reflect_completed_reading(book: EndogenousBookPursuit) -> dict | None:
    """Use one authenticated book goal, and recover an already written thought.

    The selected tradition order is a disclosed engineering mapping. It is
    not proof of unconstrained preference or historically exact scholarship.
    Reflection uses the canonical brain's actual memory-ranking and policy
    function; a generated question cannot itself assert a new fact.
    """
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
    readings = conclave.interpret(Stimulus(
        memory["source_event_id"], "world_verified", context,
        memory["text"][:2000].strip(),
    ))
    if not readings:
        return None
    chosen = min(readings, key=lambda r: PREFERENCE.index(r.tradition_id))
    query = chosen.question
    query_digest = sha256(query.encode()).hexdigest()
    with closing(store.connect()) as db:
        previous = db.execute(
            "SELECT id,selected_action,state_pressure_json FROM policy_decisions "
            "WHERE trigger=? ORDER BY rowid", (trigger,),
        ).fetchall()
    if len(previous) > 1:
        raise RuntimeError("Duplicate original Conclave reflection")
    if previous:
        policy_id = previous[0]["id"]
        tendency = previous[0]["selected_action"]
        if json.loads(previous[0]["state_pressure_json"]).get("decision_text_sha256") != query_digest:
            raise PermissionError("Prior reflection has different question provenance")
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
        raise RuntimeError("Conclave question lacks original Noesis thought")
    result = {
        "schema": "pretorius.conclave-reading-reflection.v1",
        "goal_id": goal["id"], "memory_id": memory["id"],
        "source_event_id": memory["source_event_id"], "context_key": context,
        "reading_id": chosen.id, "question_sha256": query_digest,
        "policy_id": policy_id, "thought_id": thoughts[0]["id"],
        "selected_tendency": tendency,
        "retrieved_record_ids": json.loads(thoughts[0]["source_record_ids_json"]),
        "lived_fact_created": False, "motor_authority": False,
        "host_selected_tradition_mapping": True,
    }
    prior = store.meta(key)
    if prior is not None:
        if json.loads(prior) != result:
            raise PermissionError("Existing reflection receipt differs from original cognition")
        return result
    # A chosen question has actually been considered by canonical Noesis;
    # it is not automatically adopted, supported or made true.
    if chosen.state == "generated":
        conclave.transition(chosen.id, "considered",
                            reason="Original Noesis deliberated on the source-bound question.")
    with store.transaction() as db:
        store.set_meta(key, json.dumps(result, sort_keys=True), db)
        store.bump_state_version(db)
    return result
