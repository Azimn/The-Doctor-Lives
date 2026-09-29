# Deep-History matched-stimuli control

This record preserves the completed matched-stimuli production control required by
[Issue #4](https://github.com/Azimn/The-Doctor-Lives/issues/4).

## Frozen baselines

- Pre-deep-history production baseline: `88e36ba354b8d55f196c47f7dd0358b3b8bf9297`
- Deep-History v1 production baseline: `7be60ed46add7c74359b322cc033aa7dfabb08e8`

The harness used exact isolated checkouts of both SHAs, fresh state per stimulus, the same
deterministic small recurrent configuration (seed 1842), the same three seeded lived
experiences, and the same six probe stimuli. The frozen baselines did not provide
query-conditioned historical retrieval, so each probe was ingested as external content
before measuring the bounded 14-item cognitive view.

Harness: `tools/deep_history_matched_control.py`

Workflow: `.github/workflows/deep-history-matched-control.yml`

## Execution provenance

- Workflow run: `36518895031`
- Workflow head: `f818fd3b6f0afe48031549d3bc0d73452a0915d5`
- Artifact ID: `11011604024`
- Artifact name: `deep-history-matched-control-f818fd3b6f0afe48031549d3bc0d73452a0915d5-36518895031`
- Artifact ZIP SHA-256: `a210d5bcfc5190191a3a5e16ce7a45c97457f1c5589541c3615442c02eb218d0`
- Artifact size: 13,482 bytes

The workflow completed successfully. Full baseline JSON, comparison JSON, retrieval
provenance, result summary, and SHA256SUMS were uploaded by the workflow. The
non-expiring repository copy of the per-stimulus comparison is
`results/deep_history_matched_control/comparison.json`; the executable harness remains
the authoritative way to regenerate the complete artifact bundle.

## Aggregate observations

| Measure | Pre-deep-history | Deep-History v1 |
|---|---:|---:|
| Mean relevant inherited recall | 2.000 | 2.667 |
| Mean irrelevant inherited intrusion | 11.000 | 14.000 |
| Mean lived-memory displacement | 0.333 | 1.000 |

Selected-action divergence was `0 / 6`, and mean action-score L1 distance was
`0.000000`.

The production characterization therefore shows a tradeoff in this frozen test:
Deep-History v1 increased mean relevant inherited recall, but it also increased
irrelevant inherited intrusion and displaced all three seeded lived memories from the
bounded workspace. The effect was not uniform across relevant probes: Ingolstadt
relevant recall decreased from 1 to 0, homunculi increased from 4 to 6, and Creature
increased from 1 to 2.

No action-policy difference was observed under these six matched probes. That result is
limited to this harness and these frozen baselines.

## Interpretation boundary

This is a production characterization of two frozen software baselines. It is not a
confirmatory cognitive-science experiment, does not establish human-like memory, and
does not validate the historical truth of any autobiographical claim.

The result is diagnostic evidence for the v2 production requirement that inherited
history be epistemically typed, query-relevant, bounded, and prevented from silently
crowding out lived runtime memory. It is not a license to retune the frozen baseline
comparison after seeing its outcome.
