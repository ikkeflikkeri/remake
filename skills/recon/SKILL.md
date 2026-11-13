---
name: recon
description: Inspect authorized application references and produce a structured, evidence-backed recon artifact for the Remake workflow.
---

# Recon

Inspect only references the user is authorized to access, within the agreed scope. Record the target and acceptance criteria; avoid copying protected source or assets. Do not perform external side effects without authorization.

Inspect the checkpoint with `python /path/to/remake/scripts/workflow.py show`. Start recon with `python /path/to/remake/scripts/workflow.py start --stage recon` only if it is pending; if it is already in progress, continue without starting it again. If blocked, resolve the blocker and resume it as described below. If completed, stop recon work and inspect the recorded evidence and its review notes as described below; do not start or complete the stage again, create or overwrite its artifact, or change the completed checkpoint. Evidence may include blocker reasons as well as artifact references. If correction is needed, retain the old checkpoint, artifact, and review notes and use separate paths as described below. Gather observable features and user journeys, recording source locations and distinguishing observation from inference. Include limitations, inaccessible areas, and unanswered questions. Do not claim to have inspected or tested anything you did not.

Write a UTF-8 JSON artifact such as `.remake/recon.json` with exactly these fields:

- `reference` and `target`: strings exactly matching the workflow checkpoint.
- `scope`: nonempty string describing what was inspected and its limits.
- `observations`: nonempty array of strings describing findings and their source references.
- `unknowns`: nonempty array of strings; explicitly state when none are known.
- `sources`: nonempty array of strings identifying authorized sources inspected.

Run `python /path/to/remake/scripts/verify_recon.py .remake/recon.json` from the target project, then review the content against the sources. The verifier checks structure and identity, not truth, source access, or completeness. Save durable UTF-8 review notes at the artifact path with `.review.md` appended (for example, `.remake/recon.json.review.md`). Include the artifact path, the verifier's full SHA-256, sources checked, review findings and limitations, and the review date. Keep these notes with the artifact. Complete recon with `python /path/to/remake/scripts/workflow.py complete --stage recon --evidence .remake/recon.json` only after both checks pass. The workflow CLI itself does not enforce verification; artifact changes after verification require repeating verification and the source review, and recording the new hash with the updated review notes.

The completion evidence is the artifact path, so a later reader can find the notes by appending `.review.md` to that path. Inspect the completion artifact and its notes when handing off or revisiting recon; blocker reasons may also appear in the evidence list. The CLI does not check that either file exists or that the notes are accurate.

## Correcting completed recon

Completed checkpoints cannot be reopened. From the target project, choose unused paths for a fresh checkpoint, artifact, and notes. For example, using `.remake/correction-1/` (choose another unused directory for each correction):

```bash
python /path/to/remake/scripts/workflow.py init --file .remake/correction-1/workflow.json --reference "https://example.com" --target "web"
python /path/to/remake/scripts/workflow.py show --file .remake/correction-1/workflow.json
python /path/to/remake/scripts/workflow.py start --file .remake/correction-1/workflow.json --stage recon
# Inspect sources and write .remake/correction-1/recon.json with matching reference and target.
python /path/to/remake/scripts/verify_recon.py .remake/correction-1/recon.json --workflow .remake/correction-1/workflow.json
# Review against sources and save the hash and review in .remake/correction-1/recon.json.review.md.
python /path/to/remake/scripts/workflow.py complete --file .remake/correction-1/workflow.json --stage recon --evidence .remake/correction-1/recon.json
python /path/to/remake/scripts/workflow.py show --file .remake/correction-1/workflow.json
```

Use the intended reference and target, and carry the new checkpoint path through the handoff and all later workflow commands (including `show`, `block`, `resume`, and the next stage). Use the same path as `--workflow` for every verification. If blocked, use `block --file .remake/correction-1/workflow.json --stage recon --evidence "reason"`, resolve it, and use `resume --file .remake/correction-1/workflow.json --stage recon`. Continue to use the new artifact and notes paths; never overwrite completed evidence. For a default-path workflow, omit `--file` and `--workflow` and use the default paths above. Do not fabricate findings to satisfy the schema.
