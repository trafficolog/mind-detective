# Изменения плагина

[English](CHANGELOG.en.md)

## [0.3.0] — 2026-09-11

Плагин `0.3.0` выделяет restricted portable execution kernel и certified intrinsic semantics, которые остаются Python source of truth и используются генератором Web local executor. Сохранены пять production skills, safety/provenance/search invariants и case-local persistence contract. Web/PWA может выполнять deterministic Case transitions локально только через generated certified artifact; вручную поддерживаемого второго reducer нет.

## [0.2.0] — 2026-09-10

Web/PWA release расширяет продукт отдельным browser/API surface, сохраняя канонический Python Case Controller и прежние safety/provenance/search invariants плагина. Добавлены contract-traceability для Web requirements, PWA/offline сценарии, browser persistence/export-import contracts и provider boundary через stateless API/LiteLLM integration. Пять production skills остаются неизменным plugin surface.

## [0.1.0] — 2026-09-09

Первый production scope: пять skills, Case Controller, provenance-aware statements, timeline, guard, SearchCheck log, categorical planner, safety routing, case-local store и handoff/outcome artifacts.
