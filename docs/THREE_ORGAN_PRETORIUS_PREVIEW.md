# Three-component Pretorius preview (research integration; no production promotion)

**Branch:** `integration/three-organ-pretorius-preview`, deliberately
stacked on draft Doctor [PR #57](https://github.com/Azimn/The-Doctor-Lives/pull/57).
The upstream standalone Sensus and Synthetic Ipseity repositories remain
unchanged. This is a real `PretoriusBrainPort` / actual Pretorius identity
running in a **separate state directory named `three-organ-preview`**,
not a synthetic pretend brain. The render transport is still the proven
`DoctorSyntheticIpseitySession` durable organ.

### One coherent path

```text
Authenticated typed shell Percepts
  -> Sensus v0.1 candidate scene (source/evidence preserved, conflicting bind veto)
  -> Doctor's approved ingress (only uncontested observed facts or reported User speech)
  -> Doctor's existing concern ledger (verified observed conflicts become UNCERTAINTY only)
  -> existing Doctor state-to-policy bridge (opt-in recall/continue/ask/defer deliberation)
  -> Doctor host-bound recollection controller (only on selected recall)
  -> Doctor factory-controlled typed SubjectFrame
  -> durable Synthetic Ipseity v0.9.11
  -> subject-only local Ollama renderer
```

**No actor is granted credibility by Sensus type-checking alone.** The host
must supply a separately authenticated `trusted_source_refs` allowlist.
This is a trusted Python boundary, not cryptographic authentication or a
sandbox. The standalone CLI can authenticate local User speech only:
`--say` is `Evidence.REPORTED` and does *not* become visual or
physical proof. Direct observed Percepts require a real upstream trusted
sensor/simulation host using `ThreeOrganPretoriusPreview.cycle()`.
Inferred, remembered, and interoceptive raw streams are never laundered
into world observations or autobiographical fact. Any contested object
is withheld altogether. Two contradictory, confirmed observed claims
may open a **source-marked epistemic concern** (not a memory) and the
Doctor's deliberative policy may elect to recall, without host-forcing
a question.

Every `publish_*` still passes a genuine Doctor typed frame through the
actual durable Ipseity host. The model sees only first-person text, not
Sensus scene IDs, raw evidence class, hidden policy scores, source hashes,
authorization tokens, or protected action data. The engineer receives a
separate receipt (never feed it to the renderer).

### Exact development dependencies

Doctor and Ipseity integration are available on Doctor main, but
Ipseity's 0.9.11 package is **optional**, not installed by plain
`pip install -e .`. Sensus has no pip packaging definition, so its
pinned repository root must be exposed to Python without copying its
implementation into Doctor. On the preview host:

```bash
git clone https://github.com/Azimn/synthetic-ipseity.git ../synthetic-ipseity
git -C ../synthetic-ipseity checkout --detach e2d1dc3978c952e59d270a29e84704c8a1fe264a
python -m pip install -e ../synthetic-ipseity
git clone https://github.com/Azimn/Sensus-Communis-Artificialis.git ../Sensus-Communis-Artificialis
git -C ../Sensus-Communis-Artificialis checkout --detach 802e459ee68950414347d5fa324484c034f57b81
python -m pip install -e .
PYTHONPATH="../Sensus-Communis-Artificialis:." doctor-lives-three-organ-preview \
  --state ./three-organ-preview --enable-experimental-preview --say "Good evening."
```

In Windows PowerShell, instead set `$env:PYTHONPATH` to the
Sensus checkout's absolute path (and run `python -m doctor_lives.three_organ_preview`
with the same `--state`, `--enable-experimental-preview`, and `--say`
arguments). This uses local Ollama default `qwen3:1.5b`; no paid API.

For a verified multi-channel test, run the pinned-donor CI job in
`.github/workflows/three-organ-pretorius-preview.yml`. It uses
small disposable neural configurations and tests conflict-to-recall,
model input isolation, source class preservation, missing permission
rejection, and pending-outbox recovery.

### Scientific and operational constraints

- **Live policy is opt-in preview only.** Synthetic research v0.1 still
  refuses Pretorius by default. The live preview uses a different
  `policy_version` and only consumes independently verified Sensus
  conflicts; it never sees hypothetical gold answers.
- The prior independent policy benchmark **lost 13/18 vs 14/18** against
  the strong simple gap rule. Successful plumbing does not reverse that
  negative result or prove model-selected autonomy.
- The Sensus donor explicitly says cross-project implementation should
  wait until after its Oct 15–23 blinded ablation period. This branch
  runs a **parallel experimental preview** with no donor mutations,
  reclassification of existing results, or production adoption. It
  must not contaminate independent blinded evaluation.
- The fresh local preview host has no end-to-end journal for replaying
  a scene-to-Doctor admission after a crash. Pending Ipseity delivery
  can be resumed safely but a crash between Sensus scene and durable
  outbox admission still requires operator intervention. Do not
  deploy as an unattended production host.
- Sensus short-lived object files are in-memory only. They reset on
  re-invoking the preview CLI; continuity of cross-process object
  re-identification is not yet guaranteed.
- The repo's existing production `doctor-lives-local` CLI and
  canonical state remain unmodified. Do not merge this branch into
  `main` until explicit independent security review, adoption gates,
  crash/replay transaction design and blinded downstream comparison.
