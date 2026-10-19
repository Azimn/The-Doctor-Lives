# C03 Intact Whole-FlyWire Execution Freeze

**Protocol:** `pretorius-flywire-whole-connectome-c01-v2`  
**Status:** FROZEN BEFORE C03 OUTCOME  
**Production baseline:** `fb9e9c29f98e8a532fdff82f3152778328af57a6`  
**C02 accepted evidence:** `results/flywire/C02_BACKEND_SMOKE_EVIDENCE.md`

## Sources

C03 uses existing infrastructure and published FlyWire data rather than a new
simulator.

- Whole-brain backend:
  `eonsystemspbc/fly-brain@a3db62f9436074e485c0278290c2164ed6150808`
- FlyWire annotations:
  `flyconnectome/flywire_annotations@a83b2776d60d5764cef36b927f5f9679c16c47a2`
- Annotation table:
  `supplemental_files/Supplemental_file1_neuron_annotations.tsv`
- Connectome materialization: FlyWire/FAFB v783.
- Neural dynamics: the pinned backend's Shiu-style LIF PyTorch implementation.

The complete backend graph is used. No 16K/64K subgraph is selected first.

## Frozen afferent input pool

The candidate sensory/input pool is constructed mechanically:

1. read the official v783 annotation table;
2. select rows whose `flow` value, stripped and lowercased, is exactly
   `afferent`;
3. take their numeric `root_id`;
4. intersect those IDs with the exact neuron IDs in the pinned backend
   `2025_Completeness_783.csv`;
5. remove no additional cell type, anatomical class, modality or side;
6. sort numerically and hash the resulting complete candidate-ID list.

This uses a biological input-flow annotation only. Pretorius concepts are not
mapped to named fly cell types.

## Frozen Pretorius projection

The existing deterministic 512-dimensional signed-hash text encoder is used
with no scalar features and no action teaching signal.

For each nonzero encoder feature:

- feature index and sign are hashed with BLAKE2;
- **8** candidate afferents are selected deterministically;
- projection seed is **7301**;
- collisions accumulate drive;
- the resulting per-probe drive vector is normalized so its maximum is 1.0.

The exact 12-probe feature-to-afferent manifest is written and SHA-256 hashed
before the neural runner starts.

No semantic labels such as identity, curiosity, autonomy, memory, relationship,
threat or persistence are used when choosing biological neurons.

## Frozen probes

Twelve probes are used, two in each family:

1. novelty / exploration / creation;
2. authority / autonomy / coercion;
3. social approach / cooperation / distrust;
4. threat / avoidance / control;
5. persistence / competence / outcomes;
6. fatigue / affiliation / continuity.

The literal texts are those committed in
`scripts/build_flywire_probe_manifest.py` before C03 execution.

## Frozen neural execution

For every probe:

- whole graph: all **138,639** neurons expected from the C02 pinned backend;
- maximum Poisson input rate: **150 Hz** times frozen relative afferent drive;
- biological simulation duration: **50 ms**;
- integration step: upstream fixed **0.1 ms**;
- **500 neural timesteps** per probe/trial;
- no synaptic learning or parameter optimization;
- independent stochastic trial seeds: **8301, 8302, 8303**;
- each probe/trial starts from a fresh `state_init()` state;
- recurrent weights and the afferent mapping are identical across trials;
- spike output is accumulated in memory, not exported as a full event raster.

There are 12 × 3 = **36** probe-trials and **18,000** whole-brain neural
timesteps.

## Frozen neural response representation

For each probe/trial, the response vector is the length-N vector:

`spike_count_per_neuron / 0.05 seconds`

in Hz over the complete stimulus window.

The primary probe state is the elementwise mean of the three trial response
vectors. Trial vectors remain in the artifact for reproducibility analysis.

No trained decoder and no Pretorius action score participates in C03.

## Frozen measurements

Primary exploratory measurement:

- centered whole-response context separation:
  mean within-family cosine minus mean across-family cosine after subtracting the
  per-neuron mean across the 12 mean probe states and row-normalizing.

Also report:

- uncentered within-minus-across cosine;
- centered participation-ratio effective dimensionality;
- active-neuron fraction per probe;
- mean, standard deviation and maximum firing rate;
- within-probe trial cosine reproducibility;
- response norms;
- topology fingerprint and edge/sign counts;
- candidate-afferent count and manifest hashes;
- wall runtime and device.

All 12 probe states are reported. No favorable subset may replace the frozen
set.

## Interpretation boundary

C03 is an **intact-topology exploratory result**. Even a strong context-separation
signal does not establish that biological FlyWire topology caused it.

A topology claim requires C04 with the same probe/input protocol and audited:

1. intact v783 topology;
2. degree-preserving directed rewiring;
3. random-scale topology control.

C03 cannot promote a production neural profile or alter subject-visible state.
