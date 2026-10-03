# Быстрый старт

[English](GETTING_STARTED.en.md)

## Plugin surface

Канонический plugin id — `mind-detective`; текущая release line — `0.5.0`. Пять production skills сохраняются: router, reconstruct, plan, resume и close. Plugin runtime использует Python standard library и не требует сетевых credentials.

Plugin persistence остаётся явным и case-local: сохранение идёт в `.mind-detective/cases/<case-id>/case.json` по explicit persistence action. Web/PWA имеет отдельный browser-local persistence contract и записывает новый Case в IndexedDB сразу.

`0.4.0` с deterministic Web Reconstruction Foundation опубликован. `0.5.0` (мобильная оболочка Glass Modern) опубликован. Любая следующая release publication остаётся отдельным human-authorized publisher gate после exact post-merge `main` CI.

## Мобильная оболочка 0.5.0 (Glass Modern)

Продуктовая оболочка Web/PWA — мобильный интерфейс из `docs/design/2026-09-30-glass-modern-mobile/` (спецификация: `docs/superpowers/specs/2026-09-30-mind-detective-0.5.0-glass-modern-mobile-design.md`). Прежняя оболочка 0.4.0 и evaluation-стенд доступны на `/lab` и `/evaluation`.

### Режим 1 — без агента (полностью локально)

```bash
pnpm install --frozen-lockfile
pnpm --dir apps/web dev --host 0.0.0.0 --port 3000   # разработка, открыть с телефона по IP компьютера
pnpm --dir apps/web build                              # статическая PWA в apps/web/.output/public
```

`.output/public` раздаётся любым статическим хостингом с HTTPS (для установки PWA на телефон и работы микрофона нужен HTTPS или `localhost`). Сервер API и модели не нужны: реконструкция, поиск, журнал, экспорт/импорт работают офлайн после первой загрузки; ассистент даёт шаг из локального контрольного списка, голос распознаёт браузер (Web Speech API).

### Открыть на телефоне (GitHub Pages)

Workflow `.github/workflows/pages.yml` собирает PWA с базовым путём репозитория и публикует её на `https://trafficolog.github.io/mind-detective/` при каждом push в `main` (или вручную: Actions → Deploy Web/PWA to GitHub Pages → Run workflow).

1. Один раз: Settings → Pages → Build and deployment → Source: **GitHub Actions**.
2. Откройте адрес на телефоне → «Поделиться» / меню браузера → «На экран Домой» (iOS) или «Установить приложение» (Android).
3. После первого открытия приложение работает офлайн; дела хранятся только на телефоне. Ассистент с n8n подключается в настройках так же, как локально (адрес n8n должен быть `https`).

Сайт публичный: любой, у кого есть ссылка, может открыть приложение, но не видит чужих дел.

**Смоук-тест опубликованного сайта.** После каждой публикации job `smoke` ждёт, пока CDN начнёт отдавать новую сборку (`scripts/wait_for_pages_build.py`, сверка `_nuxt/builds/latest.json`), и открывает живой адрес в эмуляции Android (Chromium) и iPhone (WebKit): заставка, манифест и service worker под подпутём, затем офлайн — онбординг, новое дело, рассказ и событие сохраняются и открываются заново (в Chromium — в том числе после полной перезагрузки страницы без сети; эмуляция офлайна в WebKit-драйвере Playwright не пропускает такую загрузку до service worker, поэтому для iPhone проверяется переход внутри приложения). Тест пишет только в IndexedDB тестового браузера. Тот же набор в CI для каждого PR гоняется против локальной сборки под `/mind-detective/`. Вручную:

```bash
SMOKE_BASE_URL=https://trafficolog.github.io/mind-detective/ pnpm --dir apps/web exec playwright test -c playwright.smoke.config.ts
```

### Режим 2 — с агентом через n8n

1. Импортируйте `integrations/n8n/mind-detective-assistant.workflow.json` в свой n8n и следуйте `integrations/n8n/README.md` (credentials, CORS, активация).
2. В приложении: **Настройки → Сервер ассистента (n8n)** — адрес (`https://…` или `http://localhost:5678`) и токен webhook; затем **Включить онлайн-ассистента**.
3. «Предложить следующий шаг» идёт в `md-propose`, «Надиктовать» — в `md-transcribe`. Ответ модели проверяется guard в приложении; при сбое, таймауте 10 с или отказе guard используется локальный контрольный список. Предложение становится данными дела только по вашему нажатию.

Ключи моделей хранятся только в n8n Credentials; в браузере — адрес и токен webhook (localStorage этого устройства).

### Режим 3 — evaluation-стенд с LiteLLM

Прежний B↔C стенд (`/lab`, `/evaluation`) по-прежнему использует FastAPI → LiteLLM (раздел «API» ниже, ADR 012).

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

Generated files должны оставаться byte-clean после повторной генерации. Production merge выполняется только после exact-head CI; release publication — после explicit human authorization и exact post-merge `main` CI через hardened publisher.
