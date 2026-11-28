# M6 original-brain two-way operator conversation, October 30, 2026

**Development branch:** `integration/m6` created directly from fully green M5 `99b6cdb71c5ff4db2ae9382b344a279ba5dcc406`. No change to production `main`, PR #98, draft PR #102, or any other branch. The original pinned Laboratory is `6e49795752835d64fa6fd63d16359669a1ca2ba7`.

**Evidence-first completion:**

- [x] Step 0: Freeze the independent 40-family, 120-utterance semantic holdout before touching M6 semantic mapping in `tests/data/m6_semantic_heldout.json`. The first source run [41075126006](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41075126006) found **116/120 correct (96.67%)**, with **37/40 families stable across all three paraphrases (92.5%)**. No phrase-specific tweaks to that set, no semantic mapper edits to M6.
- [x] Step 0: Instrumented each M5 donor family per original Noesis decision with entered/eligible/contribution, then exercised all three with original-source tailored controls. [Same source CI 41075126006](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41075126006) logged 18 actual decisions: CASCADE **18 called, 0 eligible, 0 score-positive**, household pure feasibility **0 called, 0 eligible, 0 score-positive**, habit **18 called, 16 eligible, 16 score-positive**. Isolated genuine-source controls demonstrated canonical commitment score **+0.03**, valid physical household `clean` preflight (no bonus), and actual verified repeat journal habit score **+0.03**. The **historical 0/180** M5 result is **UNTESTED for household** in its prior operator-only task set, not an empirical negative; CASCADE routine zero in M6 likewise lacks eligibility evidence. All donors remain disabled by default.
- [x] Step 1: Authored `scripts/verify_conversation.py` and negative tests before runtime. Adapted original source-indexed outbound-firsthand guard from `research/outbound-firsthand-claim-gate-stage03-20261009` at `361ac5e1607b2a1a3457306fb1ad218c49328146`, preserving its positive/negative categories and adding original Laboratory/BrainStore source checks.
- [x] Step 2: One original-brain `OperatorConversation` stores labeled operator utterances and replies in the *existing BrainStore*, uses existing `DoctorHomeBridge`, `OperatorWork`, original Noesis and original Laboratory. Both terminal `doctor-lives chat` and `doctor-lives chat-serve` local HTML use the same `submit` ingress; no hosted account, external API or alternate planner. Incoming operator statements are `external_statement` and cannot assert firsthand physical truth. Source-indexed outbound claims are admitted only from authentic lived actions or explicitly recorded wishes; local model additions are separately unverified. No-model replies use deterministic source text.
- [x] Step 2: 3-day simulated absence and actual SIGKILL followed by cold restart. Original Noesis source-backed operator-message acts were registered as spontaneous initiative only after a matching policy, independently verified event and one lived memory; rate limited to 2/day. [M6 pinned original-world and live model run 41075702190](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41075702190) **SUCCESS**, genuine outgoing messages on simulated days 2 and 3 (**[0,1,1]**), not host-selected action names.
- [x] Step 3: A real local `qwen2.5:0.5b` Ollama run (not mocked or remotely hosted), model-off control, 20 matched source-clone CausalAuditHarness seeds, authenticated physical receipts and full conversation history. In [same run 41075702190](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41075702190), operator topic-X messages changed actual selected affordance in **6/20** comparisons versus no-message, **12/20** versus shuffled-topic, variance **18/40 = 0.45**. Actual model: **2 calls, 30 generated tokens**, measured elapsed inference varies by CI run, and every surfaced autobiographical claim is source-verified. These are selection contrasts, **not** proof operator advice improved physical task outcomes.
- [x] Independent stronger source gate added after initial green: [strict real-world source-validation run 41076414424](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41076414424) **SUCCESS** with original-world receipts rechecked: **9 authenticated lived action sources**, **17 matched outbound source claims**, **2 source-verified autonomous Noesis messages** in each of the model-on and model-off jobs. A mutable producer report cannot assert its own proof without the original SQLite world and BrainStore.
- [x] Retained existing M2, M4, semantic, PR #98 Linux host, Windows, soak, wheelhouse and 17-book source checks on M6 (original workflow triggers extended only on the candidate branch). Previous exact-head M5 baseline had all gates green.
- [ ] **Exact final candidate head acceptance:** Latest changes to truthful operator ingress classification, terminal plus localhost end-to-end check, original stage03 firsthand corpus, and bounded model-load transcript reporting are subject to current M6 CI; no green claim is inherited by later untested commits.
- [ ] Production R1-R6 final gates, actual 24-hour elapsed soak, independent reviewer acceptance, merge into `main` and release tag: **not claimed**.

