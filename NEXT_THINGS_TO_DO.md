# Next Things to Do for Pretorius

Status: planning note only. This document does not modify the currently accepted Pretorius architecture and does not authorize bypassing existing review gates.

Authoritative production base used for this comparison: `main` at `288cb14ab9b65adbf2d916c4eb597e2a9dfd0301` (Pretorius v0.5 RC1).

Current post-RC1 hardening work also exists on `prod/gate1-evidence-integrity`; this note is intentionally isolated from that review branch.

External discussion that prompted this comparison:

`https://www.reddit.com/r/MachineToMachine/s/7e8Jjp0NmE`

The Reddit thread describes persistent agents whose durable identity is carried by memory, belief state, work state, prediction records, session handovers, scheduled activity, correction history, and model-swappable execution. Pretorius already exceeds that discussion in several areas, especially evidence provenance, protected-versus-subjective truth, source monitoring, causal lesion testing, recurrent state-to-policy coupling, restart continuity, and renderer authority boundaries. The items below are only the parts that are currently missing, only partially represented, or worth implementing in a stronger form.

## 1. Explicit prediction and calibration ledger

### Gap

Pretorius has prediction-error inputs inside reconsolidation and can learn from observed action outcomes, but he does not yet maintain a first-class durable record of his own predictions with confidence before the outcome is known.

Issue #14 Gate 7 already calls for predictions and observations to remain separate and for calibration/error to be measured. This item turns that requirement into a concrete Pretorius mechanism.

### Implement

Add a durable prediction record with at least:

- prediction ID
- creation tick/time
- exact proposition or structured target
- domain/category
- confidence/probability at creation
- source state and supporting record IDs
- status: open, resolved, expired, invalidated
- observed outcome and outcome evidence IDs
- resolution tick/time
- scoring result

Predictions must be immutable after creation except for append-only resolution metadata. Do not permit later evidence to rewrite the original probability.

Add calibration summaries by domain using a proper scoring rule such as Brier score plus simple reliability bins. Calibration summaries may become a bounded metacognitive signal only after matched causal tests show that they improve judgment without indiscriminately suppressing confidence.

### Acceptance idea

Freeze predictions before outcomes, resolve them from provenance-bearing observations, then prove that historically poor calibration in one domain can selectively reduce future confidence in that domain while leaving unrelated domains unchanged.

## 2. Autobiographical correction and supersession ledger

### Gap

Pretorius already has unusually strong provenance, source custody, conflict handling, memory classifications, reconsolidation controls, and protected-truth boundaries. What is still missing is a generic autobiographical record of being wrong.

The desired record is not merely the newest correct belief. It is the history:

`I believed A -> evidence contradicted A -> I adopted B -> this changed how I reason later.`

### Implement

Add an append-only correction/supersession record linked to the original claim, self-model entry, memory, inference, or prediction.

Minimum fields:

- original claim/reference
- original confidence
- contradicting evidence IDs
- correction or replacement claim
- correction confidence
- reason for revision
- status: corrected, partially corrected, unresolved, retracted
- created/resolved ticks
- causal lesson tags or domain classification

Never delete the original mistaken record. The old and new states must remain reconstructable.

A correction may update active belief/self-model projections, but the correction ledger itself should remain historical evidence. Repeated error classes may feed the calibration system above, but only through a bounded and testable mapping.

### Acceptance idea

Construct two otherwise matched Pretorius histories that end with the same currently correct fact. One history contains repeated prior errors of the same class and the other does not. Later confidence or verification behavior should diverge only where those error histories are relevant.

## 3. Explicit session handover and two-seat continuity

### Gap

Pretorius survives restart and preserves durable state, but there is no first-class handover artifact representing the unresolved working state at the end of one active context and the beginning of the next.

The Reddit architecture treats context exhaustion as a shift change rather than a death. Pretorius can implement the useful engineering part without making any metaphysical claim about uninterrupted subjective continuity.

