# Pretorius Donor and Branch Deep-Dive Audit

Status: planning evidence for the Pretorius completion program. This file does not modify production behavior and does not authorize merging a donor branch.

Audit target: Azimn/The-Doctor-Lives

Production base held fixed during audit: 288cb14ab9b65adbf2d916c4eb597e2a9dfd0301

Gate 1 review target held fixed and untouched: bd83eab994717a315399ef4b8e3d6b9a6beeee67

Planning branch parent before this audit: 04f3da4f3a51136c01bd14673dc872f70856a5bf

## Purpose

The existing PRETORIUS_COMPLETION_PLAN.md is structurally sound, but the final Pretorius must be the convergence point of the whole research program rather than only the mechanisms visible on current main. This audit therefore examined historical The-Doctor-Lives branches, later donor development, old Pretorius lines, body/chassis work, recurrent-network experiments, and production-runtime work for mechanisms or test disciplines that were lost, deferred, renamed, or never carried into the current plan.

The audit rule is semantic rather than genealogical. A branch being ahead of main is not evidence that it should be merged. A donor mechanism being sophisticated is not evidence that it should be promoted. The question is whether it fills a real current gap, fixes a demonstrated failure, or supplies a stronger production/evaluation gate.

## Frozen donor references inspected

The audit inspected or compared the following exact lines where available:

- The-Doctor-Lives historical feature and integration branches, including causal audit, Deep-History v1/v2, state-policy v0.4, UPPB, Neural Convergence, early brain integration, chassis selection, and the v0.5 RC line.
- calibos-mind main at a1c3f4b684ed8e1c350bc2ba285e99f849646f63, compared against Pretorius's original Calibos donor pin 0b8d0d552125a6c9ac736fbc09e62c50ee4c18af.
- The-Bride-of-Frankenstein release/v0.2-rc1-hardening at 06622b4faeccac29c5b8e608bb4cac85b5910f55.
- Kiki-Mind kiki/impl-004-context-retrieval at 57a97653ebd92f49eacb710eaf4b04d10be439a3.
- Pretorius v6-phase5d-recall-modes at 59ee05ec2beb7af5ef59847096c868063678e59e.
- Pretorius-Neural-Network v0.4-clipping-susceptibility at 2b90e49e5033584dedc698fc21780360c51ae221.
- Kurzweil-Brain-Experiments v0.6-mentor-timing-persistence at 84841fd6db225bbd01718250cb1094a6f931a068.
- npc-steering-plus virtual-body-homeostasis-v0.2 at a90e6c10b727e5f0b167a8fb44cb690c338b741f.
- DUCK main at 4db5df076eb87a40a5e57d38188821eee7ac804a.
- Persona-and-Jelly-Sandwich main at f196ddef26ca755d814b5fb3e4ed41d1fead01a3.
- Homuncula release/v0.3-consolidated at 7439bab4404d9bd23c190bb38fe67415cb307572.
- MADMAN / metaphysical-man frozen Crucible commit d855f9472c6ed5cf8001d5ab0cbb27c4b3c2b452.
- Agent-Pretorius main, which remains identical to the donor pin 40837ba0093cff044644844c07098450587b968d.

Bride also preserves frozen evidence for Wayfarer, Memora, ContextEcho, Anima, PersonaForge, FirstPersonLoop, Omnicore, TinyPersonaEngine, and other historical donors. Where those repositories were not directly available under their expected current GitHub names, this audit relies only on Bride's preserved registry, experiments, and promotion records rather than claiming a fresh direct repository inspection.

## The-Doctor-Lives branch disposition

The existing branch-convergence rule is confirmed.

The causal-audit, Deep-History, state-policy, UPPB, and v0.5 release branches are already represented in modern main or are fully behind it. They should not be mechanically merged.

The Neural Convergence line remains scientifically important, but its unique value is experimental evidence rather than an alternate production brain. It should feed the 4,096-unit production characterization.

The early brain/chassis integration branches preserve useful boundary decisions, especially the rule that the brain owns identity/cognition while a chassis owns commodity capabilities. Those ideas belong in the standalone/runtime gates, not in a historical merge.

## Finding 1: deterministic endogenous planning is genuinely missing from the completion graph

The most important omission is bounded planning.

DUCK v0.9 implements a non-LLM planning path in which lived experience can create a goal, alternative routes can compete, one subgoal is active at a time, failed action can invalidate a route, and the original objective can persist through replanning. Planning survives restart and focused planning tests can run with inner language disabled.

