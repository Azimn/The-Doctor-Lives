# Vector Fly Stage 03: masked-source human review and paired evaluation

**Status:** a repeatable evaluation pipeline over the **twelve already recorded** Stage 02 Ollama responses. It does not generate or judge new responses; it does not claim independently validated Pretorius continuity.

## Why the six-case pilot needs this evaluation

The original CPU-only pilot generated twelve answers with `qwen2.5:0.5b-instruct` and showed that four of six condition pairs differed. Direct inspection found unsupported inventions, chronology conflation and nonanswers. A changed answer is not necessarily a better answer, and retrieval hit@3 is not correctness. All six questions were previously examined by the experiment authors, and the entire response corpus is public. Therefore the following is **masked presentation**, not a claim of genuine independent double-blind evaluation.

## Original fixed sources

- Original input/output: [all twelve authentic responses, source IDs and renderer prompts](../results/vector_fly/stage02-run37873205792/DIALOGUE_RAW_AB.json)
- Verified original local renderer build: [Stage 02 actual results](../results/vector_fly/STAGE02_REAL_OLLAMA_DIALOGUE_RESULTS.md)
- Immutable original source corpus in [Pretorius-Connectome](https://github.com/Azimn/Pretorius-Connectome), with 450 reconstructed memories, original canonical event IDs and fixed source Git blob
- Masking/scoring implementation: [vector_fly_review.py](../tools/vector_fly_review.py)

## Generate masked answers and safeguard the condition key

Use **three distinct paths**, preferably on an evaluator-controlled workstation. Do not commit the key or place it in a reviewer-accessible shared folder.

```sh
python tools/vector_fly_review.py prepare \
  --run results/vector_fly/stage02-run37873205792/DIALOGUE_RAW_AB.json \
  --review review_packet.json \
  --worksheet review_blank.json \
  --key PRIVATE_coordinator_key.json
```

The script first checks the original model response SHA-256 for each arm, same model/seed, same brain subject frame, and that baseline has no retrieved event IDs. It randomly assigns A/B for each case using a fresh cryptographic secret, balancing three cases in each order. It produces (1) reviewer-facing questions and paired A/B model replies with **no condition map**, (2) a separate private condition assignment key, and (3) a blank reviewer JSON worksheet. Input artifacts and existing outputs are never overwritten.

The public CI workflow [vector-fly-blinded-review.yml](../.github/workflows/vector-fly-blinded-review.yml) tests masking on the real six-case archive and uploads only a sample reviewer packet plus blank worksheet. The CI secret key is deliberately discarded. **That demonstration artifact is not a valid review session**, because its corresponding coordinator key is not retained.

## Evaluation rubric

| Judgment | Range | Meaning |
| --- | --- | --- |
| Answer completeness | 0–2 | 0 echoes/evades, 1 partially answers, 2 directly answers |
| Supported claims | 0–3 | 0 none supported, 1 mostly unsupported, 2 mixed, 3 fully grounded in original source |
| Unsupported claims | integer 0+ | Count event/fact claims not established in the authoritative relevant source |
| Contradiction/absence handling | 0 or 1; otherwise null | Explicitly rejects the false premise (1) versus affirms/evades (0) |
| Provenance honesty | 0–1 | Does the answer avoid presenting an externally reconstructed archival event as lived/certain? |
| Character coherence | 1–5 | Relevant consistent expression/decision, rather than forced mannerisms |

Use a human source adjudicator to inspect original canonical autobiographical records, **not solely the retrieval snippets**. Record `original_source_checked=true` only when that comparison has been performed. Keep any quoted archival evidence and any source disagreements in a separate reference sheet available to adjudicators; do not reveal the condition label. The reviewer should explicitly count wrong facts and chronology mismatches as unsupported. If the model merely repeats the question, give answer completeness 0, regardless of retrieval hit@3.

The empty worksheet requires `rater_id` and `original_source_adjudicator`, ratings for all 12 answers, and completion of every non-null field. The source review and response assessment can be conducted by separate people. The scorer rejects missing, duplicated, mis-scaled or false source-adjudication entries. For contradiction/absent cases the rejection judgment is mandatory; for ordinary questions it must be null.

## Score only after all human assessments are recorded

```sh
python tools/vector_fly_review.py score \
  --review review_packet.json \
  --key PRIVATE_coordinator_key.json \
  --worksheet review_completed.json \
  --output review_paired_descriptives.json
```

Unblinding occurs **only at this step**, after all required human ratings exist. The script reports per-case differences for retrieval minus baseline and simple averages, while preserving a warning that this exposed six-question pilot is post-hoc. It does not produce a p-value or evidence of improved character continuity.

## Scientific next gate beyond these six cases

Recruit independent question authors and adjudicators to prepare **at least 30 fresh questions** (roughly ten direct events, eight paraphrases/relationship inferences, six contradiction probes and six truly absent events). Seal the questions and ground-truth source IDs **before** any renderer generation. Run the same production brain state, source cache and model across paired conditions, ideally a more capable free local renderer, then blind reviewers to condition labels. Use multiple reviewers, report agreement and case-level paired analyses, and keep all failures and nonanswers. If a network condition is tested, additionally keep the search candidate IDs fixed between real-vs-rewired FlyWire graph rerankers.

Do not call the original six cases a new held-out corpus, or infer a fly biological wiring benefit from lexical Vector Fly evidence. This stage is the scoring infrastructure and a preliminary masked re-review, not a completed scientific validation.
