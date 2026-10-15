"""The actual-host pilot must retain its null and absent-history controls."""
import importlib.util
import unittest

DONORS = (importlib.util.find_spec("synthetic_ipseity") is not None
          and importlib.util.find_spec("sensus_artificialis") is not None)


@unittest.skipUnless(DONORS, "Pinned organ dependencies required")
class PairedArticlePilot(unittest.TestCase):
    def test_actual_host_restarts_and_no_history_control(self):
        from tools.run_cascade_articles_pilot import run_pilot
        report = run_pilot()
        self.assertEqual(len(report["trials"]), 18)
        self.assertEqual(len(report["paired_full_vs_existing"]), 6)
        self.assertTrue(all(r["same_policy_action"] and r["same_fact_access"]
                            and r["same_input_size"] for r in report["paired_full_vs_existing"]))
        self.assertTrue(all(r["governor_allowed"] and r["ipseity_pending"] == 0
                            and not r["disputed_fact_leaked"] for r in report["trials"]))
        cascade = {r["session"]: r for r in report["trials"] if r["arm"] == "cascade"}
        self.assertTrue(cascade["delayed_question"]["source_fact_accessible"])
        self.assertTrue(cascade["transfer_question"]["source_fact_accessible"])
        # Preserve the exposed miss. Never rebrand matching wrappers as efficacy.
        self.assertFalse(cascade["delayed_paraphrase"]["source_fact_accessible"])
        self.assertFalse(any(r["source_fact_accessible"] for r in report["trials"]
                             if r["arm"] == "no_task_history"))
        self.assertTrue(all(len(w["policy_decision_ids"]) == 1 for w in report["background_receipts"]))
        self.assertFalse(report["full_article_assessment"]["all_claims_supported"])
        self.assertTrue(all(r["outcome"] == "Unassessable"
                            for r in report["full_article_assessment"]["articles"]))
