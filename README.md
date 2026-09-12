# MIND Detective / Детектив памяти

<!-- release-0.3.1 -->

[English](README.en.md)

**MIND Detective — помощник систематического поиска потерянных вещей.** Он разгружает рабочую память во время поиска: отделяет воспоминания пользователя от гипотез, ведёт журнал физических проверок, предлагает одно следующее действие и сохраняет кейс для продолжения.

## Что добавляет 0.3.1

Версия `0.3.1` — patch-hardening после внешнего review поверх local-first контура `0.3.0`:

- high-risk action uncertainty блокируется на interaction ingress до мутации Case;
- Web Search использует отдельный структурированный target вместо эхо произвольного сообщения;
- active requirement helpers проверяются на production reachability;
- evaluation vocabulary приведён к реально измеряемым decision events;
- Case import валидируется и мигрируется локально без обязательного `/api/v1/case/validate`;
- Web/PWA честно ограничен физическим Search/checklist workflow; полная reconstruction остаётся plugin/agent capability;
- semantic scenario corpus явно помечен как manual review, без ложного automated-runner claim;
- proposal `copy_key` типизирован и рендерится через RU/EN copy;
- PWA содержит installable PNG 192/512 и Apple touch icon;
- API больше не зависит от фиксированной глубины монорепо: plugin root задаётся `MIND_DETECTIVE_PLUGIN_ROOT` либо находится bounded discovery.

`mind-detective-case/v2` остаётся текущей схемой. Cloud sync, Pyodide/WASM, Bayesian/POD, calibrated location percentages и hidden belief state не добавляются.

## Архитектура 0.3.1

```text
portable Python kernel
        │
        ├── certified generator ──► committed TypeScript executor
        │                              │
        │                              ▼
        │                    local executor + IndexedDB
        │                    Case + execution receipt
        │
        └── FastAPI assistant boundary
                    │
                    ├── plugin root: env/discovery
                    └── LiteLLM/provider (assistant arm only)
```

Python остаётся authoritative source semantics. TypeScript artifact генерируется и проверяется conformance corpus; вручную поддерживаемого параллельного Case reducer нет.

## Offline и AI

Deterministic create/mutation/checklist/import path работает локально. Service worker кэширует только application shell/static assets и не кэширует Case/user/model/evaluation data и `/api/`; Background Sync для Case-команд не используется.

AI arm обращается к server-side proposal boundary только для assistant proposal. Каждый запрос несёт execution identity (`version`, `kernel_sha256`, `generated_sha256`, `generator_version`). При mismatch запрос блокируется до provider creation. При transport failure UI использует локальный deterministic fallback и не переигрывает старый model request после reconnect.

## Хранение и приватность

Web canonical persistence — IndexedDB на устройстве; новый Web Case сохраняется локально сразу. Explicit JSON export/import остаётся способом переносимости. Plugin surface отдельно сохраняет case-local файл `.mind-detective/cases/<case-id>/case.json` только при явном persistence action. Browser-local storage не означает, что assistant model context никогда не покидает устройство: только минимально необходимый transient context проходит через LiteLLM и настроенного provider при online assistant proposal.

## Границы продукта

Продукт не диагностирует причину забывания, не утверждает фактическую локацию предмета, не гарантирует результат поиска и не присваивает локациям калиброванные вероятности. High-risk uncertainty маршрутизируется отдельно от ordinary physical-search reasoning. Web/PWA — Search/checklist surface; reconstruction остаётся доступна через plugin/agent workflow.

## Разработка и проверка

Нормативные контракты `MD-REQ-*`, `MD-WEB-REQ-*` и `MD-OFFLINE-REQ-*` имеют exact selectors в `docs/CONTRACT_MATRIX.json`. CI на exact PR head проверяет Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, generated artifact freshness, conformance corpus, frozen pnpm install, Vitest, production PWA build, Playwright Chromium/WebKit и secret scan.

См. [Getting Started](docs/GETTING_STARTED.md), [Architecture](docs/ARCHITECTURE.md), [Privacy](docs/PRIVACY.md), [Product Evaluation](docs/PRODUCT_EVALUATION.md), [Methodology](docs/METHODOLOGY.md) и [Release Policy](docs/RELEASE_POLICY.md).
