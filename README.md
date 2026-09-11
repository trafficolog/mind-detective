# MIND Detective / Детектив памяти

<!-- release-0.3.0 -->

[English](README.en.md)

**MIND Detective — помощник систематического поиска потерянных вещей.** Он разгружает рабочую память во время поиска: отделяет воспоминания пользователя от гипотез, ведёт журнал физических проверок, предлагает одно следующее действие и сохраняет кейс для продолжения.

## Что добавляет 0.3.0

Версия `0.3.0` делает детерминированный Web/PWA контур local-first, не создавая второй вручную поддерживаемый domain reducer:

- authoritative portable Python kernel с ограниченным stdlib-only контрактом;
- certified generator → committed TypeScript executor + identity metadata;
- differential Python↔TypeScript conformance corpus;
- local Case creation и deterministic commands без обязательных `/api/v1/case/*` вызовов;
- atomic IndexedDB commit: canonical Case + execution receipt;
- idempotent retry по `command_id`, conflict reuse fail-closed;
- local deterministic checklist proposal;
- assistant transport fallback без retrospective replay после reconnect;
- execution identity/version/hash skew guard перед model provider;
- preloaded PWA выполняет канонический search workflow офлайн.

`mind-detective-case/v2` остаётся текущей схемой. Cloud sync, Pyodide/WASM, Bayesian/POD, calibrated location percentages и hidden belief state не добавляются.

## Архитектура 0.3.0

```text
portable Python kernel
        │
        ├── certified generator ──► committed TypeScript executor
        │                              │
        │                              ▼
        │                    local executor + IndexedDB
        │                    Case + execution receipt
        │
        └── FastAPI compatibility / proposal boundary
                                       │
                        assistant only ─┴─► LiteLLM Proxy
```

Python остаётся authoritative source semantics. TypeScript artifact генерируется и проверяется conformance corpus; вручную поддерживаемого параллельного Case reducer нет.

## Offline и AI

Deterministic create/mutation/checklist path работает локально. Service worker кэширует только application shell/static assets и не кэширует Case/user/model/evaluation data и `/api/`; Background Sync для Case-команд не используется.

AI arm обращается к server-side proposal boundary только для assistant proposal. Каждый запрос несёт execution identity (`version`, `kernel_sha256`, `generated_sha256`, `generator_version`). При mismatch запрос блокируется до provider creation. При transport failure UI использует локальный deterministic fallback и не переигрывает старый model request после reconnect.

## Хранение и приватность

Web canonical persistence — IndexedDB на устройстве. Explicit JSON export/import остаётся способом переносимости. Plugin surface сохраняет case-local файл `.mind-detective/cases/<case-id>/case.json`. Browser-local storage не означает, что assistant model context никогда не покидает устройство: только минимально необходимый transient context проходит через LiteLLM и настроенного provider при online assistant proposal.

## Границы продукта

Продукт не диагностирует причину забывания, не утверждает фактическую локацию предмета, не гарантирует результат поиска и не присваивает локациям калиброванные вероятности. High-risk uncertainty маршрутизируется отдельно от ordinary physical-search reasoning.

## Разработка и проверка

Нормативные контракты `MD-REQ-*`, `MD-WEB-REQ-*` и `MD-OFFLINE-REQ-*` имеют exact selectors в `docs/CONTRACT_MATRIX.json`. CI на exact PR head проверяет Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, generated artifact freshness, conformance corpus, frozen pnpm install, Vitest, production PWA build, Playwright Chromium/WebKit и secret scan.

См. [Getting Started](docs/GETTING_STARTED.md), [Architecture](docs/ARCHITECTURE.md), [Privacy](docs/PRIVACY.md), [Product Evaluation](docs/PRODUCT_EVALUATION.md) и [Release Policy](docs/RELEASE_POLICY.md).
