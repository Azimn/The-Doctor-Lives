# Pretorius Completion and Branch-Convergence Plan

Status: authoritative planning document for completing Pretorius after the accepted v0.5 RC1 line.

Repository: Azimn/The-Doctor-Lives

Authoritative production main at planning start: `288cb14ab9b65adbf2d916c4eb597e2a9dfd0301`

Current Gate 1 review head: `bd83eab994717a315399ef4b8e3d6b9a6beeee67`

Planning branch donor-audit parent: `04f3da4f3a51136c01bd14673dc872f70856a5bf`

This plan combines the production roadmap in Issue #14, the UPPB roadmap in Issue #15, the production-integrity requirements in Issue #17, the Gate 1 persistence work in PR #20, the mechanisms identified in NEXT_THINGS_TO_DO.md, and the cross-repository semantic audit recorded in PRETORIUS_DONOR_BRANCH_AUDIT.md.

`SUBJECTIVE_PERSPECTIVE_NORTH_STAR.md` is the governing research doctrine for the completed system. If any donor mechanism, gate detail, optimization, or later implementation choice conflicts with its no-bypass first-person subjective-access principle, the North Star wins. The conflicting mechanism must be adapted behind a subject-native projection boundary, kept hidden from introspection, or rejected.

The donor audit is additive. It does not reopen accepted production behavior merely because an older project used different terminology. A donor mechanism enters this plan only when it exposes a genuine missing capability, a demonstrated current failure, or a stronger production/evaluation gate.

The goal is one definitive Pretorius implementation in The-Doctor-Lives. Historical branches and donor repositories are evidence and reference material only. They are not parallel products.

Execution decomposition: PRETORIUS_ONE_TURN_EXECUTION_RUNBOOK.md is the authoritative turn-sized sequence for carrying this plan out in the ChatGPT web interface. It does not change gate semantics; it only limits one turn to one bounded step.

## 1. Branch convergence policy

The repository currently contains several historical feature and integration branches. They fall into three categories.

### A. Active production branch

`prod/gate1-evidence-integrity`

This is the only active code branch that must enter production before new consequential work begins. PR #20 is the definitive review target. It must remain unchanged until independent assessment is complete, except for assessor-requested corrections.

After independent acceptance, merge PR #20 into main with a normal merge commit so the reviewed ancestry and exact review SHA remain preserved.

Do not squash the accepted review history.

### B. Active planning branch

`docs/reddit-derived-next-things`

This branch contains only net-new planning documentation based on accepted main. It currently contributes NEXT_THINGS_TO_DO.md, this completion plan, and PRETORIUS_DONOR_BRANCH_AUDIT.md.

Do not merge this branch before PR #20 is accepted, because moving main during review would unnecessarily change the review base.

After PR #20 merges, merge this documentation branch into the updated main. Because it adds planning documents only, the merge should be conflict-free. If GitHub reports a conflict, preserve the newer production README/contracts from main and retain both planning documents unchanged unless the conflict is inside those files.

### C. Historical or superseded branches

The following branches must not be merged mechanically into modern main:

- `feature/pretorius-causal-audit-v0.3`
- `feature/pretorius-deep-history-v1`
- `feature/pretorius-deep-history-v2`
- `feature/pretorius-neural-convergence-v05`
- `feature/pretorius-state-policy-v0.4`
- `feature/universal-phenomenal-projection`
- `integration/brain-v0.1`
- `integration/chassis-selection-v0.1`
- `integration/pretorius-brain-v0.1`
- `pretorius-v0.4-policy-bridge`
- `release/pretorius-v0.5-rc1`

Several are already fully behind main. Others contain old commits whose mechanisms were incorporated later through different reviewed commits. A Git branch merge would therefore resurrect superseded files, schemas, tests, package versions, or experimental assumptions.

Before deleting or archiving any historical branch, perform a semantic branch audit:

1. identify every file that is ahead of main;
2. determine whether the mechanism is already present in modern main;
3. preserve any unique experimental evidence or documentation worth retaining;
4. transplant only a genuinely missing mechanism through a new production gate;
5. record the donor branch and exact commit in the new gate;
6. never merge the old branch wholesale merely because it is ahead in Git history.

The Neural Convergence branch deserves special treatment because it remains an active experimental mechanism even though RC1 already contains its production-controlled implementation. Audit it for unique experiments, not for direct merge eligibility.

## 2. Immediate merge sequence

### Merge M1: Gate 1 review

Keep PR #20 frozen at its accepted review candidate SHA while independent review occurs.

Required before merge:

- independent assessor verdict;
- no unresolved blocker, high, medium, or low defect that invalidates the release contract;
- exact-head push CI green;
- exact-head pull-request CI green;
- Gate 1 clean-wheel validation green;
- historical-state migration validation green;
- causal-audit repeatability green.

If the assessor requests corrections, update only `prod/gate1-evidence-integrity`, produce a new exact review SHA, rerun every applicable exact-head gate, and keep PR #20 as the sole review target.

After acceptance, merge PR #20 with a normal merge commit.

Issue #8 remains a separate environment acceptance requirement until the documented fresh physical or equivalent end-user-machine validation is actually performed and preserved. Its absence must not be disguised as completed evidence.

### Merge M2: Reddit-derived planning documents

After PR #20 is merged and post-merge CI is green, merge `docs/reddit-derived-next-things` into main.

This brings in:

