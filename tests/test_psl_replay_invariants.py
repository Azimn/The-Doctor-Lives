"""Core/dynamic replay separation is specific and fail-closed."""
import unittest

from research_prototypes.predictive_self.compare_native_replays import compare, core_payload


def sample():
    return {
        "schema": "pretorius.psl.native-policy-chronological.v1",
        "source": {"snapshot_digest": "a" * 64},
        "n_total": 1,
        "cases": [{
            "index": 0,
            "selected_action": "explore",
            "forecasts": {
                "frozen_neural": {"explore": .6, "persist": .4},
                "psl_episode_only": {"explore": .7, "persist": .3},
                "native_pre_ingest_diagnostic": {"explore": .4999999999, "persist": .5000000001},
            },
            "scored": {
                "frozen_neural": {"log_loss": .5},
                "psl_episode_only": {"log_loss": .35},
                "native_pre_ingest_diagnostic": {"log_loss": .7},
            },
            "sealed_forecast_digests": {"psl_episode_only": "b" * 64},
        }],
        "summary": {
            "in_family_holdout": {
                "n": 1,
                "metrics": {
                    "frozen_neural": {"mean_log_loss": .5},
                    "psl_episode_only": {"mean_log_loss": .35},
                    "native_pre_ingest_diagnostic": {"mean_log_loss": .7},
                },
            },
        },
    }


class ReplayTests(unittest.TestCase):
    def test_only_live_floating_diagnostic_may_differ(self):
        first = sample()
        import copy
        second = copy.deepcopy(first)
        second["cases"][0]["forecasts"]["native_pre_ingest_diagnostic"]["explore"] += 1e-9
        second["cases"][0]["scored"]["native_pre_ingest_diagnostic"]["log_loss"] -= 1e-8
        second["summary"]["in_family_holdout"]["metrics"]["native_pre_ingest_diagnostic"]["mean_log_loss"] += 1e-8
        report = compare(first, second)
        self.assertTrue(report["core_equal"])
        self.assertFalse(report["full_json_equal"])
        self.assertTrue(report["selected_action_sequence_equal"])

    def test_actual_target_or_control_changes_are_detected(self):
        import copy
        first = sample()
        altered = copy.deepcopy(first)
        altered["cases"][0]["scored"]["psl_episode_only"]["log_loss"] += .001
        self.assertFalse(compare(first, altered)["core_equal"])
        altered = copy.deepcopy(first)
        altered["cases"][0]["selected_action"] = "persist"
        report = compare(first, altered)
        self.assertFalse(report["core_equal"])
        self.assertFalse(report["selected_action_sequence_equal"])
        altered = copy.deepcopy(first)
        altered["source"]["snapshot_digest"] = "z" * 64
        self.assertFalse(compare(first, altered)["core_equal"])

    def test_diagnostic_cannot_silently_disappear(self):
        first = sample()
        del first["cases"][0]["forecasts"]["native_pre_ingest_diagnostic"]
        with self.assertRaisesRegex(ValueError, "dynamic diagnostic"):
            core_payload(first)


if __name__ == "__main__":
    unittest.main()
