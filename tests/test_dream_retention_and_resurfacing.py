"""Controlled decay and fragment selection, not donor qualification."""
import copy
import unittest
from doctor_lives.dream_retention import dream_accessibility, dream_strength
from doctor_lives.dream_resurfacing import fragment_options, select_fragment, verify_fragment

def fixture(**changes):
    text = "I recall a dream: a lavender brass pendulum swings above a flooded library; the walls turn into feathers."
    row = dict(id="memory-one", active=True, kind="dream_recollection", evidence_class="dreamed_not_lived",
               external=True, source="phantasmagorium:dream-recollection:"+"a"*64, text=text, created_tick=0,
               last_rehearsed_tick=None, rehearsal_count=0, base_salience=.35)
    row.update(changes)
    history = [dict(key="ipseity:tower-history:imagination:"+"a"*64, phase="imagination", content=[dict(
        organ="Phantasmagorium", mode="recollection", attribution="dreamed", external=True,
        text=text, source_refs=["sleep-one", "memory-one"])])]
    return row, history

class DreamRetentionTests(unittest.TestCase):
    def test_decay_and_latent_strength(self):
        row, _ = fixture()
        self.assertEqual(dream_accessibility(row, 0), 1)
        self.assertGreater(dream_accessibility(row, 12), dream_accessibility(row, 24))
        self.assertEqual(dream_accessibility(row, 60), 0)
        self.assertGreater(dream_strength(row, 60), 0)
    def test_reflection_is_not_pristine_restore(self):
        row, _ = fixture()
        reflected, _ = fixture(last_rehearsed_tick=12, rehearsal_count=1)
        self.assertGreater(dream_accessibility(reflected, 35), dream_accessibility(row, 35))
        self.assertLess(dream_strength(reflected, 12), 1)
        self.assertEqual(dream_accessibility(reflected, 220), 0)
    def test_repeat_salience_and_bounded_strength(self):
        row, _ = fixture(last_rehearsed_tick=120, rehearsal_count=10)
        self.assertGreater(dream_accessibility(row, 135), .5)
        self.assertGreater(dream_accessibility(fixture(base_salience=.9)[0],40),
                           dream_accessibility(fixture(base_salience=.1)[0],40))
        self.assertEqual(dream_accessibility(fixture(rehearsal_count=100000)[0],200),0)
    def test_independent_trace(self):
        for kind, evidence in (("confirmed_written_utterance","lived_runtime_memory"),
                               ("internal_reflection","self_observed_expression")):
            self.assertEqual(dream_accessibility(fixture(kind=kind,evidence_class=evidence)[0],10000),1)
    def test_clock(self):
        self.assertAlmostEqual(dream_strength(fixture(created_tick=100)[0],112),
                               dream_strength(fixture()[0],12))
        self.assertEqual(dream_strength(fixture(created_tick=100)[0],99),1)
    def test_partial_image(self):
        row, history = fixture()
        before = copy.deepcopy((row, history))
        one = select_fragment([row],history,60,"lavender brass")
        self.assertIsNotNone(one)
        self.assertIn("pendulum", one[2])
        self.assertNotIn("feathers",one[2])
        self.assertNotIn("I recall a dream:",one[2])
        self.assertTrue(verify_fragment(row,history,60,one[2]))
        self.assertEqual(one,select_fragment([row],history,60,"lavender brass"))
        self.assertEqual((row,history),before)
    def test_negative_cues(self):
        row, history = fixture()
        for cue in ("What do I remember about dreams?", "apples bread", "brass"):
            self.assertIsNone(select_fragment([row],history,60,cue))
        self.assertFalse(fragment_options(row,0,"lavender brass"))
        self.assertIsNone(select_fragment([row],history,10000,"lavender brass"))
    def test_ownership_and_bounded_fragment(self):
        row, history = fixture()
        self.assertIsNone(select_fragment([row],[],60,"lavender brass"))
        self.assertFalse(verify_fragment(row,history,60,"I have a fleeting image of a golden dragon; I cannot quite place it."))
        history[0]["content"][0]["text"] += " altered"
        self.assertIsNone(select_fragment([row],history,60,"lavender brass"))
        self.assertFalse(fragment_options(fixture(text="I recall a dream: lavender brass pendulum.")[0],60,"lavender brass"))
        self.assertIsNone(select_fragment([fixture(kind="confirmed_written_utterance")[0]],history,60,"lavender brass"))
