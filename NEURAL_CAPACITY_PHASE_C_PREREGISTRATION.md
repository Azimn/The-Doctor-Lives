# C01 — Pretorius Neural Capacity, Calibration, and Developmental Mediation

**Status:** FROZEN PREREGISTRATION, NO PHASE C OUTCOMES GENERATED  
**Protocol ID:** `pretorius-capacity-mechanism-c01-v1`  
**Date frozen:** 2026-10-07  
**Branch:** `research/neural-capacity-phase-c`  
**Baseline:** Phase B merge commit `fb9e9c29f98e8a532fdff82f3152778328af57a6`  
**Authoritative predecessor:** `NEURAL_CONVERGENCE_4096_PREREGISTRATION.md`; `results/neural_characterization/B08_PRODUCTION_DISPOSITION.md`; `B08_DECISION.json`; `B08_INDEPENDENT_REVIEW.md`.

## C01 boundary and research question

Phase B was accepted and merged without changing production defaults: `legacy_v04` remains the default and `neural_convergence_v05` remains opt-in. The accepted B08 disposition is **RETAIN OPTIONAL — CAPACITY ADEQUACY UNRESOLVED; SCALING STUDY REQUIRED BEFORE REJECTION**.

Phase C asks whether increased network capacity improves context-sensitive representation or behavior, whether changing the excitability-homeostat target explains those effects, and whether recurrent development influences behavior indirectly through learned motor-head state even when the **final recurrent-weight delta** is not load-bearing.

Phase B's six-seed behavioral advantage and approximately 2.31× effective dimensionality are background observations, *not* confirmatory Phase C outcomes. Phase B's raw cosine separation is sensitive to a common firing-rate offset; Phase B's gain bound may be a calibration artifact. Neither a larger network nor a recalibrated homeostat is presumed beneficial.

No Phase C decisive experiment, outcome probe, behavioral score, or capacity comparison may run before the C02 implementation, C03 audit, and exact comparison protocol validation. C01 itself is document-only; it changes no neural implementation, checkpoint, personality, subject-facing content, or prior experiment.

## Competing hypotheses and possible outcomes

- **H-CAP (capacity-limited representation):** From 4,096 to 16,384 neurons, held-out context discrimination improves under *both* native and calibrated homeostasis at matched exposure, without unacceptable behavioral regression. Higher dimensionality alone is not sufficient.
- **H-CAL (calibration limitation):** Correcting the upward saturation-target pressure substantially improves context discrimination or behavioral value at a fixed capacity, and/or an apparent capacity effect disappears under calibration.
- **H-MED (developmental mediation):** Allowing recurrent plasticity during developmental exposure changes subsequent action behavior through learning retained in the motor head or other non-recurrent state, even if reverting the final recurrent delta at test time has little effect.
- **H-NULL/H-TRADEOFF:** None of these causal mechanisms exceeds predeclared thresholds; improvements are noise/seed-specific, accompanied by loss of contextual behavior, or too expensive. Null and adverse findings remain valid outputs.

Mechanisms may coexist. A result may establish capacity dependence without establishing that recurrent plasticity itself is necessary.

## Frozen sizes and capacity normalization

The reserved B02 ladder is retained in order:

`1,024 → 4,096 → 16,384 → 65,536`.

The **primary confirmatory capacity contrast** is **4,096 vs 16,384**. The 1,024 rung tests low-capacity behavior and possible nonlinearity. The 65,536 rung tests a larger regime **only if it passes the outcome-blind C02 feasibility gate**. Feasibility must be assessed before any decisive Phase C results are inspected. Omitting 65,536 for measured infeasibility is allowed by B02 and must be documented; it is not evidence of a performance plateau.

The sparse recurrent fan-in is held at `avg_recurrent_degree=32` across sizes. Total recurrent edges thus grow approximately linearly, not quadratically, in neuron count; the exact deduplicated CSR edge count is recorded. `sensory_dim=512`, `input_degree=10`, `excitatory_fraction=0.80`, initial weight scale, decay, eligibility, Oja parameters, noise, neuromodulation, synaptic tagging, spectral-homeostasis band, input encoding and motor-temperature parameters retain their Phase B values unless explicitly varied below.

For comparability, **action_population_size=48 at every size**. This avoids the implementation's `min(configured_size, max(8, neurons//20))` rule silently shrinking a nominal 72-cell action population only at 1,024. This is a *new Phase C configuration* for **all** sizes, including 4,096, so C 4,096 results must be generated anew. Do **not** treat Phase B's 4,096 runs with action population 72 as identical C controls.

