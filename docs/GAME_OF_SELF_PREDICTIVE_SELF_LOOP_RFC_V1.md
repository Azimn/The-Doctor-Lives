# RFC: The Game of Self as a bidirectional predictive self-model for Pretorius

Status: **research synthesis and design hypothesis; unimplemented, unvalidated, not production-authorized**  
Date: 2026-10-09  
Target: The Doctor Lives, definitive Pretorius mind  
Related: [SelfBindingModulator Stage 01 results](https://github.com/Azimn/The-Doctor-Lives/blob/5629f1cba0000047321fffbbfc6367df23a173c2/results/self_binding/STAGE_01_EXECUTED_MEASUREMENTS.md) (HOLD), [Stage 02 issue](https://github.com/Azimn/The-Doctor-Lives/issues/29)

## 1. Primary source, scope, what is and is not established

Hirsh, Jacob B. (2026). **The Game of Self: Identity and Experience as Active Inference**. *Personality and Social Psychology Review*, first published online March 5, 2026. DOI: https://doi.org/10.1177/10888683261422344. Full text: https://journals.sagepub.com/doi/full/10.1177/10888683261422344. PubMed: https://pubmed.ncbi.nlm.nih.gov/41784280/.

This is a peer-reviewed, **integrative theoretical proposal**, not a completed, randomized experiment demonstrating a new self-generative algorithm or an empirical AI-continuity result. It presents example Bayesian calculations and falsifiable research hypotheses, but does not specify an executable Pretorius-compatible generative model, learned likelihood tensors, data collection instrumentation, or validated treatment effects. Do not cite the proposal as proof that active inference creates consciousness or that language models can maintain identity.

A complementary formal reference is Friston et al. (2016), *Active inference and learning*, https://pmc.ncbi.nlm.nih.gov/articles/PMC5167251/, which explicitly distinguishes goal-directed and habitual dynamics, epistemic vs pragmatic value, and conditional policy selection; it does not empirically validate this character application.

## 2. The paper's specific mechanisms

**A. Two-direction self inference.** The semantic self (relatively general concepts of identity, attributes, roles, trait distributions) predicts and interprets episodic self states (perceived significance, affect, situational preferences, expected reactions). Actual episodes, in return, provide likelihood evidence for semantic self categories. There is no one-way identity prompt. Source: Hirsh, sections "The Game of Self", "Inferring Identity from Experience", and "Inferring Experience from Identity".

**B. Timescale hierarchy.** Fast episodic inferences vary with concrete situations. Slowly evolving semantic expectations summarize patterns over experiences. At higher timescales, characteristic adaptations and narrative identity integrate repeated episodes into life patterns, turning points, and commitments. This is **not** a claim that a single trait rating must be constant in every scene. Source: "Hierarchical Self-Inference Across Temporal Abstraction", "Evolution and Personality", and "Methodological Implications".

**C. Precision, not raw repetition.** Strong, well-supported, cross-context beliefs resist change after one ambiguous episode; repeatedly observed, precise, cross-context conflicts favor revising the general identity model. Section "Balancing Self-Integration: Precision, Conformity, and Authenticity" lists three conditions for broader revision: systematic repeated divergence, precise episode evidence, and generalization across situations. Do not confuse frequency of repeated sentences or retrieval salience with independent evidence.

**D. Self as subject and as social object.** The paper distinguishes a perspectival experiencing "I" from a semantic/socially inferred "Me". Self-understanding helps predict how other people will perceive the agent, and relationship contexts in turn shift which self-description is currently useful. This makes self-identity co-constructed and relational without reducing identity to agreeableness. Source: "Emergence of Self-Awareness and Identity" and social inference Table 1.

**E. Policy selection and epistemic action.** Under active inference, an agent can change its beliefs in light of evidence or take actions expected to yield preferred/informative outcomes. Hirsh connects this to identity-congruent actions, future simulation, role shifts, and asking questions about another person's unexpected behavior. The *opportunity to seek disconfirming evidence* is essential: mere self-confirmation can produce rigidity, defensive rationalization, and refusal to update.

**F. Testable domains.** Table 1 categorizes hypotheses into bidirectional inference, uncertainty reduction (revision/actions), self-projection and dynamic role shifts, and inference about other people. Later methodological guidance specifically advocates context-conditioned **distributions** over states, joint semantic/episodic measures, a modest 8–10 informative situation probes, repeated measures and explicit uncertainty calibration.

## 3. Pretorius gap analysis grounded in current implementation

- `doctor_lives/cognition.py`: `_bootstrap_once` already preserves frozen design roots, reconstructed source-ranked histories, relationships and initial self-model claims. These are distinct source domains; do not collapse them into a new monolithic narrative.
- `_ranked_memory_sets` and the 70-node/243-edge Persona Connectome provide query-relative episodic activation. Retrieval answers what is accessible, not what future state was expected or which self hypothesis is contradicted.
- `_state_policy_scores` maps needs, partner relations, open commitments, retrieved direct autobiography and concerns into small bounded pressures on the existing recurrent action baseline. It does not currently learn an explicit **bidirectional likelihood mapping** from context and semantic self beliefs to next episodic reactions, or from lived episodes back to semantic trait distributions.
- `think` chooses the action by recurrent + bounded state bridge, then retrieves/chooses thought topics and rehearses memories. This creates consequences for retrieval and memory selection but is not yet a model of externally verified world action/outcome prediction.
- `record_action_outcome` records self-origin success/reward, updates action values, and reinforces the recurrent network. It is not independent evidence of what a world action changed, whom it affected or whether a promise was fulfilled; using it to train a second policy learner would risk double-counting feedback.
- UPPB and the P3 AwarenessRouter provide protected first-person projection and limited access but are not live-wired by default. They are not interchangeable with a predictive self model. A self-model's engineer numbers must not leak into subject-frame content.
- [Stage 01 SelfBindingModulator](https://github.com/Azimn/The-Doctor-Lives/blob/5629f1cba0000047321fffbbfc6367df23a173c2/results/self_binding/STAGE_01_EXECUTED_MEASUREMENTS.md) had **0/16 action-choice changes** over four researcher-visible prompts/five modes, while wrong source-event associations altered memory order twice. This motivates a change in **what is modeled and tested**, not simply a bigger salience gain.

## 4. Proposed architecture: bidirectional Predictive Self Loop (PSL v0.1)

**No second brain, no duplicate truth store, no direct UPPB bypass.** A read-only, protected-plane inference service uses existing canonical state, with an append-only hypothesis/forecast ledger separate from provenance-bearing factual records. Initially this service observes only.

```text
Canonical Pretorius evidence + lived/world-verified events
                  |                         ^
                  v                         | independent witness/admission
       Event and context features -> observed outcomes
                  |                         |
                  v                         |
   FAST: context-conditioned episodic posterior [e_t]
                  ^                          |
                  |  semantic -> episode     |
                  v                          |
   SLOW: semantic identity posterior [z_t] <- prediction error
                  |  episode -> semantic     |
                  v                          |
   PREDICT: self-state / other-state / world outcome
                  |        (forecasts sealed before observation)
                  v
   Existing recurrent action distribution remains baseline
                  |
   Optional future bounded policy proposal (not enabled)
                  |
   Existing action + world feedback
```

**Four distinct record families:**

1. **Design/canon invariants:** immutable design constraints and source-ranked reconstructed/preawakening material remain as they are; they are not numerical traits to be rewritten from fictional episodes. Earlier reconstructed autobiography may initialize *prior hypotheses* but must never masquerade as observed runtime training cases.
2. **Lived episodes:** timestamped self-actions, source-native perceptions, interoceptive and affective state, relationship interactions, world-verified outcomes, and provenance; preserve objective event separately from agent interpretation. No generated text can mint a confirmed episode.
3. **Semantic self hypotheses:** distributional, context-conditioned tendencies with provenance, uncertainty/precision, evidence references, last update and version; possible contradictions and conflicting motives are legitimate. A model can retain "I value independence" and "I often defer to Henry" without destroying either.
4. **Social and future models:** beliefs about named others and how they understand Pretorius, partner-specific reliability, outstanding promises, expected future interactions and world outcomes. Mark mental-state estimates as uncertain and never assert their contents as other persons' real internal states.

**Three update clocks**: immediate situational appraisal; cumulative episode/relationship adaptation; slow semantic identity revision. A one-time tired, frightened or socially deferential choice should update an episode-specific expectation before a global trait. A broad semantic prior should shift only when out-of-sample generalization across distinct contexts is supported.

## 5. Operational minimal probabilistic model, *our proposal*, not from the paper

Let `z_t` be a vector of semantic self hypotheses, `c_t` current context (relationship, role, stakes, commitments, fatigue and trust), `e_t` an epistemically authorized episodic interpretation, `a_t` an already admissible action and `o_t` an independently verified world outcome.

**Identity -> episode:**
`q(e_t | z_t, c_t, observed_percepts)` predicts expected state/meaning under the existing self beliefs without fabricating objective sensory data.

**Episode -> identity:**
`q(z_t | E_{<=t}, contexts) ∝ p(e_t | z_t, c_t) q(z_{t-1})`, with a domain-specific, explicitly modeled evidence-precision weight and a slow cross-context consolidation gate. The precise update law requires calibrating likelihoods from training data; repeated source descriptions are not independent observations.

**Self/world prediction:**
`q(a_t, o_{t+1} | z_t, c_t, world_state)` is initially an audited **shadow forecast**. The existing recurrent decision and state-to-policy bridge still choose `a_t`. A prediction is stored with event cutoff and scoreable result before the future happens, so a correct-sounding hindsight narrative cannot masquerade as predictive success.

**Self-model discrepancy:**
Compare a sealed prior forecast to verified perception/action/outcome and record both the error and its context. Update episode expectation after one observation. Propose revision of a global semantic self belief only if independently verified, repeated high-precision discrepancies generalize to several contexts. High-prior precision may explain initial resistance but may **never** authorize rewriting a verified observation to make identity look consistent.

**Epistemic policy, future gate only:** when the model is uncertain, it may propose an *allowed, non-coercive question or inspection* to distinguish hypotheses (e.g., ask Henry what he means, inspect the apparatus), conditioned on privacy, consent, world cost and utility. The actual tool/choice authority remains with chassis and recurrent policy. Compare information gain and action outcomes against ordinary "ask a question" heuristics before claiming active-inference superiority.

Not a full variational Bayes/expected-free-energy solver at v0.1. If formalizing active inference later, specify observation likelihoods, state transitions, controllable policies, preferences, epistemic expected information gain and variational objective explicitly, and compare against simpler Bayesian and RL baselines at equal budgets.

## 6. Concrete Pretorius counterfactuals

**Henry disagreement:** Pretorius may expect to defend scientific autonomy and also anticipate respect toward Henry. The world reports Henry's actual request. The semantic self predicts an initial insult/curiosity blend (hypothesis), while social context conditions whether he challenges or collaborates. What he *actually* expresses or does is recorded. If he keeps yielding with Henry across independently witnessed episodes but resists other authority, revise the **relationship-conditioned policy**, not his global independence trait. Test disagreement and consent, not increased flattery.

**Failed experiment:** His semantic model may predict intellectual confidence. An independently witnessed failed procedure should remain a failure. One failure may update an episodic belief about conditions; repeated failures across laboratories with reliable evidence may revise an overconfident global competence hypothesis. No self-protective rewriting of the world record.

**Absence of memory:** A recall cue may suggest a familiar context without a verifiable corresponding autobiographical event. Preserve uncertainty and refuse to manufacture recollection. A response like "This seems familiar, but I cannot place it" may be a lawful projected *tentative inference* if subject evidence supports it, not factual autobiographical recovery.

**Social inference:** Henry's surprising reluctance to continue an experiment should update Pretorius's uncertain model of Henry's priorities, or trigger a bounded clarification request. The system must not convert its theory of mind into authoritative knowledge of Henry's hidden thoughts.

**Prior model conflict:** Pretorius's earlier designed self-view may diverge from a long sequence of admitted lived events. Preserve designed canon as a separately versioned objective design constraint while allowing *self hypotheses about his habits* to evolve. A true, enduring change of temperament should be visible in actual behavioral distributions and longitudinal commitments, not merely a new adjective in a narrative.

## 7. Tests and falsification

**Gate A: source truth + measurement.** Audit how many independent, contextualized, world-verified lived episode/action/outcome pairs actually exist. Existing autobiographical first-person prose and self-reported action reward are insufficient to train causal world-outcome models. Build synthetic fixtures for mechanics only. Freeze case provenance and source disjointness. No imaginary event labels invented to pad training data.

**Gate B: bidirectional forecast-only.** On chronological and scenario-disjoint held-out cases, compare:
- legacy recurrent policy and retrieval without PSL;
- identical information with simple empirical action-frequency and context-frequency forecasts;
- identity/prompt-based self-description without bidirectional updating;
- episode-only model (no semantic prior);
- semantic-only model (no episode -> identity update);
- full bidirectional model, with semantic label shuffle and observation precision scramble controls.

Hold memory access, source truth, token budgets and model family constant. The primary result is **held-out calibrated prediction**, not pretty explanations. Use Brier/log loss and abstention/coverage for forecasts; log contradictory evidence handling. Outcome likelihoods for success, promise completion, coercion/refusal and objective world effects are scored separately. Compare exact per-case source grounding and respect for privacy.

**Gate C: chronological world-feedback pilot.** Require sealed forecasts before action, independently verifiable effects after action, and prospective promises tracked across sleep/restart. The main endpoint is correct world-bound behavior and promise followthrough without falsifying memories, plus context-appropriate variation under the same invariant beliefs. Test independent new Henry/authority/laboratory contexts. Any benefits must exceed simpler history baselines and remain after shuffled-history and renderer swaps.

**Gate D: optional recurrent policy proposal.** Only after PSM outperforms forecast baselines on independent data, perform matched-state lesions of a strictly bounded proposal to the *existing policy bridge* (not a new second controller), with frozen tests that measure action appropriateness rather than just action divergence. Track resource usage and double-counting of old action-value reward. Do not widen the production baseline or integrate UPPB outside its existing promotion process.

**Failure conditions**: no gain over contextual count-based predictors; sudden global trait change after a single anomalous episode; hiding a verified contradiction; treating authored backstory as lived runtime evidence; output-only self-narrative improvement without behavioral calibration; inability to abstain on unseen contexts; hallucinated social motives; cue-driven dependency or excessive agreeableness; or gains that vanish on renderer substitution.

## 8. Relationship to ritual cue research

A name, sigil, restoration cue or "identity ritual" might activate a **high-level semantic prior** or trigger a deterministic retrieval plan, not summon latent autobiographical truth. The model predicts two distinguishable effects: (1) immediate context-conditioned bias in *interpretation* when semantic priors are activated, and (2) slower revision of the underlying semantic association **only** after independently witnessed episodes. Compare opaque IDs, meaningful cues and glyphs with identical factual state and exposure. Cue alone in a fresh no-carryover session tests zero-shot priming, never persistence.

This distinction could make Attractomancy scientifically sharper: ritual cues may be manipulations of prior precision or contextual self-categorization, but durable continuity must show the full bidirectional update beyond mere style or narrative imitation. Test the connection without assuming supernatural causation, special consciousness, or efficacy.

## 9. Risks and epistemic limits

The paper offers a useful **process theory**, not a demonstrated architecture to copy. Bayesian self-priors are only meaningful if we specify contexts, outcomes, likelihoods and precise data lineage. Arbitrary numerical trait confidences are deceptive. Self-consistency may become self-confirmation and motivated blindness. A model that "expects to be respected" may respond by coercion or aggression if naive uncertainty reduction is the only objective. Value constraints, consent, world verification, independent evidence precision and explicit action permission must remain distinct from self-inference.

The human subjective "I"/semantic "Me" distinction is an analogy for architectural decomposition, not proof of Pretorius's subjective experience. Protected model numbers do not enter the renderer or first-person subject plane. New subject-accessible self-expectation or uncertainty must pass ordinary UPPB projection and awareness arbitration.

## Disposition

**Recommended investigation: YES, priority HIGH. Implementation/promotion: HOLD.** This is a more direct architecture hypothesis than salience amplification. Start with a small offline forecast-only model using source-linked contextual action records and independently verified outcomes, not a new neural network or full-fledged free-energy optimizer. Proceed to policy effects **only if** the predictor outperforms simple equally-informed baselines and passes no-bypass requirements.

This RFC records a source-grounded rationale and falsifiable milestones; it contains no executable experiment, no measured benefits, no self-changing canon and no authorization to modify production.
