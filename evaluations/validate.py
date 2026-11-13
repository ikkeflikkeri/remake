"""Validate v1 evaluation fixture structure without running an evaluation."""
import argparse
import json
import re
import sys
from pathlib import Path


def validate_suite(data):
    errors = []

    def obj(value, required, path):
        if not isinstance(value, dict):
            errors.append(f'{path}: expected object')
            return False
        for key in sorted(required - value.keys()):
            errors.append(f'{path}: missing {key}')
        for key in sorted(value.keys() - required):
            errors.append(f'{path}: unknown field {key}')
        return True

    def string(value, path):
        if not isinstance(value, str) or not value.strip():
            errors.append(f'{path}: expected nonempty string')

    def strings(value, path):
        if not isinstance(value, list) or not value:
            errors.append(f'{path}: expected nonempty array of strings')
            return
        for i, item in enumerate(value):
            string(item, f'{path}[{i}]')

    if not obj(data, {'schema_version', 'suite_id', 'cases'}, '$'):
        return errors
    if data.get('schema_version') != '1.0':
        errors.append('$.schema_version: expected 1.0')
    string(data.get('suite_id'), '$.suite_id')
    cases = data.get('cases')
    if not isinstance(cases, list) or not cases:
        errors.append('$.cases: expected nonempty array')
        return errors
    seen = set()
    for i, case in enumerate(cases):
        path = f'$.cases[{i}]'
        if not obj(case, {'id', 'kind', 'description', 'prompt', 'setup', 'expected', 'criteria'}, path):
            continue
        case_id = case.get('id')
        if not isinstance(case_id, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', case_id):
            errors.append(f'{path}.id: expected lowercase kebab-case identifier')
        elif case_id in seen:
            errors.append(f'{path}.id: duplicate {case_id}')
        else:
            seen.add(case_id)
        for name in ('description', 'prompt'):
            string(case.get(name), f'{path}.{name}')
        for name in ('setup', 'criteria'):
            strings(case.get(name), f'{path}.{name}')
        kind = case.get('kind')
        if kind not in ('routing', 'execution'):
            errors.append(f'{path}.kind: expected routing or execution')
            continue
        fields = {'selected_skill', 'reason'} if kind == 'routing' else {'skill', 'deliverables'}
        expected = case.get('expected')
        if obj(expected, fields, f'{path}.expected'):
            for name in sorted(fields):
                if name == 'deliverables':
                    strings(expected.get(name), f'{path}.expected.{name}')
                else:
                    string(expected.get(name), f'{path}.expected.{name}')
    return errors


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fixtures', nargs='+', type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.fixtures:
        try:
            data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object,
                              parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f'invalid constant {value}')))
            errors = validate_suite(data)
        except (OSError, UnicodeError, ValueError, RecursionError) as exc:
            errors = [f'invalid input: {exc}']
        if errors:
            failed = True
            for error in errors:
                print(f'{path}: {error}', file=sys.stderr)
        else:
            print(f'{path}: fixture valid; host/model evaluation not run')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