Every condition uses one initialized topology for a given (size, seed). Paired calibration and developmental-lesion conditions derive from the same initialized checkpoint for that (size, seed), so configuration changes do not inadvertently re-sample connectivity. Size comparisons share the same stimulus and outcome stream per seed but **cannot** share literal topology across sizes; same seed does not mean nested networks.

## Frozen experimental conditions

Two full-ladder Neural Convergence conditions (size × homeostasis) are decisive:

1. **NATIVE:** Unchanged opt-in convergence configuration except frozen size and 48-action population; `intrinsic_excitability_homeostasis=True`, `target_state_saturation=0.18`, `excitability_homeostasis_rate=0.015`, `min_state_gain=0.20`, `max_state_gain=1.20`.
2. **ZERO-TARGET:** Exactly the NATIVE settings except `target_state_saturation=0.0`. This removes positive gain pressure when saturation is zero, but the homeostat can still *reduce* gain if saturation rises. It is a target-calibration counterfactual, not a guarantee that gain remains exactly one.

Additional fixed-4,096 controls, using identical seeds and stimulus stream:

3. **GAIN-CLAMP:** Native convergence with `min_state_gain=max_state_gain=1.0`. The homeostatic rule remains enabled but cannot change the gain. This is a mechanistic sensitivity arm, not a third full-ladder factor.
4. **LEGACY:** Legacy v0.4, using the same 4,096, 48-action-population configuration, schedules and seeds. This is an updated within-C anchor, **not** a substitute for the immutable B04 control.

No additional calibration targets or doses may be selected based on results. Report both gain and actual saturation at every checkpoint; do not infer that a bound hit implies inadequate neurons.

## Frozen seeds, exposure, and comparisons

Decisive Phase C seeds: `3842, 3843, 3844, 3845, 3846, 3847`. These differ from Phase B's inspected `1842–1847` seeds. No seed may be replaced for an unfavorable result. Phase C deliberately uses a new confirmatory seed cohort; the existing B02-generated stimulus families and procedures remain public and known, so these are **new seeds, not a claim of wholly novel task families**.

Per seed, all conditions receive the *same*, manifest-hashed ordered stimuli, ordinary scalars, externally generated felt-state schedules where supported, confidences, teaching actions, and outcomes. The comparison harness must make these streams independent of neural size/configuration. Do not use network outputs to adapt the teaching curriculum. A control encoder ignoring optional convergence-only felt channels is an explicit profile difference, not a reason to alter the world sequence.

Freeze the B02 **5,120 step** timeline:
- 512 neutral stabilization steps, `learn=False`;
- 3,584 developmental steps, seven 512-step blocks in original B02 order with matched outcome schedule and `learn=True`;
- 512 held-out/seen/near-neighbor/opposite-context evaluation steps, `learn=False`, no outcomes;
- 512 checkpoint-restart equivalent evaluation steps, `learn=False`, no outcomes.

C02 must reuse B03 stimulus family definitions and hash each seed's complete generated curriculum, teaching/outcome schedule, and evaluation sequence **before** its first decisive step. The 4,096 and 16,384 conditions must have identical hashes within each seed. If the B03 harness needs mechanical extension for size/calibration, the new code and hashes must be independently reviewed in C03 *before* C04 results.

Capture identical frozen probe arrays at post-stabilization and post-development; record each block's anchor response. Ensure all analysis uses one fixed and documented evaluation ordering. No model renderer, personality prompt, or subject memories participate in these neural-only probes.

## Predeclared endpoints

### Primary A: centered held-out context discrimination

Take the 512 × N recurrent **firing-rate** matrix captured at evaluation, cast to float64, and subtract the per-neuron mean across the 512 evaluation rows. Divide each centered row by its Euclidean norm (norms below `1e-12` yield a zero row). Compute pairwise cosine on centered rows. Let `S_centered = mean(within_context_cosine) - mean(across_context_cosine)` over all unordered distinct probe pairs, using the exact B03 `probe.block` labels and no self pairs. Preserve seed-level numerator counts and values.

This **new Phase C preregistered** primary metric was only a *post hoc* falsification analysis in Phase B. The Phase B values and interpretations remain unchanged. Because centering across the whole evaluation batch is unsupervised but transductive, this is a contextual-geometry diagnostic, not a stand-alone proof of generalization or semantic competence.

Primary confirmatory comparison: paired `S_centered(16,384) - S_centered(4,096)` separately in NATIVE and ZERO-TARGET across the six seeds.

A capacity-specific positive signal requires **at least four of six seeds positive and median paired gain ≥ +0.02 absolute cosine-separation units in each homeostasis condition**, alongside the behavioral non-regression safeguard below. This is an engineering evidence threshold fixed before C outcomes, not a p-value.

### Primary B: meaningful behavior safeguard

