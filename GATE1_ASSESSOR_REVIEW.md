# Gate 1 Persistence and Migration Hardening Assessor Review

## Review subject

This review subject is the post-RC1 persistence and migration hardening phase for Pretorius in The-Doctor-Lives. The accepted v0.5 RC1 production merge remains the architectural base. This candidate does not reopen the accepted recurrent policy, Deep-History v2 semantics, UPPB P0 through P6D, the Persona Connectome, the renderer boundary, or Neural Convergence promotion status.

Authoritative base commit: 288cb14ab9b65adbf2d916c4eb597e2a9dfd0301.

Accepted RC1 source parent preserved by that merge: d1567f3243b928b9086ba2b13ce59ee345fe1009.

Review branch: prod/gate1-evidence-integrity.

Candidate package version: 0.5.0rc2.

The final exact review SHA and final push and pull-request workflow run IDs belong in the pull-request description because adding those values to this file would itself change the exact review SHA.

## Scope

| Surface | Candidate behavior |
| --- | --- |
| Canonical evidence | Versioned manifest, content-digest verification before cognition, immutable state-local snapshots, fail-closed corruption detection, append-only recovery, protected-reference verification |
| SQLite durable state | Schema version inspected before mutation, future and malformed versions rejected, pre-migration SQLite backup, rollback restoration, structural post-migration validation, migration lineage |
| Recurrent checkpoint | Versioned checkpoint format, legacy RC1 compatibility, structural validation, atomic write-validate-replace, interrupted-write preservation |
| Clean install | Non-editable wheel installed in an isolated virtual environment outside the checkout, production-size state created and restarted |
| Offline runtime | Validation installs a Python audit hook that rejects socket operations after installation and records any attempted network event |
| Historical migration | Exact commit 7be60ed46add7c74359b322cc033aa7dfabb08e8 executes old code to generate a real state directory, then the current candidate migrates and restarts it |
| Physical user-machine validation | Procedure is documented, but Issue #8 remains open until a fresh end-user machine or equivalent external environment supplies preserved evidence |

## Frozen architecture retained

The accepted production-default recurrent path remains the legacy v0.4 control. Neural Convergence remains opt-in and is not promoted by this candidate.

UPPB P0 through P6D remains outside the live Pretorius subject-facing path. This candidate does not implement P7, does not create subject-facing cue producers, and does not weaken protected-truth versus subjective-memory boundaries.

Deep-History v2 evidence classes, source custody, wording provenance, canon authority, and the rule against silent promotion into lived memory remain unchanged.

The language model remains outside persistence authority. No renderer, plugin, prompt, hosted model, or external account becomes necessary for the core mind to boot, persist, retrieve history, render an audit request, or restart.

## Canonical evidence evidence

The candidate introduces doctor_lives/data/canonical_evidence_manifest_v1.json and doctor_lives/evidence_authority.py.

Startup verifies the installed distribution before opening the cognitive store. The manifest identifies the admitted bootstrap, Deep-History corpus, Deep-History policy, evolution policy, Persona Connectome, seed agenda, and source manifest by exact Git blob content digest.

Pretorius uses a verified state-local evidence snapshot after startup. Recovery never repairs the damaged active snapshot in place. It verifies the installed distribution, creates a new snapshot, validates it, records an audit event, then advances the active pointer. The damaged snapshot remains available for forensic inspection.

The SQLite state records the exact manifest version and fingerprint it adopted. Partial binding, manifest rollback, missing artifacts, modified artifact bytes, and mismatched protected references fail closed.

## SQLite migration evidence

BrainStore no longer runs SCHEMA and then unconditionally rewrites schema_version. Existing state is inspected first.

A state whose schema version is newer than the runtime is rejected before schema mutation. A malformed or missing version is rejected. A database that declares the current version but lacks required structure is rejected rather than silently repaired.

Supported older state receives a complete SQLite backup through the SQLite backup API before migration. The snapshot is content-addressed with SHA-256 and retained under migration_snapshots. If migration or post-migration validation fails, the active database is restored from that exact snapshot.

The deterministic fixture suite exercises schema v2 to v6 preservation of lived memory, relationship state, commitment state, needs, tick, rollback behavior, future-schema rejection, malformed-version rejection, and idempotent reopen.

The stronger workflow path executes historical commit 7be60ed46add7c74359b322cc033aa7dfabb08e8 itself to generate an older Pretorius state directory. That directory contains lived and external events, a commitment, Deep-History v1 state, and a recurrent checkpoint before current code opens it.

