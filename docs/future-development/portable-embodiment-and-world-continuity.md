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
