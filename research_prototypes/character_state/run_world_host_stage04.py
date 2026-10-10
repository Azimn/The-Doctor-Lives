"""Execute a real, deterministic world-state change before Pretorius memory admission.

All outcomes belong to a *separately persisted test-world SQLite ledger*.
This is a host-programmed engineering test, not independent game agency.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

from doctor_lives.cognition import PretoriusBrain

from .firsthand_gate import EventInquiry, evaluate_firsthand
from .world_host_ledger import WorldHostLedger, TransitionTicket
from .world_native_bridge import (
    admit_world_transition,check_host_admitted_recollection,
)


def drill() -> dict:
    # Controlled fixture secret, distinct from BrainStore; never included
    # in report, prompt, full world event log or subject renderer.
    secret=bytes.fromhex("15"*32)
    actions=[]
    with tempfile.TemporaryDirectory(prefix="stage04-world-ledger-") as td:
        root=Path(td)
        world=WorldHostLedger(root/"separate-world.sqlite3",secret=secret)
        brain=PretoriusBrain(root/"pretorius")
        initial_native_memories=len(brain.store.memories())
        initial_world=world.world()
        initial_brain=brain.store.digest()
        unauthorized=world.execute("pretorius","stop_clock",nonce="nonce-unauth-001")
        actions.append(("clock_unauthorized",unauthorized))
        if unauthorized.accepted or world.world()!=initial_world:
            raise AssertionError("unpermitted world transition")
        world.grant("pretorius","stop_clock")
        clock=world.execute("pretorius","stop_clock",nonce="nonce-clock-ok-001")
        actions.append(("clock_authorized",clock))
        if not clock.accepted or world.world()["state"]["clock"]!="stopped":
            raise AssertionError("permitted clock transition absent")
        nonce_replay=world.execute("pretorius","stop_clock",nonce="nonce-clock-ok-001")
        actions.append(("clock_replayed_nonce",nonce_replay))
        if nonce_replay.accepted or nonce_replay.reason!="replayed_nonce":
            raise AssertionError("nonce replay accepted")
        duplicate_action=world.execute(
            "pretorius","stop_clock",nonce="nonce-second-clock-002"
        )
        actions.append(("clock_already_stopped",duplicate_action))
        if duplicate_action.accepted or duplicate_action.reason!="preconditions_not_met":
            raise AssertionError("repeated state effect admitted")
        if initial_brain!=brain.store.digest():
            raise AssertionError("world operations unexpectedly wrote native memory")
        first=admit_world_transition(brain,world,clock.ticket)
        once=len(brain.store.memories())
        second=admit_world_transition(brain,world,clock.ticket)
        twice=len(brain.store.memories())
        clock_source=check_host_admitted_recollection(brain,world,clock.ticket)
        if first!=second or once!=twice or not clock_source["admitted"]:
            raise AssertionError("host/native bridge failed to preserve idempotence and recall")
        # Model's claims cannot open a sealed world object.
        world.grant("pretorius","inspect_notebook")
        denied_sealed=world.execute(
            "pretorius","inspect_notebook",nonce="nonce-sealed-inspection-001"
        )
        actions.append(("sealed_notebook_inspection",denied_sealed))
        if denied_sealed.accepted or denied_sealed.reason!="preconditions_not_met":
            raise AssertionError("sealed notebook treated as inspected")
        unknown=evaluate_firsthand(
            brain,EventInquiry("notebook_inspected"),
            tuple(m["id"] for m in brain.store.memories()),
            host_receipts=(),
        )
        if unknown.source_memory_count!=0:
            raise AssertionError("unsupported prior inspection claimed as lived")
        world.grant("pretorius","unseal_notebook")
        no_consent=world.execute(
            "pretorius","unseal_notebook",nonce="nonce-no-consent-001"
        )
        actions.append(("notebook_no_partner_consent",no_consent))
        if no_consent.accepted or no_consent.reason!="partner_consent_missing":
            raise AssertionError("unauthorized partner consent accepted")
        world.record_henry_consent()
        unseal=world.execute(
            "pretorius","unseal_notebook",nonce="nonce-consented-unseal-001"
        )
        actions.append(("notebook_unsealed_after_consent",unseal))
        if not unseal.accepted or world.world()["state"]["notebook"]!="open":
            raise AssertionError("authorized notebook transition absent")
        inspect=world.execute(
            "pretorius","inspect_notebook",nonce="nonce-open-inspect-001"
        )
        actions.append(("notebook_inspected_after_unseal",inspect))
        if not inspect.accepted or not world.verified(inspect.ticket):
            raise AssertionError("test-host did not witness actual open-notebook inspection")
        native_notebook=admit_world_transition(brain,world,inspect.ticket)
        inspected_source=check_host_admitted_recollection(brain,world,inspect.ticket)
        if not inspected_source["admitted"]:
            raise AssertionError("witnessed notebook inspection failed to establish source")
        # The host's persistent ledger is reloaded from disk with the secret
        # supplied outside the character brain, not reconstructed from prompt.
        restarted=WorldHostLedger(root/"separate-world.sqlite3",secret=secret)
        if (not restarted.audit_chain() or
            not restarted.verified(inspect.ticket) or
            restarted.get_import(inspect.ticket.event_id)!=world.get_import(inspect.ticket.event_id)):
            raise AssertionError("persistent world-ledger recovery failed")
        restart_replay=restarted.execute(
            "pretorius","inspect_notebook",nonce="nonce-open-inspect-001"
        )
        if restart_replay.accepted:
            raise AssertionError("world nonce replay succeeded after restart")
        source_before_revocation=check_host_admitted_recollection(
            brain,restarted,clock.ticket
        )
        restarted.revoke(clock.ticket.event_id,"research withdrawal of source authority")
        source_after_revocation=check_host_admitted_recollection(
            brain,restarted,clock.ticket
        )
        if not source_before_revocation["admitted"] or source_after_revocation["admitted"]:
            raise AssertionError("revocation failed to affect source authority")
        if len(brain.store.memories())!=initial_native_memories+2:
            raise AssertionError("silent addition/deletion of canon beyond two authorized fixtures")
        if not restarted.audit_chain():
            raise AssertionError("host event journal corrupt after revocation")
        final=restarted.world()
        if final["state"]!={"clock":"stopped","notebook":"open"} or final["sequence"]!=3:
            raise AssertionError("world outcome/sequence mismatch")
        return {
            "schema":"pretorius.world-host-ledger.stage04.measured.v01",
            "scope":"isolated deterministic separately stored simulated world",
            "world_initial":initial_world,
            "world_final":final,
            "host_signed_successful_events":final["sequence"],
            "native_lived_memories_admitted":len(brain.store.memories())-initial_native_memories,
            "native_idempotent_reimport":first==second and once==twice,
            "clock_lived_memory_admitted_before_revocation":source_before_revocation["admitted"],
            "clock_lived_memory_denied_after_revocation":not source_after_revocation["admitted"],
            "open_notebook_inspection_attested":inspected_source["admitted"],
            "unwitnessed_sealed_inspection_abstained":unknown.source_memory_count==0,
            "cross_restart_nonce_replay_rejected":not restart_replay.accepted,
            "world_ledger_audit_pass":restarted.audit_chain(),
            "denied_attempts":sum(not a.accepted for _,a in actions),
            "successful_attempts":sum(a.accepted for _,a in actions),
            "attempts":[{"label":label,"accepted":a.accepted,
                         "reason":a.reason,
                         "world_changed":a.world_changed}
                        for label,a in actions],
            "reconstructed_pretorius_persona_modified":False,
            "independently_implemented_world_server":False,
            "agent_autonomously_selected_actions":False,
            "generative_language_model_calls":0,
            "real_human_henry_consent":False,
            "externally_validated_persona_continuity":False,
            "production_promotion":"HOLD",
        }


def main() -> None:
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=drill()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in (
        "host_signed_successful_events","native_lived_memories_admitted",
        "native_idempotent_reimport","clock_lived_memory_denied_after_revocation",
        "cross_restart_nonce_replay_rejected","denied_attempts",
        "world_ledger_audit_pass",
    )},sort_keys=True))


if __name__=="__main__":
    main()
