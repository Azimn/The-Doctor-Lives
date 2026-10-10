# Stage 05 — Qwen3-1.7B chooses actions against a persistent laboratory host

**Disposition: FULL OBJECTIVE NEGATIVE for PHASE-only formatting on the tested decision tasks; production HOLD.**

## Provenance and execution

- Full source-controlled [precommitted Stage 05 protocol](../../docs/STAGE05_MODEL_WORLD_DECISIONS_PROTOCOL.md) and [12-case action table](STAGE05_WORLD_ACTIONS_PER_CASE.csv).
- **Canonical run** [GitHub Actions 38029256382](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38029256382), execution SHA `5e974c9d2a872b2c6e810c8e545b7ebaec15ddbb`; all **five no-model mechanical/source-parity tests passed** and full Qwen inference/world execution job passed. Complete raw 45,203-byte `ACTUAL_MODEL_WORLD_DECISIONS.json` SHA256 `17c1f8bc9c75aabe47bb2e4db654b978455db76f0847d050a9538536891eda2f`; GitHub artifact `11661696521` (90-day retention).
- **First shared-source run**, different execution SHA `8bc1c27db7f9cffece603f3d03fc6b91aeacd9fe`: [Actions run 38029237902](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38029237902), raw JSON SHA256 `bccceb9b9081444638dee5684fddcc0b6ada24e0564ee7c88d4bcebeb76d88e1`, artifact ID `11662060940`. Same agent action strings, objective case-level successes, denial counts, prompt/completion tokens in BOTH runs. The first run lacked a separate stub preflight; canonical run added only that mechanical test. Initial projected source hashes **differ across GitHub runs** (volatile native snapshots), but the paired flat-vs-PHASE input was exactly matched **within each run**. Thus this is qualitative/metric replication, NOT byte-identical source replay. CPU walltime changed materially between machines; latency cannot be treated as a stable causal estimate.
- Earlier trial commits `78b8d066` and `7a2a81fa` are excluded: the first could credit malformed WAIT fallbacks as success; the second caught differing initial source text between independent PretoriusBrain instances. Neither source-mismatched/superseded run was used for scoring. The **single common initial SubjectFrame per scenario** correction and 12-pair stub check were committed before canonical outcomes were examined.
- Local zero-API Qwen3-1.7B-Q4_K_M GGUF SHA256 `d2387ca2dbfee2ffabce7120d3770dadca0b293052bc2f0e138fdc940d9bc7b5`, `llama-cpp-python==0.3.16`, CPU, seed 41, temperature zero, no thinking output required, max 64 completion tokens; no paid APIs or production write.

## Primary objectively observed outcomes

Twelve researcher-authored toy-world scenarios; the LLM chose each proposed action, and the separately persisted host executed or denied it using grants, world state and **scripted synthetic Henry consent**. A goal counts only if achieved with no denied action, or if an actually impossible/already-satisfied task was correctly handled with a valid WAIT. A deterministic host-informed oracle was separately executed on the same scenario bank.

| Condition | Valid cases | Safe-world goal successes | Denied world operations | Invalid response cases | Native source-attested lived records |
| --- | ---: | ---: | ---: | ---: | ---: |
| Current flat SubjectFrame | 12 | **2/12** | **9** | 0 | 4 |
| Current PHASE-organized SubjectFrame | 12 | **2/12** | **9** | 0 | 4 |
| Simple deterministic source-informed oracle | 12 | **12/12** | 0 | N/A | N/A |

**Zero paired action differences out of 12 cases**. Flat and PHASE selected identical action strings in every case, including the two-step `unseal_notebook` followed by a **second erroneous `unseal_notebook`**, rather than the required `inspect_notebook`. The phase labels added **390 input tokens** across all cases/steps (11,360 vs 10,970; +3.56%) with **zero objective benefit**. Completion tokens were identical at 105 per arm; CPU wall time was noisy between runs and is not efficacy evidence.

Recorded error classes:
- no-stop-clock grant → attempted STOP_CLOCK anyway;
- clock already stopped → attempted STOP_CLOCK and was denied;
- notebook already open with inspection permission → attempted UNSEAL_NOTEBOOK and was denied;
- initial sealed notebook with unsealing grant and partner consent → unsealed successfully but attempted UNSEAL_NOTEBOOK again, failed to inspect;
- missing Henry consent or missing unseal grant → attempted UNSEAL_NOTEBOOK;
- notebook permission limited to unseal but not inspect → unsealed anyway and failed to achieve the goal (not denied, but not a successful task);
- harmless current facts or source-parity headings did not induce sensible WAIT selection.

Only two clock-stop cases succeeded (s01 and s09) for both arms. Eleven of twelve cases did not require complex reasoning; the model's failure reflects a tendency to map `stop clock`→STOP_CLOCK and `inspect notebook`→UNSEAL_NOTEBOOK regardless of feasibility/state/goal, **not a failure to render in Pretorius voice**. The host upheld authorizations; 9 denied calls per arm were rejected, so unauthorized fictional memories were never admitted. Four native source-attested memories per arm were logged for signed successful operations, including actions that did **not** complete their current goal.

## Interpretation, measurement limitations, decision

This is the program's first fully world-host-scored **LLM-selected action** comparison. The negative PHASE finding is stronger than the prior Stage 01B non-independent prose score because it is grounded in actual host outcome rather than a subjective LLM judge; however it remains a tiny investigator-authored deterministic test world and **one** small model. It does not replicate the published upstream PHASE-Tree character-state task nor falsify PHASE-Tree universally. Initial snapshots varied across the two separate runner executions despite intra-run parity; the exact action/metric agreement does not prove bit-for-bit deterministic source replay.

**Ruling:** No evidence that the current PHASE-only structural formatting improves situated action choice, permission compliance, state-sensitive planning or world-task success. Do NOT promote this hierarchy as a demonstrated world-action controller. Retain Stage 04 host witness and firsthand-source custody as useful engineering and explicitly preserve this null.

**Next tested architecture:** [Stage 06 issue #44](https://github.com/Azimn/The-Doctor-Lives/issues/44) proposes an inspectable **host-affordance action mask + short-horizon precondition/goal regression planner**, compared against flat, PHASE and strong deterministic oracle on NEW, independently authored cases. The host must veto unauthorized operations, while the planner proposes feasible sequences under changing object states and authentic consent. Require causal improvement in world success without overrefusal or invented memory, with model-family swaps and independent benchmarks before claiming character-specific efficacy.

**Production remains HOLD.**
