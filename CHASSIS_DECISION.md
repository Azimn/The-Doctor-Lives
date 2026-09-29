# Agent chassis decision record v0.1

Status: exploratory production integration decision. This document is not scientific evidence.

Production baseline: `7be60ed46add7c74359b322cc033aa7dfabb08e8`.

## Boundary

`doctor_lives.PretoriusBrainPort` is the only Pretorius-facing chassis boundary. Pretorius owns identity, cognition, inherited and lived autobiographical state, relationships, concerns, commitments, recurrent state, and provenance. A chassis owns shell, browser, filesystem and other tools, events, scheduling, messaging, and capability enforcement. Chassis memory or persona facilities must not become canonical Pretorius state.

The adapter is intentionally transport-shaped: deliver an observation through `ingest`, obtain bounded cognition through `cognition` or `view`, construct renderer input through `render_request`, and persist through `save`. Tool results return as new provenance-bearing experiences. Tool authority never enters the brain.

## Candidates inspected

### Hermes Agent

Preferred first integration target. Hermes is a mature local-capable agent runtime with persistent gateway operation, cron/background jobs, messaging integrations, provider abstraction, tools, and support for local inference endpoints including Ollama and other OpenAI-compatible servers. Its Python ecosystem also makes a thin sidecar/bridge to `PretoriusBrainPort` practical.

Integration risk is real rather than hypothetical. Recent upstream reports show Ollama/local-model regressions and Windows local-runtime concurrency problems. Therefore The Doctor Lives must not depend on Hermes-managed memory, identity, or local-model lifecycle. The first adapter should treat Hermes as an external capability/event chassis and keep Pretorius state in this repository's existing store. Pin a tested Hermes release before an executable adapter is promoted.

### OpenClaw

Strong alternate chassis because it combines a gateway, messaging, tools and local-provider support. It remains a fallback rather than the first target because recent upstream reports include Ollama plus Telegram authentication/pairing failures. A later adapter remains feasible because the Pretorius port is runtime-neutral.

### Skales

Functionally attractive for Windows desktop use: local-first operation, Ollama and other local providers, desktop/browser automation, scheduling, mobile pairing, and a broad tool surface. Current licensing is the principal production-integration constraint. The current project is distributed under a proprietary end-user licence, while older releases used BSL 1.1. Do not vendor, fork, or make it a required dependency without a separate licence decision. It remains a useful manually attached body candidate.

## Decision

Proceed with a reversible Hermes-first adapter. Do not embed Hermes in the brain package and do not transfer Hermes memory into Pretorius. The next implementation unit is an explicit chassis bridge contract plus contract tests that simulate event ingress, renderer request construction, tool-result re-ingestion, persistence, shutdown, and restart without requiring Hermes to be installed. After those tests pass, pin a tested Hermes release and add the smallest external-process integration needed to drive that contract.

OpenClaw is the primary fallback if Hermes cannot satisfy local-model or Windows stability requirements at the pinned version. Skales remains an operator-level candidate subject to its licence and interoperability surface.

## Promotion gates

A chassis integration is acceptable only if a clean brain restart produces the same canonical continuity state; chassis identity/persona fields cannot overwrite Pretorius identity; every external observation and tool result enters with provenance; renderer requests remain read-only; tool execution requires chassis-side authority; sleep does not advance the waking clock; and removing the chassis adapter leaves the Pretorius store usable by another adapter.

No chassis-specific success is evidence for Pretorius cognitive mechanisms. It is production engineering evidence only.
