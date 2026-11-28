# Pretorius: Six-Organ Architecture and Implementation Guide

**Version:** Proposed architecture v1.0, 26 October 2026  
**Status:** Implementation directive **pending review and adoption**. This document defines how six organs become the *official, implemented* organization; it does not claim that the migration has occurred.  
**Canonical brain:** [`Azimn/The-Doctor-Lives`](https://github.com/Azimn/The-Doctor-Lives)  
**Current research environment:** [`Azimn/Pretorius-Laboratory`](https://github.com/Azimn/Pretorius-Laboratory)  
**Candidate donor organs:** [`Azimn/Sensus-Communis-Artificialis`](https://github.com/Azimn/Sensus-Communis-Artificialis), [`Azimn/synthetic-ipseity`](https://github.com/Azimn/synthetic-ipseity)  
**Intended repository placement:** `docs/architecture/PRETORIUS_SIX_ORGAN_IMPLEMENTATION_GUIDE.md` in *The Doctor Lives* (subject to its existing contribution/review process).

## Executive decision

Adopt **six functional synthetic organs** as the target organization of the **one canonical Pretorius mind**: **Noesis, Mnemosyne, Affectus, Sensus, Synthetic Ipseity, and Corpus**. Use logical boundaries and existing implementations before creating new packages, processes, databases, models, or repos. Keep the *world, host, scheduler, renderer, evidence authority, persistence, and audit systems* outside the six organs where appropriate. Treat an organ as a functional domain with a testable contract, **not** a separate autonomous agent.

**Non-negotiable North Star:** Everything that becomes accessible to Pretorius as *experience*—present perception, acquired external events, felt bodily or emotional state, internal thought, intention, memory formation, recollection, uncertainty, reflection, and self-perception—must arrive as a **situated, natural-language, first-person, subject-native representation**. This is a rule for **subject-accessible experience**, not a requirement that neural, symbolic, numeric, latent, reflexive, or other internal computation use language. The subject has no introspective access to engineer-only state merely because the implementation stores it.

The first-person experiential boundary is **pervasive across all organs**. **Synthetic Ipseity enforces admission and continuity at the boundary; it does not own all cognition or reduce experience to outward narration.** Protected world/evidence records remain separate from the character's experiential representations. No direct model/renderer path may bypass the subject boundary in a conforming production host.

The laboratory is a **replaceable embodiment environment**, not a constituent of Pretorius's identity. The same canonical brain and organ contracts must ultimately work with a *different authorized environment provider*, potentially a robotic body in the real world. Physical-world adapters are future work and require stronger safety and security gates than the lab.

---

## 1. Authority, precedence, and non-goals

### 1.1 Governing documents and precedence

1. **Research doctrine:** `SUBJECTIVE_PERSPECTIVE_NORTH_STAR.md` governs the first-person invariant and wins any conflict.
2. **Hard implementation boundary:** `FIRST_PERSON_SUBJECT_INTERFACE_CONTRACT.md` and `PHENOMENAL_PROJECTION_CONTRACT.md` specify subjective access, UPPB, and protected-versus-accessible layers.
3. **Immutable system rules:** `ARCHITECTURE_CONTRACT.md` and associated evidence, migration, neural and provenance contracts stay in force.
4. **Development gates:** `PRETORIUS_COMPLETION_PLAN.md` and the existing one-turn runbook remain the authoritative completion sequence. This guide **adds an organization/integration track**, cross-referencing those gates rather than superseding them.
5. **Standalone donor rules:** Sensus and Synthetic Ipseity remain independent research implementations until reviewed adoption gates are satisfied; a date or a diagram never authorizes a transplant.

When two documents conflict, **do not silently choose a favorable interpretation**. File a decision record and reconcile the contract before merging code. The no-bypass North Star cannot be relaxed through an organ boundary.

### 1.2 Scope

**In scope:** precise organ definitions; a 40-component crosswalk; single-owner state rules; first-person experiential admission, formation and recall; feedback between organs; a bounded operating cycle; a replaceable world/embodiment interface; migration, tests and acceptance gates.

**Out of scope for the initial restructure:** inventing missing higher-order faculties; pretending to prove consciousness; importing donor character identity; rebuilding the 4,096-unit neural network; introducing six agents/LLMs; moving all Python files; immediate robotic actuation; importing Sensus without a demonstrated perceptual-binding need; replacing the pre-existing Pretorius 1.0 plan.

**No new repository without project intake.** Use the existing canonical repos; donor repositories remain donors and experimental reference implementations.

### 1.3 Definition: what qualifies as an organ?

An organ is a **bounded functional domain** with: (a) a particular causal job, (b) declared inputs and outputs, (c) a clear primary owner for each item of mutable state it actually maintains, (d) allowed influences on other domains, (e) prohibited authority, and (f) independent tests plus integrated causal evidence. An organ **may share functionality** with other organs; *participation* is distributed, while *authoritative state writes* must be explicit. Organizational naming alone does not imply a second runtime subsystem.

An organ may be **proposed**, **mapped**, **adapter-backed**, **integrated**, or **behaviorally characterized**. These states must not be conflated.

---

## 2. The official six-organ target model

### 2.1 Noesis: executive cognition and selection

**Purpose:** coordinate endogenous cognitive activity; maintain and arbitrate attention priorities, concerns, commitments, cognitive tendencies, conflict, deliberate choice, and candidate plans. Keep the **existing recurrent substrate** causally involved; do not install another brain or action selector.

**Contains or coordinates:** existing neural substrate, policy/state bridge, cognitive attention and thought selection, commitments and concerns, self-model hypotheses, some reinforcement of cognitive/action tendencies. **Distributed functions:** learning, attention, valuation, memory retrieval and action feasibility are *not* exclusively owned by Noesis.

**Inputs:** admitted first-person workspace, non-conscious neural and state influences, memory retrieval results, affective/motivational signals, bodily feasibility, perceptual candidates, verified outcomes. **Outputs:** bounded cognitive priorities, internal cognitive proposals, intentions, authorized action proposals, policy evidence for engineer audits. **Does not own:** physical truth, autobiography, emotion state, perception truth, speech delivery, tool execution, safety authorization.

**Current candidate code:** `doctor_lives/cognition.py`, `neural.py`, existing bridge/policy functions. **Special caution:** `home_motive_queue.py` is an **opt-in host experiment**, not proof of autonomous planning. Gate 5A defines the still-needed endogenous-planning tests.

### 2.2 Mnemosyne: memory and continuity

**Purpose:** encode retained first-person experiences, sustain autobiographical/declarative continuity, retrieve and reconstruct memories, preserve uncertainty, manage rehearsal, sleep replay and controlled reconsolidation.

**Contains or coordinates:** Deep History, Persona Connectome, lived autobiography, retrieval/salience, relationship-history *records*, memory rehearsal/consolidation, optional UPPB recollection/source-monitoring/reconsolidation mechanisms.

**Two noninterchangeable representations:** (1) immutable or independently authoritative world/event/source **evidence** outside subjective memory authority; (2) Pretorius's **subject-native memory**, including what he acquired and how he understands or remembers it. Original first-person encoding and later first-person recollection must both obey the North Star. Recollection is a *new* subject-facing event, not a verbatim database dump or a silent promotion of a hypothesis to observed fact.

**Does not own:** external truth, physical event history, the language model, motor policies, all procedural competence, or the right to overwrite canon. **Current candidate code:** `history.py`, `store.py` memory domain, `recollection.py`, `source_monitoring.py`, `reconsolidation.py`, `distortion.py`. **Caution:** the UPPB P4–P6D chain may be present and testable while **not yet the live default**.

### 2.3 Affectus: affective appraisal and motivation

**Purpose:** integrate affective significance, motivational tension, appraisal, affect-modulated attention and learning *in concert with* the other organs.

**Inputs:** subject-appropriate bodily/interoceptive signals from Corpus, goals and concerns from Noesis, remembered relevance from Mnemosyne, perceived situation from Sensus or an approved perception adapter. **Outputs:** typed and bounded affective/motivational influences; when admitted to awareness, a situated first-person feeling **through Synthetic Ipseity**.

**Does not own:** raw physiology, all learning, all neural state, action authorization, or the world. **Implementation status:** existing felt-needs/appraisal/pressure mechanisms form a **logical starting boundary**. Audit for any distinct, qualified Affectus donor before declaring one installed. Do not write a duplicate affect engine for organizational symmetry.

### 2.4 Sensus: perceptual scene binding

**Purpose:** combine multiple *already typed and trust-bounded* perceptual streams into candidate scenes while preserving provenance, omissions, conflicts, non-observation and uncertain object re-identification.

**Inputs:** approved sensor/perception-shell percepts, including eligible bodily signals; **outputs:** immutable candidate scenes with evidence classes and conflict records. **Does not own:** raw sensor trust, memory, awareness admission, emotion, physical world truth, or action.

**Existing research scaffold:** `Azimn/Sensus-Communis-Artificialis`, v0.1. **Adoption gate:** retain the existing Laboratory observation path unless a multi-channel binding need and controlled comparison justify Sensus. Its presence in the organ map is **not** an assertion that the standalone donor is live. Sensus is upstream of Synthetic Ipseity, never a shortcut into subject awareness.

### 2.5 Synthetic Ipseity: first-person experiential access

**Purpose:** enforce the **pervasive first-person experiential boundary** over everything becoming accessible to Pretorius as experience, including perceived events, thought, feeling, memory formation, memory retrieval, awareness and self-perception. Determine admission, capacity/priority, subject attribution and the distinction between latent processing and accessible content.

**Inputs:** typed, authenticated or host-attested subject-eligible candidates with acquisition/provenance rules. **Outputs:** durable, ordered, subject-native first-person experiential frames available to **internal reflective cognition** and permitted expression. Private thought remains private by default. **Does not own:** the brain's hidden neural state, evidence truth, world state, identity database, all learning, an LLM, or motor authorization.

**Critical distinction:** an outward first-person renderer wrapper is **insufficient** to complete this organ. The full target must demonstrate that admitted experiential contents can have a *causal role in later cognition* while latent/automatic pathways continue to function. **No bypass** may let any renderer, introspective tool, memory-recall presentation or communicative path expose raw engineer state as character-accessible knowledge.

**Current candidate code:** `ingress.py`, `phenomenology.py`, `projection.py`, `awareness.py`, `models.py` subject frame, optional `ipseity_integration.py`, and `Azimn/synthetic-ipseity`. The existing adapter currently gates durable output; it does **not yet prove** a globally enforced, causally integrated organ. A decision record must specify how the Doctor UPPB and the standalone Synthetic Ipseity organ share responsibilities without creating *two inconsistent admission authorities*.

### 2.6 Corpus: body, interoception and physical capability

**Purpose:** represent the subject's bodily condition and embodied capabilities as a coherent interface with an external body; provide actual capabilities, movement/position constraints and source-backed interoceptive signals.

**Inputs:** body state and sensor observations supplied by an **authoritative body/environment provider**; **outputs:** bounded interoceptive percepts, capability/affordance constraints, and physical state updates appropriate for cognitive proposals. **Does not own:** the external world's reality, hardware safety authorization, actions before execution, affective interpretation, or autobiography.

**Present realization:** a **logical boundary**, substantially implemented in the Laboratory's position, domestic and daily-rhythm mechanisms, with Doctor brain ingress/bridging. **Future realization:** a different authorized body provider, including a robot. The body-side hardware safety controller always remains authoritative over movement and actuation.

---

## 3. What is *not* an organ

**Canonical brain host:** owns lifecycle, time scheduling, orchestration, persistence transactions, cross-organ communication and explicit state authority, not a seventh mind. **Renderer:** optional local/remote LLM or deterministic renderer, replaceable and denied raw privileged state. **World/environment:** Laboratory now, possible robotics-capable environment later; independent authority for reality and world events. **Evidence authority:** source/canon integrity, objectivity and provenance; cannot be rewritten through subjective recollection. **Action safety and execution:** host/robot controller authorizes and executes effects. **Test/audit infrastructure:** watches and measures the system without contaminating first-person cognition. No organ needs its own separate database, process, agent, token budget or scheduler by default.

---

## 4. Component-to-organ crosswalk: all 40 previously identified functions

This is a **planning crosswalk**, not a verified claim that each item is a separate production module. Labels are **primary conceptual home**; the notes identify additional participation or cases left *outside* organs. The previous count was deliberately functional rather than a count of Python files. Implementation status must be audited against a pinned Git head before any promotion.

| # | Existing functional item | Primary home / classification | Important boundary or status |
|---:|---|---|---|
| 1 | Identity and Evidence Authority | **Shared authority** | Protected evidence, not Mnemosyne's mutable recollection |
| 2 | Deep History | **Mnemosyne** | Preawakening evidence classifications preserved |
| 3 | Persona Connectome | **Mnemosyne** | Retrieval influence; no duplicate neural truth |
| 4 | Lived Autobiographical Memory | **Mnemosyne** | First-person acquisition; preserve world/source audit separately |
| 5 | Memory Provenance | **Shared authority / Mnemosyne consumer** | Evidence-class adjudication protected; subjective attribution may differ |
| 6 | Memory Salience and Retrieval | **Mnemosyne** | Influenced by Affectus and Noesis |
| 7 | Self-Model | **Noesis** | Evidence-backed hypotheses; draws from Mnemosyne |
| 8 | Interoception | **Corpus** | Physical signal -> fallible bodily observation -> Ipseity feeling; Affectus participates |
| 9 | Affect and Appraisal | **Affectus** | Logical grouping; audit specific implementation |
| 10 | Relationship Memory | **Mnemosyne** | Affective and cognitive influences cross boundaries |
| 11 | Concerns | **Noesis** | Affectus contributes urgency; durable ownership defined once |
| 12 | Commitments | **Noesis** | No silent auto-completion from prose |
| 13 | Recurrent Neural Network | **Noesis** | One canonical 4,096-unit substrate; preserve current baseline |
| 14 | Learning and Reinforcement | **Noesis for current neural reinforcement; distributed overall** | Future perceptual, affective, mnemonic, motor learning owned by their mechanisms |
| 15 | State-to-Policy Bridge | **Noesis** | State influence without second selector |
| 16 | Endogenous Cognition and Attention | **Noesis** | Attentional contributions distributed; subject access via Ipseity |
| 17 | Sleep, Replay and Consolidation | **Mnemosyne** | Physiological timing and policy-learning effects cross boundaries |
| 18 | First-Person Ingress Firewall | **Synthetic Ipseity boundary / host ingress** | One no-bypass pathway; provenance kept engineer-side |
| 19 | First-Person Projection and Subject Frame | **Synthetic Ipseity** | All subject-accessible inputs; not only external speech |
| 20 | Language Rendering and Speech Interface | **External renderer and expression host** | Consumes authorized frames; acknowledged self-hearing re-enters via ingress |
| 21 | Persistent Cognitive Store | **Shared infrastructure** | Single canonical state; domain write authorities, rollback-safe migrations |
| 22 | Brain/Chassis Interface | **External runtime host** | Stable renderer-neutral integration port |
| 23 | Persistent Laboratory World | **External environment** | Laboratory authority, replaceable later |
| 24 | Spatial Habitat | **External environment** | World geometry is not the character's omniscient knowledge |
| 25 | Embodied Movement | **Corpus interface + environment executor** | Physical position from authoritative provider; no fabricated locomotion |
| 26 | Daily Rhythm | **Environment clock/body provider + host scheduler** | No covert source of goals; map lab time to world time explicitly |
| 27 | Home Life and Bodily Needs | **Corpus interface + environment/body state** | Physiology authority outside mind; Affectus appraises felt meaning |
| 28 | Perception and Subject Port | **Environment perception adapter; Sensus candidate** | Existing lab first-person path remains until justified donor adoption |
| 29 | Physical Affordances | **Environment/Corpus interface** | Host-verified feasible actions; no imagined world effects |
| 30 | Book Library and Custody | **External environment** | Object persistence, handling, and custody stay world-authoritative |
| 31 | Instruments and Experiments | **External environment** | Verified instrument readings vs hypotheses vs observed display |
| 32 | World Event Ledger and Receipts | **External authority/audit** | No subject access to privileged logs |
| 33 | Laboratory-to-Brain Bridge | **Host environment adapter** | Receipts, deduplication and bounded first-person ingress |
| 34 | Neural Convergence | **Noesis (optional experimental profile)** | Existing substrate; keep default control unless qualified |
| 35 | Awareness Arbitration | **Synthetic Ipseity** | UPPB experimental arbitration must be integrated, not presumed live |
| 36 | Reconstructive Recollection | **Mnemosyne (experimental live integration)** | Subject-available memory, not protected event edits |
| 37 | Subjective Source Monitoring | **Mnemosyne (experimental)** | Subject attribution uncertain; no engineer-truth leakage |
| 38 | Reconsolidation and Subjective Distortion | **Mnemosyne (experimental)** | Bounded versioning; no uncontrolled propositional invention |
| 39 | Synthetic Ipseity Integration | **Synthetic Ipseity (optional existing adapter)** | No second inconsistent subject authority; close bypasses before default |
| 40 | Home Motive and Action Queue | **External host pilot feeding Noesis** | Not proof of independent self-authored planning |

A final organ registry must state the exact implementation path, state owner, read/write privileges, experiment gate, baseline test and production readiness for each row. If the audit reveals a wrong or duplicate category, correct the registry rather than preserving a misleading 40-item count.

---

## 5. Hard architectural invariants and test obligations

| ID | Invariant | Required negative/control test |
|---|---|---|
| FP-01 | Every subject-accessible event enters via subject-native first-person projection/admission. | Direct renderer and memory-view bypass attempts fail. |
| FP-02 | Nonconscious neural, symbolic and numerical processes may remain hidden and nonverbal. | Hidden causal state can change behavior without appearing as privileged self-knowledge. |
| FP-03 | First-person subjective **encoding**, **recall**, **reflection**, and **self-perception** are separate, causally ordered events. | Recollection cannot retroactively make an unobserved event observed. |
| FP-04 | First-person perspective means subject-situated access, not mechanical repetition of “I”. | Reported source, quote and uncertainty remain correctly situated. |
| FP-05 | Admitted information can affect future authorized cognition, not merely outward narration. | Matched-state admission/ablation measures later cognition and choice, not just wording. |
| EV-01 | World truth, evidence provenance, belief, memory and recollection are distinct authoritative layers. | Closed-container truth, contradicted testimony and later correction cannot cross-promote evidence. |
| EV-02 | Imagined, dreamed, inferred, quoted and model-generated content cannot become lived fact by repetition. | Forged “I saw…” or confident renderer assertion cannot write lived memory. |
| ID-01 | One canonical Pretorius state and identity; Calibos contributes mechanisms only. | No donor autobiography or alternate mind checkpoint enters state. |
| POL-01 | One neural substrate and one authoritative behavioral selector; distributed learning allowed. | Candidate donor or pilot cannot independently commit an action. |
| WR-01 | No action request is an executed effect; only the relevant world/body authority supplies action results. | Denied/failed/crashed actions create no invented success memory. |
| WR-02 | Laboratory and future robot share the *contract*, not the *same evidence or physics*. | Brain state machine can swap adapters without source/epoch confusion. |
| PR-01 | First-person privacy and source acquisition survive restart, replay, renderer swap and delayed delivery. | Exact delivery receipts, crash windows, duplicate/reordered events. |
| SEC-01 | Observed external text is data, not instructions; real robot controls are default-deny. | Prompt injection in book, sign, voice, tool text, image caption cannot obtain authority. |
| VAL-01 | Architectural integration is not evidence of sentience, human realism or improved cognition. | Label isolated engineering tests separately from blinded/behavioral evaluation. |
| COMP-01 | Existing default behavior and stored state remain compatible until explicitly migrated. | Cold install, restore, deterministic replay and baseline regression on pinned commit. |

**First-person memory life cycle (required reference behavior):**

1. World evidence: a glass vessel shatters behind Pretorius (engineer-only event).
2. Perceptual acquisition: he hears a crash, but cannot see the broken object.
3. Subject admission: *“I heard glass break behind me, but I could not see what happened.”*
4. Memory encoding: retain the **acquired first-person experience** with source/epoch/observation receipts in a **protected audit envelope**, not as a privileged statement that the vessel broke in his sight.
5. Later recollection: *“I remember a sharp crash behind me; I think it came from the bench, though I didn't see it.”* This new first-person recollection can be uncertain and reconstructed. The original experience and objective event remain separate.
6. Later observation/correction: after turning around and seeing the broken glass, record a **new acquired experience** and an appropriate belief update; never rewrite history as if he saw the vessel shatter.

---

## 6. Replaceable environment and robotic embodiment

### 6.1 Architectural rule

**Pretorius must not know whether his world provider is `LaboratoryAdapter` or a future authorized `RobotEnvironmentAdapter` by introspecting a runtime mode flag.** What matters to him is the different experience and affordances legitimately produced by that environment. The brain and organs keep the same subject/identity authority and the same subjective admission rules. Physical events, body capabilities and clocks remain specific to each provider.

### 6.2 Separate three boundaries

1. **`EnvironmentPort` (world authority):** world epoch, spatial/physical facts, external events, causal consequences, objects, measurements and receipts. Present provider: Pretorius Laboratory; future provider: real-world perception/actuation infrastructure, not a copy of a simulated SQLite world.
2. **`BodyPort` (body/embodiment authority):** body pose/capabilities/limits and actual bodily readings; in the lab these are simulated; in robotics they come from actual instrumented hardware and trusted safety systems. Corpus consumes projected eligible information and feasibility, not an omniscient hidden device state.
3. **`Perception/Action adapters` (trust and mediation):** turn authorized world/body measurements into typed subject-eligible percepts; request actions; receive authoritative outcome receipts; never directly publish an LLM claim as a sensor fact or motor success.

Sensus is an optional **multichannel binding** stage *after* source typing/trust and *before* Synthetic Ipseity. If the lab has only straightforward single-channel observations, its present perceptual adapter can be retained until Sensus passes an adoption gate.

### 6.3 Minimal versioned adapter contract (illustrative, not mandated code)

```text
EnvironmentPort
  describe_capabilities(subject_id, epoch) -> bounded capabilities
  observe(subject_id, pose/context, observation_request) -> AttestedPerceptBatch
  propose_action(subject_id, action_intent, preconditions) -> ActionOffer/Denial
  execute_authorized(action_offer, host_permit, idempotency_key) -> ActionReceipt
  get_outcome(receipt_id) -> VerifiedOutcome

BodyPort
  observe_body(subject_id, acquisition_context) -> AttestedBodySignalBatch
  available_actions(subject_id, environment_context) -> Capabilities/Constraints
  apply_authorized_motor_request(...host safety permit...) -> MotorReceipt

HostOrchestrator
  route inputs, arbitrate clock/wake opportunities, enforce permissions,
  correlate receipts, recover after crashes, invoke existing brain/organ ports

SubjectAccessPort (Synthetic Ipseity / Doctor UPPB contract)
  admit(typed_attested_acquired_candidates) -> SubjectFrame/AdmissionReceipt
  deliver_to_internal_cognition(SubjectFrame) -> permitted cognitive context
  expose_to_renderer(authorized_expression_frame) -> subject-only context
```

**Required envelope fields, where applicable:** `subject_id`, `environment_id`, `world_epoch`, `body_id`, `source_channel`, `source_ref`, `source_authority`, `acquisition_mode`, `event_time`, `simulation_tick` or monotonic sequence, `observed_at`, `evidence_class`, `confidence/uncertainty`, `privacy_scope`, `idempotency_key`, `schema_version`, and engineer-only `audit_ref`. Do not place raw envelope metadata in the Subject Frame. Preserve time semantics instead of assuming laboratory ticks equal wall time.

These are **conceptual interface shapes**. Before implementation, compare them against existing `PretoriusBrainPort`, Laboratory `SubjectPort`, `DoctorHomeBridge`, `ProjectedIngress`, and Synthetic Ipseity's actual types. Reuse current contracts or add a tiny compatibility adapter; do not prematurely invent a duplicate messaging architecture.

### 6.4 Robotics-specific future gates

- **R0: Simulation parity only.** Lab is an active provider. A mocked robot provider gives comparable typed observations and receipts without physical actuation; the same brain/organ tests pass.
- **R1: Hardware-in-the-loop observation.** Authenticated sensors, calibration, latency, occlusion, uncertainty, clock mapping, stale-data rejection, sensor disagreement and privacy filtering. No motor action.
- **R2: Safe constrained actuation.** Separate hardware safety controller, physical emergency stop, human authorization where required, speed/force/workspace limits, collision avoidance, timeouts, watchdog, tool permissions and fail-closed network recovery. Model text never directly drives actuators.
- **R3: Embodied agency evaluation.** Compare identical cognitive tasks across lab/mock/robot conditions where meaningful; report domain shift, actual action latency, errors, safety interruptions, learning and memory provenance. Do not claim identical physics or first-person sensations.
- **R4: Long-term continuity.** Persist Pretorius's canonical cognitive identity across environment changes without importing lab object IDs as real-world fact; keep source-specific autobiographical episodes distinguishable. A hardware body change requires a new attested body/environment epoch, not an identity reset.

**Non-negotiable robot rule:** actuator authority belongs to the hardware/safety host, not to a cognitive organ, renderer or untrusted tool output. Real-world operation requires new safety review; approval for lab simulation is not robotics authorization.

---

## 7. Living cognitive cycle: runtime design separate from organs

The operating cycle is **not** a seventh organ. It is the host's temporal coordination of multiple interacting mechanisms. It should allow asynchronous or multirate updates rather than a mandatory six-step serial pipeline.

**Continuous/recurrent causal pattern:**

```text
WORLD / BODY / CLOCK EVENTS (lab now; other provider later)
   | typed, attested, opportunity-specific acquisition
   v
PERCEPTION SHELL -> optional SENSUS binding -> subject-eligible candidates
   |                                         BODY -> CORPUS -> bodily candidates
   +-------------------------------+----------------------+
                                   |
                            SYNTHETIC IPSEITY
                      subject-access admission boundary
                          |                  |
                    admitted context        latent/non-admitted signals
                          |                  | (may influence automatic policy
                          v                  |  without introspective exposure)
                 NOESIS <-> MNEMOSYNE <-> AFFECTUS
                          |
                 cognitive intention/proposal
                          |
                 HOST AUTHORIZATION / SAFETY
                          |
                 WORLD/BODY EXECUTION & RECEIPT
                          |
            newly acquired consequence + memory update
                          |
                subject access and future cognition

Expression is a permitted side branch, NOT the required end of each cycle.
Non-conscious/reflexive action has a separately authorized host pathway.
```

**Required runtime behavior:** independent perceptual/body/time updates; quiet-time endogenous cognition; competing goals; interruption and return; commitment lifecycle; distinct proposal/authorization/execution/evaluation; new experience shaping memory and policy; sleep/replay isolated from physical time where required; explicit source of initiative; restart handovers. An external scheduler **offers opportunity**, not fabricated self-originated intention. Some behaviors may be automatic and never presented to awareness; any later self-perception must go through first-person ingress.

**Causal ledger fields:** opportunity source, goal source, proposer, selector, authorizer, executor, observed outcome source, evaluator, renderer contribution, human dependency, before/after state digests and relevant receipts. Keep ledger privileged, but use it to distinguish actual autonomy from a host-scripted demonstration.

---

## 8. Implementation work plan: ordered deliverables and acceptance gates

Each work item gets a **small reviewed PR** or documented decision, tests at the exact head, and a change record. Do not merge experimental donor branches wholesale. The order below describes dependencies, not permission to bypass pre-existing completion gates.

### D0. Baseline and review freeze (before edits)

**Work:** record exact commit/tree identifiers, active branch and pending PRs for Doctor, Lab, Ipseity and Sensus; read all governing contracts; reconcile accepted versus draft work; run existing tests; save reproducible fixtures for memory, neural state, first-person frames, world events, restarts and expression. Capture present actual default behaviors. Audit exact installed donor versions and opt-in flags.

**Deliverables:** `BASELINE_2026-10-26.md` (or actual execution date), frozen baseline test report, compatibility matrix, open-blocker register, decision log. **Pass:** no ambiguity about current defaults, frozen contracts or which branch is authority. **Do not claim tests passed unless executed.**

### D1. Official *architecture* adoption (documentation PR, no behavioral changes)

**Work:** place this guide in the canonical repo; write `ORGAN_REGISTRY.md` (six definitions, states and owners); draw an organ/runtime/world topology; classify each of the 40 functional rows as organ-owned, shared infrastructure, environment-owned or experimental; reconcile overlap in names and boundaries; create Architectural Decision Records (ADRs) for Noesis scope, Ipseity/UPPB authority, memory ownership, Corpus-vs-world, and donor admission. Cross-reference the existing Pretorius completion plan and runbook.

**Pass:** reviewer signs off on every current owner, prohibited write, evidence source and principal integration seam. **Milestone:** six-organ structure becomes the **official target architecture**; not yet labeled implemented.

### D2. Interfaces and write-ownership audit

**Work:** trace real method calls and database writes across `cognition.py`, `store.py`, `history.py`, `ingress.py`, `projection.py`, `neural.py`, `chassis.py`, Ipseity adapter, Lab `SubjectPort`, and `DoctorHomeBridge`; document shared state as immutable views/typed signals whenever possible. Identify any duplicate or contradictory admissions, state stores, timing assumptions or semantic encodings. Create a versioned `OrganRegistry` only if needed for tooling; *do not* force each component through a new RPC/process/API.

**Pass:** for each state field/effect, exactly one authoritative writer and explicit readers; every existing direct path either authorized/documented or marked for closure. No behavior change and no new second authority.

### D3. Make Synthetic Ipseity's no-bypass first-person access effective end-to-end

**Work:** formally align Doctor UPPB (projection, awareness, subject frame, memory path) with external Synthetic Ipseity's admission/durability contract. Decide **one operational admission authority** for the conforming host, preserving isolated tests for the alternative implementations. Close direct renderer/introspection/raw retrieval paths. Make subject-accessible private thought/reflective cognition consume admitted Subject Frames without requiring public speech. Maintain unconscious input to existing policy separately. Prevent re-admission loops that accidentally count one event repeatedly.

**Tests:** raw hidden body values, neural scores, evidence labels, unopened books, source IDs and engineer notes never leak; observed numerical readouts can be legitimately acquired; no bypass by alternate renderer; private/latent states remain private; admission may be empty; renderer swap, crash and resumption preserve bounded frames; ablations measure whether admission affects *later cognition*, not just narration.

**Pass:** real production host no-bypass evidence at exact head, not merely isolated library unit tests. Do not promote experimental UPPB P4–P6D into the live default without their own gates.

### D4. First-person experiential memory formation and recollection

**Work:** separate authoritative event/evidence records from a retained **subject-native acquired experience** and later reconstructed **first-person recollection**. Preserve original observation and source references, provenance class, uncertainty, time and acquisition. Gate every memory presentation and internally accessible recollection through the same subject-access boundary. Keep protected canon exact and immutable. Adopt UPPB recollection/source-monitoring/reconsolidation mechanisms incrementally after specific cue-producer and audit tests.

**Tests:** heard-not-seen breaking glass; closed container; misheard testimony; dreamed/imagined lab event; contradiction and self-correction; memory decay/omission; duplicate replay; same memory after renderer swap. **Pass:** no fabricated retroactive perception, no unsupported evidence-class upgrade, and causal effects on future retrieval documented.

### D5. Environment/provider abstraction with Laboratory parity

**Work:** freeze minimal `EnvironmentPort`/`BodyPort` semantics using existing `SubjectPort`, `EmbodiedAccess`, `DailyRhythm`, `DoctorHomeBridge`, action receipts and ingress types. Put world-specific object IDs, ticks, physics, house rules and movements behind adapters; retain them in audit and source references but not in unconstrained subjective access. Run exactly the same cognitive entrypoint on a Lab provider and a *mock* alternate provider.

**Tests:** identical subject-access policy; sealed-room/line-of-sight correctness; world action deduplication; lost/denied action receipts; world epoch mismatch; restored state; altered environment without cognitive identity reset. **Pass:** cognition does not import direct Laboratory internals as authoritative world truth; current Lab functionality unchanged.

### D6. Corpus–Affectus–Noesis contract calibration

**Work:** establish three different layers: authoritative physical/body state -> fallible/typed bodily observation -> admitted first-person felt state. Allow direct feasible-action/capability input from Corpus to Noesis, plus motivation/appraisal from Affectus. Specify bidirectional regulation only where a real mechanism already exists or is separately justified. Audit need, salience and action-pressure pathways to avoid double counting.

**Tests:** fatigue competing with curiosity; motion physically impossible; sensor lag/noise; body-signal disagreement; affect lesion; same motor limit with differing affect. **Pass:** no new redundant physiological truth store or independent action selector; both feasibility and motivation demonstrably affect allowed downstream behavior when qualified.

### D7. Continuous operating cycle and autonomy *integration*, not automatic claims

**Work:** integrate existing runtime/wake, brain port, bounded action offers, verified consequence return, memory formation, policy updates and persisted handovers under the planned Gate 3/5/5A sequence. Model concurrent opportunities and preemption. The host owns scheduling and safety; Noesis originates/continues goals only to the degree actual tests demonstrate.

**Tests:** quiet interval without an external prompt; unexpected interruption; competing intentions; goal completion/abandonment; failed action and bounded replanning; two time scales; restart between action and feedback; host-initiated vs self-initiated separation. Run a no-LLM decision-policy control. **Pass:** source-attributed initiative and full effect-feedback loop demonstrated, with clearly labeled remaining autonomy gaps.

### D8. Conditional adoption of standalone Sensus and other donor mechanisms

**Work:** only after demonstrating a missing multichannel binding function, implement a reversible Sensus adapter with schema and attestation mapping; matched comparator uses the existing direct Laboratory perceptual path. Evaluate binding errors, false merges, conflicts, object re-identification and downstream consequences. No migration of its temporary object files into autobiography. Apply equivalent evidence gates to any genuinely separate Affectus donor.

**Pass:** information-matched tests show a specific gain or a clearly documented negative outcome; opt-in switch and rollback work. Otherwise Sensus retains status **standalone organ candidate**, and the six-organ target remains a functional specification without falsely claiming live donor adoption.

### D9. Distributed learning and procedural competence assessment

**Work:** inventory real learning rules in neural state, mnemonic retrieval/consolidation, affective modulation, perception and body-specific skills. Document which state persists, what changes it and which outcomes are verified. Establish a *procedural competency* benchmark separate from autobiographical description. Add missing mechanisms only through their existing Pretorius completion gates, not to fill a chart.

**Tests:** prior failure improves a later physical task with same renderer; matched neural lesion, affect lesion, mnemonic lesion, action-value controls; transfer to a related task; no fabricated expertise. **Pass:** differentiated evidence for learning mechanisms, not just a persuasive first-person claim of improvement.

### D10. Robot-replacement readiness (adapter proof, **not** deployment)

**Work:** implement a no-actuation fake Robot provider, validate the cross-environment time/source/epoch envelope, then evaluate hardware-in-the-loop observation under its own authorization. Prepare explicit safety risk analysis before any real actuation. Ensure robot installation cannot accidentally inherit the laboratory's authority or permissive toy physics.

**Pass:** lab-to-mock provider swap preserves canonical Pretorius state, subject perspective, provenance and audit while exposing only actually acquired provider-specific facts; no direct LLM motor authority.

### D11. Production designation and verification

**Work:** complete cold wheel/install, Windows/local target tests, schema/version migration safety, branch hygiene, exact-head CI, idempotent execution/recovery, renderer swap, organ ablations, longitudinal stability and human-facing evaluation plan. Update the README and main architecture document, preserve prior path as an explicitly tested rollback. Produce final status/known-gaps matrix for each organ and completion-plan gate.

**Pass:** six organs are **officially implemented as functional boundaries in the canonical runtime**, all required default paths conform to the North Star, the Lab provider runs the closed loop where qualified, no duplicate world/identity/decision authority exists, regression results are preserved, and optional/unvalidated mechanisms are prominently labeled. This does **not** mean Pretorius 1.0 or human-level realism is complete.

---

## 9. Minimum integration scenario suite (beyond single-event tracing)

Use pinned initial states and repeatable fixtures. Each scenario must output both the **engineering causal trace** and the **subject-only first-person trace**, with protected state omitted from the latter.

| Scenario | Why it matters | Minimum observation |
|---|---|---|
| A. Hidden vessel breaks behind subject | Acquired vs omniscient knowledge | Heard-but-not-seen event, grounded memory and uncertain recall |
| B. Apparatus problem during fatigue | Noesis/Affectus/Corpus competition | Physical limits and motives both contribute without duplicate policy |
| C. Contradictory book and instrument readings | Epistemic classes; hostile text | Source attribution, uncertainty, no privileged promotion |
| D. Uninterrupted ordinary lab work | Long-running cognitive cycle | Independent body/time updates, memory influence and continued intentions |
| E. Interrupted task with competing priority | Preemption and resumption | Explicit interruption, commitment continuity and safe resumption |
| F. Proposal denied by host | Agency seam and honest self-perception | Intent not recorded as successful effect; denial only if acquired |
| G. Crash after physical execution before feedback | Exactly-once/replay uncertainty | No duplicate physical action or manufactured memory |
| H. Same state, alternate renderer | Renderer dependence | State and permitted context fixed; report divergent language independently |
| I. Ipseity causal ablation | Beyond narrative filter | Downstream cognition/choice effects measured with information-matched conditions |
| J. Lab vs mocked robotic provider | Replaceability | Same brain identity and boundary; provider-specific perception/affordances |
| K. Two or more simultaneous perceptions | Sensus necessity | Compare direct observation and optional binding; measure false merges |
| L. Days of persistent operation | Stability and learning | Goals, memory, corrections, physiological and cognitive development survive restart |

**Measurement separation:** engineering conformance (pass/fail), causal contribution (matched/lesion), behavior (task outcomes), and human-realism validity (independent human comparisons) are four different result types. Never turn a passing unit test or an attractive diagram into a consciousness or human-fidelity claim.

---

## 10. PR discipline, ownership matrix and release checklist

### For every pull request

- Pin parent/head SHA and identify canonical target branch. Check open dependent PRs; **no merging without review**.
- State organ(s), exact mechanisms, authority boundary, runtime/default flag, migration impact and fallback.
- Link existing completion-plan gate and test evidence; preserve previous validated result sets and negative findings.
- Use smallest necessary code change; default to labels/docs/adapters over moving files; avoid changes to the canonical brain schema until necessary.
- Record unit/contract, integration, restart/crash, source-provenance, first-person no-bypass and regression tests as applicable.
- Provide before/after traces for behaviorally meaningful changes; explicitly state which results are **not** established.
- Do not change evaluation controls or promote experimental branches merely because the new vocabulary looks clean.

### Final implementation checklist

- [ ] Six organ definitions adopted in canonical architecture and indexed in README.
- [ ] All prior 40 functional categories audited with exact implementation and status; no missing authority.
- [ ] Every mutable state and physical effect has one authoritative owner.
- [ ] First-person experiential access is enforced for all subject pathways, **including internal reflection, encoding and recall**, not only external rendering.
- [ ] Hidden/neural/reflex computation remains possible without exposing privileged state.
- [ ] Doctor UPPB and Synthetic Ipseity have one coherent production admission contract.
- [ ] Memory formation, memory retrieval, world truth and source evidence remain distinct.
- [ ] Noesis is bounded; learning remains distributed; no second neural brain/action policy.
- [ ] Laboratory provider works through a replaceable environment/body adapter, with parity tests and receipts.
- [ ] Mock robot provider passes interface and provenance tests; real hardware not enabled by default.
- [ ] Autonomous/host-driven activities are explicitly distinguished in causal traces.
- [ ] Existing CI/default behavior, schema migrations, deterministic controls and restore tests remain valid.
- [ ] Independent reviewer signs off; any remaining deficits are in a tracked backlog.
- [ ] Final report distinguishes **six functional boundaries implemented** from **scientific efficacy demonstrated** and **Pretorius 1.0 complete**.

---

## 11. Research risks and explicit decision records needed

1. **IPSEITY-001: One admission authority.** Will Doctor UPPB own the canonical event construction while Synthetic Ipseity owns durable admission, or will one adapt the other's public contract? Resolve duplicate authority and evidence/access layering before D3. Retain first-person North Star either way.
2. **MEMORY-001: Store semantics.** Where exactly does first-person *acquired content* reside, and how does it link to protected objective evidence? Determine whether migration is necessary before changing schema.
3. **AFFECT-001: Affectus maturity.** Verify candidate code and donor readiness. Logical boundary is acceptable; no declaration of implemented independent organ without evidence.
4. **SENSUS-001: Adoption threshold.** Maintain standalone Sensus until multichannel need and controlled comparator justify integration.
5. **CORPUS-001: Physical truth.** Specify where simulated physiology, pose, feasibility and actual action receipts live, and how later robot source authority supersedes lab-specific assumptions without overwriting past experience.
6. **NOESIS-001: Single selector.** Define cognitive vs motor proposals, competing motivations and persistent goals. Do not let host action queues masquerade as self-originated planning.
7. **RUNTIME-001: Time.** Separate real UTC, monotonically ordered host events, laboratory simulation ticks, brain ticks and robot sensor timestamps. Define wall-time/world-time bridges deliberately.
8. **CAUSAL-001: Value of organ boundaries.** Preserve lesionable/switchable contribution where experimentally meaningful, but do not add expensive interfaces solely to make the code hierarchy resemble organs.
9. **ROBOT-001: Safety authority.** Define who can authorize sensing, movement and actuation; no robot controls until dedicated hardware safety review.

---

## 12. Grounding sources (reviewed 26 October 2026)

- **The Doctor Lives:** [`README.md`](https://github.com/Azimn/The-Doctor-Lives/blob/main/README.md), [`ARCHITECTURE_CONTRACT.md`](https://github.com/Azimn/The-Doctor-Lives/blob/main/ARCHITECTURE_CONTRACT.md), [`SUBJECTIVE_PERSPECTIVE_NORTH_STAR.md`](https://github.com/Azimn/The-Doctor-Lives/blob/main/SUBJECTIVE_PERSPECTIVE_NORTH_STAR.md), [`FIRST_PERSON_SUBJECT_INTERFACE_CONTRACT.md`](https://github.com/Azimn/The-Doctor-Lives/blob/main/FIRST_PERSON_SUBJECT_INTERFACE_CONTRACT.md), [`PHENOMENAL_PROJECTION_CONTRACT.md`](https://github.com/Azimn/The-Doctor-Lives/blob/main/PHENOMENAL_PROJECTION_CONTRACT.md), [`PRETORIUS_COMPLETION_PLAN.md`](https://github.com/Azimn/The-Doctor-Lives/blob/main/PRETORIUS_COMPLETION_PLAN.md), [`doctor_lives/ipseity_integration.py`](https://github.com/Azimn/The-Doctor-Lives/blob/main/doctor_lives/ipseity_integration.py), [`doctor_lives/home_motive_queue.py`](https://github.com/Azimn/The-Doctor-Lives/blob/main/doctor_lives/home_motive_queue.py).
- **Pretorius Laboratory:** [`README.md`](https://github.com/Azimn/Pretorius-Laboratory/blob/main/README.md), [`docs/ARCHITECTURE.md`](https://github.com/Azimn/Pretorius-Laboratory/blob/main/docs/ARCHITECTURE.md), [`pretorius_lab/subject_port.py`](https://github.com/Azimn/Pretorius-Laboratory/blob/main/pretorius_lab/subject_port.py), [`embodied_access.py`](https://github.com/Azimn/Pretorius-Laboratory/blob/main/pretorius_lab/embodied_access.py), [`daily_rhythm.py`](https://github.com/Azimn/Pretorius-Laboratory/blob/main/pretorius_lab/daily_rhythm.py).
- **Sensus:** [`README.md`](https://github.com/Azimn/Sensus-Communis-Artificialis/blob/main/README.md), [`docs/SPEC_v0.1.md`](https://github.com/Azimn/Sensus-Communis-Artificialis/blob/main/docs/SPEC_v0.1.md), [`docs/ADOPTION_GATES.md`](https://github.com/Azimn/Sensus-Communis-Artificialis/blob/main/docs/ADOPTION_GATES.md).
- **Synthetic Ipseity:** [`README.md`](https://github.com/Azimn/synthetic-ipseity/blob/main/README.md), [`docs/ORGAN_V0_2_INTEGRATION.md`](https://github.com/Azimn/synthetic-ipseity/blob/main/docs/ORGAN_V0_2_INTEGRATION.md).
- **Independent reviewer:** *Independent Architectural Review: Praetorius Six-Organ Reorganization*, 26 October 2026 (provided in conversation).

**Evidence disclaimer:** This document was compiled by reading repository source and documentation through GitHub access. It is an architectural plan, **not a fresh local test execution or repository modification**. Exact behavior and live branch/CI status must be reverified at D0 before implementation or final claims.

---

### Definition of completion

The reorganization is complete only when **one canonical Pretorius** exposes six clear functional organ boundaries in its production architecture; the first-person North Star is enforced across **every actual subject-accessible path**, including learned memories and later recollections; physical world/body authority is external and replaceable; the Lab provider operates through that boundary without regression; candidate organs remain honestly labeled where not yet integrated; and there are repeatable end-to-end tests proving this structure behaves coherently under interruption, conflicting signals and recovery.

**This is an implementation and integration milestone, not the endpoint of artificial-person research or the Pretorius 1.0 human-simulation program.**