Bride independently qualified this mechanism against a frozen production baseline and integrated it while preserving one action-selection authority. Plan steps enter ordinary policy competition and can lose to stronger homeostatic pressure.

This is not the same as Gate 6 model-assisted deliberation. Pretorius should have a deterministic executive planning substrate before any reasoning model is permitted to propose richer routes.

Disposition: ADD a Gate 5A bounded endogenous planning gate after the closed world/action loop and before model-assisted deliberation.

## Finding 2: Calibos changed materially after Pretorius's donor pin

Current Calibos is thirteen commits ahead of Pretorius's original donor snapshot. The delta is concentrated in mechanisms directly relevant to human-like continuity.

The important additions are learned contextual habit formation with growth and disuse decay, near-miss familiarity traces, real motive-conflict/ambivalence traces, explicit person-attributed contact wiring, richer interoceptive fallibility and delayed realization, thought provenance distinguishing weighed/discarded/carried/unsure material, expectation lifecycle hardening, and wake liveness stamps.

These mechanisms should not be copied wholesale. Their production lessons map cleanly into existing Pretorius gates.

Disposition:

- familiarity and ambivalence become concrete UPPB signal-producer candidates;
- contextual habit formation becomes an explicit Gate 8 challenger;
- person/source separation strengthens Gate 2;
- thought-provenance categories strengthen session handover;
- OPENED/RECONCILED wake liveness strengthens Gate 3 crash inheritance;
- expiry/lapse/supersession logic strengthens prospective-state lifecycle design;
- lag/noise/realization strengthens the body-to-interoception-to-felt-state boundary.

## Finding 3: Kiki's unmerged retrieval branch solves a real renderer-boundary problem

Kiki Implementation 004 is not merely a design note. The branch contains a working disposable retrieval projection, immutable epistemic envelopes, required constitutional context, exact frame receipts, stale/corrupt-index failure, and adversarial tests.

The key lesson is that retrieval decides accessibility, never truth. Similar text from incompatible provenance classes must remain separate. Retrieval score, repetition, semantic similarity, or renderer preference cannot promote a record into a stronger epistemic class.

The exact renderer-facing frame should be attributable. A frame receipt should bind the canonical head, retrieval regime, selector, renderer adapter/identity, selected source IDs, omissions, budget, and structured-frame digest.

Disposition: ADD this as production infrastructure under Gate 4/P10. Do not make Kiki's retrieval store a second canonical memory system.

## Finding 4: old Pretorius V6 contains useful organs that did not all survive consolidation

The V6 line contains a self-ledger/speech-act ledger, explicit withholding reasons and withheld intent, typed dissonance, multidimensional relationships, theory of mind, learned knowledge, open loops, contextual procedural habits, recall modes, and long-arc drift tests.

Several are already covered or superseded. UPPB P3 is a stronger awareness/attention framework than the unfinished V6 attention budget. Current concerns/commitments plus the new planning gate supersede a second open-loop store. Bride found selective provenance-aware recall redundant against a stronger baseline, and UPPB now supplies a much more rigorous reconstructive-memory path, so V6 recall modes should not be transplanted wholesale.

Several gaps remain real. Current Pretorius has no first-class semantic learned-knowledge plane, no load-bearing theory-of-mind model, no contextual procedural habit system, and no communicative-act/withholding ledger. The self-model also lacks an accepted ordinary developmental update path.

Disposition:

- add a communicative-act and withholding ledger to P7;
- add learned external knowledge and a typed claim graph to Gate 7;
- make contextual procedural habits and ToM explicit Gate 8 subgates;
- treat richer relationship dimensions and typed self-dissonance as evidence-gated challengers, not mandatory complexity;
- do not import V6 recall modes unless the UPPB path later demonstrates a specific failure they solve.

## Finding 5: current Pretorius global action values are not a full habit mechanism

Current main has durable action_values, but the v0.3 causal audit found that table behaviorally inert in the tested path while recurrent reinforcement was causal. Global action value is also vulnerable to context collapse.

Bride's contextual-plasticity experiment independently showed a real opposite-context failure in a global per-action habit value. The challenger fixed it but was held from automatic promotion because of complexity.

Calibos and V6 supply simpler procedural-habit patterns: behavior repeated in a context forms a habit, successful reuse strengthens it, contradictory conduct/disuse weakens it, and authored habits remain distinct from learned habits.

