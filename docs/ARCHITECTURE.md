# Архитектура

[English](ARCHITECTURE.en.md)

## Единственный источник детерминированной семантики

В `0.3.0` Python остаётся authoritative source для детерминированных Case semantics. Portable subset вынесен в `plugins/mind-detective/scripts/portable_kernel.py` и certified intrinsics. Web не содержит вручную поддерживаемого второго reducer: TypeScript executor генерируется из проверенного Python source и коммитится как воспроизводимый artifact вместе с identity metadata.

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
                 │         ├── differential conformance corpus
                 │         ▼
                 │   Nuxt local executor
                 │         │
                 │         ▼
                 │   IndexedDB atomic transaction
                 │   canonical Case + execution receipt
                 │
                 └── FastAPI compatibility / proposal boundary
                                      │
                           assistant ──┴──► LiteLLM Proxy
```

## Local execution boundary

Case creation, deterministic commands и checklist proposals выполняются в браузере через generated certified artifact. `apps/web/app/lib/execution/localExecutor.ts` добавляет persistence/idempotence boundary, но не определяет собственную domain semantics.

Каждая command mutation вычисляется из canonical input Case и immutable command envelope. Case и execution receipt записываются одной IndexedDB transaction. Повтор того же `command_id` с тем же input возвращает уже сохранённый canonical result; повтор id с другим input fail-closed. Failed transaction не должна частично менять persisted Case.

`mind-detective-case/v2` остаётся текущей схемой данных. `0.3.0` не вводит Case v3, cloud sync, Pyodide/WASM, Bayesian/POD, calibrated location probabilities или hidden belief state.

## Generator и conformance

Generator принимает только restricted AST/call surface и certified intrinsics. Запрещённые/неподдержанные конструкции отклоняются до emission. CI повторно генерирует artifact и corpus и требует byte-level отсутствия diff.

Committed conformance corpus содержит deterministic vectors для create, commands, proposal и planner. Vitest прогоняет каждый vector против generated TypeScript executor. Это подтверждает observable parity покрытого portable contract, а не общую эквивалентность произвольного Python и TypeScript.

## API и assistant boundary

FastAPI остаётся stateless compatibility boundary и server-side proposal boundary. Он не является обязательным mutation path для deterministic Web commands и не хранит Case database.

Assistant proposal отправляется на сервер только при необходимости live-model generation. Клиент передаёт execution identity: `version`, `kernel_sha256`, `generated_sha256`, `generator_version`. Server сравнивает identity до provider creation; mismatch возвращает `MD_WEB_EXECUTION_CONTRACT_MISMATCH` и не вызывает model provider. Уже committed local deterministic mutation при этом не откатывается.

При transport failure assistant arm использует local deterministic checklist fallback. После восстановления сети старый model request не воспроизводится ретроспективно.

## Persistence, PWA и privacy boundary

Web canonical persistence — IndexedDB. Service worker precache содержит application shell/static assets; `/api/`, Case payload, user text, model output и evaluation records не кэшируются и Case commands не используют Background Sync. После preload canonical search workflow выполняется офлайн.

Plugin surface сохраняет explicit case-local file contract `.mind-detective/cases/<case-id>/case.json`. Web и plugin surfaces не создают cross-case learning/profile.

## Проверяемые границы

Нормативные `MD-REQ-*`, `MD-WEB-REQ-*` и `MD-OFFLINE-REQ-*` находятся в `REQUIREMENTS.md` и имеют exact selectors в `CONTRACT_MATRIX.json`. CI на exact head проверяет Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, generated-artifact freshness, conformance corpus, frozen pnpm install, Vitest, production PWA build, Playwright Chromium/WebKit и secret scan.

Ключевые решения зафиксированы в ADR, включая [ADR 013](adr/013-generated-portable-local-execution.md) и [ADR 014](adr/014-execution-identity-skew-gate.md).
