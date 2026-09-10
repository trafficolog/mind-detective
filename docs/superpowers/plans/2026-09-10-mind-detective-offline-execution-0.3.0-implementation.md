# MIND Detective 0.3.0 Offline Deterministic Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the already-loaded MIND Detective PWA complete deterministic lost-item-search workflows without network round-trips by generating a TypeScript local executor from a restricted Python transition kernel and certifying exact parity with the Python reference runtime.

**Architecture:** `CaseController` remains the public Python domain boundary, but browser-eligible deterministic semantics move into a pure JSON-compatible `PortableTransitionKernel`. A stdlib-only generator emits `apps/web/app/generated/localExecution.ts`; CI certifies it with canonical hashing and a deterministic Python↔TypeScript conformance corpus. The Web app commits `Case v2 + execution receipt` atomically in IndexedDB, uses the generated checklist proposal path offline, and only calls LiteLLM for new assistant proposals while online and execution-contract-compatible.

**Tech Stack:** Python 3.10/3.13 stdlib-first plugin core; Python `ast`/`hashlib`/`json` generator tooling; generated TypeScript; Nuxt 4.5.2; Vue; IndexedDB; Vitest 5.0.0; Playwright 1.63.0; existing FastAPI + LiteLLM/OpenAI-compatible transport; existing GitHub Actions/release publisher.

**Spec:** `docs/superpowers/specs/2026-09-10-mind-detective-offline-execution-0.3.0-design.md`

## Global Constraints

- Release target is repository `0.3.0` and plugin `mind-detective 0.3.0`.
- Existing immutable `0.1.0` and `0.2.0` releases/tags remain untouched.
- `mind-detective-case/v2` remains the canonical persisted Case schema; no Case v3.
- `CaseController` remains the public Python mutation boundary.
- The browser may execute only code generated from the restricted Python portable kernel; no hand-maintained TypeScript domain reducer is allowed.
- Generated TypeScript is build output and is never manually edited.
- Python remains the reference oracle; every supported generated transition/proposal must match Python output or exact machine error code on the conformance corpus.
- No clocks, randomness, filesystem/network access, environment access, reflection, dynamic imports, model calls, floating-point ranking/probability math, or mutable globals are allowed in the portable kernel.
- IDs and timestamps are supplied by request/command envelopes only.
- Deterministic commands are local-first for a compatible `0.3.0` Web client.
- Case mutation and execution receipt write occur in one IndexedDB transaction.
- Duplicate `command_id` with the same input identity is idempotent; conflicting identity fails with `MD_WEB_COMMAND_ID_CONFLICT`.
- Offline assistant mode uses deterministic checklist guidance immediately; offline history is never automatically replayed to LiteLLM after reconnect.
- LiteLLM remains server-side only for newly requested online assistant proposals.
- Execution-contract version/hash mismatch fails assistant/network semantics closed with `MD_WEB_EXECUTION_CONTRACT_MISMATCH` while leaving local certified execution available.
- No accounts, server case DB, cloud sync, background case upload, Pyodide/WASM, Bayesian/POD/probability scoring, cross-case learning, or native app work in `0.3.0`.
- CI retains Python 3.10/3.13, Ruff, strict Mypy, repository/plugin/API tests, frozen pnpm install, Vitest, Nuxt/PWA build, Chromium/WebKit Playwright, secret scan, exact PR-head verification and canonical full-SHA release governance.

---

## File Structure

### Portable domain source

- `plugins/mind-detective/scripts/portable_kernel.py` — JSON-compatible deterministic transitions and checklist proposal semantics.
- `plugins/mind-detective/scripts/portable_contract.py` — contract version, supported commands/schemas and stable error codes.
- `plugins/mind-detective/scripts/controller.py` — public dataclass boundary delegating eligible transitions to the portable kernel.
- `plugins/mind-detective/scripts/planner.py` — existing typed planner retained as compatibility/reference facade over portable planner semantics.
- `plugins/mind-detective/tests/test_portable_kernel.py` — transition parity with existing controller behavior.
- `plugins/mind-detective/tests/test_portable_planner.py` — categorical proposal/planner parity.

### Generator and conformance tooling

- `scripts/local_execution_ast.py` — restricted-AST validator.
- `scripts/generate_local_execution.py` — deterministic Python→TypeScript emitter.
- `scripts/local_execution_manifest.py` — SHA-256/contract metadata generation.
- `scripts/generate_local_execution_corpus.py` — deterministic synthetic conformance vectors.
- `conformance/local-execution/v1/*.json` — committed synthetic vectors and expected Python results/errors.
- `tests/test_local_execution_generator.py` — AST fail-closed and deterministic generation tests.
- `tests/test_local_execution_corpus.py` — corpus shape/coverage/hash tests.
- `apps/web/app/generated/localExecution.ts` — generated executor; do not edit manually.
- `apps/web/app/generated/localExecution.meta.json` — generated contract/hash metadata.
- `apps/web/tests/unit/localExecutionConformance.spec.ts` — generated-TS conformance runner.

### Web local execution

- `apps/web/app/lib/storage/indexeddb.ts` — DB v2 upgrade, execution receipts and atomic apply/delete.
- `apps/web/app/lib/execution/canonicalJson.ts` — TypeScript canonical JSON/SHA-256 helpers.
- `apps/web/app/lib/execution/localExecutor.ts` — generated-executor wrapper and idempotence checks only.
- `apps/web/app/lib/execution/contract.ts` — embedded execution-contract metadata and compatibility checks.
- `apps/web/app/composables/useCommandQueue.ts` — compatibility/network fallback only; no longer primary deterministic path.
- `apps/web/app/composables/useLocalExecution.ts` — local-first command and checklist proposal orchestration.
- `apps/web/app/composables/useCaseApi.ts` — contract metadata and compatible online assistant calls.
- `apps/web/app/pages/index.vue` — offline local Case creation.
- `apps/web/app/pages/cases/[id].vue` — local deterministic mutations/proposals and online assistant fallback boundary.
- `apps/web/app/lib/i18n/ru.ts`, `apps/web/app/lib/i18n/en.ts` — reviewed offline/contract-skew copy.

