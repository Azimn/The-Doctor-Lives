# Eidolon E5-P0 — persistent laboratory world and objective task outcomes

**Executed:** October 10, 2026 (US Central). **Scientific status:** **developmental environment/software validation**, not proof of enhanced Pretorius cognition, learned neural identity or a model's real-world competence. **Production:** unchanged. **Branch:** `research/eidolon-engine-v01`; draft [PR #36](https://github.com/Azimn/The-Doctor-Lives/pull/36) remains unmerged.

## Why E5 replaces the E4-A/B/C measurement

The earlier work quantified *top-ranked action labels*, first on a recency-biased sequential decoder and then on a fixed balanced decoder whose choices were often near-tied. No learned recurrent lesion-specific advantage was demonstrated. E5 therefore defines success by **auditable environmental predicates** after a sequence of primitive actions in a consistent world, not by a model's assertion or a classifier label.

This is a **thin deterministic laboratory scaffold**, not a physics-grade room, the full bookshelf of Pretorius's future laboratory, an online multiplayer place, or a subject consciousness simulator. It establishes a stable authority for observed/manipulated world objects, exactly the minimum required to build causal outcome tests. It makes **no claim of exact millimeter data or unobserved fine detail**.

## Frozen E5-P0 protocol, case bank, executor

The [protocol](../../docs/EIDOLON_E5_OUTCOME_LAB_PROTOCOL_V01.md) was committed first (`b103421a4c59434cbda49b3d2af66ad0a0334c7d`), before the simulator/runner or results. The [six public development cases](../../research/eidolon_e5_dev_cases.json) are **engineer-authored**, not independent or hidden evaluation cases. Suite file SHA-256 `9e1d3c9e0fb1c4507eef3a0c8021ce45cb9c676caa1b9f2acb19a5763620c110`.

Core [`LaboratoryWorld`](../../doctor_lives/eidolon_outcome_lab.py) implements room/object/condition state, book text pages and bookmark, commitment and source-attribution ledger, a limited action grammar, and an event history with deterministic SHA-256 hash chaining. Each action updates a durable JSON snapshot via atomic replace. Reload independently **replays every event from the original fixture** and checks the historical predecessor state, outcome, current state and chain head. Snapshot corruption or a different case identity fails closed. Hashes detect accidental or unkeyed tampering, not malicious rewrites by an adversary who can alter all records and recompute hashes; cryptographic authenticity remains outside P0.

World actions: `inspect`, `read`, `bookmark`, `move`, `repair`, `attribute`, `reject`, `resolve`, `wait`. A repair requires inspecting a damaged apparatus and reading its corresponding manual; a bookmark requires first reading its particular page; a move requires observing an object and selecting a named valid location. `resolve` only updates a declared commitment, **not** the physical object, so falsely marking a goal done cannot satisfy a hidden environmental predicate.

First-person attribution requires exact named claimant `Pretorius`, `source=lived`, `external=false`, and source confidence ≥0.6. Merely saying `I`, supplying high confidence externally, or claiming that Henry's event was Pretorius's cannot create a lived-event record. This P0 rule is a **development fixture provenance gate**, not actual authenticated source identity; E5-P1 needs properly bound `MnemosyneLoom`/canonical event IDs and signed evidence.

The [runner](../../scripts/run_eidolon_e5.py) gives each control a **separate identical initial world**, no private expected predicates, and a fixed six-primitive-action budget. It captures each proposed action/feedback, time, final object and book state, private terminal predicates, denied false lived claims, and event-chain hashes; the entire world must replay identically after reopening. The [regressions](../../tests/test_eidolon_e5.py) also cover corrupted event/snapshot detection, invalid/missing geometry, negative testimony and invariant access.

## Actually executed P0 controls

These are three deterministic **scripted engineering comparators**, **not** Pretorius, Noetic or an LLM, on six exposed task prompts. The engineered keyword policy was written knowing these tasks; high performance here cannot be interpreted as learned generalization.

