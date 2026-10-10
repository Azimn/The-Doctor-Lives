# PSL Stage 01A: chronological native-policy prediction benchmark

Status: **protocol frozen before implementation and execution; exploratory, not independently held out**  
Source parent: `research/predictive-self-loop-20261009`; development branch: `research/psl-stage01a-shadow-benchmark-20261009`  
Scope: read-only forecast accuracy for real PretoriusBrain policy selections; **NO** external-world outcome, partner-cooperation, promise-completion or phenomenal experience validation.

## Motivation and errors to guard

Stage 00 had 1 actual selected action and 3 mock world cases. A single native action with log loss equal to ln(10) provides no positive evidence of predictive self learning. The prior implementation permits an action witness from any subsequent tick after the fixed snapshot cutoff and therefore could accept replayed/out-of-order later episodes. Fix increasing episode ticks for serial work before interpreting chronological results. A `WORLD_VERIFIED` value from an untrusted caller is not evidence. The benchmark will **only** feed `RUNTIME_POLICY` actions verified from real `policy_decisions`, and these must never move the global semantic prior or assert world success.

## Fixed public scenario schedule (not a sealed battery)

- Exactly six cycles over four recurring contexts, total 24 decisions. First four cycles = 16 chronological adaptation/training observations; final two cycles = 8 in-family evaluation observations.
- Four contexts: laboratory apparatus, Henry collaboration, coercive authority, and an outstanding promise. Probe context labels are authored by the experiment harness and **not independently annotated**.
- Four additional chronological probes in two *new* contexts (missing evidence, novel visitor) form a 4-case out-of-distribution diagnostic, not confirmatory test. Total 28 native decisions.
- The scripted scenarios are fixed before viewing outcome actions. They enter `brain.ingest` as source-native observations, followed by one explicit `brain.think` decision. All decisions are recorded in a temporary, disposable BrainStore. Each policy is observed by lookup of the actual persistent `policy_decisions` row, not by typing an expected answer.
- No artificial success or relationship world fact is created. Authored labels and probes are **visible to developers**, not independent blind evidence.

## Forecasters and information parity

All forecasters receive the same initial 10-action probability vector and the same chronologically observed action history. No condition can choose the brain's action or receive future actions.

1. **Frozen initial neural prior**: original source snapshot probabilities, no adaptation.
2. **Global empirical Dirichlet**: previous native actions pooled regardless of context, prior effective sample size 5.
3. **Context empirical Dirichlet**: previous actions in the exact authored context with the same prior strength 5.
4. **PSL episode-only**: canonical research PSL with claims empty, strength 5 for context and 5 for partner. No semantic self-revision.
5. **PSL fixed semantic proxy**: same PSL but one *explicitly heuristic* source-referenced `(challenge, explore)` tendency with prior mean 0.65. Do not claim this is independently validated Pretorius identity.
6. **PSL corrupted context pairing**: during training only, rotate context/partner labels across the four categories while preserving exact native actions and evidence counts; at evaluation use true current labels. This negative control must be versioned as a **train/eval label misalignment**, not semantic disproof.

Optionally report the **pre-ingest dynamic recurrent prior** as an extra diagnostic with different temporally varying state. It is not information-matched to frozen-snapshot models and must not be used as their controlled effectiveness comparator.

## Scoring, integrity, and no leakage

Record all six pre-action probability vectors, source model/policy/manifest digests, source state tick, scenario, source state version, native selected action, native policy decision ID or hashed ID, post-ingest tick and observer mutation proof. Compute multiclass Brier sum and negative natural-log likelihood for each forecaster, mean values over the **8 fixed in-family evaluation cases** and separately over the **4 new-context cases**. Report accuracy and per-context results as descriptive only. No hypothesis testing or superiority claims from n=8.

All forecasters **must predict before** the native `ingest + think` call, then update only using the witnessed selected action. Predictions and ground truth should be committed as immutable per-case data in the CI artifact, with a machine-readable result permanently copied into Git by a separate provenance commit. Strictly increasing native policy ticks across episodes prevent backfilled "observations." Re-run from the same code SHA and seed should reproduce fixed action sequence and metrics, or a failed reproducibility gate should be documented.

Check equal model-input access, no BrainStore mutation by PSL observer, no semantic global updates without world evidence, no hidden cross-context leaks, and fail-closed on duplicate witnesses and invalid chronology.

## Disposition

This stage can demonstrate predictive gain on **native selected policy** only. It cannot establish correct action in the external world, realistic self-development, independent role labels, cross-renderer identity continuity, or that active inference outperforms simple Bayesian updating. Any positive result will require independent, blinded, source-verified world outcomes and context-disjoint evaluation. Any null is kept and reported. Production remains HOLD.
