"""Stage 01A chronology, parity and honest null-world controls."""
from __future__ import annotations

import unittest

from research_prototypes.predictive_self.loop import (
    EvidenceKind, ObservedEpisode, PredictiveSelfLoop, SelfSnapshot, Situation,
)
from research_prototypes.predictive_self.run_native_policy_benchmark import (
    _context_rotation, cases, run_benchmark,
)


class BenchmarkContractTests(unittest.TestCase):
    def test_frozen_scenarios_and_context_split(self):
        c = cases()
        self.assertEqual(len(c), 28)
        self.assertEqual(
            {phase: sum(s.phase == phase for s in c)
             for phase in {"training", "in_family_holdout", "new_context_diagnostic"}},
            {"training": 16, "in_family_holdout": 8,
             "new_context_diagnostic": 4},
        )
        self.assertEqual(len({s.family for s in c[:24]}), 4)
        self.assertEqual(
            {s.family for s in c[24:]},
            {"missing-record", "unfamiliar-visitor"},
        )
        rotated = [_context_rotation(s.situation) for s in c[:4]]
        self.assertTrue(all(
            case.situation.key != r.key for case, r in zip(c[:4], rotated)
        ))
        self.assertEqual(
            sorted(x.situation.context_id for x in c[:4]),
            sorted(x.context_id for x in rotated),
        )

    def test_sealed_forecast_must_advance_beyond_last_observed_tick(self):
        source = SelfSnapshot(
            "synthetic", "a"*64, 1, "b"*64, 5,
            ("explore", "challenge"), (.5, .5),
        )
        model = PredictiveSelfLoop(source)
        context = Situation("archive", "researcher")
        first = model.forecast(context)
        model.observe(ObservedEpisode(
            "episode-one", first.forecast_id, 6, context,
            "challenge", EvidenceKind.RUNTIME_POLICY, "policy:one",
        ))
        next_forecast = model.forecast(context)
        self.assertEqual(next_forecast.cutoff_tick, 6)
        with self.assertRaisesRegex(ValueError, "not later"):
            model.observe(ObservedEpisode(
                "episode-two", next_forecast.forecast_id, 6, context,
                "explore", EvidenceKind.RUNTIME_POLICY, "policy:two",
            ))
        self.assertEqual(model.audit()["n_scored"], 1)
        model.observe(ObservedEpisode(
            "episode-two", next_forecast.forecast_id, 7, context,
            "explore", EvidenceKind.RUNTIME_POLICY, "policy:two",
        ))
        self.assertEqual(model.audit()["n_scored"], 2)

    def test_native_chronological_benchmark_is_genuine_action_only(self):
        result = run_benchmark()
        self.assertEqual(result["schema"], "pretorius.psl.native-policy-chronological.v1")
        self.assertEqual(result["n_total"], 28)
        self.assertEqual(result["n_native_policy_witnesses"], 28)
        self.assertEqual(result["n_independent_world_outcomes"], 0)
        self.assertEqual(result["n_cross_context_semantic_world_updates"], 0)
        self.assertEqual(
            result["forecaster_counts"],
            {"psl_episode_only": 28,
             "psl_semantic_proxy_unvalidated": 28,
             "psl_shifted_training_context": 28},
        )
        self.assertEqual(
            {k: v["n"] for k,v in result["summary"].items()},
            {"training": 16, "in_family_holdout": 8,
             "new_context_diagnostic": 4},
        )
        for case in result["cases"]:
            self.assertTrue(case["native_store_unchanged_by_forecaster"])
            self.assertFalse(case["world_outcome_verified"])
            self.assertGreater(
                case["native_decision_tick"],
                case["event_tick_before_forecast"],
            )
            self.assertEqual(
                set(case["forecasts"]),
                {"frozen_neural", "global_frequency", "context_frequency",
                 "native_pre_ingest_diagnostic", "psl_episode_only",
                 "psl_semantic_proxy_unvalidated",
                 "psl_shifted_training_context"},
            )
            self.assertEqual(
                len(case["forecasts"]["frozen_neural"]),
                len(result["source"]["actions"]),
            )
            for probs in case["forecasts"].values():
                self.assertAlmostEqual(sum(probs.values()), 1.0)
            for evidence_hash in case["sealed_forecast_digests"].values():
                self.assertEqual(len(evidence_hash), 64)
        original = result["cases"][0]
        self.assertEqual(
            original["forecasts"]["frozen_neural"],
            result["cases"][-1]["forecasts"]["frozen_neural"],
        )


if __name__ == "__main__":
    unittest.main()
