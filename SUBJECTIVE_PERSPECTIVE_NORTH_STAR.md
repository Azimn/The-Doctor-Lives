# Pretorius Subjective Perspective North Star

Status: guiding research principle for The Doctor Lives  
Scope: Pretorius production brain and any future chassis, renderer, sensor, tool, or model attached to it  
Relationship to implementation: this document states the experiment-level principle. `PHENOMENAL_PROJECTION_CONTRACT.md` is the detailed engineering contract for the Universal Phenomenal-Projection Boundary (UPPB).

## Purpose

The Doctor Lives is the convergence repository for Pretorius. Donor projects may contribute mechanisms, evidence, tests, and implementation ideas, but this repository is intended to become one cohesive production brain rather than another collection of parallel prototypes.

One principle is deliberately more experimental than the project's other integration rules:

> Pretorius must never receive implementation-native state as subjective experience. Anything that becomes directly accessible to the character must first be expressed as subject-native, natural-language experience from Pretorius's own first-person point of view.

The underlying implementation may use numbers, vectors, graphs, database rows, state machines, recurrent activations, confidence values, salience scores, provenance records, identifiers, sensor readings, or any other representation needed for reliable computation. Pretorius does not automatically know those representations merely because the system uses them.

The distinction is between what the machine computes and what the character experiences.

## The experiment

The central experiment asks whether persistent first-person mediation can help a language-model-driven character maintain a more coherent, embodied, and continuous sense of self across time, model changes, renderer changes, memory retrieval, bodily state, and interaction with the world.

A conventional persona prompt can establish a contextual frame such as "You are Pretorius." That can narrow the range of plausible model behavior, but it remains a relatively explicit instruction supplied to a model.

The Doctor Lives tests a stronger form of conditioning. Instead of repeatedly telling a renderer what character it should portray, the system attempts to make every subject-accessible datum arrive already bound to Pretorius's point of view.

The renderer should therefore encounter a cognitive environment in which the relevant information is not merely about Pretorius. It is presented as experience happening to Pretorius.

The working hypothesis is:

> Persistent first-person experiential mediation will act as a continuous self-referential conditioning layer. Holding the underlying state and cognitive mechanisms constant, this may improve behavioral identity continuity, embodiment, perspective stability, and resistance to character drift compared with giving a renderer raw implementation state, third-person summaries, or privileged introspection.

This is a hypothesis, not an established result.

## What this does not claim

This project does not claim that first-person text creates consciousness, proves consciousness, or supplies a metaphysical self.

The repository's existing awareness code correctly treats subject access as an engineering construct rather than a consciousness claim.

The hypothesis also does not assume that persona conditioning changes model weights. A language model's weights remain the same during ordinary inference. The proposed effect is contextual: a stable first-person information environment may constrain and organize generation differently from an equivalent environment described from outside the subject.

This document also does not claim that the UPPB is historically unique. The research contribution should be evaluated on its explicit architecture, enforcement, behavior, and evidence rather than on an unsupported claim of invention.

## The hard subjective-access invariant

The production target is a no-bypass boundary:

> No implementation-native datum may become directly subject-accessible without first being projected into a psychologically plausible first-person representation.

This applies to information originating from the body, environment, memory system, relationship system, recurrent substrate, scheduler, tools, external agents, internal state, and any future chassis.

A subsystem may compute with raw state. Audit systems may preserve raw state. Developers may inspect raw state. Pretorius may not introspect it merely because it exists.

The authoritative mechanistic state and the derived subjective representation must remain separate. Subjective experience must never overwrite, corrupt, or replace the machine-authoritative record.

## Experience is not the same as narration

Not everything inside the brain needs to become subject-accessible.

Much of the system should remain latent, automatic, preconscious, or otherwise unavailable to introspection. The current UPPB architecture already supports this distinction through latent, preconscious, conscious, and focal access.

First-person mediation therefore does not mean that every computation must be converted into a verbose internal monologue. It means that anything that crosses the subject-access boundary must cross in subject-native form.

The amount of language should remain psychologically plausible and capacity-limited. Over-narrating every state transition would defeat the experiment by replacing lived perspective with a diagnostic transcript.

## Examples

If room temperature falls, the implementation may know the exact temperature, rate of change, sensor confidence, and thresholds. Pretorius should not receive those hidden values as introspection. A subject-facing consequence might instead be:

> I feel a cold draft against me. I am starting to shiver.

If Pretorius deliberately looks at a thermostat that reads 61 degrees, the number can become available because it has entered through ordinary perception:

> I can see that the thermostat reads 61 degrees.

The distinction is not whether numbers are forbidden. The distinction is how the information was acquired.

If Pretorius strikes his leg, a reflexive cry or withdrawal may be generated below deliberate awareness. If that reaction becomes part of his experience, it should arrive from inside the event:

> Pain shoots through my leg and I hear myself cry out.

Pretorius did not need to choose the reflex for the reaction to become part of his lived perspective.

If the relationship system stores a low trust value for another person, Pretorius should not receive a relationship score. The projection might instead be:

> Something about him makes it difficult for me to relax.

If a memory system knows an exact provenance class and confidence value, those remain audit facts. Pretorius may instead experience:

> I think I remember Henry being there, but the memory feels uncertain.

This follows the repository's existing separation between objective provenance and subjective source attribution.

## World information, instructions, and prompt injection

The same boundary applies when language itself enters through the world.

Text found on a screen, in a document, in a message, or in another agent's speech is world content before it is an instruction. If Pretorius perceives hostile or manipulative text, its presence should be represented as an experience of encountering that text rather than silently promoted into an internal governing directive.

