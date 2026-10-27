"""Independent source-pinned Affectus donor evaluation; NO Pretorius adoption.

Run ONLY against Azimn/Sensus-Communis-Artificialis, branch
affectus-prototype, pinned SHA 904bf11861700739ccc03d4b0d4340ff3422a7d3.

The donor's published 'next-4-tick' case hist[33]-hist[29] overlaps its
input direction window hist[30:38]. We retain that historical metric but
evaluate genuinely FUTURE ticks in a separate untouched-seed holdout.

The adoption verdict is *reported*, not asserted as positive: a failing
prospective fitness gate must block promotion without making a negative
scientific result disappear from a green audit workflow.
"""
from __future__ import annotations

import json
from random import Random
import unittest

# Donor is intentionally absent from the default Doctor installation.
# Dedicated CI must load this exact pinned donor and run unskipped tests.
try:
    from sensus_artificialis import Attribution, Evidence, Sensus
    from sensus_artificialis.affectus import (
        Affectus, AffectusConfig, DriverEvent, DIMS, DRIVER_KINDS,
    )
except ModuleNotFoundError as exc:
    if exc.name != "sensus_artificialis":
        raise
    Affectus = None


_KINDS = (
    "goal_progress", "goal_impediment", "social_feedback",
    "novelty", "monotony", "prediction_error",
)


def sign(v, eps):
    return 1 if v > eps else (-1 if v < -eps else 0)


def episode(seed):
    """Generate all future evidence *after* each prediction is recorded."""
    rnd = Random(seed)
    weather = Affectus(AffectusConfig(seed=seed))
    history = []
    reported = {}
    for tick in range(1, 87):
        weather.step(tick, (DriverEvent(
            kind=rnd.choice(_KINDS),
            magnitude=rnd.uniform(-1.0, 1.0),
            source_ref="heldout:verified-driver",
        ),))
        history.append(dict(weather.state))
        if tick in (28, 40, 52, 64, 76):
            value = weather.emit_interoception(
                tick, "audit-" + str(seed) + "-" + str(tick),
            )
            reported[tick] = value
    return history, reported


