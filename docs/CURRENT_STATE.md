# CURRENT STATE: The Doctor Lives

## Active M5 + PR #98 reconciliation, October 30, 2026

`integration/m5` now contains a real two-parent merge of existing M5 `eed7720` and draft PR #98 `13007ce`: [merge `be3e1e0`](https://github.com/Azimn/The-Doctor-Lives/commit/be3e1e0024abd78027ea30a36b38903132e4ad5d). The subsequent [`fc8df09`](https://github.com/Azimn/The-Doctor-Lives/commit/fc8df096d07aee80d60901758b5addccb4111ca3) preserves the existing model import-inventory regression while recognizing M4/M5's loopback-only research adapters. M5 retains its broader M2 motor-ID/no-reuse validation in preference to the narrower PR98 version. Source Laboratory is still pinned at `6e49795752835d64fa6fd63d16359669a1ca2ba7`. Production `main` and original PR #98 have not been merged or modified.

**Combined candidate evidence, not release acceptance:** Linux physical/host/wheelhouse [41062084909](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062084909) and complete BrainStore [41062084977](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062084977) passed on the initial merge SHA. New latest-source combined runs are [M2/M4/M5 judges](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219862), [real M4 Ollama plus PR98 model gloss](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219854), [PR98 Linux Laboratory](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219883), [Windows and offline wheelhouse](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219917), [full BrainStore](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219845), and [original 17-book source read](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219850). These must be examined for actual pass/fail on one exact head; earlier results do not automatically transfer.

**R1 integration is a candidate, not independently accepted. R2/R3 are incomplete candidates. R4, R5 and R6 remain NO-GO**, notably no uncoached self-originated three-task goal, no 24-hour real elapsed-time soak, and no merged-main release. No Conclave, Phantasmagorium, Calibos or new features are included. Defer unrelated security enhancements without relaxing provenance, functional integrity or preexisting tests.


**Research snapshot:** October 30, 2026. Definitive production repository: Azimn/The-Doctor-Lives. The only canonical character is Doctor Septimus Pretorius, whose original BrainStore owns his identity, memories, relationships, thoughts, neural checkpoints and policies.

## Branch custody

- `main` remains production and has not been modified for M1, M2, M4 or M5.
- `integration/m1`: stacked six-organ, D3 provenance, autobiographical book preference, and experience-to-action integration, verified by draft PR #102. **PR #102 stays draft; do not merge.**
- `integration/m2`: accepted bounded three-day *simulated* original-Noesis work trial, retained as exact regression.
- `integration/m4`: accepted hybrid local-model open-intentions source evidence; fallback and new data-described operator capabilities.
- `integration/m5`: active isolated candidate based on M4's green `1406668dd2dce7585acd6ea80bad1b3406b42032`; no production promotion.
- PR #98 branch `experiment/pretorius-experience-to-action-20261028`: six changed source files reconciled onto M5, including elapsed-time Laboratory work and its tests, with the M2 work-ID collision repaired without allowing cross-domain reuse.
- Six-organ architecture PR #89 remains draft. PR #100 contains design-only Conclave and Phantasmagorium, not executable organoids. No Calibos identity, memories or agent state have been imported.

## M5 substance

`scripts/verify_semantics.py` was written first. M5 replaces the 10-action text hash with a transparent meaning-based fallback and opt-in local Ollama embeddings (`PRETORIUS_LOCAL_EMBED_MODEL`, loopback only). Original Noesis retains sole choice authority. Per-family novelty is capped at +0.05, familiarity and history capped separately, and each decision records components and the final policy. Source-verified Laboratory/operator permissions still own all actual actions.

`scripts/m5_attribute.py` is a 20-seed real CausalAuditHarness clone experiment that neutralizes both cloned recurrent weights and motor readouts; it must report native policy choice changes and expressly states this is not itself a paired, altered M5 physical-work rollout. `scripts/m5_donor_ablation.py` provides a 20-seed same-snapshot nonactuating donor-on/off/cheap-control comparison. All donor modifiers are OFF by default; see `docs/DONOR_HARVEST.md`.

