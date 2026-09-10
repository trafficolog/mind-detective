# MIND Detective 0.3.0 Implementation Plan Hardening

**Status:** normative execution addendum to `2026-09-10-mind-detective-offline-execution-0.3.0-implementation.md`.

**Precedence:** executors must read the base design, codegen hardening design addendum, base implementation plan, then this file. Where this file is more specific, it overrides the corresponding task wording without changing task numbering or release scope.

## Task 4 hardening — eliminate the API-side reducer

Extend Task 4 files with:

- Modify: `apps/api/mind_detective_api/commands.py`
- Modify: `apps/api/tests/test_commands.py`
- Create: `tests/test_api_portable_boundary.py`

After `CaseController` delegates supported transitions to the portable kernel, `apps/api/mind_detective_api/commands.py` must stop implementing those same transitions branch-by-branch.

The API adapter may:

- validate Pydantic/transport shape;
- reject forbidden payload keys;
- map HTTP errors;
- convert envelope dictionaries;
- invoke the portable kernel / controller facade.

It may not independently construct `Statement`, `CandidateCheck`, `SearchCheck`, `ActionFeedback`, journal entries or lifecycle mutations for supported local-execution commands.

Add a RED boundary test that parses `commands.py` AST and rejects imports/constructor calls to supported domain mutation types after the refactor:

```python
def test_api_command_adapter_has_no_supported_domain_reducer() -> None:
    source = (ROOT / "apps/api/mind_detective_api/commands.py").read_text()
    tree = ast.parse(source)
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert called.isdisjoint({"Statement", "CandidateCheck", "SearchCheck", "ActionFeedback", "JournalEntry"})
```

`apps/api/tests/test_commands.py` remains the HTTP/transport regression suite and must stay GREEN after reducer removal.

## Task 6 hardening — define certified portable intrinsics

Add files:

- Create: `plugins/mind-detective/scripts/portable_intrinsics.py`
- Create: `plugins/mind-detective/tests/test_portable_intrinsics.py`
- Modify: `scripts/local_execution_ast.py`
- Modify: `tests/test_local_execution_generator.py`

The portable kernel may call only these observable-semantics intrinsics in `v1`:

```python
def clone_json(value: object) -> object: ...
def unicode_casefold(value: str) -> str: ...
def split_python_whitespace(value: str) -> list[str]: ...
def compare_python_strings(left: str, right: str) -> int: ...
def portable_error(code: str, message: str) -> NoReturn: ...
```

Python implementations are reference behavior. The generator recognizes the exact intrinsic names and emits certified TypeScript helpers. Calls to JS-native `toLowerCase`, locale-sensitive lowercasing, default `.sort()`, or regex `\s+` as substitutes for Python domain semantics are forbidden in generated domain decisions.

`clone_json` may use `copy.deepcopy` in the Python intrinsic implementation; the portable kernel itself must call `clone_json()` rather than importing `copy`.

Cross-runtime fixture tests must include:

- `Straße` / `STRASSE` case-fold distinction;
- Cyrillic `Ё/ё`;
- non-ASCII whitespace such as NBSP and Unicode line separators;
- supplementary-plane characters for string ordering;
- nested JSON clone identity/non-aliasing.

## Task 7 hardening — generator emits intrinsic prelude and hashes exact artifact

The generated TypeScript file must include an emitter-owned prelude implementing only the certified intrinsics required by the portable source.

Generated metadata is exactly:

```json
{
  "version": "mind-detective-local-execution/v1",
  "kernel_sha256": "sha256:<64-hex>",
  "generated_sha256": "sha256:<64-hex>",
  "generator_version": "local-execution-generator/v1",
  "case_schemas": ["mind-detective-case/v2"]
}
```

`generated_sha256` hashes the exact UTF-8 bytes of `localExecution.ts` after final emission. Metadata generation must not create a self-referential hash cycle: the generated TypeScript header contains contract version, kernel hash and generator version, while `generated_sha256` exists in the separate `.meta.json` artifact and API release metadata.

Add deterministic tests that Python 3.10 and 3.13 generation produce byte-identical TypeScript and metadata for the same source.

## Task 13 hardening — offline Case creation is create-only

Extend files:

- Modify: `apps/web/app/lib/storage/indexeddb.ts`
- Modify: `apps/web/app/composables/useLocalExecution.ts`
- Modify: `apps/web/tests/e2e/offline-command-flow.spec.ts`

Add:

```ts
createCaseIfAbsent(caseValue: CaseV2): Promise<CaseV2>
```

Semantics:

1. open one `readwrite` transaction on `cases`;
2. if `case_id` absent, add with `objectStore.add`, not `put`;
3. if present and canonical creation identity (`case_id`, `item_label`, `created_at`) matches, return existing Case;
4. if present but identity conflicts, throw `{ code: 'MD_WEB_CASE_ID_CONFLICT' }`;
5. never overwrite an existing Case during creation.

E2E must double-submit the same generated creation identity and verify one Case record, then reuse the same `case_id` with different item text and verify the exact conflict code.

## Task 15 hardening — full execution identity participates in skew detection

Replace the base plan's three-field execution identity with four semantic identity fields plus schemas.

`GET /api/v1/execution/contract` returns:

```json
{
  "version": "mind-detective-local-execution/v1",
  "kernel_sha256": "sha256:<64-hex>",
  "generated_sha256": "sha256:<64-hex>",
  "generator_version": "local-execution-generator/v1",
  "case_schemas": ["mind-detective-case/v2"]
}
```

Assistant `ProposalRequest` adds all four client identity fields:

- `execution_contract_version`;
- `execution_kernel_sha256`;
- `execution_generated_sha256`;
- `execution_generator_version`.

The API must compare all four before any LiteLLM client construction/invocation. Each single-field mismatch is a separate test vector and returns `MD_WEB_EXECUTION_CONTRACT_MISMATCH`.

## Task 17 hardening — add four stable requirements

In addition to the base plan's `MD-OFFLINE-REQ-*` set, add exact selectors for:

- `MD-OFFLINE-REQ-API-01` — API command/checklist adapters contain no independent reducer for supported semantics.
- `MD-OFFLINE-REQ-INTRINSIC-01` — Python-observable string/clone/error semantics use certified intrinsics and cross-runtime vectors.
- `MD-OFFLINE-REQ-IDENTITY-01` — contract version, kernel hash, generated hash and generator version all participate in compatibility checks.
- `MD-OFFLINE-REQ-CREATE-01` — offline Case creation is create-only, idempotent for matching identity and conflict-detecting otherwise.

The final release-ready verification must therefore include the API portable-boundary test and portable-intrinsic tests in addition to the commands already listed in the base plan.

## Hardening self-review

- No API-side supported reducer survives Task 4.
- Python/TypeScript differences for case folding, whitespace and string ordering are explicit generated intrinsics rather than implicit JS substitutions.
- Deployment compatibility includes generator/artifact identity, not only Python source identity.
- Offline creation cannot silently overwrite an existing Case.
- No new Case schema, server persistence or model replay behavior is introduced.
