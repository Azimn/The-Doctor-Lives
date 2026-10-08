# C04 FlyWire Topology-Control Evidence

**Protocol:** `pretorius-flywire-whole-connectome-c01-v2`  
**Execution freeze:** `FLYWIRE_C04_TOPOLOGY_CONTROL_FREEZE.md`  
**Status:** COMPLETE — TOPOLOGY-SPECIFIC EFFECT PRESENT, PRIMARY PRETORIUS-FAMILY DIRECTION ADVERSE  
**Definitive hardened run:** GitHub Actions `37722526360`  
**Definitive commit:** `b4ed8cca72d82a6e51d5551b074f956daa640099`  
**Initial complete replication run:** `37717940797` at `4dd6c829ac651d73e7a3ec780ba510f4be815ffd`

## Purpose

C04 asks whether the C03 intact-connectome result depends on the actual FlyWire
wiring or is typical of graphs with comparable scale/statistics under the exact
same frozen input interface, neural dynamics, run budget and metrics.

C04 does **not** test whether the FlyWire topology is generally useful under a
learned interface or learned graph dynamics. It tests the frozen C03 combination:
generic hashed Pretorius-to-afferent projection plus the pinned Shiu-style LIF
dynamics.

## Frozen common experiment

All seven conditions used:

- backend: `eonsystemspbc/fly-brain@a3db62f9436074e485c0278290c2164ed6150808`;
- materialization: FlyWire/FAFB v783;
- neurons: **138,639**;
- directed weighted neuron-pair edges: **15,091,983**;
- frozen C03 afferent/probe manifest SHA-256:
  `7204b9ac2860d94b5ac28edb5976695831b61e366a920da67629ee8c99a13228`;
- 12 probes in six context families;
- 3 trials per probe with seeds 8301, 8302 and 8303;
- 50 ms per trial at 0.1 ms integration steps;
- 500 whole-brain steps per trial;
- 150 Hz maximum afferent drive;
- no synaptic learning.

The primary metric remained centered within-family minus across-family cosine
separation. No post-result normalization or replacement metric was introduced.

## Conditions

- **INTACT:** exact v783 wiring.
- **DEGREE_PRESERVING:** three topology seeds 9401, 9402, 9403 using the pinned
  `Kisame76/drosophila-brain-mlx@e417b33616513ef350b1b1c3cdf2b5b7a1799c8e`
  `lif.shuffle_pack.shuffle_edges` implementation.
- **RANDOM_SCALE:** three topology seeds 9501, 9502, 9503 using the frozen
  balanced directed scaffold plus the same audited shuffle implementation.

All six control topologies passed the predeclared integrity gates.

### Degree-preserving integrity

All three degree controls retained:

- exact intact per-neuron in-degree;
- exact intact per-neuron out-degree;
- exact per-source positive and negative edge counts;
- exact per-source signed-weight sum;
- exact per-source absolute-weight sum;
- exact per-source squared-weight sum;
- zero parallel directed pairs.

Self loops remained far below the frozen 0.1% invalidity threshold:

- seed 9401: **293** self loops, fraction **0.0000194143**;
- seed 9402: **285** self loops, fraction **0.0000188842**;
- seed 9403: **285** self loops, fraction **0.0000188842**.

### Random-scale integrity

All random-scale controls retained the complete global signed-weight multiset,
exact neuron count and exact edge count, with zero parallel directed pairs.

Self loops:

- seed 9501: **104**, fraction **0.0000068910**;
- seed 9502: **113**, fraction **0.0000074874**;
- seed 9503: **123**, fraction **0.0000081500**.

All are far below the frozen invalidity threshold.

## Primary result

Centered context separation:

| Condition | Seed | Separation |
| --- | ---: | ---: |
| INTACT | — | **-0.1535267494** |
| DEGREE_PRESERVING | 9401 | +0.0522497561 |
| DEGREE_PRESERVING | 9402 | +0.0521333550 |
| DEGREE_PRESERVING | 9403 | +0.0520058123 |
| RANDOM_SCALE | 9501 | +0.0519603538 |
| RANDOM_SCALE | 9502 | +0.0512969920 |
| RANDOM_SCALE | 9503 | +0.0510904972 |

Degree-preserving mean: **+0.0521296411**.  
Degree-preserving median: **+0.0521333550**.  
INTACT greater than degree controls: **0/3**.

Random-scale mean: **+0.0514492810**.  
Random-scale median: **+0.0512969920**.  
INTACT greater than random controls: **0/3**.

INTACT-minus-control differences were approximately **-0.205** for every
control instance.

The topology therefore has a large and highly reproducible effect under this
frozen interface/dynamics combination, but the effect is in the adverse direction
for the preregistered Pretorius semantic-family separation objective.

## Secondary result

Uncentered separation:

- INTACT: **-0.0408261481**;
- degree-preserving: **+0.0334088250, +0.0333269955, +0.0331941603**;
- random-scale: **+0.0333412324, +0.0328071921, +0.0327147018**.

