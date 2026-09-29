# Component Registry

Every adopted mechanism records its donor and semantic boundary. Donor code is not silently rewritten.

Pinned production donors:
- `Azimn/calibos-mind@0b8d0d552125a6c9ac736fbc09e62c50ee4c18af`
- `Azimn/Pretorius-Neural-Network@f53f8226b97f20cc9811db4aea81206989917841`

| Component | Donor / version | Status | Pretorius role | Adopted semantics / boundary | Replacement path |
| --- | --- | --- | --- | --- | --- |
| Persistent subject/workspace | calibos-mind @ `0b8d0d5` | selected, adapter implementation | persistent cognitive state and bounded view | Adopt wide non-destructive record history, pinned identity roots, bounded cognitive view and record provenance. Do not import Calibos identity, autobiography, relationships, or private state. The Doctor Lives owns its storage schema so the donor runtime is not a production dependency. | `PretoriusStore` contract |
| Salience | calibos-mind @ `0b8d0d5` | selected, later slice | retrieval ordering | Adopt deterministic retrieval-time ranking and unresolved-concern boost after base persistence is green. | workspace ranking adapter |
| Unresolved loops | calibos-mind @ `0b8d0d5` | selected, later slice | concerns/commitments | Preserve categorical state and evidence links; all content is Pretorius-owned. | continuity adapter |
| Interoception | calibos-mind @ `0b8d0d5` | selected, later slice | body-facing state | Minimal state first; no Calibos body values imported. | interoception adapter |
| Consolidation / sleep | calibos-mind @ `0b8d0d5` | selected, dormant until base persistence | offline maintenance/cognition | Preserve isolation and provenance semantics; no world authority during offline cognition. | offline-cognition adapter |
| Drift/provenance | calibos-mind @ `0b8d0d5` | selected | continuity diagnostics | Renderer output is never silently promoted to autobiography; provenance travels with accepted experience. | provenance policy |
| Recurrent substrate | Pretorius-Neural-Network @ `f53f822` | selected, adapter pending | character-specific neural influence | Preserve validated scientific semantics; production adapter must not rewrite frozen donor experiments. | recurrent adapter |
| Development/encoding | Pretorius-Neural-Network @ `f53f822` | donor evidence, optional boot module | neural construction/update | Experimental provenance retained; not required for first boot. | recurrent adapter |
| Autobiography | existing Pretorius assets | assembly required | lived prior history | Seed only from provenance-bearing source evidence, never renderer invention. | bootstrap loader |
| Relationships | existing Pretorius assets | assembly required | persistent social history | Evidence-bearing state evolves only from accepted experience. | continuity store |
| Renderer | external | interface only | language realization/reasoning | Replaceable and cannot own identity. | `RendererBoundary` |
| Agent chassis | external | not selected | body/tools/runtime | Selection begins only after brain done condition. | `AgentBodyBoundary` |

## Novel-code justification

The local persistence adapter is Pretorius-specific glue, not a replacement database or retrieval engine. Calibos' subject/workspace implementation depends on its frozen Jelly/PsiDuck runtime and carries Calibos-specific lifecycle semantics. Importing that runtime wholesale would violate the identity boundary and unnecessarily couple production Pretorius to a donor organism. The adapter therefore reuses the demonstrated invariants (pinned identity, bounded views, provenance, non-destructive persistence) on Python's standard SQLite engine. No bespoke database abstraction, vector store, scheduler, inference server, event bus, or retrieval engine is introduced.
