# Eidolon E5-P0A: Real cognitive-policy-to-primitive-laboratory adapter (pre-execution protocol)

**Status:** preregistered development-corpus comparison, not blinded/independent cognition evidence. **Date:** 2026-10-10. **Source:** [E5-P0 world's public cases](../research/eidolon_e5_dev_cases.json), [E5-P0 results](../results/eidolon/E5_P0_OUTCOME_LAB_RESULTS_V01.md), [E4-C's frozen balanced decoder](../results/eidolon/E4C_BALANCED_DECODER_RESULTS_V01.md). Commit this protocol before source, tests or execution.

## Hypothesis and scope

Test whether **actual native `PretoriusBrain.think()` outputs** and **actual E4-C Noetic native sparse-W / balanced-decoder predictions** can drive concrete world actions under a single observation-only adapter, without silently substituting the engineered 6/6 keyword solver. The test may fail all tasks. No code should claim success by replacing a neural class with an oracle action.

## Frozen policies and equivalent interface

Evaluate the same six *already-inspected public development cases*, with six primitive steps at most per case, each starting from an identical E5 world snapshot:
1. `native_pretorius`: independent disposable `PretoriusBrain` initialized with existing default v0.4 policy bridge and a 128-unit native neural substrate (`seed=151`); feed it a serialized **public observation**, advance native recurrent `step(...,learn=False)` to process that observation, and call actual `PretoriusBrain.think(...,bridge_enabled=True, decision_text=<public observation>)`. Record exact native selected action, top ten policy scores and source state audit. No world terminal expected predicates reach the brain. No canonical Pretorius production state is touched.
2. `noetic_balanced`: frozen E4-C Noetic-trained W and readout from E4-A's development cues, using seed 151 and 160 synthetic training events. Predict ten native actions from the same public observation via `native_features`. No retraining on E5 tasks or objective labels.
3. `noetic_virgin_W_lesion`: **same** trained Noetic readout (unchanged weights and centering), with trained native W replaced with the same-seed virgin W. An ablation, not another independently trained model.
4. `fixed_reservoir_balanced`: untrained virgin W with equally fitted balanced decoder using exactly the same E4-A cues/labels. This is the E4-C decoder-only control.
5. `keyword_baseline`: the existing E5-P0 scripted task-specific benchmark, retained as **exposed six-case upper engineering reference**.
6. `no_op`: exact E5-P0 negative reference.

The three E4-C-based arms have **identical** teacher information and frozen test parameters; Pretorius uses different existing background biography and training budget, so native-vs-neural results are **descriptive**, not a matched-training causal comparison. The *within-Noetic* W swap is the narrow recurrent intervention.

## Fixed public action translator — never a planner

The shared `ObservationActionAdapter` enumerates only publicly observable or physically attemptable candidates from `public_observation()`:
- `inspect`: any uninspected object
- `read`: book pages 1–3, excluding pages already read. A fixed affordance limit; the adapter is told neither a book's hidden total page count nor a task's target page.
- `bookmark`: only a page that was previously read
- `move`: inspected object to any named room other than its current location
- `repair`: inspected damaged apparatus with a publicly read first manual page
- `attribute` / `reject`: any unreviewed claim, even if it appears suspicious; the world retains veto authority
- `resolve`: any open commitment, regardless of physical outcome; auditor independently detects false completion
- `wait`: always offered.

A permanent, **task-agnostic** mapping from each of the ten neural action classes to primitive verb families is precommitted in code and documented in the result. The adapter must choose the top-ranked *actual neural policy class* unconditionally. It may choose a public operand among candidates of that class using fixed lexical overlap with the public goal/prompt; ties break by deterministic full-action JSON. If there is no candidate for the selected class, it **waits**; it may not search down the score ranking until it finds a conveniently achievable action. **No multi-step plan, force-success shortcut, hidden predicate access or special case-name logic** is permitted. Strict logs must show both raw policy tendency and the translated primitive, including `wait` and premature `resolve`.

Every E5 world feedback and observation is common to the policy; neural models do not receive private goal scoring, case IDs or human-designed action sequences. The adapter does not acquire authority to mutate lived memories. `think()` may write thoughts to its **disposable Pretorius brain clone only**. Preserve a separate E5 world/state ledger, reload it after every episode, and verify clone roots do not cross-contaminate.

## Primary measurements and negative controls

For each arm/case retain source snapshot hashes, raw ten-way probabilities, selected categorical neural action, available candidate verbs, translated action and operand, exact environment feedback, final objective predicate checks, action counts, actor/false autobiography attempts, and replay hashes. No-op and scripted baseline results must reproduce E5-P0. Enforce the same action budget and world public view for all. Record `no_valid_affordance` abstention separately from a world-denied action.

Critical tests: the same public observation produces the same candidate list regardless of case expected predicates; world rejects forged actor/source even when Noetic asks to `attribute`; counterfactual W transplant preserves Noetic readout and action interface; native `think()` truly runs; neural output is never replaced by the scripted task-solver.

**Success** of P0A is the experimental integration and accurate outcome measurements, **not** a positive neural improvement. A genuine recurrent advantage would additionally require Noetic to outperform its fixed-reservoir and W-lesioned controls on new independently authored E5-P1 cases, losing that gain when W is swapped. Do not retune this public case bank. Keep PR #36 draft and production Pretorius unchanged.