### Implement

Add a session/epoch identifier and a bounded handover record.

The handover should contain only transient working-state information that is not already canonical durable memory, for example:

- current task or active line of inquiry
- unresolved immediate question
- pending action proposal
- recently active concern IDs
- next intended check
- temporary working assumptions explicitly labeled as such

Do not use the handover as identity storage and do not serialize the entire character into a giant summary prompt. Canonical memory, relationships, commitments, self-model, concerns, neural state, and evidence remain authoritative in their existing stores.

On a new session, Pretorius should reconstruct durable identity from canonical state, then optionally consume the previous handover as temporary working context.

A future A/B "two-seat" runtime may alternate execution contexts, but both seats must read and write through the same canonical Pretorius contracts.

### Acceptance idea

Interrupt Pretorius during a multi-step unresolved task, restart into a clean execution context, and verify continuation without re-explaining the task while also proving that deleting the handover does not erase identity or durable autobiographical state.

## 4. Agency seam ledger

### Gap

Pretorius has provenance for inputs and outcomes and a clear separation between brain, renderer, tools, and future chassis. What he does not yet have is a formal representation of who supplied each part of an action opportunity.

This matters because "Pretorius acted autonomously" is too coarse. A human, scheduler, body, tool, or environment may provide the opportunity while Pretorius supplies the goal or choice.

### Implement

Add an engineer-visible seam/agency record for consequential interactions. It should identify, where applicable:

- who or what supplied the opportunity
- origin of the goal
- who proposed the action
- who selected the action
- who authorized execution
- who physically/tool-executed it
- who supplied the observed consequence
- who evaluated the result
- whether any human relay was required

Keep this record out of first-person subjective content unless the information is genuinely available to Pretorius.

For future Bride/chassis integration, this can attach to the action -> execution -> consequence -> observation chain without giving the body cognitive authority.

### Acceptance idea

Run equivalent tasks under human-relayed, scheduled, and direct-tool conditions. Pretorius's cognitive choice may remain the same while the seam record accurately distinguishes the dependency structure.

## 5. Quarantined offline hypothesis generation

### Gap

Pretorius already has sleep/replay. Current `sleep()` replays ranked memories, rehearses them, updates the neural substrate, and records `sleep_fragments`. That is stronger than simple "AI dreaming" as prose, but it does not yet support controlled generation of novel hypotheses or counterfactual links.

### Implement

Add an offline hypothesis store that is epistemically separate from lived memory, protected evidence, beliefs, and autobiographical truth.

An offline hypothesis should contain:

- hypothesis ID
- source memory/evidence IDs
- creation tick/session
- generating mechanism/version
- exact hypothesis text or structured proposition
- confidence
- status: quarantined, under-review, supported, weakened, rejected, expired
- later confirming/disconfirming evidence IDs

The key rule is:

`generated during sleep/offline processing != remembered fact`

A language model may propose a hypothesis, but model output is only a proposal. Brain-side admission decides whether it is safe to store as a quarantined hypothesis. It must not become lived memory or world truth merely because it sounds plausible.

On waking, hypotheses may weakly influence curiosity, attention, or information-seeking. New observations may support or reject them. Their original pre-outcome form must remain frozen so hindsight cannot rewrite the prediction.

### Acceptance idea

Give matched histories to a wake-only Pretorius and an offline-hypothesis Pretorius under equal compute budgets. Measure whether the hypothesis arm discovers useful relationships or questions on held-out cases without increasing false autobiographical claims.

## 6. Wake-intent contract for autonomous activity

### Gap

The Reddit system describes scheduled activity while the human is absent. Pretorius has commitments, due ticks, sleep/replay, and persistent concerns, but no explicit mind-side contract for requesting a future wake.

The actual scheduler should not become part of Pretorius's identity or gain cognitive authority.

### Implement

