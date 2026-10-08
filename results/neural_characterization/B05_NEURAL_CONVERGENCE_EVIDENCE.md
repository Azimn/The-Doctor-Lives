# B05 Neural-Convergence Characterization Evidence

Status: **COMPLETE**

This file records the preregistered B05 `neural_convergence_v05` challenger characterization. It is matched to the B04 legacy-v0.4 control and is evidence for B06-B08. It is not, by itself, a production disposition.

## Run identity

- execution commit: `311c651e4c2f3af563890e91ad2cebef3751c5ac`
- workflow: `neural-characterization-convergence-b05`
- workflow run: `37676112099`
- profile: `neural_convergence_v05`
- neurons: **4,096**
- seeds: **1842, 1843, 1844, 1845, 1846, 1847**
- causal timeline: **5,120 steps per seed**
- result validation: **6/6 PASS**
- checkpoint restart equivalence: **6/6 exact**
- no failed seed was replaced or selectively rerun
- B04/B05 curriculum hashes: **6/6 exact seed-matched**
- B04/B05 outcome-schedule hashes: **6/6 exact seed-matched**

The GitHub Actions artifacts retain each complete schedule, prepared manifest, result JSON, compressed 512 x 4,096 evaluation-state arrays, initial/stabilized/developed checkpoints, and CI summary. Artifact retention at execution was configured for 90 days.

## Immutable artifact ledger

| Seed | GitHub artifact ID | GitHub artifact digest | result.json SHA-256 | internal result artifact SHA-256 | evaluation state SHA-256 |
|---:|---:|---|---|---|---|
| 1842 | 11506828435 | `131b9e407cbc39ec6b4ee1d735fdb95025f60343bd81fd8e5b7c367e998bd06c` | `893f208cfeb0e4b1ef24a6953d8a4a33b9e8c883d6847c401026532323daff91` | `309e4c95ad83eb8ebc74cdfaf220ca1cfa84f848dde4b0407c878eb1289e2cdb` | `e56bb3571a26244fe5a0caaebf811f027e0a1550240e1d9b61e80b09413adaf1` |
| 1843 | 11507322618 | `609d10148a836838db692ebe9deb90aed928d332b85fd7c9a8ef0955071936d8` | `84d42fe418722a4af75561015b1834abb905f7e73ce1c499a2eea0a0c1f955e1` | `4f53cf7c10bc92921c1964f12ffc240d0f754c869c933243da0368d3b27d148f` | `cab90d4ff902cf4df74e07cbca3215277dbcf1aab8c4c3ca17a8491db41a47db` |
| 1844 | 11507093107 | `18caa465d3e006a7fa5cc34c3f11e5a44995edd13a096949dc648258dfdd2e8b` | `8c02f87b51d996026d63400d3b234ab03f881f411159648ec06d94323b952b97` | `2b23847c382b122d2ea02c9c47658d37bd1477be0c7772196907078cab86e334` | `5b54e416e63b09b8708cd5d624ef02a9f3fdc49839ae686237110756173f0a4e` |
| 1845 | 11506533482 | `ed2fbbdb8582a5909ce87f97c737526980e5e423c881e00f054471195d374d2e` | `3b48a69b4be311548400080b7b84fbafa9f5c38a568b9f3f1ca9983de7641150` | `0709483611ba84ce1cf32248334831dfd7380e4a83623531981d1b6c6e106ac3` | `e03335c8ea0d57f77e0650e6cf0f434bde6b315040e2e279273f907f1d9e2f92` |
| 1846 | 11507307820 | `626eaeec5dad4876e12b5db2ed103bb7b30e197811cc25caa59990dd59b2f6f7` | `f627ee4142f4972de641e3cbdd9c4e3f99a5f4b13ce6a02701d2be3e53c9b295` | `9a0af255bd3e904d14411016425aa5db0c43cdb3307db1a8c34b2634a5e84124` | `d3ae7398d1c18a2a2e1c593ab4af5db57733e5803fdd14b5dad86fc178d47562` |
| 1847 | 11507352516 | `a5058bbd3b6c23315b49bea18caf7f79a5d0cf2ca192474363d4091a39bcc9ff` | `1254569223b12ce0fc410a7fb6c9c92a0f5f70cb1cb84b542da6902e100e9ca0` | `f36422aa6395ce656b83828756b9c95368595cb8c541bf13f4365d2c7dc28099` | `14562c439753edd7e4ea311b07037b355c2e7f65f92001e10a16f4f135fbd888` |

