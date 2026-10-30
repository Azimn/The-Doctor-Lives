"""Offline contracts for language-as-proposal, never language-as-motor."""
import unittest

from doctor_lives.open_inference import DeterministicFallback, LocalOllama, make_inference
from doctor_lives.open_intentions import grounding

class ProviderNeutralContracts(unittest.TestCase):
    def test_provider_cannot_use_remote_api_or_unauthorized_url(self):
        for endpoint in ("https://127.0.0.1:11434",
                         "http://api.openai.com:443",
                         "http://example.org:11434",
                         "http://127.0.0.1:11434/remote",
                         "http://username:password@localhost:11434"):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                LocalOllama("local-only", endpoint=endpoint)

    def test_never_choose_default_remote_provider(self):
        for option in ("openai","http","cloud","hosted","unknown"):
            with self.subTest(provider=option), self.assertRaises(ValueError):
                make_inference(option)
        self.assertIsInstance(make_inference("fallback"),DeterministicFallback)

    def test_fallback_is_stable_and_yields_open_proposals(self):
        context={"situation":"I am in a lab", "memories":["I read about circuits."],
                 "needs":[{"need":"curiosity","felt":0.5}],
                 "affordances":[{"description":"read the actual document"},
                                {"description":"append the daily journal"},
                                {"description":"send the operator a message"}]}
        p=DeterministicFallback().propose(context)
        self.assertEqual(p,DeterministicFallback().propose(context))
        self.assertTrue(3<=len(p)<=8)
        self.assertTrue(all(isinstance(t,str) and t.strip() for t in p))
        self.assertTrue(any("I wish" in t or "I would like" in t for t in p))

    def test_novel_free_text_is_only_grounded_when_real_capability_exists(self):
        affordances=[{"affordance_key":"document_read","description":"read the research document",
                      "goal_type":"study"}]
        actual,note=grounding("I might read the research document.",affordances)
        self.assertEqual(actual["affordance_key"],"document_read")
        absent,note=grounding("I want to travel to an unknown city.",affordances)
        self.assertIsNone(absent)
        self.assertIn("wish",note)

    def test_new_capability_is_data_not_a_new_action_function(self):
        before=[{"affordance_key":"document_read","description":"read the research document",
                 "goal_type":"study"}]
        phrase="I might append a finding to the newly opened archive."
        self.assertIsNone(grounding(phrase,before)[0])
        after=before+[{"affordance_key":"archive_findings",
                       "description":"append a finding to the newly opened archive",
                       "goal_type":"archive"}]
        self.assertEqual(grounding(phrase,after)[0]["affordance_key"],"archive_findings")

if __name__=="__main__":
    unittest.main()
