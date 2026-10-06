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
