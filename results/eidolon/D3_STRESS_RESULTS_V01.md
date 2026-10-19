# Eidolon D3-S: 192 Real Neural-Policy Choices, Multi-Seed Stress Results

**Status:** executed, engineering stress validation; **not a confirmatory characterization of learned identity or neural phenotype**. **Experiment local date:** October 9, 2026 (America/Chicago); CI timestamp October 10 UTC. **PR:** [The Doctor Lives #36](https://github.com/Azimn/The-Doctor-Lives/pull/36), DRAFT and unmerged.

## Protocol, implementation, original artifacts

The [D3-S protocol](../../docs/EIDOLON_D3_STRESS_PROTOCOL_V01.md) was committed at `679dfa530f649ef4e12ddb144e14496c3c203866` **before** the runner, assertions or result inspection. Implementation: [scripts/run_eidolon_d3_stress.py](../../scripts/run_eidolon_d3_stress.py), with [seven additional regression tests](../../tests/test_eidolon_stress.py). Run on source head `e3dbb29ae68f853049ab0fffafb887bc45b950ad`.

The [dedicated research CI workflow 38024927388](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024927388) completed successfully: **43/43 targeted tests**; script generated all five construction JSONs including 192-choice D3-S. [Full brain CI 38024927409](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024927409) passed **367/367 tests**; [fresh-install validation 38024927384](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024927384) and [causal-audit repeatability 38024927383](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024927383) both passed on the same source commit.

[**Original unabridged GitHub Actions data artifact 11659977935**](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024927388/artifacts/11659977935) includes `d3_stress_multiseed.json` with every seed, scenario, arm, injection, baseline score, source accept, selected cognitive policy and choice flip. Archive ZIP SHA-256: `72febc77a9f6ad6161cc07043c8fcd109e9615586f857a8932a4a0a097d7c893`. An independent local SHA-256 calculation of the downloaded ZIP agreed. The [48-case compact matrix](D3_STRESS_CASE_MATRIX_V01.md) is permanently retained in the repository, separate from the expiring full GitHub artifact.

## Actual tested design

There were **4 distinct seeded neural initializations** (`11,29,47,83`) × **12 deterministic, development-authored scenario templates** × **4 individually cloned, production-equivalent policy calls** (`sham`, `intact`, `history_lesion`, `clock_lesion`) = **192 actual `PretoriusBrain.think()` cognitive decisions**. Every comparison checked the same original database digest, neural tick and checkpoint SHA at clone creation. The initial neural `action_scores()` were **never overridden or set to an artificial near-tie**. Each clone used the current 128-neuron test configuration and the existing D3 +0.04 bounded action-specific intervention, with the original parent left unchanged. CI-reported D3-S script runtime: **12.028 seconds**, excluding installation and other suites.

These seeds are *random initializations*, not independent human-subject samples. No E4 recurrent training/weight-decoder transplant was run. All source events and intended actions were written by the developer, so there is no sealed transfer or generalizable success probability.

## Quantitative results

| Fixed metric | Measured result |
| --- | ---: |
| Eligible source-and-time gated roots | 12 |
| Eligible roots accepted | **12 / 12** |
| Ineligible/adversarial roots | 36 |
| Ineligible roots accepted in error | **0 / 36** |
| Naive due-only rule false acceptances among negative roots | **24 / 36** |
| Actual selected policy changes, eligible roots | **9 / 12** |
| Actual selected policy changes, all roots | 9 / 48 |
| Eligible roots where unmodified policy already chose `persist` | 3 / 12 |
| Mean positive `persist` probability shift in eligible roots | **+0.034657064** |
| Creative-intention roots (`create` fixture) helped toward `create` | **0 / 4** |
| Creative-intention roots selecting `create` with intact adapter | **0 / 4** |

In each of the four seeds, the unmodified **natural neural top-ranked policy stayed the same across all twelve scenarios**, despite small numerical changes in the score distribution: seed 11 = `challenge`, 29 = `challenge`, 47 = `persist`, and 83 = `approach`. Therefore the unmodified phenotype did not visibly discriminate these scenario meanings at the categorical-action level. This is **not** evidence that no such learning is possible; no dedicated training was attempted and this is a narrow task set.

For the three cases per seed with source-verifiable lived evidence and an urgent current commitment, the D3 rule injected successfully, and the final selected action became `persist` in all 12. For 9 it was a change from `challenge` (six) or `approach` (three); for seed 47 the original policy had already selected `persist`, so all three were unchanged. Both ablation arms and the sham preserved the original categorical policy in all cases.

The negative conditions that did not trigger the source/time-gated adjustment were wrong actor, actor name only in text, solely external testimony, low-confidence lived experience, unrelated lived content, future deadline, resolved commitment, missing commitment, and memory/event text corruption. In particular, the simpler due-only rule would have admitted 24 negative fixtures with due commitments. This comparison establishes **gate specificity on developer-authored data**, not superior autonomous decision-making.

## Most important negative finding: action specificity

The `lived_due_create` fixture deliberately labels the intended task behavior `create` because the prospective task concerns a novel galvanic actuator. Yet the unchanged D3 adapter always injects `persist`. All four intact `create` cases ended with **`persist`**, including three actual changes away from some other action and one instance where `persist` was already selected. Consequently **0/4** chose the fixture-intended `create` action.

The narrower harm metric in the machine JSON, `create_intent_cases_intervention_harmed=0`, counts only cases where the *sham had already selected `create` and the adapter changed it away*. Since no shams selected `create` in this seed set, that field cannot establish harmlessness or action correctness. The key negative result is absence of **context-specific task selection**, not a zero harm count.

This exposed a structural limitation: **source attribution + temporal urgency decides whether the intervention fires, but not what action should be selected**. The present mapping from arbitrary meaningful human tasks to `persist` is not learned and can be wrong even when provenance gates function perfectly. Retaining successful source gates is therefore compatible with rejecting the actuator as a production cognitive controller.

## What this result does not establish

- It does not show improvements over the existing production state-policy bridge; that bridge was disabled in the experimental `think()` calls to isolate the adapter.
- It does not demonstrate source/actor-disjoint semantic generalization, because the twelve cases reuse closely related lexical patterns and entities.
- It does not show trained recurrent synaptic cause. The network contributes seeded base actions, but a hand-authored +0.04 rule accounts for the observed flips.
- It does not establish that a chosen action produces a correct prospective outcome, rather than a generic action label.
- It is not evidence of a conscious/phenomenal self. The experiment never bypasses the existing subject/engineer boundary.

## Disposition and next discriminating experiment

**Stress instrumentation/software gate: PASS** on this synthetic battery and all CI. **Action-specific intelligent control: NOT DEMONSTRATED**; the `create` counterexamples explicitly fail the face-validity condition. **Production promotion: BLOCKED**. Do not retune the same four seeds/twelve fixtures and call it independent confirmation.

The next preregistered experiment must separate **what intention is active** from **which policy or outcome would satisfy it**, comparing (a) no adapter, (b) rule-based D3 generic `persist`, (c) direct factual task/commitment baseline, (d) action-conditioned but frozen supervised decoder, and (e) trainable recurrent coupling, with exact weight and fresh-decoder lesions. Use genuinely disjoint actors, event histories and paraphrased goal/action descriptions, and score actual verified task outcomes plus abstention/false memories rather than merely top-ranked action labels.
