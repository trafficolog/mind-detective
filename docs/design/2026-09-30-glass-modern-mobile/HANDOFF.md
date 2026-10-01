# Handoff: Mind Detective — мобильное PWA (Glass Modern)

## Overview
Mind Detective — системный поиск потерянного: вещи (`physical`) и фото/файла (`digital`). Пользователь рассказывает, что помнит, подтверждает сведения, видит неизвестное и противоречия, затем явно переходит к проверкам мест/источников и ведёт журнал до итога. Ассистент — только исследование: один следующий шаг, никогда не факт. Данные — локально; сервер ассистента и распознавания речи — n8n.

## About the Design Files
Файлы в `prototype/` — **дизайн-референсы в HTML**: кликабельный прототип, показывающий целевой вид и поведение. Это **не** код для копирования. Задача — **пересоздать экраны в существующем окружении** `trafficolog/mind-detective` → `apps/web` (Nuxt 3, Vue) на его паттернах и на компонентах MIND Detective Design System (Glass Modern).

Исключение — `prototype/domain.js`: это чистое ядро без DOM, покрытое тестами. Его логику переносим 1:1 (в TypeScript), а тесты — в Vitest.

## Fidelity
**High-fidelity.** Цвета, типографика, отступы, тексты и состояния финальные. Эталон для визуальной сверки — `screenshots/` (колонка 430 px, внутренние отступы 16 px; снимки полной высоты, шторки — нижние 844 px).

## Порядок работ (SDD → TDD)
1. Прочитать `docs/SPEC.md` (инварианты I1–I10) и `docs/MEANING.md` (смыслы и словарь).
2. Перенести `domain.js` → `apps/web/app/lib/domain/*.ts`; тесты T01–T47 из `prototype/tests.html` → Vitest (red → green). Эталон: в прототипе 47 passed, 0 failed.
3. Хранилище: Case v2 через `toCaseV2` (`docs/SCHEMA_MAPPING.md`); ADR на `item_kind` и цифровые способы проверки.
4. Экраны (ниже) на компонентах DS; правки DS — `docs/DS_CHANGES.md`.
5. Сервер: импорт `docs/n8n/mind-detective-assistant.workflow.json`, инструкция `docs/n8n/README.md`.
6. E2E Playwright по сценариям M1–M10 (`docs/PLAN.md`) + визуальная сверка со `screenshots/`.

## Screens / Views
Общая оболочка: фон `--bg-ambient`; колонка `max-width: 430px`, центрирована, отступы 20px сверху / 16px по бокам; шрифт Inter; текст `#0B1733`. Внутри дела — плавающий `BottomNav` (Дела · Реконструкция · Поиск · Журнал), `position: sticky; bottom: 0`, отступ снизу 18px.

| # | Экран | Назначение | Состав (компоненты DS) | Скриншот |
|---|---|---|---|---|
| 1 | Splash | первый запуск | «Mind Detective» 56/60 w500, подпись 18/26 `#587196`, `splash-sphere.png`, полоса 6px `linear-gradient(90deg,#4AEEFC,#0B86EA)`, «Готово к работе офлайн», `Button lg block` «Начать» | 01 |
| 2 | Онбординг | правила | лого 48px, H1 36/42 w700 −0.02em, лид 16/24, `GlassCard` padding 8 с 3 строками (плитка иконки 40px, r14, bg `#E3F1FF`), строка приватности 13/18, `Button` «Понятно, начать» | 02 |
| 3 | Главный | старт голосом | `AppHeader` (подпись «Системный поиск потерянного»), надзаголовок 12px caps `#0B86EA`, H1 34/40; микрофон: кольцо 248 (radial rgba(88,174,255,.16→0)), стеклянная подложка 200, кнопка 152 `linear-gradient(160deg,#4AAEFF,#0B86EA 55%,#005CFC)`, тень `0 16px 36px rgba(11,134,234,.38)`, нажатие scale .96, фокус 3px `#58AEFF` offset 4; `Button ghost sm` «Написать вручную»; внизу `GlassCard` padding 8: `ListRow` последнего открытого дела + «Все дела · N дел · M открыто» | 03 |
| 4 | Новое дело | название и старт | «Шаг 1 из 2», `ChoiceGroup` «Что ищем» (Вещь / Фото или файл, 2 колонки), `TextArea` rows 1, «Надиктовать»; «Шаг 2 из 2» — две `GlassCard interactive` (плитка 48, r16): «Восстановить события» (`waypoints`, bg `#E3F1FF`), «Сразу к поиску» (`search`, bg `#DDF3F6`/`#0A6E80`) | 04–06 |
| 5 | Дела | список | кнопки «назад» и «настройки», H1 40/44 + счётчик, `Button` «Новое»; 3 плитки-счётчика (`GlassCard` p14 r18, число 28/32 w700 tabular); `FilterChips` (Все / Активные / Пауза / Завершённые); `CaseCard` (иконка `key-round` / `image`); `EmptyState` | 07–08 |
| 6 | Реконструкция | рассказ → сведения → timeline | `CaseHeader` со степпером; 3 плитки (подтверждено / неизвестно / противоречия, варианты `GlassCard` в цветах состояний); `TextArea` рассказа + «Надиктовать» / «Сохранить»; сведения (`GlassCard confirmed`, `StatusChip`); `TimelineEvent` (connector по статусам); `StatePanel` unknown / contradiction / hypothesis; карточка ассистента; CTA перехода к поиску | 09, 12 |
| 7 | Поиск | проверки | `GlassCard` p20: `WorkflowProgress segments` «N из M мест», следующая проверка (плитка `map-pin`), `Button lg` «Проверить сейчас»; «Места / Источники проверки» — `ListRow`; «Добавить место / источник», «Нашёл», «Завершить без результата»; карточка ассистента | 10, 13, 15 |
| 8 | Журнал | история проверок | H2 28/34 + счётчик; 3 плитки (Всего / Повторные / Неполные); `SearchCheckCard` (physical) или `GlassCard + ListRow` (digital — до правки DS) | 11, 14 |
| 9 | Закрытое дело | итог | `Notice info` «… — найдено» / «Поиск завершён без результата»; действия изменения скрыты | 16 |
| 10 | Шторки | ввод | `BottomSheet fixed`: сведение (4 типа, текст, время по маске ЧЧ:ММ, ограничение), событие (точность: Точное / Примерное / Неизвестное), место / источник, проверка (способы по типу дела, результат, заметка), закрытие (где относительно плана), меню дела, подтверждение удаления | 17–22 |
| 11 | Настройки | приватность, данные, сервер | `Notice privacy` ×2; экспорт / импорт — `ListRow` в `GlassCard`; «Сервер ассистента (n8n)»: адрес + токен (`.md-field` / `.md-textarea`); ассистент research-only + переключатель; удаление всех дел | 23 |