### API compatibility

- `apps/api/mind_detective_api/contracts.py` — execution contract identity in network requests/responses.
- `apps/api/mind_detective_api/execution_contract.py` — API-side metadata and compatibility validation.
- `apps/api/mind_detective_api/app.py` — `GET /api/v1/execution/contract` and fail-closed assistant mismatch handling.
- `apps/api/tests/test_execution_contract.py` — metadata/mismatch contracts.

### Repository contracts/release

- `docs/REQUIREMENTS.md`, `docs/CONTRACT_MATRIX.json`, `docs/EVAL_TOKEN_REGISTRY.json` — stable `MD-OFFLINE-REQ-*` requirements/selectors.
- `docs/ARCHITECTURE.md`, `docs/ARCHITECTURE.en.md`, `docs/PRIVACY.md`, `docs/PRODUCT_EVALUATION.md` — `0.3.0` architecture/privacy/evaluation documentation.
- `docs/adr/013-portable-local-execution-kernel.md` — source/authority/codegen decision.
- `docs/adr/014-offline-execution-receipts.md` — atomic receipt/idempotence decision.
- `docs/adr/015-execution-contract-skew.md` — installed-PWA/API compatibility decision.
- `README.md`, `README.en.md`, `CHANGELOG.md`, `CHANGELOG.en.md` — RU/EN public release documentation.
- `.github/workflows/ci.yml` — generation-drift + differential-conformance + offline browser gates.
- `.github/releases/0.3.0.md`, `.github/releases/release.json` — declarative release set.

---

### Task 1: Define the portable local-execution contract and fail-closed vocabulary

**Files:**
- Create: `plugins/mind-detective/scripts/portable_contract.py`
- Create: `plugins/mind-detective/tests/test_portable_contract.py`

**Interfaces:**
- `LOCAL_EXECUTION_CONTRACT = "mind-detective-local-execution/v1"`.
- `SUPPORTED_CASE_SCHEMAS = ("mind-detective-case/v2",)`.
- `SUPPORTED_COMMAND_TYPES = ("set_mode", "add_statement", "record_search_check", "refine_search_check", "reject_next_action", "pause", "resume", "close_found", "close_unresolved")`.
- Stable errors include `MD_WEB_STALE_COMMAND`, `MD_WEB_FORBIDDEN_FIELD`, `MD_WEB_COMMAND_PAYLOAD`, `MD_WEB_COMMAND_ID_CONFLICT`, `MD_WEB_EXECUTION_CONTRACT_MISMATCH` plus existing domain errors surfaced by supported transitions.

- [ ] **Step 1: Write the failing contract test**

```python
from scripts.portable_contract import (
    LOCAL_EXECUTION_CONTRACT,
    SUPPORTED_CASE_SCHEMAS,
    SUPPORTED_COMMAND_TYPES,
)


def test_local_execution_v1_contract_is_exact() -> None:
    assert LOCAL_EXECUTION_CONTRACT == "mind-detective-local-execution/v1"
    assert SUPPORTED_CASE_SCHEMAS == ("mind-detective-case/v2",)
    assert SUPPORTED_COMMAND_TYPES == (
        "set_mode", "add_statement", "record_search_check", "refine_search_check",
        "reject_next_action", "pause", "resume", "close_found", "close_unresolved",
    )
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_contract.py' -v`

Expected: FAIL because `portable_contract.py` does not exist.

- [ ] **Step 3: Implement immutable constants only**

Use tuples/frozensets and string constants; do not import FastAPI, Web types, environment variables or model SDKs.

- [ ] **Step 4: Run GREEN**

Run the same command; expected PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/portable_contract.py plugins/mind-detective/tests/test_portable_contract.py
git commit -m "feat: define local execution contract"
```

---

### Task 2: Introduce pure JSON Case creation and lifecycle/mode transitions

**Files:**
- Create: `plugins/mind-detective/scripts/portable_kernel.py`
- Create: `plugins/mind-detective/tests/test_portable_kernel.py`

**Interfaces:**
- `create_case(case_id: str, item_label: str, now: str) -> dict[str, object]`.
- `apply_command(case: dict[str, object], command: dict[str, object]) -> dict[str, object]`.
- Initial supported operations in this task: `set_mode`, `pause`, `resume`, `close_found`, `close_unresolved`.
- Input is copied before mutation; caller input remains byte-semantically unchanged.

- [ ] **Step 1: Write RED transition tests**

```python
def test_portable_create_case_matches_case_v2_shape() -> None:
    case = create_case("case-1", "ключи", "2026-09-10T18:00:00Z")
    assert case["schema"] == "mind-detective-case/v2"
    assert case["lifecycle"] == "active"
    assert case["current_mode"] == "unselected"
    assert case["statements"] == []
    assert case["interaction_journal"] == []


def test_pause_does_not_mutate_input() -> None:
    source = create_case("case-1", "keys", "2026-09-10T18:00:00Z")
    before = json.loads(json.dumps(source))
    result = apply_command(source, command("pause", now="2026-09-10T18:01:00Z", expected=source["updated_at"]))
    assert source == before
    assert result["lifecycle"] == "paused"
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_portable_kernel.py' -v`

Expected: FAIL because portable functions are missing.

