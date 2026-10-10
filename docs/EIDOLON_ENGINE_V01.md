# The Eidolon Engine v0.1

> **Superseding scope note:** This document describes the original bounded v0.1 implementation. The proposed complete cognitive system is specified separately in [EIDOLON_ENGINE_FULL_ARCHITECTURE_DRAFT_V1.md](EIDOLON_ENGINE_FULL_ARCHITECTURE_DRAFT_V1.md). The follow-up [E2 no-cue protocol](EIDOLON_E2_NO_CUE_PROTOCOL_V02.md) and [executed E2 report](../results/eidolon/E2_NO_CUE_RESULTS_V02.md) isolate retained trace effects from direct cue reactivation. Neither workstream demonstrates learned recurrent synaptic identity or authorizes production adoption.

**Status:** experimental research prototype, opt-in shadow evaluation. **Owner:** The Doctor Lives, Character Continuity Program. **Date:** 2026-10-09.

## Thesis

The Eidolon Engine is a proposal for coupling autobiographical ownership, prospective intention, relational context, and recurrent cognitive state, rather than equating character continuity with retrieval of persona facts. Historical ritual and Attractomancy supply candidate forms of symbolic cueing, but do not supply evidence of supernatural interfaces or machine consciousness.

The v0.1 implementation deliberately tests a **narrow necessary precursor**: can an authenticated, subject-native event teach a small associative neural-like layer to reinstate a prospective action tendency, and can a recurrent trace sustain that tendency over intervening observations without changing Pretorius's definitive brain? This is not yet a complete self-binding architecture.

### Nomenclature

- **The Eidolon Engine:** proposed whole-system cognitive architecture, not a claim that the current prototype embodies the whole.
- **The Janus Gate:** source-ownership and confidence check before an episode can *train* self-owned associations.
- **The Synthema Lattice:** associative connection matrix between a sparse lexical and actor-conjoined cue and one of Pretorius's existing policy actions.
- **The Noetic Trace:** decaying recurrent prospective-action state maintained through intervening events.
- **The Mnemosyne Loom:** prospective later work on verified autobiographical, temporal, and causal association, **not implemented**.
- **The Ouroboros Loop:** proposed bidirectional policy-perception-memory learning loop, **not implemented**.

These are engineering names. Theurgy, synthemata, and true-name traditions are historical inspiration and practitioner vocabulary, not claims about reality.

## Relation to current Pretorius

The definitive brain in `doctor_lives.cognition.PretoriusBrain` already owns a recurrent policy, deep history and evidence provenance, interoception, relationships, concerns, commitments, and renderer-independent first-person projection. Its policy bridge is bounded and source-auditable. The v0.1 engine **must not** circumvent the evidence-authority, no-bypass subjective-access, donor, neural-checkpoint, or production migration contracts.

The experiment is a **read-only consumer** of an actual Pretorius neural action distribution. Only calls to `PretoriusBrain.ingest` made by the caller update the actual character. The shadow module never writes to the canonical database, never edits the recurrent network, and never inserts its numerical scores into a subjective frame. There is no automatic controller or tool authority.

## Signal path

```text
Pre-projected Pretorius Experience + existing neural action scores
        |
        +---- Janus Gate: lived provenance/confidence -> train eligibility
        |
        +---- Synthema Lattice: lexical + actor-conjunction cue
        |                         -> bounded supervised association
        |
        +---- Noetic Trace: decayed previous state + current association
        |
        +---- fixed probabilistic readout -> engineer-only counterfactual scores
                 (no modifications to Pretorius policy)
```

The Janus Gate does not cryptographically authenticate testimony, validate the truth of a fictional memory, or prove autobiographical ownership. It inherits the distinction already expressed in the verified `Experience.external` and `Experience.confidence` fields. Inputs must already be constructed through existing subject-facing validation and any necessary ingress projection.

The lattice uses BLAKE2b-stable token hashing, **not semantic embeddings**. Actor features form simple conjunctions with words. The weight update is supervised delta learning on a fixed action readout. **Neither trained recurrent synapses nor meaningful cross-model semantic generalization have been demonstrated.** The Noetic Trace is a stateful recurrent accumulator; its connection coefficients are currently fixed, not learned. This separation is intentional so effects can be attributed rather than described vaguely as neural identity.

