# E4-A: Native Pretorius Recurrent–Decoder Causal Audit

**Experiment:** Eidolon E4-A revision 1, six-seed transfer/distraction construction. **Date:** October 9, 2026 (US Central), October 10 UTC. **Status:** executed, **negative recurrent-causality gate**, not an independently authored semantic benchmark. **Production Pretorius:** untouched, PR #36 draft and unmerged.

## Frozen provenance and protocol integrity

- [Original E4-A protocol](../../docs/EIDOLON_E4_RECURRENT_DECODER_PROTOCOL_V01.md), precommitted before any code at `494372bfb91b6f03480c9f3430d86074c2faf758`.
- First executed E4-A source `6647b50bad8651369714eaa0e83fcaa9dd775725`, [original GitHub Actions run 38025624705](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025624705), **INVALID AS A RECURRENT LEARNING TEST**. Every cue arrived on odd ticks and every multiple-of-four learning step on nonlearning blank ticks; *all six* recurrent weight changes were exactly zero. The decoder did learn. This result is a discovered training-dose/scheduling bug, **not evidence that trained recurrence failed**. Original ZIP [artifact 11659478280](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025624705/artifacts/11659478280); SHA-256 `a3fb01196af0fc1b2278c8d3780fae1de76ea73ad95fa7d0c52c0c4f45eca2f8`. The first run's hybrid/decoder equivalence should never be counted as a scientific null.
- The [preregistered timing amendment](../../docs/EIDOLON_E4_AMENDMENT_01_PLASTICITY_TICKS.md) was committed at `e736af3ced92b52b8d2b468c4a27d8abf284fbe9` before any rerun. It removed only the intertrial blank from *training*, preserving source dataset, actors, labels, seeds, motor updates, reward, config, original test and three cue-free evaluation steps. A hard assertion now fails a trial if trained recurrent weight change is <=1e-9.
- **Corrected source:** `3fc841d9888dedfdfc2f9b7854b89a9ee54f2de9`. [Corrected CI run 38025788297](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025788297) successfully executed **55/55 targeted tests**, including deterministic replay and nonzero recurrent-weight test. [Full brain run 38025788229](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025788229) passed **379/379 tests**; [fresh-install validation 38025788291](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025788291) and [causal-audit repeatability 38025788240](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025788240) both passed.
- Original corrected row-level JSON is `e4_recurrent_decoder_assay.json` in [artifact 11660305032](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025788297/artifacts/11660305032), downloadable ZIP SHA-256 `124c8f81805c2de6a7b435675dc065c8e702afd69196c44695f1b7fba6a5e569`. The ZIP also contains all six earlier Eidolon assays. Its E4 report records **1,344 per-arm, per-seed, direct/delayed rows**, full action-score dictionaries, data/hash audit, and original training norms. Frozen train/test fixture SHA-256 `8c5690e4f067072933d1ab44b39177818ab0d146adba574a9281856519948b35`. Original corrected runner reported 0.897 seconds for the six-seed core experiment, excluding CI setup and other jobs.

## Neural experiment

Six matched native `PretoriusRecurrentSubstrate` initializations: seeds `11,29,47,83,113,127`, 128 units, sensory dim 64, recurrent degree 8. Each seed trained on **32 synthetic supervised cue/goal experiences** repeated five times (160 cue ticks); all arms had the same training examples and target motor supervision. The **16 held-out cases** per seed used actors and episode/location tokens disjoint from training, plus novel action-specific text templates; actor-disjoint does not make the stimulus semantically independent from the researcher's code.

Labels were `create`, `persist`, `cooperate`, `challenge`, four cases per label in each test split. Primary outcome was correct **top-1 among the full ten Pretorius actions** after three no-cue ticks, plus calibrated action probability/log loss. Model training used the native `step`, local Hebbian/reward-modulated synaptic updates when enabled, and `reinforce_action` for the supervised output decoder. The six-seed report evaluated seven arms, including one intentionally redundant same-seed recurrent-transplant alias. That alias is a software equality check and must **not** be double counted as an independent sample.

### Training actually occurred

| Learned parameter group | Observed L2/Frobenius change |
| --- | ---: |
| Hybrid recurrent synapses, across seeds | **1.418710 to 1.439002** |
| Decoder-only recurrent synapses | **0.000000** |
| Hybrid motor decoder weights | about **0.832–0.843** |
| Decoder-only motor decoder weights | about **0.832–0.843** |

