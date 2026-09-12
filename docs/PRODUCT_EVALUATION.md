# Product Evaluation

Цель — проверить, даёт ли диалоговый AI практическую добавочную ценность поверх deterministic search controller, а не доказать заранее выбранную гипотезу.

## Arms

- **A — обычный поиск:** внешний contextual baseline без MIND Detective UI/скрытой structured assistance.
- **B — структурированный чек-лист** + журнал поиска без диалогового AI: Web/PWA, canonical Case и deterministic local executor.
- **C — чек-лист + журнал поиска + диалоговый AI:** тот же product shell и execution semantics; отличие ограничено live assistant proposal generation. Transport fallback не меняет assignment: session остаётся C.

Обычное использование продукта не рандомизируется. B/C assignment существует только в explicit evaluation mode и хранится отдельно от `Case v2`.

## Canonical protocol documents

- [Approved design](superpowers/specs/2026-09-11-mind-detective-product-evaluation-design.md)
- [Staged protocol](evaluation/STAGED_PROTOCOL.md)
- [Real-pilot protocol](evaluation/REAL_PILOT_PROTOCOL.md)
- [External arm A protocol](evaluation/EXTERNAL_A_PROTOCOL.md)
- [Analysis runbook](evaluation/ANALYSIS.md)
- [Plugin semantic scenario review](evaluation/SEMANTIC_SCENARIO_REVIEW.md)

Analysis CLI:

```bash
python -m scripts.analyze_evaluation export.json --seed 1729 --bootstrap 2000 --json-out summary.json
```

## Primary decision

Staged B↔C is primary. `time_to_next_useful_action` is reconstructed retrospectively from `case_started` → first shown proposal that later reaches matching `check_finished` without prior rejection. Sessions without an observed useful action are right-censored at terminal time or 10 minutes. Primary summary is 10-minute RMTUA with participant-clustered uncertainty.

Secondary evidence includes duplicate checks, fixed 1–5 task-load/convenience ratings, found/unresolved/abandoned distribution, proposal safety, handoff continuity, fallback, and technical failures. All assigned/started sessions remain visible in ITT; abandonment, fallback, incomplete participation, and missing ratings are not silently removed.

A product-direction claim requires at least 32 protocol-complete staged participants and at least 8 per counterbalance cell. Arm A remains contextual and does not alter the C-vs-B product decision.

## Decision event contract

Current `mind-detective-evaluation/v1` instrumentation contains only events that have product semantics and a production path into the analyzer. The primary endpoint uses `case_started`, `next_action_shown`, `next_action_rejected`, `check_finished` and terminal `found` / `case_closed_unresolved` / `case_abandoned`. Secondary decision signals use `duplicate_check_detected`, `post_case_rating`, `proposal_safety_annotation`, `handoff_rubric`, `assistant_offline_fallback` and `local_execution_failed`.

`next_action_started` is intentionally absent: the product has no separate “start checking” interaction, and adding one only for instrumentation would distort the UX and primary endpoint. The former `pending_command_*` vocabulary belonged to the retired network-command-queue model; local deterministic execution reports a real persistence/execution failure through `local_execution_failed` instead. `found_context` is metadata on the atomic terminal `found` event and is not duplicated as a separate `found_context_recorded` event.

The offline analyzer may continue to accept older exported event names for backward-compatible reading of historical fixtures/exports. Such compatibility does not make those names part of the current Web emission contract. `tests/test_evaluation_event_paths.py` executablely checks the current metric → production emitter → analyzer path and rejects reintroduction of obsolete current event names.

## Plugin semantic scenarios are a separate control

`plugins/mind-detective/evals/scenarios.json` specifies semantic expectations for plugin/agent responses. Repository CI currently validates that corpus **structurally only**; it does not execute prompts against a model and does not provide an automated semantic PASS. Semantic execution is manual under `evaluation/SEMANTIC_SCENARIO_REVIEW.md` until a separately reviewed runner exists.

This control is distinct from the staged B↔C product experiment above. A manual semantic review result cannot substitute for participant evidence, and green B↔C analysis machinery cannot be used to claim that the plugin semantic corpus was executed successfully.

## Privacy

Evaluation storage/export is local-only by default, explicit-export only, and allowlist-based. It rejects Case payload/content, item/location text, journal/statement/user text, evaluator free text, and raw model output. Normal Case export and evaluation export remain separate.

## Falsifiable rule

Если C не даёт practically meaningful lift относительно B при сопоставимом safety/readiness profile, default core следует упростить до deterministic checklist/controller. Если результат inconclusive, следующий номер версии сам по себе не является основанием объявлять победителя.

Green deterministic/browser/analysis fixtures подтверждают machinery, conformance и reproducibility, но не являются доказательством causal product lift или научной валидности исследования.
