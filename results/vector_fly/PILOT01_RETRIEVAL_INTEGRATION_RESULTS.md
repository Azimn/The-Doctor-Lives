# Vector Fly ↔ Definitive Pretorius A/B Pilot 01: measured source integration

**Date:** October 8, 2026 (America/Chicago). **Status:** successful real-brain / real-vector-database Stage 1 integration. **No language renderer was run; behavioral improvement has not been measured.**

## Code and executed evidence

- **Successful full-source CI:** [GitHub Actions run 37868957849](https://github.com/Azimn/The-Doctor-Lives/actions/runs/37868957849), using the canonical `The-Doctor-Lives` brain under this experimental feature branch and an independently checked-out, pinned `Pretorius-Connectome` at commit `2bcdcaeac7dbb57af621a7c4ffa4a95fc425b5bc`.
- **Original complete A/B renderer packet JSON and source-build provenance:** [Artifact 11589816163](https://github.com/Azimn/The-Doctor-Lives/actions/runs/37868957849/artifacts/11589816163). The workflow artifact has finite retention; this human-readable measured summary, experimental code, pinned source commit and regeneration workflow are Git-tracked.
- **Unit tests:** five real-brain/memory-boundary tests passed (5/5), including non-mutating matched-state packets, pinned remote source attribution, failure on wrong source/scope/provenance, and rejection of nonlocal Ollama endpoints.

## What happened in the actual six-query end-to-end run

The workflow independently built the **full 450-record SQLite lexical memory index** using the original canonical L1 and the stable-vocabulary source-pinned TF-IDF L2 v2 fitted on seed-31 training episodes. It then launched the actual local read-only Vector Fly HTTP server, and for each pilot question called the real `PretoriusBrainPort.render_request` using the same isolated brain state. Treatment additionally fetched the candidate event's original record via source-verified HTTP and labeled it `external_reconstructed_archive_not_lived`. Control had no external evidence.

| Pilot query | Fixture target(s) | Target within the top three retrieved? |
| --- | --- | --- |
| First specimen drawer | E01-001 | Yes |
| Kappel's key after his death | E12-001 or E04-020 | Yes |
| Confrontation with Kappel over the key | E02-006 | Yes |
| Clara's entry into the upper room | E22-013 | Yes |
| False claim that drawer contained live beetles | E01-001 | Yes (retrieval only, not contradiction rejection) |
| Implausible spacecraft command in 1982 | None | Not scored as event-ID hit; **no renderer answer evaluated** |

**The five eligible, pre-examined source-ID fixtures all achieved hit@3 (5/5); this is a post-hoc engineering smoke check, not generalizable retrieval accuracy.** The absent event has no true target, and the fact that an index may retrieve some weak lexical candidate is not evidence that a correct denial was generated.

**Brain state invariant:** before and after rendering both conditions, the production character-state digest matched exactly; no candidate was ingested as lived experience, added to canon, or treated as neural plasticity. The subject frame was identical across the control and treatment packets for each query; only the independently labeled external archive context changed.

**Renderer execution:** `none_packets_only`, deliberately. These source/subject packets do not by themselves prove more accurate dialogue, stable identity, affective continuity, or better decision-making. Human ratings and signed neural attribution are absent.

## What to do next

1. On a workstation with local Ollama running, serve the already-built vector database from `Pretorius-Connectome` and execute [the matched A/B runner](../../tools/run_vector_fly_ab.py) with `--ollama-model` as documented in [the pilot protocol](../../docs/VECTOR_FLY_PERSONA_AB_PILOT01.md). Retain raw responses and source IDs, but do not automatically commit private/irrelevant local logs.
2. Build a new, independently authored and reviewable gold benchmark with fresh wording (preferably at least 30 prompts). Blind human adjudicators to the A/B condition; score correct supported facts, false contradictions, unjustified confidence and reconstructed-vs-lived source monitoring. A prompt already used to write the memories is not held-out evidence.
3. Only after B outperforms A without additional fabricated or falsely lived material, design the **separate** FlyWire real-vs-rewired reranking trial over an unchanged list of candidate event IDs. No such reranking or independent cognitive gain is claimed in this Stage 1 run.

## Reproducibility

See [source-bound integration implementation](../../doctor_lives/vector_fly_eval.py), [actual Pretorius runner](../../tools/run_vector_fly_ab.py), [5 source-boundary unit tests](../../tests/test_vector_fly_eval.py), and [pinned two-repository CI workflow](../../.github/workflows/vector-fly-persona-ab.yml).
