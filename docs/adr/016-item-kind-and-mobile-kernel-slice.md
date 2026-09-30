# ADR 016 — Тип дела, цифровые способы проверки и мобильный срез ядра

Status: Accepted for `0.5.0` (Glass Modern mobile).

## Context

Дизайн Glass Modern (`docs/design/2026-09-30-glass-modern-mobile/`) добавляет второй тип потерянного — фото, видео, файл (`digital`) — с источниками вместо мест и собственными способами проверки, явное добавление мест/источников, правку свободного рассказа, время событий в формате ЧЧ:ММ и вывод неизвестного/противоречий из событий. Прототип реализует это в `domain.js`, но ADR 009/013/015 запрещают второй редьюсер в Web.

Схема `mind-detective-case/v2` закрыта (`additionalProperties: false`), поле `item_kind` в неё добавить нельзя без Case v3.

## Decision

1. Все новые правила Case реализуются в Python portable kernel и попадают в Web только через генератор `localExecution.ts` и conformance-корпус. Контракт `mind-detective-local-execution/v1` расширяется аддитивно: прежние команды и дела остаются валидными.
2. Тип дела кодируется тегом `constraints: ["item_kind:digital"]`; отсутствие тега = `physical`. Отдельное поле `item_kind` откладывается до Case v2.1/v3 с отдельным ревью схемы.
3. Способы проверки: физические `visual, hand, flashlight, opened, moved, asked` (+ прежние ключи), цифровые `name_search, date_filter, browsed, trash, shared, asked`. Способ чужого типа отклоняется `MD_SEARCH_METHOD_KIND`.
4. Новые команды: `add_search_target` (явное место/источник, дубликат → `MD_SEARCH_TARGET_EXISTS`) и `revise_free_account` (append-only ревизия рассказа, дословно).
5. `record_search_check` и `add_search_target` требуют режима поиска (`MD_SEARCH_MODE_REQUIRED`); `rebuild_timeline` и первичный рассказ разрешены и в режиме поиска.
6. Время события: `ЧЧ:ММ` или ISO-timestamp; события без времени дают `unknown_intervals: event:<id>`; одинаковое точное время с разными названиями даёт `contradictions: MD_TIME_SAME_EXACT_TIME:<время>`.

## Consequences

- одна авторская семантика; Web получает правила через генерацию;
- старые дела без тега — физические, импорт 0.4.0 не меняется;
- цифровое дело никогда не даёт приложению доступа к файлам: в Case хранятся только названия источников и результаты;
- замена тега на поле схемы потребует миграции и отдельного решения.
