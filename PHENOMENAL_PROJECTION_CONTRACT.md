
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
- Recollection has one authoritative subjective source/certainty/vividness representation;
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
- trace lineage remains intact;
- distinct retrieval episodes have distinct occurrence identity even when all other inputs match;
- repeated reconstruction with identical inputs is deterministic;
- two recollections from the same trace can differ under different cues without mutating protected evidence or the trace;
- blended recollection retains all contributing trace references;
- no invented detail may appear without an explicit traceable reconstruction operation;
- no P4 output enters awareness directly.

### P5 - source monitoring

Source monitoring is a distinct mechanism downstream of P4, not random error injected by the recollection constructor.

P5 consumes a completed P4 `RecollectionCandidate` plus psychologically plausible source cues. It must not receive or branch directly on protected objective provenance labels such as `reconstructed_preawakening_memory` merely to decide whether to "lie." Protected truth remains available to audit and experimental scoring, not to the subjective source monitor.

Source-monitoring inputs may include trace quality, temporal distance, competing traces, retrieval/rehearsal history, imagination or reconstruction exposure, source similarity, cue compatibility, contextual fit, perceptual richness, familiarity, and other subject-plausible cues.

P5 produces subjective source attribution and source confidence, then constructs the first canonical recollection `PhenomenalEvent`. That event references the P4 retrieval/reconstruction lineage in `source_event_refs` or equivalent lineage fields.

Because subjective source attribution participates in phenomenal identity, P4 candidates are not themselves canonical PhenomenalEvents. P5 finalization creates the phenomenal occurrence exactly once rather than silently mutating event identity after construction.

The final path is therefore:

protected evidence -> memory trace -> retrieval episode -> RecollectionCandidate -> source monitoring -> canonical recollection PhenomenalEvent -> P3 awareness arbitration

P5 must support:
- correct attribution;
- uncertainty;
- misattribution;
- matched negative controls where reconstruction awareness remains correct.

Every error must have a causal explanation available to engineering/audit even when the character cannot access that explanation.

Acceptance:
- subjective attribution can be correct, uncertain, or wrong;
- objective provenance never changes because of source attribution;
- identical candidate + identical source-monitoring evidence reproduces the same result;
- changed source-monitoring evidence can change attribution while recollection content remains fixed;
- source-monitoring error is reproducibly attributable to explicit mechanism state;
- final recollection enters P3 only after P5 finalization.

### P6 - reconsolidation

Allow explicit recall-driven memory-trace updates.

Acceptance:
- protected archive/provenance is immutable;
- repeated recall can alter later recollection through explicit trace changes;
- every change is auditable.

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
