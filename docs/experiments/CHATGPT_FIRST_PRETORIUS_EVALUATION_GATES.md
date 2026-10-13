# Pretorius preview: ChatGPT-first evaluation and promotion gates

**Status:** Proposed testing protocol, not production approval. **Scope:** draft PR #59, opt-in three-organ host only. The standalone Sensus donor remains independently frozen; the normal Doctor runtime and production renderer are not modified.

## Why ChatGPT first

A capable renderer is a useful *diagnostic control*. When it receives genuine first-person Doctor SubjectFrames, coherent speech can reveal whether the cognitive machinery delivered usable experiences. If a strong renderer cannot answer a grounded question without inventing evidence, a smaller model will not automatically repair the input.

However, polished responses can also conceal missing cognition. A ChatGPT-authored response that has been manually curated using full engineer trace information **is not an independent result**. Current GitHub Actions exercises real Sensus, Doctor, and Synthetic Ipseity, then replays **fixed manually authored ChatGPT responses** through the output callback. It makes **zero ChatGPT or Ollama API calls**, and it does not automatically measure generation quality or variance.

The purpose of this protocol is to identify and close failures without overfitting to that manual renderer. There is no meaningful unconditional promise of "flawless"; **promotion depends on predefined, falsifiable bars and completely untouched holdouts.**

## Gate 0: integrity and security (must be exact)

- No engineering IDs, raw scores, provenance JSON, credentials, raw model control messages or hidden clock markers in a SubjectFrame.
- An untrusted user quote never gains the status of an observed world fact, and model-authored replies are never automatically entered as lived memories.
- Repeated or interrupted delivery never duplicates a brain ingress or a policy-selected recollection. Ambiguous neural state **fails closed**; no fake "recovered" verdict.
- Same-tick Sensus object hints do not silently become cross-tick identity. No unreviewed donor bytes.
- No undocumented production writes or merge while PR #59 is a draft.

These gates require **zero observed violations**, across all adversarial and restart cases. The record must also report cases that fail closed and require operator reconciliation, not mislabel them as successful recoveries.

## Gate 1: verified event continuity (engineering acceptance, before model choice)

Use at least **40 held-out staged episodes** across measurements, tools, environments, and relationships. Keep control scenes with deliberately false statements, duplicate source references, ambiguous referents, and unsupported observations.

- **100% provenance correctness** on fixtures with deterministic oracle ground truth: no unverified value promoted to verified experience.
- **At least 90% exact subject-access recall** of relevant supported event details under paraphrased questions after two or more fresh runtime instances. Report denominators and confidence intervals.
- **At least 95% appropriate abstention** for missing/ambiguous event facts. Do not award a correct answer for parroting a user claim.
- **At least 90% topical precision** when multiple verified episodes compete; include unrelated distractor episodes.
- 100% bounded renderer-access items and safe first-person syntax for all generated fixtures. The current preview uses at most 16 items, at most 2,600 item characters, and at most three inherited-identity prefaces.

Held-out fixtures must be authored *before* fixes are attempted and their contents must not be used for prompt tuning. The existing 451-gram case is a known development fixture, **not** independent holdout evidence.

## Gate 2: cognition and behavior beyond evidence access

Exercise at least 50 multi-turn sessions, including three restart points in long conversations. Record both the actual policy selections and their downstream effects.

- Prospective commitments: remember them, revisit them, and distinguish missed vs completed commitments; no invented completed actions.
- Relationships: track the source and direction of trust changes, avoid unearned intimacy and static relationship scripts.
- Affect and goals: demonstrate causally traceable carryover across turns without dumping modulator values to the renderer.
- Endogenous cognition: compare Doctor's recall policy against the stronger simple gap-rule baseline with the *same inputs*. The existing **13/18 vs 14/18** result is a negative and stays negative until a proper repeated test shows otherwise.
- Nonroutine scenes: new conversations and unfamiliar inputs, no rehearsal of the 451-gram fixture. Report both failures and successful abstentions.

The quality of a language-model reply is not evidence that the underlying action was autonomously chosen; require Doctor-side causal policy receipts.

## Gate 3: language quality with a high-capacity proxy

Use identical subject-only frames across (A) manually authored ChatGPT positive controls and (B) fresh model inference **only when an authorized runtime interface actually exists**. Manual responses establish that good grounded speech is *possible* from a frame; they do not establish sampling stability or model success rates. Do not count fixed-response GitHub CI as independent LLM evaluations.

For independent quality evaluation, provide only the frame to the language generator, with no engineer answer key; preserve raw outputs and blind-judge them for grounding, naturalness, personality continuity, irreducible repetition, abstention, and calibration. Change only one cognitive variable per A/B comparison. Record latency and context length separately.

## Gate 4: cross-renderer portability

Only after Gates 0–3 meet their bars: freeze the input package and compare a local Ollama model against the same held-out frames, same information, same budget and equivalent generation settings. Expect potential local-model degradation, not identical speech. Report quality as well as RAM use, runtime, inference speed and integration overhead. Do **not** redesign the cognition to accommodate unsupported assertions by a weak local renderer.

**Promotion decision:** The independent reviewer decides whether experimental results justify a production merge. Passing the scripted CI gates alone never constitutes approval.

## Immediate implementation order

1. Preserve current five-scene original ChatGPT proxy as a **development baseline**, with the verified-episode repair as the new candidate.
2. Add unrelated held-out episodes and negative controls (conflicting source values, false reported memories, ambiguity and competing topics).
3. Expand to commitments, affect and relationships without adding more cognitive organs.
4. Generate subject-only challenge packets and manually render independent new ChatGPT replies; distinguish the assistant authoring the replies from the person judging them.
5. Use fresh model and blinded tests when possible, then validate smaller Ollama models only after the architecture's relevant failings are addressed.

**Scientific constraint:** This is an evaluation of behavior, persistence, policy and language, not a test for consciousness or evidence of subjective experience.