- [ ] **Step 3: Implement pure JSON transitions**

Use `copy.deepcopy`, explicit string comparisons and explicit field writes. Check `expected_updated_at` before dispatch. Reject terminal mutation before any result copy is returned.

- [ ] **Step 4: Run GREEN**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/portable_kernel.py plugins/mind-detective/tests/test_portable_kernel.py
git commit -m "feat: add portable lifecycle transitions"
```

---

### Task 3: Add portable statement, candidate, search-check and feedback transitions

**Files:**
- Modify: `plugins/mind-detective/scripts/portable_kernel.py`
- Modify: `plugins/mind-detective/tests/test_portable_kernel.py`

**Interfaces:**
- Extend `apply_command()` for `add_statement`, `record_search_check`, `refine_search_check`, `reject_next_action`.
- Search-mode `search_suggestion` candidate id is `candidate-{statement_id}` and target is exactly `original_text`.
- One-tap search method default is `reported_check`.
- `inaccessible` cannot be a new Web method; inaccessible parts remain separate.
- Candidate state changes only when `SearchCheck.based_on` contains that candidate id.

- [ ] **Step 1: Write RED edge tests**

```python
def test_search_suggestion_creates_exact_user_supported_candidate() -> None:
    case = search_case()
    result = apply_command(case, add_statement_command(
        statement_id="stmt-1",
        statement_type="search_suggestion",
        text="карман синего рюкзака",
    ))
    assert result["candidates"][0]["id"] == "candidate-stmt-1"
    assert result["candidates"][0]["target"] == "карман синего рюкзака"
    assert result["candidates"][0]["based_on"] == ["stmt-1"]


def test_reported_check_marks_related_candidate_checked() -> None:
    case = case_with_candidate("candidate-stmt-1")
    result = apply_command(case, check_command("candidate-stmt-1"))
    assert result["search_checks"][-1]["method"] == "reported_check"
    assert result["candidates"][0]["check_state"] == "checked"
```

- [ ] **Step 2: Run RED**

Run the portable-kernel test module; expected FAIL on unsupported commands.

- [ ] **Step 3: Implement explicit JSON helpers**

Add pure helpers for required-string/list validation, target normalization for exact duplicate suppression, journal append, candidate update, refinement and categorical feedback. Do not use regex/NLP extraction for candidate targets.

- [ ] **Step 4: Run GREEN**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/portable_kernel.py plugins/mind-detective/tests/test_portable_kernel.py
git commit -m "feat: add portable search transitions"
```

---

### Task 4: Make `CaseController` delegate eligible semantics to the portable kernel

**Files:**
- Modify: `plugins/mind-detective/scripts/controller.py`
- Modify: `plugins/mind-detective/scripts/store.py`
- Modify: `plugins/mind-detective/tests/test_controller.py`
- Create: `plugins/mind-detective/tests/test_controller_portable_parity.py`

**Interfaces:**
- Public `CaseController` method signatures do not change.
- Controller serializes current `Case`, constructs the same deterministic command payload, invokes portable kernel, and deserializes the result for eligible transitions.
- Methods not part of local execution contract remain existing typed Python implementations.

- [ ] **Step 1: Write RED parity test**

```python
def test_controller_pause_result_equals_portable_result() -> None:
    controller_case = self.controller.pause(self.case, "2026-09-10T18:05:00Z")
    portable = apply_command(case_to_dict(self.case), pause_command(self.case.updated_at))
    self.assertEqual(case_to_dict(controller_case), portable)
```

Add one parity vector per supported command, including failure code parity.

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s plugins/mind-detective/tests -p 'test_controller_portable_parity.py' -v`

Expected: FAIL until controller delegation is introduced.

- [ ] **Step 3: Delegate without changing public behavior**

Use small private conversion helpers; do not import API Pydantic contracts into plugin core.

- [ ] **Step 4: Run full plugin regression**

Run: `python -m unittest discover -s plugins/mind-detective/tests -v`

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/controller.py plugins/mind-detective/scripts/store.py plugins/mind-detective/tests
git commit -m "refactor: delegate web-safe transitions to portable kernel"
```

---

### Task 5: Move deterministic planner/checklist proposal semantics into the portable kernel

**Files:**
- Modify: `plugins/mind-detective/scripts/portable_kernel.py`
- Modify: `plugins/mind-detective/scripts/planner.py`
- Modify: `apps/api/mind_detective_api/checklist.py`
- Create: `plugins/mind-detective/tests/test_portable_planner.py`
- Modify: `apps/api/tests/test_checklist_proposals.py`

**Interfaces:**
- `select_next_action_json(candidates: list[dict[str, object]], rejected_ids: list[str]) -> dict[str, object] | None`.
- `build_checklist_proposal_json(case: dict[str, object], mode: str) -> dict[str, object]`.
- Planner order is exact: safe filter → urgency → basis → route → check state → effort → id.
- Existing `planner.select_next_action()` and API checklist facade delegate/convert rather than maintain separate ranking logic.

- [ ] **Step 1: Write RED categorical-boundary tests**

```python
def test_portable_planner_prefers_episode_before_better_route_habit() -> None:
    chosen = select_next_action_json([
        candidate("habit-direct", basis="habit", route="direct"),
        candidate("episode-none", basis="episode", route="none"),
    ], [])
    assert chosen["candidate_id"] == "episode-none"


def test_rejected_candidate_is_excluded() -> None:
    chosen = select_next_action_json([candidate("a"), candidate("b")], ["a"])
    assert chosen["candidate_id"] == "b"
```

- [ ] **Step 2: Run RED**

Run portable planner + API checklist tests; expected FAIL on missing portable functions.

