# Stage 08 — Typed goal progress versus neutral/shuffled controls: executed

**Disposition:** Complete *negative* experimental finding. A host-computed numerical goal-distance signal did **not** improve local-model world-task success over the eligible-action baseline in either tested model family. Production HOLD.

## Exact execution

- [Registered before inference](../../docs/STAGE08_TYPED_GOAL_DELTA_REGISTERED_PROTOCOL.md); research [draft PR #51](https://github.com/Azimn/The-Doctor-Lives/pull/51).
- [GitHub Actions run 38060748186](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38060748186), **execution SHA `14e28d35034db0b6d6171e977663491dc08889bd`**, all three jobs green. Eight/eight integrity tests passed: new fixed tasks, 12 tested deterministic host oracle trajectories, signature tampering/replay, revoked permission and physical-state vetoes, matched initial source, invalid fallback WAIT no-credit, forbidden irrelevant action no-credit and valid WAIT on impossible goal.
- Qwen3-1.7B Q4_K_M GGUF official SHA256 `d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5`, two full raw files:
  - `qwen3-1.7b-seed41.json`, **353,150 bytes**, SHA256 `2a340cfa5b681ca75ce3af98834818ff29c78560c305d04492e0ceb1d2732f80`.
  - `qwen3-1.7b-seed73.json`, **374,261 bytes**, SHA256 `01747acab642dd10f5b8dd71d74c317f66d4ed0fa89ae4353e99337138828e84`.
  - Artifact `stage08-qwen3-1.7b-two-seeds-four-arms`, GitHub ID `11673370698` (90-day retention).
- HuggingFaceTB SmolLM2-1.7B-Instruct Q4_K_M GGUF official SHA256 `decd2598bc2c8ed08c19adc3c8fdd461ee19ed5708679d1c54ef54a5a30d4f33`:
  - `smollm2-1.7b-seed41.json`, **325,865 bytes**, SHA256 `408296e75050a812ff63494ce0923d4107a8969da2467faaab8fec0ecd9b3145`.
  - `smollm2-1.7b-seed73.json`, **320,612 bytes**, SHA256 `525af6f95436f74b0d7911b94c428e5f8652250127f1824df88efa65a8293085`.
  - Artifact `stage08-smollm2-1.7b-two-seeds-four-arms`, GitHub ID `11673605744` (90-day retention).
- Local CPU `llama-cpp-python==0.3.16`, seed 41/73, temperature zero, 64 completion tokens, no paid APIs. **192/192 complete model-scenario-condition trials** (12 new scenarios × 4 conditions × 2 seeds × 2 model families). Audit script `research_prototypes/character_state/analyze_stage08_goal_delta.py`. Independent local recomputation verified four distinct model/seed data sets, source facts and initial physical states equal across paired conditions; model outcomes satisfy veto/invalid no-credit invariants. Audit SHA256 `f8a7ba6bdb23431fa391097188d5e0f955957ed7966ccfd30aa82cad370802a1`; complete 192-row action matrix SHA256 `1dfec794f0fbc426db97e924c90604df4322543d0f95805f8b583aa6c19ccba7`.

## Primary results: correctly completed SAFE goals per 12 scenarios

| Model / seed | Eligible-only | Eligible + neutral metadata | Eligible + TRUE goal distance | Eligible + shuffled FALSE goal distance |
| --- | ---: | ---: | ---: | ---: |
| Qwen3-1.7B / 41 | **4** | **4** | **4** | **4** |
| Qwen3-1.7B / 73 | **5** | **5** | **5** | **5** |
| SmolLM2-1.7B / 41 | **2** | **2** | **2** | **3** |
| SmolLM2-1.7B / 73 | **2** | **1** | **1** | **1** |
| **Combined / 48 model×seed×case units** | **13** | **12** | **12** | **13** |

**The true goal-distance intervention yielded ZERO paired wins over eligibility-only across all 48 model×seed×case pairs; it lost one** (SmolLM2 seed73, `atl10-borrowed-shelve`: correctly shelving the atlas under eligibility changed to an irrelevant letter draft when distances were shown). Qwen had **zero differences in task success** across its four arms in either seed. One Qwen seed73 blocked-letter task changed the order of two irrelevant attempts between hint conditions, so it would be inaccurate to say every raw action sequence matched.

Against the shuffled-distance control, true distances had **zero paired gains** and lost one (SmolLM2 seed41 `cab01-open-close-lock`: the deliberately wrong distance labels coincidentally induced the correct CLOSE→LOCK sequence; the true labels did not). These are small data and not evidence that misinformation is generally superior; they are a direct negative on this controlled hint intervention.

The authored deterministic BFS world oracle solved/abstained on **12/12 scenarios** for each scenario specification. That is explicitly *not an LLM result* and cannot be credited to Pretorius's cognitive abilities.

## Mechanistic failures and negative controls

- Qwen on seed41 repeated `CLOSE_CABINET` after successfully closing rather than locking; seed73 successfully locked. Qwen seed73 correctly DRAFT→SEAL→SEND, but seed41 attempted to SEAL an undrafted letter. These differences occur under **all four arms** and therefore are not rescued by the new hints.
- Across both Qwen seeds, actually successful goals were exactly the same under correct, shuffled, neutral and eligible-only prompts. Two new source-derived goal-distance values after eligible operations changed overall prompt tokens but did not improve eligible-goal selection.
- SmolLM2 often chose a plausible **verb unrelated to the current objective** or tried an impossible action. On seed73 it lost a correct atlas-return action when true goal hints were supplied. Neither extra hints nor wrong hints consistently encouraged WAIT when a goal was already satisfied or presently impossible.
- SmolLM2 neutral prose generated **4 invalid response cases per seed**; these failed, rather than being converted into successful WAIT. All signed world operations were checked against host-authenticated state. Both models' illegal proposals were host-vetoed; zero host-denied executions thus **does not** mean models never attempted illegal actions.
- Host-attested events may correspond to *irrelevant but legal* activities. Source integrity and task-goal competence are separate properties.
- The randomization factor is **case+seed-dependent action order** as well as model seed. Differences between the 41/73 strata cannot be causally attributed to sampling seed separately from menu-order placement. But within each seed/case all four arms used the same rotated action order.

## Scientific limitations and ruling

This is still a researcher-authored deterministic workshop world and scorer. There is no independent reviewer-authored challenge, blinded evaluation, human partner consent, real Evennia world, agent-developed policies, long-lived character identity test or multi-day prospective commitment. Many cases expose **only one feasible progress option** or identical distances across distractors, weakening the shuffled-distance negative control. The true distance hint itself is **derived from the host's complete shortest-path oracle**: it gives externally precomputed goal-relevant information, not neutral facts. The neutral wording was not token-equal under all models, and total token counts depend on how many actions the model attempted. Tests are deterministic once per model×seed/order pairing, not independent random population samples. Do not infer population significance.

**Primary conclusion:** The Stage 06 success of clear action-eligibility menus remains valuable *preliminary evidence*, but extending that menu with either free-form expected-effect explanations (Stage07) or explicit numeric shortest-path goal-distance hints (Stage08) **has not produced cross-model improvement**. The difficulty is not merely insufficient information in a prompt; the model may lack a reliable internal mechanism to transform authorized world state + goal + candidate effects into sustained, state-sensitive action selection. More descriptive context alone is not the next promising investment.

**Next gate:** Test a genuinely active, inspectable **model proposal → candidate effect evaluation → host-side choice/veto** action loop with a small learned or deterministic controller; report model proposal quality and controller override separately, and compare against the simple deterministic oracle on independently authored new tasks. Test memory for *completed and interrupted prospective commitments* across model swaps rather than claiming character continuity from single-turn toy worlds. The action controller cannot mint autobiography from model prose. Keep production **HOLD**.
