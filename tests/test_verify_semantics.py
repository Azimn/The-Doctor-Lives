"""Semantic mapping and provenance-judge adversarial tests."""
import unittest
from scripts.verify_semantics import evaluate, verify_report, MIN_INVARIANCE
from doctor_lives.semantic_intentions import (
    LocalOllamaEmbeddings, semantic_category, semantic_scores, fallback_scores)

class SemanticIntentionContract(unittest.TestCase):
    def test_thirty_intentions_and_sixty_paraphrases(self):
        r=evaluate(semantic_category)
        self.assertEqual(r["examples"],90)
        self.assertEqual(r["families"],30)
        self.assertGreaterEqual(r["invariance"],MIN_INVARIANCE)
        self.assertGreaterEqual(r["category_accuracy"],0.90)

    def test_meaning_not_randomized_hash_and_repeatable(self):
        for phrase in ("I want to build a new device",
                       "I wish to construct a new machine",
                       "I ought to create a mechanism"):
            self.assertEqual(semantic_category(phrase),"create")
        self.assertEqual(semantic_scores("I ought to read a manuscript"),
                         semantic_scores("I ought to read a manuscript"))

    def test_explicitly_local_embedding_port(self):
        for endpoint in ("https://localhost:11434",
                         "http://example.org:11434",
                         "http://127.0.0.1:11434/remote"):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                LocalOllamaEmbeddings("nomic-embed-text",endpoint)

    def test_no_faked_ablation_or_uncapped_novelty(self):
        base={"selected_proposal_id":"a","contributions":{
            "a":{"neural":0.1,"novelty":0.0,"familiarity":0.0,"history":0.0,"total":0.1},
            "b":{"neural":0.1,"novelty":0.1,"familiarity":0.0,"history":0.0,"total":0.2}}}
        with self.assertRaisesRegex(ValueError,"cap"):
            verify_report({"decisions":[base],"recurrent_lesion":{"seeds":20,
                "executed_with_causal_audit_harness":True}})
        base["contributions"]["b"]["novelty"]=0.05
        with self.assertRaisesRegex(ValueError,"CausalAuditHarness"):
            verify_report({"decisions":[base]})

if __name__=="__main__":
    unittest.main()
