# Source memory with consequences in the Laboratory

This opt-in runtime change continues experimental PR #61. It adds a narrow executable book-reading task policy to the existing CASCADE host. It is not a learned planner, an autonomous scheduler, semantic recollection, or full Article qualification. No production or standalone-organ runtime is replaced.

## Mechanism

The world authority is Pretorius-Laboratory at `290ec97727c84728e61f69265949551e4ce911ec`. Its existing embodied access API restricts movement to adjacent stations, observation to nearby objects, and reading to a physically reachable book with installed source text. The experiment uses disposable simulated worlds. It does not modify the user's canonical Laboratory.

`CascadePretoriusPreview.laboratory_read` accepts a trusted host authorization, stable task and book IDs, and a finite action allowance. Moves, looks, opens and reads each consume one unit. The task policy checks active Doctor memories against verified Laboratory sighting receipts, searches the last-seen shelf first, then searches the remaining shelves. It obtains current local evidence before opening a book. An earlier sighting never establishes current location. Real absence can enter Doctor memory and invalidate that search prior on the next task.

The observation adapter admits bounded first-person sightings through the existing Doctor ingress firewall. Exact source receipt hashes remain engineer-side provenance. It stores no second cognitive identity or independent memory database. It does not infer subject awareness from a world offer: host ingestion is an explicit engineering attention selection. This world adapter bypasses Sensus fusion for these already verified local offers, and does not constitute an end-to-end multimodal qualification or a Synthetic Ipseity lived-awareness test.

Each chosen external action is durably reserved before execution, and its actual tool receipt is retained. Action choice does not depend on generated prose. Page delivery is checked against the Laboratory's replay-verified source page digest before being ingested as a tool result. The task's success is source-backed page delivery, not a claim that Pretorius understood or learned the page.

Completed task replay returns the old report without new actions or memory ingestion. Changed requests cannot reuse task IDs. Interrupted actions block new Laboratory tasks and CASCADE foreground/background operations pending manual reconciliation; they do not automatically retry, refund or declare failure-free recovery. A local in-process host is trusted. This is not a network authentication boundary. Multiple independent processes writing the same world are not coordinated by the Doctor host lock; the Laboratory enforces its own individual action transactions and position guards.

## Exploratory comparison

The pilot in `tools/run_cascade_laboratory_pilot.py` constructs three authored cases, placing the same book on each shelf in turn. A real local sighting enters Doctor memory, the host closes, and matched world and Doctor checkpoints are copied. Four arms start at the same center station with four actions available. Lesion removes only the relevant active memory; restoration reactivates it on a separate copy. A simple explicit receipt-ledger controller receives the same original sighting, with no privileged location map. It uses an independently implemented lookup-and-search loop.

| Condition | Source-backed page deliveries |
| --- | --- |
| Doctor memory | 3/3 |
| Relevant memory archived | 1/3 |
| Relevant memory restored | 3/3 |
| Simple receipt ledger | 3/3 |

The lesion still succeeds on shelf 1 because the uninformed search starts there. On shelves 2 and 3 the lesion changes the first physical route and exhausts the budget before delivery. Restoring the memory restores the useful route and delivery. The effect is a causal consequence of persistent information access. The simple controller ties: no unique advantage for the recurrent substrate or CASCADE wrapper has been demonstrated. Retain the simple policy unless more complex machinery earns a measured advantage.

Raw case records, source hashes and verified action outcomes are in `results/cascade/LABORATORY_ACTION_PILOT.json`. These are author-executed exploratory software experiments using a small neural configuration and deterministic governor renderer, not independent held-out evidence. No live LLM is called by the task policy. Host restart is real, but multi-day elapsed time, social interactions, acquired habits, prospective planning, consequence-contingent operating leases and cultural learning have not been tested here.

## Article implications

This closes a narrow implementation gap behind Articles 4 and 22: selective source memory now changes a real permitted action and its task consequence. It adds a tool-action interface relevant to Articles 11, 14 and 19. Source-grounded outcome ingestion and stale-prior revision are useful engineering controls for Articles 20 and 21, but are not demonstrations of an empirical affordance learner or general error learning. Authorization is supplied at invocation; the background worker still performs internal heartbeat cognition only. No autonomous world-action initiation or anticipatory preparation is claimed.

All full-domain Article qualification outcomes remain unchanged. The canonical rubric, historical nulls and prior raw results are preserved. Next discrimination should use independently authored task families, interference and elapsed delays, and equal-information simple controls. Broad all-34 support cannot be inferred from this one task family.

## Reproduction

Install this repository and its existing pinned optional governor dependency. Put the pinned Sensus and Laboratory checkouts on `PYTHONPATH`, or install Laboratory editable. Run `python -m unittest discover -s tests -p 'test_cascade*.py' -v` and `python -m tools.run_cascade_laboratory_pilot --output results/cascade/LOCAL_LABORATORY_ACTION_PILOT.json`. The CASCADE workflow now installs the frozen Laboratory and runs the pilot and all focused regressions on Python 3.11, 3.12 and 3.13. Remote CI status must be read separately from local test results.

Local verification passed 525 full-suite tests with no skips before two additional Laboratory tests were added; the final focused run passed all 41 CASCADE tests with no skips, including those additions. The production entrypoint gate passed. Exact commands, code hashes and result hashes are in `results/cascade/LOCAL_LABORATORY_VERIFICATION.json`; both test transcripts are archived alongside it. These results are local, not a claim about pending remote CI.
