# Phase C protocol status

Active research branch: `research/neural-capacity-phase-c`

Production baseline: `fb9e9c29f98e8a532fdff82f3152778328af57a6`

## Active protocol

`pretorius-flywire-whole-connectome-c01-v2` in
`FLYWIRE_WHOLE_CONNECTOME_PHASE_C_PREREGISTRATION.md`.

This protocol supersedes `pretorius-capacity-mechanism-c01-v1` **before any
Phase C scientific outcomes were generated**. The v1 document remains in the
repository and Git history as an abandoned preregistration. It must not be
silently reactivated or mixed with v2 evidence.

The reason for supersession is methodological, not outcome-dependent: before
executing the capacity ladder, a resource survey identified reusable whole-brain
FlyWire simulators and analysis tooling. Phase C therefore tests the actual
evolved connectome topology at full scale before spending the research budget on
hand-scaled 16,384- or 65,536-unit derivatives.

Phase B is immutable. `legacy_v04` remains the production default.
`neural_convergence_v05` remains opt-in research. Nothing in Phase C is
subject-accessible or production-promoting.

## Sequence

1. C02: reproduce a pinned upstream whole-brain backend smoke run without
   Pretorius scoring.
2. C03: run a full-FAFB exploratory Pretorius input-projection pilot on the
   intact connectome.
3. C04: compare intact topology with audited topology controls.
4. C05: if an effect survives controls, lesion/compress from the full graph
   downward and determine whether 65K, 16K, or another scale preserves it.
5. Any production decision requires a separate release gate.

Only this single Phase C branch is to be used.
