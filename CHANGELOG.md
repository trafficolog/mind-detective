# Журнал изменений

[English](CHANGELOG.en.md)

## [0.4.0] — 2026-09-13

### Добавлено
- полноценный state-first Web Reconstruction workflow: free account → user-confirmed structure → timeline → explicit Search transition;
- канонические portable-команды `record_free_account` и `rebuild_timeline` с free-account-first gate;
- отображение неизвестных интервалов и противоречий без устранения неопределённости догадками;
- локальный offline Reconstruction после preload PWA через generated executor и IndexedDB;
- сохранение Reconstruction state при reload и Case v2 export/import;
- 10 active `MD-WEB-REQ-RECONSTRUCT-*` contracts с exact production reachability и test selectors;
- ADR 015 и RU/EN документация deterministic Web Reconstruction boundary.

### Изменено
- Web/PWA больше не ограничен Search/checklist: Reconstruction доступен как отдельный режим, визуально и семантически отделённый от Search;
- Python portable semantics остаются единственным authoritative source для deterministic Reconstruction/Search mutations;
- release intent обновлён до repository `0.4.0` и plugin `mind-detective-v0.4.0`.

### Не изменено
- схема Case остаётся `mind-detective-case/v2`;
- live model не требуется для core Reconstruction и не может писать canonical memory evidence;
- не добавлены Bayesian/POD state, calibrated probabilities, hidden belief state, cloud Case DB, background sync или cross-case learning.

## [0.3.1] — 2026-09-12

### Исправлено
- high-risk action uncertainty теперь блокируется на interaction ingress до мутации Case;
- Web Search использует структурированный checklist target вместо эхо произвольного сообщения пользователя;
- подпись проверки явно соответствует записываемому результату `not_found`: «Проверил — не нашёл»;
- `checked` имеет приоритет над stale inaccessible metadata в progress summary;
- active helpers в contract matrix проверяются на production reachability; удалены obsolete queue/privacy helpers;
- live evaluation event vocabulary приведён к реально эмитируемым decision events;
- Case import выполняет validation/migration локально без обязательного `/api/v1/case/validate`;
- Web/PWA больше не имитирует незавершённую reconstruction surface: это физический Search/checklist workflow, полная reconstruction остаётся plugin/agent capability;
- plugin-only reconstruction mutations заведены за явную reducer boundary;
- semantic eval corpus честно объявлен manual review и не выдаётся за automated runner;
- proposal `copy_key` типизирован и реально рендерится через RU/EN copy;
- добавлены installable PNG 192/512 и Apple touch PWA icons;
- API plugin root и execution metadata больше не зависят от фиксированной глубины монорепо;
- RU/EN README, Getting Started, plugin standard, semantic scenarios и reference docs синхронизированы с текущим product contract;
- четыре научных DOI повторно проверены и зафиксированы в `docs/REFERENCE_VERIFICATION.json`.

### Не изменено
- схема Case остаётся `mind-detective-case/v2`;
- не добавлены Bayesian/POD state, calibrated location probabilities, cloud sync или новый production skill.

## [0.3.0] — 2026-09-11

### Добавлено
- restricted portable Python kernel как authoritative executable semantics для local execution;
- certified Python→TypeScript generator, committed generated executor и identity metadata;
- deterministic conformance corpus для Python↔TypeScript observable parity;
- local-first Case creation, deterministic commands и checklist proposals;
- atomic IndexedDB Case + execution receipt commit, idempotent retry и command-id conflict protection;
- assistant transport fallback без reconnect replay и execution-contract skew guard;
- full offline PWA vertical slice после предварительной загрузки shell;
- 16 active `MD-OFFLINE-REQ-*` contracts с exact traceability.

### Изменено
- FastAPI остаётся stateless compatibility/proposal boundary, но больше не является обязательным mutation path для deterministic Web commands;
- Web не содержит hand-maintained Case reducer: выполняется только generated certified artifact;
- release intent обновлён до repository `0.3.0` и plugin `mind-detective-v0.3.0`.

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
