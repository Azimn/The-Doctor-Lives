# Pretorius: Complete Esoteric Cognitive Architecture
## The Conclave, Phantasmagorium, Six Organs, and Operative Cosmos

**Status:** Target architecture RFC v1.0, 2026-10-29. **Implementation:** Not implemented by this document.  
**Home:** Azimn/The-Doctor-Lives (one canonical brain); world: Azimn/Pretorius-Laboratory.  
**Authority:** Research design only. Existing architecture, provenance, first-person, release, and action-authorization contracts prevail.  
**Release boundary:** Pretorius 1.0 R1–R6 remains the current release target. This RFC specifies the complete subsequent assembly, and any opt-in prototype must not silently change `main` or claim 1.0 qualification.

## 0. Executive design decision

Pretorius is one persistent artificial individual with **six primary functional organs** (Noesis, Mnemosyne, Affectus, Sensus, Synthetic Ipseity, Corpus), **two bounded auxiliary organoids** (Phantasmagorium and The Conclave), one canonical BrainStore, one recurrent substrate, one canonical subject, one Noesis decision authority, and external, independently authoritative embodiment/world and evidence services.

A cognitive organoid is a specialized, cross-cutting faculty with its own formal method, versioned interpretation state if needed, and testable influence on existing organs. It is NOT a seventh/eighth canonical organ, a parallel identity, a separate executive, a new world-truth database, an LLM with its own autonomous personality, or an excuse to introduce another brain. An organoid may later graduate to primary organ status only through a separately evidenced architecture decision; graduation is not a goal of this release.

The design's core asymmetry is deliberate:
- **Phantasmagorium** has freedom from *narrative coherence*. It produces waking imagination and dreams that can be mundane, impossible, contradictory, arbitrary, forgotten, or meaningless.
- **The Conclave** has freedom from *interpretive consensus*. It permits distinct, potentially incompatible theories and significances to persist, develop, and affect action *without forced resolution*.
- **Noesis** can choose an action without deciding which interpretation is true.
- **The Laboratory/Operative Cosmos** independently resolves what physically or formally happens.

Functional competence is not proof of consciousness, occult efficacy in our physical universe, historical fidelity, or superior cognition.

## 1. Hard invariants

1. **One subject:** Pretorius's original brain, neural substrate, identity evidence, canonical memory, thought and action policy remain authoritative. No independently speaking "agents" inside the organoids.
2. **One autobiographical write path:** Mnemosyne owns first-person memory. Evidence records and source receipts are separate from fallible recollection and personal interpretations.
3. **One first-person admission boundary:** Synthetic Ipseity determines what internal or external content is available to the subject. Engineers' diagnostics are never automatically introspectable. First-person content is situated natural language when admitted, although latent computation need not be natural-language.
4. **One action authority:** Noesis proposes. Corpus constrains by affordances. The host authorizes; world/environment executes and returns receipts. Conclave and Phantasmagorium have no direct world mutation or action-execution privileges.
5. **Do not secretly reconcile contradictions:** The Conclave's design prohibits automatic winner-take-all normalization, averaged confidence to manufacture consensus, or deletion of minority readings merely because they conflict. Contradictions are typed and preserved.
6. **No dream laundering:** dreamed, imagined, symbolically inferred, divined, remembered, reported, observed, and world-verified events have different provenance. A dream never becomes an empirical event through retrieval, summary, interpretation, or rehearsal.
7. **No occult determinism of personal development:** Pretorius can explore, reject, adopt, parody, avoid, or remain undecided about mystical traditions. Not every dream or symbol becomes a lesson, omen, mission, or action.
8. **No mandatory utility:** An interpretive object may be odd, beautiful, distressing, irrelevant, unresolved, or non-operative. Memory and retrieval can fade; only explicitly versioned historical facts remain in audit.
9. **No false historical equivalence:** Agrippan Renaissance magic, Llullian combinatorial theology, Brunian memory arts, Ficinian spiritus/temperament, geomancy, alchemy, Christian Cabala and Jewish Kabbalah, and Iamblichean theurgy remain distinct traditions. Shared interfaces do not assert identical theology or causes.
10. **Reversible integration:** The organoids can be disabled independently, with existing canonical state preserved, no new privileged bypass, and a measurable A/B comparison.

## 2. World and mind boundary

