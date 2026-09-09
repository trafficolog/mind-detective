# ADR-001: Canonical Case Controller

**Status:** Accepted for 0.1.0

## Decision
Один `Case` и `CaseController` владеют deterministic state/lifecycle. Skills не хранят параллельное состояние.

## Consequences
Resume, persistence и artifacts имеют одну каноническую основу; helper-модули владеют своими узкими invariants и не дублируются в controller.
