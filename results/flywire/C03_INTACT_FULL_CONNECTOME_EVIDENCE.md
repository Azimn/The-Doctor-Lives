# C03 Intact Whole-FlyWire Pilot Evidence

**Protocol:** `pretorius-flywire-whole-connectome-c01-v2`  
**Execution freeze:** `FLYWIRE_C03_EXECUTION_FREEZE.md`  
**Frozen execution commit:** `6478cbd723ff830ac9fc904abb062d51962c0e8a`  
**Status:** VALID INTACT-CONDITION RESULT — NO TOPOLOGY CLAIM  
**Workflow run:** `37716649821`  
**Artifact ID:** `11523888794`  
**Artifact digest:** `sha256:b9b3e663535ac7cc1210862e61c788abe6f4d050f648fca3a783c352aa990141`

## Frozen sources

- Whole-brain backend:
  `eonsystemspbc/fly-brain@a3db62f9436074e485c0278290c2164ed6150808`
- FlyWire annotations:
  `flyconnectome/flywire_annotations@a83b2776d60d5764cef36b927f5f9679c16c47a2`
- Materialization: FlyWire/FAFB v783.
- Condition: `INTACT_FLYWIRE_V783`.

## Input pool and manifest

The official annotation table contained **139,248** rows and **19,262**
`flow=afferent` rows/unique IDs. Intersecting them with the pinned backend's
**138,639** neurons left **18,664** candidate afferents.

Candidate-ID list SHA-256:

`87b977849d734cc83959e3870afd89c68c93d6ea65815b19742801e1d8143319`

The frozen 12-probe projection drove a union of **1,130** afferent neurons.

Projection manifest semantic SHA-256:

`7204b9ac2860d94b5ac28edb5976695831b61e366a920da67629ee8c99a13228`

Manifest file SHA-256:

`3a351f538eeca14e9a397f66b5fcf4fb828f3b66954676a6bd76de5b98b6f465`

## Whole graph

- neurons: **138,639**
- directed weighted neuron-pair edges: **15,091,983**
- excitatory edges: **9,059,302**
- inhibitory edges: **6,032,681**
- zero-weight edges: **0**
- topology fingerprint:
  `267c9329a5babe921ac2f60e5d7e48d9f7e0a04b802711544a1c8eb66da3e997`

These are the backend's aggregated neuron-pair edges. They should not be
misreported as the raw count of individual synaptic contacts.

## Frozen run

- 12 probes in 6 preregistered context families;
- 3 trials/probe with seeds 8301, 8302, 8303;
- 50 ms/probe/trial;
- 0.1 ms integration step;
- 500 whole-brain steps/trial;
- 18,000 whole-brain timesteps total;
- 150 Hz maximum afferent drive;
- no synaptic learning;
- full firing-rate response vector retained for every trial.

The model setup took **8.9493 s** on the GitHub-hosted CPU runner. The 36 frozen
whole-brain trials took **392.2319 s**.

## Primary exploratory result

Centered whole-response context separation:

- within-family mean cosine: **-0.2102872109**
- across-family mean cosine: **-0.0567604615**
- within-minus-across separation: **-0.1535267494**
- within-family pairs: **6**
- across-family pairs: **60**

The preregistered direction was not observed. Under this generic afferent
projection, probes assigned to the same semantic family were, on average, less
similar to each other than probes from different families after centering.

Uncentered context separation was also negative:

- within-family mean cosine: **0.2956767426**
- across-family mean cosine: **0.3365028907**
- separation: **-0.0408261481**

Centered effective dimensionality was **2.8819340209**.

## Reliability and activity

Despite the adverse family-separation result, trial responses were not simply
unreproducible noise. Mean within-probe pairwise trial cosine was
**0.7692741086**, with per-probe means ranging from **0.5593020638** to
**0.9457113087**.

Across all mean probe response vectors:

- mean firing rate: **0.5712277293 Hz**
- firing-rate standard deviation: **5.6668119431 Hz**
- maximum observed mean-probe rate: **246.6666718 Hz**
- active-neuron fraction varied substantially by probe, from approximately
  **0.095%** to **4.733%**.

The large activity-range variation is a real feature of this pilot and a
possible confound for semantic-family geometry. It must not be silently
normalized away after seeing C03; any alternative normalization belongs in a
new predeclared sensitivity analysis.

## Preserved result hashes

Response NPZ SHA-256:

`228aad330259aeb1c7232fec408bd0f7a72ba368b111d0877b616e5757a0ec69`

Summary semantic SHA-256:

`5c6f62b82630e4a566390f05a3f576b9ca62cad34d4561fb9269f5c46516fae9`

## Interpretation

C03 does **not** provide evidence that the intact FlyWire graph organizes these
Pretorius text probes by the six semantic families under the frozen generic
projection. It is a valid negative/adverse result and remains part of the
record.

C03 also does **not** establish that FlyWire topology is worse than random or
that the whole-connectome approach has failed. There is no matched topology
control yet. The result can arise from the topology, the generic hashed
afferent interface, the published fly LIF dynamics, the 50 ms observation
window, or interactions among those factors.

The next mandatory step is C04. The exact C03 input manifest, neural dynamics,
trial seeds, durations and metrics must be held fixed while the intact graph is
compared against topology controls.

No production or subject-visible state changes are authorized by this result.