`tests/test_m5_ingress_shipping.py` exercises the shipping `doctor-lives` CLI on forged book sources, world JSON, received fictional claims, and privileged telemetry. It distinguishes the actually lived *receipt of a report* from a verified physical book read. The existing `tools/verify_17_full_text_lab.py` and pinned Laboratory 17-book workflow remain source-backed tests; the optional corpus is not silently installed into normal fresh worlds.

## Release gates

An isolated development success is not permission to promote `main`. All existing M2/M4 judges, the new semantic judge, full BrainStore CI, source-backed default-entrypoint tests, and new donor evidence must pass at the final exact M5 head. Donor superiority requires verifiable **behavioral/outcome** advantages over equal-information simple controls, not merely a new neural score, a permitted action, a test fixture or nicer prose.

The six primary organs remain unevenly graduated. Conclave and Phantasmagorium are planned auxiliary organoids, not deployed runtime modules. Keep independent first-person provenance, authorized Laboratory receipts and subject-visible versus engineer-private state separation. Preserve UTC ISO timestamps for source ordering, with Swatch @beats for project-facing displays where clocks are surfaced.

## Executed semantic and neural attribution checkpoint

The original semantic judge was written before the semantic mapper: 30 intentions, 3 phrasings each, 60 discriminating paraphrase comparisons. The deterministic semantic fallback maps **58/60 paraphrases to the same category (96.67% invariance)** and **88/90 utterances to their preregistered expected class (97.78% accuracy)**. The predeclared gate was 90% for both metrics. This is **not** yet a measured embedding-model accuracy result.

In a completed 20-seed M5 source-backed CI run [41006397303](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41006397303), source clone analysis recorded **12/180** selected M4 intentions changing when the bounded novelty contribution was removed; counterfactually neutralizing the cloned recurrent motor and weights changed **8/20** matched native *cognitive* choices, mean native score L1 **0.02395957**. The lesion has not yet established a change to the *open intention action* itself on matched physical rollouts. No default host action grants or world receipts are removed. All three donor adapters remain OFF unless explicitly enabled for research.

The M5 donor ablation reported CASCADE **0/180**, grounded household **0/180**, habit history **42/180** choice differences versus donor-off. Those are nonactuating counterfactual ranking changes, not verified additional world outcomes. See `docs/DONOR_HARVEST.md` for the equal-information simple baseline and decision.

The latest M5 execution status must be determined from the exact-head GitHub Actions workflow results; do not treat this earlier measured passing run as a blanket certification of later changes. The new pinned seventeen-book and shipping-entrypoint workflows must pass before release qualification.

## M5 updated causal-result disposition

[Exact-source CI 41007830836](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41007830836) passed the original M2 judge, original M4 fallback judge, M5 semantics attribution and 20-seed donor comparisons. The post-null bounded original-neural contrast produces a different profile from the earlier phase: **34/180** decisions sensitive to removing novelty; native W-plus-motor readout lesion **10/20** different native cognitive choices and **13/20** different same-source free-intention candidate replays. Recurrent-W-only lesion changes **0/20** in both native cognition and candidate replays. Hence the *overall native motor readout* matters in the candidate score, but the recurrent weights alone were not necessary in this test.

The donor comparison now shows CASCADE 0/180 choice changes, household physical grounding 0/180, habit trace 41/180, with zero verified additional physical outcomes. All remain explicitly OFF. Local 768-dimensional Ollama embedding smoke passed; 58/60 paraphrase invariance is measured on the deterministic fallback, not the full model-on embedding pathway. The absolute evidence is limited to the experiments' sources, not new artificial-general-intelligence, human equivalence or consciousness claims.

The historical earlier M5 numbers retained above are *source-specific checkpoints*, not alternative current success claims. Full latest-head 17-full-text book CI and any subsequent documentation-only push must be checked separately for actual green status before promotion.
