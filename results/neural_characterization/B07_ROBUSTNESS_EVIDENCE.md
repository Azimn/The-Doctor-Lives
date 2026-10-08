# B07 Topology, Distribution, Clipping, and Robustness Evidence

Status: **COMPLETE**

This file records the preregistered B07 robustness phase for the 4,096-unit Neural Convergence challenger. B07 tests whether the recurrent developmental mechanism depends on exact topology, learned-delta assignment, high-change edges, clipping choices, or fragile weight values. It also verifies the E/I sign contract and fixed-seed repeatability. B07 does not decide the B08 production disposition and does not execute the reserved scaling ladder.

## Run identity

| Field | Value |
|---|---|
| Definitive B07 implementation/execution commit | `1f7071a7d6888fd80af37c895d0bcfe6b23f1b43` |
| Workflow | `neural-robustness-b07` |
| Definitive workflow run | `37683049666` |
| Profile | `neural_convergence_v05` |
| Neurons | 4,096 |
| Donor seeds | 1842, 1843, 1844, 1845, 1846, 1847 |
| Independent-topology recipients | next decisive seed cyclically |
| Source B04 workflow run | `37674813225` |
| Source B05 workflow run | `37676112099` |
| Source B06 workflow run | `37679303736` |
| B07 result validation | 6/6 PASS |
| Fixed-seed condition reruns | 6/6 PASS across all B07 conditions |
| E/I sign contract | 6/6 PASS across all B07 conditions |
| Preserved B04-B06 provenance | 6/6 PASS |
| Fresh-install / brain / causal-audit gates at execution head | PASS |

The workflow verifies preserved B04, B05, and B06 result hashes and repository SHAs before running. B07 also verifies the source checkpoint hashes recorded by B04/B05, recomputes the B05 learned recurrent delta, and requires the B06 stored learned delta and top-5-percent edge set to match exactly.

## Frozen B07 manipulations

Topology-matched transfer applies the exact same-seed B05 learned recurrent delta to the same-seed B04 phase1-stabilized recurrent topology. The B04 and B05 recurrent topology and E/I assignment must be exactly identical before this transfer is allowed.

Independent-topology functional homology uses the next preregistered seed's B04 topology. Donor recurrent deltas are projected separately within excitatory and inhibitory strata by baseline-weight quantile. This is a recurrent-mechanism transfer probe only. It is not identity transfer.

Assignment permutation deterministically permutes the exact learned-delta multiset within excitatory and inhibitory strata on the original B05 topology. High-change versus ordinary-edge comparison reverts the top 5 percent by absolute learned delta and compares it with an equal-size, E/I-matched set nearest the median absolute learned-delta magnitude.

Recurrent-weight clipping uses fixed magnitude quantiles of the developed recurrent weights. The p99 condition clips the largest approximately 1 percent of recurrent magnitudes; p95 clips the largest approximately 5 percent. Delta clipping separately clips learned recurrent deltas at their p95 and p75 absolute-magnitude quantiles.

Brittleness is tested with a deterministic multiplicative perturbation of every developed recurrent weight in the interval ±2 percent, followed by the normal sign/bounds contract. Every condition is independently rebuilt and evaluated twice within the same workflow job. Exact equality of action records and recurrent-state snapshots is required.

## Harness repair provenance

The first B07 workflow attempt, run `37682305260` at commit `a5b69978b874ad8ce0000d1effddf3ddb52c7762`, is **not accepted as decisive B07 evidence**.

That implementation expressed recurrent-weight clipping as 75 percent and 50 percent of the configured hard maximum weight. The developed networks did not contain weights near either threshold, so both manipulations changed zero recurrent edges on every seed. This made the required recurrent-weight clipping sensitivity arm a no-op.

The defect was discovered before B07 was accepted or summarized as completed. The repair changed only this clipping manipulation and its focused test. It replaced the ineffective hard-bound fractions with fixed p99 and p95 developed-weight magnitude quantiles, guaranteeing a structurally defined 1-percent and 5-percent clipping intervention without using behavioral outcomes to choose thresholds. Seeds, source artifacts, transfer definitions, assignment permutation, high-change comparison, delta clipping, perturbation, and all other B07 choices were unchanged.

The repaired implementation committed as `1f7071a7d6888fd80af37c895d0bcfe6b23f1b43` and the entire six-seed B07 workflow was rerun from scratch. Only run `37683049666` is used below.

## Immutable artifact ledger

