# Pretorius One-Turn Execution Runbook

Status: authoritative execution decomposition for finishing Pretorius from the current v0.5 RC2 Gate 1 review state through a show-floor-ready 1.0 release.

This runbook does not replace PRETORIUS_COMPLETION_PLAN.md, NEXT_THINGS_TO_DO.md, PRETORIUS_DONOR_BRANCH_AUDIT.md, Issue #14, Issue #15, or Issue #17. It converts those authorities into deliberately small web-ChatGPT-sized work units.

Current production main at runbook creation: 288cb14ab9b65adbf2d916c4eb597e2a9dfd0301

Current Gate 1 review PR: #20

Current Gate 1 exact review head: bd83eab994717a315399ef4b8e3d6b9a6beeee67

## One-turn operating rule

Every numbered step below is one ChatGPT web turn.

A turn may inspect the repository, change the files required for that one step, add focused tests, commit, and push. It must not begin the next numbered step.

Implementation, broad validation, independent review, and merge are separate steps.

If a step fails tests or review, do not advance the step number. The next turn repairs only that same step and reruns its focused evidence.

Do not create a new long-lived branch for every micro-step. Use one branch per production gate or tightly related reviewed slice, with one small commit per runbook step.

Do not merge a gate in the same turn that implements or materially repairs it.

Do not mechanically merge historical donor branches. Transplant mechanisms through Pretorius-owned contracts.

At the end of every turn, record:

1. current runbook step ID;
2. exact branch and head SHA;
3. files changed;
4. focused tests run and result;
5. workflow status if already available;
6. any residual defect;
7. the next allowed step ID.

If CI has not completed by the end of the turn, stop anyway. The next numbered validation turn inspects CI. Do not wait in the background.

## Standard prompt for every future turn

Use this form:

Continue The-Doctor-Lives using PRETORIUS_ONE_TURN_EXECUTION_RUNBOOK.md. Perform only step [STEP ID]. Inspect current main, the active branch, and the runbook first. Do not start the next step. Push the completed step to GitHub, report the exact head SHA and focused test result, then stop.

If the current step is blocked or fails, stay on the same step and make only the minimum repair needed for that step.

# Phase A: finish Gate 1 and converge the planning line

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| A01 | Reconfirm PR #20 review state and exact evidence | Verify head, base, open review status, workflows, artifacts, and no competing Gate 1 PR | Repository status note only. No code change |
| A02 | Perform independent review of PR #20 | Independent verdict against GATE1_ASSESSOR_REVIEW.md, exact head only | ACCEPT or a bounded defect list with severity |
| A03 | Repair Gate 1 only if A02 rejects | Minimal corrections on prod/gate1-evidence-integrity | New exact review SHA plus focused tests. Remain on A03 until reviewable |
| A04 | Re-review corrected Gate 1 only if A03 occurred | Independent exact-head reassessment | ACCEPT required before A05 |
| A05 | Merge accepted PR #20 | Normal merge commit preserving reviewed ancestry | PR merged, production main SHA recorded |
| A06 | Verify post-merge Gate 1 production CI | Inspect fresh main workflows and installed-wheel/historical-migration evidence | All required production workflows green |
| A07 | Complete Issue #8 end-user-machine validation | Run the documented fresh physical or equivalent user-machine procedure and preserve evidence | Exact machine/environment result recorded. If user action is required, stop with exact instructions |
| A08 | Merge the planning branch after Gate 1 is stable | Bring NEXT_THINGS_TO_DO.md, completion plan, donor audit, and this runbook into main | Planning docs present on main and post-merge docs/CI clean |

# Phase B: retire branch ambiguity and characterize Neural Convergence

