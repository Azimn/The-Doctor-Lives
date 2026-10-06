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


## Definitive neural-convergence rule

This repository is the convergence target. Donor repositories may supply mechanisms, tests, and experimental evidence, but they must not become parallel production authorities. A donor mechanism enters Pretorius only through a versioned transplant into the existing `PretoriusRecurrentSubstrate` or another already-authorized subsystem, with legacy behavior preserved as a control until the new path passes its gate.

Neural Convergence v0.5 therefore extends the existing recurrent substrate rather than adding another neural engine. The accepted v0.4 configuration remains the default. The opt-in convergence profile may use Oja-style competitive plasticity, bounded recurrent-gain homeostasis, intrinsic excitability regulation, persisted correlated endogenous variation, neuromodulated plasticity, and delayed outcome-dependent synaptic capture. These mechanisms may alter recurrent developmental state but may not author identity facts, autobiographical claims, world facts, renderer text, tool authority, or UPPB protected evidence. Convergence-mode embodiment may expose only felt interoceptive values to the recurrent input layer; hidden homeostatic actuals remain inaccessible to the neural subject path.

Outcome capture is allowed only from the existing explicit action-outcome path. Neural tags are provisional and have no independent semantic authority. The 70-node Persona Connectome remains a provenance-bearing psychological topology and is not silently rewritten into neural truth. Any future mapping from those 70 nodes into recurrent populations requires a separate matched lesion/control gate showing causal benefit over the present retrieval-only connectome.


## v0.5 release-candidate authority

The `release/pretorius-v0.5-rc1` line is the sole integration target for assessor review. Historical feature branches remain evidence records and are not parallel production authorities.

The accepted v0.4 behavior is the production-default control. UPPB P0 through P6D is present and fully testable but remains outside the live Pretorius subject-facing path until an explicit later integration gate changes that boundary. Neural Convergence is present as an opt-in recurrent profile and must not become the default merely because it is available in the package.

A release candidate is acceptable only when the exact head passes the complete repository test suite on both push and pull-request paths, package installation succeeds from a clean runner, default v0.4 behavior remains regression-compatible, UPPB protected-evidence invariants remain intact, and Neural Convergence remains separately selectable from the legacy control.