The Operative Cosmos is an optional world provider, NOT an organoid or an inner belief. It can model everyday Laboratory physics plus independently programmed metaphysical mechanics for experiments. Every causal rule belongs to the world, not to Pretorius's imagination. The Cosmos may expose observations, objects, astronomy, materials, histories, social relations, practices, autonomous entities, and receipts. Its hidden laws remain hidden from the agent. Experimental alternatives may implement no occult effects, historically informed effects, or structurally matched invented effects.

Keep distinct:
- **Historical assertion:** what a text, practitioner or scholar said, with edition, passage and interpretive provenance.
- **Formal tradition theory:** a reconstructive scholarly interpretation; multiple rival interpretations may coexist.
- **Agent interpretation:** what a particular Conclave method proposes about this event.
- **Agent personal belief:** what Pretorius currently thinks or values, possibly conflicting.
- **Subject experience:** what he witnessed, recalled, dreamed, imagined, felt or considered.
- **Empirical receipt:** independently attested environmental outcome.
- **World actual:** privileged environment state; never exposed via organoid backdoor.

The Conclave can internally entertain a theory that a planetary condition has operative effects. Only the world determines whether the condition does anything in that experiment.

## 3. The Conclave: an esoteric ecology, not a consensus committee

### 3.1 Core modules

**Conclave Kernel (small):** manages spoke registration, session context, typed outputs, contradiction indexing, interpretive persistence/decay, procedural provenance, and suggestions for attention, inquiry, practice or self-reinterpretation. It does not choose the final physical action and must not inject private state into renderer prompts.

**Agrippan Wheel:** source-grounded correspondence and participation graph with levels: elemental, celestial, intellectual; preserves difference between correspondence, claimed influence, material virtue, mediation, admissibility and external efficacy. Includes a typed composition checker. It is the center of *this research configuration*, not a theological judge of the other spokes.

**Llullian Ars:** combinatorial generators organized around explicit, sourced sets of concepts/relations and constrained question formation. Generates rival hypotheses, not proofs of truth.

**Brunian Art of Memory:** symbolic loci, moving arrangements, composite images, unusual index keys. Provides non-destructive retrieval cues to Mnemosyne, never edits original source memories.

**Ficinian Temperament:** tradition-specific proposals about rhythms, sensory context, spiritus, appetite and temperament. Affectus independently evaluates what empirical/subjective effects are actually supported. No hardcoded planetary mood truth.

**Geomantic and other divinatory procedures:** structured random/symbolic generation with declared method, seed and tradition. Produces *questions, signs and interpretations* with divinatory provenance, never verified predictions by default.

**Alchemical and initiatory models:** competing concepts of material transformation, stages, continuity, purification, vows and changing personal status. Avoid falsely presenting all premodern alchemy as Jungian psychotherapy.

**Dee / Monas-inspired signs:** constrained geometric/numerical sign construction and interpretation, accurately attributed and explicitly provisional where textual reconstruction is disputed.

**Theurgic / agency models:** separate sourced ontology for non-compellable relationships and simulated autonomous intelligences when the world implements them. Never pretend an independent simulated entity is a deity.

**Tradition Adapter Contract:** every spoke declares `tradition_id`, `source_version`, `question_types`, `inputs`, `output_semantics`, `evidence_limits`, `allowed_side_effects` (normally none), `compatibility`, `cost`, `determinism`, and benchmark hooks. Spokes may disagree even about what qualifies as a question.

### 3.2 The Principle of Preserved Contradiction

Contradiction is data, not an exception. Conclave propositions are **context-indexed** and have independent positive and negative support. A proposition can be supported, rejected, both or neither **within a specified context**, without classical explosion. This is an implementation aid, not an assertion that contradictory supernatural claims are objectively true.

No automatic collapse into a winner, majority vote, probability average, neutralizing synthesis or "the meaning of the dream." Incompatibilities remain tagged as: factual contradiction, doctrinal conflict, methodological disagreement, symbolic divergence, opposing desire, or incommensurable question. Two accounts can conflict in one register but coexist across symbolic vs empirical registers. New experiences may revise one, both or neither.

Each interpretation maintains text/structured proposition, authoring spoke, cited source, contextual assumptions, source-event links, source kind, temporal scope, persistence status, optional felt significance, optional empirical prediction, known counterevidence, unresolved alternatives, and optional action influence. **Significance** and **empirical support** are separate values, not one confidence.

