"""Boundary and native-policy contribution, without world side effects."""
import tempfile
from pathlib import Path
import unittest
from doctor_lives.portable_doctor_adapter import advise_doctor
from doctor_lives.portable_life_policy import Opportunity, PortableLifePolicy


class FakeSourceVerifiedBridge:
    def __init__(self):
        self.requests = 0
    def observe(self):
        return {'subject': {'inner': 'I see an unfinished task.', 'spoken_aloud': None},
                'memory_id': 'mem_verified_source_1'}
    def request_cognition(self, trigger):
        self.requests += 1
        if trigger != 'portable_life_advisory': raise AssertionError('Wrong trigger')
        return {'action_scores': {'explore': .75, 'persist': .25},
                'policy_decision_id': 'native-policy-1'}


class DoctorAdapterTests(unittest.TestCase):
    def test_real_shape_brain_inputs_are_bounded_and_advisory(self):
        with tempfile.TemporaryDirectory() as path:
            bridge = FakeSourceVerifiedBridge()
            policy = PortableLifePolicy(Path(path)/'habits.db')
            choices = [Opportunity('a','lab','investigate',{'curiosity': .5}),
                       Opportunity('b','social','assist',{'duty': .6})]
            r = advise_doctor(bridge, policy, choices,
                              motives={'curiosity': .6, 'duty': .3},
                              native_to_strategy={'explore': 'investigate', 'persist': 'assist'})
            self.assertEqual(r['advice'].strategy, 'investigate')
            self.assertEqual(r['observed_memory_id'], 'mem_verified_source_1')
            self.assertEqual(bridge.requests, 1)
            with policy._db() as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM receipts').fetchone()[0], 0)

    def test_requires_first_person_source(self):
        with tempfile.TemporaryDirectory() as path:
            bridge = FakeSourceVerifiedBridge()
            bridge.observe = lambda: {'subject': {'inner': 'health=8','spoken_aloud':None},'memory_id':'mem_1'}
            with self.assertRaises(ValueError):
                advise_doctor(bridge, PortableLifePolicy(Path(path)/'a.db'),
                              [Opportunity('a','lab','investigate',{'curiosity':1})],
                              motives={'curiosity':.8}, native_to_strategy={'explore':'investigate'})

    def test_mismatched_subject_keys_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            bridge = FakeSourceVerifiedBridge()
            bridge.observe = lambda: {'subject': {'inner': 'I see a letter.', 'telemetry': 4},'memory_id':'m'}
            with self.assertRaises(ValueError):
                advise_doctor(bridge, PortableLifePolicy(Path(path)/'a.db'), [],
                              motives={}, native_to_strategy={})
