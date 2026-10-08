# B06 Recurrent-Core Causal Lesion Evidence

Status: **COMPLETE**

This file records the preregistered B06 causal lesion phase for the 4,096-unit Neural Convergence challenger. B06 tests whether the learned recurrent-weight change observed after the frozen B05 developmental curriculum is causally load-bearing for the B05 effects. It does not decide the final B08 production disposition.

## Run identity

| Field | Value |
|---|---|
| Definitive B06 implementation/execution commit | `9a88767853fdffa0a9f21d031c4f0b73106a8863` |
| Workflow | `neural-causal-lesions-b06` |
| Definitive workflow run | `37679303736` |
| Profile | `neural_convergence_v05` |
| Neurons | 4,096 |
| Seeds | 1842, 1843, 1844, 1845, 1846, 1847 |
| Source B04 workflow run | `37674813225` |
| Source B04 execution commit | `4346ffb95be634c9695009d21317a2f80e5fccc5` |
| Source B05 workflow run | `37676112099` |
| Source B05 execution commit | `311c651e4c2f3af563890e91ad2cebef3751c5ac` |
| B06 result validation | 6/6 PASS |
| Same-run zero-edge sham | 6/6 exact in action records and recurrent states |
| Source curriculum/outcome hash matching | 6/6 PASS |
| Targeted/random lesion size and E/I matching | 6/6 PASS |

The B06 workflow verifies the preserved B04 and B05 result hashes, profiles, seeds, 4,096-unit configuration, restart status, curriculum hash, outcome-schedule hash, and B05 checkpoint hashes before a lesion is allowed to run.

## Frozen lesion implementation

The necessity lesion loads the B05 developed checkpoint and replaces every recurrent weight with the corresponding B05 phase1-stabilized value. Recurrent topology remains unchanged, while developed non-recurrent checkpoint state remains in place.

The sufficiency condition loads the B05 phase1-stabilized checkpoint and adds only the exact learned recurrent delta. It does not import the developed motor weights, motor bias, neural state, eligibility, synaptic tags, or RNG state.

The causal-core ranking metric is absolute developed-minus-stabilized recurrent-weight change. The top 5 percent of recurrent edges are selected with ascending CSR data index as the deterministic tie-break. The matched random lesion is disjoint from the targeted set and exactly matches its excitatory/inhibitory edge counts for each seed.

The sham validity gate is an explicit same-run zero-edge recurrent lesion. Two independently loaded developed checkpoints are evaluated on the same runner, with one passed through a zero-edge lesion operation. Exact equality of action records and recurrent states is required. This avoids turning heterogeneous GitHub runner numerical behavior into an unintended causal criterion.

Relearning starts from the developed checkpoint after the full necessity lesion and replays the original 3,584-step developmental curriculum with the original learning, reinforcement, and outcome-capture interfaces.

## Immutable artifact ledger

| Seed | GitHub artifact ID | GitHub artifact digest | result.json SHA-256 | internal result artifact SHA-256 | learned-delta SHA-256 |
|---:|---:|---|---|---|---|
| 1842 | 11507682716 | `28fcdc8381c7911f9f481d1ce13c48dbd8362baf8b4a2c1251ba6c3fbd68ee87` | `9a044467b5e45c72077287f58e8dab70f0e234a15410feea48037afcf5edc8b6` | `2268df74c6e6ab3f0e63cfa937237ca7cd16889011f8594a679178df2437f365` | `39dba12e978b9bf568cb8fa391d1bcac0f71ed77b17118aabc602796623d4bbe` |
| 1843 | 11508267185 | `ffd9111087eeab11f6edf277e1cfd3132dde8e7b210f1dd563eff118b5672003` | `d396aff84c551aa331131797242b17a5ed1bd3f0287384635eda8a9f920131eb` | `da8e479c1d694325d697fcb46406523e2cc223d37eecf111d859d7cbe1bf44ff` | `4d8867baeb103cd4b3c1be8e12b99f6e3ae5fa45974bb860676072e716b441cb` |
| 1844 | 11509012060 | `347dd497c2870e3b1d8b60215edf92e7f8c60d56db117de7dc606a354e8e70ff` | `7b5dff046bdaa95a5312df7134a39c7df80f6b422f9f5838dd2aa8fc95771211` | `048b5c829ffd22bee7c6e633c383623b901d9b933db26fa3bab5ab79dfa6c98f` | `d9ba05456d22ee8b1c14aa577e49b8acce096c5347c27f6dd7750347f9dc9060` |
| 1845 | 11507662842 | `f07032171be5226bf916a02c1b36262fdd38bc9819a7d7c39129262570a0293f` | `0a0ec8ea41ffb077b0a81209ff31e5ed580711ff7050f3f62731fa6cfc69bfe4` | `d88ccc46a3ed191bc4a8435386c9ebccb7f8658f8bad82dabd098ee65cb52b06` | `31a2b3cbf6261997e9271b3999ecc8117b87016ec8a6d95bbea9568414ccafbb` |
| 1846 | 11508926744 | `a7903d4c7c21eb9d36ca08ff7aa902d6f234f63f84d140171bbf8765b5566b49` | `68e16eb6ac0f1f3530db6820a850f27fcbc166bc3539c2c700142339ccf37bdc` | `2b5db27534856b9ab86c643fe28f6478832601e6afc98cae316bf648e5c4e43d` | `ddd277f289f0c2ef0beabd53729d76cfc747af930fe73772accb660cda4349bd` |
| 1847 | 11508697103 | `a36e371e4a17a19176c3a03a790fc7763db3a8d6c930f689ef9dd62234c2dbcc` | `7d131fe99832c38bd62d16c7e0625a222d768103a5b7fc0bbf94225f210eafee` | `1cf5965492c83926eb6f28b01eb1ce05d3fd7dd1e312fbfbda17e36daa15056d` | `9a02451ec90402c3ccd9ada64d0aad7be4ac9f85cbe07c1bb5af59fa6a4b46eb` |

