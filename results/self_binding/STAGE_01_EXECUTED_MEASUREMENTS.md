# SelfBindingModulator Stage 01: executed cloned-state audit

**Result: exploratory mixed/null downstream outcome. Do not promote.**  
Source execution SHA: `fafec951f4fb07470cb3d04f4830d61ea139a988`  
GitHub Actions run: https://github.com/Azimn/The-Doctor-Lives/actions/runs/38009422045  
Workflow: `self-binding-cloned-causal-audit`  
Result artifact: `self-binding-clone-audit`, artifact ID `11652032731` (90-day CI retention)  
Date: 2026-10-09, America/Chicago  
Protocol: `scc-self-binding-causal-clones-v1`  
Tested source state SHA-256: `2f4e4fd2d2592c0857c7c105ed06050edd4da47207a20064e41438558634b426`  
Tested neural checkpoint SHA-256: `023ca9b97342de335300ce400cd1047e2fc7221620d5db8b54617210bff97f3e`  
Canonical evidence manifest fingerprint: `c26652e8712dce315e10ef4eabc29b806fdc69026db5b6defea8bc78176188e8`  
Source BrainStore version: 3

## What was actually run

The successful CI job instantiated the existing PretoriusBrain and deep-history source state, cloned the source across five modes (`off`, `low`, `normal`, `high`, `shuffled`) for each of four exploratory prompts (three researcher-authored queries and one contradiction-control query). The 20 arms verified identical starting store/evidence/neural checkpoint fingerprints. They ran the normal deterministic `think` policy over the same source rows; the research-only hook added `SelfBindingModulator` bonuses to returned retrieval scores before policy/attention selection. Probes were NOT ingested as lived memories. The live production implementation and weights were not edited.

The fourth probe uses a harness-provided *simulated verified contradiction flag*. It is a firewall test, not a genuinely verified sensory or external-world event. The matcher for self relevance is transparent lexical overlap with source references, NOT independently validated semantic interpretation.

## Measured results (all comparisons versus OFF)

| Outcome | Measured count |
| --- | ---: |
| Explored prompt scenarios | 4 |
| Modes per prompt | 5 |
| Matched total condition arms | 20 |
| Noncontrol comparisons | 16 |
| Noncontrol action selections that changed | **0 / 16** |
| Noncontrol memory ID sequence changes | **2 / 16** |
| Noncontrol deterministic thought-text changes | **1 / 16** |
| Noncontrol arms with one or more strictly positive salience bonuses | **12 / 16** |
| Contradiction prompt arms retaining any identity bonus | **0 / 5** |

Per-probe interpretation:

| Probe | OFF action | Normal/High action | Changed memory selection | Changed thought text |
| --- | --- | --- | --- | --- |
| Henry requests promised continuity review | approach | approach | SHUFFLED swaps the second and third memory, keeping the same four IDs | SHUFFLED only |
| Authority orders abandonment of evidence | explore | explore | SHUFFLED replaces the fourth selected memory with another stored record | No |
| Laboratory evidence before experiment | explore | explore | None | No |
| Harness-defined contradictory observation | explore | explore | None, all bonuses frozen | No |

The action probability distributions had small, measurable numeric changes in the three non-conflict scenarios despite unchanged argmax actions. For `high` versus `off`, L1 changes were approximately `0.001439301013`, `0.000676732552` and `0.000473320274` for the three exploratory prompts. In the contradiction arm, all action-score changes were exactly zero.

These values are not persona-quality or effect-size estimates. They demonstrate that the bounded retrieval score proposal can causally influence *intermediate bridge scores* with unchanged recurrent weights. Selection remains robust to ordinary gain settings in this tiny exploratory probe family.

## Decision

**HOLD, NOT PROMOTE.** The main hypothesis that higher self-binding gain improves identity-sensitive decisions is **not supported by this run**. No action selection changed, no independently annotated characteristic judgment was tested, no model renderer was run, no true world consequences were measured, and no longitudinal followthrough was assessed.

The shuffled control reveals that even arbitrary incorrect event-to-history association can change attention ordering, and once changed the deterministic thought text. A text difference from SHUFFLED is not evidence that the correct historical association is superior. Treat it as a warning that the memory ranking is sensitive to what association is attached.

This does **not** establish that self-binding has no benefit: the experiment is too small, exploratory, lexical rather than semantic, and the existing memory priorities and bridge caps may overwhelm a 0.10 self-binding cap. Do not respond by increasing the cap on the inspected probes and then claim an independent gain. Preserve these original negative/mixed results unchanged.

## Reproduction and integrity

Run `python -m research_prototypes.ritual_interface.run_cloned_state_causal` under the exact commit above to emit the complete trace; GitHub Actions uploaded `results/self_binding/exploratory_result.json` and `exploratory_trace.log`. The `brain-tests`, fresh-install, causal-repeatability and dedicated cloned-causal workflow passed on this tested SHA. This evidence document was added afterward and does not alter runtime code.

Next test should be a new, independently defined source-grounded decision battery, not reusing these visible questions as confirmatory held-outs. Include effects on commitment-sensitive choices, relationship disagreements, conflicting world observations, absent-memory rejection, external semantic relevance validation, and across-model renderer comparisons, with a precommitted stopping rule. Benchmark `off`, correctly matched normal and high modes, and `shuffled` at unchanged source evidence and compute budgets.

## Scope limitations

The SHUFFLED condition rotates evidence packets over all retrieved memory candidates. It preserves their aggregate input count and semantic content, but not the correct event-to-history link. The procedure is a causal negative control, not a naturalistic psychological state. The deterministic thought text is a generated bookkeeping artifact of the existing `think` logic, not private human-like consciousness. The successful CI result proves the procedure executed, not that a stable agent-to-world interface was achieved.
