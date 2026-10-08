# C02 Whole-FlyWire Backend Smoke Evidence

**Protocol:** `pretorius-flywire-whole-connectome-c01-v2`  
**Status:** PASS — technical backend gate only  
**Run:** GitHub Actions `37715901213`  
**Artifact:** `flywire-c02-backend-smoke`, artifact ID `11523552921`  
**Artifact ZIP SHA-256:** `0a249a34b674030e724cebc1769f169e29b34cf3bdf59381b8719b817368dd79`  
**Pinned backend:** `eonsystemspbc/fly-brain@a3db62f9436074e485c0278290c2164ed6150808`  
**Execution date:** 2026-10-08 UTC

## Purpose

C02 verifies that The Doctor Lives can reuse an existing whole-brain FlyWire
runtime without rewriting the simulator. It is deliberately non-scientific:
there is no Pretorius context score, no topology comparison, no action-quality
measurement, and no Phase C hypothesis adjudication.

## Exact smoke configuration

- Backend: upstream PyTorch whole-brain runner.
- Device: GitHub-hosted CPU runner.
- FlyWire materialization: upstream v783 dataset at the pinned backend SHA.
- Neurons instantiated: **138,639**.
- Simulation duration: **0.001 s** biological time.
- Integration step: **0.1 ms**.
- Neural timesteps executed: **10**.
- Trials: **1**.
- Spike probing/output: **disabled**.
- Upstream returned benchmark status: **success**.

## Measured engineering timings

- ID mapping: **0.087 s**.
- Weight construction/loading: **9.517 s**.
- Model creation: **0.003 s**.
- Model setup total: **9.519 s**.
- Ten neural timesteps: **0.193 s**.
- Total measured backend elapsed: **9.799 s**.

The reported `Active neurons: 0` and `Total spikes: 0` in this smoke are not
biological or architectural observations. Spike probing/output was explicitly
disabled to keep C02 a resource/integration gate, so the backend intentionally
did not collect those events.

## Integrity observations

The workflow:

1. verified the local FlyWire adapter tests;
2. cloned the existing upstream backend rather than copying its simulator;
3. checked out the exact pinned SHA and asserted HEAD equality;
4. built the upstream sparse FlyWire weights;
5. instantiated all 138,639 neurons;
6. executed ten actual PyTorch recurrent timesteps;
7. required the upstream result object's `status` field to equal `success`;
8. preserved the technical log as a workflow artifact.

Two workflow defects were found and corrected before this accepted run:

- an initial 0.001 s call through upstream `main.py` would have been rejected by
  its CLI duration whitelist without proving execution;
- an embedded Python heredoc was initially malformed YAML.

Both were plumbing defects discovered before C02 acceptance. Neither generated
or exposed a Pretorius scientific outcome.

## C02 conclusion

The full-scale FlyWire path is technically viable enough to proceed to C03
design and execution. This does **not** establish that the fly connectome is a
useful Pretorius substrate, that its topology is superior to controls, or that
138,639 neurons are necessary.

The next scientific step remains C03: freeze the generic afferent input manifest,
run the intact full connectome under the pinned LIF dynamics, preserve response
states, and only then evaluate the preregistered architecture-discovery metrics.
