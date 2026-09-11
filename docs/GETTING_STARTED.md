# Быстрый старт

[English](GETTING_STARTED.en.md)

## Plugin surface

Канонический plugin id — `mind-detective`, версия `0.3.0`. Пять production skills сохраняются: router, reconstruct, plan, resume и close. Сам plugin runtime использует Python standard library и не требует сетевых credentials.

Для явного plugin persistence кейс записывается только по действию пользователя (`save`/`pause`/`retain`) в `.mind-detective/cases/<case-id>/case.json`.

## Web/PWA 0.3.0

Web surface использует Nuxt 4 и browser-local IndexedDB. Deterministic Case create/commands/checklist proposals выполняются локально generated certified executor; server API для них не обязателен. AI proposal при online assistant arm проходит через FastAPI → LiteLLM/provider boundary и execution-identity check.

Service worker кэширует только shell/static assets. Чтобы проверить реальный offline path, сначала загрузите PWA online и дождитесь active service worker, затем отключите сеть: создание/поиск/проверка/pause-resume/close/export должны оставаться локальными.

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

Generated files должны оставаться byte-clean после повторной генерации. Production merge выполняется только после exact-head CI; release — после exact post-merge `main` CI через hardened publisher.