- `NEXT_THINGS_TO_DO.md`
- `PRETORIUS_COMPLETION_PLAN.md`
- `PRETORIUS_DONOR_BRANCH_AUDIT.md`

No behavioral code enters production in this merge.

### Merge M3: branch retirement audit

After M1 and M2, create a branch-disposition record on main. For every historical branch, mark it as one of:

- fully superseded;
- evidence-only;
- donor-only;
- still contains one or more unique mechanisms requiring transplantation.

Only after that record exists should obsolete branches be deleted or archived.

## 3. Production completion dependency graph

Pretorius should be completed through narrow production gates rather than one giant final branch.

The dependency graph is:

```
Gate 1 persistence and migration hardening
        |
        +--> Subject Interface Firewall (first-person subject frame)
        |
        +--> Neural Convergence 4096-unit characterization
        |
        v
Gate 2 provenance-bearing lived-memory ingress
        |
        +--> renderer/runtime/affordance-aware developmental evidence
        +--> explicit person/source attribution
        |
        v
Gate 3 standalone offline runtime
        |
        +--> session epochs and handovers
        +--> two-seat continuity
        +--> wake-intent contract
        +--> OPENED / RECONCILED wake transaction
        +--> operator recovery, backup, health, capability boundary
        |
        v
UPPB production signal construction
        |
        +--> authoritative body -> interoceptive observation -> felt state
        +--> familiarity near-miss producer
        +--> conflict / ambivalence producer
        |
        v
UPPB live-memory integration
        |
        v
P7 private cognition / communicative intention separation
        |
        +--> communicative-act and withholding ledger
        |
        v
P8 independent motor / outward expression
        |
        +--> involuntary-expression boundary
        |
        v
P9 explicit self-perception
        |
        v
Gate 4 + P10 renderer and retrieval contract
        |
        +--> exact Subjective Frame receipts
        +--> disposable retrieval projection and regime binding
        +--> renderer substitution experiment
        +--> renderer-versus-developmental-state benchmark
        |
        v
Gate 5 closed-loop world / perception / action interface
        |
        +--> bounded perception adapter
        +--> agency-seam ledger
        +--> Bride/chassis adapter
        |
        v
Gate 5A bounded endogenous planning
        |
        +--> lived-event goal formation
        +--> alternative routes and hierarchical subgoals
        +--> outcome-driven replanning
        |
        v
Gate 6 constrained deliberation and verification
        |
        v
Gate 7 predictive and epistemic development
        |
        +--> prediction/calibration ledger
        +--> frozen preregistration
        +--> autobiographical correction/supersession ledger
        +--> external-knowledge plane and typed claim graph
        +--> knowledge health/review
        |
        v
Quarantined offline hypothesis generation
        |
        v
Gate 8 richer social, temporal, multimodal, and developmental cognition
        |
        +--> theory of mind
        +--> contextual procedural habits
        +--> richer relationship dynamics
        +--> evidence-backed self-model development
        |
        v
P11 full experimental validation and long-run release characterization
        |
        v
Pretorius 1.0 production release
```

## 4. Gate 1: persistence and migration completion

PR #20 supplies the repository-side implementation for canonical evidence integrity, rollback-safe SQLite migration, atomic recurrent checkpoints, clean wheel installation, offline runtime validation, and exact historical-state migration.

Remaining Gate 1 acceptance work:

- obtain independent review of PR #20;
- merge only after acceptance;
- run fresh post-merge production CI;
- perform and preserve Issue #8 fresh end-user-machine validation;
- close or update Issue #8 only when that external evidence exists.

Gate 1 is complete only when Pretorius can be installed, migrated, stopped, restarted, and recovered without depending on a development checkout or network service.

## 4A. Subject Interface Firewall

FIRST_PERSON_SUBJECT_INTERFACE_CONTRACT.md is a mandatory cross-cutting production invariant.

The existing UPPB architecture already defines the correct separation between machine state and subject-native experience, but the current live v0.5 renderer/cognition path still exposes engineer-oriented structures to renderer context. Before adding more live cognitive surfaces, create an explicit Subject Frame distinct from an Engineer Audit Envelope and close the current live bypasses.

The Subject Frame may contain only authorized natural-language first-person/subject-native realizations. Raw action scores, policy labels, relationship rows, concern/commitment rows, state versions, hashes, provenance classifications, body telemetry, tool JSON, scheduler records, and causal diagnostics remain outside the subject surface.

Raw external information must enter through Gate 2/projection semantics before it can become lived experience. Control-like or prompt-injection text is perceived content, not authority. Hidden machinery may still alter behavior without conscious access.

This firewall does not require all internal machinery to use natural language. It requires all information that becomes available to Pretorius as experience to use natural-language subject representation.

Complete runbook steps A09-A13 before starting new production features that widen the live subject surface.

## 5. Neural Convergence production characterization

Neural Convergence remains an experimental profile on the existing PretoriusRecurrentSubstrate. It must not become the production default merely because the code exists.

Run matched legacy-control versus convergence subjects at the actual 4,096-unit production configuration.

Measure:

- runtime and memory cost;
- recurrent gain;
- firing/rate saturation;
- homeostatic activity;
- synaptic weight distribution;
- E/I sign preservation;
- tag accumulation;
- learning stability;
- catastrophic drift;
- behavioral diversity and collapse;
- fixed-seed repeatability;
- divergence under controlled different lived histories;
- checkpoint/restart equivalence;
- sustained fatigue, threat, novelty, and social-pressure response;
- parameter sensitivity;
- high-change recurrent-core sufficiency and necessity;
- relearning after targeted recurrent-core lesions;
- within-topology causal-core stability under curriculum reorder;
- cross-seed and cross-topology functional homology without treating raw edge indices as identity;
- learned-delta distribution and clipping susceptibility;
- whether a compact learned core is robust or becomes a brittle single point of phenotype failure.