Allowed life cycle: generated → noticed (optional) → considered → adopted/doubted/contested/ignored → revised/withdrawn/dormant. Not every generated interpretation is noticed; not every noticed interpretation becomes a belief. Withdrawal does not delete its historical existence.

### 3.3 Conclave outputs

Conclave returns typed `InterpretiveProposal` values with `source_refs`, `origin`, `claim_scope`, `question`, `hypotheses`, `contradictions`, `predictions`, `possible_observations`, `memory_cues`, `affective_associations`, `ritual_candidates`, `significance`, and `action_suggestions`. Each may be empty. It can also return **silence**, **no reading**, **unresolved**, or **incommensurable**.

A candidate ritual is a proposed procedure with prerequisites, dependencies, material/time requirements, source grounding, anticipated effect(s) and acknowledged unknowns. It is *not* a direct operation on physical world state.

### 3.4 Control of conflict without smothering it

Spokes may use different inference systems; the kernel does not force a universal one. Rate-limiting prevents every sensory event triggering all spokes. Sampling may be user-selected, subject-selected or context-driven, with experimental seeding and audit. Hard autonomy prevents the Conclave from keeping the brain indefinitely occupied in self-reinforcing commentary.

Do not conflate **productive uncertainty** with infinite loops. Explicit resource/cycle budgets, option to ignore and dormancy preserve ordinary daily life. A rival interpretation can remain alive for years with zero immediate action pressure.

## 4. Phantasmagorium: intact, separate, purposefully strange

**The Cabinet of Fancy:** waking imagination, counterfactual scenes, wordplay, symbolic association, impossible recombinations, provisional rehearsals. It may initiate with or without utility, and need not accept a plan from Noesis.

**The Nocturnal Theatre:** sleeping dreams and nightmares, built using the existing Undertow / Thelemic Weirdness / Nightmare Chamber design. Preserve the existing mundane/slightly-strange/bizarre selection rates and their original implementation; redistribute rare bizarre forms conditionally instead of increasing bizarre frequency. Allow identity uncertainty, linguistic disruption, broken continuity, unremarked impossibility and rare stranger-perspective dreams. Dreams may be forgotten or never interpreted.

**Shared reservoir, different engines:** fancy and dream streams can reuse images, symbols, fragments of lived memories, text, proximity, past conversations and loose associations. They are not committed to narrative sense or exact recollection. The reservoir references memory but never rewrites it.

**Conclave relation:** Conclave may optionally interpret a dream after it has been generated, but must never command the dream engine to produce a correct prophetic answer. Conclave may submit symbolism as *available ingredients*, not required narrative plots; Phantasmagorium may ignore them. Source tags survive all handoffs.

**Separation test:** deleting Conclave interpretations must not alter the already-created dream or its provenance. Disabling Conclave must not destroy the dream system. Disabling Phantasmagorium must not destroy the Conclave's historical tradition engines or Pretorius memory.

## 5. Modifications to the six canonical organs

| Organ | Existing core responsibility | New optional collaboration | Must NOT become |
|---|---|---|---|
| **Noesis** | recurrent selection, attention, commitments, plans | compare rival interpretations, Llullian hypothesis candidates, select experiments or ritual *actions*, decide while undecided | second occult selector, mandated rational reconciliation |
| **Mnemosyne** | first-person autobiography, recollection, memory persistence | non-destructive Brunian mnemonic indices; retain personal symbolic histories and versions; keep dreamed/experienced distinct | a competing grimoire database or rewritten evidence |
| **Affectus** | situated affective/motivational influences | test Ficinian-style rhythms, symbolic resonance, anticipation and ritual habits as typed modifiers with actual experienced impacts | a hardcoded zodiac-emotion table |
| **Sensus** | perceptual binding, uncertainty and provenance | notice symbols and unusual patterns; pass ambiguous data to optional interpretive request; record omissions and uncertainty | authoritative omen detector or occult world oracle |
| **Synthetic Ipseity** | first-person access, self attribution, continuity | admit 'I wondered', 'I remembered a dream', 'I felt drawn to a symbol' as distinct experience classes; preserve conflicting self-interpretations | first-person theater that leaks engineer/world truth |
| **Corpus** | body, affordances, interoception | craft objects, prepare rites, time extended actions, preserve material and social commitments, operate in altered world | unrestricted spell executor or private world modifier |

