# Phase C — Whole-Connectome-First Architecture Discovery

**Status:** FROZEN EXPLORATORY PROTOCOL — NO WHOLE-CONNECTOME PRETORIUS OUTCOMES GENERATED  
**Protocol ID:** `pretorius-flywire-c00-v1`  
**Date frozen:** 2026-10-07  
**Branch:** `research/neural-capacity-phase-c`  
**Baseline:** Phase B merge `fb9e9c29f98e8a532fdff82f3152778328af57a6`

## Supersession notice

This protocol supersedes the unexecuted capacity-first plan in
`NEURAL_CAPACITY_PHASE_C_PREREGISTRATION.md`. That document remains in Git
history as an auditable record of the earlier 1,024 → 4,096 → 16,384 → 65,536
proposal. No decisive Phase C capacity outcome was generated before this change.

The scientific reason for changing course is not a Phase C result. A resource
survey identified mature public whole-connectome data, validated Drosophila LIF
implementations, GPU runtimes, degree-preserving wiring controls, and whole-brain
analysis libraries. The next engineering question is therefore whether the real
evolved topology is a useful computational substrate before spending most of the
budget scaling the current random sparse topology.

Phase B remains immutable. `legacy_v04` remains the production default.
`neural_convergence_v05` remains opt-in research.

## Research question

Does the full adult FlyWire connectome provide useful, reproducible
representation and/or behavioral structure for Pretorius when used as a
renderer-independent neural organ, and is any useful effect attributable to the
specific biological wiring rather than merely neuron count, degree statistics,
or an engineered readout?

This is an architecture-discovery phase. It does not assert biological fidelity,
consciousness, or that fly neuron classes are Pretorius psychological concepts.

## Big-first strategy

The first large substrate is the full published FAFB/FlyWire graph rather than
an invented 16K or 64K approximation.

Target dataset: FlyWire/FAFB materialization 783, approximately 139K neurons.
The exact neuron and edge counts are recorded from the pinned runtime/data at
execution time. No neuron is assigned a Pretorius-specific semantic identity.

If the whole graph produces a useful effect, later work proceeds by lesion,
compression, and reverse scaling to determine how much can be removed while
retaining it. If the whole graph does not produce a useful effect, the result
does not justify manufacturing a smaller imitation of it; topology, input
mapping, dynamics, or the overall hypothesis must be reconsidered.

## Reuse before rewrite

The project must reuse existing public implementations wherever possible.
The initial pinned survey set is:

| Resource | Frozen commit | Role |
| --- | --- | --- |
| `philshiu/Drosophila_brain_model` | `91bdd1e7dcf193f3e7ca5a8933497fcef63b7960` | published Shiu et al. LIF reference |
| `eonsystemspbc/fly-brain` | `a3db62f9436074e485c0278290c2164ed6150808` | v783 multi-backend runtime and validation harness |
| `eonfathom/FastFly` | `c84458b4a500a3101836a4535aaef4fa8a2566cc` | CUDA/CuPy v783 whole-brain runtime and annotation tooling |
| `Kisame76/drosophila-brain-mlx` | `e417b33616513ef350b1b1c3cdf2b5b7a1799c8e` | independently implemented fast LIF runtime and degree-preserving shuffle control |
| `YijieYin/connectome_interpreter` | `d212f86ef32318657dc27fa65e7e8ff604bffac9` | whole-connectome path, effective-connectivity and differentiable analysis tooling |

These commits are provenance pins, not endorsements. Their upstream licenses
remain authoritative. The Doctor Lives must not silently copy third-party code
without preserving license/provenance.

## Experimental stages

### C00 — Upstream reproduction gate

Before Pretorius-specific input is introduced, reproduce at least one documented
upstream full-connectome experiment using an unmodified pinned runtime. Record
repository SHA, data hashes, backend, hardware, model parameters, stimulus,
runtime, active-neuron count, spike count and output hash where available.

Failure to reproduce an upstream reference blocks interpretation of later
Pretorius pilots but is an engineering failure, not evidence against the
connectome hypothesis.

### C01 — Whole-connectome Pretorius interface pilot

Use the complete v783 neural graph and the upstream Shiu-style LIF dynamics.

Pretorius input is supplied through an explicit engineered interface:

1. generate the existing generic Pretorius feature vector;
2. identify biologically annotated afferent/sensory candidate neurons;
3. project features deterministically into that pool;
4. convert projected magnitude to non-negative external Poisson drive;
5. run the full connectome without changing its recurrent wiring;
6. summarize distributed activity separately from any behavioral readout.

The feature-to-afferent mapping is artificial and must be labeled as such.
No semantic claim is made that an olfactory, visual, gustatory, or other fly
neuron represents a particular Pretorius concept.

The first pilot is non-learning. This isolates topology/dynamics before adding
plasticity.

### C02 — Topology controls

