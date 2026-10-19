# Eidolon D3: Disposable-Clone Policy Selection, Executed Construction Report

**Date:** 2026-10-09 America/Chicago / 2026-10-10 UTC. **Status:** executed source-bound test of the policy-selection integration *plumbing*. **Production:** unchanged, draft PR #36 only. [Precommitted protocol](../../docs/EIDOLON_D3_CLONED_POLICY_PROTOCOL.md) was created at commit `b99b45186f00f3b78672ed9b077c7fd50cb0f528` before this implementation.

## Methods and authority boundary

The runner [scripts/run_eidolon_d3.py](../../scripts/run_eidolon_d3.py) created a new isolated 128-unit Pretorius with one witnessed Henry apparatus event and one due commitment. It then made four **file-identical disposable clones**, verifying the initial authoritative database digest, recurrent tick and checkpoint SHA before each test. Every clone received an equal, deliberately **synthetic** ten-action neural policy: `challenge=0.120`, `persist=0.110`, each of the other eight actions `0.09625`. That is a forced, nearly tied decoder control, not a phenotype learned by Pretorius.

The [research-only `run_disposable_policy_probe`](../../doctor_lives/eidolon_choice.py) checks for an explicit disposable-clone marker. It reads the already verified D2 autobiographical and temporal signal and, only when a lived-evidence witness, urgent active commitment and priority threshold all pass, injects **+0.04** mass into the `persist` action of that **clone's** real `PretoriusBrain.think()` policy-selection path and renormalizes. This injection is a hand-designed algorithm, not recurrent synaptic plasticity. The monkeypatch is always restored; the original parent is not called by the intervention.

## Results

| Arm | Source memory permitted | Temporal signal permitted | Real selected cognitive policy | Applied research delta |
| --- | --- | --- | --- | --- |
| A: unchanged sham | yes | yes | **challenge** | no |
| B: intact source + time | yes | yes | **persist** | yes, +0.04 before renormalization |
| C: history lesion | no | yes | **challenge** | no |
| D: clock lesion | yes | no | **challenge** | no |

The untouched base was `challenge=0.120`, `persist=0.110`. Under the accepted research intervention, normalized final probabilities became `challenge=0.115384615`, `persist=0.144230769`. All four clones executed `brain.think()`, persisted one cognitive thought record, and selected four memories according to their existing policy mechanism. Their starting states matched the parent exactly. The parent canonical database digest, recurrent neural tick and neural checkpoint SHA remained unchanged.

The comparison establishes **a real downstream effect on a disposable clone's policy-tendency selection**, not just an isolated shadow probability. It is not evidence that the resulting choice is better, autonomous, semantically correct or caused by the learning of neural synapses. The experimenter intentionally arranged a narrow action-score margin and intervention strong enough to flip it. No external tool action, genuine prospective outcome, independent blinded problem or model swap was involved. The selected memory count was four in all arms; this does **not** establish more contextually appropriate memory selection.

## CI and audit artifacts

[Isolated Eidolon run 38024363702](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024363702) passed **36/36 targeted tests**, encompassing E2, D2 and D3. The [full brain suite 38024363692](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024363692) passed **360/360 tests**. [Gate1 fresh install 38024363707](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024363707) and [causal audit repeatability 38024363717](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024363717) also passed on tested implementation commit `064e145a35925db196a1cd00bf270ef1f571ca03`.

The original [four-assay artifact 11659136914](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024363702/artifacts/11659136914) has ZIP SHA-256 `c13495e08a61aa4c2df69225a5b2a99b9ab67c6800689e2d17be3ec465a72ff5`. The original file was `d3_matched_clone_assay.json`; a permanent [D3 case transcription](D3_MATCHED_CLONE_POLICY_V01.json) resides in the branch alongside prior E2 and D2 records. GitHub Actions created a PR merge-ref commit `cf0e498abefb23d1bf792ad692ca757f907f8c9c`; that is not the same as the tested source branch SHA. No controlled original source data were discarded.

## Research decision and gate

**D3 policy-plumbing construction: PASS.** The source+time adapter has a controlled, inspectable causal path into `PretoriusBrain.think()` in deliberately marked test clones; the original parent stays untouched.

**Learned recurrent cognitive architecture improvement: NOT ESTABLISHED.** No trained recurring synapse was necessary for this policy flip, since the source evidence, deterministic rule and controlled synthetic base distribution fully explain the result. A claimed success in identity continuity, planning or character cognition would be unjustified.

**Production migration: BLOCKED.** The complete Eidolon architecture remains a proposal with bounded donor fragments. Before D4/E4 neural evidence, require a novel, independent, actor- and episode-disjoint real decision task, matched access to autobiographical and relational evidence, a strong literal commitment/due-sort baseline, a trained recurrent challenger, fresh decoder control, neural/decoder swap and lesion suites, false-cue probes and correctly supported outcomes. Keep the historical v0.1 recurrence-lesion failure, E2 engineered-state gain and D2 deterministic temporal advantage visible as distinct findings.