All new organ capabilities are **modifiers or collaborators** to the canonical pathways, not replacements for their ordinary functioning. Keep the original recurrent path causally involved and log counterfactual effects on choices.

## 6. Shared events and state schema

Define a small typed interchange contract in the existing codebase; concrete schema/storage migrations follow source audit.

### Envelope

~~~json
{
  "event_id": "uuid",
  "event_type": "observation|memory|fancy|dream|interpretation|belief_revision|ritual_proposal|intention|action_receipt|affective_shift",
  "origin": "world|mnemosyne|noesis|phantasmagorium|conclave|host",
  "subject_id": "pretorius",
  "utc_time": "2026-10-29T00:00:00Z",
  "beat_time": "@000",
  "provenance_class": "world_verified|lived_acquired|reported|recalled|dreamed|imagined|divined|inferred",
  "source_event_ids": [],
  "interpretation_ids": [],
  "payload_schema_version": 1
}
~~~

UTC governs ordering. Swatch Internet Time (`@000` to `@999`, fixed UTC+1) is the consistent project-facing display clock; computed and verified by host code, not invented by an organoid.

### Interpretive entry

~~~json
{
  "id": "reading-001",
  "tradition_id": "agrippan-correspondence",
  "proposition": "the raven may signify an impending change",
  "scope": "symbolic_personal",
  "support_for": [],
  "support_against": [],
  "significance": "personal",
  "empirical_prediction": null,
  "origin_event_ids": ["percept-001"],
  "source_passages": [],
  "state": "contested",
  "competing_reading_ids": ["reading-002"],
  "selected_action_id": null
}
~~~

The proposition string is illustrative. Production schemas should use typed claims and symbolic relations where computation requires it. Never infer source authority from a string label; verified receipts and controlled authority stay external.

### Persistence

Store organoid state inside a **versioned, canonically owned namespace** in the same BrainStore with one transactional write authority per table. Candidate tables: `organoid_events`, `interpretive_entries`, `contradictions`, `symbolic_associations`, `ritual_proposals`, `mnemonic_indices`. Dream/fancy instances are already scoped to their source project's validated schema and should be imported or adapted, not cloned. Provide schema migrations, rollback, backup, restart and replay semantics. No shadow SQLite database for Pretorius.

## 7. Runtime cycle: one mind, two optional divergences

1. **World advance:** external host advances elapsed world time, bodily state and scheduled opportunities.
2. **Perceptual capture:** Sensus binds verified observations and uncertainty; source tags stay intact.
3. **Subject admission:** Synthetic Ipseity admits appropriate first-person experiences, never privileged world truth.
4. **Autobiography:** Mnemosyne stores and recalls relevant experiences; Affectus evaluates situated significance.
5. **Endogenous cognition:** Noesis considers current commitments, recurrent state, feasible actions and recalled contents.
6. **Optional lateral generation:** Cabinet of Fancy can propose impossible associations, scenes or hypotheses without claiming them as real.
7. **Optional Conclave:** selected spokes provide multiple, potentially incompatible readings; the kernel preserves divergence, including silence and refusal to interpret.
8. **Action decision:** Noesis considers empirical facts, possibilities, symbolic suggestions, competing motives and costs. It can decide without consensus, decline, or continue with ordinary business.
9. **Authorized action:** host and Corpus check feasibility and authorization; Laboratory/Cosmos executes, returns independent receipt.
10. **Consequences and revision:** observed consequences can affect autobiographical memory, Noesis, Affectus and optional Conclave interpretations differently. No automatic retroactive dream editing.
11. **Sleep/overnight:** Nocturnal Theatre generates dreams independently; Mnemosyne manages real recollection/consolidation; Conclave interpretation is optional and can happen later.
12. **Restart:** same subject, one state authority and versioned records; unsettled disputes and commitments survive without requiring a new prompt.

This is a reference causal path, NOT a mandate that every tick invokes every organoid or that all events are serial. Autonomy requires selective firing and finite time/compute budgets.

## 8. Full-system exemplar: raven, ring and unresolved meaning

