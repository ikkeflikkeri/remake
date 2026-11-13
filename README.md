# Remake

An artifact-driven Claude Code skill pack for researching, rebuilding, verifying, and shipping independently branded applications.

## Status

Phase 3 has begun: the workflow coordinator and a recon skill with artifact verification are implemented. Other specialized execution skills are **not implemented yet**.

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
# Follow skills/recon/SKILL.md to inspect sources and create .remake/recon.json.
python /path/to/remake/scripts/verify_recon.py .remake/recon.json
# Manually review the artifact against its sources and record the SHA-256 with review notes.
python /path/to/remake/scripts/workflow.py complete --stage recon --evidence ".remake/recon.json"
python /path/to/remake/scripts/workflow.py show
```

State is stored at `.remake/workflow.json`. Use `block` and `resume` to recover a blocked stage. Initialization refuses to overwrite existing state.

Start recon only once; if it is already in progress, continue with the recon skill without starting it again. The recon skill describes the required artifact and review process. If the artifact changes after verification, rerun verification and review and record the new hash before completion. Its verifier checks structure and workflow identity and prints a content hash; it does not verify factual accuracy. Verification is a separate step and is not enforced by the workflow CLI. Other stages still accept unverified evidence references. Concurrent writers are not supported.

## Roadmap

1. Foundation and CI — complete
2. Versioned workflow state, checkpointing, and tests — implemented
3. Artifact schemas, verified evidence, and recon/architecture skills
4. Build, test, parity, and release workflows
5. Routing and execution evaluations
