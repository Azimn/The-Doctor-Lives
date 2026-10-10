# Eidolon Engine v0.1.1, Unicode symbolic-cue follow-up

**Status:** executed exploratory implementation test. The original v0.1 findings remain preserved at [PILOT_V01_RESULTS.md](PILOT_V01_RESULTS.md), including the original CI SHA and probability values. This follow-up adds Unicode-aware word and symbol features to the Synthema Lattice without changing the frozen production Pretorius brain.

## Provenance

[GitHub Actions run 38022599281](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38022599281) passed **11/11 targeted tests**, including a new controlled symbol substitution test distinguishing `🜁` from `🜂` in otherwise identical prose. The executable construction assay emitted [artifact 11658579169](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38022599281/artifacts/11658579169), SHA-256 of archived ZIP `3743d716cac3633404601f44e289bb042b292a8ce8835ab4089fd3f8c58d277f`. Test head commit `23430db1822bc80c2c185ac7156d1b22aa4db014`; [per-case permanent transcription](UNICODE_ASSAY_V011.json) preserves these results separately from v0.1.

## Results in the original four controlled cases

| Condition | Correct top-1 | Mean target probability |
| --- | ---: | ---: |
| Intact | 4/4 | 0.323679438 |
| No learning | 0/4 | 0.100000000 |
| Binding lesion | 0/4 | 0.100000000 |
| Recurrent-state lesion | **4/4** | **0.121655562** |
| Shuffled label | 0/4 | 0.075146729 |

The real Pretorius shadow integration was unchanged: live Pretorius baseline `create` probability 0.105365660, shadow immediately after learned cue 0.416057682, shadow after one distractor 0.462066035; the subject database digest and recurrent tick were unchanged by the shadow interface.

The glyph test establishes that the character-facing validated text can carry distinct Unicode symbols and that the engineered feature encoder distinguishes them when the rest of the prose is identical. It **does not** show symbolic semantics, occult efficacy, non-lexical personhood, or model-general transfer. The direct feature pathway continues to produce 4/4 top-1 scores even when recurrent carryover is lesioned, so independent recurrence-dependent functional value remains unproven.

The revised encoder altered several numerical values in the construction assay, so do not average v0.1 and v0.1.1 or claim that the original results were unchanged. Both runs are preserved for longitudinal provenance. Repeating a synthetic dataset after a feature revision is regression testing, **not independent replication**.

**Disposition:** maintain draft research status; no merge to production until independent causal/semantic tests and migration review.
