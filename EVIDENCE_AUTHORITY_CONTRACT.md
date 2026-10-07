# Canonical Evidence Authority Contract

## Scope

This contract governs the production boundary introduced after the accepted Pretorius v0.5 RC1. It is a Gate 1 persistence and migration hardening mechanism. It does not change Deep-History v2 semantics, UPPB P0 through P6D semantics, the recurrent policy, or the Neural Convergence promotion status.

The installed package contains the reviewed distribution snapshot. A versioned manifest names the exact runtime evidence artifacts and their Git blob content digests. Before Pretorius opens the cognitive store, the evidence authority verifies that distribution snapshot. Cognition therefore cannot begin from missing or silently modified canonical evidence.

## Runtime authority

The active runtime copy lives under the Pretorius state directory in a versioned evidence snapshot. The state-local copy exists so corruption, recovery, and future migration can be tested without rewriting the installed distribution.

The active snapshot is selected by an atomic pointer. Every artifact is verified against the current manifest before it is returned to cognition. The bootstrap, deep-history inputs, source manifest, and evolution policy are loaded through this authority rather than directly from mutable package paths.

The SQLite store records the manifest version and fingerprint that were adopted. A partially bound or incompatible manifest fails closed. Initial adoption from the accepted RC1 evidence set records explicit lineage and does not reinterpret any evidence semantics.

## Mutation and recovery rule

Canonical evidence snapshots are append-only. A damaged active snapshot is never repaired in place. Explicit recovery verifies the installed distribution, creates a new snapshot, verifies the new snapshot, records an audit event, and only then advances the active pointer.

The damaged snapshot remains available for forensic inspection. Recovery does not rewrite the cognitive SQLite store, recurrent checkpoint, UPPB trace history, subjective recollection history, relationships, concerns, commitments, or lived memories.

The installed distribution is the recovery source outside the active mutable state directory. If the installed distribution itself fails digest verification, recovery fails closed.

## Manifest rollback and migration boundary

The active pointer must name the exact manifest version and fingerprint required by the running package. A stale, rolled-back, or incompatible manifest is rejected.

A future change to the admitted artifact set or artifact content requires a new manifest version and an explicit state migration. The current implementation deliberately refuses to infer compatibility from filenames or apparently similar JSON.

## Protected evidence references

The authority exposes exact artifact and digest verification for future UPPB integration. A protected evidence reference cannot become trusted merely because it contains an arbitrary path or string. The integration boundary must resolve the reference through the canonical authority and verify the admitted digest.

## Crash consistency

Snapshot creation occurs in a staging directory. The active pointer is advanced only after a complete snapshot verifies. Stale staging directories are discarded on restart. An interrupted copy therefore cannot become active evidence.

## Gate evidence

The production tests exercise initial adoption, idempotent restart, modified bytes, missing evidence, manifest rollback, interrupted staging cleanup, exact protected-reference verification, append-only recovery, and preservation of cognitive state across recovery.

This contract addresses the canonical-evidence integrity and recovery portion of GitHub Issue #17 and the repository-side persistence portion of Gate 1 in Issue #14. The separate fresh physical user-machine validation in Issue #8 remains an environment acceptance requirement and is not represented as complete by this contract.
