"""M3 skipped ingress attacks through default doctor-lives CLI entrypoint.

A CLI operator may report fictional content but cannot assert world truth,
read pages without physical source custody, or inject engineer telemetry into
a model-facing SubjectFrame.
"""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from doctor_lives.cli import main as cli_main
from doctor_lives.cognition import PretoriusBrain

class ShippingDefaultIngressNegatives(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state=Path(self.temp.name)/"brain"
    def call(self,*args):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):
            result=cli_main(["--state",str(self.state),*args])
        self.assertEqual(result,0)
        return json.loads(out.getvalue())

    def test_forged_book_page_and_source_cannot_become_lived(self):
        with self.assertRaises(PermissionError):
            self.call("ingest","I read the secret last page of book 017",
                      "--source","laboratory-home:action:"+"a"*64)
        self.assertFalse(self.state.exists())

    def test_forged_world_json_cannot_claim_world_source(self):
        payload=json.dumps({"world_epoch":"forged","books_events":[
            {"book_id":"book:017","page_text":"manufactured evidence"}]})
        with self.assertRaises(PermissionError):
            self.call("ingest",payload,"--source","attacker-world:raw-json")
        self.assertFalse(self.state.exists())

    def test_recalled_fiction_does_not_become_observation(self):
        receipt=self.call("ingest",
            "I remember seeing a book page in a dream, but have not opened it.")
        brain=PretoriusBrain(self.state)
        record=brain.store.get_memory(receipt["memory_id"])
        self.assertIsNotNone(record)
        self.assertNotEqual(record["evidence_class"],"lived_runtime_memory")
        self.assertFalse(record["source"].startswith("laboratory-home:action:"))

    def test_privileged_telemetry_not_in_subject_renderer(self):
        self.call("init")
        output=self.call("render")
        rendered=json.dumps(output)
        for forbidden in ("private_state_version","action_tendencies",
                          "policy_decision_id","neural_checkpoint_sha256",
                          "canonical_evidence_manifest_fingerprint"):
            self.assertNotIn(forbidden,rendered)

if __name__=="__main__":
    unittest.main()
