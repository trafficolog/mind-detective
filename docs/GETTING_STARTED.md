# Быстрый старт

[English](GETTING_STARTED.en.md)

## Plugin surface

Канонический plugin id — `mind-detective`, текущая опубликованная версия — `0.3.1`. Пять production skills сохраняются: router, reconstruct, plan, resume и close. Plugin runtime использует Python standard library и не требует сетевых credentials.

Plugin persistence остаётся явным и case-local: сохранение идёт в `.mind-detective/cases/<case-id>/case.json` по explicit persistence action. Web/PWA имеет отдельный browser-local persistence contract и записывает новый Case в IndexedDB сразу.

В `main` уже реализован deterministic Web Reconstruction foundation для следующего release gate; это не меняет опубликованную версию до отдельной release authorization.

## Установка зависимостей

Из корня репозитория:

```bash
python -m pip install -e apps/api
pnpm install --frozen-lockfile
```

Скопируйте `.env.example` в локальное окружение и задайте только нужные значения. Никогда не коммитьте реальные ключи.

## API

Для запуска из монорепо plugin root и execution metadata находятся автоматически bounded discovery:

```bash
uvicorn mind_detective_api.app:app --app-dir apps/api --host 127.0.0.1 --port 8000 --reload
```

Для отдельно упакованного/перемещённого API пути задаются явно:

```bash
export MIND_DETECTIVE_PLUGIN_ROOT=/absolute/path/to/plugins/mind-detective
export MIND_DETECTIVE_EXECUTION_METADATA=/absolute/path/to/localExecution.meta.json
uvicorn mind_detective_api.app:app --app-dir apps/api --host 127.0.0.1 --port 8000
```

Assistant transport настраивается переменными `LITELLM_API_KEY`, `MIND_DETECTIVE_LITELLM_MODEL` и `MIND_DETECTIVE_LITELLM_BASE_URL`. Без assistant arm deterministic Web path остаётся local-first.

## Web/PWA

```bash
pnpm --dir apps/web dev --host 127.0.0.1 --port 3000
```

Web runtime variables:

- `NUXT_PUBLIC_MIND_DETECTIVE_API_BASE` — API base URL, по умолчанию `http://127.0.0.1:8000`;
- `NUXT_PUBLIC_MIND_DETECTIVE_ARM` — `checklist` или `assistant`;
- `NUXT_PUBLIC_MIND_DETECTIVE_LOCALE` — `auto`, `ru` или `en`;
- `NUXT_PUBLIC_MIND_DETECTIVE_EVALUATION=1` — явное включение evaluation UI.

### Reconstruction flow

Для свежего Case можно явно войти в Reconstruction до начала физических проверок:

1. Введите **свободный рассказ**. Он сохраняется **дословно** как `free_account`; подробные structured statements до этого шага недоступны.
2. Добавляйте только подтверждённые пользователем structured recollection/habit/observation. UI не выводит новые concrete locations из предположений.
3. Соберите timeline. `rebuild_timeline` выполняется portable authoritative semantics и сохраняет неизвестные интервалы и противоречия явно.
4. При готовности выберите переход в Search. `set_mode(search)` меняет режим явно и сохраняет reconstruction evidence без promotion.

`record_free_account`, `rebuild_timeline`, Search mutations и Case persistence проходят через generated local executor и IndexedDB. Схема остаётся `mind-detective-case/v2`.

### Offline proof

Service worker кэширует только shell/static assets. Чтобы проверить реальный offline path, сначала загрузите PWA online и дождитесь active service worker, затем отключите сеть. Create → Reconstruction free account → user-confirmed evidence → timeline rebuild → Search → check/pause-resume/close/export/import deterministic path не должен зависеть от Case API или model provider.

Live-model clarification не является dependency local deterministic Reconstruction. Assistant proposal boundary используется отдельно в Search assistant arm.

## Проверка для разработчика

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -v
python -m scripts.write_local_execution_artifacts
python -m scripts.generate_local_execution_corpus
pnpm install --frozen-lockfile
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

Generated files должны оставаться byte-clean после повторной генерации. Production merge выполняется только после exact-head CI; release — после explicit human authorization и exact post-merge `main` CI через hardened publisher.
