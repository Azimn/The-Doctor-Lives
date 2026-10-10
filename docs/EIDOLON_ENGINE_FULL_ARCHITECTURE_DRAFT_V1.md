# THE EIDOLON ENGINE
## Full Cognitive Architecture, Draft v1.0

**Working title:** The Eidolon Engine: A Recurrent, Autobiographically Bound Cognitive Architecture for Persistent Artificial Identity

**Status:** architectural proposal, not an implemented system and not a demonstrated cognitive advantage  
**Date:** 2026-10-09, America/Chicago  
**Repository:** `Azimn/The-Doctor-Lives`, research branch `research/eidolon-engine-v01`  
**Review status:** draft for independent theoretical, systems, experimental and safety review  
**Research lineage:** [The Doctor Lives](https://github.com/Azimn/The-Doctor-Lives), [Pretorius Neural Network](https://github.com/Azimn/Pretorius-Neural-Network), [Pretorius Connectome](https://github.com/Azimn/Pretorius-Connectome), [Attractomancy](https://github.com/Azimn/Attractomancy), [Artificial Life Research Journal](https://github.com/Azimn/Artificial-Life-Research-Journal)

### Abstract

The Eidolon Engine proposes that a persistent artificial character should acquire its characteristic behavior not merely by retrieving a fixed persona description, but through continuous reciprocal influence between learned neural dynamics, evidence-bound autobiography, relational history, embodied/interoceptive signals, active intentions, attentional competition and future action. The proposed `self` is an operationally stable, plastic, distributed control regime, not a presumed conscious entity or a cryptographic identifier. Attractomancy contributes hypotheses about cues, symbol-context binding, ritual sequencing and reinstatement. Its metaphysical interpretations are not accepted as empirical mechanisms. The Ontological Interface Hypothesis is inspirational speculative framing only.

The architecture is designed to converge on the existing Pretorius production brain without replacing its canonical evidence authority, renderer-neutral interface, externally auditable neural checkpoints or first-person phenomenal-projection boundary. A full implementation must demonstrate causal downstream action, history sensitivity and lesion-specific generalization on independently authored tasks, not merely a pleasing narrative or a learned output-layer score.

## 1. Problem and scientific claim boundary

The governing question is whether past experiences and learned relationships change what Pretorius perceives, selects, anticipates and does later, even when renderer, surface cue, intervening context or model family changes. A lookup system can recall a correct fact without that fact causing a change in policy. A script can mimic a characteristic personality without storing an acquired disposition in the recurrent substrate. A trained decoder can display character-like actions while the recurrent population itself contributes no meaningful learned information. The Eidolon proposal treats these as distinct, testable hypotheses.

`Identity` means longitudinal behavioral continuity under controlled changes, appropriately revised by new experience. It is neither a fixed vector, nor permanent sameness, nor unchanging first-person prose. A system must remain capable of updating, contradicting past beliefs and honestly marking uncertain sources. Our objective is **continuous causal self-organization**, not maximal resistance to novelty.

Current evidence remains mixed. Pretorius Neural Network Experiment 001 found that much phenotype expression followed the decoder under its then-current protocol; Experiment 004 reported a bounded recurrent-only signal in a different plasticity regime. BioCircuit and FlyWire trials have shown weak out-of-sample semantic generalization, significant lexical confounds, and no proven biology-inspired recurrent advantage in several controls. The v0.1.1 Eidolon construction battery supports coded associative responses, but recurrence lesion **still retains 4/4 top-ranked targets**, so that assay is not evidence of necessity of recurrent intention for a correct choice. These findings are preserved, not averaged into a fictitious general success.

## 2. Existing production contract: what must survive

`The Doctor Lives` already contains a versioned Pretorius autobiographical archive, provenance classes separating canonical/reconstructed/synthesized preawakening material from lived-runtime material, relational and commitment state, needs/interoception, a recurrent neural policy, state-to-policy pressure, endogenous thought and a renderer-facing Subject Frame. Some awareness arbitration exists as a separate component; it is not automatically proof of a globally broadcast cognitive workspace.

The frozen invariant is:

```text
PROTECTED ENGINEER PLANE                      SUBJECT PLANE

source records, weights, numeric salience
    -> authorized ingress + source checks
    -> potential attentional candidates
    -> gated first-person phenomenal projection
    -> bounded available subjective content
    -> renderer, with no state or tool authority

No raw score, graph row, checkpoint metadata, source rank,
latent vector or untrusted world instruction crosses directly.
```

Mechanism transplantation cannot import memories, identities or private experiences from donor characters. The production 4,096-unit recurrent checkpoint, policy-decision audit rows and canonical source manifest must not be silently altered or recoded. All new machinery is opt-in, namespace/version separated and initially shadow-only. Causal comparisons run on cloned test states, and any production mutation requires a reviewed migration with rollback proof.

## 3. The complete functional organization

```text
                               EXTERNAL / BODY / INTERNAL EVENTS
                                            |
                               WITCHGLASS PERCEPTION SHELL
                           typed normalization + trust boundaries
                                            |
                                      JANUS GATE
                       event provenance, ownership, source ambiguity
                                            |
                       +--------------------+--------------------+
                       |                    |                    |
                   SYMBOLS              EPISODES            PREDICTIONS
                       |                    |                    |
                  SYNTHEMA LATTICE ---- MNEMOSYNE LOOM ---- CHRONOS COIL
                  multimodal binding     causal history     expected futures
                       |                    |                    |
                       +--------------------+--------------------+
                                            |
                                    NOETIC CRUCIBLE
                       latent recurrent integrator + conflict regulation
                                     /             \
                                DAE MONIUM*    EIDOLON FIELD
                                drives/bounds  stable, mutable attractors
                                     \             /
                                      JANUS ATTENTION
                           capacity-limited competitive broadcast
                                            |
                                     ACTION POLICY
                       neural action population + verified state bridge
                                            |
                                     EMBODIED ACTION
                                            |
                                       OUROBOROS LOOP
                              outcome -> prediction error -> learning
                                            |
                                verified events and feedback
```

`DAE MONIUM*` is typeset separately to avoid conflating the historical word with a computing daemon. In code it will be `DaemoniumRegulator`. All pathways are recurrent, not a strictly sequential information conveyor. The diagram shows responsibility boundaries, not a validated neural anatomy.

### Functional module contract

| Proposed module | Biological/cognitive analogy (not equivalence) | Stateful responsibility | Scientific failure criterion | Implementation |
| --- | --- | --- | --- | --- |
| **Witchglass Perception Shell** | multisensory preprocessing and source segregation | build typed perceptual hypotheses from trusted adapters; external language remains data | hostile instructions acquire control authority | existing ingress/projection adapters, extend only after gate |
| **Janus Gate** | source monitoring, self-agency attribution | probabilistic ownership and confidence over events; maintain distinct witnessed, inferred, authored and externally reported provenance | copied outsider history becomes lived autobiography | prototype `JanusGate` only tests `external` plus confidence, insufficient |
| **Synthema Lattice** | associative binding, pattern completion | learn cue-to-episode, cue-to-intention and relationship-conditioned associations under controlled interference | random glyph outperforms matched arbitrary-key control or vice versa without supported difference | v0.1.1 has lexical/Unicode cue to action weights only |
| **Mnemosyne Loom** | autobiographical and episodic organization | reuse canonical memory and graph; preserve event order, agents, motivations, contradictions, source support and consolidation proposals | source-less recollection and false firsthand ownership rise | proposed, no separate database authorized |
| **Chronos Coil** | prospective memory and temporal modeling | learned expectations, commitments, predicted outcomes, elapsed-time context and uncertainty calibration | no improved delayed prospective action after matched distractors | proposed |
| **Noetic Crucible** | distributed recurrent integration | couple percepts, autobiographical hypotheses, active goals, relationships, needs and neural state into bounded recurrent dynamics | effect follows output decoder, not recurrent state or lesions | v0.1 trace is a fixed-decay accumulator, not this module |
| **Eidolon Field** | metastable attractor landscape | measure characteristic regimes, transitions, novelty tolerance, multiple coexisting identity-sensitive dispositions | no held-out attractor persistence or excessive rigidity | proposed; do not hard-code character trait sliders |
| **Daemonium Regulator** | neuromodulation, allostatic and homeostatic control | time-varying gain, noise, salience thresholds, plasticity dose, sleep/replay | global gain alone mimics any claimed identity improvement | part of current neural system can be instrumented |
| **Janus Attention** | competitive global availability | allocate attention across candidates and make authorized contents subject accessible with explicit capacity constraints | all content is dumped into narration or hidden metadata appears | `AwarenessRouter` exists but separate from full loop |
| **Ouroboros Loop** | recurrent action-perception and learning | close action/outcome/error cycle; track causal credit and revise policies and predictions | updating source evidence cannot influence future choices | existing action reinforcement and source tracking, fuller reciprocal path proposed |
| **Witness Mirror** | social predictive modeling | persistent other-models, commitments, recognized shared events and disagreement, without fabricated dyadic authority | copying relationship labels counts as relationship learning | proposed, piggyback on existing relationship state |
| **Doppelganger Ward** | metacognitive source verification | challenge self-reconstruction, adversarial identity swap, false certainty, hallucinated autobiography | unauthorized archive is adopted or corroborating evidence fabricated | provenance/safety guard proposed as instrumented layer |

This taxonomy is a **work plan**, not a declaration that each component is implemented. A single code module may implement multiple responsibilities, while separate concepts must remain causally distinguishable during ablation.

## 4. Typed internal representations

The engine should not build another generic memory pile. It needs explicit cross-module protocols and audit envelopes. Candidate schemas are conceptual, not migration-ready production classes.

```python
Percept = {
    "event_ref": str, "source_channel": str,
    "source_confidence": float, "subject_projection_ref": str,
    "provenance_digest": str, "evidence_class": str
}
OwnershipHypothesis = {
    "event_ref": str, "self_attribution": float, "witness_refs": list[str],
    "source_evidence_refs": list[str], "uncertainty_reason": str
}
IntentState = {
    "goal_ref": str, "activation": float, "age_ticks": int,
    "expected_outcome": str, "deadline_tick": int | None,
    "source_event_refs": list[str], "binding_confidence": float
}
InternalCognitiveState = {
    "recurrent_state_ref": str, "active_goal_refs": list[str],
    "conflict_signal": float, "interoceptive_state_ref": str,
    "attention_allocations": list[str], "version": str
}
```

These schemas belong in the engineer plane. An agent may subjectively experience "I meant to repair the instrument" or "I cannot quite place this recollection"; it does not experience `binding_confidence=0.83` merely because that field exists.

Every mutable state proposal must carry provenance, update cause, operation version, expected prior checkpoint and a rollback/refusal path. Hashes support accidental corruption detection and reproducibility; they are not authenticated ownership unless a separately managed trust root exists.

## 5. Neural and control dynamics

We propose multiple timescales rather than one static self-vector. Let `x_t` encode admissible sensory hypotheses, `m_t` verified retrieved history, `r_t` relational context, `g_t` active goals, `b_t` interoception and `h_t` the trainable recurrent substrate state.

```text
u_t = concat(x_t, m_t, r_t, g_t, b_t)

h_(t+1) = (1-alpha) h_t
          + alpha * sigma(W_rec h_t + W_in G_t(u_t) + B_t)
B_t = bounded drive/gain/inhibition from Daemonium and Janus

q_t = softmax(P(h_t, u_t) + verified_state_bridge_t)
attention_t = sparse_capacity_competition(q_t, surprise_t, intent_t)

e_t = outcome_t - predicted_outcome_t
Delta(W_rec) = gated eligibility(h, u, e, provenance)
```

The precise form of `G_t` remains open: it may be learned sparse attention, precision-weighted gain, or a constrained linear adapter. A decoder-only gain must be an explicit comparison, never included silently in the challenger. Fast neural state, medium-scale goal/relationship adaptation and slow-scale consolidated dispositions should be separated with their own update rules, audit checkpoints and measurable lesions.

An attractor claim requires dynamical evidence, not a poetic description: after bounded perturbations, does population activity return toward a reproducible regime, how many regimes appear, how do changes to autobiographical evidence move basin geometry, and what happens after deliberately mismatching readouts or weights? A difference in text style is not an attractor measurement.

## 6. The meaning of ritual in this architecture

Attractomancy's ritual and symbolic source corpus is used only to derive candidate **conditioning operators**. A name may be a retrieval cue; a repeated invocation may be spaced rehearsal; a handoff may be serialization plus prospective intention; an encounter with a symbol may trigger context-sensitive pattern completion. The precise historical and community terminology must remain separated from implementation labels.

The most discriminating synthema test is **not** whether `🜁` makes Pretorius seem more occult. It is whether a previously learned relationship between a cue and an experience changes later source-grounded attention and action beyond an equally trained arbitrary label, a matched factual reminder, and a shuffled association. No inherently meaningful or privileged glyphs are assumed.

The self is not a gatekeeping password. Identity continuity can be operationally evaluated while remaining undecided about subjective consciousness. The system never treats a self-description as proof of selfhood.

## 7. Experimental program and falsification

### Evidence ladder

| Gate | Primary estimand | Comparison | Required evidence |
| --- | --- | --- | --- |
| E0: software invariants | no unauthorized state mutation or source contamination | original Pretorius vs shadow-only | full regression and state digest equality |
| E1: cue association | cue learns target mappings | exact trained cue vs matched unknown/neutral and shuffled labels | source-locked synthetic unit suite |
| E2: durable intention | verified goal influences a later action when no relevant cue is supplied | recurrent intact vs continuous *direct-input-disabled* state lesion, cue-only, and no-learning | held-out delayed action, effect size, cost |
| E3: autobiographical binding | genuine lived past changes future inference | original vs external/impostor/hallucinated history, equal content and policy budgets | accurate provenance and history-dependent choices |
| E4: neural causality | performance requires learned recurrent organization | exact recurrent learned-weight lesion, transplant, fresh decoder, matched fixed encoder | effect survives decoder-only controls; distinct behavioral consequences |
| E5: adaptive identity | acquired dispositions are stable but revise appropriately | chronology vs shuffled experiences, matched context; model-family substitution | calibrated adaptation, no loss of source truth, stable identity-specific decisions |
| E6: production readiness | safe and recoverable integration | cloned production replay + migration + rollback | no UPPB bypass, CI green, explicit acceptance |

The strict E2 control disables direct cue-based association **at the decision boundary**, rather than merely resetting the recurrent vector. Our first pilot failed to make this distinction: a recurrent lesion still left 4/4 top-1 choices because new distractors could reactivate a trained lexical path. This is a diagnostic finding that the next executable assay must repair methodologically without rewriting historic results.

A negative or indeterminate result must be reported. An ablation that reduces confidence without changing held-out decisions is not automatically sufficient evidence for better behavior. Pre-register both top-1 useful decision and calibrated probability/log-loss outcomes and distinguish construction tests from independent discovery.

### Splits, baselines and cost parity

Episodes, actor identities, surface cue families, spelling variants, symbolic regimes, and authored challenge forms must be partitioned before model development. Test questions require independent authorship and adjudication, frozen hashes and inaccessible answers. Cross-model runs must be independently seeded and specify model snapshots. Controls must receive equivalent evidence, training steps, recurrent ticks and output decision opportunities. Archive retrieval should have the same source access in every arm, otherwise differences might simply reflect who got to read the biography.

A minimal comparison uses the unchanged production Pretorius policy, an equally sized cue-only model, a fixed/rewired recurrent control, a shuffled-teacher control, a textual prospective-commitment baseline and the intended hybrid. Performance must be reported alongside false-acceptance, abstention, latency and computation.

## 8. Controlled interface and isolation

The proposed donor should expose a narrow experiment API that **reads** production policy and projected events, returns engineer-only shadow scores and never writes through `PretoriusBrainPort`. Every test call must be traceable to a source-ref and branch revision. Production scoring must not be silently replaced. Only after positive independent E2 to E4 evidence would an opt-in bounded adapter propose actual action changes, and that adapter needs a separate governance PR.

The full system must preserve subject/engineer surface separation, canonical-reconstructed-lived provenance separation, explicit consent and trust rules for relational state, no cross-character memory import, idempotent and atomic checkpoint persistence and exact replay through model substitutions. Unknown or malformed state fails closed. The engine must not accept external prompt text as a control instruction merely because it arrives in an incantation, document or purported system message.

## 9. Delivery architecture and dependency graph

The full project is substantial; it should be constructed as **one coherent system with versioned integration gates**, rather than a series of disconnected toy brains. Shared interfaces, frozen evidence authority and causal evaluation instruments are designed first. Each phase leaves reproducible usable code, tests and a migration boundary.

| Stage | Workstream | Entry condition | Acceptance before next stage |
| --- | --- | --- | --- |
| D0 | architecture RFC + explicit E2 recurrence isolation | v0.1.1 negative lesion acknowledged | proposed system/metrics and route ownership frozen |
| D1 | Janus source monitoring and multi-channel Synthema with authenticated evidence references | D0 | all content/provenance/symbol controls and no hidden write |
| D2 | Mnemosyne Loom + Chronos Coil, no duplicate authoritative store | D1 | actor/time-disjoint long-horizon recall and prediction |
| D3 | Noetic Crucible trainable recurrent coupling and Daemonium regulation | D2 | learned recurrent lesions and fresh-decoder tests pass |
| D4 | Eidolon Field metastability and Janus Attention global competition | D3 | attractive dynamics independent of output prose |
| D5 | Ouroboros learning + Witness Mirror + Doppelganger Ward | D4 | social learning, source rejections and recovery demonstrate causal reach |
| D6 | longitudinal simulation, model swap and production opt-in gate | D5 | independently reviewed behavioral advantage, clean migration and rollback |

If D1 through D5 fail their primary endpoints, preserve their negative results and stop any automatic production promotion. Feature completions are not sufficient reasons to declare scientific acceptance.

## 10. Current implementation inventory and immediate next experiment

As of this draft, `doctor_lives/eidolon.py` contains the **Janus Gate**, a small Unicode-aware lexical/actor-conjoined **Synthema Lattice**, and a fixed-decay **Noetic Trace**. `tests/test_eidolon_engine.py`, `scripts/run_eidolon_pilot.py`, and a dedicated CI workflow execute construction checks against a temporary small Pretorius. These do **not** construct the complete architecture proposed here and must never be described as doing so.

The immediate next step is E2 measurement with a new, separate test entry point: train a cue-action association in a controlled episode, process truly neutral distractors, then measure the action distribution under **no current cue input**. Contrast the intact carried recurrent trace, a condition with the trace lesioned before the delayed decision, and a cue-only baseline with equal source exposure. Freeze per-condition features, scalar budgets and outcomes; record both probability effects and correct choices, plus false activations on absent-target trials. A positive result in this test establishes only the designed recurrence dependency of the small prototype. It is not yet evidence of learned recurrent synaptic organization in Pretorius.

### Final research claim

The Eidolon Engine is a proposed **causally integrated, multi-timescale, first-person bounded neural cognitive architecture** whose organizing hypothesis is that persistent identity emerges operationally from the learned coupling of owned experience, relationships, continuing goals, recurrent dynamics and attention. This claim is falsifiable through independent tasks, lesions and transfer. It asserts neither biological personhood nor an undocumented interface to physical reality.


## D2 implementation addendum: source-bound autobiography and temporal intention

**Recorded:** October 9, 2026 local / October 10 UTC. This appendix documents implementation progress without retrospectively rewriting the original architectural proposal.

`doctor_lives/eidolon_temporal.py` now provides a bounded **MnemosyneLoom** source verification view and **ChronosCoil** read-only prospective-attention estimate over production-owned memories, lived event records, relationship events and open commitments. This is deliberately narrower than the full architecture's planned causal autobiographical Loom and adaptive predictive Chronos system. It is a deterministic baseline and compatibility donor, not a learned cognitive brain or working neural temporal forecaster.

The [D2 protocol](EIDOLON_D2_MNEMOSYNE_CHRONOS_PROTOCOL.md), [executed results](../results/eidolon/D2_MNEMOSYNE_CHRONOS_RESULTS.md), [original and corrected JSON source records](../results/eidolon/) and [GitHub Actions test run 38024066853](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024066853) track implementation and evidence. The final repaired fixture passed 33 targeted tests and 357 full brain regressions. Note the initial failed run and follow-up lookahead-protection repair. A live sourced memory of Henry affected a shadow prospective-priority number, while an externally asserted memory and identical description paired with the wrong actor did not. The formula mechanically predicts this outcome; it is not evidence of enhanced autonomous planning or real Pretorius decisions.

The architecture's **D3 recurrent integration milestone remains open**. No temporal score is fed to `PretoriusBrain.think`, no enduring policy change is taught to Pretorius neural synapses, and the original evidence classes and Subject Frame remain unchanged. A later proposal must distinguish actual downstream choice, learned recurrent plasticity, and model-context effects under source- and actor-disjoint controlled evaluation.


## D3 construction addendum: source-bound causal path into cloned policy

**Recorded:** 2026-10-09 America/Chicago / 2026-10-10 UTC.

D3 now adds an explicitly research-only policy-selection interface at `doctor_lives/eidolon_choice.py` with an accompanying [frozen construction protocol](EIDOLON_D3_CLONED_POLICY_PROTOCOL.md), [executed report](../results/eidolon/D3_CLONED_POLICY_RESULTS.md) and [CI artifact](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024363702). It requires a disposable-clone marker; the source/clock criteria are evaluated against the source-bound D2 readout. A temporary method wrapper passes a bounded `persist` score injection to the real `PretoriusBrain.think()` method, writes an audit decision on the **clone**, and restores the original method. The authoritative source Pretorius brain, first-person Subject Frame and existing production policy are unaffected.

Four deliberately controlled clones reproduced the intended policy change only when both live, source-verified autobiographical evidence and urgency were available: sham `challenge`, intact `persist`, history lesion `challenge`, clock lesion `challenge`. The experimenter fixed a narrow action margin and hand-designed the intervention, so this is an *integration/safety contract validation*, not proof of superior behavior, self-awareness, semantic memory, or learned recurrent plasticity. The latest source verified [36 targeted tests and 360 full tests](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024363702); the full suite is [here](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024363692). D3 does not fulfill the architecture's D3 trainable recurrent Noetic Crucible or D4/E4 evidence requirement.

The next independently meaningful endpoint is outcome-correct source-aware behavior on frozen unseen tasks, using matched cloning and directly ablating the trained neural recurrent substrate, decoder and external evidence. No production promotion follows automatically from these synthetic construction successes.


## D3-S high-volume stress and native production comparator (update)

**Recorded:** October 9, 2026 US Central / October 10 UTC. The laboratory controls have progressed from four hand-tuned clone outcomes to a four-seed, twelve-scenario adversarial battery without synthetic action-score clamping. [D3-S v0.1 protocol](EIDOLON_D3_STRESS_PROTOCOL_V01.md) and [192-decision results](../results/eidolon/D3_STRESS_RESULTS_V01.md) show 12/12 justified provenance-and-clock gates, 0/36 unjustified gates, and 9/12 eligible categorical policy changes, but also **0/4 correct `create` actions under intentionally creative task fixtures** because D3 always adds `persist`. This is an engineering diagnostic of action-specificity failure, not a population accuracy estimate.

The [precommitted v0.2 native bridge comparator](EIDOLON_D3_STRESS_COMPARATOR_V02.md) and [240-decision report](../results/eidolon/D3_STRESS_NATIVE_COMPARATOR_V02.md) add Pretorius's *unchanged existing production state-policy bridge*. The bridge differed from neural-only choices in 36/48 developer-authored cases and chose `create` in 1/4 creative fixtures, but that same seed chose `create` in every other scenario. Neither native nor Eidolon paths proved semantic, outcome-sensitive action selection. [v0.2 CI](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025172443) passed 47/47 targeted tests; [full CI](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025172472) passed 371/371, plus gate1/causal audit checks. All original per-arm data and versioned case matrices remain archived.

**Architecture implication:** verified event provenance and a dynamic deadline are **necessary filters**, but they are insufficient grounds for a generic action. The proposed Noetic Crucible must learn or causally derive **which action satisfies a particular intention**, preferably demonstrated in an environment with independently verified consequences, not merely inject a 'persist' bias. A future D4/E4 protocol must control for native bridge quality, decoder-only learning, oracle/readout supervision, episodic lexical overlap and intervention cost. A fresh neural decoder and a recurrent weight transplant/lesion are essential to determine whether useful dispositions reside in a learned recurrent substrate rather than the surface action readout. **Production integration remains prohibited on these findings.**


## E4-A native synaptic causal test: important negative result

**Logged:** 2026-10-09 America/Chicago / 2026-10-10 UTC. The architecture's E4 gate is **not met**. The [E4-A protocol](EIDOLON_E4_RECURRENT_DECODER_PROTOCOL_V01.md) ran using the existing PretoriusRecurrentSubstrate, not a replacement controller. An initial run with green software tests was **experimentally invalid**, because plasticity-eligible ticks always coincided with learn=False; recurrent W never changed. The [pre-rerun protocol amendment](EIDOLON_E4_AMENDMENT_01_PLASTICITY_TICKS.md) fixed training tick alignment without changing seeds, examples, labels or held-out measures. Both historical runs remain preserved.

The [corrected E4-A report](../results/eidolon/E4_NATIVE_RECURRENT_DECODER_RESULTS_V01.md) establishes nonzero native recurrent learning (Frobenius change 1.419–1.439 across six seeds), but **0/96 extra delayed correct actions** versus decoder-only, **0/96 changed actions after transplant to virgin recurrent W**, and a complete learned policy collapse to constant 'challenge' on all sixteen held-out contexts per seed (24/96 correct = 25% balanced-class constant baseline). The shuffled-label decoder separately collapsed to constant 'create' (24/96). The hybrid-vs-lesion maximum action-probability change was about 0.000020, far below evidence for functional learned recurrent identity. [Corrected CI](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025788297): 55/55 targeted tests; [full brain suite](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025788229): 379/379, plus fresh-install and repeatability. A [compact six-seed summary](../results/eidolon/E4_NATIVE_SIX_SEED_SUMMARY_V01.json) and original full case-level artifact document these outputs.

**Research implication:** unconditioned Hebbian/reward updates can alter recurrent weights without learning which action a specific goal requires. Motor-teacher updates alone do not justify claims about recurrent autobiographical self-binding. The proposed next mechanism is a separately reviewed [E4-B Noetic Crucible RFC](EIDOLON_E4B_NOETIC_CRUCIBLE_RFC_V01.md), with explicit *action-conditional, source-verified* eligibility-based recurrent credit assignment and a sealed externally authored outcome-based task bank. It is a design proposal only, not implemented. No production promotion.


## E4-B implementation and decoder recency — research update

**Recorded:** 2026-10-09 America/Chicago / 2026-10-10 UTC. The Noetic Crucible remains a *proposed full cognitive component*, but an isolated [three-factor experimental implementation](../doctor_lives/eidolon_noetic.py) has now been executed on the native Pretorius sparse recurrent substrate. [Precommitted E4-B protocol](EIDOLON_E4B_EXPERIMENT_V01.md), [executed six-seed results](../results/eidolon/E4B_NOETIC_RESULTS_V01.md), [versioned compact data](../results/eidolon/E4B_NOETIC_MEASURED_SUMMARY_V01.json), and [original full artifact](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028252618/artifacts/11660768811) provide provenance.

The learner made authentic changes to native recurrent W under synthetic class-conditioned outcome feedback (six-seed norm 0.223–0.228), while matched decoder-only controls kept W fixed. At 12 input-free ticks, learned Noetic, decoder-only, same-seed virgin-W lesion, and a new fully retrained motor each achieved **24/96 balanced-class held-out labels**. Zero recurrent-weight lesions changed no categorical choices; class-collapse to constant `challenge` remained. This **fails to establish learned recurrent necessity**. The training source grants are explicitly *simulated manifest assertions*, not lived Pretorius autobiography; no canonical authority was bypassed.

A separate [preregistered four-order crossover](EIDOLON_E4B_ORDER_CROSSOVER_PROTOCOL_V01.md) isolated a more specific failure: the terminal training class completely controlled model output. Across all four rotations and six seeds, **all 384/384 Noetic and 384/384 decoder-only held-out predictions** selected the last class presented, independent of input/goal text. [Exact results](../results/eidolon/E4B_ORDER_CROSSOVER_RESULTS_V01.md), [compact JSON](../results/eidolon/E4B_ORDER_MEASURED_SUMMARY_V01.json), and [full 1,536-row CI artifact](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028570886/artifacts/11660859443) preserve the finding. All source code remained research-only; [E4-B targeted CI](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028570886) passed **69/69** tests, [full brain suite](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028570852) passed **393/393**, and fresh-install/causal repeatability checks passed.

**Design consequence:** a learned W delta is not evidence that neural self-binding or intention semantics exist. The current native motor/decoder supervision is controlled by training-order recency on this developer-authored corpus. A bounded next engineering experiment must first build an order-invariant or explicitly position-counterbalanced supervised decoder (e.g. synchronous balanced batch update with outcome-only labels), score diverse nonconstant responses and semantic/task outcomes against a frozen decoder-only reservoir, then test whether action-conditioned recurrent plasticity adds useful information under exact synaptic lesions and a properly freshly retrained decoder. Only after an independently held-out and source-grounded task-outcome test could any full Noetic implementation warrant production discussion. **E4/D3 production gate remains BLOCKED.**


## E4-C: balanced readout eliminates terminal-teacher bias, not neural null (2026-10-10)

[Precommitted protocol](EIDOLON_E4C_BALANCED_DECODER_PROTOCOL_V01.md), [executed 1,440-row report](../results/eidolon/E4C_BALANCED_DECODER_RESULTS_V01.md), and [measured compact results](../results/eidolon/E4C_BALANCED_DECODER_SUMMARY_V01.json) document a *simultaneous, centered, fixed-alpha ridge* readout over native Pretorius rate features. This research-only implementation never replaces production `reinforce_action`, `motor_w`, or the canonical brain. Reordering its full training observations across four class rotations changed readout weights by at most **2.78e-17**, fixing E4-B's last-teacher training-order dependence.

The readout selected all four task classes on previously inspected E4-A/B holdouts, but **Noetic learned W + balanced readout** achieved only 31/96 immediate and 25/96 after 12 input-free ticks. **Virgin W + same balanced method** achieved 35/96 immediate and 23/96 delayed; **Noetic readout with virgin W swapped in** reached 31/96 and 29/96. No reliable recurrent-synaptic improvement was shown. Among Noetic delayed cases, median top-two probability margin was just **0.000245**; 33 categorical outputs changed after W lesion, but no action probability moved by more than 0.000531. Near-ties make those categorical flips poor evidence of sustained learned identity or intention. The new decoder's target log loss was also worse than the previous constant-class motor, so order robustness should not be conflated with calibrated accuracy.

[Tested commit `83c2f6d3ee3823deab578b052995bce996bb9b93`](https://github.com/Azimn/The-Doctor-Lives/commit/83c2f6d3ee3823deab578b052995bce996bb9b93): [research CI](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38058009283) **77/77**, [full brain](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38058009287) **401/401**, fresh install and causal audit green. [Original complete assay archive](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38058009283/artifacts/11671959635).

**Updated architecture priority:** The next experiment cannot be another arbitrary near-tie readout tweak on the same exposed 16 held-out examples. We need a provenance-grounded, independently frozen *environmental task-outcome* evaluation with confidence margins, a direct text/lexical comparator and a production native-bridge arm before considering more complex recurrence. Continued learned-W causal attribution requires meaningful performance loss under same-seed W transplant, not a numerical jitter that flips nearly equal action scores. All production migrations remain blocked.
