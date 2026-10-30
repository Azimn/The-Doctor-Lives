# M1 integration progress

**Status:** Source integration complete; all 13 applicable PR CI workflows plus the push brain suite passed for source head `03b30b7a595a10e18f659e21cb59a08402f3babd`. This record-only completion commit preserves exactly the tested source files.

**Scope:** Only `integration/m1`. Draft verification PR [#102](https://github.com/Azimn/The-Doctor-Lives/pull/102) is **not approved to merge**. Production `main` verified at `784cff39d58a7fe46bb5e4ffc16e0284e6663c78`. Original Laboratory strictly pinned to `Azimn/Pretorius-Laboratory@6e49795752835d64fa6fd63d16359669a1ca2ba7`.

## Completed integration and validation

- [x] Verify current `main` and absence of pre-existing `integration/m1`; start at #89 `61814d22077b37dc177e2e26a32d6b8bd400deaf`.
- [x] Merge stacked #96 `0a704a634d1c1a3e4cfbff2b2a7abd06ad525d33`.
- [x] Merge stacked #97 `fcbde54f7d681ad110a0e59879ae7c74bc717db5`.
- [x] Merge stacked #98 `f734a1d73b52eeec4c1f00c7e36344c730ce06e1`.
- [x] Source tree contains every #98 file unchanged except added `PROGRESS.md`; no conflict fixes or test modifications required.
- [x] Entire standard brain suite passed: **582 discovered, 410 executed, 172 existing optional-environment skips, zero failures**.
- [x] Actual original pinned-Laboratory bridge and historic-Doctor parity passed: **45 unit tests**, plus external classic-versus-six-organ JSON diff with no differences.
- [x] Pinned real Lab experience-to-action suite passed: **65 tests, zero skips**, broken down as **15 experience/action, 5 Noesis selection, 5 Noesis consequences, 3 autobiographical book choice, 15 authenticated Lab bridge, 18 offline real-time host, 4 wheelhouse integrity**.
- [x] Build and seal offline wheels against immutable Doctor and Lab sources, install in a clean virtual environment and exercise the installed console: **host smoke `result=PASS`**, one verified world action and one lived memory, crash recovery exactly once, second restart does not duplicate.
- [x] Source-backed 17-book real Laboratory fixture: **17/17 complete text books, 17/17 physical shelves, 17/17 authenticated reads, 17 distinct lived memories, zero duplicate read memories, brain and world restart verified**, 2,359 digital segments.
- [x] All **13 applicable pull-request workflows** passed at integration source head; **one additional push brain-tests workflow** passed.
- [x] Paste actual integration CI URLs and measured pass counts below.

## Exact-source CI evidence, 2026-10-30 UTC

The pull-request runs identify `03b30b7a595a10e18f659e21cb59a08402f3babd` as their head. GitHub checked out virtual PR merge `95829363001679348e216acbbe4720036e173be4`. Both commits have **identical tree SHA `60d969f93ce006ef33c267d6618ccc18562b6608`**, so the tested files are byte-identical.

| Gate | GitHub Actions URL | Result |
| --- | --- | --- |
| Complete Doctor brain suite | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989698728 | PASS: 582 discovered, 172 optional skips, zero failures |
| Authenticated original Doctor + pinned Lab | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989698855 | PASS: 45 tests and historical parity diff |
| Physical experience-to-action, real-time host and offline installed host smoke | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989699070 | PASS: 65/65 tests, 0 skips, wheelhouse seal/verify, installed smoke PASS |
| Full-text Laboratory source verification | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989699099 | PASS: 17/17 full-text books, 17/17 verified reads |
| Canonical six-organ Laboratory, D3 and full suite | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989698665 | PASS: both jobs |
| Fresh install and historical migration | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989698995 | PASS: both jobs |
| Six-organ Sensus causal pilot | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989698725 | PASS |
| Mnemosyne causal recall | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989699039 | PASS |
| Spinoza/Affectus audit | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989699014 | PASS |
| Affectus causal ablation | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989699049 | PASS |
| Synthetic Ipseity | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989698861 | PASS |
| Actual local model smoke | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989699211 | PASS |
| Causal audit repeatability | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989699236 | PASS |
| Branch push brain suite | https://github.com/Azimn/The-Doctor-Lives/actions/runs/40989685466 | PASS |

## Remaining unresolved items

**None within this M1 integration and pinned-Lab CI acceptance.** The 172 pre-existing skips in the general suite are optional-environment cases, not suppressed failing tests. Do not interpret these green runs as graduation of unrelated research or production release gates. No changes to `main`, second brain, second BrainStore, alternative Noesis selector, independent planner, paid API dependencies, Calibos, Phantasmagorium or Conclave.
