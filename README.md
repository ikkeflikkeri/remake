# Remake

An artifact-driven Claude Code skill pack for researching, rebuilding, verifying, and shipping independently branded applications.

## Status

Phase 3 has begun: the workflow coordinator and recon and architect skills with artifact verification are implemented. Other specialized execution skills are **not implemented yet**.

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
# Follow skills/architect/SKILL.md after the recon handoff passes; it checks
# recon again, reviews sources, and owns architect through completion.
python /path/to/remake/scripts/workflow.py show
```

State is stored at `.remake/workflow.json`. Use `block` and `resume` to recover a blocked stage. Initialization refuses to overwrite existing state.

Hand recon over to the recon skill; it owns the stage through completion, so do not complete it again afterward. The completion evidence names the artifact; its durable review notes and SHA-256 are stored at the artifact path plus `.review.md` (for example, `.remake/recon.json.review.md`). On a completed handoff, follow the recon skill to rerun verification against the correct checkpoint, compare the hash, and inspect the evidence. If verification fails, the hash differs, or older evidence or notes are missing or unusable, retain the old checkpoint and evidence and follow the correction workflow. It uses a fresh checkpoint, artifact, and review with `--file` and `--workflow`; its later stages start pending and must be reassessed and recorded in order. If the artifact changes before completion, rerun verification and review and record the new hash. The verifier checks structure and workflow identity and prints a content hash; it does not verify factual accuracy. Verification is a separate step and is not enforced by the workflow CLI. The architect skill repeats the recon handoff check and requires a fresh source-backed review, then creates and reviews a versioned architecture artifact. Its verifier checks workflow identity, completed recon, the exact recon evidence path, recon validity and digest, and architecture structure. Hashes do not prove review or factual accuracy. Both verifiers and reviews are separate from the workflow CLI; all stages can still accept unverified evidence references. Use the selected checkpoint with `--file` for workflow commands and `--workflow` for verifiers. Concurrent writers are not supported.

## Roadmap

1. Foundation and CI — complete
2. Versioned workflow state, checkpointing, and tests — implemented
3. Artifact schemas, verified evidence, and recon/architecture skills
4. Build, test, parity, and release workflows
5. Routing and execution evaluations
