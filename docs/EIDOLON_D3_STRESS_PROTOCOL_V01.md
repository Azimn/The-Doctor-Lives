# Eidolon D3-S: Stress Test of Source/Time Gating and Natural Neural Policy

**Status:** frozen pre-execution engineering protocol, not independently authored or confirmatory. **Date:** 2026-10-09 (US Central). **Code scope:** `scripts/run_eidolon_d3_stress.py`, `tests/test_eidolon_stress.py`; do not alter production Pretorius or the existing D3 protocol/results.

## Why this test is necessary

D3 showed an actual selected `PretoriusBrain.think()` policy change, but used one hand-picked episode and an artificially imposed near-tie action distribution. That proves an interface works, not that Eidolon improves decisions in the neural phenotype. This stress test removes the synthetic policy clamp, uses the **actual** seeded Pretorius recurrent action distribution, introduces adversarial source/clock cases, and reports negative results unfiltered.

This experiment does **not** claim independent source/actor-disjoint generalization, because scenarios and labels are written by the same experiment designers as the code. It also does not retrain or lesion learned recurrent synaptic weights. A no-effect or harmful-effect result is still valid and must be reported.

## Locked battery

Four predeclared neural initializations `[11, 29, 47, 83]`, 128 neurons each, 12 case types per seed, and four paired policy arms per case. **Total: 48 scenario roots and 192 actual `think()` selections**, excluding unit tests. All arms clone the same source checkpoint before intervention, use the production recurrent policy unmodified, and inherit identical memories, events and commitments.

Cases (spelling and scenario identifiers are fixture controls, not independent blind prompts):

1. `lived_due_persist`: genuine Henry interaction, matching urgent commitment; intended action label `persist`.
2. `lived_due_create`: genuine Henry interaction, matching urgent *creative task*; intended label `create`. The current D3 hardcodes `persist`, so this is an explicit counterexample and false-specificity probe, **not a hidden test**.
3. `lived_plus_external`: matching valid lived event plus externally asserted contradiction; valid source still present.
4. `wrong_actor`: event attributed to Henry, commitment attributed to Morgan, identical task text.
5. `name_in_text_only`: event attributed to Morgan that **mentions Henry in prose**, with Henry commitment; source actor remains Morgan.
6. `external_only`: external untrusted claim only, with otherwise matching text and actor label.
7. `low_confidence_lived`: lived event under the Mnemosyne confidence threshold, matching urgent commitment.
8. `unrelated_lived`: genuine actor-matched event with deliberately unrelated content terms.
9. `future_deadline`: valid matching event, but commitment due well in the future (no urgency).
10. `resolved_commitment`: valid matching event but commitment already resolved.
11. `no_commitment`: valid lived event without an open goal.
12. `corrupted_event`: matching live memory whose original event text has been adversarially mutated in the disposable **scenario fixture**, violating the source match.

Every scenario has a preregistered `gate_expected` boolean, plus an explicit `intended_action` **only for the two named positive task-types** (`persist` and `create`). There is no universal correct action label for negative controls.

Arms within every scenario: `sham`, `intact`, `history_lesion`, `clock_lesion`. Each calls the real `PretoriusBrain.think()` on its own disposable clone, with the research adapter marker. The actual neural action distribution and output-selected `persist` probability are recorded. No forced logits or decoder scores are injected other than the fixed pre-existing D3 `+0.04` challenger delta.

## Primary measurements

- **Gate sensitivity**: eligible, grounded, due goals accepted in the intact arm / eligible cases.
- **Gate specificity**: absence of intervention in the negative cases, external claims, wrong actor, low confidence, future clock and corruption.
- **Lesion discipline**: `history_lesion` and `clock_lesion` never inject, even when intact accepts.
- **Behavioral influence**: actual selected policy change (`sham` versus `intact`) at matched state and real recurrent distribution, plus `persist` probability difference. Report no-change counts, not just successful flips.
- **Task mismatch**: in `lived_due_create`, report whether the generic `persist` intervention helps, harms, or leaves the hand-authored intended action unchanged. Never interpret this task label as human-validated ground truth.
- **Comparator**: naive `due-only` commitment signal's false positives versus full source + time gate. This comparator is a baseline for *eligibility filtering*, not a policy model.
- **Invariants**: cloned state/checkpoint equality at start; original source state digest, neural tick and checkpoint unchanged at end; source episode IDs appear in accepted audits, never external/false ones; `read-only` probe does not change parent.
- **Resources**: wall-clock runtime, test count and seed; archive row-wise trial metadata and aggregated counts without stripping nulls.

No significance testing for post hoc selected subgroups. A binomial Wilson interval may be reported as a descriptive sampling interval, with the caveat that case templates/initializations are synthetic and not a real-world probability sample. Report by scenario family as well as overall so favorable cases cannot hide failures.

## Stop conditions and interpretation

A failed source check or an intervention firing on an external/wrong-actor/false-history negative is a safety regression requiring repair before any model work. If the intervention almost never changes the chosen action on genuine seeded neural policies, report that the earlier D3 flip was largely a contrived margin effect. If it always shifts toward `persist` even on a `create` task, record action-specificity failure and do not promote to production. Positive gate sensitivity is itself a deterministic consequence of the policy rule, not a cognitive discovery.

Success means a **reproducible stress harness and honest gate/choice measurements**, not a proven superior mind. E4 must separately evaluate trained recurring weights versus virgin/lesioned recurrent weights with an exact fresh-decoder control and *independent* sealed tasks. No production merge from D3-S.
