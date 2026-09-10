# MIND Detective / Детектив памяти

<!-- release-0.2.0 -->

[English](README.en.md)

**MIND Detective — помощник систематического поиска потерянных вещей.** Он помогает разгрузить рабочую память во время поиска: аккуратно фиксирует воспоминания пользователя без превращения их в «факты», ведёт журнал физических проверок, предлагает одно полезное следующее действие и позволяет продолжить сохранённый кейс после паузы.

## Что добавляет 0.2.0

Версия 0.2.0 сохраняет пять production skills плагина и добавляет mobile-first **Nuxt 4 Web/PWA** поверх того же Python `CaseController`:

- один production shell для checklist и AI arms без отдельной arm-идентичности;
- canonical browser persistence в IndexedDB, явный JSON export/import и deterministic v1→v2 migration;
- stateless FastAPI adapter без server-side Case database;
- sequential retryable command queue без optimistic canonical mutation;
- one-tap `Проверил` как нейтральный `reported_check`, с отложенным уточнением качества;
- reviewed guard fallback без сохранения/показа заблокированного raw proposal;
- PWA shell caching без `/api/`, Case/user/model/evaluation data и без Background Sync;
- RU/EN reviewed copy, keyboard/focus contracts, dark/reduced-motion/increased-contrast support;
- privacy-filtered browser-local evaluation events для сравнения checklist и AI подходов.

Python `Case` + `CaseController` остаются единственным детерминированным источником истины: TypeScript port/domain reducer отсутствует.

## Архитектура

```text
Nuxt 4 PWA
  │  IndexedDB / reviewed RU+EN UI / command queue
  ▼
FastAPI stateless adapter
  │
  ├── Python CaseController / planner / guard / artifacts
  │
  └── AI proposal ──► LiteLLM Proxy ──► configured model provider
```

Checklist и AI проходят один canonical mutation path. В AI arm модель может предложить структурированный candidate action, но model output не становится состоянием автоматически: server-side proposal/guard boundary возвращает только reviewed structured proposal или deterministic fallback.

## LiteLLM для AI arm

Web/API не содержит provider-specific client configuration. Единственный live-model gateway — **LiteLLM Proxy**. Для API задаются server-side переменные:

```bash
export LITELLM_API_KEY="<proxy-key>"
export MIND_DETECTIVE_LITELLM_MODEL="<model-alias-from-litellm>"
export MIND_DETECTIVE_LITELLM_BASE_URL="http://127.0.0.1:4000"  # optional; это default
```

`LITELLM_API_KEY` и provider credentials нельзя помещать в browser bundle. В AI request transiently передаётся только контекст, необходимый для текущего proposal. Поэтому browser-local persistence **не означает**, что данные никогда не покидают устройство: модельный контекст обрабатывается LiteLLM и настроенным model provider согласно их deployment/privacy boundary.

## Хранение и офлайн

Web-кейсы хранятся локально в IndexedDB. Persistent Storage API может уменьшить риск eviction, но не является гарантией backup; для переносимости используйте explicit JSON export. Service worker хранит только shell/static assets. Offline mutation не считается сохранённой, пока API не вернул новый canonical Case; retry повторяет тот же command envelope.

Plugin surface сохраняет прежний explicit local-file contract `.mind-detective/cases/<case-id>/case.json`.

## Чего продукт не заявляет

MIND Detective не является медицинским инструментом, не восстанавливает «истинную» память, не диагностирует причину забывания, не знает фактическую локацию вещи, не присваивает локациям калиброванные проценты и не использует Bayesian/POD/hidden belief weight. Повторные быстрые проверки не считаются независимыми доказательствами отсутствия. Неопределённость о high-risk действии выводится из ordinary physical-search reasoning.

## Разработка и проверка

Проект использует SDD + TDD: `SPEC → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY`. Нормативные `MD-REQ-*` и `MD-WEB-REQ-*` связаны с exact selectors в `docs/CONTRACT_MATRIX.json`. CI на exact PR head проверяет Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, frozen pnpm install, Vitest, production PWA build, Playwright Chromium/WebKit и secret scan.

Начните с [Getting Started](docs/GETTING_STARTED.md), затем см. [Architecture](docs/ARCHITECTURE.md), [Methodology](docs/METHODOLOGY.md), [Privacy](docs/PRIVACY.md), [Product Evaluation](docs/PRODUCT_EVALUATION.md) и [Release Policy](docs/RELEASE_POLICY.md).