Active branch for B01-B08: a new production-research branch cut from accepted main.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| B01 | Create branch-disposition inventory | Classify every The-Doctor-Lives historical branch as superseded, evidence-only, donor-only, or unique-transplant-needed | BRANCH_DISPOSITION.md with exact refs |
| B02 | Freeze 4,096-unit Neural Convergence protocol | Define control, challenger, metrics, seeds, duration, lesions, stop criteria | Preregistered protocol committed before results |
| B03 | Build production-size characterization harness | Add only the harness/config needed for 4,096-unit matched runs | Focused harness tests green |
| B04 | Run legacy-control characterization | Produce machine-readable control artifact and summary | Artifact digest and run identity recorded |
| B05 | Run convergence-profile characterization | Same protocol, challenger profile only | Artifact digest and run identity recorded |
| B06 | Run recurrent-core causal lesions | Sufficiency, necessity, relearning after lesion, and fixed-seed controls | Lesion artifact and result summary |
| B07 | Run distribution/topology/clipping probes | Functional homology, topology transfer, delta distribution, clipping/brittleness checks | Probe artifact and explicit null/failure preservation |
| B08 | Decide Neural Convergence disposition | Promote, retain optional, or reject as default based on B02-B07 | Decision document. No silent default change |

# Phase C: Gate 2 provenance-bearing ingress

Active branch: gate2-ingress.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| C01 | Write ingress contract | Define the single public observation-admission API and authority classes | Contract and schema only |
| C02 | Add typed observation envelope | Implement event ID, source identity, authority class, confidence, uncertainty, tick/time, and payload | Unit tests for construction/validation |
| C03 | Add idempotency and replay semantics | Duplicate-event handling and deterministic replay rules | Duplicate/replay tests green |
| C04 | Add explicit source/person attribution | Separate who supplied information from who the information is about | Attribution tests, including same-person/different-source cases |
| C05 | Add developmental-context fields | Renderer/model/runtime/modality/tool/affordance context for developmental observations | Context survives restart without becoming subjective truth |
| C06 | Add lived-memory eligibility bridge | Only eligible ingress can become lived-runtime memory | Positive/negative admission tests |
| C07 | Add non-autobiographical ingress classes | Tool result, user assertion, external knowledge, body observation, renderer output, scheduler/wake | None silently become lived autobiography |
| C08 | Add agency-seam record skeleton | Opportunity, goal source, proposer, selector, authorizer, executor, consequence source, evaluator | Engineer-visible record tests |
| C09 | Add provenance-forgery adversarial tests | Reject forged authority, mismatched IDs, duplicate laundering, protected-truth spoofing | Adversarial suite green |
| C10 | Gate 2 review and merge | Independent review, correction loop if needed, merge only after acceptance | Accepted PR merged and post-merge CI green |

# Phase D: Gate 3 standalone offline runtime

Active branch: gate3-standalone-runtime.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| D01 | Write standalone host contract | Define initialize, open, ingest, tick, think, act, render, persist, shutdown, audit | Contract committed |
| D02 | Implement minimal offline host shell | Boot accepted Pretorius with no renderer and no network | Offline host smoke test |
| D03 | Implement clean shutdown and reopen | Persist and reopen through host API | Restart equivalence test |
| D04 | Add session/epoch identity | Stable session record separate from identity | Session lifecycle tests |
| D05 | Add bounded handover schema | Current task, immediate question, pending proposal, concern refs, next check, temporary assumptions | Schema tests and size bound |
| D06 | Add handover write/read path | Create at shutdown/shift, consume at new session | Restart continuation test |
| D07 | Add two-seat continuity harness | Alternate two clean runtimes over one canonical state plus explicit handover | Identity survives seat swap; handover deletion does not erase identity |
| D08 | Add WakeIntent schema | Reason, earliest time/tick, deadline, linked records, priority, expiration | Wake intent unit tests |
| D09 | Add wake OPENED/RECONCILED transaction | Crash inheritance and idempotent reconciliation | Half-completed wake recovery test |
| D10 | Add host scheduler adapter boundary | Host honors wake request without becoming mind authority | Scheduler simulation test |
| D11 | Add operator health/doctor surface | State version, evidence authority, checkpoint health, pending migrations, wake state, capability state | Deterministic diagnostics test |
| D12 | Add portable backup/restore | Backup canonical state and restore to a clean location | Backup/restore/restart test |
| D13 | Add single-writer/process ownership | Explicit lock/transaction owner and safe refusal of conflicting writer | Multi-process contention test |
| D14 | Add capability boundary and local-service authentication rule | Default-deny side effects; localhost is not automatic trust if service mode exists | Denial/authorization tests |
| D15 | Add packaged-runtime smoke validation | Installed package runs outside source checkout with networking disabled | Artifact from clean package execution |
| D16 | Gate 3 review and merge | Independent review and post-merge validation | Accepted runtime on main |

