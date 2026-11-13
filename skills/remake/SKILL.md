---
name: remake
description: Coordinate a staged application remake from authorized reference material. Use when a user explicitly asks to recreate or rebuild an app or website with a research-to-release workflow; do not use for isolated debugging or ordinary feature requests.
---

# Remake — workflow coordinator

Use this skill to plan and track an authorized app remake. The recon skill is available; other stage-specific skills are still under development.

## Intake

1. Confirm the user is authorized to use the reference material.
2. Record the reference, target platform, and measurable acceptance criteria.
3. Explain what is implemented and what remains manual.

## Checkpoint workflow

The repository provides a dependency-free state manager at `scripts/workflow.py`. Run from the target project with a path to the script.

```bash
python /path/to/remake/scripts/workflow.py init --reference "https://example.com" --target "web"
python /path/to/remake/scripts/workflow.py show
# Hand off to the recon skill to run recon through completion.
python /path/to/remake/scripts/workflow.py show
# Only after recon is complete, start the next stage:
python /path/to/remake/scripts/workflow.py start --stage architect
```

The default state path is `.remake/workflow.json`. Never reinitialize an existing state file. Use `show` to inspect and resume it.

Stages execute in order: recon, architect, design, build, backend, test, diff, entrepreneur, brand, launch, deploy. A stage cannot start until all prior stages have completed. Each completion requires a nonempty evidence reference. **The state manager checks that evidence is nonempty but does not verify that referenced files exist or that the work was actually performed.** Check those claims separately.

Hand off recon to the `recon` skill, which owns starting or resuming the stage, creating and verifying the artifact, manually reviewing it against sources, recording the SHA-256 and review in the durable sidecar at the artifact path plus `.review.md`, and completing the stage with the artifact path as evidence. Do not start or complete recon again after the handoff. Check the checkpoint before advancing; if recon is blocked or otherwise incomplete, do not start architect. For completed recon, follow the recon skill's handoff check: rerun verification against that checkpoint, compare the hash with the notes, and inspect the evidence. If verification fails, the hash differs, or evidence or notes are missing or unusable, preserve the old checkpoint and use the correction workflow before advancing. Carry its `--file` checkpoint path through every later workflow command and use it as `--workflow` for verification. All later stages in the fresh checkpoint are pending; reassess and record them in order. If the artifact changes before completion, repeat verification and review and record the new hash. The verifier is not enforced by the checkpoint manager.

If blocked, use `block --stage STAGE --evidence "reason"`, resolve the blocker, then `resume --stage STAGE`. Do not bypass stage prerequisites or edit workflow JSON manually.

## Safety

- Only use material the user has permission to access.
- Do not copy proprietary code, protected assets, or private APIs.
- Publishing, deployment, payments, and other external side effects require explicit user approval.
- A completed checkpoint is not proof of quality; run actual tests and document results.
- Do not claim that unimplemented specialized skills ran.

## Further guidance

See [workflow state contract](references/workflow.md) for the state contract and limitations, and [stage map](references/stage-map.md) for stage inputs, outputs, dependencies, and evidence guidance.