Точные тексты — в `prototype/MobileScreen.dc.html` (шаблон) и в словаре `vocab()` в `domain.js`.

## Interactions & Behavior
- Навигация по шагам: splash → onb → home ↔ new / settings / main (вкладки). Онбординг показывается один раз (`md.proto.onboarded`).
- Кнопка микрофона на главном: открывает «Новое дело» и сразу начинает диктовку названия.
- Переход в поиск — только по явной кнопке (I5). Проверка с результатом «Нашёл» закрывает дело; закрытое дело не меняется (I9).
- Время: маска ЧЧ:ММ, `inputmode="numeric"`, 4 цифры, двоеточие вставляется само; проверка при сохранении (`time_invalid`).
- Ошибки ядра — коды → русские сообщения (`ERR` в логике прототипа), показ через `Notice tone="error" compact`.
- Голос: при подключённом n8n — MediaRecorder → `md-transcribe`; без него — Web Speech API (ru-RU). Текст дописывается в поле и сохраняется только по кнопке. Состояния кнопки: «Надиктовать» / «Остановить» / «Распознаю…».
- Ассистент: `proposalFlow` → n8n `md-propose` (10 с таймаут) → `guardProposal` → при сбое `fallbackProposal`. Подпись источника: «Ассистент · только исследование» / «Контрольный список». Действия: «Добавить в список проверки» / «Ответить» / «Отклонить».
- Анимации: только по токенам DS (140/200/320ms, `cubic-bezier(.2,.8,.2,1)`), нажатие scale .96–.99, без пульсаций.
- Адаптивность: одна колонка до 430px; на планшете допускается разделение timeline | детали (по гайду DS).

## State Management
`cases[]` (localStorage `md.proto.cases.v1` → в продукте IndexedDB, Case v2), `cid`, `step`, `tab`, `sheet`, `form`, `filter`, `err`, `assistantOn`, `server {url, token}`, `listening`, `transcribing`, `prop`, `busy`. Все изменения дела — только через чистые функции `domain.js` (иммутабельно).
QA-хук для визуальных тестов: `window.mdQA.set(patch)` меняет состояние без записи в хранилище (им сняты `screenshots/`).

## Design Tokens
Из `prototype/_ds/.../tokens/*.css` (использовать переменные, не литералы):
- Действие `#0B86EA` (hover `#0875D2`, press `#0674D8`); текст `#0B1733` / `#587196` / `#8095AF`; бренд 50–900 `#EFF8FF … #103F73`.
- Состояния (bg / fg / ink): confirmed `#E8F8F1/#05875B/#04714C`, unknown `#FFF7E6/#B87800/#8A5A00`, contradiction `#FFF0F1/#D93845/#B82533`, hypothesis `#EEF2FF/#4D5EEA/#3E4FD6`, research `#F4ECFF/#7A35D8/#6A28C4`.
- Режимы: reconstruction `#E2F0FF/#075CAF`, search `#DDF4F7/#0A6E80`.
- Стекло: `rgba(255,255,255,.52)` + `blur(22px) saturate(135%)`, рамка `1px rgba(255,255,255,.75)`, тень `--shadow-glass`; действие `--shadow-action`.
- Типографика: Display XL 40/44/700, Title L 28/34/700, Title M 22/28/650, Body L 17/25, Body M 15/22, Body S 13/18, Label 12/16/600, Micro 11/14/500; трекинг display −0.02em.
- Радиусы: 10 / 14 / 18 / 24 / 30 / pill. Отступы: 4 / 8 / 12 / 16 / 20 / 24 / 32 / 40.

## Assets
`prototype/assets/`: `logo-mark.svg/.png`, `logo-mark-white.svg`, `logo-lockup.svg`, `app-icon.svg`, `icon-512.png`, `icon-192.png`, `apple-touch-icon.png` — новый знак «Мозаика состояний»; `logo-mark-legacy.svg` — прежний; `splash-sphere.png` — из DS. Иконки — Lucide (через `Icon` DS).

## Files
- `prototype/MobileScreen.dc.html` — приложение (открывать через статический сервер из папки `prototype/`)
- `prototype/domain.js`, `prototype/tests.html` — ядро и 47 тестов
- `prototype/Assistant Workflows.dc.html` — схемы Mastra / n8n (выбран n8n)
- `prototype/Logo Concepts.dc.html` — варианты логотипа (выбран 3d)
- `docs/` — SPEC, PLAN, TEST_CASES, MEANING, SCHEMA_MAPPING, DS_CHANGES, n8n/
- `screenshots/00-overview.png` + 01–23 — эталон визуальной сверки
