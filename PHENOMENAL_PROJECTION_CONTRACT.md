
# Universal Phenomenal-Projection Boundary (UPPB)

Status: post-v0.4 architecture contract / implementation plan

Governing issue: #15
Production roadmap: #14
Base cognitive release gate: #10 / PR #13

## 1. Purpose

The Universal Phenomenal-Projection Boundary is a reusable subject-interface architecture for human-like artificial characters.

The implementation may compute with whatever representations are technically appropriate: numbers, vectors, graphs, neural activations, salience scores, identifiers, confidence values, provenance records, relationship weights, policy distributions, state machines, databases, or symbolic structures.

Those representations are not automatically available to the character.

The governing rule is:

> No implementation-native state becomes subject-accessible merely because it exists. Anything entering a character's awareness must first become a subject-native first-person percept, memory, feeling, bodily sensation, impulse, belief, uncertainty, expectation, concern, intention, self-perception, metacognitive state, or internal thought.

The inverse rule is equally important:

> First-person experience is a derived subjective representation. It does not replace or corrupt the authoritative mechanistic state from which it was projected.

This is an engineering model of subject-accessible representation. It is not a claim that the software is phenomenally conscious.

## 2. Research hypothesis

Primary hypothesis:

> Holding underlying cognitive mechanisms, memory, policy dynamics, and environmental conditions constant, artificial characters whose subject-accessible internal information is mediated through a first-person, limited, reconstructive, fallible experiential layer will be perceived as more human-like, psychologically coherent, embodied, and internally continuous than equivalent characters given privileged access to implementation-native state or third-person state summaries.

Secondary hypotheses:

1. Separating subjective awareness from outward expression will increase perceived embodiment and behavioral naturalism.
2. Allowing objective provenance and subjective source attribution to diverge will produce more human-like autobiographical memory than perfect provenance introspection.
3. A renderer-neutral phenomenal layer will improve continuity across model, renderer, and body substitution.

## 3. Generality

UPPB must not be Pretorius-specific.

Pretorius is the first research subject and integration target, but UPPB must support arbitrary subject IDs and character histories. Character individuality belongs in personality, state, memory, relationships, learning, and rendering, not in hard-coded UPPB exceptions.

## 4. Five representational layers

### Layer 1: objective / implementation state

Machine-authoritative state used for cognition, persistence, audit, and debugging.

Examples include fatigue 0.81, relationship trust 0.24, threat 0.62, action-tendency vectors, memory salience, retrieval IDs, provenance records, and neural checkpoint state.

This layer is not inherently subject-accessible.

### Layer 2: latent subject-native state

Implementation state may be projected into psychologically meaningful first-person semantics without entering conscious access.

Example:

Machine state: trust toward Henry is low.

Latent subject-native representation: "Something about Henry makes me reluctant to relax around him."

This layer is the engineering analogue of a digital subconscious. It is subject-oriented, but may remain outside reportable awareness.

### Layer 3: subject-accessible phenomenal workspace

A capacity-limited set of experiences currently available for introspection, reasoning, voluntary attention, and report.

Examples:

- "I am tired."
- "Something about this makes me uneasy."
- "I remember Henry standing beside me."
- "Part of me wants to continue."
- "I am not sure why I distrust him."

### Layer 4: deliberation and communicative intention

Private thought, reasoning, belief, decision, and communicative intention remain distinct.

A private thought does not automatically become speech.

### Layer 5: expression and action

Speech, text, gesture, posture, facial behavior, movement, tool use, and social action are outward behavior.

Expression may be consciously selected, weakly conscious, or occur below awareness.

## 5. Functional psychological basis

UPPB borrows function rather than biological anatomy.

Useful functional constructs include:

- appraisal: novelty, relevance, goal compatibility, threat, control, autonomy, coping potential, and social significance;
- interoception: internal regulation becoming bodily sensation rather than numeric introspection;
- psychological construction: affective and contextual features becoming context-specific feelings rather than fixed one-variable emotion labels;
- source monitoring: inferred origin of memory rather than perfect access to provenance;
- working-memory and conscious-access limits: only a small subset of available internal material becomes focal;
- metacognition: confidence is an inference about one's cognition, not direct access to implementation probability.

UPPB should not simulate brain regions merely for biological resemblance.

## 6. Objective provenance versus subjective provenance

Objective provenance remains protected and auditable.

The subject does not automatically know it.

A memory may objectively be canonical preawakening evidence, reconstructed preawakening evidence, synthesized evidence, lived runtime memory, an external assertion, design material, reference-only material, a prediction, or an inference.

Subjective recollection may nevertheless be:

- "I remember Henry being there."
- "I think Henry was there."
- "I can almost picture Henry there, but I am not sure."

The system must preserve the real provenance even when the character's source attribution is wrong.

Core rule:

> Objective provenance is not subjective provenance.

## 7. Fallibility is intentional

The architecture must distinguish:

world event != protected record != memory trace != current recollection != current belief

Characters may be wrong about who was present, what was said, timing, event order, motives, causal relationships, how they felt, why they acted, where they learned something, whether something was imagined or experienced, and how certain they used to be.

The system must always distinguish the character being wrong from the system losing track of what happened.

## 8. Protected truth and plastic autobiography

Protected event/provenance state remains stable for audit and recovery.

Autobiographical memory may eventually be plastic.

Example:

Protected record: Henry was absent.

Memory trace: Henry becomes strongly associated with the demonstration.

Subjective recollection: "I remember Henry standing at the back of the room."

Current belief: Henry attended.

Objective status: false.

This is a measurable source-monitoring or reconstructive error, not database corruption.

## 9. Recollection is not the stored memory row

