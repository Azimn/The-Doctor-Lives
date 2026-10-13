# Issue #53: Interrupted host commit, safe research reconciliation

## Problem and authoritative source

The laboratory is physically persistent and independent from Pretorius's autobiographical BrainStore. Host object commits and subject-memory admissions are separate database transactions. An interrupted process can leave an action committed to the physical ledger even though no firsthand outcome was admitted to Pretorius. Calling that operation denied would falsify the world audit; silently inserting a lived memory on restart would falsify his subjective history.

## Recovery contract

The approved research adapter verifies the laboratory's entire physical ledger, inspects committed events attributed to the trusted local research actor and compares their authoritative hashes with successfully indexed firsthand admissions. When a committed collect/place event has no indexed firsthand admission, the adapter can ingest a **new external record of the recovered laboratory report** via PretoriusBrain, with `external=True` and evidence_class `external_statement`. It uses the existing memory store, not an artificial organ or second brain. The source is bound to the exact physical event ID, event hash and world epoch in the disposable admission index. The first-person wording states that the laboratory record attributes an operation to the subject actor label, but the subject cannot retrieve a firsthand record of witnessing its outcome.

The actor label proves authorization provenance, not that the subject observed the committed state. This recovered report MUST NOT unlock the first-person `lab:action` eligibility contract or be counted as a firsthand action memory. The accepted Subject Interface Firewall may expose a valid indexed report as external evidence, rather than presenting engineer event envelopes or hidden simulator state. Raw implementation details remain outside subjective presentation. Repeating a restart must not duplicate the report, and forged or unindexed `lab:recovery` source strings must not enter the accepted subject frame.

The action executor separately labels a physical commit that succeeded but whose observation/admission subsequently failed as `world_committed_pending_reconciliation`, never as a host denial. On the next wake, the ledger-derived external record can be admitted. No pretend rollback of the physical world is performed.

## Tests and scientific limits

Dedicated model-free crash-contract tests simulate a real committed physical action without subject admission, destroy/reopen the brain context, recover the event as an external report, verify `external_statement` provenance and no firsthand action admission, and assert restart idempotency. Another test checks that the operator-created initial problem and a forged recovery source do not become Pretorius's memory.

This is a constrained trusted-host recovery protocol, not proof that a malicious operator cannot rewrite local SQLite, not a distributed atomic transaction, and not a solution to arbitrary filesystem corruption. A crash after an internally written but unindexed firsthand memory leaves a conservative separate external event record instead of retroactively certifying the earlier memory. Distinguish persistence engineering from cognition quality. No canonical production memory, Frankenstein Village, Sensus, or experimental donor architecture is modified.

The code remains isolated in draft PR #54 and must be reviewed before production.
