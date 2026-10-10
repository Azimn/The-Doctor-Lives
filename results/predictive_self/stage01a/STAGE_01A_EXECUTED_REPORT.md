# Predictive Self Loop Stage 01A: executed chronological native-policy benchmark

**Status: COMPLETED EXPLORATORY CHARACTERIZATION / production HOLD**  
Protocol frozen **before** code execution: [PREDICTIVE_SELF_STAGE_01A_PROTOCOL.md](../../docs/PREDICTIVE_SELF_STAGE_01A_PROTOCOL.md)  
Source execution SHA: `edf35dcaa6449bc2ed73a359c349e8be31e50f0b`  
GitHub Actions run: https://github.com/Azimn/The-Doctor-Lives/actions/runs/38016542721 (SUCCESS; 3/3 dedicated benchmark tests pass)  
Full 28-case raw artifact: `psl-stage01a-native-policy-benchmark`, artifact ID `11655798019` (90-day Actions retention)  
Full extracted JSON SHA-256: `fa98969ab939cb055bfede464f7c5653ee9f53052a3745fa6bf097de46d17ef2`  
Git-persisted, rounded row evidence: [MEASURED_PER_CASE.csv](MEASURED_PER_CASE.csv).  
Primary state manifest: `c26652e8712dce315e10ef4eabc29b806fdc69026db5b6defea8bc78176188e8`.  
Initial checkpoint fingerprint: `023ca9b97342de335300ce400cd1047e2fc7221620d5db8b54617210bff97f3e`.

## Experiment

One source-verified native PretoriusBrain was initialized with real canonical evidence and a scripted open Henry review commitment before the experimental snapshot. Across 28 investigator-authored subject-native stimulus texts, each forecast was sealed before `brain.ingest` and a subsequent explicit `brain.think`. A read-only adapter verified each action against the actual persisted native `policy_decisions` row. The subject was not asked to execute any real-world action. No `WORLD_VERIFIED` events were fabricated for this benchmark, no canonical identity information was modified, and the shadow observers did not write BrainStore.

The sample is 16 sequential training/adaptation cases from four repeated contexts; 8 later cases drawn from those familiar contexts; and 4 cases from two new context categories. Scene labels are author-supplied, the scenes are closely related paraphrases, and the four unseen-context cases are diagnostic, not independently blinded validation.

Forecasters: frozen neural prior; global action-frequency predictor with prior strength 5; exact-context frequency predictor with strength 5; Predictive Self Loop (episodic-only); PSL with an **unvalidated** source-anchored semantic action proxy; PSL with rotated training-time context/partner assignments (negative control); plus a dynamic pre-ingest neural-score diagnostic. Every main comparator receives the same initial 10-action vector and action history in chronological order.

## Primary results

The metric is **multiclass log loss in natural logarithm units**, lower is better. These are selected action predictions, not whether Pretorius's behavior was appropriate, characteristic, or beneficial.

| Model | Familiar contexts (n=8): mean log loss | Familiar multiclass Brier | Familiar top-1 | New contexts (n=4): mean log loss | New top-1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Frozen original neural prior | 2.302585 | 0.900000 | 0.125 | 2.302585 | 0 |
| Global frequency | 1.129793 | 0.507148 | 0.750 | **1.670225** | **0.500** |
| Exact context frequency | 1.318439 | 0.530154 | 0.625 | 2.393746 | 0 |
| PSL episodic only | **1.126915** | **0.431498** | 0.625 | 2.439326 | 0 |
| PSL source-anchored, *unvalidated* semantic proxy | 1.121084 | 0.431549 | 0.625 | 2.418055 | 0 |
| PSL corrupted training context/partner mapping | 1.568965 | 0.791746 | 0.250 | 2.439326 | 0 |
| Dynamic pre-ingest neural diagnostic (different state) | 2.301622 | 0.899851 | 0 | 2.316231 | 0 |

The PSL episodic forecaster had a **0.002878 smaller mean log loss** than the simple global-frequency baseline on the 8 familiar-context cases. This difference is too small and the case set too limited to claim an overall benefit. The Brier difference, `0.431498` vs `0.507148`, is larger, but likewise not an independently replicated advantage. Global frequency had higher familiar top-1 accuracy, **6/8** versus PSL's **5/8**.

On the **4 new-context cases**, PSL had worse log loss (`2.439326`) than the global baseline (`1.670225`) and **0/4** top-1 choices compared with **2/4** for the baseline. Repeated context-specific adaptation has not generalized to novel situations. Note that these two unfamiliar labels recur twice within the OOD phase, so even the OOD diagnostics are not four wholly independent contexts.

