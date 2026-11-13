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
# Follow skills/recon/SKILL.md: it starts or resumes recon, creates and verifies
# the artifact, reviews sources, records the hash, and completes the stage.
python /path/to/remake/scripts/workflow.py show
```

State is stored at `.remake/workflow.json`. Use `block` and `resume` to recover a blocked stage. Initialization refuses to overwrite existing state.

Hand recon over to the recon skill; it owns the stage through completion, so do not complete it again afterward. The completion evidence names the artifact; its durable review notes and SHA-256 are stored at the artifact path plus `.review.md` (for example, `.remake/recon.json.review.md`). If recon is already completed, inspect both without overwriting them. For corrections, the recon skill provides a separate checkpoint and artifact example using `--file` and `--workflow`; retain those paths throughout the new workflow. The recon skill describes the required artifact and review process. If the artifact changes after verification, rerun verification and review and record the new hash before completion. Its verifier checks structure and workflow identity and prints a content hash; it does not verify factual accuracy. Verification is a separate step and is not enforced by the workflow CLI. Other stages still accept unverified evidence references. Concurrent writers are not supported.

## Roadmap

1. Foundation and CI — complete
2. Versioned workflow state, checkpointing, and tests — implemented
3. Artifact schemas, verified evidence, and recon/architecture skills
4. Build, test, parity, and release workflows
5. Routing and execution evaluations