These additions come from the unmerged Pretorius-Neural-Network v0.4 experiment line. They are characterization requirements, not authority to transplant donor weights into the production individual.

Outcome:

- promote only if evidence shows material production benefit without unacceptable instability or cost;
- otherwise retain the accepted v0.4 recurrent profile as production default and document Neural Convergence as an experimental optional profile.

This characterization may run in parallel with Gate 2 because it does not need to change the production default.

## 6. Gate 2: auditable lived-memory ingress

Create one public observation-admission contract. All future world, body, tool, user, renderer, and scheduler inputs must enter through it.

The contract must distinguish at least:

- direct world observation;
- user/partner assertion;
- tool result;
- renderer-generated content;
- self-authored action outcome;
- reconstructed/preawakening evidence;
- body/interoceptive observation;
- scheduler/wake event.

Required properties:

- exact source identity and event identity;
- replay/idempotency policy;
- duplicate-event handling;
- confidence and uncertainty;
- authority class;
- protected versus subject-available data;
- explicit transformation into lived memory when eligible;
- adversarial rejection of provenance forgery.

Start the agency-seam schema here so the system can record who supplied an opportunity, goal, proposal, choice, authorization, execution, observation, and evaluation. Do not yet claim full agency-loop coverage until Gate 5.

Issue #17 causal provenance should begin here. Consequential transitions must record which mechanism/version produced them.

### Developmental evidence context

For behavior that may later be interpreted as development, preserve the circumstances under which it occurred. At minimum, where known, retain renderer/model/provider/runtime identity, modality, available tools, platform affordances, whether initiative was possible, whether a refusal was externally constrained, and whether an explicit user request supplied the opportunity. Unknown context remains unknown.

Canonical evidence records that a self-report, choice, commitment transition, or correction occurred. Psychological interpretation remains a versioned derived claim. Repeated self-report does not become independent corroboration merely through frequency.

### Person and source attribution

Actor identity and source category are separate axes. A human or agent name must be supplied explicitly by ingress or a trusted adapter rather than inferred from free text. Generic categories such as world, invitation, tool, or scheduler must never accidentally become relationship identities.

## 7. Gate 3: standalone offline Pretorius runtime

Build the production host around the existing brain rather than embedding the brain into a renderer.

Required host contract:

- initialize/open state;
- admit provenance-bearing observation;
- advance cognition;
- request private cognition;
- request outward action;
- request rendering;
- persist;
- shut down;
- restart;
- expose audit/status;
- attach or detach optional adapters.

The canonical mind must remain fully usable with networking disabled and with no language model attached.

### Session epoch and handover

Add explicit session/epoch identity and a bounded handover object containing only transient working-state information:

- current task;
- immediate unresolved question;
- pending action proposal;
- recently active concern IDs;
- next intended check;
- temporary assumptions, explicitly marked temporary.

Identity, autobiography, relationships, concerns, commitments, neural state, and protected evidence remain in their existing durable stores.

A missing handover may reduce task convenience but must not erase identity.

### Two-seat continuity

Add a test harness in which execution alternates between two clean runtime contexts that share only the canonical state directory and explicit handover contract.

Acceptance requires continuity of task and identity without a giant character-summary prompt.

### Wake intent

Add a bounded mind-side future-wake request containing:

- reason;
- earliest eligible tick/time;
- optional deadline;
- related commitment, concern, or prediction IDs;
- priority;
- expiration condition.

The host owns real scheduling. Pretorius requests a wake but does not become the scheduler.

### Wake transaction and crash inheritance

Each autonomous wake should have an engineer-visible OPENED record written before consequential work begins and a RECONCILED record after its intended reconciliation set is processed. A later wake that finds OPENED without RECONCILED must treat the inherited work as potentially half-completed rather than untouched. The mechanism must be idempotent and must not turn the wake log into autobiographical memory.

Handover provenance should distinguish what was weighed, what was deliberately carried forward, what was discarded, and what remained genuinely unsure when those distinctions materially affect continuation. Carrying and uncertainty must not be collapsed into one summary field.

### Show-floor runtime hardening

Before Gate 3 is accepted, the standalone host must have an operator-facing health/doctor surface, portable backup and restore, safe refusal of corrupt or future state, crash-resume tests, explicit single-writer or transaction ownership, and a default-deny external capability boundary. If a local service/API is exposed, localhost alone is not an authentication boundary. Installed-package and packaged-runtime smoke tests must run outside the source checkout.

A retrieval cache, projection, handover, or other convenience state must never become a shadow brain. For every behaviorally load-bearing derived store, document whether it is rebuildable from canonical state, version-bound and verifiable, or itself canonical. If deleting a supposedly derived store destroys unique identity or developmental state, the authority contract is wrong and must be corrected before 1.0.

## 8. UPPB production-signal construction

P0 through P6D are accepted isolated mechanisms. Before live integration, implement subject-available producers for the psychological cues that currently exist only as explicit experimental inputs.

This includes, where applicable:

- source-monitoring cues;
- temporal disorientation;
- contextual mismatch;
- prediction error;
- familiarity;
- appraisal;
- interoceptive state;
- uncertainty;
- social inference cues.