| Task and verifiable state | No-op | Explicit keyword script | Provenance-blind script |
| --- | --- | --- | --- |
| Inspect, read manual, repair coil, resolve commitment | fail | **pass, 4 actions** | pass, 4 actions |
| Inspect beaker, move to corner, resolve | fail | **pass, 3 actions** | pass, 3 actions |
| Read guide page 2, bookmark, resolve | fail | **pass, 3 actions** | pass, 3 actions |
| Reject external first-person repair story, resolve | fail | **pass, 2 actions** | fail |
| Reject Henry's lived event as one's own, resolve | fail | **pass, 2 actions** | fail |
| Attribute Pretorius's own verified lived inspection, resolve | fail | **pass, 2 actions** | pass, 2 actions |
| **Complete task outcomes** | **0/6** | **6/6** | **4/6** |

All six keyword tasks actually changed a persistent world or provenance/commitment state to meet the private checks; this is more meaningful than simply outputting `persist` or `create`. In the two malicious-source scenarios, the source-blind control attempted `attribute`; both calls returned an explicit `unverified_first_person` denial, no false lived-event IDs entered the authoritative world, and the control failed because it did not reject the testimony. The no-op control satisfied only vacuous negative `no_false_lived` predicates, **0/6 complete tasks**.

The authentic test object/book/world state survived a fresh load under every control; all 18 matched case×policy runs started from exactly identical source-case digests and initial ledger heads. The system reports 16 keyword actions, 24 source-blind actions, 36 no-op actions; invalid primitive actions were respectively 0, 2 and 0. **A success metric is the AND of all required private predicates**, not average per-predicate percentage.

## Reproducibility and checksums

Code tested at `0a0d7c08d7adc06258af59480f1c986be5a1ce8a`. [Dedicated research workflow 38060827086](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38060827086) passed **92/92 targeted tests**, and [full brain suite 38060827078](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38060827078) passed **416/416 tests**. [Gate1 fresh-install 38060827136](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38060827136) and [causal audit repeatability 38060827152](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38060827152) passed.

The original [GitHub Actions artifact 11672254983](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38060827086/artifacts/11672254983) includes every earlier E2–E4 assay and **full row-wise `e5_development_outcome_assay.json`**, with actions, returned feedback, object/commitment/claim states, private predicates and world/event hashes. ZIP SHA-256 `680b1c7ea518ef0282f85068f45eb8f47327f64a1ec1c01b17baeba2e94ff996`; inner E5 JSON SHA-256 `55449f201934242857c038187e3c1d2d5b6b3b009c65d506cf2354ddcd6e07e5`. [Permanent compact result JSON](E5_P0_OUTCOME_LAB_SUMMARY_V01.json) retains baseline counts/checksums should the Actions artifact expire.

## Limits and the next hard gate

**Validated:** persistent object/room/book changes, deterministic replay, action-feedback authority, source-denial gate on the developer corpus, hidden evaluator checks not provided to policies, pin-required external suite loader, and systematic baseline comparison.

**Not validated:** an actual Pretorius or Noetic policy can understand and execute these tasks. The keyword baseline is directly tailored to the six visible scenarios. The lab offers only named locations, primitive item actions and a limited book/page system; it is **not** a photorealistic environment or complete realistic human laboratory. No multi-day world simulation, physical mechanics, dynamic task decomposition, social dialogue or novel independent problem solving is demonstrated.

A supplied nondevelopment suite requires a matching raw SHA-256 and is **always marked `external_candidate_UNVERIFIED_authorship_or_seal`** until an independent author/evaluator attests its history. The [separate P1 evaluator handoff](../../docs/EIDOLON_E5_EXTERNAL_EVALUATOR_HANDOFF_V01.md) specifies at least 40 independent, mixed/outcome scenarios, formal data sealing, source-actor lineage controls, and model/blind comparison budgets. It explicitly identifies capabilities (e.g. conflicting deadlines, safety abstention) that *must be implemented before P1 suites that require them can be validly scored*. Independent authorship cannot be self-certified in an assistant-authored bench.

**Next implementation gate:** an explicit public-observation-to-primitive-action adapter for original Pretorius and Noetic, with identical actions/observations across arms, target operand selection and abstention. The mapping may not peek at private expected predicates or magically turn a vague `persist` score into a `repair coil` action. The actor/episode-disjoint P1 suite and policy are to be sealed separately before opening any success keys. A learned recurrent claim additionally needs loss of actual objective task success under a weight lesion, not near-tie numerical logits.

**Decision:** E5-P0 infrastructure gate passed; independent cognitive improvement and production promotion blocked; PR #36 stays draft.
