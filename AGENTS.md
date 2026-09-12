# Agent instructions

- Canonical product: systematic lost-item search assistant, not memory restoration or mechanism diagnosis.
- Follow `docs/SDD_TDD_WORKFLOW.md` and `docs/CONTRACT_MATRIX.json`.
- Production code requires a failing test first.
- Keep `plugins/mind-detective/scripts/` standard-library-only and transport-free.
- Preserve statement provenance, unknowns, repeated SearchChecks, and case-local persistence.
- Keep exactly five production skills unless an explicitly approved architecture change says otherwise.
- Never introduce numerical location probability, POD, Bayesian state, hidden belief weight, or cross-case learning into the current product contract.
- Web/PWA is the physical Search/checklist surface; full reconstruction remains plugin/agent capability unless that boundary is explicitly redesigned.
- Do not merge or publish without explicit human authorization and exact-SHA verification.