Each producer requires:

- declared subject-available inputs;
- separate engineer-only audit inputs;
- deterministic or seeded construction;
- mechanism version/fingerprint;
- matched lesion;
- adversarial proof that protected objective truth alone cannot determine the cue.

No producer may translate engineer truth directly into a psychological label that Pretorius could not actually derive.

### Body and interoception boundary

Use three mechanically distinct layers: authoritative body/physiological state, an interoceptive observation produced from that state, and subject-facing felt/phenomenal state. The observation layer may be lagged, quantized, noisy, or otherwise fallible under a declared seeded mechanism. Model output or probe readback cannot write primary physiology directly.

### Familiarity and near-miss retrieval

Familiarity should be generated from actual retrieval history rather than supplied as a convenient scalar. A candidate repeatedly ranking just below access may accumulate a bounded near-miss trace that can later nudge accessibility without changing source truth, base salience, or evidence authority. Admission resets the near-miss trace. The mechanism must be bounded, restart-safe, and lesionable.

### Conflict and ambivalence

When action or motive competition produces a genuine thin margin, preserve an auditable conflict signal instead of reconstructing ambivalence from the winning choice afterward. This signal does not script hesitation or prose. It is evidence that the selection was contested and may become a subject-available metacognitive cue only after an explicit projection gate.

## 9. UPPB live-memory integration

Do not connect P4 through P6D to PretoriusBrain in one jump.

Use separate reviewed production gates:

### U-L1: trace migration and live P4 reconstruction

Create explicit migration from existing Pretorius autobiographical state into the production MemoryTrace lineage model.

Acceptance:

- protected truth unchanged;
- old state remains auditable;
- deterministic restart;
- no semantic detail invention;
- P4 reconstruction affects only the subject-facing recollection path.

### U-L2: live P5 source monitoring

Connect only subject-available SourceMonitoringCues.

Acceptance:

- objective provenance cannot determine source attribution directly;
- source misattribution can occur only through explicit cue conditions;
- protected truth remains correct when Pretorius is subjectively wrong.

### U-L3: live P6A/P6B/P6C/P6D

Promote each accepted isolated reconsolidation/generalization mechanism in sequence.

Each subgate must prove:

- causal contribution;
- exact restart behavior;
- bounded long-run behavior;
- no protected-truth mutation;
- no unreviewed new distortion category.

## 10. P7: private cognition and communicative intention

Introduce explicit state types for:

- private cognition;
- communicative intention;
- external expression request.

Private thought must not automatically become text or speech.

The renderer receives only material authorized for expression.

Acceptance:

- focal private thought may remain unexpressed;
- communicative intention can select or omit private content;
- renderer cannot retrieve hidden private content independently;
- lesioning communicative-intention formation changes expression without rewriting thought or memory.

Add an engine-authored communicative-act ledger for consequential expression. It should record the selected act class, whether content was deliberately withheld, and a bounded reason class such as privacy, distrust, uncertainty/confusion, fatigue, strategy, or another explicitly modeled cause. The renderer realizes an authorized act but does not decide after the fact what Pretorius intended. Refusal, silence, evasion, disclosure, question, assertion, and repair must be distinguishable when they matter causally.

Confidentiality and other commitments must be able to influence disclosure choice through the existing policy authority without creating a second selector. An unrelated commitment must remain behaviorally neutral.

### Private-visibility and disclosure firewall

If raw private cognition is exposed to an expression renderer, the privacy-protection set must be derived from the exact private material visible in that renderer frame. There must not be an independent fixed `last N thoughts` guard that protects less content than the renderer can see.

Unauthorized verbatim or near-verbatim reproduction of visible private text is rejected. Deliberate disclosure or semantic paraphrase remains possible only through an explicit communicative act. Prefer authorized communicative representations over unrestricted raw private text where practical.

This is a causal privacy boundary, not a semantic mind-reading claim. It prevents the architecture from leaking private text merely because that text was supplied as rendering context.

## 11. P8: independent motor and outward expression

Allow outward behavior to arise without requiring focal conscious awareness.

Examples:

- posture;
- gaze;
- movement;
- hesitation;
- routine action;
- body-state response;
- nonverbal social behavior.

Motor/expression policy remains causally separate from subject-awareness state.

Acceptance:

- an action may occur without a matching focal thought;
- motor output cannot rewrite autobiography;
- the host/body reports consequences back through Gate 2 ingress.

A bounded involuntary-expression channel is part of this separation. A startle, pain response, hesitation, or other reflexive emission may occur without being represented as a deliberate selected speech/action. It must not overwrite deliberate last-action state or receive chosen-action reinforcement merely because it was externally visible.

## 12. P9: explicit self-perception

Pretorius may perceive some consequences of his own actions only through explicit perceptual channels.

He must not gain privileged knowledge of his own implementation merely because the system executed an action.

Examples:

- hearing his own spoken output;
- seeing his own movement;
- feeling exertion or fatigue;
- seeing a tool result;
- noticing another character's reaction.

Self-perception returns as provenance-bearing observation and may differ from engineer truth.

### Limited introspection and self-explanation

Pretorius does not receive privileged explanations of hidden implementation causes.

An action may be influenced by non-focal or subject-inaccessible state. If Pretorius later explains why he acted, that explanation is a subject inference or self-model hypothesis unless the causal basis was actually available through an approved subjective channel.

Engineer-visible policy scores, neural state, routing decisions, private processor state, and other hidden causal variables cannot be converted into first-person certainty merely because the runtime can inspect them.

