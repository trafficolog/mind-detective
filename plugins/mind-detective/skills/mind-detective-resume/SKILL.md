---
name: mind-detective-resume
description: Use when the user explicitly supplies or names a previously saved MIND Detective case and wants to continue or hand it to another person.
---
# Resume or hand off an explicit case

## Inputs

- an explicit case id and local root, or a supplied canonical case artifact;
- the user's explicit intent to resume or hand off that case.

## Deterministic calls

1. Load only the requested case with `scripts.store.load_case`; do not enumerate sibling cases or build a cross-case index/profile.
2. Resume a paused case with `CaseController.resume`.
3. Build a shareable state summary with `scripts.artifacts.build_handoff` when needed. Treat the handoff as a derived read artifact, not a second source of truth.
4. Continue through `mind-detective-plan` or `mind-detective-close` according to the saved lifecycle/state.

## Outputs

Return the resumed canonical case or a handoff artifact that preserves statement provenance, timeline uncertainty, search methods, inaccessible parts, constraints and the current next action.

## Limitations

`0.1.0` has case-local persistence only. Saved cases are not silently aggregated into priors, recommendations or user profiles. Missing history remains missing; resume must not invent it.

## Transition

`explicit saved/supplied case → load → resume/handoff → plan | close`. See `references/resume-close.md`.
