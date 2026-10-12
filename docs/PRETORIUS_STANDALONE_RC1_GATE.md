# Pretorius Standalone RC1: release gate and stop condition

**Decision:** Freeze new cognitive organs and pause integration with the
permanent Pretorius Laboratory and Frankenstein Village until the
standalone character runtime has passed this gate.

## Release promise, and no more

One local user can launch Doctor Septimus Pretorius on a Windows machine
using a free Ollama model. The same Doctor BrainStore, neural checkpoint,
and source-grounded autobiographical memory persist across conversations.
All model-visible subject inputs come through Doctor's typed first-person
projection plus Synthetic Ipseity. A model-generated reply is never
mistaken for world truth. Only a trusted host-confirmed emitted text is
recorded as the character's own written utterance. State survives
ordinary restart and recoverable failures; ambiguous output is flagged,
not silently replayed.

This is **a deployable persistent artificial character**, not evidence
of consciousness, broad tool autonomy, or behavior superior to a strong
prompt-only model. The complete cognitive substrate need not be
scientifically validated to ship a guarded local alpha.

## Gates in mandatory order

| Gate | Evidence required | Status on draft PR #56 |
|---|---|---|
| R1. First-person model input | Strict source/epoch, typed SubjectFrame, no raw telemetry, bounded Ollama output; 2 real-model calls | Passing integration + previous live Ollama smoke |
| R2. Emission truth | Exact reply stored pre-render-ACK; sink identity/hash ACK before autobiographical self-speech; no duplicate output on interrupted ACK; unsafe prose not quoted uncritically | Passed automated failures and real Ollama loopback acceptance; independent review pending |
| R3. One protected launcher | A single supported CLI, no raw engineer diagnostics to model, research paths explicitly unapproved for deployment | Static package inventory passing; independent audit pending |
| R4. Installer / configuration | Pinned Doctor commit plus pinned Synthetic Ipseity commit; Windows Python/Ollama prerequisites; model pulled; one-command health preflight; no paid API | Partly documented, manual scratch-state install; packaging and fresh Windows test pending |
| R5. Coherent recovery | Forced stop during ingress, neural save, organ outbox, model call, stream emit and self-speech admission; no silent invented experience; operator instruction for uncertain stdout | Automated restart tests present; operator reconciliation, bundle backup/restore drill pending |
| R6. Conversation acceptance | Real local model on ≥20 conversation turns across ≥3 restarts, without hidden engineer state; ordinary greeting, follow-up, correct self-speech recall, unsupported claims abstain; record failures | Not tested |
| R7. Release review | Independent reviewer approves access boundary, durable storage, trusted speech emitter and packaging; all PRs merged in dependency order | Draft, not approved |

## Stop rule

The character may be offered as **Standalone RC1 / local invited alpha**
only after **all seven gates pass**, with known limitations documented.
Once achieved, freeze RC1 and return to separate cognitive-quality
experiments and optional Laboratory/Village integration. Do not expand
this release scope with unrelated neural modules or environmental assets.

A narrow API representing output acknowledgments is preferable to
premature TTS or multiple chat protocols. The initial terminal receipt
means only a successful *local stdout write and flush*. It does not
prove a person read the response, audio was played, or a remote client
accepted delivery. Those later transports must implement their own
honest host-side acknowledgment semantics.

## Exact candidate lineages

- Doctor production main is distinct from stacked PR #55
  (read-only subject recollection) and PR #56 (Synthetic Ipseity local
  runtime). Neither is automatically a production release.
- Synthetic Ipseity upstream main v0.9.11 provides a tiny, separately
  authorized laboratory reference action gateway. Combined upstream
  plus Pretorius-specific donor PR #31 is pinned by the Doctor
  CI workflows to `e2d1dc3978c952e59d270a29e84704c8a1fe264a`.
- The reference laboratory is **not** the permanent Pretorius world,
  and no world action APIs are part of the RC1 launcher.

## Immediate next work after the speech receipt merge

1. Verify the full speech/subject route with a real local model and
   artificial crashes, then independently audit it.
2. Make a fixed-version Windows launcher and nonmutating dependency
   preflight, using a dedicated state directory.
3. Back up and restore the whole correlated state bundle, and run a
   controlled restart/continuity trial on the restored copy.
4. Run and record the dialogue acceptance corpus, fix only release
   blockers, and cut the first local invited-alpha release.

This is the finite definition of *deployable*. Adding more neurons,
new cognitive organs, or expanding the laboratory is not a prerequisite.

## First actual emitted-speech acceptance result

**2026-10-12: the unmocked host-speech test passed.** GitHub Actions
[38213575823](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38213575823)
at Doctor commit `8481195f1cd9d8a8dec97dd2a6c32499696452c4`
started an actual fixed-loopback Ollama v0.40.3 instance, downloaded
`smollm2:135m`, and ran the real source-projected subject through
the combined Synthetic Ipseity donor and the host's acknowledgment port.
The result reported exactly **two** actual inference HTTP calls,
**two** host-acknowledged emitted texts with matching SHA-256 hashes,
**two** distinct canonical human input events and **two** subject-owned
emission memories, all across persistent SQLite plus recurrent state.

The model output became autobiographical material **only because the
trusted output sink attested that it wrote that exact text**. No model
claim by itself authorized self-speech or a world observation. The
full Doctor integration, forced-crash receipt suite, ordinary regression
suite and fresh install workflow also passed at `8481195f1`.
The tiny SmolLM2 checkpoint is a transport fixture, NOT a quality-approved
Pretorius personality model.

The next milestone is now **R4 + R5: fixed-version launch and verified
state-bundle backup/restore**, followed by a 20-turn suitability trial
and independent release review. The permanent laboratory stays parked.
