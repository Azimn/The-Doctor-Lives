# B04 Legacy-Control Characterization Evidence

Status: **COMPLETE**

This file records the preregistered B04 legacy-v0.4 control characterization. It is evidence for the later matched B05-B08 decision and is not, by itself, a disposition of Neural Convergence.

## Run identity

- execution commit: `4346ffb95be634c9695009d21317a2f80e5fccc5`
- workflow: `neural-characterization-legacy-control-b04`
- workflow run: `37674813225`
- profile: `legacy_v04`
- neurons: **4,096**
- seeds: **1842, 1843, 1844, 1845, 1846, 1847**
- causal timeline: **5,120 steps per seed**
- result validation: **6/6 PASS**
- checkpoint restart equivalence: **6/6 exact**
- no failed seed was replaced or rerun

The GitHub Actions artifacts retain each complete schedule, prepared manifest, result JSON, compressed 512 x 4,096 evaluation-state arrays, initial/stabilized/developed checkpoints, and CI summary. Artifact retention at execution was configured for 90 days.

## Immutable artifact ledger

| Seed | GitHub artifact ID | GitHub artifact digest | result.json SHA-256 | internal result artifact SHA-256 | evaluation state SHA-256 |
|---:|---:|---|---|---|---|
| 1842 | 11506201901 | `fdb4ff13306bd20bc85c2416f2f7a487f4a7cf5e0b458dbf45175117c8efbea9` | `a253b6a0e40b426e0f667071d659e028a3afa1167741e638aec002fd2354b67f` | `5a16e6c3a783c4a17ab33cdfce55ad50e07bcd8565ee770601efb8f175d552af` | `8875986763686ce4c535889eff7d4ee0f796fe53b7583c370554b401a4656896` |
| 1843 | 11506381713 | `b9a5497a4b48fa9f0ec035b2f7ffbb353e6caa2df1d5f52b8bf28c85690c1dea` | `d0cdab0be020986b73b1140fac39c78ca613e2c38f5780ae5cb90e55025ef1e5` | `bd99910e825c8fcd6f054857917fda352b984941cfc0316781b7719b862fcb77` | `730e88da1d0251c0c03960f69ac08193d6b115dfbc659669dc9f7ca36955e6d0` |
| 1844 | 11506002377 | `c44f94fe84c778282803acfca1823647dd990eb1d957e9d7515353133ed3ae37` | `ea9ec2ae0c6859bf4013a28bebbd7ee85cb36a0ecbec20cfce57e3efd7fda9fa` | `ebef9c8ae71208c0bc4f8dca91f0a2f5a1ecd0f49335cb5a774242641288f2b4` | `ff98038c64bf004e0a0ef4366a74632d9e3c52b32741a47c0f0982a5ca6c9bee` |
| 1845 | 11506266850 | `8458d3dff89804b42894a2be4897b872ae8c01e8724cdffae8223cdeaac7709d` | `3e5877dfe8a676efbad633f3617a53ba843d2c069f6b6b5236ca719670114434` | `69b87df4bb0a509cb06426700ca19b571e0a12d61c4a58d980e55a0947c06d10` | `872eed3157917dea6f41353cd2d61a9e3ede57aa9b18ca3bc36a44eb8d5942d2` |
| 1846 | 11507440188 | `30e2a33ad9d88211caf2dc3bb9a6b0f99dcdd0040de2990788a0677ff9da4aa9` | `9350406cef1729662a78faea1754aedb95025b0d9d545b2a268f2257122711e9` | `d008b41f3737119f4b038c5f7dc8e38778f51a8f4e330b9eb1976f96e0096b43` | `7ae2c9da2b9a072549b8af21c1fccd84bbbf4f82187353e8cb517e7ee84f6ca9` |
| 1847 | 11507375610 | `97f75f46c1481ab029f716fbfbaa25014b9a2e75256a06bd74f10d8cd39e9dd6` | `8dd2507f4f93abb307e3150b5ce4a82d23db3fa06ffac58aa5d41bcf23b8af66` | `19a6bf895de6608401496c6e099abae51c54b753b47015658bbfc232331256f2` | `5fdbaf9902e59af568a71168525f3d468668d0e0119ef343a53b60deb85d7903` |

## Descriptive control baseline

These values are recorded before the B05 challenger and must not be used alone to promote or reject Neural Convergence.

| Seed | mean expected-action p, pre | mean expected-action p, post | post-pre | mean pre/post JS | post entropy | post top-two margin | post effective dimensionality | context-separation cosine |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1842 | 0.099905 | 0.099225 | -0.000680 | 0.068506 | 0.921166 | 0.024158 | 5.429759 | 0.000001308 |
| 1843 | 0.099851 | 0.131541 | +0.031690 | 0.130536 | 0.807454 | 0.252050 | 6.149295 | 0.000001332 |
| 1844 | 0.100450 | 0.097770 | -0.002680 | 0.043811 | 0.945438 | 0.114040 | 6.500616 | 0.000001295 |
| 1845 | 0.099399 | 0.093455 | -0.005944 | 0.026602 | 0.968410 | 0.010100 | 5.342834 | 0.000001223 |
| 1846 | 0.099378 | 0.097529 | -0.001849 | 0.038274 | 0.960146 | 0.036942 | 5.281920 | 0.000001146 |
| 1847 | 0.100548 | 0.111379 | +0.010831 | 0.069444 | 0.901948 | 0.246682 | 5.520158 | 0.000001371 |

The control baseline is visibly seed-sensitive. Four seeds decreased slightly on mean expected-action probability after development, while two increased, including a larger increase for seed 1843. This is precisely why B02 preregistered matched per-seed comparison rather than a single default-seed demonstration.

The postdevelopment state representations are also highly correlated across probe contexts: mean within- and across-context cosine similarities are both approximately 0.99998, producing context-separation differences around 1e-6. This is a descriptive control observation only. Whether the challenger materially improves representational separation is a B05/B08 question.

## Runtime sanity

All six runs completed with finite outputs and exact checkpoint/restart reproduction. Characterization wall time per seed was approximately 5.64-7.02 seconds on the GitHub-hosted runner, with peak RSS approximately 179-187 MiB. Each developed checkpoint was approximately 1.40 MB and each run retained a compressed 512 x 4,096 float32 evaluation-state artifact.

## Interpretation boundary

B04 establishes the accepted legacy-v0.4 baseline under the frozen B02 protocol. It does **not** establish:

- that Neural Convergence is better or worse;
- that 4,096 units are sufficient;
- that 4,096 units are a capacity ceiling;
- that a favorable or unfavorable aggregate metric is causal evidence;
- that later lesion work may be skipped.

The next permitted runbook step is B05, using the exact same six seeds and frozen schedules with `neural_convergence_v05`.
