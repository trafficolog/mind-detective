# MIND Detective 0.3.0 Offline Deterministic Execution Design

**Status:** proposed canonical design; awaiting written review  
**Release target:** repository `0.3.0`, plugin `mind-detective 0.3.0`  
**Base:** released `0.2.0` at `44b8edaba11a0637c6a05fce30e4c87708a3d9d2`

## 1. Purpose

`0.3.0` removes the most important remaining Web/PWA usability penalty from `0.2.0`: deterministic actions should not require a network round-trip while a user is physically moving through a search.

The release adds an offline-capable generated local executor while preserving the product's core safety model:

- no manually maintained TypeScript copy of domain rules;
- no Bayesian/POD/probability layer;
- no cross-case learning;
- no silent reinterpretation of user memory;
- no hidden synchronization database;
- no retrospective LLM processing of offline activity.

The app must remain usable for a complete deterministic lost-item-search loop when the PWA is already available on the device and connectivity disappears.

## 2. Architectural decision

### 2.1 Chosen approach

Use a **portable deterministic Python kernel** as the source for Web-local semantics, generate the TypeScript executor from that restricted source, and certify the generated projection with deterministic differential conformance against the Python runtime.

```text
                        build / release time

      Python plugin core
             │
             ▼
┌──────────────────────────────┐
│ Portable Transition Kernel   │
│ pure + stdlib-only           │
│ JSON-compatible values only  │
│ restricted Python subset     │
└──────────────┬───────────────┘
               │ AST/codegen
       ┌───────┴────────┐
       ▼                ▼
Python reference   generated TypeScript
execution          local executor
       │                │
       └───────┬────────┘
               ▼
       differential corpus
       exact semantic equality

                         runtime

Nuxt PWA ── deterministic command ──► generated local executor
   │                                      │
   │                                      ▼
   │                              canonical Case v2
   │                                      │
   └──────────────────────────────► IndexedDB transaction

assistant proposal while online ──► FastAPI ──► LiteLLM
assistant proposal while offline ─► generated checklist fallback
```

The generated TypeScript file is a build artifact, not a second hand-authored reducer.

### 2.2 Why not Pyodide/WASM

Running the Python core in-browser would preserve one implementation but adds a large runtime, startup/memory cost, packaging complexity, service-worker complexity and a much larger security/update surface for a PWA whose deterministic transition logic is comparatively small.

### 2.3 Why not only improve the existing network queue

Better pending/retry UX does not solve the primary failure mode: the user may be in a corridor, garage, basement, stairwell or outdoor route with no reliable network. The app must be able to record checks and choose the next deterministic action without connectivity.

## 3. Authority model

`0.3.0` refines the `0.2.0` invariant rather than abandoning it.

- `CaseController` remains the public Python domain boundary.
- A new internal `PortableTransitionKernel` becomes the implementation source for the subset of state transitions that are safe to execute in the browser.
- `CaseController` delegates those eligible transitions to that kernel.
- The generated TypeScript executor is produced from the same restricted Python kernel source.
- Generated TypeScript is never manually edited.
- CI regenerates the artifact and fails if the repository differs.
- Python remains the release/reference oracle: every generated-Web transition must match the Python result or Python error code exactly on the conformance corpus.

This means the browser executes a certified projection of the Python semantics, not an independently designed reducer.

## 4. Portable kernel constraints

The kernel must be deliberately small and transpilable. It operates on canonical JSON-compatible `Case v2` and command dictionaries rather than Python dataclasses/classes.

Allowed data types:

- object/dict;
- array/list;
- string;
- boolean;
- integer where already required for non-probabilistic metadata;
- null/None.

Allowed control flow is a documented subset sufficient for current deterministic rules:

- assignment;
- field/index access;
- equality/inequality;
- membership tests;
- boolean expressions;
- `if`/`elif`/`else`;
- bounded iteration over arrays;
- deterministic sorting/filtering by explicit categorical order;
- calls to an allowlisted set of pure kernel helpers.

Forbidden in portable kernel source:

- filesystem or network I/O;
- clocks/time generation;
- randomness;
- environment access;
- reflection/eval/exec;
- dynamic imports;
- threads/processes;
- model/provider calls;
- floating-point probability/ranking math;
- mutable global state.

All IDs and timestamps continue to come from the command/request envelope. The executor never generates them internally.

The generator must fail closed on any unsupported AST node or helper call.

## 5. Local Execution Contract

