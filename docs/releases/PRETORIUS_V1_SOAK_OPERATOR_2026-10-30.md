# Pretorius 1.0 offline elapsed-time soak operator procedure

Status: **candidate instrumentation only**. No 24-hour qualification is claimed by the presence of this command, by a short CI smoke, or by a self-reported JSONL record. The independent reviewer must inspect the original Laboratory and canonical BrainStore receipts.

## Preconditions

Use the exact reviewed Doctor candidate, the pinned original Laboratory at `6e49795752835d64fa6fd63d16359669a1ca2ba7`, an existing single Doctor BrainStore/neural checkpoint, and an existing authoritative Laboratory SQLite world. Install the sealed offline wheelhouse before disconnecting from the network. Stop other Doctor and Laboratory writers. Do not use cloud credentials, hosted APIs, or a separate planner. Do not delete the persistent sidecar lock files.

## Start a real 24-hour run

From the offline virtual environment:

```text
doctor-lives --state ./doctor-state lab-soak --world ./laboratory.sqlite3 --evidence-log ./pretorius-soak.jsonl --seconds 86400 --segment-seconds 900 --interval-seconds 30
```

The command holds the **same two cooperative host locks** for the entire run. It calls the existing single-brain Laboratory runtime in real-elapsed segments, with original-world LOOKs and canonical neural pulses. No physical work is invented. At a genuine bench, optional `--work-every-seconds 300` offers physical work, but original Noesis alone chooses among eligible actions. It cannot navigate Pretorius to a workbench or invent a goal. Book activity, self-originated goals and sleep/wake must be evidenced separately, not inferred from this log.

Place the engineering JSONL file in an ordinary external directory, never at the Laboratory SQLite path, its `-wal`, `-shm`, `-journal`, master-journal or persistent `.laboratory-host.lock` sidecars. The companion evidence `.lock` file must also avoid these names. Hardlinks to original world, world sidecars or canonical BrainStore files are refused. The host validates these paths before opening either authority; a refused location must not cause a LOOK, physical action or lived memory. Keep the evidence file and its lock separate from both the original world and canonical mind.

Each completed segment appends one fsynced, hash-chained engineering record containing UTC start/end, monotonic active seconds measured by the existing runtime, original-world epoch, pulse count, authenticated work IDs and receipt counts. The log never contains first-person text, hidden neural scores or an alternate autobiography. Swatch @beats remain in the ordinary Laboratory host report; UTC remains authoritative for ordering.

## Verify and recover

```text
doctor-lives --state ./doctor-state lab-soak-verify --evidence-log ./pretorius-soak.jsonl
```

A successful verifier reports `active_seconds`, `wall_span_seconds`, `largest_gap_seconds`, `continuous` and `qualified_24h_candidate`. The last flag can become true only after at least 86,400 measured active seconds, at least 86,400 UTC span seconds, no interrupted segments and no inter-segment gap greater than 60 seconds. It is **not independent release acceptance**.

If stopped gracefully, the last segment is marked interrupted and the record remains visible. A later invocation refuses to promote that interrupted log to a continuous 24-hour run. Start a **new evidence file** for a new qualification attempt. A process crash mid-append may leave a torn final record; the verifier fails closed. Preserve the failed file for negative evidence rather than rewriting history. Backup/restore must use the existing canonical `lab-backup` and `lab-restore` commands, not the evidence log.

If a completed segment log is restarted within the 60-second continuity window, the same command can continue toward the original target without counting downtime as active time. A larger gap is denied. Original-world epoch mismatch, duplicate work IDs, reversed timestamps and a broken record chain are denied. A privileged writer can recompute the hash chain, so this is **accidental-tamper detection**, not a signed attestation or protection from a malicious host.

## Independent release evidence

Pin the Doctor commit, Laboratory commit, sealed wheelhouse digest, operating system, exact start/end UTC, full log, raw original-world receipts, canonical BrainStore lived memory/policy records, checkpoint/backup/restore results, observed sleep/rest/book/work tasks and negative failures. Independent QA must compare actual world and mind records and verify no duplicate or ghost action after restart. The R5 24-hour requirement and R1-R6 release gates remain NO-GO until that execution and independent signoff actually occur.