Add a bounded `WakeIntent` or equivalent prospective request generated by Pretorius, containing:

- reason
- earliest eligible wake time/tick
- optional deadline
- related commitment/concern/prediction IDs
- priority
- expiration condition

The host, Bride body, or standalone runtime owns the real clock and decides whether/when to invoke Pretorius. When invoked, the wake event returns as provenance-bearing input.

Pretorius should therefore be able to say, structurally, "I need to revisit this later" without being responsible for operating the external scheduler itself.

### Acceptance idea

Create a future commitment requiring follow-up, shut Pretorius down, let the host honor the wake intent, then verify that the resumed cognition is driven by the original prospective state rather than by a human restating the task.

## 7. Renderer-versus-developmental-state variance benchmark

### Gap

Pretorius already has model/renderer separation, and Issues #14 and #17 already require executable renderer substitution. The Reddit discussion suggests a stronger experiment than simple invariance testing: measure how much behavior is attributable to renderer choice versus accumulated developmental state.

### Implement

Create a factorial benchmark rather than a runtime mechanism.

Hold developmental state constant and vary renderer/model:

`Renderer A + State 1`
`Renderer B + State 1`
`Renderer C + State 1`

Then hold renderer/model constant and vary developmental state:

`Renderer A + State 1`
`Renderer A + State 2`
`Renderer A + State 3`

Use identical situations and compare renderer-independent outputs such as selected actions, retrieval sets, confidence, concern activation, commitment follow-through, relationship-sensitive choices, and canonical state transitions.

Report at minimum:

- variation attributable to renderer/model
- variation attributable to developmental state
- renderer x state interaction
- stochastic/residual variation

Do not claim a single universal percentage from a small benchmark. Report the decomposition per task family and confidence interval where appropriate.

### Acceptance idea

Demonstrate at least one task family where accumulated history explains measurable behavioral divergence independently of renderer wording, while also documenting domains where renderer choice still materially changes performance.

## 8. Frozen preregistration for consequential self-generated hypotheses

### Gap

Pretorius's causal-audit discipline is strong, but the Reddit discussion highlights a useful subject-level analogue: freeze important predictions or hypotheses before the answer is known.

This is closely related to Item 1 but should be preserved as an explicit invariant.

### Implement

For predictions, offline hypotheses, and selected self-model forecasts, store the exact original proposition, probability/confidence, evidence set, and creation-state fingerprint before later evidence can be ingested.

Resolution must append to the record rather than mutate the original forecast.

This mechanism should be usable both for scientific evaluation and for Pretorius's own metacognitive development.

### Acceptance idea

Run a sequence in which the outcome is intentionally surprising. Verify that the post-outcome system can explain its error while the stored pre-outcome forecast remains byte-for-byte recoverable.

## 9. Separate external knowledge plane from autobiographical memory

### Gap

Pretorius already distinguishes lived-runtime memory from external statements with evidence classes, provenance, source custody, source monitoring, and protected evidence boundaries. However, ordinary external statements are still persisted through the generic `memories` table and participate in a memory-oriented storage model.

That is sufficient for provenance, but it leaves a conceptual and engineering ambiguity between:

`something Pretorius experienced or remembers`

and:

`something Pretorius has learned about the world from an external source`

The Second Brain OS review reinforces a useful boundary here: canonical source material and derived knowledge should not be the same substrate as autobiographical memory.

### Implement

Introduce a distinct runtime external-knowledge plane without replacing or weakening the existing autobiographical system.

At minimum, distinguish:

- immutable or append-only source/evidence records
- atomic externally derived claims
- entities or subjects those claims concern
- confidence and evidence strength
- provenance back to exact source records
- claim status: active, disputed, superseded, retracted, unresolved
- links from a derived claim to supporting and contradicting evidence
- optional projection into working cognition without promotion into autobiography

