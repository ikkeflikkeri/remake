---
name: remake
description: Coordinate a staged application remake from authorized reference material. Use when a user explicitly asks to recreate or rebuild an app or website with a research-to-release workflow; do not use for isolated debugging or ordinary feature requests.
---

# Remake (foundation)

This is the initial scaffold, **not an operational end-to-end orchestrator**.

## Safety and scope

- Use only sources the user is authorized to access.
- Do not copy proprietary source code, trademarks, or copyrighted assets.
- Ask for explicit approval before publishing, deployment, payments, or other external side effects.
- Do not claim that tests, visual comparisons, or deployments passed unless actually run.

## Current behavior

1. Clarify the reference and authorized scope.
2. Identify the target stack and requested fidelity.
3. Produce a proposed plan with measurable acceptance criteria.
4. Explain that execution stages are not implemented in this release.

## Next implementation

Introduce a validated workflow state contract and checkpointed stage execution.
