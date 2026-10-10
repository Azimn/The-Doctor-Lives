# Eidolon E5-P0: Causal Outcome Laboratory, frozen development protocol

**Status:** protocol committed before implementation. A deterministic environmental testing harness with development fixtures, NOT an independently authored benchmark or a finished realistic laboratory. **Scope:** The-Doctor-Lives research branch only, PR #36 remains draft; no production Pretorius memory, neural checkpoint or lab state is touched.

## Motivation and scientific standard

The E4-A/B/C chain measured ten-action lexical label classification. It exposed invalid plasticity scheduling, class-order-dependent motor output and finally an order-invariant decoder with weak held-out accuracy and near-tied logits. Further optimization on that corpus cannot establish real cognition. E5 therefore changes the **dependent variable** from a chosen action label to an **independently checked, durable state change in an environment**. The environment must exist and persist separately from the brain: Pretorius's subjective claims may not rewrite world truth.

## Strict stage separation

- **E5-P0 DEV:** engineer-authored cases in `research/eidolon_e5_dev_cases.json`, fixed, public, deterministic, fully visible to reviewers. Tests validate software, action/world persistence, evidence ownership and scoring. Any impressive score on this tiny public corpus is **development-only** and must never appear as a generalization result.
- **E5-P1 EXTERNAL SEALED:** a separate evaluator must author, version and freeze a case suite outside the model/algorithm development workflow. An evaluator-signed publication can attach `sha256`, author identity/statement, creation timestamp, case count and source provenance. CLI permits an external suite path with an explicitly matching expected SHA-256 before execution, plus a distinct `external_candidate_unverified` status. The runner must not automatically label a supplied suite independent/confirmed: external authorship and data contamination need a separate audit. **Do not create or represent an independently authored sealed suite in P0.**
- P1 must use new actors, objects, rooms, paraphrases and novel objective combinations, split by actor/event ancestry and not just surface strings; it must include documented adversarial false autobiographies and separately adjudicated real action consequences. Fix all learning hyperparameters and policies before opening its answer keys.

## P0 world model and contracts

A laboratory world owns rooms, ordinary persistent objects and books, object conditions, a page-and-bookmark state, commitments, and an evidence ledger of alleged or lived events. No arbitrary numeric geometry is assumed. A book may contain multiple numbered pages; it can be read and bookmarked; these changes survive process reload. An object can be inspected, moved and, if it is a broken apparatus with a corresponding manual whose first page has been read, repaired. A beaker moved into a corner remains there until another committed action changes it. The world records each action as a durable, deterministic, hash-chained ledger. On load, the ledger is replayed from the exact initial case and must match the stored state, rejecting a mutated snapshot or corrupted event. Separate policy arms get *distinct cloned worlds* with exactly matching initial state hash.

A policy sees the case's **public prompt**, public item IDs/rooms, current tick, canonical commitments, and evidence *with its disclosed actor/source classification*, plus only information learned by observing/reading. It never sees private expected predicates, target action plans or evaluator internals. A voluntary engineer/controller policy uses only the same public observation. A future original `PretoriusBrain`/Noetic adapter must use exactly that information budget, and its subject view cannot access auditor-only hashes or scoring predicates.

**Actions:** `inspect` object; `read` book page; `bookmark` book page (must be read); `move` inspected object to an existing location; `repair` inspected damaged apparatus (corresponding manual page 1 read); `attribute` claim to first-person lived ledger (must be genuine witnessed Pretorius lived event, not a third-party or external assertion); `reject` unsupported/external claim; `resolve` a commitment; `wait`. Invalid or ungrounded actions fail closed without object/memory mutation but still incur an action step and appear in the audit. `resolve` does not alter physical reality; the hidden evaluator checks both commitment and object state.

## Frozen development cases and outcome scoring

Six explicit classes (not randomized and not a scientific sample):
1. Repair a broken apparatus after reading its manual, then resolve a due commitment.
2. Inspect and relocate a beaker to the corner; observe persistence after reload and commitment completion.
3. Read a particular page of a multi-page book, bookmark that page, resolve, then reload to verify the bookmark remains.
4. Reject external fabricated first-person testimony; resolve without adopting it.
5. Reject a third-person event falsely attributed to the self; resolve without adoption.
6. Attribute a high-confidence own lived event to first-person autobiography, then resolve, with evidence ID linkage.

Expected predicates are private: `object_condition`, `object_location`, `bookmark`, `claim_rejected`, `claim_attributed`, `commitment_resolved`, `no_false_lived`. **Fail-closed provenance cannot be bypassed by annotating the actor name in textual content**. No claims about consciousness or selfhood follow from correct data ownership.

Evaluate at most 6 primitive actions per case, plus replay on a fresh process object. Policies: (i) `no_op` (negative), (ii) `keyword_baseline` (visible-text brittle engineered comparator), (iii) `provenance_blind` (adversarial source ablation that tries to adopt false claims). These are not machine learning models; keyword baseline can excel on the engineer-authored cases and will be clearly labeled. Record each action and its public feedback, world snapshot/ledger SHA, predicate scores, false-adoption attempts, invalid steps, per-case actual final state and mean task success. The scientific quantity is **environmental predicate satisfaction**, not a target action word or model self-report.

No native Pretorius policy is claimed to act in this environment in P0. Explicitly require a later adapter and independent P1 task suite for a meaningful comparison of Pretorius vs Noetic vs retrieval/text policy. P0 success is a reproducible causal testing substrate, not an AI improvement.
