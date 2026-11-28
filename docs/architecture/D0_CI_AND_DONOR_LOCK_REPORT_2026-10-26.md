# Pretorius six-organ D0 exact-head CI and donor-lock report

Execution date: 2026-10-26. This is an **engineering baseline result**, not a six-organ runtime acceptance or human-realism result.

## Exact tested code

- PR: #89 (draft); source branch: `implementation/pretorius-six-organs-2026-10-26`.
- Tested head SHA: `22e592ef3b54ae5f4acd8ba23106ede2ef7baf60`.
- Immutable pre-migration `main`: `784cff39d58a7fe46bb5e4ffc16e0284e6663c78`.
- Original-main backup: `backup/main-before-six-organ-2026-10-26-784cff3`.
- Regression file: `tests/test_six_organ_migration_baseline.py` (four D0 regression methods).

## Verified GitHub Actions outcomes

| Workflow | Run ID | Conclusion | Evidence |
|---|---:|---|---|
| `brain-tests` | 40398664367 | **success** | `python -m pip install -e .` and `python -m unittest discover -s tests -v` completed successfully on the exact head |
| `gate1-fresh-install-validation` | 40398664410 | **success** | GitHub Actions run conclusion on exact head |
| `causal-audit-repeatability-v05` | 40398664451 | **success** | GitHub Actions run conclusion on exact head |

Links: [brain-tests](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40398664367), [fresh install](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40398664410), [causal audit](https://github.com/Azimn/The-Doctor-Lives/actions/runs/40398664451). Workflow success does not mean optional donors were installed or their skipped tests actually executed. The D0 suite tests the existing production brain and its authority boundaries, not the completed target runtime.

## Donor lock: explicit finding

The inspected `DONORS.lock.json` at frozen `main` lists pinned `calibos_mind`, `pretorius_neural_network`, `agent_pretorius`, and `pretorius_neural_v04`. It **does not** lock current Sensus, Synthetic Ipseity or the Laboratory environment as production organ dependencies. `doctor_lives/ipseity_integration.py` separately requires reviewed Synthetic Ipseity package version `0.9.11`. A donor branch's current head is not a version-pinned installation. Before D3/D5/D8, reconcile the standalone donor source revisions and package hashes, dependency install paths and tests, without importing donor identity or rewriting protected evidence.

## Remaining D0 failures to close

The guide requires frozen representative event/neural/memory/world fixtures, actual default and alternate-renderer trace captures, Laboratory source/epoch and restart controls, donor/branch disposition and independent review. Those are still pending. Passing these three existing CI workflows is useful baseline evidence, not sufficient to mark D0 complete. Keep PR #89 draft and leave `main` on the existing implementation until later D11 qualification.