The generated artifact carries a versioned contract identity:

```text
mind-detective-local-execution/v1
```

It includes:

- contract version;
- source SHA-256 of the portable kernel;
- generated artifact SHA-256;
- supported Case schemas;
- supported deterministic command types;
- supported deterministic proposal modes.

The contract version is independent from `Case.schema`.

`0.3.0` keeps:

```text
mind-detective-case/v2
```

No `case/v3` is introduced because no persisted Case field is required for offline execution.

## 6. Locally executable operations

The first local execution contract must cover every deterministic operation used by the existing Web shell:

1. create a new Case v2;
2. `set_mode`;
3. `add_statement`;
4. `record_search_check`;
5. `refine_search_check`;
6. `reject_next_action`;
7. `pause`;
8. `resume`;
9. `close_found`;
10. `close_unresolved`.

The Web client must not contain command-specific mutation logic outside the generated executor.

### 6.1 Candidate creation remains evidence-bound

The `0.2.0` rule remains unchanged:

- in search mode, an explicit user-origin `search_suggestion` may create a candidate whose target is exactly the text entered by the user;
- the client must not parse a different concrete location from that text;
- reconstruction input never creates a concrete search candidate merely because it sounds location-like.

### 6.2 Search check semantics remain unchanged

- one-tap check defaults to `reported_check`;
- inaccessible portions remain orthogonal to method;
- candidate check-state updates must match the Python reference exactly;
- repeated checks remain history, not independent probability evidence.

## 7. Local deterministic proposal generation

Offline mutation alone is insufficient because the user needs a next step after recording a check.

The portable contract therefore also includes deterministic checklist proposal generation equivalent to the current Python checklist path:

- reconstruction clarification;
- next safe search action using categorical planner ordering;
- partial/inaccessible clarification;
- neutral need-more-information fallback.

The categorical planner order remains:

1. exclude unsafe;
2. urgent over normal;
3. episode over habit over generic;
4. direct route over indirect over none;
5. unchecked over partial over checked;
6. low effort over medium over high;
7. deterministic ID tiebreak.

No numeric score or location probability is introduced.

Rejected candidate IDs remain excluded unless new evidence or an explicit future reset changes the Case.

## 8. Assistant arm offline behavior

When the experiment/deployment arm is `assistant` and connectivity is unavailable:

- the app does not attempt LiteLLM;
- it immediately uses the generated deterministic checklist proposal;
- the UI remains the same shell;
- a reviewed non-alarming indicator states that the app is operating offline with deterministic guidance;
- evaluation records `assistant_offline_fallback` without user text;
- offline user entries keep their normal reconstruction/search provenance.

When connectivity returns:

- no offline journal entry is retroactively sent to LiteLLM merely because the connection returned;
- no previous deterministic next action is rewritten;
- the next newly requested assistant proposal may use LiteLLM normally;
- blocked/raw model content remains subject to the existing guard path.

This prevents retrospective contamination of memory/search history.

## 9. Local-first runtime semantics

### 9.1 Deterministic commands

For a supported command:

1. capture the current canonical Case v2 snapshot;
2. create the complete immutable command envelope with `command_id`, `expected_updated_at`, IDs and timestamps;
3. execute through the generated local executor;
4. atomically persist the resulting Case plus an execution receipt in IndexedDB;
5. update the visible Case from the persisted result;
6. derive progress/annotations from the new canonical Case;
7. request the next local checklist proposal immediately when appropriate.

No network request is required for these steps.

### 9.2 No speculative reducer state

Unlike ordinary optimistic UI, the local executor output is the canonical browser-local Case after a successful IndexedDB transaction. The UI must not separately increment counters or maintain a second speculative Case.

### 9.3 Failure

If the generated executor rejects a command:

- no Case write occurs;
- the error code is rendered through reviewed copy;
- no fallback mutation is invented in JavaScript UI code.

If IndexedDB commit fails:

- the UI must not present the transition as completed;
- the previous Case remains canonical;
- retry reuses the same command envelope.

## 10. Execution receipts and idempotence

`0.3.0` adds a separate IndexedDB store such as `execution_receipts`.

A receipt contains only execution metadata:

```json
{
  "command_id": "cmd-...",
  "case_id": "case-...",
  "contract_version": "mind-detective-local-execution/v1",
  "input_case_hash": "sha256:...",
  "output_case_hash": "sha256:...",
  "applied_at": "..."
}
```

