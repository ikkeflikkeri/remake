---
name: recon
description: Inspect authorized application references and produce a structured, evidence-backed recon artifact for the Remake workflow.
---

# Recon

Inspect only references the user is authorized to access, within the agreed scope. Record the target and acceptance criteria; avoid copying protected source or assets. Do not perform external side effects without authorization.

Inspect the checkpoint with `python /path/to/remake/scripts/workflow.py show`. Start recon with `python /path/to/remake/scripts/workflow.py start --stage recon` only if it is pending; if it is already in progress, continue without starting it again. If blocked, resolve the blocker and resume it as described below. If completed, stop recon work and inspect the recorded evidence and its review notes; do not start or complete the stage again, create or overwrite its artifact, or change the completed checkpoint. Evidence may include blocker reasons as well as artifact references. If correction is needed, retain the old checkpoint and artifact, and start a new workflow with a separate artifact path as described in the workflow contract. Gather observable features and user journeys, recording source locations and distinguishing observation from inference. Include limitations, inaccessible areas, and unanswered questions. Do not claim to have inspected or tested anything you did not.

Write a UTF-8 JSON artifact such as `.remake/recon.json` with exactly these fields:

- `reference` and `target`: strings exactly matching the workflow checkpoint.
- `scope`: nonempty string describing what was inspected and its limits.
- `observations`: nonempty array of strings describing findings and their source references.
- `unknowns`: nonempty array of strings; explicitly state when none are known.
- `sources`: nonempty array of strings identifying authorized sources inspected.

Run `python /path/to/remake/scripts/verify_recon.py .remake/recon.json` from the target project, then review the content against the sources. The verifier checks structure and identity, not truth, source access, or completeness. Record its SHA-256 output with your review notes. Complete recon with `python /path/to/remake/scripts/workflow.py complete --stage recon --evidence .remake/recon.json` only after both checks pass. The workflow CLI itself does not enforce verification; artifact changes after verification require repeating verification and the source review, and recording the new hash with the updated review notes.

If access is blocked, record the reason with the workflow's block command and resume after it is resolved. Do not fabricate findings to satisfy the schema.
