# Pretorius v0.4 causal gate record

This record binds the current v0.4 implementation, regression evidence, causal artifact, and reviewer-requested retrieval-boundary corrections without replacing earlier null or failed results.

Implementation and audit-input SHA: `74b63e2690599d43ea3bc473297cfb2dc0afeb25`

Regression and causal gates on that implementation:
- brain-tests push run 37333399273: success
- brain-tests pull_request run 37333408945: success
- causal-architecture-audit-v04 run 37333399771: success

Causal artifact:
- artifact id 11354664182
- name `causal-architecture-audit-v04-74b63e2690599d43ea3bc473297cfb2dc0afeb25-37333399771`
- digest `sha256:ecbf47644523d866be9894645d77919f51a645489a4d6d089724a9122f1604d7`
- durable audit-result commit: `ae3f0e98a80f2f2f375a41ee76f8139b70d0b2be`

Reviewer correction evidence:
- The retrieval operation now produces two explicit views from one operation: a direct pre-spreading retrieval set and a post-spreading retrieval set.
- History pressure can consume only the direct pre-spreading retrieval set supplied by that same policy retrieval. The bridge no longer scans the entire autobiographical store.
- Every history pressure source is checked at runtime to be a subset of the audited direct policy retrieval IDs. The policy decision also stores `history_retrieval_ids` for this binding.
- A held-out stress test creates more query-relevant autobiographical records than the 48-record policy retrieval limit and verifies that non-retrieved records cannot become history pressure sources.
- Causal traces now capture `policy_retrieval` immediately after `think()` and before rendering, then capture `renderer_retrieval` separately. The backwards-compatible `retrieval` field aliases the policy retrieval.
- The harness fails closed if policy `history_retrieval_ids` differ from the audited direct retrieval IDs or if any history source lies outside that retrieval.
- Spreading activation remains structurally excluded from history pressure. The graph-active matched lesion still exercises 15 activated memories intact versus 0 lesioned while policy divergence remains exactly L1 `0.0`.
- Deep-history remains causally load-bearing at action-score L1 `0.0853657019720969` under the autobiographical-only lesion.
- Deep-history lesioning remains restricted to preawakening autobiography and preserves provenance-bearing design material.
- Cross-version experiment fingerprinting and explicit `comparable: false` legacy rows remain in force.
- Integrated neutral-history `think()` control remains green.

The earlier deep-history null, prior over-broad lesion, failed activation fixtures, retrieval-boundary counterexample, and intermediate workflow push conflicts remain preserved in repository and workflow history. They are not rewritten as passes.

The workflow-authored durable audit commit may receive a PR `action_required` check because it is created by GitHub Actions. That infrastructure state is not used as scientific evidence. Exact-head regression after this gate-record commit is the final pre-review check.

Independent re-review remains required before v0.4 approval.
