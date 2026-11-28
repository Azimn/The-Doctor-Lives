# CURRENT STATE: The Doctor Lives

## M6 two-way operator conversation, October 30, 2026

`integration/m6` branched from the verified `integration/m5@99b6cdb`, preserving one original BrainStore, Noesis recurrent policy and source-pinned original Laboratory. The new `doctor-lives chat` and loopback-only `chat-serve` share one operator ingress and one source-verified reply path. Incoming operator claims are attributed as **operator statements**, never original world observations. Autobiographical replies cite authentic Laboratory action receipt and BrainStore memory, or an explicitly hypothetical stored wish. The local Ollama model is optional; deterministic model-off replies are guaranteed.

Frozen 40-family semantic holdout: **116/120 correct**, **37/40 all-paraphrases stable** without holdout-specific tuning. 18-decision donor wiring: CASCADE entered 18, eligible 0; household entered 0, eligible 0; habit entered 18, eligible 16, score-positive 16. The old household 0/180 is **untested**, not negative. Positive targeted original-world donor control scenarios were executed but no physical-world outcome advantage was shown. Donors remain OFF.

[Original-Lab M6 conversational CI 41075702190](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41075702190) demonstrated real multi-turn model-on/off three-day simulated conversation, authentic Noesis-first operator messages **[0,1,1]** per simulated day, authenticated memory and actual mid-session SIGKILL recovery. Original 20-seed CausalAuditHarness comparisons found **6/20** altered choices against no message and **12/20** against shuffled topic; report pressure is independently recorded per family. [Strict-source M6 41076414424](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41076414424) independently verified **9 lived actions, 17 outbound claim citations and 2 genuine Noesis initiative receipts**. Real local `qwen2.5:0.5b` used 2 model calls and 30 generated tokens; no hosted API.

**Current caution:** M6 remains a candidate branch, with final CI rerun needed after further source classification, surface integration tests and transcript reporting. Production `main` and draft PRs #98/#102 are unchanged. Full R1-R6 release approval, 24h elapsed soak and independent review are outstanding.


## M5 ChatGPT-authored stand-in and semantic donor harvest, October 30, 2026

On the existing combined `integration/m5` (M4 plus PR #98), [`878fbae`](https://github.com/Azimn/The-Doctor-Lives/commit/878fbae9c60b4d41c93e531e825f1efc589949a1) added a *test-only* ChatGPT-authored candidate corpus fed through original `InferencePort` and actual pinned Laboratory. It is not a ChatGPT API or live Ollama substitution. Five of six hypothetical ideas grounded in existing operator actions; one remained a wish. The original Noesis, not the fixture, chose one physical/operator task; independent receipt, one lived memory and one cold restart were verified in [CI 41068903914](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41068903914) and [CI 41069141705](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141705).

Initial new natural-language semantic checks were **7/10**, with diary writing, returning to interrupted work and hiding pages misclassified. The frozen fixture preceded the targeted semantic fixes at [`b92ac12`](https://github.com/Azimn/The-Doctor-Lives/commit/b92ac12ab7894041d91957e60c4eb787ca3ff978), now **10/10**. The original 90-utterance judge remained 88/90 correct and 58/60 paraphrase-consistent. The follow-on 20-seed, 180-original-decision donor audit found CASCADE 0 changes, household feasibility 0, habit 60, but **no proven superior physical outcomes**, so all remain OFF. Original BrainStore and offline Windows/Laboratory regression tests passed on `b92ac12`; see PROGRESS and DONOR_HARVEST for exact run links.

The branch also has later independent R3 loopback transport work at `a503452702184a34f549758a0e97078ebad99232`. Verify that head's CI before claiming full current-branch acceptance. The owner prioritizes functional integration and has deferred separate security hardening to documented technical debt. The initial QA redirect finding was a local 302 destination-bypass control, not evidence of Internet exfiltration. No production main merge, external API key, new brain/organ, donor promotion or release tag occurred. R1-R6 complete release gates remain open.


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
