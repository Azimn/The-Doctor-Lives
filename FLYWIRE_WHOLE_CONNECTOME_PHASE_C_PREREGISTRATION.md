# C01 v2 — Whole-Connectome-First Pretorius Neural Study

**Status:** FROZEN PREREGISTRATION — NO C02+ SCIENTIFIC OUTCOMES GENERATED  
**Protocol ID:** `pretorius-flywire-whole-connectome-c01-v2`  
**Date frozen:** 2026-10-07  
**Branch:** `research/neural-capacity-phase-c`  
**Production baseline:** `fb9e9c29f98e8a532fdff82f3152778328af57a6`

## Supersession

This protocol supersedes `pretorius-capacity-mechanism-c01-v1` before any
Phase C capacity, calibration, mediation, or whole-connectome result was run.
The earlier preregistration remains preserved as a null experimental plan. No
result caused this change.

The change follows an outcome-blind resource review showing that complete
FlyWire/FAFB simulation infrastructure already exists. Reusing those systems
allows Phase C to test an evolved ~139K-neuron topology directly before
constructing additional artificial 16K/64K networks.

## Research question

The primary exploratory question is:

> Does the intact adult Drosophila FlyWire topology provide useful,
> reproducible context-sensitive neural state differentiation under a generic,
> nonsemantic Pretorius input projection, beyond topology controls with matched
> scale and degree statistics?

Secondary questions are whether the effect depends on the published LIF
dynamics, whether Neural-Convergence-style dynamics can later exploit the same
topology, and how far a useful full graph can be reduced before the effect is
lost.

This is **not** a claim of biological identity, consciousness, human cognition,
or fly-brain equivalence to Pretorius.

## Reuse-first requirement

Phase C must adapt existing public infrastructure before writing a new
whole-brain simulator. The initial pinned references are:

- Shiu reference model:
  `philshiu/Drosophila_brain_model@91bdd1e7dcf193f3e7ca5a8933497fcef63b7960`
- Multi-backend Shiu implementation:
  `eonsystemspbc/fly-brain@a3db62f9436074e485c0278290c2164ed6150808`
- FastFly CUDA/CuPy implementation:
  `eonfathom/FastFly@c84458b4a500a3101836a4535aaef4fa8a2566cc`
- Connectome Interpreter:
  `YijieYin/connectome_interpreter@d212f86ef32318657dc27fa65e7e8ff604bffac9`
- Dataset: FlyWire/FAFB materialization v783.

The Shiu model defines the initial neural-dynamics reference. Accelerated
backends may replace it only after parity/fidelity checks. Upstream code is not
copied into The Doctor Lives unless a later engineering need requires vendoring;
the preferred interface is a thin adapter around a pinned checkout.

## C02 — backend fidelity gate

C02 is technical only. It must:

1. check out the pinned multi-backend repository;
2. verify the exact upstream SHA;
3. run its PyTorch whole-brain path for a very short non-scientific smoke
   simulation;
4. record completion, runtime, memory if available, package versions and exact
   upstream SHA;
5. perform **no Pretorius context scoring, topology comparison, action scoring,
   or architecture selection**.

Failure is an engineering result. Repair may change plumbing but not C03's
scientific definitions.

## C03 — intact whole-connectome exploratory pilot

C03 uses the complete v783 graph supported by the selected faithful backend.
The graph is not reduced to 64K or 16K first.

### Input boundary

Pretorius inputs are projected only through a generic afferent interface.

- Start from the existing deterministic 512-dimensional hashed text encoder.
- Obtain the candidate neuron pool from FlyWire metadata classified as
  afferent/input-flow neurons.
- Map encoder feature index + sign to candidate afferents through a frozen
  BLAKE2-based deterministic projection.
- Shared encoder features therefore recruit overlapping afferent populations.
- No neuron is assigned a semantic meaning such as curiosity, memory,
  arrogance, identity, autonomy or relationship.
- Cell-type names are not used to hand-route Pretorius concepts.
- Projection fan-out is fixed before C03 execution and stored in the manifest.

The adapter must write the complete feature-to-afferent manifest and its SHA-256
before the first neural run.

### Initial neural dynamics

The first whole-connectome pilot uses the published Shiu-style LIF dynamics as
implemented by the pinned backend. No synaptic learning is introduced in C03.
This deliberately tests topology/state propagation before adding Pretorius
plasticity.

