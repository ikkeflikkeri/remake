---
name: recon
description: Inspect authorized application references and produce a structured, evidence-backed recon artifact for the Remake workflow.
---

# Recon

Inspect only references the user is authorized to access, within the agreed scope. Record the target and acceptance criteria; avoid copying protected source or assets. Do not perform external side effects without authorization.

Start the recon stage using the workflow CLI. Gather observable features and user journeys, recording source locations and distinguishing observation from inference. Include limitations, inaccessible areas, and unanswered questions. Do not claim to have inspected or tested anything you did not.

Write a UTF-8 JSON artifact such as `.remake/recon.json` with exactly these fields:

- `reference` and `target`: strings exactly matching the workflow checkpoint.
- `scope`: nonempty string describing what was inspected and its limits.
- `observations`: nonempty array of strings describing findings and their source references.
- `unknowns`: nonempty array of strings; explicitly state when none are known.
- `sources`: nonempty array of strings identifying authorized sources inspected.

Run `python /path/to/remake/scripts/verify_recon.py .remake/recon.json` from the target project, then review the content against the sources. The verifier checks structure and identity, not truth, source access, or completeness. Record its SHA-256 output with your review notes. Complete recon with `python /path/to/remake/scripts/workflow.py complete --stage recon --evidence .remake/recon.json` only after both checks pass. The workflow CLI itself does not enforce verification; artifact changes after verification require repeating it.

If access is blocked, record the reason with the workflow's block command and resume after it is resolved. Do not fabricate findings to satisfy the schema.
