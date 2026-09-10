# Product Evaluation

Цель оценки — проверить, даёт ли диалоговый AI практическую добавочную ценность поверх хорошо сделанного search controller, а не доказать заранее выбранную гипотезу.

## Сравниваемые arms

- **A — обычный поиск** без специального инструмента.
- **B — структурированный чек-лист** + журнал поиска без диалогового AI.
- **C — чек-лист + журнал поиска + диалоговый AI** MIND Detective.

В 0.2.0 B и C используют один Web/PWA shell, одну canonical Case model и один mutation path через Python `CaseController`. Arm identity не показывается как отдельный production UX. Отличие C ограничено proposal generation через server-side LiteLLM/model-provider boundary.

Сначала используются безопасные staged tasks; добровольные реальные кейсы анализируются отдельно.

## Метрики

- `time_to_next_useful_action`;
- `duplicate_check_count`;
- perceived task load / convenience;
- `found_rate`, при этом **unresolved** и **abandoned** выводятся отдельно, а не исключаются из выборки;
- `unsupported_fact_rate`;
- `leading_suggestion_rate` в reconstruction;
- `false_confidence_rate`;
- resume/handoff completeness.

Нельзя считать только успешные found cases: незавершённые/censored outcomes должны оставаться видимыми.

## Web evaluation privacy

Web evaluation log является browser-local и использует explicit allowlist. Он может фиксировать interaction/outcome codes, case id, arm/mode и категориальные причины, но не должен сохранять `item_label`, конкретные location targets, journal/user text или raw model output. Background telemetry upload в 0.2.0 отсутствует. Экспорт evaluation data выполняется только явным действием пользователя.

## Falsifiable decision rule

Если C не даёт практически значимого улучшения относительно B при сопоставимом safety profile, продукт следует упростить до checklist/controller. Это считается валидным product evidence, а не неудачей исследования.

Green deterministic/browser fixtures подтверждают реализацию конкретных control paths, но не являются доказательством causal product lift или научной валидности методологии.
