# Product Evaluation

Цель оценки — проверить, даёт ли диалоговый AI практическую добавочную ценность поверх хорошо сделанного deterministic search controller, а не доказать заранее выбранную гипотезу.

## Сравниваемые arms

- **A — обычный поиск** без специального инструмента.
- **B — структурированный чек-лист** + журнал поиска без диалогового AI.
- **C — чек-лист + журнал поиска + диалоговый AI** MIND Detective.

В `0.3.0` B и C используют один Web/PWA shell, одну canonical Case model и один certified local deterministic execution path. Этот path — generated TypeScript artifact из authoritative portable Python semantics; отдельного вручную поддерживаемого reducer для arm нет. Отличие C ограничено live assistant proposal generation через execution-identity-guarded FastAPI → LiteLLM/provider boundary. При transport failure C временно использует тот же deterministic local proposal, без reconnect replay.

Сначала используются безопасные staged tasks; добровольные реальные кейсы анализируются отдельно.

## Метрики

- `time_to_next_useful_action`;
- `duplicate_check_count`;
- perceived task load / convenience;
- `found_rate`, при этом **unresolved** и **abandoned** выводятся отдельно и не исключаются из выборки;
- `unsupported_fact_rate`;
- `leading_suggestion_rate` в reconstruction;
- `false_confidence_rate`;
- resume/handoff completeness.

Нельзя считать только успешные found cases: незавершённые/censored outcomes должны оставаться видимыми.

## Evaluation privacy

Browser evaluation log является local-only и использует explicit allowlist. Он может фиксировать interaction/outcome codes, case id, arm/mode и categorical reasons, но не сохраняет `item_label`, конкретные location targets, journal/user text или raw model output. Background telemetry upload отсутствует; export выполняется только явным действием пользователя.

## Falsifiable decision rule

Если C не даёт практически значимого улучшения относительно B при сопоставимом safety profile, продукт следует упростить до checklist/controller. Это валидный product evidence, а не неудача исследования.

Green deterministic/browser fixtures подтверждают конкретные control paths и conformance covered portable semantics, но не являются доказательством causal product lift или научной валидности методологии.
