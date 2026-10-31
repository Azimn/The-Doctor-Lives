"""Read-only QA evidence for frozen Pretorius A. Never writes to either authority.

This reports original-Noesis decisions and authenticated physical receipts,
not inferred scheduled timers, operator actions, or autonomy credit.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

DOCTOR = 'a8cc49ab15a4d6453c8a5954e1a39a047e4fe4a3'
LAB = '6e49795752835d64fa6fd63d16359669a1ca2ba7'
SCHEMA = 'pretorius-a-hosted-opportunity-ledger.v1'

def canonical_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=False).encode('utf-8')).hexdigest()

def readonly(path):
    p = Path(path).resolve(strict=True)
    connection = sqlite3.connect(p.as_uri() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    return connection

def analyze(state: Path, world: Path, setup: Path):
    prepared = json.loads(setup.read_text())
    if (prepared.get('schema') != 'qa-4h-operator-setup.v1'
            or prepared.get('autonomy_credit') is not False
            or prepared.get('status') != 'prepared'):
        raise RuntimeError('Missing disclosed operator preparation')
    if any(x.get('actor') != 'operator_fixture' for x in prepared.get('observed', [])):
        raise RuntimeError('Unexpected operator fixture author')
    entries = []
    with readonly(state/'brain.sqlite3') as mind, readonly(world) as lab, readonly(Path(str(world)+'.doctor-action-intents.sqlite3')) as intents:
        rows = mind.execute("""SELECT id,created_at,selected_action,action_scores_json,state_pressure_json
            FROM policy_decisions WHERE trigger='noesis_situated_choice' ORDER BY rowid""").fetchall()
        operator_messages = 0
        if mind.execute("SELECT 1 FROM sqlite_master WHERE name='operator_conversation_turns'").fetchone():
            operator_messages = mind.execute('SELECT COUNT(*) FROM operator_conversation_turns').fetchone()[0]
        for row in rows:
            evidence = json.loads(row['state_pressure_json'])
            offered = json.loads(row['action_scores_json'])
            action = row['selected_action']
            event_id = evidence.get('motor_event_id')
            auth = evidence.get('motor_authorization')
            if event_id is None:
                receipt, world_valid = None, False
            else:
                matches = lab.execute('SELECT event_hash,envelope FROM rhythm_events WHERE event_id=?', (event_id,)).fetchall()
                receipt = dict(matches[0]) if len(matches) == 1 else None
                world_valid = (len(matches) == 1
                               and canonical_hash(json.loads(receipt['envelope'])) == receipt['event_hash']
                               and json.loads(receipt['envelope']).get('op') == action)
            intent = intents.execute('SELECT request_json,status FROM doctor_action_intents WHERE event_id=?', (event_id,)).fetchone() if event_id else None
            intent_valid = bool(intent and json.loads(intent['request_json']) == {'op': action, 'args': {}}
                                and intent['status'] == 'complete')
            source = 'laboratory-home:action:' + receipt['event_hash'] if receipt else None
            memory = mind.execute('SELECT id,evidence_class,external FROM memories WHERE source=?', (source,)).fetchall() if source else []
            memory_valid = bool(len(memory) == 1 and memory[0]['evidence_class'] == 'lived_runtime_memory'
                                and memory[0]['external'] == 0)
            valid = (bool(offered) and action in offered
                     and evidence.get('selector_authority') == 'original_noesis'
                     and auth == 'authorized' and world_valid and intent_valid and memory_valid)
            entries.append({'schema': SCHEMA, 'doctor_sha': DOCTOR, 'laboratory_sha': LAB,
                'timestamp_utc': row['created_at'], 'policy_decision_id': row['id'],
                'offered_actions': sorted(offered), 'selected_action': action,
                'receipt_id': event_id, 'receipt_hash': receipt['event_hash'] if receipt else None,
                'lived_memory_id': memory[0]['id'] if memory_valid else None,
                'source_authenticated': world_valid, 'intent_authenticated': intent_valid,
                'canonical_memory_authenticated': memory_valid, 'policy_authorized': auth == 'authorized',
                'selection_original_noesis': evidence.get('selector_authority') == 'original_noesis',
                'external_input_marker': {
                    'operator_fixture_prepared_world': True,
                    'operator_selected_this_action': False,
                    'host_scheduled_this_opportunity': True,
                    'autonomous_spontaneous_goal_claim': False},
                'valid_opportunity_with_receipt': valid})
    result = {'schema': 'pretorius-a-hosted-opportunity-summary.v1',
        'doctor_sha': DOCTOR, 'laboratory_sha': LAB,
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'scheduled_work_opportunities_fired': len(entries),
        'complete_original_noesis_opportunities': sum(int(x['valid_opportunity_with_receipt']) for x in entries),
        'missing_or_invalid_opportunities': sum(int(not x['valid_opportunity_with_receipt']) for x in entries),
        'actions_selected': dict(Counter(x['selected_action'] for x in entries)),
        'operator_conversation_turns': operator_messages,
        'operator_fixture_actions': prepared['observed'],
        'autonomous_three_task_life_proven': False, 'independent_source_attestation': False}
    return entries, result

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--state', type=Path, required=True)
    p.add_argument('--world', type=Path, required=True)
    p.add_argument('--setup', type=Path, required=True)
    p.add_argument('--ledger', type=Path, required=True)
    p.add_argument('--summary', type=Path, required=True)
    p.add_argument('--min-complete', type=int, default=5)
    p.add_argument('--no-gate', action='store_true')
    a = p.parse_args()
    entries, result = analyze(a.state, a.world, a.setup)
    a.ledger.write_text(''.join(json.dumps(x, sort_keys=True) + '\n' for x in entries))
    gated = (result['complete_original_noesis_opportunities'] >= a.min_complete
             and result['missing_or_invalid_opportunities'] == 0
             and result['operator_conversation_turns'] == 0)
    result['smoke_min_complete'] = a.min_complete
    result['smoke_gate_passed'] = gated
    a.summary.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))
    if not a.no_gate and not gated:
        raise SystemExit('SMOKE_GATE_FAILED: fewer than five complete original-Noesis opportunity/receipt/policy triples, invalid evidence, or operator conversation recorded')

if __name__ == '__main__':
    main()
