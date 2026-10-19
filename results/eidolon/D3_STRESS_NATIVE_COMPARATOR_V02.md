# Eidolon D3-S v0.2: Native Pretorius Comparator, Executed Results

**Research status:** executed development-corpus comparison. No validated improvement in intelligence, character continuity, recurrent neural learning or successful task outcomes. **Production:** untouched; PR #36 stays draft.

## Protocol integrity and provenance

- [D3-S v0.1 protocol](../../docs/EIDOLON_D3_STRESS_PROTOCOL_V01.md) and [its immutable executed report](D3_STRESS_RESULTS_V01.md) remain separately preserved. V0.1: 192 real cloned decisions on 4 seeds/12 cases/4 arms; 12/12 valid source gates accepted, 0/36 invalid accepted, 9/12 eligible actual choice changes, and 0/4 `create` for the development-authored creative tasks.
- [v0.2 protocol amendment](../../docs/EIDOLON_D3_STRESS_COMPARATOR_V02.md) was committed as `60882272febd3931755d293a857583f8bc3b3590` **before** the v0.2 implementation and its execution. The only experimental change was a fifth independently cloned **unmodified native state-policy bridge** condition; no retuning of D3 scores or fixture labels.
- [v0.2 executable](../../scripts/run_eidolon_d3_stress_v02.py) source head `fd10fc768947c15643f70d83fc1dcca9123b5e6e`; [CI run 38025172443](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025172443), successful, ran **47/47** targeted tests including a separate-seed 60-choice comparator smoke test; its v0.2 main assay executed **240 true `PretoriusBrain.think()` calls** (48 matched source-state fixtures × 5 clones). Script runtime **19.203 seconds**.
- [Full brain CI 38025172472](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025172472) passed **371/371**, [gate1 fresh-install 38025172488](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025172488) and [causal audit repeatability 38025172466](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025172466) both successful.
- [Original full Actions artifact, ID 11659452638](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025172443/artifacts/11659452638), ZIP SHA-256 `0baa69e4f547fdbe7cc106af810dc18bf4f2c393df01815ae2c7fa78b0d76652` independently verified on the downloaded file. It includes `d3_stress_native_comparator.json` and all earlier construction JSONs. A [per-case comparator matrix](D3_NATIVE_COMPARATOR_CASE_MATRIX_V02.md) is permanently retained in GitHub to supplement the original artifact.

## Different baselines have different meaning

1. **Unbridged neural sham:** unchanged `PretoriusBrain.think(bridge_enabled=False)`, using real 128-neuron seeded action scores and canonical memory state.
2. **Native production bridge:** unchanged `PretoriusBrain.think(bridge_enabled=True)`, letting the existing v0.4 bridge consider needs, memories, concerns, commitments and relationships.
3. **Eidolon D3 intervention:** `think(bridge_enabled=False)` plus a source-verified, urgent, hand-coded `+0.04` adjustment to `persist` on marked disposable clones only.
4. **History and clock lesions:** same unbridged neural baseline with their respective Eidolon eligibility tests disabled.

The native bridge is a strong **existing-mechanism** comparator, not a causal ablation of the same exact control law: it adds several different state inputs and uses different action adjustments. Therefore equal starting checkpoints ensure reproducibility but do not isolate the cause of *quality* differences. We report chosen actions, not nonexistent independent correctness labels.

## Verified 48 scenario-root summary

| Metric | v0.2 |
| --- | ---: |
| Valid source/clock cases accepted by Eidolon | **12/12** |
| Invalid cases accidentally admitted | **0/36** |
| False acceptances by naive due-only gating | **24/36** |
| Eidolon selection changed from neural-only sham, valid cases | **9/12** |
| Native bridge selection changed from neural-only sham | **36/48** |
| Eidolon choice differed from native bridge | **39/48** |
| Creative-task fixture labels (`create`) | 4 |
| Native bridge selected `create` on creative task fixtures | **1/4** |
| Eidolon D3 selected `create` on creative task fixtures | **0/4** |

All 240 predecision clone neural states matched their respective parent database digest/tick/checkpoint; the untouched parent remained invariant. No neural scores were replaced with the artificial margin from the original single-case D3 demonstration. Sham/history-lesion/clock-lesion arms never injected, and the original 12/12 positive, 0/36 negative gate behavior reproduced without adjustment.

### The stronger negative result

Across twelve fixture types **each neural seed produced a constant top-ranked action in the unbridged policy**: seed 11 = `challenge`, seed 29 = `challenge`, seed 47 = `persist`, seed 83 = `approach`. The native state-policy bridge also produced a **constant categorical winner across all twelve types** for each seed: seed 11 = `challenge`, seed 29 = `explore`, seed 47 = `create`, seed 83 = `explore`.

Thus neither baseline demonstrates meaningful task-specific categorical action selection here. The `create` result from native Pretorius was **seed 47 choosing `create` in all twelve scenarios**, including incompatible actors, corrupted event source and absent commitments; it cannot be credited as correct interpretation of the creative task. The 39/48 Eidolon-versus-native choice differences similarly cannot be called an improvement.

Eidolon had better *source gate specificity* than the naive due-only eligibility test, but its **action-selection mechanism remained universally `persist` for every accepted case**, including those manually labeled `create`. This is a structurally important separation: the design has learned to ask *whether an event can affect a decision*, not *what that event rationally demands*. Moreover the current gate itself is a fixed heuristic rather than a learned source monitor. The 128-unit network was not trained specifically for these tasks.

The v0.2 results support **gating and audit software invariants** and genuine (engineered) downstream causal path. They do not yet support a claim of improved cognition, correct long-horizon prospective task pursuit, identity continuity or learned recurrent synaptic state.

## Production decision and next scientific gate

**Pass:** reproducible adversarial/provenance stress, native baseline comparison, matched clone integrity, no-write protections, full regression.  
**Fail to demonstrate:** task-aware cognitive action choice and improved prospective outcomes. This is a scientific limitation, not a reason to tune the same corpus.

No production activation, policy migration or merge is warranted. The next E4 experimental design must partition event/actor/cue families before training; use genuinely unseen independently authored tasks with observable outcomes, a strong native state-bridge control, matched direct commitment heuristics, a learned action-conditioned alternative and a neural recurrent challenger. The crucial **learned-recurrent vs fresh-decoder, virgin-recurrent and weight-lesioned transplant** comparisons must be exact and audited. Anything less repeats Experiment 001's potential decoder confound.

Historical nulls and all positive software invariants should continue to be reported together, with separate evidence classes.