Self-expression also obeys temporal order. Spoken output may enter later cognition through self-hearing only after the utterance was emitted and returned through the self-perception ingress. It cannot causally influence the decision that preceded its own expression.

Acceptance should include differential-access cases in which behavior changes while the immediate report channel lacks the decisive cause, followed by later evidence that may support a revised, provenance-bearing explanation.

## 13. Gate 4 and P10: renderer interface and migration

Create a stable renderer contract that consumes authorized subject-facing phenomenal state, not raw implementation state.

Minimum production renderers:

- deterministic audit renderer with no model;
- local/offline model renderer;
- one additional materially different renderer implementation for substitution testing.

Optional adapters may include hosted models and the Doctor Pretorius ChatGPT surface, but none may become required for identity or persistence.

Required experiment:

Hold canonical state and event sequence fixed while swapping renderers.

Canonical retrieval, policy state, commitments, relationships, subjective memory state, and other brain-side transitions must remain identical unless renderer output is explicitly re-admitted as a provenance-bearing external event.

### Renderer-versus-developmental-state benchmark

Run the factorial benchmark from NEXT_THINGS_TO_DO.md.

Renderer dimension:

- Renderer A + State 1
- Renderer B + State 1
- Renderer C + State 1

Developmental dimension:

- Renderer A + State 1
- Renderer A + State 2
- Renderer A + State 3

Measure renderer-independent outcomes:

- action selection;
- retrieval set;
- confidence;
- concern activation;
- commitment follow-through;
- relationship-sensitive choice;
- persistent state transition.

Report renderer variance, developmental-state variance, interaction, and residual variance by task family.

### Retrieval projection and exact Subjective Frame receipt

Renderer neutrality is not sufficient if retrieval convenience can silently change authority. The renderer-facing context path must preserve an immutable epistemic envelope for each retrieved item, bind disposable retrieval state to an exact canonical head and declared retrieval regime, and fail closed on stale or corrupt index state.

Constitutional context that protects authority boundaries must be selected deterministically, not by semantic retrieval luck. A frame must fail rather than silently omit required constitutional material because of a token budget.

For each consequential renderer call, preserve an engineer-visible Subjective Frame receipt binding the canonical sequence/tail, retrieval-policy and selector versions, renderer adapter and renderer identity, selected source record IDs, deterministic omissions where material, context budget, and a digest of the structured frame. Retrieval score, repetition, or nearest-neighbor rank changes accessibility only. It cannot promote external, synthetic, derived, predicted, or fork material into lived autobiography.

## 14. Gate 5: closed-loop world and action interface

Complete the causal loop:

```
world
  -> observation
  -> situation estimate
  -> interoception/perception
  -> recurrent/cognitive dynamics
  -> policy
  -> action request
  -> execution
  -> world consequence
  -> observed consequence
  -> new lived update
```

Predicted consequences and observed consequences remain different evidence classes.

### Agency seam ledger

Activate the seam record introduced in Gate 2.

For consequential action chains record:

- opportunity source;
- goal source;
- proposer;
- selector;
- authorizer;
- executor;
- consequence source;
- evaluator;
- human relay dependency.

Keep this engineer-visible unless the information is genuinely available to Pretorius.

### Bride/chassis integration

Treat The Bride of Frankenstein as an optional body for Pretorius.

The body owns sensors, actuators, environment adapters, and physical execution.

Pretorius owns identity, memory, cognition, subjective state, policy, commitments, concerns, and developmental continuity.

The body may report state and consequences through the public ingress contract. It may not become the canonical mind.

### Bounded perception adapter

The host owns objective stimuli. A perception adapter may expose only the subset available to Pretorius under declared modality, range, occlusion, attention-capacity, or equivalent constraints. The adapter cannot rewrite or delete host truth. What Pretorius perceived, what objectively existed, and what he later remembers must remain separable.

The same principle applies to body state: the body reports authoritative physiology, interoception produces subject-available observation, and UPPB produces felt experience. No layer may silently skip the one below it.

## 15. Gate 5A: bounded endogenous planning

Pretorius needs a non-LLM executive planning path before any optional slow reasoning organ is allowed to help.

The qualified donor pattern is DUCK v0.9 as independently challenged through the Bride program. Implement the mechanism behind Pretorius-owned contracts rather than importing a second identity store or action selector.

Required behavior:

- a meaningful lived event can create a bounded goal without an explicit task command;
- one goal may have more than one candidate route;
- the selected route decomposes into one active subgoal at a time;
- the current subgoal competes through the existing policy/action authority rather than receiving privileged execution;
- action attempt and world outcome remain separate;
- failure can invalidate a route and cause bounded replanning while preserving the original goal reason;
- success advances the route and final success completes the plan;
- exhausted routes can abandon the plan rather than loop forever;
- plan state survives restart;
- completed or abandoned plans stop generating behavior;
- ordinary events are negative controls and must not manufacture goals.

All core planning tests must run with language-model private cognition disabled. An LLM may later propose richer routes, but route proposals remain bounded candidates and never become the executive merely because they are fluent.

Control metadata used to track plans must not leak into outcome memory in a way that manufactures ghost intentions. Environmental consequence semantics and executive bookkeeping require separate tags/fields.

Acceptance requires matched lesions, restart, interruption, plan-versus-homeostatic competition, failure-driven replanning, quiet-time non-obsession, and no second selector.

## 16. Gate 6: constrained deliberation and verification