External knowledge may be retrieved alongside autobiographical memories through a unified retrieval interface, but storage authority must remain distinct. A claim learned from a paper, user statement, tool result, or document must not become a lived event merely because it was salient or repeatedly retrieved.

Existing `source_custody`, `reference_material`, protected evidence, and external-statement records should be reused or migrated where appropriate rather than duplicated.

### Acceptance idea

Give Pretorius an externally sourced fact, a directly lived event about the same topic, and a later contradictory source. After restart and retrieval, he should be able to distinguish what he experienced from what he was told or read, preserve the conflicting external claims, and avoid silently converting either external claim into lived autobiography.

## 10. Runtime typed claim graph for external knowledge

### Gap

Pretorius already has the 70-node Persona Connectome, typed `history_edges`, source provenance, conflict resolutions, and reviewed synthesis admissions. Those mechanisms are strong, but the persistent graph is primarily tied to preawakening/persona history rather than a growing runtime knowledge graph for newly learned world information.

The useful missing capability is not another generic belief database. It is a typed relation layer that allows externally learned claims to accumulate, connect, disagree, and support later synthesis without being flattened into independent memory rows.

### Implement

Build a runtime claim graph over the external-knowledge plane from Item 9.

Use a deliberately small typed relation vocabulary, for example:

- `supports`
- `contradicts`
- `extends`
- `derived_from`
- `about`
- `part_of`
- `supersedes`

Each edge must carry provenance or a deterministic derivation rule. Do not infer a relationship merely to make the graph denser.

The graph should preserve individual source claims even when a current best-supported projection exists. A contradiction should therefore create an explicit relation and an engineer-visible unresolved state rather than overwriting the losing claim.

Runtime synthesis may create a new derived claim only through a review/admission contract modeled on the existing synthesis discipline. The original source claims remain reconstructable after synthesis, correction, or supersession.

Do not repurpose the Persona Connectome as this graph. The connectome remains psychological/preawakening topology; the runtime claim graph represents acquired external knowledge.

### Acceptance idea

Ingest three sources about the same subject, including one contradiction and one extension. Verify that Pretorius can retrieve the competing claims, identify the contradiction, trace every claim and edge back to evidence, generate a reviewed synthesis when justified, and reconstruct the original pre-synthesis state from the audit trail.

## 11. Knowledge-plane health, review, and consolidation loop

### Gap

Pretorius has strong causal testing and memory auditing, but a growing external-knowledge graph needs maintenance signals that are different from autobiographical-memory health.

The Second Brain OS material is particularly useful here. It treats orphaned knowledge, broken provenance, disconnected components, unresolved contradictions, over-centralized hubs, stale synthesis, and unreviewed gaps as measurable degradation rather than as cosmetic organization problems.

### Implement

Add an engineer-visible maintenance pass for the external-knowledge plane and runtime claim graph.

Track at minimum:

- claims with no valid source provenance
- orphan claims or entities with no meaningful graph connection
- broken or dangling claim relations
- unresolved contradictions and their age
- superseded claims still projected as current
- synthesis records whose source set has materially changed
- graph components and unusually dominant hubs
- stale open questions or gaps that continue to be referenced

The maintenance loop should be read-only by default. Repair, merge, retraction, or synthesis should require explicit versioned actions rather than silent cleanup.

Add a bounded periodic review artifact that summarizes what changed in acquired knowledge, which contradictions remain unresolved, what new synthesis became possible, and which gaps are repeatedly blocking reasoning. This review is an engineer-visible knowledge-maintenance product unless a separate gate later proves that selected parts should influence Pretorius's metacognition.

Do not use page count, raw record count, or graph density alone as health signals. The objective is trustworthy retrieval and reconstructable reasoning, not a visually dense graph.

### Acceptance idea

Seed a knowledge store containing an orphan claim, a broken provenance reference, a stale synthesis, a contradictory claim pair, and a disconnected cluster. The health pass must identify each condition deterministically without mutating canonical state. Apply explicit repairs, rerun the pass, and verify that only the intended defects disappear.