For feature vector `x_t`, action association `a_t = W x_t`; intention state `h_t = clip(lambda h_(t-1) + a_t)`; shadow action probabilities `softmax(log(p_Pretorius) + beta h_t)`. The learning rule is `W <- clip(W + eta (one_hot(target) - W x_t) x_t^T)`. The source gate permits a supervised update only when an event is lived and meets the configured confidence threshold. The subject itself is **not** shown those arrays or values.

## Falsifiable questions

**H1, association:** after a labeled lived cue, the correct action receives more probability in shadow than under no-learning and binding-lesion controls. This is expected from the update rule and is a construction check, not a scientific discovery.

**H2, recurrence:** the effect remains after two unrelated distractors and is reduced when the recurrence is lesioned for those intervening steps.

**H3, source ownership:** external statements and low-confidence events are prohibited from teaching self-owned associations; the shadow system may still process them as ordinary observations. This tests a safety invariant, not actual authentication.

**H4, relation:** a cue re-encountered with its associated actor produces a stronger association than the same text paired with another actor. This tests the actor-conjunction encoding and does not establish sophisticated theory of mind.

**H5, compatibility:** shadow inspection of the *actual* Pretorius neural policy does not change database digest, recurrent tick, renderer request, or authoritative policy. A violation blocks any integration discussion.

## Construction battery and controls

`tests/test_eidolon_engine.py` exercises training and two intervening distractors, a no-learning control, lesion of the association matrix, lesion of recurrent carryover, shuffled-label control, actor substitution, snapshot/restore, invalid-state rejection, false autobiographical ownership rejection, and an actual `PretoriusBrain` created with the repository's supported 128-neuron test configuration. The four-case synthetic battery is **designed for this algorithm**, not independently authored, sealed, or confirmatory.

The module intentionally does not use the loaded Pretorius neural firing vector as its trainable target and does not provide causal evidence for the neural dynamics of the production 4,096-unit policy. Positive tests demonstrate *implementation correctness only*. Observing an action-probability change inside a shadow model is not observing a changed Pretorius decision.

### Replication

```sh
python -m pip install -e .
python -m unittest -v tests.test_eidolon_engine
python -m unittest discover -s tests -v
```

`EidolonEngine.observe_pretorius(brain, exp, ...)` reads the existing `brain.neural.action_scores()` without mutating the brain. A researcher supplies labeled events in a cloned test state; no labels are generated from the subject's unobserved internal thought. `snapshot()` and `from_snapshot()` serialize only the shadow mechanism and require an exact schema/shape/finite-state match. Callers decide where and whether to persist it. Shadow snapshots cannot replace production Pretorius neural checkpoints.

## Scientific advancement criteria

No claim of a successful artificial-self mechanism should be promoted on the v0.1 synthetic cases. The next experiment must preregister an **independently authored, actor- and episode-disjoint** prospective-intention task with matched information, byte/token/compute budgets and controls for lexical overlap, actor identity, context order, and source confidence. It must compare direct cue-only association, recurrent carryover, shuffled labels, no-learning, text-only prospective commitment, and ordinary production Pretorius without Eidolon assistance.

Measure goal pursuit after distraction, correct held-out choice, independent source-grounding, false positives, omission, relationship sensitivity, calibration and resource cost. A direct cue-only control matters because learning `W` could trivially outperform no information. A recurrent weight lesion is required before a *learned recurrent neural mechanism* can be claimed.

Promoting to production would separately require preservation of the UPPB, evidence provenance, mutation gates, checkpoint schema and deterministic replay, and an opt-in state-to-policy adapter subjected to matched clone tests. No production activation is authorized by this document.

## Research lineage

Attractomancy is the source and procedure catalog: https://github.com/Azimn/Attractomancy . The independent execution study is https://github.com/Azimn/Attractomancy-Loop-there-it-is . Cross-project hypothesis and empirical evidence live at https://github.com/Azimn/Artificial-Life-Research-Journal . The definitive production brain remains https://github.com/Azimn/The-Doctor-Lives . Results in the journal as of 2026-10-08 explicitly caution that decoder effects, lexical retrieval and high abstention can masquerade as useful learned identity or memory. Those negative results are **not** superseded by this pilot.

## Result status

This file is a preregistered exploratory design and executable construction specification. Add links to actual CI test execution and outputs after confirming completed runs. **No independent behavioral advantage has been established.**