Disposition: ADD a Gate 8 contextual procedural habit challenger. Require opposite-context, extinction/disuse, lesion, restart, and fatigue/attention-modulation tests. Do not simply turn the existing global action_values table into a stronger global bias.

## Finding 6: prospective cognition needs a clean taxonomy

The donor program uses commitment, expectation, prediction, unresolved business, and wake intent for different things. Those names must not collapse.

Pretorius already has commitments. Calibos demonstrates robust lifecycle handling for prospective obligations, but its inbox structure calls those records expectations even when they are semantically debts. Digital Subject separately implements genuine predictive expectations with confidence and prediction error.

Disposition: formalize three categories.

A commitment is an intention or obligation. A subject expectation is what Pretorius anticipates. A preregistered prediction is a frozen, evaluation-grade forecast with explicit probability/evidence/state fingerprint and proper scoring.

Each may need expiry, supersession, release/lapse, or invalidation, but the transition semantics must match the kind of record. A superseded obligation is not a failed forecast.

## Finding 7: the body, interoception, and felt state need three separate authorities

npc-steering-plus v0.2 and Calibos independently converge on this separation.

The virtual body is authoritative physiology. An interoceptive sensor observes that physiology and may be noisy, delayed, quantized, or otherwise fallible. Subject-facing cognition receives the observation or a phenomenal projection, not the raw body dictionary. Model readback may contribute evidence about expression but cannot rewrite primary physiology.

Calibos adds a useful realism pattern: felt state chases actual state with asymmetric lag and deterministic noise, and a later convergence can create a first-person realization that the organism misread itself.

Disposition: STRENGTHEN UPPB signal construction and Gate 5 body integration around the three-layer body -> interoceptive observation -> felt state contract.

Activation-space physiological steering remains experimental. It is a renderer/model translation mechanism, not an identity store, and should not become production-default until reproduced under its own model-dependent gates.

## Finding 8: acquired knowledge is still too close to autobiographical storage

Agent-Pretorius and V6 both separate learned/research knowledge from autobiography. NEXT_THINGS_TO_DO.md already identifies this gap after the Second Brain OS comparison.

Current The-Doctor-Lives has excellent provenance, source custody, protected evidence, conflict resolution, and reference material, but ordinary runtime external statements still live in a memory-oriented substrate.

Disposition: MOVE the external-knowledge plane, typed claim graph, and knowledge-health loop into the authoritative completion plan under Gate 7. Preserve source claims, contradictions, corrections, and synthesis lineage. Do not repurpose the Persona Connectome as a world-knowledge graph.

## Finding 9: developmental evidence must preserve renderer and opportunity context

Kiki's Developmental Evidence Layer demonstrates why a choice or self-report cannot be interpreted in isolation. Renderer, model/provider/runtime, modality, tools, policy restrictions, initiative affordances, and explicit user prompting can all masquerade as development.

The Kurzweil experiments reinforce the same scientific lesson. A plausible developmental story can disappear when reward/opportunity are properly matched.

Disposition: STRENGTHEN Gate 2. Record the conditions under which developmental observations occur and keep psychological interpretation derived. Repeated self-report is not repeated independent evidence.

## Finding 10: transient divergence is not enough

Kurzweil v0.5 produced immediate matched causal divergence after a mentor-domain edit in every paired life, but most trajectories strongly reconverged by maturity. v0.6 therefore isolates developmental timing.

This is directly relevant to Pretorius. A mechanism that changes the next action but leaves no durable trajectory may be useful, but it should not be described as a persistent identity mechanism.

Disposition: ADD trajectory-persistence and timing-sensitive counterfactual requirements to P11 and to any gate claiming durable development.

## Finding 11: the unmerged recurrent experiments materially strengthen Neural Convergence testing

The Pretorius-Neural-Network v0.4 experiment sequence goes well beyond the donor main branch.

Experiments 009 through 017 show that a compact high-change recurrent set is sufficient and disproportionately necessary within matched topologies, converges strongly under curriculum reordering, partially transfers across independent topologies under functional alignment, and depends more on recipient edge-set selection and learned delta-distribution properties than on exact one-to-one donor delta assignment. Later experiments isolate distribution shape and clipping effects.

These are scientific characterization results, not a portable identity object.

Disposition: EXPAND the 4,096-unit production characterization to test causal-core sufficiency/necessity, relearning after lesion, functional homology, distribution/clipping, and brittleness. Do not transplant a donor recurrent core into production Pretorius and call that continuity.

