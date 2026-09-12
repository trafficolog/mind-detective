# Getting Started

[Русский](GETTING_STARTED.md)

## Plugin surface

The canonical plugin id is `mind-detective`; the current published version is `0.3.1`. The five production skills remain router, reconstruct, plan, resume, and close. The plugin runtime uses the Python standard library and needs no network credentials.

Plugin persistence remains explicit and case-local at `.mind-detective/cases/<case-id>/case.json`. The Web/PWA has a separate browser-local persistence contract and writes a newly created Case to IndexedDB immediately.

`main` already contains the deterministic Web Reconstruction foundation intended for the next release gate; this does not change the published version until separate release authorization.

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

## Web/PWA

```bash
pnpm --dir apps/web dev --host 127.0.0.1 --port 3000
```

Web runtime variables:

- `NUXT_PUBLIC_MIND_DETECTIVE_API_BASE` — API base URL, default `http://127.0.0.1:8000`;
- `NUXT_PUBLIC_MIND_DETECTIVE_ARM` — `checklist` or `assistant`;
- `NUXT_PUBLIC_MIND_DETECTIVE_LOCALE` — `auto`, `ru`, or `en`;
- `NUXT_PUBLIC_MIND_DETECTIVE_EVALUATION=1` — explicitly enables the evaluation UI.

### Reconstruction flow

A fresh Case can explicitly enter Reconstruction before physical checks begin:

1. Enter a **free account**. It is preserved **verbatim** as `free_account`; detailed structured statements are unavailable before this gate.
2. Add only **user-confirmed** structured recollection/habit/observation. The UI does not infer new concrete locations from guesses.
3. Build the timeline. `rebuild_timeline` uses portable authoritative semantics and keeps explicit **unknowns** and **contradictions**.
4. When ready, switch explicitly into Search. `set_mode(search)` changes mode while preserving reconstruction evidence without promotion.

`record_free_account`, `rebuild_timeline`, Search mutations, and Case persistence run through generated local execution and IndexedDB. **Local deterministic reconstruction** uses the unchanged `mind-detective-case/v2` schema.

### Offline proof

The service worker caches only shell/static assets. To exercise the real offline path, load the PWA online and wait for an active service worker before disabling the network. Create → Reconstruction free account → user-confirmed evidence → timeline rebuild → Search → check/pause-resume/close/export/import must remain deterministic without depending on the Case API or a model provider.

Live-model clarification is not a dependency of local deterministic Reconstruction. The assistant proposal boundary is used separately in the Search assistant arm.

## Developer verification

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -v
python -m scripts.write_local_execution_artifacts
python -m scripts.generate_local_execution_corpus
pnpm install --frozen-lockfile
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

Regenerating committed artifacts must leave a byte-clean diff. Production merge requires exact-head CI; release requires explicit human authorization and exact post-merge `main` CI through the hardened publisher.
