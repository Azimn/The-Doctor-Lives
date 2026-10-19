# E4-B training-order crossover: decisive decoder recency result

**Executed** 2026-10-10 UTC (2026-10-09 US Central). **Status:** confirmed developer-corpus training-order **mechanism diagnostic**, not independent evidence of cognition. **Production:** unchanged; draft PR #36.

## Provenance

The [protocol](../../docs/EIDOLON_E4B_ORDER_CROSSOVER_PROTOCOL_V01.md) was frozen in commit `f7b291a41bf7265b7c20d636df1f630e5690fb82` before the runner and before seeing the result. [Runner](../../scripts/run_eidolon_e4b_order.py) and [tests](../../tests/test_eidolon_e4b_order.py) use native `PretoriusRecurrentSubstrate` plus the same E4-B Noetic three-factor credit code, unchanged hyperparameters, identical six neural seeds, the exact same 32 training samples ×5 repetitions, and the **same already-inspected** 16 test items per seed. Only the order of four action classes inside each four-example training block changes.

[Tested source commit `f65e2560ae6fef3c9c623a0eb3f052d4d33843e1`](https://github.com/Azimn/The-Doctor-Lives/commit/f65e2560ae6fef3c9c623a0eb3f052d4d33843e1). [Research CI 38028570886](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028570886) passed **69/69 targeted tests**; [full brain suite 38028570852](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028570852) passed **393/393**, plus [fresh-install 38028570868](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028570868) and [causal-audit repeatability 38028570869](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028570869).

[**Original full 1,536-row JSON artifact 11660859443**](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38028570886/artifacts/11660859443) contains both E4-B and the order-crossover JSON plus all prior pilot reports. ZIP SHA-256 `70e03fec83fbe9aab41628cb9eb667c3187740c86c8972703671ce3de20097aa`, inner order JSON SHA-256 `4c8ebdfc726180064a8315cb4f699ec26bca65f14e6d455e95a047785c63aef5`. [Permanent compact archive](E4B_ORDER_MEASURED_SUMMARY_V01.json).

## Prespecified 12-step results

There are six independent seeded weight initializations × four terminal teacher labels × two arms (Noetic W learner, frozen-W motor-only) × sixteen held-out examples × two delays (0 and 12) = **1,536 predictions**. Each arm sees 40 examples of every label, 160 total presentations, on the exact same text. The number of examples of each class and the neural configuration are invariant across four orders; **position** is the only altered training dimension.

| Final class during training | Noetic's output on 96 held-out examples | Decoder-only output on 96 held-out examples | Top-1 matches target, each arm |
| --- | --- | --- | --- |
| `challenge` | **`challenge` on 96/96** | **`challenge` on 96/96** | 24/96 |
| `create` | **`create` on 96/96** | **`create` on 96/96** | 24/96 |
| `persist` | **`persist` on 96/96** | **`persist` on 96/96** | 24/96 |
| `cooperate` | **`cooperate` on 96/96** | **`cooperate` on 96/96** | 24/96 |

This exact outcome holds in **each individual seed**. In all 24 seed×order Noetic combinations and all 24 seed×order frozen-W combinations, the predicted category is the corresponding final supervised training label for **all sixteen test examples**, regardless of the true class. The class difference is causal under this controlled intervention: moving the last label moves the constant output class, while all training content/counts and seed are fixed.

All four Noetic training orders still changed native recurrent W (Frobenius change range **0.22306058–0.22775024**); all decoder-only arms left W unchanged. Noetic changes did **not** create task-specific generalization nor protect against terminal-label dominance. Each distinct class is correct exactly 25% because the held-out corpus has four equally frequent targets, not because 25% proves the model has learned a discriminative classifier.

## Scientific assessment

**Training-order recency effect: POSITIVE MECHANISTIC EVIDENCE.** The training label presented last completely determines the trained model's *categorical response on this developer-authored test* across six seeds, and the effect is preserved with W frozen. That is direct evidence that the current motor decoder/supervision process, rather than a persistent recurrent self representation, explains E4-A/E4-B's collapsed outputs. We do not infer an exact microphysical cause of the decoder dynamics solely from this crossover; the main causally varied dimension was class order.

**Recurrent functional advantage: NOT DEMONSTRATED.** Noetic did not outperform decoder-only and continued to exhibit total response collapse under every order. The observed class tracking is not a validated skill, autobiographical learning or artificial consciousness.

**Next construction stage:** fix the decoder's class-order/recency sensitivity *before* exploring a larger neural architecture. Possible independently gated alternatives: simultaneous balanced multiclass gradient computed from a frozen batch; centered features and a readout with normalized class-specific exposures; validation of class-conditioned separability prior to training the recurrent representation. Run an explicit matched decoder-only baseline and randomized/balanced class-order sequence **on a newly prepared task bank**. Changes to the current already-inspected fixture are engineering interventions, not independent cognitive confirmation.

Retain failed and successful E4-A/E4-B results, versioned control protocols, exact original artifacts and this order-crossover outcome. Do not merge into production Pretorius.
