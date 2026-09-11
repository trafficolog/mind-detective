# Architecture

[Русский](ARCHITECTURE.md)

## Single source of deterministic semantics

In `0.3.0`, Python remains the authoritative source for deterministic Case semantics. The portable subset lives in `plugins/mind-detective/scripts/portable_kernel.py` plus certified intrinsics. Web has no second hand-maintained reducer: the TypeScript executor is generated from validated Python source and committed as a reproducible artifact together with identity metadata.

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
                 │         ├── differential conformance corpus
                 │         ▼
                 │   Nuxt local executor
                 │         │
                 │         ▼
                 │   IndexedDB atomic transaction
                 │   canonical Case + execution receipt
                 │
                 └── FastAPI compatibility / proposal boundary
                                      │
                           assistant ──┴──► LiteLLM Proxy
```

## Local execution boundary

Case creation, deterministic commands, and checklist proposals execute in the browser through the generated certified artifact. `apps/web/app/lib/execution/localExecutor.ts` adds persistence and idempotence boundaries but does not define separate domain semantics.

Each command mutation is calculated from a canonical input Case and immutable command envelope. The Case and execution receipt are written in one IndexedDB transaction. Reusing the same `command_id` with the same input returns the persisted canonical result; reusing it with different input fails closed. A failed transaction must not partially mutate the persisted Case.

`mind-detective-case/v2` remains the current data schema. `0.3.0` does not introduce Case v3, cloud sync, Pyodide/WASM, Bayesian/POD logic, calibrated location probabilities, or hidden belief state.

## Generator and conformance

The generator accepts only the restricted AST/call surface and certified intrinsics. Unsupported constructs fail before emission. CI regenerates the artifact and corpus and requires a byte-clean git diff.

The committed conformance corpus contains deterministic vectors for create, commands, proposal, and planner operations. Vitest executes every vector against the generated TypeScript executor. This verifies observable parity for the covered portable contract, not general equivalence between arbitrary Python and TypeScript.

## API and assistant boundary

FastAPI remains a stateless compatibility and server-side proposal boundary. It is not the required mutation path for deterministic Web commands and stores no Case database.

Assistant proposals cross the server boundary only when live-model generation is needed. The client sends execution identity fields `version`, `kernel_sha256`, `generated_sha256`, and `generator_version`. The server validates identity before provider creation; mismatch returns `MD_WEB_EXECUTION_CONTRACT_MISMATCH` and does not call the provider. An already committed local deterministic mutation is not rolled back.

On assistant transport failure, the arm uses the local deterministic checklist fallback. The old model request is not retrospectively replayed after reconnect.

## Persistence, PWA, and privacy boundary

Web canonical persistence is IndexedDB. The service-worker precache contains application-shell/static assets; `/api/`, Case payloads, user text, model output, and evaluation records are excluded, and Case commands do not use Background Sync. After preload, the canonical search workflow can run offline.

The plugin surface retains its explicit case-local `.mind-detective/cases/<case-id>/case.json` contract. Neither Web nor plugin surfaces create cross-case learning or profiles.

## Verifiable boundaries

Normative `MD-REQ-*`, `MD-WEB-REQ-*`, and `MD-OFFLINE-REQ-*` contracts live in `REQUIREMENTS.md` with exact selectors in `CONTRACT_MATRIX.json`. Exact-head CI covers Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, generated-artifact freshness, conformance corpus, frozen pnpm installation, Vitest, production PWA build, Chromium/WebKit Playwright, and secret scanning.

Key decisions are recorded as ADRs, including [ADR 013](adr/013-generated-portable-local-execution.md) and [ADR 014](adr/014-execution-identity-skew-gate.md).
