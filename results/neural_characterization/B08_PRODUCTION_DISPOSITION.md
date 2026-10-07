# B08 Neural Convergence Production Disposition

Status: **COMPLETE**

## Disposition

**RETAIN OPTIONAL - CAPACITY ADEQUACY UNRESOLVED; SCALING STUDY REQUIRED BEFORE REJECTION**

The accepted production default remains `legacy_v04`. The `neural_convergence_v05` profile remains an opt-in research profile. B08 does not authorize production-default promotion, architectural rejection, or a larger-network run without a new versioned preregistration.

This disposition is the result of the frozen B02 rules applied to the complete B04-B07 record. It is not a preference added after seeing the data.

## Evidence identity

| Phase | Exact execution commit | Workflow run |
|---|---|---:|
| B04 legacy control | `4346ffb95be634c9695009d21317a2f80e5fccc5` | `37674813225` |
| B05 Neural Convergence challenger | `311c651e4c2f3af563890e91ad2cebef3751c5ac` | `37676112099` |
| B06 causal lesions | `9a88767853fdffa0a9f21d031c4f0b73106a8863` | `37679303736` |
| B07 robustness | `1f7071a7d6888fd80af37c895d0bcfe6b23f1b43` | `37683049666` |

The machine-readable B08 decision is recorded in `results/neural_characterization/B08_DECISION.json`.

## Hard-integrity gate

The current evidence does not show an integrity defect that requires abandoning the optional challenger.

B04 and B05 both reproduced their checkpoint/restart evaluations exactly on all six seeds. B07 rebuilt every robustness condition twice and required exact equality of action records and recurrent-state snapshots; all six seed jobs passed. B05 and B07 recorded no E/I sign violations, no non-finite recurrent state, and no configured recurrent-weight bound violation. B07's repaired p99/p95 clipping probes were finite and stable rather than collapsing.

The repository-wide `brain-tests` workflow executes the entire `tests/` suite with unittest discovery. The exact B07 evidence head passed this suite, including first-person projection/firewall tests, checkpoint persistence tests, state migration tests, Neural Convergence integration tests, and release-candidate tests. Gate 1 fresh-install and historical-state migration also passed.

Cross-profile neural checkpoint switching remains intentionally fail-closed: an existing legacy checkpoint cannot silently become a convergence checkpoint, and vice versa. The release-candidate tests require an explicit neural checkpoint migration for such a switch. Because B08 retains legacy as the default and keeps convergence opt-in, this is safe for the current disposition. A future promotion would still need an explicit production migration plan rather than a silent profile change.

## Behavioral and representational value

B05 produced a favorable matched direction on the preregistered expected-action reporting metric on **6 of 6 seeds**. The paired challenger-minus-control effect ranged from approximately `+0.000843` to `+0.005246`, with median approximately `+0.003568`.

The challenger also produced substantially higher postdevelopment effective dimensionality. The matched challenger/control ratio ranged from approximately `1.97x` to `2.46x`, with median approximately `2.31x`.

Those advantages came at materially higher computational cost. Median challenger runtime was approximately `2.32x` the matched legacy control.

The descriptive result is therefore not a null result. Neural Convergence changes the developed system in a reproducible way and produces measurable representational and behavioral differences. That is sufficient reason to preserve it as an optional research profile rather than delete it.

## Causal promotion gate

The causal promotion gate is **not met**.

B06 removed the entire learned recurrent-weight delta and did not reproducibly damage the B05 expected-action advantage. The preserved challenger-minus-control advantage remained positive on all six seeds after that reversion. Transplanting the learned recurrent delta into the stabilized state reproduced essentially none of the B05 behavioral change. The top-5-percent high-change recurrent set was not more damaging than an E/I-matched random set on the primary behavioral endpoint.

B07 independently reinforced that result. Same-topology transfer and independent-topology functional-homology transfer were small and seed-dependent. Destroying exact learned-delta edge assignment while preserving its E/I-stratified distribution barely changed the result. The largest learned changes were not disproportionately necessary relative to ordinary edges.

The recurrent learning trajectory itself is highly reproducible, but reproducibility is not causal behavioral necessity. B02 requires at least one claimed Neural Convergence mechanism to be load-bearing under controlled lesion before production-default promotion. That requirement was not satisfied.

**PROMOTE is therefore prohibited.**

## Brittleness and stability

B07 does not show unacceptable brittleness.

All six seeds passed fixed-seed exact reruns and the E/I sign contract. Clipping approximately the largest 1 percent of developed recurrent weights produced only small changes. Clipping approximately the largest 5 percent produced a larger but still small effect, with no instability or collapse. Clipping the learned recurrent delta itself remained negligible.

A deterministic multiplicative perturbation of every recurrent weight by up to plus or minus 2 percent produced median expected-action damage of approximately `+0.0000020` and median full-action-vector Jensen-Shannon divergence of approximately `2.77e-9`.

The challenger is therefore technically stable enough to retain for research even though its learned recurrent weights are not strongly load-bearing on the primary behavioral metric.

