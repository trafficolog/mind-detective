# Changelog

[Русский](CHANGELOG.md)

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

### Fixed
- Nuxt auto-import resolution for nested production components;
- synchronous `DataCloneError` when cloning a Vue-reactive Case in the command queue;
- premature quality clarification immediately after a new `reported_check`;
- pause-command wiring from the production shell;
- experimental-arm identity leaking into production UI;
- guard journal identity, storage-control mounting, and modal focus contracts.

### Release
- declarative release intent: repository `0.2.0`, plugin `mind-detective-v0.2.0`;
- the existing hardened publisher remains the only publication path;
- publication is allowed only after human-authorized merge, exact post-merge `main` CI, and a separate human-approved **full 40-hex target SHA**.

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

A release is published only after human-authorized merge, exact-main CI, and a separate human-approved publisher gate.
