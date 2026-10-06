# The Doctor Lives

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
