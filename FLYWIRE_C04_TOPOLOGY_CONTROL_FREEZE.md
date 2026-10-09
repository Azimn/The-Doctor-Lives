# C04 FlyWire Topology-Control Execution Freeze

**Protocol:** `pretorius-flywire-whole-connectome-c01-v2`  
**Status:** FROZEN BEFORE C04 OUTCOMES  
**C03 evidence:** `results/flywire/C03_INTACT_FULL_CONNECTOME_EVIDENCE.md`

## Purpose

C03 showed reproducible whole-brain responses but negative preregistered
semantic-family separation. C04 asks whether that result depends on the actual
FlyWire wiring or is typical of graphs with comparable scale/statistics under
the exact same Pretorius input interface.

C04 does not retune C03.

## Frozen simulator and data

- FlyWire backend:
  `eonsystemspbc/fly-brain@a3db62f9436074e485c0278290c2164ed6150808`
- FlyWire annotations:
  `flyconnectome/flywire_annotations@a83b2776d60d5764cef36b927f5f9679c16c47a2`
- Degree-preserving shuffle implementation:
  `Kisame76/drosophila-brain-mlx@e417b33616513ef350b1b1c3cdf2b5b7a1799c8e`
  function `lif.shuffle_pack.shuffle_edges`.
- Dataset/materialization: FlyWire/FAFB v783.

The external shuffle implementation was selected before C04 results because it
already has a dedicated test suite and has been used as a Drosophila
connectome-wiring control.

## Frozen common neural protocol

Every condition uses the exact C03 protocol:

- all 138,639 backend neurons;
- exact C03 official afferent-pool derivation;
- exact C03 probe text and BLAKE2 projection;
- projection fanout 8, projection seed 7301;
- expected semantic manifest hash
  `7204b9ac2860d94b5ac28edb5976695831b61e366a920da67629ee8c99a13228`;
- maximum afferent drive 150 Hz;
- 50 ms/probe/trial;
- 0.1 ms integration step;
- trial seeds 8301, 8302, 8303;
- no learning;
- same response-vector and geometry calculations.

No condition receives a different input mapping or stimulation budget.

## Conditions

### INTact

One fresh rerun of exact v783 wiring. It must reproduce the C03 direction and
serves as a same-workflow replication.

### DEGREE_PRESERVING

Three independently shuffled topologies, seeds:

`9401, 9402, 9403`

For each seed, the pinned `shuffle_edges` implementation:

- preserves every source neuron's out-degree;
- preserves every target neuron's in-degree;
- preserves each source row's signed connection-count multiset;
- therefore preserves each source neuron's output sign/weight budget;
- changes edge destinations;
- repairs parallel edges until each row has unique destinations;
- sorts destinations within each CSR row.

The reused implementation can introduce self-loops. This limitation is known
before outcomes. Self-loop count is reported and the control is technically
invalid only if self-loops exceed **0.1% of all edges**. An invalid seed is not
silently replaced; C04 stops and records the technical failure.

### RANDOM_SCALE

Three independently randomized topologies, seeds:

`9501, 9502, 9503`

This control deliberately removes the fly's heterogeneous degree structure as
well as its wiring.

A deterministic balanced directed scaffold is first created with:

- the exact same neuron count;
- the exact same edge count;
- out-degrees differing by at most one;
- near-balanced in-degree;
- no initial parallel edges.

The complete FlyWire signed-weight vector is globally permuted using
`seed + 10000`, so the global signed-weight multiset is exactly retained but
biological source-neuron sign identity is not retained.

The pinned `shuffle_edges` algorithm then randomizes destinations while
preserving that scaffold's exact in/out degrees and repairing parallel edges.
The same 0.1% self-loop validity bound applies.

This is a random-scale control, not a claim to be a biologically realistic
network or an exact Erdős–Rényi draw.

## Topology integrity gates

Before neural execution every generated control must emit and pass:

- exact neuron count equality;
- exact edge count equality;
- zero parallel directed pairs;
- degree-preserving condition: exact in-degree and out-degree equality to intact;
- degree-preserving condition: exact per-source positive/negative edge counts,
  signed-weight sum, absolute-weight sum and squared-weight sum;
- random-scale condition: global signed-weight multiset SHA-256 equality to
  intact;
- self-loop fraction <= 0.001;
- deterministic topology fingerprint;
- output Parquet SHA-256.

Any integrity failure invalidates the control before neural metrics are read.

## Frozen C04 reporting

For every topology instance record the same C03 metrics.

Primary topology comparison:

`centered_context_separation`

Report:

- intact value;
- the three degree-preserving values and their mean/median;
- the three random-scale values and their mean/median;
- intact-minus-each-control differences;
- count of control seeds for which intact is greater (0-3) in each family.

Secondary comparisons:

- uncentered separation;
- effective dimensionality;
- trial reproducibility;
- activity statistics.

C04 is exploratory. With only three topology instances per control family, it
does not authorize inferential claims of biological optimality.

## Interpretation

If intact is consistently greater than both control families, retain
topology-specific organization as a live hypothesis.

If intact is indistinguishable from or worse than controls, do not spend the
next major resource block merely shrinking the intact connectome. The more
likely next target becomes the input interface, neural dynamics, observation
window, or the mismatch between semantic probe families and the biological
computation being driven.

No C04 result changes production Pretorius.
