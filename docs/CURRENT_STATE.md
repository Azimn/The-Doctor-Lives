# CURRENT STATE: The Doctor Lives

**Research snapshot:** October 30, 2026. Definitive production repository: Azimn/The-Doctor-Lives. The only canonical character is Doctor Septimus Pretorius, whose original BrainStore owns his identity, memories, relationships, thoughts, neural checkpoints and policies.

## Branch custody

- `main` remains production and has not been modified for M1, M2, M4 or M5.
- `integration/m1`: stacked six-organ, D3 provenance, autobiographical book preference, and experience-to-action integration, verified by draft PR #102. **PR #102 stays draft; do not merge.**
- `integration/m2`: accepted bounded three-day *simulated* original-Noesis work trial, retained as exact regression.
- `integration/m4`: accepted hybrid local-model open-intentions source evidence; fallback and new data-described operator capabilities.
- `integration/m5`: active isolated candidate based on M4's green `1406668dd2dce7585acd6ea80bad1b3406b42032`; no production promotion.
- PR #98 branch `experiment/pretorius-experience-to-action-20261028`: six changed source files reconciled onto M5, including elapsed-time Laboratory work and its tests, with the M2 work-ID collision repaired without allowing cross-domain reuse.
- Six-organ architecture PR #89 remains draft. PR #100 contains design-only Conclave and Phantasmagorium, not executable organoids. No Calibos identity, memories or agent state have been imported.

## M5 substance

`scripts/verify_semantics.py` was written first. M5 replaces the 10-action text hash with a transparent meaning-based fallback and opt-in local Ollama embeddings (`PRETORIUS_LOCAL_EMBED_MODEL`, loopback only). Original Noesis retains sole choice authority. Per-family novelty is capped at +0.05, familiarity and history capped separately, and each decision records components and the final policy. Source-verified Laboratory/operator permissions still own all actual actions.

`scripts/m5_attribute.py` is a 20-seed real CausalAuditHarness clone experiment that neutralizes both cloned recurrent weights and motor readouts; it must report native policy choice changes and expressly states this is not itself a paired, altered M5 physical-work rollout. `scripts/m5_donor_ablation.py` provides a 20-seed same-snapshot nonactuating donor-on/off/cheap-control comparison. All donor modifiers are OFF by default; see `docs/DONOR_HARVEST.md`.

`tests/test_m5_ingress_shipping.py` exercises the shipping `doctor-lives` CLI on forged book sources, world JSON, received fictional claims, and privileged telemetry. It distinguishes the actually lived *receipt of a report* from a verified physical book read. The existing `tools/verify_17_full_text_lab.py` and pinned Laboratory 17-book workflow remain source-backed tests; the optional corpus is not silently installed into normal fresh worlds.

## Release gates

An isolated development success is not permission to promote `main`. All existing M2/M4 judges, the new semantic judge, full BrainStore CI, source-backed default-entrypoint tests, and new donor evidence must pass at the final exact M5 head. Donor superiority requires verifiable **behavioral/outcome** advantages over equal-information simple controls, not merely a new neural score, a permitted action, a test fixture or nicer prose.

The six primary organs remain unevenly graduated. Conclave and Phantasmagorium are planned auxiliary organoids, not deployed runtime modules. Keep independent first-person provenance, authorized Laboratory receipts and subject-visible versus engineer-private state separation. Preserve UTC ISO timestamps for source ordering, with Swatch @beats for project-facing displays where clocks are surfaced.
