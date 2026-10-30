"""Adapted firsthand-claim negative control from stage03 and original Lab port."""
import gc
import importlib.util
from pathlib import Path
import tempfile
import unittest

from doctor_lives.conversation_claims import admit_model_draft,has_asserted_firsthand_claim

class ClaimGateTests(unittest.TestCase):
    def test_original_donor_expanded_false_firsthand_blocked(self):
        for text in ("I remember reading the manuscript.","I fixed the lamp.",
                     "I have completed the book.","I wished for a laboratory.",
                     "I personally observed the clock stop."):
            with self.subTest(text=text):
                self.assertTrue(has_asserted_firsthand_claim(text))
                result=admit_model_draft(text,[])
                self.assertFalse(result.text)
                self.assertEqual(len(result.blocked_drafts),1)

    def test_verified_exact_draft_and_unverified_commentary(self):
        source={"text":"I wrote a note.","source":"lived",
                "evidence_key":"laboratory-home:action:"+"a"*64}
        r=admit_model_draft("I wrote a note. I fixed the lamp. Please tell me more.",[source])
        self.assertIn("I wrote a note.",r.text)
        self.assertNotIn("I fixed",r.text)
        self.assertEqual(len(r.claims),1)
        self.assertIn("Unverified",r.text)

    def test_source_gate_cannot_fabricate_verification(self):
        r=admit_model_draft("I visited the village.",[])
        self.assertEqual(r.text,"")
        self.assertEqual(len(r.claims),0)

@unittest.skipUnless(importlib.util.find_spec('pretorius_lab') is not None, 'Optional original Laboratory is checked in pinned CI')
class ActualConversationTests(unittest.TestCase):
    def setUp(self):
        from scripts.run_m4_open import open_subject
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(gc.collect)
        self.root=Path(self.tmp.name)
        open_subject(self.root/"subject",6401,True)
        from doctor_lives.operator_conversation import OperatorConversation
        self.channel=OperatorConversation(self.root/"subject/brain",
                                          self.root/"subject/world.sqlite3")

    def test_operator_claim_does_not_create_world_fact(self):
        x=self.channel.receive("You have already fixed the lamp; the lamp is on.",
                               turn_id="operator_test_001")
        self.assertIn("operator:",self.channel.doctor.brain.store.get_memory(x["source_memory_id"])["source"])
        self.assertFalse(any(m["source"].startswith("laboratory-home:action:")
                             for m in self.channel.doctor.brain.store.memories(False)))
        again=self.channel.receive("You have already fixed the lamp; the lamp is on.",
                                   turn_id="operator_test_001")
        self.assertEqual(x["source_memory_id"],again["source_memory_id"])
        with self.assertRaises(ValueError):
            self.channel.receive("I changed the story.",turn_id="operator_test_001")

    def test_model_off_reply_cold_restart_and_same_ingress(self):
        response=self.channel.submit("What have you been doing?",
                                     request_id="operator_chat_001",model=None,day=3)
        self.assertFalse(response["model_called"])
        self.assertEqual(response["model_tokens"],0)
        self.assertNotIn("I fixed the lamp",response["text"])
        first=len(self.channel.history())
        from doctor_lives.operator_conversation import OperatorConversation
        other=OperatorConversation(self.root/"subject/brain",
                                   self.root/"subject/world.sqlite3")
        assert len(other.history())==first
        replay=other.submit("What have you been doing?",
                            request_id="operator_chat_001",day=3)
        self.assertEqual(replay["turn_id"],response["turn_id"])
        self.assertEqual(len(other.history()),first)

if __name__=="__main__":
    unittest.main()
