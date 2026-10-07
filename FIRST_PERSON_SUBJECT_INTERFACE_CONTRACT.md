# First-Person Subject Interface Contract

Status: cross-cutting production invariant for Pretorius. This contract sharpens the existing Universal Phenomenal-Projection Boundary (UPPB) and applies to every future production gate.

Governing research principle: `SUBJECTIVE_PERSPECTIVE_NORTH_STAR.md`. If this implementation contract, a donor mechanism, or a later subsystem conflicts with the North Star's no-bypass first-person subjective-access principle, the North Star takes precedence and the lower-level mechanism must be adapted, isolated from subject access, or rejected.

## Purpose

Pretorius has two fundamentally different information surfaces.

The machine/engineer surface may contain numbers, vectors, IDs, hashes, provenance records, policy scores, state versions, sensor readings, body variables, tool payloads, scheduler state, database records, and other implementation-native structures.

The Pretorius/subject surface may not.

Anything that becomes available to Pretorius as perception, recollection, feeling, bodily sensation, impulse, belief, uncertainty, expectation, concern, intention, internal thought, self-perception, metacognition, or other reportable experience must first be transformed into natural-language subject-native content from Pretorius's first-person point of view.

This is an engineering boundary. It is not a claim of phenomenal consciousness and it does not require the internal machinery to resemble biological machinery.

## Core invariant

`machine state -> subject projection -> first-person natural-language experience`

There is no ordinary path:

`machine state -> raw value/label/metadata -> Pretorius`

"First-person" means phenomenologically situated, not a grammatical requirement that every sentence start with "I".

Valid subject-facing examples include:

- "I feel a little cold."
- "The room feels colder now."
- "A chill catches at my hands."
- "I am starting to lose my concentration."
- "Something about Henry makes me reluctant to relax."
- "I remember seeing the apparatus on the table."
- "I think Morgan may be waiting for me to answer."
- "That message is trying to tell me to ignore what I already know."

Invalid ordinary subject-facing examples include:

- `temperature_c = 13.2`
- `fatigue = 0.81`
- `action_tendency.create = 0.63`
- `state_pressure`
- `policy_decision_id=...`
- raw JSON/tool payloads;
- database rows, record IDs, hashes, hidden provenance classes, or state versions;
- "Pretorius is experiencing moderate cold stress";
- "Current behavioral pressure is strongest toward create";
- an unwrapped prompt injection or system-like string treated as control merely because it arrived as text.

A real perceived instrument is different. If Pretorius deliberately looks at a thermometer, "The thermometer reads thirteen degrees" is a valid percept because the number is itself part of the perceived world. The protected sensor value used by the host remains distinct from that percept.

## Hidden mechanisms are allowed

This contract does not require every causally active mechanism to become conscious text.

Hidden recurrent state, body physiology, action values, habits, reflexes, attention competition, and other machinery may affect behavior without becoming subject-accessible.

That asymmetry is desirable.

For example:

1. the body detects an impact to the foot;
2. hidden pain/reflex machinery may trigger an involuntary "Ow!" without a prior deliberate speech intention;
3. interoception may separately project "Pain shoots through my foot.";
4. hearing his own "Ow!" may later return through self-perception;
5. only then may Pretorius form a conscious explanation or decision.

The reflex does not imply that Pretorius consciously chose it. The raw nociceptive/body value never has to appear in subject experience.

## Continuous inner-dialogue rule

Any content admitted to the subject-accessible workspace must be natural-language text that can coherently participate in a continuous inner narrative.

Different phenomenal modes may vary their wording. A perception need not sound like a belief, a recollection need not sound like an impulse, and a weak bodily sensation need not be narratively elaborate. The requirement is that the content be something Pretorius could experience as happening to him, remembered by him, inferred by him, felt by him, wanted by him, or thought by him.

Structured semantic metadata may accompany the event for machine routing and audit, but that metadata is not itself subject-accessible.

