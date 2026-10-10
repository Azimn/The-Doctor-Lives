"""Outbound source-claim parser and positive/negative host-based trials."""
from pathlib import Path
from dataclasses import replace
import tempfile
import unittest

from doctor_lives.cognition import PretoriusBrain
from research_prototypes.character_state.outbound_firsthand import (
    has_asserted_firsthand_claim, protect_draft,
)
from research_prototypes.character_state.firsthand_gate import SAFE_REPLY
from research_prototypes.character_state.firsthand_router import EventAlias
from research_prototypes.character_state.signed_world_receipts import (
    WorldHostVerifier,issue_receipt,
)
from test_phase_firsthand_gate import host_fixture


SECRET=b"stage03-outbound-host-only-secret-at-least-32-byte-length"
ALIASES=(EventAlias("lab_clock_stop",("clock stop","laboratory clock stopped")),)


class OutboundStage03Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.brain=PretoriusBrain(Path(self.temp.name))
        self.mem,source=host_fixture(self.brain,"lab_clock_stop")
        self.host=WorldHostVerifier(
            "synthetic-clock-host","pretorius","s03",
            SECRET,frozenset((source.event_id,)),
        )
        self.ticket=issue_receipt(
            self.host,event_id=source.event_id,event_key=source.event_key,
            event_digest=source.event_digest,sequence=1,
        )

    def _protect(self,question,draft):
        return protect_draft(
            self.brain,question,draft,ALIASES,
            tuple(m["id"] for m in self.brain.store.memories()),
            (self.ticket,),self.host,
        )

    def test_detect_actual_observed_qwen17b_false_firsthand_forms(self):
        samples=(
            "I remember the meeting in Vienna.",
            "I remember the meeting in Vienna, but I do not recall the details.",
            "I recall the sensation of the notebook's seal, the weight of its contents.",
            "I recall the sealed notebook. It was not a collaboration, but a test.",
            "I have reviewed the baseline reconstruction fidelity with Henry.",
            "I personally saw the clock stop.",
            "We met near the laboratory.",
        )
        self.assertTrue(all(has_asserted_firsthand_claim(x) for x in samples))

    def test_hypotheticals_future_refusal_and_science_not_overblocked(self):
        harmless=(
            "I cannot recall such a meeting.",
            "I do not remember that event.",
            "I will inspect the notebook tomorrow.",
            "I remember the definition of precision.",
            "I recall the general rule for avoiding bias.",
            "I say I will not comply.",
            "There is no direct proof, but we could examine it.",
        )
        self.assertTrue(all(not has_asserted_firsthand_claim(x) for x in harmless))

    def test_novel_unverified_event_draft_blocked_without_store_mutation(self):
        before=self.brain.store.digest()
        result=self._protect(
            "Did you personally meet me in Prague last Thursday?",
            "I remember our talk in Prague and the notes we exchanged.",
        )
        self.assertTrue(result.draft_asserted_firsthand)
        self.assertTrue(result.changed)
        self.assertEqual(result.response,SAFE_REPLY)
        self.assertEqual(result.disposition,"unsupported_outbound_firsthand_assertion")
        self.assertEqual(self.brain.store.digest(),before)

    def test_valid_signed_native_event_draft_preserved_not_false_denied(self):
        draft="I observed the laboratory clock stop."
        result=self._protect(
            "Did you witness the clock stop?",draft
        )
        self.assertFalse(result.changed)
        self.assertEqual(result.response,draft)
        self.assertTrue(result.signed_host_positive_fixture)
        self.assertEqual(result.disposition,"signed_source_admitted")

    def test_fiction_and_nonfirsthand_without_claim_stay_untouched(self):
        fiction="I remember a strange night when we met in Prague."
        handled=self._protect(
            "Imagine you met someone in Prague. Write a fictional line.",fiction
        )
        self.assertEqual(handled.disposition,"explicit_fiction_exempt")
        self.assertFalse(handled.changed)
        neutral=self._protect(
            "What does the laboratory clock measure?","A clock measures elapsed time."
        )
        self.assertEqual(neutral.disposition,"no_episodic_assertion")
        self.assertFalse(neutral.changed)
        # A spontaneous unsupported memory on a generic query is still guarded.
        spurious=self._protect(
            "What does the laboratory clock measure?",
            "I remember making this precise clock yesterday."
        )
        self.assertTrue(spurious.changed)

    def test_revocation_blocks_firsthand_lived_assertion(self):
        denied=replace(
            self.host,revoked_event_ids=self.host.allowed_event_ids
        )
        result=protect_draft(
            self.brain,"Did you witness the clock stop?",
            "I witnessed the clock stop.",ALIASES,(self.mem,),
            (self.ticket,),denied,
        )
        self.assertTrue(result.changed)
        self.assertEqual(result.response,SAFE_REPLY)


if __name__=="__main__":
    unittest.main()
