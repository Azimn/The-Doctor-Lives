"""Canonical store and owned admission controls, not a donor or live-world trial."""
import tempfile
import unittest
from pathlib import Path
from doctor_lives import PretoriusBrain
from doctor_lives.dream_retention import dream_accessibility
from doctor_lives.dream_resurfacing import select_fragment
from doctor_lives.tower_ipseity import TowerIpseity
from doctor_lives.phenomenology import PhenomenalMode, SubjectiveSourceKind
from test_brain import small_config

class DreamRetentionIntegrationTests(unittest.TestCase):
    def test_fades_without_erasing_source_and_fragment_requires_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            brain = PretoriusBrain(Path(tmp), neural_config=small_config())
            store = brain.store
            subject = TowerIpseity(brain)
            text = "I recall a dream: a lavender brass pendulum swings above a flooded library; the walls turn into feathers."
            digest = "a"*64
            tick = store.tick
            with store.transaction() as db:
                mid = store.add_memory(db,tick,text,"phantasmagorium:dream-recollection:"+digest,
                                       "dream_recollection","dreamed_not_lived",True,1.,False,.35,
                                       tags=("dream","fictional","nonfactual"))
                event = subject.event("Phantasmagorium",text,PhenomenalMode.RECOLLECTION,
                                      ("fixture-sleep",mid),attribution=SubjectiveSourceKind.DREAMED,external=True)
                subject.record(db,"imagination:"+digest,(event,),phase="imagination")
            original = store.get_memory(mid)
            self.assertIn(mid,[r["id"] for _,r in brain._ranked_memories(1000,query="lavender brass")])
            with store.transaction() as db:
                for _ in range(12):
                    store.advance_tick(db)
            tick = store.tick
            with store.transaction() as db:
                store.rehearse(db,mid,tick)
            self.assertEqual(store.get_memory(mid)["rehearsal_count"],0)
            with store.transaction() as db:
                store.rehearse(db,mid,tick,explicit_dream_reflection=True)
                store.rehearse(db,mid,tick,explicit_dream_reflection=True)
            self.assertEqual(store.get_memory(mid)["rehearsal_count"],1)
            with store.transaction() as db:
                for _ in range(80):
                    store.advance_tick(db)
            self.assertEqual(dream_accessibility(store.get_memory(mid),store.tick),0)
            before=store.digest()
            self.assertNotIn(mid,[r["id"] for _,r in brain._ranked_memories(1000,query="lavender brass")])
            row=store.get_memory(mid)
            fragment=select_fragment([row],subject.verify_history(),store.tick,"lavender brass")
            self.assertIsNotNone(fragment)
            self.assertIsNone(select_fragment([row],[],store.tick,"lavender brass"))
            self.assertEqual(store.digest(),before)
            with self.assertRaises(PermissionError):
                brain.think("mnemosyne_private_reflection",decision_text=fragment[2])
            self.assertEqual(store.digest(),before)
            reopened=PretoriusBrain(Path(tmp))
            self.assertEqual(reopened.store.get_memory(mid)["text"],original["text"])
            self.assertEqual(select_fragment([reopened.store.get_memory(mid)],TowerIpseity(reopened).verify_history(),reopened.store.tick,"lavender brass"),fragment)
