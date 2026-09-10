# Agent instructions

- Canonical product: systematic lost-item search assistant, not memory restoration or mechanism diagnosis.
- Follow `docs/SDD_TDD_WORKFLOW.md` and `docs/CONTRACT_MATRIX.json`.
- Production code requires a failing test first.
- Keep `plugins/mind-detective/scripts/` standard-library-only and transport-free.
- Preserve statement provenance, unknowns, repeated SearchChecks, and case-local persistence.
- Never introduce numerical location probability, POD, Bayesian state, hidden belief weight, cross-case learning, or a sixth production skill in 0.1.0.
- Do not merge or publish without explicit human authorization and exact-SHA verification.
