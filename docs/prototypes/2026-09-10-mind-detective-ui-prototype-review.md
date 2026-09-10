# MIND Detective 0.2.0 UI Prototype Review

**Status:** reviewed updated UX/state reference; non-normative where it conflicts with the canonical `0.2.0` design spec.

**Canonical spec:** `docs/superpowers/specs/2026-09-10-mind-detective-web-pwa-0.2.0-design.md`

**Reviewed source:** user-supplied updated HTML prototype, 2026-09-10.

## Review conclusion

The updated prototype is materially closer to the approved `0.2.0` architecture and should remain the primary visual/state reference for implementation. It now demonstrates several previously missing invariants directly rather than only through explanatory notes.

It is still a **scenario harness**, not production logic. Five behaviors remain intentionally overridden by the canonical spec and implementation plan.

## What the updated prototype now gets right

### 1. One B/C shell

The updated version uses one active-case structure for checklist and assistant arms:

- one navigation model;
- one mode banner;
- one next-action card;
- one persistent checked/remaining/inaccessible strip;
- one interaction journal slot;
- one chip area;
- one free-text escape hatch;
- one bottom dock (`Журнал`, `Написать`, `Нашёл`);
- the same pending/error area.

This resolves the earlier prototype divergence where checklist and assistant modes had different lower interaction structures.

### 2. Visible command transport state

The prototype now includes a visible command queue with:

- pending state;
- `aria-busy` on the triggering control;
- retryable error state;
- stable visible `command_id`;
- an explicit same-command-id retry path.

This is a good visual model for the production transport queue. The queue remains transport state only and must not become planner evidence.

### 3. Mode provenance and v1 migration presentation

The prototype now shows:

- reconstruction/search tags on individual historical entries;
- non-color-only differentiation through label/icon/treatment;
- a neutral `Режим не выбран` state for a case migrated from v1.

Production data still comes from canonical `case/v2.interaction_journal`; the browser must not infer historical mode from the currently selected screen phase.

### 4. RU/EN shared rendering templates

The updated prototype contains RU and EN copy maps feeding the same component templates. This is aligned with the planned RU/EN key-parity contract.

Production copy resources will be separated from the prototype JavaScript and covered by exact parity/safety selectors.

### 5. Accessibility mechanics

Useful implementation references now include:

- `:focus-visible` treatment;
- 44px target sizing;
- focus trapping in modal sheets;
- Escape close;
- trigger-focus restoration;
- background `inert` handling;
- reduced-motion handling;
- increased-contrast overrides;
- no automatic keyboard focus on active-case load.

### 6. Neutral-check and accessibility concepts are visually separated

The check-quality sheet distinguishes method quality from an orthogonal inaccessible-parts control. The copy correctly describes the initial check as neutral rather than automatically systematic.

The timing of this sheet still needs the production correction described below.

### 7. Explicit research and close states

The prototype now has useful visual references for:

- `action_feedback` / `Не подходит`;
- planner-empty state;
- found-context variants;
- local research-log export;
- persistent-storage denied/request states;
- case export/import affordances;
- retained/deleted close outcome.

## Prototype-only controls

The left-side control rail is developer/test tooling. It must not ship as normal product navigation.

The rail may continue to force:

- light/dark/auto theme;
- translucency;
- RU/EN locale;
- checklist/assistant arm;
- reconstruction/search phase;
- normal/empty/error scenarios;
- direct navigation to scenario screens.

Those controls are useful for visual regression and E2E fixtures but do not define canonical Case behavior.

## Remaining normative corrections

### 1. Production case creation is still too configurable

The updated `Новое дело` screen still exposes:

- `Как работать`: checklist vs assistant;
- `С чего начнём`: reconstruction vs physical search;
- copy saying the engine mode can be changed at any time.

Production `0.2.0` must instead keep the first-case flow to:

1. one item-label field;
2. one primary `Начать поиск` action.

The research arm is deployment/test configuration and is not user-selectable. Initial mode is canonical Case state (`unselected`) and is resolved by the controller-driven flow after case creation rather than through a pre-creation configuration form.

