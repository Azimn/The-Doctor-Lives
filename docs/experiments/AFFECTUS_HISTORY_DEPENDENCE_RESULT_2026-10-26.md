# Affectus weather history-dependence: controlled execution receipt

Date: 2026-10-26/27. **Status: draft experimental result, no production adoption.**

## Version and source boundaries

- PR #90 was branched at PR #89 exact head `e8c770a0140991dc308e194a79adcee148ab2248`. `main` at that point was `784cff39d58a7fe46bb5e4ffc16e0284e6663c78`; neither original branch was edited in this experiment.
- Donor `Azimn/Sensus-Communis-Artificialis` at exact `904bf11861700739ccc03d4b0d4340ff3422a7d3`; all original config defaults, driver equations, habituation, opponent response and slow decay unchanged.
- Predeclared method: [`AFFECTUS_HISTORY_DEPENDENCE_PREREG_2026-10-26.md`](AFFECTUS_HISTORY_DEPENDENCE_PREREG_2026-10-26.md), commit `485ea44b3846c4c15d2898751bff2b3b5eaac631`, written **before** the test at `7ab10720c192cb745d2d770766cfb9b3e8dc8778`.
- Tested implementation: `tests/test_six_organ_affectus_weather_causal.py:test_same_current_inputs_distinct_weather_histories_affect_native_choices`; source checkout and two-arm original native decision wiring pinned and verified by [GitHub Actions run 40446192875](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40446192875).

## Exact controlled comparison

Twenty independent neural seed comparisons, seeds 2200–2219. All arms have identical original recurrent/needs state and no externally sourced world percept. Each compares:
- History A: 72 consecutive `goal_progress` driver ticks, each magnitude +1.
- History B: 72 consecutive `goal_impediment` driver ticks, each magnitude +1.
- **Both** finish with eight identical ticks of zero-magnitude `rest_density` input, then select an action tendency using the original `PretoriusBrain.think` via `NoesisOrgan.deliberate`.
- For each history, weather ON consumes the donor's unchanged `exploration_bias` through previously preregistered `0.05*bias` score adjustments at the existing policy boundary; weather OFF consumes no modulation. No weather state is written into another identity store or default checkpoint.

### Matched results

| Counted outcome | Numerator / denominator |
| --- | ---: |
| Different ON tendency between histories A and B | **20/20** |
| Different OFF tendency between histories A and B | **0/20** |
| ON vs OFF after goal progress | **0/20** |
| ON vs OFF after goal impediment | **20/20** |

Every progress-history ON and needs-only OFF decision was `explore`; every impediment-history ON decision was `persist`. Progress-history weather `exploration_bias`: **+0.0640 to +0.1316**. Impediment-history weather `exploration_bias`: **-0.1275 to -0.0599**. Both weather histories had nonempty opponent forces, nontrivial slow state and altered sensitivity. The donor's `snapshot/restore` recreated the exact state, sensitivity, opponents and receipts. The existing `salience_gain`, `rehearsal_bias`, `decay_multiplier` outputs remain unconsumed.

**Narrow claim supported:** remembered *driver history* in donor weather causally changes **subsequent selected policy** with identical immediate drivers and matched initial canonical brain/needs. This is more informative than one uniform fixed negative nudge. **Not established:** which individual dynamics component caused the split, whether the donor beats a well-designed history-sensitive simple controller, whether the resulting choices accomplish physical tasks, or whether weather survives the canonical Pretorius checkpoint. These remain qualification blockers.

### CI

At implementation commit `7ab10720c192cb745d2d770766cfb9b3e8dc8778`:
- [Pinned donor research run 40446192875](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40446192875): **PASS**, 17 unchanged original donor tests, four non-skipped weather causal tests, **493 full Doctor tests with 104 explicitly reported optional skips**.
- [Independent ordinary Doctor run 40446192734](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40446192734): **PASS**, optional donor tests are skipped when their exact source is not installed.
- Previous [fresh-install run 40445870035](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40445870035) passed at earlier workflow-repair commit `f43d8f0e953d37c001b728c919245b6747642805`; it was not triggered on the subsequent tests-only commit, so do not imply the fresh-install job reran at the latest head.
- Previous failing combined suite [40442763940](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40442763940) exposed a Sensus pinned-donor import conflict and a Python-3.11 exact floating-point normalization assertion. The workflow now runs original Doctor suite without overlaying the differently pinned Sensus donor and uses the existing repository's Python 3.12. **No assertion was relaxed, no neural/needs source edited, and no negative evidence changed.** The Python-3.11 equality caveat is not a production issue certified resolved by this isolation.

## Evidence boundaries and following gates

This test is an opt-in research harness, not an operating Affectus subsystem. No renderer sees the engineer-only driver sequence, modulation audit or private target labels. No world action is claimed without a Laboratory receipt. The original source-qualified bodily injury route `affectus_lab_pilot.py` is unchanged and its results should not be conflated with this weather experiment.

Next meaningful work: preregister and measure actual source-verified Laboratory task completion against matched needs-only and nontrivial simple-controller baselines, while preserving identical task information, authorized actions, crash/replay and first-person provenance. Later, agree how donor weather could persist **inside the existing canonical BrainStore/checkpoint**, without any independent organ identity or database, and investigate the three unconsumed modulation channels. Existing Sensus/Mnemosyne/Ipseity/Noesis–Corpus integration obligations and D11 superiority remain unchanged.

The settled Spinoza descriptive transition cannot be cited as forecasting: original **48/57** used overlapping intervals, independent prospective **144/294**, donor-time-aligned **29/61**, unquantized level baseline **46.94%**. No parameter in that evaluation was touched here.
