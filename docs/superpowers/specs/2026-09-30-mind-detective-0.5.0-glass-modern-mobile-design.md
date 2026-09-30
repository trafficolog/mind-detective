# MIND Detective 0.5.0 — Glass Modern mobile PWA

Status: approved design slice for implementation (owner instruction 2026-09-30: «реализовать проект в точности повторяющий дизайн приложенного состава и правил»)
Date: 2026-09-30
Base: `main` @ `ccd1dd4` (released Web/PWA `0.4.0`)
Design source: `docs/design/2026-09-30-glass-modern-mobile/` (Claude Design handoff: `HANDOFF.md`, `SPEC.md`, `MEANING.md`, `PLAN.md`, `TEST_CASES.md`, `SCHEMA_MAPPING.md`, `DS_CHANGES.md`, prototype, screenshots 01–23)

## 1. Цель

Заменить продуктовую оболочку Web/PWA на мобильный интерфейс «Glass Modern» из handoff и довести его до работающего продукта, который запускается:

1. **без агента** — полностью офлайн, детерминированные реконструкция и поиск, локальный контрольный список, распознавание речи браузером;
2. **с агентом** — пользователь подключает свой сервер n8n (адрес + токен webhook) и получает research-only предложения ассистента и серверное распознавание речи; при любом сбое — локальный fallback.

Дизайн воспроизводится с high-fidelity: тексты, цвета, типографика, отступы, состояния и поведение — по `prototype/MobileScreen.dc.html` и `screenshots/`.

## 2. Что сохраняется из 0.4.0 (инварианты репозитория)

- Python portable kernel — единственный автор детерминированной семантики Case; Web исполняет сгенерированный `apps/web/app/generated/localExecution.ts` (ADR 009, 013, 015). Прототипный `domain.js` **не** переносится как редьюсер: его правила, которых нет в ядре, добавляются в Python по TDD и попадают в Web через генератор и conformance-корпус.
- Case schema остаётся `mind-detective-case/v2` (Case v3 не вводится). Тип дела кодируется тегом `constraints: ["item_kind:digital"]` (ADR 016).
- Каноническое хранилище — IndexedDB с атомарной записью Case + execution receipt; экспорт/импорт — Case v2 JSON.
- Никаких вероятностей, POD, скрытых весов, cross-case learning.
- Ассистент не мутирует Case: предложение становится данными только через явное действие пользователя и существующий командный путь.
- Evaluation-стенд 0.2.0–0.4.0 (B↔C arms, observer) сохраняется без изменений семантики; его оболочка переезжает на `/lab` (§6).

## 3. Эпистемические инварианты дизайна (I1–I10) → где обеспечиваются

| # | Инвариант | Обеспечение |
|---|---|---|
| I1 | Свободный рассказ хранится дословно | ядро: `record_free_account`, новая `revise_free_account` (append-only, дословно) |
| I2 | Сведение только по явному подтверждению | ядро: `add_statement` (`source: user`, `user_confirmation: true`); UI — шторка «Подтвердить и добавить» |
| I3 | Неизвестное допустимо | ядро: событие `time_precision: unknown` → `timeline.unknown_intervals` (`event:<id>`) |
| I4 | Противоречия показываются, не разрешаются | ядро: ≥2 точных события в одно время с разными названиями → `timeline.contradictions` (`MD_TIME_SAME_EXACT_TIME:<ЧЧ:ММ>`) |
| I5 | Поиск только явным действием | ядро: `record_search_check` и `add_search_target` требуют `current_mode = search` |
| I6 | Проверка = место + способ + результат; повтор — отдельная запись | ядро: `record_search_check` + способы по типу дела; UI помечает повтор |
| I7 | Только конечные счётчики | UI + guard ассистента |
| I8 | Ассистент — только исследование | web `lib/assistant` (контекст, guard, fallback), ADR 017 |
| I9 | Закрытое дело неизменяемо | ядро: терминальные lifecycle отклоняют мутации |
| I10 | Приложение не открывает файлы/галерею/облака | UI (нет file/media API, кроме импорта JSON и микрофона по кнопке), промпт ассистента |

## 4. Расширение ядра (portable kernel, контракт `mind-detective-local-execution/v1`, аддитивно)

K1. **Тип дела.** `create_case_with_kind(case_id, item_label, now, item_kind)`; `item_kind ∈ {physical, digital}`, иначе `MD_CASE_ITEM_KIND_INVALID`. `digital` добавляет `item_kind:digital` в `constraints`. `item_kind_json(case)` — `digital` при наличии тега, иначе `physical` (старые дела — физические).

K2. **Способы проверки.** Физические: `visual`, `hand`, `flashlight`, `opened`, `moved`, `asked` (плюс прежние `reported_check`, `glance`, `visual_systematic`, `empty_and_check`, `tactile` для совместимости). Цифровые: `name_search`, `date_filter`, `browsed`, `trash`, `shared`, `asked`. Способ чужого типа → `MD_SEARCH_METHOD_KIND`.

K3. **Явное место/источник.** Команда `add_search_target {statement_id, target}`: только в режиме поиска, непустая цель, дубликат (casefold, ё→е, пробелы) → `MD_SEARCH_TARGET_EXISTS`. Создаёт `search_suggestion`-сведение пользователя, кандидата и запись журнала.

