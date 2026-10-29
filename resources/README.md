# Pretorius resource library

**Purpose:** A source-controlled intake area for proven open-source components, code references, licenses, and experiments that can shorten the remaining six-organ, Phantasmagorium, and Conclave construction.

**Status 2026-10-29:** Resource collection started on research PR #100, **not** adopted into the canonical Pretorius runtime. The `sources.lock.json` manifest contains 17 repositories with observed licenses and exact commit SHAs. The `companion-directory.md` links **252** additional projects/list entries from a pinned community directory. **Two self-contained third-party Python components have actually been copied**, for inspection and isolated testing.

## Where things are

| Path | Meaning |
| --- | --- |
| `sources.lock.json` | 17 manually prioritized and GitHub-metadata-checked upstream repositories, pinned to commits with expected integration locations and concerns. `integrated:false` is literal. |
| `companion-directory.md` | 252 upstream names/links for discovery, categorized by subject. These are not independently validated candidates. |
| `candidates/revive-companion/control_pid.py` | Byte-for-byte source snapshot of a dependency-free MIT PID controller at `pearthink123/revive-companion@7d11386b778c89de52479a91f838a99c3372fd07`; potential **Affectus regulation** mechanism, not installed. |
| `candidates/revive-companion/bayesian_state.py` | Byte-for-byte snapshot of an MIT, stdlib-only Bayesian user-state estimator; potential companion outreach timing research, NOT Pretorius's own subject state or autonomy. |\n| `candidates/revive-companion/LICENSE` | Upstream copyright/permission notice preserved verbatim. |
| `tests/test_snapshots.py` | Offline stdlib-only integrity and representative behavior tests for both isolated candidates, not evidence of Pretorius integration. |

## Top integration opportunities

**Priority 1: revive the existing six-organ runtime without replacing it.** Inspect the original brain/BrainStore, laboratory host, Noesis action selection and existing donor subsystems before importing anything. Since Python and SQLite already cover persistence, rewriting storage around a third-party graph DB is usually counterproductive.

**Priority 2: adopt small conventional, independently tested mechanisms.** `pytransitions/transitions` is worth piloting for persistent work/ritual lifecycles; `NetworkX` for graph operations where the Persona Connectome needs them; dependency-free functions such as the candidate PID module can be compared against the existing Affectus code. `revive-companion` offers additional local stochastic timing and Bayesian utility code but **must not** be used to fake autonomous initiative with random pings.

**Priority 3: inspect close-to-domain AI companion donor code.** `hanamorix/companion-emergence` contains real Python modules for emotion decay, associative memory, and monologue and deserves targeted source-level evaluation. `m-rui001/Persisto-Mate` has sleep and autonomous reminder ideas. `moeru-ai/airi` has mature interface/avatar and interaction plumbing, but a large TypeScript project should not be transplanted as the Pretorius brain.

**Priority 4: maintain the distinct research experiments.** For Conclave use an explicit contradiction ledger, separate symbolic and empirical support, sourced traditions and nonconsensus by design. For Phantasmagorium preserve mundane-majority dream selection, rare nonsensical ruptures and dreamed-not-lived attribution. Don't replace either with a generic LLM roleplay companion.

## Intake checklist for each candidate

1. Locate the actual source/commit/license. Read API contracts and relevant tests.
2. Check Python 3.11, Windows 11, stdlib or locally installable dependencies, cost, model requirements and offline suitability.
3. Classify **REUSE**, **WRAP**, **ADAPT**, **REFERENCE ONLY**, or **REJECT** with a concrete reason and expected seam.
4. Prefer a pinned upstream dependency or narrow wrapper to wholesale vendoring. A checked-in code snapshot is permitted only with explicit license, provenance and functional test.
5. Write the compatibility spike and compare actual effect with canonical Pretorius behavior before adoption.
6. Preserve one BrainStore, one subject, one Noesis selector, independent authoritative world receipts, and source/dream/imagined provenance. A locally hosted LLM's convincing narration is not a substitute for real cognitive-state and world-action proof.
7. Only after a reviewed integration, update the manifest's `integrated` field and link exact commit and CI evidence.

**Important legal distinction:** repository metadata listing `AGPL-3.0` or `LGPL-3.0` does not authorize arbitrary relicensing; assess obligations before integrating. `LICENSE-REVIEW` means classification needs inspection, not that the source is free to copy. CC-BY list metadata is linked, not imported as source code.

**Network and pricing:** Build-time retrieval of public code may need an internet connection, but production Pretorius must function offline, without an API key or paid hosted model. No external dependency is allowed to become a second agent, shadow autobiographical memory or privileged world-state writer.

**Division of labor:** Main scheduled Pretorius production and QA remain dedicated to offline six-organ R1–R6. The user and assistant collaboratively evaluate organoids in research issue #101 and draft PR #100. No Calibos participation.

## Source attribution

The directory is derived from [awesome-ai-companion at e4135de](https://github.com/DasterProkio/awesome-ai-companion/tree/e4135de4ee40d489d1c8a40aa6c9adba26be07ab) (project names and links only), which is listed as CC-BY-4.0. Pinned third-party code retains its own copyright and license. The repository's local research design is [Pretorius Complete Esoteric Cognitive Architecture](../docs/architecture/PRETORIUS_COMPLETE_ESOTERIC_COGNITIVE_ARCHITECTURE.md).
