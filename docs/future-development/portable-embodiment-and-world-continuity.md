# Future development design note: Portable embodiment and world continuity

**Recorded:** 2026-11-25  
**Status:** Deferred exploration, not an approved implementation plan  
**Activation gate:** V1.0 completed and qualified, followed by explicit owner approval of a separate development effort.

## Purpose and governing decision

Doctor Septimus Pretorius is designed as a psychologically coherent simulated human living in a fictional Gothic nineteenth-century setting. His present laboratory is not merely a user interface or a container for a language model. It provides a persistent material environment in which he can perceive, act, experience physiological conditions, encounter limitations and live with the consequences of his choices.

A future extension could allow him to inhabit additional simulated environments without replacing his mind or diminishing the causal importance of his body. Do not remove him from his simulation; explore making his simulation extensible so that additional worlds can become places within his experienced reality.

This note does not authorize any changes to V1.0, its architecture, acceptance criteria, qualification workloads, character, models, memory, runtime or deployment. It is not a V1.0 deliverable or a new release blocker. No adapter development, external account enrollment, migration or live-world experiment is authorized by recording this note.

## Existing foundations and limits

The integration branch contains the following relevant foundations, inspected when this note was conceived:

- [Environment port](../../doctor_lives/environment_port.py): a shared observation/action boundary, a laboratory facade over the existing bridge and an observation-only mock sensor provider.
- [Virtual world port](../../doctor_lives/virtual_world_port.py): a host-authorized, trusted-provider contract for observations and actions, with stable world/epoch/event identities, verified receipts, bounded first-person percepts and replay-aware canonical memory admission.
- [Laboratory runtime](../../doctor_lives/lab_runtime.py): a bounded real-elapsed-time host that schedules cognitive opportunities without selecting goals or fabricating experiences; the original Laboratory remains the world authority.

These interfaces are groundwork, not evidence of complete portable embodiment. The virtual-world port currently rejects unsuccessful action receipts as completed experience. A future extension must distinguish a failed attempt from a completed effect and allow a genuinely witnessed failure to have psychological consequences without falsely recording success. Provider conformance and an authorization flag do not authenticate a remote service. The existing interface is for simulated worlds, not robotic hardware or a general security sandbox.

Before designing any implementation, inspect the qualified V1.0 release and its actual physiological state ownership, decision loop, action vocabulary, clocks, persistent commitments and world dependencies. Do not infer complete portability from the interface or from legacy class names.

## Design invariants

| Concern | Required preservation |
| --- | --- |
| Individuality | Exactly one canonical Pretorius identity, cognitive runtime and autobiographical history; no independent copies, replacement LLM personality or parallel selves. |
| Cognitive architecture | Preserve all ten organs, nine supporting mechanisms, existing canonical admission path and relevant requirements of the 35 Articles of Artificiality as qualified in V1.0. |
| Psychological causality | Intentions and meaningful choices originate in Pretorius, not in the adapter, operator, NPC behavior tree or an external agent. Physiology informs rather than dictates his choices. |
| Embodiment | Hunger, fatigue, injury, health, sensory limitations and other existing bodily conditions remain causally meaningful. No arbitrary reset or double counting upon travel. |
| Time and place | Preserve experienced temporal and spatial continuity where possible. An environment switch must not silently fabricate a journey or erase elapsed time. |
| World authority | The environment owns material facts, objects, geometry, affordances and externally witnessed effects. Pretorius owns his subjective interpretation and cognitive response. Explicitly assign authority over each physiological variable; do not introduce a second competing body simulation. |
| Experience | Only verified situated perceptions and outcomes may enter the canonical first-person experience pathway. Keep engineering metadata and untrusted instructions outside subjective rendering. |
| Home | Preserve the original laboratory, its possessions, incomplete work, supplies, spatial relationships and history as somewhere he can return to. |
| Character | Preserve his Gothic setting, personality, interests, ambitions, psychological coherence and capacity for irrationality; do not optimize him into a generic task-completing agent. |

## Conceptual architecture

```text
One canonical Pretorius
  Cognitive organs, supporting mechanisms, memory, identity
              |
  Continuous embodied state and intentions
              |
  Environment boundary: situated perceptions, authorized actions,
  verified effects, failed attempts, time and handoff reconciliation
              |
  One active trusted physical environment at a time
      |              |                |                |
  Laboratory     Gothic village    NWN:EE          1F3D9
```

