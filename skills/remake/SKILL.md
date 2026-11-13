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
python /path/to/remake/scripts/workflow.py start --stage recon
python /path/to/remake/scripts/verify_recon.py .remake/recon.json
python /path/to/remake/scripts/workflow.py complete --stage recon --evidence ".remake/recon.json"
python /path/to/remake/scripts/workflow.py start --stage architect
```

The default state path is `.remake/workflow.json`. Never reinitialize an existing state file. Use `show` to inspect and resume it.

Stages execute in order: recon, architect, design, build, backend, test, diff, entrepreneur, brand, launch, deploy. A stage cannot start until all prior stages have completed. Each completion requires a nonempty evidence reference. **The state manager checks that evidence is nonempty but does not verify that referenced files exist or that the work was actually performed.** Check those claims separately.

For recon, follow the `recon` skill to create, verify, and review the artifact before completing the stage. The verifier is not enforced by the checkpoint manager.

If blocked, use `block --stage STAGE --evidence "reason"`, resolve the blocker, then `resume --stage STAGE`. Do not bypass stage prerequisites or edit workflow JSON manually.

## Safety

- Only use material the user has permission to access.
- Do not copy proprietary code, protected assets, or private APIs.
- Publishing, deployment, payments, and other external side effects require explicit user approval.
- A completed checkpoint is not proof of quality; run actual tests and document results.
- Do not claim that unimplemented specialized skills ran.

## Further guidance

See `references/workflow.md` for the state contract and limitations.
