# E4-B Order Crossover: Precommitted Recency/Position Confound Test

**Status:** new causal software/learning diagnostic, not independently authored or generalizable cognitive evaluation. **Committed before code and execution.** Parent: [E4-B Noetic results](../results/eidolon/E4B_NOETIC_RESULTS_V01.md). Same known development corpus (already inspected), unchanged neural/hyperparameter/eligibility and decoder rules.

## Question and predictions

In E4-B, 160 exposures were class-balanced but ordered in repeated `create,persist,cooperate,challenge` quartets. All trained decoders eventually produced constant `challenge`. A competing explanation for seemingly successful training is **motor-decoder recency / last-label contamination**, not failure or success of recurrent symbolic cognition. The falsifiable ordering control is to rotate the four supervised action classes while holding the exact multiset of training items and exposure counts constant.

## Locked experiment

- Seeds `[151,167,179,191,211,223]` (the same as E4-B for exact matched initial weights); same `E4-A::cases()` training/test and same synthetic outcome grants. This **cannot** be described as fresh confirmation because the fixture has been repeatedly inspected.
- Keep native Pretorius 128-unit W, encoder, motor temperature, three-factor eligibility update (`ETA=0.05` etc.), and 5×32=160 training examples per condition.
- **Exactly four rotated quartet orders**:
  - `create,persist,cooperate,challenge` (last `challenge`)
  - `persist,cooperate,challenge,create` (last `create`)
  - `cooperate,challenge,create,persist` (last `persist`)
  - `challenge,create,persist,cooperate` (last `cooperate`)
- Conditions per rotated order: Noetic W + trained motor, and virgin/frozen W + identically supervised motor. Fresh baseline starts from the same seed each time.
- Within each order all eight training items of each class appear in the same relative original order; only the action class ordering inside each quartet changes. No test examples are used in training. Both arms see identical 160 cue/outcome pairs, only recurrent W update eligibility differs.
- Evaluate all 16 training-disjoint held-out items per seed/order/arm at immediately after cue (0) and after 12 blank cue-free ticks (12). 6×4×2×16×2 = **1,536 row-wise observations**. Retain per-seed/order trained W/motor norms, selected class diversity, mean target probabilities and per-action probabilities.
- Primary metric: **fraction of conditions in which the top-ranked action on every held-out item follows the final class of the training order**. Record whether changing the order changes the selected class, and whether W learning changes this behavior beyond decoder-only. Do NOT make a statistical population claim.
- Invalid if equal training counts diverge, recurrent W doesn't change in Noetic, frozen W changes, feature/test leakage occurs, any arm gets target label during inference, nonfinite weights arise, or production state is accessed.
- A class shift tracking the last label in **both** arms strongly supports a decoder training-order/recency mechanism and rejects the idea that the observed single-class response is acquired cognitive identity. A class shift only in Noetic would be an interesting representational effect requiring fresh evaluation; neither result authorizes deployment.
