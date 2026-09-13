# Architecture

[Русский](ARCHITECTURE.md)

## Single source of deterministic semantics

Python remains the authoritative source for deterministic Case semantics. The portable subset lives in `plugins/mind-detective/scripts/portable_kernel.py` plus certified intrinsics. Web has no second hand-maintained reducer: the TypeScript executor is generated from validated Python source and committed together with identity metadata.

```text
portable Python kernel + certified intrinsics
                 │
                 ├── AST/certification gate
                 │
                 ├── deterministic generator
                 │         │
                 │         ▼
                 │   committed TypeScript executor + metadata
                 │         │
                 │         ├── record_free_account
                 │         ├── rebuild_timeline
                 │         ├── differential conformance corpus
                 │         ▼
                 │   Nuxt local executor
                 │         │
                 │         ▼
                 │   IndexedDB atomic transaction
                 │   canonical Case + execution receipt
                 │
                 └── FastAPI compatibility / Search proposal boundary
                                      │
                           assistant ──┴──► LiteLLM Proxy
```

## Local execution boundary

Case creation, deterministic commands, Reconstruction, and checklist proposals execute in the browser through the generated certified artifact. `apps/web/app/lib/execution/localExecutor.ts` adds persistence and idempotence boundaries but does not define separate domain semantics.

Each command mutation is calculated from a canonical input Case and immutable command envelope. The Case and execution receipt are written in one IndexedDB transaction. Reusing the same `command_id` with the same input returns the persisted canonical result; reusing it with different input fails closed. A failed transaction must not partially mutate the persisted Case.

`mind-detective-case/v2` remains the current data schema. Web Reconstruction does not introduce Case v3, cloud sync, Pyodide/WASM, Bayesian/POD logic, calibrated location probabilities, or hidden belief state.

## Reconstruction boundary

Web Reconstruction is a state-first **local deterministic reconstruction** path, not a separate chatbot or handwritten reducer contour.

1. `record_free_account` preserves the user's **free account** **verbatim** as `author=user`, `mode=reconstruction`, `entry_type=free_account`. It does not automatically create a structured statement.
2. After the free-account gate, the user can explicitly confirm structured recollection/habit/observation. Canonical structured evidence remains **user-confirmed** and user-originated.
3. `rebuild_timeline` validates statement references and atomically stores the canonical timeline, including explicit **unknowns** and **contradictions**.
4. Vue components collect payloads and render canonical state. They do not own reconstruction truth, compute competing timeline semantics, or resolve uncertainty by plausibility.
5. `set_mode(search)` is an explicit transition into Search and does not promote or rewrite reconstruction evidence.

Reconstruction does not infer new concrete locations. A user-supplied location may remain part of user-confirmed material; Search proposals are a separate semantic category.

## Generator and conformance

The generator accepts only the restricted AST/call surface and certified intrinsics. Unsupported constructs fail before emission. CI regenerates the artifact and corpus and requires a byte-clean git diff.

The committed conformance corpus contains deterministic vectors for create, commands, proposal, planner, and Reconstruction commands. Vitest executes every vector against the generated TypeScript executor. This verifies observable parity for the covered portable contract, not general equivalence between arbitrary Python and TypeScript.

## API and assistant boundary

FastAPI remains a stateless compatibility and server-side Search proposal boundary. It is not the required mutation path for deterministic Web commands and stores no Case database.

Live-model clarification is not a dependency of the Reconstruction core path. Reconstruction does not call `nextProposal()` and model output cannot write canonical recollection/habit/observation on the user's behalf. Assistant proposals cross the server boundary only in the Search assistant arm. The client sends execution identity fields `version`, `kernel_sha256`, `generated_sha256`, and `generator_version`; mismatch returns `MD_WEB_EXECUTION_CONTRACT_MISMATCH` before provider creation.

On assistant transport failure, the Search arm uses the local deterministic checklist fallback. The old model request is not retrospectively replayed after reconnect.

## Persistence, PWA, and privacy boundary

Web canonical persistence is IndexedDB. The service-worker precache contains application-shell/static assets; `/api/`, Case payloads, user text, model output, and evaluation records are excluded, and Case commands do not use Background Sync. After preload, the canonical Search and Reconstruction deterministic paths can run offline.

The verbatim free account, user-confirmed structured evidence, timeline unknowns/contradictions, and Search state live in the same Case v2. Explicit JSON export/import preserves this reconstruction state without a separate schema migration.

The plugin surface retains its explicit case-local `.mind-detective/cases/<case-id>/case.json` contract. Neither Web nor plugin surfaces create cross-case learning or profiles.

## Verifiable boundaries

Normative `MD-REQ-*`, `MD-WEB-REQ-*`, and `MD-OFFLINE-REQ-*` contracts live in `REQUIREMENTS.md` with exact selectors in `CONTRACT_MATRIX.json`. Reconstruction is covered by `MD-WEB-REQ-RECONSTRUCT-01..10`. Exact-head CI covers Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, generated-artifact freshness, conformance corpus, frozen pnpm installation, Vitest, production PWA build, Chromium/WebKit Playwright, and secret scanning.

Key decisions are recorded in [ADR 013](adr/013-generated-portable-local-execution.md), [ADR 014](adr/014-execution-identity-skew-gate.md), and [ADR 015](adr/015-web-reconstruction-portable-boundary.md).