Retain B03's mean probability assigned to the preregistered expected action over the same evaluation probes and the complete ten-action vectors. For capacity-specific positive classification, 16,384 must not lose more than `0.005` absolute expected-action probability versus matched 4,096 in median, and must not show a severe retention or opposite-context regression on four or more seeds. Report action entropy, margin, seen/held-out contrasts, and complete paired effects; a higher-dimensional representation without functional preservation does not earn a capacity-positive label.

The held-out expected action is a scripted measurement under this curriculum, not a validated general measure of character identity, subjective experience, or personality continuity.

### Primary C: calibration alternative

Compare ZERO-TARGET with NATIVE at each fixed size on centered context separation, expected-action probability, `state_gain` occupancy, and observed saturation. A calibration-specific signal requires at least **four of six** paired seeds favorable on centered separation with a **median gain ≥ +0.02**, plus the same behavioral non-regression safeguard.

Record whether the NATIVE 4,096→16,384 effect persists, disappears, reverses, or changes sign in ZERO-TARGET. An effect present only under NATIVE must be classified **capacity × calibration dependent**, not independently capacity-caused. A change in gain ceiling occupancy alone is a manipulation check, not behavioral improvement.

### Secondary geometry and stability

Also report without post hoc substitutions: **uncentered** within-minus-across cosine (the literal B02 endpoint), centered covariance participation ratio `(trace(C)^2 / trace(C^2))` computed using the B03 Gram-matrix method, effective-dimensionality fraction `PR/N`, per-neuron variance, context-opposite and block-anchor retention, non-finite counts, E/I sign violations, clipping-bound fraction, state saturation, per-block and per-step state-gain traces, recurrent spectral gain and corrections, motor entropy, restart equality, per-run time/RSS, checkpoint bytes, edge count, and rate of steps per second.

Dimension-scaled ratios must not be mistaken for absolute contextual information. Explicitly distinguish increased rank from functional separation.

### Multiple outcomes and uncertainty

Analyze **paired within-seed contrasts** first. Report all six individual results, median, min/max, directional counts, and a fixed-seed bootstrap 95% percentile interval with 10,000 resamples seeded `7301`, flagged **descriptive** given n=6. Do not cherry-pick favorable sizes, calibration arms, probe subsets, or alternate normalization. Only the above three primary decisions are confirmatory; all other comparisons are descriptive and hypothesis-generating. No single summary metric authorizes a production-default change.

## Developmental-mediation factorial: independent causal sub-study

At **4,096 and 16,384** neurons, for **both NATIVE and ZERO-TARGET** calibrations, execute the same six seeds in a frozen 2 × 2 intervention design from a common stabilized checkpoint:

| Condition | Recurrent synaptic plasticity during development | Motor-head learning during development |
|---|---|---|
| R+M+ | enabled | enabled |
| R−M+ | disabled | enabled |
| R+M− | enabled | disabled |
| R−M− | disabled | disabled |

The R intervention suppresses Oja/Hebbian/reward recurrent synaptic writes, recurrent weight decay attributable to learning, and outcome-dependent `capture_outcome` weight changes throughout the 3,584 developmental steps, **but** preserves ordinary recurrent dynamics, intrinsic excitability adaptation, and spectral homeostasis in every arm. The M intervention suppresses `reinforce_action` writes to `motor_w` and `motor_b` only, leaving equivalent externally scheduled teaching/outcomes and any allowed recurrent capture active. Preserve the same input, outcome, tick schedule, and probe order. C02 must implement these as explicit switches with no algorithmic side effects, and C03 must establish a sham and precise per-store write/no-write controls before C04 outcomes.

Contrast recurrent-development influence under motor learning (`R+M+ − R−M+`) against recurrent-development influence without motor learning (`R+M− − R−M−`) for mean expected-action probability and centered separation. The difference of those contrasts is an interaction suggestive of mediation. A provisional mediation signal on the behavioral metric requires a **median interaction magnitude ≥ 0.002**, the *same interaction direction* on **≥4/6 seeds**, and both intervention-control integrity checks. **An interaction alone is not proof of a uniquely identified causal pathway.**

For mechanistic localization, also preregister a post-development motor-head transplant from R+M+ to R−M+ and its corresponding same-source sham; transplant both `motor_w` and `motor_b`, not recurrent weights. Report change in expected-action probability and full action-vector JS divergence. Preserve the recipient recurrent state and topology. A transplant does not establish identity transfer; it tests contribution of a downstream learned component to the measured endpoint.

Separately reproduce B06's **final-delta reversion** on R+M+ as a terminal lesion. Interpret recurrent-development-on/off and terminal-delta lesions as distinct interventions; neither one licenses the statement that recurrent learning generally "does not matter."

