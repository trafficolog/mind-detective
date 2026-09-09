---
name: mind-detective
description: Use when the user wants structured help finding a misplaced physical item, continuing a saved search case, or closing a lost-item search.
---
# MIND Detective router

## Inputs

- the user's current request;
- item label when starting a case;
- an explicit case id or supplied case artifact when resuming;
- urgency or real-world constraints stated by the user.

## Deterministic calls

1. Call `scripts.safety.classify_request` **before** ordinary lost-item routing.
2. For a new ordinary-search case, create state through `scripts.controller.CaseController.create_case`.
3. Route reconstruction to `mind-detective-reconstruct`, physical search planning/logging to `mind-detective-plan`, an explicitly saved/supplied case to `mind-detective-resume`, and case completion to `mind-detective-close`.

## Outputs

Return one bounded next workflow step and preserve the canonical `Case` state. State limitations explicitly when the request is outside `0.1.0`.

## Limitations

MIND Detective does not restore memory, know where an item is, diagnose a forgetting mechanism, or provide calibrated location probabilities. High-risk uncertainty about whether an action happened (for example whether a medication dose was taken) must not enter ordinary lost-item reasoning. Generic skill hosts do not provide a repository-controlled mandatory pre-send interceptor.

## Transition

`router → reconstruct | plan | resume | close`, with safety classification preceding every ordinary route.
