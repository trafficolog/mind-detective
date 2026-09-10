# Architecture

[Русский](ARCHITECTURE.md)

## Single domain source of truth

The canonical `Case` together with the Python `CaseController` remains the only deterministic state authority. Version 0.2.0 adds a Web/PWA surface but does **not** port the domain state machine to TypeScript or introduce a parallel reducer. The Nuxt client sends commands and accepts the full canonical Case returned by the API.

The plugin runtime still separates provenance (`statements.py`), uncertainty-preserving sequence (`timeline.py`), physical checks (`search_log.py`), categorical one-next-action planning (`planner.py`), guard checks (`guard.py`), plugin-surface local file persistence (`store.py`), and derived artifacts (`artifacts.py`). Safety routing runs before ordinary search reasoning.

## Web/PWA 0.2.0

```text
Nuxt 4 PWA
  │  IndexedDB: browser-local canonical Case copy
  │  sequential command queue / reviewed RU+EN copy
  ▼
FastAPI stateless adapter
  │
  ├── Python CaseController / planner / guard / artifacts
  │
  └── proposal adapter ──► LiteLLM Proxy ──► configured model provider
```

`apps/web` owns presentation, browser-local IndexedDB persistence, the PWA shell, import/export, and interaction telemetry that excludes raw case content. `apps/api` is a thin stateless transport adapter: it does not store user cases and does not become another domain state owner.

For the AI arm, LiteLLM Proxy is the single live-model gateway. Provider credentials are never shipped to the client; model output crosses the server-side proposal/guard boundary and is converted into a reviewed proposal contract. Checklist and AI arms use the same production shell and the same canonical mutation path.

## Persistence and PWA boundary

Web cases are stored in IndexedDB. The service worker caches only application-shell/static assets: `/api/`, Case payloads, user text, model output, and evaluation records are excluded from the PWA cache and are not submitted through background sync. The persistent-storage API is treated only as a browser capability request, never as a backup guarantee. Explicit JSON export/import provides portability, including deterministic v1→v2 migration.

The plugin surface keeps the existing explicit case-local file persistence contract at `.mind-detective/cases/<case-id>/case.json`; Web persistence does not change that contract and does not create cross-case learning or profiles.

## Verifiable boundaries

Normative requirements live in `REQUIREMENTS.md`, with exact traceability in `CONTRACT_MATRIX.json`. CI validates Python 3.10/3.13, API behavior, Ruff, strict Mypy, frozen pnpm installation, Vitest, production PWA build, Playwright on Chromium/WebKit, and secret scanning against the exact PR head SHA.

Eval/browser fixtures demonstrate specific control paths; they are not proof of scientific validity or arbitrary live-model semantic compliance. Architectural decisions are recorded under `docs/adr/`.