The prototype may retain these controls only in its external scenario rail/test fixtures.

### 2. Demo JavaScript still owns Case-like counters

The updated prototype waits for a simulated successful command before calling `applyCheck()`, which is better than true optimistic mutation. However `applyCheck()` still performs browser-local domain-like mutation:

```text
state.done += 1
state.left = max(0, state.left - 1)
```

Production must not do this. After a successful `/case/command` response it replaces the canonical IndexedDB Case with the validated full Case returned by Python, then derives progress from that Case.

No client-side Case reducer or authoritative `done/left` mutation is allowed.

### 3. Check-quality clarification is still immediate

After every successful simulated check the prototype calls the method-quality sheet immediately.

Production behavior is:

1. one tap records neutral `reported_check`;
2. the user continues without a mandatory method sheet;
3. method quality is requested only later when it becomes decision-relevant to repeating or interpreting that target.

The sheet itself is a valid visual reference; its automatic timing is not.

### 4. Assistant privacy copy still lacks provider-processing disclosure

The storage screen states that cases remain in the browser and are not stored on the application server. That is correct for persistence, but incomplete for assistant mode.

Production copy must separately disclose that the minimum current proposal context is transiently processed by the configured model provider. Local persistence must never be paraphrased as `never leaves this device` when the assistant arm is enabled.

The provider API key/model configuration remains server-side, and application logs exclude raw Case/user/model text by default.

### 5. A guard-blocked raw proposal must not reappear later

The current reconstruction guard copy says, in effect, that the concrete place suggestion is hidden now and will appear when the user moves to search.

That is not the canonical behavior.

When AI output is blocked:

1. the raw rejected proposal is not persisted as a future user-facing suggestion;
2. the journal receives reviewed system copy with the guard reason class;
3. the current request returns a deterministic safe fallback;
4. switching to search may trigger a **new** proposal request under search-mode rules;
5. only that newly generated and freshly validated proposal may be rendered.

A blocked reconstruction proposal therefore cannot be cached and revealed later merely because the mode changed.

## Scenario matrix to preserve in automated tests

The implementation must support at least these reference states:

1. no cases / first case;
2. migrated v1 case with `current_mode=unselected`;
3. active reconstruction + checklist arm;
4. active reconstruction + assistant arm;
5. active search + checklist arm;
6. active search + assistant arm;
7. pending deterministic command;
8. retryable command failure with same-id retry;
9. successful command where canonical Case changes only after response;
10. blocked assistant proposal + deterministic fallback;
11. mode switch after blocked proposal without revealing stale raw proposal;
12. partial/inaccessible prior check;
13. neutral `reported_check` without immediate quality dialog;
14. later repeated target requiring method-quality clarification;
15. empty planner / need-more-information state;
16. next-action rejection with categorical feedback;
17. paused case on case list;
18. found on current suggested action;
19. found elsewhere/unplanned;
20. unresolved close;
21. persistent storage granted / denied / unsupported;
22. valid v1 import migrated to v2;
23. invalid/future schema import rejected;
24. RU/EN parity;
25. light/dark, reduced-motion and increased-contrast behavior.

## Visual details worth carrying into production

Use the prototype as a visual reference for:

- 4px-based spacing rhythm;
- compact system-font typography;
- 44px minimum interactive targets;
- safe-area-aware bottom controls;
- SVG `currentColor` icon system;
- readable glass-opacity floors;
- persistent progress strip;
- compact system events;
- one primary next-action card;
- modal sheet mechanics and focus behavior;
- mobile-first centered desktop presentation.

Do not treat the decorative iPhone frame, external control rail, hard-coded sample item/location data, timers, fake command latency, or local demo counters as product requirements.

## Precedence rule

When the supplied HTML and canonical design disagree, implementation follows:

1. canonical design spec;
2. stable `MD-WEB-REQ-*` requirements and exact contract tests;
3. implementation plan;
4. this prototype review;
5. literal visual/JavaScript behavior of the HTML prototype.
