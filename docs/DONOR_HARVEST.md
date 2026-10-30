# Donor Harvest: Pretorius M5

Status: M5 research integration, on `integration/m5` only. Production `main`, draft PR #102, and all source branches remain untouched. This is a REUSE/ADAPT audit, not authorization to merge every donor or silently add a second cognitive policy.

## Selection contract

One canonical PretoriusBrain/BrainStore, original recurrent Noesis as sole decision authority. A proposed donor contributes, at most, one typed and per-family capped source-linked influence to the existing selector. No donor executes a physical action, writes world state, introduces a second subjective memory store, or imports Calibos identity/persona/memories. The Laboratory and operator-work receipt ledgers are external action authorities, not rival brains.

Disabled is the default: `PRETORIUS_M5_DONORS` is unset. Donor code only participates when an explicit comma-separated set of audited names is requested. Enabled names: `cascade_commitments`, `household_grounded`, and `household_habit`. A verified task advantage over a simple controller with the same admissible facts is necessary before changing the default.

## Candidate inventory and provenance

| Donor source branch and original source | Original test/provenance | M5 candidate/use | Disposition |
| --- | --- | --- | --- |
| CASCADE `cascade_commitments.py` at [commitment branch](https://github.com/Azimn/The-Doctor-Lives/tree/experiment/cascade-persistent-commitments-20261015) | [original 8-case test](https://github.com/Azimn/The-Doctor-Lives/blob/experiment/cascade-persistent-commitments-20261015/tests/test_cascade_commitments.py), [original checkpoint](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38784906337) | Canonical BrainStore open commitment pressure, max +0.03, no dispatcher or private store | **LEAVE OFF** |
| CASCADE `cascade_background.py` | [original scheduling tests](https://github.com/Azimn/The-Doctor-Lives/blob/experiment/cascade-persistent-commitments-20261015/tests/test_cascade_background.py) | Review candidate for wake/lease discipline; no second scheduler introduced | **NOT TRANSPLANTED** |
| CASCADE `cascade_governance.py` | [original conformance tests](https://github.com/Azimn/The-Doctor-Lives/blob/experiment/cascade-persistent-commitments-20261015/tests/test_cascade_preview.py) | Read-only budget/preflight interface candidate | **NOT TRANSPLANTED** |
| Household `home_grounded_actions.py` | [source real-world tests](https://github.com/Azimn/The-Doctor-Lives/blob/experiment/doctor-household-care-20261019/tests/test_home_grounded_actions.py), [measured physical pilot](https://github.com/Azimn/The-Doctor-Lives/actions/runs/39130969724) | Port PURE `physically_available` to `m5_home_feasibility.py`; exclude host chooser/executor | **LEAVE OFF** as extra preference, keep pure preflight available |
| Household `home_habit_trace.py` | [original source replay tests](https://github.com/Azimn/The-Doctor-Lives/blob/experiment/doctor-household-care-20261019/tests/test_home_habit_screen.py) | Adapt into BrainStore-backed, independently receipted candidate-history signal in `m5_donors.py`; never create `habits.sqlite3` | **LEAVE OFF** |
| Household `home_native_practice.py` | [original native practice result](https://github.com/Azimn/The-Doctor-Lives/blob/experiment/doctor-household-care-20261019/docs/experiments/ARTICLE08_NATIVE_PRACTICE_RESULTS_20261018.md) | Prior negative neural-label mapping; useful as regression control, not a new plan | **NOT TRANSPLANTED** |
| Self-reference governor `self_reference_adapter.py` and pinned upstream Synthetic Ipseity | [original A/B evidence](https://github.com/Azimn/The-Doctor-Lives/blob/integration/self-reference-governor-pinned-preview/docs/experiments/SELF_REFERENCE_GOVERNOR_PRETORIUS_AB.md) | Candidate for distinct future Ipseity/renderer milestone, not action selection | **NOT TRANSPLANTED** |

## One-at-a-time decision record, original measured comparisons

These are **historical donor experiments**, not new M5 transplant wins. The new M5 20-seed audit is `scripts/m5_donor_ablation.py`, using original Noesis records, independent CausalAuditHarness BrainStore clones and matched same-information cheap comparisons. It is nonactuating, so any choice changes alone cannot establish better *physical outcomes*. Its raw JSON must be retained with M5 CI; no claimed M5 numeric success is fabricated in advance.

| Attempt order | Source-backed donor on | Same-information simple rule | Intervention / negative result | M5 default |
| --- | --- | --- | --- | --- |
| 1. CASCADE commitments | **3/3** original Laboratory commitments completed | **3/3** completed | Missing authentic memory **0/3**; memory restored **3/3**. Neural superiority not established. | **OFF** |
| 2. Household grounded actions | **72/72** physical activities completed | **72/72** completed | Arbitrary ungated neural mapping only **15/72**. Host physical preflight improves correctness, not neural superiority. | **OFF** |
| 3. Household habit trace | **3/6** held-out cue predictions; three abstentions | **6/6** latest-action predictions in the original skewed study | True native household choices were **21/24** `avoid`; no distinct context-specific habit improvement. These prediction endpoints are not physical success rates. | **OFF** |

For CASCADE: source `docs/experiments/CASCADE_PERSISTENT_COMMITMENT_EVIDENCE.md` on the original branch. Household: source `docs/experiments/ARTICLE08_GROUNDED_HOME_ACTION_RESULTS_20261018.md` and `ARTICLE08_NATIVE_PRACTICE_RESULTS_20261018.md`. The original tests exercise larger experimental hosts and cannot be silently copied as if their obsolete second journals were the canonical BrainStore. The M5 adaptation is separately regression-tested with `tests/test_m5_donors.py`, plus the pinned-Lab full-suite and counterfactual test.

## Why no donor was promoted

This milestone's standard is *incremental attributable superiority*, not just positive engineering cases. CASCADE's simple controller ties, grounded task feasibility is equally good when supplied to a simple controller, and the measured cue habit does worse than the recency predictor. Therefore the three candidates are importable/inspectable but disabled by default. A later independently authored outcome suite might reverse these verdicts, but only with new evidence, not by rescaling a donor bonus or changing the gate.

Important limitations: the 20-seed M5 counterfactual audit reconstructs choice rankings from actual preserved decisions; it does not replay each alternative action into an identically initialized physical world. Full paired donor-on/off source-replayed *outcomes* are a remaining acceptance gate. The original tests remain cited and auditable on their pinned source branches. No claims of an external human response or a newly installed organoid are made.

## M5 exact source-backed 20-seed ablation results

The nonactuating first completed M5 candidate run is [M5 CI 41006397303](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41006397303), at source commit `f956f5d5df3b8c0a5042613db0d11b45d387ac64`. A dedicated CausalAuditHarness-based clone pairs the same original 20 independent Pretorius BrainStores. The resulting 180 originally recorded Noesis decisions were reconstructed, donor modifiers applied counterfactually, and a simple no-neural ranking using the same available familiarity, novelty and history supplied. No world action is executed in this counterfactual stage, so changes of selection cannot be called task success.

| Port, original donor | M5 donor-on vs donor-off selection changes /180 | Donor-off vs simple control disagreements /180 | Donor-on vs simple disagreements /180 | Keep decision |
| --- | ---: | ---: | ---: | --- |
| CASCADE commitment pressure | **0** | 0 | 0 | **OFF** |
| Household physically grounded preflight | **0** | 0 | 0 | **OFF** as action preference; keep source world preflight available |
| Household receipt-linked habit history | **42** | 0 | 42 | **OFF**, unverified outcome benefit |

These data demonstrate a nonzero counterfactual influence for the habit modifier, but no measured advantage over the simple baseline. The sampled M4 operator task set does not include the original physical household task categories, so `household_grounded` has zero influence by design in this experiment. A full 20-seed paired physical-household outcome evaluation remains unresolved. Original donor suites remain in source branches, and M5 includes scoped adapted contract tests; do not describe this as a completed one-for-one original-test transplant.
