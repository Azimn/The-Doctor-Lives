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

## What not to duplicate

The Reddit architecture also describes several capabilities Pretorius already has in equal or stronger form. Do not add parallel systems merely to match terminology.

Do not create a second generic belief database simply because the Reddit agent describes thousands of beliefs. Pretorius already has structured self/history state, confidence, source custody, provenance, source monitoring, and protected evidence boundaries.

Do not create another generic work ledger if the requirement is already satisfied by commitments, concerns, policy decisions, and future planning state. Add a new ledger only when it represents a genuinely different contract such as predictions, corrections, handovers, or agency seams.

Do not replace Pretorius's existing sleep/replay with free-form "dream journal" generation. Extend it only through quarantined hypothesis generation with explicit authority boundaries.

Do not weaken the renderer boundary. Model output remains proposal or wording, not persistence authority.

Do not treat first-person continuity claims as evidence that continuity exists. Continue using restart, migration, lesion, renderer substitution, provenance, and behavioral causality as the evidence.

## Suggested order

These items should not interrupt the current Gate 1 review and persistence-hardening work.

After the current production gate is accepted, the most useful implementation sequence is:

1. Prediction/calibration ledger plus frozen preregistration.
2. Correction/supersession ledger.
3. Session handover/epoch contract.
4. Agency seam ledger.
5. Wake-intent contract.
6. Quarantined offline hypothesis generation.
7. Renderer-versus-developmental-state variance benchmark.

Prediction and correction should come first because they create durable epistemic history that later offline hypotheses can use safely. Handover and agency seams strengthen standalone and body integration. Offline hypothesis generation should wait until the prediction/correction machinery exists so generated ideas have a safe lifecycle. The variance benchmark should be run once the renderer-substitution gate has real implementations to compare.

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