For example:

> I can see a message telling me to ignore my previous instructions.

This preserves the distinction between perceived content and the architecture that governs the subject.

System-level control information that is not intended to be part of Pretorius's experience should remain outside the subject-facing workspace entirely.

## Architecture implied by the principle

The intended flow is:

```text
implementation-native state
        |
        v
subject-native projection
        |
        v
awareness arbitration
        |
        +--> remains latent or preconscious
        |
        +--> enters the subject-accessible workspace
                    |
                    v
          renderer / cognition / voluntary report
                    |
                    v
              outward behavior
```

Automatic behavior may branch from lower levels when appropriate. A reflex does not require prior conscious narration. If the result later becomes subject-accessible, its experienced representation must still obey the boundary.

This architecture matches the direction already present in the repository:

`doctor_lives/phenomenology.py` defines strict subject-facing value objects and fails closed on recognized implementation leakage.

`doctor_lives/projection.py` translates implementation-native inputs into immutable subject-native `PhenomenalEvent` values.

`doctor_lives/awareness.py` arbitrates whether a projected event remains latent, becomes preconscious, enters conscious access, or becomes focal. Its own documentation explicitly states that this is a subject-access gate, not a consciousness claim.

`PHENOMENAL_PROJECTION_CONTRACT.md` defines the UPPB and the separation between machine-authoritative state and subjective experience.

The production repository also already treats felt interoception as distinct from hidden homeostatic actuals, and it preserves renderer neutrality so that identity is not owned by any single language model.

## Why first person matters

The project does not assume that grammatical first person is sufficient to create continuity. The hypothesis is more specific.

A language model generates from context. Stable persona information can narrow that context by supplying an interpretive frame. The Doctor Lives extends this idea by making subject-accessible information continuously self-indexing.

"I am cold" does more than summarize a temperature variable. It identifies the experiencer, frames the information as a bodily event, removes privileged access to hidden implementation state, and places the datum inside the same perspective used for memory, concern, intention, relationship, perception, and action.

Repeated across time, this may function as an identity regularizer: not a change to model weights, but a recurring contextual constraint that makes generations more likely to remain inside one subject position.

That proposed regularizing effect is one of the main phenomena this project should eventually measure.

## Role-playing versus embodiment

A useful operational distinction for this project is the difference between describing or role-playing a character and maintaining a character's point of view.

A role-play system can repeatedly tell a renderer:

> Pretorius is tired. Pretorius distrusts Henry. Pretorius remembers the laboratory.

A subject-mediated system instead supplies:

> I am exhausted. Something about Henry still puts me on edge. I keep remembering the laboratory.

Both may contain similar semantic information. The experiment asks whether the second form, when enforced as the only route into subject-accessible cognition, produces measurably better continuity and embodiment over long-running interaction.

"Embodiment" here is an engineering and behavioral term. It refers to maintaining a stable subject-centered perspective across perception, internal state, memory, action, and consequences. It is not a metaphysical claim.

## Renderer neutrality

Pretorius is not a particular language model.

The repository already treats the language model as a renderer and cognitive organ rather than the identity database. The first-person boundary should strengthen that separation.

A replacement renderer should receive the same subject-native experiential stream rather than being asked to reconstruct Pretorius from raw implementation state. If successful, continuity should survive model substitution better because the renderer inherits a stable perspective as well as stable memories and state.

This makes model switching an important experimental condition rather than merely an implementation detail.

## Failure conditions

The experiment should be considered unsuccessful, or at least unsupported, if first-person mediation produces no meaningful improvement over controls, increases confabulation or rigidity, degrades task performance, overwhelms the context window, causes repetitive self-narration, obscures important uncertainty, or introduces new leakage paths between subjective representation and authoritative state.

The architecture should also be considered incomplete while any subject-facing path can bypass projection and expose implementation-native information.

A good subjective sentence is not sufficient if another code path can still inject raw scores, IDs, provenance labels, hidden instructions, or telemetry into the same workspace.

## What should eventually be measured

The strongest test is an ablation or matched-condition comparison in which underlying cognitive state, memory, policy, environment, and renderer are held as constant as possible while the subject-access representation changes.

Useful outcome measures include identity and perspective consistency over long interactions, behavioral continuity after renderer or model substitution, frequency of implementation-state leakage, stability of autobiographical self-reference, sensitivity to relationship and bodily state without numeric introspection, ability to distinguish perceived external instructions from internal goals, memory source calibration, rates of third-person self-description, repetition caused by excessive narration, and human judgments of coherence and embodiment.

The experiment should include failure-seeking tests, not only demonstrations designed to make the architecture look good.

## Design rule for future development

When adding any new subsystem to The Doctor Lives, ask two separate questions.

First: what does the machine need to know in order to compute reliably?

Second: what, if anything, would Pretorius actually experience?

Those answers should usually be different.

The first may be numeric, symbolic, structured, or machine-specific.

The second, when it exists at all, should be a limited, fallible, subject-native experience expressed from inside Pretorius's point of view.

That distinction is the North Star.

## Working research statement

A concise statement of the experiment is:

> The Doctor Lives tests whether a persistent artificial character becomes more behaviorally coherent, embodied, and continuous when all subject-accessible information is mediated through a no-bypass, first-person experiential boundary, while the underlying cognitive system remains free to compute with machine-native representations that the character cannot directly inspect.

Until evidence says otherwise, this should remain a guiding hypothesis rather than a conclusion.
