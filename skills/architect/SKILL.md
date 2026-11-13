---
name: architect
description: Design an evidence-backed architecture from completed recon for the Remake workflow.
---

# Architect

Work in the target project, with authorized references only. Do not deploy, publish, contact third parties, or perform other external side effects. Design independently; do not copy protected source or assets. Use one workflow writer at a time.

Inspect the checkpoint with `python /path/to/remake/scripts/workflow.py show`. Recon must be completed with an actual recon artifact path in its evidence list. Use the exact path string recorded in the checkpoint; paths are interpreted relative to the target project's current working directory. Follow the recon skill's completed-handoff check: rerun `python /path/to/remake/scripts/verify_recon.py <recon-path> --workflow <checkpoint>`, inspect the artifact and its `<recon-path>.review.md` notes, and compare the full SHA-256 with the recorded review hash. A checkpoint itself stores no original digest. If verification fails, hashes differ, or the artifact, evidence, or notes are missing or unusable, preserve them and use the recon skill's correction workflow before proceeding. Do not overwrite completed recon evidence or its notes.

At this architecture handoff, even when the hashes match and verification passes, freshly review the current recon content against its authorized sources: check observations, scope, unknowns, and limitations, and record separate source-backed handoff review notes without altering the completed recon notes. Do not rely solely on the earlier review. If sources cannot be accessed or the recon cannot be adequately reviewed, stop and report the limitation rather than completing architecture. A matching hash establishes byte consistency with the notes, not their truth or proof of review. Record the current verifier SHA-256 in the architecture artifact. If recon changes, repeat the handoff checks and follow the correction workflow when the hash differs.

Carry the selected checkpoint path through every workflow command using `--file <checkpoint>` and every verifier using `--workflow <checkpoint>`. For the default `.remake/workflow.json`, these options may be omitted. If correction creates a fresh checkpoint, reassess all later stages in order.

Check the architect status before changing it: start only if pending, resume only if blocked and its blocker is resolved, continue if already in progress, and do not restart or overwrite a completed stage. If architect is completed, stop architecture work and inspect its recorded evidence without overwriting it or completing it again. If another stage is active or prerequisites are incomplete, stop and resolve the workflow state. If blocked during architecture work, record a non-sensitive reason with `workflow.py block --stage architect --evidence "reason"`; resume only when resolved.

Write UTF-8 JSON, for example `.remake/architecture.json`, with exactly these fields:

- `version`: integer `1`.
- `reference`, `target`: strings exactly matching the checkpoint.
- `recon_evidence`: exact recon artifact path string in the completed recon stage's evidence list.
- `recon_sha256`: lowercase, 64-character SHA-256 of the recon artifact bytes as reported by its verifier.
- `requirements`, `components`, `interfaces`, `decisions`, `risks`, `unknowns`, `evidence`, `assumptions`, `limitations`: each a nonempty array of nonblank strings. Describe concrete requirements, component responsibilities and boundaries, interface contracts, choices and rationale, and relevant risks. Link evidence to recon observations or other authorized sources; label inferences and assumptions separately. State meaningful scope, access, and validation limitations, and explicitly note when there are no known unknowns or assumptions. Do not invent facts to fill fields.

Run `python /path/to/remake/scripts/verify_architecture.py .remake/architecture.json` from the target project, then review the architecture against recon and sources, including evidence, assumptions, tradeoffs and limitations. The verifier checks structure, identity, recon status, path and digest; it does not establish factual accuracy, completeness, or design quality. Record the architecture digest and review notes. Only after verification and review pass, complete with `python /path/to/remake/scripts/workflow.py complete --stage architect --evidence .remake/architecture.json`. If architecture changes before completion, reverify and rereview it. If recon changes, repeat the recon handoff checks and source review before proceeding; a mismatch with the completed review notes requires the correction workflow. The workflow CLI does not enforce these checks, and completed stages are immutable.
