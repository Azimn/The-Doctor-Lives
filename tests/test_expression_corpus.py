import unittest
from tools.prepare_expression_corpus import grouped_split, validate, normal
from tools.train_expression_lora import masked_example


class ExpressionCorpusTests(unittest.TestCase):
    def test_grouped_overlapping_turns_never_cross_splits(self):
        def record(user, assistant):
            return {"messages":[{"role":"system","content":"Voice"},{"role":"user","content":user},
                                {"role":"assistant","content":assistant}]}
        rows=[record("same question!", "answer one"),record("Same question", "answer two"),
              record("new question", "ANSWER TWO"),record("three", "a3"),
              record("four", "a4"),record("five", "a5"),record("six", "a6")]
        splits, groups=grouped_split(rows)
        self.assertEqual(groups,5)
        self.assertTrue(any(set((0,1,2)).issubset(ids) for ids in splits.values()))
        self.assertEqual(sorted(i for ids in splits.values() for i in ids),list(range(len(rows))))
        self.assertEqual(grouped_split(rows),(splits,groups))

    def test_assistant_only_token_mask(self):
        class Tokenizer:
            def apply_chat_template(self, messages, tokenize, add_generation_prompt):
                result=[]
                for m in messages:
                    role={"system":10,"user":20,"assistant":30}[m["role"]]
                    result.extend([role,ord(m["content"]),99])
                if add_generation_prompt: result.append(30)
                return result
        messages=[{"role":"system","content":"S"},{"role":"user","content":"U"},
                  {"role":"assistant","content":"A"},{"role":"user","content":"V"},
                  {"role":"assistant","content":"B"}]
        result=masked_example(Tokenizer(),messages,100)
        self.assertEqual([x for x in result["labels"] if x!=-100],[65,99,66,99])
        with self.assertRaises(ValueError):
            masked_example(Tokenizer(),messages,3)
