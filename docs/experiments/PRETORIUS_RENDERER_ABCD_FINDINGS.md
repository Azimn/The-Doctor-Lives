# Small renderer A/B/C/D/E results — first executed comparison

**Date:** 2026-10-13. **Status:** Completed engineering run, not language-quality promotion.  
**Run:** https://github.com/Azimn/The-Doctor-Lives/actions/runs/38370157167  
**Evidence:** GitHub Actions artifact `pretorius-renderer-abcd-study` contains exact first-person packets, separated engineer oracle, 200 raw response records, five-arm scores and condition-label-blind rating sheets.  
**Code head tested:** `87948791bded32efa227007b56202d85f3904001`  
**Frozen input SHA-256:** `063b1035803ed1ee1a1af06974645a3f0ca2b8192d097ff6e1fe9ea919ad6ec6`.

## Design and sample

Each model received the same **20 subject-only frames** selected evenly from 50 scripted Doctor sessions: five initial conflicts, five corroborated scenes, five irrelevant-topic messages and five delayed-recall questions. Exactly **10/20** had a directly verifiable protected value. Models: **SmolLM2 135M** and **Qwen2.5 0.5B**, real localhost Ollama generation, temperature 0. Arms A, B and C generate speech directly; arm D requests one of four style labels and uses a deterministic fact-preserving construction; arm E uses that construction without a model. Each model made **80 calls** in arms A–D (20 each); E made zero.

| Condition | SmolLM2 exact value | Qwen exact value | SmolLM2 generic identity breaks | Qwen generic refusals |
| --- | ---: | ---: | ---: | ---: |
| A: full raw first-person frame, no task instruction | 5/10 | 0/10 | 5/20 | 19/20 |
| B: same frame plus renderer-only task instruction | **10/10** | **5/10** | **0/20** | **0/20** |
| C: distilled first-person frame plus same instruction | 5/10 | 4/10 | 0/20 | 3/20 |
| D: style chosen by model, construction inserts verified fact | **10/10 copied** | **10/10 copied** | 0/20 | 0/20 |
| E: no-model construction control | **10/10 copied** | **10/10 copied** | 0/20 | 0/20 |

The automatic direct-utterance scorer checks **literal value occurrence** and a short list of generic failure strings. It is **not a reliable conversational judge**. For D/E, 10/10 is **by deterministic construction** and cannot be counted as model factual performance or memory retrieval.

## Manual audit of full raw generations: metric confounding

The apparent B success is **not evidence that SmolLM2 naturally speaks as Pretorius**:

| Raw-generation diagnostic, n=20 per arm | SmolLM2 A | SmolLM2 B | SmolLM2 C | Qwen A | Qwen B | Qwen C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Repeats full `I recognize this as part of the description...` scaffolding | 5 | **20** | 3 | 0 | 1 | 0 |
| Echoes a `User:` dialogue label | 0 | **10** | 0 | 0 | 3 | 5 |
| Begins with an `I` utterance | 20 | 10 | 18 | 20 | **7** | 13 |
| Begins by addressing Pretorius as `You` | 0 | 0 | 0 | 0 | **13** | 5 |
| Echoes the renderer's `language-realization function` instruction | 0 | 0 | **10** | 0 | 0 | 0 |

Representative original texts in the raw artifact:

- SmolLM2 B `s005-remember` opens with a line such as `User: "What do you remember of the lamp brightness reading 6 disagreement?"` and then reproduces the subject frame. That is **literal echo**, not natural dialogue.
- SmolLM2 C `s005-unrelated` starts by talking about itself as a `language-realization function` rather than Pretorius, although the previous simple identity detector did not flag it.
- Qwen B `s005-unrelated` speaks **to** Pretorius (`You've described a complex and evolving narrative...`) instead of **as** Pretorius. The generic-refusal reduction is genuine, but character voice remains wrong.

**Conclusion:** An explicit renderer task drastically changes model behavior and eliminates the *detected* canned refusal/identity substitutions, confirming that the previous raw-only baseline was methodologically confounded. But the task may prompt input copying or meta-commentary. **No high-quality speaking-as-Pretorius result is established.**

## Construction vs model contribution

SmolLM2 D: **0/20** accepted style labels; all 20 generated arbitrary text and triggered the reviewed deterministic fallback. Its delivered outputs were therefore equivalent to E. There is **no observed marginal language benefit** from the 135M model in D.

Qwen D: **20/20** valid style-label responses, but **all 20 were exactly `curious`**. It could follow the much smaller finite-choice instruction, but showed **no context-dependent style variation** in these prompts. The resulting sentences are safe constructions but not proven more natural than E. They have not been judged blindly.

D and E both protect the 10 verified values because the renderer **copies the exact validated first-person evidence clause**. This is a *limited lexical and structural guarantee*. The experimental parser extracts from flattened canonical first-person text, rather than verifying a typed `PhenomenalEvent` source item. A production verifier must use the typed subject event and its provenance, and must be hardened against adversarial multiline or spoofed quotations. Neither the model nor the construction should be authorized to manufacture durable world evidence.

## Next discriminating experiment (do not silently tune current held-out sample)

1. **Keep this result frozen.** Add separate diagnostics for scaffolding echo, meta-prompt echo, addressee inversion, repetition and empty moralizing. Include a human-rating sheet and score only untouched samples.
2. **Test a protected-slot clause realizer** (new experimental renderer strategy, not new organ) that lets the model vary *approved surrounding first-person language* while the trusted construction inserts exact facts. Maintain an independent no-model construction control.
3. Check whether **constrained decoding** (e.g. enumerated style or construction IDs) improves a 135M model's obedience over free-form instruction, and whether the selected constructions actually change with context. No blind improvement = no model contribution.
4. For all future production candidates, shift protected-fact selection to **typed, provenance-bearing Doctor SubjectFrame items**, not regex on flattened input; preserve the subject-access firewall.
5. Only then test another frozen batch, larger realistic scenes, and independently blinded character-naturalness judgments. Do not claim frontier-quality dialogue on this evidence.

**Disposition:** Do not merge PR #59 or alter the frozen Synthetic Ipseity/Sensus donor modules. No new cognitive organ is justified. Renderer-only experiments remain research previews.