**Operator usage:** `doctor-lives --state ./brain chat --world ./world.sqlite3` opens interactive terminal chat. Use `chat --text "What have you been doing?"` for a single request; add `--local-model qwen2.5:0.5b` for optional local Ollama. `chat-serve --world ./world.sqlite3 --port 8766` starts a web chat at `http://127.0.0.1:8766/`. Both require an already initialized, source-verified original Doctor brain and world, and neither creates a fake character on missing input. Three simulated days are not a three-day wall-clock soak. Client ports are local only.

---
# M5 ChatGPT-authored stand-in and semantic donor harvest, October 30, 2026

**Source lineage:** This work continues solely on `integration/m5`, after true M4/PR #98 merge [`be3e1e0`](https://github.com/Azimn/The-Doctor-Lives/commit/be3e1e0024abd78027ea30a36b38903132e4ad5d). The ChatGPT-authored test-only fixture is [`878fbae`](https://github.com/Azimn/The-Doctor-Lives/commit/878fbae9c60b4d41c93e531e825f1efc589949a1); the observed semantic-refinement implementation is [`b92ac12`](https://github.com/Azimn/The-Doctor-Lives/commit/b92ac12ab7894041d91957e60c4eb787ca3ff978). Independent transport changes subsequently advanced the same branch to `a503452702184a34f549758a0e97078ebad99232`; do not inherit test approval from `b92ac12` without checking newer exact-head CI. Only original canonical BrainStore/Noesis and pinned Laboratory `6e49795752835d64fa6fd63d16359669a1ca2ba7` remain authoritative.

**First actual-world ChatGPT stand-in:** Six static intentions authored by ChatGPT in the project conversation pass through the original `InferencePort` as *hypothetical proposed texts*, with no ChatGPT API, Ollama request, remote compute or shadow decision process. The original source-verified Laboratory yielded five grounded affordances and one unfulfilled wish. Original Noesis selected one, the operator Laboratory bridge produced one independently verifiable action receipt and one original lived action memory, and cold restart preserved both without a duplicate. Initial [actual source run 41068903914](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41068903914) chose `operator_reply`; [corrected run 41069141705](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141705) chose `daily_journal`. These are separate seeded executions and **not** evidence that the language model itself made the choice or that Pretorius initiated the proposal without external input.

**Semantic correction measured before and after:** The ten newly authored phrases were frozen in the first fixture commit. Initial test mapped **7/10** as intended. Diary writing, interrupted-work resumption and concealed pages were all erroneously mapped to explore. The constrained lexicon and phrase adjustments in `b92ac12` map **10/10** of the frozen regression cases without altering original neural motor scores or the preregistered 30-family/90-example test: that judge remained **88/90 accurate and 58/60 paraphrase pairs invariant**. Treat these ten as in-sample regressions after correction, not new blinded generality evidence.

**Donor harvest follows the semantic step and stays OFF:** [Combined exact-code-head audit 41069141705](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141705) replayed 180 original Noesis decisions from 20 causal BrainStore seeds. CASCADE commitment pressure changed **0/180** choices, household grounded preflight **0/180**, and receipt-linked habit **60/180**. Donor-OFF disagreed with an equal-information no-native control **87/180**; habit-ON disagreed **145/180**. These are nonactuating counterfactual rankings, **not proof of better physical outcomes**. All three remain opt-in and disabled by default; no donor promoted. This result supersedes previous M5 counts only for this later source/semantic implementation, not as a same-world performance claim. See `docs/DONOR_HARVEST.md`.

**Regression evidence:** On `b92ac12`, [M5 judge 41069141705](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141705), [BrainStore 41069141362](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141362) (**651 tests / 186 optional skips**), [real M4 Ollama plus PR98 interpretation 41069141505](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141505), [original Laboratory physical and host 41069141473](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141473), [Windows wheelhouse/recovery 41069141314](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141314), and [subject regression 41069141315](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141315) succeeded. [17-book acceptance 41069141826](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41069141826) was pending at the time this note was prepared, although the earlier combined exact `e3d69b6` [17-book run 41062553459](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062553459) passed. No claim of a live ChatGPT connection, independent QA approval, physical donor superiority, actual 24-hour wall-clock soak or full Pretorius 1.0 release.

