"""Bound-subject admission regression; synthetic inputs are not physical evidence."""
import tempfile
import unittest
from pathlib import Path
from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.models import Experience
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.tower_ipseity import TowerIpseity

class TowerUniversalIngressTests(unittest.TestCase):
    def test_all_projected_channels_enter_one_history_before_cognition(self):
        with tempfile.TemporaryDirectory() as temp:
            cfg=dict(DEFAULT_CONFIG)
            cfg.update(neurons=96,sensory_dim=48,avg_recurrent_degree=8,
                       input_degree=4,action_population_size=6,seed=1842)
            port=PretoriusBrainPort(Path(temp),neural_config=cfg)
            brain=port.brain
            with brain.store.transaction() as db:
                brain.store.set_meta("small-tower:world-binding-v1",'{"test_fixture":true}',db)
            subject=TowerIpseity(brain)
            events=(
                ({"channel":"user","actor":"Visitor","text":"The rain is cold."},"told","Sensus"),
                ({"channel":"world","text":"The road is flooded."},"told","Sensus"),
                ({"channel":"tool","percept":"The scale reads ten grams."},"read","Sensus"),
                ({"channel":"body","signal":"fatigue","level":0.8},"self_observed","Corpus"),
            )
            for event,attribution,organ in events:
                result=port.ingest(event)
                history=subject.verify_history()
                admitted=[(e,i) for e in history for i in e["content"]
                          if e["phase"]=="acquisition" and result["memory_id"] in i["source_refs"]]
                self.assertEqual(len(admitted),1)
                entry,item=admitted[0]
                self.assertEqual(item["text"],result["ingress"]["subject_text"])
                self.assertEqual(item["organ"],organ)
                if organ!="Corpus":
                    self.assertEqual(item["attribution"],attribution)
                if result["thought"]:
                    thought=next(e for e in history if e["key"].endswith("thought:"+result["thought"]["id"]))
                    self.assertLess(entry["sequence"],thought["sequence"])
            before=brain.store.digest()
            with self.assertRaises(PermissionError):
                brain.ingest(Experience("I see a fabricated world.",source="world"))
            self.assertEqual(brain.store.digest(),before)
            thought=brain.think("test-owned-context",decision_text="I wonder what caused the rain.")
            audit=thought["state_pressure"]["ipseity_context"]
            entries={e["key"]:e for e in subject.verify_history()}
            self.assertEqual(entries[audit["key"]]["sha256"],audit["sha256"])
            self.assertEqual(entries[audit["key"]]["content"][0]["text"],"I wonder what caused the rain.")