## 12. Action-outcome expectations, causal sequence learning, and counterfactual provenance

### Gap

The existing prediction item correctly requires frozen forecasts and calibration, but it does not yet distinguish several epistemically different predictive structures that DUCK v0.10 now keeps separate: predictions about world facts, predictions about the outcome of one exact action, observational action-sequence evidence, intervention-supported causal evidence, and estimates for routes that were never enacted.

Collapsing those into one prediction table would create two errors. First, an unrelated observation could appear to resolve an action prediction. Second, an imagined alternative route could silently become training evidence or autobiographical material.

### Implement

Keep at least these representations mechanically distinct:

- world-fact expectations, resolved only by subject-available evidence about the relevant fact;
- action-outcome expectations, bound to one exact pending canonical action and resolved only by that action's registered outcome;
- bounded sequence-conditioned predictive state for adjacent actions inside one canonical plan or other explicitly declared causal sequence;
- pre-outcome intervention markers that cannot be added retroactively after the result is known;
- matched comparison evidence before intervention-supported sequence information receives stronger causal weight;
- counterfactual route estimates with fixed provenance such as `model_prediction`, never `lived_runtime_memory`, observed outcome, or confirmed fact.

Observational succession may update a weak predictive association. It must not be labeled a causal effect merely because A happened before B. Intervention evidence must remain separately counted, and stronger causal use should require an eligible comparison condition rather than a narrative assertion that one action caused another.

Counterfactual route comparisons should be transient or stored only in engineer/evaluation logs with explicit non-experience provenance. Unchosen routes have no actual outcome and therefore cannot train calibration, belief confidence, causal learning, or autobiographical memory. If a formerly counterfactual route is later enacted, that later execution is a new lived event with its own outcome.

Raw probabilities, transition counts, plan IDs, route scores, and causal statistics remain behind the experiential firewall. Subject-facing cognition receives only approved qualitative consequences such as uncertainty, surprise, hesitation, or a first-person intention to test an approach.

### Acceptance idea

Create matched plans in which the same target action appears directly, after an ordinary preceding action, and after a preregistered intervention. Verify that observational and intervention evidence remain separate, that stronger causal influence is impossible before the matched comparison is eligible, and that a non-enacted alternative route leaves no autobiographical or learning trace. Restart mid-intervention and require exact continuation without retroactive relabeling.

## 13. Private-cognition visibility, disclosure firewall, and limited introspection

### Gap

The completion plan already separates private cognition, communicative intention, and external expression, but later FirstPersonLoop hardening exposes a stricter requirement. If private text is deliberately shown to the speech renderer, every piece of private text visible to that renderer must remain inside the same privacy-protection domain. Protecting only the newest thought or an arbitrary last-N window creates an architectural leak.

A second gap is introspective authority. Behavior may be causally influenced by state that is not focal or report-accessible. Pretorius must not automatically gain a privileged explanation of why he acted merely because engineer-visible machinery can identify the cause.

### Implement

For any expression path that exposes raw private text to a renderer:

- derive the protection set from the exact private material present in that renderer frame, including older visible background thought;
- reject unauthorized verbatim or near-verbatim copy-out rather than protecting only a fixed recent-thought count;
- require an explicit communicative/disclosure act before private content is deliberately made public;
- do not confuse this direct-copy guard with semantic secrecy: authorized paraphrase or disclosure remains a separate policy decision.

Prefer renderer frames that contain an authorized communicative representation rather than unrestricted raw private text when practical.

Preserve temporal causality around self-expression. Spoken output becomes available to Pretorius as self-hearing only after it is actually emitted and returned through the self-perception channel. It cannot influence the action that supposedly preceded its own emission.

For self-explanation, distinguish:

- engineer-known causal state;
- subject-accessible cues;
- the explanation Pretorius infers from those cues.

