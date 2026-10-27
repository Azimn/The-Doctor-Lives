# Locked follow-up: history-dependent affect modulation, not a constant nudge

**Preregistered before running test.** Research-only extension of draft PR #90, branched from PR #89. No production adoption, no new brain or persistent database, no changes to PR #89/main.

## Motivation
The prior pinned causal result was **40/40** selected tendency changes, uniformly needs-only `explore` to weather-on `persist`. The weather's signed exploration bias was negative in every case. A static negative score offset could explain the entire result. This experiment tests whether **different prior driver histories with identical current input** lead to different downstream selected policies, not merely different numeric weather states.

## Fixed design before first execution

- Original donor unchanged and pinned: `Azimn/Sensus-Communis-Artificialis@904bf11861700739ccc03d4b0d4340ff3422a7d3`. Unmodified donor default config, including trajectory window, thresholds, weather drift, habituation and opponent dynamics. No evaluation of its descriptive transition as a future signal.
- 20 matched neural seeds **2200..2219** (not the earlier 2000..2039), same original canonical `SixOrganRuntime` config as existing PR #90, same initial needs and absent external percepts and physical world effects. For each seed, compare four controlled short-lived instances of the SAME canonical brain implementation: histories A/B, each with weather ON/OFF. Each instance uses only the original `brain.think` native selection path. No competing decision planner.
- History A: ticks **1–72**, one `goal_progress` driver at magnitude +1 per tick.
- History B: ticks **1–72**, one `goal_impediment` driver at magnitude +1 per tick.
- **Shared current period:** ticks **73–80** are *identical* in both histories: one zero-magnitude `rest_density` event per tick. Neither has current positive or negative goal driver. The two histories do differ, so a reasonable dynamic state may differ, but an instantaneous driver-only rule has identical input at choice time.
- Output sampled exactly after tick **80**. Weather ON consumes *only* donor `modulation().exploration_bias`, passed via existing PR #90 opt-in `original_policy_with_weather` test harness with its already preregistered **0.05** gain. Weather OFF computes the same original donor dynamics but lesions its downstream policy contribution. Same native neural/needs state must be verified by assertions. No threshold or coupling rule changes.
- **Primary:** count of 20 seeds where the selected tendency differs between histories A and B in the weather-ON condition. Also report needs-only A/B differences (negative control), and weather-on vs needs-only changed counts separately for each history. Predeclared criterion for evidence of history-dependent *selected policy* is **at least one different A/B selected tendency**, alongside 0/20 A/B differences in needs-only. Differences in raw scores/weather alone do not meet this criterion. If 0/20, report dynamics not demonstrated at the decision level on this battery; stop rather than tune.
- **Mechanism audit:** exposure sensitivity, opponent levels, slow state and the complete append-only donor receipts should be nonempty; snapshots restored with donor API must reproduce these state variables. No claim that individual habituation/opponent mechanisms are separately necessary, since no individual-mechanism lesion is included.
- **Secondary:** *no objective task measure in this history-only follow-up.* It is not a replacement for the existing 20/40 vs 20/40 vs 40/40 task-proxy result. Separately design source-receipted Laboratory task success against needs-only and simple controller, before making any efficacy claim. No action or observation is taken in this history experiment.
- In both histories `salience_gain`, `rehearsal_bias`, `decay_multiplier` remain **unconsumed**, and canonical checkpoint persistence remains missing. Interoceptive attributions are never promoted to world facts.

The earlier Spinoza donor audit still reads **48/57 historical overlapping**, **144/294 strictly future**, **29/61 time-aligned**, level baseline **46.94%**. None is altered by this experiment.