# Phase E: production UPPB signal construction

Active branch: uppb-signal-producers.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| E01 | Write signal-producer registry contract | Declare subject inputs, engineer-only audit inputs, version/fingerprint, output type | Contract committed |
| E02 | Implement body to interoceptive observation boundary | Authoritative body state remains distinct from sensed/felt state | Lag/noise/fallibility tests |
| E03 | Implement source-monitoring cue producer | Use subject-available cues only | Protected provenance alone cannot determine cue |
| E04 | Implement temporal-disorientation producer | Subject-available timing evidence only | Matched lesion and provenance-laundering test |
| E05 | Implement context-mismatch producer | Contextual mismatch from admissible subject evidence | Matched lesion test |
| E06 | Implement familiarity near-miss producer | Bounded retrieval-history trace, restart-safe, admission reset | Near-miss and reset tests |
| E07 | Implement appraisal/prediction-error/uncertainty producers | Keep each cue independent and versioned | Crossed-state tests |
| E08 | Implement social-inference cue producer | No omniscient person-state read | Asymmetric-information test |
| E09 | Implement conflict/ambivalence producer | Thin-margin conflict captured before winner-only reconstruction | Winner-equal/conflict-different test |
| E10 | Run producer provenance-laundering matrix | Adversarially vary protected truth while holding subject evidence fixed | No illicit cue changes |
| E11 | Review and merge signal-producer gate | Independent review | Accepted producers on main |

# Phase F: live UPPB memory integration

Active branch: uppb-live-memory.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| F01 | Freeze live-memory migration plan | Map current autobiographical records into MemoryTrace lineage | Migration contract only |
| F02 | Implement migration/reconstruction adapter | Existing state becomes valid trace state without rewriting protected truth | Historical-state migration test |
| F03 | Integrate live P4 reconstruction | Subject-facing recollection uses P4 while protected evidence remains separate | P4 lesion/restart tests |
| F04 | Integrate live P5 source monitoring | Only E03 subject cues may drive source attribution | Objective-provenance adversarial test |
| F05 | Integrate live P6A | Accepted scalar reconsolidation only | Exact ancestry and lesion tests |
| F06 | Integrate live P6B | Accessibility weakening only | Omission-cause and recovery tests |
| F07 | Integrate live P6C | Temporal confidence and association strength only | Orthogonality and crossed-state tests |
| F08 | Integrate live P6D | Structured temporal generalization only | No arbitrary semantic rewriting; restart audit |
| F09 | Run whole-chain migration/restart/adversarial suite | P4-P6D as one live chain | All lineage and protected-truth invariants green |
| F10 | Review and merge live UPPB gate | Independent review | Accepted live subjective-memory path on main |

# Phase G: P7, P8, P9 thought, expression, motor, and self-perception

Active branch: p7-p9-expression-body.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| G01 | Add explicit private cognition state type | Private thought exists without expression | Construction and persistence tests |
| G02 | Add communicative-intention state type | Intent to disclose/question/refuse/repair/silence separate from thought | State-transition tests |
| G03 | Add external-expression request type | Renderer receives only authorized expression material | Hidden-thought access test |
| G04 | Add communicative-act/withholding ledger | Act class, withholding flag, bounded reason class | Ledger/restart tests |
| G05 | Add visible-private disclosure firewall | Every private item visible to renderer is inside direct-copy protection | Long-episode and older-background leak tests |
| G06 | Verify commitment-sensitive disclosure policy | Confidentiality can affect disclosure; unrelated commitments are neutral | Matched policy tests |
| G07 | Add independent motor/outward-action channel | Action may occur without focal thought | Thought-lesion motor test |
| G08 | Add involuntary-expression channel | Startle/pain/hesitation separate from deliberate selector | No chosen-action reinforcement test |
| G09 | Add explicit self-perception ingress | Self-hearing, movement, exertion, tool results return as observations | Provenance and timing tests |
| G10 | Add limited-introspection/self-explanation rule | Hidden causes do not become first-person certainty | Differential-access report test |
| G11 | Run P7-P9 integrated causality suite | Thought, intention, expression, action, self-perception remain separate | Integrated suite green |
| G12 | Review and merge P7-P9 gate | Independent review | Accepted separation on main |