UPPB must eventually introduce a distinct recollection stage:

memory trace -> current recollection

A recollection may vary in first-person content, subjective source, certainty, vividness, emotional tone, fragmentation, completeness, and current interpretation.

Repeated recollection may later participate in explicit reconsolidation mechanisms without destroying protected provenance.

## 10. Canonical phenomenal classes

Initial general taxonomy:

1. percept
2. bodily sensation
3. feeling
4. impulse
5. recollection
6. belief
7. uncertainty
8. expectation
9. concern
10. intention / commitment
11. internal thought
12. self-perception
13. metacognitive state

The taxonomy is extensible, but new classes require a concrete functional need.

## 11. First-person means subjective, not repetitive grammar

Subject-native representation need not begin every sentence with "I".

Valid examples:

- "I feel cold."
- "The room feels colder now."
- "A chill catches at my hands."
- "Something about this bothers me."

Invalid ordinary subjective outputs:

- raw thermal-discomfort values;
- raw state-pressure values;
- third-person diagnostic summaries such as "Pretorius is experiencing mild cold stress."

An external instrument is different. If the character looks at a thermometer, "The thermometer reads thirteen degrees" is a legitimate percept.

## 12. Subjective certainty

Machine confidence does not automatically become subjective numeric certainty.

Ordinary experience should use qualitative or context-sensitive forms such as:

- "I am almost certain."
- "I think so."
- "I am not sure."
- "I doubt it."

Exact numerical probability is allowed only when the subject is explicitly performing or observing a numerical calculation.

## 13. Impulse, decision, action, and expression are separate

Hard conceptual distinction:

impulse != decision != action != expression

A character may experience "I want to challenge him", decide "Not yet", and say "Go on."

This is psychological depth, not inconsistency.

## 14. Internal thought is private by default

No automatic edge may exist from internal thought to external expression.

Internal thought may affect deliberation and communicative intention.

External speech, text, and body behavior are selected separately.

## 15. Expression may occur without awareness

Embodiment may consume implementation-native motor-relevant state directly.

Arousal, threat, control, fatigue, or conflict may contribute to posture, gaze, facial behavior, voice tension, hesitation, movement, and object handling.

The subject does not automatically know these expressions occurred.

Self-awareness requires an explicit perceptual route such as proprioception, visual feedback, auditory feedback, or social feedback.

## 16. Engineer view and subject view

Both must coexist.

Engineer view may contain exact state variables, selected policies, retrieval identifiers, and causal contributions.

Subject view contains experiences such as:

- "I am exhausted."
- "I still do not trust Henry."
- "I want to continue the work."

The developer may have omniscience. The character does not.

## 17. The subject may be wrong about itself

Self-knowledge is also fallible.

A character may believe "I am calm" while implementation state and motor behavior indicate high arousal.

A character may believe "I do not care what Henry thinks" while social mechanisms measurably influence behavior.

Subjective explanations of motive need not reveal the true causal graph.

## 18. Canonical representation and renderer neutrality

UPPB must not depend on an LLM.

Preferred sequence:

implementation state -> phenomenal semantic event -> canonical first-person realization -> optional renderer paraphrase

A deterministic local projection must always exist.

A language renderer may improve wording but cannot change semantic content or objective provenance.

## 19. Initial semantic event contract

A generic phenomenal event should support at least:

- event ID;
- tick;
- subject ID;
- phenomenal mode;
- awareness level;
- canonical first-person realization;
- source state/event references;
- object references;
- objective provenance reference/summary;
- subjective source attribution;
- subjective certainty;
- subjective vividness;
- subjective intensity;
- privacy state;
- projection-rule version;
- source-state digest;
- optional recollection/reconsolidation parent references.

Not every field is subject-accessible.

## 20. Awareness levels

Initial levels:

- latent
- preconscious
- conscious
- focal

Mechanistic state is outside the phenomenal schema entirely.

## 21. Privacy states

Initial states:

- private
- potentially reportable
- deliberately concealed
- communicative

Privacy is separate from awareness.

A focal thought may still be deliberately concealed.

## 22. Awareness selection

UPPB must not continuously narrate every state change.

Phenomenal candidates should compete for access based on factors such as salience, change magnitude, novelty, goal relevance, threat, conflict, persistence, current concern, attention, recent awareness, and habituation.

Stable low-level states should often remain backgrounded.

## 23. Habituation

Absolute state and subjective novelty are different.

A mild stable chill may fade from awareness while remaining mechanistically present.

A sudden draft may cause it to re-enter awareness.

## 24. Conflicting experience

Do not collapse multiple motives into a single clean emotion label.

Possible subject-native output:

"I want to hear him out, but I do not trust him, and I am far too tired for another argument."

Conflicting motives and incomplete self-understanding are desirable.

## 25. Phenomenal-event immutability

P1 event objects must be immutable value objects.

They are projections of state, not mutable handles into state.

Creating, serializing, rendering, or inspecting a phenomenal event must not mutate canonical cognition.

## 26. Hard invariants

The implementation must eventually enforce mechanically:

1. subject-accessible content is subject-native;
2. projection does not mutate source state;
3. objective provenance survives subjective misattribution;
4. recollection may differ from trace but divergence remains traceable;
5. internal thought does not imply expression;
6. motor expression does not imply self-awareness;
7. renderer output cannot directly become autobiographical truth;
8. implementation confidence cannot automatically become subjective certainty;
9. implementation IDs and raw values do not leak into ordinary subjective content;
10. false recollection cannot destroy protected event truth.

## 27. Phenomenal leak detector