It does **not** contain:

- item label;
- location text;
- user text;
- command payload copy;
- model output.

Rules:

- Case update + receipt are committed in one IndexedDB transaction;
- duplicate `command_id` with matching input identity is treated as already applied, not executed twice;
- duplicate `command_id` with conflicting input identity fails closed with `MD_WEB_COMMAND_ID_CONFLICT`;
- deleting a local Case deletes its receipts in the same user-confirmed delete operation;
- receipts are not exported as part of canonical Case JSON.

The existing network pending queue ceases to be the primary path for deterministic mutations. It may remain only as an online compatibility/fallback path for an unsupported execution contract.

## 11. Canonical hashing

Case hashes used for receipts and conformance are based on canonical JSON serialization:

- UTF-8;
- sorted object keys;
- compact separators;
- arrays preserve order;
- no Unicode normalization that changes user text;
- SHA-256.

Python and TypeScript canonicalizers must share exact fixtures including Cyrillic, English, punctuation and empty/null fields.

Hashes are integrity/idempotence metadata only; they are not authentication or user identity.

## 12. Conformance architecture

### 12.1 Corpus

Repository-owned synthetic fixtures define deterministic input/output vectors:

```text
conformance/local-execution/v1/
  create-case/
  set-mode/
  add-statement/
  search-check/
  refine-check/
  reject-action/
  lifecycle/
  planner/
  failures/
```

Each vector contains:

- input Case or create request;
- command/proposal request;
- expected full canonical Case or proposal;
- expected error code for failure cases;
- contract version/source hash metadata.

No real user content is used.

### 12.2 Required comparison

For every vector:

```text
Python reference result == generated TypeScript result
```

Comparison uses structured deep equality after canonical JSON normalization.

Failure equivalence compares exact machine error codes.

### 12.3 Deterministic generated corpus

The corpus includes both hand-selected edge cases and a deterministic seeded matrix generated from legal categorical combinations. The seed is committed and stable.

It must cover at least:

- active/paused/terminal lifecycle states;
- stale `expected_updated_at`;
- all command types;
- all search methods/results;
- repeated/partial/inaccessible checks;
- rejected candidates;
- unsafe candidate exclusion;
- every planner category ordering boundary;
- RU/EN/Unicode text preservation;
- forbidden probability/POD/belief fields;
- duplicate command IDs;
- deterministic retry of the same command/input.

No production release may reduce corpus coverage without an explicit requirement/contract update.

## 13. Code generation

A repository generator, implemented with Python standard library, reads the restricted portable kernel and emits the TypeScript executor.

Generated output path:

```text
apps/web/app/generated/localExecution.ts
```

The file header contains:

- `GENERATED FILE — DO NOT EDIT`;
- local-execution contract version;
- portable-kernel SHA-256;
- generator version.

CI executes generation and requires:

```text
git diff --exit-code -- apps/web/app/generated/localExecution.ts
```

Any manual edit or stale generated file fails CI.

The generated executor must not use:

- `eval`;
- `new Function`;
- dynamic remote code loading;
- runtime code generation;
- provider SDKs.

## 14. Version skew and deployment compatibility

The static PWA bundle and API may briefly be on different deployment revisions.

`0.3.0` therefore exposes an API metadata endpoint:

```text
GET /api/v1/execution/contract
```

Response:

```json
{
  "version": "mind-detective-local-execution/v1",
  "kernel_sha256": "...",
  "case_schemas": ["mind-detective-case/v2"]
}
```

The client embeds the same metadata.

For assistant/network requests the client sends its contract version/hash.

If the API detects a semantic mismatch:

- it fails closed with `MD_WEB_EXECUTION_CONTRACT_MISMATCH`;
- it does not run LiteLLM against potentially incompatible Case semantics;
- the PWA may continue deterministic local/offline execution with its installed certified bundle;
- the user receives reviewed "update available / reconnect and refresh" guidance;
- no Case is deleted or rewritten.

The service worker may cache the generated executor as part of the static app shell because it contains no user data.

## 15. API role after 0.3.0

The server remains stateless with respect to persisted cases.

`POST /api/v1/case/command` remains for:

- compatibility with `0.2.x` clients;
- conformance/reference execution;
- explicit online fallback if the installed local executor does not support a future command.

It is no longer the normal mutation path for a compatible `0.3.0` Web client.

`POST /api/v1/proposal/next` remains required for online assistant proposals.