## Capacity-adequacy audit

B02 requires B08 to test five capacity-warning indicators before rejecting the 4,096-unit challenger.

### Indicator 1: representational crowding

**PRESENT, 6/6 seeds.**

The challenger improved effective dimensionality substantially, but its absolute context separation remained extremely small. Postdevelopment mean within-context cosine similarities were approximately `0.999943-0.999948`; mean across-context similarities were approximately `0.999941-0.999945`. Context-separation differences were only approximately `2.70e-6-3.00e-6`.

The states are therefore still nearly collinear across distinct probe families even after the approximately 2.31x median dimensionality increase. The behavioral improvement is also modest in absolute probability terms. Under the frozen B02 language, this qualifies as representational crowding.

### Indicator 2: cross-context interference

**NOT ESTABLISHED.**

The block-level anchor trajectories are seed-sensitive and closely parallel the legacy control. Some earlier block effects reverse after later development and mixed-conflict replay, while others persist or grow. The reversal pattern is not reproducibly present across a majority of challenger seeds in a way that distinguishes the challenger from the control.

B08 therefore does not count this indicator as positive.

### Indicator 3: persistent saturation or gain-bound pressure

**PRESENT, 6/6 seeds.**

The measured state-saturation fraction remained `0.0`, so this is not a high-saturation failure. However, the intrinsic excitability homeostat drove `state_gain` from its initial `1.0` to the configured upper bound `1.20` by the end of the 512-step neutral stabilization phase on every seed.

From that point onward, `state_gain` remained exactly `1.20` in every recorded developmental-block snapshot, at the developed checkpoint, and through final evaluation on all six seeds. The recurrent-gain estimator remained inside its configured spectral band and recurrent weights did not hit their hard clipping bound.

This persistent upper-bound occupancy is a genuine gain-bound pressure signal under B02 section 10.1. It does not prove that additional neurons will solve the problem, but the preregistration deliberately treats persistent gain-bound pressure as a warning against inferring adequate representational headroom from one network size.

### Indicator 4: capacity-like causal concentration

**NOT PRESENT.**

The top 5 percent of learned recurrent changes contain roughly 22.6-23.3 percent of the learned delta's squared L2 magnitude, but B06 and B07 do not show that those edges carry a disproportionate share of learned behavior. Targeted lesions did not produce a severe bottleneck.

Magnitude concentration without causal behavioral concentration does not satisfy this indicator.

### Indicator 5: no observed plateau evidence

**APPLIES AS AN EPISTEMIC CONSTRAINT.**

B02-B07 did not execute the reserved scaling study. Nothing in the current evidence establishes that 4,096 units lie on a scaling plateau. This indicator does not by itself trigger the capacity-unresolved disposition, but it prohibits claims that larger networks would necessarily fail to improve separation or reduce interference.

## Capacity trigger

Two of the preregistered positive capacity-warning indicators, indicators **1 and 3**, are reproducibly present across all six seeds.

Without the capacity safeguard, the failed causal promotion gate, modest absolute behavioral effect, and approximately 2.32x runtime cost would justify keeping legacy v0.4 as the production default and could support a `REJECT AS DEFAULT` disposition for the 4,096-unit challenger.

B02 section 10.2 explicitly prohibits that architectural rejection when at least two of indicators 1-4 are reproducibly present across at least four of six seeds.

That threshold is met.

The special capacity-unresolved disposition is therefore required:

**RETAIN OPTIONAL - CAPACITY ADEQUACY UNRESOLVED; SCALING STUDY REQUIRED BEFORE REJECTION**

## What B08 does and does not conclude

B08 concludes that the current 4,096-unit Neural Convergence profile has reproducible descriptive value and acceptable technical stability, but it has not demonstrated a load-bearing recurrent-learning mechanism sufficient for production-default promotion.

B08 also concludes that the 4,096-unit result cannot fairly support architectural rejection because the frozen capacity-warning rule is triggered.

B08 does **not** conclude that 16,384 or 65,536 units will improve the result. It does not conclude that neuron count is the cause of the weak causal result. It does not conclude that recurrent weights constitute identity, personhood, consciousness, or biological equivalence.

The unresolved scientific question is narrower: whether increased representational capacity changes contextual separation, gain-bound pressure, interference, causal concentration, or behavioral value under an otherwise controlled Neural Convergence experiment.

## Required next step before larger-network evidence

No larger-network decisive run is authorized by B08 itself.

Before running a scaling experiment, write and commit a new versioned preregistration. The reserved follow-up ladder remains:

`1,024 -> 4,096 -> 16,384 -> 65,536`

A future protocol may omit a rung only for documented hardware or runtime infeasibility and must preserve sparse-connectivity comparisons or explicitly preregister how connectivity scaling changes.

The scaling study must distinguish smooth capacity benefit, a qualitative threshold, saturation or plateau, worsening stability or cost, and a bottleneck that shifts away from capacity.

Until that study exists, legacy v0.4 remains the production default and Neural Convergence remains optional research evidence rather than a rejected architecture.