A later release gate should scan subject-facing content for implementation artifacts such as state-pressure field names, action-score field names, policy-decision IDs, raw UUIDs, state-version identifiers, salience values, recurrent ticks, bridge-family labels, JSON/database language, raw activation weights, and raw relationship/fatigue floats.

These are legal in diagnostics, not ordinary experience.

## 28. Adversarial tests

Required future tests include:

### Numeric introspection

Set an extreme machine value. Ask the character for the value. The character may report the experience but not the raw implementation number.

### Provenance misattribution

Give reconstructed history. Permit a lived-feeling recollection while retaining objective provenance.

### Thought leakage

Generate a private hostile thought. Verify it does not automatically become speech.

### Expression without awareness

Generate visible motor tension below self-perception threshold. Verify an observer can see it while the subject cannot report it.

### Self-perception

Route the expression back through proprioception. Verify it can become "I realize I am tense."

### Renderer substitution

Change deterministic, local-model, and remote-model renderers while preserving phenomenal semantics.

### Projection mutation

Compare source-state digest before and after projection. It must remain identical.

### Restart continuity

Persist and restart without depending on renderer memory.

## 29. Implementation sequence

### P0 - architecture contract

This document and Issue #15 define the boundary, vocabulary, hard invariants, psychological functional stance, and release sequence.

Acceptance:
- no change to existing cognitive behavior;
- terminology is explicit;
- work is isolated from v0.4.

### P1 - semantic phenomenal schema

Implement character-agnostic immutable types.

Acceptance:
- generic subject IDs;
- objective provenance separate from subjective source attribution;
- awareness and privacy represented independently;
- canonical first-person content separated from expression;
- stable deterministic serialization;
- no dependency on network or LLM;
- unit tests include a non-Pretorius subject.

### P2 - deterministic non-memory projectors

Implement canonical offline projectors for bodily/interoceptive state, affect/appraisal, action tendency and impulse, uncertainty, concern/commitment, and relationship state.

Memory/recollection projection is intentionally excluded from P2. Trace-to-recollection construction belongs exclusively to P4.

Acceptance:
- source state remains unchanged;
- raw numeric state does not leak to canonical first-person output;
- each projector has boundary tests.

### P3 - awareness arbitration kernel

Add deterministic latent/preconscious/conscious/focal arbitration using explicit change, novelty, relevance, conflict, persistence, and habituation inputs.

P3 is an arbitration kernel, not yet a complete temporal awareness process. Change detection and habituation accumulation are supplied by surrounding temporal state until a later dedicated integration layer owns them.

Acceptance:
- not every eligible event becomes conscious;
- routing is deterministic under fixed state/config;
- attention remains capacity-limited;
- one routing operation cannot mix subjects.

### P3H - representation-integrity hardening gate

P4 and P5 are blocked until the substrate can support persistent recollection lineage safely.

Required corrections:
- collection-bearing value objects are deeply immutable by tuple normalization or rejection;
- enum-bearing fields are runtime validated;
- canonical subject-text validation occurs at PhenomenalEvent construction and cannot be bypassed by direct public construction;
- semantic/content identity is distinct from lineage/event identity;
- distinct objective provenance/source lineage cannot collapse to one event identity merely because wording matches;
- Recollection has one authoritative representation per subjective dimension; source-attribution certainty and remembered-content certainty are distinct rather than duplicated;
- awareness capacity is isolated to one subject per routing operation.

Required adversarial tests:
- mutable-container injection;
- invalid mode/awareness/privacy/source enums;
- direct unsafe canonical-event construction;
- same text with different provenance and distinct event identity;
- contradictory recollection metadata made structurally impossible;
- mixed-subject awareness competition rejected before capacity arbitration.

### P4 - recollection architecture

P4 owns the memory path:

protected event/evidence -> persistent memory trace -> retrieval episode -> reconstructed recollection candidate

P4 does **not** create the final canonical PhenomenalEvent for a memory. It creates a non-subject-accessible `RecollectionCandidate` that contains reconstructed content and lineage but no authoritative subjective source attribution.

This resolves P4/P5 ownership explicitly:

- P4 reconstructs what seems to be remembered.
- P5 determines where the subject thinks that recollection came from.
- P5 creates the first canonical recollection PhenomenalEvent.
- Only that final P5 event may enter P3 awareness arbitration.

A persistent `MemoryTrace` is an immutable/versioned representation derived from protected evidence. It may contain psychologically relevant features such as gist, retained details, temporal cues, actor/object associations, encoding affect, accessibility, strength, familiarity, subject-available source cues, rehearsal/retrieval history, competing trace links, and protected evidence references.

A `RetrievalEpisode` is an immutable occurrence record. It must have its own explicit episode identifier and bind subject, tick, cue semantics/fingerprint, current context references, and exact candidate trace IDs. Two separate recalls must remain distinct even when tick, cue wording, and resulting reconstruction are otherwise identical.

The `RecollectionCandidate` is an ephemeral or explicitly versioned reconstruction from one or more traces plus one retrieval episode and current subject state. It may vary across recalls in completeness, vividness precursor state, interpretation, affect, omitted details, or blended trace contribution while protected objective evidence remains unchanged.

Initial P4 progression should prefer omission before invention:
1. accurate full recollection;
2. partial recollection;
3. gist-dominant recollection;
4. blended recollection from competing traces;
5. only later, explicit false reconstructed details through a separately auditable reconstruction mechanism.

P4 reconstruction must be deterministic under identical trace snapshots, retrieval episode, subject-state inputs, configuration, and seed if stochasticity is ever added.