The learned recurrent delta was nonzero on every recurrent edge for every seed. The networks contained approximately 130.6 thousand recurrent edges, so the frozen top-5-percent causal-core lesion contained 6,528 to 6,530 edges depending on the seed.

## Primary causal contrasts

Positive necessity damage means the full recurrent-delta reversion reduced expected-action probability. Positive targeted-minus-random damage means the targeted top-5-percent lesion was more damaging than its matched random lesion.

| Seed | Necessity damage | Paired B05 effect after necessity lesion | Sufficiency gain over stabilized sham | Targeted damage | Random damage | Targeted minus random damage |
|---:|---:|---:|---:|---:|---:|---:|
| 1842 | -0.000004008 | +0.005250132 | +0.000003520 | -0.000000884 | +0.000000782 | -0.000001666 |
| 1843 | -0.000011538 | +0.004968149 | +0.000000223 | -0.000003265 | +0.000000010 | -0.000003275 |
| 1844 | +0.000000129 | +0.001196215 | +0.000001712 | +0.000000349 | -0.000000222 | +0.000000570 |
| 1845 | +0.000002027 | +0.000840493 | +0.000001659 | +0.000000822 | -0.000000630 | +0.000001452 |
| 1846 | -0.000001894 | +0.002705748 | -0.000001127 | -0.000001917 | +0.000000206 | -0.000002122 |
| 1847 | -0.000005489 | +0.004437436 | -0.000002658 | -0.000000440 | -0.000000629 | +0.000000189 |

Full recurrent-delta necessity damage was negative on four of six seeds and positive on two. The median was approximately -0.00000295. In other words, removing the entire learned recurrent-weight delta did not reproducibly damage the preregistered expected-action measure.

More importantly, the preserved challenger-minus-control developmental effect remained positive on all six seeds after the full recurrent-delta lesion. Its median was approximately +0.00357159, essentially the same scale as the B05 paired descriptive improvement. This is strong evidence that the B05 expected-action advantage is not carried by the learned recurrent-weight delta isolated by B06.

The sufficiency transplant was positive on four seeds and negative on two, with a median gain of only about +0.000000941 over the stabilized sham. The absolute sufficiency fraction relative to each seed's own B05 profile change never reached 0.14 percent. The learned recurrent delta therefore recovered essentially none of the B05 behavioral change by itself.

Targeted top-5-percent lesions were more damaging than matched random lesions on only three of six seeds. The median targeted-minus-random expected-action damage was approximately -0.000000739. The frozen causal-core test therefore does not support disproportionate necessity on the primary behavioral measure.

## Full action-vector and representational effects

The necessity lesion changed the complete action vector only microscopically. Median mean Jensen-Shannon divergence from the intact same-run condition was approximately `6.39e-9`, with a range from approximately `1.83e-9` to `3.72e-8`.

Removing the entire recurrent delta also left the B05 representational geometry nearly unchanged. Across seeds, the median change in covariance participation ratio was approximately +0.000652 against intact values around 12 to 15. Median context-separation change was approximately `-4.18e-10`, and median state-vector-variance change was approximately `+5.38e-10`.

The sufficiency transplant likewise produced only trace representational changes relative to its stabilized sham. Median participation-ratio change was approximately -0.000176. Median context-separation change was approximately `+3.94e-10`, positive on all six seeds but negligible in absolute magnitude. Median state-vector-variance change was approximately `-5.11e-10`.

