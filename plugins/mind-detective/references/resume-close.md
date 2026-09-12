# Resume and close reference

Plugin persistence is explicit and case-local under `.mind-detective/cases/<case-id>/case.json`; plugin case creation alone does not silently persist the file. The Web/PWA has a separate local-first contract and persists a newly created Web Case to IndexedDB immediately. Resuming requires an explicit case id or supplied artifact; do not scan sibling cases to infer which one the user means.

A handoff preserves provenance and checked-state details so another person can continue without repeating low-value checks. It is derived from the canonical case and must not strengthen old statements.

At close, distinguish `found`, `unresolved`, and user-requested `abandoned`. The found location is user-reported. A possible cause can be preserved only as user-authored context; it is never a diagnosed forgetting mechanism. Retention and deletion are explicit choices, and deletion targets only the selected case.
