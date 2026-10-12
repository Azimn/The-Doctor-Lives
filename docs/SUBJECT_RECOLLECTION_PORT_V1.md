# Stable first-person recollection port v1

Status: proposed production-owned interface, gated by review and tests.
Implementation branch: `integration/subject-recollection-port-v1`.
Related laboratory evidence: Pretorius-Laboratory research PRs #13, #14, #15 and #16; The-Doctor-Lives Issue #53.

## Concrete defect fixed

The ordinary `PretoriusBrainPort.render_request(user_input=...)` takes a query as an incoming User message. Reusing that entry point for a question authored by the character falsely projects an interlocutor. Pretorius-Laboratory PR #16 established a read-only research workaround, but it called two private Doctor methods.

This branch adds `PretoriusBrainPort.subject_recollection(question)` as a Doctor-owned, in-process API that returns a versioned packet containing only authorized first-person `subject_frame` strings. It reuses `PretoriusBrain.cognitive_view(query=...)` and the original `SubjectFrame` projector. It does not create a fake incoming user event, does not directly expose `CognitiveView`, cannot admit a memory, and does not alter the selected neural profile.

## Contract

The `PretoriusBrainPort` is **default deny** for direct `subject_recollection(question)` calls. A trusted, in-process host must bind a single zero-argument internal-question selector with `bind_recollection_controller(choose_question)`. The returned `HostRecollectionController.recollect()` obtains the question from that callback rather than accepting it from an external input. The brain port issues an ephemeral, single-use, question-bound, state-bound authorization before reading memory, and consumes it before retrieval. A raw message, a JSON object claiming to be a controller, a token for another port, a stale permit, or an already-used permit fails closed.

```python
# Only the trusted local host can bind a controller it has verified.
controller = port.bind_recollection_controller(choose_authorized_internal_question)
result = controller.recollect()
```

**Host authorization is not evidence of spontaneous cognition.** The host must independently verify that `choose_authorized_internal_question` is an internal controller and that its selected cue did not originate as a relabeled human, tool or renderer instruction. This code does not authenticate the selector's actual causal origin inside the callback. Forced questions in engineering tests are explicit positive controls, never scored as self-initiated memories. Do not expose controller registration, the port instance, the selector callable, or Python method invocation to a language model or remote tool. In-process Python authority is trusted, not sandboxed. The direct `PretoriusBrain.subject_recollection` method remains a research/internal operation and is not an authorized runtime provider route. The stacked Synthetic Ipseity PR #56 must be updated to call this gated chassis interface before its release approval.

Never relabel a human/tool message as an internal thought. No subject-visible record ID or authorization token is passed to Pretorius.

The question must be 16 to 150 characters, a single first-person natural-language recollection question beginning with one of the recognized query forms and ending in a single question mark. Control-like, debugging, structured, system-instruction and implementation-native queries fail closed with `SubjectInquiryError`. The validator constrains the lookup cue; it does not certify the model or underlying memory contents.

The result is:
```json
{"schema": "the-doctor-lives.subject-recollection.v1", "subject_frame": ["I remember ..."]}
```

The `subject_frame` is produced by the current approved projection path, not composed from database rows by the caller. The packet does not carry record IDs, hashes, action scores, raw context, the original question, a fabricated User message, or authorization to act. Audit evidence remains with the engineer layer, separate from subject access. Recollection suppresses retrieval-audit writes, and both SQLite query-only enforcement and the before/after guard verify the read-only contract. Controller permit bookkeeping is ephemeral and engineer-only.

No external memory can be promoted simply by being retrieved. Existing source epistemics continue to determine how text is represented.

## Narrow acceptance

Unit/integration tests cover source-present versus source-absent retrieved text, repeated read-only equality, absence of a fabricated User turn, structural metadata exclusion, state preservation, an actual checkpoint restart, and malicious/invalid query rejection.

The original Gate 4 experimental results are unchanged: the tested small local model did not elect to recall and achieved 0/8 in the mediated-recall arm. A forced source-directed question is a positive control only and **does not demonstrate self-initiated retrieval, superior action selection or consciousness**.

Promotion requires independent interface/security review, exact-head CI, concrete verification of the registered host callback's source in the actual chassis, and a new separately scored model-selected recall plus action/operand trial on sealed goals. Concrete action authority always remains in the real laboratory host, not in this query API. This patch does not resolve the known GROUND-001 behavior failure by itself.
