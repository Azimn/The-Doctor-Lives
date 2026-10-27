# Spinoza Affectus: reproduced fitness and strictly prospective audit

Date: 2026-10-26/27. **Status: independent research audit, no production adoption.**

## Exact pinned source and reproduction

- Donor: `Azimn/Sensus-Communis-Artificialis` on `affectus-prototype` at commit `904bf11861700739ccc03d4b0d4340ff3422a7d3`.
- Candidate source: `sensus_artificialis/affectus.py`, original tests: `tests/test_affectus.py`, source spec: `docs/AFFECTUS_PROTOTYPE.md`.
- Independent auditor: `tests/test_six_organ_affectus_donor_audit.py`, run by `.github/workflows/six-organ-affectus-donor-audit.yml`.
- Original donor tests: **17/17 pass**. Independent audit tests: **6/6 pass**. Green audit CI is *not* an admission or forecasting-success decision.

Run the audit through the linked GitHub Actions workflow. Equivalent local Python 3.11 commands at the six-organ repository root:

```sh
git clone https://github.com/Azimn/Sensus-Communis-Artificialis.git pinned-affectus-donor
git -C pinned-affectus-donor checkout 904bf11861700739ccc03d4b0d4340ff3422a7d3
PYTHONPATH=pinned-affectus-donor python -m unittest discover -s pinned-affectus-donor/tests -p test_affectus.py -v
PYTHONPATH=pinned-affectus-donor python -m unittest discover -s tests -p test_six_organ_affectus_donor_audit.py -v
```

## Source fidelity and test design

Both batteries use the donor's **unchanged** `AffectusConfig(seed=seed)`: `trajectory_window=8`, `direction_epsilon=0.02`, `felt_quantum=0.25`, `noise_std=0.004`, and every other default parameter. Each tick draws one of the same six driver types (`goal_progress`, `goal_impediment`, `social_feedback`, `novelty`, `monotony`, `prediction_error`) using `Random(seed).choice`, with magnitude `uniform(-1,1)`. The two other possible donor drivers are not in the original fitness battery and are not added to the holdout.

- **Original 40 seeds (0–39):** direction computed from `hist[30:38]`, i.e. `hist[37]-hist[30]` with threshold 0.02; purported next-four-tick outcome `hist[33]-hist[29]`, threshold 0.005. The outcome ends *before* the direction window does: the two share sample times. This cannot test prediction.
- **Initial strictly future holdout 40 seeds (40–79):** one report at each tick `28, 40, 52, 64, 76` of the 86-tick generated trajectory; compare direction token computed from the past eight recorded ticks to `state[t+4]-state[t]`, threshold 0.005. Every outcome is strictly after its predictor. The extended episode and evaluation anchors are a **methodological difference** from the original battery. The two batteries are not a clean sample-only A/B.
- **Donor-time-aligned post-hoc diagnostic:** same source regime, seeds 40–79, predictor endpoint at tick 38 (end of donor `hist[30:38]`), and future label `hist[41]-hist[37]`, ticks 38→42. This isolates the *time-anchor* difference without using a leaked outcome. It is a diagnostic conducted after looking at the initial holdout, not a fresh preregistered holdout.

Only comparisons where both predicted and actual signs are nonzero are counted in the binary agreement denominator. Report these exclusions: neither raw per-observation sample count nor a binomial confidence interval treating correlated dimension/tick scores as independent is justified.

## Actual measured receipts

| Battery | Correct / nonflat | Accuracy | Qualification |
| --- | ---: | ---: | --- |
| Original source overlap, seeds 0–39 | 48/57 | **84.21%** | Reproduced; NOT prospective |
| Strict future, five anchors, seeds 40–79 | 144/294 | **48.98%** | Below >60% threshold |
| Strict future, original endpoint tick 38, seeds 40–79 | 29/61 | **47.54%** | Post-hoc replication of non-predictive result |

Original 84.21% breakdown: valence 17/18, arousal 14/19, security 10/12, fatigue 7/8. These are all *overlapping* comparisons.

Prospective five-anchor per-dimension results, with observed sign coverage out of 200 potential cells per dimension:

| Dimension | Correct / qualified | Accuracy | Excluded neutral sign |
| --- | ---: | ---: | ---: |
| Valence | 54/103 | 52.43% | 97 |
| Arousal | 46/95 | 48.42% | 105 |
| Security | 33/68 | 48.53% | 132 |
| Fatigue | 11/28 | 39.29% | 172 |
| **All** | **144/294** | **48.98%** | **506/800** |

Tick-38 strict-future post-hoc diagnostic by dimension:

| Dimension | Correct / qualified | Accuracy | Excluded of 40 |
| --- | ---: | ---: | ---: |
| Valence | 11/24 | 45.83% | 16 |
| Arousal | 9/21 | 42.86% | 19 |
| Security | 5/11 | 45.45% | 29 |
| Fatigue | 4/5 | 80.00% | 35 |

**Baseline caution:** the *felt quantized* level is often `0.00`; scoring its sign only in cases where the trajectory predictor and actual outcome are both nonzero produces a misleading **3.06%** comparator. A more useful *unquantized actual state-level sign* baseline on the same 294 cases gets **46.94%**, against direction **48.98%**. This is still not a matched, calibrated best predictor, nor necessarily the donor document's claimed 42% method. Do not claim 49% beats a meaningful level baseline on the basis of the 3.06% figure.

## Interpretation and adoption decision

1. The transition tag is a meaningful **retrospective descriptor** of how a state moved. A positive-but-falling `valence:0.25v` is legitimate, and the four-dimensional weather, opponent, habituation, persistence, and attribution boundaries have separate evidence.
2. The original source's reported 84% is genuine **overlap-biased agreement**, not predictive validation. The observed **49% prospective** and **47.5% donor-time-aligned** results fail the donor's `>0.60` revert criterion on these deterministic batteries.
3. None of the broader prospective dimension results supports a qualified narrower predictive claim; the aligned fatigue 4/5 is underpowered. Scores share episodes and evaluation anchors; treat 294 dimensional cells as correlated, not 294 independent trials.
4. These tests establish **no** downstream learning or improvement beyond Pretorius's existing needs baseline, verified injury coupling, or a simple controller. No causal provenance of a felt attribution is upgraded to world fact.

**Decision:** source is reviewed and pinned, but the **predictor claim is blocked** and the donor has **not been adopted** into the six-organ runtime. Before proposing any new predictive criterion or downstream mechanism, preregister its driver regime, horizons, thresholds, coverage, independent-seed split, metrics and baselines. Existing negative results cannot be overwritten by a new metric. No main merge or production-entrypoint change.
