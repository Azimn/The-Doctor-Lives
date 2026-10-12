# Stable first-person recollection port v1

Status: proposed production-owned interface, gated by review and tests.
Implementation branch: `integration/subject-recollection-port-v1`.
Related laboratory evidence: Pretorius-Laboratory research PRs #13, #14, #15 and #16; The-Doctor-Lives Issue #53.

## Concrete defect fixed

The ordinary `PretoriusBrainPort.render_request(user_input=...)` takes a query as an incoming User message. Reusing that entry point for a question authored by the character falsely projects an interlocutor. Pretorius-Laboratory PR #16 established a read-only research workaround, but it called two private Doctor methods.

This branch adds `PretoriusBrainPort.subject_recollection(question)` as a Doctor-owned, in-process API that returns a versioned packet containing only authorized first-person `subject_frame` strings. It reuses `PretoriusBrain.cognitive_view(query=...)` and the original `SubjectFrame` projector. It does not create a fake incoming user event, does not directly expose `CognitiveView`, cannot admit a memory, and does not alter the selected neural profile.

## Contract

Callers are trusted local hosts. The caller must separately establish that a candidate question was genuinely produced by Pretorius's authorized decision process; natural-language validation alone cannot authenticate authorship. Do not mount this method as an unauthenticated endpoint. Never relabel a human/tool message as an internal thought.

The question must be 16 to 150 characters, a single first-person natural-language recollection question beginning with one of the recognized query forms and ending in a single question mark. Control-like, debugging, structured, system-instruction and implementation-native queries fail closed with `SubjectInquiryError`. The validator constrains the lookup cue; it does not certify the model or underlying memory contents.

The result is:
```json
{"schema": "the-doctor-lives.subject-recollection.v1", "subject_frame": ["I remember ..."]}
```

The `subject_frame` is produced by the current approved projection path, not composed from database rows by the caller. The packet does not carry record IDs, hashes, action scores, raw context, the original question, a fabricated User message, or authorization to act. Audit evidence remains with the engineer layer, separate from subject access. A before/after guard verifies that lookup did not change brain tick, store version/digest or neural tick.

No external memory can be promoted simply by being retrieved. Existing source epistemics continue to determine how text is represented.

## Narrow acceptance

Unit/integration tests cover source-present versus source-absent retrieved text, repeated read-only equality, absence of a fabricated User turn, structural metadata exclusion, state preservation, an actual checkpoint restart, and malicious/invalid query rejection.

The original Gate 4 experimental results are unchanged: the tested small local model did not elect to recall and achieved 0/8 in the mediated-recall arm. A forced source-directed question is a positive control only and **does not demonstrate self-initiated retrieval, superior action selection or consciousness**.

Promotion requires independent interface/security review, exact-head CI, host authorization design, and a new separately scored model-selected recall plus action/operand trial on sealed goals. Concrete action authority always remains in the real laboratory host, not in this query API. This patch does not resolve the known GROUND-001 behavior failure by itself.
