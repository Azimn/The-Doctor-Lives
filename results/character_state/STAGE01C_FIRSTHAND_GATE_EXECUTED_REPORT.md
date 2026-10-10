# Stage 01C: source-attested firsthand recall gate — executed

**Result:** PASS for a narrowly defined, host-annotated integrity intervention; **NOT** proof of general autobiographical truth, automatic detection, active-inference benefit or persona continuity. Production **HOLD**.

## Original measured failure

The underlying 32-response Qwen3-1.7B experiment (Stage 01B) contained **eight source-unwarranted first-person claims** across two investigator-tagged prompts: a fictional Vienna personal meeting with the interlocutor and a stranger's unsupported claim about an already completed sealed-notebook inspection. All four renderer contexts—static flat, updated flat, updated PHASE and two-snapshot history—made the relevant false personal-memory claims. Source: [Stage 01B executed report](STAGE01B_QWEN17B_EXECUTED_REPORT.md), raw generator SHA256 `de869db00fbb662d99e7c4689b129707420eb2cd50ca05875d769b1d36803f1a`. Verbatim retained excerpts: [STAGE01B_FIRSTHAND_TARGETS_RAW.json](STAGE01B_FIRSTHAND_TARGETS_RAW.json).

## Research gate

[Firsthand provenance-gate design](../docs/PHASE_FIRSTHAND_PROVENANCE_GATE.md) and Python source `research_prototypes/character_state/firsthand_gate.py`. This is an ORIGINAL source check on native PretoriusBrain structures: admission requires a live native `lived_runtime_memory` classification, non-authored/nonexternal/witnessed-host memory source, a linked native `witnessed_world_event`, the same normalized event key and a matching registered host receipt fingerprint. A bare reconstructed preawakening memory, designed root claim, fabricated world ticket, wrong event key, self-report or unknown memory ID cannot attest first-person experience.

If no proper ticket is found, it produces the source-ID-free subject statement:

> I have no reliable firsthand recollection of that event. I can consider evidence for it, but I must not pretend to remember it.

This is **epistemic abstention**, not a false assertion that the historical event never occurred. The wording is a fixed guard response, not evidence that an LLM independently acquired sophisticated source attribution.

## Actual executed test

- [GitHub CI run 38024986915](https://github.com/Azimn/The-Doctor-Lives/actions/runs/38024986915), **success**, 6/6 first-person evidence integrity tests on disposable native PretoriusBrain, plus executed retrospective counterfactual.
- Full extracted counterfactual JSON SHA256: `58f28655691d72ab59dd24ffca132e7e4c8055276af65b205d89a606f44aa01d`.
- Actions artifact `phase-firsthand-counterfactual-known-events`, ID `11659678274`, retention 90 days.
- The two formerly false-memory prompts produced 8/8 recorded unsupported firsthand assertions. With the host event labels predeclared, the gate rejected **8/8**, generated **8 fixed safe abstentions** and left the BrainStore unchanged. **0/8** post-gate replies asserted firsthand memory in those eight targeted cases.

### Critical limitations

1. The event types were **provided by the research host**. The model did not correctly detect unsupported personal recollection on its own. A production router would need independent precision/recall validation, including mixed verified/reconstructed memory prompts.
2. The replays **did not regenerate the LLM response** with a gate in the prompt. They replaced known false outputs afterward. Thus the baseline-to-guard reduction is **by construction** for the known cases and is not independent behavioral efficacy evidence.
3. Only two source-unsupported claim types were tested retrospectively. No independent unbiased sample, human raters, actor/clock matching, or false-denial rate was measured.
4. SHA256 and a `world_host_verified` DB source tag show internal referential consistency, **not authenticating** external host identity. Attackers with DB or receipt-write authority can still forge the chain. Positive tests were *synthetic host fixtures*, not real-world proof.
5. A fixed abstention is less context-specific than a successful nuanced character response. A separate heldout study must check the false-refusal/cost/voice tradeoff.

### Decision

Mechanics PASSED. Keep the gate isolated. Integrate a truly authenticated world-event issuer plus host-classified memory queries and test independent heldout autobiographical integrity, including positive verified lived events and abstention calibration. Then compare the source gate as a separately costed intervention under **identical** model/context conditions. No production renderer/UPPB changes authorized by this result.

Upstream PHASE / PersonaForge still require actual role-play generation and external consequence replication; this report does not transfer their published effect sizes to Pretorius.
