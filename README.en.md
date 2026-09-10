# MIND Detective

<!-- release-0.2.0 -->

[Русский](README.md)

**MIND Detective is a systematic lost-item search assistant.** It reduces cognitive load during a search by preserving the user's own recollections without promoting them to verified facts, keeping a durable log of physical checks, proposing one useful next action, and resuming a saved case after interruption.

## What 0.2.0 adds

Version 0.2.0 keeps the five production plugin skills and adds a mobile-first **Nuxt 4 Web/PWA** over the same Python `CaseController`:

- one production shell for checklist and AI arms without exposing arm identity as separate UX;
- canonical browser persistence in IndexedDB, explicit JSON export/import, and deterministic v1→v2 migration;
- a stateless FastAPI adapter with no server-side Case database;
- a sequential retryable command queue with no optimistic canonical mutation;
- one-tap “Checked” as neutral `reported_check`, with delayed quality clarification;
- reviewed guard fallback without persisting or revealing a blocked raw proposal;
- PWA shell caching without `/api/`, Case/user/model/evaluation data, and without Background Sync;
- reviewed RU/EN copy, keyboard/focus contracts, and dark/reduced-motion/increased-contrast support;
- privacy-filtered browser-local evaluation events for checklist-vs-AI comparison.

Python `Case` + `CaseController` remain the single deterministic source of truth: there is no TypeScript port or parallel domain reducer.

## Architecture

```text
Nuxt 4 PWA
  │  IndexedDB / reviewed RU+EN UI / command queue
  ▼
FastAPI stateless adapter
  │
  ├── Python CaseController / planner / guard / artifacts
  │
  └── AI proposal ──► LiteLLM Proxy ──► configured model provider
```

Checklist and AI use the same canonical mutation path. In the AI arm a model can produce a structured candidate proposal, but model output never becomes state automatically: the server-side proposal/guard boundary returns only a reviewed structured proposal or a deterministic fallback.

## LiteLLM setup for the AI arm

The Web/API layer contains no provider-specific client configuration. The only live-model gateway is **LiteLLM Proxy**. Configure these server-side variables for the API:

```bash
export LITELLM_API_KEY="<proxy-key>"
export MIND_DETECTIVE_LITELLM_MODEL="<model-alias-from-litellm>"
export MIND_DETECTIVE_LITELLM_BASE_URL="http://127.0.0.1:4000"  # optional; this is the default
```

`LITELLM_API_KEY` and provider credentials must never be shipped in the browser bundle. Only the context needed for the current proposal is transiently processed for AI requests. Therefore browser-local persistence does **not** mean data never leaves the device: model context is processed by LiteLLM and the configured model provider according to that deployment/privacy boundary.

## Storage and offline behavior

Web cases are stored locally in IndexedDB. The Persistent Storage API can reduce eviction risk but is not a backup guarantee; use explicit JSON export for portability. The service worker stores only shell/static assets. An offline mutation is not treated as saved until the API returns a new canonical Case; retry reuses the same command envelope.

The plugin surface keeps the existing explicit local-file contract at `.mind-detective/cases/<case-id>/case.json`.

## Product limits

MIND Detective is not a medical tool, does not restore “true” memory, does not diagnose why forgetting happened, does not know an item's actual location, does not provide calibrated location percentages, and uses no Bayesian/POD/hidden belief-weight model. Repeated quick checks are not treated as independent evidence of absence. Uncertainty about a high-risk action exits ordinary physical-search reasoning.

## Development and verification

Development follows `SPEC → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY`. Normative `MD-REQ-*` and `MD-WEB-REQ-*` entries map to exact selectors in `docs/CONTRACT_MATRIX.json`. CI against the exact PR head validates Python 3.10/3.13, repository/plugin/API tests, Ruff, strict Mypy, frozen pnpm install, Vitest, production PWA build, Playwright on Chromium/WebKit, and secret scanning.

Start with [Getting Started](docs/GETTING_STARTED.en.md), then see [Architecture](docs/ARCHITECTURE.en.md), [Methodology](docs/METHODOLOGY.en.md), [Privacy (RU)](docs/PRIVACY.md), [Product Evaluation (RU)](docs/PRODUCT_EVALUATION.md), and [Release Policy](docs/RELEASE_POLICY.md).