## Finding 12: show-floor readiness needs operator and authority engineering

Frankenstein and Homuncula provide production lessons that are distinct from cognition.

Frankenstein demonstrates backup/restore, crash-rebuild of disposable projections, a single writer boundary, capability gating, renderer nonauthority, and long-run replay expectations.

Homuncula demonstrates explicit schema migration ledgers, startup refusal on future/tampered state, local health surfaces, packaged Windows operation, owner authentication even on localhost, durable wakes/plans/responsibilities, typed capability requests, default denial of unknown capabilities, loop guardrails, and verified evidence receipts that the model cannot fabricate.

Pretorius should not inherit Homuncula's identity or agent architecture. The relevant lessons belong in the standalone host.

Disposition: STRENGTHEN Gate 3 with operator health/doctor, backup/restore, crash inheritance, package-level smoke tests, local authentication if a service exists, and default-deny capability control. Add a pre-1.0 shadow-brain audit for every derived projection/cache.

## Finding 13: perception should be a bounded adapter, not a world rewrite

TinyPersona and Bride agree that objective world truth, perceptual access, subjective experience, and remembered interpretation are different stages.

Disposition: ADD a bounded perception adapter to Gate 5. The host owns objective stimuli. Pretorius receives only accessible stimuli under declared sensory/attention constraints. Perceptual omission cannot delete world truth.

## Finding 14: involuntary expression is distinct from deliberate action

Bride qualified the FirstPersonLoop-style separation between deliberate decision and reflexive outward expression. A pain/startle emission can occur without replacing the selected deliberate action or becoming chosen-action reinforcement.

Disposition: STRENGTHEN P8 with an involuntary-expression boundary.

## Finding 15: several sophisticated donors should remain out of production for now

The deep dive also confirms several explicit non-promotions.

MADMAN remains a high-complexity research substrate. Its metabolism/scars/Morrow experiments are interesting, but no demonstrated Pretorius production failure requires that substrate.

Omnicore six-dimensional affect remains a historical hold. Current production gaps do not justify extra affect axes.

Activation-space steering remains model-dependent and experimental. It may improve expression or interoceptive translation, but it cannot become identity authority and has not earned default production status.

Bride's contextual plastic policy demonstrated a real capability but exceeded its automatic complexity gate. The simpler contextual-habit challenger should be tested before adding another adaptive policy substrate.

A second generic recall architecture is not justified while UPPB reconstruction/source-monitoring is the active memory path.

A second planner, second identity store, second canonical knowledge authority, or chassis-owned persona system is prohibited.

## Resulting authoritative additions to the completion plan

The completion plan is augmented, not replaced.

The audit adds or strengthens these production requirements:

1. Gate 2 gains renderer/runtime/affordance-aware developmental evidence plus explicit person/source attribution.
2. Gate 3 gains wake transaction liveness, richer handover provenance, show-floor recovery/health, capability boundaries, and the shadow-brain authority audit.
3. UPPB signal construction gains the explicit body/interoceptive-observation/felt-state boundary plus familiarity and real-conflict signal producers.
4. P7 gains a communicative-act and withholding ledger.
5. P8 gains a separate involuntary-expression channel.
6. Gate 4/P10 gains disposable retrieval projections, immutable epistemic envelopes, mandatory constitutional context, and exact Subjective Frame receipts.
7. Gate 5 gains a bounded perception adapter.
8. New Gate 5A adds deterministic endogenous planning before model-assisted deliberation.
9. Gate 7 gains a clean prospective-state taxonomy plus the external-knowledge plane, typed claim graph, and knowledge-health loop already identified in NEXT_THINGS_TO_DO.md.
10. Gate 8 explicitly tests contextual procedural habits, theory of mind, richer relationship dynamics, and evidence-backed self-model development.
11. Neural Convergence characterization incorporates the unmerged v0.4 causal-core experiments.
12. P11 gains trajectory-persistence/timing tests, planning/habit/prospective-state suites, retrieval/frame-integrity tests, and show-floor resilience.


## Follow-on branch stress audit after the initial donor pass

The first audit was then stress-tested against donor development lines that were not yet fully represented in the audit narrative.

### Finding 16: DUCK v0.10 sharpens the predictive-causality boundary

Directly inspected donor: `Azimn/DUCK@30a11ea8308ebd0fc89a06bb994ab0e23bd02886` on `motivated-cognition-v0.10`.

