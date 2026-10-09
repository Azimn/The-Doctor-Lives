# The Doctor Lives

> **Research coordination (2026-10-08):** The Doctor Lives remains the definitive production Pretorius, not a competitor experimental brain. It participates in the [cumulative Character Continuity Program](https://github.com/Azimn/Artificial-Life-Research-Journal/blob/main/programs/CHARACTER_CONTINUITY_PROGRAM_V1.md) as a candidate for independently gated, opt-in mechanism transfer. Experimental neural, retrieval and conditioning claims are tracked in the [cross-project evidence register](https://github.com/Azimn/Artificial-Life-Research-Journal/blob/main/programs/CHARACTER_CONTINUITY_EVIDENCE_REGISTER_V1.md) and [comparison protocol](https://github.com/Azimn/Artificial-Life-Research-Journal/blob/main/programs/CHARACTER_CONTINUITY_COMPARISON_PROTOCOL_V1.md). Production release, evidence authority, persistence and migration gates remain separate and must not be bypassed by research results.

The Doctor Lives is the production assembly repository for Doctor Septimus Pretorius as a persistent, renderer-neutral cognitive system.

The brain owns identity evidence, autobiographical continuity, relationships, concerns, prospective commitments, interoception, salience, endogenous cognition, offline replay, consolidation, recurrent state, and provenance. A language model is a renderer and cognitive organ, not the identity database. Shell, browser, scheduler, messaging, and other capabilities remain outside the brain until a chassis is attached through the stable port.

Calibos is used as a structural donor only. No Calibos memories, private thought stream, relationships, preferences, values, or persona cartridge are imported. The enforced transplant surface is mechanism: salience, interoceptive lag, unresolved loops, sleep and replay, consolidation discipline, drift accounting, and provenance boundaries. Pretorius identity comes from pinned Pretorius evidence under `evidence/` and `doctor_lives/data/bootstrap.json`.

The recurrent Pretorius network is causally load-bearing. Its action distribution selects the cognitive policy used to choose which otherwise-salient non-root memories enter endogenous attention. Every such decision is written to `policy_decisions` with action scores, candidate and selected memory IDs, recurrent tick, checkpoint SHA-256, trigger, and policy version. Outcome reinforcement and sleep replay can therefore change later cognition through the network, and those changes are auditable.

The architectural mutation boundary is defined in `ARCHITECTURE_CONTRACT.md` and `doctor_lives/data/evolution_policy.json`. Frozen invariants require explicit migration. Lived memory, relationships, self-model hypotheses, felt state, salience, recurrent weights, and other developmental state are allowed to evolve.

The current public Jelly-Psiduck repository does not contain the frozen v0.2 engine implementation used by Calibos. This repository therefore reproduces the required first-person workspace and endogenous-cognition semantics behind local interfaces rather than claiming to vendor unavailable code. An exact engine snapshot can later replace that compatibility layer only if it passes the same contract tests.

Install with `python -m pip install -e .`. The command-line entry point is `doctor-lives`. The stable chassis API is `doctor_lives.PretoriusBrainPort`.

Run the regression suite with `python -m unittest discover -s tests -v`.

## Deep-History v2

The current production baseline uses `pretorius-deep-history-v2` with schema v5. Preawakening autobiography is separated into canonical, reconstructed, and admitted-synthesized classes; events experienced by the running implementation use `lived_runtime_memory`. Evidence class, event subtype, source authority/canon rank, continuity, wording status, and classification reasoning remain independent provenance axes.

The 70-node, 243-edge Persona Connectome is preserved with signed retrieval-time spreading activation. Inhibitory edges remain inhibitory and do not write back to base salience or source graph weights. Deterministic canon-conflict resolutions affect normal retrieval while losing accounts remain stored and auditable. Synthesized autobiography requires an approved admission that is bound by SHA-256 to the exact reviewed claim.

Character invariants are design material rather than autobiography. LoRA examples, prompt-control material, and reference-only legacy material cannot become memories by repetition. Unsupported childhood claims remain withheld unless evidence improves or a synthesis passes the admission gate.

Deep-History v2 was merged at production SHA `001321b30fdbcde59e388ce907031788543611b6`.

## v0.4 bounded state-to-policy bridge

The v0.3 causal audit demonstrated that deep history, felt needs, relationship state, and commitments could change downstream context without changing action selection. v0.4 introduces the smallest correction justified by that result.

The recurrent action distribution remains Pretorius's baseline policy contribution. A deterministic state-to-policy bridge can apply bounded pressure from felt needs, relevant relationship state, open commitments, relevant autobiographical history, and open concerns before the winning tendency is selected. Each state family is capped independently, the combined correction is capped, and every policy decision preserves the recurrent base scores, per-family pressure, final scores, and selected action.

Concerns now have an explicit durable resolution lifecycle. Resolved concerns no longer remain in the open-concern set, no longer drive open-term salience, and no longer create permanent heartbeat cognition merely because they once existed.

The self-model and spreading activation are deliberately excluded from the bridge pending stronger causal evidence. Durable action values also remain outside the bridge for now because recurrent reinforcement already demonstrated a causal learning path and double-counting the same outcome signal is not justified.

No chassis/body integration is part of v0.4.

## v0.3 causal architecture audit

The current development phase is a temporary feature freeze devoted to causal characterization of the architecture already present. See `CAUSAL_AUDIT_CONTRACT.md` and GitHub Issue #9.

`doctor_lives.CausalAuditHarness` runs matched-state lesion/control conditions against cloned brain state. It records retrieval, policy scores, selected tendency, renderer request, felt needs, relationships, concerns, commitments, action values, self-model state, recurrent checkpoint hashes, and deterministic downstream audit renders.

The audit currently targets deep history, needs/interoception, relationship history, commitments, recurrent policy, spreading activation, sleep replay, reinforcement/action values, concern accumulation, and self-model causal reach.

Run the production audit with:

`python tools/run_causal_architecture_audit.py`

This phase deliberately does **not** add the proposed state-to-policy bridge. That change is only eligible after the audit establishes which existing state variables fail to influence decisions under matched tests.


## Definitive convergence target

`The-Doctor-Lives` is the canonical integration repository for Pretorius. Earlier repositories such as `Pretorius-Neural-Network`, `Persona-and-Jelly-Sandwich-`, DUCK, and related experiments are mechanism donors and evidence archives, not competing production brains. New validated mechanisms are transplanted here behind versioned gates rather than creating another parallel Pretorius implementation.

The Neural Convergence v0.5 candidate keeps the accepted v0.4 recurrent path reproducible by default while adding an opt-in convergence profile. That profile brings the already tested donor mechanisms into the existing 4,096-unit substrate: Oja-style competitive recurrent plasticity, affect/novelty/threat-conditioned plasticity gating, provisional synaptic tags with delayed outcome capture, sparse recurrent-gain homeostasis, intrinsic excitability regulation, persisted correlated endogenous variation, and restart-safe persistence of the new neural state. The same opt-in profile also adds signed input channels for Pretorius's felt fatigue, affiliation, competence, autonomy, curiosity, and continuity state, so subjective interoception can directly perturb recurrent dynamics without exposing hidden homeostatic actuals. It remains the same recurrent substrate and the same action vocabulary. No second planner, second identity store, or second neural brain is introduced.

The convergence work is intentionally separate from the active UPPB branch. UPPB can continue proving reconstructive subjective-memory semantics without silently changing live PretoriusBrain behavior, while Neural Convergence proves the lower-level substrate migration against the accepted v0.4 baseline.


## v0.5 release candidate

The v0.5 release candidate is the single review target for current Pretorius development. It consolidates the accepted v0.4 state-to-policy line, the complete green UPPB P0 through P6D implementation, and Neural Convergence v0.5 in one tree.

The production default remains the accepted v0.4 behavioral path. This is intentional. UPPB P0 through P6D is included as a complete standalone subsystem but is not yet allowed to replace the live subject-facing Pretorius path. Neural Convergence is included behind the explicit `NEURAL_CONVERGENCE_CONFIG` profile while the legacy v0.4 neural configuration remains the control. The release candidate therefore gives the assessor one repository state that contains all validated work without silently promoting an experimental mechanism past its evidence gate.

The release provenance and assessor scope are recorded in `ASSESSOR_REVIEW.md`.


## Gate 1 canonical evidence authority

Post-RC1 production hardening now places canonical package evidence behind a versioned runtime authority. The installed distribution is verified against doctor_lives/data/canonical_evidence_manifest_v1.json before the cognitive store is opened. Pretorius then consumes an immutable state-local snapshot rather than reading identity and deep-history files directly from package paths.

The active snapshot is append-only. Corruption or a missing artifact fails closed. Explicit recovery creates and verifies a new snapshot from the installed distribution before atomically advancing the active pointer, leaving the damaged snapshot available for audit and leaving subjective or lived state untouched. The SQLite store binds itself to the exact manifest version and fingerprint and rejects partial or incompatible bindings. See EVIDENCE_AUTHORITY_CONTRACT.md.

This is the repository-side canonical-evidence portion of Issue #17 and Gate 1 in Issue #14. It does not claim completion of the separate fresh physical user-machine validation in Issue #8.


## Gate 1 state-schema migration safety

Long-lived SQLite state now checks its declared schema version before mutation. Supported older state is snapshotted through SQLite backup, migrated, structurally validated, and recorded in an append-only migration lineage. A failed migration restores the exact pre-migration snapshot. Future schemas, malformed versions, and partial current schemas fail closed rather than being rewritten to the runtime version. See PERSISTENCE_MIGRATION_CONTRACT.md.


The recurrent NPZ checkpoint now uses an atomic write-validate-replace path. New checkpoints carry an explicit checkpoint schema marker, legacy RC1 checkpoints remain structurally validated and loadable, and truncated or future-schema checkpoints fail closed without overwriting the previous valid recurrent state.


## Gate 1 clean-install validation

The repository now has a dedicated non-editable wheel-install workflow, gate1-fresh-install-validation. It installs the built wheel into an isolated virtual environment, runs outside the source checkout, forbids Python socket activity during runtime validation, creates real production-size Pretorius state, ingests lived experience, persists relationship and commitment state, verifies render read-only behavior and deterministic retrieval, saves, restarts, and emits a preserved JSON validation artifact.

The separate physical or equivalent fresh end-user-machine procedure remains documented in GATE1_FRESH_MACHINE_VALIDATION.md. CI evidence is supporting evidence and does not by itself close Issue #8.


Gate 1 migration CI now also executes exact historical commit 7be60ed46add7c74359b322cc033aa7dfabb08e8 to generate a real older Pretorius state directory, then opens and migrates that directory with the current candidate. This supplements the deterministic SQL schema fixture with an actual old-code state-generation path.


## v0.5.0rc2 review candidate

The Gate 1 persistence and migration hardening branch is packaged as 0.5.0rc2 for independent review. This version label does not mean Gate 1 is fully accepted. The external fresh end-user-machine evidence required by Issue #8 remains outstanding until it is actually run and preserved. See GATE1_ASSESSOR_REVIEW.md.
