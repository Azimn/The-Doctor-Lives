# E4-B development assay v0.1 — Action-conditional Noetic Crucible

**Pre-execution protocol / status:** Development experiment, not a sealed independent test or production-authorized migration. The same E4-A lexical training/held-out cases were previously inspected; this experiment **cannot** establish external validity. Refer to [E4-A's corrected negative result](../results/eidolon/E4_NATIVE_RECURRENT_DECODER_RESULTS_V01.md).

## Hypothesis and falsifier

Test whether giving **native Pretorius recurrent synapses** a goal/action-dependent eligibility signal changes held-out decisions beyond (a) a motor decoder trained for the same number of examples, (b) class-balanced example order, and (c) a freshly trained readout with frozen virgin weights. Define retained learned-recurrence advantage before seeing outcomes as: greater delayed top-1 *and* lower mean target log-loss than decoder-only, and degradation of both when the trained W is transplanted back to same-seed virgin W. If only the motor decoder matters, or all arms make a constant choice, report **negative**.

The tested pathway is a **proposal**, not a validated biologically local plasticity model:
```text
pre_j = rate_j - target_rate
post_i = rate_i - target_rate
eligibility_ij <- 0.90 * eligibility_ij + post_i * pre_j
error_a = onehot(target)_a - p_a
feedback_i = mean(error_a for a whose initial motor population includes i)
delta_W_ij = eta * feedback_i * eligibility_ij
W <- clip to sign and original fixed spectral constraints
```
The feedback uses the **fixed, seed-generated native action populations**, not held-out labels or learned decoder weights. Do **not** provide target label to `step` during evaluation. `feedback` must be computed from an explicitly supervised **outcome at training time**, never an external unverified claim.

## Experiment lock

- Seeds: `[151,167,179,191,211,223]`, 128-neuron version of the native Pretorius substrate; same architecture/hyperparameters as corrected E4-A, `plasticity_interval=4`; **160 training cue presentations**.
- Input cases: reuse exactly `scripts/run_eidolon_e4.py::cases`, including 32 training, 16 held-out, separate training/test actors, objects, episodes and templates. Record fixture SHA. This data was previously inspected, so this is not independent confirmation.
- **Round-robin across four classes, fixed order** for every arm to neutralize E4-A's blocked-class final-label confound (classes listed `create,persist,cooperate,challenge` and items interleaved position-wise); do not tune ordering after seeing results.
- Native `PretoriusRecurrentSubstrate.step(cue, learn=False)` computes the neural state in all arms. In Noetic arms, apply one **explicit action-conditional three-factor update** to the existing same-seed sparse W after the cue and after motor `reinforce_action`. Never also run native generic Hebbian updates, so the mechanism is isolated. Frozen/W-lesion arms receive the same cue presentations and motor teacher. Set `eta=0.05`, `eligibility_decay=0.90`, `weight_update_clip=0.02` per synapse per event, and enforce native sign/max-weight protection. These are fixed engineering defaults, not tuned against held-out data.
- Label-conditioned feedback must be withheld when a proof token is from an external statement, simulated false claim, wrong actor or unverified outcome. An *offline fixture grant* is a manifest-derived assertion for testing; **not an authenticated Pretorius lived event**. Do not claim the E4-B evaluation trained on real autobiographical evidence.
- Arms: `noetic_hybrid`, `decoder_only`, `noetic_recurrent_lesion`, `noetic_fresh_untrained_decoder`, `noetic_fresh_trained_decoder` (train a newly initialized motor on frozen trained W, equal 160 cues), `virgin_recurrence_fresh_trained_decoder` (equal fresh training on frozen virgin W), `shuffled_outcome_noetic`, `virgin`. Recurrent-lesioned arm must have **exact same trained motor weights** as intact and same-seed virgin W, not merely zero W.
- Direct and delayed evaluations after **0, 3, and 12 input-free steps** with no updates, paired identical held-out inputs across arms. Every case begins with reset dynamic state; outcome metric is full ten-action probability, top-1 accuracy on four balanced labels, log loss, class diversity, and explicit per-seed counts. Enforce no test-time parameter changes and report W/motor change norms.
- Audit `training_grants` with a strict synthetic manifest evidence class and `verified_outcome=True`. Test that a disallowed grant cannot change W and that selecting wrong actor/source fails the positive gate. This validates API isolation only, **not** actual authentication of source.
- Stop/go: a software pass requires nonzero W update for Noetic, exactly zero for decoder-only, stable finite weights, exact graft equivalence, equal train steps, repeatability and no production writes. A behavioral pass separately requires the prespecified lesion-specific advantage over decoder-only. Do not merge on a favorable subset; publish every seed and negative.

The fresh trained readout controls test **representation transfer**, but they are not full cross-model renderer swaps or independent experimental validation. Production Pretorius, canonical database, Subject Frame and checkpoint format remain unchanged.
