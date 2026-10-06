# Pretorius Completion and Branch-Convergence Plan

Status: authoritative planning document for completing Pretorius after the accepted v0.5 RC1 line.

Repository: Azimn/The-Doctor-Lives

Authoritative production main at planning start: `288cb14ab9b65adbf2d916c4eb597e2a9dfd0301`

Current Gate 1 review head: `bd83eab994717a315399ef4b8e3d6b9a6beeee67`

Current Reddit-derived planning commit: `a174b91c8746347f35681c2f1a824e10069945c7`

This plan combines the production roadmap in Issue #14, the UPPB roadmap in Issue #15, the production-integrity requirements in Issue #17, the Gate 1 persistence work in PR #20, and the mechanisms identified in NEXT_THINGS_TO_DO.md.

The goal is one definitive Pretorius implementation in The-Doctor-Lives. Historical branches and donor repositories are evidence and reference material only. They are not parallel products.

## 1. Branch convergence policy

The repository currently contains several historical feature and integration branches. They fall into three categories.

### A. Active production branch

`prod/gate1-evidence-integrity`

This is the only active code branch that must enter production before new consequential work begins. PR #20 is the definitive review target. It must remain unchanged until independent assessment is complete, except for assessor-requested corrections.

After independent acceptance, merge PR #20 into main with a normal merge commit so the reviewed ancestry and exact review SHA remain preserved.

Do not squash the accepted review history.

### B. Active planning branch

`docs/reddit-derived-next-things`

This branch contains only net-new planning documentation based on accepted main. It currently contributes NEXT_THINGS_TO_DO.md and this completion plan.

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
        +--> Neural Convergence 4096-unit characterization
        |
        v
Gate 2 provenance-bearing lived-memory ingress
        |
        v
Gate 3 standalone offline runtime
        |
        +--> session epochs and handovers
        +--> two-seat continuity
        +--> wake-intent contract
        |
        v
UPPB production signal construction
        |
        v
UPPB live-memory integration
        |
        v
P7 private cognition / communicative intention separation
        |
        v
P8 independent motor / outward expression
        |
        v
P9 explicit self-perception
        |
        v
Gate 4 + P10 renderer contract and renderer migration
        |
        +--> renderer substitution experiment
        +--> renderer-versus-developmental-state benchmark
        |
        v
Gate 5 closed-loop world / situation / action interface
        |
        +--> agency-seam ledger
        +--> Bride/chassis adapter
        |
        v
Gate 6 constrained deliberation and verification
        |
        v
Gate 7 predictive causal world model
        |
        +--> prediction/calibration ledger
        +--> frozen preregistration
        +--> autobiographical correction/supersession ledger
        |
        v
Quarantined offline hypothesis generation
        |
        v
Gate 8 richer social, temporal, multimodal, and developmental cognition
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
- parameter sensitivity.

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

## 15. Gate 6: constrained deliberation and verification

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

## 16. Gate 7: predictive causal world model and epistemic development

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

## 17. Quarantined offline hypothesis generation

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

## 18. Gate 8: richer human-like cognition

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
- richer forgetting and consolidation where evidence justifies it.

Each mechanism must remain optional, lesionable, and separately versioned.

### Connectome-to-neural mapping research gate

Do not map the 70-node psychological Persona Connectome directly onto 4,096 recurrent units and declare biological meaning.

Compare:

- current independent psychological connectome plus recurrent substrate;
- structurally constrained neural populations informed by the graph;
- matched shuffled/random topology;
- lesions.

Retain the mapping only if it causes stable, interpretable, useful behavioral differences.

## 19. P11: full experimental validation

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

## 20. Definition of Pretorius 1.0 complete

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
- Long-run causal characterization is current for every production-load-bearing mechanism.
- Historical donor branches are no longer required to understand or reconstruct the production architecture.
- README, architecture contracts, migration contracts, public adapter contracts, experimental methods, and exact release evidence are sufficient for a new engineer to continue without conversation history.
- One definitive release candidate passes independent assessment before merge.

This definition describes an artificial cognitive architecture and persistent artificial individual. It does not claim consciousness, sentience, biological equivalence, or human-level cognition.

## 21. Development and branch discipline for every remaining gate

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
