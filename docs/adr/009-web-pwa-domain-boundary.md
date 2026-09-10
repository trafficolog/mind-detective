# ADR 009: Web/PWA не владеет доменной state machine

Status: Accepted for 0.2.0

## Context

0.2.0 добавляет Nuxt Web/PWA поверх уже выпущенного Python core. Параллельный TypeScript reducer быстро создал бы semantic drift между plugin и Web surfaces.

## Decision

`Case` + Python `CaseController` остаются единственным детерминированным источником истины. Nuxt отправляет command envelope и получает полный canonical Case от stateless FastAPI adapter. В `apps/web` запрещены порт `CaseController`, локальный domain reducer и optimistic canonical mutation.

Checklist и AI используют один mutation path. Proposal generation может различаться, но результат всё равно проходит Python proposal/guard boundary.

## Consequences

- domain semantics тестируются один раз в Python core;
- Web retry может повторять byte-equivalent command envelope;
- network failure оставляет IndexedDB canonical Case без optimistic изменения;
- UI может иметь transient presentation state, но не вторую Case state machine.
