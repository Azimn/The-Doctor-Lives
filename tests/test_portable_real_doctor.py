"""Pinned independent Laboratory required: real Doctor, real world receipt."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

HAS_LAB = importlib.util.find_spec('pretorius_lab') is not None

@unittest.skipUnless(HAS_LAB, 'Run using pinned Pretorius-Laboratory dependency')
class RealDoctorPhysicalTransfer(unittest.TestCase):
    def test_advisor_executes_only_through_existing_authorized_bridge(self):
        from doctor_lives.portable_life_policy import PortableLifePolicy, Opportunity
        from doctor_lives.portable_doctor_adapter import advise_doctor
        from doctor_lives.home_choice_probe import _shortest_route
        from doctor_lives.chassis import PretoriusBrainPort
        from doctor_lives.lab_home_bridge import DoctorHomeBridge
        from doctor_lives.neural import DEFAULT_CONFIG
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            world = SpatialHabitat.create(root/'house.db')
            HomeLife(world).initialize()
            rhythm = DailyRhythm(world)
            rhythm.initialize()
            cfg = dict(DEFAULT_CONFIG)
            cfg.update(neurons=128, sensory_dim=64, avg_recurrent_degree=8,
                       input_degree=4, action_population_size=8)
            doctor = PretoriusBrainPort(root/'doctor', neural_config=cfg)
            bridge = DoctorHomeBridge(doctor, SubjectPort(world), authorized=True)
            policy_path = root/'doctor'/'portable_procedures.db'
            policy = PortableLifePolicy(policy_path)
            choices = [Opportunity('laboratory:experiment', 'laboratory', 'investigate',
                                   {'curiosity': 1.0}),
                       Opportunity('laboratory:rest', 'laboratory', 'recover',
                                   {'wellbeing': 1.0})]
            before = rhythm.audit_state()['experiments']
            advice = advise_doctor(bridge, policy, choices,
                                   motives={'curiosity': .9, 'wellbeing': .1},
                                   native_to_strategy={'explore':'investigate'})
            self.assertEqual(advice['advice'].key, 'laboratory:experiment')
            self.assertTrue(advice['neural_policy_decision_id'])
            self.assertTrue(advice['observed_memory_id'].startswith('mem_'))
            self.assertEqual(rhythm.audit_state()['experiments'], before,
                             'An advisory decision must not secretly act')
            station = bridge.subject.embodied.verify()['station']
            for n, stop in enumerate(_shortest_route(station, 'station:bench')):
                bridge.act('walk', event_id=f'portable-walk-{n}', station=stop)
            bridge.act('experiment', event_id='portable-work-1')
            self.assertEqual(rhythm.audit_state()['experiments'], before+1)
            def verify_receipt(receipt, action_key, succeeded):
                bridge.subject.verify()  # verify complete authoritative world chain
                with world._open() as db:
                    row = db.execute("SELECT event_hash FROM rhythm_events WHERE event_id=?",
                                     ('portable-work-1',)).fetchone()
                    return bool(row and receipt == row[0] and
                                action_key == 'laboratory:experiment' and
                                succeeded == (rhythm.audit_state()['experiments'] > before))
            with world._open() as db:
                receipt = db.execute("SELECT event_hash FROM rhythm_events WHERE event_id=?",
                                     ('portable-work-1',)).fetchone()[0]
            self.assertTrue(policy.record_outcome(source_receipt=receipt,
                                action_key='laboratory:experiment',
                                cue='uncompleted_research', strategy='investigate',
                                succeeded=True, verify_receipt=verify_receipt))
            self.assertFalse(policy.record_outcome(source_receipt=receipt,
                                action_key='laboratory:experiment',
                                cue='uncompleted_research', strategy='investigate',
                                succeeded=True, verify_receipt=verify_receipt))
            self.assertEqual(PortableLifePolicy(policy_path).habit('uncompleted_research',
                                                                    'investigate'), (1,0))

if __name__=='__main__': unittest.main()
