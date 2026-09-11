# Getting Started

[Русский](GETTING_STARTED.md)

## Plugin surface

The canonical plugin id is `mind-detective`, version `0.3.0`. The five production skills remain router, reconstruct, plan, resume, and close. The plugin runtime uses the Python standard library and needs no network credentials.

Explicit plugin persistence writes a case only after a user action (`save`/`pause`/`retain`) to `.mind-detective/cases/<case-id>/case.json`.

## Web/PWA 0.3.0

The Web surface uses Nuxt 4 with browser-local IndexedDB. Deterministic Case creation, commands, and checklist proposals run locally through the generated certified executor; a server API is not required for those operations. An online assistant proposal crosses the FastAPI → LiteLLM/provider boundary only after the execution-identity check.

The service worker caches only shell/static assets. To exercise the real offline path, load the PWA online and wait for an active service worker before disabling the network; create/search/check/pause-resume/close/export remain local.

## Developer verification

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
python -m unittest discover -s apps/api/tests -v
python -m scripts.write_local_execution_artifacts
python -m scripts.generate_local_execution_corpus
pnpm install --frozen-lockfile
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

Regenerating committed artifacts must leave a byte-clean diff. Production merge requires exact-head CI; release requires exact post-merge `main` CI through the hardened publisher.
