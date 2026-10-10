# Eidolon E4-C: Order-invariant decoder and learned-recurrence lesion — executed results

**Date:** October 10, 2026 (US Central). **Status:** research engineering diagnostic. **Source:** [frozen protocol](../../docs/EIDOLON_E4C_BALANCED_DECODER_PROTOCOL_V01.md), committed before the implementation; production Pretorius unchanged and [draft PR #36](https://github.com/Azimn/The-Doctor-Lives/pull/36) unmerged.

## Question

E4-B's Noetic native-motor decoder emitted whichever teacher label appeared last, regardless of input. Could a simultaneous, class-balanced supervised readout end that training-order failure, and if so does the learned Noetic recurrent W contribute something beyond a fixed native reservoir? This is a *method repair*, not a new scientific confirmatory experiment, because the E4-A/B lexical cases and labels were already inspected.

## Implementation, data, and provenance

- [Isolated research module](../../doctor_lives/eidolon_balanced_decoder.py) fits a centered, deterministic 10-output ridge readout against `PretoriusRecurrentSubstrate` rate features; fixed alpha **0.10** and logit scale **4.0**. There are no sequential motor-teacher updates and the production motor weights are untouched.
- [Runner](../../scripts/run_eidolon_e4c.py) and [tests](../../tests/test_eidolon_e4c.py) compare six E4-B seed initializations `151,167,179,191,211,223`, each with 32 familiar training cases, **96 balanced native feature observations (cue plus 3 and 12 input-free ticks)** and 16 held-out actor/episode/template-disjoint cases. Test evaluates all ten native actions at delays 0, 3, and 12.
- **Five recorded arms:** virgin W + batch readout; Noetic-trained W + batch readout; Noetic-trained batch readout on an otherwise identical *virgin recurrent W transplant*; learned W with the original sequential motor decoder; repeated fresh virgin-W batch readout (equivalence check, never counted as an independent arm).
- The runner verified identical W coordinate topology and source weights, no changes to the native motor matrix or any evaluation parameters, and readout invariance across four class-order permutations with no sample-count imbalance.
- [Original unabridged GitHub Actions artifact, ID 11671959635](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38058009283/artifacts/11671959635) contains `e4c_balanced_decoder_assay.json`, **1,440 per-seed/per-case/per-arm/per-delay rows** with all ten action probabilities, as well as all previous E2–E4B assays. ZIP SHA-256: `66eda6f22fd11aa3f8ef0e1d5741893e5f7331de9254ed45d5486141c4e33e44`; inner E4-C JSON SHA-256: `0acb6a585b3e6926b3d8af36c4681a34363caf36bb6a18ee6d60ed60f13ac9aa`. [Permanent measured summary](E4C_BALANCED_DECODER_SUMMARY_V01.json).
- Tested source commit `83c2f6d3ee3823deab578b052995bce996bb9b93`. [Targeted CI 38058009283](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38058009283) passed **77/77** tests; [full brain suite 38058009287](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38058009287) passed **401/401**; fresh-install [38058009359](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38058009359) and causal-audit repeatability [38058009290](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38058009290) completed green.

## Measured results

**Order invariance succeeds at the decoder level.** Refitting all four rotations on the same frozen neural features produced maximum absolute readout-weight difference **2.78 × 10⁻¹⁷**; native motor training had earlier tracked the terminal class with 100% categorical collapse. The new batch readouts predict **all four labeled actions** in the immediate test, not a single terminal teacher label.

| Arm | Immediate top-1 / 96 | Three-tick / 96 | Twelve-tick / 96 | Mean 12-tick target probability |
| --- | ---: | ---: | ---: | ---: |
| Virgin W + balanced decoder | **35** | **29** | **23** | 0.161140701 |
| Noetic learned W + balanced decoder | **31** | **31** | **25** | 0.161140667 |
| Noetic decoder + virgin W transplant | **31** | **33** | **29** | 0.161140692 |
| Previous sequential motor on Noetic W | **24** | **24** | **24** | 0.206838197 |
| Independent repeat fresh batch on virgin W | 35 | 29 | 23 | 0.161140701 |

In-sample (training) categorization was **140/192** for virgin W and **131/192** for Noetic W across the six seeds. This is evidence that the readout can discriminate examples it was supervised on, *not* robust unfamiliar contexts. The four held-out labels are balanced; a constant one-of-four action yields 24/96 = 25% top-1.

**Crucial precision warning:** The balanced decoder's probabilities are often almost tied. Under Noetic W at twelve ticks, median difference between the largest and second-largest action probability is only **0.000245**, and **77/96** cases have a margin below **0.0005**. Replacing learned W caused 0/96 categorical flips immediately, **23/96** at three ticks and **33/96** at twelve ticks, but the maximal probability changes were just **0.000007936**, **0.000159341** and **0.000530421** respectively. Such category flips are primarily a symptom of near-tied logits and should **not** be represented as durable learned dispositions. On the 12-tick primary endpoint, learned W selected the fixture target 25/96, versus **29/96 with the very same fitted decoder on virgin W**.

In addition, the balanced model's twelve-tick mean correct-target probability (~0.16114) and log loss (~1.82548) are **worse** than the prior constant-class motor's ~0.20684 and ~1.57609 in this restricted task. The batch model fixes training-order bias but does not establish superior calibrated confidence or semantic understanding.

## Interpretation

**Decoder order/recency software gate: PASS.** A simultaneous, class-balanced decoder removes the formerly conclusive terminal-teacher dependency on a fixed neural feature representation. Full training, clone isolation, parameter invariants and CI regression are green.

**Held-out robust action selection: NOT ESTABLISHED.** Immediate 31/96 for Noetic balanced is better than the 24/96 constant-choice baseline, but *worse* than 35/96 from virgin-W balanced, and delayed performance declines toward chance. The experiment has no independently adjudicated outcomes or new externally sealed cases.

**Causal learned recurrent necessity: NOT ESTABLISHED.** Learned W is not required for the small correct-target effect; direct virgin-W balanced reaches higher immediate test accuracy and W lesion sometimes improves delayed top-1. The lesion's high categorical flip count is explainable by tiny differences at near-tied action probabilities. No claim of stable learned identity, long-horizon planning or personhood is warranted.

## Next discriminating work

The decoder bottleneck is partially addressed; the emerging problem is **weak separation and temporal stability of native neural representations for goal/action semantics**. Do **not** tune ridge alpha, logit scale or inspect this dataset for improved results and then claim confirmation. Design a *new externally authored, frozen task-outcome suite* with strong no-brain direct-text/lexical retrieval and native-bridge comparators, explicit provenance/actor mismatches and actual environment consequences. Require **margin, calibration and W-lesion-specific improvement**, not merely tiny near-tie categorical flips. Cost/report comparisons must preserve equal input/outcome information budgets.

**Decision:** maintain PR #36 as a draft, production Pretorius untouched. The only clear improvement this stage establishes is order-invariant balanced readout construction.