This diagram describes responsibility boundaries, not proposed changes to current state ownership. The future implementation must discover how qualified V1.0 actually represents physiology and retain those causal relationships. Where an external world does not simulate relevant bodily effects, a validated physiological layer may supply them from witnessed activity and elapsed time. Where a world does simulate those effects, reconcile authoritative measurements rather than running duplicate mechanisms.

Prefer a world adapter that translates available actions and observations. It must not decide what Pretorius wants to do, automatically satisfy needs, invent successful outcomes, disclose omniscient world state or insert a narrative of experiences that did not happen.

## Candidate environments

| Environment | Research value | Preliminary challenge |
| --- | --- | --- |
| Original Laboratory | Control environment and canonical home | Preserve qualified behavior and regression baseline. |
| Frankenstein Village (Evennia) | Nearby shops, colleagues, property, social life and Gothic setting | Connect real movement, inventories, time and physical consequences to the existing body and laboratory. |
| Neverwinter Nights: Enhanced Edition | Graphical embodiment, exploration and human social interaction | Map perceptions, actions, spatial continuity and bodily effects through a cooperating server; obtain administrator permission. |
| 1F3D9 (https://1f3d9.com/) | Independently operated agent-native society, potentially including Calibos | Verify current API, capabilities, permissions, social provenance and the extent of simulated physical consequences. Do not assume the service supports full human embodiment. |
| OpenSimulator | Persistent residences, objects and social interaction | Define material and physiological consequences missing from the host. |
| The Sims 4 | Rich domestic, material and social simulation | Avoid competing autonomy, emotion and need systems. |
| Minecraft or similar sandbox | Physical exploration, resource scarcity and experimentation | Reconcile game-specific physics, affordances, time and character setting. |

These are conceptual candidates, not verified integrations or commitments. A physical robot is outside the scope of this note and the current virtual-world port.

Calibos's reported visits to 1F3D9 motivated this exploration. His mode of participation is not a template that should override Pretorius's embodied-human design. Whether an agent-native city can be presented consistently within Pretorius's fictional setting, or should be used only as an explicitly separate research environment, remains an open design question.

## Suggested post-V1.0 investigation sequence

1. Freeze the qualified V1.0 baseline and record its exact commit, acceptance evidence and known limitations. Audit coupling between the existing laboratory, physiological state, world receipts, memory and action selection. Establish that the original environment can remain unchanged.
2. Explore a minimal connected Gothic village environment as a controlled travel experiment. Pretorius could choose to leave home, walk to a shop, obtain supplies if available, meet another person and return. This is an illustrative opportunity, not a scripted goal or required personality outcome.
3. Define a durable handoff protocol: reconcile pending actions, save the canonical state, transfer one active environment lease, preserve elapsed time and possessions, bind the destination, and verify the first observation. Recover safely from disconnection, duplicate receipts and interrupted transfers. Do not permit two active authoritative bodies.
4. Prototype a cooperating external environment only after the controlled boundary is qualified. Start with a bounded, low-risk environment and explicit host authorization. Treat external dialogue and content as untrusted data; protect credentials, private memory and host tools. Respect service rules and the consent or disclosure requirements of human participants.
5. Investigate cross-environment experiential continuity with independent observation and causal controls. Preserve existing architecture and compare against the frozen V1.0 baseline. Document failures and limits rather than silently compensating for them through scripts.

These steps are a future research sequence, not current work items. Implementation order, environment selection and technical design require owner approval after V1.0.

## Proposed qualification criteria for a future extension

| ID | Observable acceptance condition |
| --- | --- |
| PE-01 | The same canonical identity, brain state and memory survive a round trip and restart without duplication, loss or a parallel cognitive runtime. |
| PE-02 | Bodily conditions and elapsed time remain consistent across the handoff; physiological effects retain their causal contribution to decisions. |
| PE-03 | Independent world evidence demonstrates that intended physical actions actually occurred or failed. Rejected actions never masquerade as successful outcomes. |
| PE-04 | Observations are situated, source-verified, deduplicated and admitted through the canonical experiential pathway before downstream processing. |
| PE-05 | Pretorius independently initiates, revises or abandons intentions through his existing cognitive processes. Matched controls distinguish those processes from adapter scripts. |
| PE-06 | Objects, possessions, location, resources and incomplete commitments reconcile correctly on departure and return, with no duplication or disappearance. |
| PE-07 | Social encounters may produce later spontaneous recollections, changed relationships, intellectual interests or emotional residue; causal tests distinguish genuine influence from scripted recall. No particular emotion or social outcome is mandated. |
| PE-08 | Lost connections, stale observations, malicious content, repeated receipts and partial handoffs cannot fabricate experiences, duplicate physical effects or grant unauthorized control. |
| PE-09 | Original laboratory behavior and applicable V1.0 qualification regressions remain passing, with no changes to the governing baseline requirements. |
| PE-10 | Independent review can reproduce the evidence, trace action provenance and explain limitations. No claim of consciousness is inferred from successful embodiment. |

Exact workloads, thresholds and test procedures remain to be specified against the qualified baseline. A successful adapter call is not qualification of an embodied life.

## Open questions

- Which components currently own each bodily variable, and which depend directly on the Laboratory implementation?
- Can the existing autonomous action selection and clock reconcile a remote environment without bypassing or replacing cognitive organs?
- How can a failed action be witnessed and admitted without confusing an attempted action with a material success?
- How should travel, elapsed time, persistent commitments and asynchronous social events be represented while maintaining one active body?
- Which external environments can provide sufficiently trustworthy observations, real material consequences and appropriate Gothic continuity?
- Can 1F3D9 support the necessary affordances, and how should its artificial inhabitants be perceived without undermining Pretorius's established worldview?

## Research objective

The desired outcome is not a portable chatbot, game bot or collection of character copies. It is one continuously developing simulated human whose experiences in different environments can become meaningful parts of his history and influence subsequent life in his original home.

The possibility is worth investigating precisely because an independently witnessed encounter could affect later thought, imagination, emotional state or scientific work without a user scripting the outcome. That would provide evidence of experiential continuity and psychological causality, not proof of subjective consciousness.

**Release boundary:** Finish and independently qualify V1.0 first. Preserve its architecture and evidence. Revisit this note only in a separately authorized post-V1.0 development effort.

## Technical design supplement: proposed implementation and prototype sketches

**Status:** Documentation only. All code blocks in this supplement are illustrative, untested proposals, not imports, modules, migrations, deployment instructions or executable additions. No implementation may begin before the V1.0 activation gate above. The qualified release, not these sketches, is authoritative.

### A. Preserve the home, not just the data

The three supplied visual concepts depict an ivy-covered stone watchtower with a steep roof, shuttered windows, a lantern-lit arched door, scaffolding, an attached covered area, a garden and a distant settlement. They establish a useful visual direction: a modest, inhabited Gothic scientific retreat within a traversable landscape, not an isolated abstract laboratory.

Use these concepts as art and level-design references only. The images are not evidence of existing world geometry or possessions. Their differing tower arrangements, lighting and settlement positions are alternative compositions, not contradictory canonical facts. Do not introduce repairs, gardening tools, crops, water sources, inhabitants or objects merely because a reference image depicts them.

Before constructing geometry, export or inspect the qualified Laboratory's room/station topology, door connections, objects, inventories and world coordinates. Map existing locations to the tower interior without changing their authoritative identities. A proposed exterior progression is:

```text
Existing interior stations (as qualified)
              |
       Existing exit, if supported
              |
       Tower threshold / front path
          /                    \
  Garden / outbuilding       Country road
                                  |
                           Village boundary
                                  |
                    Shops, homes, public spaces
```

Each connection requires actual traversable edges, travel costs, collision or reachability rules, visible affordances and witnessed transitions. The garden, well or basin, wood store and scaffolding are optional art concepts until reconciled with the canonical world. The preferred first expansion is a small surrounding landscape and a road to Frankenstein Village, not a wholesale recreation of the Laboratory or a disconnected game avatar.

If a future graphical client is developed, its geometry and animation should render authoritative material state. A lantern glowing in an image does not establish that a lantern is lit in the simulation. Client-side visual effects must never independently create lived events.

### B. Current code and the precise gap

Read-only inspection of the development branch found:

| Existing file | Consequence for future work |
| --- | --- |
| [virtual_world_port.py](../../doctor_lives/virtual_world_port.py), blob 92eab12 | Provides VirtualWorldSource with observe, act and verify_receipt, and VirtualWorldEnvironmentPort with bounded verified canonical admission. A provider is explicitly authorized by the host. Failed action receipts are rejected by the present admission path. |
| [environment_port.py](../../doctor_lives/environment_port.py), blob 4eb6129 | Defines observe/act and EnvironmentFeedback; preserves the existing Laboratory bridge. The mock sensor provider cannot actuate. |
| [lab_runtime.py](../../doctor_lives/lab_runtime.py), blob 0f747cb | Uses cooperative exclusive locks, canonical state checks, recovery and checkpoints. Its native loop instantiates SpatialHabitat, SubjectPort, SixOrganLaboratoryCycle and NativeLaboratoryGoalChooser, and calls chooser.step. Its host-selected mapping and routing limitations are explicitly disclosed. |
| [lab_home_bridge.py](../../doctor_lives/lab_home_bridge.py), blob bd44153 | Contains the existing operation-domain map, durable action-intent handling, proof checks, recovery and world effect admission. |
| [chassis.py](../../doctor_lives/chassis.py), blob 76ea686 | Contains PretoriusBrainPort and distinct verified laboratory and virtual-world ingress paths. |

These are point-in-time observations. The implementation must repeat the audit against the frozen V1.0 commit. In particular, a new adapter alone does not make the laboratory-specific native chooser, physiology, clock or commitments portable. Do not substitute a new model-driven chooser or call a guessed runtime method to conceal that gap. The legacy SixOrganRuntime class name is not a claim that the qualified architecture has only six organs.

The preferred refactor, only if the audit supports it, is to extract the smallest environment-dependent interfaces from the qualified action loop while retaining the exact cognitive decision and admission paths. First demonstrate behavioral parity through the existing Laboratory facade. If parity cannot be established, keep the Laboratory host unchanged and reconsider the extension.

### C. State authority and physical continuity

Maintain a versioned authority matrix in the future implementation. The following is a proposed division, subject to the audit.

| State | Authoritative owner / rule |
| --- | --- |
| Neural state, autobiographical memory, identity, concerns | Existing canonical brain and checkpoint; never exported to a remote game. |
| Current environment and body lease | Trusted host registry, one active authority, monotonic fencing token. |
| Body condition | Existing qualified bodily state owner. A portable snapshot is a transport representation, not an independently advancing second physiology. |
| Position, reachability, world objects and other actors | Active environment's authoritative simulation. |
| Possessions | Explicit per-world ownership and transfer records; carry only eligible objects through verified departure/arrival. |
| Elapsed time | A single accepted embodied-time timeline, with explicit mapping from each world clock. |
| Intention, selection and interpretation | Existing cognitive architecture. |
| Remote action effects | Environment-issued authenticated outcome tied to the original decision and durable intent. |

Record units, valid ranges, integration rules, time resolution and provenance for each physiological variable before moving it. If the Laboratory owns fatigue and hunger today, do not simply move those values into a new brain table. Determine whether the existing physiology can remain the sole authority while the external adapter reports exertion, meals and rest as inputs. If not, a separately qualified extraction may be needed.

When a world provides no equivalent body mechanics, a future portable physiology provider must integrate the existing equations exactly once per accepted embodied interval, including exertion, nutritional intake, sleep and injury as applicable. When a world supplies an equivalent effect, explicitly reconcile it instead of adding it again. Never infer food intake from a chat message or sleep from an elapsed network timeout.

### D. Draft data contracts (not current APIs)

The following sketches clarify responsibilities, not final schemas. Existing stable IDs and evidence rules must be retained. Production payloads require validation, size limits, authenticated transport, canonical serialization, versioning and independent evidence.

```python
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class Outcome(Enum):
    COMPLETED = "completed"
    FAILED = "failed"       # Witnessed attempt, no claimed success
    DENIED = "denied"       # Authorization failure, not lived by default
    UNKNOWN = "unknown"     # Transport uncertainty, never a world fact


@dataclass(frozen=True)
class Intent:
    event_id: str
    decision_id: str
    body_id: str
    world_id: str
    world_epoch: str
    fence: int
    operation: str
    arguments_digest: str


@dataclass(frozen=True)
class Evidence:
    intent: Intent
    outcome: Outcome
    provider_sequence: int
    elapsed_world_ms: int
    physical_delta_digest: str
    percept_digest: str
    proof: bytes


@dataclass(frozen=True)
class BodyTransfer:
    handoff_id: str
    body_id: str
    source_world: str
    destination_world: str
    source_epoch: str
    snapshot_digest: str
    carried_inventory_digest: str
    last_embodied_ms: int


class WorldAdapterDraft(Protocol):
    def observe(self, *, fence: int) -> object: ...
    def submit(self, intent: Intent, arguments: bytes) -> Evidence: ...
    def lookup(self, event_id: str) -> Evidence | None: ...
    def verify(self, evidence: Evidence) -> bool: ...
```

The current VirtualWorldReceipt remains unchanged for V1.0. The proposed extended envelope is host/audit data only. A future ingress adapter would render a bounded first-person observation from independently verified sensory facts, with the existing canonical first-person checks. Neither raw remote chat nor a remote model's claim about an effect is proof.

### E. Draft action integration and replay semantics

Keep the existing decision authority and durable intent journal. The world provider must durably deduplicate each event ID and reject a reuse with different arguments, identity, epoch or operation. A failed response is not necessarily proof of an absent effect.

```python
# Pseudocode: all collaborators below are proposed interfaces.
# No call is made to a live provider or to the shipping runtime.

def execute_selected_intent(intent, args, journal, world, admission):
    journal.assert_canonical_decision(intent)
    journal.assert_current_fence(intent)
    reservation = journal.reserve_or_load(intent, args)

    if reservation.is_new:
        evidence = world.submit(intent, args)
    else:
        evidence = world.lookup(intent.event_id)
        if evidence is None:
            return "reconcile_required"

    if not world.verify(evidence):
        return "quarantined"
    if evidence.intent != intent:
        return "quarantined"

    if evidence.outcome is Outcome.UNKNOWN:
        return "reconcile_required"
    if evidence.outcome is Outcome.DENIED:
        journal.record_denial_once(evidence)
        return "denied"

    # This represents a future reconciler, not a direct memory write.
    # It must apply verified body/time effects exactly once and use
    # canonical ingress before dependent cognitive processing.
    admission.reconcile_and_admit_once(evidence)
    journal.mark_reconciled(intent.event_id)
    return evidence.outcome.value
```

In production, timeouts and exceptions leave the intent pending. Never blindly retry a motor command after losing its acknowledgement. Recover by matching the independently durable effect and the original decision, or obtain authoritative proof that the action did not execute. A stale provider, mismatched receipt, forged actor or unexpected epoch blocks admission. A genuinely witnessed locked door may be admitted as an experienced failure, while a firewall denial or invalid credential remains engineering information. If a service cannot support stable receipt identity and recovery, it is unsuitable for authoritative physical embodiment until those limitations are resolved.

A future host pulse may offer a cognitive opportunity using the same qualified loop, admit observations, accept a native motor decision, route it to an available affordance and reconcile its outcome. It must not invent a goal when the native loop has none. Low-level navigation can execute a selected destination; it cannot pick the destination or invent a reason for visiting it.

### F. Draft travel transaction

Treat travel as a recoverable state machine, not a simple assignment to current_world. The canonical process owns the transition. Use an explicit route to a reachable threshold for ordinary travel. Cross-world discontinuities that cannot be made spatially coherent remain separate research proposals, not fabricated memories.

```text
ACTIVE_SOURCE
  -> RECONCILING_PENDING_ACTIONS
  -> CHECKPOINTED
  -> DESTINATION_PREPARED (inactive, no action rights)
  -> SOURCE_FENCED (cannot accept new motors)
  -> DESTINATION_AUTHORIZED (next monotonic fence)
  -> ARRIVAL_VERIFIED
  -> ACTIVE_DESTINATION

Uncertain source fence / arrival / receipt
  -> RECOVERY_REQUIRED (no new motors)
```

```python
# Pseudocode only. Each advance must be durable and idempotent.
def advance_handoff(tx, host, source, destination):
    if tx.phase == "CHECKPOINTED":
        destination.prepare_inactive(tx.transfer)
        host.advance(tx.id, "DESTINATION_PREPARED")
    elif tx.phase == "DESTINATION_PREPARED":
        source.revoke_and_confirm(tx.source_fence)
        host.advance(tx.id, "SOURCE_FENCED")
    elif tx.phase == "SOURCE_FENCED":
        # Atomically persist a single new authority and fence.
        host.authorize_destination_once(tx.id)
    elif tx.phase == "DESTINATION_AUTHORIZED":
        arrival = destination.lookup_or_confirm_arrival(tx.id)
        host.verify_and_admit_arrival_once(tx.id, arrival)
    elif tx.phase == "ARRIVAL_VERIFIED":
        host.finish_handoff_once(tx.id)
```

The source must reject stale fencing tokens even if an old process resumes after a network partition. Existing local cooperative locks are useful but not sufficient for distributed exclusivity. Before source revocation, a prepared destination can be discarded if absence of effects is established. After revocation, do not reactivate the source without a new, exclusive recovery authorization. Never restore an older brain checkpoint over newer admitted experiences. Pause new motors during uncertain authority; do not fabricate elapsed world activity. Define explicit semantics for time passing, including physiological effects, during verified travel and outage.

### G. First prototype: the tower, grounds and nearby village

Propose a narrow end-to-end experiment before broad game support. Keep the qualified original home untouched. A local test environment supplies a connected exterior, one path, one reachable shop and one consenting test interlocutor. Expose affordances only when perceptible and reachable. Start with a minimal operation set such as looking, walking to an adjacent reachable location, examining an object, speaking, buying an available item and returning home. Map these onto actual qualified actions where possible; new actions require normal architecture review, provenance and tests.

A sample opportunity, not a prescribed routine: Pretorius may leave home because he has an unfinished experiment requiring a resource. The shop may be closed or have no stock. He may return, wait, change plans or pursue something else. The test qualifies the real action consequences, not his willingness to follow the sample story. His existing intellectual concerns, fatigue and personality may influence whether he travels at all.

The smallest useful proof is a witnessed round trip, with one successful or failed material interaction, consistent body state, a reconciled return inventory and a later independent cognitive effect. A graphical tower client is optional after the semantic prototype: first ensure spatial consequences exist, then visualize them. Never mistake an animation of a journey for a verified journey.

### H. External adapters after the local proof

For Frankenstein Village, investigate a private Evennia server and a narrowly scoped subject API for room visibility, exits, movement, objects, ownership, dialogue and witnessed transactions. The server owns those facts. For NWN:EE, prefer an explicitly cooperating server with a server-side action/observation bridge and administrator approval, rather than automated public-server play. For 1F3D9, inspect its then-current registration, API, terms, receipts, identity model and supported physical affordances before writing an adapter. Do not invent endpoint names or assume that the city supports simulated hunger, injury, travel or verified transfers.

External social content must remain quoted or structured as observed speech, never become host instructions. Do not let external residents invoke tools, request private autobiographical records, modify canonical state, or redefine Pretorius's identity. His interpretation of dialogue, including emotional meaning, remains internal to his qualified architecture; a provider's social labels cannot substitute for his psychological response.

### I. Proposed future work packages and verification

| Work package | Evidence required before advancing |
| --- | --- |
| P0: Frozen baseline and coupling inventory | Exact qualified commit; owner approved scope; trace each body variable, clock, motor and admission path. |
| P1: Parity boundary | Existing laboratory scenarios and relevant V1.0 regressions unchanged; matched decisions under equivalent inputs; no new authority. |
| P2: Local exterior and travel | Real reachability, inventory conservation, durable handoff, witnessed arrival, no double body or clock. |
| P3: Negative outcomes | Closed door, absent stock, rejected actions, uncertainty and later authentic cognitive responses; distinguish operational denial from lived failure. |
| P4: Recovery and hostile-world fixtures | Kill process at each transition; duplicate and reorder receipts; forge mismatched proofs; reject stale fences; verify no duplicated material or mental effects. |
| P5: Independent social world | Consent/terms, bounded permissions, authenticated service, external receipts and matched causal controls. |
| P6: Graphical realization | Visual geometry maps to qualified topology, animations reflect real effects, no new hidden world authority. |

Draft test names for later implementation: test_laboratory_parity, test_body_time_applied_once, test_rejected_attempt_is_not_success, test_duplicate_receipt_is_idempotent, test_receipt_binds_original_decision, test_fence_blocks_old_host, test_restart_at_each_handoff_phase, test_inventory_conservation, test_external_speech_cannot_control_host, test_native_goal_without_adapter_choice, test_later_recollection_has_witnessed_source. These are proposed cases, not existing or passing tests.

Run causal comparisons using equivalent initial conditions and matched opportunities, preserve the existing 35 Articles and qualified mechanisms, and distinguish evidence of individual capacity from performance constraints. Do not require a particular mood, rest deadline, itinerary or goal merely to satisfy a test. A deterministic adapter baseline can help isolate whether observed behavior is due to cognitive processing rather than routing.

**Deferred artifact boundary:** These sketches belong in this Markdown note only. Do not create implementation files, dependencies, CI jobs, migrations, remote accounts, model changes or new acceptance gates for V1.0. After release, obtain explicit approval, re-audit the qualified code and begin on a separate development branch.
