# D3 repair and alternative renderer entrypoint audit
**Date:** 2026-10-28. **Status:** isolated experiment, pending exact-head CI and review. NOT D3 graduation.
**Base:** six-organ draft PR #89 at `61814d22077b37dc177e2e26a32d6b8bd400deaf`. **Candidate:** draft PR #96.
**Scope:** explicit original chassis ingress, pinned real Laboratory, Sensus, virtual-world and synthetic mock adapters; CLI; real optional Synthetic Ipseity renderer and research Ollama paths.

## Implemented repairs; security semantics

1. **Public world ingress is not world authority.** `PretoriusBrainPort.ingest({"channel":"world","percept":...})` now rejects an unverified direct percept even when its caller invents a valid-looking `laboratory-home:action:...` source string. Plain `world.text` is admitted only as an explicitly *unverified report* with `external_statement` evidence, not as firsthand `lived_runtime_memory`. This is a changed trust boundary, not a simple wording filter.
2. **Real physical admission uses a distinct host capability.** The original `DoctorHomeBridge` registers its one original brain port and uses a one-use source/text handoff after its existing world-state and independently hashed action-receipt checks. The original world/physiology/books remain in the independently pinned Laboratory, never a new brain store. Actual read events still require the existing source-verified installed page and physical book custody.
3. **Tool JSON cannot become experience merely by adding a first-person prefix.** TOOL `percept` checks reject JSON objects, embedded JSON fields, raw machine state, and control-like instructions **before** prepending natural language. A permitted human-readable measurement remains attributed as a **tool result**, not independently verified physical world truth. Raw `payload` alone remains denied.
4. **Source-specific providers are separated:** the observation-only `MockRobotEnvironmentPort` now uses typed finite authorized synthetic-fixture admission and persists `external_statement`, not authentic physical lived truth; the virtual-world adapter rechecks the original bound provider's `verify_receipt` before canonical original-brain lived admission; opt-in Sensus explicitly uses a host-authorized Sensus organ handoff, not the public ingestion method.
5. **CLI no longer constructs arbitrary `Experience` as physical truth.** The `doctor-lives ingest` CLI command routes operator-authored text through `PretoriusBrainPort.ingest(channel=user)`. It denies arbitrary `--source` and `--external` claims, including a forged Laboratory hash. This is an intentionally stricter CLI security contract. It is still a privileged operator utility for other commands.

### Scope and remaining hard limitations

**This is a trusted in-process Python host contract, NOT a security sandbox or an external cryptographic root.** A caller with unrestricted access to `PretoriusBrain`, its BrainStore, a trusted bridge's internals, an authorized Sensus object, or an arbitrary model callback can still bypass Python visibility conventions. `host_authorized=True` is not an independently signed sensor attestation. We have improved and narrowed the public canonical port and actual source-checked provider paths, **not proven global unforgeability**. Source roots, process isolation, and a complete model-facing tool-denial boundary remain prerequisites for production D3. Objective authorizer/data and received claims still require independent source and cross-database replay checks.

## Alternative renderer and model entrypoint inventory (source-based)

| Entrypoint | Exact source | Model/renderer exposure | Finding / disposition |
| --- | --- | --- | --- |
| Protected local conversational command | `doctor_lives/ipseity_local.py::local_turn/main`; `pyproject.toml` script `doctor-lives-local` | `LocalOllamaRenderer` passed via real `DoctorSyntheticIpseitySession`, durable `SubjectOnlyRendererPort`; rendered reply via bounded speech-ack/self-hearing path | Reviewed production-candidate path, subject-only design; requires live exact-head regression and host process controls |
| Durable Ipseity adapter | `doctor_lives/ipseity_integration.py::publish_current/publish_recollection/deliver_next` | Factory `SubjectFrame` converted to authorized subject strings, no engineer envelope on tested callback | Opt-in only; constructor itself says direct model clients elsewhere can bypass it |
| Renderer-neutral request | `doctor_lives/chassis.py::render_request`, `cognition.py::render_request` | Typed subject frame plus separate renderer control rules, NO automatic model invocation | Safe on tested route, not an enforcement boundary for arbitrary model clients |
| CLI renderer export | `doctor_lives/cli.py::main(render)` | `RenderRequest.to_dict()` JSON to console, no model call | Subject-facing fields structured correctly; operator can pipe arbitrary stdout, outside host enforcement |
| CLI engineer view / diagnostics | `doctor_lives/cli.py::main(view)`, `PretoriusBrainPort.view`, `render_audit_envelope` | Engineer-only scores, record IDs and states can reach trusted operator, **not subject renderer automatically** | N3 remains open if untrusted renderer is given a privileged host handle or command surface |
| CLI operator ingress | `doctor_lives/cli.py::main(ingest)` | No model call. Previously `PretoriusBrain.ingest(Experience(...))` bypassed projector; now canonical user projection and forged-source denial | Closed this direct CLI bypass on candidate; exact-head tests must verify it |
| Pinned actual-model smoke | `tools/ipseity_live_ollama_smoke.py` | Real loopback Ollama, via `local_turn` and host-approved recollection | Separate existing smoke gate, not proof of every renderer client |
| Vector Fly paired research | `doctor_lives/vector_fly_eval.py::invoke_ollama`, `tools/run_vector_fly_ab.py`; manually dispatched vector-fly workflow | **Direct HTTP Ollama** experiment; manually assembled condition-matched prompts from typed `RenderRequest` and retrieved evidence | **Research-only exception** in the static allowlist; not covered by durable Ipseity delivery or a safe production entrypoint |
| Static shipping entrypoint gate | `tools/ipseity_entrypoint_gate.py` | AST inventory of direct provider/network imports in `doctor_lives/*.py` and listed `pyproject.toml` console scripts | Useful smoke/allowlist check; **not a dynamic callgraph, subprocess/third-party plugin, or runtime sandbox audit** |
| External host/plug-in renderers | Not present in this source tree / not connected to this review | Arbitrary consumers may call `view()`, `brain.ingest()`, model APIs directly if given host privileges | **Not audited and not certified.** Prohibit privileged handles in model-facing components until isolation/negative tests |

### Actual-execution conditions

Existing preceding adversarial run **40638022040** ran 17/17 real-donor tests non-skipped and exposed N1/N2/N3. For the current FIX candidate, no successful run is claimed without the exact commit's completed checks:
- new fail-closed negative tests for forged world sources, untrusted reports, mock fiction, TOOL embedded JSON/control text, CLI forged physical source, host handoff;
- positive actual trusted Laboratory `SubjectPort.observe`, body/rest and **17 distinct full-text physically receipted book reads**, exact local original BrainStore, restart and no duplicate events;
- Sensus original neural and model-free source-admission pilots, mock and virtual-world parity, true donor Ipseity callback + recorded-transport Ollama serializer, complete brain-tests, clean-install, and original scientific negative benchmarks unchanged.

### Remaining release blockers

1. Independently audited source-root and trust boundary for *all* future provider adapters, including Sensus and arbitrary model-chassis clients. No Python private method naming is a security perimeter.
2. Static code review and adversarial penetration across every model API/wrapper in any real deployed host, not only scripts in this repo. The Vector Fly research path must not be installed as a production character interface.
3. Prohibit engineer `view`, command-line tooling, `brain.ingest` and world-action ports from untrusted LLM tool namespaces.
4. V432.6B independent completion remains unverified. Three world-query capabilities remain deferred. D3 does not graduate from a green test run alone.

**No production merge, organ integration or entrypoint switch is authorized by this audit.**
