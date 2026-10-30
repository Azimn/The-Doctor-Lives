# Pretorius 1.0 candidate: local first-person Laboratory console

**Status:** Experimental release candidate in draft PR #98. Not a released 1.0 product or proof of independent daily-life initiative. The one canonical Doctor BrainStore and the pinned original Laboratory remain the only authorities. No model API, cloud account or network connection is needed for these commands once the pinned wheels are installed.

## Offline installation (Windows PowerShell)

Obtain the verified, source-pinned wheelhouse from the controlled build process, including its `wheelhouse-manifest.json`. Do not treat an arbitrary downloaded collection of wheels as authenticated. Run the existing `tools/offline_wheelhouse.py verify` procedure with the **actual Doctor build SHA** and original Laboratory SHA `6e49795752835d64fa6fd63d16359669a1ca2ba7` before copying the wheels to the offline machine. The wheel build itself may have fetched dependencies; this instruction concerns installation from a previously sealed wheelhouse.

```powershell
py -3.12 -m venv .pretorius
$env:PIP_NO_INDEX = "1"
.\.pretorius\Scripts\python.exe -m pip install --no-index --find-links .\wheelhouse "the-doctor-lives[laboratory]==0.5.0rc2"
.\.pretorius\Scripts\python.exe -m pip check
```

The current CLI does **not** initialize a new authoritative Laboratory or create a full-size six-organ Doctor from scratch. Supply an existing, source-verified Laboratory `world.sqlite3` and matching Doctor `brain` directory containing `brain.sqlite3` and `pretorius_recurrent.npz`. A missing world or brain is a hard error, never permission to mint a substitute. Use the tested source-controlled setup/fixture process until a standalone first-install wizard is independently qualified.

## Read and operate the existing individual

```powershell
$doctor = ".\.pretorius\Scripts\doctor-lives.exe"
& $doctor --state .\brain lab-start --world .\world.sqlite3 --human
& $doctor --state .\brain lab-run --world .\world.sqlite3 --seconds 60 --interval-seconds 5 --human
```

`--human` prints the Swatch Internet Time `@000` to `@999` and **only** the `inner` text of source-qualified first-person subject frames returned by the trusted Laboratory host. If no new frame exists, the console explicitly reports `(No new first-person account.)`; it does not invent Pretorius dialogue. The default without `--human` remains machine-readable JSON with UTC/ISO-8601 and diagnostic fields for the operator. Human mode does not accept a caller-supplied frame, arbitrary tool JSON, renderer prompt, remote model endpoint or source override. An optional fixed-loopback Ollama interpretation can be requested separately; it is explicitly unverified and never replaces the source-backed first-person frame.

To offer repeated real-elapsed-time bench opportunities, add `--work-every-seconds 15` to `lab-run`. The original recurrent Noesis chooses among physically feasible work offers. The host never chooses an action or walks Pretorius to the bench. `lab-work --world .\world.sqlite3 --event-id <unique-id> --human` offers one opportunity only if he is physically at the bench. `lab-sleep --world .\world.sqlite3 --event-id <stable-id> --human` requires his body in the actual bedroom. Reuse a stable ID only to replay the same authorized action, never for a new action. Sleep advances Laboratory simulated time, **not** real elapsed soak time.

A Ctrl+C interruption of `lab-run` requests orderly stop and checkpoint. A killed process is recovered by the next `lab-start`, which reconciles original-world receipts and durable action reservations before admitting lived memory. This is a cooperative local process boundary, not protection from privileged Python or direct database tampering.

## Optional local-model interpretation (not Pretorius's voice)

For an installed local Ollama service listening on the standard loopback endpoint `127.0.0.1:11434`, the existing source-only CLI can append a clearly marked operator interpretation:

```powershell
& $doctor --state .\\brain lab-run --world .\\world.sqlite3 --seconds 60 --interval-seconds 5 --human --local-render-model qwen3:14b
```

The source-verified first-person account always prints first, unchanged. The local model receives **only** bounded first-person `inner` text, never world receipts, BrainStore identifiers, neural scores or engineering diagnostics. Its output is labeled `Unverified local-model interpretation; not lived memory`, is never written to memory and cannot authorize a physical action. No remote URLs, API keys or cloud dependencies are accepted. If Ollama is absent, times out or returns malformed output, the same verified account is printed with an availability note. A cold start with no authenticated new frame never calls a model. Omit `--local-render-model` for the original deterministic zero-model experience. This is a renderer substitution control, not proof of cognition or a completed full-model acceptance matrix.

## Backup and recovery

Stop active Laboratory host processes before taking a backup. Non-SQLite writers must be quiescent.

```powershell
& $doctor --state .\brain lab-backup --world .\world.sqlite3 --output .\snapshot-001
```

A restore requires **new, absent** destination paths. Never overwrite a live original mind or world.

```powershell
& $doctor --state .\restored-brain lab-restore --world .\restored-world.sqlite3 --archive .\snapshot-001
& $doctor --state .\restored-brain lab-start --world .\restored-world.sqlite3 --human
```

The archive verifier checks both canonical brain and original-world authority, their physical domain ledgers, the action journal and manifest digests. Corrupt, rehashed-corrupt, mixed-authority or incomplete archives must fail before creating the replacement authorities. The full-size 4,096-neuron crash/archive/restore test is a candidate regression, not a substitute for a 24-hour wall-clock operational soak.

## Current limitations

This is a text-only console, not an autonomous three-task day or a self-authored enduring project. It does not navigate to books, bedrooms or workstations; does not certify every renderer/model substitution path; and does not make a first-person transcript into proof of cognition. No production-main merge, immutable release tag, or independent R1-R6 acceptance is implied.
