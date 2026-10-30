# M4 open intention engine, verified source-backed implementation

Branch `integration/m4` descends from `integration/m2@8310833d9d5fb5058b0288d5681d2d6ca5a8e24a` because no finished M3 Parts A and B integration branch was available. Main was not touched. Original Lab pinned at `6e49795752835d64fa6fd63d16359669a1ca2ba7`. PR #102 remains a draft.

## Acceptance checklist
- [x] Read inherited PROGRESS.md; branch only from the finished M2.
- [x] First behavioral work followed `scripts/verify_open.py` and hostile/positive judge tests.
- [x] M2 baseline fails the M4 requirements. Its fixed action menu cannot satisfy novel capability, open candidate, or persisted-wish gates.
- [x] `InferencePort` with explicitly loopback-only `LocalOllama` plus deterministic, model-off fallback.
- [x] Free-language proposed intentions, 3 to 8 per opportunity, all tagged `source="proposed"` in the one original BrainStore.
- [x] Unfulfilled proposals persist as explicitly hypothetical wishes after a real SIGKILL and restart. They are available as hypothetical future context, never promoted to facts.
- [x] Ground against data-registered, source-verified operator and Laboratory-bridge affordances, retaining unavailable ideas.
- [x] Authorized source-backed document reading, document notes requiring a prior source read, append-only logical journal entries, local operator inbox messages and reply reading.
- [x] New data-only `archive_findings` capability introduced after the first inference prompt, discovered and executed within eight cycles without new action code.
- [x] Original Noesis recurrent scores drive action selection or decline, with separate original policy/first-person thought and host permission before world write.
- [x] Independent original Doctor action-intent journal, canonical lived-memory source, source operator receipt, and immutable recorded prompt context verified for every action.
- [x] Twenty independent actual recurrent seeds checked against original persisted neural checkpoint files, three simulated days, six-goal-type preregistered threshold, no action without a state change.
- [x] Matched memory-ablation evidence changes aggregate proposals AND choices; paired real Ollama proposer used in local-model control and lesion per seed.
- [x] Separate complete deterministic model-off M2 day still passes the UNCHANGED `verify_day.py`.
- [x] Actual CPU-local Ollama 0.5b test and a full independent 20-seed Ollama-assisted source-backed judge run have passed.
- [x] CI paths include actual pinned Lab, hostile negative tests, native BrainStore regression, local inference and full source-ledger artifacts.

## Evidence: independently passed local-model-assisted research run

**Local Ollama (real runner CPU model, 20 paired seeds):** https://github.com/Azimn/The-Doctor-Lives/actions/runs/41003827338 . It succeeded on both `verify_open.py` and the original M2 judge, after 20 independent seeds, three simulated days and 175 independently receipted actions. Original source-ledgers artifact: https://github.com/Azimn/The-Doctor-Lives/actions/runs/41003827338/artifacts/12954184808 .

**Model-off 20-seed source run:** https://github.com/Azimn/The-Doctor-Lives/actions/runs/41003948845 , green on M4 judge, original M2 judge, negative tests, and loopback-Ollama smoke.

Exact accepted local-model result (a later push strengthens source checks and keeps the preregistered bounds):

```json
{
  "pass": true,
  "checks": {"a":true,"b":true,"c":true,"d":true,"e":true,"f":true},
  "seeds": 20,
  "days": ["day-1","day-2","day-3"],
  "goal_types": 7,
  "threshold": 6,
  "actions": 175,
  "novel_discovery_deadline": 8,
  "m2_fallback_pass": true,
  "choices": {
    "archive": 37, "catalog": 22, "correspond": 21,
    "journal": 25, "read": 32, "reflect": 18, "study": 20
  }
}
```

### Five source-stored proposal and grounding witnesses

| Provider | Hypothetical proposal text | Grounded original authority |
| --- | --- | --- |
| LocalOllama | `append an observation to my daily journal` | `daily_journal` |
| LocalOllama | `read a reply from my operator's inbox` | `operator_reply` |
| DeterministicFallback | `I might read the research document.` | `document_read` |
| DeterministicFallback | `I might send a message to my operator's inbox.` | `operator_message` |
| DeterministicFallback | `I wish I could visit the village beyond the laboratory.` | **unfulfilled wish**, preserved in original BrainStore, no motor permission |

