# Pretorius: pinned Self-Reference Governor integration A/B results

**Date:** 2026-10-13. **Status:** Experimental, draft PR #60; not production-adopted.

## Repository separation

- Canonical Self-Reference Governor: [Azimn/synthetic-ipseity PR #34](https://github.com/Azimn/synthetic-ipseity/pull/34), exact external commit `c0747901e7434b9418204a331487172a7894b6e0`.
- Pretorius host integration: [The-Doctor-Lives PR #60](https://github.com/Azimn/The-Doctor-Lives/pull/60), stacked on the three-organ preview PR #59 (not merged).
- Optional dependency: `pip install -e ".[self-reference-governor-preview]"`. No donor code copied into Doctor.
- Thin adapter: `doctor_lives/self_reference_adapter.py`. Typed identity originates **only** in the real Doctor Ipseity host: `host.SUBJECT_ID`, `host._doctor.brain.render_request().subject`, and explicitly host-configured aliases.
- `ReferenceContext` speaker/addressee/rhetorical fields are host-supplied. User speech and model output cannot change subject identity or addressee binding.
- Renderer input remains exactly the admitted first-person string from Ipseity. The corrected renderer-only instruction is a separate trusted configuration argument. Digests/score receipts are engineer-only and cannot become Pretorius memory or renderer input.

## Tracks and outcomes

### Independent canonical donor contract
The *unchanged* standalone `synthetic_ipseity/tests/test_self_reference.py` (11 tests) passed, using exact external pinned donor commit. This is not a Doctor-specific override.

### Integrated three-organ host
The new `tests/test_self_reference_governor_preview.py` (8 tests) passed against the real Sensus → Doctor state/policy → typed SubjectFrame → durable Synthetic Ipseity outbox. The original 31-test three-organ preview suite also passed. Specific integration checks:

1. Governor disabled: output with unlicensed self-vocative is returned exactly as baseline; no governor intervention.
2. Governor enabled with host-self addressee: pre-render instruction receives annotated clarification; output with unlicensed self-vocative is **vetoed before durable ACK**, leaving one pending frame.
3. With an approved first-person response, both modes complete delivery with the original text and no pending frame.
4. With host-defined other addressee, another person's name in a first-person clause is not automatically reclassified as self-reference; spoofed user statement claiming to be Doctor Pretorius cannot alter host bindings.
5. With an explicit trusted rhetorical-self-address license, the same self-vocative is accepted.
6. Unbound or forged-host adapter initialization fails closed.
7. No governor rule ID or correction text enters the subject frame. Raw model or governance results do not establish autobiographical memory.
8. The scope stays within the standalone governor's constrained English naming ladder; no broad semantic recognition is claimed.

Full integrated CI: [run 38412572697](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38412572697) (green).

### Actual paired local model A/B, first completed run
Source: [run 38412572697](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38412572697), GitHub artifact `pretorius-srg-model-a-b`. Frozen subject-only frames were captured from the real unified Pretorius runtime. The frame-replay experiment reused identical input for off and on; it is **not** a whole new cognitive run on every model draw.

Three scenarios: (a) host addressee is Pretorius; (b) host addressee is another subject; (c) Pretorius rhetorical address expressly licensed by the host. Two seed-controlled draws per scenario with each of two CPU Ollama models: `smollm2:135m` and `qwen2.5:0.5b`. Thus 3 × 2 × 2 × 2 = **24 live model calls**.

| Model | Governor off returned | Governor on returned | Pre-render conflicts found when on | Model outputs vetoed when on |
| --- | ---: | ---: | ---: | ---: |
| SmolLM2 135M | 6/6 | 6/6 | 2/6 | 0/6 |
| Qwen2.5 0.5B | 6/6 | 6/6 | 2/6 | 0/6 |

The governor annotated exactly the two unlicensed self-address **instructions** in the enabled branch per model. There were no output vetoes. This does **not** establish improved compliance; many outputs did not contain any narrow-name violation in either arm.

Direct inspection of the generated speech shows major limitations:

- SmolLM2 often reproduced first-person frame annotations, invented meta-descriptions, or replied as though editing a user's text.
- Qwen sometimes addressed Pretorius in the second person, failed to consistently deliver a three-sentence response, or adopted assistant-like language.
- Simple 3-sentence heuristic passed in only **3/6 off versus 2/6 on** outputs for SmolLM2, and **1/6 off versus 1/6 on** for Qwen (not a grammatical quality assessment).
- A Qwen off/self sample addressed `Pretorius,` directly; the corresponding enabled/self sample did not. That is a useful example of the difference annotation can make but is **not statistically meaningful** by itself.
- A later exact-pin rerun [38413139239](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38413139239) **passed both host and live-model CI jobs**, and kept raw model replies in an engineer-only artifact, including outputs eligible for veto. In that rerun the heuristic three-sentence count was **3/6 off versus 2/6 on** for SmolLM2, and **1/6 off versus 2/6 on** for Qwen. Per-model vetoes remained **zero**; each enabled group still annotated two host-self instruction conflicts. These are small-sample, nonblind diagnostics, not evidence of general quality improvement.

## Known unresolved gates

- The governor's current `check` method recognizes only a narrow name-in-desire / sentence-initial self-vocative regex fixture; quotation, paraphrases and nested syntax can evade it. It is a linguistic validator, **not a semantic identity, evidence or consciousness authority**.
- A name used in third-person quotation is not equivalent to a speaker addressing themselves.
- The model may produce unnatural or non-first-person text while still passing the governor.
- Stronger, held-out natural utterances and blinded human ratings of false positives/false negatives, usefulness, and persona quality are not complete.
- A spoken message rejected by the adapter remains pending in the Ipseity outbox. The existing lease/reconciliation mechanism must handle this; no automatic retry or duplicate brain ingestion was added.
- The standalone donor PR #34 and parent unified preview PR #59 remain draft; this integration must remain draft and must not merge until independent review.
- The general Doctor `brain-tests` workflow may run without the optional Synthetic Ipseity donor and fail importing an older renderer test; a baseline run from the parent commit already showed that issue. Keep that CI limitation separate from the dedicated exact-pin contract workflow.

## Reproduction

Run the GitHub workflow `.github/workflows/pretorius-self-reference-governor.yml`, or install the pinned optional dependency and separately clone the exact Sensus donor:

```sh
python -m pip install -e ".[self-reference-governor-preview]"
python -m unittest discover -s tests -p test_self_reference_governor_preview.py -v
```

A local Sensus checkout at `802e459ee68950414347d5fa324484c034f57b81` must also be on `PYTHONPATH` to run the actual preview test.

**Decision:** Implementation and narrow contract compliance are substantiated. Measurable *natural language improvement* is **not yet established**, and the governor should not be used to claim that the tiny renderer's generic-assistant behavior is resolved. Keep source ownership upstream and treat Pretorius strictly as the first integration host.
