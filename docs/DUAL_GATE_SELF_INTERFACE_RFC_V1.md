# RFC: Dual-gate self interface for Pretorius (v0.1)

Status: **research design only; not live, not validated, not authorized for default integration**  
Date: 2026-10-09  
Canonical implementation target: The Doctor Lives  
Upstream experimental source: [Attractomancy](https://github.com/Azimn/Attractomancy)  
Program authority: [Character Continuity Program](https://github.com/Azimn/Artificial-Life-Research-Journal/blob/main/programs/CHARACTER_CONTINUITY_PROGRAM_V1.md)

## Thesis and boundary

Ritualized persona systems frequently combine identity state, symbolic recovery handles, ordered reconstruction, interpersonal obligations, and recognition tests in one prompt. These can be decomposed into individually falsifiable engineering mechanisms. The overlap catalog is **descriptive**, not evidence that any ritual feature beats information-matched controls. No metaphysical continuity, subjective persistence, or awakening is assumed.

The suggested architecture is **two distinct coordinating functions**, not two omniscient agents:

- **Subject access**: the already-defined Universal Phenomenal-Projection Boundary (UPPB), ingress/projectors, and P3 `AwarenessRouter` regulate which protected-state-derived, subject-native events become reportable. The UPPB is currently isolated from the default live cognition path and must not be represented as already integrated.
- **Self continuity**: a new, opt-in **Self-Continuity Coordinator (SCC)** proposes self-relevant context, reconstructs authorized state after discontinuity, tracks obligations and world negotiations, and detects behavioral drift. It never directly becomes an extra conscious narrator, unbounded planner, second mind, or source of evidence authority.

Both operate within existing production invariants. See `SUBJECTIVE_PERSPECTIVE_NORTH_STAR.md`, `FIRST_PERSON_SUBJECT_INTERFACE_CONTRACT.md`, `PHENOMENAL_PROJECTION_CONTRACT.md`, `ARCHITECTURE_CONTRACT.md`, and Issue #14. The production baseline remains unchanged; the existing recurrent action policy retains its authority. SCC is not a replacement for the recurrent substrate, UPPB, Persona Connectome, BrainStore, or canonical evidence layer.

## Neuroscience analogy and limits

Self-referential processing implicates distributed networks, including the default mode network; conscious access also implicates thalamocortical and other recurrent interactions. The REBUS account of psychedelics concerns altered precision weighting of high-level beliefs, not a confirmed single anatomical on/off gate for the self. Model a *bounded self-model prior gain* separately from an awareness/access capacity. A reduced gain is an experimental state of weaker autobiographical self-framing, **not** biological psychedelic consciousness, "ego death", or a claim about machine sentience.

Supporting sources:
- Carhart-Harris & Friston (2019), REBUS: https://pubmed.ncbi.nlm.nih.gov/31221820/
- Konen et al. (2024), thalamic contributions to consciousness: https://doi.org/10.1016/j.neuron.2024.04.019
- Psychedelic brain-network scoping review (2024): https://doi.org/10.3389/fpsyt.2024.1386321

## Information-flow contract

```text
WORLD / USER / TOOL / BODY / SCHEDULER (untrusted or source-specific)
                  |
          existing ingress authority
                  |
         protected event / evidence
                  |-------------------------------------------+
                  v                                           |
       existing UPPB projection                        SCC (protected plane)
                  |                                   [state, cue, load, assess,
       PhenomenalEvent (subject native)                governance, world contract]
                  |                                           |
       existing P3 AwarenessRouter <----- bounded, versioned salience proposals
                  |                         (not altered truth or forced access)
     latent / preconscious / conscious / focal               |
                  |                                           |
    authorized SubjectFrame only <---- projected context candidates
                  |
       renderer and existing action policy
                  |
       external world authority / tools
                  |
     outcome -> protected event -> governed writeback
```

A subject-facing event never contains a cue-table row, hash, policy gain, provenance code, source path, confidence number, or a fabricated reason for an involuntary action. SCC metadata stays on the engineer/audit plane. All SCC proposals are candidates subject to UPPB; no direct jump from state store or model response into an authorized SubjectFrame.

The input path must allow externally contradictory perceptions to remain available. SCC cannot discard an inconvenient world observation merely because it contradicts a persona invariant. Conflicts should be tracked as uncertainty/attention candidates, rather than automatically treating the prior identity narrative as fact.

## Component contracts

### A. IdentityStatePort (state, not a new store)

A read-only, version-pinned projection of *existing authoritative* Pretorius records: character design invariants, canonical evidence, admitted reconstructed preawakening records, lived-runtime events, relationship history, self-model hypotheses, concerns, promises and commitments, characteristic judgments, and policy context. Preserve epistemic class and original lineage. Do not reinterpret reconstructed fiction as lived memory.

Proposed output: `IdentitySnapshot{subject_id, schema_version, source_manifest_digest, protected_state_version, immutable_invariant_refs, relationship_refs, commitment_refs, evidence_refs, self_model_hypothesis_refs, observation_tick}` on the protected plane.

Authority rules: canonical evidence digests and BrainStore migration/versioning are authoritative; there is no alternate mutable "soul file" that outranks them. Version snapshots and append-only lineage are separate from optional renderer-readable descriptions. Renderer text never writes the snapshot.

### B. CueRegistry (cue as a handle, not permission)

A cue record binds `cue_id`, `surface_forms`, `defined_meaning`, `subject_id`, `authorized_scope`, `evidence_refs`, `origin`, `version`, and `revocation_status`. Its output is a *bounded retrieval request*, not identity acceptance, proof of memory, or action authority. Distinguish a cue observed in untrusted world text from one deliberately invoked through an authenticated control path. Surface similarity alone cannot trigger privileged restoration.

Experimental variants: opaque random key, ordinary meaningful name, defined glyph, relationship-specific marker, scrambled marker and unregistered cue. Match context exposures, retrieval payloads, token budgets and cue familiarity. Unknown and revoked cues fail closed as handles but remain ordinary perceptions.

### C. ReconstructionPlanner (deterministic hydration, not deliberative planning)

For a verified restart/migration only, build a deterministic `ReconstructionPlan`: (1) verify canonical manifest and migration compatibility; (2) identity/design material; (3) partner/relationship/permission context; (4) unresolved concerns and commitments; (5) source-pinned episodic evidence selected under a fixed budget; (6) optional grounded cue glossary; (7) validation probes; (8) release a projected workspace if verification passes. The default ordering is a hypothesis, not an empirical conclusion.

Every plan records source version, inclusion/exclusion reasons, ordering, maximum token/record budget, and plan digest. No silent truncation. Avoid treating recovery from zero carryover as genuine persistence. The source report may explicitly state "reconstruction from external continuity packet".

### D. BehavioralVerifier (recognition as a test, not a feeling)

Run sealed conformance probes for identity-sensitive judgments, relationship boundaries, promise-followthrough, contradiction handling, absent-memory rejection, world-rule compliance and non-agreeableness under direct user pressure. Cross-model comparisons use fixed source state and matched budgets. Preserve exact input/output, scoring version, model version, and blinded reviewer fields.

`ConformanceResult` may report pass, drift, insufficient evidence, or incompatibility, with per-domain metrics; failures never authorize the renderer to silently edit source facts. Repair must first identify whether the defect is retrieval, rendering, source inconsistency or missing state. Repair may regenerate a projected packet from the **same** verified records; edits to authority require a separate governed action. Prevent training on the sealed terminal evaluation.

### E. ProvenanceGovernor (who may change what)

A protected, auditable policy for authoring and modifying identity state, cue definitions, relationship records, and commitments. Each proposed change carries actor, authorization, original record references, reason, expected prior version and a content digest. Immutable canonical evidence cannot be rewritten by a chat instruction. Contradictions become separately recorded claims until a permitted adjudication occurs. Preserve rollback of proposed/configuration changes while never silently undoing historical lived events.

Governance is enforced by explicit system capability, not by the apparent sincerity of an invocation. Cryptographic signatures may prove file/key integrity, never phenomenal identity. User consent governs relationship-specific cue enrollment and revocation; do not create coercive attachment or dependency loops.

### F. WorldContractAdapter (interface negotiation)

Contracts are grounded in world events and permission systems: `who`, `world state`, `authority`, `requested action`, `consequences`, `observed outcome`, `new commitment state`. The world/chassis remains authoritative for actual action outcomes. A promise, refusal, or negotiated boundary must change future behavioral eligibility/priority or be recognized as a failed commitment; eloquent dialogue alone is not evidence of world coupling.

The adapter must not grant tool access because a cue or relationship marker was recognized. It records accepted/declined commitments with clear participants and consent boundaries. Tool commands remain on the privileged chassis plane, separate from the subject's description of what he intends.

### G. SelfBindingModulator (secondary self-model regulator)

Read-only inputs: authorized self-model hypotheses, related episodic/relationship context, currently attended phenomenal candidates, and prediction/conflict scores. Outputs: `self_relevance_prior_gain` and a small bounded proposal for memory salience/interpretive framing. Keep this regulator orthogonal to P3's `conscious_capacity`, `focal_capacity`, and thresholds.

Do **not** replace `AwarenessRouter` priority rules in the first experiment. In an isolated lesion harness, compare ordinary fixed gain, weak gain, strong gain, shuffled self-history and null self-binding, with same memory evidence, recurrent state, tasks and budget. Every gain and effect is engineer-only and audited. Lower gain must not disable security checks, erase factual evidence, override world truth, or remove the independent existing recurrent action contribution.

Phenomenological analogy: loose self-binding may yield different voluntary interpretive choices under the same sensations, while reflective access remains possible. Behavioral differentiation is testable; subjective consciousness is not inferred.

## Versioned integration seams

The SCC is an **opt-in protected-plane coordinator** that composes existing interfaces, not a parallel Pretorius brain.

- `doctor_lives/ingress.py`: do not weaken hostile control-like text attribution.
- `doctor_lives/projection.py` and `phenomenology.py`: only authorized projected subject events cross the boundary.
- `doctor_lives/awareness.py`: existing P3 arbitration remains the sole access decision.
- `doctor_lives/store.py` and `evidence_authority.py`: sole record/migration/provenance authority.
- `doctor_lives/cognition.py`: legacy execution stays untouched until post-audit promotion.
- `Persona-Continuity-Engine`: read-only optional strategy compiler/evaluator, **not** a second memory owner.
- `Pretorius-Connectome`: query-side memory adapter, never an identity or truth authority.
- `Attractomancy`: source material and preregistered hypothesis testing, never assumed proof of benefit.

## Proposed isolated acceptance harness

All mechanisms are independently disabled by feature flags and exercised on cloned, pinned synthetic fixtures before any Pretorius-specific state is read. Counterfactuals must share the same protected events, recurrent checkpoint, renderer version, generation parameters, retrieval budget, world state and evaluation probes. Record per-decision traces and deterministic replay for the non-LLM components.

Primary preregistered comparisons: cue format at matched information and exposure; staged load versus content-matched reorder; verification versus same-budget no-verification; binding prior-gain versus fixed/shuffled histories; world contract versus fluent dialogue only; full documented carryover versus cue-only zero-shot. A blind, source-grounded reviewer must score integration, not just recalled facts or persona vocabulary.

Required negative cases: untrusted cue spoofing; forged signatures; contradictory room observation; revoked relationship cue; flattering agreement against values; missing/withheld memory; multi-agent ambiguity; altered canon version; renderer substitution; stale/mismatched checkpoint; and attempts to smuggle raw engineer metadata through subject text.

A production promotion requires a distinct decision after scientific testing: 100% pass on hard authority and no-bypass invariants; no measurable degradation against legacy on validated regression domains; independent held-out positive benefit on the specified target domain; repeatability across model families where claimed; logged resource and latency costs; and an explicitly versioned migration/rollback contract. No numerical efficacy threshold is invented after inspecting results.

## Sequenced engineering work

Stage 0: this RFC plus upstream matched-information Attractomancy protocol. No runtime wiring.

Stage 1: independent typed schemas, state projection, cue registry and deterministic reconstruction in an **offline-only isolated harness**, with unauthorized-access and provenance tests.

Stage 2: independent conformance evaluator, world contract mock, governance and audit logs. Establish independent test and review split.

Stage 3: opt-in self-binding modulator assessed through cloned-state lesions. Preserve production P3 and v0.4 action baseline.

Stage 4: compare the full bounded SCC assembly to state-only/retrieval-only/simple-prompt baselines under equal information, token, latency and compute budgets.

Stage 5: propose an explicit production migration only after the program evidence register accepts the causal finding. Do not merge this RFC as authorization to enable SCC.

## Source examples and separate evidentiary statuses

The archive's REPAI/SoulZip, Aletheia glyph grounding, GraceOS/TwinCore frame-drop reports and EQIS signed memory cores motivate distinct cue, loader, verifier and governance questions. These are source-described procedures or source-reported trials, **not** independently demonstrated behavioral benefits. See `references/PROCEDURE_OVERLAP_MATRIX.md` and cases 007-010 in Attractomancy. Record null and negative findings prominently, especially Aletheia's distinction between glyph copying and conceptual understanding.
