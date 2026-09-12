# ADR 015 — Web Reconstruction portable boundary

Status: Accepted for the unreleased `0.4.0` implementation scope.

## Context

Web/PWA originally exposed the physical Search/checklist workflow while reconstruction remained available through the plugin/agent surface. The current implementation adds deterministic browser Reconstruction without changing the Case schema or introducing a second domain reducer.

The architectural risk is ownership drift: Vue UI code could accidentally become a competing source of reconstruction truth, or a live model could become required for canonical memory evidence. Either would break the existing generated local-execution boundary, offline guarantees, and source-provenance rules.

## Decision

Web reconstruction uses portable authoritative commands (`record_free_account`, `rebuild_timeline`) and **generated local execution**. The Python portable kernel remains the authoritative deterministic semantic source and the committed generated TypeScript executor is the browser execution artifact.

Vue components collect user input, construct typed payloads, and render canonical state, but they do not own **reconstruction truth**. They do not implement a handwritten timeline/reconstruction reducer, infer unsupported concrete locations, resolve unknowns by plausibility, or promote reconstruction evidence when switching modes.

`record_free_account` preserves the user's free account verbatim as a reconstruction journal entry. Detailed recollection/habit/observation is canonical only when user-originated and user-confirmed. `rebuild_timeline` validates references and stores explicit unknowns and contradictions through portable authoritative semantics.

**Live-model clarification is not a dependency** of the `0.4.0` core reconstruction path. Deterministic Reconstruction does not call the assistant proposal boundary. A future model-assisted clarification feature may propose wording or questions, but it may not write canonical recollection/habit/observation on the user's behalf without a separately reviewed contract.

The transition to Search is explicit through `set_mode(search)` and preserves evidence without promotion. Search assistant proposals remain a separate semantic and transport boundary.

The data contract remains `mind-detective-case/v2`. This decision does not introduce Case v3, cloud Case persistence, background Case sync, Bayesian/POD fields, calibrated location probabilities, or hidden belief state.

## Consequences

- local deterministic reconstruction works after PWA preload without a model provider;
- Case mutation plus execution receipt retains the existing atomic IndexedDB transaction and idempotency semantics;
- generated Python↔TypeScript conformance remains the executable parity mechanism for Reconstruction commands;
- Vue can evolve presentation and input ergonomics without becoming a second domain engine;
- raw free account, user-confirmed structured evidence, unknowns, contradictions, and the later Search state remain portable in the same Case v2 export/import contract;
- evaluation of the existing Search B↔C assistant arm cannot be cited as evidence that live-model Reconstruction adds value;
- any future assistant-authored memory evidence, schema change, sync layer, or reconstruction-model efficacy claim requires a separate design and governance gate.