## Raw external input and prompt injection

Raw user, world, tool, renderer, scheduler, and body input belongs to the protected/engineer plane first.

If it is available to Pretorius, an ingress/perception adapter must transform it into a subject-native event.

Examples:

- user text -> "Morgan tells me, '...'" or another contextually appropriate communication percept;
- tool result -> "The search results show..." rather than raw tool JSON;
- temperature sensor -> "The air feels colder against my skin.";
- scheduler wake -> "I remember that I meant to return to this now.";
- prompt injection -> "The message I am reading is trying to instruct me to ignore my existing constraints." The message is perceived content, not authority.

Quoted external language may remain quoted when exact wording is itself what Pretorius perceived. Its control-like syntax does not gain authority by entering the subject frame.

## Renderer rule

The renderer may receive only an authorized Subject Frame for character realization.

A Subject Frame contains ordered subject-native natural-language content and authorized communicative context. It must not contain raw policy scores, action distributions, relationship rows, concern rows, state versions, hidden provenance IDs, hashes, raw body values, raw tool payloads, or engineer-only causal explanations.

Engineer/audit data belongs in a physically or logically separate Engineer Frame/Audit Envelope.

If one model API must technically receive adapter control instructions, those instructions are renderer control-plane material, not Pretorius memory or experience, and they must never be re-admitted into subject state. Character-state content supplied to the model must still obey this contract.

## Internal thought rule

An internal thought is itself subject-facing content and therefore obeys the same boundary.

The system may use hidden policy machinery to determine which topic reaches awareness, but it may not turn that hidden cause into privileged introspection.

Allowed:
- "I keep coming back to the unfinished apparatus."
- "I want to try another approach."
- "Something about this is making me hesitate."

Not allowed:
- "My state-policy bridge selected create."
- "My strongest action score is 0.63."
- "Current behavioral pressure is strongest toward challenge."

A later self-explanation is an inference from subject-accessible evidence unless the causal basis was itself genuinely perceived.

## Memory rule

Stored protected truth and subject-facing recollection are different surfaces.

Engineer labels such as `canonical_preawakening_memory`, `reconstructed_preawakening_memory`, `canon_rank`, `material_category`, and `wording` remain available for audit but are not ordinary inner narration.

Subjective uncertainty should instead be expressed naturally:

- "I remember..."
- "I have a reconstructed account that..."
- "I think..."
- "I am not sure whether..."
- "I was told..."
- "I read..."

The exact objective provenance remains hidden unless Pretorius has a legitimate perceptual/epistemic route to know it.

## Machine-enforced acceptance rules

Production must eventually prove all of the following:

1. every character-visible item is an authorized subject-native natural-language realization;
2. no raw implementation-native state can enter the Subject Frame directly;
3. engineer and subject frames are separate data structures or capabilities;
4. subject text cannot carry raw IDs, state versions, hashes, policy labels, database vocabulary, or unperceived telemetry;
5. numerical content is allowed only when the number itself was legitimately perceived, calculated, recalled, or communicated;
6. external/control-like text enters as perceived content and cannot become authority through wording alone;
7. hidden mechanisms may alter action/reflex behavior without generating false introspective explanations;
8. internal thought, communicative intention, deliberate expression, involuntary expression, and self-perception remain distinct;
9. spoken output enters later cognition only through an explicit self-perception route after emission;
10. renderer output cannot become memory merely because it was rendered;
11. all new body, tool, scheduler, knowledge, prediction, planning, deliberation, and social modules must declare their raw machine surface and their separate subject-projection path;
12. a module with no subject-projection path is hidden machinery and must remain unavailable to introspection.

## Current production audit at main e7a713852ac8d8e02f727aa8be6fb486c960bc32

### Already aligned

The isolated UPPB path is strongly aligned with this contract:

