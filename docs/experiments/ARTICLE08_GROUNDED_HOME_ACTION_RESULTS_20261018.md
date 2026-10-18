# Grounded household action arbitration — remediation findings

**Date:** October 18, 2026. **Status:** isolated research, stacked on draft Article 8 PR #78. **Preregistered comparator and criteria:** [ARTICLE08_GROUNDED_HOME_ACTION_PREREG_20261018.md](ARTICLE08_GROUNDED_HOME_ACTION_PREREG_20261018.md), committed before the new code and first run. **Laboratory authority pinned:** `6e49795752835d64fa6fd63d16359669a1ca2ba7`.

## What was defective

The preceding pilot mapped an undifferentiated neural `avoid` label directly to `tea` and kept requesting tea after supplies were depleted; its physical world correctly denied the actions. That arbitrary mapping was **not a learned choice** or a plausible personal preference. Trying to tune the 10 generic action weights or relax Laboratory supply limits would have concealed this problem, not solved it.

## Changes

A new opt-in host controller separates **verified affordance eligibility** from **preference**. It uses the same original Laboratory's deterministic `transition` function to simulate each entire real household task, including source-supported route steps, lighting, physical prerequisites, finite materials and compound meal preparation. Only complete, feasible tasks are ranked, using the **existing unchanged** Sims-style bodily scores and, in one arm only, a bounded preference derived from the Doctor's actual recurrent action scores. No raw state reaches the first-person subject. Each successful action goes through `DoctorHomeBridge.act`, survives source verification and enters the actual Doctor's authenticated experiences.

The executor refuses stale physical-world snapshots, unsupported controller identities and tasks whose preflight differs when execution begins. Genuine physical denials are reported honestly; internal authenticity/brain failures **propagate instead of being mislabeled as routine denials**. Movement, consumables, clock, damaged equipment, physical item state and replay still belong to the Laboratory. No new brain or habit ledger is installed.

## Predeclared matched-world pilot

The same physical setup, body station and initial first-person room description per case/seed/controller. Four case families: ordinary morning, **three cups actually consumed**, workbench worn by **two real experiments**, and evening reached via three authenticated four-hour clock advances. Three original neural seeds: 1842/2718/31415. Six selections per run. Three matched arms: original arbitrary neural-label mapping; proposed world-grounded host arbitration with neural preference; and the **equally informed cheap** grounded controller without neural preference.

The first completed [original full-cohort CI run](https://github.com/Azimn/The-Doctor-Lives/actions/runs/39130969724) produced:

| Controller | Completed physical activities /72 | Failed activity attempts /72 | Materially beneficial activities /72 | Tried tea while unavailable |
| --- | ---: | ---: | ---: | ---: |
| Original arbitrary native-action mapping | 15 | 57 | 7 | 24 |
| Grounded world + Doctor bounded neural preference | **72** | **0** | **72** | **0** |
| Cheap world-grounded rule, same world data | **72** | **0** | **72** | **0** |

All source world replays and same-initial-world/first-person frame parity checks passed. The new selector never requested tea without actual supplies, and every proposed complete grounded plan passed pure Laboratory preflight before authentic execution. The researcher's predeclared engineering remediation check passed.

**Interpretation:** the repair solves *impossible command selection* in these known bounded tasks. It does **not** demonstrate extra neural cognition. Candidate and simple rule tied exactly, and the new selector uses engineer-visible physical information and the same deterministic engine as its foresight oracle; successful dry-run-selected execution is expected on an otherwise stationary world. Comparisons against the old arbitrary mapping demonstrate **interface correctness**, not a causal claim of neural emergence or independent autonomy.

The domain covers six familiar household tasks, still not open-ended life, library reading, personal authorship, spontaneous activity, independent social life or subjective enjoyment. No unprompted action schedule has been added. This is a repairable host/subject boundary, not completion of Article 8.

## Scientific and production adjudication

- **Article 8 stays at 10/100**. Independent transfer, causal habituation and subjective Article qualification remain unassessed.
- **Article 7 stays 80/100**, aggregate and all other Articles unchanged.
- No unmerged physical Laboratory upgrades, no Village systems, no main-branch lived memory changes. Draft, opt-in research.
- This controller is **not** a replacement for actual personality, meaningful past choices or real-world persistent content. Its true value is to keep ordinary actions causally possible before letting the Doctor decide whether they are worth doing.

**Next work:** integrate the better physical affordance system with the Laboratory's newer opt-in object-permanence, physically depleted provisions, written-page and reading capabilities; then compare a Doctor-grounded natural-language choice policy against the *same-information* simple controller across unseen diverse situations. Only grant a procedural habit advantage when the Doctor makes and revises preferences using actual experience over time. Prefer welcoming daily life, comfort, curiosities, reading and self-directed projects over repetitive survival pressures.

**Primary evidence:** the original [full outcome artifact](https://github.com/Azimn/The-Doctor-Lives/actions/runs/39130969724/artifacts/12138156957). Additional validation of the later fail-closed integrity patch is a separate CI run, not a changed hypothesis or result.
