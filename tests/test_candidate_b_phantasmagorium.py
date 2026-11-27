"""Regression checks for Candidate B's opt-in Phantasmagorium boundary."""
from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

from doctor_lives.store import BrainStore
from doctor_lives.phantasmagorium_bridge import PhantasmagoriumBridge, verify_archive


class PinnedOrganoidBoundaryTests(unittest.TestCase):
    def test_refuse_missing_or_unreviewed_zip_and_disabled_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = BrainStore(root / "brain.sqlite3")
            bad = root / "donor.zip"
            bad.write_bytes(b"unreviewed")
            with self.assertRaises((PermissionError, ValueError)):
                verify_archive(bad)
            with self.assertRaises(PermissionError):
                PhantasmagoriumBridge(store, bad, enabled=False)
            with self.assertRaises(FileNotFoundError):
                PhantasmagoriumBridge(store, root / "missing.zip", enabled=True)

    def test_tower_refuses_unverified_provider(self):
        from doctor_lives.tower_phantasmagorium import sync_tower_phantasmagorium
        with self.assertRaises(PermissionError):
            sync_tower_phantasmagorium(None, object(), None, "invented", None)

    def test_fancy_motif_requires_original_fiction_labels(self):
        from doctor_lives.tower_phantasmagorium import verified_fancy_motifs
        fragment = {"epistemic_status": "dreamed_not_lived", "marked": True,
                    "factual_memory_eligible": False, "world_fact_authority": False,
                    "tool_authority": False, "motif": "a clock made of clouds"}
        result = dict(fragment, epistemic_status="hypothetical_only", fragments=[fragment])
        self.assertEqual(verified_fancy_motifs(result), ("a clock made of clouds",))
        with self.assertRaises(PermissionError):
            verified_fancy_motifs(dict(result, fragments=[dict(fragment, world_fact_authority=True)]))

    def test_retrieval_requires_exact_owned_imagery_and_withholds_legacy_report(self):
        from hashlib import sha256
        from types import SimpleNamespace
        from doctor_lives.tower_ipseity import TowerIpseity
        from doctor_lives.tower_phantasmagorium import LATEST_FANCY, retrieval_motifs, fancy_line
        from doctor_lives.lab_phantasmagorium import _digest, _stable
        from doctor_lives.phenomenology import PhenomenalMode, SubjectiveSourceKind
        from doctor_lives.phantasmagorium_bridge import DONOR_SHA256
        from doctor_lives import PretoriusBrain, Experience
        from test_brain import small_config
        with tempfile.TemporaryDirectory() as tmp:
            brain = PretoriusBrain(Path(tmp), neural_config=small_config())
            store = brain.store
            subject = TowerIpseity(brain)
            source = "virtual-world:small-tower:fixture:action:reading"
            observation = "virtual-world:small-tower:fixture:observation:next"
            self.assertEqual(retrieval_motifs(store, observation), ())
            # Controlled provenance fixture, not a live Tower qualification.
            mid = brain.ingest(Experience("I read a folio.", source=source))["memory_id"]
            memory = store.get_memory(mid)
            digest = sha256(source.encode()).hexdigest()
            key = "phantasmagorium:tower-event:" + digest
            motif = "a clock made of clouds"
            report = {"source_sha256": digest, "source_memory_id": mid,
                      "source_event_id": memory["source_event_id"], "operation": "fancy",
                      "donor_sha256": DONOR_SHA256, "world_authority": False,
                      "factual_memory_eligible": False, "motor_authority": False,
                      "fictional_motifs": [motif]}
            def seal():
                with store.transaction() as db:
                    store.set_meta(key, _stable(report), db)
                    store.set_meta(LATEST_FANCY, _stable({"key": key, "source": source,
                                                        "report_sha256": _digest(report)}), db)
            seal()
            with self.assertRaises(PermissionError):
                retrieval_motifs(store, observation)
            with self.assertRaises(PermissionError):
                retrieval_motifs(store, observation, subject=TowerIpseity(SimpleNamespace(store=object())))
            self.assertEqual(retrieval_motifs(store, observation, subject=subject), ())
            self.assertEqual(subject.verify_history(), [])
            event = subject.event("Phantasmagorium", fancy_line(motif), PhenomenalMode.INTERNAL_THOUGHT,
                                  (mid,), attribution=SubjectiveSourceKind.IMAGINED, external=True)
            with store.transaction() as db:
                admission = subject.record(db, "imagination:" + digest, (event,), phase="imagination")
            report["ipseity_admission_sha256"] = admission["sha256"]
            seal()
            before = store.digest()
            self.assertEqual(retrieval_motifs(store, observation, subject=subject), (motif,))
            self.assertEqual(store.digest(), before)
            brain.save() if hasattr(brain, "save") else None
            reopened = PretoriusBrain(Path(tmp))
            self.assertEqual(retrieval_motifs(reopened.store, observation, subject=TowerIpseity(reopened)), (motif,))
            report["fictional_motifs"] = ["a mirror made of clouds"]
            seal()
            with self.assertRaisesRegex(PermissionError, "owned admission"):
                retrieval_motifs(store, observation, subject=subject)

    def test_missing_archive_not_silently_ignored_after_activation(self):
        from unittest.mock import patch
        from doctor_lives.tower_phantasmagorium import require_archive, CURSOR
        with tempfile.TemporaryDirectory() as tmp:
            store = BrainStore(Path(tmp) / "brain.sqlite3")
            with patch.dict(os.environ, {"PRETORIUS_PHANTA_DONOR": ""}):
                self.assertIsNone(require_archive(store))
                with self.assertRaises(FileNotFoundError):
                    require_archive(store, required=True)
                with store.transaction() as db:
                    store.set_meta(CURSOR, '{"epoch":"test","cursor":0}', db)
                with self.assertRaises(FileNotFoundError):
                    require_archive(store)

    def test_canonical_snapshot_and_fiction_boundary(self):
        from doctor_lives.lab_phantasmagorium import _snapshot, _digest, _nonfactual
        import json
        blank = _snapshot(None, "world-1")
        self.assertEqual(blank["nights"], 0)
        sealed = json.dumps({"payload": blank, "sha256": _digest(blank)})
        self.assertEqual(_snapshot(sealed, "world-1"), blank)
        with self.assertRaises(PermissionError):
            _snapshot(sealed, "world-2")
        packet = {"epistemic_status": "dreamed_not_lived", "marked": True,
                  "factual_memory_eligible": False, "world_fact_authority": False,
                  "tool_authority": False}
        self.assertTrue(_nonfactual(packet, "dreamed_not_lived"))
        for key in ("factual_memory_eligible", "world_fact_authority", "tool_authority"):
            self.assertFalse(_nonfactual(dict(packet, **{key: True}), "dreamed_not_lived"))

    @unittest.skipUnless(os.environ.get("PRETORIUS_PHANTA_DONOR"),
                         "Exact v0.5 donor must be explicitly provided")
    def test_actual_persistent_facade_two_nights_and_fancy(self):
        from doctor_lives.lab_phantasmagorium import _run, _nonfactual
        from doctor_lives.phantasmagorium_bridge import DONOR_SHA256
        archive = verify_archive(os.environ["PRETORIUS_PHANTA_DONOR"])
        request = {"pin": DONOR_SHA256, "files": {}, "day": 1, "seed": 42,
                   "cues": ["I read a page of a book about the moon."],
                   "op": "fancy", "scene": {"initial_scene": {"entities": [
                       {"id": "book", "kind": "book", "properties": {"form": "bound volume"}},
                       {"id": "page", "kind": "page", "properties": {"words": "The moon is cold."}},
                   ], "relations": []}, "max_fragments": 4}}
        fancy = _run(archive, request)
        self.assertGreater(len(fancy["result"]["fragments"]), 0)
        self.assertTrue(_nonfactual(fancy["result"], "hypothetical_only"))
        from doctor_lives.tower_phantasmagorium import verified_fancy_motifs
        self.assertTrue(verified_fancy_motifs(fancy["result"]))
        request.update(files=fancy["files"], op="night", seed=123)
        first = _run(archive, request)
        self.assertTrue(_nonfactual(first["result"], "dreamed_not_lived"))
        self.assertTrue(_nonfactual(first["recall"], "dreamed_not_lived"))
        request.update(files=first["files"], day=2, seed=333)
        second = _run(archive, request)
        self.assertTrue(_nonfactual(second["result"], "dreamed_not_lived"))
        self.assertEqual(second["result"]["day"], 2)
        self.assertEqual(second["result"]["id"], first["result"]["id"] + 1)
        self.assertIn("dream_ecology/dream_journal.json", second["files"])

    @unittest.skipUnless(os.environ.get("PRETORIUS_PHANTA_DONOR"),
                         "Exact v0.5 donor must be explicitly provided")
    def test_real_original_donor_fancy_and_dream_source_boundary(self):
        archive = Path(os.environ["PRETORIUS_PHANTA_DONOR"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = BrainStore(root / "brain.sqlite3")
            organoid = PhantasmagoriumBridge(store, archive, enabled=True)
            scene = {"entities": [
                {"id": "raven", "kind": "bird", "properties": {"color": "black"}},
                {"id": "stone", "kind": "rock", "properties": {"material": "granite"}},
            ], "relations": []}
            imagination = organoid.fancy(scene, seed=7, max_fragments=2)
            dream = organoid.single_night_probe(
                day=1, seed=7, experience={"place": "study", "person": "a scholar"})
            self.assertFalse(imagination["lived_fact"])
            self.assertFalse(dream["lived_fact"])
            self.assertFalse(dream["longitudinal_dream_continuity_proven"])
            self.assertEqual(dream["result"]["epistemic_status"], "dreamed_not_lived")
            self.assertFalse(dream["result"]["factual_memory_eligible"])
            reopened = BrainStore(root / "brain.sqlite3")
            self.assertIsNotNone(reopened.meta(
                "phantasmagorium:probe:" + imagination["record_id"]))
            self.assertIsNotNone(reopened.meta(
                "phantasmagorium:probe:" + dream["record_id"]))
            import json
            for result in (imagination, dream):
                opaque = reopened.meta(
                    "phantasmagorium:probe:" + result["record_id"])
                parsed = json.loads(opaque)
                self.assertFalse(parsed["subject_admitted"])
                self.assertTrue(parsed["no_autobiographical_content"])
                self.assertNotIn('"result"', opaque)
                self.assertNotIn('"entities"', opaque)
            # Not even a generated *dream* can silently become lived memory.
            self.assertEqual(len(reopened.memories()), 0)


if __name__ == "__main__":
    unittest.main()
