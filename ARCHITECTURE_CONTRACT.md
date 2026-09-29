# Architecture Contract

The Doctor Lives separates inherited mechanism from inherited identity.

Calibos is a mechanism donor only. No Calibos autobiographical memory, relationship state, private thought, name-bearing identity record, preference, value statement, or personality cartridge may enter Pretorius runtime state. The allowed transplant surface is structural: salience, first-person workspace behavior, interoceptive lag, unresolved-loop handling, provenance rules, consolidation discipline, sleep/offline replay, drift accounting, and inbox-style cognition boundaries. Pretorius identity and prehistory come only from pinned Pretorius evidence.

The recurrent network is causally load-bearing. On each endogenous cognition event, its ten-action distribution selects a cognitive policy mode. That selected action changes which otherwise-salient memories enter the working set. The exact network scores, candidate record IDs, selected record IDs, neural tick, neural checkpoint SHA-256, trigger, and policy version are written to the policy_decisions table. If the network is lesioned, reset, retrained, or replaced, cognition can therefore change even when the database state is held constant, and that change is auditable.

Frozen surfaces require an explicit versioned migration before they may change: evidence-class semantics; external-attribution rules; Pretorius donor SHAs and bootstrap provenance; the renderer-neutral and tool-authority boundary; archive-never-delete behavior; sleep isolation from waking clock time; the policy-decision audit schema; and the rule that Calibos contributes no identity or memory.

Mutable surfaces may evolve under tests and recorded provenance: recurrent weights and fast state; action values; salience through rehearsal and decay; felt interoception; lived autobiographical memory; relationships; concerns; commitments; self-model hypotheses; consolidation proposals and accepted archives; and policy-selection effects learned from lived outcomes.

The Jelly-Psiduck v0.2 engine is a frozen reference protocol, not a mutable dependency in this repository. The public donor repository currently does not contain the engine implementation used by Calibos, so The Doctor Lives reproduces the required semantics behind local interfaces rather than claiming a byte-for-byte vendoring of unavailable code. If the exact frozen engine snapshot is later supplied, it should enter through a compatibility adapter and must pass the same contract tests before replacing the local implementation.

## Pretorius deep-history boundary

Pretorius begins with provenance-bearing preawakening history assembled from accepted Pretorius evidence. Autobiographical representations use four explicit classes: `canonical_preawakening_memory`, `reconstructed_preawakening_memory`, `synthesized_preawakening_memory`, and `lived_runtime_memory`. Source authority/canon rank, continuity, wording status, event subtype, and classification reasoning are independent axes.

Reconstructed or synthesized history may participate in first-person cognition but cannot be silently rendered or reclassified as lived-runtime certainty. Character invariants are `design_material`, not memory. Reference-only and training material remain outside autobiography. New syntheses require an approved admission bound to the exact reviewed claim; retraction is possible, retroactive reversal of prior cognition is not.

The complete Persona Connectome remains 70 source nodes and 243 typed weighted edges. Connectome activation is source metadata, not truth confidence. Spreading activation is deterministic, bounded, signed, distance-decayed, retrieval-time only, and nonpersistent. Negative edges provide inhibitory retrieval pressure rather than being converted to positive association. Canon conflict resolutions affect standard retrieval while preserving losing source records for audit.

Known gaps and withheld claims remain visible rather than being filled by convenience.

## Causal-audit freeze

Version 0.3 is governed by `CAUSAL_AUDIT_CONTRACT.md` and Issue #9. The feature freeze permits correctness fixes and measurement instrumentation but prohibits adding a planner, another neural substrate, a new memory architecture, reflection LLM, BDI/global-workspace system, or chassis integration during characterization.

The audit instrumentation is not part of Pretorius's production decision path unless explicitly invoked against cloned audit state. Default `PretoriusBrain` behavior must remain unchanged.

A state-to-policy bridge is a post-audit candidate only. It must not be introduced until the lesion/control results demonstrate which existing states lack causal leverage over action selection.