**R1 to R6:** R1 merged M4/PR98 development candidate evidence present, production/main approval absent. R2 bounded offline/restart candidate operational, autonomous enduring life missing. R3 authentic source/renderer plus real Ollama and manual ChatGPT-proposal path observed, full release gate still open. R4 three uncoached self-originated physical tasks not proven. R5 true elapsed 24-hour soak not complete. R6 end-user release acceptance and immutable tag absent. Conclave/Phantasmagorium/Calibos excluded. Separately logged QA's local Ollama redirect issue as deferred security hardening per owner preference, without treating a model transport workaround as a reason to weaken original functional/provenance tests.

---

# M5 + PR #98 reconciliation checkpoint, 2026-10-30

**Integration provenance:** `integration/m5` descends from last green M4 `1406668dd2dce7585acd6ea80bad1b3406b42032`; existing M5 `eed77201275a4f00a6895837fc0424aa94844d5b` merged PR #98 exact head `13007ce672a185cc8d4c2c1786864ce81eb91ba0` at [two-parent merge `be3e1e0`](https://github.com/Azimn/The-Doctor-Lives/commit/be3e1e0024abd78027ea30a36b38903132e4ad5d). The subsequent import-inventory reconciliation is [`fc8df09`](https://github.com/Azimn/The-Doctor-Lives/commit/fc8df096d07aee80d60901758b5addccb4111ca3). Original Laboratory pin: `6e49795752835d64fa6fd63d16359669a1ca2ba7`. `main`, PR #98 and draft PR #102 are unchanged by this integration.

**Actual merge resolution:** Keep M5's stronger `inspected_noesis_motor_bindings` and original M2 cross-domain operation/authorization checks in `lab_home_bridge.py` and `noesis_lab_work.py`. Use PR #98's superset CLI, runtime, tests and new host/backup/soak/model modules. Preserve all M2/M4 judges, PR #98 tests and the complete original BrainStore suite. M4 local Ollama is an untrusted intention proposer; PR #98 Ollama adds only explicitly unverified operator commentary, never a replacement brain or first-person factual source.

**Exact-head verification ledger:** [First merge PR98 actual-Lab Linux run 41062084909](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062084909) and [full BrainStore run 41062084977](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062084977) were successful on `be3e1e0`. The [combined M5 judge](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219862), [full BrainStore](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219845), [PR98 physical/host/wheelhouse](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219883), [Windows host and offline install](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219917), [17 authentic full-text books](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219850), [M4 live Ollama plus PR98 model interpretation](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219854), and [subject entrypoint inventory](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41062219830) are the new `fc8df09` acceptance runs. Check final conclusion and raw job logs before recording a pass. The earlier subject-entrypoint job failed on unregistered M4 `urllib` imports, prompting the narrow `fc8df09` source-inventory correction; do not hide that negative.

**R1-R6 release accounting:** **R1 candidate, not accepted**: true two-parent ancestry, exact Lab pin, combined tests and independent source review still required. **R2 candidate**: offline original host, work opportunities and restart tests exist but sustained self-initiated goal continuation is unproven. **R3 candidate**: authenticated original subject frames and opt-in model commentary; real Ollama + full renderer validation must pass. **R4 NO-GO**: no independently verified self-originated enduring three-task physical life. **R5 NO-GO**: finite soak, crash/backup controls, Windows/4096-neuron wheel tests exist; no authentic 86,400-second elapsed-time soak. **R6 NO-GO**: draft operator CLI only, no exact integrated-main acceptance or release tag. No gate is promoted solely by code ancestry or previous-branch CI.

**REUSE/WRAP/ADAPT/CUSTOM:** WRAP the existing original recurrent Noesis/BrainStore, M4 loopback Ollama proposer, PR98 loopback operator gloss and pinned actual Laboratory host; no second planner, memory authority, hosted inference, donor drift or new feature. Conventional dependencies remain NumPy/SciPy, Python standard library and source-locked offline wheelhouse. The live Ollama job must demonstrate real model output rather than mocked HTTP.

---

# M5 semantic integration and donor harvest: research evidence checkpoint

