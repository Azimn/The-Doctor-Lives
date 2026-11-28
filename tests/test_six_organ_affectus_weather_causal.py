"""D6 isolated Affectus weather causal ablation, not a production organ.

Donor: Azimn/Sensus-Communis-Artificialis @
904bf11861700739ccc03d4b0d4340ff3422a7d3.
Felt direction is solely a description of preceding weather movement.
All experimental signals and policy diagnostics remain engineer-side.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from doctor_lives.neural import DEFAULT_CONFIG, ACTIONS
from doctor_lives.organs import SixOrganRuntime

try:
    from sensus_artificialis.affectus import (
        Affectus, AffectusConfig, DriverEvent, DRIVER_KINDS,
    )
except ModuleNotFoundError as exc:
    if exc.name != "sensus_artificialis":
        raise
    Affectus = None

# Locked by AFFECTUS_WEATHER_CAUSAL_PREREG_2026-10-26.md before trial.
SEEDS = tuple(range(2000, 2040))
MAGNITUDES = (1.0, -0.75, 0.8, 0.9, 0.6, 0.5, 0.65, -0.4)
TICKS = 80
FIXED_GAIN = 0.05
NEUTRAL_FLOOR = 1e-9


def config(seed):
    cfg = dict(DEFAULT_CONFIG)
    cfg.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
               input_degree=4, action_population_size=8, seed=seed)
    return cfg


def input_program(weather):
    """Engineering fixtures only, never authenticated percepts or autobiography."""
    for tick in range(1, TICKS + 1):
        idx = ((tick - 1) // 4) % len(DRIVER_KINDS)
        weather.step(tick, (DriverEvent(
            kind=DRIVER_KINDS[idx],
            magnitude=MAGNITUDES[idx],
            source_ref="engineer-controlled-dynamics-fixture",
        ),))


def needs_and_neural(runtime):
    brain = runtime._port.brain
    with brain.store.connect() as conn:
        needs = tuple((row["key"], row["actual"], row["felt"])
                      for row in conn.execute(
                          "SELECT key,actual,felt FROM needs ORDER BY key"
                      ))
    return needs, dict(brain.neural.action_scores())


@contextmanager
def original_policy_with_weather(brain, modulation, *, enabled):
    """Feed one donor delta into ORIGINAL policy scores; no new selector.

    This is a reversible test-only wrapper on this one short-lived instance,
    not a persistent policy hook or model-facing telemetry path.
    """
    original = brain._state_policy_scores
    def adjust(*args, **kwargs):
        base, scores, audit = original(*args, **kwargs)
        if not enabled:
            return base, scores, audit
        delta = FIXED_GAIN * modulation.exploration_bias
        altered = dict(scores)
        altered["explore"] = max(NEUTRAL_FLOOR, altered["explore"] + delta)
        altered["persist"] = max(NEUTRAL_FLOOR, altered["persist"] - delta)
        denominator = sum(altered.values())
        altered = {action: value / denominator
                   for action, value in altered.items()}
        # Ordinary policy audit, never supplied to any renderer.
        audit = dict(audit)
        audit["restricted_affectus_ablation"] = {
            "experimental": True,
            "family_cap_gain": FIXED_GAIN,
            "consumed": ["exploration_bias"],
            "unconsumed": ["salience_gain", "rehearsal_bias",
                           "decay_multiplier"],
            "delta": delta,
        }
        return base, altered, audit
    with patch.object(brain, "_state_policy_scores", side_effect=adjust):
        yield


def run_arm(root, *, seed, enabled):
    runtime = SixOrganRuntime.open(root, neural_config=config(seed))
    brain = runtime._port.brain
    baseline = needs_and_neural(runtime)
    weather = Affectus(AffectusConfig(seed=seed))
    input_program(weather)
    modulation = weather.modulation()
    assert len(weather.receipts) == TICKS
    assert any(v != 1.0 for v in weather.sensitivities.values())
    assert any(abs(v) > 1e-12 for v in weather.opponent_levels.values())
    assert any(abs(v) > 1e-12 for v in weather.state.values())
    with original_policy_with_weather(brain, modulation, enabled=enabled):
        result = runtime.noesis.deliberate(
            host_trigger="affectus_causal_trial"
        )
    policy = brain.store.get_memory if False else None  # no extra acquisition
    after = needs_and_neural(runtime)
    assert baseline == after, "Private policy test must not change needs or neural state"
    with brain.store.connect() as db:
        row = db.execute(
            "SELECT selected_action,action_scores_json,base_action_scores_json,"
            "state_pressure_json FROM policy_decisions WHERE id=?",
            (result.policy_decision_id,),
        ).fetchone()
    scores = json.loads(row["action_scores_json"])
    audit = json.loads(row["state_pressure_json"])
    if enabled:
        assert audit["restricted_affectus_ablation"]["consumed"] == [
            "exploration_bias"
        ]
    else:
        assert "restricted_affectus_ablation" not in audit
    # No private diagnostics enter the factory-controlled first-person frame.
    from doctor_lives.models import SubjectRendererCapability
    subject = "\n".join(
        SubjectRendererCapability.read(
            runtime.synthetic_ipseity.project_subject_frame()
        )
    )
    for hidden in ("exploration_bias", "opponent_levels",
                   "sensitivity", "restricted_affectus_ablation"):
        assert hidden not in subject
    return {
        "tendency": result.selected_tendency,
        "scores": scores,
        "base_scores": json.loads(row["base_action_scores_json"]),
        "modulation": {
            "exploration_bias": modulation.exploration_bias,
            "salience_gain": modulation.salience_gain,
            "rehearsal_bias": modulation.rehearsal_bias,
            "decay_multiplier": modulation.decay_multiplier,
        },
        "baseline": baseline,
        "checkpoint_root": str(root),
    }


@unittest.skipUnless(Affectus is not None, "Optional pinned donor absent; run dedicated causal CI")
class AffectusWeatherCausalAblation(unittest.TestCase):
    def test_preregistered_two_arm_decision_change_rate_and_task_proxy(self):
        counts = {"changed": 0, "score_changed": 0,
                  "weather_task_match": 0, "needs_task_match": 0,
                  "simple_task_match": 0}
        per_seed = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for seed in SEEDS:
                on = run_arm(root / f"{seed}-on", seed=seed, enabled=True)
                off = run_arm(root / f"{seed}-off", seed=seed, enabled=False)
                self.assertEqual(on["baseline"], off["baseline"])
                self.assertEqual(on["base_scores"], off["base_scores"])
                target = "explore" if seed % 2 == 0 else "persist"
                change = on["tendency"] != off["tendency"]
                counts["changed"] += int(change)
                counts["score_changed"] += int(on["scores"] != off["scores"])
                counts["weather_task_match"] += int(on["tendency"] == target)
                counts["needs_task_match"] += int(off["tendency"] == target)
                counts["simple_task_match"] += 1  # label supplied to trivial controller
                per_seed.append({
                    "seed": seed,
                    "target": target,
                    "weather_tendency": on["tendency"],
                    "needs_only_tendency": off["tendency"],
                    "different": change,
                    "exploration_bias": on["modulation"]["exploration_bias"],
                })
        result = {
            "schema": "pretorius.affectus-weather-causal-ablation.v1",
            "reference_donor": "904bf11861700739ccc03d4b0d4340ff3422a7d3",
            "paired_episodes": len(SEEDS),
            "changed_decisions": counts["changed"],
            "change_rate": counts["changed"] / len(SEEDS),
            "different_score_maps": counts["score_changed"],
            "task_proxy": {
                "metric": "host-labeled selected tendency matches explore/persist",
                "weather_on": counts["weather_task_match"],
                "needs_only": counts["needs_task_match"],
                "simple_controller": counts["simple_task_match"],
                "denominator": len(SEEDS),
                "objective_world_task_success": "not tested",
            },
            "consumed": ["exploration_bias"],
            "unconsumed": [
                "salience_gain", "rehearsal_bias", "decay_multiplier"
            ],
            "durable_weather_in_canonical_checkpoint": False,
            "source": "engineer-only driver fixtures, no external world input",
            "per_seed": per_seed,
        }
        print("AFFECTUS_MATCHED_CAUSAL_ABLATION=" +
              json.dumps(result, sort_keys=True))
        self.assertEqual(counts["simple_task_match"], len(SEEDS))
        self.assertGreaterEqual(counts["score_changed"], counts["changed"])

    def test_experimental_lesion_reverts_to_unchanged_original_policy(self):
        with tempfile.TemporaryDirectory() as directory:
            a = run_arm(Path(directory) / "a", seed=2000, enabled=False)
            b = run_arm(Path(directory) / "b", seed=2000, enabled=False)
            self.assertEqual(a["scores"], b["scores"])
            self.assertEqual(a["tendency"], b["tendency"])
            self.assertEqual(a["baseline"], b["baseline"])

    def test_same_current_inputs_distinct_weather_histories_affect_native_choices(self):
        """History-dependent modulation with an identical final eight driver ticks.

        This is an independently preregistered causal check, never a measure
        of successful real-world action or a subject-facing felt explanation.
        """
        groups = {"weather_on_different_history": 0,
                  "needs_only_different_history": 0,
                  "progress_on_vs_off": 0,
                  "impediment_on_vs_off": 0}
        observations = []
        def controlled_arm(root, seed, history_kind, enabled):
            runtime = SixOrganRuntime.open(root, neural_config=config(seed))
            prior = needs_and_neural(runtime)
            weather = Affectus(AffectusConfig(seed=seed))
            for tick in range(1, 81):
                kind = history_kind if tick <= 72 else "rest_density"
                magnitude = 1.0 if tick <= 72 else 0.0
                weather.step(tick, (DriverEvent(
                    kind=kind, magnitude=magnitude,
                    source_ref="unlived-experimental-driver-fixture",
                ),))
            self.assertEqual(len(weather.receipts), 80)
            self.assertLess(weather.sensitivities[history_kind], 1.0)
            self.assertNotEqual(weather.opponent_levels[history_kind], 0.0)
            self.assertTrue(any(abs(x) > 1e-6 for x in weather.state.values()))
            # Weather persistence is only donor-local, never stored as
            # another organ's checkpoint.
            saved = weather.snapshot()
            restored = Affectus.restore(saved, AffectusConfig(seed=seed))
            self.assertEqual(weather.state, restored.state)
            self.assertEqual(weather.sensitivities, restored.sensitivities)
            self.assertEqual(weather.opponent_levels, restored.opponent_levels)
            self.assertEqual(weather.receipts, restored.receipts)
            mod = weather.modulation()
            with original_policy_with_weather(
                runtime._port.brain, mod, enabled=enabled,
            ):
                proposal = runtime.noesis.deliberate(
                    host_trigger="affectus_history_trial"
                )
            self.assertEqual(needs_and_neural(runtime), prior)
            with runtime._port.brain.store.connect() as db:
                row = db.execute(
                    "SELECT action_scores_json FROM policy_decisions WHERE id=?",
                    (proposal.policy_decision_id,),
                ).fetchone()
            return {
                "choice": proposal.selected_tendency,
                "scores": json.loads(row["action_scores_json"]),
                "bias": mod.exploration_bias,
                "state": weather.state,
                "needs_neural": prior,
            }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for seed in range(2200, 2220):
                a_on = controlled_arm(
                    root / f"{seed}-a-on", seed, "goal_progress", True,
                )
                a_off = controlled_arm(
                    root / f"{seed}-a-off", seed, "goal_progress", False,
                )
                b_on = controlled_arm(
                    root / f"{seed}-b-on", seed, "goal_impediment", True,
                )
                b_off = controlled_arm(
                    root / f"{seed}-b-off", seed, "goal_impediment", False,
                )
                for candidate in (a_off, b_on, b_off):
                    self.assertEqual(a_on["needs_neural"], candidate["needs_neural"])
                # The final 8 ticks, including current driver, are identical.
                self.assertNotEqual(a_on["state"], b_on["state"])
                self.assertEqual(a_off["choice"], b_off["choice"],
                                 "A needs-only control should not see hidden weather")
                self.assertEqual(a_off["scores"], b_off["scores"])
                groups["weather_on_different_history"] += int(
                    a_on["choice"] != b_on["choice"]
                )
                groups["needs_only_different_history"] += int(
                    a_off["choice"] != b_off["choice"]
                )
                groups["progress_on_vs_off"] += int(
                    a_on["choice"] != a_off["choice"]
                )
                groups["impediment_on_vs_off"] += int(
                    b_on["choice"] != b_off["choice"]
                )
                observations.append({
                    "seed": seed, "progress_bias": a_on["bias"],
                    "impediment_bias": b_on["bias"],
                    "progress_weather_choice": a_on["choice"],
                    "impediment_weather_choice": b_on["choice"],
                    "needs_only_choice": a_off["choice"],
                })
        report = {
            "schema": "pretorius.affectus-history-dependence.v1",
            "locked_protocol":
                "docs/experiments/AFFECTUS_HISTORY_DEPENDENCE_PREREG_2026-10-26.md",
            "independent_neural_seeds": 20,
            "driver_prefix_ticks": 72,
            "identical_final_driver_ticks": 8,
            "selected_tendency_counts": groups,
            "different_history_causal_choice_effect": (
                groups["weather_on_different_history"] > 0
                and groups["needs_only_different_history"] == 0
            ),
            "modulation_consumed": ["exploration_bias"],
            "unconsumed": [
                "salience_gain", "rehearsal_bias", "decay_multiplier",
            ],
            "world_tasks_tested": 0,
            "observations": observations,
        }
        print("AFFECTUS_SAME_CURRENT_DIFFERENT_HISTORY="
              + json.dumps(report, sort_keys=True))
        self.assertEqual(groups["needs_only_different_history"], 0)
        # No forced-positive assertion: a null decision effect is valid
        # evidence and must not provoke post-hoc changes to driver inputs.

    def test_weather_snapshot_restores_but_canonical_brain_does_not_persist_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "canonical-brain"
            runtime = SixOrganRuntime.open(path, neural_config=config(2000))
            weather = Affectus(AffectusConfig(seed=2000))
            input_program(weather)
            snapshot = weather.snapshot()
            restored = Affectus.restore(snapshot, AffectusConfig(seed=2000))
            self.assertEqual(restored.state, weather.state)
            self.assertEqual(restored.receipts, weather.receipts)
            for tick in range(TICKS + 1, TICKS + 6):
                restored.step(tick)
                weather.step(tick)
            self.assertEqual(restored.state, weather.state)
            self.assertEqual(restored.receipts, weather.receipts)
            runtime.checkpoint()
            reopened = SixOrganRuntime.open(path)
            self.assertFalse(hasattr(reopened.affectus, "_weather"))
            self.assertFalse((path / "affectus.sqlite3").exists())
            self.assertFalse((path / "spinoza_weather.json").exists())
            self.assertIs(reopened.affectus._port, reopened.noesis._port)


if __name__ == "__main__":
    unittest.main()
