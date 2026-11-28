"""Post-fixture semantic regression for independently authored free-language intentions.

The phrases were frozen in the earlier 878fbae ChatGPT fixture commit
before the bounded semantic-vocabulary refinement. They are an in-sample
regression now, not a new held-out benchmark or independent LLM evaluation.
"""
import unittest
from doctor_lives.semantic_intentions import semantic_category, semantic_scores
from scripts.chatgpt_standin_probe import SEMANTIC_HOLDOUT

class ChatGPTAuthoredSemanticRegressions(unittest.TestCase):
    def test_preexisting_original_judge_is_preserved(self):
        from scripts.verify_semantics import evaluate, MIN_CATEGORY_ACCURACY, MIN_INVARIANCE
        result = evaluate(semantic_category)
        self.assertGreaterEqual(result["category_accuracy"], MIN_CATEGORY_ACCURACY)
        self.assertGreaterEqual(result["invariance"], MIN_INVARIANCE)

    def test_chagpt_authored_ten_phrases_retain_intended_meanings(self):
        self.assertEqual(len(SEMANTIC_HOLDOUT), 10)
        for phrase, expected in SEMANTIC_HOLDOUT:
            with self.subTest(phrase=phrase):
                self.assertEqual(semantic_category(phrase), expected)
                self.assertEqual(semantic_scores(phrase), semantic_scores(phrase))

if __name__ == "__main__":
    unittest.main()