- [ ] **Step 3: Implement one categorical planner source**

Use tuple/list categorical order constants and deterministic ID tiebreak. No arithmetic score.

- [ ] **Step 4: Run GREEN across plugin + API checklist suites**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add plugins/mind-detective/scripts/portable_kernel.py plugins/mind-detective/scripts/planner.py plugins/mind-detective/tests/test_portable_planner.py apps/api/mind_detective_api/checklist.py apps/api/tests/test_checklist_proposals.py
git commit -m "refactor: centralize deterministic proposal semantics"
```

---

### Task 6: Enforce the restricted portable-kernel Python subset

**Files:**
- Create: `scripts/local_execution_ast.py`
- Create: `tests/test_local_execution_generator.py`

**Interfaces:**
- `validate_portable_source(path: Path) -> None`.
- Raises `PortableSourceError(code, line, detail)`.
- Reject at minimum: imports inside kernel other than approved stdlib modules, `with`, `try`, `raise` of arbitrary dynamic types, comprehensions not supported by emitter, lambdas, generators, async/await, class definitions, decorators, reflection, `eval`, `exec`, `globals`, `locals`, `getattr`, `setattr`, filesystem/network/env/random/time calls, floating constants and unapproved helper calls.

- [ ] **Step 1: Write RED validator tests**

```python
def test_rejects_randomness() -> None:
    source = "def f():\n    return random.random()\n"
    with self.assertRaisesRegex(PortableSourceError, "MD_CODEGEN_FORBIDDEN_CALL"):
        validate_source_text(source)


def test_accepts_current_portable_kernel() -> None:
    validate_portable_source(ROOT / "plugins/mind-detective/scripts/portable_kernel.py")
```

- [ ] **Step 2: Run RED**

Run: `python -m unittest discover -s tests -p 'test_local_execution_generator.py' -v`

Expected: FAIL because validator does not exist.

- [ ] **Step 3: Implement an explicit AST allowlist**

Walk every AST node and every `Call`; unsupported syntax fails closed with stable code and line number. Do not silently skip unknown nodes.

- [ ] **Step 4: Run GREEN**

Expected: PASS against both synthetic forbidden snippets and the real kernel.

- [ ] **Step 5: Commit**

```bash
git add scripts/local_execution_ast.py tests/test_local_execution_generator.py
git commit -m "test: enforce portable kernel subset"
```

---

### Task 7: Generate deterministic TypeScript and contract metadata

**Files:**
- Create: `scripts/local_execution_manifest.py`
- Create: `scripts/generate_local_execution.py`
- Create: `apps/web/app/generated/localExecution.ts`
- Create: `apps/web/app/generated/localExecution.meta.json`
- Modify: `tests/test_local_execution_generator.py`

**Interfaces:**
- `generate_typescript(source_path: Path) -> str`.
- `build_execution_metadata(source_bytes: bytes, generated_bytes: bytes) -> dict[str, object]`.
- Generated header includes contract version, kernel SHA-256, generator schema/version and `GENERATED FILE — DO NOT EDIT`.
- Generation is byte-deterministic on Python 3.10 and 3.13.

- [ ] **Step 1: Write RED determinism tests**

```python
def test_generation_is_byte_deterministic() -> None:
    first = generate_typescript(KERNEL)
    second = generate_typescript(KERNEL)
    self.assertEqual(first.encode(), second.encode())
    self.assertIn("GENERATED FILE — DO NOT EDIT", first)


def test_metadata_uses_sha256_prefixed_hex() -> None:
    meta = build_execution_metadata(b"kernel", b"generated")
    self.assertRegex(str(meta["kernel_sha256"]), r"^sha256:[0-9a-f]{64}$")
```

- [ ] **Step 2: Run RED**

Expected: FAIL because generator/manifest do not exist.

- [ ] **Step 3: Implement the emitter over the validated AST subset**

Emit plain deterministic TypeScript functions and literal objects/arrays. Generated code must contain no `eval`, `new Function`, dynamic import or runtime code generation.

- [ ] **Step 4: Generate artifacts and rerun tests**

```bash
python scripts/generate_local_execution.py
python -m unittest discover -s tests -p 'test_local_execution_generator.py' -v
```

Expected: PASS and a clean second generation.

- [ ] **Step 5: Commit**

```bash
git add scripts/local_execution_manifest.py scripts/generate_local_execution.py apps/web/app/generated tests/test_local_execution_generator.py
git commit -m "build: generate certified local executor"
```

---

### Task 8: Define canonical JSON hashing identically in Python and TypeScript

**Files:**
- Modify: `scripts/local_execution_manifest.py`
- Create: `apps/web/app/lib/execution/canonicalJson.ts`
- Create: `tests/fixtures/local-execution/canonical-json.json`
- Create: `apps/web/tests/unit/canonicalJson.spec.ts`
- Modify: `tests/test_local_execution_generator.py`

**Interfaces:**
- Python `canonical_json_bytes(value: object) -> bytes`.
- TypeScript `canonicalJson(value: unknown) -> string`.
- TypeScript `sha256Canonical(value: unknown) -> Promise<string>` returns `sha256:<hex>`.
- Objects sort keys recursively; arrays preserve order; UTF-8 text is preserved without NFC/NFD rewriting; separators are compact; booleans/null use JSON spelling.

- [ ] **Step 1: Commit exact cross-language fixture vectors**

Fixture includes Cyrillic `ё/е`, English, punctuation, emoji, nested keys, empty arrays/objects and null.

- [ ] **Step 2: Write RED Python + Vitest tests**

Python and TS tests assert the same exact canonical strings and SHA-256 values from the fixture.

- [ ] **Step 3: Run RED**

```bash
python -m unittest discover -s tests -p 'test_local_execution_generator.py' -v
pnpm --dir apps/web exec vitest run tests/unit/canonicalJson.spec.ts
```

Expected: TS test FAIL before helper exists.

- [ ] **Step 4: Implement canonicalizers and rerun GREEN**

Expected: identical fixture outputs in both runtimes.

- [ ] **Step 5: Commit**

```bash
git add scripts/local_execution_manifest.py apps/web/app/lib/execution/canonicalJson.ts tests/fixtures/local-execution/canonical-json.json apps/web/tests/unit/canonicalJson.spec.ts tests/test_local_execution_generator.py
git commit -m "feat: add cross-runtime canonical hashing"
```

---

### Task 9: Build the committed differential conformance corpus

**Files:**
- Create: `scripts/generate_local_execution_corpus.py`
- Create: `conformance/local-execution/v1/manifest.json`
- Create: `conformance/local-execution/v1/vectors.json`
- Create: `tests/test_local_execution_corpus.py`

**Interfaces:**
- Corpus vector fields: `id`, `operation`, `input_case`, `request`, `expected_result`, `expected_error_code`.
- Exactly one of `expected_result` or `expected_error_code` is non-null.
- Generator seed is fixed as integer `303001` and recorded in manifest.
- Expected results are computed only by Python portable/reference functions.

- [ ] **Step 1: Write RED corpus-contract tests**

```python
def test_corpus_covers_all_commands_and_required_failures() -> None:
    corpus = load_vectors()
    operations = {vector["operation"] for vector in corpus}
    self.assertTrue(set(SUPPORTED_COMMAND_TYPES).issubset(operations))
    errors = {vector["expected_error_code"] for vector in corpus if vector["expected_error_code"]}
    self.assertIn("MD_WEB_STALE_COMMAND", errors)
    self.assertIn("MD_WEB_FORBIDDEN_FIELD", errors)
