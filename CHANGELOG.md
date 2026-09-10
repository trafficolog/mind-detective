# Журнал изменений

[English](CHANGELOG.en.md)

## [0.2.0] — 2026-09-10

### Добавлено
- mobile-first Nuxt 4 Web/PWA поверх единственного Python `CaseController` без TypeScript domain reducer;
- browser-local IndexedDB persistence, explicit JSON export/import и deterministic `mind-detective-case/v1` → `v2` migration;
- stateless FastAPI adapter без server-side Case database;
- LiteLLM Proxy как единственный live-model gateway AI arm с server-side credentials и structured proposal/guard boundary;
- единый production shell для checklist и AI arms, provenance-aware interaction journal и persistent checked/remaining/inaccessible summary;
- sequential retryable command queue без optimistic canonical mutation;
- нейтральный one-tap `reported_check`, delayed quality clarification и отдельный accessibility state;
- explicit next-action rejection, pause/resume и found/unresolved close flows;
- PWA shell/static caching без API/Case/user/model/evaluation data и без Background Sync;
- browser storage durability disclosure, install education и явный Case export;
- RU/EN reviewed copy parity, keyboard/focus management, dark mode, reduced motion, increased contrast и responsive contracts;
- privacy-filtered browser-local evaluation logging и scenario matrix для Web/PWA;
- 23 active `MD-WEB-REQ-*` с exact selectors в `docs/CONTRACT_MATRIX.json`;
- ADR 009–012 для Web domain boundary, local persistence, shared experiment shell и LiteLLM model-data boundary;
- pinned Node/pnpm toolchain, committed lockfile и frozen-install CI contract.

### Исправлено
- Nuxt auto-import вложенных production components;
- синхронный `DataCloneError` при клонировании Vue reactive Case в command queue;
- преждевременное quality clarification сразу после нового `reported_check`;
- wiring команды pause из production shell;
- раскрытие experimental arm identity в production UI;
- guard journal identity, storage controls и modal focus contracts.

### Релиз
- declarative release intent: repository `0.2.0`, plugin `mind-detective-v0.2.0`;
- существующий hardened publisher остаётся единственным publication path;
- публикация возможна только после human-authorized merge, exact post-merge `main` CI и отдельного human-approved **полного 40-hex target SHA**.

## [0.1.0] — 2026-09-09

### Добавлено
- детерминированный Case Controller и provenance-aware statement model;
- uncertainty-preserving timeline;
- mode-aware reconstruction/search guard;
- физический SearchCheck journal и categorical one-next-action planner;
- explicit case-local save/resume/delete;
- handoff/outcome artifacts;
- ровно пять production skills;
- exact CONTRACT_MATRIX и adversarial eval v2.

Релиз становится опубликованным только после human-authorized merge, exact-main CI и отдельного human-approved publisher gate.
