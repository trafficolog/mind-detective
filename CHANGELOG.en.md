# Changelog

[Русский](CHANGELOG.md)

## [0.3.1] — 2026-09-12

### Fixed
- high-risk action uncertainty is now stopped at interaction ingress before Case mutation;
- Web Search uses a structured checklist target instead of echoing arbitrary user prose;
- the check action now explicitly matches the stored `not_found` result: “Checked — not found”;
- canonical `checked` state takes precedence over stale inaccessible metadata in the progress summary;
- active contract-matrix helpers are checked for production reachability and obsolete queue/privacy helpers were removed;
- the live evaluation-event vocabulary now matches the decision events the product actually emits;
- Case import validates and migrates locally without requiring `/api/v1/case/validate`;
- Web/PWA no longer presents an unfinished reconstruction surface: it is the physical Search/checklist workflow, while full reconstruction remains a plugin/agent capability;
- plugin-only reconstruction mutations are behind an explicit reducer boundary;
- the semantic eval corpus is explicitly governed as manual review and is not presented as an automated runner;
- proposal `copy_key` is typed and rendered through RU/EN copy;
- installable 192/512 PNG and Apple touch PWA icons were added;
- API plugin-root and execution-metadata resolution no longer depend on fixed monorepo parent depth;
- RU/EN README, Getting Started, plugin standard, semantic scenarios, and reference docs are aligned with the current product contract;
- four scientific DOI references were re-verified and recorded in `docs/REFERENCE_VERIFICATION.json`.

### Unchanged
- the Case schema remains `mind-detective-case/v2`;
- no Bayesian/POD state, calibrated location probabilities, cloud sync, or new production skill is introduced.

## [0.3.0] — 2026-09-11

### Added
- a restricted portable Python kernel as the authoritative executable semantics for local execution;
- certified Python→TypeScript generation, a committed generated executor, and identity metadata;
- a deterministic conformance corpus for Python↔TypeScript observable parity;
- local-first Case creation, deterministic commands, and checklist proposals;
- atomic IndexedDB Case + execution receipt commits, idempotent retry, and command-id conflict protection;
- assistant transport fallback without reconnect replay plus an execution-contract skew guard;
- a full offline PWA vertical slice after shell preload;
- 16 active `MD-OFFLINE-REQ-*` contracts with exact traceability.

### Changed
- FastAPI remains a stateless compatibility/proposal boundary but is no longer the required mutation path for deterministic Web commands;
- Web has no hand-maintained Case reducer: it executes only the generated certified artifact;
- release intent is now repository `0.3.0` and plugin `mind-detective-v0.3.0`.

## [0.2.0] — 2026-09-10

### Added
- a mobile-first Nuxt 4 Web/PWA over the single Python `CaseController`, with no TypeScript domain reducer;
- browser-local IndexedDB persistence, explicit JSON export/import, and deterministic `mind-detective-case/v1` → `v2` migration;
- a stateless FastAPI adapter with no server-side Case database;
- LiteLLM Proxy as the only live-model gateway for the AI arm, with server-side credentials and a structured proposal/guard boundary;
- one production shell for checklist and AI arms, a provenance-aware interaction journal, and persistent checked/remaining/inaccessible summary;
- a sequential retryable command queue with no optimistic canonical mutation;
- neutral one-tap `reported_check`, delayed quality clarification, and separate accessibility state;
- explicit next-action rejection, pause/resume, and found/unresolved close flows;
- PWA shell/static caching without API/Case/user/model/evaluation data and without Background Sync;
- browser-storage durability disclosure, install education, and explicit Case export;
- reviewed RU/EN copy parity, keyboard/focus management, dark mode, reduced motion, increased contrast, and responsive contracts;
- privacy-filtered browser-local evaluation logging plus the Web/PWA scenario matrix;
- 23 active `MD-WEB-REQ-*` requirements with exact selectors in `docs/CONTRACT_MATRIX.json`;
- ADR 009–012 for the Web domain boundary, local persistence, shared experiment shell, and LiteLLM model-data boundary;
- pinned Node/pnpm toolchain, committed lockfile, and frozen-install CI contract.

## [0.1.0] — 2026-09-09

### Added
- deterministic Case Controller and provenance-aware statement model;
- uncertainty-preserving timeline;
- mode-aware reconstruction/search guard;
- physical SearchCheck journal and categorical one-next-action planner;
- explicit case-local save/resume/delete;
- handoff/outcome artifacts;
- exactly five production skills;
- exact CONTRACT_MATRIX and adversarial eval v2.
