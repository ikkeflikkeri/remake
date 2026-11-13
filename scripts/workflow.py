#!/usr/bin/env python3
"""Versioned, atomic workflow checkpoints. Python standard library only."""
import argparse
import json
import os
import tempfile
from pathlib import Path

STAGES = ("recon", "architect", "design", "build", "backend", "test", "diff", "entrepreneur", "brand", "launch", "deploy")
STATUSES = ("pending", "in_progress", "completed", "blocked")
VERSION = 1


class WorkflowError(ValueError):
    """Invalid workflow input or transition."""


def initial(reference, target):
    if not isinstance(reference, str) or not reference.strip():
        raise WorkflowError("reference must be a non-empty string")
    if not isinstance(target, str) or not target.strip():
        raise WorkflowError("target must be a non-empty string")
    return {"version": VERSION, "reference": reference, "target": target,
            "stages": {name: {"status": "pending", "evidence": []} for name in STAGES}}


def validate(data):
    if not isinstance(data, dict) or set(data) != {"version", "reference", "target", "stages"}:
        raise WorkflowError("unexpected workflow fields")
    if type(data["version"]) is not int or data["version"] != VERSION:
        raise WorkflowError("unsupported workflow version")
    for field in ("reference", "target"):
        if not isinstance(data[field], str) or not data[field].strip():
            raise WorkflowError(f"{field} must be a non-empty string")
    stages = data["stages"]
    if not isinstance(stages, dict) or set(stages) != set(STAGES):
        raise WorkflowError("stage keys do not match contract")
    for name in STAGES:
        stage = stages[name]
        if not isinstance(stage, dict) or set(stage) != {"status", "evidence"}:
            raise WorkflowError(f"{name}: invalid fields")
        if stage["status"] not in STATUSES:
            raise WorkflowError(f"{name}: invalid status")
        evidence = stage["evidence"]
        if not isinstance(evidence, list) or any(not isinstance(x, str) or not x.strip() for x in evidence):
            raise WorkflowError(f"{name}: invalid evidence")
        if stage["status"] == "completed" and not evidence:
            raise WorkflowError(f"{name}: completed stage requires evidence")
    active = [name for name in STAGES if stages[name]["status"] == "in_progress"]
    if len(active) > 1:
        raise WorkflowError("only one stage can be in progress")
    for index, name in enumerate(STAGES):
        if stages[name]["status"] != "pending" and any(
            stages[previous]["status"] != "completed" for previous in STAGES[:index]
        ):
            raise WorkflowError(f"{name}: prerequisites are not complete")
    return data


def transition(data, stage, status, evidence=None):
    validate(data)
    if stage not in STAGES:
        raise WorkflowError("unknown stage")
    if status not in STATUSES:
        raise WorkflowError("unknown status")
    current = data["stages"][stage]["status"]
    allowed = {"pending": {"in_progress"}, "in_progress": {"completed", "blocked"},
               "blocked": {"in_progress"}, "completed": set()}
    if status not in allowed[current]:
        raise WorkflowError(f"invalid transition: {current} -> {status}")
    if status == "in_progress" and any(
        item["status"] == "in_progress" for name, item in data["stages"].items() if name != stage
    ):
        raise WorkflowError("another stage is already in progress")
    result = json.loads(json.dumps(data))
    item = result["stages"][stage]
    if evidence is not None:
        if not isinstance(evidence, str) or not evidence.strip():
            raise WorkflowError("evidence must be non-empty")
        if evidence not in item["evidence"]:
            item["evidence"].append(evidence)
    item["status"] = status
    return validate(result)


def read(path):
    try:
        return validate(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkflowError(str(exc)) from exc


def save(path, data):
    validate(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Never overwrite existing workflow state during initialization.
    fd, temporary = tempfile.mkstemp(prefix=".workflow-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "show", "start", "complete", "block", "resume"))
    parser.add_argument("--file", default=".remake/workflow.json")
    parser.add_argument("--reference")
    parser.add_argument("--target")
    parser.add_argument("--stage", choices=STAGES)
    parser.add_argument("--evidence")
    args = parser.parse_args()
    try:
        path = Path(args.file)
        if args.command == "init":
            if path.exists():
                raise WorkflowError("workflow already exists; refusing to overwrite")
            data = initial(args.reference, args.target)
        else:
            data = read(path)
            if args.command != "show":
                if not args.stage:
                    raise WorkflowError("--stage is required")
                statuses = {"start": "in_progress", "complete": "completed",
                            "block": "blocked", "resume": "in_progress"}
                data = transition(data, args.stage, statuses[args.command], args.evidence)
        if args.command != "show":
            save(path, data)
        print(json.dumps(data, indent=2))
    except WorkflowError as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
