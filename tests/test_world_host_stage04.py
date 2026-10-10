"""Stage 04 deterministic host-world / native memory source-boundary tests."""
from dataclasses import replace
from pathlib import Path
import json
import sqlite3
import tempfile
import unittest

from doctor_lives.cognition import PretoriusBrain
from research_prototypes.character_state.world_host_ledger import (
    WorldHostLedger,fingerprint,
)
from research_prototypes.character_state.world_native_bridge import (
    admit_world_transition,check_host_admitted_recollection,
)
from research_prototypes.character_state.run_world_host_stage04 import drill


class WorldStage04Tests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.path=Path(self.t.name)
        self.secret=b"S"*32
        self.host=WorldHostLedger(self.path/"host-world.sqlite3",secret=self.secret)
        self.brain=PretoriusBrain(self.path/"pretorius")
        self.initial_native=self.brain.store.digest()

    def _clock(self):
        self.host.grant("pretorius","stop_clock")
        result=self.host.execute("pretorius","stop_clock",nonce="clock-test-nonce-1")
        self.assertTrue(result.accepted)
        return result.ticket

    def test_all_world_state_transitions_and_native_lived_fixture(self):
        result=drill()
        self.assertEqual(result["world_final"]["state"],
                         {"clock":"stopped","notebook":"open"})
        self.assertEqual(result["world_final"]["sequence"],3)
        self.assertEqual(result["host_signed_successful_events"],3)
        self.assertEqual(result["native_lived_memories_admitted"],2)
        self.assertTrue(result["native_idempotent_reimport"])
        self.assertTrue(result["clock_lived_memory_denied_after_revocation"])
        self.assertTrue(result["unwitnessed_sealed_inspection_abstained"])
        self.assertTrue(result["cross_restart_nonce_replay_rejected"])
        self.assertFalse(result["agent_autonomously_selected_actions"])

    def test_unauthorized_partner_consent_and_sealed_state_leave_no_receipt(self):
        before=self.host.world()
        for actor,action,nonce in (
            ("pretorius","stop_clock","no-grant-actor-1"),
            ("calibos","stop_clock","wrong-subject-actor-1"),
            ("pretorius","inspect_notebook","notebook-sealed-1"),
        ):
            outcome=self.host.execute(actor,action,nonce=nonce)
            self.assertFalse(outcome.accepted)
            self.assertIsNone(outcome.ticket)
        self.host.grant("pretorius","unseal_notebook")
        no_henry=self.host.execute(
            "pretorius","unseal_notebook",nonce="no-henry-consent"
        )
        self.assertFalse(no_henry.accepted)
        self.assertEqual(no_henry.reason,"partner_consent_missing")
        self.assertEqual(self.host.world(),before)
        self.assertEqual(self.brain.store.digest(),self.initial_native)

    def test_signatures_reject_altered_claims_and_fake_event_keys(self):
        ticket=self._clock()
        self.assertTrue(self.host.verified(ticket))
        changed=(
            replace(ticket,event_key="notebook_inspected"),
            replace(ticket,mac_sha256="0"*64),
            replace(ticket,subject_id="calibos"),
            replace(ticket,actor="calibos"),
            replace(ticket,session_id="other-session"),
            replace(ticket,sequence=9),
            replace(ticket,after_state_digest="0"*64),
        )
        self.assertTrue(all(not self.host.verified(x) for x in changed))
        with self.assertRaises(ValueError):
            admit_world_transition(self.brain,self.host,changed[0])
        self.assertEqual(self.brain.store.digest(),self.initial_native)

    def test_cross_restart_nonce_replay_and_native_idempotence(self):
        ticket=self._clock()
        a=admit_world_transition(self.brain,self.host,ticket)
        old_count=len(self.brain.store.memories())
        rebooted=WorldHostLedger(
            self.path/"host-world.sqlite3",secret=self.secret,
        )
        self.assertTrue(rebooted.audit_chain())
        replay=rebooted.execute(
            "pretorius","stop_clock",nonce="clock-test-nonce-1"
        )
        self.assertEqual(replay.reason,"replayed_nonce")
        b=admit_world_transition(self.brain,rebooted,ticket)
        self.assertEqual(a,b)
        self.assertEqual(old_count,len(self.brain.store.memories()))
        self.assertTrue(check_host_admitted_recollection(
            self.brain,rebooted,ticket
        )["admitted"])

    def test_host_revocation_does_not_erase_natively_lived_history(self):
        ticket=self._clock()
        a=admit_world_transition(self.brain,self.host,ticket)
        count=len(self.brain.store.memories())
        self.host.revoke(ticket.event_id,"withdrawn experimental admission")
        self.assertFalse(self.host.verified(ticket))
        self.assertFalse(check_host_admitted_recollection(
            self.brain,self.host,ticket
        )["admitted"])
        with self.assertRaises(ValueError):
            admit_world_transition(self.brain,self.host,ticket)
        self.assertEqual(count,len(self.brain.store.memories()))
        self.assertIsNotNone(self.brain.store.get_memory(a["native_memory_id"]))

    def test_cross_subject_and_cross_session_reconstruction_fails_closed(self):
        ticket=self._clock()
        for kwargs in (
            {"subject_id":"calibos"},
            {"session_id":"session-pretending-to-be-original"},
            {"issuer":"other-issuer"},
            {"secret":b"D"*32},
        ):
            options=dict(secret=self.secret)
            options.update(kwargs)
            another=WorldHostLedger(self.path/"host-world.sqlite3",**options)
            self.assertFalse(another.verified(ticket))

    def test_tampered_host_world_state_breaks_signed_chain(self):
        ticket=self._clock()
        with self.host.connect() as conn:
            conn.execute("UPDATE world_state SET state_json=? WHERE id=1",
                         (json.dumps({"clock":"running","notebook":"open"}),))
            conn.commit()
        self.assertFalse(self.host.audit_chain())
        self.assertFalse(self.host.verified(ticket))
        self.assertEqual(
            self.host.execute("pretorius","inspect_notebook",
                              nonce="bad-chain-action-1").reason,
            "corrupt_host_ledger",
        )

    def test_tampered_native_payload_breaks_existing_source_admission(self):
        ticket=self._clock()
        admitted=admit_world_transition(self.brain,self.host,ticket)
        with self.brain.store.transaction() as db:
            db.execute("UPDATE events SET payload_json=? WHERE id=?",
                       (json.dumps({"event_key":"clock_stopped",
                                    "host_event_id":"forged"}), admitted["native_event_id"]))
        verdict=check_host_admitted_recollection(self.brain,self.host,ticket)
        self.assertFalse(verdict["admitted"])
        with self.assertRaises(ValueError):
            admit_world_transition(self.brain,self.host,ticket)

    def test_missing_host_import_marker_fails_closed_without_duplicate_memory(self):
        ticket=self._clock()
        original=admit_world_transition(self.brain,self.host,ticket)
        before=len(self.brain.store.memories())
        with self.host.connect() as db:
            db.execute("DELETE FROM native_imports WHERE event_id=?",(ticket.event_id,))
            db.commit()
        with self.assertRaisesRegex(ValueError,"unreconciled native event"):
            admit_world_transition(self.brain,self.host,ticket)
        self.assertEqual(before,len(self.brain.store.memories()))
        self.assertIsNotNone(self.brain.store.get_memory(original["native_memory_id"]))


if __name__=="__main__":
    unittest.main()
