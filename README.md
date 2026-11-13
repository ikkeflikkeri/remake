# Remake

An artifact-driven Claude Code skill pack for researching, rebuilding, verifying, and shipping independently branded applications.

## Status

Phase 2: the workflow coordinator and checkpoint state manager are implemented. Specialized execution skills are **not implemented yet**.

## Principles

- Use authorized references; do not copy proprietary source code or assets.
- Keep each skill narrowly scoped with explicit inputs, outputs, and verification.
- Require explicit approval before deployment, publication, or external side effects.
- Improve code, instructions, tests, and documentation with every change.

## Development

```bash
python scripts/validate_skills.py
python -m unittest discover -s tests -v
```

## Workflow CLI

Run the manager from the **target application** directory:

```bash
python /path/to/remake/scripts/workflow.py init --reference "https://example.com" --target "web"
python /path/to/remake/scripts/workflow.py start --stage recon
python /path/to/remake/scripts/workflow.py complete --stage recon --evidence ".remake/recon.md"
python /path/to/remake/scripts/workflow.py show
```

State is stored at `.remake/workflow.json`. Use `block` and `resume` to recover a blocked stage. Initialization refuses to overwrite existing state.

**Limitations:** Evidence references are not independently verified, concurrent writers are not supported, and stage-specific skills are not implemented yet. A completed checkpoint does not mean an artifact has passed validation.

## Roadmap

1. Foundation and CI — complete
2. Versioned workflow state, checkpointing, and tests — implemented
3. Artifact schemas, verified evidence, and recon/architecture skills
4. Build, test, parity, and release workflows
5. Routing and execution evaluations
