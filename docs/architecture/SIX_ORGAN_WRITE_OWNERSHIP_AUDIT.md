# D2 preliminary write-ownership and bypass audit

Status: **source-inspected first pass**, not an exhaustive dynamic trace or D2 approval. No production code or schema changed by this document.

| State, access or effect | Current authority / inspected module | Legitimate downstream consumers | Risk and next inspection |
|---|---|---|---|
| Canonical brain memory, relationship, commitments, concerns | `BrainStore` in `store.py`; mutation via `cognition.py` | Mnemosyne/Noesis/Affectus read views and provenance-aware frames | Audit all SQL writes and transaction ownership; distinguish private acquisition and evidence classifications |
| Recurrent neural checkpoint and action tendency | `PretoriusBrain` / `neural.py`, `cognition.py` | Noesis policy and hidden causal signals | Forbid second donor selector; prove action proposal is not world receipt |
| Subject-native ingress | `ingress.py.project_raw_ingress` | Brain ingestion and bounded phenomenal projection | Verify every host route uses it and rejects privileged control-like content |
| Subject frames and renderer request | `cognition.py._subject_frame_from_view`, `render_request`, typed `models.SubjectFrame` | Renderer through subject-only capabilities | `render_audit_envelope` exposes engineer diagnostics; a trusted host MUST keep it off the subject/model path |
| Optional durable admission/outbox | `DoctorSyntheticIpseitySession` in `ipseity_integration.py` | Subject-only rendering callback | Explicit bypass risk if renderer called outside session; donor pin 0.9.11; reconcile UPPB admission stages before making default |
| Recollection inquiry authorization | `chassis.HostRecollectionController`, `subject_inquiry.py` | Host-selected private recollection projected into typed frames | Bound question callback is a positive control, not demonstrated endogenous intent; preserve private reflection |
| Objective Laboratory action state and receipts | External Laboratory domain tables and `DoctorHomeBridge` receipt verification | Corpus capability/motor proposal, doctor acquired sensory text | Bridge is opt-in and tied to Laboratory semantics; receipt idempotence is not yet a generic provider contract |
| World sensor truth and scene binding | External Laboratory `SubjectPort`; standalone Sensus donor only | Candidate Sensus scene, then synthetic subject admission | No default live Sensus import; prevent source-attribution upgrades on fusion |
| Body/needs/affect | Laboratory body/rhythm plus `PretoriusBrain._update_needs` and `_felt_state` | Corpus bodily percepts and Affectus/Noesis influences | Split authority from derived feelings before considering D6 qualified |
| Time, persistence, audit | Host, `BrainStore` transaction/version, world journal and independent evidence records | Typed event envelopes and engineer traces | Audit independent host/world epochs and crash windows; keep subjective view clean |

## Direct-access surfaces requiring D3 closure

`PretoriusBrainPort.view` and `PretoriusBrain.render_audit_envelope` are engineer APIs, not model-facing capabilities. `PretoriusBrain.render_request` is a permitted **bounded** renderer route if the host controls it. `DoctorSyntheticIpseitySession.publish_current` and `publish_recollection` add optional durable admission but do not yet globally enforce it. `SubjectFrame.renderer_context` is protected by factory capabilities in the current design; inspect every alternate route including CLI, `ipseity_local.py`, speech, cognition pilot and external renderer ports before declaring a complete no-bypass host.

## Pending evidence

Inspect code and exact SQL statements across all modules, trace Laboratory `SubjectPort` and `DoctorHomeBridge` against frozen Lab head, build malicious and crash/restart fixture suite, resolve ADR IPSEITY-001 and MEMORY-001, execute control/ablation tests at a pinned PR head. A static architectural table is never a negative-test result.
