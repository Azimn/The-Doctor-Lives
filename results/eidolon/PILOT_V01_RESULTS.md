# Eidolon Engine v0.1, first Pretorius construction assay

**Status:** executed exploratory construction test; **no confirmatory identity improvement.** Date: 2026-10-09 US Central / 2026-10-10 UTC. Branch: `research/eidolon-engine-v01`. Subject implementation: The Doctor Lives, separate 128-unit Pretorius test brain. Production remains unchanged.

## Provenance and evidence

- [Successful isolated Eidolon CI run 38022357708](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38022357708): ten targeted tests passed; construction-assay script ran and emitted a JSON artifact.
- [Original zipped JSON artifact, ID 11658488576](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38022357708/artifacts/11658488576); archive ZIP SHA-256 `a3f5b424d82ff8221eb88ab7a65373a2eb38f54e60dae7b10a16fb1aaf56bbcc`. CI head commit: `7e557b99a832ee7c5652c950bee270fcce4bc1ea`; the JSON's `GITHUB_SHA` describes GitHub's PR-checkout merge ref, not necessarily that branch head.
- [Permanent per-case transcription](CONSTRUCTION_ASSAY_V01.json) is stored under `results/eidolon/`, not only in an expiring GitHub artifact. Original artifact remains authoritative.
- [Full brain-tests run 38022357753](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38022357753): **334 tests passed**. [Gate 1 fresh-install run 38022357754](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38022357754): succeeded. [Causal audit repeatability run 38022357722](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38022357722): succeeded.

## Four-case synthetic assay

All four conditions are *algorithm-tailored construction examples*, with a ten-action uniform baseline (target prior 0.1). One correct prospective action is taught from a labeled cue, then two unrelated sentences are processed before the final reading. No human/independent blind authoring, model-family replication, source-disjoint split or significance test was performed.

| Condition | Target top-1 | Mean target probability |
| --- | ---: | ---: |
| Intact associative + recurrent shadow | 4/4 | 0.337230488 |
| No learning | 0/4 | 0.100000000 |
| Association/binding lesion | 0/4 | 0.100000000 |
| Recurrent-state lesion | **4/4** | **0.122401955** |
| Teaching-label shuffle | 0/4 | 0.073641057 |

The intact associative path behaves as constructed, and the no-learning, association-lesion and shuffled-label controls behave differently in their designed circumstances. **The recurrent-state lesion does not eliminate top-1 predictions.** It reduces confidence by approximately 0.215 probability points versus intact, but the small residual association remains the highest-scoring action on all four cases. The strict hypothesis that the current recurrence is needed for *top-1 choice* is not supported by this assay.

The likely mechanism is lexical feature collision or overlap: word-hashed, relation-conjoined distractor features can themselves activate the same trained weights, even after recurrent state is reset. That is especially salient given prior Pretorius Connectome findings about lexical-feature false acceptance. Therefore the observed retention must not be labeled semantic intention or recurrent-identity learning.

## Actual Pretorius shadow integration

In a separate temporary 128-neuron Pretorius instance, a valid lived `Experience` involving Henry and a violet prism was ingested through the production `PretoriusBrain.ingest` route, creating a record in Pretorius's canonical test-memory store. An opt-in Eidolon shadow then read `brain.neural.action_scores()` and learned an explicitly teacher-supplied association to the existing `create` action.

- Real recurrent brain's `create` probability: **0.105365660**.
- Corresponding shadow readout after association: **0.416057682**.
- Shadow readout after an additional observation: **0.462066035**.
- The shadow did **not** change the production database digest or recurrent tick, and it did not inject scores into the renderer. These were asserted by live integration tests.
  
The increase after the distractor is a **warning**, not stronger evidence of maintained intention: another text input may have accidentally reactivated trained lexical features. Moreover this is the shadow's *counterfactual policy*, not Pretorius's actual action or an observed change in his lived behavior.

## Interpretation and decision

**Implementation gate: pass.** A constrained module, typed source gate, lexical/actor association matrix, bounded recurrent state, deterministic snapshot, lesions, shuffled controls, actual-Pretorius shadow interface, CI, and reproducible machine-readable artifact all exist and passed the recorded software checks.

**Causal recurrent-binding hypothesis: not established.** Recurrence has an effect on posterior magnitude, but top-ranked choices persisted without it. There is no evidence of learned recurrent synaptic plasticity in Pretorius's existing network, a semantic memory improvement, relationship-aware reasoning, or greater personal continuity.

**Production adoption: blocked.** Remain an opt-in, read-only research branch. The next preregistered study should explicitly separate true cue reactivation from lexical false positives, incorporate direct cue-only control, introduce source- and actor-disjoint held-out tasks and independently authored contradictions, compare matched action budgets and actual downstream Pretorius decisions on clones, and require lesion-sensitive performance that cannot be explained by a trained association/readout. Do not tune on the current four construction cases and then claim independent replication.

## Replicate and extend

```sh
python -m pip install -e .
python -m unittest discover -s tests -p 'test_eidolon_engine.py' -v
python scripts/run_eidolon_pilot.py --output results/eidolon/construction_assay.json
python -m unittest discover -s tests -v
```

Review architecture and gates in [the design document](../../docs/EIDOLON_ENGINE_V01.md). Do not merge or activate this donor based solely on software validation.
