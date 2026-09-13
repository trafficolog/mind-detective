# MIND Detective / Детектив памяти

<!-- release-0.4.0 -->

[English](README.en.md)

**MIND Detective — помощник систематического поиска потерянных вещей.** Он разгружает рабочую память во время поиска: отделяет рассказ пользователя от гипотез, сохраняет проверяемые сведения, ведёт журнал физических проверок и позволяет продолжить кейс позже.

> Текущая release line и declarative intent — `0.4.0` (Web Reconstruction Foundation). Опубликованный predecessor `0.3.1` остаётся immutable history; создание тегов и GitHub Releases для `0.4.0` выполняется только через отдельный human-authorized publisher gate после зелёного exact-main CI.

## Web Reconstruction в `0.4.0`

Reconstruction является частью Web/PWA и остаётся отдельным режимом от физического Search:

- сначала пользователь вводит **свободный рассказ**, который сохраняется **дословно** как `free_account` и не превращается автоматически в recollection/habit/observation;
- структурированные сведения добавляются только как явно **подтверждённые пользователем** evidence;
- timeline строится каноническими portable semantics и сохраняет **неизвестные интервалы** и **противоречия**, а не заполняет пробелы правдоподобными догадками;
- Reconstruction не подсказывает новые конкретные места как будто они следуют из памяти пользователя и не устанавливает фактическую локацию предмета;
- переход в Search выполняется явно через `set_mode(search)` и не повышает статус reconstruction evidence;
- `record_free_account` и `rebuild_timeline` исполняются через generated local executor и IndexedDB, поэтому локальная детерминированная reconstruction работает после preload PWA без live model;
- live-model clarification не является зависимостью core reconstruction path и не может записывать canonical recollection/habit/observation от имени пользователя.

Схема Case остаётся `mind-detective-case/v2`.

## Архитектура

```text
portable Python kernel
        │
        ├── certified generator ──► committed TypeScript executor
        │                              │
        │                              ├── record_free_account
        │                              ├── rebuild_timeline
        │                              ▼
        │                    local executor + IndexedDB
        │                    Case + execution receipt
        │
        └── FastAPI assistant boundary
                    │
                    └── LiteLLM/provider (Search assistant arm only)
```

Python остаётся authoritative source deterministic semantics. Vue-компоненты Reconstruction собирают пользовательский ввод и отображают canonical state, но не владеют reconstruction truth и не содержат параллельного timeline/reconstruction reducer.

## Offline и AI

Deterministic create/mutation/reconstruction/search/checklist/import path работает локально. Service worker кэширует только application shell/static assets и не кэширует Case/user/model/evaluation data или `/api/`; Background Sync для Case-команд не используется.

Reconstruction core не требует model provider. В Search assistant arm server-side proposal boundary используется только для assistant proposal. Каждый online assistant request несёт execution identity (`version`, `kernel_sha256`, `generated_sha256`, `generator_version`); mismatch блокируется до provider creation. При transport failure Search UI использует локальный deterministic fallback и не переигрывает старый model request после reconnect.

## Хранение и приватность

Web canonical persistence — IndexedDB на устройстве; новый Web Case сохраняется локально сразу. Verbatim `free_account`, user-confirmed statements, timeline unknowns/contradictions и Search state входят в тот же Case v2 и сохраняются локально. Explicit JSON export/import остаётся способом переносимости.

Plugin surface отдельно сохраняет case-local файл `.mind-detective/cases/<case-id>/case.json` только при явном persistence action. Browser-local storage не означает, что online Search assistant context никогда не покидает устройство: только минимально необходимый transient context проходит через LiteLLM и настроенного provider при online assistant proposal. Deterministic Reconstruction сам по себе provider не вызывает.

## Границы продукта

Продукт не диагностирует причину забывания, не утверждает фактическую локацию предмета, не гарантирует результат поиска и не присваивает локациям калиброванные вероятности. Reconstruction структурирует только рассказ пользователя и подтверждённые им сведения; Search отвечает за физические проверки и предложения следующих действий. High-risk uncertainty маршрутизируется отдельно от ordinary physical-search reasoning.

## Release `0.4.0`

`0.4.0` фиксирует Web Reconstruction Foundation как minor release: state-first free account, user-confirmed evidence, uncertainty-preserving timeline, explicit Search transition, offline local execution и Case v2 portability. Publication не меняет исторические release/tag surfaces и выполняется только hardened repository-native publisher после отдельной авторизации.

## Разработка и проверка

Нормативные контракты `MD-REQ-*`, `MD-WEB-REQ-*` и `MD-OFFLINE-REQ-*`, включая `MD-WEB-REQ-RECONSTRUCT-01..10`, имеют exact selectors в `docs/CONTRACT_MATRIX.json`. CI на exact PR head проверяет Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, generated artifact freshness, conformance corpus, frozen pnpm install, Vitest, production PWA build, Playwright Chromium/WebKit и secret scan.

См. [Getting Started](docs/GETTING_STARTED.md), [Architecture](docs/ARCHITECTURE.md), [Privacy](docs/PRIVACY.md), [Product Evaluation](docs/PRODUCT_EVALUATION.md), [Methodology](docs/METHODOLOGY.md), [ADR 015](docs/adr/015-web-reconstruction-portable-boundary.md) и [Release Policy](docs/RELEASE_POLICY.md).
