# Pretorius Dream Architecture: experimental traceable surrealism

Status: owner-approved research design, not a V1.0 production requirement or active runtime feature. This supplements the symbolic guide and Cabinet of Fancy. It is deliberately separate from production dream retention and associative resurfacing. Original Phantasmagorium v0.5 donor SHA-256: 31e31c0a87e155c072227b086cf012a5f1dcb5aa2de51f676b909ae8255454a8. Do not modify or replace the pinned original archive.

## Objective

Generate surprising, visually specific, occasionally profound imaginative experiences while maintaining private reconstructable engineering traces. The goal is traceable surrealism, not historical or doctrinal accuracy, forced symbolism, or a prescribed narrative. Thelema-inspired correspondences are a symbolic guide, not factual or religious authority. Null output is valid.

## Experimental enhancements

| Enhancement | Purpose |
|---|---|
| Expanded symbolic graph | Increase diversity of associative routes |
| Designer-authored correspondences | Permit intentionally strange or beautiful associations without historical justification |
| Personal symbolic learning | Let authentic experience and admitted reflection shape associations |
| Broader cue vocabulary | Include perceptual, domestic, emotional and project-related cues |
| Visual transformation operators | Compose memorable scenes rather than merely naming symbols |
| Trace logging | Preserve replayable causal chains |
| Separate stochastic streams | Isolate graph walking, transformation, selection, rare omens and ordinary dream randomness |
| Baseline comparison | Compare pinned donor, shuffled edges, uniform randomness and feature-off |

## Symbolic graph and cues

Nodes and edges have stable identifiers and explicit origin: inherited, authored, learned or generated. Each edge stores edge ID, source node, target node, relation type, origin, graph version, optional weight and enable/disable status. Association strength never means factual certainty. Retain graph versions and hashes; learned or generated overlays do not mutate the donor bytes.

Eligible cues include laboratory tools and materials, household objects, metals, animals, bodily sensations, odors and perfumes, sounds, colors, numbers, shapes, textures, lighting, weather, time of day, motion, remembered people, current projects, concerns and unresolved emotions. Use only authorized cues and latent associations; do not expose private metadata or hidden world facts. A cue may yield nothing.

## Visual transformation operators

Bounded transformations include enlargement, miniaturization, inversion, fusion, material substitution, repetition, displacement to another setting, impossible movement or scale, metamorphosis, anthropomorphism, fragmentation, mirrored duplication, animated still objects, recursive containment, shifting architecture, environmental mood conversion and impossible spatial relations. Operators add visual specificity while respecting candidate size, depth and resource budgets.

## Personal symbolic learning

A smell may become associated with a person; an object with grief, comfort or scientific ambition; a room with an emotional tone. Preserve authentic source references, revision history, contradictions and contextual dependence. Multiple contradictory meanings are allowed. Do not infer lived events from imagined scenes, force associations, or treat subjective interpretation as objective source truth.

## Private trace and random streams

For each selected symbolic candidate record canonical subject ID, episode/scene ID, simulation tick, cue IDs, source references where applicable, graph version/hash, node path and edge IDs, independent random stream identifiers, state snapshots or replay parameters, transformation IDs, final candidate representation, insertion outcome and conscious admission receipt if accessed. Include algorithm version and budget for reproducibility. Keep rejected or null status where needed for audit. Trace access is engineer-only; Pretorius need not know the causal chain.

Use independent seeded streams for graph walk, transformation, selection, rare-omen selection and unrelated dream randomness. Derive stream seeds from a stable versioned episode seed and distinct domain labels; never reseed the original donor or change ordinary dream randomness when an experiment is disabled.

## Suggested generation contract (pseudocode only)

```python
def generate_symbolic_candidate(cues, context, graph, rng_bundle, budget):
    trace = begin_private_trace(
        subject_id=context.subject_id,
        cue_ids=cues.ids,
        graph_hash=graph.hash,
        rng_state=rng_bundle.snapshot(),
        algorithm_version=ALGORITHM_VERSION,
    )
    path = bounded_associative_walk(
        cues=cues,
        graph=graph,
        rng=rng_bundle.graph_rng,
        max_depth=budget.max_depth,
        max_branches=budget.max_branches,
    )
    if path is None:
        trace.finish(status="no_candidate")
        return None
    candidate = compose_visual_scene(
        path=path,
        rng=rng_bundle.transform_rng,
        context=context,
        operators=budget.allowed_operators,
    )
    trace.record_path(path)
    trace.record_candidate(candidate)
    return opaque_nonfactual_handle(candidate), trace.finish(status="candidate")
```

Latent candidates remain unconscious until promoted. Any conscious dream, imagined scene or recollection requires the existing Synthetic Ipseity natural-language first-person admission into the one canonical hash-chained history before recurrent processing. A candidate handle alone grants no conscious, factual or motor access. Preserve objective provenance and allow subjective ambiguity. Preserve natural forgetting: prior reflections and diary evidence remain independent traces, and meaningful cue-driven fragments may resurface without reconstructing the complete archival dream.

## Evaluation and promotion

Compare with the exact pinned donor, shuffled-edge graph, uniform random baseline and feature-off behavior using matched authenticated cues, matched seeds and isolated experimental copies. Predeclare sample sizes, budgets, evaluation measures and acceptance criteria before running. Measure visual specificity, surprise, variety, repetition rate, replayability, computational cost, preservation of null cases and nonfactual provenance. Historical fidelity is not an evaluation dimension. Report negative results and counterexamples. No claim of improvement before empirical results.

Acceptance boundary: never authenticate world facts, grant motor authority, fulfill goals, count as practice, change inventory or physics, overwrite source provenance, or leak hidden guide structure into subjective introspection. The experiment may influence imaginative content only. No new organ, separate subject, or duplicate memory authority.

Promotion requires demonstrated improved visual richness or variety, reproducibility, no ownership bypass, no hidden authority promotion and no R4 regression against the unchanged 520 authenticated receipt capacity observation and 3600-second infrastructure watchdog. Feature-off behavior must preserve the production baseline. No promotion into V1.0 without separate owner authorization. Production and scientific qualification remain distinct.
