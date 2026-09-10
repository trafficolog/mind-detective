# Архитектура

[English](ARCHITECTURE.en.md)

## Единственный доменный источник истины

Канонический `Case` вместе с Python `CaseController` остаётся единственным детерминированным центром состояния. Версия 0.2.0 добавляет Web/PWA, но **не** переносит доменную машину состояний в TypeScript и не создаёт второй reducer. Nuxt-клиент отправляет команды и принимает полный канонический Case от API.

Плагинный runtime по-прежнему разделяет provenance (`statements.py`), последовательность с сохранением неопределённости (`timeline.py`), физические проверки (`search_log.py`), категориальный выбор одного следующего действия (`planner.py`), guard-проверки (`guard.py`), локальное файловое хранение plugin surface (`store.py`) и derived artifacts (`artifacts.py`). Safety routing выполняется до обычной логики поиска.

## Web/PWA 0.2.0

```text
Nuxt 4 PWA
  │  IndexedDB: browser-local canonical Case copy
  │  sequential command queue / reviewed RU+EN copy
  ▼
FastAPI stateless adapter
  │
  ├── Python CaseController / planner / guard / artifacts
  │
  └── proposal adapter ──► LiteLLM Proxy ──► configured model provider
```

`apps/web` отвечает за представление, локальную IndexedDB persistence, PWA shell, импорт/экспорт и interaction telemetry без raw case content. `apps/api` — тонкий stateless transport adapter: он не хранит пользовательские кейсы и не становится новым владельцем доменного состояния.

Для AI-arm единственный live model gateway — LiteLLM Proxy. Клиенту не передаются provider credentials; модельный вывод проходит server-side proposal/guard boundary и превращается в reviewed proposal contract. Checklist и AI arms используют один production shell и одинаковый canonical mutation path.

## Persistence и PWA boundary

Web-кейсы хранятся в IndexedDB. Service worker кэширует только application shell/static assets: `/api/`, Case payload, пользовательский текст, model output и evaluation records не входят в PWA cache и не отправляются через background sync. Persistent-storage API используется только как browser capability request и не интерпретируется как гарантия резервного копирования. Для переносимости есть явный JSON export/import с deterministic v1→v2 migration.

Plugin surface сохраняет прежний explicit case-local file persistence contract `.mind-detective/cases/<case-id>/case.json`; Web storage не меняет этот контракт и не создаёт cross-case learning/profile.

## Проверяемые границы

Нормативные требования находятся в `REQUIREMENTS.md`, а exact traceability — в `CONTRACT_MATRIX.json`. CI проверяет Python 3.10/3.13, API, Ruff, strict Mypy, frozen pnpm install, Vitest, production PWA build, Playwright Chromium/WebKit и secret scan на exact PR head SHA.

Eval/browser fixtures подтверждают конкретные control paths, но не доказывают научную валидность продукта или semantic compliance произвольного live-model ответа. Архитектурные решения зафиксированы в `docs/adr/`.
