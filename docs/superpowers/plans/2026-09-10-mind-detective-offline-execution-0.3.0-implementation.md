# MIND Detective 0.3.0 Offline Deterministic Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the already-loaded MIND Detective PWA complete deterministic lost-item-search workflows without network round-trips by generating a TypeScript local executor from a restricted Python transition kernel and certifying exact parity with the Python reference runtime.

**Architecture:** `CaseController` remains the public Python domain boundary, but browser-eligible deterministic semantics move into a pure JSON-compatible `PortableTransitionKernel`. A stdlib-only generator emits `apps/web/app/generated/localExecution.ts`; CI certifies it with canonical hashing and a deterministic Python↔TypeScript conformance corpus. The Web app commits `Case v2 + execution receipt` atomically in IndexedDB, uses the generated checklist proposal path offline, and only calls LiteLLM for new assistant proposals while online and execution-contract-compatible.

**Tech Stack:** Python 3.10/3.13 stdlib-first plugin core; Python `ast`/`hashlib`/`json` generator tooling; generated TypeScript; Nuxt 4.5.2; Vue; IndexedDB; Vitest 5.0.0; Playwright 1.63.0; existing FastAPI + LiteLLM/OpenAI-compatible transport; existing GitHub Actions/release publisher.

**Specs:**
- `docs/superpowers/specs/2026-09-10-mind-detective-offline-execution-0.3.0-design.md`
- `docs/superpowers/specs/2026-09-10-mind-detective-offline-execution-0.3.0-codegen-hardening.md`

**Execution hardening:** `docs/superpowers/plans/2026-09-10-mind-detective-offline-execution-0.3.0-implementation-hardening.md`

## Global Constraints

- Release target is repository `0.3.0` and plugin `mind-detective 0.3.0`.
- Existing immutable `0.1.0` and `0.2.0` releases/tags remain untouched.
- `mind-detective-case/v2` remains the canonical persisted Case schema; no Case v3.
- `CaseController` remains the public Python mutation boundary.
- The browser may execute only code generated from the restricted Python portable kernel; no hand-maintained TypeScript domain reducer is allowed.
- Generated TypeScript is build output and is never manually edited.
- Python remains the reference oracle; every supported generated transition/proposal must match Python output or exact machine error code on the conformance corpus.
- API command/checklist adapters validate transport and delegate supported semantics; they may not preserve an independent reducer.
- Python-observable clone/string/error semantics that can differ in JavaScript use certified portable intrinsics; approximate JavaScript substitutes are forbidden for domain decisions.
- Execution identity includes contract version, kernel SHA-256, generated artifact SHA-256 and generator version.
- No clocks, randomness, filesystem/network access, environment access, reflection, dynamic imports, model calls, floating-point ranking/probability math, or mutable globals are allowed in the portable kernel.
- IDs and timestamps are supplied by request/command envelopes only.
- Deterministic commands are local-first for a compatible `0.3.0` Web client.
- Case mutation and execution receipt write occur in one IndexedDB transaction.
- Duplicate `command_id` with the same input identity is idempotent; conflicting identity fails with `MD_WEB_COMMAND_ID_CONFLICT`.
- Offline Case creation is create-only; matching creation identity is idempotent and conflicting `case_id` fails with `MD_WEB_CASE_ID_CONFLICT`.
- Offline assistant mode uses deterministic checklist guidance immediately; offline history is never automatically replayed to LiteLLM after reconnect.
- LiteLLM remains server-side only for newly requested online assistant proposals.
- Execution-contract identity mismatch fails assistant/network semantics closed with `MD_WEB_EXECUTION_CONTRACT_MISMATCH` while leaving local certified execution available.
- No accounts, server case DB, cloud sync, background case upload, Pyodide/WASM, Bayesian/POD/probability scoring, cross-case learning, or native app work in `0.3.0`.
- CI retains Python 3.10/3.13, Ruff, strict Mypy, repository/plugin/API tests, frozen pnpm install, Vitest, Nuxt/PWA build, Chromium/WebKit Playwright, secret scan, exact PR-head verification and canonical full-SHA release governance.

---

## File Structure

### Portable domain source

