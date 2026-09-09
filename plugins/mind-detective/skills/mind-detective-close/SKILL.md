---
name: mind-detective-close
description: Use when the user found the item, stops an unresolved search, abandons the case, or wants to retain/delete the case-local artifact.
---
# Close a MIND Detective case

## Inputs

- one active or resumed `Case`;
- `found`, `unresolved`, or user-requested `abandoned` outcome;
- user-reported found location when applicable;
- immediately preceding search-check id when known;
- optional user-authored possible-cause statement id;
- optional simple prevention note;
- explicit `retain` or `delete` decision.

## Deterministic calls

1. Close through `CaseController.close_found` or `close_unresolved`.
2. Build the artifact with `scripts.artifacts.build_outcome`; a possible cause must reference a user-authored statement.
3. On explicit retain, persist with `scripts.store.save_case`. On explicit delete, remove only that case with `scripts.store.delete_case`.

## Outputs

Return `mind-detective-outcome/v1` with status, supported outcome fields, retention decision and limitations.

## Limitations

Finding the item does not diagnose why it was forgotten. A user-authored possible cause remains context/hypothesis. Do not add a `forgetting_mechanism`, probability, private chain-of-thought or cross-case learning record.

## Transition

`active/resumed case → found | unresolved | abandoned → outcome artifact → retain | delete`. See `references/resume-close.md`.
