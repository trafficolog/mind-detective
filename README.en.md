# MIND Detective

<!-- release-0.3.1 -->

[Русский](README.md)

**MIND Detective is a systematic lost-item search assistant.** It reduces working-memory load during a search by separating user recollection from hypotheses, logging physical checks, selecting one next action, and preserving a case for later resume.

## What 0.3.1 adds

Version `0.3.1` is a review-driven hardening patch on top of the `0.3.0` local-first execution contour:

- high-risk action uncertainty is stopped at interaction ingress before Case mutation;
- Web Search uses a structured checklist target instead of echoing arbitrary prose;
- active requirement helpers are checked for production reachability;
- evaluation vocabulary matches the decision events the product actually measures;
- Case import validates and migrates locally without requiring `/api/v1/case/validate`;
- the Web/PWA boundary is explicit: physical Search/checklist only, with full reconstruction remaining a plugin/agent capability;
- the semantic scenario corpus is explicitly governed as manual review, with no automated-runner claim;
- proposal `copy_key` values are typed and rendered through RU/EN copy;
- the PWA ships installable 192/512 PNG icons plus an Apple touch icon;
- the API no longer assumes a fixed monorepo depth: plugin root is supplied through `MIND_DETECTIVE_PLUGIN_ROOT` or bounded discovery.

`mind-detective-case/v2` remains the current Case schema. This release does not add cloud sync, Pyodide/WASM, Bayesian/POD logic, calibrated location percentages, or hidden belief state.

## 0.3.1 architecture

```text
portable Python kernel
        │
        ├── certified generator ──► committed TypeScript executor
        │                              │
        │                              ▼
        │                    local executor + IndexedDB
        │                    Case + execution receipt
        │
        └── FastAPI assistant boundary
                    │
                    ├── plugin root: env/discovery
                    └── LiteLLM/provider (assistant arm only)
```

Python remains the authoritative semantic source. The TypeScript artifact is generated and checked against the conformance corpus; there is no hand-maintained parallel Case reducer.

## Offline and AI

The deterministic create/mutation/checklist/import path executes locally. The service worker caches only application-shell/static assets; it does not cache Case/user/model/evaluation data or `/api/`, and Case commands do not use Background Sync.

The AI arm calls the server-side proposal boundary only for an assistant proposal. Every request carries execution identity (`version`, `kernel_sha256`, `generated_sha256`, `generator_version`). A mismatch fails closed before provider creation. A transport failure uses the local deterministic fallback and is not replayed after reconnect.

## Storage and privacy

Web canonical persistence is device-local IndexedDB; a new Web Case is persisted locally immediately. Explicit JSON export/import remains the portability mechanism. The plugin surface separately writes `.mind-detective/cases/<case-id>/case.json` only after an explicit persistence action. Browser-local storage does not mean assistant model context never leaves the device: only the minimum transient context needed for an online assistant proposal crosses LiteLLM and the configured provider boundary.

## Product boundaries

The product does not diagnose why forgetting occurred, assert the real location of an item, guarantee search success, or assign calibrated probabilities to locations. High-risk action uncertainty is routed outside ordinary physical-search reasoning. The Web/PWA is a Search/checklist surface; reconstruction remains available through the plugin/agent workflow.

## Development and verification

Normative `MD-REQ-*`, `MD-WEB-REQ-*`, and `MD-OFFLINE-REQ-*` contracts have exact selectors in `docs/CONTRACT_MATRIX.json`. Exact-head CI covers Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, generated-artifact freshness, conformance corpus, frozen pnpm installation, Vitest, production PWA build, Chromium/WebKit Playwright, and secret scanning.

See [Getting Started](docs/GETTING_STARTED.en.md), [Architecture](docs/ARCHITECTURE.en.md), [Privacy](docs/PRIVACY.md), [Product Evaluation](docs/PRODUCT_EVALUATION.md), [Methodology](docs/METHODOLOGY.en.md), and [Release Policy](docs/RELEASE_POLICY.en.md).
