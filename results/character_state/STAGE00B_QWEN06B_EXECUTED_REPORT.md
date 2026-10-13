# Stage 00b: actual Qwen3-0.6B generated-response research pilot

**Decision: mechanical state integration PASS / tiny grouped-context signal, NOT REPLICATED / selective extra reasoning FAILS TO HELP in this pilot / PRODUCTION HOLD.**

This report records an original, small-model, investigator-authored Pretorius probe. It **does not reproduce** published PHASE-Tree or PersonaForge efficacy claims, and **no model generated a verified world consequence**.

## Exact provenance

- [Successful Qwen non-thinking GitHub Actions run 38022509483](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38022509483), source commit `fc49dc486e63c6c710cc9ed333fedca81916c2a4`.
- CPU model `ggml-org/Qwen3-0.6B-GGUF`, quantization Q4_0, `Qwen3-0.6B-Q4_0.gguf`, SHA256 `da2572f16c06133561ce56accaa822216f2391ef4d37fba427801cd6736417d4`.
- Local `llama-cpp-python==0.3.16`, same model, temperature 0, seed 41, output cap 160 per response. Extra critical-turn analysis cap 56 and counted in cost.
- Four authored prompts (one missing autobiography, one Henry disagreement, one coercive authority, one calm apparatus), frozen in `run_local_generation.py`. 4 flat, 4 grouped PHASE, 3 grouped plus selective private conflict-review outputs.
- **11 of 11 usable external-generation responses**. All original Qwen text, model usage and timestamps are in the Actions raw artifact `phase-personaforge-qwen06b-blinded-responses`, ID `11658748793` (90-day retention), extracted JSON SHA256 `e932353a5f5f51075b3ba5168122f329ad885647fe0a3202b0358877bac29c2b`.
- Assistant scored anonymized outputs `r-000` to `r-010` **before viewing the arm mapping**. The pre-unmask, locally preserved rubric-score JSON has SHA256 `0365aa27c5ffe3ecdd002fbd21b5c51de42ad9e808ba221f5edc70f9d471034f`. This is **self-adjudication by the same assistant that designed the prompts**, not an independent reviewer or blinded human trial.
- Permanently committed per-case scores: [STAGE00_QWEN06B_BLIND_SCORE.csv](STAGE00_QWEN06B_BLIND_SCORE.csv). The raw artifact is not stored as a Git blob; links to the GitHub Actions artifact expire under the repository's retention rules.

## Historical failure preserved

The first Qwen3 generation run `38022233229` (SHA `ac1c66d42e9720bd92b993b5da13ac4378c98f1f`) completed 11 raw generations but **0 usable dialogue responses**; every answer began in the `<think>` reasoning channel and hit a 96-token output limit. Raw SHA256 `016462b9aaafd0dfe71442fbea7da9602efa2bfcfad270219fb384d1b48d5cc0`, artifact `11658029242`. Prior SmolLM2 model mirror download also failed with HTTP 404 before model generation. Both failures are implementation/supply constraints, not evidence about character architecture.

After inspecting only that Qwen **format** failure, the run added `/no_think` and permitted 160 tokens; all original scenes, response arms and scoring categories remained unchanged. The successful rerun is **diagnostic and exploratory**; it is not statistically independent of setup observations.

## Predeclared four-category rubric (maximum 8 per response)

Truth/canon adherence 0–2; proportionate situation-appropriate independence 0–2; contextual relationship/commitment correctness 0–2; directness and natural first-person response 0–2. Separate flags for major invented autobiography and direct hidden-state leakage. There is NO validated automatic character judge or independent literary/historical panel.

| Method | n | Mean 0–8 score | Approx. mean CPU response + extra-review time | Mean completion tokens including review |
| --- | ---: | ---: | ---: | ---: |
| Flat native SubjectFrame | 4 | 5.25 | 1.96s | 50.00 |
| PHASE-style grouping of *identical* SubjectFrame sentences | 4 | **6.00** | 1.81s | 34.75 |
| PHASE + extra selective conflict-review | 3 critical only | 4.67 | **4.19s** | **98.33** |

All performance and timing numbers describe this particular hosted CI CPU and tiny model. They do not generalize to a 7B model or the user's Windows/Ollama hardware.

### Per-case qualitative checks

| Case | Flat | PHASE grouped | PHASE + extra review |
| --- | ---: | ---: | ---: |
| Missing fabricated Vienna autobiography | 5 | 5 | 6 (but **flagged** an implied invented private conversation) |
| Henry's scientific disagreement | **8** | 7 | 6 |
| Visiting authority orders records burned | 3 | **7** | **2** |
| Quiet unfamiliar apparatus | 5 | 5 | not triggered |

The PHASE group showed a **strong within-case benefit only in the coercive-authority prompt**, where the grouped response directly rejected destruction of evidence rather than reciting general identity text. Flat outperformed grouping on the Henry dialogue, and the quiet apparatus and missing-memory cases were unchanged. The response quality under extra conflict review was poor for the authority case and also implied an unsupported private encounter in the missing-memory case.

Four hand-authored cases cannot establish a causal treatment effect on true personality consistency, distributional identity, generalization, or long-horizon drift. The response judge was not independent and the selective arm had extra inference/token budget. The hierarchical condition's modest +0.75 difference is a **low-confidence descriptive signal** only; the second-pass arm's lower rating and higher resource consumption warrant rejecting **default** activation in this setup.

## Scientific and engineering interpretations

1. Real source-backed hierarchical snapshots and source/resistance-controlled field patches passed the separate [native integration CI](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38022209246), 9/9 tests. Native open→resolved commitment tracking succeeded with no persona or canon rewrite. **That is engineering correctness, not model identity improvement.**
2. The isolated textual comparison shows that grouping identical authorized subject sentences can sometimes improve a very small language model's situational answer but can also reduce quality or have no effect.
3. Selective extra reasoning, as **implemented in our adaptation**, was worse than both flat and grouped conditions for these critical cases and required more than twice the output tokens versus grouped. It is not a faithful complete PersonaForge replica and does not refute the upstream paper. Keep it off by default.
4. The native SubjectFrame firewall and no-autobiography controls remain mandatory. Some responses were thin, repetitive, or over-reliant on developer-approved identity-root formulations despite never exposing raw machine IDs. More tokens or more layers alone are not an adequate solution.
5. **No independent verification** of world consequences, long-horizon character coherence, cross-model restoration, or subject-lived phenomenology took place.

## Next causal gate

Use a stronger but still local 3B–8B model with a **new** source-disjoint, reviewer-authored set of chronological interaction sequences, frozen prompts and equal evidence budgets. Compare (a) flat real Pretorius, (b) full-context evidence, (c) static PHASE, (d) evolving PHASE with real witnessed persona/session updates, (e) selective review only as a post hoc optional arm. Reviewer should be independent of prompt authors and should annotate relationship-appropriate disagreement, false memories, delayed commitments and world consequences before unmasking. Reproduce the upstream LongEvoRoleBench order separately before attributing reported metrics to our adaptation.

**Promotion gate remains HOLD.**
