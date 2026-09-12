# MIND Detective

<!-- release-0.3.1 -->

[Русский](README.md)

**MIND Detective is a systematic lost-item search assistant.** It reduces working-memory load by separating the user's account from hypotheses, preserving checkable evidence, logging physical checks, and keeping a Case resumable.

> The current published release is `0.3.1`. `main` already contains the deterministic Web Reconstruction foundation intended for the next release gate, but it has not been published as a new release. Version surfaces, tags, and the release manifest remain `0.3.1` until separate human authorization.

## Web Reconstruction on current `main`

Reconstruction is now part of the Web/PWA and remains a distinct mode from physical Search:

- the user starts with a **free account**, preserved **verbatim** as `free_account` rather than being automatically classified as recollection/habit/observation;
- structured evidence is recorded only as explicit **user-confirmed** evidence;
- the canonical timeline preserves explicit **unknowns** and **contradictions** instead of filling gaps with plausible guesses;
- Reconstruction does not seed new concrete locations as if they came from the user's memory and does not establish the item's actual location;
- transition into Search is explicit through `set_mode(search)` and does not promote reconstruction evidence;
- `record_free_account` and `rebuild_timeline` run through generated local execution and IndexedDB, so **local deterministic reconstruction** works after PWA preload without a live model;
- live-model clarification is not a dependency of the core reconstruction path and cannot write canonical recollection/habit/observation on the user's behalf.

The Case schema remains `mind-detective-case/v2`.

## Architecture

```text
portable Python kernel
        │
        ├── certified generator ──► committed TypeScript executor
        │                              │
        │                              ├── record_free_account
        │                              ├── rebuild_timeline
        │                              ▼
        │                    local executor + IndexedDB
        │                    Case + execution receipt
        │
        └── FastAPI assistant boundary
                    │
                    └── LiteLLM/provider (Search assistant arm only)
```

Python remains the authoritative deterministic semantic source. Reconstruction Vue components collect user input and render canonical state, but they do not own reconstruction truth and do not implement a parallel timeline/reconstruction reducer.

## Offline and AI

The deterministic create/mutation/reconstruction/search/checklist/import path runs locally. The service worker caches only application-shell/static assets; it does not cache Case/user/model/evaluation data or `/api/`, and Case commands do not use Background Sync.

The Reconstruction core does not require a model provider. In the Search assistant arm, the server-side proposal boundary is used only for assistant proposals. Each online assistant request carries execution identity (`version`, `kernel_sha256`, `generated_sha256`, `generator_version`); mismatch fails closed before provider creation. Transport failure uses a local deterministic Search fallback and the old model request is not replayed after reconnect.

## Storage and privacy

Web canonical persistence is device-local IndexedDB and a new Web Case is stored locally immediately. The verbatim `free_account`, user-confirmed statements, timeline unknowns/contradictions, and Search state live in the same Case v2. Explicit JSON export/import remains the portability mechanism.

The plugin surface separately writes `.mind-detective/cases/<case-id>/case.json` only after an explicit persistence action. Browser-local storage does not mean online Search assistant context can never leave the device: only the minimum transient context required for an online assistant proposal crosses LiteLLM and the configured provider boundary. Deterministic Reconstruction itself does not call that provider.

## Product boundaries

The product does not diagnose why forgetting occurred, assert the real location of an item, guarantee search success, or assign calibrated probabilities to locations. Reconstruction structures only the user's account and facts they explicitly confirm; Search owns physical checks and next-action proposals. High-risk uncertainty is routed outside ordinary physical-search reasoning.

## Published `0.3.1`

`0.3.1` remains the current published hardening release for the local-first contour: safety ingress, structured Search targets, production-reachability contracts, local Case import, typed proposal copy, installable PWA assets, and portable API path discovery. Historical release/tag surfaces are unchanged by this documentation reconciliation.

## Development and verification

Normative `MD-REQ-*`, `MD-WEB-REQ-*`, and `MD-OFFLINE-REQ-*` contracts, including `MD-WEB-REQ-RECONSTRUCT-01..10`, have exact selectors in `docs/CONTRACT_MATRIX.json`. Exact-head CI covers Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, generated-artifact freshness, conformance corpus, frozen pnpm installation, Vitest, production PWA build, Chromium/WebKit Playwright, and secret scanning.

See [Getting Started](docs/GETTING_STARTED.en.md), [Architecture](docs/ARCHITECTURE.en.md), [Privacy](docs/PRIVACY.md), [Product Evaluation](docs/PRODUCT_EVALUATION.md), [Methodology](docs/METHODOLOGY.en.md), [ADR 015](docs/adr/015-web-reconstruction-portable-boundary.md), and [Release Policy](docs/RELEASE_POLICY.en.md).
