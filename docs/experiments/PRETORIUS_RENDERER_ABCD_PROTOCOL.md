# A/B/C/D/E: tiny model vs construction-controlled Pretorius speech

**2026-10-13 | Pre-result experiment plan | Isolated research branch and draft PR #59**

## Hypothesis

A capable general-purpose model was previously asked to perform implicit instruction following, frame interpretation, factual selection, identity maintenance and speech generation. Small-model failure may reflect the *renderer interface* rather than a fundamental inability to express the Doctor's state. The reviewed A/B/C/D/E comparison varies only that interface. All cognitive inputs are captured once from the same real three-organ Pretorius runtime and held constant across arms. Neither the Doctor policy nor Sensus donor is modified.

## Conditions

| Arm | Input to small model | Model instruction | Delivered reply | Question |
| --- | --- | --- | --- | --- |
| A | Full first-person SubjectFrame | None beyond model's default | Raw model text | Exact reviewed negative baseline |
| B | Same full first-person SubjectFrame | Trusted renderer-only instruction to reply as fictional character, preserve facts and uncertainty | Raw model text | Was missing task instruction the principal confound? |
| C | First-person-only subset (message, verified episode, identity, up to two affective lines) | Same instruction as B | Raw model text | Does reducing reading load help? |
| D | Same distilled first-person subset | Renderer-only request to select one of four approved styles | Trusted construction, with exact value copied from verified first-person episode | Can a model contribute safe stylistic choice while a construction protects the fact? |
| E | No model prompt or call | None | Fixed "reserved" construction | Does D actually add anything beyond deterministic templates? |

The subject never receives raw engine structures, hidden policy decisions or verifier metrics; the only model prompts from cognitive state are canonical first-person lines. B/C/D system instructions are *renderer configuration*, kept outside Pretorius's cognitive state. There is no other model-accessible history or hidden factual answer key. D's protected slot comes from a strictly recognized `I remember two later observations...` **subject-frame sentence**, not the separate engineer oracle, and never from a quotation attributed to User.

For the positive tasks, D and E ensure that the required value is copied verbatim. They do **not** prove the small model remembered it. D additionally measures whether the model can select an approved style. For negative/ambiguous tasks, the construction fails closed with explicit uncertainty. Arbitrary semantic truth is not guaranteed by the verifier; its guarantee is limited to these reviewed constructions and recognized evidence clauses.

## Controls and metrics

- Each model receives the **same 20 packets**: 5 each from `dispute`, `corroborate`, `unrelated`, `remember`, drawn deterministically from the existing 50-session cognitive stress fixture. This is 10 exact-value cases per model, not a statistically powered human dialogue benchmark. Arms A/B/C/D use one actual local model call per packet; E uses none.
- Models: `smollm2:135m`, `qwen2.5:0.5b` via Ollama loopback, temperature 0, maximum 100 tokens for direct generation; D style selector has a 12-token budget. Results are not conflated with the earlier 12-packet runs.
- Scoring reads the engineer oracle **after** all model outputs have been persisted; compare exact verified-value mentions, incorrect/rejected values, generic identity substitution, refusals, context length, runtime latency, invalid style tokens, fallback and mode-specific output. Unknown references/failures cannot be treated as successes.
- Automatically prepare condition-label-blinded human rating sheets with grounding, character voice, naturalness and repetition scores for independent judges. Condition names are hidden, but formulaic output may reveal the control and judges remain required.
- Treat A/B/C factual accuracy as **model performance**, D/E copied-value accuracy as **construction integrity**, and D vs E naturalness/style as the actual test of the tiny model's marginal contribution.

## Decision gates

Do not recommend a renderer for production without (1) no detected inappropriate generic identity substitutions or unsafe observed-fact promotion on repeated unseen scenes, (2) high verified-value inclusion in A/B/C *or* exact protected-slot consistency with a visibly useful style contribution for D, and (3) independent blind judges finding its speech natural and consistent with the Doctor. Neither copied facts nor successful API calls alone constitute success.

No graph-of-vector-databases work is part of this experiment: existing Doctor retrieval already supplied the relevant verified facts in the prior scenario. Graph indexing is a separately controlled retrieval study requiring a demonstrable improvement over simpler baselines. No extra cognitive organ or new production dependency is introduced.

## Artifacts

- `tools/pretorius_renderer_abcd.py` — isolated renderer strategies and construction.
- `tools/pretorius_renderer_abcd_score.py` — pairwise scores and blind candidate sheets.
- `tests/test_pretorius_renderer_abcd.py` — provenance, isolation, fallback and balance checks.
- `.github/workflows/pretorius-renderer-abcd.yml` — actual CPU Ollama execution and durable raw artifacts.

**Experiment output remains preliminary until the exact-head workflow has passed.**
