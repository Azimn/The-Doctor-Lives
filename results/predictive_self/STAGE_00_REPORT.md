# Predictive Self Loop Stage 00: executed mechanics and native shadow witness

**Disposition:** PASS as an isolated mechanics/interface test; **NO CLAIM** of improved persona continuity, active-inference optimality, real-world competence, or identity development.

**Execution identity**

- Source commit: `b7d71ccd03ebf2ab37ce749db0aa87ea1e4cac44`
- GitHub Actions: https://github.com/Azimn/The-Doctor-Lives/actions/runs/38015971437
- Tested suite: `python -m unittest discover -s tests -p 'test_predictive_self_loop.py' -v`
- Outcome: 16/16 targeted tests passed; full repository brain tests and existing fresh-install/causal regressions also passed at that code revision.
- Full permanent result: [STAGE_00_SHADOW_EXECUTED.json](STAGE_00_SHADOW_EXECUTED.json)

## Native Pretorius observation

The genuine PretoriusBrain created a 10-action recurrent baseline, then processed an unfamiliar laboratory apparatus in a temporary state. The shadow loop sealed an action forecast **before** the brain ingested the test observation and chose a native policy. The subsequently stored `policy_decisions` record was checked through a read-only adapter, and the shadow loop scored the action.

| Quantity | Measured result |
| --- | --- |
| Selected native action | `create` |
| Observed type | Stored native `runtime_policy` |
| Prior action log-loss | 2.30258509 nats |
| Scoreable forecasts | 1 |
| Any world-effect verification | No |
| BrainStore mutation by the shadow observer | None |
| Canon/evidence manifest | `c26652e8712dce315e10ef4eabc29b806fdc69026db5b6defea8bc78176188e8` |

Log-loss near `ln(10)` indicates that the new shadow predictor did not gain information beyond the effectively uniform initial recurrent prior in this one case. This one observation is a wiring proof, not a comparative effectiveness experiment.

## Explicitly synthetic/mock-world outcomes

The mechanics suite provided three host-labeled **mock witness** events over three distinct contextual roles, each choosing `cooperate`, to exercise slow update, partner prediction and suggestion generation. An illustrative source-labeled operational independence proxy decreased from 0.75 to 0.60, reaching the v0.1 revision cap. Three forecasts received action log-loss values 0.98861139, 0.74077523 and 0.98861139 nats. The predicted probability that the named partner would visibly cooperate changed from 0.5 before the first episode to 0.6666667 before the second.

These observations are fabricated by the synthetic test on purpose. They do not show Pretorius developing identity in a real scenario, and no lived experiences, canon or relationships were written to the production brain.

## Isolation and integrity

The read-only adapter verified an unchanged BrainStore digest while extracting the source snapshot. The future selected action was obtained from a real policy decision record. The shadow observer's scoring did not change BrainStore after the native action had already been recorded. Synthetic unit tests check no automatic tool execution, no world-result inference from runtime-only policy, no updating of global identity from internal policy alone, multi-context witness gates, duplicate-witness rejection, mismatched forecast rejection, error scoring and exact replay from a content-addressed portable checkpoint.

These tests are mechanics-only. Caller-provided `WORLD_VERIFIED` still requires a real authenticated witness adapter to be genuinely trustworthy. SHA-256 protects replay integrity, not cryptographic authenticity. Context labels and action indicators remain researcher-supplied, which limits scientific interpretation.

## Gate assessment

**Stage 00 PASS:** technical feasibility and read-only isolation demonstrated.

**Stage 01 BLOCKED:** no independently verified, chronological world-outcome corpus or sealed context/role annotations was supplied, and the single observed native action cannot establish calibration or forecast benefit. Do not optimize a semantic prior against this inspected demonstration and then claim a confirmatory result.

Next: independently collect real world-action/outcome witnesses and relationship confirmations, freeze source/episode/context splits, and compare the PSL against equal-information recurrent, contextual frequency, semantic-only, episode-only and shuffled-context controls. Keep renderer/model swaps as a separate experimental variable. The implementation remains opt-in research on a draft PR.
