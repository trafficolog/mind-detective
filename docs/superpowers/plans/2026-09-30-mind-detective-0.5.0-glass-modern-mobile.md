# MIND Detective 0.5.0 — план реализации Glass Modern mobile (SDD → TDD)

Design: `docs/superpowers/specs/2026-09-30-mind-detective-0.5.0-glass-modern-mobile-design.md`
Branch: `feature/0.5.0-glass-modern-mobile`
Цикл на каждую задачу: `SPEC → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY` (`docs/SDD_TDD_WORKFLOW.md`).

## Задачи

| # | Задача | RED (тесты сначала) | GREEN | Статус |
|---|---|---|---|---|
| 1 | Спецификация, план, ADR 016/017, импорт handoff в `docs/design/2026-09-30-glass-modern-mobile/` | — | документы | готово |
| 2 | Ядро K1–K7 | `plugins/mind-detective/tests/test_portable_mobile_slice.py` | `portable_kernel.py`, `portable_contract.py` | готово |
| 3 | Генерация и conformance | `apps/web/tests/unit/localExecutionConformance.spec.ts` (новые векторы) | `scripts.write_local_execution_artifacts`, `scripts.generate_local_execution_corpus` | готово |
| 4 | Web-lib: словарь, view-model, команды, маска времени, настройки | `apps/web/tests/unit/mobile*.spec.ts` | `apps/web/app/lib/mobile/*` | готово |
| 5 | Ассистент, guard, fallback, n8n, STT | `apps/web/tests/unit/assistant*.spec.ts` | `apps/web/app/lib/assistant/*` | готово |
| 6 | Компоненты DS на Vue, токены, иконки, Inter, ассеты | `apps/web/tests/unit/designSystem.spec.ts` (контракты токенов/иконок) | `apps/web/app/components/ds/*`, `assets/css/glass/*` | готово |
| 7 | Экраны 1–11 и шторки, legacy → `/lab` | Playwright M1–M10 (`apps/web/tests/e2e/mobile-*.spec.ts`) | `apps/web/app/pages/*`, `components/mobile/*` | готово |
| 8 | n8n: workflow, инструкция, документация запуска | — | `integrations/n8n/`, `docs/GETTING_STARTED*.md` | готово |
| 9 | VERIFY: полный набор, сборка PWA, визуальная сверка | все | — | готово |
| 10 | Публикация на GitHub Pages под подпутём | `tests/test_pages_build_check.py` | `.github/workflows/pages.yml`, `scripts/check_pages_build.py`, `NUXT_APP_BASE_URL` | готово |
| 11 | Анимированная заставка из частиц (запрос владельца продукта, отступление от DS в `VISUAL_REVIEW.md`); адаптивная плотность для медленных устройств | `apps/web/tests/unit/splashParticles.spec.ts`, `apps/web/tests/e2e/mobile-splash.spec.ts` | `components/mobile/SplashParticles.vue`, `lib/mobile/splashParticles.ts` | готово |
| 12 | Смоук опубликованного сайта после деплоя (Android Chromium, iPhone WebKit; онлайн и офлайн) и тот же набор в CI для PR против сборки под подпутём | `tests/test_wait_for_pages_build.py`; проверено на живом сайте (pass), сборке с неверной базой (fail), верной сборке (pass) | `apps/web/tests/smoke/`, `playwright.smoke.config.ts`, `scripts/wait_for_pages_build.py`, job `smoke` | готово |

## Трассировка тестов прототипа T01–T47

Прототипные тесты перенесены по уровню ответственности: семантика Case — в Python-ядро (и далее в conformance), презентация и ассистент — в Vitest.

