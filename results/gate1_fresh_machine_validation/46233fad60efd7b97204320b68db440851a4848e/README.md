# Gate 1 fresh user-environment validation

Candidate: `46233fad60efd7b97204320b68db440851a4848e`

Result: **PASS**

This evidence satisfies Issue #8's "fresh machine or equivalent clean user environment" path. Validation ran outside GitHub Actions in an isolated OS-level task container with no repository preinstalled, no external network access, a newly created virtual environment, an empty state directory, and a non-editable `0.5.0rc2` wheel installation.

GitHub Actions was used only to create transport media from the exact candidate SHA because the isolated validation environment intentionally had no external network access. Artifact `11495238315` contains the exact-source archive and offline wheels used for installation. The validation process itself ran outside Actions.

All required checks passed: fresh state creation, Deep-History v2, lived experience ingress, commitment and relationship persistence, read-only rendering, save/restart continuity, evidence class and wording provenance, deterministic repeated historical retrieval, canonical evidence continuity, and zero runtime network events.

See `gate1-validation.json`, `gate1-environment.txt`, `gate1-transcript.txt`, and `evidence-manifest.txt`.