These are model-proposed *ideas*, not necessarily chosen physical actions. Actual choices have independent Noesis policy rows and separate physical receipts.

## Scope and limitations

The validated local-model experiment is **hybrid**: the initial restart-surviving choice is deterministic, Ollama generates open candidates at the post-introduction opportunity on each seed and in each paired memory-lesion run, and the remaining bounded opportunities use the no-model fallback. The local model never makes the final motor choice. A continuously model-on, unconstrained calendar soak has not been demonstrated. Replies are local operator-inbox fixture content, not evidence of a real human response or an externally sent email. Free-language grounding remains bounded lexical matching against authorized physically executable verbs; the ability vocabulary is data-extensible, not a learned general robotics API. These are research follow-ups, not fabricated M4 outcomes.

## Follow-up

Preserve original evidence and the strict judge. Further work can measure genuine generalization beyond these executable operator capabilities and improve non-repetitive long-horizon goal composition without adding a planner or weakening the receipt boundary.

## Historical M2 acceptance
# M2 autonomous-day integration: exit gate PASS

Branch: `integration/m2`, based on `integration/m1@0757197a762f4ba3809a56f888f3bf8d7fe4480c`. Do not touch production `main` or merge draft verification PR #102. Exact original Lab pin: `Azimn/Pretorius-Laboratory@6e49795752835d64fa6fd63d16359669a1ca2ba7`.

## Acceptance checklist
- [x] Read M1 PROGRESS.md and create `integration/m2` from the accepted M1 commit.
- [x] Write the fail-closed `scripts/verify_day.py` judge and adversarial unit tests **before** behavioral modifications.
- [x] Run previous M1 behavior against source-verified real Lab and record all seven failed criteria.
- [x] Subject authors an original-Noesis `pretorius_day_noesis_goal_v1` in the ORIGINAL BrainStore, preserves goal ID and policy/thought across a genuine SIGKILL and fresh process.
- [x] Every executed physical action on primary day binds one ORIGINAL Noesis decision to the host intent and independently hashed original Lab receipt; **four** distinct source-verified task kinds.
- [x] Twenty separately seeded original-neural / original-Lab pairs verify a consequence-only ablation; **11/20 changed** choices and a changed aggregate choice distribution.
- [x] Independent random-controller run has original Lab receipts but fails the Noesis provenance gate, as a real negative control must.
- [x] Original world-source pressure yields **competing bodily needs** while the Noesis selector has alternative feasible affordances. Rest was **not** claimed or forced.
- [x] Strict original-Lab CI executes the short day, cold restart, ablation, random baseline and independent saved-ledger judge on each M2 push.
- [x] The negative tests explicitly reject scripted next actions, unclaimed real-world physical work, forged receipts, duplicates, missing kill, fake ablation and missing random baseline. Original Lab read-only LOOKs are correctly classified as perceptions, never motor commands.
- [x] Save the original Doctor BrainStore, Laboratory SQLite, durable intent journal, source-backed memories, twenty seed checkpoints and report as a reproducible GitHub Actions artifact.
- [x] Record source-pinned real CI run URL and three action-to-decision-to-Lab receipt witnesses.

## Judge-first baseline, measured prior to behavior changes

Pinned original-world negative probe: https://github.com/Azimn/The-Doctor-Lives/actions/runs/40995800827

Old M1 behavior failed **a/b/c/d/e/f/g (7/7)**. Exact failures:
- a: fewer than three different completed Laboratory physical task kinds.
- b: host-specified physical walk `m1-host-center` had no unique original-Noesis policy.
- c: no original-neural-policy-authored durable goal.
- d: no hard-kill/restart exactly-once evidence.
- e: fewer than 20 independently seeded paired trials.
- f: neither original-Noesis rest nor independently demonstrated needs conflict.
- g: no independent random controller evidence.

M2 fixes those shortcomings in the actual behavior and experimental evidence, **not by changing the gate to accept unverified actions**. The Lab's own `SubjectPort.observe()` writes both read-only domestic and rhythm LOOK receipts; the judge correctly excludes those perceptions from the set of physical actions. An unclaimed real `experiment` still fails check b.