## Descriptive challenger baseline

| Seed | mean expected-action p, pre | mean expected-action p, post | post-pre | mean pre/post JS | post entropy | post top-two margin | post effective dimensionality | context-separation cosine |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1842 | 0.099445 | 0.104011 | +0.004566 | 0.088238 | 0.896205 | 0.011166 | 12.087952 | 0.000002966 |
| 1843 | 0.099463 | 0.136110 | +0.036647 | 0.165540 | 0.761561 | 0.290615 | 12.094305 | 0.000002755 |
| 1844 | 0.100548 | 0.099065 | -0.001484 | 0.052616 | 0.932303 | 0.123227 | 14.656868 | 0.000003004 |
| 1845 | 0.100115 | 0.095014 | -0.005101 | 0.032484 | 0.960152 | 0.009222 | 12.611863 | 0.000002763 |
| 1846 | 0.098810 | 0.099665 | +0.000855 | 0.045840 | 0.952822 | 0.043855 | 12.968006 | 0.000002703 |
| 1847 | 0.100334 | 0.115597 | +0.015263 | 0.090713 | 0.870482 | 0.294491 | 13.459145 | 0.000003003 |

The developed challenger remained finite on every seed. Final development snapshots recorded zero state saturation, zero recurrent-weight clipping, zero E/I sign violations, and one spectral-homeostasis event per seed. The final recurrent-gain estimates were approximately 0.8720-0.8724, inside the preregistered 0.74-0.95 band.

## Matched B04/B05 descriptive comparison

The following comparison is descriptive. B05 does not satisfy the B02 causal gate; B06 lesions are still required.

| Seed | control post-pre expected-action p | challenger post-pre | challenger minus control | control effective dim. | challenger effective dim. | dim. ratio | runtime ratio |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1842 | -0.000680 | +0.004566 | +0.005246 | 5.429759 | 12.087952 | 2.226 | 2.439 |
| 1843 | +0.031690 | +0.036647 | +0.004957 | 6.149295 | 12.094305 | 1.967 | 2.702 |
| 1844 | -0.002680 | -0.001484 | +0.001196 | 6.500616 | 14.656868 | 2.255 | 2.648 |
| 1845 | -0.005944 | -0.005101 | +0.000843 | 5.342834 | 12.611863 | 2.361 | 2.211 |
| 1846 | -0.001849 | +0.000855 | +0.002704 | 5.281920 | 12.968006 | 2.455 | 2.196 |
| 1847 | +0.010831 | +0.015263 | +0.004432 | 5.520158 | 13.459145 | 2.438 | 2.149 |

Observed under the frozen matched protocol:

- challenger-minus-control change in mean expected-action probability is positive on **6/6 seeds**;
- median paired improvement on that reporting metric is approximately **+0.003568**;
- challenger postdevelopment effective dimensionality is approximately **1.97x-2.46x** the matched control, median approximately **2.31x**;
- context-separation cosine difference is approximately **2.07x-2.36x** the matched control, but remains very small in absolute magnitude, so it must not be described as strong contextual separation;
- challenger runtime is approximately **2.15x-2.70x** the matched control, median approximately **2.32x**;
- challenger peak RSS is approximately 199-201 MiB, compared with approximately 179-187 MiB for B04;
- challenger developed checkpoints are approximately 1.89 MB, compared with approximately 1.40 MB for B04.

These observations are consistent with a more differentiated recurrent state and a modest behavioral advantage on the preregistered reporting metric, at materially greater compute cost. They do not establish which convergence mechanism caused the difference, whether the difference is necessary or sufficient, whether it survives causal lesion, or whether Neural Convergence should become the production default.

## Regression integrity at execution head

On exact execution head `311c651e4c2f3af563890e91ad2cebef3751c5ac`:

- brain-tests: PASS, run `37676117351`
- Gate 1 fresh-install validation: PASS, run `37676117374`
- causal-audit repeatability v0.5: PASS, run `37676117236`

## Interpretation boundary

B05 establishes the challenger side of the frozen matched characterization. It does **not** establish:

- causal sufficiency or necessity;
- that a learned recurrent core constitutes identity;
- that 4,096 units are sufficient;
- that 4,096 units are a capacity ceiling;
- that the observed effective-dimensionality increase is automatically beneficial;
- that the runtime tradeoff is acceptable for production;
- that Neural Convergence should be promoted.

The next permitted runbook step is B06: recurrent-core causal lesions using the preserved B04/B05 artifacts and exact matched seeds.