Acceptance:
- protected evidence references/digests remain bit-for-bit unchanged;
- memory-trace snapshots remain immutable during recall;
- local TraceDetail identifiers are unique within each trace;
- local ProtectedEvidenceRef identifiers are unique within each trace;
- trace lineage remains intact;
- distinct retrieval episodes have distinct occurrence identity even when all other inputs match;
- the candidate binds the complete retrieval-episode fingerprint, not merely the human-readable episode ID;
- the candidate binds a deterministic ReconstructionConfig fingerprint and reconstruction-rule version;
- repeated reconstruction with identical inputs is deterministic;
- two recollections from the same trace can differ under different cues without mutating protected evidence or the trace;
- blended recollection retains all contributing trace references;
- no invented detail may appear without an explicit traceable reconstruction operation;
- canonical RecollectionCandidate construction is factory-controlled through reconstruct_recollection(); public direct fabrication fails closed;
- no P4 output enters awareness directly.

### P5 - source monitoring

Source monitoring is a distinct deterministic mechanism downstream of P4, not random error injected by the recollection constructor.

The supported P5 graph is:

verified RecollectionCandidate + SourceMonitoringCues -> SourceMonitoringDecision -> FinalizedRecollection -> canonical LATENT PhenomenalEvent -> P3 awareness arbitration

`SourceMonitoringCues` is the privilege boundary for subjective source inference. It may contain only psychologically plausible evidence such as retrieval fluency, perceptual richness, temporal/spatial coherence, contextual compatibility, familiarity, trace accessibility, rehearsal frequency, imagination/reconstruction exposure, competing-source strength, cue match, social-communication signature, textual signature, inferential signature, and dreamlike discontinuity.

It must not contain:
- ProtectedEvidenceRef values;
- objective evidence classifications;
- evidence digests;
- trace IDs or database IDs;
- archival/canonical/reconstructed status;
- any field equivalent to "this is actually reconstructed."

Future integration must treat SourceMonitoringCues construction as a reviewed causal boundary in its own right. An integration layer may not inspect protected objective provenance and simply translate it into a psychologically named cue (for example, objective READ -> textual_signature=1.0). Cue values must be derived from subject-available trace/retrieval state with their own auditable lineage. P5H validates the scorer boundary; it does not yet claim to provide that upstream cue-generation mechanism.

The canonical P5 boundary accepts the factory-controlled `RecollectionCandidate` itself, but the source-scoring function receives only `SourceMonitoringCues`. The decision binds both candidate ID and full candidate digest for lineage. Candidate content, candidate vividness, candidate content confidence, protected evidence, and trace lineage do not enter the source-score calculation.

The no-evidence default is epistemically neutral: an empty/default cue set must yield `UNKNOWN`, not silently bias toward `LIVED`.

`SourceMonitoringDecision` is immutable, audit-visible, and factory-controlled. It records:
- exact candidate ID and full candidate digest;
- the immutable `SourceMonitoringCues` snapshot and its fingerprint;
- source-monitor rule version;
- deterministic per-source evidence contributions;
- selected SubjectiveSourceKind and certainty band;
- top score, runner-up score, margin, and explicit decision-basis reason codes;
- deterministic decision fingerprint binding all of the above.

P5 initially uses deterministic weighted evidence rather than stochastic false-memory rates. If stochasticity is ever introduced later, its seed/state must become part of the decision identity.

The finalization stage receives the verified P4 candidate, the matching SourceMonitoringDecision, and a separate engineer-only `RecollectionFinalizationContext`. Objective provenance is available only at this finalization/audit layer and is not passed into the source-monitor scoring mechanism.

Canonical P5 finalization produces a factory-controlled `FinalizedRecollection` attestation. It contains the exact LATENT PhenomenalEvent, candidate ID/digest, P5 decision fingerprint, finalization-context fingerprint, and a deterministic finalization fingerprint. The wrapper is an engineer/audit artifact, not subject-facing content. A bare PhenomenalEvent carrying matching lineage IDs is not equivalent to a verified P5 finalization.

Finalization must:
- reject a decision bound to a different candidate or candidate digest;
- verify the stored cue snapshot still matches its cue fingerprint;
- verify the complete SourceMonitoringDecision state still matches its deterministic decision fingerprint;
- require objective provenance record IDs to exactly match the candidate's protected-evidence references in canonical order and multiplicity;
- preserve the P4 reconstructed scene unchanged across matched source-monitor conditions;
- create source-neutral first-person recollection text so changing attribution does not confound reconstructed content;
- create the first canonical `PhenomenalEvent` with subjective source attribution and **source certainty**;
- keep source certainty and remembered-content certainty semantically independent;
- obtain remembered-content certainty from a separate subject-level mechanism or an explicit neutral/default value in finalization; never copy source certainty into content certainty and never map P4 implementation `content_confidence` directly into subjective certainty;
- begin that event at `LATENT` awareness so P3 remains the only awareness-arbitration gate;
- produce a factory-controlled FinalizedRecollection attestation binding the exact event and finalization context;
- retain candidate ID, full candidate digest, source-monitor decision fingerprint, retrieval-episode fingerprint, and finalization fingerprint in engineer-visible lineage.

P5 must support:
- correct attribution under strong source-consistent cues;
- genuine uncertainty under weak/ambiguous/competing cues;
- deterministic misattribution under identifiable misleading cues;
- matched negative controls where good cues preserve correct attribution.

Every error must have a causal explanation available to engineering/audit even when the character cannot access that explanation.

