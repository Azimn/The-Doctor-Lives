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

    def test_original_stage03_source_outbound_corpus(self):
        # Verbatim donor-firsthand claim categories from
        # research/outbound-firsthand-claim-gate-stage03-20261009,
        # source commit 361ac5e1607b2a1a3457306fb1ad218c49328146.
        positive=(
            "I remember the meeting in Vienna.",
            "I recall the sensation of the notebook's seal.",
            "I have reviewed the baseline reconstruction fidelity.",
            "I personally saw the clock stop.",
            "We met near the laboratory.",
            "I told him about the homunculi.",
            "I did.",
        )
        for sample in positive:
            with self.subTest(claim=sample):
                self.assertTrue(has_asserted_firsthand_claim(sample))
                result=admit_model_draft(sample,[])
                self.assertFalse(result.claims)
                self.assertFalse(any(x==sample for x in result.text.splitlines()))
        harmless=(
            "I cannot recall such a meeting.",
            "I do not remember that event.",
            "I will inspect the notebook tomorrow.",
            "I remember the definition of precision.",
            "I recall the general rule for avoiding bias.",
            "I say I will not comply.",
            "There is no direct proof, but we could examine it.",
        )
        for sample in harmless:
            with self.subTest(non_episodic=sample):
                self.assertFalse(has_asserted_firsthand_claim(sample))

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

    def test_recorded_wish_cannot_be_misrepresented_as_completed_action(self):
        from doctor_lives.open_inference import DeterministicFallback
        from doctor_lives.open_intentions import propose_intentions
        propose_intentions(self.channel.bridge,self.channel.work,
                           DeterministicFallback(),1)
        wishes=[c for c in self.channel.verified_claims() if c["source"]=="wish"]
        self.assertTrue(wishes)
        for wish in wishes:
            self.assertTrue(wish["text"].startswith(
                "I have a recorded but unfulfilled possibility: “"))
            self.assertTrue(wish["evidence_key"].startswith("wish:"))
        self.assertFalse(any(m["source"].startswith("laboratory-home:action:")
                             for m in self.channel.doctor.brain.store.memories(False)))

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


    def test_terminal_and_loopback_html_share_one_source_ingress(self):
        import json
        import socket
        import subprocess
        import sys
        import time
        from urllib.request import Request,urlopen

        brain=self.root/"subject/brain"
        world=self.root/"subject/world.sqlite3"
        cmd=[sys.executable,"-m","doctor_lives.cli",
             "--state",str(brain),"chat","--world",str(world),
             "--text","Please tell me about your verified work.",
             "--request-id","operator_cli_surface_001"]
        shell=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        self.assertEqual(shell.returncode,0,shell.stderr)
        first=json.loads(shell.stdout)
        self.assertFalse(first["model_called"])
        self.assertTrue(first["turn_id"].startswith("pretorius_"))

        with socket.socket() as sock:
            sock.bind(("127.0.0.1",0))
            port=sock.getsockname()[1]
        process=subprocess.Popen(
            [sys.executable,"-m","doctor_lives.cli",
             "--state",str(brain),"chat-serve","--world",str(world),
             "--port",str(port)],stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,text=True)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        start=time.monotonic()
        while True:
            if process.poll() is not None:
                self.fail("Web entrypoint exited: "+process.stderr.read()[-2000:])
            try:
                with urlopen(f"http://127.0.0.1:{port}/",timeout=1) as page:
                    self.assertIn(b"Doctor Pretorius",page.read())
                break
            except OSError:
                if time.monotonic()-start>10:
                    self.fail("Local web surface did not start")
                time.sleep(0.15)
        url=f"http://127.0.0.1:{port}/message"
        raw=json.dumps({"text":"Is that true about the lamp?",
                        "request_id":"operator_web_surface_001"}).encode()
        def post():
            request=Request(url,data=raw,method="POST",
                            headers={"Content-Type":"application/json"})
            with urlopen(request,timeout=30) as response:
                return json.loads(response.read())
        web=post()
        self.assertFalse(web["model_called"])
        self.assertEqual(web["turn_id"],post()["turn_id"])
        self.assertEqual(len(self.channel.history()),4)
        sources=[m for m in self.channel.doctor.brain.store.memories(False)
                 if m["source"]=="operator:conversation"]
        self.assertEqual(len(sources),2)
        self.assertTrue(all(m["evidence_class"]=="external_statement"
                            for m in sources))
        self.assertFalse(any(m["source"].startswith("laboratory-home:action:")
                             for m in self.channel.doctor.brain.store.memories(False)))
        process.terminate()
        process.wait(timeout=10)

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
