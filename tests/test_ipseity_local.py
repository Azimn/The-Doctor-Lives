"""One-turn local session enforces the durable subject-only renderer route."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from doctor_lives.neural import DEFAULT_CONFIG


def small_config():
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({
        "neurons": 128,
        "sensory_dim": 64,
        "avg_recurrent_degree": 8,
        "input_degree": 4,
        "action_population_size": 8,
    })
    return cfg


@unittest.skipUnless(
    importlib.util.find_spec("synthetic_ipseity"),
    "optional donor not installed",
)
class LocalIpseityRuntimeTests(unittest.TestCase):
    def setUp(self):
        from doctor_lives.ipseity_local import local_turn
        from synthetic_ipseity import LocalOllamaRenderer
        self.local_turn = local_turn
        self.local_renderer = LocalOllamaRenderer
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name)
        self.payloads = []

    def renderer(self, fn=None):
        def transport(data, timeout):
            decoded = json.loads(data)
            self.payloads.append(decoded)
            if fn is not None:
                return fn(data)
            return b'{"response":"I see why you have asked."}'
        return self.local_renderer("qwen3:1.5b", transport=transport)

    def test_local_turn_renders_actual_external_communication_without_diagnostics(self):
        reply = self.local_turn(
            self.path,
            user_text="Please examine the brass balance.",
            renderer=self.renderer(),
            neural_config=small_config(),
            now_ms=1000,
        )
        self.assertEqual(reply, "I see why you have asked.")
        self.assertEqual(len(self.payloads), 1)
        prompt = self.payloads[0]["prompt"]
        self.assertIn("I read a message from User", prompt)
        self.assertIn("brass balance", prompt)
        self.assertNotIn("source_record_ids", prompt)
        self.assertNotIn("state_pressure", prompt)
        self.assertNotIn("local-conversation:", prompt)
        self.assertNotIn("local_turn_journal", prompt)
        self.assertEqual(self.payloads[0]["model"], "qwen3:1.5b")
        self.assertEqual(set(self.payloads[0]), {"model", "prompt", "stream", "options"})

        # A second turn reopens the original brain and independent organ state.
        second = self.local_turn(
            self.path,
            user_text="Thank you. Please reconsider the balance.",
            renderer=self.renderer(),
            now_ms=2000,
        )
        self.assertEqual(second, reply)
        from doctor_lives.chassis import PretoriusBrainPort
        store = PretoriusBrainPort(self.path).brain.store
        self.assertTrue(any(
            "brass balance" in x["text"] for x in store.memories()
        ))
        self.assertTrue(any(
            "Please reconsider the balance" in x["text"] for x in store.memories()
        ))
        # A generated model response is not a firsthand event just because
        # the renderer produced it. Self-perception requires a future
        # separately attested speech/emission receipt.
        self.assertFalse(any(
            "I see why you have asked" in x["text"] for x in store.memories()
        ))

    def test_failed_delivery_is_retried_without_duplicate_human_input(self):
        calls = 0
        def fail_once(data):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("simulated model outage")
            return b'{"response":"I may continue now."}'
        renderer = self.renderer(fail_once)
        with self.assertRaisesRegex(RuntimeError, "simulated model outage"):
            self.local_turn(
                self.path,
                user_text="The flask is intact.",
                renderer=renderer,
                neural_config=small_config(),
                now_ms=100,
            )
        from doctor_lives.chassis import PretoriusBrainPort
        before = PretoriusBrainPort(self.path).brain.store
        count = len(before.memories())
        digest = before.digest()
        with self.assertRaisesRegex(RuntimeError, "Previous subject experience"):
            self.local_turn(
                self.path,
                user_text="The flask is broken.",
                renderer=renderer,
                now_ms=200,
            )
        self.assertEqual(count, len(PretoriusBrainPort(self.path).brain.store.memories()))
        recovered = self.local_turn(
            self.path, resume=True, renderer=renderer, now_ms=30101,
        )
        self.assertEqual(recovered, "I may continue now.")
        self.assertEqual(count, len(PretoriusBrainPort(self.path).brain.store.memories()))
        self.assertEqual(digest, PretoriusBrainPort(self.path).brain.store.digest())
        self.assertEqual(calls, 2)
        with self.assertRaisesRegex(RuntimeError, "No pending"):
            self.local_turn(
                self.path, resume=True, renderer=renderer, now_ms=40000,
            )

    def test_invalid_turn_rejected_prior_to_state_mutation(self):
        with self.assertRaises(ValueError):
            self.local_turn(
                self.path, user_text="  badly formatted ", renderer=self.renderer(),
                neural_config=small_config(),
            )
        with self.assertRaises(ValueError):
            self.local_turn(
                self.path, renderer=self.renderer(), neural_config=small_config(),
            )
        self.assertEqual(self.payloads, [])


if __name__ == "__main__":
    unittest.main()