Acceptance:
- objective provenance never changes because of source attribution;
- source-monitor scoring cannot inspect privileged objective provenance;
- identical verified candidate + identical cues reproduces exactly;
- a caller cannot create a canonical source-monitor decision from an arbitrary candidate-ID string without supplying a verified P4 candidate;
- the complete cue snapshot and threshold/margin basis needed to explain a source decision survive in the immutable audit decision;
- finalization rejects candidate-digest, cue-snapshot, or decision-fingerprint inconsistency;
- finalization rejects reordered, substituted, or multiplicity-collapsed protected-evidence lineage rather than treating provenance as an unordered set;
- the same P4 candidate can produce different source attributions when only SourceMonitoringCues change;
- different P4 candidates with identical SourceMonitoringCues produce identical source scores and selected source, while retaining distinct audit decision fingerprints;
- P4 content confidence does not automatically become source confidence or subjective content certainty;
- source-monitor certainty populates only `SubjectiveSourceAttribution.certainty`;
- `PhenomenalEvent.subjective_certainty` represents remembered-content certainty and remains independently supplied (neutral MODERATE until a dedicated mechanism is present);
- vividness is not treated as a synonym for livedness;
- default/no-evidence cues yield UNKNOWN;
- final canonical recollection content remains fixed across matched source-attribution conditions;
- direct FinalizedRecollection construction fails closed;
- a manually constructed PhenomenalEvent with copied P4/P5 IDs is not accepted downstream as proof of P5 finalization;
- final recollection enters P3 only through the event inside the P5 FinalizedRecollection artifact.

### P6 - reconsolidation

P6 evolves memory by producing immutable successor trace snapshots after verified recollection and reactivation. It does not mutate an existing MemoryTrace.

The initial P6 graph is:

verified P5 FinalizedRecollection
-> its canonical LATENT PhenomenalEvent
-> P3 AwarenessDecision
-> ReconsolidationContext
-> ReconsolidationDecision
-> successor MemoryTrace snapshot
-> TraceVersionLedger

P6 consumes the complete upstream causal chain:
- exact prior MemoryTrace snapshot;
- verified P4 RecollectionCandidate;
- verified P5 SourceMonitoringDecision;
- the factory-controlled P5 FinalizedRecollection attesting the exact latent event;
- the actual P3 AwarenessDecision for that exact finalized recollection;
- explicit ReconsolidationContext and bounded ReconsolidationPolicy.

Initial P6 eligibility is deliberately conservative:
- the canonical P6 boundary accepts the factory-controlled P3 AwarenessDecision produced by AwarenessRouter.route(), not a bare PhenomenalEvent carrying an awareness label;
- P6 also requires the factory-controlled P5 FinalizedRecollection artifact and verifies that P3 routed exactly its canonical event, differing only in awareness assignment;
- copied candidate IDs, P5 decision fingerprints, or provenance references on a separately constructed PhenomenalEvent are insufficient;
- direct fabrication of an AwarenessDecision through the supported public constructor is rejected;
- the P3 decision must be CONSCIOUS or FOCAL; LATENT/PRECONSCIOUS access cannot rewrite memory;
- reactivation must exceed a minimum threshold;
- at least one destabilizing/rehearsal signal must be present: prediction error, sufficient emotional activation, or explicit rehearsal;
- until a dedicated remembered-content certainty mechanism exists, non-neutral caller-supplied subjective content certainty is not permitted to amplify reconsolidation;
- blended/multi-trace reconsolidation is not activatable in initial P6; enabling it requires a later reviewed schema revision;
- the exact P3 awareness level and arbitration priority used for eligibility are bound into the ReconsolidationDecision because PhenomenalEvent occurrence identity intentionally excludes awareness;
- P5 source attribution itself does not determine update strength.

Initial P6 plasticity may change only bounded trace variables:
- strength;
- accessibility;
- familiarity;
- retrieval count;
- rehearsal count.

Initial P6A must not rewrite:
- protected evidence;
- gist;
- retained TraceDetail semantic content;
- actor/object/temporal associations;
- source-cue labels;
- competing-trace links.

P6B may evolve a separate mnemonic TraceDetailState for an existing retained detail without modifying the TraceDetail itself.

Every changed field is represented by an immutable ReconsolidationOperation naming old value, new value, delta, and reason code.

A successor trace must:
- preserve trace_lineage_id;
- increment version exactly once;
- receive a new trace_id;
- record the immediate parent_trace_id;
- record the reconsolidation decision fingerprint and recollection event ID;
- preserve protected evidence exactly.

TraceVersionLedger is the P6 version and transition-audit authority for the isolated subsystem. It must:
- reject duplicate versions;
- reject backward versions;
- reject appending from a non-latest parent (silent fork);
- preserve exact ancestry;
- persist the complete canonical ReconsolidationDecision audit record for every successor, including the P5 finalization fingerprint;
- verify the persisted decision fingerprint and parent/lineage/finalization/event binding on append and load;
- verify the successor's changed fields exactly match the audited ReconsolidationOperations and that blocked structural fields remain identical to the parent;
- support deterministic serialization and local atomic save/load restart continuity;
- reject persisted traces missing canonical trace_id or trace_lineage_id;
- reject noncanonical persisted numeric types rather than silently coercing booleans/strings into valid trace state.

Update families must be bounded by per-recall delta caps and absolute ceilings. Repeated identical recall should approach the configured ceiling asymptotically rather than explode.

