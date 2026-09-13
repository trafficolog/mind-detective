# Изменения плагина

[English](CHANGELOG.en.md)

## [0.4.0] — 2026-09-13

Плагин `0.4.0` расширяет canonical portable semantics для Web Reconstruction: добавлены `record_free_account` и `rebuild_timeline`, free-account-first gate, user-only provenance для structured evidence и uncertainty-preserving timeline с unknowns/contradictions. Эти semantics остаются Python source of truth и сертифицированно генерируются в Web local executor. Пять production skills, `mind-detective-case/v2`, safety/provenance/search invariants и запрет calibrated location probabilities остаются неизменными.

## [0.3.1] — 2026-09-12

Patch-hardening после внешнего review: safety routing применяется на interaction ingress, plugin reconstruction mutations проходят через явную reducer boundary, production helper reachability проверяется механически, semantic scenario corpus честно обозначен как manual review, а plugin/API portability больше не зависит от фиксированной глубины монорепо. Сохранены пять production skills, `mind-detective-case/v2`, provenance/search invariants и отсутствие calibrated location probabilities.

## [0.3.0] — 2026-09-11

Плагин `0.3.0` выделяет restricted portable execution kernel и certified intrinsic semantics, которые остаются Python source of truth и используются генератором Web local executor. Сохранены пять production skills, safety/provenance/search invariants и case-local persistence contract. Web/PWA может выполнять deterministic Case transitions локально только через generated certified artifact; вручную поддерживаемого второго reducer нет.

## [0.2.0] — 2026-09-10

Web/PWA release расширяет продукт отдельным browser/API surface, сохраняя канонический Python Case Controller и прежние safety/provenance/search invariants плагина. Добавлены contract-traceability для Web requirements, PWA/offline сценарии, browser persistence/export-import contracts и provider boundary через stateless API/LiteLLM integration. Пять production skills остаются неизменным plugin surface.

## [0.1.0] — 2026-09-09

Первый production scope: пять skills, Case Controller, provenance-aware statements, timeline, guard, SearchCheck log, categorical planner, safety routing, case-local store и handoff/outcome artifacts.
