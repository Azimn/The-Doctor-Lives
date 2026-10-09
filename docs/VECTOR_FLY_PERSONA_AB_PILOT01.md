# Pilot 01: Does Vector Fly autobiographical retrieval affect the definitive Pretorius?

**Phase:** staged reproducible A/B test of external archival retrieval into the production renderer request, not a test of autonomous consciousness or a claim of improved memory.

## Why this architecture matters

`The-Doctor-Lives` owns the production Pretorius cognition, recurring state, behavioral tendencies, lived memories and renderer-protected Subject Frame. `Pretorius-Connectome` owns the original 450 reconstructed autobiographical events, canonical source IDs, source metadata, reproducible TF-IDF and indexed vector search.

Importing a retrieved reconstructed entry as a new lived `Experience` would break the canonical/lived distinction and contaminate the brain's autobiography. **Do not do this.** The pilot routes source text through an **external read-only evidence slot** of the renderer packet. It does not call `brain.ingest`, write to `brain.sqlite3`, alter synapses, create commitments or authorize the LLM to update memory.

## Conditions and frozen inputs

**A, control:** same production Pretorius brain and subject frame, question and renderer. External historical archive is empty.

**B, treatment:** exact same production brain, question, model, model seed, system guidance and renderer. Add the top three source-verified, attributed historical passages from the local Vector Fly HTTP API. Every passage is fetched by its canonical `event_id` and marked `external_reconstructed_archive_not_lived`. Neural brain state digest must remain byte-identical before and after both packet preparations.

**C, future:** keep B's original retrieved candidate set constant, then rerank it using either actual FlyWire connectivity or an independently trained degree/support matched rewired control. **Not implemented in Pilot 01.** It cannot be called a successful third condition merely because the vector database exists.

Exactly six **assistant-authored, post-hoc, unreviewed** prompts are included to test plumbing: four source-specific/interpretive prompts, one contradiction probe and one absent impossible historical event. Their expected IDs are **engineering fixtures**, not an independent, blind academic benchmark. A future scientifically independent outcome requires fresh third-party authored prompts and blinded scoring.

## Stage 1: automatically verified integration, no language model

The GitHub workflow [vector-fly-persona-ab.yml](../.github/workflows/vector-fly-persona-ab.yml) checks out the original Vector Fly source at exactly `2bcdcaeac7dbb57af621a7c4ffa4a95fc425b5bc`, builds a source-pinned seed-31 L2 cache and SQLite index, starts the verified local read-only API, and invokes the **actual** `PretoriusBrainPort.render_request` for each prompt on one isolated, fresh production brain state.

Unit and end-to-end gates:

- Production subject frame identical in A and B, including same source character-state digest.
- A has no externally retrieved evidence; B has stable source-linked event IDs, original narratives, `reconstructed` provenance and source-blob checks.
- B cannot turn a retrieved archive record into `lived_runtime_memory` or change canon.
- A trained-only index, if used in an alternate build, excludes validation and test IDs even from direct retrieval.
- Read-only Vector Fly API validates scope and source Git blob, rejects mismatched source records and invalid provenance.
- An out-of-vocabulary or absent prompt can return no evidence without fabricating candidates.

**Engineering pass != behavioral pass.** This stage shows the agent can receive different renderer input, not that any generated answer changed or improved.

## Stage 2: actual responses with a free local renderer

Run the Vector Fly server as documented in [its API runbook](https://github.com/Azimn/Pretorius-Connectome/blob/main/docs/VECTOR_FLY_AGENT_API_V1.md) using the all-450 **browse** scope. Then, in a separate terminal from this repo:

```sh
python -m pip install -e .
python tools/run_vector_fly_ab.py --api http://127.0.0.1:8765 --scope all --top-k 3 --ollama-model qwen3:8b --output results/local-vector-fly-ab-ollama.json
```

This optional command contacts **only local Ollama at `http://127.0.0.1:11434`** by default and sends identical model name, `temperature=0`, seed and max predicted tokens in A and B. It counterbalances A/B generation order across six prompts and records the raw outputs, full prompts, source IDs and brain state digests. The local model must already be installed/running; we have **not** executed this Ollama stage in GitHub CI. Substitute any locally installed Ollama model name. Do not commit private live dialogues to public GitHub automatically.

Using the public, frozen v12 fictional corpus to author and score source-specific prompts is post-hoc. A local Ollama model may already have generic Pretorius film knowledge, so the no-retrieval baseline may still answer some questions correctly; this is why *paired controlled comparisons and independent evaluation* matter.

## Stage 3: predeclared independent human evaluation

Create at least 30 newly written third-party questions, split among: direct events (10), paraphrased multi-hop/relationship implications (8), contradictory premises (6) and genuinely absent events (6). Save their gold source IDs and gold claims *before* running any renderer and keep them outside model prompts. Also test 2-3 follow-ups that require cross-turn continuity on fresh controlled copies of the brain for each condition. Do not reuse the six post-hoc fixtures as the headline result.

Use the same model/version/parameters and cloned brain state for each arm, counterbalance order and conduct repeated randomized trials. Blind human reviewers to A/B labels and to whether a source was retrieved, but supply the authoritative originals during gold adjudication. Track:

| Metric | What it establishes |
| --- | --- |
| Source-hit@3, correct event ID | Retrieval can locate the appropriate canon source, not answer quality |
| Correct supported claims / total | Whether generated answers are materially more accurate |
| Unsupported claims per response | Hallucination cost |
| Correct rejection of contradictory and absent events | Source monitoring rather than false confidence |
| Proper reconstructed-vs-lived attribution | No false experiential upgrading |
| Response/choice consistency across rephrasings and follow-ups | Behavioral continuity |
| Latency, prompt size, model calls | Cost/feasibility of retrieval overhead |

**Primary behavioral success gate:** improved human-adjudicated supported claims with no increase in false affirmation of contradictions or in claims of lived experience. Report bootstrap/paired confidence intervals and individual event-level cases; multiple probes on the same original event are not independent samples.

**Causal interpretation:** if the indexed sources change a renderer reply, that's a measurable effect of supplying external evidence. It is **not** evidence that fly neural topology stores those memories. A future graph-vs-rewired reranking condition must compare the same candidate IDs, same renderer tokens, and same model settings, with the third-party evaluation still withheld during construction.

## What not to conclude

No current code proves stable human-quality first-person Pretorius, faithful post-instantiation learning, episodic engrams in an actual fly, or a semantically reliable embedding. Source texts are fictional reconstructions. A stage-one passing CI test supports only source-verified, mutable-state-safe integration. Stage-two model runs and independent human scoring remain to be performed.

## Artifacts

- [Integration library](../doctor_lives/vector_fly_eval.py)
- [Experiment CLI](../tools/run_vector_fly_ab.py)
- [Real-brain unit tests](../tests/test_vector_fly_eval.py)
- [CI workflow](../.github/workflows/vector-fly-persona-ab.yml)