| Seed | GitHub artifact ID | GitHub artifact digest | result.json SHA-256 | internal artifact SHA-256 | transform artifact SHA-256 |
|---:|---:|---|---|---|---|
| 1842 | 11510037291 | `e887904ee22aa9a58747f03a36519c49c43bd4f679b15f2c2dbbf3cd6bf447e2` | `92f12a2adeccf1ae40f6273a2da21f1a06863c864eeaf133c0755ccca9a4ca72` | `b302bc37a2db713a8e02581c0053ff8662bd0a32dd44116d07a1cdc7e0ac8ca2` | `4a2c213dd4c6808c096c038479d35fc7c55278420844e1950b613b906225aefd` |
| 1843 | 11509906857 | `9514b0c98a2c80fdf8d9d31b3d96502dc390a3fa68240f69935cad2a811e0e21` | `fd645815770f6c122059214d07fa6cdd66f3cb78e54acfffc46702a11c7cb45a` | `16c0bd38b7ec1bf7962e775cf9070d6c2dd8e49bdbf5deed9fa9a94f0eaa77e7` | `2f13403a45b23aaded25923c4159c5f431426ce8305f855842048b9082dde7d9` |
| 1844 | 11510521279 | `fea7cc0ceb8685b7d630035befaef1fa18095fc017b873d53117e31d02b17f8d` | `e88d0cc911435fab7b309842e4fa89988d5cfe2913fd87c5aacad6328a9fa810` | `ac3e7471b654148cd472b64cd90fe52fbcb5dd5a6165e85e1b46e5c5ff614a32` | `b6a7408cd7e341703cfa105273b0a5ed2f9cf42abb65f8cd3f41ba6ebd5261f4` |
| 1845 | 11509612616 | `a64d21d06ffe90206ee09106f7de1efea7d5272b3dd4c552ac8139e000dc6f67` | `ba66df4083b4e58f034cadffe442a94c02eead0ec9a557eaffd66324950a882a` | `daa37c51ef95bc7da18c4af62e02f0931ffa1c49ff952c6aca189e49642e7cdb` | `1cece18001cea5622c6c694f64d7534f78fbfd634751cc6339ebaf95d2f019d9` |
| 1846 | 11509327808 | `6d6af61e1fee8ab4aad58a21d7103a702a5bbffffce3b005bfe3857c1ce606a2` | `eac2152b2a2cc8656372aac22b9b3093b4b607ac7be6f8f285864934de186a6d` | `c8e984be450d6600f4bee351ec012ac6a517b6632648d4d5d74337931c291908` | `5e8b1a7108fba8ac2373ac4afc23129440c0b665aa68dfd1f578eedd2d06ee45` |
| 1847 | 11510416353 | `9751390b90c51be34446c68d4d72b298d348c03924d556cdb2b594d22d20ba22` | `58f26bb2e75f526540499b027ba4ecb8109c70c67b48efa1ec03076d2041c418` | `fe9ee7ee9f3a10456f7fbe4413de3fdb809822382a418454c477827ddcb7ab7e` | `af0182e21de543eb7f7f9e47bb16d4a3eea0b780a520bb12262c04b2eab1c984` |

## Transfer and distribution results

Positive transfer gain means the recipient's expected-action probability increased relative to its stabilized sham. Positive high-change-minus-ordinary damage means reverting high-change edges was more damaging than reverting the E/I-matched ordinary set.

| Seed | Topology-matched transfer gain | Independent-topology homology gain | Permuted minus exact-delta gain | High-change minus ordinary damage |
|---:|---:|---:|---:|---:|
| 1842 | +0.000014033 | +0.000006681 | +0.000000099 | -0.000000677 |
| 1843 | +0.000006435 | +0.000000265 | -0.000000431 | -0.000003253 |
| 1844 | +0.000000137 | -0.000008023 | -0.000001072 | +0.000000292 |
| 1845 | -0.000007213 | +0.000008537 | -0.000001104 | +0.000001811 |
| 1846 | +0.000008944 | -0.000002311 | +0.000001308 | -0.000001861 |
| 1847 | -0.000002286 | +0.000013724 | +0.000001232 | -0.000000226 |

Topology-matched transfer was positive on four seeds and negative on two, with median gain approximately +0.000003286. Independent-topology homology was also positive on four and negative on two, with median approximately +0.000003473. These are small, seed-dependent effects and do not establish robust transfer of the learned recurrent mechanism.

Assignment permutation versus the exact-delta condition split three positive and three negative, with median approximately -0.000000166. Preserving the learned-delta distribution while destroying exact edge assignment therefore changed the primary measure only microscopically.

The high-change versus ordinary-edge comparison was positive on only two of six seeds. Median high-change-minus-ordinary damage was approximately -0.000000452. This independently agrees with B06 that the largest learned recurrent changes do not form a reproducibly load-bearing behavioral core.

The top 5 percent of recurrent edges nevertheless carried roughly 22.6 to 23.3 percent of the learned delta's squared L2 norm across seeds. The delta is therefore magnitude-concentrated, but that statistical concentration did not translate into comparable causal concentration on the primary behavioral endpoint.

## Recurrent-weight clipping sensitivity

