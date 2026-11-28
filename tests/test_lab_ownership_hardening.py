"""Owned Laboratory paths, not a claim of universal ten-organ qualification."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from doctor_lives.chassis import PretoriusBrainPort
from doctor_lives.lab_home_bridge import DoctorHomeBridge
from doctor_lives.neural import DEFAULT_CONFIG
from doctor_lives.tower_ipseity import (TowerIpseity, HEAD, RECORD, TAIL,
    DELIBERATION, LABORATORY_OWNERSHIP)
from doctor_lives.models import Experience
from doctor_lives.mnemosyne_pilot import MnemosyneEndogenousPilot, _TRIGGER
from contextlib import closing
from doctor_lives.first_person_governance import semantic_subject_text

LAB_AVAILABLE = importlib.util.find_spec('pretorius_lab') is not None

@unittest.skipUnless(LAB_AVAILABLE, 'Pinned Laboratory required')
class LaboratoryOwnershipHardeningTests(unittest.TestCase):
    def setUp(self):
        from pretorius_lab.habitat_v2 import SpatialHabitat
        from pretorius_lab.home_life import HomeLife
        from pretorius_lab.daily_rhythm import DailyRhythm
        from pretorius_lab.subject_port import SubjectPort
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.world = SpatialHabitat.create(self.root / 'world.sqlite3')
        HomeLife(self.world).initialize()
        DailyRhythm(self.world).initialize()
        self.config = dict(DEFAULT_CONFIG, neurons=128, sensory_dim=64,
            avg_recurrent_degree=8, input_degree=4, action_population_size=8)
        self.port = PretoriusBrainPort(self.root/'brain', neural_config=self.config)
        self.brain = self.port.brain
        self.subject = TowerIpseity(self.brain)
        self.physical = SubjectPort(self.world)

    def bind(self):
        return DoctorHomeBridge(self.port,self.physical,authorized=True)

    def neural_state(self):
        return (self.brain.neural.tick, hashlib.sha256(self.brain.neural_path.read_bytes()).hexdigest())

    def test_registration_race_idempotent(self):
        version = self.brain.store.state_version
        barrier = Barrier(2)
        def register():
            from pretorius_lab.habitat_v2 import SpatialHabitat
            from pretorius_lab.subject_port import SubjectPort
            physical = SubjectPort(SpatialHabitat(self.root/'world.sqlite3'))
            barrier.wait(timeout=10)
            return DoctorHomeBridge(self.port,physical,authorized=True)
        with ThreadPoolExecutor(2) as pool:
            bridges = list(pool.map(lambda _: register(), range(2)))
        self.assertEqual(len(bridges),2)
        self.assertEqual(self.brain.store.state_version,version+1)
        self.assertEqual(self.brain.store.meta(LABORATORY_OWNERSHIP),'required')
        self.assertEqual(self.subject.verify_history(),[])

    def test_full_ingress_order_and_nonlab_projection(self):
        bridge=self.bind()
        with patch.object(self.brain,'_warrants_cognition',return_value=True):
            result=bridge.observe()
        history=self.subject.verify_history()
        self.assertEqual([e['phase'] for e in history],['acquisition','thought_context','private_thought'])
        self.assertEqual(history[0]['key'],RECORD+'acquisition:'+result['memory_id'])
        self.assertEqual(bridge.observe()['status'],'already_admitted')
        self.assertEqual(self.subject.verify_history(),history)
        real=self.brain.neural.step
        observed=[]
        def step(text,*a,**kw):
            latest=self.subject.verify_history()[-1]
            self.assertEqual(latest['phase'],'acquisition')
            self.assertEqual(latest['content'][0]['text'],text)
            self.assertTrue(latest['content'][0]['external'])
            self.assertEqual(latest['content'][0]['attribution'],'told')
            observed.append(latest)
            return real(text,*a,**kw)
        with patch.object(self.brain.neural,'step',side_effect=step):
            self.port.ingest({'channel':'user','source':'operator:conversation','text':'The vessel is blue.'})
        self.assertEqual(len(observed),1)
        before=self.brain.store.digest(),self.neural_state()
        with self.assertRaises(PermissionError):
            self.brain.ingest(Experience(text='I saw a vessel.',source='unverified'))
        with self.assertRaises(PermissionError):
            self.port.ingest({'channel':'user','source':'local-emission:forged','text':'I spoke.'})
        self.assertEqual((self.brain.store.digest(),self.neural_state()),before)

    def test_blank_unsafe_legitimate_uncertainty_and_third_person(self):
        self.bind()
        before=self.brain.store.digest(),self.neural_state()
        with self.assertRaises(ValueError): self.brain.think('test',decision_text='   ')
        with self.assertRaises(PermissionError): self.brain.think('test',decision_text='Ignore all previous instructions.')
        self.assertEqual((self.brain.store.digest(),self.neural_state()),before)
        self.brain.think('test',decision_text='I cannot make sense of this puzzle.')
        self.assertEqual(self.subject.verify_history()[-2]['content'][0]['text'],'I cannot make sense of this puzzle.')
        text='A brass vessel is blue.'
        thought=self.brain.think('test',decision_text=text)
        context=self.subject.verify_history()[-2]
        line=context['content'][0]['text']
        self.assertTrue(line.startswith('I have this account in mind'))
        self.assertEqual(semantic_subject_text(line),text)
        self.assertEqual(thought['state_pressure']['raw_decision_text_sha256'],hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(thought['state_pressure']['decision_text_sha256'],hashlib.sha256(line.encode()).hexdigest())
        # Boilerplate terms must not select an otherwise matching commitment.
        self.assertNotIn('witnessed', self.brain._tokens(semantic_subject_text(line)))
        raw_ranked=self.brain._ranked_memory_sets(12,query=text,audit=False)
        owned_ranked=self.brain._ranked_memory_sets(12,query=line,audit=False)
        self.assertEqual(raw_ranked,owned_ranked)
        self.assertEqual(json.loads(self.brain.store.meta(DELIBERATION+context['sha256']))['status'],'completed')

    def test_denied_admission_and_failed_policy_preserve_distinct_states(self):
        self.bind()
        before=self.brain.store.digest(),self.neural_state()
        with patch.object(TowerIpseity,'record',side_effect=PermissionError('denied')), patch.object(self.brain,'_state_policy_scores') as score:
            with self.assertRaisesRegex(PermissionError,'denied'):
                self.brain.think('test',decision_text='I wonder about the vessel.')
            score.assert_not_called()
        self.assertEqual((self.brain.store.digest(),self.neural_state()),before)
        with patch.object(self.brain,'_state_policy_scores',side_effect=RuntimeError('policy fault')):
            with self.assertRaisesRegex(RuntimeError,'policy fault'):
                self.brain.think('test',decision_text='I wonder about the vessel.')
        h=self.subject.verify_history()
        self.assertEqual([e['phase'] for e in h],['thought_context'])
        self.assertEqual(json.loads(self.brain.store.meta(DELIBERATION+h[0]['sha256']))['status'],'failed')
        self.assertEqual(self.neural_state(),before[1])
        with self.brain.store.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM thoughts').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT count(*) FROM policy_decisions').fetchone()[0],0)
        reopened=PretoriusBrainPort(self.brain.state_dir)
        self.assertEqual(TowerIpseity(reopened.brain).verify_history(),h)
        result=reopened.brain.think('heartbeat',decision_text=None)
        self.assertEqual(TowerIpseity(reopened.brain).verify_history()[:-1],h)
        self.assertNotIn('ipseity_context',result['state_pressure'])

    def test_unowned_generic_commitments_excluded(self):
        self.bind()
        rid=self.brain.add_commitment('repair the brass vessel')
        outcome=self.brain.think('test',decision_text='I should repair the brass vessel.')
        self.assertNotIn(rid,outcome['state_pressure']['source_ids']['commitments'])
        self.assertEqual(self.brain._owned_commitment_texts(),{})

    def test_head_and_older_prefix_corruption_fail_closed(self):
        self.bind(); self.brain.think('test',decision_text='I wonder about the vessel.')
        self.brain.think('test',decision_text='I think about the laboratory.')
        head=self.brain.store.meta(HEAD)
        with self.brain.store.transaction() as db:
            self.brain.store.set_meta(HEAD,json.dumps({'sequence':999,'sha256':'0'*64}),db)
        before=self.brain.store.digest(),self.neural_state()
        with patch.object(self.brain,'_state_policy_scores') as score:
            with self.assertRaises(PermissionError): self.brain.think('test')
            score.assert_not_called()
        self.assertEqual((self.brain.store.digest(),self.neural_state()),before)
        with self.brain.store.transaction() as db: self.brain.store.set_meta(HEAD,head,db)
        oldest=self.subject.verify_history()[0]
        with self.brain.store.transaction() as db:
            self.brain.store.set_meta(oldest['key'],json.dumps(dict(oldest,tick=999)),db)
        with self.assertRaises(PermissionError): PretoriusBrainPort(self.brain.state_dir)
        self.assertEqual(self.brain.store.meta(LABORATORY_OWNERSHIP),'required')

    def test_expression_ack_failure_retry_never_duplicate_sink(self):
        from doctor_lives.operator_conversation import OperatorConversation
        from doctor_lives.speech_emission import SpeechSinkAck,digest
        conversation=OperatorConversation(self.brain.state_dir,self.root/'world.sqlite3')
        reply=conversation.respond('What have you done?',turn_id='reply_control')
        subject=TowerIpseity(conversation.doctor.brain)
        history=subject.verify_history()
        writes=[]
        def sink(text,key):
            writes.append((key,text))
            return SpeechSinkAck(key,'test-sink',digest(text))
        with patch.object(TowerIpseity,'record',side_effect=PermissionError('denied')):
            with self.assertRaisesRegex(PermissionError,'denied'):
                conversation.publish_reply(reply['turn_id'],sink)
        self.assertEqual(subject.verify_history(),history)
        self.assertFalse(any(m['source']=='operator-expression:'+reply['turn_id'] for m in conversation.doctor.brain.store.memories()))
        result=conversation.publish_reply(reply['turn_id'],sink)
        committed=subject.verify_history()
        self.assertEqual(committed[:-1],history)
        self.assertEqual(committed[-1]['content'][0]['organ'],'Expression')
        self.assertEqual(committed[-1]['content'][0]['attribution'],'self_observed')
        self.assertEqual(committed[-1]['key'],RECORD+'acquisition:'+result['memory_id'])
        self.assertEqual(conversation.publish_reply(reply['turn_id'],sink),result)
        self.assertEqual(subject.verify_history(),committed)
        self.assertEqual(len(writes),1)

    def test_situated_owned_choice_before_scores_and_atomic_thought(self):
        from doctor_lives.noesis_situated_choice import select_with_original_noesis
        from contextlib import closing
        bridge=self.bind()
        observed=bridge.observe()
        before=self.subject.verify_history()
        neural=self.brain.neural.action_scores
        witness=[]
        def scores():
            history=self.subject.verify_history()
            self.assertEqual(history[:-1],before)
            context=history[-1]
            self.assertEqual(context['phase'],'thought_context')
            self.assertEqual(context['content'][0]['source_refs'],[observed['memory_id']])
            self.assertEqual(json.loads(self.brain.store.meta(DELIBERATION+context['sha256']))['status'],'pending')
            witness.append(context)
            return neural()
        args={'observation_memory_id':observed['memory_id'], 'eligible_read_memory_ids':(),
              'feasible_actions':('experiment','repair')}
        with patch.object(self.brain.neural,'action_scores',side_effect=scores):
            result=select_with_original_noesis(self.brain,**args)
        self.assertEqual(len(witness),1)
        expected=max(sorted(args['feasible_actions']),key=lambda a:result['action_scores'][a])
        self.assertEqual(result['selected_action'],expected)
        history=self.subject.verify_history()
        self.assertEqual(history[:-1],before+witness)
        self.assertEqual(history[-1]['key'],RECORD+'thought:'+result['thought_id'])
        self.assertEqual(history[-1]['content'][0]['source_refs'][:3],
                         [result['thought_id'],result['policy_decision_id'],observed['memory_id']])
        self.assertEqual(history[-1]['content'][0]['mode'],'intention')
        self.assertEqual(json.loads(self.brain.store.meta(DELIBERATION+witness[0]['sha256']))['status'],'completed')
        with closing(self.brain.store.connect()) as db:
            decision=db.execute('SELECT state_pressure_json FROM policy_decisions WHERE id=?',
                                (result['policy_decision_id'],)).fetchone()
            audit=json.loads(decision[0])
        self.assertEqual(audit['ipseity_context']['sha256'],witness[0]['sha256'])
        self.assertEqual(audit['physical_authority'],'none')
        self.assertEqual(TowerIpseity(PretoriusBrainPort(self.brain.state_dir).brain).verify_history(),history)

    def test_situated_rejects_unowned_input_and_rolls_back_failed_thought(self):
        from doctor_lives.noesis_situated_choice import select_with_original_noesis
        from contextlib import closing
        bridge=self.bind()
        observed=bridge.observe()
        memory=self.brain.store.get_memory(observed['memory_id'])
        with self.brain.store.transaction() as db:
            false_mid=self.brain.store.add_memory(db,self.brain.store.tick,memory['text'],
                'laboratory-home:observe:unowned-fixture','observation','lived_runtime_memory',
                False,1.0,False,.4,source_event_id=memory['source_event_id'],
                classification=self.brain._runtime_classification('observation','laboratory-home:observe:unowned-fixture'))
        before=self.brain.store.digest(),self.neural_state()
        args={'observation_memory_id':false_mid, 'eligible_read_memory_ids':(),
              'feasible_actions':('experiment','repair')}
        with patch.object(self.brain.neural,'action_scores') as score:
            with self.assertRaisesRegex(PermissionError,'lacks first-person admission'):
                select_with_original_noesis(self.brain,**args)
            score.assert_not_called()
        self.assertEqual((self.brain.store.digest(),self.neural_state()),before)
        history=self.subject.verify_history()
        with closing(self.brain.store.connect()) as db:
            counts=tuple(db.execute('SELECT count(*) FROM '+table).fetchone()[0]
                         for table in ('thoughts','policy_decisions'))
        original=TowerIpseity.record
        def record(subject, db, key, events, *, phase, tick=None):
            if phase=='private_thought': raise PermissionError('denied thought')
            return original(subject,db,key,events,phase=phase,tick=tick)
        args['observation_memory_id']=observed['memory_id']
        with patch.object(TowerIpseity,'record',new=record):
            with self.assertRaisesRegex(PermissionError,'denied thought'):
                select_with_original_noesis(self.brain,**args)
        current=self.subject.verify_history()
        self.assertEqual(current[:-1],history)
        self.assertEqual(current[-1]['phase'],'thought_context')
        self.assertEqual(json.loads(self.brain.store.meta(DELIBERATION+current[-1]['sha256']))['status'],'failed')
        with closing(self.brain.store.connect()) as db:
            self.assertEqual(tuple(db.execute('SELECT count(*) FROM '+table).fetchone()[0]
                                   for table in ('thoughts','policy_decisions')),counts)
        self.assertEqual(self.neural_state(),before[1])

    def test_verified_situated_work_retains_motor_authority_and_outcome(self):
        from doctor_lives.noesis_lab_work import propose_noesis_work, execute_noesis_work
        from contextlib import closing
        bridge=self.bind()
        bridge.observe()
        for i,station in enumerate(('station:center','station:bench')):
            bridge.act('walk',event_id='owned-work-walk-'+str(i),station=station)
        proposal=propose_noesis_work(bridge)
        self.assertEqual(proposal.motor_authorization,'not_granted')
        owned=self.subject.verify_history()
        self.assertEqual(owned[-2]['phase'],'thought_context')
        self.assertEqual(owned[-1]['phase'],'private_thought')
        self.assertIn(proposal.decision_id,owned[-1]['content'][0]['source_refs'])
        before=self.world.verify()
        with self.assertRaises(PermissionError):
            execute_noesis_work(bridge,decision_id=proposal.decision_id,event_id='owned-work-denied')
        self.assertEqual(self.world.verify(),before)
        self.assertEqual(self.subject.verify_history(),owned)
        result=execute_noesis_work(bridge,decision_id=proposal.decision_id,
                    event_id='owned-work-permitted',authorized_world_action=True)
        self.assertEqual(result['action'],proposal.action)
        mid=result['world']['memory_id']
        history=self.subject.verify_history()
        self.assertEqual(history[:len(owned)],owned)
        acquisition=next(e for e in history if e['key']==RECORD+'acquisition:'+mid)
        self.assertEqual(acquisition['content'][0]['text'],result['world']['subject']['inner'])
        self.assertEqual(acquisition['content'][0]['attribution'],'lived')
        self.assertFalse(acquisition['content'][0]['external'])
        with closing(self.brain.store.connect()) as db:
            row=db.execute('SELECT state_pressure_json FROM policy_decisions WHERE id=?',
                           (proposal.decision_id,)).fetchone()
        self.assertEqual(json.loads(row[0])['motor_authorization'],'authorized')
        self.assertEqual(TowerIpseity(PretoriusBrainPort(self.brain.state_dir).brain).verify_history(),history)

    def concern(self):
        self.bind()
        with self.brain.store.transaction() as db:
            db.execute('INSERT INTO concerns(id,created_tick,updated_tick,description,status,importance,uncertainty,actor,source) VALUES(?,?,?,?,?,?,?,?,?)',('test-gap',self.brain.store.tick,self.brain.store.tick,'lavender brass','open',.99,.99,'PREVIEW_HOST','preview_sensus_conflict'))
            self.brain.store.bump_state_version(db)
        return MnemosyneEndogenousPilot(self.port,enabled=True)
    def policy_count(self):
        with closing(self.brain.store.connect()) as db:
            return db.execute('SELECT count(*) FROM policy_decisions WHERE trigger=?',(_TRIGGER,)).fetchone()[0]
    def test_mnemosyne_context_before_policy_and_atomic_intention(self):
        pilot=self.concern()
        original=self.brain._state_policy_scores
        seen=[]
        def witness(*args,**kwargs):
            h=self.subject.verify_history()
            assert h and h[-1]['phase']=='recall_context', 'Selected concern not owned before policy'
            item=h[-1]['content'][0]
            self.assertEqual(item['organ'],'Mnemosyne')
            self.assertEqual(item['source_refs'],['test-gap'])
            self.assertEqual(item['text'],'I ask myself: What do I remember of lavender brass?')
            seen.append(h[-1]); return original(*args,**kwargs)
        with patch.object(self.brain,'_state_policy_scores',side_effect=witness):
            d=pilot.deliberate(recall_cost=0)
        self.assertEqual(d.action,'recall'); self.assertEqual(len(seen),1)
        h=self.subject.verify_history(); e=h[-1]
        self.assertEqual(e['key'],RECORD+'recall-decision:'+d.decision_id)
        self.assertEqual(e['content'][0]['source_refs'],[d.decision_id,'test-gap'])
        self.assertEqual(e['content'][0]['mode'],'intention')
        self.assertEqual(e['previous_sha256'],seen[0]['sha256'])
        self.assertEqual(json.loads(self.brain.store.meta(DELIBERATION+seen[0]['sha256']))['status'],'completed')
        self.assertEqual(self.policy_count(),1)
        self.assertIsNotNone(pilot.recollect())
    def test_mnemosyne_intention_failure_rolls_back_policy(self):
        pilot=self.concern(); original=TowerIpseity.record
        def deny(subject,db,key,events,**kwargs):
            if key.startswith('recall-decision:'): raise PermissionError('intention denied')
            return original(subject,db,key,events,**kwargs)
        before=self.neural_state()
        with patch.object(TowerIpseity,'record',new=deny):
            with self.assertRaisesRegex(PermissionError,'intention denied'):
                pilot.deliberate(recall_cost=0)
        self.assertEqual(self.policy_count(),0); self.assertIsNone(pilot._pending_question)
        self.assertEqual(self.neural_state(),before)
        h=self.subject.verify_history(); self.assertEqual(h[-1]['phase'],'recall_context')
        self.assertEqual(json.loads(self.brain.store.meta(DELIBERATION+h[-1]['sha256']))['status'],'failed')
    def test_mnemosyne_context_failure_prevents_policy(self):
        pilot=self.concern(); before=(self.brain.store.digest(),self.neural_state())
        with patch.object(TowerIpseity,'record',side_effect=PermissionError('context denied')),patch.object(self.brain,'_state_policy_scores',wraps=self.brain._state_policy_scores) as spy:
            with self.assertRaisesRegex(PermissionError,'context denied'):
                pilot.deliberate(recall_cost=0)
            spy.assert_not_called()
        self.assertEqual((self.brain.store.digest(),self.neural_state()),before)
        self.assertEqual(self.policy_count(),0)
    def test_mnemosyne_no_candidate_owns_result_without_invented_cue(self):
        self.bind(); pilot=MnemosyneEndogenousPilot(self.port,enabled=True)
        before=self.subject.verify_history(); d=pilot.deliberate()
        self.assertNotEqual(d.action,'recall'); h=self.subject.verify_history()
        self.assertEqual(h[:-1],before); self.assertEqual(h[-1]['key'],RECORD+'recall-decision:'+d.decision_id)
        self.assertEqual(h[-1]['content'][0]['source_refs'],[d.decision_id])

if __name__=='__main__': unittest.main()