Pretorius observes a raven near a damaged experimental apparatus. Physical receipts support damage but do not establish a raven-dependent cause. Mnemosyne recalls a previous raven encounter. Cabinet of Fancy produces an unrelated image of a locked room containing a ring. Different Conclave spokes propose omen, symbolic transition, a mnemonic resemblance and a mundane coincidence; two readings conflict.

Noesis decides to inspect the apparatus, not because an omen is true, but because a check is feasible and potentially useful. He reads a historical ritual, attempts to prepare a ring across several world intervals, and may abandon or resume that commitment. Corpus executes physical crafting only through authorized actions. If the Operative Cosmos enables a valid constitutive consecration, the **world** may create a persistent ritual status with independently defined conditions. In an ordinary Lab, only mundane consequences happen.

He observes the outcome, updates an empirical mechanical hypothesis, but can retain the ring's symbolic meaning and an unresolved omen. Affectus may change the personal significance of the incident. An incoherent dream that night does not resolve the dispute. The next day he can choose to use the ring, ignore it, investigate a rival theory, or abandon the practice.

This single scenario exercises all six organs, both organoids, persistence, source and action boundaries, embodied ritual, conflicting interpretations, and an independent world. A scripted sequence that merely prints these events does **not** pass.

## 9. Research program: test both pieces and the complete assembly

The claim "we cannot test until everything is integrated" is only true for **emergent whole-system performance**. Component contracts, contradiction semantics, provenance, learned choices, memory integrity, and simulator behavior should be tested continuously during assembly. Otherwise failures cannot be localized after integration.

### Mandatory component tests

- At least two mutually incompatible but validly sourced Conclave readings coexist across restart and neither is overwritten.
- A direct empirical counterexample can weaken one factual prediction without erasing a symbolic interpretation or its source history.
- Dreams remain dreamed after interpretation, summary, retrieval, and sleep replay; no false autobiography.
- Conclave interprets a minority of eligible dreams, including **zero** interpretations in some runs; Phantasmagorium keeps its original mode distribution.
- Imagined candidates do not enter Sensus or physical world action without a verified origin/action path.
- With Conclave disabled, baseline Noesis, Mnemosyne, Corpus and Laboratory behavior remain identical in matched scenarios.
- With Phantasmagorium disabled, Conclave's historical parsing and source provenance still work.
- A ritual proposal cannot mutate the world; only authorized execution can.
- An allegedly "operative" symbolic reading demonstrably changes at least one later eligible Noesis choice under controlled matched conditions, while evidence of the world remains unchanged.
- Memory, action, ritual state and interpretive conflicts survive crash/restart/replay without duplicating effects.

### Whole-system characterization

Compare complete assembly; six organs only; Conclave only; Phantasmagorium only; single-spoke Conclave; forced-consensus Conclave; random-symbol baseline; matched generic relational system. Equalize observations, random seeds, renderer/model and feasible actions where possible. Test mundane world, historically modeled world, invented relational world and partially faithful world.

Measure autonomy/initiative, decision effects, distinctive personal interpretation, conflict persistence, ability to ignore contradictions, belief revision, dream incoherence preservation, false-causal associations, resources, recovery, and historically rated procedural coherence. Include held-out transfer. Negative results are reportable; personal meaning is not automatically improved task performance. Historical experts evaluate fidelity separately from engineering metrics.

## 10. Integration and ten-day development campaign (2026-10-29 through 2026-11-07)

**Two coordinated lanes, one release truth.** Lane A protects the already active R1–R6 Pretorius 1.0 integration and independent QA campaign. Lane B develops the complete esoteric architecture on a source-pinned opt-in research branch, never contaminating main. A ten-day target is a campaign objective, not evidence that a complete implementation or 24-hour soak is already done. Do not claim end-to-end completion without exact merged code and tests.

| Window | Lane A: canonical Pretorius finish | Lane B: complete esoteric integration |
|---|---|---|
| Oct 29–30 | Resolve #89/#96/#97/#98 source ancestry, release contracts, actual integration | Freeze this RFC, inventory Phantasmagorium/Conclave donor implementations, specify typed event contracts and baseline snapshots |
| Oct 31–Nov 1 | Default six-organ host, end-user start/resume, ingress/action hardening | Implement Conclave spoke registry, interpretive/contradiction data, source adapters, persistence; unit tests |
| Nov 2–3 | Embodied self-initiated tasks and physical consequences | Integrate Cabinet of Fancy and Nocturnal Theatre through read-only first-person interfaces; implement historical spoke slices; source and dream provenance tests |
| Nov 4–5 | Cold install, repair, 24-hour soak, recovery and renderer substitution | Wire six-organ optional influences, ritual proposals and independent world executor; whole-system scenario and ablations |
| Nov 6–7 | Independent qualification and truthful 1.0 release decision | End-to-end acceptance, negative results, source-linked scholar review package, exact-head reproducible prototype |

