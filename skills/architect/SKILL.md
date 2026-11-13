---
name: architect
description: Design an evidence-backed architecture from completed recon for the Remake workflow.
---

# Architect

Work in the target project, with authorized references only. Do not deploy, publish, contact third parties, or perform other external side effects. Design independently; do not copy protected source or assets. Use one workflow writer at a time.

Inspect the checkpoint with `python /path/to/remake/scripts/workflow.py show`. Recon must be completed with an actual recon artifact path in its evidence list. Verify that artifact using `python /path/to/remake/scripts/verify_recon.py <recon-path>` and review its content and limitations. Use the exact path string recorded in the checkpoint; paths are interpreted relative to the target project's current working directory. Record the verifier's SHA-256 digest. If recon is invalid, missing, or unsuitable, stop and report the issue; completed stages cannot be reopened, so preserve the checkpoint and start a new workflow if correction is necessary.

Check the architect status before changing it: start only if pending, resume only if blocked and its blocker is resolved, continue if already in progress, and do not restart or overwrite a completed stage. If another stage is active or prerequisites are incomplete, stop and resolve the workflow state. If blocked during architecture work, record a non-sensitive reason with `workflow.py block --stage architect --evidence "reason"`; resume only when resolved.

Write UTF-8 JSON, for example `.remake/architecture.json`, with exactly these fields:

- `version`: integer `1`.
- `reference`, `target`: strings exactly matching the checkpoint.
- `recon_evidence`: exact recon artifact path string in the completed recon stage's evidence list.
- `recon_sha256`: lowercase, 64-character SHA-256 of the recon artifact bytes as reported by its verifier.
- `requirements`, `components`, `interfaces`, `decisions`, `risks`, `unknowns`, `evidence`, `assumptions`, `limitations`: each a nonempty array of nonblank strings. Describe concrete requirements, component responsibilities and boundaries, interface contracts, choices and rationale, and relevant risks. Link evidence to recon observations or other authorized sources; label inferences and assumptions separately. State meaningful scope, access, and validation limitations, and explicitly note when there are no known unknowns or assumptions. Do not invent facts to fill fields.

Run `python /path/to/remake/scripts/verify_architecture.py .remake/architecture.json` from the target project, then review the architecture against recon and sources, including evidence, assumptions, tradeoffs and limitations. The verifier checks structure, identity, recon status, path and digest; it does not establish factual accuracy, completeness, or design quality. Record the architecture digest and review notes. Only after verification and review pass, complete with `python /path/to/remake/scripts/workflow.py complete --stage architect --evidence .remake/architecture.json`. Reverify and rereview if either artifact changes before completion. The workflow CLI does not enforce these checks, and completed stages are immutable.