```

Also require planner category boundaries, unsafe exclusion, partial/inaccessible, rejection, terminal lifecycle, RU/EN/Unicode and deterministic retry vectors.

- [ ] **Step 2: Run RED**

Run corpus test; expected FAIL because corpus files/generator do not exist.

- [ ] **Step 3: Implement deterministic corpus generator**

Use `random.Random(303001)` only in the build-time corpus generator, never portable runtime. Stable-sort vectors by `id` before writing JSON.

- [ ] **Step 4: Generate twice and verify byte equality**

```bash
python scripts/generate_local_execution_corpus.py
sha256sum conformance/local-execution/v1/vectors.json
python scripts/generate_local_execution_corpus.py
sha256sum conformance/local-execution/v1/vectors.json
python -m unittest discover -s tests -p 'test_local_execution_corpus.py' -v
```

Expected: hashes identical; tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_local_execution_corpus.py conformance/local-execution/v1 tests/test_local_execution_corpus.py
git commit -m "test: add local execution conformance corpus"
```

---

### Task 10: Certify generated TypeScript against every Python corpus vector

**Files:**
- Create: `apps/web/tests/unit/localExecutionConformance.spec.ts`
- Modify: `apps/web/vitest.config.ts`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Vitest imports generated `applyCommand`, `createCase` and `buildChecklistProposal` functions.
- Every vector compares full structured result after canonical JSON normalization or exact error `code`.
- CI regenerates TypeScript and corpus and requires clean git diff before Vitest.

- [ ] **Step 1: Write RED generated-executor conformance test**

```ts
for (const vector of vectors) {
  it(vector.id, () => {
    if (vector.expected_error_code) {
      expect(() => runVector(vector)).toThrowError(expect.objectContaining({ code: vector.expected_error_code }))
    } else {
      expect(canonicalJson(runVector(vector))).toBe(canonicalJson(vector.expected_result))
    }
  })
}
```

- [ ] **Step 2: Run RED before CI wiring fixes**

Run: `pnpm --dir apps/web exec vitest run tests/unit/localExecutionConformance.spec.ts`

Expected: FAIL on any generator/runtime mismatch; do not adjust expected vectors in TS.

- [ ] **Step 3: Fix generator/portable source until exact parity is GREEN**

Only Python portable source or emitter may change semantic output. Generated file is always regenerated, never hand-edited.

- [ ] **Step 4: Add CI generation-drift gates**

CI commands:

```bash
python scripts/generate_local_execution.py
python scripts/generate_local_execution_corpus.py
git diff --exit-code -- apps/web/app/generated conformance/local-execution/v1
pnpm --dir apps/web exec vitest run tests/unit/localExecutionConformance.spec.ts
```

- [ ] **Step 5: Commit**

```bash
git add apps/web/tests/unit/localExecutionConformance.spec.ts apps/web/vitest.config.ts .github/workflows/ci.yml
git commit -m "test: certify generated executor parity"
```

---

### Task 11: Upgrade IndexedDB for atomic Case + execution receipts

**Files:**
- Modify: `apps/web/app/lib/storage/indexeddb.ts`
- Create: `apps/web/app/lib/execution/localExecutor.ts`
- Create: `apps/web/tests/unit/localExecutor.spec.ts`
- Create: `apps/web/tests/e2e/offline-receipts.spec.ts`

**Interfaces:**
- IndexedDB version increments from `1` to `2`.
- Add store `execution_receipts` keyed by `command_id`; add `case_id` index for delete cleanup.
- `ExecutionReceipt`: `command_id`, `case_id`, `contract_version`, `input_case_hash`, `output_case_hash`, `applied_at`.
- `applyCaseAndReceipt(caseValue, receipt) -> Promise<void>` uses one `readwrite` transaction spanning `cases` and `execution_receipts`.
- `deleteCaseAndReceipts(caseId) -> Promise<void>` deletes selected Case and all matching receipts atomically.

