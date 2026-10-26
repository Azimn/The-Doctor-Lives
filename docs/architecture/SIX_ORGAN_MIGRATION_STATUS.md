# Pretorius six-organ migration ledger

As of 2026-10-26. Official production `main` remains untouched while this review track is open. The previous main is preserved as `backup/main-before-six-organ-2026-10-26-784cff3`.

| Guide phase | Actual status | Evidence / next required milestone |
|---|---|---|
| D0 baseline | **Started, blocked** | Exact refs, backup, defaults and CI definition recorded in `BASELINE_2026-10-26.md`; test run/fixtures/review still missing |
| D1 registry and decisions | **Proposed for review** | This registry, topology, 40-row classification and 9 provisional ADRs; do not label official until approved |
| D2 interfaces/writers | **Opt-in adapter implementation and partial tests; incomplete** | Six executable seams in `doctor_lives/organs.py`, contracts in `D2_SIX_ORGAN_RUNTIME_SEAMS.md`, baseline and scenario tests; source-level writer audit done but dynamic single-writer authority proof pending |
| D3 Ipseity | **Not promoted** | Global no-bypass, private cognition and causal admission tests required |
| D4 Mnemosyne | **Not promoted** | Acquisition, recollection and protected-truth separation tests required |
| D5 environment/Corpus port | **Not implemented** | Lab parity + mock alternate provider contract and identity continuity |
| D6 Corpus/Affectus/Noesis | **Not calibrated** | Physical feasibility, affect and control tests |
| D7 closed loop | **Not qualified** | Gate 3/5/5A integration and independent initiative controls |
| D8 Sensus donor | **Not adopted** | Optional conditional comparator and source-boundary tests |
| D9 learning | **Not characterized** | Mechanism-specific lesion and transfer controls |
| D10 mock robot | **Not implemented** | Fake provider, no actuation or authority leakage |
| D11 production | **Not eligible** | Cold install, CI, reviewer sign-off, migration/rollback and longitudinal suite |

## Promotion rule

No default runtime change and no merge into `main` from this branch until prerequisite review and tests have actually passed. A green documentation/test check alone cannot promote D3-D11. When qualified, integrate small reviewed PRs in dependency order, rerun tests at exact merged heads, and retain the preservation branch permanently. The final main branch must contain the guide, reviewed registry, tested code, status matrix and release evidence. Preserve negative experimental findings.
