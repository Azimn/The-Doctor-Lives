# PRETORIUS: REUSE-FIRST PARALLEL DEVELOPMENT DIRECTIVE
**Issued:** 2026-10-29
**Target:** October 29–November 7, 2026 research integration campaign
**Primary issue:** https://github.com/Azimn/The-Doctor-Lives/issues/101
**Design RFC:** https://github.com/Azimn/The-Doctor-Lives/pull/100
**Canonical brain:** Azimn/The-Doctor-Lives
**World:** Azimn/Pretorius-Laboratory
**Companion source ownership:** no Calibos work or identity/state transplant.

## Mission: finished code over more architectural theory

Produce a **functional end-to-end candidate** integrating Conclave, Phantasmagorium, and six organs. Do not postpone all code until every theoretical question is settled. Use existing tested, licensed, source-pinned implementations for general infrastructure whenever practical. Reserve custom engineering for the genuinely research-distinctive behaviors: persistent incompatible interpretations, historically distinct methods, purposefully incoherent dreams, source-aware imaginative recall, and a single subject with actual world consequences.

**No Calibos collaboration.** Do not read or import Calibos identity, memory or agent outputs. Source reuse means publicly inspectable libraries, existing Pretorius donor code, and ordinary local developer tooling.

Two existing scheduled workers own the 1.0 production lane (producer :10 and independent QA :40). This document governs the **separate organoid/reuse lane**. Do not change their R1–R6 delivery scope, edit their reserved paths, self-approve releases, or merge into main without the established review gates. The production release stays bounded to the already declared v1.0 contract; organoids belong on a separately reviewed opt-in line.

## 1. Mandatory REUSE-FIRST protocol for EVERY component

Before implementing or extending a component, do a short, real source audit:
1. Inspect current The-Doctor-Lives implementation and any existing donor implementation first, including commit SHA, tests, API contracts and actual integration status.
2. Identify at least two relevant public, maintained libraries/repositories or one strong library plus a defensible standard-library implementation.
3. Examine actual APIs, dependency chain, version compatibility, license, maintenance, portability to local Windows/offline Python and integration cost. Never infer suitability from a README headline alone.
4. Run a small **compatibility spike** or isolated contract test on the preferred candidate when an execution surface exists. Estimate code needed for adapter vs rewrite.
5. Decide **REUSE**, **WRAP**, **ADAPT**, **DONOR TRANSPLANT**, or **CUSTOM**, recording the technical reason and negative alternatives.
6. Reuse at the **component level**, not by replacing the one-brain architecture with a multiagent platform. Each imported library remains subordinate to the canonical subject/memory/Noesis/world-authority contracts.
7. Pin dependency versions or source commits, add SPDX/attribution/license notices where applicable and supply Windows/offline install smoke. Reject library adoption that introduces mandatory cloud API keys, a second identity authority or hidden persistence unless an isolation strategy is implemented.

No prose-only "researched X" result counts as completion. Record artifacts: file path, SHA, tested command/CI URL, actual result, and next integration seam.

## 2. Source shortlist to investigate, not a mandatory stack

