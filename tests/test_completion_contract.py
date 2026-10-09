import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/completion-contract'


class CompletionContract(unittest.TestCase):
    def record(self):
        return json.loads((FIXTURES / 'valid.json').read_text())

    def run_record(self, record):
        with tempfile.TemporaryDirectory(prefix='rstack-contract-') as directory:
            path = Path(directory) / 'record.json'
            path.write_text(json.dumps(record))
            p = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/rstack.py'),
                                'validate', str(path), '--now', '2026-01-01T12:05:00Z'],
                               capture_output=True, text=True)
            self.assertEqual(p.stderr, '')
            return p.returncode, json.loads(p.stdout)

    def check(self, record, code=None, complete=False):
        status, result = self.run_record(record)
        self.assertEqual(result['completion_supported'], complete, result)
        if code is None:
            self.assertEqual((status, result['decision']), (0, 'record_consistent'), result)
        else:
            self.assertIn(code, [e['code'] for e in result['errors']], result)
            self.assertIn(status, (1, 2))
        return result

    def waiting(self, record):
        record['claim_status'] = 'waiting'
        record['execution']['state'] = 'waiting'
        return record

    def goal(self, record, status='complete'):
        record['completion_contract']['native_goal_required'] = True
        record['native_goal'] = {'state': 'retained', 'id': 'fixture:goal-1', 'outcome_id': record['outcome_id'],
            'prior_readback': {'ref': 'fixture:initial-read', 'state': 'same_unfinished',
                              'goal_id': 'fixture:goal-1', 'outcome_id': record['outcome_id']},
            'current_readback': {'ref': 'fixture:final-read', 'goal_id': 'fixture:goal-1',
                                'outcome_id': record['outcome_id'], 'status': status, 'native_status': status}}
        return record

    def test_retained_behavioral_fixtures(self):
        for case in json.loads((FIXTURES / 'cases.json').read_text()):
            with self.subTest(name=case['name']):
                self.check(case['record'], case['expected_code'], case['expected_completion'])

    def test_old_or_incomplete_records_cannot_bypass_new_contract(self):
        for field in ['completion_contract', 'native_goal', 'outcome_results', 'handoff_receipts']:
            r = self.record(); del r[field]
            self.check(r, 'INVALID_INPUT')
        r = self.record(); r['schema_version'] = 1
        self.check(r, 'INVALID_INPUT')
        for field in ['approval_ref', 'request_ref']:
            r = self.record(); r['completion_contract'][field] = 'fixture:other'
            self.check(r, 'CONTRACT_BINDING')

    def test_native_goal_unavailable_conflict_absent_and_not_selected(self):
        for state in ('unavailable', 'conflict', 'absent'):
            r = self.record(); r['completion_contract']['native_goal_required'] = True
            r['native_goal'] = {'state': state, 'dependency': {'action': 'get goal', 'owner': 'coordinator',
                'resume_when': 'supported compatible readback available', 'observation_ref': 'fixture:actual-error'}}
            self.check(r, 'GOAL_NOT_BOUND')
            self.check(self.waiting(r))
            r['next_action']['kind'] = 'create_goal'; r['approval']['allowed_actions'].append('create_goal')
            self.check(r, 'GOAL_CREATE_AUTHORITY')
        self.check(self.record(), complete=True)
        r = self.record(); r['completion_contract']['native_goal_required'] = True
        self.check(r, 'GOAL_NOT_BOUND')

    def test_proposed_goal_creation_is_scoped_and_absence_is_observed(self):
        r = self.waiting(self.record())
        r['completion_contract']['native_goal_required'] = True
        self.check(r, 'GOAL_NOT_BOUND')
        r['native_goal'] = {'state': 'absent',
            'dependency': {'action': 'create approved goal', 'owner': 'worker',
                           'resume_when': 'authorized creation readback', 'observation_ref': 'fixture:none'},
            'prior_readback': {'ref': 'fixture:none', 'state': 'none_unfinished'}}
        r['next_action']['kind'] = 'create_goal'
        self.check(r, 'PERMISSION_DENIED')
        r['approval']['allowed_actions'].append('create_goal')
        self.check(r)
        r['approval']['stop'] = True
        self.check(r, 'STOP_GATE')

    def test_goal_identity_and_completion_readback(self):
        self.check(self.goal(self.record()), complete=True)
        r = self.goal(self.record(), 'unfinished')
        self.check(r, 'GOAL_NOT_BOUND')
        self.check(self.waiting(r))
        for branch, field in [('prior_readback', 'goal_id'), ('prior_readback', 'outcome_id'),
                              ('current_readback', 'goal_id'), ('current_readback', 'outcome_id')]:
            r = self.goal(self.record()); r['native_goal'][branch][field] = 'fixture:different'
            self.check(r, 'GOAL_REPLACEMENT' if branch == 'prior_readback' else 'GOAL_BINDING')
        for value in [True, None, '', '   ']:
            r = self.goal(self.record()); r['native_goal']['current_readback']['ref'] = value
            self.check(r, 'INVALID_INPUT')

    def test_goal_creation_requires_absence_and_current_authority(self):
        r = self.goal(self.record())
        r['native_goal'].update(state='created', prior_readback={'ref': 'fixture:read-none', 'state': 'none_unfinished'},
            creation_approval_ref=r['approval']['ref'], creation_receipt='fixture:create-result')
        self.check(r, 'GOAL_CREATE_AUTHORITY')
        r['approval']['allowed_actions'].append('create_goal')
        self.check(r, complete=True)
        for update in [{'creation_approval_ref': 'fixture:other'}, {'creation_receipt': ''},
                       {'prior_readback': {'ref': 'fixture:read', 'state': 'different_unfinished'}}]:
            changed = copy.deepcopy(r); changed['native_goal'].update(update)
            self.check(changed, 'GOAL_CREATE_AUTHORITY')
        r['approval']['denied_actions'].append('create_goal')
        self.check(r, 'GOAL_CREATE_AUTHORITY')

    def test_goal_must_not_close_before_required_results_or_handoff(self):
        for operation in ('reported_complete', 'proposed_complete'):
            for gap in ('acceptance', 'part', 'incorporation'):
                r = self.goal(self.record(), 'complete' if operation == 'reported_complete' else 'unfinished')
                self.waiting(r)
                if operation == 'proposed_complete':
                    r['next_action']['kind'] = 'complete_goal'; r['approval']['allowed_actions'].append('complete_goal')
                if gap == 'acceptance': r['acceptance'][0]['status'] = 'pending'
                if gap == 'part': r['outcome_results'][1]['status'] = 'blocked'
                if gap == 'incorporation': r['handoff_receipts'].pop('incorporation')
                self.check(r, 'GOAL_PREMATURE_COMPLETION')
        r = self.goal(self.record(), 'unfinished'); self.waiting(r)
        r['next_action']['kind'] = 'complete_goal'; r['approval']['allowed_actions'].append('complete_goal')
        self.check(r)

    def test_all_parts_and_original_acceptance_must_be_retained(self):
        r = self.record(); r['outcome_results'][1]['status'] = 'pending'
        self.check(r, 'COMPLETION_CONTRACT_OPEN')
        self.check(self.waiting(r))
        for transform in (lambda r:r['outcome_results'].append(copy.deepcopy(r['outcome_results'][0])),
                          lambda r:r['outcome_results'][0].update(part_id='invented'),
                          lambda r:r['completion_contract']['obligations'][0].update(acceptance_ids=['A1']),
                          lambda r:r['acceptance'].pop()):
            r = self.record(); transform(r)
            self.check(r, 'OBLIGATION_COVERAGE')
        r = self.record(); r['outcome_results'][1]['evidence_ids'] = ['missing']
        self.check(r, 'OUTCOME_EVIDENCE')

    def test_support_can_complete_only_its_own_outcome(self):
        r = self.record(); r['completion_contract'].update(outcome_kind='support', parent_outcome_id='fixture:product')
        self.check(r, 'OUTCOME_SUBSTITUTION')
        r['completion_contract']['obligations'][0]['kind'] = 'support'
        for result in r['outcome_results']: result['kind'] = 'support'
        out = self.check(r, complete=True)
        self.assertEqual((out['completion_scope'], out['parent_completion_supported']), ('demo-parser', False))
        r['completion_contract']['parent_outcome_id'] = r['outcome_id']
        self.check(r, 'INVALID_INPUT')

    def test_handoff_stages_are_selected_and_distinct(self):
        r = self.record(); r['handoff_receipts'].pop('incorporation')
        self.check(r, 'COMPLETION_CONTRACT_OPEN')
        r['claim_status'] = 'delivered'; self.check(r)
        r = self.record(); r['completion_contract']['handoff']['required_stages'] = ['persistence']
        r['handoff_receipts'] = {'persistence': r['handoff_receipts']['persistence']}
        self.check(r, complete=True)
        r['completion_contract']['handoff']['required_stages'].append('attachment')
        self.check(r, 'HANDOFF_OPEN')
        r['handoff_receipts']['attachment'] = copy.deepcopy(r['handoff_receipts']['persistence'])
        r['handoff_receipts']['attachment']['ref'] = 'fixture:attachment-operation'
        self.check(r, complete=True)
        r['handoff_receipts']['attachment']['status'] = 'uncertain'
        self.check(r, 'HANDOFF_OPEN')

    def test_one_event_cannot_stand_for_distinct_handoff_stages(self):
        r = self.record()
        r['handoff_receipts']['recipient_readback']['ref'] = r['handoff_receipts']['persistence']['ref']
        self.check(r, 'HANDOFF_RECEIPT_REUSE')
        r['handoff_receipts']['recipient_readback']['ref'] = 'fixture:actual-recipient-readback'
        self.check(r, complete=True)

    def test_handoff_binding_and_retained_disposition(self):
        for field in ('artifact_ref', 'destination', 'recipient', 'revision', 'ref'):
            r = self.record(); r['handoff_receipts']['recipient_readback'][field] = '' if field == 'ref' else 'wrong'
            self.check(r, 'HANDOFF_RECEIPT')
        for field in ('register_ref', 'writer', 'readback_ref', 'disposition', 'detail'):
            r = self.record(); r['handoff_receipts']['incorporation'][field] = ''
            self.check(r, 'HANDOFF_RECEIPT')
        r = self.record(); r['handoff_receipts']['incorporation'].update(disposition='retained', detail='Exact delta retained as intentionally local; canonical writer read it back')
        self.check(r, complete=True)
        for value in (True, None, 1, []):
            r = self.record(); r['handoff_receipts']['recipient_readback']['ref'] = value
            self.check(r, 'INVALID_INPUT')
        r = self.record(); r['handoff_receipts']['incorporation']['manifest']['diagram'] = 'f' * 64
        self.check(r, 'HANDOFF_RECEIPT')


if __name__ == '__main__':
    unittest.main()
