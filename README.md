# Remake

An artifact-driven Claude Code skill pack for researching, rebuilding, verifying, and shipping independently branded applications.

## Status

Phase 1: repository foundation. The orchestrator and specialized skills are **not implemented yet**.

## Principles

- Reimplement functionality using authorized references; do not copy proprietary code or assets.
- Keep each skill narrowly scoped with explicit inputs, outputs, and verification.
- Never deploy or publish without explicit approval.
- Improve instructions, tests, and documentation with each change.

## Development

```bash
python -m unittest discover -s tests -v
python scripts/validate_skills.py
```

## Installation

After publishing this directory to GitHub, configure it as a Claude Code plugin using the `.claude-plugin` manifest. No production commands are implemented in this foundation release.

## Roadmap

1. Repository foundation and automated checks
2. Orchestrator with state transitions and checkpoint contracts
3. Recon and architecture skills
4. Build, test, parity, and release workflows
5. Routing and execution evaluations