The factorial's R+M+ arm is the **same** result as the corresponding main-ladder condition and must be reused, not rerun until favorable. The additional three 2×2 arms exist only at the two prespecified capacities.

## C02 outcome-blind feasibility gate and costs

C02 is a **technical-only** 256-step neutral, non-learning resource pilot for the four prespecified sizes and both calibration arms. It must use distinct pilot seeds `9342,9343`, with **no developmental training, no expected-action scoring, no context-separation calculation, and no inspection of unblinded Phase C outcome metrics**. Record runtime, peak RSS, checkpoint size, CSR nonzero count, finite state, and binary completion only.

A size is feasible for decisive Phase C only if both pilot seeds complete within **60 minutes per 5,120-step projected full run**, with projected peak memory **≤ 5 GiB** and projected per-seed artifact payload **≤ 2 GiB**, under a pinned supported runner. The projection method must be recorded and may use a conservative factor relative to 256 steps and measured save/evaluation overhead. C02 may reject a rung on resource grounds alone; it must not tune network architecture after seeing performance.

The total Phase C run budget is **120 GitHub runner-hours for decisive experiments**. Each matrix job has an **at most 90-minute wall-time limit**. If the predeclared budget is exhausted, preserve completed evidence, mark skipped/incomplete arms, and report the corresponding primary comparison **unresolved**, not negative or positive. The scientific protocol cannot choose a cheaper replacement rung based on preliminary accuracy.

If 65,536 fails outcome-blind feasibility, record the exact hardware/runtime evidence and omit that rung in accordance with B02. If 16,384 fails, the primary capacity hypothesis is **not evaluable** under this protocol; no smaller or better-looking contrast may be relabeled primary.

No direct production changes, paid infrastructure, external API calls, or neural checkpoint migrations are authorized.

## Failure, invalid-run, and artifact rules

Hard failures: wrong SHA, unapproved protocol/config or seeds, mismatched per-seed curriculum/outcome hashes, wrong topology pairing, non-finite state, E/I sign failure, invalid mask, broken checkpoint/restart, missing manifest, or failure of fixed-seed deterministic same-run replay. A technical failure is corrected by a **minimal documented harness repair**, followed by rerunning only invalidated affected arms. If a correction changes a scientific factor, outcome definition, threshold, learning intervention, seed, or lesson schedule, write a **new versioned preregistration before rerunning**, and preserve the invalidated history.

Stable but poor learning, plateau, high runtime within the feasibility envelope, context collapse, negative mediation interaction, or failure to transfer are **valid negative results** and must be reported.

Each decisive result must retain protocol version and frozen Git SHA; full config, size, seed, condition, source checkpoint hashes, curriculum/probe/outcome hashes, all phase times, evaluation arrays or auditably lossless summaries, motor/recurrent learned deltas, all measured outcomes, compute costs, repository SHA, Python/NumPy/SciPy versions, timestamp, result SHA-256, and an immutable CI artifact ledger. Artifacts are kept independent from human-readable result summaries.

## Fixed adjudication and production boundary

C04–C05 must classify and report, not optimize. Allowed research verdicts are **capacity-supported**, **calibration-supported**, **capacity×calibration dependent**, **mediation-supported provisionally**, **no measured support**, and **incomplete/unresolved**; combinations are permitted where warranted. All decisions must include the exact paired seeds and sizes checked and a nontriviality threshold status.

Regardless of outcome, **Phase C cannot itself promote Neural Convergence** to production default. Such a change requires separate independent causal evaluation, explicit cross-profile checkpoint migration, Subject Interface Firewall review, release testing, and a subsequent approved production PR.

Phase B's accepted data and interpretations must remain untouched. The user-facing Pretorius identity, autobiographical state, renderer inputs, and subject projections are completely outside this mechanistic experiment. No raw recurrent state, configuration, hypothesis label, action score, or engineering audit may leak to subject-accessible content.

## Next-step sequence

- **C01**: freeze this design *before* experiments; commit with clean ancestry from merged Phase B.
- **C02**: implement separate reproducible runner/config and outcome-blind resource-only feasibility probe; add focused tests. No full neural developmental results.
- **C03**: independently audit protocol fidelity, intervention isolation, seeds/hashes, and artifact validity before unblinding.
- **C04**: run the feasible frozen decisive capacity/calibration and developmental mediation matrices, including all preregistered nulls, with seed-level immutable artifacts.
- **C05**: integrate machine evidence, decide under the frozen thresholds, obtain independent review, and determine next research steps without touching production defaults.

Only one coherent Phase C research branch should be used. Phase B is already in production `main`; C01–C05 must not reopen or rewrite its accepted experiments.
