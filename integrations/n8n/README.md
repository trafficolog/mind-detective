# n8n — сервер ассистента и распознавания речи

Необязательный транспорт research-only ассистента Mind Detective 0.5.0 (ADR 017). Без n8n приложение полностью работоспособно локально.

Выбранный вариант сервера. Приложение знает только **адрес n8n** и **токен webhook**; ключи моделей живут в n8n Credentials.

## Контракт (реализован в `apps/web/app/lib/assistant/server.ts`; тесты `apps/web/tests/unit/assistantServer.spec.ts` T45–T47, E2E `mobile-assistant.spec.ts`)
| Webhook | Запрос | Ответ 200 | Ошибка |
|---|---|---|---|
| `POST {base}/webhook/md-propose` | JSON `{ "prompt": string }`, `Authorization: Bearer <token>` | `{ "text": "<JSON Proposal от модели>" }` | любой не-2xx → приложение показывает fallback |
| `POST {base}/webhook/md-transcribe` | multipart: `file`, `model`, `language=ru` | `{ "text": "распознанный текст" }` | не-2xx → «Сервис распознавания недоступен» |

Prompt строит приложение (`assistantPrompt` в `apps/web/app/lib/assistant/proposals.ts`) из минимального контекста — без свободного рассказа и гипотез. Ответ модели всегда проходит `guardProposal` в приложении (единственный источник правил, DRY); n8n — тонкий прокси (KISS).

## Установка
1. n8n → Workflows → Import from file → `mind-detective-assistant.workflow.json`.
2. Credentials: **Header Auth** «MD webhook token» (Name: `Authorization`, Value: `Bearer <ваш токен>`), **OpenAI** — ключ API. Привяжите их к узлам. В n8n 2.x после изменений workflow нужно опубликовать (Publish).
3. Webhook → Options → Allowed Origins: замените `*` на домен PWA.
4. Активируйте workflow. В приложении: Настройки → «Сервер ассистента (n8n)» → адрес (например, `https://n8n.example.com`) и токен.
5. Проверка: `curl -X POST https://n8n.example.com/webhook/md-propose -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"prompt":"Верни JSON {\"kind\":\"question\",\"text\":\"Проверка связи\"}"}'`.

## Приватность
- В workflow выключено хранение данных выполнений (`saveDataSuccessExecution: none`, `saveDataErrorExecution: none`).
- Модель и Whisper заменяемы: для локального варианта укажите в узлах URL self-hosted OpenAI-совместимого сервера (например, faster-whisper-server, Ollama) — контракт с приложением не меняется.

## Проверено

2026-10-01: workflow импортирован в **n8n 2.41.4** (`n8n import:workflow` → `publish:workflow`), модель и Whisper подменены локальным OpenAI-совместимым моком. Проверены:

- `md-propose` → `{ "text": … }` (200), неверный/отсутствующий токен → 403, сбой модели → 502 `llm_unavailable`;
- `md-transcribe` (multipart, поле `file`) → `{ "text": … }` (200), сбой Whisper → 502 `stt_unavailable`;
- CORS preflight с `Authorization` → 204 и `Access-Control-Allow-Origin`;
- сквозной сценарий из браузера: `apps/web/tests/e2e/mobile-n8n-live.spec.ts` (ответ проходит guard; запись микрофона распознаётся и дописывается в поле).

Особенность Webhook v2: файл из multipart-поля `file` попадает в binary-свойство `file0` (опция `binaryPropertyName: file` + индекс), поэтому узел Whisper читает `file0`. Узлы под 1.x-совместимые версии (Webhook v2, HTTP Request v4.2, Respond to Webhook v1.1); на n8n 1.x импорт не проверялся.

Проверить свой сервер: `./smoke-test.sh https://n8n.example.com <токен> [audio.webm]`; из браузера — `MD_E2E_N8N_URL=… MD_E2E_N8N_TOKEN=… pnpm --dir apps/web exec playwright test mobile-n8n-live --project=chromium`.

## Дальше (группа агентов)
Схема «05 · n8n, группа агентов» в `docs/design/2026-09-30-glass-modern-mobile/prototype/Assistant Workflows.dc.html`: добавить Code `route()` + Switch и sub-workflows. Контракт с приложением тот же.

## Локальный запуск n8n для проверки

```bash
docker run -it --rm -p 5678:5678 -e N8N_DEFAULT_BINARY_DATA_MODE=filesystem n8nio/n8n
```

В приложении укажите `http://localhost:5678` (разрешено только для localhost; для телефона нужен HTTPS-адрес, например через обратный прокси). В узле Webhook → Options → Allowed Origins укажите origin приложения (например, `http://localhost:3000`).
