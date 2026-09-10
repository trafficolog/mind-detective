# Архитектура

[English](ARCHITECTURE.en.md)

## Центр системы

Канонический `Case` и `CaseController` — единственный детерминированный центр состояния. Skills оркестрируют диалог и вызывают helper-модули, но не создают параллельные источники истины.

```text
skills
  │
  ▼
safety ──► limitation / escalation
  │ ordinary physical search
  ▼
CaseController
  ├─ statements.py   provenance/type invariants
  ├─ timeline.py     unknowns + contradictions
  ├─ search_log.py   durable physical checks
  ├─ planner.py      one categorical next action
  ├─ guard.py        mode-aware candidate utterance checks
  ├─ store.py        explicit case-local persistence
  └─ artifacts.py    derived handoff/outcome
```

## Границы P0

`plugins/mind-detective/scripts/` остаётся transport-free и Python-standard-library-only. В 0.1.0 отсутствуют connector runtime, ModelAdapter, Web/PWA, voice/messenger surface, cloud storage, cross-case learning, Bayesian/POD/numerical location model и скрытый `belief_weight`.

## Источники истины

- Case — runtime/source-of-truth для пользовательского кейса.
- `docs/REQUIREMENTS.md` — нормативные требования.
- `docs/CONTRACT_MATRIX.json` — traceability.
- eval fixtures — machine-checkable expectations, но не доказательство live-model semantic compliance.
- release manifest — единственный declarative intent публикации после Task 15.

См. ADR в `docs/adr/`.