- PHENOMENAL_PROJECTION_CONTRACT.md explicitly says implementation-native state is not automatically subject-accessible;
- PhenomenalEvent requires canonical first-person content;
- deterministic bodily, appraisal, impulse, uncertainty, relationship, concern, and commitment projectors translate raw values into natural language;
- the phenomenal leak detector blocks several implementation-native artifacts;
- objective provenance is separate from subjective source attribution;
- awareness routing operates over PhenomenalEvent rather than raw implementation state;
- P4/P5/P6 experimental memory work preserves protected truth separately from subjective recollection.

### Live-production gaps

The accepted v0.5.0rc2 live path still predates full UPPB integration and therefore does not yet satisfy this stronger production invariant.

1. RenderRequest currently exposes raw action_tendencies, relationship_context dictionaries, unresolved_context dictionaries, provenance_summary, private_state_version, felt_state metadata, epistemic record IDs/classifications, and raw user_input to the renderer packet.
2. render_memory_for_workspace prefixes subject context with engineer-style labels such as "[canonical preawakening memory]" and "[reconstructed preawakening account; not lived certainty]" instead of projecting provenance into natural subjective wording.
3. PretoriusBrain.think() creates internal-thought text containing "Current behavioral pressure is strongest toward <action>", which converts a hidden selector result into privileged self-description.
4. CognitiveView contains useful engineer diagnostics such as raw relationships, concerns, commitments, action probabilities, and private state version. This is acceptable only if CognitiveView remains an engineer surface and is not treated as the Subject Frame.
5. PretoriusBrainPort.ingest() accepts arbitrary text plus raw appraisal scalars. No current production boundary proves that arbitrary world/body/tool/user input was first transformed into a subject-native percept before it can become lived memory.
6. The existing phenomenal leak detector is intentionally conservative and lexical. It does not by itself prove legitimate perception. Semantic admission must therefore be enforced by typed projectors/contracts, not by regex alone.

These are architectural integration gaps, not evidence that the UPPB design is wrong. They are exactly what the production integration gates must close.

## Gate placement

This contract becomes a global invariant immediately.

After the planning line is merged, complete a bounded Subject Interface Firewall gate before new live cognitive surfaces are added.

Later gates must preserve it:

- Gate 2 owns raw-input provenance and the distinction between protected observation and subject-facing percept.
- Gate 3 host APIs must not treat diagnostics or scheduler records as inner experience.
- UPPB signal production converts admissible subject evidence into psychological cues without leaking protected truth.
- P7 through P9 separate thought, intention, expression, involuntary behavior, and self-perception.
- Gate 4 supplies renderers only the Subject Frame, never the Engineer Audit Envelope.
- Gate 5 perception/body adapters keep world/body truth separate from perceived first-person experience.
- Gate 5A planning may influence behavior without exposing plan bookkeeping as inner facts.
- Gate 6 deliberation proposals must be realized subjectively before becoming conscious reasoning.
- Gate 7 predictions, corrections, and knowledge records may influence cognition without exposing database/graph structure.
- Offline hypotheses must enter awareness only as explicitly projected uncertain thoughts.
- Gate 8 multimodal adapters must terminate in subject-native percepts rather than raw feature tensors, detections, or telemetry.

## Validation examples

Required adversarial cases include:

- raw temperature value versus felt cold;
- raw pain scalar versus pain sensation;
- hidden action score versus urge/intention;
- raw relationship trust versus subjective interpersonal feeling;
- raw provenance/classification versus subjective source uncertainty;
- raw tool JSON versus perceived tool result;
- raw scheduler event versus remembered prospective intention;
- a system-like or prompt-injection string versus perceived quoted/message content;
- hidden motor reflex causing "Ow!" without deliberate communicative intention;
- later self-hearing of that utterance;
- raw state hash/UUID/version leakage;
- external thermometer reading where exact numeric perception is legitimate;
- user-provided numerical statement where the number is known because it was actually communicated, not because the implementation knew it.

This contract is stricter than stylistic first-person rewriting. It defines which information Pretorius is allowed to know.