Shuffling the training context/source association harmed familiar-context PSL predictions (`1.568965` vs `1.126915`), consistent with context alignment mattering for these authored scenarios. It does not demonstrate semantic autobiographical truth: this lesion shuffled simple event labels, not independently adjudicated life meanings.

## Action-state skew and alternative explanation

Across the 28 native choices: **persist 18**, **explore 7**, **challenge 3**; the other 7 action classes were not selected. Training had 10 persist / 6 explore, familiar evaluation 6 persist / 1 explore / 1 challenge, new-context diagnostic 2 persist / 2 challenge. This serious imbalance favors frequency predictors and makes large relative improvements over an approximately uniform ten-action neural prior unsurprising.

The native recurrent distribution before each probe remained nearly uniform on these sampled conditions even though the final policy repeatedly selected persist. The established state-to-policy bridge and recurrent argmax selection may explain this disconnect; this study did not lesion the bridge, so do not assign exclusive causal responsibility.

## Semantic identity hypothesis still untested

No real world-attested episode was admitted, so the model's slow semantic self posterior had **zero** externally witnessed revision events. The semantic proxy is a manually chosen action mapping with an admitted source identifier but **not a reviewed claim-to-behavior entailment**. Its small forecast changes cannot support a conclusion that identity is better modeled. The subject's actual relationships, consent, world actions and delayed promise outcomes were never measured. The experiment's claim is restricted to predicting internally stored choices.

## Integrity and reproducibility

The original frozen protocol, executable source code, CI run and 28 case labels and rounded per-arm losses are available in Git. GitHub Actions stores the full, signed-by-no-one runtime JSON artifact for 90 days, including each case's sealed forecast digests, source state, native selected action and pre-outcome forecast distribution. Its SHA-256 is recorded above to detect alteration. The permanent CSV preserves chronological action labels and outcome losses, but not full unrounded probabilities; do not misrepresent it as identical to the full artifact.

The source adapter witnesses real local policy choices, not an independent physical or simulated external-world actor. A new temporal guard rejects out-of-order observations and advances the forecast cutoff after each admitted event. Unit tests assert 28 native witnesses, 0 world outcomes, unchanged BrainStore by the observers, increasing event ticks, probability normalization and fixed baseline.

## Decision and next engineering hypothesis

**HOLD PSL policy promotion.** The meaningful result is not that the Game of Self has been empirically proved, but that context-sensitive shadow forecasts are feasible and can outperform a frozen uninformed prior in a limited setting; simple global empirical frequency remains a strong competitor, especially under context change.

Next proposal: a **hierarchically smoothed context model** that backs off to a calibrated global action prior when a context is unseen or weakly supported, while retaining partner-specific context only when supported by sufficient observations. Freeze a **new** evaluator including genuinely distinct scenarios before testing this post hoc idea. Compare contextual frequency plus global fallback against PSL, and independently add verified world outcomes, promise followthrough, disagreement and source-grounded relationship priors. None of this authorizes a second decision controller or automatic subjective access.

## Independent rerun audit and qualified repeatability

The exact source execution commit `edf35dcaa6449bc2ed73a359c349e8be31e50f0b` was rerun as a separate GitHub Actions job attempt within workflow run `38016542721`, and it passed again. Full extracted raw JSON SHA-256 hashes were:

- Attempt 1, artifact `11655798019`: `fa98969ab939cb055bfede464f7c5653ee9f53052a3745fa6bf097de46d17ef2`.
- Attempt 2, artifact `11656373275`: `c059006361a02a6794d340d8cdbe61ea14c5da1eb53e3167792c4b4a286f166e`.

**The raw files are NOT byte-for-byte identical.** Structural comparison found differences exclusively in the `native_pre_ingest_diagnostic` probabilities and its floating-point score calculations, at roughly 1e-9 magnitude. All 28 actual action choices and **every controlled forecast vector and scoring result** were exactly equal. If the explicitly ancillary dynamic-neural diagnostic is removed from per-case forecasts/scores and phase summaries, both payloads canonicalize to the **same** SHA-256: `43b4c2dc6cc3298b633a91126b6d3a540829d5bb91be8eb27d68258539c7a7b6`.

A fail-closed comparator `research_prototypes/predictive_self/compare_native_replays.py` and tests formalize that narrow exclusion. Details are preserved in [REPLAY_VERIFICATION.json](REPLAY_VERIFICATION.json). Therefore, the **primary policy-prediction results reproduced exactly**, but whole-file byte identity was not achieved. Do not hide this qualified repeatability when reporting or synthesizing findings.