- [ ] **Step 1: Write RED unit/browser tests**

Assert DB upgrade preserves existing Case records; simulated transaction abort leaves prior Case and no receipt; delete removes only selected case/receipts.

- [ ] **Step 2: Run RED**

```bash
pnpm --dir apps/web exec vitest run tests/unit/localExecutor.spec.ts
pnpm --dir apps/web exec playwright test tests/e2e/offline-receipts.spec.ts
```

Expected: FAIL before DB v2 APIs exist.

- [ ] **Step 3: Implement atomic storage and wrapper**

The wrapper may validate contract/idempotence and call generated functions, but it must not contain command-specific domain mutation branches.

- [ ] **Step 4: Run GREEN**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/app/lib/storage/indexeddb.ts apps/web/app/lib/execution/localExecutor.ts apps/web/tests/unit/localExecutor.spec.ts apps/web/tests/e2e/offline-receipts.spec.ts
git commit -m "feat: persist local execution atomically"
```

---

### Task 12: Enforce command-id idempotence and conflict handling

**Files:**
- Modify: `apps/web/app/lib/execution/localExecutor.ts`
- Modify: `apps/web/app/lib/storage/indexeddb.ts`
- Modify: `apps/web/tests/unit/localExecutor.spec.ts`
- Modify: `apps/web/tests/e2e/offline-receipts.spec.ts`

**Interfaces:**
- `executeLocalCommand(caseValue, envelope) -> Promise<CaseV2>`.
- Existing matching receipt + same input hash returns the already persisted Case without re-executing.
- Existing receipt + different input hash throws error with `code="MD_WEB_COMMAND_ID_CONFLICT"`.
- Retry reuses original envelope.

- [ ] **Step 1: Write RED idempotence tests**

```ts
it('returns persisted result for duplicate command id and same input identity', async () => {
  const first = await executor.executeLocalCommand(caseFixture, commandFixture)
  const second = await executor.executeLocalCommand(caseFixture, commandFixture)
  expect(second).toEqual(first)
  expect(await receipts.countForCase(caseFixture.case_id)).toBe(1)
})
```

Add conflicting-input case expecting exact machine code.

- [ ] **Step 2: Run RED**

Expected: FAIL until receipt lookup semantics exist.

- [ ] **Step 3: Implement hash/receipt lookup before execution**

Do not duplicate command payload into the receipt.

- [ ] **Step 4: Run GREEN**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/app/lib/execution/localExecutor.ts apps/web/app/lib/storage/indexeddb.ts apps/web/tests/unit/localExecutor.spec.ts apps/web/tests/e2e/offline-receipts.spec.ts
git commit -m "feat: make local commands idempotent"
```

---

### Task 13: Switch deterministic Web mutations and Case creation to local-first execution

**Files:**
- Create: `apps/web/app/composables/useLocalExecution.ts`
- Modify: `apps/web/app/composables/useCommandQueue.ts`
- Modify: `apps/web/app/pages/index.vue`
- Modify: `apps/web/app/pages/cases/[id].vue`
- Create: `apps/web/tests/unit/useLocalExecution.spec.ts`
- Create: `apps/web/tests/e2e/offline-command-flow.spec.ts`

**Interfaces:**
- `useLocalExecution().createCase(caseId, itemLabel, now) -> Promise<CaseV2>`.
- `useLocalExecution().sendCommand(caseValue, envelope) -> Promise<CaseV2>`.
- Compatible `0.3.0` client does not call `/case/create` or `/case/command` for normal deterministic operations.
- Existing network queue remains only explicit compatibility fallback for unsupported local contract state.

- [ ] **Step 1: Write RED tests with network disabled**

E2E route-aborts `/api/v1/case/create` and `/api/v1/case/command`, then creates Case, sets mode, adds search suggestion, records/refines check, rejects action, pauses/resumes and closes successfully.

- [ ] **Step 2: Run RED**

Run: `pnpm --dir apps/web exec playwright test tests/e2e/offline-command-flow.spec.ts`

Expected: FAIL because pages still use API/command queue.

- [ ] **Step 3: Wire pages exclusively through local execution for supported commands**

Do not add local counter mutations; page state is replaced only with the atomically persisted Case returned by `useLocalExecution`.

- [ ] **Step 4: Run GREEN plus existing create/check/close suites**

```bash
pnpm --dir apps/web exec playwright test tests/e2e/offline-command-flow.spec.ts tests/e2e/create-resume.spec.ts tests/e2e/check-flow.spec.ts tests/e2e/close-flow.spec.ts
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/app/composables/useLocalExecution.ts apps/web/app/composables/useCommandQueue.ts apps/web/app/pages/index.vue apps/web/app/pages/cases/[id].vue apps/web/tests
git commit -m "feat: execute deterministic web actions locally"
```

---

### Task 14: Produce checklist proposals locally and degrade assistant mode explicitly offline

**Files:**
- Modify: `apps/web/app/composables/useLocalExecution.ts`
- Modify: `apps/web/app/pages/cases/[id].vue`
- Modify: `apps/web/app/lib/i18n/ru.ts`
- Modify: `apps/web/app/lib/i18n/en.ts`
- Modify: `apps/web/app/lib/eval/log.ts`
- Create: `apps/web/tests/e2e/offline-proposal-flow.spec.ts`

**Interfaces:**
- `buildLocalChecklistProposal(caseValue, mode) -> ProposalModel` uses generated executor.
- Checklist arm always uses local deterministic proposal path.
- Assistant arm while offline uses same local proposal and displays reviewed `offline deterministic guidance` indicator.
- Evaluation adds `assistant_offline_fallback` with metadata-only payload.
- Reconnect never sends past journal entries automatically.

