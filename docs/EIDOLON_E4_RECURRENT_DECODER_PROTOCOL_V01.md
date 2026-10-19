# Eidolon E4-A: Recurrent-versus-Decoder Causality Probe, Preregistered Construction Experiment

**Status:** development-authored, pre-execution protocol. **Date:** October 9, 2026 (America/Chicago). **Location:** The Doctor Lives, Eidolon research branch, NOT production.

## Problem

Eidolon D3-S found real policy flips and reliable source gating on 240 matched-clone decisions, but `persist` was indiscriminately selected across substantively different goals. Before inventing more controls, test the strongest mechanistic alternative: a decoder can acquire output labels while the recurrent substrate contributes little durable, action-specific learned signal. The result of Experiment 001 in Pretorius Neural Network makes this a standing risk.

## Subject and intervention

Use the *existing* `doctor_lives.neural.PretoriusRecurrentSubstrate`, initialized from identical seeded virgins for all arms. This is a research pilot on real Pretorius neural code, not a production brain state. Do not train the definitive Pretorius checkpoint or import fictional biography as training truth.

Six prespecified seeds: **11, 29, 47, 83, 113, 127**. Small test profile: `neurons=128`, `sensory_dim=64`, `avg_recurrent_degree=8`, `input_degree=4`, `action_population_size=8`, `plasticity_interval=4`, `motor_lr=0.025`, with all other parameters on the current `DEFAULT_CONFIG`. Only actions `create`, `persist`, `cooperate`, `challenge` are teacher labels; all ten production action scores remain available to the decoder.

### Fixed synthetic task design

Four goal families are deliberately labelled by their intended cognitive action, with **two distinct cue constructions per family** at training and **two different constructions** at test. Examples: constructing a mechanism → `create`; keeping a repair promise → `persist`; coordinating with another actor → `cooperate`; refusing an unsafe demand → `challenge`. Actors, objects and episodic identifiers must be partitioned by train/test, so the test has **no exact actor or episode repetition**, though generic connective words overlap. Test includes (1) directly after a cue and (2) after **three identical no-cue delay steps**; no supervised label or `action` argument is presented at evaluation. The fixture must record disjointness assertions and a frozen SHA-256 hash of its cases. Hand-authored labels are *not* independently adjudicated behavioral outcomes.

All conditions get identical ordered experiences, episode resets and prediction opportunities. Where `learn=False` is used, this is an explicitly named recurrent-plasticity lesion, not a different number of training examples. Controls that train decoder `motor_w/motor_b` must see the same teacher labels/steps. All reinforcement uses the repository's native `reinforce_action`; the recurrent learning condition uses the native `step(..., learn=True, reward=+0.75)`. The control uses the native `step(..., learn=False, reward=+0.75)`. Labels are not injected as a separate input channel during inference. Decoder receives supervision after the cue state is formed.

### Conditions evaluated from matched learned checkpoints

1. **hybrid**: plastic recurrent + trained motor decoder.
2. **decoder_only**: recurrence held fixed, same motor-decoder supervision.
3. **hybrid_recurrent_lesion**: hybrid-trained decoder and all other learned state, but replace trained recurrent matrix with its *same-seed virgin version* at evaluation; reset dynamic state. If original recurrent weights barely changed, report effect size and interpret accordingly.
4. **hybrid_fresh_decoder**: trained recurrent with same-seed virgin motor weights and bias; no decoder retraining. This is **not** the full E4 new-decoder transfer test; it is the cheap zero-shot control.
5. **hybrid_virgin_recurrence_trained_decoder**: same-seed virgin recurrent weights with hybrid's trained decoder, explicitly paired to condition 3; retained as an alias/check if numerically identical and reported as such, never double counted.
6. **untrained**: virgin recurrent and virgin motor; no learning.

Add a **shuffled-label decoder control**, trained with deterministic class-label permutation while receiving the same experiences and decoder update count. Report intended-label accuracy rather than score on its permuted teacher as a negative check.

### Metrics and nulls

For every seed, task, arm and direct/delayed condition, retain ten-action probabilities (or probability of target plus selected action and sum), top-1 correct on all ten actions, cross-entropy of the intended action, neural recurrent matrix change norm, motor decoder change norm and training/test timing. Full JSON stores per-row trials. Aggregate macro top-1 and mean target probability by arm/time; report per-seed rates rather than only pooled successes.

The **primary diagnostic** is the difference in held-out delayed target probability and top-1 between **hybrid** and **decoder_only**. A positive recurrent-learning claim *also* requires that replacing trained recurrent weights with the virgin recurrent matrix materially harms hybrid test behavior. A hybrid result that follows its decoder into a virgin recurrent state is evidence AGAINST meaningful learned recurrent identity under this pilot. Fresh-decoder performance need not be good in an unaligned action basis, and by itself proves neither benefit nor failure.

Do NOT select the best seed, modify post hoc task labels, tune parameters against the test split, or claim significance/generalization from developer-authored fixtures. No recurrent neural plasticity improvement shall be asserted solely because weights changed: measure whether held-out actions changed in the right direction.

### Safety and software requirements

The experiment must touch only new files `scripts/run_eidolon_e4.py`, `tests/test_eidolon_e4.py`, the dedicated research CI workflow, and versioned documentation/results. Leave `doctor_lives/neural.py`, `doctor_lives/cognition.py`, production state, checkpoint schema and UPPB unchanged. Require deterministic replay at a fixed seed; fail on invalid action distribution, nonfinite weights, train/test actor crossover, or stateful evaluation leakage. A single small-seed smoke suite and six-seed CI report suffice for this construction stage. Use clear result statuses: software gate, recurrent causality gate, external validity gate.

### Acceptance and next step

Passing means a *runnable, measured* native-substrate causal comparison with honest nulls. Recurrent advantage and decoder-independent identity are **not presumed**. If the result is inconclusive or near chance, preserve the null and do not merge to production. Only then design a stronger E4-B experiment with an independently sealed task bank and separately trained fresh-decoder transfer; current fresh-decoder weights are deliberately virgin, not calibrated.
