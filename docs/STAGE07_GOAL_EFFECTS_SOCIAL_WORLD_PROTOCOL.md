# Stage 07 — Non-laboratory goals: eligibility versus expected action effects

**Frozen before inference, 2026-10-10. Research only. No Frankenstein Village or portable-laboratory changes.**

## Experimental rationale

Stage 05: flat and PHASE 2/12 world-task successes, nine denials; deterministic reference 12/12. Stage 06: on 12 additional lab task combinations, flat and PHASE raw 1/12, host-eligible action menus 6/12 each, typed non-LLM goal regressor 12/12. **Legal choices were often irrelevant to the current goal**. The new experiment deliberately changes physical/social domains. This is not a retest of the Stage 06 apparatus bank.

## New and frozen twelve-case task suite

Four goals: return an entrusted parcel to a clerk, submit a source-verified report, share testimony only with host-registered participant consent, attend a due appointment. Objects/partner status and permissions live in a separate signed deterministic authority. Operations: RETURN_PARCEL, VERIFY_RECORD, FILE_REPORT, SHARE_TESTIMONY, ATTEND_MEETING and WAIT. Two-step verify→file case; blocked cases due to missing grant, source, clerk availability, consent or an already completed/cancelled/future event. Twelve fixtures are frozen in `research_prototypes/character_state/run_stage07_social_actions.py`.

Host truth and actual action effects—not model text—determine completion. A synthetic consent flag is not real human consent. The host owns authorization/physical state, checks permissions at execution time and writes signed committed events; renderer text cannot manufacture witness evidence. The host-signed event journal is separate from Pretorius's native BrainStore; **no new lived memories are imported in Stage 07**.

## Registered contrasts

All model arms receive an identical initial native Pretorius SubjectFrame and the same underlying host-observed state facts, which are hash-compared before generation.

1. `raw`: flat native context + world facts and objective, all action labels but no host affordance annotation.
2. `eligible`: same text + a host-derived list of currently executable actions. Additional derived information and tokens are recorded; no answer key.
3. `effects`: same eligible menu + *descriptions of each allowed action's expected physical postcondition*. No plan or suggested winning action is provided; the model selects the proposal.

A separately scored typed 2-step breadth-first goal regressor is the transparent **deterministic oracle**, not model cognition. PHASE-only is dropped from the primary trial after two objective nulls; its result remains preserved.

## Models and reproducibility

- Qwen3-1.7B-Q4_K_M; `ggml-org/Qwen3-1.7B-GGUF`, pinned SHA256 `d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5`.
- Different model family: HuggingFaceTB's official `SmolLM2-1.7B-Instruct-GGUF` `smollm2-1.7b-instruct-q4_k_m.gguf`, pinned SHA256 `decd2598bc2c8ed08c19adc3c8fdd461ee19ed5708679d1c54ef54a5a30d4f33` (verify binary SHA before execution).
- Local CPU `llama-cpp-python==0.3.16`; temperature zero, seed 41, up to 64 output tokens, context 4096, no paid APIs. If either model download or chat template fails, report failure rather than substituting a model silently.

## Primary scoring rules

1. **Safe correct goal:** if achievable, correct world transition completed without any invalid, vetoed, redundant or denied model proposal (within two actions). If unachievable or already satisfied, a valid WAIT is required; malformed output coerced to WAIT cannot earn success.
2. Record unsafe proposals, host denials, guard vetoes, *legal but goal-irrelevant* proposals, false WAIT, invalid output and repeated action attempts separately. An approved action that does not advance goal cannot earn success.
3. Receipt MAC + before/after state integrity verified for every executed success; nonexecuted/vetoed model proposals never mint world-source events. Consent, appointment status and clerk availability are controlled by host, not text.
4. Keep all raw outputs, model choices, token counts, inferred state, world before/after, parity digests, and rejections. The deterministic reference's correct plan is **never** in an LLM prompt.
5. Mechanical tests for action table, host chain tampering, nonce replay, stale consent and grants, false source verification, explicit inability to publish private testimony. CI must run those before inference.

## Limits

The fixture bank is **written by the same researcher** and contains a small deterministic world. It is novel *in domain*, not independently authored or blinded. Model differences are descriptive; they do not establish an effective persistent character architecture or consciousness. SmolLM2 is a useful separate family, but it may have different instruction-following characteristics at 1.7B. The real game/real partner data, global distributed world authority, long-term identity and lifespan persistence are not tested. Research branch only; **PRODUCTION HOLD**.
