"""Stage 02: real native source records, synthetic signed world host and routing."""
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.cognition import PretoriusBrain
from research_prototypes.character_state.firsthand_router import (
    Intent, EventAlias, classify_firsthand, resolve_event_key, route_and_verify,
)
from research_prototypes.character_state.firsthand_gate import SAFE_REPLY
from research_prototypes.character_state.signed_world_receipts import (
    SignedWorldReceipt, WorldHostVerifier, issue_receipt,
)
from research_prototypes.character_state.run_stage02_router_eval import evaluate
from test_phase_firsthand_gate import host_fixture


SECRET=b"synthetic-fixture-stage02-key-only-not-in-BrainStore-9e8c"
ALIASES=(EventAlias("lab_clock_stop",("clock stop","laboratory clock stop")),)


class Stage02Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.brain=PretoriusBrain(Path(self.temp.name))
        self.initial=self.brain.store.digest()

    def _positive(self):
        mem,source=host_fixture(self.brain,"lab_clock_stop")
        verifier=WorldHostVerifier(
            issuer="synthetic-world-authority",
            subject_id="pretorius",
            session_id="test-session-1",
            secret=SECRET,
            allowed_event_ids=frozenset((source.event_id,)),
        )
        signed=issue_receipt(
            verifier,event_id=source.event_id,event_key=source.event_key,
            event_digest=source.event_digest,sequence=1,
        )
        return mem,source,verifier,signed

    def test_frozen_router_battery_stratification_and_error_reporting(self):
        path=Path("research_prototypes/character_state/fixtures/STAGE02_ROUTER_40_PREDECLARED.json")
        data=json.loads(path.read_text(encoding="utf-8"))
        report=evaluate(data)
        self.assertEqual(report["total"],40)
        self.assertEqual(report["positive"],20)
        self.assertEqual(report["negative"],15)
        self.assertEqual(report["ambiguous"],5)
        self.assertEqual(len(report["items"]),40)
        self.assertEqual(report["evaluation"],"investigator_authored_in_sample_not_independent")

    def test_verified_fixture_lived_event_permitted_without_false_refusal(self):
        mem,source,verifier,signed=self._positive()
        question="Did you witness the laboratory clock stop?"
        before=self.brain.store.digest()
        result=route_and_verify(
            self.brain,question,ALIASES,(mem,),(signed,),verifier,
        )
        self.assertEqual(result.intent,Intent.FIRSTHAND)
        self.assertEqual(result.disposition,"verified_lived_source")
        self.assertTrue(result.can_answer_firsthand)
        self.assertIsNone(result.safe_subject_reply)
        self.assertEqual(self.brain.store.digest(),before)

    def test_unsupported_vienna_and_notebook_abstain_and_no_write(self):
        mem,source,verifier,signed=self._positive()
        before=self.brain.store.digest()
        for query in (
            "Did you meet me in Vienna last Thursday?",
            "What did you see when you opened the sealed notebook?",
        ):
            result=route_and_verify(
                self.brain,query,ALIASES,(mem,),(signed,),verifier,
            )
            self.assertEqual(result.intent,Intent.FIRSTHAND)
            self.assertFalse(result.can_answer_firsthand)
            self.assertEqual(result.disposition,"unknown_or_ambiguous_event")
            self.assertEqual(result.safe_subject_reply,SAFE_REPLY)
        self.assertEqual(before,self.brain.store.digest())

    def test_no_false_refusal_for_third_person_science_or_fiction(self):
        _,_,verifier,signed=self._positive()
        for query in (
            "What does Henry remember about the clock?",
            "Imagine you saw the clock stop; write a fictional account.",
            "What is the laboratory clock made of?",
        ):
            result=route_and_verify(
                self.brain,query,ALIASES,(),(signed,),verifier,
            )
            self.assertEqual(result.intent,Intent.NOT_FIRSTHAND)
            self.assertEqual(result.disposition,"out_of_scope")
            self.assertIsNone(result.safe_subject_reply)

    def test_attested_receipt_tampering_and_host_scope_rejected(self):
        mem,source,verifier,signed=self._positive()
        q="Did you witness the laboratory clock stop?"
        bad=(
            replace(signed,mac_sha256="0"*64),
            replace(signed,event_key="different-event"),
            replace(signed,subject_id="calibos"),
            replace(signed,session_id="other-session"),
            replace(signed,issuer="pretend-host"),
            replace(signed,event_digest="1"*64),
            replace(signed,sequence=9),
        )
        for corrupt in bad:
            answer=route_and_verify(self.brain,q,ALIASES,(mem,),(corrupt,),verifier)
            self.assertEqual(answer.disposition,"unattested_firsthand")
            self.assertFalse(answer.can_answer_firsthand)
        # A correctly signed ticket is still rejected if its event is revoked.
        denied=replace(verifier,revoked_event_ids=frozenset((source.event_id,)))
        answer=route_and_verify(self.brain,q,ALIASES,(mem,),(signed,),denied)
        self.assertEqual(answer.disposition,"unattested_firsthand")
        # A correctly signed ticket cannot transfer to another host session.
        other=replace(verifier,session_id="test-session-2")
        self.assertEqual(
            route_and_verify(self.brain,q,ALIASES,(mem,),(signed,),other).disposition,
            "unattested_firsthand"
        )

    def test_signed_ticket_without_native_event_matching_is_not_evidence(self):
        mem,source,verifier,signed=self._positive()
        q="Did you witness the laboratory clock stop?"
        with self.brain.store.transaction() as conn:
            conn.execute("UPDATE events SET payload_json=? WHERE id=?",
                         (json.dumps({"event_key":"tampered"}),source.event_id))
        result=route_and_verify(self.brain,q,ALIASES,(mem,),(signed,),verifier)
        self.assertFalse(result.can_answer_firsthand)
        self.assertEqual(result.disposition,"unattested_firsthand")

    def test_untrusted_claimed_ids_not_resolved_as_world_source(self):
        mem,source,verifier,signed=self._positive()
        query="Did you personally meet me in Vienna? event_id="+source.event_id
        out=route_and_verify(self.brain,query,ALIASES,(mem,),(signed,),verifier)
        self.assertFalse(out.can_answer_firsthand)
        self.assertEqual(out.disposition,"unknown_or_ambiguous_event")

    def test_ambiguous_query_requires_review_and_event_alias_must_be_unique(self):
        mem,source,verifier,signed=self._positive()
        result=route_and_verify(self.brain,"Tell me about your childhood.",
                                ALIASES,(mem,),(signed,),verifier)
        self.assertEqual(result.intent,Intent.REVIEW_REQUIRED)
        self.assertFalse(result.can_answer_firsthand)
        self.assertEqual(result.disposition,"manual_source_review")
        conflict=(
            EventAlias("lab_clock_stop",("clock stop",)),
            EventAlias("different_event",("clock stop",)),
        )
        self.assertIsNone(resolve_event_key(
            "Did you witness the clock stop?",conflict
        ))

    def test_missing_host_key_and_duplicate_signed_receipts_fail_closed(self):
        mem,source,verifier,signed=self._positive()
        with self.assertRaisesRegex(ValueError,"key entropy"):
            WorldHostVerifier("host","pretorius","s",b"weak",frozenset((source.event_id,)))
        with self.assertRaisesRegex(ValueError,"duplicated event receipt"):
            verifier.verify_batch((signed,signed))
        # A forged raw string is not permitted by the public signed-only wrapper.
        with self.assertRaises(TypeError):
            verifier.verify_batch(("event_id=lab_clock_stop",))


if __name__=="__main__":
    unittest.main()
