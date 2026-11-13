#!/usr/bin/env python3
"""Verify an architecture artifact and its completed recon dependency."""
import argparse
import hashlib
import json
import re
from pathlib import Path

try:
    from . import verify_recon, workflow
except ImportError:
    import verify_recon
    import workflow

LIST_FIELDS = ('requirements', 'components', 'interfaces', 'decisions', 'risks',
               'unknowns', 'evidence', 'assumptions', 'limitations')
FIELDS = ('version', 'reference', 'target', 'recon_evidence', 'recon_sha256', *LIST_FIELDS)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'),
                      object_pairs_hook=verify_recon.unique_object)


def verify(path, workflow_path):
    state = workflow.validate(read_json(workflow_path))
    raw = Path(path).read_bytes()
    data = json.loads(raw.decode('utf-8'), object_pairs_hook=verify_recon.unique_object)
    if not isinstance(data, dict) or set(data) != set(FIELDS):
        raise ValueError('artifact must contain exactly: ' + ', '.join(FIELDS))
    if type(data['version']) is not int or data['version'] != 1:
        raise ValueError('unsupported architecture version')
    for key in ('reference', 'target', 'recon_evidence'):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f'{key} must be a nonempty string')
    if data['reference'] != state['reference'] or data['target'] != state['target']:
        raise ValueError('reference and target must match the workflow')
    for key in LIST_FIELDS:
        if not isinstance(data[key], list) or not data[key] or any(
            not isinstance(item, str) or not item.strip() for item in data[key]
        ):
            raise ValueError(f'{key} must be a nonempty list of nonempty strings')
    digest = data['recon_sha256']
    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise ValueError('recon_sha256 must be a lowercase SHA-256 digest')
    recon = state['stages']['recon']
    if recon['status'] != 'completed' or data['recon_evidence'] not in recon['evidence']:
        raise ValueError('completed recon must contain the exact evidence path')
    actual = verify_recon.verify(data['recon_evidence'], state['reference'], state['target'])
    if actual != digest:
        raise ValueError('recon SHA-256 does not match')
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact')
    parser.add_argument('--workflow', default='.remake/workflow.json')
    args = parser.parse_args()
    try:
        digest = verify(args.artifact, args.workflow)
        print(f'PASS: {args.artifact} sha256:{digest}')
    except (ValueError, OSError, UnicodeError, RecursionError, TypeError) as exc:
        parser.exit(2, f'error: {exc}\n')


if __name__ == '__main__':
    main()
