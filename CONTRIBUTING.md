# Contributing

MIND Detective uses SDD + strict TDD. Start from the canonical design and implementation plan under `docs/superpowers/`.

For behavior changes: write one failing test, verify the expected RED failure, implement the smallest GREEN change, refactor only while green, update exact traceability/evals, then run full verification. Do not add transport/provider dependencies to plugin runtime and do not expand P0 scope without a new approved design slice.

Normative changes to `MD-REQ-*`, schemas, safety routing, persistence, planner ordering, or release governance require explicit review. Published tags/releases are immutable.
