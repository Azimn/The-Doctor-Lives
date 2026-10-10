# Issue #53: First Living-Laboratory Vertical Integration

**Disposition:** disposable engineering research; not a production release or claim of superior cognition.

**Exact authorities:** The-Doctor-Lives main base 56aab5493ef48cdb560881a138b2277ca6ebcce0; Pretorius-Laboratory main 93d19671f7666b2996e6fcad211c5e6509336466. The laboratory world, book and observation ledgers are imported from this real pinned repository. No alternate brain, copied simulator, production subject archive, Village state, or Sensus implementation is opened or altered.

## Reproduction (Python 3.12)

From The-Doctor-Lives working tree at this research branch, using an otherwise empty scratch directory:

~~~sh
git clone https://github.com/Azimn/Pretorius-Laboratory.git _lab
git -C _lab checkout 93d19671f7666b2996e6fcad211c5e6509336466
python -m pip install -e . -e ./_lab
python -m unittest discover -s tests -p 'test_living_laboratory_integration.py' -v
python tools/run_living_lab_demo.py \
  --output-root /tmp/issue53-fresh-research \
  --fixture _lab/fixtures/DEMO_BOOK_007.json \
  --report /tmp/issue53-raw-report.json
~~~

The runner refuses to overwrite a populated root or pre-existing evidence report. Each stage is a separate Python interpreter. All databases are disposable; even the physical seed is forked to sandbox mode. The dedicated CI workflow pins the laboratory SHA and publishes its raw trial output as a GitHub Actions artifact.

## Source, action and subjective boundaries

An outside research operator breaks the beaker in the sandbox, creating an environmental problem. That preparatory action is never credited to Pretorius. The laboratory produces a qualitative observation with a receipt. The Doctor Lives subject projector and accepted SubjectFrame present only natural-language observations and admissible autobiography, not engineer world-state data or exact metric coordinates.

The real PretoriusBrain recurrent and state-policy controller is called on the supplied subject text and the unchanged high-level goal to make broken glass safe. A declared deterministic host-side affordance adapter translates its existing abstract policy scores into concretely typed object operations, rank-scored alongside larger hand-defined relevance weights. This is not a new organ, but it is an important experimental limitation: the neural model has NOT independently learned object-level action semantics, and success cannot be attributed to the neural policy alone.

Physical execution is exclusively via the laboratory commit authority, with optimistic revision guards. Action outcomes are independently replay-verified against persisted host events. A verified consequence is projected into a Pretorius lived-memory entry, with the event ID, hash and world epoch stored as source evidence. A research-only admission index in the disposable brain SQLite database binds that proof to this subject's specific admitted memory. Raw foreign autobiography, unsupported memory strings, reused receipt IDs, or unverified host results cannot unlock object affordances. The index is an evidentiary control, not a replacement autobiography database.

An independently persistent lab world and a brain checkpoint are reopened in fresh processes. A later choice to inspect the floor is only available once Pretorius has an indexed recollection of gathering fragments. Inspecting the corner then produces its own receipt and admission; only then is that location eligible for the next action. A host-authorized placement is scored against verified physical state, not generated dialogue.

## Controls and limits

The episode-withheld condition uses an exact post-intervention world backup paired with the original preepisode brain checkpoint. Removing that episode also removes recurrent learning and any other episode updates, so this intervention is not a selective memory-only lesion. It is an engineering sensitivity check. The strong simple nonneural controller is supplied the same post-intervention host observation and allowed inspection/action ports; it can solve the task without private character state. Its success is important negative evidence for unique neural utility, not a failed engineering result.

The additional foreign-epoch control uses a third copy of the same post-collection world and a fresh copy of the initial brain. A valid physical collection receipt from another isolated laboratory epoch is injected directly into that disposable brain as an adversarial fixture. The subject-frame adapter and action-eligibility gate refuse that unindexed foreign record. The internal Pretorius policy may still retrieve the injected record because direct trusted BrainStore writes bypass the research ingress contract. Accordingly this is a boundary smoke test, not a claim that all hostile direct database writes can be made cognitively inert, and not a blinded matched autobiography-shuffle trial.

The persistent book test uses the real three-page synthetic research edition. Host operations are scripted and must be labeled that way. Only delivered, checksum-bound page one is processed by the real cognitive policy and admitted as lived reading. Page two is delivered by the host but not admitted to Pretorius memory; page three is not delivered. The persistent physical ribbon bookmark independently returns to page one after book closure and reopening. This distinguishes external source availability, a page delivery and an actual autobiographical record. It does NOT yet demonstrate autonomous book-tool selection.

The current deterministic relevance weighting strongly influences selected actions; report this honestly. Tests can establish successful continuation, causal input sensitivity, authorized actions, verified state, denied writes, correct source boundaries and abstention. They cannot demonstrate neural superiority, open-ended character autonomy, consciousness, long-duration continuity, or generalization to independent held-out goals. No external language model was run. Actual Pretorius recurrent policy execution is real; host physics and the book-contract script are deterministic by design, not substitutes for model evidence.

Prior lessons retained: Stage 04 signed host results, Stage 06 and Stage 07 eligibility wins alongside goal irrelevance, E5 failed task-level action maps, Noetic MATRIX-005 control equality, and Synthetic Ipseity as a separate future contract. No donor architecture is imported simply to improve appearances.

## Review gate

This remains draft PR #54 linked to Issue #53, on one reversible research branch. Required follow-up includes blind holdouts, source adjudication, well-matched shuffled-memory intervention, calibrated abstention and failure runs, additional crash/rollback testing, model substitution, and a promotion-security review. Preserve failed trials and null results. Canonical production main is not to be updated without the existing release, migration and rollback review gates. Portfolio authority: https://github.com/Azimn/Artificial-Life-Research-Journal/issues/23.
