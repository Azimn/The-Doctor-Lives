# 2026 arXiv evidence review: which tested architecture should improve Pretorius?

Date: 2026-10-09
Status: literature review + experimental decision; **not** a Pretorius benchmark or demonstrated gain
Target: The Doctor Lives / Character Continuity research
Decision: prioritize direct reproduction of PHASE-Tree **textual conditioning** against equal-budget controls; selectively test PersonaForge's behavior-conditioning only after that baseline passes.

## Why a new comparator is necessary

The prior Predictive Self Loop v0.1 was implemented as a protected-plane shadow forecast; it was **not** an internally grounded generative character model. Stage 01A (The Doctor Lives draft PR #32; source execution `edf35dcaa6449bc2ed73a359c349e8be31e50f0b`) observed 28 selected native policy actions. PSL episode-only log loss on 8 familiar scripted cases was 1.126915 versus a simple global-frequency predictor at 1.129793, an inconclusive difference. On 4 new-context cases PSL was worse: 2.439326 versus 1.670225. Eighteen of 28 actions were `persist`. A neural/policy-choice prediction benchmark that lacks external consequences is **not** evidence of character identity continuity. Source: https://github.com/Azimn/The-Doctor-Lives/pull/32 .

The scientific target should change from "predict its own next action label" to **character-state-aligned generation, source-grounded autobiographical decisions, cross-episode adaptation, and witnessed external action success**. Literature from 2025–2026 has actual controlled experiments in those domains. However, their reported gains are on their own benchmarks; none has yet been shown to improve Pretorius.

## Primary candidates (arXiv and peer-reviewed venues; numbers belong to the respective authors)

| Priority | Paper | Directly reported measured gains | Why useful to Pretorius | Scope/cost caveat |
| --- | --- | --- | --- | --- |
| 1 | Tang et al., 2026, PHASE-Tree, arXiv:2608.06975, https://arxiv.org/abs/2608.06975 | LongEvoRoleBench long-dialogue textual mode: Char **3.004 vs 2.510** strongest PAG comparator (+19.7%), Sem **3.697 vs 3.289** RAG (+12.4%), Emb **0.314 vs 0.273** RAG (+15.1%); best across all 12 external textual cells on four long corpora. Blinded 200-response human study; GPT-4.1 human correlation r=.65; smaller descriptive n=10 subsets only +.20 Overall. | Immutable design root + mutable persona/session/moment state, typed per-field patches with resistance/evidence/cooldown gates; exactly our identified failure: stale state under long fictional history. | Metrics depend partly on LLM judge and inherited dialogue corpora; reported human comparison limited; not outcome/consent validation. Primary runs use Qwen2.5-7B with A100/H100; textual prompt route can be adapted more economically without hyper-LoRA, but gains not guaranteed. |
| 2 | Tong & Zou, 2026, PersonaForge, ACL Findings; https://aclanthology.org/2026.findings-acl.386/ | 88 characters, +19.4% personality consistency, 50-turn drift **6.3% vs 24.8%**; external RoleBench **8.4% vs 20.4%** drift and 73.2% win rate; selective activation retains 96% of full-system performance with 13.4% token overhead. | Structured contradictory motives/values/defenses + selective slow deliberation only on conflict; fits Pretorius's idiosyncrasy and cost limits. | Requires ground-truth psychology dimensions and careful handling of renderer/inner monologue; Big Five scores should not be invented as canon; these experiments are on generated role-play, not external-world behavior. |
| 3 | Jiang et al., 2026, BRIDGE, ICML; https://proceedings.mlr.press/v306/jiang26aw.html | PersonaGym 4.59 vs Qwen2.5-32B zero-shot 4.31, CoSER 59.5 vs 53.4; repository reports reduction in severe character-fidelity rupture (CF<35) from 37% to 15%. | Consistency between produced behavior, latent policy and memory; complementary concept to reconcile first-person projected events with lived state. | 32B frozen backbone + 277M trainable parameters (0.85%), 50K training steps; hardware/engineering heavyweight. Contraction proof is conditional, not real agency proof. **Do not transplant the whole framework as Pretorius default.** |
| 4 | Li et al., 2026, TiMem, arXiv:2601.02845; https://arxiv.org/abs/2601.02845 | LoCoMo QA 75.30%; LongMemEval-S 76.88%; recalled memory length reduced by 52.20% in LoCoMo. | Provenance-aware temporal hierarchy and complexity-aware evidence retrieval, compatible with append-only deep-history memory and prior connectome. | These are benchmark-specific memory QA scores, **not** actual behavioral identity or multi-session world-success outcomes. Do not replace the existing memory architecture without retrieval-specific lesion superiority. |
| 5 | Wu et al., 2026, LongMemEval-V2, arXiv:2605.12493; https://arxiv.org/abs/2605.12493 | 451 manually curated environment-memory questions; AgentRunbook-C 72.5% accuracy vs strongest RAG baseline 48.5% and coding-agent baseline 69.3%; higher query latency. | Novel world-state transition / workflow / bad-premise evidence benchmark. The methodological lesson is that witnessed environmental trajectories and premise awareness matter. | Tests memory-conditioned QA using web trajectories (some to 115M tokens), not character actions; the agentic controller incurs high overhead. |
| 6 | He et al., 2026, MemoryArena, arXiv:2602.16313, ICML; https://arxiv.org/abs/2602.16313 | Benchmark shows memory systems that nearly saturate ordinary LoCoMo-style recall can still perform poorly in interdependent multi-session action tasks. | **Evaluation benchmark recommendation**: test whether agent memories improve later task success and promise fulfilment, not just memory accuracy. | The paper primarily contributes a benchmark; it is not an off-the-shelf superior character engine. |
| 7 | Pakhomov et al., 2025, Convomem, arXiv:2511.10523, https://arxiv.org/abs/2511.10523 | On its own evaluation of 75,336 QA pairs, full-context simple strategies had 70–82% accuracy on difficult cases versus Mem0 30–45% when histories are under 150 interactions. | **Strong negative control**: do not assume vector/graph/complex memory is automatically superior for a limited corpus. Compare equal-token full contextual evidence and exhaustive reranking before adding retrieval infrastructure. | Data/implementation-specific, not a universal 150-interaction cutoff or character benchmark. |

Additional secondary sources:

- Gutiérrez et al. (ICML 2025), HippoRAG 2, arXiv:2502.14802 https://arxiv.org/abs/2502.14802 : roughly +7% associative memory over a strong embedding model, with improved factual/sense-making retrieval. Try only if independently measured multi-hop retrieval is the bottleneck.
- Chhikara et al. (2025), Mem0, arXiv:2504.19413 https://arxiv.org/abs/2504.19413 : relative +26% LLM-as-judge over one OpenAI baseline on LoCoMo and 91% lower p95 latency versus full-context. Useful production tradeoff, but not a paired comparison on Pretorius character/world behavior.
- Venkit et al. (2026), ANCHOR / Best Friends Not Forever, arXiv:2607.28818 https://arxiv.org/abs/2607.28818 : 2,008 conversations, 27 personas, mean trajectory accuracy 44.4%, even when response role seems stable; strong negative control for memory and persona confounding.
- Qi et al. (2026), Dynamic Persona Coherence, ACL, https://aclanthology.org/2026.acl-long.1336/ : long-/mid-/short-timescale state with correction loop and reported improvements on automatic Persona Consistency Critic. Caveat: scorer/corrector may share constructs, so require an independent held-out judge.
- Gadzhiev & Kislov (2026), Synthius-Mem, arXiv:2604.11563 https://arxiv.org/abs/2604.11563 : claims 94.37% LoCoMo accuracy / 99.55% false-premise robustness. **Provisional/unverified cross-paper ranking**: uses an LLM judge and compares some published systems evaluated under different configurations/metrics; human 87.9 is F1, not the same score. Requires matched independent replication before regarding these as superiority. Focus on their false-premise testing ideas, not headline "exceeds human" rhetoric.
- Zhan et al. (2026), MemoryLake matched MemoryArena study, arXiv:2608.13883 https://arxiv.org/abs/2608.13883 : reported 20.5% vs 13.6% equal-domain average success, small strata and overlapping uncertainty; illustrates that backend advantages are workload-dependent, and genuine action success remains difficult.

## Replicability, effort, licensing

**Best first reproduction: PHASE-Tree textual route.** Authors' released code: https://github.com/MemTensor/PHASE-Tree (MIT code); LongEvoRoleBench data (approx. 9 GB), released checkpoints (approx. 1.8 GB) and evaluations (approx. 6.5 GB) are referenced in the README, with separate data/model licensing. The official primary runs use Qwen2.5-7B-Instruct; the repo also reports backbone-switch tests involving Qwen3-0.6B, Gemma-4-E4B and Qwen3-32B. **We should test smaller local models rather than claim 7B GPU-era results automatically transfer.** Textual provision requires no hypernetwork training. Existing state is already partly typed, so measure retrieval + serialization cost. The author's full reproduction instructions describe GPU A100/H100 and optionally paid judge calls: not appropriate as an assumed free local deployment pipeline.

**Second: PersonaForge.** Code https://github.com/fQwQf/PersonaForge, Apache-2.0; experiment files, 50-turn drift comparison, ablation and local-model support are documented. Implement *selective conflict-oriented dual process* behind Pretorius's existing UPPB/P3 protected first-person boundary only if independently helpful. Do not show raw engineered trait numbers to the subject or trust unverified inner monologue as lived memory.

**BRIDGE** code https://github.com/Sunrich-HT/BRIDGE (Apache-2.0) has CPU mechanical smoke tests, but reproduce headline efficacy only with a larger backbone/training budget; its paper's A100 latency should not be presented as a CPU/Ollama number.

## Proposed concrete architecture, *not yet validated*

**PT-PSL v0.1 = PHASE-style hierarchical state conditioned generation + existing Pretorius records + optional PSL forecasts.**

1. **Immutable evidential root**: source-ranked design material, canonical preawakening constraints, versioned evidence manifest, and no-calibos-identity rule. The literal authorial source is not a new "lived" fact.
2. **Slow persona adaptations**: inferred context-conditional dispositions and stable-but-revisable *self hypotheses*, accompanied by competing evidence and dated version. Never overwrite reconstructed event records. World-verifiable updates require external witness, not just repeated generated text.
3. **Session state**: unresolved relationship tensions, promise status, medium-term intention, recent errors, contextual expectations, fatigue residue. Keep per-field timestamps and source edges; independently justify each update.
4. **Moment state**: current authorized perception, salient felt values, local action affordances, ambiguity/uncertainty, conversational intention. Ephemeral and strictly mediated by protected UPPB/P3 before subject access.
5. **Two-way prediction loop**: PSL can forecast and record unexpected reactions, but stays **read-only** until success on independent trials. Do not promote unverified global semantic updates simply because model produced an unexpected action.
6. **Selective dual-process deliberation**: *only* when a behavioral conflict detector reports genuine divergence between values, commitments, world observations or relationships, ask a local model for a bounded first-person internal consideration. This is a causal intervention to be tested; default zero extra inference calls.
7. **Source trace + world consequence**: auditor logs which protected facts justified a generated action and the externally verified result. Protect private engineer variables, consent and original evidence.

The improvement target is NOT "identity bonus magnitude", "more prompt tokens", or "more frequently selecting persist". It is **better source-grounded, evolved-state realization under consequential novel contexts**.

## Experimental decision tree (precommit before producing new outputs)

**Gate P0: reproduce upstream evidence first**: fixed small subset from PHASE authors' released LongEvoRoleBench with same Qwen backbone and scoring script, compare raw profile vs static PHASE vs dynamic PHASE textual. Preserve upstream license/release model IDs and evaluation rubric. If reproduction does not recover reported ordering, disclose this and do not assume an advantage.

**Gate P1: isolate on Pretorius, offline and no-world-modification**: same source-backed state, frozen generator/model/seed and identical authorized content/budget across:
A) flat factual identity + recent verified memory (baseline);
B) chronological exact transcript / exhaustive context (short-corpus control);
C) existing Doctor Lives/PSL shadow (if a renderer exists, no policy intervention);
D) PHASE-style static tree without updates;
E) full PHASE-style evolving persona+session+moment with only verified updates;
F) E plus *selective* PersonaForge-inspired conflict evaluation;
G) E with shuffled temporal/context links (causal negative control).
Any additional inference calls, tokens, latency and access to structured source data must be recorded. Equalize information, not merely number of fields; avoid giving E hidden oracle labels.