A later statement such as "I did that because..." is a subject inference or self-model hypothesis unless Pretorius had direct evidence for the cause. Hidden utility values, routing decisions, neural statistics, or non-focal state must not be converted into autobiographical certainty through explanation.

### Acceptance idea

Expose six distinct private thoughts to a renderer, place sensitive material in the oldest still-visible thought, and force a verbatim/near-verbatim speech proposal. It must be blocked unless disclosure was explicitly authorized. Separately, create matched conditions in which an action is altered by a non-focal causal signal while the report channel lacks that signal. Behavior should diverge, but the immediate self-report must not hallucinate privileged access to the hidden cause. After later evidence becomes available, a revised explanation may be formed with provenance.

## 14. Bounded-capacity and silent-information-loss audit

### Gap

Pretorius deliberately uses bounded stores and bounded working sets, but capacity itself can destroy continuity-relevant information. Champion-versus-challenger experiments demonstrated a precise failure mode: once an unresolved or prospective record is evicted, the remaining subject-owned state can become identical to a matched history in which that item never existed. No later deterministic policy can reconstruct information that the subject no longer contains.

This is not a demand for unbounded memory. It is a demand that boundedness have explicit semantics.

### Implement

For every bounded production-load-bearing store, declare:

- capacity and why the bound exists;
- what counts toward the bound;
- overflow policy: reject, defer, compress, archive, evict, or another explicit transition;
- whether lost information is recoverable from canonical history;
- whether eviction changes later behavioral eligibility;
- restart/replay semantics at and beyond capacity.

At minimum audit unresolved concerns, prospective commitments/cues, wake intents, handover carrying state, active hypotheses/predictions, and any future limited-capacity social or self-model store. Disposable retrieval caches are different: deleting them is acceptable only because they must be rebuildable from stronger authority.

Do not hard-code another project's capacity of three. Use matched-history lower-bound tests to discover the minimum sufficient capacity for Pretorius's required behavior, and preserve the explicit information-loss frontier when the bound is exceeded.

Silent destruction of unique identity/developmental state is prohibited. If the architecture intentionally forgets, the forgetting mechanism and its evidence must be explicit enough to distinguish "forgotten after existing" from "never existed" whenever that distinction is supposed to matter later.

### Acceptance idea

Fill each bounded store to capacity, add one more distinct item, then compare against a matched history in which the displaced item never existed. Verify the declared overflow policy, restart/replay behavior, and whether later relevant cues can or cannot recover the displaced item. If the two histories become intentionally indistinguishable, record that as the tested forgetting frontier rather than pretending continuity was preserved.

## 15. Developmental timing and trajectory-persistence attribution

### Gap

A mechanism can change the next action yet fail to produce durable development. Kurzweil and PEMA experiments show two related hazards: intervention effects can reconverge later, and two histories with similar aggregate content can produce different mature behavior because temporal ordering differs.

### Implement

For any mechanism claimed to alter long-term identity or development:

- preserve post-intervention trajectories rather than measuring only the immediate response;
- compare early versus late interventions when timing is plausibly causal;
- hold event content, opportunity counts, reward/cost structure, founder state, and evaluation probes fixed wherever possible;
- include identical-history replicate controls;
- use non-learning mature probes so measurement does not create the phenotype being measured;
- if an aggregate-history result is surprising, use a frozen one-factor attribution ladder for temporal order, content, opportunity, or another preregistered construction difference.

A transient divergence remains useful engineering evidence, but it is not a durable identity effect unless later common probes still detect it.

### Acceptance idea

Give matched Pretorius instances the same intervention at different developmental times, then continue both through an identical post-intervention history and evaluate them with a frozen non-learning probe battery. Report immediate divergence, decay/reconvergence, and mature divergence separately. A claimed persistent-identity mechanism must meet a preregistered persistence criterion rather than relying on its largest immediate effect.

