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

The recurrent learning trajectory itself is highly reproducible, but reproducibility is not causal behavioral necessity. The controlled B06 result is specifically about the **final learned recurrent-weight delta at evaluation time**. The necessity lesion deliberately preserves developed motor weights, motor bias, and other learned non-recurrent state. Phase B therefore does not rule out developmental mediation in which earlier recurrent dynamics influenced learning that was subsequently stored outside the final recurrent delta.

B02 requires at least one claimed Neural Convergence mechanism to be demonstrated as load-bearing under controlled lesion before production-default promotion. That requirement was not satisfied.

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

The challenger improved effective dimensionality substantially, but its preregistered absolute context-separation endpoint remained extremely small. Postdevelopment mean within-context cosine similarities were approximately `0.999943-0.999948`; mean across-context similarities were approximately `0.999941-0.999945`. Context-separation differences were only approximately `2.70e-6-3.00e-6`.

Those preregistered cosine values are computed on **uncentered firing-rate vectors**. All neurons carry a substantial common firing-rate component, so the near-1.0 raw cosine values are sensitive to that common offset. As a post hoc falsification check requested by the independent review, the preserved B05 evaluation matrices were centered across observations per neuron before cosine geometry was recomputed. Under that non-preregistered centered calculation, within-minus-across context separation is approximately `0.0509-0.0590` across the six seeds. This check does not replace or retroactively redefine the preregistered metric.

Accordingly, the stronger phrase that the states are intrinsically "nearly collinear" is not warranted without qualification. The capacity-warning judgment instead rests on the preregistered weak raw separation **together with** the low absolute covariance participation ratio, approximately 12-15 effective dimensions in a 4,096-unit state space, and only modest absolute behavioral differentiation. Under the frozen B02 warning rule, that remains sufficient to record representational crowding as a warning, not as proof that neuron count is the cause.

### Indicator 2: cross-context interference

**NOT ESTABLISHED.**

The block-level anchor trajectories are seed-sensitive and closely parallel the legacy control. Some earlier block effects reverse after later development and mixed-conflict replay, while others persist or grow. The reversal pattern is not reproducibly present across a majority of challenger seeds in a way that distinguishes the challenger from the control.

B08 therefore does not count this indicator as positive.

### Indicator 3: persistent saturation or gain-bound pressure

**PRESENT AS A GAIN-BOUND WARNING, 6/6 seeds.**

The measured state-saturation fraction remained `0.0`, so this is not a high-saturation failure. However, the intrinsic excitability homeostat drove `state_gain` from its initial `1.0` to the configured upper bound `1.20` by the end of the 512-step neutral stabilization phase on every seed.

From that point onward, `state_gain` remained exactly `1.20` in every recorded developmental-block snapshot, at the developed checkpoint, and through final evaluation on all six seeds. The recurrent-gain estimator remained inside its configured spectral band and recurrent weights did not hit their hard clipping bound.

This is a genuine preregistered **gain-bound warning**, but it is not evidence that 4,096 neurons are inadequate. The implementation raises `state_gain` whenever measured saturation is below the configured target of `0.18`; this update occurs independently of the `learn` flag. Because measured saturation is `0.0`, the current homeostatic rule is mechanically driven toward the `1.20` ceiling even during the neutral `learn=False` stabilization phase. The observation is therefore compatible with insufficient representational headroom, but it is also compatible with a homeostatic-target or excitability-calibration mismatch. Phase B did not manipulate network size or the homeostatic target, so it cannot distinguish those explanations.

B02 deliberately treats persistent gain-bound occupancy as a warning against inferring adequate headroom from a single network size. B08 therefore counts this indicator procedurally while leaving its cause unresolved.

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

That threshold is met under the literal preregistered warning rule. Indicators 1 and 3 are **warnings**, not a diagnosis that neuron count caused the observed limitations. Their alternative explanations remain live, including common-offset sensitivity in the raw cosine endpoint and homeostatic calibration in the gain-bound observation.

The special capacity-unresolved disposition is therefore required:

**RETAIN OPTIONAL - CAPACITY ADEQUACY UNRESOLVED; SCALING STUDY REQUIRED BEFORE REJECTION**

## What B08 does and does not conclude

B08 concludes that the current 4,096-unit Neural Convergence profile has reproducible descriptive value and acceptable technical stability, but it has not demonstrated the **final learned recurrent-weight delta** as a load-bearing carrier of the primary behavioral endpoint, nor has Phase B isolated another Neural Convergence mechanism strongly enough to satisfy the production-default causal gate. Developmental mediation through non-recurrent learned state remains an unresolved possibility.

B08 also concludes that the 4,096-unit result cannot fairly support architectural rejection because the frozen capacity-warning rule is triggered.

B08 does **not** conclude that 16,384 or 65,536 units will improve the result. It does not conclude that neuron count is the cause of the weak causal result. It does not conclude that recurrent weights constitute identity, personhood, consciousness, or biological equivalence.

The unresolved scientific question is narrower: whether increased representational capacity changes contextual separation, gain-bound pressure, interference, causal concentration, or behavioral value under an otherwise controlled Neural Convergence experiment. Scaling is an unresolved hypothesis requiring experiment, not a prediction that 16,384 or 65,536 units will perform better. A follow-up should also distinguish capacity effects from homeostatic/excitability calibration effects.

## Required next step before larger-network evidence

No larger-network decisive run is authorized by B08 itself.

Before running a scaling experiment, write and commit a new versioned preregistration. The reserved follow-up ladder remains:

`1,024 -> 4,096 -> 16,384 -> 65,536`

A future protocol may omit a rung only for documented hardware or runtime infeasibility and must preserve sparse-connectivity comparisons or explicitly preregister how connectivity scaling changes.

The scaling study must distinguish smooth capacity benefit, a qualitative threshold, saturation or plateau, worsening stability or cost, and a bottleneck that shifts away from capacity.

Until that study exists, legacy v0.4 remains the production default and Neural Convergence remains optional research evidence rather than a rejected architecture.
