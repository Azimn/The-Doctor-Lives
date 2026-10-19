# E4-A protocol amendment 01: failed plasticity scheduling audit

**Logged:** 2026-10-09 America/Chicago / 2026-10-10 UTC. **Applies after:** initial E4-A source commit `6647b50bad8651369714eaa0e83fcaa9dd775725` and [original Actions run 38025624705](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025624705). **Protocol integrity:** this amendment is made *before* executing any revised neural training outcomes; the original code/results are retained in source history and original artifact.

## What invalidated the first E4 neural comparison

The native `PretoriusRecurrentSubstrate.step` changes recurrent weights only when `learn=True` **and** `tick % plasticity_interval == 0`. With `plasticity_interval=4`, the E4-A runner trained a cue at odd ticks (`learn=True`) and a blank intertrial step at even ticks (`learn=False`). Every multiple of four fell on a nonlearning blank. Therefore no recurrent plasticity ever occurred.

All six initial E4 neural models reported exact recurrent Frobenius weight change **0.0**, while motor decoder changes were approximately `0.832–0.843`. Hybrid, decoder-only and hybrid-with-virgin-recurrent conditions were numerically identical. The original held-out delayed top-1 rate was 24/96 (25%) for the decoded arms, and 16/96 for virgin decoder, but these numbers must **not** be treated as evidence against learned recurrence: recurrence was never given a learning opportunity. The unchanged synapse results are a **failed training-dose integrity gate**, not a negative result about neural architecture. Original frozen fixture SHA: `8c5690e4f067072933d1ab44b39177818ab0d146adba574a9281856519948b35`. The original original ZIP artifact is [ID 11659478280](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38025624705/artifacts/11659478280), ZIP SHA-256 `a3fb01196af0fc1b2278c8d3780fae1de76ea73ad95fa7d0c52c0c4f45eca2f8`.

## Prespecified correction

Keep all actors, phrases, test partition, seed list, motor teacher labels, reset rule, 5 repeats, input reward, E4 model arms and no-cue three-step heldout probe unchanged. **Remove the intervening blank step *during training only*.** Each training event occupies one consecutive `step` tick with `learn=True` in the hybrid arm. Plasticity now occurs on ticks 4, 8, ... 160. Decoder-only receives the exact same consecutive cue steps with `learn=False`, same supervised decoder update and same input/reset treatment. Both arms have equal 160 cue exposures and motor update opportunities. Add a hard fail-closed assertion that the hybrid recurrent weight L2 change is strictly greater than an explicit numerical tolerance (e.g. `1e-9`) in every seed, while decoder-only remains zero. A sample must never be counted as E4 recurrent-learning test if this fails.

Do **not** change the held-out task, tune neural learning rates, change plasticity interval, change decoder strength, or select seeds in response to performance. The sole controlled correction is training-tick alignment to make the originally declared experiment executable as intended.

## Attribution and evidence

This fix repairs an implementation error and is not independent confirmation because the test data and first outcome were already inspected. Preserve E4-A invalid first run and label corrected run **E4-A revision 1**. Report the learned recurrent W norm, motor norm, top-1 and probability differences, and exact virgin-recurrence lesion effects by seed and delay. Any differences are still construction findings until an externally sealed task/outcome bank is run. Do not merge or promote to production based on E4-A.
