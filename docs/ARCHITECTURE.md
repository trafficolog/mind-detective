# Архитектура

[English](ARCHITECTURE.en.md)

## Единственный источник детерминированной семантики

Python остаётся authoritative source для deterministic Case semantics. Portable subset находится в `plugins/mind-detective/scripts/portable_kernel.py` и certified intrinsics. Web не содержит второго вручную поддерживаемого reducer: TypeScript executor генерируется из проверенного Python source и коммитится вместе с identity metadata.

```text
portable Python kernel + certified intrinsics
                 │
                 ├── AST/certification gate
                 │
                 ├── deterministic generator
                 │         │
                 │         ▼
                 │   committed TypeScript executor + metadata
                 │         │
                 │         ├── record_free_account
                 │         ├── rebuild_timeline
                 │         ├── differential conformance corpus
                 │         ▼
                 │   Nuxt local executor
                 │         │
                 │         ▼
                 │   IndexedDB atomic transaction
                 │   canonical Case + execution receipt
                 │
                 └── FastAPI compatibility / Search proposal boundary
                                      │
                           assistant ──┴──► LiteLLM Proxy
```

## Local execution boundary

Case creation, deterministic commands, Reconstruction и checklist proposals выполняются в браузере через generated certified artifact. `apps/web/app/lib/execution/localExecutor.ts` добавляет persistence/idempotence boundary, но не определяет собственную domain semantics.

Каждая command mutation вычисляется из canonical input Case и immutable command envelope. Case и execution receipt записываются одной IndexedDB transaction. Повтор того же `command_id` с тем же input возвращает уже сохранённый canonical result; повтор id с другим input fail-closed. Failed transaction не должна частично менять persisted Case.

`mind-detective-case/v2` остаётся текущей схемой данных. Реализация Web Reconstruction не вводит Case v3, cloud sync, Pyodide/WASM, Bayesian/POD, calibrated location probabilities или hidden belief state.

## Reconstruction boundary

Web Reconstruction — state-first local deterministic reconstruction, а не отдельный chatbot/reducer contour.

1. `record_free_account` сохраняет свободный рассказ пользователя дословно как `author=user`, `mode=reconstruction`, `entry_type=free_account`. Он не создаёт structured statement автоматически.
2. После free-account gate пользователь может явно подтвердить structured recollection/habit/observation. Canonical evidence остаётся user-originated/user-confirmed.
3. `rebuild_timeline` валидирует ссылки на statements и атомарно сохраняет canonical timeline, включая неизвестные интервалы и противоречия.
4. Vue-компоненты только собирают payloads и отображают canonical state. Они не владеют reconstruction truth, не вычисляют competing timeline semantics и не разрешают неопределённость по plausibility.
5. `set_mode(search)` выполняет явный переход в Search; evidence не переписывается и не повышается в статусе.

Новые concrete locations не выводятся из реконструкции. User-supplied location можно сохранить как часть подтверждённого пользователем материала, но Search proposal — отдельная семантическая категория.

## Generator и conformance

Generator принимает только restricted AST/call surface и certified intrinsics. Запрещённые/неподдержанные конструкции отклоняются до emission. CI повторно генерирует artifact и corpus и требует byte-clean отсутствия diff.

Committed conformance corpus содержит deterministic vectors для create, commands, proposal, planner и Reconstruction commands. Vitest прогоняет каждый vector против generated TypeScript executor. Это подтверждает observable parity покрытого portable contract, а не общую эквивалентность произвольного Python и TypeScript.

## API и assistant boundary

FastAPI остаётся stateless compatibility boundary и server-side Search proposal boundary. Он не является обязательным mutation path для deterministic Web commands и не хранит Case database.

Live-model clarification не является dependency Reconstruction core path. Reconstruction не вызывает `nextProposal()` и не даёт model output права записывать canonical recollection/habit/observation. Assistant proposal пересекает server boundary только в Search assistant arm. Клиент передаёт execution identity (`version`, `kernel_sha256`, `generated_sha256`, `generator_version`); mismatch возвращает `MD_WEB_EXECUTION_CONTRACT_MISMATCH` до provider creation.

При transport failure Search assistant arm использует local deterministic checklist fallback. После восстановления сети старый model request не воспроизводится ретроспективно.

## Persistence, PWA и privacy boundary

Web canonical persistence — IndexedDB. Service worker precache содержит application shell/static assets; `/api/`, Case payload, user text, model output и evaluation records не кэшируются и Case commands не используют Background Sync. После preload canonical Search и Reconstruction deterministic paths выполняются офлайн.

Verbatim free account, user-confirmed structured evidence, timeline unknowns/contradictions и Search state находятся в одном Case v2. Explicit JSON export/import сохраняет этот reconstruction state без отдельной schema migration.

Plugin surface сохраняет explicit case-local file contract `.mind-detective/cases/<case-id>/case.json`. Web и plugin surfaces не создают cross-case learning/profile.

## Проверяемые границы

Нормативные `MD-REQ-*`, `MD-WEB-REQ-*` и `MD-OFFLINE-REQ-*` находятся в `REQUIREMENTS.md` и имеют exact selectors в `CONTRACT_MATRIX.json`. Reconstruction покрывается `MD-WEB-REQ-RECONSTRUCT-01..10`. CI на exact head проверяет Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, generated-artifact freshness, conformance corpus, frozen pnpm install, Vitest, production PWA build, Playwright Chromium/WebKit и secret scan.

Ключевые решения зафиксированы в ADR, включая [ADR 013](adr/013-generated-portable-local-execution.md), [ADR 014](adr/014-execution-identity-skew-gate.md) и [ADR 015](adr/015-web-reconstruction-portable-boundary.md).
