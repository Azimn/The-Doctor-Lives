# Pretorius Causal Architecture Audit v0.3 — Results

Production base: `001321b30fdbcde59e388ce907031788543611b6`

Audit code: `b584cc12ec3ecca69f3b982300b7b71ffc6dc5cf`

Workflow: causal-architecture-audit run `36624790522` (PASS)

Complete machine-readable traces:
- `audit.json`
- `summary.json`

## Scope and interpretation

This is production software causal characterization from a controlled lesion battery. It is not evidence of consciousness, biological equivalence, or general human cognition.

Matched ordinary lesion pairs began from the same cloned store digest and recurrent checkpoint. Runtime UUIDs were canonicalized into semantic memory signatures before retrieval/renderer comparisons so random IDs could not create false divergence.

## Main result: the state-to-policy gap is real

Four mechanisms altered downstream context without altering the recurrent action distribution at all:

| Mechanism | Action-score L1 | Selected action changed | Retrieval Jaccard | Renderer request changed |
| --- | ---: | --- | ---: | --- |
| Deep history | 0.000000 | No | 0.6875 | Yes |
| Needs/interoception | 0.000000 | No | 1.0000 | Yes |
| Relationships | 0.000000 | No | 1.0000 | Yes |
| Commitments | 0.000000 | No | 0.8667 | Yes |

This is the architecture-level memory/state-action gap anticipated in Issue #9. These states can alter what the renderer sees, but under the tested conditions they exert no pressure on which of the ten action tendencies wins.

Deep history had the strongest contextual effect in this battery: removing it changed both the retrieved set and selected memory set substantially, but the policy distribution remained numerically identical.

## Recurrent policy is causally load-bearing

Lesioning the recurrent policy produced:

- action-score L1 distance: `0.0285699106`
- selected-action divergence: **yes**
- renderer-request divergence: **yes**

Within the ordinary single-probe lesion matrix, recurrent policy was the only mechanism whose removal changed the selected action.

This supports retaining the recurrent substrate as a real decision variable rather than treating it as decorative state.

## Reinforcement result

The longitudinal reinforcement control separated the two learning/accounting paths:

**Neural reinforcement removed**
- action-score L1: `0.1187711398`
- selected action changed: **yes**
- selected-memory Jaccard: `0.6`

**Durable action-values neutralized after otherwise intact reinforcement**
- action-score L1: `0.0`
- selected action changed: **no**
- retrieval Jaccard: `1.0`
- renderer request changed: **no**

Therefore the recurrent reinforcement path is behaviorally causal in this battery. The durable `action_values` table is currently accounting state, not a decision variable.

## Sleep replay

Removing the sleep-replay prelude produced a small but nonzero policy difference:

- action-score L1: `0.0006832369`
- selected action changed: **no**
- renderer request changed: **yes**

Sleep replay therefore has measurable downstream effect in this run, but the effect was much smaller than direct reinforcement and did not cross the action-selection boundary for this probe.

## Spreading activation

The spreading-activation lesion produced no downstream difference in this specific probe:

- action-score L1: `0.0`
- retrieval Jaccard: `1.0`
- selected-memory Jaccard: `1.0`
- renderer request changed: **no**

This is a null result for this battery, not evidence that spreading can never matter. It should receive a broader topology-targeted battery before simplification or removal.

## Self-model

Removing the current self-model produced no measured difference:

- action-score L1: `0.0`
- retrieval Jaccard: `1.0`
- selected-memory Jaccard: `1.0`
- renderer request changed: **no**

The present self-model is therefore causally disconnected from the tested decision and renderer paths. This is consistent with code inspection showing no ordinary developmental update path.

## Concern accumulation failure mode confirmed

Five lexically distinct high-pressure events produced five open concerns.

Afterward:
- a neutral event still warranted cognition;
- four neutral heartbeats produced four thoughts;
- no public `resolve_concern` method exists.

This confirms the predicted persistent-high-alert failure mode. Concern lifecycle/resolution is an evidence-backed correction candidate.

## Architectural consequence

The next architecture change should be small and explicit rather than another framework.

The audit supports a bounded, deterministic, auditable **state-to-policy bridge** upstream of action selection, using only existing state. The strongest currently disconnected candidates are:

1. needs/interoception;
2. relationship state;
3. commitments;
4. relevant autobiographical/history evidence;
5. concern state, after a proper lifecycle/resolution mechanism exists;
6. durable action values, if retained rather than removed as redundant accounting.

The recurrent action distribution should remain the baseline phenotype contribution. The bridge should add bounded pressures and preserve the pre-bridge and post-bridge score vectors in every policy audit.

The self-model should not be connected merely because it exists; it first needs a defined developmental and evidentiary role.

Spreading activation should not be promoted into the bridge based on this null probe.

## Completion judgment

v0.3 answers the question it was designed to answer: the architecture contains several meaningful state systems, but most currently affect context rather than action selection. The recurrent policy and recurrent reinforcement pathways are demonstrably causal. Concern lifecycle is incomplete. Action values and the self-model are currently inert in the tested pathways.

The next production version should address those measured deficits without adding another cognitive framework.
