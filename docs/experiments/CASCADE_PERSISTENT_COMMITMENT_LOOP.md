# CASCADE persistent commitment to Laboratory action: engineering milestone

Status: experimental, unmerged; branch based on PR #61 commit 29adbf6.
This is not a qualification result for any of the 34 Articles.

## Mechanism and authority

An authenticated host accepts a bounded intent for a specific book and Laboratory
world epoch via `CascadePretoriusPreview.accept_laboratory_commitment(port,
task_id=..., book_id=..., expires_ms=..., max_actions=4, authorized=True)`.
Acceptance writes a durable operational binding and calls the **existing**
`PretoriusBrain.add_commitment`. The Doctor remains the source of truth for
whether a commitment exists and whether it has been kept.

A later host-scheduled wake invokes
`CascadePretoriusPreview.service_laboratory_commitment(port, task_id=...,
now_ms=..., authorized=True)`. Without a source-verified, active Doctor
sighting memory, it reports `waiting_prerequisite` and takes zero actions.
Unrelated Doctor cognition does not erase the task. The host and commitment
store may be closed and reopened between these steps.

When the prerequisite is witnessed, the dispatcher durably reserves one attempt
and calls PR #61's unchanged `laboratory_read` controller, retaining the same
four-action budget and real source delivery checks. The outcome is verified
against a live Doctor memory whose source matches the authenticated Laboratory
read hash. Only then does the Doctor's existing
`resolve_commitment(..., kept=True)` run. Subsequent wakes return the same
receipt without a second action.

Authorization at acceptance limits the task to one world, expiry, book and
attempt. Dispatch requires a separate trusted host wake authorization. This
is a scheduled host-driven agent, not an always-on service and not authority
for arbitrary external actions. No language model invents the plan, and there
is no newly learned planning algorithm.

## Safety and limitations

State transitions that span two SQLite databases and the external Laboratory
are not globally atomic. Incomplete action receipts block automatic recovery.
If a crash happens between the Laboratory's completed action and commitment
finalization, the same immutable task ID can replay the **completed** action
receipt and verify it without moving again. If the external outcome is
uncertain, manual reconciliation is required. No blind retry, quota refill
or implicit release of the Doctor goal is allowed. Expired authority does not
delete the underlying intention. A failed bounded search leaves the Doctor
commitment open and the operational binding in `needs_review`.

The prerequisite is an authentic *observed* local sighting, not a global
world-state scan; host or environment must supply an actual observation. The
dispatcher is a small explicit scheduler. This is narrower than autonomous
planning over changing prerequisites and multiple tools.

## Evidence gates

First gate: a task is accepted, persists through a real host restart,
remains pending after an unrelated heartbeat, requires an authentic sighting,
acts under finite authority, verifies delivered evidence, and resolves once.

Second gate: lesion the single relevant lived memory after admission. In the
same world the task should remain pending. Restoration should recover the
previous route. Both interventions must preserve other state and prior
receipts. Repeat for other books and different prerequisites.

Third gate: an equally informed receipt-ledger controller gets the same
observation and allowance. Report ties as ties, including differences in
reliability, latency and actual actions. Independent authors must construct
held-out tasks, interruptions, delays and negative controls before a
generalization claim. Test real elapsed time and an actual scheduler separately.

Fourth gate: introduce multiple Doctor commitments with a shared
authorization budget, predeclared priority rule, uncertainty-dependent
verification, and external outcomes affecting future selections. Only after
this is stable add partner-specific belief histories, learned habits and
empirical tool reliability.

Article 17 (goal structure), 18 (prospection), 19 (agency), 4 (memory
artificiality), and 22 (internal causality) receive **engineering evidence**
from this work, not supported full-domain outcomes. The other Article
outcomes and the revised manuscript's support criteria remain unchanged.