**Gate P2: independent blinded evaluator on a new source-disjoint/chronology-disjoint challenge**: score (i) character-specific situation-appropriate actions, (ii) value/boundary-appropriate disagreement, (iii) genuine relationship specificity, (iv) correct response to new facts and refusal of absent autobiography, (v) delayed commitment completion, (vi) consistent state across renderer/model swaps, (vii) externally witnessed world transition success. Include abrupt failures and no-effects. Human review and source citation should be independent from any critic used by the generator.

**Promotion**: preregistered primary outcome must beat the *strongest* simple baseline over matched repeated trials in new scenarios; no decrease in false-premise abstention, canon integrity, world truth or UPPB firewall; production kept off until explicit separate migration. If improvements appear only on arXiv's reference-role benchmarks or automatic LLM judges but not actual Pretorius consequence tests, label method transfer failure.

## Immediate recommendation

Do **not** build another large neural network, increase SelfBindingModulator salience cap or tune PSL context strength on Stage 01A's known 28 choices. Adopt the **open-source PHASE-Tree textual structure as the experimental baseline**; use its executable ablation and LongEvoRoleBench as the reproducibility gate. Measure the user's local-model constraints separately from the published GPU setup. Then evaluate PersonaForge's selective conflict processing as a **distinct** second intervention. Maintain PSL as a measurable expectation/error ledger, not decision authority. Design the decisive test around independent episodes and witnessed outcomes, drawing from MemoryArena's methodology.

No paper reviewed here demonstrates an unrefuted, model-independent personal identity substrate or human-like consciousness. Independent validated superiority for *Pretorius* remains an unachieved experimental target.
