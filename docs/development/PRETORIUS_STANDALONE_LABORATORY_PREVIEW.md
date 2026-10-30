# Standalone Pretorius Laboratory preview: operator genesis

Status: **experimental candidate, NOT Pretorius 1.0 R1-R6 acceptance**. No automatic chat, remote model, new organ, second brain, alternate planner or shadow world. This command initializes the **original** source-pinned Laboratory and the one canonical Doctor BrainStore. It is a local operator setup action, not lived experience.

## Install and start on a clean offline machine

Install the existing pinned original-Laboratory and Doctor wheels from the sealed offline wheelhouse created by the GitHub original-Laboratory workflow (the wheelhouse must be exported to the machine before disconnecting from the network). Python 3.11 or newer is required. The setup command does not download any dependency. Verify the original Laboratory source pin against the wheelhouse manifest; distribution names and versions alone are not a source-commit attestation.

```console
doctor-lives preview-init --workspace ./pretorius-alone
doctor-lives --state ./pretorius-alone/state lab-start --world ./pretorius-alone/laboratory.sqlite3
doctor-lives --state ./pretorius-alone/state lab-run --world ./pretorius-alone/laboratory.sqlite3 --seconds 60 --interval-seconds 5 --human
```

The initializer uses original SpatialHabitat, HomeLife and DailyRhythm APIs, creates the same canonical PretoriusBrain and recurrent checkpoint, verifies both, and publishes the pair with one directory rename. A preexisting workspace is refused, including an empty one. A failed stage is cleaned rather than half-publishing an individual. Do not relocate the world or BrainStore independently. `lab-start` is the verified cold-process start/resume, and `lab-run` uses actual elapsed time and stops cooperatively on Ctrl+C.

The ordinary JSON output is operator-only diagnostics, not Doctor memory. `--human` displays source-verified first-person subject frames and user-facing Swatch @beats, with no raw engineering data. The initializer deliberately declares `subject_experienced_initialization=false`, `laboratory_source_commit_runtime_attested=false`, `books_installed=false`, and `three_task_autonomy_proven=false`. A clean startup may legitimately produce no new first-person speech.

## Real work, books and interruption

`lab-work --event-id YOUR_UNIQUE_ID --world ./pretorius-alone/laboratory.sqlite3` offers Noesis a physically feasible bench decision and the original Laboratory authorizes any movement or work result. This is an **operator-given opportunity**, not a self-proposed goal. A source-backed full-text book must be installed separately using the original Laboratory's pinned edition workflow before `lab-native` can genuinely read it. The local Sensus, Synthetic Ipseity and verified Affectus donors are also mandatory for the opt-in native book/rest path. No demo pages are invented or silently installed by the bootstrap.

Use the same state/world paths after stopping or restarting. For durable backup and recovery:

```console
doctor-lives --state ./pretorius-alone/state lab-backup --world ./pretorius-alone/laboratory.sqlite3 --output ./pretorius-backup.zip
```

Restore using the existing `lab-restore` instructions to a separate clean destination, never over the live workspace. The still-outstanding 24-hour operational soak must run for at least 86,400 genuine elapsed seconds on continuously running local hardware or an appropriately isolated self-hosted runner, then pass `lab-soak-verify` against original-world action and canonical BrainStore evidence. Short CI and fast-forward time do not count. No soak has been started by this initializer.

The authoritative Laboratory source currently pinned by this campaign is `6e49795752835d64fa6fd63d16359669a1ca2ba7`. Production main is unchanged. The preview does not claim three uncoached activities or release acceptance.
