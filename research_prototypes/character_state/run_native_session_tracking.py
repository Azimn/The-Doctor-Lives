"""Real Pretorius source-driven PHASE session evolution (no fabricated events).

Engineering integration check: initial -> new commitment -> resolved.
Measures accurate presence/absence of a real status transition only, NOT
quality of any language-model output or independent world-action success.
"""
import json
from pathlib import Path
import tempfile

from doctor_lives.cognition import PretoriusBrain
from .adapter import snapshot_from_brain


def run() -> dict:
    with tempfile.TemporaryDirectory(prefix="phase-native-session-") as td:
        brain = PretoriusBrain(Path(td))
        initial, _ = snapshot_from_brain(brain)
        initial_memories = len(brain.store.memories())
        new_ref = brain.add_commitment(
            "Review the laboratory findings with Henry Frankenstein.",
            actor="Henry Frankenstein", importance=.85, due_tick=12,
        )
        middle, _ = snapshot_from_brain(brain)
        field_path = "session.commitment." + new_ref
        if initial.get(field_path) is not None:
            raise AssertionError("precondition failure")
        if middle.get(field_path) is None:
            raise AssertionError("live commitment absent from session layer")
        if middle.get(field_path).source_refs != ("commitment:" + new_ref,):
            raise AssertionError("source provenance lost")
        brain.resolve_commitment(
            new_ref, outcome="The review was deliberately closed in this research fixture.",
            kept=True,
        )
        last, _ = snapshot_from_brain(brain)
        if last.get(field_path) is not None:
            raise AssertionError("resolved commitment remained an open session obligation")
        if len(brain.store.memories()) != initial_memories:
            raise AssertionError("shadow layer manufactured new autobiographical memories")
        if initial.identity != middle.identity or middle.identity != last.identity:
            raise AssertionError("native invariant identity was edited")
        initial_persona = tuple(x for x in initial.fields if x.path.startswith("persona."))
        middle_persona = tuple(x for x in middle.fields if x.path.startswith("persona."))
        last_persona = tuple(x for x in last.fields if x.path.startswith("persona."))
        if not initial_persona == middle_persona == last_persona:
            raise AssertionError("session transition leaked into slow semantic persona")
        return {
            "schema": "pretorius.phase.native-session-engineering.v01",
            "claim": "state tracking integration only, not conversational improvement",
            "source_manifest": initial.manifest_digest,
            "initial_has_commitment": initial.get(field_path) is not None,
            "after_add_has_commitment": middle.get(field_path) is not None,
            "after_resolve_has_open_commitment": last.get(field_path) is not None,
            "static_initial_snapshot_stale_after_add": initial.get(field_path) is None,
            "immutable_root_all_three": initial.identity == middle.identity == last.identity,
            "persona_unchanged": initial_persona == middle_persona == last_persona,
            "snapshot_digests_differ": len({
                initial.fingerprint, middle.fingerprint, last.fingerprint,
            }) == 3,
            "no_new_autobiography": len(brain.store.memories()) == initial_memories,
            "world_outcome_independently_verified": False,
            "native_brain_state_committed": True,
            "shadow_canonical_modification": False,
        }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