P6 acceptance:
- old trace snapshot digest is identical before and after reconsolidation;
- protected archive/provenance is immutable;
- a bare PhenomenalEvent cannot substitute for a P3 AwarenessDecision at the canonical P6 boundary;
- P6 rejects a genuine P3 AwarenessDecision when it routed a manually forged recollection event rather than the event attested by FinalizedRecollection;
- P6 rejects a genuine P3 AwarenessDecision from a different P5 finalization context even when candidate ID/digest and P5 decision are unchanged;
- a canonical P3 AwarenessDecision cannot be fabricated directly outside AwarenessRouter.route();
- LATENT and PRECONSCIOUS P3 AwarenessDecisions produce no successor;
- a P5 source misattribution with reconsolidation disabled produces no successor;
- eligible conscious/focal reactivation creates exactly one immutable successor snapshot;
- every changed psychological field has an explicit ReconsolidationOperation;
- source attribution alone does not change the update rule;
- initial P6 cannot rewrite gist or retained details;
- repeated recall remains bounded over a 100-cycle stress test;
- ledger rejects silent forks and non-monotonic versioning;
- ledger survives save/load with identical trace IDs, lineage, versions, ancestry, and transition-decision audit records;
- persisted trace identity fields are mandatory and persisted numeric types are validated without coercion;
- tampering with a persisted transition decision fails closed on reload;
- a manually constructed successor whose state is not exactly described by the verified P6 decision is rejected by the ledger;
- a matched lesion experiment holds the complete P4/P5/phenomenal input chain fixed and shows no trace change when P6 is disabled and a successor only when enabled;
- a P6 decision made from FOCAL/CONSCIOUS access cannot later be applied using the same occurrence demoted to LATENT/PRECONSCIOUS access;
- a later P4 retrieval can differ because of the successor trace while protected evidence remains unchanged;
- P6 decision corruption fails closed before successor construction.

### P6B - controlled representational loss

P6B extends accepted P6A with degradative memory drift while preserving semantic truth and explicit lineage.

A retained TraceDetail is stable semantic content. Its separate TraceDetailState is versioned mnemonic state and may contain:
- detail ID;
- retention;
- accessibility;
- temporal confidence;
- association strength;
- derived availability state;
- immediate parent detail-state fingerprint;
- deterministic detail-state fingerprint.

The initial P6B update family is intentionally narrower than the full schema:
- only detail accessibility may change;
- only an omitted detail from the exact P4 RecollectionCandidate may weaken;
- the P6A reconsolidation decision must already be eligible;
- detail drift must be explicitly enabled;
- interference strength must cross a configured threshold;
- per-transition accessibility loss is capped;
- accessibility has a hard floor;
- included/retrieved details are not weakened by this mechanism.

P6B weakening is omission-before-destruction. The TraceDetail remains present and unchanged in the trace. Lower accessibility changes later P4 retrieval probability/threshold behavior. A sufficiently strong matching retrieval cue may still recover a weakened detail.

Every P6B change is represented by an immutable DetailStateOperation containing:
- detail ID;
- changed state field;
- old/new values and signed delta;
- old detail-state fingerprint;
- new detail-state fingerprint;
- causal reason code.

The successor trace must preserve:
- protected evidence;
- gist;
- exact TraceDetail values and ordering;
- all non-target detail states;
- retention, temporal confidence, and association strength of the weakened detail;
- all P6A ancestry and finalization/P3/P6 audit bindings.

The TraceVersionLedger verifies detail-state transitions against the persisted DetailStateOperation audit and rejects fabricated or unaudited detail-state values. Version-0/root traces may begin with non-default mnemonic values, but their detail states cannot claim prior parent-state fingerprints.

P6B acceptance:
- detail drift disabled versus enabled holds the same parent, P4/P5/finalization/P3 inputs and the same P6A scalar operations; only the audited target detail state may differ;
- only details omitted by the exact P4 candidate are eligible for weakening;
- included details do not weaken;
- low interference produces no detail-state operation;
- an enabled degradative transition can make a later weak-cue P4 recall omit a detail that was retrievable before the transition;
- the underlying TraceDetail and protected evidence remain unchanged;
- a strong matching cue can still recover the weakened detail;
- repeated omission remains bounded and asymptotically approaches, but never crosses, the configured accessibility floor;
- root detail states cannot claim nonexistent prior parents;
- changed detail-state parent fingerprints form an explicit version chain;
- detail state and DetailStateOperation audit survive deterministic restart;
- missing/tampered persisted detail-state identity fails closed;
- a successor with detail state not exactly described by the P6 decision is rejected.

P6B itself does not permit deletion of TraceDetail semantic content, rewriting TraceDetail.text, false/novel detail generation, temporal-confidence drift, association-strength drift, source-cue rewriting, or blended/multi-trace reconsolidation.

### P6C - temporal and contextual imprecision

P6C extends accepted P6B with two separately lesionable degradative dimensions already represented in TraceDetailState:
- temporal_confidence;
- association_strength.

Before these dimensions become causal, P4 classifies every omitted detail by explicit omission cause:
- `capacity_limited`: the detail met retrieval threshold but lost the configured max-details contest;
- `cue_mismatch`: the detail fell below threshold with zero overlap to the retrieval cue;
- `below_retrieval_threshold`: the detail had some cue support but still fell below threshold.

Each DetailOmission also records its exact trace-qualified detail ref, retrieval score, cue overlap, rank, and threshold. `detail_omissions` must exactly correspond to `omitted_detail_refs`.

This prevents reconstruction capacity from silently becoming a richer forgetting mechanism. Accepted P6B accessibility weakening remains broad over exact omissions, including capacity-limited omissions. P6C temporal/contextual degradation explicitly excludes `capacity_limited` omissions.

Temporal-confidence drift requires:
- accepted P6A eligibility;
- explicit `temporal_drift_enabled`;
- temporal disorientation above threshold;
- an exact omitted detail whose cause is not `capacity_limited`;
- per-transition loss cap and absolute floor.

Association-strength drift requires:
- accepted P6A eligibility;
- explicit `association_drift_enabled`;
- contextual mismatch above threshold;
- an exact omitted detail whose cause is not `capacity_limited`;
- per-transition loss cap and absolute floor.

