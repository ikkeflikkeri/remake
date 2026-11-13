# Workflow state contract (v1)

State lives at `.remake/workflow.json` in the **target application** repository.

- `version`: integer, currently `1`.
- `reference`: nonempty string identifying an authorized reference.
- `target`: nonempty string describing the intended platform.
- `stages`: exactly 11 named stages, each with `status` and `evidence`.
- `status`: `pending`, `in_progress`, `blocked`, or `completed`.
- `evidence`: array of nonempty strings identifying supporting artifacts or blockers.

Transitions: `pending → in_progress → completed`; `in_progress → blocked → in_progress`. Completed stages are immutable in v1. Later stages require every earlier stage to be completed; only one stage may be in progress.

The state manager writes JSON atomically using a temporary file and replace, and refuses to overwrite an existing workflow on initialization. **It does not implement inter-process locking**: do not run multiple writers simultaneously. Evidence strings are not checked against the filesystem and should not be interpreted as verified completion.

A new workflow version must include a migration strategy and regression tests. Do not silently change v1 semantics.

## Operational guidance

- Supply a specific artifact reference to `complete --evidence` each time; check the artifact and the work before completing a stage.
- Supply a reason to `block --evidence`. In v1 the evidence list contains both blocker reasons and artifact references, so review its entries in context.
- Use a single writer at a time. Atomic replacement prevents partial files but does not prevent lost updates from concurrent transitions.
- Back up checkpoints before recovery or upgrades. Completed stages cannot be reopened; retain the old checkpoint and start a new workflow if correction is needed.
- Treat checkpoint data as potentially sensitive. Avoid storing secrets in references, evidence, or blocker reasons.
- When changing the state contract, preserve existing v1 files or introduce a versioned migration and tests covering older checkpoints.
