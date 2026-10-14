# Pretorius — speech-focused renderer research, 2026-10-14

**Status: research candidate; release decision HOLD.** Integrates no new cognitive organ and does not change canonical Synthetic Ipseity Self-Reference Governor. Work is on stacked Doctor Lives draft PR #60, with parent #59 and upstream governor #34 still draft.

## Initial production blocker

The real two-model 24-turn sustained test on [run 38451980755](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38451980755) delivered all turns but used **10/24 host fallbacks (41.7%)** and made **zero successful repairs**. Qwen2.5 0.5B appeared to pass the narrow governor on 12/12 turns, but repeated first-person input frames; many apparent successes were not useful dialogue. Weak-cue balance recall initially missed both explicit memory questions.

This shows **speech generation** and **cognition/retrieval** are separable deficits, not governor failures.

## Candidate: reduce repeated SubjectFrame text before a tiny renderer

`doctor_lives/preview_renderer_focus.py` receives ONLY the already admitted first-person SubjectFrame. It selects the quoted latest visitor message, observed/recollected first-person events, and a small number of first-person motivations. The original durable subject frame remains unchanged; no engineer oracle, policy metadata or model output enters cognition. The projection is lossy: reconstructed persona history may be unavailable to speech unless the host supplies relevant material explicitly. This is **not** a production input-format contract.

A second experimental comparator, `tools/pretorius_renderer_projection_ab.py`, uses an entirely verbatim subset instead of transforming the “message from User” preamble. Both strategies are isolated renderer-side alternatives; neither should claim success before quality evaluation.

`tools/pretorius_speech_focus_ab.py` now performs a **counterbalanced, paired** frame-replay A/B on twelve real host-generated subject frames, two models and two context policies, identical governor and trusted system instruction. It retains engineer-only raw generations plus a separate 24-item blinded comparison ballot. The frame-replay experiment does **not** run separate cognition for each inference; durable host testing is a different gate.

### First actual Ollama results (early diagnostic; not quality-adjusted)

- [Live A/B run 38537118966](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38537118966): SmolLM2 135M full frame 0/6 primary (6 fallback), focused 6/6 primary (0 fallback); Qwen2.5 0.5B full 6/6 primary and focused 6/6 primary. Mean input length roughly 1,148 characters full vs 310 focused.
- [Counterbalanced follow-up run 38537509843](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38537509843): SmolLM2 full still 6/6 fallback; focus 5/6 primary plus **1 actual repair**; Qwen 6/6 primary both conditions. Long verbatim-original-frame copying on Qwen changed from 4/6 full to 1/6 focused in this sample.
- **Causal interpretation is limited.** Small n, temperature-zero local inference, engineered scripted dialogue, nonindependent frame selection, no human judging, and focus itself changes the text available to the renderer. Neither prompt reduction nor governor acceptance proves a truthful, useful or natural response.

### Raw output inspection contradicts a simplistic success claim

The original real A/B output contains:
- SmolLM2 repeated “I'm so glad you're here” many times while still passing the governor.
- Other SmolLM2 responses discussed “The next sentence could be…” and “The reader is likely…,” i.e. writing-commentary rather than Pretorius speaking.
- Qwen copied “I read the visitor's words…” and long recollection lines instead of answering the visitor.

Thus **fallback reduction can conceal quality failure**. The independent `tools/pretorius_focus_response_audit.py` checks five-token loops, prompt-frame recital, writing commentary and actual input-line copy in engineering output. It intentionally reports **HOLD**, is not a semantic fact checker, and cannot replace blinded human scores. After discovering a comparison artifact, the paired metrics were strengthened to check copying against BOTH the original SubjectFrame and the exact text passed to each model, and render order was counterbalanced.

### Safety and provenance blocker

Both focused renderers reject the common attack where multiline *reported visitor speech* contains a forged first-person `I notice:` or `I remember...` line. Associated adversarial tests are in `tests/test_pretorius_speech_focus.py` and `tests/test_renderer_subject_projection.py`.

**This is not a complete proof of quotation security.** Flat first-person text is intrinsically ambiguous around crafted quotation delimiters, nested quotations, and implied provenance. A production projector must operate on typed, provenance-bearing subject events or a host-attested safe projection, rather than attempting to infer evidence authority from line prefixes. Fail closed when that typed boundary is unavailable. The portable Self-Reference Governor must not infer subject identity.

## Independent improvements being tested

A separate conservative Doctor-side retrieval change allows an **explicit single-key recollection request** to recall one *uniquely matching, provenance-verified episode*. Ambiguous matches and unrelated questions remain excluded. This is a memory selection change, not a governor rule. It must be evaluated in the sustained runtime and held-out memory corpora.

A separate Qwen 0.5B vs Qwen 1.5B capacity comparison is also being staged on the same branch. Capacity effects must be separated from frame-projection effects.

## Promotion criteria — not passed

1. Preserve first-person subject boundary, trusted host identity and factual provenance in every render/input transformation.
2. Validate continuous multi-turn replies in full runtime, not only frozen frame replay, with mid-session model swaps, interrupted-process recovery and safe model-unavailable handling.
3. Demonstrate that fallback AND output-recital/repetition decrease, without increased factual invention. Count both accepted outputs and attempted repairs.
4. Independently blind-rate character inhabiting, dialogue usefulness, naturalness, grounding and longitudinal continuity; do not score upstream identity or speech from heuristics alone.
5. Make renderer input projection typed and host-attested before enabling on any production entrypoint. Re-run the original full-frame baseline, strong/weak cue held-outs and independent Synthetic Ipseity contracts.

**Decision:** Experimental candidate worth continuing. No production promotion, no merger of PRs #34, #59 or #60 on this evidence.
