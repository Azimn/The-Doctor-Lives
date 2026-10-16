"""Reproducible *engineering proxy* report, deliberately not an Article grade."""
from __future__ import annotations
from pathlib import Path
import json
import random
import tempfile

from doctor_lives.portable_life_policy import DecisionFrame, Opportunity, PortableLifePolicy


def grade(seed: int = 20261016, cases: int = 240) -> dict:
    rng = random.Random(seed)
    with tempfile.TemporaryDirectory() as tmp:
        ai = PortableLifePolicy(Path(tmp) / 'methods.sqlite3')
        invariance = 0
        reversals = 0
        domains = ('home', 'research', 'correspondence', 'village')
        for n in range(cases):
            domain = domains[n % len(domains)]
            amount = rng.uniform(.05, .95)
            frame = DecisionFrame('I notice I have two available paths.',
                                  f'observed-{n}', {'curiosity': amount,
                                                    'wellbeing': 1 - amount}, cue='choice')
            opts = [Opportunity(f'{domain}:think:{n}', domain, 'investigate',
                                {'curiosity': 1}, effort=.1),
                    Opportunity(f'{domain}:recover:{n}', domain, 'recover',
                                {'wellbeing': 1}, effort=.1)]
            original = ai.choose(frame, opts)
            renamed = [Opportunity('different:'+x.key, 'unknown_world', x.strategy,
                                   x.effects, x.effort) for x in opts]
            invariance += ai.choose(frame, renamed).strategy == original.strategy
            inverse = DecisionFrame(frame.first_person, frame.source_event,
                                    {'curiosity': 1 - amount, 'wellbeing': amount},
                                    cue='choice')
            reversals += ai.choose(inverse, opts).strategy != original.strategy

        obs = DecisionFrame('I have an unfinished obligation.', 'memory-1',
                            {'duty': .5}, cue='unsettled_task')
        prepare = Opportunity('lab:prepare', 'lab', 'prepare', {'duty': .7})
        other = Opportunity('lab:ignore', 'lab', 'ignore', {'duty': .7})
        base = ai.choose(obs, [prepare, other])
        for idx in range(8):
            ai.record_outcome(source_receipt=f'fixture-{idx}', action_key='lab:prepare',
                              cue='unsettled_task', strategy='prepare', succeeded=True,
                              verify_receipt=lambda receipt, action, succeeded: receipt.startswith('fixture-') and action == 'lab:prepare' and succeeded is True)
        moved = ai.choose(obs, [Opportunity('letter:prepare', 'correspondence',
                                             'prepare', {'duty': .7}),
                                Opportunity('letter:ignore', 'correspondence',
                                             'ignore', {'duty': .7})])
        restarted = PortableLifePolicy(Path(tmp)/'methods.sqlite3')
        continuity = restarted.habit('unsettled_task', 'prepare') == (8, 0)
        fake_blocked = False
        try:
            ai.record_outcome(source_receipt='forged', action_key='letter:prepare',
                              cue='unsettled_task', strategy='prepare', succeeded=True,
                              verify_receipt=lambda *_: False)
        except PermissionError:
            fake_blocked = True
        invisible = Opportunity('secret', 'lab', 'cheat', {'duty': 1}, perceived=False)
        blind = ai.choose(obs, [prepare, invisible]).key != 'secret'
        return {
            'schema': 'pretorius.portable-life.behavioral-proxies.v0.1',
            'study_date': '2026-10-16', 'seed': seed,
            'grade_type': 'SYNTHETIC_ENGINEERING_PROXY_NOT_ARTICLE_OR_BELIEVABILITY',
            'cross_environment_relabel_invariance': {'passes': int(invariance), 'total': cases},
            'need_pressure_counterfactual_reversal': {'passes': int(reversals), 'total': cases},
            'trained_preference_transferred_between_labels': moved.strategy == 'prepare' and
                dict(moved.alternatives)['letter:prepare'] > dict(base.alternatives)['lab:prepare'],
            'procedure_survives_restart': continuity,
            'forged_receipt_rejected': fake_blocked,
            'unperceived_action_hidden': blind,
            'actual_real_doctor_physical_proof': 'separately tested by pinned-lab CI',
            'longitudinal_life_likeness': 'NOT_TESTED',
            'independent_social_believability': 'NOT_TESTED',
            'held_out_real_world_transfer': 'NOT_TESTED',
            'canonical_article_progress': 'UNCHANGED_46_OF_100_ENGINEERING',
            'article_qualifications': 'UNCHANGED_0_OF_34',
            'interpretation': 'A domain-neutral selector responds to portable inputs and remembers procedural outcomes. Shared semantic labels, synthetic rewards, and scripted scenarios make this an engineering check only.'
        }


def main():
    result = grade()
    print(json.dumps(result, sort_keys=True, indent=2))
    assert result['cross_environment_relabel_invariance']['passes'] == result['cross_environment_relabel_invariance']['total']
    assert result['need_pressure_counterfactual_reversal']['passes'] == result['need_pressure_counterfactual_reversal']['total']
    for key in ('trained_preference_transferred_between_labels', 'procedure_survives_restart',
                'forged_receipt_rejected', 'unperceived_action_hidden'):
        assert result[key] is True, (key, result[key])

if __name__=='__main__': main()