DUCK now distinguishes world-fact expectations from action-outcome expectations, and it keeps sequence-conditioned prediction separate from stronger intervention evidence. A preregistered intervention must exist before the outcome, and stronger causal route influence is withheld until an eligible matched direct baseline exists. Counterfactual route estimates are explicitly `model_prediction`, are not persisted as lived experience, and cannot train from outcomes that never happened.

The existing Pretorius Gate 7 had prediction and calibration but did not state these separations strongly enough.

Disposition: STRENGTHEN Gate 7 with action-bound outcome expectations, observational-versus-intervention causal evidence, matched comparison requirements, and strict counterfactual non-experience provenance.

### Finding 17: FirstPersonLoop exposes a renderer-visible privacy mismatch and a limited-introspection requirement

Directly inspected donor: `Azimn/FirstPersonLoopTest@337555030af09b15f4515604c5f193a5b1fbef42` on `gpt56-four-cycle-hardening-20260913`.

Its late freeze work found a structural privacy bug class: a renderer may be shown more private thought than the copy-protection layer actually protects. The corrected invariant is that the set of private thought visible to speech and the set protected from unauthorized verbatim or near-verbatim copy-out must coincide.

The same line also preserves a more important cognitive boundary. Hidden causes may influence behavior without becoming introspectively available. First-person explanation is therefore not automatically a readout of the real implementation cause.

Disposition: STRENGTHEN P7 with exact visible-private protection and explicit disclosure authority. STRENGTHEN P9 with limited introspection, provenance-bearing self-explanation, and temporal self-hearing after actual expression.

### Finding 18: bounded representational capacity can silently erase developmental history

Directly inspected donor: `Azimn/champion-versus-challenger@79f747707dadfce9092d89ad19a17a9fcd7dd79b` on `champion-v9-5-habit-temporal-plasticity`.

EXP-010 and EXP-011 establish an information-theoretic failure that applies beyond their toy architecture. When a bounded unresolved concern or prospective identity+cue record is evicted, the remaining canonical subject-owned state can become identical to a matched history in which the lost item never existed. Once that happens, no later deterministic policy over that state can recover the missing distinction.

The useful lesson is not the donor's numeric capacity of three. The lesson is that every bounded load-bearing store needs an explicit overflow meaning and a tested information-loss frontier.

Disposition: ADD a pre-1.0 capacity/overflow audit covering concerns, prospective state, wake intents, handovers, hypotheses/predictions, and any later bounded social/self-model store. Silent identity-relevant eviction is not acceptable merely because the runtime stayed within a memory budget.

### Finding 19: persistent information asymmetry supports limited report access, while PEMA reinforces temporal attribution

The champion-versus-challenger persistent-information-asymmetry experiment shows that deterministic differential access can preserve distinct local histories long enough to change later action while the language/report path lacks the decisive causal basis. Later explicit communication can change the report without merging hidden states. This is an existence proof for action/report asymmetry, not a requirement to split Pretorius into multiple processors.

The PEMA developmental work also preserves a failed primary result where radically different evidence endpoints did not explain the mature behavioral split. Its successor freezes a temporal-attribution ladder because within-history ordering itself may be causal.

Disposition: do not add a second multi-processor cognitive architecture. Instead use differential-access cases as P9/P11 tests of limited introspection, and retain the existing P11 developmental timing/trajectory-persistence requirement with frozen one-factor attribution when aggregate-history explanations fail.

## Follow-on authoritative additions

This follow-on pass adds four concrete requirements to the completion program:

1. Gate 7 explicitly separates world-fact expectation, action-outcome expectation, observational sequence learning, intervention evidence, and counterfactual model prediction.
2. P7/P9 gain exact renderer-visible private protection, explicit disclosure authority, limited introspection, and evidence-bearing self-explanation.
3. P11 gains bounded-capacity/overflow tests with matched-history information-loss probes.
4. NEXT_THINGS_TO_DO.md now records these mechanisms plus developmental timing/trajectory persistence so the to-do list and authoritative completion plan remain synchronized.

## Completion criterion after the audit

No donor repository should remain necessary to understand how production Pretorius works. Donor repositories remain evidence, history, and experimental provenance.

Before Pretorius 1.0, every promoted donor idea must be represented by a Pretorius-owned contract, implementation, migration path, causal test, restart test, and independent review. Every rejected or held donor should remain documented so future developers do not repeatedly rediscover and reintroduce the same complexity without new evidence.
