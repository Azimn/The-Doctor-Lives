import unittest
from doctor_lives.first_person_governance import admissible_output, govern_renderer, first_person_line

class FirstPersonTests(unittest.TestCase):
    def test_original_governor_direct_stance(self):
        for text in ("Pretorius, I need rest.", "I recognize that Pretorius wants tea.",
                     "Pretorius is tired.", "I want Pretorius to rest.",
                     "I am an AI language model.", "I see state_pressure=0.2."):
            with self.subTest(text=text):
                self.assertFalse(admissible_output(text))
        self.assertTrue(admissible_output("I would rather make tea. Rosa can wait."))
        self.assertTrue(admissible_output("I heard Rosa say, “Pretorius is late.”"))
    def test_only_narrative_input_and_safe_fallback(self):
        lines = []
        def render(text):
            lines.append(text)
            return "Pretorius is tired."
        out = govern_renderer(render)("A historical account.\nI feel tired.\nstate_pressure=0.3")
        self.assertTrue(all(x.startswith("I ") for x in lines[0].splitlines()))
        self.assertNotIn("state_pressure", lines[0])
        self.assertTrue(admissible_output(out))
        self.assertIn("without claiming I witnessed it", first_person_line("A historical account."))