Centered effective dimensionality:

- INTACT: **2.8819340209**;
- degree-preserving: **7.5358336338, 7.5373349145, 7.5430061691**;
- random-scale: **7.5049652348, 7.5208519902, 7.5148411622**.

The intact graph also generated a substantially different activity regime. Its
C03/C04 intact response had mean firing about **0.5712 Hz** and probe-dependent
active-neuron fractions reaching about **4.73%**, whereas the topology controls
were near **0.09–0.10 Hz** mean firing and generally below about **0.2%** active
neurons per probe. This is a descriptive observation and does not by itself
identify the mechanism.

## Exact C03 reproduction

The fresh C04 INTACT rerun produced response NPZ SHA-256:

`228aad330259aeb1c7232fec408bd0f7a72ba368b111d0877b616e5757a0ec69`

This is exactly the response hash preserved for C03. The intact result therefore
reproduced bit-for-bit at the retained response-artifact level.

## Hardened-run replication

An edge-case defect was identified in the C04 control builder after the first
complete run: its per-source invariant reducer used `numpy.add.reduceat` in a
form that can reject a **trailing empty CSR row** because the corresponding
start index equals the edge-array length.

Commit `b4ed8cca72d82a6e51d5551b074f956daa640099` changed only that reduction
helper so empty rows are reduced by operating on non-empty rows and scattering
the results into a zero-initialized vector. It did not alter topology seeds,
shuffle logic, neural dynamics, inputs, metrics, thresholds or any scientific
condition.

The complete seven-condition matrix was then rerun as Actions run
`37722526360`.

For every one of the seven conditions:

- the retained response NPZ SHA-256 is **identical** between the first and
  hardened runs;
- generated control connectivity SHA-256 values are identical;
- topology-validation JSON is exact-identical for all generated controls;
- differences in recomputed summary floats are limited to final machine
  precision digits.

The technical repair therefore had no effect on the executed scientific
conditions or their neural responses.

## Definitive hardened artifacts

| Artifact | ID | ZIP SHA-256 |
| --- | ---: | --- |
| `flywire-c04-intact` | 11526462460 | `67e370e8e8f43f606374a05646fa346c965357567dd5122011feae67a5292943` |
| `flywire-c04-degree-9401` | 11526815699 | `0a6b8314fe20ecd65f4067064606010daaec74f685c30f068d754d586489b395` |
| `flywire-c04-degree-9402` | 11526691297 | `aacbd20d4fab84441384b280a3826af425b6c47a8841eb30ea61ac487f238fbd` |
| `flywire-c04-degree-9403` | 11526786007 | `fa46da168d3367d77269cef642efe2cb559f760bcf199494dc48a8fd2b83f6eb` |
| `flywire-c04-random-9501` | 11526409524 | `677255d5a0cf9b6748afd58e45352bf836ef1c9c2ea848d92cc75c088a898a86` |
| `flywire-c04-random-9502` | 11526695901 | `acae25f2379107af2ef1ad6d330ea41abb633f07331e9e44c9bd993661737009` |
| `flywire-c04-random-9503` | 11526503512 | `f38b9be34ad4faf9f63de973b6544848611abda0ddedc1420cb7a262a791269e` |
| `flywire-c04-comparison` | 11526796141 | `b3ed91e2722b827b5ad91bb95ad632f9552e4ca5bf8c21fa5e068fe6d793cded` |

The initial full run `37717940797` is retained as independent same-protocol
replication evidence rather than discarded.

## Repository regression status

At definitive C04 head `b4ed8cca72d82a6e51d5551b074f956daa640099`:

- `brain-tests` PR run `37722529964`: **315 tests PASS**;
- `gate1-fresh-install-validation` run `37722529969`: **PASS**;
- `causal-audit-repeatability-v05` run `37722530002`: **PASS**;
- C04 topology-control run `37722526360`: all seven condition jobs plus
  comparison: **PASS**.

## Interpretation and next gate

C04 establishes a topology-specific dynamical difference under the frozen C03
interface. It does **not** establish that the evolved topology is generally
harmful or generally beneficial.

The intact graph strongly differs from both degree-preserving and random-scale
controls, but with the generic hash-to-selected-afferent interface and fixed
Shiu LIF dynamics it compresses the tested Pretorius semantic families rather
than separating them.

The frozen C04 decision rule therefore applies:

> **Do not begin reverse scaling yet.**

The next major experiment should isolate the more plausible bottlenecks:

1. the engineered Pretorius-to-afferent interface;
2. fixed LIF dynamics versus learned connectome-conditioned dynamics;
3. observation/readout timescale;
4. interactions among those factors.

A particularly relevant next challenger is a FlyGM-like learned
connectome-structured model: low-dimensional learned encoding broadcast through
the afferent population, fixed real FlyWire message passing, shared trainable
neuron-state update conditioned on per-neuron descriptors, and an efferent
readout. This must be preregistered as a new experiment before outcomes are
generated.

No C04 result changes production Pretorius.