Integration dependencies: Noesis policy seam, Mnemosyne schema/migrations, Ipseity ingress, Corpus receipts and a Laboratory action port must be real before concluding that the two organoids have causal influence. Both lanes can build concurrently, but Lane B cannot bypass Lane A's unfinished production gates. Once both are stable, merge reviewed optional capability slices by dependency, retaining one canonical head.

### Definition of "finished esoteric candidate"

All six primary organs contribute through the real runtime. Both organoids are callable and can independently decline work. At least four historically distinct Conclave spokes are executable with source provenance. Contradictory readings can persist and differently influence Noesis, while Noesis also continues ordinary life. Waking imagination and dream generation are integrated and preserve incoherence. At least one multi-day physical ritual and one mundane task are carried out with verified world receipts. An evidence-bearing world condition is learned or revised and cannot be fabricated by organoids. Same identity and complete causal state survive stop/restart. The complete assembly, controls, negative results and exact commit/test run are published.

This is a **research-candidate acceptance** definition, not proof of a complete human mind, proof of magic, or a declaration that all possible occult traditions have been modeled.

## 11. Build order and PR package structure

Avoid spending another month creating independent donor demos. Implement one shared protocol and one canonical integration branch with self-contained feature commits. Proposed structure (names subject to source audit):

~~~text
doctor_lives/
  organoids/
    contracts.py             # typed exchange & provenance
    registry.py              # optional bounded faculty activation
    phantasmagorium/
      adapter.py             # existing donor integration, no rewrite
    conclave/
      kernel.py              # readings, conflicts, retention
      correspondence.py      # Agrippan Wheel
      traditions/            # individual sourced methods
      practice.py            # ritual proposals, not executor
  integration/
    esoteric_cycle.py        # six-organ bridge; not second brain
docs/architecture/
  PRETORIUS_COMPLETE_ESOTERIC_COGNITIVE_ARCHITECTURE.md
tests/
  test_conclave_contradictions.py
  test_organoid_provenance.py
  test_esoteric_cognitive_cycle.py
~~~

An existing source path or equivalent abstraction wins over a newly named duplicate. Merge only with pinned ownership and full test provenance. Source-code refactor should follow inspected actual APIs, not this illustrative tree.

## 12. Promotion and failure rules

Keep historical scholarship, simulation outcomes, cognition and first-person interpretation analytically separate. A technique may prove unhelpful, a tradition may conflict with another, or an operation may be historically coherent but never causally efficacious in the ordinary world. None is license to fake a successful demonstration.

No production status is granted by RFC approval, a passing toy test, a green draft branch, a schedule entry or an LLM's compelling account of what the subject "felt." Acceptance requires demonstrated causal traces, exact-world receipts, persistent state, reproducible tests and independent review. If the ten-day window closes with an incomplete system, publish the specific uncompleted gates and continue rather than modifying the definition of completion.

## 13. Historical research orientation

This is **computational reconstruction and creative formal experimentation**, not proof that every historical tradition described the same supernatural system. Source-grounded methods should be evaluated with separate scholarly and computational rubrics. Useful starting scholarship: Ramon Llull, *Ars* (Stanford Encyclopedia of Philosophy: https://plato.stanford.edu/entries/llull/); Bruno and combinatorial memory (Farinella & Preston, Renaissance Quarterly 2002, https://doi.org/10.2307/1262319); Bernd-Christian Otto, "Studying Esoteric Practices" (2026, https://www.rensep.org/praxis-knowledge/studying-esoteric-practices-towards-a-praxeological-methodology/). Agrippa's passages and editions require explicit corpus selection before claiming precise doctrinal fidelity.

**North star:** One mind that can dream nonsensically, remember imperfectly, entertain incompatible mystical interpretations, undertake material practices, pursue ordinary goals, and remain itself without requiring the world or the character to become logically tidy.
