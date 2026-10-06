# Pretorius v0.5 RC1 Assessor Review

This file defines the single review surface for the current Pretorius production handoff.

## Review target

Repository: `Azimn/The-Doctor-Lives`

Branch: `release/pretorius-v0.5-rc1`

Package version: `0.5.0rc1`

This release candidate replaces the prior practice of treating multiple feature branches as competing production candidates. The historical branches remain available as provenance and experimental evidence, but this release branch is the only integration target to assess.

## Consolidated source lines

| Source line | Exact source head | Status in RC1 |
| --- | --- | --- |
| Pretorius v0.4 state-to-policy | `3500d4c31fc8b5d0289ae8e6312dd8f868794aaa` | Included as production-default behavioral baseline |
| UPPB P0-P6D | `06b8fec7cc2953defb384851f335f15ab8538375` | Included as complete standalone subjective-memory and phenomenal subsystem |
| Neural Convergence v0.5 | `cf009630f1c623b0bcac1eb9e5e7242fa3e8a0e7` | Included behind explicit opt-in neural profile |
| Deep-History v2 | `001321b30fdbcde59e388ce907031788543611b6` | Included through v0.4 lineage |

## Production authority

The production-default behavior is the accepted v0.4 path. This is not because later work is discarded. It is because both later research lines were deliberately designed with controlled promotion gates.

UPPB P0 through P6D is part of the package and is fully regression tested. It preserves protected evidence, reconstruction lineage, source monitoring, reconsolidation audit, omission-aware degradation, and structured temporal generalization. It does not yet replace the live Pretorius subject-facing path. That remains a future explicit migration rather than an accidental side effect of consolidation.

Neural Convergence is part of the existing `PretoriusRecurrentSubstrate`, not a second brain. The accepted v0.4 configuration remains the default control. `NEURAL_CONVERGENCE_CONFIG` enables Oja-style local competition, bounded neuromodulated plasticity, provisional synaptic tagging with delayed outcome capture, recurrent-gain homeostasis, intrinsic excitability regulation, correlated endogenous variation, restart-safe neural state, and felt-interoception input channels.

## Required assessor invariants

The assessor should reject RC1 if any consolidated mechanism acquires identity authority, if Calibos identity material enters Pretorius, if protected evidence can be rewritten by subjective-memory operations, if UPPB first-person state overwrites mechanistic truth, if renderer or chassis code gains canonical identity authority, if sleep advances waking time, if neural convergence silently becomes the default control, if hidden homeostatic actuals become subject-accessible, or if the 70-node Persona Connectome is silently rewritten into neural ground truth.

The assessor should also verify that the recurrent network remains causally load-bearing, the v0.4 state-to-policy bridge remains bounded and audited, deep-history provenance remains intact, and the exact release head passes the full test suite on both GitHub Actions paths.

## Deferred work that is not claimed complete

RC1 does not claim live UPPB migration, arbitrary false-memory generation, P7 through P11, direct mapping of the 70-node Persona Connectome into recurrent neural populations, biological equivalence, consciousness, or a completed external chassis deployment.

Those are intentionally outside this review gate. Their absence is not hidden technical debt inside the claimed RC1 scope.

## Validation command

From a clean checkout:

`python -m pip install -e .`

`python -m unittest discover -s tests -v`

The pull request description records the exact-head push and pull-request workflow run IDs used for the final handoff.


## Assessor correction gate

Following independent review of the initial RC1 head, this release line now requires four additional invariants before acceptance:

1. Low-pressure `ingest()` must use the same query-aware direct pre-spreading history retrieval semantics as the thinking path without changing the cognition-trigger threshold.
2. Causal-audit identity and clock data must be deterministic within the audit harness only; production UUID and wall-clock behavior must remain unchanged. A release workflow executes the complete audit twice in independent directories and requires byte-identical canonical outputs.
3. An explicitly supplied neural configuration for an existing checkpoint must match the persisted configuration exactly or fail closed with an explicit migration-required error. No implicit checkpoint migration is permitted.
4. The archived v0.4 causal workflow is read-only in this release tree: manual dispatch and repository writeback are removed.

These corrections do not reopen the accepted v0.4 bridge design, Deep-History v2, UPPB P0-P6D, or Neural Convergence mechanisms.