Checklist proposals can be produced locally or server-side and must be conformant.

No server-side case database is introduced.

## 16. Case creation and offline vertical slice

If the PWA shell has already been loaded/installed, the following flow must work with network disabled:

1. open local case list;
2. create a new Case v2;
3. choose reconstruction or search mode;
4. add user-supported information;
5. obtain a deterministic local checklist proposal;
6. record a check;
7. immediately obtain the next deterministic proposal;
8. refine check quality if prompted;
9. reject an unsuitable action;
10. pause/resume;
11. close found or unresolved;
12. export the Case locally;
13. reopen retained local cases.

Assistant-only semantic enhancement is unavailable offline, but the search workflow itself remains usable.

## 17. Import/migration scope

`0.3.0` does not need a new Case schema migration.

- existing Case v2 loads locally;
- Case v1 import may continue to use the existing validation/migration API while online;
- full offline v1 import migration is explicitly not required for this release;
- Case v2 import may be locally schema-checked if generated validation is available, but this is not a blocker for the core offline search loop.

This keeps the release focused on deterministic execution rather than introducing a second migration subsystem.

## 18. Privacy and security

The `0.2.0` privacy boundary remains intact and is strengthened by reducing required network calls.

- deterministic commands stay on device by default;
- local checklist proposals stay on device;
- assistant proposals still send only minimal current proposal context to the configured LiteLLM gateway while online;
- returning online does not automatically upload offline history;
- execution receipts contain hashes/IDs only;
- no new analytics identifier is introduced;
- no background case synchronization is introduced;
- generated code is static and release-verified;
- no remote code download controls domain behavior.

## 19. UX changes

### 19.1 Deterministic actions

For locally supported deterministic actions, the old network `pending` spinner is removed as the normal success path. UI updates only after the IndexedDB transaction commits, but no server round-trip is awaited.

A brief local `saving` state is permitted when persistence is not instantaneous.

### 19.2 Offline state

Offline state must be visible but not dominant. The app should communicate:

- deterministic search remains available;
- assistant enhancement is temporarily replaced by deterministic guidance;
- data remains local;
- no queued AI interpretation will be performed automatically later.

### 19.3 Network fallback

If a command is not supported by the installed execution contract and network is available, the app may use the server-authoritative command endpoint with the existing pending/retry UX.

If no network is available, unsupported commands fail explicitly rather than being guessed locally.

## 20. Evaluation additions

Local evaluation events add:

- `local_command_started`;
- `local_command_applied`;
- `local_command_failed`;
- `local_persistence_failed`;
- `assistant_offline_fallback`;
- `server_command_fallback`;
- `execution_contract_mismatch`;
- `app_update_required`.

No raw Case/user/model content is recorded.

Useful derived metrics include:

- deterministic action completion without network;
- local command failure rate;
- local persistence failure rate;
- assistant-offline fallback frequency;
- online server-fallback frequency;
- time from tap to persisted canonical Case;
- time from completed check to next deterministic action.

These latency metrics are UX/performance metrics, not location probability signals.

## 21. Stable candidate requirements

The implementation plan must assign exact selectors to at least:

- `MD-OFFLINE-REQ-KERNEL-01` — portable deterministic kernel is pure, stdlib-only and uses the approved restricted subset.
- `MD-OFFLINE-REQ-GEN-01` — Web executor is generated and CI fails on generated drift/manual edits.
- `MD-OFFLINE-REQ-CONFORMANCE-01` — Python and generated TypeScript match on every conformance vector.
- `MD-OFFLINE-REQ-CONFORMANCE-02` — failure paths match exact machine error codes.
- `MD-OFFLINE-REQ-COMMAND-01` — all current deterministic Web commands execute locally without network.
- `MD-OFFLINE-REQ-CREATE-01` — new Case v2 creation works offline after app shell availability.
- `MD-OFFLINE-REQ-PLANNER-01` — deterministic checklist proposal/planner works offline and matches Python reference.
- `MD-OFFLINE-REQ-IDEMPOTENCE-01` — Case write and command receipt are atomic and duplicate command IDs cannot double-apply.
- `MD-OFFLINE-REQ-HASH-01` — Python/TypeScript canonical JSON SHA-256 fixtures match exactly.
- `MD-OFFLINE-REQ-ASSISTANT-01` — assistant arm uses explicit local checklist fallback while offline.
- `MD-OFFLINE-REQ-ASSISTANT-02` — reconnect does not retrospectively send or reinterpret offline history.
- `MD-OFFLINE-REQ-VERSION-01` — client/server execution contract mismatch blocks assistant/network semantic mixing.
- `MD-OFFLINE-REQ-STORE-01` — deterministic Case + receipt persist atomically before UI marks completion.
- `MD-OFFLINE-REQ-STORE-02` — deleting a Case deletes its execution receipts without affecting other cases.
- `MD-OFFLINE-REQ-PRIVACY-01` — local execution/receipts introduce no automatic history upload or raw-text telemetry.
- `MD-OFFLINE-REQ-PWA-01` — generated executor may be cached only as static code; no sensitive payload enters Cache Storage.
- `MD-OFFLINE-REQ-SCHEMA-01` — Case remains `mind-detective-case/v2` for `0.3.0`.
- `MD-OFFLINE-REQ-RELEASE-01` — repository/plugin `0.3.0` retain existing exact-main/full-SHA immutable publication governance.

