# Eidolon D2: Mnemosyne Loom + Chronos Coil, Executed Construction Report

**Date:** October 9, 2026 (US Central), October 10 UTC. **Status:** executed, source-verified implementation construction; no evidence of neural or behavioral superiority. **Production:** untouched. **PR:** [#36](https://github.com/Azimn/The-Doctor-Lives/pull/36), draft.

## Immutable sources and test provenance

The D2 protocol [was committed](../../docs/EIDOLON_D2_MNEMOSYNE_CHRONOS_PROTOCOL.md) as `c561db3000aa2abf15310502539f022d094893b4`, before the code. The initial CI attempt [38023911319](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38023911319) **failed** with a class-variable naming error in the `@staticmethod` evidence filter. That failure was retained in Actions rather than concealed. [Correction `16caa801`](https://github.com/Azimn/The-Doctor-Lives/commit/16caa801b3519a79b456c07cfb1947728505248f) reran the original 12 D2 tests with the preceding 20 Eidolon tests and successfully produced the first D2 source JSON; its original artifact is at [run 38023948675](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38023948675). This original output is permanently archived as [D2_SOURCE_CLOCK_ASSAY_V01.json](D2_SOURCE_CLOCK_ASSAY_V01.json).

A follow-up code audit identified **future relationship-state leakage in retrospective queries**: reading the current relationship trust score when evaluating an earlier tick could insert evidence that was not available at that time. The adapter now reconstructs a bounded relationship-trust proxy from *source-verified lived relationship event deltas present by the requested tick*, rather than consulting the latest relationship row. This is not asserted to reproduce Pretorius's complete production relationship-state history. A new regression test verifies historical output stability after an irrelevant later interaction. Old data was not silently overwritten.

**Latest audited implementation/CI source head:** `5ab28c043cea6b070e881f93d9a59374254d196b`. The last complete confirmed isolated [Eidolon run 38024066853](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024066853) passed **33/33 targeted tests**, including the historical trust-leak test and previous E2 tests. [Full production brain suite 38024066836](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024066836) passed **357/357 tests**, while [fresh install 38024066821](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024066821) and [causal audit repeatability 38024066866](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024066866) completed successfully. Later report/document-only commits do not modify the mechanisms.

**Original latest machine artifact:** [run 38024066853, artifact 11659171384](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024066853/artifacts/11659171384) with ZIP SHA-256 `ea4680ce6431f0ec0ff477e9332ff149a9787743a78b3e27fe6239e49c825c11`. The ZIP contains all three current researcher construction assays. The D2 JSON is also permanently [archived on the branch](D2_SOURCE_CLOCK_ASSAY_V011.json), preserving original and leakage-fixed versions separately.

## Measured deterministic construction behavior

The fixture created a real, isolated 128-neuron Pretorius instance, ingested one lived conversation about an anatomical apparatus with Henry and one external claim about a greenhouse door with Morgan. It then registered three active commitments and inspected their source-grounded prospective priorities. Scores are fixed by the scoring function; they are not the result of independent neural learning.

| Exact control condition | Prospective priority | Lived source events contributing |
| --- | ---: | ---: |
| Henry apparatus commitment, current clock | **0.489195** | 1 |
| Same goal with all history contributions disabled | **0.252000** | 0 |
| Identical description but falsely assigned to Morgan | **0.252000** | 0 |
| Commitment supported only by external testimony | **0.252000** | 0 |
| Henry apparatus commitment at projected due tick | **0.937195** | 1 |
| Projected due tick, temporal mechanism disabled | **0.517195** | 1 |
| Current clock, temporal mechanism disabled | **0.517195** | 1 |

The matched lived-event history contribution adds **0.237195** priority points at the same current tick, while the same text assigned to a different actor receives no such boost. The temporal mechanism moves the matched goal from **0.489195** to **0.937195** in the explicitly counterfactual future-clock evaluation. With temporal scoring disabled, the projected clock and current clock both yield **0.517195**. The external claim does not become evidence of Pretorius's lived past. Resolved commitments are omitted.

These are deliberately constructed demonstrations of the algorithm's gates and scoring. The numerical coefficients were chosen by the experiment designer. There are no independently authored tasks, no prospective observed outcomes, no train/test split, no learned temporal forecasts, and no human-adjudicated case labels. **The result does not prove the invented scoring formula improves Pretorius's judgments** compared with his existing v0.4 bridge, simple commitment sorting, graph retrieval, or another baseline.

## State, subject-access and provenance invariants

The tests verified that the D2 shadow returned the same values when run repeatedly on the same state and did not modify the authoritative database digest, Pretorius recurrent tick, neural action distribution or renderer-facing Subject Frame. The evidence reader excludes externally attributed events, inactive/corrupt records and preawakening memory classes. The relational test restricts actor-specific evidence to records whose **original event actor** matches the active commitment, not prose that happens to contain a person's name.

The retrospective safety check verifies that adding later unrelated relationship evidence does not change a historical priority estimate when the as-of tick remains fixed. The system preserves event IDs and memory IDs for machine audit only, never for character introspection. Subjectively narrated recollection remains under the production UPPB.

## Research decision

**D2 software/provenance/time invariants: PASS.** A source-bound verified memory reader and bounded prospective attention prototype function against real Pretorius stores, and the recorded CI checks are green.

**Improved artificial identity or learned neural intentionality: NOT ESTABLISHED.** All changes concern engineer-only shadow scores. Pretorius did not make a new decision, take an action, acquire learned recurrent synaptic dispositions, or demonstrate semantic generalization because of D2.

**Production promotion: BLOCKED.** PR #36 stays draft. The next meaningful test is a *pre-registered, independently authored matched-clone behavioral task* with future-source barriers, blind actor/episode splits, direct retrieval and due-sort baselines, a temporal adapter and a learned neural challenger. It must show actual differences in evidence-linked actions, correct negative/unknown responses, and causal learned-weight/readout lesions before becoming a candidate for production.
