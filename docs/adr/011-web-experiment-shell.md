# ADR 011: Checklist и AI используют один production shell

Status: Accepted for 0.2.0

## Context

Product evaluation сравнивает structured checklist с checklist + conversational AI. Если arms отличаются навигацией, storage, progress UX или визуальной оболочкой, measured effect смешивается с UI differences.

## Decision

Arms B/C используют один `CaseShell`, один journal, progress strip, next-action card, input dock, persistence UX и command path. Experimental arm identity не раскрывается отдельным production label. Отличие AI arm ограничено proposal generation через server-side model boundary.

Mode provenance хранится в canonical interaction journal и визуально кодируется не только цветом, но также текстовой меткой/icon/treatment.

## Consequences

- experiment сравнивает proposal assistance, а не два разных продукта;
- shell equivalence имеет browser regression test;
- новые arm-specific UI forks требуют отдельного решения и evaluation review.
