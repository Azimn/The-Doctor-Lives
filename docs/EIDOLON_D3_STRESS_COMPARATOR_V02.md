# Eidolon D3-S v0.2 Amendment: Add the Real Production Policy Baseline

**Status:** preregistered construction-comparator amendment, committed before its runner or results. **Source:** [D3-S v0.1 protocol](EIDOLON_D3_STRESS_PROTOCOL_V01.md) and [executed v0.1 results](../results/eidolon/D3_STRESS_RESULTS_V01.md). Historical v0.1 run/results are immutable.

## Motivation

D3-S v0.1's `sham` and `intact` arms deliberately called `brain.think(bridge_enabled=False)` to isolate the D3 +0.04 rule. However, Pretorius's existing **production state-policy bridge** normally takes autobiographical memory, concerns, relationships, commitments and needs into account. A meaningful product comparison requires showing what that existing bridge does on the same source evidence, not merely how neural-only policy and a generic test intervention compare.

## Locked amendment

Use the **same 4 original seeds, 12 source/actor/time scenarios and untouched original neural policies**. Add one fifth clone per scenario, `production_bridge`, calling the actual `brain.think("eidolon-d3-stress-production-baseline", bridge_enabled=True)` **without any Eidolon monkeypatch**. This yields **240 actual decisions** (48 roots × 5 arms). Every clone is independently copied from the same scenario parent checkpoint, and each source parent stays untouched.

The first four arms remain byte-for-byte equivalent to v0.1: `sham`, `intact`, `history_lesion`, `clock_lesion`. The fifth is an **external baseline** because the bridge is enabled; it is not an additional causal lesion paired with the disabled-bridge arms. Never conflate differences from the bridge with effects from Eidolon.

## Primary post-extension metrics

1. Reproduce v0.1 source-gate results with same seeds: 12/12 valid acceptances, 0/36 invalid acceptances, and unchanged four-arm categorical choices. Differences require investigation.
2. Report `production_bridge` top-ranked action by seed/scenario and whether `create` appears for the four development-authored creative tasks. Report corresponding counts for sham and intact, without claiming fixture labels are an independent scientific ground truth.
3. Report `production_bridge` action change relative to neural-only sham and `intact` relative to production bridge. These are different computations, not randomized interventions with isolated components.
4. Preserve the actual returned selected policy's action distribution and source-memory counts. The default bridge must have its original source and mutation gates, not a shadow shortcut.
5. Preserve full parent state, checkpoint and neural tick across all five clones; do not modify `doctor_lives/cognition.py`, neural weights, memory stores, production code, or historical results.

**Nonclaim:** a production baseline that chooses `create` more often here would make the generic `persist` injection look worse on these chosen examples, but still not establish general effectiveness. A baseline that does not choose `create` does not justify adopting the new controller. This is a fixed development corpus, and we will need truly independent actor/event-disjoint labels and observed outcomes to validate usefulness.

## Stopping rule

No tuning, refitting or changes to the original four-arm D3 intervention are authorized by these results. The comparator is purely for evidence-quality and architectural-go/no-go decisions. No production merge.
