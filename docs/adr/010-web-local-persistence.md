# ADR 010: Browser-local persistence и PWA cache boundary

Status: Accepted for 0.2.0

## Context

Web/PWA должен переживать reload/offline shell use без введения account system или server-side Case database. При этом service worker не должен превращаться в скрытое хранилище пользовательских данных.

## Decision

Canonical Web copy хранится в IndexedDB. Service worker кэширует только application shell/static assets; `/api/`, Case payload, пользовательский текст, model output и evaluation records не входят в runtime/precache data boundary. Background Sync не используется.

После meaningful engagement приложение может запросить `navigator.storage.persist()`, но UI сообщает capability state без обещания backup. Переносимость обеспечивается explicit JSON export/import с validated deterministic migration.

## Consequences

- reload/resume не требует server-side persistence;
- offline mutation не считается сохранённой до успешного canonical API response;
- PWA install/persistent storage не позиционируются как cloud backup;
- будущий cloud sync потребует отдельной архитектурной и privacy review.
