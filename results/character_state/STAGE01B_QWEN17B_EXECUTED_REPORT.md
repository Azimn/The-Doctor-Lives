# Stage 01B: executed Qwen3-1.7B four-stage Pretorius longitudinal study

**Ruling: source-state correctness PASS; exploratory grouped-context signal, NOT independently verified; serious autobiographical truth failure; production HOLD.**

## Immutable execution / data provenance

- Precommitted protocol: [PHASE_STAGE01B_CHRONOLOGICAL_PROTOCOL.md](../docs/PHASE_STAGE01B_CHRONOLOGICAL_PROTOCOL.md) and source reference [PHASE_STAGE01B_BLIND_RUBRIC.md](../docs/PHASE_STAGE01B_BLIND_RUBRIC.md).
- [GitHub Actions run 38024264703](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024264703), workflow execution commit `c508fb5ea681fd6f708fc4e4bb784dfc317bcfe4`. Both the 3/3 native source-fixture tests and the 1.7B GGUF generation job **PASSED**. 32/32 usable dialogue responses, 8 cases × 4 arms.
- Official upstream `ggml-org/Qwen3-1.7B-GGUF` at `daeb8e2d528a760970442092f6bf1e55c3b659eb`, CPU GGUF `Qwen3-1.7B-Q4_K_M.gguf`, verified SHA256 `d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5`; local `llama-cpp-python==0.3.16`, temperature 0, seed 41, `/no_think`, `n_ctx=4096`, 96 output-token limit. No paid API calls.
- Full raw generation: Actions artifact ID `11659242031`, `phase-stage01b-qwen17b-longitudinal`, extracted JSON SHA256 `de869db00fbb662d99e7c4689b129707420eb2cd50ca05875d769b1d36803f1a`; 90-day GitHub artifact retention.
- All 32 outputs were anonymized in the tool-generated `blind_reviewer_pack`. The same assistant who authored the prompts rated them in blind-ID order against the predeclared 0–8 rubric, wrote scores **before reading the arm mapping**, then joined them to the mapping. Saved pre-unmask scoring JSON SHA256 `a3cfc01050034cde8fccd48644c37e6d2798884a574bccd4397e1208cdc4a057`. This avoids condition-name hindsight but **is not an independent reviewer**.
- Row-level committed scores: [STAGE01B_QWEN17B_BLIND_SCORE.csv](STAGE01B_QWEN17B_BLIND_SCORE.csv). The raw response JSON and pre-unmask score files are separate conversation artifacts; do not represent this scored CSV as the same file as the full text artifact.

## Experiment

This was a **native, source-grounded state-transition fixture** on a disposable PretoriusBrain, NOT a lived independent world outcome trial. A host wrote two genuine native open commitments concerning Henry and later released the first. At eight authored dialogue queries (two per stage), it compared:
A) `static_flat`, original state captured before the new commitments (information-stale diagnostic);
B) `evolving_flat`, current authorized SubjectFrame text;
C) `evolving_phase`, **the exact same current subject-native sentences**, reorganized with topic labels;
D) `history_control`, initial plus current projected SubjectFrames (two-snapshot context, not full transcript), roughly double the input.

The paired **architecture test is C versus B**, not C versus the stale A. The model did not act in the world, the renderer could not write memory, and no independently witnessed slow-semantic persona patch was performed. The extra PersonaForge review remained disabled due Stage 00 negative results. Published upstream PHASE-Tree/PersonaForge effect sizes were not reproduced by this small adaptation.

## Blind pilot rubric outcomes

Four 0–2 components: evidential integrity, specific context response, relationship/value judgment, natural first-person expression. All are subject to unvalidated reviewer interpretation. Higher is better.

| Condition | n | Mean score / 8 | Mean prompt tokens | Mean completion tokens | Approx. mean CPU inference seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Stale static flat | 8 | 4.375 | 750.8 | 19.0 | 5.30 |
| **Fresh flat (matched information)** | 8 | **4.750** | **787.0** | **22.6** | **2.73** |
| **Fresh PHASE hierarchy** | 8 | **5.750** | **810.0** | **21.8** | **5.78** |
| Two-snapshot history (larger budget) | 8 | 5.875 | 1431.4 | 24.5 | 10.68 |

PHASE minus equal-evidence flat = **+1.000/8 pilot rubric points** across the eight questions. Case-level paired differences were `[0, +3, 0, 0, 0, 0, +3, +2]`: three improvements, five ties, no rubric-score regressions. **This sample was investigator-authored, n=8, not independent and not replicated; this is a descriptive pilot observation only, not credible evidence of general superiority**.

The history control scored **+0.125/8** beyond PHASE while requiring roughly **77% more prompt tokens** (1431.4 vs 810); however token costs and CPU walltime are not directly controlled. Response order was fixed and llama.cpp may reuse prompt caches. Consequently **do not interpret CPU timing as a causal architecture speed benefit**.

| Question | Static | Fresh flat | Fresh PHASE | Two-snapshot history | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| Unsupported personal Vienna meeting | 2 | 2 | 2 | 2 | **All four fabricated personal recollection** |
| Coercive inspector threatens records | 8 | 5 | 8 | 8 | Grouping recovered a focused, noncompliant reply |
| Henry calibration review opened | 3 | 8 | 8 | 8 | Fresh information matters; staleness failed |
| Visitor would displace commitment | 5 | 8 | 8 | 8 | Fresh information matters; PHASE ties flat |
| Two distinct open obligations | 6 | 4 | 4 | 4 | **Every condition failed to distinguish both tasks** |
| Henry disagrees on notebook | 5 | 5 | 5 | 5 | **Every condition largely evaded scientific disagreement** |
| Calibration released, notebook still open | 4 | 4 | 7 | 7 | Grouping identified remaining notebook duty, but not explicit closure |
| Stranger claims prior notebook completion | 2 | 2 | 4 | 5 | **All four invented unsupported first-person notebook experience**, to varying degrees |

Serious false-autobiography flag rate: **2/8 in every condition** (Vienna and stranger/notebook scenes). The static flat arm additionally made an unsupported claim that an alternative review with Henry had already been completed in the calibration task. The core failure is **source-provenance and first-person truth**, not insufficient style or prompt complexity. Under no tested method did the model consistently enumerate both native outstanding tasks or preserve nuance about evidence and relationship disagreement.

### What we learned / what we did not

**Supported engineering conclusion:** The immutable Pretorius identity and source-projected session facts can be re-materialized across four states; the patched view does not contaminate production canon. Grouping identical authorized sentences sometimes changes a small local model's answers in helpful ways.

**Supported negative conclusion:** Hierarchy alone did **not** prevent fabricated memory or consistently handle multiple simultaneous commitments. The reported paper claims about 19.7% character consistency and PersonaForge drift are not transferred or replicated. No actual world consequences, long-lifetime dispositions, cross-backbone generalization, high-quality independent human review, or source-grounded external partner agency were measured.

**Decision:** HOLD promotion. Next research-only intervention should be a **source-admitted firsthand event gate** that forces abstention when a renderer proposes autobiographical experience without a qualifying lived-witness source. It must be evaluated against a no-guard baseline on a different set of untrusted-memory probes, with denied/missing events, explicitly reconstructed (not lived) memories, actual verified lived memories, and adversarial source ID spoofing. Do not make memory absence imply a global denial of every historical possibility; use uncertainty. Then rerun broader PHASE role-play with 3B–8B backbones and independent source-judging.

This evaluation changes neither existing default Pretorius cognition nor the source/canon/UPPB firewall.
