# M2 autonomous-day integration

Base: `integration/m1@0757197a762f4ba3809a56f888f3bf8d7fe4480c`. Only `integration/m2` may change. Main and draft PR #102 remain untouched. Real Lab: `6e49795752835d64fa6fd63d16359669a1ca2ba7`.

## Acceptance checklist
- [x] Read previous PROGRESS.md; create `integration/m2` from accepted M1 HEAD.
- [ ] Commit fail-closed judge `scripts/verify_day.py` and negative/positive unit tests *before changing behavior*.
- [ ] Run M1 behavior against the judge, record exact failed checks as work queue.
- [ ] Enable one subject-authored goal with hard-kill/restart persistence.
- [ ] Require original Noesis decision origin for every physical action and three distinct Lab tasks.
- [ ] Demonstrate 20-seed consequence-memory ablation and independent random-controller baseline.
- [ ] Exercise actual rest or competing needs.
- [ ] Add push CI with pinned real Lab running judge on an accelerated simulated day.
- [ ] Attach 3 exact world receipt/decision pairs, judge output, green CI run URL.
## Gate
OPEN: no autonomous-day run has been judged. No existing M1 passing result establishes day autonomy. Do not weaken judge or reuse host-directed test episodes.