@unittest.skipUnless(Affectus is not None, "Pinned donor runs only in its isolated CI")
class PinnedSpinozaTransitionAudit(unittest.TestCase):
    def test_four_dimensions_eight_drivers_untrusted_attribution_and_no_reset(self):
        self.assertEqual(DIMS, ("valence", "arousal", "security", "fatigue"))
        self.assertEqual(len(DRIVER_KINDS), 8)
        self.assertFalse(hasattr(Affectus(), "reset"))
        generator = Affectus(AffectusConfig(seed=1))
        generator.step(1, (DriverEvent("unresolved_loops", 1.0),))
        wrong = generator.emit_interoception(
            1, "test-misattributed",
            attributions=(Attribution("wrong_social_cause", 0.6),),
        )
        self.assertEqual(wrong.evidence, Evidence.INTEROCEPTIVE)
        self.assertEqual(wrong.attributions[0].cause_ref, "wrong_social_cause")
        scene = Sensus().step(1, (wrong,))
        self.assertEqual(
            scene.objects[0].claims[0].evidence, Evidence.INTEROCEPTIVE
        )
        self.assertFalse(any(
            p.evidence == Evidence.OBSERVED
            for o in scene.objects for p in o.claims
        ))

    def test_positive_but_falling_direction_and_snapshot_continuity(self):
        weather = Affectus(AffectusConfig(seed=5))
        for tick in range(1, 11):
            weather.step(tick, (DriverEvent("goal_progress", 1.0),))
        for tick in range(11, 41):
            weather.step(tick)
        value = weather.emit_interoception(40, "falling").value
        assert weather.state["valence"] > 0.0
        valence = next(x for x in value.split() if x.startswith("valence:"))
        self.assertTrue(valence.endswith("v"), valence)
        restored = Affectus.restore(weather.snapshot(), AffectusConfig(seed=5))
        self.assertEqual(
            restored.emit_interoception(40, "restored").value, value
        )
        for tick in range(41, 50):
            weather.step(tick)
            restored.step(tick)
        self.assertEqual(weather.state, restored.state)
        self.assertEqual(weather.receipts, restored.receipts)

    def test_original_interval_overlap_is_explicit(self):
        # Inspect the executed pinned donor test, not merely a paraphrase
        # of its formula. If the donor test changes, the interval proof
        # must be inspected anew before anyone repeats this criticism.
        from pathlib import Path

        source = (
            Path(__file__).resolve().parent.parent
            / "pinned-affectus-donor" / "tests" / "test_affectus.py"
        )
        self.assertTrue(source.is_file(), "source-pinned donor is required")
        text = source.read_text(encoding="utf-8")
        self.assertIn('w = hist[30:30 + win]', text)
        self.assertIn('past = w[-1][dim] - w[0][dim]', text)
        self.assertIn('fut = hist[33][dim] - hist[29][dim]', text)
        self.assertIn('win, eps = 8, 0.02', text)

        # Donor fitness: direction from hist[30:38], then "future" label
        # hist[33]-hist[29]. Label ends BEFORE its predictor window ends.
        self.assertLessEqual(33, 37)
        self.assertTrue(set(range(29, 34)) & set(range(30, 38)))

    def test_exact_donor_time_aligned_future_holdout_by_dimension(self):
        """Post-hoc diagnostic: match donor's predictor endpoint at tick 38.

        SAME: config defaults (window=8, epsilon=.02), six driver kinds,
        uniform(-1,1) magnitudes, seeded random/noise.
        DIFFERENT: donor leak used hist[33]-hist[29]; this test observes
        hist[37] THEN scores hist[41]-hist[37], so it is prospective.
        Unseen seeds 40..79 have already been inspected elsewhere in this PR:
        this diagnostic cannot be called a NEW preregistered holdout.
        """
        groups = {
            dim: {"compared": 0, "correct": 0, "excluded": 0,
                  "realized_up": 0, "realized_down": 0}
            for dim in DIMS
        }
        for seed in range(40, 80):
            history, _ = episode(seed)
            current_idx = 37  # same as donor's hist[30:38][-1]
            future_idx = 41  # four updates AFTER index 37
            for dim in DIMS:
                delta_past = history[current_idx][dim] - history[30][dim]
                prediction = sign(
                    delta_past, AffectusConfig(seed=seed).direction_epsilon
                )
                realized = sign(
                    history[future_idx][dim] - history[current_idx][dim],
                    0.005,
                )
                d = groups[dim]
                if not prediction or not realized:
                    d["excluded"] += 1
                else:
                    d["compared"] += 1
                    d["correct"] += int(prediction == realized)
                    d["realized_up" if realized > 0 else "realized_down"] += 1
        n = sum(x["compared"] for x in groups.values())
        self.assertGreater(n, 0)
        successes = sum(x["correct"] for x in groups.values())
        result = {
            "schema": "pretorius.affectus-donor.donor-time-aligned-v1",
            "type": "posthoc_diagnostic_not_preregistered",
            "seed_range": [40, 79],
            "same_driver_regime": True,
            "same_default_trajectory_window": 8,
            "same_default_direction_epsilon": 0.02,
            "prediction_at_tick": 38,
            "label_at_tick": 42,
            "four_tick_future_accuracy": round(successes / n, 6),
            "compared": n,
            "by_dimension": {
                dim: {
                    **data,
                    "accuracy": round(data["correct"] / data["compared"], 6)
                    if data["compared"] else None,
                } for dim, data in groups.items()
            },
            "adoption_qualified": False,
        }
        print("AFFECTUS_DONOR_TIME_ALIGNED_DIMENSIONS="
              + json.dumps(result, sort_keys=True))
        self.assertTrue(0.0 <= successes / n <= 1.0)

    def test_independent_strict_future_holdout_reports_actual_coverage(self):
        compared = 0
        direction_correct = 0
        level_correct = 0
        raw_level_correct = 0
        flat = 0
        per_dimension = {
            d: {
                "compared": 0, "correct_direction": 0,
                "correct_coarse_level": 0, "correct_raw_level": 0,
                "excluded_flat": 0, "predicted_up": 0,
                "predicted_down": 0, "realized_up": 0,
                "realized_down": 0,
            } for d in DIMS
        }
        for seed in range(40, 80):  # distinct from original donor's 0..39
            history, reports = episode(seed)
            for tick, report in reports.items():
                current = history[tick - 1]  # only data as of tick
                future = history[tick + 3]   # tick+4, strictly unseen
                fields = dict(p.split(":", 1) for p in report.value.split())
                for dim in DIMS:
                    token = fields[dim]
                    pred = {"^": 1, "v": -1, "~": 0}[token[-1]]
                    # Level sign is an independent, naive comparator.
                    baseline = sign(float(token[:-1]), 0.001)
                    raw_baseline = sign(current[dim], 0.001)
                    realized = sign(
                        future[dim] - current[dim], 0.005
                    )
                    counts = per_dimension[dim]
                    if not pred or not realized:
                        flat += 1
                        counts["excluded_flat"] += 1
                        continue
                    compared += 1
                    counts["compared"] += 1
                    counts["predicted_up" if pred > 0 else "predicted_down"] += 1
                    counts["realized_up" if realized > 0 else "realized_down"] += 1
                    counts["correct_direction"] += int(pred == realized)
                    counts["correct_coarse_level"] += int(baseline == realized)
                    counts["correct_raw_level"] += int(raw_baseline == realized)
                    direction_correct += (pred == realized)
                    level_correct += (baseline == realized)
                    raw_level_correct += (raw_baseline == realized)
        self.assertGreaterEqual(compared, 40)
        accuracy = direction_correct / compared
        baseline = level_correct / compared
        result = {
            "schema": "pretorius.affectus-donor.prospective-v1",
            "source_commit": "904bf11861700739ccc03d4b0d4340ff3422a7d3",
            "episodes": 40,
            "holdout_seeds": "40..79",
            "strict_future_horizon_ticks": 4,
            "compared_nonflat_dimension_cases": compared,
            "excluded_zero_sign_cases": flat,
            "direction_accuracy": round(accuracy, 6),
            "level_only_accuracy": round(baseline, 6),
            "raw_state_level_accuracy": round(raw_level_correct / compared, 6),
            "level_comparator_note": "coarse value is often 0.00; conditionally scored only when direction and actual sign nonzero",
            "episodes_are_independent_units": 40,
            "four_dimensions_and_five_anchors_per_episode": True,
            "per_dimension": {
                dim: {
                    **counts,
                    "accuracy": round(
                        counts["correct_direction"] / counts["compared"], 6
                    ) if counts["compared"] else None,
                    "raw_level_accuracy": round(
                        counts["correct_raw_level"] / counts["compared"], 6
                    ) if counts["compared"] else None,
                } for dim, counts in per_dimension.items()
            },
            "beats_level": accuracy > baseline,
            "passes_donor_revert_criterion": accuracy > 0.60,
            "production_adopted": False,
            "claims": "forecast audit only, NOT cognition advantage",
        }
        print("AFFECTUS_STRICTLY_PROSPECTIVE_HOLDOUT="
              + json.dumps(result, sort_keys=True))
        # Deliberately no forced-positive threshold: negative findings
        # remain executable evidence and must block promotion externally.
        self.assertTrue(0 <= accuracy <= 1)
        self.assertTrue(0 <= baseline <= 1)


if __name__ == "__main__":
    unittest.main()
