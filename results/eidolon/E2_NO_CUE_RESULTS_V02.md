# Eidolon E2 No-Cue Prospective Intention: Executed Construction Report v0.2

**Date:** 2026-10-09 America/Chicago, 2026-10-10 UTC.  
**Evidence status:** executed, reproducible, algorithm-tailored construction demonstration. Not an independent scientific replication or evidence of learned recurrent synaptic identity.  
**Protocol:** [EIDOLON_E2_NO_CUE_PROTOCOL_V02.md](../../docs/EIDOLON_E2_NO_CUE_PROTOCOL_V02.md).  
**Full architecture:** [EIDOLON_ENGINE_FULL_ARCHITECTURE_DRAFT_V1.md](../../docs/EIDOLON_ENGINE_FULL_ARCHITECTURE_DRAFT_V1.md).

## Source and execution provenance

The protocol was committed before source/testing changes: `d6a5b0a4858373bfd7f185fee9e4755fd02268e1`. The pre-result implementation/CI head was `a27c6653dba27796e4ecfb7109efdd1b9828a848`. GitHub Actions executed on PR merge ref `bcdbe504caf8c773a33f31b64ff6f359a3cbbd84`.

[Isolated Eidolon CI run 38023217798](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38023217798): **20/20 targeted tests passed**. Both old v0.1 construction assay and new E2 JSON were generated. [Original archived artifact 11658388408](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38023217798/artifacts/11658388408) contains the two JSON files; ZIP SHA-256 is `377188f4ca9a0b8bcc207284902ab7636e9da28576564f05a15c04adae3503ee`. [Permanent per-case E2 JSON transcription](E2_NO_CUE_CONSTRUCTION_V02.json) retains the E2 data if CI artifacts expire.

[Production brain test suite 38023217784](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38023217784): **344/344 tests passed**. [Gate1 fresh install 38023217757](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38023217757) and [causal-audit repeatability 38023217821](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38023217821) also completed successfully. These workflows establish software safety and regression compatibility, not biological or behavioral validity.

## Six-arm fixed construction assay

Each arm trained or withheld one explicit symbolic/lexical cue associated with one action, carried three input-free state transitions, then supplied the same uniform ten-action base policy to a **read-only, no-cue** decision probe. Cases are constructed for this algorithm. There is no statistical generalization claim.

| Condition | Correct target top-1 | Mean target probability |
| --- | ---: | ---: |
| Intact bound trace | 4/4 | 0.237215240 |
| No learning | 0/4 | 0.100000000 |
| Binding lesion | 0/4 | 0.100000000 |
| Recurrence lesion at decision | 0/4 | 0.100000000 |
| Cue-only with recurrence removed | 0/4 | 0.100000000 |
| Shuffled teacher labels | 0/4 | 0.084753862 |

The intact mean target advantage over recurrence lesion is **+0.137215240** probability points. Each of four intact cases is identical under the fixed uniform policy and each returns 0.237215240 for its assigned action. The label-shuffled model chooses its trained *wrong* action rather than the correct test target. The 0/4 for neutral ten-action conditions arises from stable ties resolving to `explore`, not evidence those control policies actively reject the target or meaningfully choose incorrectly.

**Interpretation:** E2 successfully isolates the designed *state-carryover computation* from a fresh direct-cue lookup. On this construction battery, final policy probabilities depend on whether the Noetic Trace is available. This resolves the instrumentation confound observed in v0.1.1, where the recurrence lesion still had 4/4 top-1 because the next incoming text could immediately reactivate an association. The original v0.1.1 result remains historical evidence and is not revised.

This test is almost guaranteed to favor the explicit trace in the absence of a cue because its fixed readout receives information from that trace and the lesion arm cannot. It is consequently **mechanistic verification, not independent evidence that this is a superior cognitive architecture**.

## Real Pretorius shadow integration

A temporary real `PretoriusBrain` instance with the repo's 128-unit test configuration received a subject-native lived interaction involving Henry and an explicit supervised `create` target. The intact shadow then advanced three no-cue transitions while leaving the actual Pretorius database, neural state and renderer untouched.

| Output | Probability assigned to `create` |
| --- | ---: |
| Real Pretorius neural policy before shadow modification | 0.105351503 |
| Shadow after trained intention and three no-cue ticks | 0.247887315 |
| Same shadow with trace removed at the final readout | 0.105351503 |

The real Pretorius database digest, recurrent neural tick and Subject Frame remained identical before and after shadow evaluation. The change is a numerical **counterfactual shadow distribution**, not an actual action taken by Pretorius. No evidence yet establishes altered action selection, episodic causal memory, autonomous goal formation, learned recurrent synapses or any subjective experience.

## Decision and continuation

**E2 engineering instrumentation: PASS.** E2 behavior matches the declared construction mechanism; 20 targeted and 344 overall tests passed. **Evidence of genuinely improved identity or learned recurrent neural plasticity: NOT ESTABLISHED.** Production adoption remains BLOCKED.

The next research phase must add prospective temporal goals and provenance-carrying events to the architecture while keeping the authoritative Pretorius store singular. It must construct an independently authored, sealed evaluation with matched direct-cue, recurrent, external-memory and no-learning baselines, then test whether the learned recurrent substrate changes verified downstream decisions in matched cloned Pretorius states. Distinguish *acquired dispositions* from persistent short-term activation and arbitrary keyed recall. The production branch and neural checkpoint migration rules remain unchanged.