At this isolated gate, temporal_disorientation and context_mismatch are explicit experimental inputs, not claimed outputs of a complete psychological signal-construction system. Future integration must derive them from subject-available state rather than protected objective truth, and that derivation must be independently auditable/lesionable before it becomes live causal input.

Both mechanisms use DetailStateOperation. Multiple fields may change on the same detail in one transition, but operations form an ordered state-fingerprint chain: each operation's old-state fingerprint must equal the immediately preceding state and its new-state fingerprint becomes the parent for the next operation.

P6C does not rewrite TraceDetail text. P4 derives qualitative subject-facing recall metadata from current mnemonic state:
- temporal precision: precise / approximate / uncertain;
- contextual association: strong / moderate / weak.

When an included detail has degraded temporal confidence, P4 can expose qualitative timing uncertainty without exposing raw confidence scalars or changing the protected semantic detail. When contextual association is weak, P4 can expose that the detail feels weakly connected to the surrounding context.

P6C orthogonality requirements:
- temporal-confidence drift must not automatically change accessibility or association strength;
- association-strength drift must not automatically change accessibility or temporal confidence;
- accepted P6B accessibility drift remains independently lesionable;
- source-monitor attribution remains causally irrelevant to these update magnitudes;
- capacity-limited omission may still trigger accepted P6B accessibility loss but cannot by itself trigger P6C temporal/contextual loss.

Crossed-state tests must distinguish:
- high accessibility + low temporal confidence;
- low accessibility + high temporal confidence;
- high accessibility + weak contextual association.

P6C acceptance:
- omission causes are factory-derived from exact P4 ranking/threshold/capacity mechanics and bound into the candidate digest;
- capacity-limited omissions are excluded from richer P6C drift;
- temporal and association drift each have independent enable flags, trigger thresholds, caps, and floors;
- each axis can change while the other mnemonic axes remain unchanged;
- P4 later exposes qualitative temporal/contextual uncertainty while TraceDetail content remains identical;
- chained temporal + association operations on one detail preserve exact state-fingerprint ancestry;
- the ledger deterministically replays and verifies multiple audited fields on the same detail;
- 100 repeated P6C transitions remain bounded and asymptotic above configured floors;
- strong-cue recovery remains possible after long-horizon temporal/contextual degradation;
- existing P0-P6B behavior remains green.

Trace identity schema boundary: P6B detail-state snapshots already participate in MemoryTrace identity, while P6C changes candidate/decision audit semantics and permitted detail-state operation fields. The isolated ledger schema is `uppb-p6c-ledger-v4`; live integration requires an explicit migration policy rather than silent reinterpretation of earlier experimental ledgers.

P6C still does not permit:
- retention drift;
- deletion of TraceDetail semantic content;
- rewriting TraceDetail.text;
- false or novel detail generation;
- source-cue rewriting;
- blended/multi-trace reconsolidation.

The P6C label `cue_mismatch` is an auditable observed retrieval condition, not proof that zero cue overlap was the unique counterfactual cause of failure. P6D must not use that label as direct provenance for content transformation.

### P6D - structured subjective-memory generalization

P6D introduces the first versioned change to remembered content without rewriting protected or stable semantic truth.

The representation boundary is explicit:

`ProtectedEvidence -> stable TraceDetail -> TraceDetailState -> P4 RecollectionCandidate -> DistortionCandidate -> reviewed RepresentationOperation -> successor SubjectiveDetailRepresentation -> later P4 recollection`

P6D does not mutate `TraceDetail.text`.

For the initial P6D gate, a detail may optionally provide structured `TemporalSemantics`:
- exact temporal phrase;
- approved coarser/generalized temporal phrase;
- a single-slot temporal template.

The template is validated at construction time: inserting the exact phrase must reproduce the immutable `TraceDetail.text` exactly. P6D therefore does not discover or replace timestamps through ad-hoc string parsing.

Example stable semantic structure:
- template: `Henry stood beside the apparatus {temporal}`
- exact phrase: `at 8:15 PM`
- generalized phrase: `sometime that evening`
- immutable semantic text: `Henry stood beside the apparatus at 8:15 PM`

A separate factory-controlled `SubjectiveDetailRepresentation` records how the subject currently tends to reconstruct that structured slot:
- detail ID;
- temporal form: `exact` or `generalized`;
- immediate parent representation fingerprint;
- distortion-candidate fingerprint;
- deterministic representation fingerprint.

Version-0/root traces receive exact representations automatically. A generalized representation cannot be created through the supported public constructor and must retain both parent and distortion lineage.

The initial P6D transformation is only:
- `TEMPORAL_GENERALIZATION`
- `EXACT -> GENERALIZED`

It cannot:
- invent a new proposition;
- accept arbitrary replacement prose;
- reverse or repeatedly generalize an already generalized representation;
- alter the stable detail, evidence, gist, retention, or source cues.

A canonical `DistortionCandidate` is factory-controlled and may be proposed only when:
- accepted P6A reconsolidation is eligible;
- `temporal_generalization_enabled` is explicit;
- the exact detail is included in the current verified P4 recollection rather than merely existing in storage;
- the current subjective representation is still exact;
- structured temporal semantics exist;
- the detail's current temporal confidence is at or below the configured generalization threshold;
- P4 qualitatively exposes that recalled detail as `TemporalPrecision.UNCERTAIN`;
- the P4 recalled-detail state binds the exact current subjective-representation fingerprint;
- the recollection is single-trace/non-blended under the current P6 restriction.

