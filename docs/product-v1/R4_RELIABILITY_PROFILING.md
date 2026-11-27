# R4 reliability profiling and termination

The owner-confirmed 520 additional original receipt target and 3600-second watchdog are unchanged. The profiler is opt-in, diagnostic-only, runs the same installed preview-start command, and does not create cognitive input, goals, world authority or a new history.

## Instrumentation mapping

| Governing phase | Existing boundaries measured |
| --- | --- |
| Cognitive processing | Original PretoriusBrain.ingest/think/memory ranking and recurrent substrate step/action scores |
| Model inference | Actual LocalOllamaRenderer call; zero when original source-only Laboratory renderer is used |
| Physical simulation | Original Laboratory commit, act, offer, and book/world operation boundaries |
| Persistence and evidence | Canonical donor authentication, original world replay/verify, SQLite open/transaction scope, BrainStore digest, neural checkpoint load/save |
| Operator/auditor | Runtime initialization/cold reopen, typed output delivery, native host step, read-only witness and original source audit |

Monotonic perf_counter_ns and process_time_ns measure elapsed and CPU durations. Inner measured spans are subtracted from outer spans to avoid summing overlapping work. Transaction scope is not a pure SQLite engine timing. The output includes raw per-boundary samples streamed per native opportunity, counts, median/p95/max and cumulative costs derivable from samples, world and canonical row counts, and peak RSS when supported. Uninstrumented gaps (imports, pacing, portions of fallback daily life, other operations) must be disclosed rather than mislabeled. Compare matched pristine copies with profiling off/on, exact policy ticks, selected action, score JSON and checkpoint hash; no single pair establishes a reliable overhead distribution. The profiler never supplies qualification evidence.

Opt-in diagnostic invocation on a disposable sealed install:
\`\`\`sh
python tools/run_uncoached_r4_trial.py --install-root /path/to/install --seconds 3600 --capacity-receipts 520 --report /path/to/report.json --profile
\`\`\`
Normal qualification invocation is unchanged. The report preserves the independent source audit separately and includes evidenced stop initiator, error details and raw logs. An actual watchdog stop is only classified when the live operator has reached the monotonic watchdog deadline and the harness initiated termination. A signal alone cannot establish OOM. Unknown cases stay unknown. Source/evidence failure remains a qualification failure.

## Local preliminary measurement, 2026-11-25

Diagnostic control used the sealed original e8f7240 Linux bundle, extracted original donor source and wheels with local Python 3.13, NumPy 2.3.5, SciPy 1.17.0 (not the sealed CI Python 3.12 environment). A single native opportunity from two copies of the same pristine world and brain, instrumented vs uninstrumented, produced four additional receipts in each (17->21) and two identical policy rows in tick, trigger, selected action, base/final scores, neural tick and checkpoint SHA. Wall times 16.587307909s without profiling and 15.448492309s with profiling; this single non-counterbalanced pair is not an overhead estimate. Original-world verification spans: 291 calls, 12.698287713s exclusive, 82.20% of measured wall time. This measured original full-text replay cost is a diagnostic lead, not authorization to skip authentication or change cognition.

Original copied-world replay measurements with original source: BookLibrary.verify 7.100498819s on 196-receipt old-fail snapshot, 7.623953930s on 277-receipt old-pass snapshot, 9.507267993s on 509-receipt capacity snapshot. All five original verifiers completed for each; copied main DB SHA unchanged. These are local single measurements, not full-run CI profiling or evidence that receipt count alone causes the slowdown. No verification optimization is proposed until repeated matched measurements, source integrity analysis and original donor review.