- [ ] **Step 1: Write RED assistant-offline test**

Abort `/api/v1/proposal/next`; use assistant arm; assert local next action appears, offline indicator is visible, Case/journal are not rewritten, and no retry request is issued merely after `online` event.

- [ ] **Step 2: Run RED**

Expected: FAIL because assistant proposal path still requires API.

- [ ] **Step 3: Implement local proposal orchestration and copy**

Use `navigator.onLine` plus request-failure fallback only to choose transport; never persist the experimental arm or fallback status as evidence.

- [ ] **Step 4: Run GREEN in Chromium and WebKit**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/app/composables/useLocalExecution.ts apps/web/app/pages/cases/[id].vue apps/web/app/lib/i18n apps/web/app/lib/eval/log.ts apps/web/tests/e2e/offline-proposal-flow.spec.ts
git commit -m "feat: add offline deterministic proposal fallback"
```

---

### Task 15: Add execution-contract metadata and fail-closed API/PWA skew handling

**Files:**
- Create: `apps/api/mind_detective_api/execution_contract.py`
- Modify: `apps/api/mind_detective_api/contracts.py`
- Modify: `apps/api/mind_detective_api/app.py`
- Create: `apps/api/tests/test_execution_contract.py`
- Create: `apps/web/app/lib/execution/contract.ts`
- Modify: `apps/web/app/composables/useCaseApi.ts`
- Modify: `apps/web/app/lib/i18n/ru.ts`
- Modify: `apps/web/app/lib/i18n/en.ts`
- Create: `apps/web/tests/e2e/execution-contract-skew.spec.ts`

**Interfaces:**
- `GET /api/v1/execution/contract` returns `version`, `kernel_sha256`, `case_schemas`.
- Assistant `ProposalRequest` adds `execution_contract_version` and `execution_kernel_sha256`.
- API rejects mismatch before LiteLLM invocation with `MD_WEB_EXECUTION_CONTRACT_MISMATCH`.
- Local certified execution remains available after network mismatch.

- [ ] **Step 1: Write RED API test**

```python
def test_assistant_contract_mismatch_fails_before_provider_call(self) -> None:
    response = self.client.post("/api/v1/proposal/next", json=mismatched_assistant_request())
    self.assertEqual(response.status_code, 409)
    self.assertEqual(response.json()["code"], "MD_WEB_EXECUTION_CONTRACT_MISMATCH")
    self.assertEqual(self.fake_provider.calls, 0)
```

- [ ] **Step 2: Write RED Web skew E2E**

Mock API metadata with a different kernel hash; assert update/reconnect copy and successful local deterministic check while assistant request remains blocked.

- [ ] **Step 3: Implement metadata endpoint/request fields/compatibility check**

Do not compare repository version strings; compatibility is based on local execution contract version + kernel hash + Case schema.

- [ ] **Step 4: Run GREEN API + Web tests**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api apps/web/app/lib/execution/contract.ts apps/web/app/composables/useCaseApi.ts apps/web/app/lib/i18n apps/web/tests/e2e/execution-contract-skew.spec.ts
git commit -m "feat: fail closed on execution contract skew"
```

---

### Task 16: Certify the complete offline PWA vertical slice and privacy boundary

**Files:**
- Modify: `apps/web/nuxt.config.ts`
- Create: `apps/web/tests/e2e/offline-vertical-slice.spec.ts`
- Modify: `apps/web/tests/e2e/pwa-storage.spec.ts`
- Modify: `apps/web/tests/e2e/scenario-matrix.spec.ts`
- Modify: `apps/web/tests/unit/evalLog.spec.ts`

**Interfaces:**
- Static generated executor is precacheable shell code.
- API/case/user/model/evaluation payloads remain excluded from service-worker caches.
- Full offline flow after initial app availability covers create → mode → statement → proposal → check → next proposal → refine → reject → pause/resume → close → export → reopen.
- No background sync or hidden offline-history upload.

- [ ] **Step 1: Write RED full-offline scenario**

Start page once online to install shell, then set context offline and complete the full flow with all `/api/**` requests failing. Assert no API request is required for deterministic completion.

- [ ] **Step 2: Run RED**

Run the dedicated offline vertical-slice test in Chromium + WebKit; expected FAIL on any remaining network dependency.

- [ ] **Step 3: Make PWA caching/runtime changes only where the RED proves necessary**

Keep `/api/**` excluded from Workbox runtime caches and keep background sync disabled.

- [ ] **Step 4: Run complete Web verification**

```bash
pnpm --dir apps/web exec vitest run
pnpm --dir apps/web build
pnpm --dir apps/web exec playwright test
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/web/nuxt.config.ts apps/web/tests
git commit -m "test: certify complete offline search workflow"
```

---

### Task 17: Trace requirements, update RU/EN docs/ADR/CI and prepare declarative `0.3.0` release

**Files:**
- Modify: `docs/REQUIREMENTS.md`
- Modify: `docs/CONTRACT_MATRIX.json`
- Modify: `docs/EVAL_TOKEN_REGISTRY.json`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/ARCHITECTURE.en.md`
- Modify: `docs/PRIVACY.md`
- Modify: `docs/PRODUCT_EVALUATION.md`
- Create: `docs/adr/013-portable-local-execution-kernel.md`
- Create: `docs/adr/014-offline-execution-receipts.md`
- Create: `docs/adr/015-execution-contract-skew.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Modify: `CHANGELOG.md`
- Modify: `CHANGELOG.en.md`
- Modify: `.github/workflows/ci.yml`
- Create: `.github/releases/0.3.0.md`
- Modify: `.github/releases/release.json`
- Modify: plugin/marketplace version descriptors
- Modify: `tests/test_contract_matrix.py`
- Modify: `tests/test_release_contract.py`
- Modify: `tests/test_repository_contracts.py`