## 22. Acceptance criteria

`0.3.0` is acceptable only if all of the following are true:

1. No manually maintained TypeScript domain reducer exists.
2. The generated executor comes from a restricted Python portable kernel and is reproducible.
3. `CaseController` remains the public Python domain boundary for state mutations.
4. Every deterministic Web command available in `0.2.0` can execute offline.
5. A new Case can be created offline after the PWA shell is available.
6. A completed offline check can produce the next deterministic checklist action without network.
7. Assistant mode degrades to explicit deterministic checklist guidance when offline.
8. Reconnection does not retroactively send offline history to LiteLLM.
9. Case v2 remains the persisted/exported Case schema.
10. Local execution updates visible Case only after atomic IndexedDB persistence succeeds.
11. Duplicate command IDs cannot double-apply a transition.
12. Execution receipts contain no raw Case/user/model text.
13. Python and generated TypeScript produce identical results for the complete conformance corpus.
14. Python and generated TypeScript produce identical machine error codes for failure vectors.
15. Planner categorical ordering matches the Python reference exactly.
16. Unsafe candidates remain excluded locally.
17. Rejected candidates remain excluded locally unless new evidence/reset semantics permit otherwise.
18. No numerical location score/probability is introduced.
19. Generated-file drift fails CI.
20. Unsupported generator syntax fails closed.
21. Client/server execution-contract mismatch blocks assistant semantic mixing.
22. Existing `0.1.0` and `0.2.0` immutable releases/tags remain untouched.
23. `0.3.0` publication uses the existing canonical full-SHA publisher and separate human release authorization.

## 23. Explicitly out of scope

- accounts/authentication;
- cloud case backup or multi-device sync;
- background upload/replay of offline cases;
- retrospective LLM interpretation after reconnect;
- Pyodide/Python-in-browser runtime;
- arbitrary Python-to-TypeScript transpilation;
- full offline Case v1 migration;
- voice input;
- camera/computer vision;
- push notifications;
- MAX/Telegram/Alice surfaces;
- cross-case learning/personal priors;
- Bayesian/POD/location probabilities;
- multi-provider model routing outside existing LiteLLM responsibilities;
- native mobile applications.

## 24. Release governance

The release process remains unchanged in principle:

1. separate design PR;
2. explicit human design merge authorization;
3. separate implementation branch/PR from approved design;
4. exact implementation-head CI;
5. explicit human implementation merge authorization;
6. exact post-merge `main` CI;
7. separate publication authorization naming exact `main` SHA;
8. canonical `publish-current-release.yml` only;
9. immutable repository `0.3.0` and plugin `mind-detective-v0.3.0` tags/releases verified against exact SHA.

No existing immutable release is edited or retargeted.

## 25. Design conclusion

The release changes the Web execution model from:

```text
UI → network pending queue → Python CaseController → IndexedDB
```

to:

```text
                    certified at build/release time
Python portable kernel ───────────────► generated TypeScript executor
          │                                     │
          └──── differential corpus ────────────┘

                         runtime
UI → generated deterministic executor → atomic IndexedDB Case + receipt
                                     └→ local checklist proposal

online assistant only:
Case → FastAPI → LiteLLM → guard → proposal
```

The purpose is not to make the browser a second independent domain implementation. The purpose is to ship a **release-certified generated projection of the Python deterministic kernel** so that the core lost-item-search workflow remains useful when network latency or connectivity is poor.