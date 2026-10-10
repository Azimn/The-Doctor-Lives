# The Portable Laboratory — permanent research habitat and optional dual-presence world

**Architecture note v0.1 — 2026-10-10. Status: proposed, not implemented or deployed.**

**Canonical technical home:** The Doctor Lives / Pretorius research. **Future adapter:** [Frankenstein Village](https://github.com/Azimn/frankenstein-village). Tracking design in the companion village note `research/portable-pretorius-laboratory-dual-presence-2026-10-10.md`. Neither the game server nor the renderer becomes Pretorius's mind.

## Decision to preserve

The separate SQLite laboratory world introduced in Stage 04 should remain a **long-lived, reusable cognitive test environment**, rather than be discarded after each battery. A possible later destination is Pretorius's permanent private laboratory in Frankenstein Village. A more flexible option is that the **same logical laboratory exists both offline and online**: an external laboratory service owns physical experiments and state, a local copy can be used without a network, and an Evennia location displays committed lab state and forwards authorized player actions. This is a proposed architecture, **not** an announcement that a cross-world sync service, laboratory room or deployed Pretorius exists today.

This follows [Stage 04's source-attested event host](../research_prototypes/character_state/world_host_ledger.py) and [Stage 05's objective PHASE-versus-flat action null](../results/character_state/STAGE05_QWEN_WORLD_ACTIONS_EXECUTED_REPORT.md): granting a model more structured personal text did not make it act sensibly; physical authority and typed action eligibility must be host-owned. Preserve the negative result. Never make unsourced renderer output into lived history.

## Three separable things

1. **Pretorius's mind:** cognition, phenotype, reconstructed preawakening archive, subjective P5 source monitoring, private diary and learned habits belong to the Pretorius process. Moving a laboratory does not migrate the mind into Evennia; logging in/out does not clone or reset autobiographical identity.
2. **Laboratory world:** rooms, apparatus, contents, calibrated instruments, grants, physical state, experiment episodes and consequential actions belong to a versioned laboratory authority. This can be an external service when online and a local implementation when offline.
3. **Frankenstein Village representation:** an Evennia room/doors/objects that *project* an admitted laboratory state and provide in-world interactions. The Village retains authority over its public world, nearby rooms, player masks, village time, economy, consent/moderation and its own event ledger. A mirrored laboratory fact is linked to an original host event, never duplicated as independent evidence.

**Do not deploy two independent authoritative copies of the same mutable laboratory.** A synced replica is not a second reality. Prefer one logical lab with stable `lab_id`, explicit authority ownership by object/operation, and one accepted sequence of mutations. In online mode the laboratory host serializes lab-owned actions; Evennia consumes authorized events. The game owns village-side doors, arrivals, public effects and participation, so it may reject a lab transition's proposed *game effect*.

## Online/offline reconciliation contract (draft, not an implemented API)

A host-signed, append-only successful laboratory event should eventually carry:
- `lab_id`, `world_epoch` (fork/reset protection), `event_id` (globally unique/idempotent), `issuer`, `actor_id`, `actor_authority`/mask reference and permitted operation, subject privacy/visibility class;
- `schema_version` (data contract), `ruleset_version` (state-machine semantics), `content_manifest_digest` (rooms/objects definitions), and `base_revision` / `committed_revision` for optimistic consistency;
- precondition digests and before/after **lab-owned** state digests, sequenced event/previous event hash, effective scene/time mapping, evidence digest, status `accepted` or `rejected` (rejection never masquerades as a successful world event);
- partner consent/authorization references, issuer signature/MAC and key epoch, with no secret keys, private cognition, or user conversation text in the public mirror.

**Version alignment is not just Git version alignment:** keep (A) schema/ruleset compatibility, (B) content assets/room contract, (C) actual world state revision and event cursor, and (D) village publication offset separate. A code commit with the same label does not guarantee equal state.

### When connected
1. Read lab authority's signed checkpoint/cursor and Evennia's applied cursor. Validate schema/ruleset/manifest and expected world epoch.
2. Send authenticated lab commands to the authority; only it can grant/deny a change. Village actions involving other players or village property require village-side authorization too.
3. The accepted lab event is applied once to the Village projection through an idempotent bridge and, if relevant, an attributed reference in the Village world-event ledger. Reconnect and restart replay must be safe.

### When offline
1. Preserve an independently checkable local snapshot at `base_revision`; mark the mirror **offline at revision N**.
2. Local simulation may proceed, but new events enter a **pending offline branch**, carrying parent revision, actor and source-clock. Pretorius may privately remember events genuinely experienced in that offline sandbox, with an explicit *offline/provisional* source class; these are **not** automatically witnessed village experiences or village canon.
3. On reconnection, validate the parent and replay proposed actions against current authoritative state, real grants, actual consent and village-side restrictions. Accept, reject, or negotiate each conflict; **never use timestamp-based last-writer-wins or silent overwrite**.
4. A rejected event remains an auditably rejected local episode. Retconning an external experiment or another player's action to match offline memories is forbidden. Prefer a new compensating event or fork the offline lab into an explicitly separate research world when reconciliation is impossible.
5. Do not import offline item creation, player injury, player presence, private rooms, stock changes or third-party interactions into the shared MUD without fresh authoritative validation. The lab cannot replay the shared world's past.

**Practical default:** Begin with online lab authority + read-only Village projection. Offline mode is a clearly labeled *experimental fork or pending-write queue*, not active multi-master. Consider a lease/single-writer ownership handoff only after crash, partition and multi-actor race tests. No background network sync should be promised in Stage 04/05.

## Version handshake and compatibility

On attach, compare `lab_id`, `world_epoch`, schema major/minor, ruleset version, manifest SHA256, snapshot hash, and event cursor. Major mismatch or divergent object state => **quarantine read-only**; upgrade through tested, reversible migrations. Minor additive fields must have defaults and forward-compatible readers; do not quietly invent source claims. A replay/deduplication journal keyed by origin event ID prevents echo loops between the lab and Village. Source revocations and prior-event corrections are new auditable actions; do not rewrite old event history. The lab's independent journal and Village's existing `world_event_ledger` remain linked but have distinct event IDs, authority and privacy policies.

Time needs its own rule: wall-clock time, offline experimental ticks and the Village's 1890s in-fiction day/hour are **not interchangeable**. An online placement must choose a lawful village timestamp when the bridge accepts an event; never retroactively create observations for villagers who were not present.

## Migration and game-canon gates

The Village Bible currently says Pretorius **does not appear at launch**; only his dark leased shop and OPENING SOON sign exist. That lore remains canon. No auto-opening shop, lab access, physical teleportation, homunculus disclosure or automatic character arrival follows from registering this plan. If the laboratory later becomes playable, explicitly approve its site, visibility, story entrance, actor permissions and publication policy in the Village. An existing open game-room door can serve as a view into the externally hosted lab **without transferring authority over Pretorius's cognition**.

The portable lab should not become a global server-side thinker or require a permanent LLM loop. Physics and authorization can be deterministic and inexpensive, with cognition on demand. The ability to test Pretorius offline remains useful even if Village hosting or its invited-alpha release is delayed. No new server/hosting spending is authorized by this proposal.

## Suggested staged implementation and go/no-go checks

- **L0 — Research habitat:** turn Stage 04's disposable fixture into a persistent named lab instance with snapshots, state inspection, backups, migration tests and non-destructive world reset/fork; run Stage 05/06 experiments against cloned start checkpoints. No Village code.
- **L1 — Shared event envelope:** versioned schema + deterministic replay, idempotent imports, scene-state checksums, strict source attestation, event-epoch and privacy fixtures. One canonical spec, both repos pin a contract hash.
- **L2 — Offline rehearsal:** queue/rebase/deny outcomes; test network partitions, conflicting laboratory writes, duplicate/cross-epoch replay, lost acknowledgements, restart restore and failed migration. No accidental canon.
- **L3 — Evennia projection adapter (shadow):** replay accepted lab events into a non-public development room and the canonical village ledger with origin reference. Test that mirroring cannot spawn items twice, open a private door, spoof actor identity or leak secret knowledge.
- **L4 — Explicit canon/play gate:** village keeper decision on Pretorius's entrance/shop, visible laboratory location, participation and player consent; then alpha players and independent AI agents may interact with the same location under the standard mixed-world compact. Do not require this for invited-alpha Gate A/B.
- **L5 — Two-view soak:** long-running online/offline rollback/sync drills, host split-brain refusal, signed actor consent changes, independent human/AI players, backup-and-restore, and source-preserving migration to a real externally hosted service. Fail closed on unresolved divergence.

Acceptance is **not** “both UIs look alike”; it is identical authority-accepted state + event revision, exactly-once visible effects, no false lived memories, respected private/public disclosure, and recoverable divergence. This is a design note only; these acceptance gates have NOT been executed.

## Open architectural choice

**Recommended future default:** a *single portable laboratory authority with two views*—research/offline simulation and village online projection—rather than building two laboratory databases that each believe they are canon. If offline events eventually need promotion into shared canon, require explicit server acceptance and, for other people's effects, actual consent. This maximizes reuse of one laboratory physics/action system while respecting both experimental provenance and the Village's shared-world autonomy.