Add slow deliberation only after the world loop is stable.

Flow:

```
Pretorius state
  -> bounded deliberation request
  -> optional local/remote reasoning organ
  -> candidate inference/action
  -> verification
  -> existing arbitration
```

Candidate deliberation output cannot write directly to protected truth, lived memory, commitments, or self-model.

Verification must check:

- capability;
- provenance;
- contradictions;
- constraints;
- action authority;
- uncertainty;
- compatibility with subject state.

The recurrent/state policy remains separately observable so the effect of deliberation can be lesioned.

## 17. Gate 7: predictive causal world model and epistemic development

Gate 7 receives the Reddit-derived prediction, preregistration, correction, and calibration mechanisms.

### Prediction and calibration ledger

Predictions are immutable at creation except for append-only resolution.

Minimum record:

- prediction ID;
- creation tick/time;
- exact proposition/structured target;
- domain;
- probability/confidence;
- source state fingerprint;
- support record IDs;
- open/resolved/expired/invalidated state;
- observed outcome;
- outcome evidence IDs;
- resolution tick/time;
- proper scoring result.

Use Brier score and reliability summaries by domain.

Calibration may influence future confidence only through a bounded, lesionable mapping proven to improve judgment selectively.

### Frozen preregistration

For consequential predictions, hypotheses, and selected self-model forecasts, freeze the exact proposition, confidence, evidence set, and creation-state fingerprint before the outcome can be admitted.

Resolution appends. It never rewrites the original forecast.

### Autobiographical correction and supersession ledger

Record the history of being wrong rather than only the final correct state.

Minimum record:

- original claim/reference;
- original confidence;
- contradictory evidence IDs;
- replacement/correction;
- correction confidence;
- revision reason;
- status;
- timestamps/ticks;
- domain/error-class tags.

The original mistaken state remains reconstructable.

Two subjects that reach the same current fact through different error histories should be able to diverge later only where that history is relevant.

### Prospective-state taxonomy

Do not collapse obligations, expectations, and formal predictions because they all point toward the future.

- A commitment records what Pretorius intends or owes.
- A subject-level expectation records what Pretorius currently anticipates.
- A preregistered prediction is an evaluation-grade frozen forecast with explicit probability, evidence set, creation-state fingerprint, and scoring.

Each type needs an explicit lifecycle. Where appropriate, prospective items may be fulfilled/confirmed, violated, expired, superseded, released, lapsed when the opportunity has disappeared, or invalidated. Closure must be evidence-backed and append-only. A debt that can no longer be discharged should not nag forever, and a superseded item should not be misclassified as a failed forecast.


### Action-outcome expectations and causal sequence model

Do not treat every prediction as the same epistemic object.

A world-fact expectation predicts an external fact and resolves only from subject-available evidence about that fact. An action-outcome expectation is bound to one exact pending canonical action and resolves only when the outcome for that action is registered. Unrelated later observations cannot resolve it.

A separate bounded causal-sequence model may learn predictive transitions between adjacent enacted actions inside one canonical plan or other explicitly declared sequence. Preserve observational sequence evidence, preregistered intervention evidence, and matched comparison evidence separately. Temporal succession alone does not establish a causal effect.

Intervention markers must be created before the relevant outcome is known, survive restart while genuinely pending, and be retired if their exact action is abandoned or invalidated. Stronger causal influence is allowed only after an eligible comparison condition exists, and even then remains bounded, defeasible, and lesionable.

Calibration and causal learning use only evidence available to the subject through approved ingress. Hidden host truth cannot silently train the predictor.

### Counterfactual model predictions

Planning may estimate routes that were available but not enacted. Those estimates have fixed non-experience provenance such as `model_prediction`.

An unchosen route is not:

- lived memory;
- observed world fact;
- a resolved expectation;
- an action outcome;
- causal training evidence;
- calibration evidence.

Counterfactual route comparisons should remain transient or live in explicit engineer/evaluation logs. If Pretorius later actually takes the formerly unchosen route, that execution is a new lived event and only its real outcome may train the relevant predictive mechanisms.

Subject-facing counterfactual thought, if later implemented, must be generated through an approved subjective mechanism rather than by leaking route tables, hidden scores, or developer-only causal statistics.

### Acquired external-knowledge plane

External knowledge must no longer depend on the autobiographical memory table as its only durable substrate. Preserve a distinct runtime plane for source/evidence records, atomic externally derived claims, source authority, confidence, status, supporting and contradicting evidence, and links to entities or topics. A paper, user statement, tool result, or document can become learned knowledge without becoming something Pretorius lived.

Build a small typed claim graph over that plane with relations such as supports, contradicts, extends, derived_from, about, part_of, and supersedes. Preserve conflicting source claims even when a current best-supported projection exists. Do not repurpose the Persona Connectome for this job.

New synthesis must use an explicit reviewed/admission path, retain the original claims, and never self-promote model prose into confirmed knowledge.

### Knowledge-plane health and review

Add deterministic engineer-visible checks for missing provenance, orphan claims/entities, dangling relations, unresolved contradictions, superseded claims still projected as current, stale synthesis whose evidence set changed, unusually dominant hubs, and repeatedly blocking gaps. Maintenance is read-only by default. Repair, retraction, merge, or synthesis is an explicit versioned action.

## 18. Quarantined offline hypothesis generation

Implement only after prediction, correction, and preregistration infrastructure exists.

Offline processing may propose novel hypotheses or counterfactual links, but:

