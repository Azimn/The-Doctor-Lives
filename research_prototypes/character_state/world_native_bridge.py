"""Native Pretorius import of a genuinely executed *test-world* transition.

The host-world ledger is a separate, persistent database whose state changes
are authorized and signed before Pretorius receives a source event. This
adapter is research-only. Subjective P5 source monitoring is not overridden.
"""
from __future__ import annotations

import json
from doctor_lives.cognition import PretoriusBrain

from .firsthand_gate import _hash, EventInquiry, evaluate_firsthand
from .world_host_ledger import WorldHostLedger, TransitionTicket


_NARRATIVE={
    "stop_clock":"I observed the laboratory clock stop.",
    "unseal_notebook":"I opened the sealed notebook after Henry's consent was recorded.",
    "inspect_notebook":"I inspected the open notebook, without learning what its contents proved.",
}


def native_event_digest(brain:PretoriusBrain,native_event_id:str) -> str:
    with brain.store.connect() as db:
        row=db.execute(
            "SELECT id,kind,source,evidence_class,external,confidence,payload_json "
            "FROM events WHERE id=?",(native_event_id,),
        ).fetchone()
    if row is None:
        raise ValueError("native event record absent")
    record=dict(row)
    payload=json.loads(record.pop("payload_json"))
    return _hash({"event":record,"payload":payload})


def _verify_native_binding(
    brain:PretoriusBrain,host:WorldHostLedger,ticket:TransitionTicket,
    imported:dict,
) -> None:
    native_event_id=imported["native_event_id"]
    native_memory_id=imported["memory_id"]
    native_row=brain.store.get_memory(native_memory_id)
    if native_row is None or (
        native_row["source_event_id"] != native_event_id or
        native_row["evidence_class"] != "lived_runtime_memory" or
        native_row["source"] != "world_host_verified"
    ):
        raise ValueError("imported memory/source no longer matches host ledger")
    with brain.store.connect() as db:
        row=db.execute("SELECT payload_json FROM events WHERE id=?",
                       (native_event_id,)).fetchone()
    if row is None:
        raise ValueError("native source event missing")
    payload=json.loads(row["payload_json"])
    if (payload.get("host_event_id") != ticket.event_id or
        payload.get("event_key") != ticket.event_key or
        payload.get("host_transition_mac") != ticket.mac_sha256):
        raise ValueError("native host provenance binding changed")
    if native_event_digest(brain,native_event_id)!=imported["native_event_digest"]:
        raise ValueError("native event digest drift after import")


def admit_world_transition(
    brain:PretoriusBrain,host:WorldHostLedger,ticket:TransitionTicket,
) -> dict:
    """Idempotent import only from a verified successful host ledger transition.

    A lost host import marker after a native commit is caught as a conflicting
    trace rather than causing a second autographic memory. Recovery of that
    crash gap requires explicit host audit and is not silently automated.
    """
    if not isinstance(brain,PretoriusBrain) or not isinstance(host,WorldHostLedger):
        raise TypeError("requires native PretoriusBrain and host authority")
    if not host.verified(ticket) or ticket.actor!="pretorius" or (
        ticket.subject_id!="pretorius"
    ):
        raise ValueError("host event not admitted to subject")
    imported=host.get_import(ticket.event_id)
    if imported is None:
        # Fail closed on a native event previously written but not committed
        # to host delivery journal (e.g., crash mid-bridge). No double memory.
        with brain.store.connect() as db:
            prior=db.execute(
                "SELECT id,payload_json FROM events "
                "WHERE kind='witnessed_world_event' AND source='world_host_verified'"
            ).fetchall()
        for row in prior:
            if json.loads(row["payload_json"]).get("host_event_id")==ticket.event_id:
                raise ValueError("unreconciled native event conflicts with host import journal")
        with brain.store.transaction() as db:
            tick=brain.store.advance_tick(db)
            native_id=brain.store.event(
                db,tick,"witnessed_world_event","world_host_verified",
                {
                    "event_key":ticket.event_key,
                    "host_event_id":ticket.event_id,
                    "host_transition_mac":ticket.mac_sha256,
                    "world_before_hash":ticket.prior_state_digest,
                    "world_after_hash":ticket.after_state_digest,
                    "actor":ticket.actor,"action":ticket.action,
                    "target":ticket.target,
                    "sequence":ticket.sequence,
                },
                "lived_runtime_memory",False,1.0,
            )
            memory_id=brain.store.add_memory(
                db,tick,_NARRATIVE[ticket.action],
                "world_host_verified","world_event",
                "lived_runtime_memory",False,1.0,False,.8,
                ("host","lived","world_transition"),
                source_event_id=native_id,
                classification={
                    "autobiographical_class":"lived_runtime_memory",
                    "event_subtype":"world_event","canon_rank":None,
                    "continuity":"lived_runtime",
                    "material_category":"autobiography",
                    "wording":"quoted",
                    "classification_reasoning":{
                        "decision":"test-host state transition verified before memory import"
                    },
                    "classifier":"isolated_world_host_stage04",
                },
            )
        digest=native_event_digest(brain,native_id)
        host.remember_import(ticket.event_id,native_id,memory_id,digest)
        imported=host.get_import(ticket.event_id)
    _verify_native_binding(brain,host,ticket,imported)
    return {
        "host_event_id":ticket.event_id,
        "native_event_id":imported["native_event_id"],
        "native_memory_id":imported["memory_id"],
        "native_event_digest":imported["native_event_digest"],
    }


def check_host_admitted_recollection(
    brain:PretoriusBrain,host:WorldHostLedger,ticket:TransitionTicket,
) -> dict:
    """Read-only revalidation uses persistent host journal and native records."""
    if not host.verified(ticket):
        return {"admitted":False,"reason":"source_revoked_or_unverified"}
    imported=host.get_import(ticket.event_id)
    if imported is None:
        return {"admitted":False,"reason":"not_admitted_to_native_memory"}
    try:
        _verify_native_binding(brain,host,ticket,imported)
        verifier,receipt=host.signed_native_receipt(
            ticket,native_event_id=imported["native_event_id"],
            native_digest=imported["native_event_digest"],
        )
        signed=verifier.verify(receipt)
        if signed is None:
            return {"admitted":False,"reason":"native_receipt_invalid"}
        result=evaluate_firsthand(
            brain,EventInquiry(ticket.event_key),
            (imported["memory_id"],),host_receipts=(signed,),
        )
        return {
            "admitted":result.source_memory_count>0,
            "reason":"trusted_world_and_native_lived_evidence"
              if result.source_memory_count>0 else "native_source_rejected",
        }
    except (ValueError,KeyError):
        return {"admitted":False,"reason":"source_digest_or_memory_mismatch"}
