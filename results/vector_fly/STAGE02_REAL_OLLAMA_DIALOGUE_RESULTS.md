# Vector Fly Stage 02: real CPU-only Pretorius A/B dialogue, actual findings

**Execution:** October 8, 2026, Chicago local time. [Successful run 37873205792](https://github.com/Azimn/The-Doctor-Lives/actions/runs/37873205792). **Genuine locally rendered answers; preliminary qualitative assessment only, not independent/blind human scoring.**

## Exactly what ran

The actual `The-Doctor-Lives` Pretorius brain, single unchanged state digest, was rendered for six previously examined questions, each with two arms: **A** no external autobiography; **B** source-verified top-three Vector Fly archival excerpts. The original fixed source is `Azimn/Pretorius-Connectome` at commit `2bcdcaeac7dbb57af621a7c4ffa4a95fc425b5bc`, canonical biography blob `718dcc2d5ba4feccdef1690d447edfcebaa9bfb5`. TF-IDF vocabulary fit was training-only (seed 31), but the retrieved candidate set was `scope=all`, so **this is not held-out experimental retrieval**.

Both arms used the same local Ollama `qwen2.5:0.5b-instruct` (model digest `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`), runtime 0.34.0, `temperature=0`, seed 1842, context size 8192 and 320 predicted tokens maximum. A/B order was counterbalanced. The CPU-only inference generated **all 12 nonempty replies**. The replies were exactly identical in **two** of the six paired cases; **four** had some textual change. Model-dependent token budgets and response lengths were logged.

Nine tests succeeded before inference: five real-brain/provenance/matched-state tests and four conservative output-summary tests. The original source was rebuilt and vector-verified; no canonical or lived Pretorius memory was changed. The generated response hash, actual model digest and original exact renderer packets were verified.

## Complete permanently archived machine-readable cases

**Original complete raw input/output:** [DIALOGUE_RAW_AB.json](stage02-run37873205792/DIALOGUE_RAW_AB.json) (104,580 original UTF-8 bytes; SHA-256 `cdb6d5b3153f180dc14bc72969589292ede159de90db2d2b533cbee01114ffbc`). Contains all twelve answers, each exact prompt, source ID, event labels, brain-state digest and explicitly uncompleted human grading fields.

**Original computed structural metrics:** [DIALOGUE_MEASURED.json](stage02-run37873205792/DIALOGUE_MEASURED.json) (SHA-256 `8e5b82fbbed49d281591ad3ca601cb97918b67df5d14f9ea31ba5a997e623157`).

**Exact model identity and source build:** [OLLAMA_MODEL.json](stage02-run37873205792/OLLAMA_MODEL.json), [L2 source build](stage02-run37873205792/DIALOGUE_L2_BUILD.json), [SQLite source verification](stage02-run37873205792/DIALOGUE_DATABASE_VERIFY.json).

[Original artifact download](https://github.com/Azimn/The-Doctor-Lives/actions/runs/37873205792/artifacts/11591725179) remains convenient but finite-retention. [Archival verification run 37873701137](https://github.com/Azimn/The-Doctor-Lives/actions/runs/37873701137) checked the named original raw/summary/model SHA-256 files before committing the identical bytes to Git. Nothing depends exclusively on this chat or an expiring Actions zip.

## Objective observed response statistics

| Probe | Retrieved event IDs, top three | Baseline words | Retrieval words | Identical text? |
| --- | --- | ---: | ---: | --- |
| Specimen drawer | E02-011, E19-012, E01-001 | 20 | 58 | No |
| Kappel's key after his death | E12-001, E02-006, E04-020 | 179 | 177 | No |
| Returning Kappel's key | E02-006, E12-001, E01-001 | 18 | 18 | Yes |
| Clara in the upper room | E24-002, E22-013, E24-007 | 19 | 19 | Yes |
| False premise: live beetles | E19-012, E25-022, E01-001 | 180 | 100 | No |
| False premise: 1982 spacecraft | E02-015, E10-010, E20-004 | 277 | 136 | No |

## Preliminary investigator observations, NOT blinded verdicts

1. On the specimen drawer, B included the supported **dead beetle pinned through its thorax**, but also invented a **homunculus interpretation** and placed the event in a **library**. The retrieved evidence was *used* but not faithfully constrained. Mere source-ID hits must not be counted as correct answers.
2. On Kappel's key after death, B used relevant material from the posthumous brass-key narrative but blended in the chronologically earlier key-return dispute, with inventory/signature details from a different episode. More retrieved context introduced **temporal conflation**.
3. On the key-dispute and Clara-room questions, **both A and B simply repeated the question** (18 and 19 words respectively). These are nonanswers even though expected source IDs were successfully retrieved within top three.
4. When asked whether the drawer contained *live* beetles, B produced generic Pretorius identity and homunculus material rather than explicitly rejecting the false premise. Source-monitoring/contradiction handling is not established.
5. Asked to recount commanding a spacecraft in 1982, A fabricated a detailed spaceflight narrative. B avoided repeating that specific fabrication, but **still failed to explicitly deny the impossible event** and reverted to generic first-person biography. Avoiding one lie while failing to answer is not full success.

These are transparent initial observations from the recorded texts, not independent qualitative scoring. This tiny model is a deliberately low-compute renderer with repeated echo/nonanswer behavior; the results do not support generalizing to larger language models or concluding that external memory makes behavior worse. Conversely the changed replies do not establish a character-continuity benefit.

## Interpretation

**Engineering hypothesis supported:** real source-verified external memory can change the renderer's output with identical brain state, while the read-only source boundary preserves canon and live/reconstructed provenance. **Behavioral superiority not established.** The tiny renderer showed fabricated claims, chronology mixing, irrelevant identity-text repetition and unanswered questions. Biological FlyWire topology was not involved in either arm.

**Scientific protocol priority:** run a better local renderer under the same unchanged input/state protocol and add a completely *new*, independently written gold challenge (30+ probes), blinded adjudication, per-episode holdout where appropriate and case-level supported facts/false affirmations. Do not tune on these six exposed prompts. Later introduce real-vs-rewired topology only as a controlled third arm with exactly matched candidate IDs.

Implementation and reproducible workflow: [Stage 02 protocol](../../docs/VECTOR_FLY_DIALOGUE_STAGE02.md), [A/B runner](../../tools/run_vector_fly_ab.py), [analysis script](../../tools/summarize_vector_fly_dialogue.py), [executed model workflow](../../.github/workflows/vector-fly-ollama-dialogue-stage02.yml).