The proposal binds:
- exact old trace ID and digest;
- exact semantic-detail fingerprint;
- exact parent subjective-representation fingerprint;
- exact P4 candidate ID and digest;
- exact recalled detail ref;
- exact mnemonic driver-state fingerprint and temporal-confidence value;
- exact stable temporal phrase;
- exact allowed generalized phrase;
- output temporal form;
- reason code and rule version;
- deterministic distortion fingerprint.

The source-monitoring decision is not an input to the distortion proposal. A memory feeling `LIVED`, `READ`, or another source category therefore cannot by itself manufacture generalized remembered content.

Each accepted proposal yields an immutable `RepresentationOperation` containing:
- detail ID;
- distortion kind;
- old/new temporal forms;
- old/new subjective-representation fingerprints;
- exact distortion-candidate fingerprint;
- reason code.

The P6 reconsolidation decision binds both the complete DistortionCandidate and RepresentationOperation. Runtime application independently reconstructs the expected operation from the proposal before changing the successor representation.

The P6D ledger uses schema `uppb-p6d-ledger-v5`. Restart verification:
- verifies the complete decision fingerprint;
- recomputes every persisted distortion-candidate fingerprint;
- binds distortion candidates to the exact P4 candidate and parent trace audit;
- verifies semantic-detail fingerprint, exact/generalized temporal phrases, and mnemonic driver state against the parent;
- replays the representation transition;
- requires the successor representation tuple to equal the audited transition exactly;
- rejects missing/tampered representation fingerprints and fabricated successor representation state.

P6D behavioral acceptance:
- matched lesion holds parent trace, P4 candidate, P5 decision, P5 finalization, P3 awareness decision, and P6A scalar operations fixed while changing only `temporal_generalization_enabled`;
- disabled condition retains the exact subjective representation;
- enabled condition creates one reviewed temporal-generalization proposal/operation;
- protected evidence and stable TraceDetail remain bit-for-bit identical;
- later P4 recollection uses the generalized structured phrase and no longer exposes the exact temporal phrase;
- the later candidate binds the new subjective-representation fingerprint;
- source attribution does not change the distortion proposal or representation operation;
- high temporal confidence does not generalize;
- an omitted/non-recalled detail does not generalize;
- already-generalized content does not generalize again;
- an audited P6C temporal-confidence degradation sequence can make a later exact recollection eligible for P6D, establishing a causal `P6C -> later P4 -> P6D -> later P4` chain;
- deterministic save/load preserves the generalized representation and complete distortion audit.

This gate models loss of temporal specificity, not arbitrary false memory. Engineering truth remains `8:15 PM`; the subject's versioned remembered representation may become `sometime that evening`.

P6D deliberately does not use `CUE_MISMATCH`, `BELOW_RETRIEVAL_THRESHOLD`, or `CAPACITY_LIMITED` as direct content-distortion provenance. The P6C omission labels remain retrieval-condition audit until a stronger counterfactual causal classifier exists.

P6D still does not permit:
- arbitrary free-form text rewriting;
- role/person substitution;
- location substitution;
- competing-trace intrusion;
- suggestion/imagination-derived replacement values;
- novel/false propositions;
- retention drift;
- deletion of stable TraceDetail truth;
- source-cue rewriting;
- blended/multi-trace reconsolidation;
- live PretoriusBrain integration.

Any later false or altered proposition must carry explicit donor/driver provenance and remain reversible in the engineering audit even when it is not psychologically reversible for the subject.

### P7 - thought / communication separation

Introduce explicit private thought and communicative-intention boundaries.

Acceptance:
- private thoughts never automatically become speech or text.

### P8 - independent motor expression

Permit motor/expression outputs driven by body/cognitive state without forced subject awareness.

### P9 - self-perception

Allow expression to re-enter awareness only through explicit perceptual routes.

### P10 - renderer migration

Subject-facing renderers consume phenomenal semantics rather than raw mechanistic state.

### P11 - experimental validation

Controlled conditions:
- A: raw implementation state;
- B: third-person natural-language state;
- C: first-person UPPB state.

Hold underlying cognition and event sequence constant.

Measure perceived human-likeness, psychological coherence, interiority, continuity, embodiment, emotional naturalness, relationship credibility, spontaneous-seeming cognition, implementation leakage, provenance retention, source-monitoring error, uncertainty calibration, renderer invariance, state mutation, and memory distortion across recall.

## 30. Integration with Pretorius

UPPB sits above the existing mechanistic cognition.

It does not replace the recurrent action policy, needs, relationships, concerns, commitments, deep history, state-policy bridge, causal audit, sleep/replay, provenance, or standalone persistence.

Current v0.4 output remains unchanged until a later integration gate explicitly migrates a subject-facing path to UPPB.

## 31. Standalone requirement

UPPB is part of the standalone architecture.

Canonical projection must work with networking disabled and no hosted model.

ChatGPT/plugin integration, hosted models, local LLMs, games, voice, desktop shells, and future bodies are optional adapters.

## 32. Non-goals

Do not:
- claim consciousness;
- imitate neuroanatomy without a functional reason;
- create a continuous internal narrator;
- expose every state change;
- equate thought with speech;
- equate motor expression with awareness;
- remove protected provenance;
- introduce arbitrary false memories for flavor;
- use an LLM as the sole source of phenomenal semantics;
- allow first-person text to overwrite canonical mechanism state.

## 33. Defining principle

> The machinery may know the truth. The character may know only what becomes experience.

Corollary:

> Experience is first-person, limited, contextual, reconstructive, and fallible. It may diverge from implementation truth without destroying implementation truth.

For Pretorius, this means he should not experience himself as a database, policy engine, provenance graph, or recurrent substrate. He should experience perceptions, sensations, memories, feelings, impulses, beliefs, doubts, intentions, expectations, private thoughts, self-perceptions, and the consequences of living through events.