Thus the corrected experiment passes a necessary **nonzero recurrent training dose** gate. The training output is not solely an untouched recurrent matrix. However, synaptic change alone is not evidence of useful identity.

## Held-out delayed results

Each distinct arm has 96 held-out, three-tick-delayed cases (16 × 6 seeds). Actions are balanced among four labels; a constant choice of one of those four labels yields 24/96 = 25% accuracy.

| Condition | Correct top-1 / 96 | Mean correct-label probability | Mean correct-label log loss |
| --- | ---: | ---: | ---: |
| **Hybrid: trained recurrent + trained decoder** | **24/96 (25.0%)** | **0.207137277** | 1.592295194 |
| **Decoder-only, frozen recurrent** | **24/96 (25.0%)** | **0.207138242** | 1.592293672 |
| **Hybrid decoder with virgin recurrent matrix** | **24/96 (25.0%)** | **0.207138256** | 1.592293691 |
| Hybrid recurrent with fresh virgin motor decoder | 16/96 (16.7%) | 0.099743653 | 2.305793389 |
| Shuffled-label supervised decoder | 24/96 (25.0%) | 0.207130180 | 1.592251755 |
| Fully virgin recurrent and decoder | 16/96 (16.7%) | 0.099744666 | 2.305783546 |

The zero-shot virgin-decoder arm is not a fully retrained fresh-decoder transfer test. It is a cheap negative calibration control and has an unaligned motor coordinate basis.

**Primary recurrent-training gain over decoder only:** **0/96 additional correct actions**. Mean target probability changes by **-0.000000964** (hybrid relative to decoder only); highest absolute *target probability* change among all 96 delayed cases was only approximately 0.0000191.

**Recurrent lesion:** replacing the entire hybrid learned sparse W with the same-seed virgin W changed **0/96 categorical actions**. Its maximum absolute difference in any of the ten action probabilities across cases was only about **0.00001998**; mean correct-label probability change was approximately -0.000000978 (hybrid minus lesioned). The learned weights did not contribute observable action discrimination on this particular battery.

**Class collapse:** in *every* seed, both hybrid and decoder-only models selected `challenge` for **all sixteen unseen test examples**, independent of the hand-authored goal family. The shuffled-label decoder selected `create` for all sixteen cases in every seed. A constant-label model therefore exactly explains the 25% figure, without any semantic or task-specific generalization. These nulls are more informative than the raw 25% number.

Direct (no delay) and delayed performance were also identical in top-1 counts for all arms. Source provenance, personal autobiography and actual future-task outcomes are not represented by these synthetic labels, so this experiment makes no claim to improve those properties.

## Why these results matter, and what they do not prove

- **Software/plasticity-integrity gate: PASS** after explicit correction. The full neural runner, repeated deterministic seed replay, W transplant, decoder reset and ten-way probability checks are reproducible; complete CI is green.
- **Recurrent learned decision advantage: NOT OBSERVED.** The trained recurrent network's changes did not produce a demonstrable extra correct choice or materially move the readout beyond decoder-only/virgin-recurrent conditions.
- **Action-conditioned semantic generalization: NOT OBSERVED.** All hybrid/frozen-decoder models collapsed to one class for the sixteen heldout text/actor/episode combinations within each seed.
- **A stronger cognitive architecture being impossible: NOT SUPPORTED.** The fixed local plasticity update is not explicitly trained with goal-specific credit at recurrent synapses; generic positive reward on each training cue does not teach the recurrent network which of four mutually exclusive action categories the stimulus signifies. This is a plausible limitation of the present learning objective and supervision allocation, not an argument that recurrence is intrinsically unnecessary.

The next study must not simply increase sample count or learning rate on this already inspected test set. **E4-B should introduce an explicit, source-verified, action-conditional recurrent credit-assignment rule** while retaining strong decoder-only and fixed-reservoir baselines, true class/context counterbalancing and an independently sealed actor/episode-disjoint test authored outside the algorithm design process. It should include a matched **newly trained fresh decoder** (not just virgin weights), trained/virgin recurrent swaps, and realized prospective-task outcomes rather than output-class labels only.

## Governance and disposition

Keep [PR #36](https://github.com/Azimn/The-Doctor-Lives/pull/36) draft. Do not alter canonical Pretorius neural checkpoints, biography, renderer, memory authority or the production policy. Preserve original invalid run and corrected null separately. File the measured negative results in the cross-project Artificial Life Research Journal and do not promote a neural identity claim.