| Need | Candidate sources | First judgment |
| --- | --- | --- |
| Persistent graph/workflow and resume | https://github.com/langchain-ai/langgraph ; https://github.com/pydantic/pydantic-ai | Reuse workflow/checkpoint ideas or opt-in subgraphs if they can write via Pretorius-owned state; **never** install a second agent memory or Noesis controller by accident. LangGraph has a SQLite checkpointer but it is separate by default. |
| Longitudinal associative relationships | https://github.com/getzep/graphiti ; https://github.com/networkx/networkx | Graphiti has temporal/provenance functionality but demands a graph backend and typically LLM embeddings; high integration cost for local/offline Pretorius. Start with existing Persona Connectome/BrainStore + NetworkX if algorithms are actually needed. |
| Contradictions and competing explanations | clingo (https://github.com/potassco/clingo), abstract argumentation packages, simple 4-valued logic | Begin with a small inspectable Belnap-style four-valued support representation and provenance. Evaluate clingo only for rule solving when actual constrained reasoning warrants it. No automatic conflict deletion. |
| Ritual / goal / commitment lifecycles | https://github.com/pytransitions/transitions | Strong lightweight state-machine candidate, but avoid introducing another authoritative task store. Custom glue only. |
| Structured outputs for local inference | Ollama https://github.com/ollama/ollama | Use localhost chat API JSON schema/tool schema; schema validation required, model output is proposal-only, never world-evidence or privileged executable command. |
| Full source / type validation | Pydantic, JSON Schema, native dataclasses | Use existing project's validators if adequate. Do not add a heavy framework merely to rename typed dictionaries. |
| Testing | pytest or existing unittest/CI | Follow existing regression harness, pinned real Laboratory, same-subject restart/replay, negative provenance cases. |

A shortlist is not an approval. The preferred option may be **the code already present in Pretorius**, even when a popular framework exists.

## 3. Work partition and file ownership

**CORE PRODUCER (existing scheduler, :10):** #89/#96/#97/#98 integration, canonical six-organ runtime, offline start/stop, genuine autonomous multi-task execution, physical and first-person receipts, persistence/recovery. Use production handoff in issue #99; do not write Conclave/Phantasmagorium implementation except minimal shared seams required for basic completion.

**CORE INDEPENDENT QA (existing scheduler, :40):** independent pinned QA, release R1–R6 verification, exact source/CI evidence, security/provenance regressions, cold install and 24-hour soak. Owns review authority for production lane.

**ORGANOID BUILD (independent scheduled research lane):** in PR #100's research branch or a clearly isolated successor branch, implement Conclave contracts/registry, historically distinct spokes, contradiction persistence and Phantasmagorium adapters, then wire to six-organ runtime only on a shared reviewed integration line. Commit working features and tests; do not rewrite canonical brain internals. Produce source-backed handoffs through issue #101, not hourly prose.

**LOCAL MODEL WORKER (Windows, user controlled, not connected to ChatGPT cloud scheduler):** Ollama/Jan/Hermes or another accessible local agent may perform offline source indexing, license and compatibility matrix creation, read-only donor/API analysis, contract-test scaffolding and schema-constrained candidate generation. It has no privileged state authority and should write only in its own Git branch/worktree. Prefer Qwen coder-capable model actually installed/validated; check model tool-call and structured JSON compliance before relying on it. A local model is not the sole reviewer of its own patch.

**INTEGRATOR (review gate):** reconcile source SHA and branch ancestry, run same-lab actual CI, execute full Conclave+Phantasmagorium+six-organ scenario, request independent review. Do not claim integration by documenting wiring.

No worker should modify a path reserved by another. Each handoff records owner, branch, exact SHA, source world SHA, files, tests and blocking decision. Reuse stable issue #101 as the organoid lane's ledger and issue #99 as the core lane's ledger. Avoid duplicative fresh PRs for every micro-step.

## 4. Preferred integration sequence: build VERTICAL functionality, not serial toy subsystems

**First slice:** existing authentic observation → optional Conclave two conflicting interpretations → store both → Noesis later attention/action differs under matched ablation → original memory and world truth unchanged → process restart → conflict still present. Must run on canonical subject through actual six-organ host.

**Second slice:** real donor dream/fancy event → origin tagged dreamed/imagined → source-preserving mnemonic retrieval → Conclave may ignore or interpret → Noesis may ignore → world observes no fake act. Preserve existing Undertow weirdness-rate distribution.

**Third slice:** history-informed ritual proposal → actual Corpus/host-authorized physical action in the Laboratory → receipt → partial empirical revision but unresolved personal symbolic meaning → recovery from interruption.

**Fourth slice:** at least four distinct tradition methods source-pinned and comparable, with nonagreement genuinely persisting. Do not author generic spooky prose as substitute.

**Final slice:** single integrated multi-day world scenario, six-only/Conclave-only/Phantasmagorium-only/full ablations, forced-consensus control, random-symbol control, local renderer replacement, offline startup, restart and negative-case report.

Test contracts as code is built; reserve the whole-system causal/emergence evaluation for the final assembly. Feature-complete is a **demonstrated working specimen**, not a full scholarly literature survey.

## 5. Worker execution template

You are the Pretorius ORGANOID REUSE-AND-INTEGRATE ENGINEER. Read current issue #101, the authoritative architecture RFC in PR #100, issue #99 producer/QA current handoffs, main and research branch SHAs. Refresh before working. You do not work for or with Calibos.

This run must return one source-backed advancement toward a running six-organ+Conclave+Phantasmagorium Pretorius. Review existing donor source and find mature third-party components before inventing new infrastructure. Select the highest-impact unresolved acceptance item that is not reserved by another worker. Choose the shortest vertical implementation that moves actual end-to-end functioning.

Do not spend this run only revising architecture. Inspect real code, choose an actual library or donor candidate, write source changes or runnable spike/test, commit to the isolated research branch, run what tests are available, and link exact real CI SHA/evidence when a workflow executes. If code cannot be touched due to source access or dependency, record the precise reproducible blocker and produce the smallest source-pinned local work packet. Do not manufacture test output. Preserve one brain, one autobiographical store, one subject admission boundary, one Noesis policy and external host/world action authority.

Your distinctive requirements are: genuinely conflicting interpretations must survive, dream incoherence must remain allowed, false memory laundering must fail, rituals cannot mutate world without host/world receipts, and ordinary life must run even when both organoids are disabled.

Before every commit show in issue #101 the REUSE verdict, pinned library/donor/source SHA, targeted path(s), concrete effect and integration test. After commit update a stable ledger comment or concise existing thread with exact SHA, actual executed test or CI URL, any negative case and next code handoff. Never claim 1.0/complete esoteric integration while it remains unqualified. Be willing to discard a beautiful abstraction for a working adapter. Cost: local/free only; no paid hosted models without owner authorization.

## 6. Definition of progress per run

A real run ends with an actual merged, reviewable or executable source artifact. Examples: passing contract tests for two conflicting readings across restart; a pinned Undertow adapter generating dreamed-not-lived events through Ipseity; a state-machine-backed persistent ritual that survives interruption; a demonstrated Noesis policy ablation with Conclave ON/OFF, or a clean local Ollama JSON validation tool that cannot rewrite world evidence.

Rejected outcomes: another independent Pretorius brain, new diagram without code, a synthetic fake terminal transcript, unexecuted "all tests passed", invisible third-party copy-paste without license/provenance, PR proliferation for the same feature, or claiming an hourly scheduler can control a local Windows PC without an installed authenticated relay.

## 7. Reporting template (compact, evidence based)

**Workstream / owner:** ...
**Source head / Lab pin:** ...
**Reuse decision:** candidate(s), licenses/maintenance, adapter cost, choice...
**Code changed:** ...
**Actual tests run:** ...
**Causal or behavioral proof:** ...
**Blocked / next code step:** ...

Keep the artifact brief enough to be consumed by the following worker. Never require the owner to restate architecture choices already in this RFC.