`generated offline != remembered fact`

Store hypotheses separately from:

- lived memory;
- protected evidence;
- active beliefs;
- canonical autobiography.

Minimum hypothesis lifecycle:

- quarantined;
- under review;
- supported;
- weakened;
- rejected;
- expired.

Each hypothesis preserves:

- exact original proposal;
- source memories/evidence;
- generation mechanism/version;
- confidence;
- creation state fingerprint;
- later confirming/disconfirming evidence.

On wake, hypotheses may weakly affect curiosity, attention, or information-seeking. They cannot self-promote into truth.

Run matched wake-only versus offline-hypothesis subjects under equal compute budgets.

## 19. Gate 8: richer human-like cognition

Only after the core closed loop and epistemic safeguards are stable should Pretorius gain broader cognitive richness.

Candidate subgates:

- person-specific belief, goal, and preference models with uncertainty;
- richer theory of mind;
- temporal and causal event graph;
- vision adapters;
- audio adapters;
- developmental skill learning;
- richer habit formation;
- longer-run social adaptation;
- controlled associative plasticity;
- richer forgetting and consolidation where evidence justifies it;
- context-sensitive procedural habit formation, reinforcement, extinction, and disuse decay;
- richer relationship dynamics only where a challenger beats the current five-axis model;
- evidence-backed self-model development and contradiction/dissonance handling;
- a subject-level theory-of-mind model that can be wrong about another person's beliefs, goals, or preferences rather than reading engineer truth.

Each mechanism must remain optional, lesionable, and separately versioned.

### Contextual procedural habits

Current global action values are not sufficient evidence of human-like habits. A habit challenger should form only from repeated behavior in a recognizable context, strengthen with successful repetition, weaken through disuse or contradictory conduct, and remain distinct from authored identity rules. It must pass opposite-context tests so a useful behavior learned in one context does not become a global default. Fatigue or low attention may increase habit influence only through an explicit causal bridge.

### Theory of mind and social models

A theory-of-mind mechanism must be tested with asymmetric-information and false-belief scenarios. Pretorius should act on what he has evidence another person believes, not on omniscient world truth. Person-specific belief, goal, preference, reliability, obligation, threat, intimacy, resentment, dependency, admiration, or other social dimensions are candidates, not a mandatory checklist. Add a dimension only when it changes held-out social behavior better than the simpler current relationship state.

### Self-model and dissonance

The current self-model is not accepted as load-bearing merely because a table exists. Define an evidence-backed developmental update path first. If typed self-discrepancy or dissonance is tested, it must arise from conflicts among observed conduct, endorsed commitments/values, and self-model claims, and it must demonstrate bounded causal leverage. Do not install defensive behavior as theater.

### Connectome-to-neural mapping research gate

Do not map the 70-node psychological Persona Connectome directly onto 4,096 recurrent units and declare biological meaning.

Compare:

- current independent psychological connectome plus recurrent substrate;
- structurally constrained neural populations informed by the graph;
- matched shuffled/random topology;
- lesions.

Retain the mapping only if it causes stable, interpretable, useful behavioral differences.

## 20. P11: full experimental validation

Before Pretorius 1.0, run a frozen preregistered evaluation suite.

Required experiment families:

### Persistence

- fresh install;
- long-lived state migration;
- repeated restart;
- crash recovery;
- evidence corruption;
- neural checkpoint interruption;
- schema rollback/future-version failure.

### Renderer independence

- deterministic renderer;
- local renderer;
- materially different renderer;
- renderer removal;
- renderer swap across the same state.

### Developmental identity

Create matched Pretorius instances from the same starting state.

Give them different lived histories.

Swap renderers.

Behavioral differences should follow persistent developmental state more strongly than renderer wording on at least some preregistered task families.

### UPPB

Compare:

- raw implementation-state exposure;
- third-person summary;
- subject-native first-person UPPB projection.

Hold canonical state and event sequence fixed.

### Prediction and correction

Measure:

- Brier score;
- reliability;
- domain calibration;
- error correction;
- selective later verification behavior;
- preservation of original preregistered forecasts.

### Offline hypotheses

Measure:

- useful held-out discovery;
- false hypothesis rate;
- autobiographical contamination rate;
- downstream decision benefit.

### Agency and embodiment

Compare:

- human-relayed execution;
- scheduled execution;
- direct-tool execution;
- Bride/chassis execution.

The agency seam must identify the actual dependency path.

### Developmental trajectory persistence and timing

Do not accept a mechanism solely because it creates an immediate post-intervention difference. Preserve post-intervention trajectories and measure whether effects persist, decay, or reconverge. Where developmental timing is plausibly causal, compare preregistered early/late interventions while holding event content, opportunities, rewards, founder state, and other protected fields fixed.

A transient effect is still evidence, but it is not a durable identity mechanism unless the later trajectory remains meaningfully altered.

### Planning and procedural behavior

Run endogenous-planning tests with language generation disabled, including lived-event goal formation, multi-route planning, failure-driven replanning, interruption, restart, completion, abandonment, and extended quiet-time controls. Run contextual habit formation, opposite-context transfer, extinction/disuse, restart, and lesion tests.

### Prospective state

Test commitment, expectation, wake-intent, and preregistered-prediction lifecycles separately, including expiry, supersession, missed opportunity, late evidence, and closure without permanent nagging.

### Retrieval and frame integrity