# Phase H: Gate 4 and P10 renderer/retrieval neutrality

Active branch: gate4-renderer-retrieval.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| H01 | Write renderer interface contract | Renderer cannot retrieve hidden memory, mutate mind state, or own identity | Contract committed |
| H02 | Implement deterministic audit renderer | No model dependency | Golden deterministic tests |
| H03 | Implement local/offline model renderer adapter | Model is swappable wording organ only | Adapter smoke test |
| H04 | Implement second materially different renderer adapter | Different rendering path for substitution evidence | Adapter smoke test |
| H05 | Build disposable retrieval projection | Accessibility index is rebuildable and noncanonical | Delete/rebuild test |
| H06 | Add immutable epistemic envelopes | Provenance classes cannot be upgraded by retrieval score | Similar-text cross-class test |
| H07 | Add exact Subjective Frame receipt | Canonical head, selector/retrieval versions, renderer, sources, omissions, budget, digest | Receipt replay test |
| H08 | Add mandatory constitutional-context failure rule | Missing required context fails closed | Corruption/omission tests |
| H09 | Run renderer substitution invariance experiment | Same mind state/events through all renderers and no-renderer condition | Canonical trajectory equality |
| H10 | Run renderer-versus-developmental-state factorial benchmark | Separate renderer variance from developmental-state variance | Frozen benchmark artifact |
| H11 | Review and merge renderer/retrieval gate | Independent review | Renderer neutrality accepted on main |

# Phase I: Gate 5 closed world/action/body loop

Active branch: gate5-world-loop.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| I01 | Write world/action interface contract | World truth, perception, action request, execution, consequence, observation distinct | Contract committed |
| I02 | Add bounded perception adapter | Modality/range/occlusion/attention limits without rewriting world | Accessibility tests |
| I03 | Add action-request object | Intent/request separate from physical execution | Construction tests |
| I04 | Add execution-result object | Executor and objective result owned by host/body/tool | Authority tests |
| I05 | Route observed consequence back through Gate 2 | Consequence becomes lived only through ingress eligibility | Closed outcome-ingress test |
| I06 | Activate full agency-seam ledger | Populate opportunity, goal, proposal, selection, authorization, execution, consequence, evaluation | Human/scheduler/tool variants |
| I07 | Build Bride/chassis adapter | Bride owns sensors/actuators; Pretorius remains canonical mind | Adapter authority tests |
| I08 | Route embodiment self-perception | Body consequences return through perceptual/interoceptive path | No privileged body read |
| I09 | Run complete closed-loop deterministic scenario | World to perception to mind to action to consequence to memory | Replay/restart equality |
| I10 | Review and merge world-loop gate | Independent review | Accepted closed loop on main |

# Phase J: Gate 5A bounded endogenous planning

Active branch: gate5a-planning.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| J01 | Write plan/goal contract | Goal reason, routes, subgoal, status, lineage, boundedness | Contract committed |
| J02 | Add lived-event goal formation | Meaningful lived event may create goal; neutral event does not | Positive/negative tests |
| J03 | Add alternative routes and active subgoal | More than one route, one active step at a time | Route-state tests |
| J04 | Bridge plan step into existing action authority | Plan candidate competes normally and may lose | Homeostatic-competition test |
| J05 | Add outcome-driven advance/replan/abandon | Success advances, failure switches route, exhaustion stops | Route-failure tests |
| J06 | Add restart/interruption persistence | Plan survives clean restart and interruption | Restart test |
| J07 | Run language-lesion and quiet-time controls | Core planning works with model/private-language disabled and does not obsess after completion | Lesion/quiet suite |
| J08 | Review and merge planning gate | Independent review | Accepted non-LLM planner on main |