- `plugins/mind-detective/scripts/portable_contract.py` — contract constants, supported schemas/commands and stable errors.
- `plugins/mind-detective/scripts/portable_intrinsics.py` — Python reference clone/casefold/whitespace/string-order/error intrinsics.
- `plugins/mind-detective/scripts/portable_kernel.py` — JSON-compatible deterministic transitions and checklist proposal semantics.
- `plugins/mind-detective/scripts/controller.py` — public dataclass facade delegating eligible transitions to the portable kernel.
- `plugins/mind-detective/scripts/planner.py` — typed compatibility facade over portable planner semantics.
- `plugins/mind-detective/tests/test_portable_contract.py`
- `plugins/mind-detective/tests/test_portable_intrinsics.py`
- `plugins/mind-detective/tests/test_portable_kernel.py`
- `plugins/mind-detective/tests/test_portable_planner.py`
- `plugins/mind-detective/tests/test_controller_portable_parity.py`

### Generator and conformance tooling

- `scripts/local_execution_ast.py` — restricted-AST/intrinsic validator.
- `scripts/generate_local_execution.py` — deterministic Python→TypeScript emitter.
- `scripts/local_execution_manifest.py` — canonical JSON and SHA-256/identity generation.
- `scripts/generate_local_execution_corpus.py` — deterministic synthetic conformance vectors.
- `conformance/local-execution/v1/manifest.json`
- `conformance/local-execution/v1/vectors.json`
- `tests/test_local_execution_generator.py`
- `tests/test_local_execution_corpus.py`
- `tests/test_api_portable_boundary.py`
- `apps/web/app/generated/localExecution.ts` — generated, never hand-edited.
- `apps/web/app/generated/localExecution.meta.json`
- `apps/web/tests/unit/localExecutionConformance.spec.ts`

### Web local execution

- `apps/web/app/lib/storage/indexeddb.ts` — DB v2, execution receipts, create-only insert, atomic apply/delete.
- `apps/web/app/lib/execution/canonicalJson.ts`
- `apps/web/app/lib/execution/localExecutor.ts`
- `apps/web/app/lib/execution/contract.ts`
- `apps/web/app/composables/useCommandQueue.ts` — compatibility network fallback only.
- `apps/web/app/composables/useLocalExecution.ts`
- `apps/web/app/composables/useCaseApi.ts`
- `apps/web/app/pages/index.vue`
- `apps/web/app/pages/cases/[id].vue`
- `apps/web/app/lib/i18n/ru.ts`
- `apps/web/app/lib/i18n/en.ts`

### API compatibility

- `apps/api/mind_detective_api/contracts.py`
- `apps/api/mind_detective_api/execution_contract.py`
- `apps/api/mind_detective_api/commands.py` — transport validation/delegation only.
- `apps/api/mind_detective_api/checklist.py` — deterministic proposal delegation only.
- `apps/api/mind_detective_api/app.py`
- `apps/api/tests/test_execution_contract.py`
- `apps/api/tests/test_commands.py`

### Repository contracts/release

- `docs/REQUIREMENTS.md`, `docs/CONTRACT_MATRIX.json`, `docs/EVAL_TOKEN_REGISTRY.json`
- `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md`, `docs/PRIVACY.md`, `docs/PRODUCT_EVALUATION.md`
- `docs/adr/013-portable-local-execution-kernel.md`
- `docs/adr/014-offline-execution-receipts.md`
- `docs/adr/015-execution-contract-skew.md`
- `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md`
- `.github/workflows/ci.yml`
- `.github/releases/0.3.0.md`, `.github/releases/release.json`

---

### Task 1: Define the portable execution contract

**Files:** create `portable_contract.py` and `test_portable_contract.py`.

**Produces:** `LOCAL_EXECUTION_CONTRACT="mind-detective-local-execution/v1"`, `GENERATOR_VERSION="local-execution-generator/v1"`, `SUPPORTED_CASE_SCHEMAS=("mind-detective-case/v2",)`, exact supported command tuple and stable local-execution errors.

- [ ] Write a failing exact-value test for all constants.
- [ ] Run `python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_contract.py' -v`; expect import failure.
- [ ] Implement immutable constants only; no Web/API/provider imports.
- [ ] Rerun; expect PASS.
- [ ] Commit `feat: define local execution contract`.

### Task 2: Define certified portable intrinsics

**Files:** create `portable_intrinsics.py`, `test_portable_intrinsics.py`.

**Produces:** `clone_json`, `unicode_casefold`, `split_python_whitespace`, `compare_python_strings`, `PortableKernelError`, `portable_error`.

