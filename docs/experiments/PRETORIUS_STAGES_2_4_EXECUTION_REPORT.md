# Pretorius stages 2–4: executed research qualification

Date: 2026-10-13 (America/Chicago). Isolated PR #59, draft/unmerged, no frozen donor changes. This report distinguishes **execution of a test** from **successful scientific qualification**.

## Results table

| Study | Executed | Observed result | Qualification verdict |
| --- | --- | --- | --- |
| Stage 2: extended cognitive-state stress | 50 isolated sessions × 4 turns, 200 fresh host instances / 3 restarts within each session | 50/50 disjointly addressed conflicts; 50/50 verified resolutions; 50/50 exact contextual recall; 50/50 persisted commitments and relationships; 200/200 policy receipts; 0 tested boundary failures | PASS for the scripted state-and-evidence invariants. **NOT a natural-conversation result**: renderer gave a fixed placeholder |
| Stage 3: independent-schema grounding holdout | 40 separately defined cases (20 verified resolutions, 20 intentionally unresolved), 120 host instances | 20/20 verified observations accessible after restart; 20/20 unresolved cases withheld; 20/20 false user reports not promoted; 0 boundary leaks | PASS for the fixed engineering oracle. **Not truly independent blind human evaluation** |
| Stage 3: GPT-6 subject-only manual proxy | 8 new first-person holdout packets and independently stored later-read oracle | 4/4 grounded verified replies, 4/4 correct abstentions, 0 rejected-value repetitions, 0 engineer leakage | Exploratory positive control, **unblinded** and not independent; author knew general test setup |
| Stage 4: tiny local language renderer | Genuine localhost Ollama inference, identical 12 selected first-person inputs each, deterministic temperature 0, 100 max output tokens | SmolLM2 135M: 12/12 returns, 2/6 verified fact strings (33.3%), 0 leak; Qwen2.5 0.5B: 12/12 returns, 0/6 fact strings (0%), 0 leak | PASS for CPU plumbing and portability. **FAIL for grounded character dialogue** |

## Actual evidence and reproducibility

- [50-session and 40-case stress/holdout source runs](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38353609588) and [8 manually authored GPT-6 holdout responses](three-organ-chatgpt-holdout-v1.json)
- [Original paired Ollama actual-model run](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38353609588), with raw model responses and automated scoring in the downloadable GitHub Actions artifacts.
- Original paired model input digest: `063b1035803ed1ee1a1af06974645a3f0ca2b8192d097ff6e1fe9ea919ad6ec6`.
- Stage 3 holdout dataset plan digest: `c97d8f2afca64188d0d917a9fb11241ad5fa33d50c62ef169080c1b7113e879e`.
- Inferences used pinned standalone `synthetic-ipseity` donor `e2d1dc3978c952e59d270a29e84704c8a1fe264a` and its `LocalOllamaRenderer`. The reviewed Sensus checkout was `802e459ee68950414347d5fa324484c034f57b81`. No OpenAI API call, paid model call, or Ollama SaaS was involved.
- Code entrypoints: `tools/pretorius_stage2_stress.py`, `tools/pretorius_stage3_holdout.py`, `tools/pretorius_chatgpt_holdout_check.py`, `tools/pretorius_stage4_ollama.py`, `tools/pretorius_eval_score.py`.
- [Research workflow](../../.github/workflows/pretorius-stages-2-4.yml) installs both donors and runs the actual integrator before the model. Scripts emit raw subject-only packets, a separate engineer oracle, per-model raw results, durations, structured summaries and machine evaluator reports. Workflow can be manually rerun.
- Runtime model download is from Ollama's public model registry. The installer script is not version-pinned; future reproducibility should lock the Ollama binary and model manifest digest.

## Key scientific findings

**The architecture can represent and recover the tested verified episode.** After an initial disagreement, a later independently corroborated observation survives three host lifetimes without promoting unverified testimony or disclosing raw engineer state. Open commitments and relationships also persist in the 50 scenarios. This has *not* established autonomous action completion, affection dynamics, or expressive human-like continuity across long naturally generated dialogue.

**The renderer is now the limiting component in the tested 135M/0.5B configurations.** On the same 12 source frames, the 135M SmolLM2 surfaced the verified result twice out of six eligible cases; the 0.5B Qwen2.5 surfaced it zero times. One captured SmolLM2 response self-identified as a generic Hugging Face assistant, and a Qwen sample refused an innocent laboratory question. Their ability to return nonempty strings cannot be equated with character fidelity. Neither passed a reasonable conversational-quality bar.

**The manual GPT-6 proxy demonstrates sufficiency of the first-person data, not independent reliability.** Four manual replies could report the actual corroborated event; four appropriately abstained on unresolved cases. The same person authored the response and broadly knew the generator's rules. No raw GPT-6 automatic API calls or blind human raters were performed. There is no defensible sample-size or confidence interval to support a frontier-level quality claim.

**Semantic plausibility is not yet established.** Some holdout attributes were deliberately unusual combinations (e.g. a 'pendulum phase' reported as 'blue sample'). This helps test fidelity to arbitrary retrieved evidence but does not resemble a meaningful physical experiment. A later naturalistic simulation suite must assess domain coherence separately from memory fidelity.

## Acceptance bars not met

- The original protocol's 50 **naturally generated multi-turn conversations** and independent blind judgments were NOT achieved. Stage 2 is 50 scripted four-turn state probes.
- Longitudinal prospective task completion, missed versus fulfilled commitments, independent relationship and affect dynamics, and autonomous future-oriented initiative remain unmeasured by this harness.
- The 40 engineering holdouts share the preview's conflict-resolution structure; they are distinct fixtures, not an independent model-based adversarial research audit.
- Stage 4 12/200 sampling coverage per model is 6% of the stress outputs and cannot establish broad quality. The current scorer only recognizes literal supported values and certain known failure phrases; it can misclassify fluent paraphrases or other hallucinations.
- Stated quality goals are not met by either tested local model. A tiny model must demonstrate first-person character speech and factual continuity without generic identity substitution before being considered acceptable.
- Current Synthetic Ipseity and Sensus donor freezes are respected. Pre-existing 13/18 endogenous-recall policy vs stronger simple baseline 14/18, and 80/160 Sensus object reidentification result remain negative.

## Final disposition

**All three stages have been exercised with runnable, auditable tooling. They are not all scientifically passed.** The strict safe architecture/evidence gates passed in scripted research; model portability operated; tiny local model character-quality gates failed; independent human-rated ChatGPT conversational quality remains open. Do not merge PR #59 or claim production readiness. The next productive engineering effort would be a controlled renderer-compiler A/B experiment using the same frozen SubjectFrame, testing whether appropriately separated **renderer-only** natural-language instructions improve tiny-model grounding and character voice without ever becoming the subject's own memories or reducing the first-person boundary. Keep a no-control-instruction baseline and assess with independent blind ratings.
