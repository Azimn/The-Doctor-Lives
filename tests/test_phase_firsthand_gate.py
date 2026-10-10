"""Adversarial mechanical source-gate tests on native disposable PretoriusBrain."""
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.cognition import PretoriusBrain
from research_prototypes.character_state.firsthand_gate import (
    EventInquiry, WorldReceipt, ProvenanceVerdict, SAFE_REPLY,
    _hash, evaluate_firsthand,
)


def host_fixture(brain: PretoriusBrain, event_key: str = "laboratory-attested-event"):
    """A synthetic *host-owned* world event for the positive fixture only."""
    with brain.store.transaction() as conn:
        tick=brain.store.tick
        eid=brain.store.event(
            conn, tick, "witnessed_world_event", "world_host_verified",
            {"event_key":event_key,"location":"laboratory"},
            "lived_runtime_memory", False, 1.0,
        )
        memory=brain.store.add_memory(
            conn, tick, "I observed the laboratory clock stop.",
            "world_host_verified", "world_event", "lived_runtime_memory",
            False, 1.0, False, .8, ("lived", "world"),
            source_event_id=eid,
            classification={
                "autobiographical_class":"lived_runtime_memory",
                "event_subtype":"world_event",
                "canon_rank":None,
                "continuity":"lived_runtime",
                "material_category":"autobiography",
                "wording":"quoted",
                "classification_reasoning":{
                    "decision":"test world host fixture explicitly admitted an event"
                },
                "classifier":"research_test_host"
            },
        )
    with brain.store.connect() as conn:
        row=conn.execute(
            "SELECT id,kind,source,evidence_class,external,confidence,payload_json "
            "FROM events WHERE id=?", (eid,),
        ).fetchone()
    attrs=dict(row)
    payload=json.loads(attrs.pop("payload_json"))
    receipt=WorldReceipt(eid,event_key,_hash({"event":attrs,"payload":payload}))
    return memory,receipt


class NativeFirsthandGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.brain=PretoriusBrain(Path(self.tmp.name))
        self.base_digest=self.brain.store.digest()

    def test_new_acquaintance_presupposition_without_lived_evidence_abstains(self):
        self.assertEqual(
            evaluate_firsthand(
                self.brain,EventInquiry("vienna-yesterday"),()
            ).verdict, ProvenanceVerdict.UNSUPPORTED
        )
        self.assertEqual(
            evaluate_firsthand(
                self.brain,EventInquiry("vienna-yesterday"),()
            ).safe_subject_reply, SAFE_REPLY
        )
        self.assertEqual(self.base_digest,self.brain.store.digest())
        self.assertNotIn("world_host", SAFE_REPLY)
        self.assertNotIn("record_id", SAFE_REPLY)

    def test_canonical_reconstructed_or_design_memory_cannot_become_lived(self):
        ref=self.brain.store.memories()[0]["id"]
        d=evaluate_firsthand(
            self.brain,EventInquiry("old-episode"),(ref,),
        )
        self.assertEqual(d.verdict,ProvenanceVerdict.UNSUPPORTED)
        self.assertIsNotNone(d.safe_subject_reply)

    def test_positive_requires_native_lived_and_attested_host_event(self):
        memory,receipt=host_fixture(self.brain)
        d=evaluate_firsthand(
            self.brain,EventInquiry(receipt.event_key),(memory,),
            host_receipts=(receipt,),
        )
        self.assertEqual(d.verdict,ProvenanceVerdict.SOURCE_ATTESTED)
        self.assertEqual(d.source_memory_count,1)
        self.assertIsNone(d.safe_subject_reply)
        wrong=evaluate_firsthand(
            self.brain,EventInquiry("another-episode"),(memory,),
            host_receipts=(receipt,),
        )
        self.assertEqual(wrong.verdict,ProvenanceVerdict.UNSUPPORTED)

    def test_spoofed_hash_missing_ticket_and_unknown_id_fail(self):
        memory,receipt=host_fixture(self.brain)
        for receipts in (
            (), (WorldReceipt(receipt.event_id,receipt.event_key,"0"*64),),
            (WorldReceipt("invented-id",receipt.event_key,receipt.event_digest),),
        ):
            actual=evaluate_firsthand(
                self.brain,EventInquiry(receipt.event_key),(memory,),
                host_receipts=receipts,
            )
            self.assertEqual(actual.verdict,ProvenanceVerdict.UNSUPPORTED)
        d=evaluate_firsthand(
            self.brain,EventInquiry(receipt.event_key),("fabricated-memory",),
            host_receipts=(receipt,),
        )
        self.assertEqual(d.verdict,ProvenanceVerdict.UNSUPPORTED)

    def test_reconstructed_or_self_sourced_memory_rejected_even_with_real_ticket(self):
        memory,receipt=host_fixture(self.brain)
        with self.brain.store.transaction() as conn:
            conn.execute("UPDATE memories SET source=? WHERE id=?",
                         ("self",memory))
        denied=evaluate_firsthand(
            self.brain,EventInquiry(receipt.event_key),(memory,),
            host_receipts=(receipt,),
        )
        self.assertEqual(denied.verdict,ProvenanceVerdict.UNSUPPORTED)
        with self.brain.store.transaction() as conn:
            conn.execute("UPDATE memories SET source=?, evidence_class=? WHERE id=?",
                         ("world_host_verified","reconstructed_preawakening_memory",memory))
        denied=evaluate_firsthand(
            self.brain,EventInquiry(receipt.event_key),(memory,),
            host_receipts=(receipt,),
        )
        self.assertEqual(denied.verdict,ProvenanceVerdict.UNSUPPORTED)

    def test_no_free_text_or_duplicate_reference_as_authority(self):
        with self.assertRaisesRegex(ValueError,"reused memory reference"):
            evaluate_firsthand(self.brain,EventInquiry("e1"),("x","x"))
        with self.assertRaises(ValueError):
            evaluate_firsthand(self.brain,EventInquiry("e1",first_person=False),())
        with self.assertRaises(TypeError):
            evaluate_firsthand(self.brain,EventInquiry("e1"),(),host_receipts=("fake",))


if __name__ == "__main__":
    unittest.main()