- [ ] RED tests must include `Straße→strasse`, Cyrillic `ЁЖ→ёж`, NBSP/U+2028 whitespace splitting, supplementary-plane string ordering, nested clone non-aliasing and coded errors.
- [ ] Run intrinsic test file; expect failure.
- [ ] Implement Python reference behavior (`copy.deepcopy`, `str.casefold`, `str.split`, Python string ordering).
- [ ] Rerun; expect PASS.
- [ ] Commit `feat: define portable execution intrinsics`.

### Task 3: Implement all deterministic JSON transitions

**Files:** create/modify `portable_kernel.py`, `test_portable_kernel.py`.

**Produces:** `create_case(...)` and `apply_command(case, command)` for the exact supported command set.

- [ ] RED tests cover Case v2 creation, lifecycle, mode, user statement/journal, exact search-suggestion candidate creation, `reported_check`, refinement, rejection feedback, stale command, terminal state, malformed payload and forbidden probability/POD/belief keys.
- [ ] Run portable-kernel tests; expect unsupported/missing failures.
- [ ] Implement only with certified intrinsics and explicit JSON operations; target normalization uses Python-equivalent casefold/whitespace semantics and explicit `ё→е`.
- [ ] Rerun; expect PASS.
- [ ] Commit `feat: add portable deterministic transitions`.

### Task 4: Remove duplicate controller/API command semantics

**Files:** modify `controller.py`, `store.py`, API `commands.py`; create controller parity and API boundary tests.

- [ ] RED controller parity: every supported public controller transition matches portable full Case output/error.
- [ ] RED API AST boundary: `commands.py` must no longer construct `Statement`, `CandidateCheck`, `SearchCheck`, `ActionFeedback` or `JournalEntry` for supported transitions.
- [ ] Run both tests; expect API boundary failure on current `0.2.0` code.
- [ ] Delegate through portable kernel/controller facade while retaining Pydantic/HTTP validation.
- [ ] Run full plugin + API suites and boundary test; expect PASS.
- [ ] Commit `refactor: centralize deterministic command semantics`.

### Task 5: Centralize planner/checklist proposal semantics

**Files:** modify portable kernel, `planner.py`, API `checklist.py`; add portable planner tests and boundary coverage.

- [ ] RED tests cover safe filter, urgency→basis→route→check-state→effort ordering, Python-equivalent ID tiebreak, rejection exclusion, partial/inaccessible clarification and neutral empty state.
- [ ] Run portable/API checklist tests; expect missing portable planner failure.
- [ ] Implement `select_next_action_json` and `build_checklist_proposal_json`; typed planner/API become facades.
- [ ] Rerun plugin/API/boundary suites; expect PASS.
- [ ] Commit `refactor: centralize deterministic proposal semantics`.

### Task 6: Enforce restricted AST and intrinsic allowlist

**Files:** create `scripts/local_execution_ast.py`, `tests/test_local_execution_generator.py`.

- [ ] RED validator snippets reject async/classes/decorators/reflection/dynamic imports/fs/network/env/random/time/floats/unrecognized calls; real kernel must be accepted.
- [ ] Run generator tests; expect missing validator failure.
- [ ] Implement exhaustive AST/call allowlist with stable `PortableSourceError(code,line,detail)`.
- [ ] Rerun; expect PASS.
- [ ] Commit `test: enforce portable kernel subset`.

### Task 7: Generate TypeScript and complete execution identity

**Files:** create generator/manifest scripts and generated TS/meta artifacts.

**Produces metadata:** `version`, `kernel_sha256`, `generated_sha256`, `generator_version`, `case_schemas`.

- [ ] RED tests require byte-deterministic output, generated-file header, certified intrinsic results and absence of `eval`, `new Function`, dynamic remote imports, provider/network/clock/random calls.
- [ ] Run RED.
- [ ] Implement emitter plus generated intrinsic prelude; `generated_sha256` lives only in meta JSON, avoiding a hash cycle.
- [ ] Generate twice; require identical SHA-256 values and GREEN tests.
- [ ] Commit `build: generate certified local executor`.

### Task 8: Add identical canonical JSON hashing

**Files:** Python manifest helper, Web `canonicalJson.ts`, shared fixture, Python/Vitest tests.

- [ ] Commit fixture vectors with Cyrillic, casefold-sensitive strings, emoji/supplementary-plane characters, nested key ordering, empty structures and null.
- [ ] RED cross-runtime tests assert exact canonical strings/hashes.
- [ ] Implement recursive key sorting using certified Python ordering and WebCrypto SHA-256.
- [ ] Run Python + Vitest; require exact equality.
- [ ] Commit `feat: add cross-runtime canonical hashing`.

