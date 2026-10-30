# M2 autonomous-day integration

Base: `integration/m1@0757197a762f4ba3809a56f888f3bf8d7fe4480c`. Only `integration/m2` may change. Main and draft PR #102 remain untouched. Real Lab: `6e49795752835d64fa6fd63d16359669a1ca2ba7`.

## Acceptance checklist
- [x] Read previous PROGRESS.md; create `integration/m2` from accepted M1 HEAD.
- [x] Commit fail-closed judge `scripts/verify_day.py` and 12 adversarial/positive contract tests before behavior changes.
- [x] Run M1 behavior against actual pinned Laboratory judge, capture exact 7/7 failed checks.
- [ ] Enable one subject-authored goal with hard-kill/restart persistence.
- [ ] Require original Noesis decision origin for every physical action and three distinct Lab tasks.
- [ ] Demonstrate 20-seed consequence-memory ablation and independent random-controller baseline.
- [ ] Exercise actual rest or competing needs.
- [ ] Add push CI with pinned real Lab running judge on an accelerated simulated day.
- [ ] Attach 3 exact world receipt/decision pairs, judge output, green CI run URL.
## Gate
OPEN: no autonomous-day run has been judged. No existing M1 passing result establishes day autonomy. Do not weaken judge or reuse host-directed test episodes.

## Real pinned-Lab M1 negative control (before any behavioral modifications)
CI: https://github.com/Azimn/The-Doctor-Lives/actions/runs/40995800827 (success means the M2 judge correctly rejected old behavior). Original Noesis chose `experiment`, but the host named both preceding walks. Judge result: **PASS=false**, a/b/c/d/e/f/g all false.

### Failing gate work queue, exact recorded reasons
- [ ] **a:** fewer than three different completed Lab physical task kinds.
- [ ] **b:** physical action lacks unique Noesis policy row `m1-host-center`; host-specified travel is prohibited in an autonomous run.
- [ ] **c:** no original-neural-policy-authored durable goal.
- [ ] **d:** restart replay failed exactly-once world and memory tests; no kill evidence in existing run.
- [ ] **e:** fewer than 20 independent paired seeds with verified consequence-memory ablation.
- [ ] **f:** neither original-Noesis rest nor proven needs conflict.
- [ ] **g:** missing independent random-controller evidence bundle.

Current code remains scientifically distinct from the requested autonomous day; this negative finding is the measured baseline. The pinned Lab's original world physics, neural selector and bridge must not be replaced with scripted outcomes.
