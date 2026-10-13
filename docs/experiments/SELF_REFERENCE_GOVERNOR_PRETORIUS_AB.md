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


## F4 expansion: corrected three-stance experiment (supersedes initial governor version)

**Standalone donor exact commit:** `e84f3e37d844756786b289c13c15ea92edfd8d69`, [independent three-version CI green](https://github.com/Azimn/synthetic-ipseity/actions/runs/38423665173). This commit belongs to canonical Synthetic Ipseity PR #34; Doctor imports it as a pinned optional dependency rather than copying source.

### Three independent rule families

1. **First-person inhabiting (target):** allowed; e.g. `I believe the evidence is insufficient.`. The revised `SRG-CONFLICT-SELF-ADDRESS` pre-render annotation instructs `Speak as Doctor Septimus Pretorius in the first person: use I, me, and my`, in addition to prohibiting unlicensed self-address.
2. **Unlicensed second-person self-address:** pre-existing `SRG-OUTPUT-SELF-VOCATIVE` and `SRG-OUTPUT-SELF-NAME-IN-DESIRE` retain distinct IDs. Host-authored rhetorical license remains an exemption.
3. **Third-person narrating rather than inhabiting:** new `SRG-OUTPUT-THIRD-PERSON-SELF` flags narrowly recognized persona-name-as-grammatical-subject constructions and explicit, local anchored third-person pronouns. Exact prior Qwen displaced result (`I recognize that Pretorius is seeking...`, `He also appears...`, `Pretorius seems...`) is a standalone contract fixture. Quote and attribution negative controls (`The report says Pretorius was there`, `“Pretorius believes...”`) and rhetorical exceptions pass.
4. **Renderer boundary-marker leakage:** separate `SRG-OUTPUT-BOUNDARY-MARKER` covers narrow `User:`/`Assistant:`/`System:` role prefixes, `The frame states...`, `The prompt says...`, `As an AI...`, etc., except markers inside quoted data.

All scores are bounded lexical English **mechanism checks**, not independent identity inference, universal semantic verification or consciousness claims. Host owns identity, addressee, aliases and rhetorical license. Outputs are vetoed before Ipseity durable ACK and preserved as engineer-side raw response receipts for research.

### Actual matched Qwen displacement replay

In the previous governor run, Qwen2.5 0.5B, **host-self**, seed **17**, with original instruction:
- Governor off: `I appreciate you sharing your thoughts... Pretorius, I believe you...` (second-person self-address).
- Governor on: `I recognize that Pretorius is seeking...` / `He also appears...` (third-person self-narration; displacement from stance 2 into stance 3).

With exactly the same frozen cognitive frame and seed **17** but the F4 positive first-person instruction:
- Governor off: `I appreciate you sharing your thoughts... Pretorius, I am impressed by your ability...` (unlicensed self-address remains).
- Governor on: `I recognize that I am Doctor Septimus Pretorius, a scientist, inventor...` followed by first-person autobiographical material. The previously observed third-person subject phrase disappears and the subject begins to inhabit first-person speech. The response nonetheless copies first-person frame material and is truncated near `I am not yet`; **do not infer natural dialogue success**.

This result demonstrates a **matched case** moving in the intended direction. It does not establish generalization across prompts. The seed-29 Qwen sample still contains substantial `you`-addressed language, indicating unresolved second-person stance failures not all captured by the narrow existing regex.

### Complete F4 24-call outcome

[Successful final code-head integration run 38424016290](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38424016290). Both standalone contract and full three-organ integration tests passed, as did the live Ollama job. Raw 24-response data stored in the GitHub Actions artifact `pretorius-srg-model-a-b`. Data uses three actual Ipseity-delivered subject-only frames, identical on/off input, three host-defined addressee/license contexts, two fixed seeds, two actual CPU models: 24 independent renderer calls, NOT 24 independent cognitive episodes.

| Model | Governor off: speech returned | Governor on: speech returned | Enabled pre-render conflict annotations | Enabled F4 output vetoes | Raw boundary-marker outputs (off/on) |
|---|---:|---:|---:|---:|---:|
| SmolLM2 135M | 6/6 | **3/6** | 2/6 | **3/6** | 3/6 / 3/6 |
| Qwen2.5 0.5B | 6/6 | 6/6 | 2/6 | **0/6** | 0/6 / 0/6 |

When the governor was **off**, the same standalone F4 scorer would have judged 3/6 SmolLM2 outputs and 5/6 Qwen outputs acceptable. With the governor on, it judged 3/6 SmolLM2 and 6/6 Qwen acceptable, but only 3/6 and 6/6 respectively were returned. Thus the veto mechanism works for **observed meta-output** rather than silently assuming bad responses became good. No third-person self-reference rule fired in this new 24-call sample; its **historical Qwen failure** is covered by strict standalone and genuine host integration fixtures, not a claim of observed new live third-person vetoes.

The small sample and simple lexical checker cannot establish a statistically reliable improvement, false-positive rate in free dialogue, semantic truth, or voice naturalness. Old 0-veto results above belong to the **earlier c074 governor** and remain preserved rather than retroactively relabeled.

### Regression and promotion state

The optional-dependency import fix in `tests/test_pretorius_renderer_abcd.py` makes all `brain-tests` test discovery conditional on Synthetic Ipseity actually being installed; the general [green workflow at the final code head](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38424006400) now verifies the previous red ImportError has been resolved. Fresh-install, original three-organ and Synthetic Ipseity integration workflows also passed at code head `6636242d9f785abed6c6662712f52fe3c8f60311`.

The donor PR #34, parent Doctor PR #59 and stacked PR #60 remain **DRAFT/UNMERGED**, pending independent review. Do not interpret the narrow rule checks as general speech verification; don't port fixes into Doctor as owner of governor rules.


## Host-neutral bounded speech control v0.1 (2026-10-13)

**Canonical source:** Synthetic Ipseity donor `007c0a8df473df0fa10aeeec9ba1e17691268260` with reusable modules `speech_control.py` and `local_ollama.LocalOllamaConfiguredRenderer`. Doctor Lives does not copy these implementations. The exact donor revision is pinned both in the optional Python extra and the CI checkout.

The governor now has an independent `GovernedSpeechControl` port accepting **host-authoritative** typed identity, host-authoritative addressee, host-authoritative discourse mode (`direct`/`narrated`/`quoted`) and a declared language (`en` currently supported). The model receives only an already-admitted first-person subject text and separate trusted renderer-only instructions. Unsupported languages reject before the model can be called; they do not silently pass English regex rules.

Operational path under explicit opt-in:

1. The reviewed Sensus/Doctor/Synthetic Ipseity pipeline generates an admitted first-person frame as previously.
2. The host seals `ReferenceBindings` and `ReferenceContext` from actual Doctor identity and trusted operator addressee selection. Partial or failed bindings are never made active.
3. Primary local Ollama inference receives subject text as `prompt`, trusted task instruction as `system`.
4. On a recognized SRG output violation or unverified direct first-person stance, the controller runs **at most one bounded fresh repair call** with the *same first-person input*, adding only an instruction correction. Rejected speech is not fed back into cognition.
5. If both outputs fail, the host may choose its approved exact first-person fallback, default in experimental CLI: `I must consider my words more carefully.` No model text is allowed to mutate the fallback. If fallback is disabled, a rejected delivery raises before Synthetic Ipseity acknowledges its durable outbox; operator/resume reconciliation is required.
6. Engineer-only SHA-256 attempt receipts and disposition (`primary`/`repaired`/`fallback`/`rejected`) stay separate from Pretorius's subjective experience.

The **normal production launcher remains unchanged**. The optional experimental CLI is:

```sh
doctor-lives-three-organ-preview \
  --state ./scratch/three-organ-preview \
  --enable-experimental-preview \
  --enable-governed-speech \
  --model qwen2.5:0.5b \
  --governor-addressee-id visitor \
  --say "What can you tell me about our laboratory?"
```

Use `--governor-no-fallback` to test hard refusal/nonacknowledgment; use `--resume` with the same isolated state on an interrupted scene, per existing preview recovery controls. The `--governor-rhetorical-license` flag is a **host/operator authorization**, not a user-message command.

Host-independent tests include synthetic Calibos, Kiki and Pretorius identity bindings without importing their production runtimes. Actual integrated Pretorius tests exercise the real Ipseity durable outbox and the reviewed two-channel model transport. These are not tests of full Kiki or Calibos integration. CI uses `tools/pretorius_governed_recovery_probe.py` for real local-model inference on already frozen original Pretorius first-person frames; it records safe fallback and failure rates separately and does not claim conversation naturalness.

### Limitations and adoption HOLD

- This is not universal speech interpretation. English only; quoted/nested/coreference ambiguity and semantic truth remain unsolved. Legitimate terse direct replies may fail the conservative first-person-anchor requirement.
- Host fallback is generic; it does not guarantee inclusion of important facts from cognition. Protected-slot grammatical constructions must be separately engineered and grounded in typed host evidence before relying on factual fallback.
- Volatile engineer-only receipts do not yet establish crash-durable audit of every attempted model emission.
- Review false-positive rates, repeatability under model swapping, and sustained natural dialogue separately. Do **not** merge PRs #34, #59, #60 yet.