### Task 9: Generate committed differential corpus

**Files:** corpus generator, manifest/vectors JSON, corpus tests.

- [ ] RED coverage test requires every command, planner boundary, unsafe exclusion, repeated/partial/inaccessible checks, rejection, terminal lifecycle, Unicode intrinsic edges, stale/forbidden fields and deterministic retry.
- [ ] Implement build-time generator with fixed `random.Random(303001)` and stable vector ordering; expected results come only from Python reference execution.
- [ ] Generate twice and require byte-identical corpus hashes.
- [ ] Run corpus tests; require PASS.
- [ ] Commit `test: add local execution conformance corpus`.

### Task 10: Certify generated TS against every Python vector

**Files:** `localExecutionConformance.spec.ts`, Vitest config, CI.

- [ ] RED Vitest iterates every vector and compares full canonical result or exact error code.
- [ ] Fix only portable source/emitter until GREEN; never hand-edit expected TS results.
- [ ] CI regenerates TS/meta/corpus and runs `git diff --exit-code -- apps/web/app/generated conformance/local-execution/v1`.
- [ ] Add generated conformance Vitest gate.
- [ ] Commit `test: certify generated executor parity`.

### Task 11: Upgrade IndexedDB atomically

**Files:** modify `indexeddb.ts`; create `localExecutor.ts`, unit/E2E receipt tests.

**DB v2:** add `execution_receipts` keyed by `command_id` with `case_id` index.

- [ ] RED tests cover v1→v2 data preservation, atomic Case+receipt abort semantics, selected Case+receipt deletion, create-only insertion, matching create identity and `MD_WEB_CASE_ID_CONFLICT`.
- [ ] Implement one readwrite transaction for Case+receipt and `objectStore.add` for first Case creation.
- [ ] Run unit + Playwright tests; require PASS.
- [ ] Commit `feat: persist local execution atomically`.

### Task 12: Make command application idempotent

**Files:** modify local executor/storage tests.

- [ ] RED same `command_id`+same input hash returns persisted result and one receipt; same id+different input hash raises `MD_WEB_COMMAND_ID_CONFLICT`.
- [ ] Implement receipt lookup before generated execution; receipt stores hashes/IDs only.
- [ ] Rerun; require PASS.
- [ ] Commit `feat: make local commands idempotent`.

### Task 13: Switch production creation/mutations to local-first

**Files:** create `useLocalExecution.ts`; modify command queue, index page, active-case page; unit/E2E tests.

- [ ] RED E2E aborts `/case/create` and `/case/command`, then completes create→mode→statement→check/refine→reject→pause/resume→close. Also test duplicate/conflicting Case creation identity.
- [ ] Implement `createCase` and `sendCommand` through generated executor + atomic IndexedDB.
- [ ] Keep network queue only as explicit unsupported-contract compatibility fallback.
- [ ] Run offline flow plus existing create/check/close suites; require PASS.
- [ ] Commit `feat: execute deterministic web actions locally`.

### Task 14: Add local checklist proposals and assistant offline fallback

**Files:** modify local execution/page/i18n/eval; create offline proposal E2E.

- [ ] RED assistant-arm test aborts proposal API and expects local deterministic next action + reviewed offline indicator; browser `online` event must not replay offline history.
- [ ] Implement checklist arm local path and assistant offline fallback; add metadata-only `assistant_offline_fallback` evaluation event.
- [ ] Run Chromium+WebKit; require PASS.
- [ ] Commit `feat: add offline deterministic proposal fallback`.

### Task 15: Add full execution identity/skew handling

**Files:** create API execution contract module and Web contract helper; modify API/Web request contracts, i18n and tests.

- [ ] RED API matrix mutates each of contract version/kernel hash/generated hash/generator version independently; every mismatch must return 409 `MD_WEB_EXECUTION_CONTRACT_MISMATCH` before LiteLLM call.
- [ ] RED Web test shows update/reconnect guidance while local deterministic command still succeeds.
- [ ] Implement `GET /api/v1/execution/contract` and full assistant request identity validation.
- [ ] Run API + Web tests; require PASS.
- [ ] Commit `feat: fail closed on execution contract skew`.

### Task 16: Certify complete offline PWA vertical slice

**Files:** modify PWA config/tests; create `offline-vertical-slice.spec.ts`.

