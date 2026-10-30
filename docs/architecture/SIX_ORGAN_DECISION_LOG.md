# Six-organ architecture decisions and review ledger

Status: **D1 proposed decisions, not accepted ADRs**. Each record requires independent review and exact-head evidence before a runtime/default migration. Effective baseline: Doctor `main` `784cff39d58a7fe46bb5e4ffc16e0284e6663c78`.

## ADR NOESIS-001: one recurrent selector

**Proposed:** keep `PretoriusBrain` and its existing 4,096-unit recurrent substrate as the single behavioral-policy owner. Host motive/action queues may OFFER candidates, not claim independent action choice. Candidate donor learning mechanisms remain isolated and matched-controlled. **Open test:** repeated verified-world choice vs host-chosen action, post-lesion, unchanged renderer. **Affected gates:** D2/D6/D7/D9, Completion Gate 5A.

## ADR IPSEITY-001: one admitted subject boundary

**Proposed:** Doctor UPPB's typed `PhenomenalEvent`/`SubjectFrame` factory constructs epistemically bounded subject-native representations; reviewed Synthetic Ipseity adapter may provide durable access admission and bounded renderer outbox. These are distinguishable stages of ONE authorized subject-access contract, never alternative raw-content backdoors. **Not yet decided:** whether to make the external donor mandatory in production or implement the same durable access contract natively. Current `DoctorSyntheticIpseitySession` is opt-in and its own documentation warns of bypass. Do not silently change default. **Open tests:** engineer-only state leak, internal reflection, thought privacy, memory encoding/recall and renderer alternatives. **Gates:** D2/D3/D4.

## ADR MEMORY-001: acquisition and protected truth

**Proposed:** the existing canonical BrainStore is sole Pretorius mutable-memory writer; independently verified evidence, classifications, Lab receipts and objective provenance remain separate protected records. New acquisition should retain first-person experience with private source/epoch links; recollection is newly admitted and cannot upgrade testimony to observation. **Open decision:** field map and whether v7 schema safely represents distinct subjective acquisition and later recollection without migration. No schema edits before exact write-path audit and fixture-backed rollback test. **Gates:** D2/D4.

## ADR CORPUS-001: physical state stays with provider

**Proposed:** Laboratory owns position, environment physics, body/rhythm reality, inventories, and action receipts. Corpus provides constrained typed interoceptive and affordance views; a future robot provider owns its own sensor/actuator evidence with a separate safety controller. Doctor host supplies no unaudited physics fact and never issues unvetted motor commands. **Open tests:** stale epoch, unavailable actions, world-source mismatch, provider parity with retained identity. **Gates:** D5/D6/D10.

## ADR AFFECT-001: no duplicate emotion engine

**Proposed:** begin with existing bounded needs/appraisal influences in `cognition.py` as a logical domain, but do not relabel them a separately completed organ. Distinguish bodily readings (Corpus), felt representation (Ipseity) and appraisal (Affectus). **Open tests:** affect lesion, motivation/feasibility orthogonal control, no double counting. **Gate:** D6.

## ADR SENSUS-001: conditional donor admission

**Proposed:** keep current Laboratory observation route. Accept a reversible, pinned standalone Sensus adapter only if matched information experiments demonstrate binding improvement without false scene merges or leaks. Do not import donor memory/identity. **Open test:** contradictory simultaneous channels vs direct adapter control. **Gate:** D8.

## ADR RUNTIME-001: one host clock and ordered handovers

**Proposed:** host owns scheduling, transaction boundaries and retry deduplication. Engineer UTC, Laboratory simulation ticks, brain ticks and future robot sensor timestamps remain explicitly typed and never merged by inference. No implicit relabeling of host-triggered action as native initiative. **Gates:** D2/D7/D10.

## ADR CAUSAL-001: distinctions must be experimentally useful

**Proposed:** promote a boundary only when it protects authority or supports a testable independent lesion/influence. A shared mechanism need not be moved into another directory to qualify; six identical wrapper classes alone prove nothing. **Gates:** D9/D11.

## ADR ROBOT-001: mock only, default deny

**Proposed:** no physical robot actuation in this migration. Demonstrate only a mock adapter with refused untrusted commands, unique epoch and source, safety grant external to language generation. Real hardware requires a separate safety and security review. **Gate:** D10.
