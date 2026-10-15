"""Preserve the distinction between policy gating and accessible memory."""
import importlib.util
import unittest

DONORS = (importlib.util.find_spec("synthetic_ipseity") is not None
          and importlib.util.find_spec("sensus_artificialis") is not None)


@unittest.skipUnless(DONORS, "Pinned organ dependencies required")
class CooldownDiagnostic(unittest.TestCase):
    def test_factorial_intervention_preserves_both_effects(self):
        from tools.run_cascade_cooldown_diagnostic import run_diagnostic
        report = run_diagnostic()
        self.assertTrue(report["common_checkpoint"])
        self.assertFalse(report["runtime_defaults_changed"])
        self.assertFalse(report["external_task_outcomes_measured"])
        self.assertFalse(report["semantic_generalization_tested"])
        self.assertEqual(len(report["trials"]), 4)
        rows = {(r["wording"], r["cooldown_ticks"]): r for r in report["trials"]}
        for wording in ("original_wording", "paraphrase"):
            default, clamp = rows[(wording, 2)], rows[(wording, 1)]
            self.assertTrue(default["cooldown_active"])
            self.assertEqual(default["policy_action"], "continue")
            self.assertEqual(default["raw_scores"]["recall"], 0)
            self.assertFalse(clamp["cooldown_active"])
            self.assertEqual(clamp["policy_action"], "recall")
            self.assertTrue(clamp["source_fact_accessible"])
        self.assertTrue(rows[("original_wording", 2)]["source_fact_accessible"])
        self.assertFalse(rows[("paraphrase", 2)]["source_fact_accessible"])
        for row in rows.values():
            self.assertEqual(row["policy_action"], row["persisted_action"])
            self.assertFalse(row["disputed_fact_leaked"])
            self.assertTrue(row["governor_allowed"])
