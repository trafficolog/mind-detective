# n8n — сервер ассистента и распознавания речи

Выбранный вариант сервера. Приложение знает только **адрес n8n** и **токен webhook**; ключи моделей живут в n8n Credentials.

## Контракт (реализован в `domain.js`: `serverEndpoints`, `serverComplete`, `serverStt`; тесты T45–T47)
| Webhook | Запрос | Ответ 200 | Ошибка |
|---|---|---|---|
| `POST {base}/webhook/md-propose` | JSON `{ "prompt": string }`, `Authorization: Bearer <token>` | `{ "text": "<JSON Proposal от модели>" }` | любой не-2xx → приложение показывает fallback |
| `POST {base}/webhook/md-transcribe` | multipart: `file`, `model`, `language=ru` | `{ "text": "распознанный текст" }` | не-2xx → «Сервис распознавания недоступен» |

Prompt строит приложение (`assistantPrompt`) из минимального контекста — без свободного рассказа и гипотез. Ответ модели всегда проходит `guardProposal` в приложении (единственный источник правил, DRY); n8n — тонкий прокси (KISS).

## Установка
1. n8n → Workflows → Import from file → `mind-detective-assistant.workflow.json`.
2. Credentials: **Header Auth** «MD webhook token» (Name: `Authorization`, Value: `Bearer <ваш токен>`), **OpenAI** — ключ API. Привяжите их к узлам.
3. Webhook → Options → Allowed Origins: замените `*` на домен PWA.
4. Активируйте workflow. В приложении: Настройки → «Сервер ассистента (n8n)» → адрес (например, `https://n8n.example.com`) и токен.
5. Проверка: `curl -X POST https://n8n.example.com/webhook/md-propose -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"prompt":"Верни JSON {\"kind\":\"question\",\"text\":\"Проверка связи\"}"}'`.

## Приватность
- В workflow выключено хранение данных выполнений (`saveDataSuccessExecution: none`, `saveDataErrorExecution: none`).
- Модель и Whisper заменяемы: для локального варианта укажите в узлах URL self-hosted OpenAI-совместимого сервера (например, faster-whisper-server, Ollama) — контракт с приложением не меняется.

## Внимание
JSON собран вручную под n8n 1.x (Webhook v2, HTTP Request v4.2, Respond to Webhook v1.1) и **не проверялся импортом**. После импорта проверьте привязку credentials и поле binary `file` в узле Whisper.

## Дальше (группа агентов)
Схема «05 · n8n, группа агентов» в `Assistant Workflows.dc.html`: добавить Code `route()` + Switch и sub-workflows. Контракт с приложением тот же.