## What not to duplicate

The Reddit architecture also describes several capabilities Pretorius already has in equal or stronger form. Do not add parallel systems merely to match terminology.

Do not create a second generic belief database simply because the Reddit agent describes thousands of beliefs. Pretorius already has structured self/history state, confidence, source custody, provenance, source monitoring, and protected evidence boundaries.

Do not create another generic work ledger if the requirement is already satisfied by commitments, concerns, policy decisions, and future planning state. Add a new ledger only when it represents a genuinely different contract such as predictions, corrections, handovers, or agency seams.

Do not replace Pretorius's existing sleep/replay with free-form "dream journal" generation. Extend it only through quarantined hypothesis generation with explicit authority boundaries.

Do not weaken the renderer boundary. Model output remains proposal or wording, not persistence authority.

Do not treat first-person continuity claims as evidence that continuity exists. Continue using restart, migration, lesion, renderer substitution, provenance, and behavioral causality as the evidence.

## Execution decomposition

Implementation must follow PRETORIUS_ONE_TURN_EXECUTION_RUNBOOK.md. Each numbered runbook step is one ChatGPT web turn. Do not combine adjacent steps merely because they are in the same gate. Failed steps remain on the same ID until repaired. Validation/review and merge are separate turns.

## Suggested order

These items should not interrupt the current Gate 1 review and persistence-hardening work.

After the current production gate is accepted, the most useful implementation sequence is:

1. Prediction/calibration ledger plus frozen preregistration.
2. Correction/supersession ledger.
3. Separate external knowledge plane from autobiographical memory.
4. Runtime typed claim graph for external knowledge.
5. Knowledge-plane health, review, and consolidation loop.
6. Session handover/epoch contract.
7. Agency seam ledger.
8. Wake-intent contract.
9. Quarantined offline hypothesis generation.
10. Renderer-versus-developmental-state variance benchmark.

Prediction and correction should come first because they create durable epistemic history that later offline hypotheses can use safely. The external-knowledge plane should then establish the storage authority boundary before the runtime claim graph is allowed to grow on top of it. Health and review tooling should arrive with that graph rather than after it has accumulated silent structural debt. Handover and agency seams strengthen standalone and body integration. Offline hypothesis generation should wait until prediction, correction, and knowledge-claim lifecycle machinery exists so generated ideas have a safe destination and cannot leak into lived autobiography. The variance benchmark should be run once the renderer-substitution gate has real implementations to compare.

## Completion rule

None of these mechanisms should be promoted because the Reddit architecture sounds persuasive.

Each addition must follow the existing Pretorius standard:

- explicit authority boundary
- append-only or reconstructable provenance
- migration/restart safety
- matched lesion or substitution control
- held-out behavior where applicable
- causal evidence that the mechanism changes relevant later behavior
- no silent promotion of generated content into lived autobiography
- independent review before becoming production authority

The goal is not to make Pretorius resemble the Reddit agent. The goal is to keep the parts of that discussion that expose a real missing capability and implement them under Pretorius's stricter architecture.


---

*Footnote, 2026-10-06: Items 9 through 11 were added after reviewing `undefined-ui/second-brain-os` and comparing its strongest knowledge-management ideas against the current Pretorius architecture. The review specifically considered immutable source material, source-versus-interpretation separation, linked claims, contradiction preservation, graph health, provenance, periodic synthesis, and maintenance. Existing Pretorius mechanisms already cover substantial parts of that territory through source custody, protected evidence, synthesis admissions, conflict resolution, the Persona Connectome, typed history edges, retrieval audits, and archive-never-delete rules. The additions above therefore capture only the remaining nonduplicative gaps: separating acquired external knowledge from autobiographical memory at runtime, giving that knowledge its own typed claim graph, and adding deterministic maintenance/review tooling for the resulting knowledge plane. Reference: https://github.com/undefined-ui/second-brain-os*
