#!/usr/bin/env python3
"""Check the structure and identity of a recon artifact."""
import argparse
import hashlib
import json
from pathlib import Path

FIELDS = ("reference", "target", "scope", "observations", "unknowns", "sources")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def verify(path, reference, target):
    raw = Path(path).read_bytes()
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    if not isinstance(data, dict) or set(data) != set(FIELDS):
        raise ValueError("artifact must contain exactly: " + ", ".join(FIELDS))
    for key in ("reference", "target", "scope"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"{key} must be a nonempty string")
    for key in ("observations", "unknowns", "sources"):
        if not isinstance(data[key], list) or not data[key] or any(
            not isinstance(value, str) or not value.strip() for value in data[key]
        ):
            raise ValueError(f"{key} must be a nonempty list of nonempty strings")
    if data["reference"] != reference or data["target"] != target:
        raise ValueError("reference and target must match the workflow")
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact")
    parser.add_argument("--workflow", default=".remake/workflow.json")
    args = parser.parse_args()
    try:
        from workflow import read
        state = read(args.workflow)
        digest = verify(args.artifact, state["reference"], state["target"])
        print(f"PASS: {args.artifact} sha256:{digest}")
    except (ValueError, OSError, UnicodeError, RecursionError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
