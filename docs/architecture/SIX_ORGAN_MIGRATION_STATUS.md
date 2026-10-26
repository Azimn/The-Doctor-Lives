# Pretorius six-organ migration ledger

As of 2026-10-26. Official production `main` remains untouched while this review track is open. The previous main is preserved as `backup/main-before-six-organ-2026-10-26-784cff3`.

| Guide phase | Actual status | Evidence / next required milestone |
|---|---|---|
| D0 baseline | **Baseline and historical Lab A/B executed; incomplete** | Pre-upgrade frozen Doctor SHA and current six-organ code have matching measured real-Laboratory behavior, including first-person memory, action replay and restart. Other frozen fixtures/review remain pending |
| D1 registry and decisions | **Proposed for review** | This registry, topology, 40-row classification and 9 provisional ADRs; do not label official until approved |
| D2 interfaces/writers | **Opt-in adapter implementation and partial tests; incomplete** | Six executable seams in `doctor_lives/organs.py`, contracts in `D2_SIX_ORGAN_RUNTIME_SEAMS.md`, baseline and scenario tests; source-level writer audit done but dynamic single-writer authority proof pending |
| D3 Ipseity | **Not promoted** | Global no-bypass, private cognition and causal admission tests required |
| D4 Mnemosyne | **Endogenous recall pilot wired; not promoted** | Reviewed PR #59 information-need/recall policy is opt-in via the original Mnemosyne/BrainPort. It derives bounded first-person recollection questions from trusted unresolved internal concerns, logs decisions in canonical BrainStore, uses the existing one-use read-only recollection capability, and passes matched no-concern, spoofing, cost and restart tests. Subjective causal effects in downstream decisions, independent holdouts and production admission still pending |
| D5 environment/Corpus port | **Portable virtual-world pilot implemented; incomplete** | Real Laboratory plus a second mutable *simulated* environment can exchange host-controlled context using the same canonical brain and first-person autobiographical store; source-scoped action receipts, retries, and return-to-Lab are tested. Generic host authentication, other game engine drivers, world-time handoff and production qualification remain pending; robotics is deferred |
| D6 Corpus/Affectus/Noesis | **Not calibrated** | Physical feasibility, affect and control tests |
| D7 closed loop | **Host-scheduled heartbeat and mnemonic replay now mapped; full closed loop not qualified** | `NoesisOrgan.pulse` and `MnemosyneOrgan.replay_sleep` delegate to unchanged brain with comparative fixture tests; world action, own goal initiative, Gate 3/5/5A and consequence return unqualified |
| D8 Sensus donor | **Pinned causal-acquisition and epistemic-gap pilot implemented; adoption not qualified** | `sensus_pilot.py` uses the exact donor source checked against approved Git blobs; matched conflicting/uncontested evidence, source restrictions, memory lesion and restart tests execute in dedicated CI. Real multi-sensor Laboratory need, host authentication and global adoption gates remain open |
| D9 learning | **Not characterized** | Mechanism-specific lesion and transfer controls |
| D10 mock robot | **Not implemented** | Fake provider, no actuation or authority leakage |
| D11 production | **Not eligible** | Cold install, CI, reviewer sign-off, migration/rollback and longitudinal suite |

## Promotion rule

No default runtime change and no merge into `main` from this branch until prerequisite review and tests have actually passed. A green documentation/test check alone cannot promote D3-D11. When qualified, integrate small reviewed PRs in dependency order, rerun tests at exact merged heads, and retain the preservation branch permanently. The final main branch must contain the guide, reviewed registry, tested code, status matrix and release evidence. Preserve negative experimental findings.

## New executable evidence (26 October 2026)

- Frozen historical Doctor vs six-organ Laboratory A/B and original baseline regressions: [run 40410091624](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40410091624), **success** at commit `b2830ce971f2409f424b914bd4114d18dd0d4086`.
- Pinned Sensus v0.1 donor conflict-veto, source-control and memory-lesion pilot: [run 40411135117](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40411135117), **success** at commit `8776488050cd27f2340115e3e5e5d933d609c137`.
- Laboratory vs mock-robot provider swap and historical-regression checks: [run 40411569425](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40411569425), **success** at commit `d2cf9e2d4235e89b997b85293f1f48b9d5d8a41f`.
- The latest runtime-seam integration and subsequent refactor have newer heads; verify CI at the final exact head before declaring an overall gate result. All of the above are experimental/restricted outcomes, not production promotion, autonomous action or human-fidelity qualifications.

## Portability priority clarification

The D5 engineering target is **cross-simulation portability**: one Pretorius identity, brain, memory, neural checkpoint and pervasive first-person subject boundary can persist as the authorized host switches among the Laboratory and unrelated simulated worlds. Each world retains its own physical/spatial/item truth and action-receipt authority. No world model or renderer obtains direct permission to rewrite canonical brain evidence. World-specific rooms, clocks and objects do not become privileged knowledge in another world; remembered experiences remain source-qualified. `doctor_lives/virtual_world_port.py` and `tests/test_six_organ_virtual_world_port.py` constitute a small, opt-in functional pilot, *not* a full Frankenstein Village or other-game-world integration. Physical robotic embodiment is an optional long-term adapter, not a prerequisite to organ graduation. The full D5 gate still needs an independently integrated second game/world engine and robust transition-time and trust contracts.

## Mechanism integration progress (26 October 2026)

- PR #59 endogenous recollection policy adapted without a second selector or memory store. `doctor_lives/mnemosyne_pilot.py` and `MnemosyneOrgan.opt_in_endogenous_recollection()` preserve host-scheduled initiation, internal concern selection, one-use state-bound recollection, and versioned engineer audit. [Dedicated CI run 40414110385](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40414110385) **success** on commit `b1dc64f317068231868fab9c132c4aeeac872245`.
- In the existing pinned Sensus pilot, only verified, contradictory OBSERVED inputs from **distinct sources and channels** may generate a provenance-carrying unresolved concern in the ONE canonical BrainStore; the opposed claims remain unadmitted to lived autobiography. `tests/test_six_organ_sensus_pilot.py` now runs a connected Sensus conflict -> selected endogenous Mnemosyne recall vs matched no-conflict control. [Dedicated CI run 40414110355](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40414110355) **success** on the same commit.
- **Not a claim** of autonomous activity, global Synthetic Ipseity no-bypass, verified external multichannel sensor trust, human realism, organ graduation, or full production adoption. No production defaults changed. Next substantive gate: route a selected first-person recollection into authorized private cognition and measured downstream decisions, with explicit holdouts and crash controls.