# Phase K: Gate 6 constrained deliberation

Active branch: gate6-deliberation.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| K01 | Write deliberation proposal contract | Slow reasoning may propose, never directly write canonical truth/action | Contract committed |
| K02 | Implement deterministic/fake deliberator adapter | Exercise interface without model confounds | Adapter tests |
| K03 | Implement verifier | Check provenance, constraints, contradictions, capability, uncertainty, authority | Rejection matrix |
| K04 | Implement local model deliberator | Optional local reasoning organ behind same contract | Offline smoke test |
| K05 | Bridge verified proposal into existing arbitration | Proposal competes as candidate, no second selector | Stronger-pressure defeat test |
| K06 | Run lesion and fabricated-proposal adversarial suite | Disable deliberation, inject bad proposals, compare behavior | Suite green |
| K07 | Review and merge deliberation gate | Independent review | Accepted bounded deliberation on main |

# Phase L: Gate 7 prediction, correction, causal learning, and knowledge

Active branch: gate7-epistemic-development.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| L01 | Add frozen prediction record schema | Exact proposition, domain, confidence, evidence, state fingerprint, status | Immutability tests |
| L02 | Add append-only prediction resolution | Outcome/evidence/time/scoring append without rewriting forecast | Byte-preservation test |
| L03 | Add calibration summaries | Brier score and bounded domain reliability | Known-data calibration tests |
| L04 | Add selective calibration influence | Domain-specific confidence adaptation only after causal eligibility | Cross-domain neutral test |
| L05 | Add autobiographical correction/supersession ledger | Preserve original error and replacement lineage | Same-final-fact/different-error-history test |
| L06 | Formalize prospective-state taxonomy | Commitment, subject expectation, evaluation-grade prediction remain distinct | Lifecycle type tests |
| L07 | Add world-fact expectation path | Resolve only from relevant subject-available fact evidence | Hidden-world and unrelated-event controls |
| L08 | Add action-outcome expectation path | Bind to one exact pending action and exact outcome | Wrong-action resolution rejection |
| L09 | Add observational sequence predictor | Learn only eligible enacted adjacent transitions | Route-boundary tests |
| L10 | Add preregistered intervention marker | Must exist before outcome; survives restart; invalidates if action abandoned | Pre/post outcome tests |
| L11 | Add matched comparison requirement for stronger causal use | No strong causal weighting without eligible baseline | Insufficient-evidence control |
| L12 | Add counterfactual route provenance | Unchosen route remains model_prediction and cannot train or become lived memory | Non-persistence/non-learning tests |
| L13 | Add external-knowledge source/claim store | Source evidence and externally learned claims separate from autobiography | Lived-vs-learned test |
| L14 | Add typed runtime claim graph | supports, contradicts, extends, derived_from, about, part_of, supersedes | Provenance-bearing edge tests |
| L15 | Add reviewed synthesis path | Derived claim needs explicit admission; originals remain reconstructable | Synthesis/retraction tests |
| L16 | Add knowledge-plane health scanner | Orphans, broken provenance, contradictions, stale synthesis, dangling edges, hubs/gaps | Read-only seeded-defect test |
| L17 | Add bounded-capacity/overflow audit harness | Test concerns, prospective state, wake, handover, predictions/hypotheses, future bounded stores | Matched never-existed versus evicted histories |
| L18 | Run Gate 7 integrated epistemic suite | Prediction, correction, causal learning, knowledge, capacity all coexist | Integrated suite green |
| L19 | Review and merge Gate 7 | Independent review | Accepted epistemic development on main |

# Phase M: quarantined offline hypothesis generation

