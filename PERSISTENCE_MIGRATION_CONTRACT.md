# Persistent State Migration Contract

## Scope

This contract governs SQLite state-schema evolution for long-lived Pretorius state directories. It supplements the canonical evidence authority. It does not alter autobiographical classification, Deep-History semantics, UPPB semantics, recurrent policy, or renderer authority.

## Version rule

An existing database must declare an integer schema_version before any schema mutation occurs. A database newer than the running code fails closed. A database older than the minimum supported direct-migration version fails closed and requires staged migration. A database that declares the current version but lacks required tables or columns also fails closed.

The runtime must never overwrite a future schema version with its own version number.

## Migration snapshot and rollback

Before a supported migration mutates the active database, BrainStore creates a complete SQLite backup using the SQLite backup API. The snapshot is content-addressed by SHA-256 and retained under migration_snapshots.

If any migration step or post-migration structural validation fails, the active database is restored from that exact pre-migration snapshot. WAL and shared-memory sidecars from the failed migration are discarded before restoration.

A successful migration records the source version, target version, migration mechanism, snapshot filename, and snapshot SHA-256 in state_schema_migrations_json. Reopening the migrated database does not append another migration record.

## Structural validation

Current-version state must pass SQLite integrity_check and contain every table and column required by the running SCHEMA declaration. Missing required structure is treated as a partial or incompatible migration, not silently repaired.

## Supported direct migration floor

The direct migration floor is schema v2, corresponding to the historical state format at commit 7be60ed. A fixture containing the exact historical v2 SCHEMA is retained under tests/fixtures/store_schema_v2.sql so migration behavior does not depend on network access or an external repository state.

The representative migration test preserves an existing lived record, relationship, commitment, need state, tick, and other durable data while migrating the schema to the current version.

## Gate boundary

This contract addresses the state-schema migration and rollback portion of production Gate 1. Fresh physical user-machine validation remains a separate environment-level acceptance requirement.


## Recurrent checkpoint crash consistency

The recurrent checkpoint is a separately versioned persistence surface. New checkpoints carry checkpoint_schema_version = 1. The accepted RC1 checkpoint shape, which did not contain this field, is treated as legacy schema 0 and remains loadable only through explicit structural validation.

Checkpoint saves are write-validate-replace operations. The runtime writes a temporary file in the checkpoint directory, flushes and fsyncs it, validates the complete NPZ structure, then atomically replaces the active checkpoint. An interrupted or invalid write cannot replace the previous valid checkpoint.

Loading validates required arrays, neuron-dependent shapes, recurrent CSR structure, motor shapes, eligibility alignment, optional convergence-state shapes, configuration JSON, and schema compatibility before constructing the recurrent substrate. Truncated checkpoints and future checkpoint schemas fail closed.

This hardening preserves the accepted neural configuration mismatch boundary. It does not promote Neural Convergence or change the production-default recurrent profile.


## Clean-install and offline-runtime validation

The repository carries tools/gate1_fresh_install_validate.py and a dedicated gate1-fresh-install-validation workflow. The workflow builds a wheel, installs it non-editably in an isolated virtual environment, runs the validator outside the source checkout, and records package location, environment, restart continuity, provenance/classification preservation, relationship and commitment recovery, deterministic retrieval, and renderer read-only behavior.

Runtime validation installs a Python audit hook that rejects socket operations. Dependency acquisition occurs before that guard is enabled; the core mind is then exercised with networking unavailable to Python runtime code.

This CI path is an equivalent clean user environment for repository regression evidence, but it does not replace the separate physical or equivalent end-user-machine validation required by Issue #8.


## Executed historical-state migration

Gate 1 also regenerates a historical state directory by running exact commit 7be60ed46add7c74359b322cc033aa7dfabb08e8, not by constructing only a current-code SQL fixture. The historical code creates lived and external memories, a commitment, Deep-History v1 state, and a recurrent checkpoint. The current candidate then opens that same directory, performs the supported schema migration, adopts the canonical evidence authority, applies Deep-History v2 migration, saves, and restarts.

The validation records the source commit, source and target Deep-History versions, source and target SQLite schema versions, retained migration snapshot identity, canonical evidence manifest version, preserved lived and external evidence classes, preserved commitment, and restart idempotency.
