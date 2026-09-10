# SDD / TDD Workflow

Канонический цикл:

`SPEC → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY`

1. **SPEC** — изменение соответствует утверждённому design/implementation plan; расширение P0 scope требует нового design slice.
2. **RED** — один минимальный failing test фиксирует требуемое поведение; нужно увидеть правильную причину падения.
3. **GREEN** — минимальная реализация, проходящая test.
4. **REFACTOR** — устранение дублирования/упрощение без изменения контракта.
5. **TRACE** — high-risk requirement получает точный `MD-REQ-*` → skill → helper → exact selector → reference.
6. **EVAL** — semantic/adversarial expectations добавляются отдельно от deterministic tests.
7. **VERIFY** — полный test/ruff/mypy/boundary/freshness/release suite и exact Git SHA evidence.

Green fixture validation не доказывает live-model compliance, scientific validity или эффективность продукта. Эти уровни evidence должны называться отдельно.
