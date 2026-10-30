# M1 integration progress

Target: `integration/m1`. Production `main` is unchanged at the verified starting SHA `784cff39d58a7fe46bb5e4ffc16e0284e6663c78`. Real-world source: `Azimn/Pretorius-Laboratory@6e49795752835d64fa6fd63d16359669a1ca2ba7`.

## Integration checklist
- [x] Verify `main` HEAD and existing `integration/m1` state.
- [x] Start integration branch at draft PR #89 head `61814d22077b37dc177e2e26a32d6b8bd400deaf`.
- [ ] Incorporate PR #96 after #89, preserving all changes.
- [ ] Incorporate PR #97 after #96, preserving all changes.
- [ ] Incorporate PR #98 after #97, preserving all changes.
- [ ] Run and pass original brain suite (`python -m unittest discover -s tests -v`).
- [ ] Run and pass paired real Laboratory bridge at the pinned SHA.
- [ ] Run and pass native Noesis, experience-to-action, restart and offline-installed host smoke.
- [ ] Confirm every applicable workflow/check is green on the integration head.
- [ ] Record final CI run URLs and observed pass counts below.

## CI verification
Pending new integration branch run. Prior PR run results do not substitute for exact integration-head validation.

## Known blockers
None identified. No tests are to be skipped, deleted or weakened. Do not merge into main.
