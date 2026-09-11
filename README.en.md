# MIND Detective

<!-- release-0.3.0 -->

[Русский](README.md)

**MIND Detective is a systematic lost-item search assistant.** It reduces working-memory load during a search by separating user recollection from hypotheses, logging physical checks, selecting one next action, and preserving a case for later resume.

## What 0.3.0 adds

Version `0.3.0` makes deterministic Web/PWA execution local-first without introducing a second hand-maintained domain reducer:

- an authoritative restricted stdlib-only portable Python kernel;
- certified generator → committed TypeScript executor plus identity metadata;
- a differential Python↔TypeScript conformance corpus;
- local Case creation and deterministic commands without required `/api/v1/case/*` calls;
- atomic IndexedDB commit of canonical Case + execution receipt;
- idempotent retry by `command_id`, with conflicting reuse failing closed;
- local deterministic checklist proposals;
- assistant transport fallback without retrospective reconnect replay;
- execution identity/version/hash skew guard before model-provider creation;
- a preloaded PWA that completes the canonical search workflow offline.

`mind-detective-case/v2` remains the current Case schema. This release does not add cloud sync, Pyodide/WASM, Bayesian/POD logic, calibrated location percentages, or hidden belief state.

## 0.3.0 architecture

```text
portable Python kernel
        │
        ├── certified generator ──► committed TypeScript executor
        │                              │
        │                              ▼
        │                    local executor + IndexedDB
        │                    Case + execution receipt
        │
        └── FastAPI compatibility / proposal boundary
                                       │
                        assistant only ─┴─► LiteLLM Proxy
```

Python remains the authoritative semantic source. The TypeScript artifact is generated and checked against the conformance corpus; there is no hand-maintained parallel Case reducer.

## Offline and AI

The deterministic create/mutation/checklist path executes locally. The service worker caches only application-shell/static assets; it does not cache Case/user/model/evaluation data or `/api/`, and Case commands do not use Background Sync.

The AI arm calls the server-side proposal boundary only for an assistant proposal. Every request carries execution identity (`version`, `kernel_sha256`, `generated_sha256`, `generator_version`). A mismatch fails closed before provider creation. A transport failure uses the local deterministic fallback and is not replayed after reconnect.

## Storage and privacy

Web canonical persistence is device-local IndexedDB. Explicit JSON export/import remains the portability mechanism. The plugin surface keeps its case-local `.mind-detective/cases/<case-id>/case.json` contract. Browser-local storage does not mean assistant model context never leaves the device: only the minimum transient context needed for an online assistant proposal crosses LiteLLM and the configured provider boundary.

## Product boundaries

The product does not diagnose why forgetting occurred, assert the real location of an item, guarantee search success, or assign calibrated probabilities to locations. High-risk action uncertainty is routed outside ordinary physical-search reasoning.

## Development and verification

Normative `MD-REQ-*`, `MD-WEB-REQ-*`, and `MD-OFFLINE-REQ-*` contracts have exact selectors in `docs/CONTRACT_MATRIX.json`. Exact-head CI covers Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, generated-artifact freshness, conformance corpus, frozen pnpm installation, Vitest, production PWA build, Chromium/WebKit Playwright, and secret scanning.

See [Getting Started](docs/GETTING_STARTED.en.md), [Architecture](docs/ARCHITECTURE.en.md), [Privacy](docs/PRIVACY.md), [Product Evaluation](docs/PRODUCT_EVALUATION.md), and [Release Policy](docs/RELEASE_POLICY.en.md).
