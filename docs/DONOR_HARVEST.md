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

## Latest corrected semantic-policy matched harvest

The later [M5 post-null source run 41007830836](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41007830836), exact candidate `c1efde65474eb4e3518607f2e2cffd92cab19f4c`, preserves all 180 real original-Noesis decision receipts across 20 seeds. The bounded original-native contrast is now a measurable selector input, and 14 of 180 donor-OFF choices disagree with the simple same-information policy. This **does not** establish superiority: different choices need independent world outcomes.

| Candidate | On versus OFF changes, 180 | On versus simple baseline disagreements, 180 | Donor default |
| --- | ---: | ---: | --- |
| CASCADE commitment | **0** | **14** | **OFF** |
| Household grounded action preflight | **0** | **14** | **OFF** |
| Household source-backed habit | **41** | **55** | **OFF** |

The equal-information simple baseline disagrees with donor-off on 14/180 across all rows. The habit's additional 41 changes are trace-dependent, but their usefulness is not known. Source-world on/off outcome studies remain an unfulfilled criterion; no donor has earned a default promotion. These newer numbers supersede the *behavioral observations* of the preceding M5 audit, while the older original historical study and exact run numbers remain archived as real prior observations.

## Latest combined-branch ChatGPT stand-in and semantic-before-donor result, October 30, 2026

The six ChatGPT-authored hypothetical proposal fixture was committed at [`878fbae`](https://github.com/Azimn/The-Doctor-Lives/commit/878fbae9c60b4d41c93e531e825f1efc589949a1) before the semantic lexicon refinement. Original pinned Laboratory, one BrainStore, original Noesis choice, an authorized operator task receipt, one lived memory, and cold-restart nonduplication were actually executed. The initial ten new semantic probes mapped **7/10** as intended. Fix [`b92ac12`](https://github.com/Azimn/The-Doctor-Lives/commit/b92ac12ab7894041d91957e60c4eb787ca3ff978) reached **10/10**, preserving original preregistered 88/90 category accuracy and 58/60 paraphrase agreement. This is a transparent narrow vocabulary improvement, not a new trained neural policy or proof of held-out model generalization.

The following donor harvest was rerun on *that exact combined code*, not the old isolated M5 branch. [Source-backed M5 workflow 41069141705](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141705) preserved all 180 original Noesis policy decisions from 20 initial seeds, then applied donors separately in CausalAuditHarness clones without actuating different world outcomes. CASCADE commitment bonus changed **0/180** choices, household feasibility bonus changed **0/180**, and receipt-linked habit changed **60/180**. Without donors, the original Noesis choice differed from the equal-information non-neural ranking in **87/180** decisions. Habit-ON differed from that same simple ranking in **145/180**. Since **none** establishes superior authenticated real-world results, **leave every donor OFF**. Earlier 41/180 counts were source observations from the previous semantic mapping and cannot be confused with this newer cohort. No shadow habit database, new scheduler, extra organ or alternate policy authority was introduced.


## M6 measured donor call coverage, 2026-10-30

The source-backed [M6 pinned-Laboratory test 41075126006](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41075126006) instrumented *every original Noesis proposal decision* in an 18-opportunity selected original-world trial, separately from M5's 20-seed nonactuating donor score counterfactual. Each donor audit traces whether the module's code path **entered**, whether the source-world candidate was **eligible**, and its exact bounded **score contribution**.

**CASCADE commitment:** 18 of 18 decision contexts entered its code path, zero eligible due to no matching canonical commitment, zero nonzero score. A targeted same-brain real commitment produced +0.03. Routine zero is not evidence of no possible effect.

**Household preflight:** 0 of 18 entered its household-specific path because that M4 operator task set had no household candidates. The historical **0/180** therefore was *never actually testing* its physical household feasibility. A targeted original-Lab `clean` activity passed the pure world feasibility preflight. This is a veto with 0.0 preference bonus; not a failed selector donor.

**Household habit:** 18/18 entered, 16/18 eligible and nonzero in the original observed operator task opportunities. Targeted repeated authenticated journal receipts yielded +0.03; no alternative world outcome was replayed. More choices changing does not imply improvement.

**Disposition:** All three donors remain disabled in the actual shipping conversation and original Noesis. The targeted tests demonstrate wiring and source preconditions, not physical-world superiority. Later M6 CI must remain green.

