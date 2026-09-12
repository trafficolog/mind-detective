# Getting Started

[Русский](GETTING_STARTED.md)

## Plugin surface

The canonical plugin id is `mind-detective`, version `0.3.1`. The five production skills remain router, reconstruct, plan, resume, and close. The plugin runtime uses the Python standard library and needs no network credentials.

Plugin persistence remains explicit and case-local at `.mind-detective/cases/<case-id>/case.json`. The Web/PWA has a separate browser-local persistence contract and writes a newly created Case to IndexedDB immediately.

## Install dependencies

From the repository root:

```bash
python -m pip install -e apps/api
pnpm install --frozen-lockfile
```

Copy `.env.example` into your local environment and set only the values you need. Never commit real credentials.

## API

In the monorepo, plugin root and execution metadata are resolved through bounded discovery:

```bash
uvicorn mind_detective_api.app:app --app-dir apps/api --host 127.0.0.1 --port 8000 --reload
```

For a separately packaged or relocated API, provide the paths explicitly:

```bash
export MIND_DETECTIVE_PLUGIN_ROOT=/absolute/path/to/plugins/mind-detective
export MIND_DETECTIVE_EXECUTION_METADATA=/absolute/path/to/localExecution.meta.json
uvicorn mind_detective_api.app:app --app-dir apps/api --host 127.0.0.1 --port 8000
```

Assistant transport uses `LITELLM_API_KEY`, `MIND_DETECTIVE_LITELLM_MODEL`, and `MIND_DETECTIVE_LITELLM_BASE_URL`. Without the assistant arm, the deterministic Web path remains local-first.

## Web/PWA 0.3.1

```bash
pnpm --dir apps/web dev --host 127.0.0.1 --port 3000
```

Web runtime variables:

- `NUXT_PUBLIC_MIND_DETECTIVE_API_BASE` — API base URL, default `http://127.0.0.1:8000`;
- `NUXT_PUBLIC_MIND_DETECTIVE_ARM` — `checklist` or `assistant`;
- `NUXT_PUBLIC_MIND_DETECTIVE_LOCALE` — `auto`, `ru`, or `en`;
- `NUXT_PUBLIC_MIND_DETECTIVE_EVALUATION=1` — explicitly enables the evaluation UI.

The Web surface is the physical Search/checklist workflow. Full reconstruction remains a plugin/agent capability; Case import, deterministic commands, and checklist proposals execute locally through the generated certified executor.

The service worker caches only shell/static assets. To exercise the real offline path, load the PWA online and wait for an active service worker before disabling the network. The deterministic create/search/check/pause-resume/close/export/import path must not depend on the Case API.

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

Regenerating committed artifacts must leave a byte-clean diff. Production merge requires exact-head CI; release requires explicit human authorization and exact post-merge `main` CI through the hardened publisher.