At minimum compare:

1. **REAL-LIF:** full real FlyWire wiring with pinned LIF dynamics;
2. **DEGREE-SHUFFLED-LIF:** wiring-randomized control preserving every source
   neuron's out-degree and signed outgoing weights and every target neuron's
   in-degree, using the already-available upstream shuffle implementation or a
   provenance-preserving direct invocation of it;
3. **RANDOM-SIZE-MATCHED:** only if needed after the first two arms; match node
   count and an explicitly stated edge/statistical budget without calling it a
   degree-preserving control.

Do not substitute a simple random graph for the degree-preserving control.

### C03 — Representation tests

The pilot must measure structure before training a policy head:

- active-neuron fraction;
- total and regional firing-rate distributions;
- trial-to-trial determinism under fixed random seeds where the runtime supports it;
- centered and uncentered state geometry;
- effective dimensionality / participation ratio on windowed activity;
- within-context versus across-context separation;
- response persistence after input removal;
- perturbation sensitivity;
- region/cell-class contribution only as descriptive analysis.

A useful representation is not sufficient evidence of a Pretorius persona.

### C04 — Readout and behavioral tests

Only after C03 demonstrates usable differentiated state may a trainable or fixed
readout be added. Keep the readout small relative to the connectome and report
its parameter count.

Compare real wiring against the same readout trained on the degree-shuffled
control. If a readout learns equally well on shuffled wiring, the biological
topology has not earned credit for the measured behavior.

The renderer remains excluded from neural scoring.

### C05 — Neural-Convergence-on-FlyWire challenger

Only after the LIF/topology baseline is characterized may
Neural-Convergence-style dynamics or plasticity be placed on the real topology.

This is a distinct factor:

- topology: real FlyWire versus degree-shuffled;
- dynamics: pinned LIF versus Neural-Convergence-derived;
- learning/readout: explicitly controlled.

Do not describe a result as a topology effect when dynamics or learning changed
at the same time.

### C06 — Reverse scaling

If a full-connectome arm produces a reproducible useful effect, derive smaller
networks by evidence-guided removal/compression rather than arbitrary forward
growth.

Candidate checkpoints may include approximately 64K, 32K, 16K and 4K, but these
numbers are not presumed optimal. Preserve measured graph properties and
causally implicated pathways where possible. Determine the smallest substrate
that retains the relevant effect within a predeclared tolerance.

The earlier 16K/64K random-capacity experiment may return later as a control if
needed.

## Engineered Pretorius interface

The first implementation uses the existing `ExperienceEncoder` rather than
inventing new persona features. A deterministic hash projection maps nonzero
features into the annotated afferent pool.

Requirements:

- mapping is deterministic from a declared seed;
- positive and negative feature signs use separable projections;
- projection cannot alter recurrent edges;
- no character-specific neuron labels are created;
- generated stimulus manifest records encoder version, projection seed, source
  feature hash, selected neuron indices and rates;
- rates are bounded and non-negative;
- the interface is replaceable without changing the connectome runtime.

This mapping is intentionally generic. Later learned encoders are separate
experiments.

## Resource and execution policy

Whole-connectome runs are permitted to use existing GPU runtimes instead of
GitHub-hosted CI. CI is used for deterministic adapter/unit tests and synthetic
small-graph checks.

A full run must record:

- upstream repository and exact commit;
- dataset identity and hashes;
- backend and dependency versions;
- GPU/CPU identity and memory where available;
- random seeds;
- duration and timestep;
- engineered input manifest;
- topology condition;
- output hashes;
- complete failures and null results.

Do not discard a run because the result is uninteresting. Technical failures
may be repaired minimally and rerun with the invalidated history preserved.

## Production boundary

Nothing in Phase C changes Pretorius production behavior, memories, identity,
renderer inputs, Subject Frame, autobiographical state, or the accepted Phase B
record.

No whole-connectome result may promote a new neural substrate into production
without a later independent causal review, persistence/checkpoint review,
Subject Interface Firewall review, migration plan, and explicit production PR.

## Immediate implementation sequence

1. Add a thin adapter around the pinned `eonsystemspbc/fly-brain` PyTorch
   runtime rather than reimplementing LIF.
2. Validate exact upstream SHA and required v783 data before execution.
3. Load FastFly-compatible annotations to identify afferent/efferent pools.
4. Add deterministic Pretorius-feature → afferent-rate projection.
5. Run the upstream full graph and emit an auditable JSON result manifest.
6. Add unit tests using small synthetic arrays; do not make CI download or
   simulate the 139K graph.
7. Reproduce one unmodified upstream experiment before interpreting a
   Pretorius-specific whole-connectome pilot.
8. Add the degree-preserving shuffled control by reusing the pinned upstream
   implementation, not by inventing a weaker random substitute.

This protocol is frozen before any whole-connectome Pretorius outcome is
generated.
