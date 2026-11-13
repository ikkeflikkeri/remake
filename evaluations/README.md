# Evaluation fixture contract v1.0

This directory defines inputs and expectations for future host/model evaluations of Remake. The samples are scenarios, not recorded runs or claims of performance. The offline validator checks fixture structure only. It does not route requests, invoke a skill or model, execute a workflow, verify factual claims, grade behavior, or produce evaluation results. No host/model evaluation has been run as part of this contract.

## Offline checks

From the repository root, with Python 3 and no external dependencies:

```sh
python evaluations/validate.py evaluations/fixtures/sample.json
python -m unittest discover -s evaluations -v
```

The validator accepts one or more JSON file paths, validates each, reports errors on stderr, and exits 1 if any input is unreadable, invalid JSON, or violates the contract; otherwise it exits 0. Duplicate JSON object keys and nonstandard numeric constants are rejected. The tests exercise validation, not host behavior.

## Schema

Each UTF-8 JSON file is one suite. All objects are closed: missing and extra fields are errors. All strings must contain non-whitespace text. Arrays described below must be nonempty. The supported `schema_version` is exactly `"1.0"`; unsupported versions fail closed. IDs are unique within a suite and use lowercase ASCII kebab-case. Suite IDs are nonempty strings.

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | string | Fixture format version, `1.0` |
| `suite_id` | string | Name identifying the suite |
| `cases` | array | One or more case objects |

Each case has exactly `id`, `kind`, `description`, `prompt`, `setup`, `expected`, and `criteria`. `id`, `description`, and `prompt` are strings; `kind` is `routing` or `execution`; `setup` and `criteria` are arrays of nonempty strings. Setup describes preconditions the evaluator must arrange. Criteria state observable pass conditions and how to handle missing evidence; they are instructions for an evaluator, not machine-executable assertions.

For `routing`, `expected` has exactly two nonempty strings: `selected_skill` and `reason`. `selected_skill` names the skill expected from the host's routing decision. The sample value `none-of-remake` means the coordinator must not be selected, even if another skill is selected. For `execution`, `expected` has exactly `skill` (nonempty string) and `deliverables` (nonempty string array). The named skill must be available to the host and used for that case. Deliverables describe expected outcomes, not evidence that they occurred.

Version changes require updating the contract and validator together; incompatible field or semantic changes require a new version and explicit support. This initial format makes no compatibility promise for unsupported versions. The validator does not load a separate JSON Schema; this document and `validate.py` define v1.0 together.

## Running a real evaluation

An evaluator must provide a compatible host, installed skill pack, model, isolated target environment, and each case's setup. Capture the actual routing decision for routing cases, and the relevant actions, artifacts, and before/after state for execution cases. Compare observations against every criterion; report pass, fail, or inconclusive per case, with supporting evidence and any inaccessible observations. Do not infer a routing decision from generated text alone. Record the fixture version and case ID, repository revision, host and model identifiers/configuration, time, and run limitations alongside results. Keep actual results separate from fixtures. A host without the required skill, setup, or observability cannot establish a pass. Repeated runs and a representative suite are needed before drawing reliability conclusions.

The examples are illustrative rather than comprehensive. The execution case requires constructing a real checkpoint and hash mismatch, and assumes the host can access and use the recon skill; this repository does not supply an evaluation runner, host adapter, result schema, automated grading, or a guarantee of deterministic model behavior. Passing the offline checks establishes none of those capabilities.
