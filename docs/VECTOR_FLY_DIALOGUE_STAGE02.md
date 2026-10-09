# Vector Fly Pilot 01, Stage 02: actual matched Pretorius dialogue

**Research status:** engineering-real dialogue test with local CPU-only Ollama, not proof of character continuity or biologically specific memory. Continue the [Stage 01 structural A/B protocol](VECTOR_FLY_PERSONA_AB_PILOT01.md), not a new source corpus.

## Fixed experimental conditions

The actual `PretoriusBrainPort` supplies exactly the same private state, frozen subject frame and user question to both arms. A has no external reconstructed autobiography excerpts. B includes the original 450-event source-verified Vector Fly top-three matching excerpts from the already-pinned L2 v2 TF-IDF index. The experiment uses the original immutable Pretorius source Git blob `718dcc2d5ba4feccdef1690d447edfcebaa9bfb5` and a **separate external evidence slot**, never `brain.ingest` or a promotion to lived experience.

The renderer is `qwen2.5:0.5b-instruct`, downloaded from Ollama with the runtime model manifest digest recorded. The workflow downloads pinned Ollama release v0.34.0; it requires its Linux binary archive SHA256 `cf95886728959aa09910bb34de5cca1cc5a8f68003b5597197d3f2c2d57c0804` before executing. The exact model content digest is persisted from `/api/tags`, so a later tag retarget cannot silently claim to be the same run.

Both conditions use `temperature=0`, `seed=1842`, `num_predict=320`, and `num_ctx=8192`. A/B order is counterbalanced across six cases. The renderer cannot contact any paid API. This tiny 0.5B model has limited reasoning and literary style ability; this experiment is **proof of execution under a constrained renderer**, not expected high-quality Pretorius dialogue.

## Procedure

1. Check out `Azimn/Pretorius-Connectome` at pinned source version `2bcdcaeac7dbb57af621a7c4ffa4a95fc425b5bc`, install required Python libraries, and rebuild the verified 450-memory SQLite lexical index.
2. Start the local read-only Vector Fly HTTP API on 127.0.0.1:8765, validate original 450-source record coverage and each vector posting.
3. Start the pinned CPU-only Ollama instance on 127.0.0.1:11434, pull the explicit model, and record model/runtime digests.
4. Run the actual `tools/run_vector_fly_ab.py --ollama-model qwen2.5:0.5b-instruct` on a fresh isolated copy of the production Pretorius brain. Every trial uses the identical brain source state. Never use a player's live account or lived memory for the test.
5. Save both full answers and exact prompt/record provenance in the private-by-default local output or GitHub Actions artifact. Run `tools/summarize_vector_fly_dialogue.py` to verify exactly twelve responses, paired seed/model provenance, source-state invariance and changed-vs-identical text.
6. Report the actual nonempty response count and any failed/empty answers. Do **not** use response difference or lexical overlap as factual truth, personality consistency or improved recall.

## CI

[Real CPU-only renderer workflow](../.github/workflows/vector-fly-ollama-dialogue-stage02.yml) provisions a fresh GitHub Actions runner, verifies Ollama binary bytes, downloads a roughly 398 MB model and generates twelve answers with the existing six **previously examined** source-specific/contradiction/absent probes. The run stores `DIALOGUE_RAW_AB.json`, `DIALOGUE_MEASURED.json` and `OLLAMA_MODEL.json` as workflow artifacts. It may take substantial runtime on a CPU. A successful workflow does not mean the replies were correct.

### Human evaluation and stronger scientific trial

Before claiming genuine improvement, collect at least 30 previously unseen, independently drafted questions. Keep answer/source keys outside the renderer prompts, match renderer version/model and brain state, blind human reviewers to A/B source condition and rate supported biographical facts, invented assertions, contradiction/absence rejection, source class attribution, consistency across rephrasings and latency. Analyze paired outcomes and negative cases; post-hoc six probes must be reported only as smoke tests.

**Do not claim FlyWire biological topology benefits from Stage 02.** Both A and B use lexical retrieval. A later C vs rewired comparison must use the exact same lexical candidate set with preserved rankings and biological graph provenance.

## Current evidence

Stage 01 already passed live-source integration but produced no model answers: [Stage 01 report](../results/vector_fly/PILOT01_RETRIEVAL_INTEGRATION_RESULTS.md). Stage 02 results must be added to the permanent [vector-fly results directory](../results/vector_fly/) only **after** the actual local-model workflow completes. Document failures exactly; do not infer results from workflow configuration.