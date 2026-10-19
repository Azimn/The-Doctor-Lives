# SelfBindingModulator v1: implementation and controlled-use contract

Status: **implemented in an isolated research prototype, not enabled in production**.  
Module: `research_prototypes/ritual_interface/self_binding_modulator.py`  
CLI: `python -m research_prototypes.ritual_interface.run_self_binding_demo`  
Unit suite: `python -m unittest discover -s tests -p 'test_self_binding_modulator.py' -v`

## Purpose and original boundary

The SelfBindingModulator is **not a consciousness gate**. It proposes a bounded, context-dependent *increase* in the importance of subject-relevant event candidates, operating on the protected engineer plane. UPPB converts implementation data into first-person subject-native PhenomenalEvents. P3 AwarenessRouter alone arbitrates latent/preconscious/conscious/focal access. Neither UPPB nor P3 nor production PretoriusBrain is modified or called by this prototype. There is no raw diagnostic material projected to Pretorius.

The separate self-binding function models the strength with which verified links to identity, relationships, commitments, autobiographical history, and self-model hypotheses contribute to contextual salience. It is an operational hypothesis inspired partly by ritual-derived identity interfaces and partly by high-level prior weighting. It does not simulate psilocybin, the default mode network, ego dissolution, or phenomenal consciousness.

## Contracts

`IdentitySnapshot` is an existing immutable, versioned list of source references; `SelfBindingModulator` checks the snapshot's manifest and state version against explicit expected values on every run. It fails closed on unknown record references or references assigned to multiple source families. It does not fetch or create records.

`EvidenceMatch(source_ref, relevance, evidential_support)` binds an input event to an admitted source reference. Relevance and evidential support are normalized [0, 1] protected-plane observations supplied by a separate verified matching stage. The modulator itself **does not infer relevance from a glyph, name, untrusted user text, language-model response, or input narrative**. Merely listing a source reference is not proof that a match is semantically correct.

`BindingCandidate(event_id, subject_id, base_salience, matches, verified_world_contradiction)` is a machine-side event descriptor, not a subject-access event. It preserves the independently determined baseline salience. All event IDs must be unique, and all candidates must match the snapshot subject.

`BindingPolicy(version, max_bonus)` is immutable, defaults to `scc-self-binding-v1`, and enforces a hard proposal cap of 0.10. Category weights are fixed prototype constants that must be independently ablated before optimization; they are not inferred truths about human cognition. They apply to authenticated source families and ensure that one candidate containing many links does not gain unlimited priority through repetition.

`SelfBindingModulator.run(...)` returns immutable `BindingRun` and `BindingProposal` records with the source snapshot digest, source manifest/version, policy version, lesion mode, gain, score breakdown, and a deterministic SHA-256 audit digest. Hashing demonstrates deterministic trace identity, not trusted signatures, confidentiality, or proof of authenticity.

## Core computation

For an event carrying validated source-linked matches, let each source family's fixed weight be `w_i`, semantic relevance be `r_i`, and evidential support be `q_i`. The normalized support is

`S = sum(w_i * r_i * q_i) / sum(w_i)` (zero if there are no matches).

For gain `g`, the proposed nonnegative bonus is

`B = min(cap, cap * g * S)`.

The proposed salience is

`salience_proposal = min(1, base_salience + B)`.

Record both the requested bonus and the *effective* post-clamp increase. Other protected perception, source truth, action eligibility, and subject access rules do not change. The "OFF" mode yields an exact zero bonus.

The chosen prototype modes are OFF=0, LOW=0.25, NORMAL=0.50, HIGH=1.0, and SHUFFLED=0.50. They are experimental gain labels, not clinical or biological states. The SHUFFLED condition deterministically rotates the entire source-match packet among sorted event IDs, keeping every original baseline, evidence packet, evidence exposure count, and global evidence pool intact while breaking the specific event-to-history alignment. With fewer than two distinct packets it fails as noninformative. Nothing about a shuffled mode creates or modifies autobiographical records.

## Verified world contradictions

If **any** batch candidate is flagged as an independently verified world contradiction, all binding bonuses in the batch are zero. This prevents self-prior amplification from indirectly crowding out a contradictory world percept through later capacity-limited awareness arbitration. World evidence remains available for its own normal perceptual routing. The flag must be asserted by a protected authoritative world/event adapter, never by untrusted prose. A corrupted, forged or user-controlled flag is not reliable verification. The correctness of this protection depends on the host.

This global freeze is intentionally conservative, not a proposed model of clinical cognition. A later design could use finer-grained conflict handling only after independent testing demonstrates that such handling cannot hide contradictory observations.

## Example (offline)

```python
from research_prototypes.ritual_interface.self_binding_modulator import (
    BindingCandidate, BindingMode, EvidenceMatch, SelfBindingModulator,
)
from research_prototypes.ritual_interface.state import IdentitySnapshot

state = IdentitySnapshot(
    subject_id="synthetic-subject", state_version=1, manifest_digest="f"*64,
    invariants=("identity:test",), relationships=(), commitments=("promise:test",),
    memories=(),
)
event = BindingCandidate(
    event_id="promise-cue", subject_id=state.subject_id, base_salience=.45,
    matches=(EvidenceMatch("promise:test", relevance=1.0),),
)
result = SelfBindingModulator().run(
    state, (event,), mode=BindingMode.NORMAL,
    expected_manifest=state.manifest_digest, expected_state_version=state.state_version,
)
assert result.proposals[0].proposed_salience == .50
```

The example uses artificial identifiers and no genuine Pretorius memories. The number `.50` is a deterministic score in a synthetic test, not a measure of identity strength.

## Controlled experiments and acceptance

`lesion_matrix` generates OFF/LOW/NORMAL/HIGH/SHUFFLED counterfactuals from precisely the same immutable state/candidates. The synthetic demonstration shows that an identity-linked event can overtake another candidate under HIGH, while OFF preserves baseline priority, and a verified contradiction freezes all bonuses. This is an **algorithmic sanity check** only. No LLM was evaluated, no prospective obligation was actually followed, no world state changed, and no persona-continuity improvement is claimed.

The primary eventual endpoint is independently rated, source-grounded decisions and world consequences under memory perturbation and relationship pressure. Proposed comparisons must control model family and version, world events, source references, retrieval and token budgets, external semantic matcher, candidate baselines, and sampling. Frozen-score differences alone cannot prove a causal behavioral effect. Include sealed cross-model probes, missing memories, hostile cues, and genuine relationship disagreement.

Promotion into the canonical `doctor_lives` runtime is **not authorized** by this implementation. It requires an explicit interface adapter through the UPPB/P3 boundary, unchanged legacy baseline, source/lesion held-outs, blind evaluator, performance and latency review, regression tests, and a new production gate. Any subsequent self-binding policy must be a bounded proposal and never a hidden way to reorder the subject's real world facts.
