# SCHEMA_MAPPING — прототип (proto/v1) → mind-detective-case/v2

Реализация: `toCaseV2(c)` в `domain.js`, тесты T42–T44. Каноническая схема: `docs/schemas/mind-detective-case-v2.schema.json` в репозитории (additionalProperties: false).

| proto/v1 | Case v2 | Правило |
|---|---|---|
| `id` | `case_id` | как есть |
| `title` | `item_label` | как есть |
| `created`, `updated` (ms) | `created_at`, `updated_at` | ISO 8601 |
| `outcome`, `paused` | `lifecycle` | found → `closed_found`, closed → `closed_unresolved`, paused → `paused`, иначе `active` |
| `mode` | `current_mode` | reconstruction / search |
| `freeAccount` | `interaction_journal[]` | одна запись `author: user, entry_type: free_account`, текст дословно (I1) |
| `statements[]` | `statements[]` | `{id, statement_type, text, event_time, limitation, confirmed_by: "user"}` |
| `events[]` | `timeline.events[]` | `null`, если событий нет |
| `zones[]` | `candidates[]` | `{id, label, source: "user"}` — только введённые пользователем |
| `checks[]` | `search_checks[]` | `checked_at` ISO, method/result — ключи прототипа |
| `outcome` | `outcome` | объект `mind-detective-outcome/v1`; `where` → `user_reported_found_location` |
| `kind` | `constraints: ["item_kind:digital"]` | **временно**, см. ниже |
| — | `next_action` | `null` (предложения не сохраняются в дело) |
| — | `action_feedback` | `[]` |

## Требует решения в репозитории (ADR)
1. **`item_kind`** — схема v2 закрыта для новых полей. Предложение: `mind-detective-case/v2.1` с необязательным `item_kind: "physical" | "digital"`; до принятия — тег в `constraints`.
2. **Способы проверки цифрового дела** (`name-search, date-filter, browsed, trash, shared, asked`) — добавить в перечисление метода SearchCheck.
3. Внутренняя структура `statements[]`, `timeline`, `search_checks[]` в схеме не описана (`type: array/object`) — сверить имена полей с `apps/web/app/lib` при переносе.
