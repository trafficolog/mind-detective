# MIND Detective 0.2.0 UI Prototype Review

**Status:** approved UX reference for implementation planning; non-normative where it conflicts with the canonical `0.2.0` design spec.

**Canonical spec:** `docs/superpowers/specs/2026-09-10-mind-detective-web-pwa-0.2.0-design.md`

## What the prototype contributes

The supplied HTML prototype is the primary visual/state reference for the `0.2.0` mobile-first shell. It demonstrates:

- Cases / local resume list;
- New case creation;
- Active case shell;
- Reconstruction and search visual states;
- checklist and assistant scenario switching;
- pending action affordance;
- checked / remaining / timeline detail views;
- guard/system note presentation;
- check-quality clarification;
- found / close flow;
- local-storage warning, export and install education;
- light/dark appearance and reduced-motion / contrast behavior;
- a developer-facing control rail for viewing scenario states.

The visual direction (platform-native mobile density, glass surfaces, 44px targets, safe-area handling, SVG icon system, readable contrast floors) is a useful implementation reference, but product semantics remain governed by the canonical spec and requirements.

## Prototype-only controls

The left-side control rail is a **developer scenario harness**, not a production navigation surface. It may be preserved as a docs/test reference or reproduced in test tooling, but it must not ship as the normal end-user experience.

In particular:

- engine arm (`checklist` / `assistant`) is assigned by test/experiment configuration, not chosen on the first-case screen;
- phase controls may force reconstruction/search states in fixtures, but production mode comes from canonical Case state;
- theme/translucency controls are visual test aids and do not create domain state.

## Normative corrections before production implementation

### 1. One shell means one interaction structure

The prototype currently hides the interaction stream in checklist mode and swaps an assistant composer for a checklist action dock. Production `0.2.0` must not do this.

Both B and C arms use the same:

- journal slot;
- quick actions/chips;
- free-text escape-hatch placement;
- next-action card;
- checked/remaining summary;
- pending/error affordances.

The experimental difference is only the server-side mechanism that produces the next structured proposal.

### 2. Case creation remains one field + one primary button

The prototype's `Как работать` engine choice is useful in the scenario harness, but it must not appear before production case creation. Research arm/configuration is external to that user flow.

### 3. No optimistic domain mutation

The prototype's demo JavaScript increments `done/left` locally after a timeout. Production must instead:

1. create a transport-only pending command;
2. render `aria-busy` / pending state;
3. send the command to the Python API;
4. replace the canonical local Case only after a validated server response;
5. derive progress counters from that returned Case.

No client-side Case reducer is allowed in `0.2.0`.

### 4. One-tap check is neutral

The prototype may open a thoroughness sheet immediately for demonstration. Production behavior follows the spec: `Проверил` records neutral `reported_check`; clarification appears only when check quality later changes the usefulness of repeating that target.

### 5. Journal mode provenance is canonical

Mode tags shown in prototype messages are retained, but production entries come from `case/v2.interaction_journal`. Historical labels survive reload and cannot be reconstructed from current screen mode.

### 6. Local persistence is not the same as no external processing

The prototype correctly emphasizes that the server does not persist the Case. Production assistant mode must additionally disclose that the minimum current proposal context is transiently processed by the configured model provider. "Stored locally" must not be presented as "never leaves this device" when the assistant arm is enabled.

## Scenario matrix to preserve in automated tests

At minimum the Web implementation must be testable in these states:

1. no cases / create first case;
2. active case in reconstruction, checklist arm;
3. active case in reconstruction, assistant arm;
4. active case in search, checklist arm;
5. active case in search, assistant arm;
6. pending deterministic command;
7. retryable network failure;
8. blocked AI proposal with deterministic fallback;
9. partial/inaccessible prior check;
10. repeated target requiring quality clarification;
11. empty planner / need-more-information state;
12. next action rejected;
13. paused case on case list;
14. found on current suggested action;
15. found elsewhere/unplanned;
16. unresolved close;
17. persistent storage granted / denied;
18. valid v1 import migrated to v2;
19. invalid/future schema import rejected;
20. light/dark + reduced-motion + increased-contrast visual checks.

## Precedence rule

When the prototype and canonical design disagree, implementation follows:

1. canonical design spec;
2. stable `MD-WEB-REQ-*` requirements / contract tests;
3. this prototype review;
4. visual behavior of the supplied HTML.