The repaired p99 manipulation changed exactly 1,306 recurrent edges on every seed. The p95 manipulation changed 6,528 to 6,530 edges, approximately five percent of the recurrent graph.

| Seed | p99 edges changed | p99 expected-action damage | p99 mean JS | p95 edges changed | p95 expected-action damage | p95 mean JS |
|---:|---:|---:|---:|---:|---:|---:|
| 1842 | 1,306 | -0.000003309 | 2.58e-8 | 6,530 | +0.000036492 | 3.75e-7 |
| 1843 | 1,306 | +0.000047585 | 2.05e-7 | 6,530 | +0.000121537 | 1.37e-6 |
| 1844 | 1,306 | +0.000004824 | 2.15e-8 | 6,528 | +0.000005426 | 1.42e-7 |
| 1845 | 1,306 | -0.000013056 | 4.12e-8 | 6,530 | -0.000023834 | 2.15e-7 |
| 1846 | 1,306 | +0.000015792 | 5.96e-8 | 6,528 | +0.000060244 | 5.62e-7 |
| 1847 | 1,306 | +0.000051422 | 2.49e-7 | 6,528 | +0.000089287 | 1.05e-6 |

Median p99 expected-action damage was approximately +0.00001031 and median mean JS from intact was approximately 5.04e-8. Median p95 damage was approximately +0.00004837 and median mean JS was approximately 4.69e-7. Five of six seeds moved in the damaging direction under p95 clipping, but the absolute effects remain small. B07 therefore detects mild sensitivity to aggressive trimming of the largest recurrent weights, not catastrophic clipping brittleness.

All clipping conditions retained finite weights and passed the E/I sign contract.

## Learned-delta clipping sensitivity

Clipping the learned recurrent delta itself remained even less consequential. The p95 delta clip affected approximately five percent of recurrent deltas and differed from the exact-delta sufficiency condition by a median expected-action change of approximately +0.000000181, with median mean JS approximately 2.10e-11.

The p75 delta clip affected approximately one quarter of recurrent deltas and differed from exact-delta sufficiency by a median of approximately +0.000000240, with median mean JS approximately 1.25e-10.

These results reinforce B06: the precise tails of the learned recurrent delta are not carrying a substantial portion of the measured behavioral effect.

## Modest perturbation and brittleness

A deterministic ±2-percent multiplicative perturbation of all developed recurrent weights produced expected-action damage of:

`+4.71e-6, +3.81e-6, -2.67e-7, +3.02e-6, -1.11e-7, +9.71e-7`

The median was approximately +0.000001997. Mean full-action-vector JS divergence from intact had a median of approximately `2.77e-9`, with every seed remaining below `4.85e-9`.

The 4,096-unit challenger therefore does not show meaningful brittleness under this preregistered modest recurrent-weight perturbation.

## Determinism and sign integrity

Every B07 condition was constructed and evaluated twice from independent checkpoint loads under the same fixed seed. Action records and recurrent-state matrices matched exactly for every condition on all six seeds.

Every evaluated condition passed the excitatory/inhibitory sign contract, finite-weight check, and configured hard-bound check. No B07 hard-integrity defect was observed.

## Capacity-adequacy relevance

B07 does not run a larger network and cannot determine whether 4,096 units are sufficient.

Within the B02 warning framework, B07 does **not** provide evidence for persistent gain-bound pressure or for a tiny behaviorally load-bearing recurrent causal core. The p95/p99 clipping probes are stable, the ±2-percent perturbation is stable, and high-change edges are not disproportionately necessary on the primary behavioral measure.

Representational crowding and cross-context interference are separate B02 indicators that must be judged from the complete B04-B07 record in B08 rather than inferred from these robustness probes alone. Likewise, the absence of a scaling experiment remains an epistemic constraint: B07 cannot establish a scaling plateau.

## B07 interpretation

B07 finds a recurrent mechanism that is technically stable but causally weak on the measured behavioral endpoint at 4,096 units.

The learned recurrent delta does not robustly transfer as a useful behavioral effect across either matched or independent topologies. Exact edge assignment is not strongly privileged over E/I-stratified permutation. The largest learned changes contain a disproportionate share of delta magnitude but are not disproportionately necessary for expected-action behavior. Delta clipping has negligible effect. Direct clipping of the largest developed recurrent weights has a small measurable effect at p95 but not a severe one. A modest global weight perturbation is essentially behaviorally invisible.

Together with B06, this argues against explaining the B05 advantage as a fragile or highly localized recurrent-weight code. It does not identify which other Neural Convergence mechanisms produce the B05 descriptive advantage, and it does not show that larger capacity would behave the same way.

No B08 disposition is authorized from B07 alone. B08 must now integrate the complete B04-B07 evidence, including the preregistered capacity-adequacy safeguards, before any production-default decision is made.