- [ ] RED: load app once, switch browser offline, complete create→mode→statement→proposal→check→next proposal→refine→reject→pause/resume→close→export→reopen with all API calls failing.
- [ ] Fix only proven residual network/PWA gaps; keep `/api/**` out of Workbox runtime cache and background sync disabled.
- [ ] Run full Vitest, Nuxt build and all Playwright Chromium/WebKit tests; require PASS.
- [ ] Commit `test: certify complete offline search workflow`.

### Task 17: Trace requirements, docs, CI and prepare `0.3.0`

**Files:** requirements/matrix/eval registry, architecture/privacy/evaluation, ADR 013–015, RU/EN README+CHANGELOG, CI, release notes/manifest, plugin/marketplace descriptors and contract/release tests.

**Stable requirements include:** `MD-OFFLINE-REQ-KERNEL-01`, `GENERATOR-01`, `CONFORMANCE-01`, `API-01`, `INTRINSIC-01`, `LOCAL-01`, `ATOMIC-01`, `IDEMPOTENCE-01`, `CREATE-01`, `PROPOSAL-01`, `ASSISTANT-01`, `IDENTITY-01`, `SKEW-01`, `PRIVACY-01`, `PWA-01`, `RELEASE-01`.

- [ ] Write RED exact-selector and version-parity tests expecting `0.3.0` while current declarations remain `0.2.0`.
- [ ] Run `test_contract_matrix.py`, `test_release_contract.py`, `test_repository_contracts.py`; require intended RED.
- [ ] Update docs/ADRs/descriptors and manifest to repository `0.3.0` + plugin `mind-detective-v0.3.0`; preserve `0.1.0`/`0.2.0` published notes unchanged.
- [ ] Run complete verification:

```bash
python scripts/validate_repo.py
python scripts/check_reference_freshness.py --strict
python scripts/generate_local_execution.py
python scripts/generate_local_execution_corpus.py
git diff --exit-code -- apps/web/app/generated conformance/local-execution/v1
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
PYTHONPATH=plugins/mind-detective:apps/api python -m unittest discover -s apps/api/tests -v
ruff check .
mypy --strict scripts tests plugins/mind-detective/scripts plugins/mind-detective/tests apps/api/mind_detective_api apps/api/tests
pnpm install --frozen-lockfile
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

Expected: all PASS and zero generated/corpus drift.

- [ ] Commit `release: prepare MIND Detective 0.3.0`.
- [ ] Preserve human gates: separate implementation PR → exact-head CI → explicit merge authorization → expected-head merge → exact post-merge main CI → explicit publication authorization/full SHA → canonical `publish-current-release.yml` only → immutable exact-tag verification.

---

## Plan Self-Review

### Spec coverage

- Portable authority + no API third reducer: Tasks 1–5.
- Certified Python-observable intrinsics: Tasks 2, 6–8.
- Restricted codegen source: Task 6.
- Deterministic artifact + full identity: Task 7.
- Canonical hashing: Task 8.
- Differential corpus/parity: Tasks 9–10.
- Atomic Case+receipt/create-only persistence: Task 11.
- Command idempotence: Task 12.
- Offline create/all deterministic mutations: Task 13.
- Local proposals + assistant no-replay fallback: Task 14.
- Full contract skew identity: Task 15.
- End-to-end offline PWA/privacy: Task 16.
- Requirements/docs/release governance: Task 17.

### Placeholder scan

No `TBD`, `TODO`, `implement later`, Python Ellipsis placeholders, undefined command names, approximate JS domain-semantic substitutions, or instructions to manually edit generated TypeScript remain.

### Type and authority consistency

- `Case v2` remains unchanged.
- Portable kernel consumes/emits JSON-compatible Cases and uses certified intrinsics.
- `CaseController`, API command adapter and API checklist adapter all converge on portable semantics.
- Generated TypeScript is derived, not authoritative.
- Receipts use canonical hashes defined before idempotence.
- Offline Case creation is create-only and separate from command receipts.
- Assistant history is never replayed after reconnect.
- Compatibility compares contract + kernel + generated artifact + generator identities, not mutable branch/repository identity.

## Execution Handoff

Implementation occurs on a separate production branch/PR only after the design documentation branch passes its human merge gate. At execution time use an isolated worktree when available and execute task-by-task with `superpowers:subagent-driven-development` or `superpowers:executing-plans`. Approval of this plan is not production merge or release authorization.
