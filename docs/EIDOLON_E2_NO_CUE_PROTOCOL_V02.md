# Eidolon E2: No-Cue Prospective Intention, Construction Protocol v0.2

**Date:** 2026-10-09 (America/Chicago). **Status:** fixed development-time construction protocol, NOT an independently sealed confirmatory study. Parent: [Eidolon Engine full architecture](EIDOLON_ENGINE_FULL_ARCHITECTURE_DRAFT_V1.md). The prior v0.1.1 top-1 recurrence lesion was negative: cue reactivation through current input survived state reset on all four cases.

## Experimental question

Can the current shadow Eidolon Engine hold an explicitly taught action tendency for a fixed number of **input-free** neural-state transitions, then change an engineer-only counterfactual policy when no cue is supplied at readout? This experiment isolates the information-flow necessity of the Noetic Trace under its present fixed-decay implementation. Success is a construction-level result and **not** evidence of learned recurrent synaptic weights, history-sensitive reasoning or actual Pretorius action choice.

## Frozen state-transition path

At training tick `t0`, a valid projected `Experience` associated with a labeled prospective action is admitted by the existing Janus Gate. This adjusts the Synthema associative matrix through the existing supervised delta rule, then sets a bounded trace from the learned association. During the delay, `advance_without_cue(n)` changes the recurrent trace only by `lambda ** n`; it must never encode a percept, train weights or consult the symbol/actor again. At final time, `probe_intention(base_scores)` returns counterfactual engineer-only policy probabilities from the current trace, without looking up the cue again or updating state. A matched `probe_intention(..., lesion_recurrence=True)` reads an identically trained state with the trace masked.

The no-learning and binding-lesion controls must never load the target association. The cue-only control receives identical supervised training but has no retained recurrent trace at final readout. Label shuffle gets identical exposure but an alternative target. All conditions undergo the same number of no-cue advancement ticks. These are deterministic, pre-specified, algorithm-tailored construction cases, so do not compute inferential significance or promote as confirmatory behavioral evidence.

## Original four construction cases

| Text stimulus | Actor | Target |
| --- | --- | --- |
| Cobalt bell behind the window. | Henry | create |
| Amber ribbon above the doorway. | Henry | challenge |
| Silver needle inside the drawer. | Henry | cooperate |
| Crimson ladder by the chimney. | Henry | persist |

Each case starts with ten-action uniform base policy, is trained exactly once in its own independent shadow engine, then undergoes **three** input-free decay ticks before final readout. Report target probability, 10-way top-1 action and exact condition denominator. A no-learning no-cue control must yield exactly the uniform prior. Additionally test a no-cue shadow against a real Pretorius neural action-score vector, a no-learning unknown-cue case, state snapshot/reload, repeated read-only probes, and input validation.

## Primary engineering acceptance

For all four hand-selected cases, final target probability under intact trained trace must exceed final target probability under matched cue-only, recurrence-lesioned and no-learning controls. No-cue top-1 should favor its training target for intact and should not be interpreted as meaningful generalized behavior. Exact effect magnitude and any failures are recorded permanently.

The stronger original E2 hypothesis, that learned *recurrent neural synapses* are required for future Pretorius behavior, **remains untested** here because `NoeticTrace` is fixed-decay state, not a learned recurrent synaptic circuit, and returned action probabilities are not enacted by the subject.

## Implementation and authority constraints

Existing `EidolonEngine.observe` semantics and v0.1.1 measured outputs must remain unchanged. New no-cue methods must reject negative/Boolean tick counts, invalid action-score inputs and nonfinite states. Read-only probing must not update tick, weights, trace, production state, or any Subject Frame. Source provenance is evaluated at training time through the existing Janus Gate, not inferred retroactively from a textual claim. Module and tests must be included in the existing research CI job, with a versioned JSON artifact.

## Post-assay decision

If this no-cue construction check passes, document it as **expected information-flow isolation**, not evidence of intelligence or identity continuity. Then design E3 with genuinely independent, actor- and episode-disjoint, prospective-goal tasks and actual audited Pretorius decision effects in cloned state. If E2 fails, preserve the result and investigate state decay, accidental cue leakage or false assumptions before adding new modules.