Active branch: offline-hypotheses.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| M01 | Add hypothesis schema and lifecycle | Quarantined, under-review, supported, weakened, rejected, expired | Schema tests |
| M02 | Add offline proposal generator boundary | Model/deterministic generator produces proposals only | No memory/belief writes |
| M03 | Add brain-side admission/quarantine | Validate provenance, sources, exact original form, mechanism version | Fabricated-proposal rejection |
| M04 | Add weak curiosity/attention influence | Hypothesis may influence inquiry only through bounded policy contribution | Stronger-pressure and lesion tests |
| M05 | Add evidence-based hypothesis resolution | Later evidence supports/weakens/rejects without rewriting original | Append-only tests |
| M06 | Run wake-only versus hypothesis A/B | Equal compute, held-out discovery, false-hypothesis rate, autobiography contamination | Frozen artifact |
| M07 | Review and merge offline-hypothesis gate | Independent review | Accepted or explicitly rejected mechanism |

# Phase N: Gate 8 richer cognition challengers

These are champion-versus-challenger steps. A failed challenger is documented and skipped. Do not force promotion.

Active branch names should be one challenger at a time.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| N01 | Freeze contextual-habit challenger protocol | Context specificity, repetition, reward, disuse, reversal, fatigue/attention modulation | Preregistration |
| N02 | Implement minimal contextual procedural habit | Smallest mechanism that fixes current global-action-value failure | Focused tests |
| N03 | Run habit opposite-context/extinction/restart lesions | Promote only if selective and stable | Decision artifact |
| N04 | Freeze Theory of Mind challenger protocol | False belief, asymmetric information, person specificity, revision | Preregistration |
| N05 | Implement minimal person-belief/goal/preference model | Subject may be wrong; no engineer-truth read | Focused tests |
| N06 | Run ToM false-belief and revision suite | Promote only if held-out behavior improves | Decision artifact |
| N07 | Test richer relationship dimensions | Add only dimensions that beat current simpler relationship state | Promote/hold/reject record |
| N08 | Build evidence-backed self-model developmental update path | Self claims update from conduct/evidence, not arbitrary narration | Matched-history tests |
| N09 | Test typed self-discrepancy/dissonance challenger | Conflict among conduct, commitments/values, and self claims only | Lesion and no-theater tests |
| N10 | Test temporal/causal event graph challenger | Add only if it improves prediction/planning beyond Gate 7 structures | Promote/hold/reject |
| N11 | Add vision adapter if show-floor target needs it | Perception adapter only, no world-authority theft | Modality tests |
| N12 | Add audio adapter if show-floor target needs it | Perception adapter only | Modality tests |
| N13 | Test developmental skill-learning challenger | Demonstrable learned competence with restart and transfer | Promote/hold/reject |
| N14 | Test richer forgetting/consolidation challenger | Must improve long-horizon remembering/forgetting without truth corruption | Promote/hold/reject |
| N15 | Run connectome-to-neural mapping research gate | Compare independent graph, graph-constrained neural populations, shuffled topology, lesions | Retain mapping only if causal and interpretable |
| N16 | Gate 8 consolidation review | Ensure only winners enter production and rejected donors remain documented | Accepted consolidated Gate 8 on main |

# Phase O: final P11 validation and show-floor release

No feature work may be added after O01 without invalidating the final preregistration.