The historical migration artifact at implementation head acbb059ae12a56c3fa4681fef90fd37bf7501dda reported source schema 2, target schema 6, Deep-History v1 to v2, canonical evidence manifest version 1, preserved lived memory, preserved external statement, preserved commitment, zero unclassified autobiographical memories, zero legacy autobiographical classes, zero invalid wording records, and restart idempotency.

## Recurrent checkpoint evidence

New recurrent checkpoints carry checkpoint_schema_version = 1. RC1 checkpoints without this field are treated as legacy schema 0 and remain loadable only after structural validation.

Checkpoint writes now target a temporary sibling file. The file is flushed and fsynced, re-opened for structural validation, then atomically replaces the active checkpoint. A simulated interrupted write proves that the prior checkpoint remains byte-identical and loadable.

Loading validates required arrays, configuration JSON, neuron-dependent state shapes, CSR dimensions, eligibility alignment, motor dimensions, optional convergence-state dimensions, and checkpoint schema compatibility before constructing the recurrent substrate.

Truncated checkpoints, missing fields, incompatible shapes, and future checkpoint schemas fail closed.

## Clean-install and offline-runtime evidence

The gate1-fresh-install-validation workflow builds a wheel, creates a separate virtual environment, installs the wheel non-editably, copies the validator outside the source checkout, and executes the installed package from the runner temporary directory.

At implementation head acbb059ae12a56c3fa4681fef90fd37bf7501dda, the installed package path was under the virtual environment site-packages rather than the checkout. The runtime validation used schema v6, bootstrap pretorius-bootstrap-v1, Deep-History pretorius-deep-history-v2, and canonical evidence manifest v1.

The validation created production-size default recurrent state, ingested a lived interaction, updated a relationship, created a commitment, generated a renderer request without durable mutation, repeated historical retrieval with identical results, saved, restarted, and verified the durable state digest and tick.

The runtime audit hook recorded zero socket events.

## Test and workflow evidence before final review-head documentation

Implementation head acbb059ae12a56c3fa4681fef90fd37bf7501dda passed 263 tests in the brain-tests workflow run 37534788333.

The Gate 1 validation workflow run 37534788309 passed both clean-wheel-install and historical-state-migration jobs.

Its clean-install artifact was gate1-fresh-install-acbb059ae12a56c3fa4681fef90fd37bf7501dda-37534788309.

Its historical migration artifact was gate1-historical-migration-acbb059ae12a56c3fa4681fef90fd37bf7501dda-37534788309.

The final pull request must additionally show green push and pull-request workflows on the final exact review SHA.

## Known residual requirement

Issue #8 is deliberately not closed by this candidate. Hosted CI is strong clean-environment evidence, but the repository explicitly distinguishes that from a fresh end-user-machine validation.

GATE1_FRESH_MACHINE_VALIDATION.md defines the external procedure and the evidence that must be preserved. Gate 1 should not be declared fully accepted until that environment-level evidence is supplied and independently checked.

This residual requirement is environmental, not an unimplemented persistence mechanism. The candidate makes the procedure repeatable and auditable but does not fabricate evidence from a machine it did not run on.

## Assessor falsification targets

The assessor should attempt to modify or delete canonical evidence after a valid snapshot exists, roll the active evidence pointer backward, corrupt the evidence pointer, interrupt recovery staging, and verify that cognition does not silently continue from damaged truth.

The assessor should attempt to open future, malformed, and structurally partial SQLite schemas and verify that the candidate does not mutate them before refusal. The injected migration-failure path should be checked to ensure the restored database is the pre-migration state rather than a second partially migrated copy.

The assessor should truncate and structurally alter recurrent checkpoints, inject a future checkpoint schema, and interrupt a save after partial temporary-file output. The previous valid checkpoint must remain intact.

The assessor should verify that the clean-install workflow imports the installed wheel, not the checkout, and that the historical migration job actually checks out and executes the exact 7be60ed commit.

The assessor should verify that no change in this branch promotes Neural Convergence, wires UPPB into the live subject path, grants renderer mutation authority, or changes the accepted recurrent state-to-policy contract.

## Promotion rule

Do not merge this candidate before independent assessment.

Acceptance of this code candidate means the repository-side persistence and migration hardening mechanisms are acceptable and ready for production integration subject to the separately required fresh end-user-machine evidence in Issue #8.

Acceptance does not close later Issue #17 renderer-neutrality, causal-freshness, subject-available signal construction, donor-independence, or connectome-learning work.