**Interfaces:**
- Add stable requirements at minimum:
  - `MD-OFFLINE-REQ-KERNEL-01` — one restricted Python portable semantic source.
  - `MD-OFFLINE-REQ-GENERATOR-01` — generated TS is reproducible and unedited.
  - `MD-OFFLINE-REQ-CONFORMANCE-01` — full corpus Python/TS result/error parity.
  - `MD-OFFLINE-REQ-LOCAL-01` — supported deterministic commands require no network.
  - `MD-OFFLINE-REQ-ATOMIC-01` — Case+receipt commit is atomic.
  - `MD-OFFLINE-REQ-IDEMPOTENCE-01` — duplicate command semantics are safe/conflict-detecting.
  - `MD-OFFLINE-REQ-PROPOSAL-01` — deterministic checklist proposal runs locally.
  - `MD-OFFLINE-REQ-ASSISTANT-01` — assistant offline fallback is explicit and not replayed.
  - `MD-OFFLINE-REQ-SKEW-01` — incompatible API/client contract blocks assistant processing.
  - `MD-OFFLINE-REQ-PRIVACY-01` — receipts contain metadata hashes/IDs only.
  - `MD-OFFLINE-REQ-PWA-01` — full deterministic offline vertical slice passes Chromium/WebKit.
  - `MD-OFFLINE-REQ-RELEASE-01` — exact-main immutable publisher governance retained.
- Release manifest declares repository `0.3.0` and plugin `mind-detective-v0.3.0` only.

- [ ] **Step 1: Write RED requirement/release tests**

Add exact selectors for all `MD-OFFLINE-REQ-*` IDs and version-parity assertions expecting `0.3.0`; before docs/descriptors are updated the tests must fail.

- [ ] **Step 2: Run RED**

```bash
python -m unittest discover -s tests -p 'test_contract_matrix.py' -v
python -m unittest discover -s tests -p 'test_release_contract.py' -v
python -m unittest discover -s tests -p 'test_repository_contracts.py' -v
```

Expected: FAIL on missing offline requirements/version `0.3.0`.

- [ ] **Step 3: Update contracts, architecture, privacy, bilingual public docs and declarative release set**

`release.json` must normalize to repository tag `0.3.0` and plugin tag `mind-detective-v0.3.0`, both using `.github/releases/0.3.0.md`. Preserve all `0.1.0`/`0.2.0` release note files unchanged.

- [ ] **Step 4: Run complete release-ready verification**

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

- [ ] **Step 5: Commit release-ready implementation**

```bash
git add plugins scripts tests conformance apps docs README.md README.en.md CHANGELOG.md CHANGELOG.en.md .github
git commit -m "release: prepare MIND Detective 0.3.0"
```

- [ ] **Step 6: Preserve integration/publication gates**

1. Push a separate implementation branch and open an implementation PR.
2. Require exact implementation-head CI success including generator drift, conformance and offline Chromium/WebKit.
3. Obtain explicit human authorization before merge.
4. Merge with expected-head protection.
5. Require exact post-merge `main` push CI success.
6. Obtain/confirm explicit human publication authorization for the full 40-hex `main` SHA.
7. Run only `.github/workflows/publish-current-release.yml` with that SHA.
8. Verify `0.3.0` and `mind-detective-v0.3.0` are non-draft, immutable and both tag refs resolve to the exact approved SHA.

---

## Plan Self-Review

### Spec coverage

- Portable semantic authority and controller delegation: Tasks 1–5.
- Restricted transpilable subset: Task 6.
- Deterministic generated artifact and metadata: Task 7.
- Canonical hashing: Task 8.
- Synthetic deterministic conformance corpus: Task 9.
- Exact Python↔TypeScript parity and generation drift CI: Task 10.
- Atomic IndexedDB Case+receipt persistence: Task 11.
- Command idempotence/conflict handling: Task 12.
- Offline local-first create and all deterministic mutations: Task 13.
- Local checklist proposals and assistant offline fallback/no replay: Task 14.
- API/PWA execution-contract skew handling: Task 15.
- Complete offline PWA + service-worker/privacy behavior: Task 16.
- Requirements/ADR/RU+EN docs/CI/release governance: Task 17.

### Placeholder scan

The plan contains no `TBD`, `TODO`, `implement later`, Python Ellipsis placeholders, hand-waved test steps, undefined command names or instructions to manually edit generated TypeScript.

### Type and authority consistency

- `Case v2` stays unchanged throughout the plan.
- The portable kernel consumes/emits JSON-compatible Case dictionaries; `CaseController` remains the public dataclass facade.
- The generator consumes only validated portable-kernel AST; generated TypeScript is not an independent source.
- Receipt hashes use the canonical JSON contract introduced before receipt/idempotence tasks.
- Local command names exactly match the `0.2.0` `CommandEnvelope` set.
- Checklist proposal shape remains the existing `ProposalModel` shape.
- Assistant path never receives offline-history replay semantics.
- Version skew is checked using execution-contract version/hash rather than mutable repository/main identity.

## Execution Handoff

Implementation must occur on a separate production branch/PR after the design documentation branch is integrated according to the repository's human gate. At execution time create an isolated worktree when available via `superpowers:using-git-worktrees`, then execute task-by-task with `superpowers:subagent-driven-development` or `superpowers:executing-plans`. Approval of this implementation plan does not by itself authorize production merge or release publication.