| Step | One-turn objective | Required output | Completion proof |
| --- | --- | --- | --- |
| O01 | Freeze Pretorius 1.0 preregistration | Exact candidate SHA, configs, seeds, task families, thresholds, interpretation rules | Frozen preregistration before final runs |
| O02 | Run persistence/recovery battery | Fresh install, migration, restart, crash, evidence corruption, checkpoint interruption, future schema | Artifact and digest |
| O03 | Run renderer-neutrality battery | Deterministic, local, alternate, no-renderer, renderer swap/restart | Artifact and canonical-state comparison |
| O04 | Run developmental-identity battery | Matched founders, different lived histories, common probes, renderer swaps | Artifact |
| O05 | Run UPPB comparison | Raw implementation, third-person summary, subject-native first-person conditions | Artifact |
| O06 | Run prediction/correction/calibration battery | Brier, reliability, corrections, error-history selective effects | Artifact |
| O07 | Run offline-hypothesis battery | Discovery, false-hypothesis rate, contamination, decision benefit | Artifact |
| O08 | Run agency/embodiment battery | Human relay, scheduler, direct tool, Bride execution | Seam correctness artifact |
| O09 | Run developmental timing/trajectory persistence battery | Early/late intervention, reconvergence, mature non-learning probes | Artifact |
| O10 | Run planning/habit battery | Language lesion, replan, interruption, quiet controls, habit reversal/extinction | Artifact |
| O11 | Run prospective-state battery | Commitment, expectation, wake, prediction, expiry, supersession, lapse, invalidation | Artifact |
| O12 | Run retrieval/frame-integrity battery | Delete/rebuild projections, corrupt index, substitute retrieval policy, verify receipts | Artifact |
| O13 | Run runtime/show-floor resilience battery | Backup/restore, wake crash, checkpoint crash, local-service restart, denial, writer contention, offline package | Artifact |
| O14 | Run bounded-capacity/information-loss battery | Every bounded load-bearing store at capacity and overflow | Frontier report |
| O15 | Run privacy/limited-introspection battery | Visible-private leak probes, hidden-cause/report asymmetry, later explanation revision | Artifact |
| O16 | Run long-duration stability battery | At least 10,000 iterations, repeated sleep/wake, renderer swaps, migrations, stressors, perturbations | Long-run artifact |
| O17 | Build release package from exact candidate | Wheel/package, clean install, CLI/runtime smoke outside checkout | Release artifact digest |
| O18 | Run operator show-floor rehearsal | Cold start, health check, interaction, restart, backup/restore, renderer swap, capability denial, Bride attach/detach where available | Rehearsal checklist and evidence |
| O19 | Reconcile all documentation | README, architecture, migrations, APIs, donor provenance, operator guide, known limits | Docs match exact candidate |
| O20 | Build final release evidence index | One document linking exact SHA, workflows, artifacts, hashes, nulls, residual limits | Release evidence manifest |
| O21 | Independent 1.0 acceptance review | Assessor verifies exact candidate and all frozen evidence | ACCEPT or bounded defect list |
| O22 | Repair final candidate only if O21 rejects | Minimal correction, rerun invalidated batteries only plus required regression | New exact candidate SHA. Return to O21 |
| O23 | Merge accepted 1.0 candidate | Normal merge preserving reviewed provenance | Production main points to accepted release |
| O24 | Run post-merge production smoke | Fresh main package/install/runtime smoke | Green post-merge evidence |
| O25 | Tag and document Pretorius 1.0 | Tag exact accepted production SHA and create final release record | One definitive show-floor-ready production line |

# Mapping from NEXT_THINGS_TO_DO.md to runbook steps

| To-do item | Runbook destination |
| --- | --- |
| Prediction and calibration ledger | L01-L04, O06 |
| Autobiographical correction/supersession | L05, O06 |
| Session handover and two-seat continuity | D04-D07 |
| Agency seam ledger | C08, I06, O08 |
| Quarantined offline hypotheses | M01-M07, O07 |
| Wake-intent contract | D08-D10, O11 |
| Renderer versus developmental-state benchmark | H10, O03-O04 |
| Frozen preregistration | L01-L02 and O01 |
| External knowledge plane | L13 |
| Runtime typed claim graph | L14-L15 |
| Knowledge-plane health | L16 |
| Action-outcome expectations and causal sequence learning | L07-L12 |
| Private-cognition visibility and limited introspection | G05, G09-G10, O15 |
| Bounded-capacity silent-information-loss audit | L17, O14 |
| Developmental timing and trajectory persistence | O09, plus per-challenger preregistration where required |

# Completion rule

Pretorius is not complete because every row has code behind it. Pretorius is complete when every required row has one of three explicit dispositions:

- ACCEPTED and merged with current evidence;
- REJECTED by a preserved causal experiment because the challenger did not improve the production system;
- NOT REQUIRED for the declared 1.0 show-floor target, with the reason recorded before O01.

No step may be skipped merely because a donor repository already implemented a similar mechanism.

No later step may silently reopen a reviewed earlier gate. If a later dependency exposes a real defect in an accepted gate, create a bounded correction step, document which evidence is invalidated, repair that gate, and resume from the first affected downstream step.

The intended end state is one production Pretorius in The-Doctor-Lives, installable and runnable without conversation history, with a body/renderer/tool ecosystem attached only through explicit contracts.