K4. **Проверки только в поиске.** `record_search_check` вне режима поиска → `MD_SEARCH_MODE_REQUIRED`.

K5. **Правка рассказа.** `revise_free_account {entry_id, text}` — только если рассказ уже есть; добавляет запись `free_account_revision` (дословно). Первичный `record_free_account` допускается в режимах реконструкции и поиска (запись остаётся режима `reconstruction`).

K6. **Время событий.** `time_precision ∈ {exact, approximate, unknown}`; для `unknown` время `null`; для остальных — `ЧЧ:ММ` (00–23:00–59) или ISO-timestamp (совместимость 0.4.0); иначе `MD_RECON_EVENT_TIME_INVALID`. `rebuild_timeline` разрешён в режимах реконструкции и поиска (активное дело, есть рассказ).

K7. **Производные timeline.** `unknown_intervals` дополняется `event:<id>` для событий без времени; `contradictions` — `MD_TIME_SAME_EXACT_TIME:<время>` для групп точных событий с одинаковым временем и разными названиями.

Изменения проходят: Python unit-тесты → регенерация `localExecution.ts` → новые conformance-векторы → Vitest conformance.

## 5. Web-слой (презентация, не семантика)

- `app/lib/mobile/vocab.ts` — словарь `physical`/`digital` из `MEANING.md`, подписи способов/результатов/типов сведений.
- `app/lib/mobile/viewModel.ts` — чистые функции Case v2 → модель экрана: сортировка timeline, статусы узлов и коннекторов, зоны и их состояние по последней проверке, прогресс «N из M», следующая зона (первая непроверенная, без ранжирования), повторные проверки, счётчики, номер дела `#001` (порядок создания), статус-чип.
- `app/lib/mobile/commands.ts` — построение командных конвертов для каждого действия экрана.
- `app/lib/mobile/timeMask.ts` — маска ЧЧ:ММ (`inputmode=numeric`, 4 цифры, двоеточие автоматически).
- `app/lib/assistant/` — минимальный контекст (без рассказа и гипотез), промпт, детерминированный guard, fallback из контрольного списка, `proposalFlow` с таймаутом 10 с, n8n-клиент (`md-propose`, `md-transcribe`), STT.
- `app/lib/mobile/settings.ts` — локальные настройки: онбординг пройден, ассистент вкл/выкл, адрес и токен n8n.

## 6. Маршруты

| Маршрут | Экран |
|---|---|
| `/` | Splash → онбординг (один раз) → главный |
| `/new` | Новое дело (шаг 1/2, шаг 2/2) |
| `/cases` | Дела (вкладка «Дела» нижней навигации) |
| `/cases/:id?tab=reconstruction\|search\|journal` | Дело: реконструкция / поиск / журнал + шторки |
| `/settings` | Настройки |
| `/lab`, `/lab/cases/:id` | прежняя оболочка 0.4.0 и evaluation-стенд |

## 7. Дизайн-система

Компоненты MIND Detective Design System (Glass Modern) реализуются на Vue 1:1 по исходникам `_ds_bundle.js` и `components.css`: `Icon`, `Button`, `IconButton`, `GlassCard`, `StatusChip`, `WorkflowProgress`, `TextArea`, `ChoiceGroup`, `FilterChips`, `AppHeader`, `CaseHeader`, `BottomNav`, `ListRow`, `SectionHeader`, `CaseCard`, `TimelineEvent`, `SearchCheckCard` (с правкой DS_CHANGES §1: цифровые способы и `kind`), `StatePanel`, `BottomSheet`, `EmptyState`, `Notice`. Токены — CSS-переменные из `tokens/*.css`. Иконки Lucide 0.460.0 и шрифт Inter вшиваются в сборку (офлайн PWA). Логотип «Мозаика состояний» и PWA-иконки — из handoff `assets/`.

## 8. Ассистент и голос (ADR 017)

- По умолчанию выключен. Кнопка «Предложить следующий шаг»: выключен → локальный контрольный список (`source: checklist`); включён и n8n задан → `md-propose` → guard → при сбое/таймауте/отказе guard — fallback с пояснением.
- В n8n уходит только `{prompt}` с минимальным контекстом; ключи моделей — в n8n Credentials.
- «Добавить в список проверки» вызывает `add_search_target`; «Ответить» открывает шторку сведения с пустым текстом. Ничего не становится фактом без действия пользователя.
- Голос: n8n задан → MediaRecorder → `md-transcribe`; иначе Web Speech API (ru-RU). Текст дописывается в поле и сохраняется только по кнопке.

## 9. Вне объёма

Аккаунты, облачная синхронизация, фото, карты, English для новой оболочки (словарь только ru), push, фоновая синхронизация, live-модель как обязательная зависимость.

## 10. Приёмка

- Python: все тесты, ruff, mypy; генератор без diff; conformance-корпус без diff.
- Vitest: прежние тесты + перенос T01–T47 (трассировка — в плане).
- Playwright: сценарии M1–M10 на новой оболочке + прежние сценарии на `/lab`.
- Визуальная сверка ключевых экранов со `screenshots/` на колонке 430 px.
