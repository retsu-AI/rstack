"""Explicit synthetic adapter; preserved v1 fixture files remain byte-identical."""
import copy
import json
from pathlib import Path


def upgrade_fixture(record):
    if record.get('schema_version') != 1:
        return record
    result = copy.deepcopy(record)
    example = json.loads((Path(__file__).resolve().parents[1] / 'templates/outcome.example.json').read_text())
    result['schema_version'] = 2
    for key in ('completion_contract', 'outcome_results', 'native_goal', 'handoff_receipts'):
        result[key] = copy.deepcopy(example[key])
    return result
