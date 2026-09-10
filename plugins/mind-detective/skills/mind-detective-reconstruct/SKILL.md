---
name: mind-detective-reconstruct
description: Use when an active lost-item case needs a neutral reconstruction of the user's own account and an uncertainty-preserving timeline.
---
# Reconstruct supported sequence

## Inputs

- one active `Case`;
- the user's free account in their own words;
- user-authored clarifications, timestamps and explicitly mentioned locations.

## Deterministic calls

1. Obtain a free account before detailed clarification. Do not seed it with candidate locations.
2. Store user material through `scripts.statements.create_statement`; never create assistant-authored `recollection`, `habit`, or `observation`.
3. Before showing an investigative clarification, submit the candidate to `scripts.guard.lint_candidate(..., mode=InteractionMode.RECONSTRUCTION, known_locations=...)`. Reformulate any blocked candidate rather than bypassing the helper.
4. Build the sequence through `scripts.timeline.build_timeline`; preserve unknowns and contradictions instead of resolving them by plausibility.
5. Update the case only through `CaseController` operations.

## Outputs

Return the updated case, explicit unknowns/contradictions, and the next neutral clarification or transition to physical planning.

## Limitations

A vivid or confident recollection is still user-reported evidence. Habit is not an episodic recollection. A missing recollection is not proof that an event did not happen. The guard's lexical checks cover submitted candidates only; they are not proof that every host/model utterance was intercepted.

## Transition

`FREE ACCOUNT → neutral clarification → timeline → mind-detective-plan` when enough supported structure exists. See `references/reconstruction.md` and `references/guard-rules.md`.
