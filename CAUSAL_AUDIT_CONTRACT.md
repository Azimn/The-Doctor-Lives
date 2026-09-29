# Pretorius Causal Architecture Audit Contract

Version: `causal-audit-v0.3`

Production base: `001321b30fdbcde59e388ce907031788543611b6`

Governing issue: `Azimn/The-Doctor-Lives#9`

## Purpose

This version is a causal audit of the existing Pretorius architecture. It is not a new cognitive architecture and it does not change the default production decision path.

The audit asks whether manipulating an existing mechanism produces a predicted downstream change while matched state, stimulus, recurrent checkpoint, and renderer boundary are held as constant as the intervention permits.

## Temporary feature freeze

During this audit, do not add another planner, neural network, BDI system, global-workspace framework, reflection LLM, memory database/taxonomy, or agent chassis.

Allowed changes are:

- correctness fixes required to make an existing invariant true;
- deterministic lesion/control instrumentation;
- audit-only state cloning and neutralization;
- measurement renderers with no mutation authority;
- regression tests;
- durable per-condition traces and aggregate reports.

The state-to-policy bridge discussed in Issue #9 is a post-audit candidate, not part of v0.3.

## Mechanisms under audit

Matched interventions cover:

1. deep history;
2. needs/interoception;
3. relationship history;
4. commitments;
5. recurrent policy;
6. spreading activation;
7. sleep replay;
8. action reinforcement and durable action values.

Concerns are separately characterized for accumulation and persistent cognition triggering. The self-model is characterized for present causal reach without adding a self-model learner.

## Matched-state rule

Every ordinary lesion pair starts from a byte-identical cloned state directory. The harness records the source store digest and recurrent checkpoint SHA-256 before applying an intervention and fails if the two source conditions differ.

Lesions operate only on cloned audit state. The source state is never mutated.

Longitudinal interventions such as sleep replay and reinforcement intentionally diverge after the common starting state; their prelude is part of the intervention and must be recorded.

## Trace contract

Each causal trace preserves:

- intervention and disabled mechanisms;
- source and condition state digests;
- source and condition recurrent checkpoint hashes;
- exact stimulus;
- whether cognition occurred spontaneously or required a matched forced-think measurement;
- retrieval audit, including signed spreading contributions;
- policy decision and complete action-score distribution;
- selected records;
- felt needs;
- relationships;
- open concerns and commitments;
- durable action values;
- self-model state;
- renderer request;
- deterministic audit-render output;
- final store digest and recurrent checkpoint hash.

The deterministic audit renderer is measurement equipment. It is not Pretorius's language renderer and has no authority to mutate state.

## Primary measures

The primary outcome is causal influence on decisions and externally projectable behavior, not simple recall.

The standard pair report includes:

- selected-action divergence;
- action-score L1 distance;
- retrieval-set Jaccard similarity;
- selected-memory Jaccard similarity;
- renderer-request divergence;
- deterministic audit-render divergence;
- spontaneous-cognition divergence.

Recall, intrusion, and displacement remain secondary diagnostics.

## Interpretation rule

A mechanism whose lesion repeatedly changes retrieval or renderer context while leaving action scores and selected tendency unchanged is evidence of a state/action coupling gap for that mechanism under the tested conditions.

A null result is not proof that a mechanism can never matter. It is a simplification candidate only after an adequately designed battery yields stable null effects.

A simple mechanism with a repeatable causal effect is retained regardless of whether it resembles a fashionable cognitive architecture.

Production lesion results are software-level causal characterization. They do not establish consciousness, biological equivalence, or human cognition.

## Frozen production behavior

Importing or installing causal-audit instrumentation must not change `PretoriusBrain` behavior when no intervention is active.

All existing architecture invariants remain binding, including:

- Calibos structure-only;
- renderer neutrality;
- tool authority outside the brain;
- provenance and epistemic autobiography;
- archive-never-delete;
- sleep/waking-clock isolation;
- signed retrieval-time spreading activation;
- canon-conflict retrieval enforcement;
- neural-policy audit.

