# Phase B Independent Review

Status: **ACCEPT WITH MINOR CORRECTIONS**

Reviewed Phase B head: `9c04e744622a3d2cb4efbaa0a77bd0f795e6cb45`

## Verdict

The completed Phase B experimental record is accepted. No B04, B05, B06, or B07 experiment requires rerun. The B08 production disposition remains unchanged:

**RETAIN OPTIONAL - CAPACITY ADEQUACY UNRESOLVED; SCALING STUDY REQUIRED BEFORE REJECTION**

The review found the B02 preregistration genuine and unchanged through the final B08 head, the B03 characterization machinery unchanged across the decisive B04/B05 executions, all 24 decisive B04-B07 seed artifacts consistent with their recorded digests and result hashes, and the headline B05 aggregates independently reproducible from machine-readable artifacts.

The review also accepted the B06 principal causal conclusion and the repaired definitive B07 record. The first B07 clipping attempt remains excluded as an invalid manipulation arm because it changed zero edges; the repaired p99/p95 experiment was a bounded harness correction rather than favorable-result tuning.

## Required minor corrections

### 1. Gain-bound interpretation

The observed `state_gain = 1.20` on all six challenger seeds is preserved as a preregistered gain-bound warning, not evidence that 4,096 units are inadequate.

The implementation increases state gain whenever measured saturation is below the target of `0.18`, independent of whether learning is enabled. Because the measured saturation is `0.0`, the current homeostat is mechanically driven toward the upper bound even during neutral `learn=False` stabilization. Insufficient representational headroom and a homeostatic/excitability calibration mismatch are therefore both compatible explanations.

### 2. Raw-cosine offset sensitivity

The preregistered context-separation cosine is preserved unchanged, but the permanent interpretation now states that it is computed on uncentered firing-rate vectors and is sensitive to their common firing-rate component.

As a post hoc falsification check, feature-centering the preserved B05 evaluation matrices before recomputing cosine geometry yields within-minus-across context separation of approximately `0.0509-0.0590` across the six challenger seeds. This non-preregistered result does not replace the frozen endpoint.

The representational-crowding warning remains procedurally supportable because the challenger also has only approximately 12-15 effective covariance dimensions in a 4,096-unit state space and only modest absolute behavioral differentiation.

### 3. Causal scope

Phase B establishes that the **final learned recurrent-weight delta at evaluation time** is not demonstrated as a load-bearing carrier of the B05 primary behavioral advantage.

It does not establish that recurrent learning had no developmental causal influence. The B06 necessity lesion preserves developed motor weights, motor bias, and other learned non-recurrent state, so an earlier recurrent trajectory could in principle have influenced learning subsequently stored outside the final recurrent delta. That developmental-mediation hypothesis remains unresolved.

## Effect on disposition

These corrections harden scientific language but do not alter any machine artifact, seed, endpoint, lesion, robustness probe, aggregate result, production default, or B08 disposition.

The capacity safeguard remains procedurally triggered under the literal B02 rules because indicators 1 and 3 were frozen in advance and are reproducibly observed on all six challenger seeds. They are to be interpreted as warnings whose causes remain unresolved, not as proof that scaling will help.

The next experimental phase should therefore begin with a new versioned scaling preregistration. Scaling is an unresolved hypothesis to test, not a prediction of improved performance.