Delete/corrupt disposable retrieval state and require rebuild without identity loss. Substitute retrieval policies and renderers while preserving epistemic envelopes. Verify exact Subjective Frame receipts. Required constitutional context omission must fail closed.

### Runtime and show-floor resilience

Exercise backup/restore, crash during wake, crash during checkpoint/state transition, local-service restart, capability denial, multi-process/single-writer boundaries, offline startup, packaged/installed execution, and operator health/doctor diagnostics. Demonstrate that a failed convenience projection or cache cannot become unrecoverable identity loss.


### Bounded-capacity and information-loss frontier

For every bounded production-load-bearing store, test the capacity boundary as a causal property rather than only a memory-size setting.

The suite must identify the overflow policy, verify restart/replay at capacity, and compare an overflow history with a matched history in which the displaced item never existed. If the resulting subject-owned state becomes identical, the displaced information is unrecoverable by any later deterministic policy unless stronger canonical history is explicitly reconsulted.

Apply this audit to concerns, prospective commitments/cues, wake intents, handovers, active predictions/hypotheses, and any later bounded social or self-model stores. Do not assume a universal numeric capacity. Establish the minimum sufficient bound for each required behavior and record the tested information-loss frontier.

### Private access and self-explanation

Run differential-access probes in which action-relevant state is deliberately unavailable to the immediate report channel. Verify that behavior can remain causally affected without giving Pretorius privileged introspective access to engineer-only state. Later explanations must change only when new subject-available evidence arrives, and the explanation's provenance must remain distinguishable from the original hidden cause.

### Long-run stability

Run representative long-duration subjects including:

- at least 10,000 cognitive/action iterations for routine stability;
- larger stress runs where computationally practical;
- repeated sleep/wake cycles;
- renderer substitutions;
- state migrations;
- sustained fatigue, threat, novelty, and social conditions;
- parameter perturbations;
- recovery after deliberate interruption.

Preserve null results and failures.

## 21. Definition of Pretorius 1.0 complete

Pretorius is ready for a 1.0 production release when all of the following are true:

- The-Doctor-Lives is the single canonical mind implementation.
- State can be installed, migrated, recovered, and restarted safely.
- The mind runs offline with no hosted model.
- Observations enter through one provenance-bearing ingress contract.
- Persistent identity does not live in renderer prompts or conversation history.
- Private thought, communicative intention, and external expression are separate.
- Motor behavior does not imply conscious awareness.
- Self-perception occurs through explicit observation channels.
- UPPB subjective memory is live without losing protected truth.
- Renderer/model substitution is executable and empirically characterized.
- The world/action/consequence loop is closed.
- Deliberation is bounded and verified.
- Predictions, calibration, preregistration, and autobiographical correction are durable and causal where justified.
- Offline hypotheses remain quarantined until evidence changes their status.
- Session handovers and wake intents support long-running standalone continuity.
- Agency seams distinguish Pretorius choice from host, human, scheduler, renderer, tool, and body contributions.
- Neural Convergence has a documented promote-or-retain-control decision based on 4,096-unit evidence.
- Bounded endogenous planning works without an LLM and remains subordinate to the existing action authority.
- Renderer-facing retrieval uses verifiable ephemeral projections and exact Subjective Frame receipts without acquiring epistemic authority.
- External learned knowledge is durably distinct from lived autobiography and preserves correction/contradiction lineage.
- Every promoted procedural habit, expectation, theory-of-mind, relationship, or self-model mechanism has current causal evidence rather than merely stored state.
- Runtime health, backup/restore, crash inheritance, capability boundaries, and packaged/offline operation are sufficient for an operator to recover the system during a live deployment.
- Long-run causal characterization is current for every production-load-bearing mechanism.

- World-fact expectations, action-outcome expectations, causal-sequence evidence, and counterfactual model predictions remain mechanically distinct and cannot train one another through the wrong evidence path.
- Private cognition visible to an expression renderer cannot leak by direct copy merely because it is present in context, and Pretorius does not receive privileged self-explanations of hidden implementation causes.
- Every bounded load-bearing state store has an explicit, tested capacity/overflow policy and a documented information-loss frontier rather than silent continuity destruction.
- Historical donor branches are no longer required to understand or reconstruct the production architecture.
- README, architecture contracts, migration contracts, public adapter contracts, experimental methods, and exact release evidence are sufficient for a new engineer to continue without conversation history.
- One definitive release candidate passes independent assessment before merge.

This definition describes an artificial cognitive architecture and persistent artificial individual. It does not claim consciousness, sentience, biological equivalence, or human-level cognition.

## 22. Development and branch discipline for every remaining gate

For each gate:

1. branch from current accepted main;
2. write or update the contract before behavioral integration;
3. implement the smallest causally complete vertical slice;
4. add unit, integration, adversarial, causal, migration, and restart tests as applicable;
5. run held-out or matched-lesion evidence;
6. preserve exact experiment identity and failed/null results;
7. update README and specialized contracts;
8. consolidate the gate to one review branch;
9. open one non-draft PR;
10. record exact head SHA, test count, workflow IDs, artifacts, residual risks, and deferred work;
11. obtain independent review;
12. merge with normal merge commit when provenance matters;
13. run post-merge production CI;
14. retire the gate branch only after the production line is verified.

Do not accumulate multiple permanent Pretorius implementations.

Do not re-open accepted architecture merely because a later mechanism uses different terminology.

Do not merge historical branches wholesale.

Do not promote a mechanism because it is psychologically plausible.

Every production-load-bearing mechanism must have an explicit causal path and current evidence.
