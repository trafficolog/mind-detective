# Быстрый старт

[English](GETTING_STARTED.en.md)

## Plugin surface

Канонический plugin id — `mind-detective`, версия `0.3.1`. Пять production skills сохраняются: router, reconstruct, plan, resume и close. Plugin runtime использует Python standard library и не требует сетевых credentials.

Plugin persistence остаётся явным и case-local: сохранение идёт в `.mind-detective/cases/<case-id>/case.json` по explicit persistence action. Web/PWA имеет отдельный browser-local persistence contract и записывает новый Case в IndexedDB сразу.

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

## Web/PWA 0.3.1

```bash
pnpm --dir apps/web dev --host 127.0.0.1 --port 3000
```

Web runtime variables:

- `NUXT_PUBLIC_MIND_DETECTIVE_API_BASE` — API base URL, по умолчанию `http://127.0.0.1:8000`;
- `NUXT_PUBLIC_MIND_DETECTIVE_ARM` — `checklist` или `assistant`;
- `NUXT_PUBLIC_MIND_DETECTIVE_LOCALE` — `auto`, `ru` или `en`;
- `NUXT_PUBLIC_MIND_DETECTIVE_EVALUATION=1` — явное включение evaluation UI.

Web surface — физический Search/checklist workflow. Full reconstruction остаётся plugin/agent capability; импорт Case, deterministic commands и checklist proposals выполняются локально generated certified executor.

Service worker кэширует только shell/static assets. Чтобы проверить реальный offline path, сначала загрузите PWA online и дождитесь active service worker, затем отключите сеть: create/search/check/pause-resume/close/export/import deterministic path не должен зависеть от Case API.

## Проверка для разработчика

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
python -m unittest discover -s apps/api/tests -v
python -m scripts.write_local_execution_artifacts
python -m scripts.generate_local_execution_corpus
pnpm install --frozen-lockfile
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

Generated files должны оставаться byte-clean после повторной генерации. Production merge выполняется только после exact-head CI; release — после explicit human authorization и exact post-merge `main` CI через hardened publisher.
