# Resume and close reference

Persistence in `0.1.0` is explicit and case-local under `.mind-detective/cases/<case-id>/case.json`. Starting a case does not save it automatically. Resuming requires an explicit case id or supplied artifact; do not scan sibling cases to infer which one the user means.

A handoff preserves provenance and checked-state details so another person can continue without repeating low-value checks. It is derived from the canonical case and must not strengthen old statements.

At close, distinguish `found`, `unresolved`, and user-requested `abandoned`. The found location is user-reported. A possible cause can be preserved only as user-authored context; it is never a diagnosed forgetting mechanism. Retention and deletion are explicit choices, and deletion targets only the selected case.
