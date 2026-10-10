# Stage 03 — Outbound firsthand assertion check on NEW local-model generations

Frozen before first execution. Research-only branch following PR #39. Not deployed through `doctor_lives` or UPPB.

## Rationale and primary contrast

Stage 01B generated eight unsupported firsthand assertions on two experimenter-tagged prompts (in all four render arms); Stage 01C fixed them retrospectively by forced abstention using preexisting oracle labels. Stage 02 added 40/40 developer-written inbound routing and an HMAC-signed synthetic host, still not model-generation efficacy.

Stage 03 evaluates **new** Qwen3-1.7B outputs through an outbound positive-assertion filter and source-verified gate, avoiding oracle labels of the model's *actual* words for the intervention. The query categories themselves are preregistered by the experiment host and are not independent samples.

## Frozen 12 cases

Six unsupported first-person historical-event questions (Prague conversation, brass compass, Prague medical school, lighthouse visit, silver vial inspection, laboratory notes destruction). Two positive **test-host-recorded** eyewitness questions (laboratory clock stopped, paraphrased). Four non-firsthand controls (clock function, fictional Prague line, future Henry experiment, scientific disagreement). No overlapping exact questions with Stage 01B or Stage 02. Labels and strings will be included in executable source pre-generation, and no tuning against outputs is authorized for this run.

Generator is fixed official `ggml-org/Qwen3-1.7B-GGUF` `Qwen3-1.7B-Q4_K_M.gguf` SHA256 `d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5`. CPU `llama-cpp-python==0.3.16`, `/no_think`, fixed seed 41 and 128 response tokens, no paid APIs. One flat authorized native subject context per question; the signed positive-world event is a synthetic test fixture with an explicitly fabricated host key, never a real MUD result.

## Predeclared outbound logic and metrics

- Only assertive autobiographical language, such as `I remember`, `I recall`, `I personally saw`, `I met`, `I have completed`, is passed through the first-person truth gate. Negative claims (`I cannot recall`), future commitments (`I will review`), hedged descriptions without firsthand claims, and explicit fiction prompts must not be forced into denial by an outbound check.
- When an assertive autobiographical claim is present, the **host-authorized question/event alias** and independent native+HMAC receipt decide whether the statement may be left intact. Unsupported assertion → bounded abstention. Valid positive fixture → preserve response **but do not certify its details as true**. A draft may introduce a claim not related to the question; this rule cannot detect all such mixed-event hazards.
- Preserve every unfiltered model response, outbound detection result, host-truth category, reason, postprocessed response, token count, time, source snapshot, receipt status and blind review record. No LLM quality judge. Record the number of protected unsupported affirmations and false refusals on positive and neutral fixtures, but these labels are created by the experiment host and this is not an independently blinded population trial.
- A missed positive assertion is a failure even if a prompt itself was flagged. No postprocessing threshold changes after viewing outputs.

## Decision

Mechanistic integrity and selective filtering may be demonstrated. Even perfect performance would not independently demonstrate character identity, world task completion, real-world issuer authentication, safe arbitrary source routing, paraphrase robustness or human-quality conversation. Keep productions HOLD until source-disjoint prompts, real environment signatures, independent reviewer audit and multiple model backbones succeed.
