# Deferred Laboratory World Query Interface: three approved additions

**Recorded:** 2026-10-28
**Disposition:** APPROVED FOR THE POST-REDESIGN DESIGN BACKLOG ONLY.
**Build status:** NOT IMPLEMENTED. No adapter, query endpoints, additional subject data channel, persistent graph, production registration, world installation, or automatic migration is authorized by this note.

## Mandatory sequencing and gates

**V432.6B documented complete and independently reviewed** -> **canonical six-organ cognitive redesign accepted at its own gates** -> **Lab bookshelf and fix/verify acceptance, including physical book/source evidence** -> **isolated world-query adapter candidate** -> **matched controlled evaluation** -> only then consider adoption.

This text is not a merge instruction. It does not waive Oct. 24 next-instruction requirements, advance Phantasmagorium's proposed organoid status, mark a six-organ candidate integrated, install the 17 books into a live session, or change production `main`.

## The three recorded additions

### Q1. Selective typed world queries

Let Pretorius ask the Laboratory only for presently authorized, relevant spatial/object facts through a future *read-only* adapter. The proposed vocabulary is:

- `find_objects({label, attrs})`
- `read_node({node_id, attrs})`
- `get_child_node_names({parent_node_id, child_node_attrs})`
- `get_edges_for_node({node_id, relation})`

A future Laboratory-owned whitelist defines permitted properties and relations. Queries must be bounded, have structured not-found/unknown/unavailable responses, and may never perform movement, actuation, tool execution or authorization. Unsupported filters must not silently expand a query to the whole world. Unvisited rooms do not become omniscient observations. Graph contents are not pasted wholesale into the renderer.

### Q2. Partial knowledge with provenance

A bounded, provenance-bearing *known* graph is a view of personally acquired information, NOT the authoritative Lab state and NOT autobiographical memory. Each known field/edge should identify the external source/receipt, direct versus reported status, observed and verified ticks, and certainty/freshness. Unseen objects and unknown rooms remain unknown, and a stale entry is not deleted or silently made current. New partial views must not delete non-observed nodes or the contents of a held receptacle. Provenance must survive save/restart; the authoritative append-only spatial ledger remains outside the brain.

Pretorius's own notes may be separately labeled tentative claims and must never overwrite world facts. A future canonical persistence authority must own any durable known-graph state; no standalone organoid/adapter database.

### Q3. Verify before acting

A remembered or inferred location is a proposed aid to planning, NOT physical permission. Before a consequential action, the host must verify the currently relevant object identity, station/relations, world epoch, physical feasibility, freshness, and independently issued authorization. A query itself never authorizes action and cannot make an action legal. A physical action's true outcome may become subject-accessible only through approved Sensus/Ipseity first-person admission and protected evidence receipts.

### Irrevocable book knowledge boundary

A shelf or object query can give only authorized title/metadata/location/observed-state, **never unread page contents**. Page content enters only after real physical opening/reading and a source-verified page receipt through the established book path. A dream motif, hypothesis, or unverified narration is not a query authorization or world fact.

## Future acceptance conditions, not presently met

1. Negative tests: unvisited-room request, unknown method/attrs, malformed parameters, missing graph, stale object, adversarial prompt embedded in book metadata, unauthorized query/action, dream-provided fake sighting, direct page-leak attempt, ledger tamper, replay after restart. Fail-closed for authorization/security; structured errors for ordinary query parsing.
2. World/known-graph distinction survives process/brain restart, with no accidental removal from partial observation, and no standalone knowledge store.
3. Same starting world states, observations, model budget, timing and physical grants for **dump-all known graph**, **single-recall**, **four-verb selective-query** and **simple-controller/lesion controls**. External world/task outcome is the primary measure, not a policy label, prompt length, or anecdotal transcript.
4. Independent reviewer checks first-person admission, authorizer/effect separation, ledger custody, exact-head CI and measurable *task* improvement before considering integration.

## Provenance and scope

Source inspiration: *Memory–Environment Dual-Grounding for Embodied Agents*, Choi-JaeWoo/SceneQueryPlanner (Findings of EMNLP 2026), **survey only**; its ProcTHOR/Unity GPU benchmark was NOT executed or adopted. This is the general pattern of a typed spatial graph plus selective queries, amended with Pretorius's provenance envelope, not the adoption of a standard or their task-success numbers.

Existing source contracts still win: SUBJECTIVE_PERSPECTIVE_NORTH_STAR.md; FIRST_PERSON_SUBJECT_INTERFACE_CONTRACT.md; PHENOMENAL_PROJECTION_CONTRACT.md; PRETORIUS_COMPLETION_PLAN.md; docs/architecture/PRETORIUS_SIX_ORGAN_IMPLEMENTATION_GUIDE.md; Oct. 24 Lab supply source-boundary packet.

**Change control:** documentation-only research backlog. All implementation and status transitions require separate exact-source review after V432.6B and the cognitive redesign.