The targeted high-change lesion did produce a larger full-vector JS perturbation than its matched random lesion on all six seeds. The median targeted-minus-random mean-JS difference was approximately `4.54e-10`. This direction is consistent across seeds, but the magnitude is far too small to characterize the selected edge set as a load-bearing causal core. It is recorded as a weak sensitivity signal only.

A key consequence is that B05's roughly twofold-plus effective-dimensionality advantage over the legacy control survives full recurrent-delta reversion. B06 therefore localizes that descriptive representational advantage away from the learned recurrent-weight delta itself. It may arise from other Neural Convergence mechanisms or state/configuration differences, which B06 does not isolate.

## Relearning after lesion

After full recurrent-delta reversion, replaying the original developmental curriculum reconstructed the original learned recurrent delta with extremely high fidelity.

| Seed | Final delta cosine to original | Final delta norm ratio | Final mean JS from original intact behavior |
|---:|---:|---:|---:|
| 1842 | 0.999996618 | 0.998757389 | 0.040206652 |
| 1843 | 0.999999300 | 0.999842845 | 0.097179696 |
| 1844 | 0.999998428 | 1.000502779 | 0.038993396 |
| 1845 | 0.999999207 | 1.000085725 | 0.026379839 |
| 1846 | 0.999999071 | 1.000157786 | 0.012392940 |
| 1847 | 0.999999153 | 1.000424379 | 0.092410761 |

Median final delta cosine was approximately 0.999999112 and the median norm ratio was approximately 1.00012176. The recurrent plasticity trajectory is therefore highly reproducible under exact curriculum replay.

That result is not evidence of behavioral recovery, because the full necessity lesion produced essentially no behavioral deficit to recover. Re-exposure also updates the non-recurrent learned components under the frozen protocol. Final behavior consequently moved away from the original intact checkpoint, with median mean JS divergence approximately 0.0396. B06 records this as reproducible recurrent relearning without claiming recovery of a lost function.

## Sham and cross-run numerical diagnostics

The explicit same-run zero-edge lesion sham matched the untouched developed condition exactly on all six seeds, in both action records and recurrent-state matrices. The lesion operator therefore passes its no-op control.

Cross-run replay against the preserved B05 artifact is retained only as a numerical diagnostic. The recurrent-state matrices reproduced bit-for-bit on all six seeds in the definitive run. Action probabilities reproduced bit-for-bit on three seeds and showed tiny cross-run differences on the other three, with maximum absolute difference no larger than approximately `1.03e-7`. Because B05 preregistered exact restart equivalence within each characterization run, not across heterogeneous GitHub hosts, this cross-run motor-output drift is not used as a B06 validity gate.

## Harness repair provenance

Several preliminary B06 workflow attempts were invalidated before the definitive evidence set was accepted. The first implementation incorrectly required literal JSON-record equality against the preserved B05 run, which was stricter than the B05 restart contract. A subsequent repair added an even stricter cross-run recurrent-state equality gate, and another attempt showed that a preserved B05 action score can also drift slightly across GitHub hosts even when the recurrent-state matrix is bitwise identical.

No preliminary lesion result was admitted as decisive evidence. The final protocol implementation instead uses the scientifically relevant same-run zero-edge sham required by B02 and records cross-run B05 replay only as a diagnostic. The lesion definitions, six seeds, curriculum, outcome schedule, 5-percent causal-core ranking rule, E/I-matched random control, and relearning curriculum were not changed in response to lesion outcomes.

## B06 interpretation

B06 does not support the hypothesis that the learned recurrent-weight delta is a load-bearing cause of the B05 expected-action improvement. Full reversion does not reproducibly damage the effect, transplantation does not reproduce a meaningful portion of it, and targeted high-change edges do not outperform matched random lesions consistently on the primary behavioral measure.

B06 also does not support a strongly concentrated causal recurrent core. The all-seed targeted-over-random JS direction is noted, but its absolute magnitude is negligible.

The most positive causal finding is narrower: the recurrent plasticity trajectory itself is highly reproducible under curriculum replay. That establishes reliable recurrent learning dynamics, but reproducibility is not the same as causal behavioral necessity.

This result does not invalidate B05. B05 established a reproducible descriptive advantage for the complete Neural Convergence profile. B06 shows that one obvious candidate carrier, the learned recurrent-weight delta, does not explain that advantage. Other convergence mechanisms remain possible causes and must not be credited or rejected without controlled evidence.

No B08 disposition is authorized from B06 alone. The next permitted step remains B07, using the frozen topology, distribution, clipping, sign-contract, brittleness, transfer, and fixed-seed probes from B02.