| ID | Проверка | Где теперь |
|---|---|---|
| T01 | пустое название → ошибка | ядро `create_case` (`MD_WEB_COMMAND_PAYLOAD`), `test_portable_mobile_slice::test_t01_blank_title_rejected` |
| T02 | номер дела растёт | `mobileViewModel.spec.ts::T02 case numbers follow creation order` |
| T03 | рассказ дословно | `test_portable_mobile_slice::test_t03_free_account_and_revision_are_verbatim` |
| T04 | сведение требует текст и тип | `test_portable_mobile_slice::test_t04_statement_requires_text_and_type` |
| T05 | неизвестное время допустимо | `test_portable_mobile_slice::test_t05_unknown_time_event_is_unknown_interval` |
| T06 | неверное время отклоняется | `test_portable_mobile_slice::test_t06_invalid_clock_time_rejected`, `mobileTimeMask.spec.ts` |
| T07 | сортировка timeline, неизвестные в конце | `mobileViewModel.spec.ts::T07` |
| T08 | противоречие одного точного времени | `test_portable_mobile_slice::test_t08_same_exact_time_different_labels_is_contradiction`, `mobileViewModel.spec.ts::T08` |
| T09 | примерное время без противоречий | `test_portable_mobile_slice::test_t09_approximate_times_do_not_contradict` |
| T10 | проверка до перехода в поиск | `test_portable_mobile_slice::test_t10_check_requires_search_mode` |
| T11 | проверка хранит способ | `test_portable_mobile_slice::test_t11_check_keeps_method_and_marks_target` |
| T12 | повтор помечается | `mobileViewModel.spec.ts::T12` |
| T13 | неполная не в прогрессе | `mobileViewModel.spec.ts::T13` |
| T14 | следующая — первая непроверенная | `mobileViewModel.spec.ts::T14` |
| T15 | «Нашёл» закрывает дело | `mobileCommands.spec.ts::T15 found check is followed by close_found` + E2E M6 |
| T16 | закрытое неизменяемо | `test_portable_mobile_slice::test_t16_closed_case_is_immutable` |
| T17 | дубликат места | `test_portable_mobile_slice::test_t17_duplicate_target_rejected` |
| T18 | пауза | `test_portable_mobile_slice::test_t18_pause_and_resume` + `mobileViewModel.spec.ts::T18` |
| T19 | экспорт → импорт | `exportImport.spec.ts` (существующий) + `mobileViewModel.spec.ts::T19 digital kind survives export/import` |
| T20 | битый JSON/чужая схема | `exportImport.spec.ts` (существующий) |
| T21 | неизменяемость входа | `localExecutor.spec.ts` (существующий) + `mobileViewModel.spec.ts::T21` |
| T22 | контекст без рассказа и гипотез | `assistant.spec.ts::T22` |
| T23–T25 | guard | `assistant.spec.ts::T23..T25` |
| T26–T27 | fallback | `assistant.spec.ts::T26..T27` |
| T28–T31 | proposalFlow | `assistant.spec.ts::T28..T31` |
| T32–T35 | STT | `assistantServer.spec.ts::T32..T35` |
| T36 | тип дела | `test_portable_mobile_slice::test_t36_item_kind_default_and_invalid` |
| T37 | способы по типу | `test_portable_mobile_slice::test_t37_methods_depend_on_item_kind` |
| T38 | словарь место/источник | `mobileVocab.spec.ts::T38` |
| T39 | старое дело без kind → physical | `test_portable_mobile_slice::test_t39_legacy_case_is_physical` |
| T40 | цифровое: промпт и fallback без доступа к файлам | `assistant.spec.ts::T40` |
| T41 | демо цифрового дела | E2E M9 (демо-данные не поставляются в продукт) |
| T42–T44 | `toCaseV2` | неприменимо: Case v2 — каноническое хранилище; покрыто схемой и `test_t36`, `test_t03` |
| T45–T47 | n8n | `assistantServer.spec.ts::T45..T47` |

## Ручные / E2E сценарии M1–M10

`apps/web/tests/e2e/mobile-flow.spec.ts`, `mobile-digital.spec.ts`, `mobile-assistant.spec.ts`, `mobile-storage.spec.ts`: M1 splash → онбординг → главный; M2 создание → реконструкция; M3 рассказ, сведение, 3 события → неизвестное и противоречие; M4 явный переход в поиск, места; M5 проверка → журнал, повтор; M6 «Нашёл» → закрыто, неизменяемо; M7 экспорт → удаление → импорт; M8 ассистент без сервера → контрольный список; M9 цифровое дело; M10 n8n (мок) → предложение ассистента, недоступен → fallback.

## Известные ограничения проверок

- Эмуляция офлайна в WebKit-драйвере Playwright обрывает загрузку страницы до service worker, поэтому полная перезагрузка без сети проверяется только в Chromium; на iPhone офлайн проверяется переходами внутри приложения.
- Адаптивная плотность заставки реагирует на частоту кадров, поэтому режим энергосбережения (кадры ограничены ~30 в секунду) тоже снижает плотность до 1x; это сознательно: в этом режиме экономия важнее резкости декоративной картинки.
