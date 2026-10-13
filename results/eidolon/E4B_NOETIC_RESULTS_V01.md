# Eidolon E4-B: Noetic Crucible action-conditional recurrent learning — Executed v0.1

**Date:** 2026-10-10 UTC / 2026-10-09 America/Chicago. **Status:** development-only experiment; software PASS, useful learned recurrent representation **NOT DEMONSTRATED**, production BLOCKED. **PR:** [#36](https://github.com/Azimn/The-Doctor-Lives/pull/36), draft.

## Source protocol and implementation lineage

The [E4-B protocol](../../docs/EIDOLON_E4B_EXPERIMENT_V01.md) was committed before implementation at `250ee1e1c0e03b8db6590bba3da3f89bf5d44f48`. Code: [native sparse W three-factor learner](../../doctor_lives/eidolon_noetic.py), [full eight-arm runner](../../scripts/run_eidolon_e4b.py), [nine regression/control tests](../../tests/test_eidolon_e4b.py). Training used native 128-neuron `PretoriusRecurrentSubstrate` with *fixed architecture-native action populations* as the feedback map. `step(...,learn=False)` disabled generic Hebbian plasticity in all conditions; the research code explicitly added an action-conditional error/eligibility update on same-seed native sparse W, and delivered matched motor teacher updates.

An **initial software run** [38028137823](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028137823) passed the unit-test step but failed at standalone report generation because running `python scripts/run_eidolon_e4b.py` did not expose the repository-root `scripts` namespace. This was a CLI packaging/import failure, not a biological or experimental null. The [one-line-path selection fix](https://github.com/Azimn/The-Doctor-Lives/commit/f83492612a73427249b20c9302099f69dde725e9) allows both module imports and standalone execution; the protocol and experimental code/parameters were not retuned.

The **successful executed source revision** is `f83492612a73427249b20c9302099f69dde725e9`. [Dedicated workflow 38028252618](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028252618) passed **64/64 targeted tests** and produced the eight-assay ZIP, [artifact 11660768811](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028252618/artifacts/11660768811). [Full brain suite 38028252630](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028252630) passed **388/388 tests**; fresh install [38028252629](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028252629) and causal repeatability [38028252638](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028252638) both passed.

**Raw data:** `e4b_noetic_assay.json` in the [original artifact](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028252618/artifacts/11660768811), alongside every earlier E2–E4 assay. Unabridged row-wise E4-B JSON contains **2,304 rows** (6 seeds × 8 arms × 16 held-out scenarios × 3 delays) and exact ten-action distributions. Original ZIP SHA-256 `2d7fea72424317053861903e7a07b87ab1fc603c211260ca303780ed382f85d7`; inner E4-B JSON SHA-256 `c79fa9c8812aae63374f7dcbe06d345e27a61b5fef2b3e1b45946444d742f2a5`. Permanent compact summary: [E4B_NOETIC_MEASURED_SUMMARY_V01.json](E4B_NOETIC_MEASURED_SUMMARY_V01.json). Fixture hash `8c5690e4f067072933d1ab44b39177818ab0d146adba574a9281856519948b35` **matches the previously inspected E4-A corpus**: do not call these held-out results independent.

## Dataset and isolation

Seeds `151, 167, 179, 191, 211, 223`, 32 development-authored training items × 5 repetitions = **160 cue/outcome presentations per seed**. Sixteen previously seen-by-the-experimenter but training-disjoint actor/episode/template items were used for evaluation. Target classes were `create`, `persist`, `cooperate`, `challenge`, four per class. Evaluated at 0, 3 and 12 cue-free steps.

All conditions used the same native encoder, fixed seed-specific neuronal population assignments, ten-action output layer, input budget, and training example count. The active Noetic learner receives a **synthetic source/outcome grant** whose actor, text hash, event identifier, evidence class and intended action must match; rejected synthetic claims produce no recurrent or motor changes. This is an explicit *fixture gate*, not cryptographically authenticated `MnemosyneLoom` or an authorized Pretorius lived event.

The test compared the trained native recurrent/motor pair, a frozen recurrent decoder-only learner, trained motor with recurrent W replaced by same-seed virgin W, trained W with virgin motor, trained W with a newly trained fresh motor, virgin W with an equally retrained fresh motor, shuffled-supervisor recurrent learner, and fully virgin model.

## Actual outcomes

Every separately trained Noetic model learned nonzero recurrent synaptic differences (six W norm changes: **0.223089–0.227696**). Frozen-recurrent decoder-only changes were **exactly zero**. Each accepted 160 supervised synthetic outcomes; fresh trained decoders separately received 160 cue/motor updates. All W/motor swaps retained the original same-seed coordinate system.

| Arm | 12-tick top-1 | Mean target probability | Mean target log loss |
| --- | ---: | ---: | ---: |
| **Noetic hybrid**, learned W and motor | **24/96** | 0.206838197 | 1.576088459 |
| **Decoder-only** (virgin W) | **24/96** | 0.206847136 | 1.576046767 |
| **Noetic with virgin W transplant** | **24/96** | 0.206847138 | 1.576046775 |
| **Noetic with new, retrained motor** | **24/96** | 0.206838332 | 1.576087809 |
| Virgin W with equally new, retrained motor | **24/96** | 0.206847136 | 1.576046767 |
| Noetic with untrained virgin motor | 8/96 | 0.099448560 | 2.308621344 |
| Shuffled-label Noetic | 24/96 | 0.206840947 | 1.576102237 |
| Fully virgin W and motor | 8/96 | 0.099447754 | 2.308626236 |

The learned Noetic hybrid, decoder-only, lesioned Noetic, and both newly trained motor conditions each selected `challenge` **in every one of the 96 held-out items**, across all six neural initializations. The shuffled-target model selected `create` on all 96, and likewise achieved 25% on this balanced four-class benchmark. This confirms output-class collapse despite round-robin class exposure.

**Primary 12-tick contrasts:** Hybrid vs decoder-only: **0/96 additional correct**, mean target probability difference **−0.00000893946**. Hybrid vs same-seed virgin W lesion: **0/96 action flips**, maximum absolute difference across all ten action probabilities **0.000277879**. Hybrid vs fully retrained new decoder with its own learned W: **0/96 action flips**, maximum probability difference **0.000000625**. Noetic with its new trained motor did not outperform virgin-W with an equally retrained motor on any categorical decisions.

Zero-cue-delay and 3-tick assays also showed **24/96** target matches in every trained motor arm; no categorical retention advantage emerged at any measured delay.

**Interpretation:** this test does NOT establish beneficial learned recurrent representations. A class-conditional three-factor *matrix update* now exists, but the learned synaptic changes fail the E4 causal-necessity and behavioral-value requirements. The numerical effects of W are measurable after 12 ticks but tiny compared with the motor decoder's deterministic class bias. An untrained, randomly oriented motor's lower 8/96 score is not evidence for learned recurrence.

## Important residual confound and next discriminating test

Although E4-B interleaved the classes within each set of four training exposures, it always used `create,persist,cooperate,challenge` and therefore **`challenge` still appeared last in every quartet and at the final training step**. Thus final-label/motor-decoder recency remains a plausible explanation for constant-`challenge` readout. The fixed class balancing in counts is not the same as **position counterbalancing**.

The next useful cheap causal experiment is a **counterbalanced training-order lesion**: keep the same model, grants, neural and motor learning doses, but permute class order so each class is final for an equal number of conditions. Measure whether categorical collapse tracks the final class. That tests a confound; it is not independent semantic validation. It must be documented in a separate protocol before execution and must not be described as rescuing this now-inspected benchmark.

Beyond that, E4-C needs independently authored, source-verified interactive tasks and an architecture in which action-conditioned feedback can actually reshape recurrent representations, assessed through downstream outcomes, not only lexical action labels. Repeating E4-A/E4-B's already inspected task bank cannot provide generalization evidence.

## Decision and protection

**Software/source-fixture gate: PASS. Recurrent synaptic update: PASS. Held-out learned recurrent necessity: FAIL to demonstrate. Task-specific cognition: FAIL to demonstrate. External validity: NOT TESTED.**

No production brain, checkpoint, memory authority, UPPB Subject Frame, policy or persistent player data was changed. Keep research PR #36 draft and unmerged; preserve the negative data and original first CI failure transparently.