### Probe set

C03 uses twelve frozen probes: two probes from each of six context families
already represented in the Phase B curriculum:

- novelty / exploration / creation;
- authority / autonomy / coercion;
- social approach / cooperation / distrust;
- threat / avoidance / control;
- persistence / competence / outcomes;
- fatigue / affiliation / continuity.

The texts are frozen in the committed probe-manifest builder before execution.
Each probe receives the same simulation duration, stimulation-rate policy and
number of independent trials. Probe order is deterministic.

### C03 measurements

The primary exploratory measurement is centered neural-state context
separation, computed from whole-brain response vectors:

`mean(within-family cosine) - mean(across-family cosine)`

after per-neuron centering across the probe matrix and row normalization.
Record within/across pair counts and raw values.

Also report:

- uncentered context separation;
- effective dimensionality / participation ratio;
- active-neuron fraction;
- mean and variance of firing rate;
- per-probe reproducibility across trials;
- response-vector norm;
- runtime and memory;
- whole-state and manifest hashes.

These are architecture-discovery measures, not persona-quality scores.

## C04 — topology controls

No intact-connectome result is interpretable as a topology effect without
controls.

At the same neuron count, probe set, input projection, neural dynamics and run
budget, C04 must compare:

1. **INTACT:** exact v783 connectivity.
2. **DEGREE-PRESERVING:** an audited directed rewiring that preserves each
   neuron's in-degree and out-degree and the global signed-weight distribution.
3. **RANDOM-SCALE:** random graph control matched on neuron count and total edge
   count, with the signed-weight distribution preserved globally.

The adapter currently includes an endpoint-shuffle utility suitable only for
engineering smoke tests. Because it may introduce self-loops or parallel edges,
it is **not** automatically the decisive C04 degree-preserving control. C04
requires an audited generator and explicit validation report before outcomes.

The same feature-to-afferent manifest is used across topology conditions by
neuron identifier where meaningful. If rewiring changes index semantics, the
frozen mapping must be transferred without resampling the stimulated set.

## Reference conditions

Phase B's accepted 4,096-unit Neural Convergence evidence is historical context,
not a matched C03/C04 control because the dynamics and timescale differ.

A large random Pretorius/Neural-Convergence network may be added later, but it
must be declared before its results are compared against intact FlyWire.
The initial whole-brain experiment is intentionally topology-first.

## Decision after the full graph

The full graph is not presumed to be the final Pretorius substrate.

If intact topology does not exceed controls reproducibly, do not infer that a
smaller fly-derived graph would necessarily fail, but do not spend the main
budget blindly scaling replicas. Revisit input interface, dynamics and topology
hypotheses separately.

If intact topology shows a reproducible topology-specific effect, the next
program is **reverse scaling**:

`~139K intact -> lesion functional/anatomical classes -> ~64K -> ~32K -> ~16K -> smallest retained effect`

Reduction must be guided by predeclared lesion/compression rules, not by
hand-selecting the best-looking subgraph after each result.

A 64K or 16K derivative earns attention because it preserves a demonstrated
property of the full system, not because those sizes were chosen in advance.

## Plasticity boundary

Neural Convergence mechanisms are not inserted into the whole fly brain during
C03. If intact-topology dynamics justify further work, a later versioned
protocol may test:

- fixed FlyWire topology + Pretorius rate dynamics;
- fixed FlyWire topology + Neural Convergence plasticity;
- plasticity restricted to predeclared edge/classes;
- motor/readout learning versus recurrent learning.

The published LIF result remains the topology reference condition.

## Integrity and evidence rules

Every C02+ result must record:

- repository SHA and protocol ID;
- upstream repository and SHA;
- FlyWire materialization/version;
- topology fingerprint;
- input-manifest SHA;
- probe-manifest SHA;
- software versions and device;
- all run parameters;
- random seeds;
- raw or auditably sufficient response state;
- result SHA-256.

Technical failures, null effects and adverse results remain first-class
evidence. No seed, probe, topology control or metric may be replaced because its
result is unfavorable.

## Production boundary

Phase C does not change production defaults, subject memory, autobiographical
state, renderer input, Subject Interface Firewall behavior, or accepted Phase B
evidence. Whole-connectome state is engineer-only experimental telemetry.

Any later production use requires a separate causal review, migration plan,
resource assessment, checkpoint contract, Subject Interface review and release
gate.
