# Standalone Pretorius Laboratory preview: operator genesis

Status: **experimental candidate, NOT Pretorius 1.0 R1-R6 acceptance**. No automatic chat, remote model, new organ, second brain, alternate planner or shadow world. This command initializes the **original** source-pinned Laboratory and the one canonical Doctor BrainStore. It is a local operator setup action, not lived experience.

## Install and start on a clean offline machine

Install the existing pinned original-Laboratory and Doctor wheels from the sealed offline wheelhouse created by the GitHub original-Laboratory workflow (the wheelhouse must be exported to the machine before disconnecting from the network). Python 3.11 or newer is required. The setup command does not download any dependency. Verify the original Laboratory source pin against the wheelhouse manifest; distribution names and versions alone are not a source-commit attestation.

```console
doctor-lives preview-init --workspace ./pretorius-alone
doctor-lives --state ./pretorius-alone/state lab-start --world ./pretorius-alone/laboratory.sqlite3
doctor-lives --state ./pretorius-alone/state lab-run --world ./pretorius-alone/laboratory.sqlite3 --seconds 60 --interval-seconds 5 --human
```

The initializer uses original SpatialHabitat, HomeLife and DailyRhythm APIs, creates the same canonical PretoriusBrain and recurrent checkpoint, and verifies both before publishing them together. Publication uses an **atomic kernel-enforced no-replace directory rename** (Linux `renameat2(RENAME_NOREPLACE)` or Windows `os.rename`), so even a competing process that creates an empty workspace immediately before publication cannot have its directory overwritten. Unsupported platforms/filesystems fail closed instead of falling back to POSIX `Path.rename`, which can replace an existing empty directory. A preexisting workspace is refused, including an empty one. Failed staging is cleaned rather than half-publishing an individual. A crash before publication may leave an unreferenced hidden staging directory, never an authorized workspace; inspect it before manually cleaning it up. Do not relocate the world or BrainStore independently. `lab-start` is the verified cold-process start/resume, and `lab-run` uses actual elapsed time and stops cooperatively on Ctrl+C.

The ordinary JSON output is operator-only diagnostics, not Doctor memory. `--human` displays source-verified first-person subject frames and user-facing Swatch @beats, with no raw engineering data. The initializer deliberately declares `subject_experienced_initialization=false`, `laboratory_source_commit_runtime_attested=false`, `books_installed=false`, and `three_task_autonomy_proven=false`. A clean startup may legitimately produce no new first-person speech.

## Real work, books and interruption

`lab-work --event-id YOUR_UNIQUE_ID --world ./pretorius-alone/laboratory.sqlite3` offers Noesis a physically feasible bench decision and the original Laboratory authorizes any movement or work result. This is an **operator-given opportunity**, not a self-proposed goal. A source-backed full-text book must be installed separately using the original Laboratory's pinned edition workflow before `lab-native` can genuinely read it. The local Sensus, Synthetic Ipseity and verified Affectus donors are also mandatory for the opt-in native book/rest path. No demo pages are invented or silently installed by the bootstrap.

Use the same state/world paths after stopping or restarting. For durable backup and recovery:

```console
doctor-lives --state ./pretorius-alone/state lab-backup --world ./pretorius-alone/laboratory.sqlite3 --output ./pretorius-backup
doctor-lives --state ./pretorius-restored/state lab-restore --world ./pretorius-restored/laboratory.sqlite3 --archive ./pretorius-backup
doctor-lives --state ./pretorius-restored/state lab-start --world ./pretorius-restored/laboratory.sqlite3
```

The backup is a **directory containing a manifest and verified files**, not a ZIP archive. Stop the live host and all other state writers before backing up. Publication uses the same atomic no-replace primitive as preview genesis, so a competing empty backup directory cannot be overwritten. Restore only to a **separate, absent** brain/world/action-journal destination, never over the live workspace. Verify the restored world epoch and cold start before retiring the original. The installed-wheel smoke now checks a full 4,096-neuron preview backup, restore and cold start, as well as competing-destination refusal. These short controls are not the 24-hour soak. The still-outstanding 24-hour operational soak must run for at least 86,400 genuine elapsed seconds on continuously running local hardware or an appropriately isolated self-hosted runner, then pass `lab-soak-verify` against original-world action and canonical BrainStore evidence. Short CI and fast-forward time do not count. No soak has been started by this initializer.

## Persistent-machine soak preparation (not started or accepted)

The existing `lab-soak` CLI and `scripts/observe_soak_runner.py` are separate processes. Run both only on a continuously powered local or self-hosted machine with sleep, scheduled updates and automatic reboot disabled, after keeper authorization. Do **not** run a nominal 24-hour job on GitHub-hosted Actions, and do not purchase compute. The observer is standard-library-only on Linux and Windows and must be given the actual running `lab-soak` process PID. It records UTC ISO-8601, monotonic nanoseconds, OS boot identity/uptime, process start identity, system CPU and memory, disk free space and the producer log's file size. It samples every 30 seconds by default and refuses a missing/replaced process, a reboot, a >60-second observer gap or an existing/symlinked evidence destination. Its evidence should be retained separately from the producer's state and log, preferably on an independently controlled volume.

Example Linux shell, from a source checkout with the sealed offline wheel already installed:

```console
doctor-lives --state ./pretorius-alone/state lab-soak --world ./pretorius-alone/laboratory.sqlite3 --evidence-log ./pretorius-soak.jsonl --seconds 86400 --segment-seconds 900 --interval-seconds 30 --work-every-seconds 300 &
SOAK_PID=$!
python scripts/observe_soak_runner.py --pid "$SOAK_PID" --disk-path ./pretorius-alone --soak-log ./pretorius-soak.jsonl --evidence-log /mnt/independent/pretorius-runner-health.jsonl --seconds 86400 --interval 30
wait "$SOAK_PID"
doctor-lives --state ./pretorius-alone/state lab-soak-verify --world ./pretorius-alone/laboratory.sqlite3 --evidence-log ./pretorius-soak.jsonl
```

On Windows, launch `doctor-lives ... lab-soak` in a dedicated PowerShell process, record its actual PID, then run the same Python observer command with `--pid <PID>` and Windows filesystem paths. The observer's test suite (`python -m unittest discover -s tests -p test_soak_observer.py -v`) uses a subsecond positive run and deliberate missing-process, exited-process, symlink and long-interval negatives. These short tests are **not** a 24-hour run.

This is runner-health instrumentation, **not independent source or wall-clock attestation**. The operator must separately preserve independent external time anchors and original-world/Noesis/BrainStore source receipts for QA. The present host offers bench work only if Pretorius is already physically at the bench; it does not autonomously navigate, read or rest through `lab-soak`. Consequently, even 86,400 elapsed seconds with a healthy runner would **not** satisfy frozen R4/R5 full-life acceptance without authentic uncoached activities, matched controls, source-verified memory and independent review. Neither process has been launched by this documentation change.

The authoritative Laboratory source currently pinned by this campaign is `6e49795752835d64fa6fd63d16359669a1ca2ba7`. Production main is unchanged. The preview does not claim three uncoached activities or release acceptance.