**Branch:** `integration/m5` from last fully green M4 commit `1406668dd2dce7585acd6ea80bad1b3406b42032`. Original Pretorius BrainStore remains singular. Original recurrent Noesis is the only choice authority. Original Laboratory source pin is `6e49795752835d64fa6fd63d16359669a1ca2ba7`. `main` has not been touched, PR #102 remains draft, and no branch has been deleted. This block supersedes only development-status claims, not any historical evidence below.

**Step 0:** Reconciled the exact six files changed across the 10 PR #98 commits that M4 lacked, including elapsed Laboratory work, CLI, world receipt journal and real tests. An initial collision with legitimate M2 Noesis-authorized non-work motor IDs was fixed by validating original policy, exact operation and authorized reservation, not by relaxing the world-receipt check.

**Step 1:** The 30-intention by three-paraphrase judge was written BEFORE semantic mapping. Hash-to-action projection was removed. Optional actual local `nomic-embed-text` through Ollama, 768-vector smoke, and a deterministic concept-similarity fallback are implemented. Original semantic judge: **58 of 60** additional paraphrases stable (96.67 percent), and **88 of 90** utterances correctly mapped (97.78 percent). Novelty, familiarity, autobiographical history and recurrent Noesis contributions are recorded separately and capped per family. Random proposal UUID is no longer the tie-breaker. No second selector or model service is installed. A post-null normalization amendment was preregistered in `docs/M5_SEMANTIC_CAUSAL_AMENDMENT.md` after discovering the native neural contrast initially did not change actual grounded candidate selection.

**Exact passed 20-seed source control after the amendment:** [M5 CI 41007830836](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41007830836), evaluated at `c1efde65474eb4e3518607f2e2cffd92cab19f4c`. The unchanged M2 and M4 fallback judges and the independent M5 semantic and attribution judges passed with 180 source-recorded open-intention opportunities. **34/180** selected intentions would have differed with the 0.05 novelty bonus removed. The native motor plus recurrent lesion changed **10/20** general native cognitive choices and **13/20** *recorded-proposal replay* choices. A stricter recurrent-weight-only lesion, preserving the original motor readout, changed **0/20** native choices and **0/20** recorded-proposal replay choices. The recurrent *readout* is behaviorally influential under the post-null policy, but there is **no demonstrated necessity of the learned recurrent W weights**. These are cloned-state causal probes, not evidence of new independent physical outcome improvement.

**Step 2, donor decision:** See `docs/DONOR_HARVEST.md`. A new 20-seed, 180-decision same-source comparison measured differences from donor-off: CASCADE commitments **0**, household grounded physical preflight **0**, household receipt habit **41**. Relative to an equal-information controller without recurrent motor scores, the new donor-off original Noesis choices differed on **14/180** decisions; donor-on habit differed on **55/180**. None of the donors demonstrated superior *world outcomes*. All three are **OFF BY DEFAULT** and the original source modules and tests remain independently preserved. The original donor-host test suites have not all been ported verbatim, because doing so would recreate disallowed auxiliary state and control authority.

**Step 3:** Original default shipping CLI source and provenance tests now reject forged book text/world JSON as physical truths, retain fictional reports only as reports received, and refuse engineer telemetry in subject renderer content. [M5 ingress and full brain CI 41007830839](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41007830839) passed **636 tests discovered with 177 expected optional-dependency skips**. [M5 physical 17-full-text book acceptance 41006600809](https://github.com/Azimn/The-Doctor-Lives/actions/runs/41006600809) passed at its earlier exact source head and produced the verified world/brain fixture; run the same independent book workflow at the final M5 head before claiming all-head completion.

**Step 4:** README, `docs/CURRENT_STATE.md`, `docs/DONOR_HARVEST.md`, and this progress ledger explain canonical production versus draft integration; no other research track is imported. Conclave and Phantasmagorium are still proposals, not runtime organoids. Calibos-derived *mechanisms* remain, but no Calibos memories, persona or separate agent state were imported.

**Acceptance accounting:** The current exact-source M2/M4/M5 semantic, donor and ingress jobs are green at the code head above. At the time of this ledger update the separate latest-head 17-fulltext workflow and any CI rerun after documentation commits must be checked independently. General held-out semantic robustness, original-donor paired world outcomes, recurrent W necessity, 24-hour wall-clock soak, and exhaustive original donor tests remain unresolved; do not label these as passes or graduate the six organs on this evidence.

---

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