## Fully green source-verification CI

- **Actual short day plus judge / adversarial tests:** https://github.com/Azimn/The-Doctor-Lives/actions/runs/40997492216 . Both CI jobs succeeded against immutable original Laboratory. Earlier fully green behavioral source run https://github.com/Azimn/The-Doctor-Lives/actions/runs/40997325782 proves the same day implementation before the evidence-archive-only change.
- **Original complete BrainStore regression:** https://github.com/Azimn/The-Doctor-Lives/actions/runs/40997325784 : **597 discovered, 425 executed, 172 pre-existing optional-environment skips, zero failures** (source implementation; archive-only changes did not affect tests).
- **Day-judge adversarial contract suite:** 15/15 passed, no skips in the pinned-Lab job.
- **Download all original day ledgers and 20 independent neural trial replicas:** https://github.com/Azimn/The-Doctor-Lives/actions/runs/40997492216/artifacts/12951708119

### Exact independent judge output (real pinned Laboratory)

```json
{
  "schema": "pretorius.day-judge-result.v1",
  "pass": true,
  "checks": {"a": true, "b": true, "c": true, "d": true,
             "e": true, "f": true, "g": true},
  "failures": {},
  "distinct_physical_tasks": ["advance", "experiment", "extinguish", "light"],
  "action_distribution": {
    "advance": 2, "experiment": 1, "extinguish": 5, "light": 5
  },
  "authored_goals": ["7d5c7808eac01158c0874b0f"],
  "ablation": {
    "seeds": 20,
    "paired_changes": 11,
    "with_memory": {"repair": 20},
    "without_memory": {"experiment": 11, "repair": 9}
  }
}
```

The actual parent process sent SIGKILL; a different process reopened the exact same original BrainStore and Laboratory without duplicating existing physical events or first-person memories. The host furnished *only a bounded number of opportunities and world-action permission*. It never supplied the chosen next action or goal. Original Noesis selected every primary-day motor action and recorded its policy row, neural checkpoint and first-person thought before source-verified world actuation.

### Three independent original Lab receipt to canonical Noesis decision witnesses

| Physical task | Event ID (host intent and real Lab receipt) | Original Noesis policy row | Independently verified Lab event SHA-256 | First-person memory ID |
| --- | --- | --- | --- | --- |
| Experiment | `day-13a6ddcb2d0448a89c1dfc86db5261a9` | `policy_b8a42930e3774cb1bdf8d2c62a96735c` | `ff752f91e14662177ada9d729d68bd31d6a92aed6d982bc852015e91de6c8bd3` | `mem_e96399d5299f436b9486cde5fc65db5e` |
| Light lamp | `day-cca2ad017a8944c6baa12c78e2cfe7dc` | `policy_6e89f3a9bd4e470cac65d036dbbc0fc9` | `548f65b755e260a01bd3ea03c0708958d5d5cc4cc4422a9aed1c1cb2fd22de34` | `mem_b61b8f8adaaa43afb0edeb7415519c1b` |
| Advance physical time | `day-88a6d399e18a4c979182a3ea1fa81bd1` | `policy_5e1baf9c0bd143e4bba22a965149ec46` | `2ca1b5e0b48cb54169eb336d72e8410acaed440e9d62f08694244de66c27768d` | `mem_fdd5a34fb9e54139b89f5ae97b567e00` |

## Scientific limitations (not failed M2 acceptance gates)

This is **bounded autonomous action selection within real Lab affordances**, not open-domain independently composed planning. The neural policy uses an existing recurrent abstract selector with a bounded mapping to source-feasible physical operations, not a new planner. The short trial displayed repetitive switching of lamp on/off five times each, a genuine but behaviorally weak result. It demonstrated **need conflict**, not spontaneous resting. The 20-seed intervention proves an influence of verified outcome memories on Noesis candidate choice, not human-level transfer or new neural conceptual learning. An unrun **24-hour wall-clock soak**, broader genuine goal generation, increased task diversity and non-repetitive behavior remain later milestones, not fabricated M2 passes.

No additional brain, memory store, planner, paid API or Calibos was added. Production `main` remains untouched; PR #102 remains a draft.
