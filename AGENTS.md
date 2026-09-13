# Agent instructions

- Canonical product: systematic lost-item search assistant, not memory restoration or mechanism diagnosis.
- Follow `docs/SDD_TDD_WORKFLOW.md` and `docs/CONTRACT_MATRIX.json`.
- Production code requires a failing test first.
- Keep `plugins/mind-detective/scripts/` standard-library-only and transport-free.
- Preserve statement provenance, unknowns, contradictions, repeated SearchChecks, and case-local persistence.
- Keep exactly five production skills unless an explicitly approved architecture change says otherwise.
- Never introduce numerical location probability, POD, Bayesian state, hidden belief weight, or cross-case learning into the current product contract.
- Released Web/PWA `0.4.0` supports deterministic, state-first Reconstruction and Search. Reconstruction follows free account → user-confirmed structured evidence → timeline/unknowns/contradictions → explicit transition to Search; it must not depend on a live model or let assistant output become memory evidence.
- Python remains the authoritative source for deterministic Case semantics; Web executes certified/generated local semantics rather than a handwritten domain reducer.
- Current Web Reconstruction implementation contract: `docs/superpowers/specs/2026-09-12-mind-detective-0.4.0-web-reconstruction-design.md` and `docs/superpowers/plans/2026-09-12-mind-detective-web-reconstruction-0.4.0.md`.
- The approved `0.4.1` Reconstruction Assistant work is research/design only until its explicit Go/No-Go process completes: `docs/superpowers/specs/2026-09-13-mind-detective-0.4.1-reconstruction-assistant-research.md` and `docs/superpowers/plans/2026-09-13-mind-detective-0.4.1-reconstruction-assistant-design.md`.
- A research assistant may propose only a candidate clarification question; it must not create recollection/habit/observation, timeline events, Search targets, mode transitions, confidence/location probabilities, or other canonical Case mutations.
- Do not merge or publish without explicit human authorization and exact-SHA verification.
