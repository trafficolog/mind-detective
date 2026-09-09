---
name: mind-detective-plan
description: Use when an active MIND Detective case needs physical search logging, candidate checks, or exactly one explicit next search action.
---
# Plan and record physical checks

## Inputs

- one active `Case`;
- supported route/context already recorded in the case;
- explicit candidate checks, including model-formulated search proposals;
- the user's report of each physical check's target, method, result and inaccessible parts.

## Deterministic calls

1. If the assistant proposes a new concrete place to search, phrase it as an explicit search proposal and submit it to `scripts.guard.lint_candidate(..., mode=InteractionMode.SEARCH_PLANNING, ...)`. Never phrase a proposal as a recovered memory or known fact.
2. Represent assistant-originated proposals as `StatementType.SEARCH_SUGGESTION`, not recollection/observation.
3. Record every completed/partial/inaccessible physical check as `scripts.search_log.SearchCheck` **before** selecting another action. Repeated checks remain in history.
4. Use `scripts.search_log.is_duplicate_target` only to surface overlap, never to suppress a check or turn repeated misses into independent probability evidence.
5. Use `scripts.planner.select_next_action` for exactly one next action. The planner's categorical order is authoritative; do not add a numerical score or hidden likelihood.
6. Apply mutations through `CaseController`.

## Outputs

Return the recorded check state plus one next action and its categorical rationale codes, or state that no safe candidate remains.

## Limitations

Search suggestions are proposals, not memories. Search checks do not create calibrated probabilities, POD estimates, Bayesian updates or proof of absence. A glance and a systematic empty-and-check are distinct search records.

## Transition

`candidate checks → record SearchCheck → refresh one next action → repeat | pause/resume | close`. See `references/search-planning.md` and `references/guard-rules.md`.
