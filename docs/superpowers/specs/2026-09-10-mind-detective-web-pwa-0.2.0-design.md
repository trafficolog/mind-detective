# MIND Detective 0.2.0 Web/PWA Design

**Status:** Proposed canonical design; human written-spec review pending  
**Release target:** repository `0.2.0`, plugin `mind-detective 0.2.0`  
**Base:** released `0.1.0` at `c1585b39747b432277c75e565e9a876db1fda54b`

## 1. Purpose

`0.2.0` adds a mobile-first Web/PWA surface over the released deterministic MIND Detective core without creating a second domain implementation.

The product remains a **systematic lost-item search assistant**. The Web/PWA exists to reduce working-memory load during a physical search by keeping the current case state, checked locations, remaining checks, uncertainty, and one next action continuously visible.

The Web/PWA is not a chatbot shell. It is a case-state shell with a structured interaction journal.

## 2. Decisions carried forward from 0.1.0

The following invariants remain normative:

- `Case` + `CaseController` are the only deterministic source of truth for case state.
- LLM output cannot directly mutate a case.
- no Bayesian priors, POD, calibrated location percentages, hidden `belief_weight`, or probability-style location claims;
- repeated checks are not independent statistical evidence;
- reconstruction and physical search have different safety rules;
- concrete locations may be proposed in search mode but must not be injected into reconstruction as user memory;
- case data is local by default;
- no cross-case learning or personal priors;
- no high-risk forgotten-action reasoning such as deciding whether medication was taken;
- the existing Python core under `plugins/mind-detective/scripts/` stays stdlib-first and transport-free.

## 3. Architectural choice

### 3.1 Chosen approach

Use:

- **Nuxt 4 static PWA** for the client;
- **IndexedDB** for browser-local case persistence;
- a thin **FastAPI** adapter for server-side domain execution and model calls;
- the existing Python MIND Detective core as the only domain implementation;
- a single configured LLM provider for `0.2.0`;
- no server-side case database.

```text
┌──────────────────────────────────────────────┐
│ Nuxt 4 static PWA                            │
│                                              │
│ Case shell                                   │
│ Interaction journal                         │
│ Timeline summary                            │
│ Checked / remaining summary                 │
│ One next action                             │
│ Found / Pause / Resume                      │
│                                              │
│ IndexedDB: canonical local Case             │
│ Command queue: client transport state only  │
└───────────────────┬──────────────────────────┘
                    │ JSON
                    ▼
┌──────────────────────────────────────────────┐
│ FastAPI adapter                              │
│                                              │
│ request/schema validation                    │
│ deterministic command execution             │
│ model proposal generation                    │
│ safety + guard validation                    │
│                │                             │
│                ▼                             │
│ existing Python CaseController               │
└───────────────────┬──────────────────────────┘
                    │
                    ▼
             configured LLM provider
```

### 3.2 Explicitly rejected in 0.2.0

- a TypeScript port of `CaseController`;
- optimistic client-side domain reduction;
- Postgres/Redis case persistence;
- accounts/authentication;
- cloud sync or multi-device resume;
- generic model-provider abstraction;
- extracting the Python core into a new shared package solely for the Web/PWA;
- native mobile applications.

These are separate future design gates.

## 4. One shell for checklist and AI

Research validity requires the checklist and AI-assisted variants to use the **same product shell**.

The following must be identical between B and C arms:

- navigation;
- screen structure;
- mode labels;
- quick actions;
- create/resume/close flows;
- next-action card;
- checked/remaining summary;
- timeline presentation;
- persistence behavior;
- reviewed RU/EN UI copy templates;
- structured input controls;
- free-text escape-hatch placement;
- failure and pending states.

The only intended experimental difference is **how the next structured proposal is generated**:

- **B — structured checklist/controller:** deterministic rules and checklist prompts generate candidates and the next action;
- **C — checklist/controller + AI:** the LLM may interpret user input and propose structured candidates/clarifications, but all proposals are validated by the same safety/guard/controller path before the same UI templates render them.

The LLM does **not** supply arbitrary final display copy in the main shell for `0.2.0`. It supplies structured proposal data. The client renders approved localization keys and structured values. This avoids measuring prose style, animation, or chat affordances as if they were AI reasoning quality.

Arm A remains ordinary unassisted search outside the application and is evaluated separately.

## 5. Interaction journal, not chatbot transcript

The persistent central stream is named **interaction journal / ход поиска**, not chat.

Every rendered journal entry carries immutable provenance:

```json
{
  "id": "entry-001",
  "author": "user",
  "mode": "reconstruction",
  "entry_type": "statement",
  "text": "Я помню, что открывал дверь машины",
  "created_at": "...",
  "statement_ids": ["stmt-001"],
  "search_check_ids": []
}
```

Allowed `mode` values:

- `reconstruction`
- `search`
- `system`

The mode is a property of each entry, not only of the current screen. A search-mode entry must remain visibly marked as search when reopened days later.

Mode presentation must not depend on color alone. Each entry uses:

- text label;
- icon;
- distinct typography/treatment;
- optional color as a redundant signal.

The current mode banner is rendered by application state, never supplied as model text.

### 5.1 Case schema implication

`0.2.0` introduces `mind-detective-case/v2` with an `interaction_journal` field. This journal is canonical presentation/audit state owned by the Python controller layer, but it is not treated as independent evidence for planner decisions. Domain facts continue to come from typed statements, timeline events, checks, candidates, constraints, and outcome.

`case/v1` must load through an explicit deterministic migration to `case/v2`; no destructive rewrite of existing `0.1.0` exports is allowed.

## 6. Mobile-first shell

### 6.1 Persistent top summary

The search-state summary is always visible:

```text
Проверено 4 · Осталось 3 · Недоступно 1
```

The values are derived from canonical case state, not maintained as separate counters.

### 6.2 Next-action card

The primary card contains exactly one current action or a deterministic empty-state prompt.

When relevant it must include prior-check context inline, for example:

> Проверить рюкзак  
> Здесь уже смотрели вчера, но способ проверки не был уточнён.

Primary actions may include:

- `Начать`
- `Проверил`
- `Не подходит`
- `Не могу проверить`
- `Нашёл`

`Удалить дело` is never adjacent to these primary physical-search actions.

### 6.3 Full lists remain reachable but are not required for orientation

Timeline, checked, remaining, and inaccessible detail views may be tabs/sections below the primary card. The user must not need to open them simply to know whether prior work exists because the persistent summary and next-action annotation expose that information continuously.

No mobile bottom sheet is the sole home of checked/to-check state.

### 6.4 Desktop

Desktop keeps the mobile interaction model centered rather than introducing a separate three-column product. A non-interactive or lightly interactive side rail may expose timeline/search summary when width permits. Domain interactions remain identical to mobile.

## 7. Required screens

### 7.1 First case creation

The stress-state entry screen contains:

- one field: `Что потерялось?` / `What is missing?`;
- one primary button: `Начать поиск` / `Start search`.

No account gate, onboarding carousel, configuration form, probability question, or multi-step wizard precedes case creation.

### 7.2 Case list / resume

The local home screen lists active and paused cases sorted by `updated_at` and provides `Новый поиск`.

Each card shows only:

- item label;
- lifecycle state;
- checked/remaining compact summary;
- last local update time.

Resume restores the exact case state. No statement is strengthened and no search check is silently reclassified on load.

### 7.3 Active case shell

Contains:

- current case label;
- lifecycle/pause control;
- persistent checked/remaining/inaccessible summary;
- next-action card;
- interaction journal;
- inline timeline/search sections;
- structured quick inputs;
- free text as an explicit escape hatch, not default keyboard focus.

### 7.4 Closing flow

`Нашёл` opens a focused close flow rather than immediately discarding context.

The user records a structured `found_context`:

- `current_suggested_action`
- `elsewhere_unplanned`
- `after_previous_check`
- `unknown`

Optional fields:

- found-location text;
- user-authored possible cause;
- simple prevention note.

The close flow explicitly separates `found` from `found while following the current plan`. `elsewhere_unplanned` is a first-class research outcome.

After close the user chooses:

- retain locally;
- export then retain;
- delete local case.

## 8. Deterministic action latency and network failure

### 8.1 No client reducer

The Nuxt client must not reimplement domain state transitions.

Tapping a deterministic action creates a **pending command**. Canonical local `Case` remains unchanged until the server returns the updated validated Case.

The UI does not freeze. It shows pending state on the affected card/control while allowing navigation and reading.

### 8.2 Command queue

The client owns a transport-only queue:

```json
{
  "command_id": "cmd-...",
  "case_id": "case-...",
  "command_type": "record_search_check",
  "payload": {},
  "created_at": "...",
  "status": "pending",
  "attempt_count": 0
}
```

The queue is **not domain state** and is not used by the planner.

Rules:

- commands for one case are sent sequentially;
- retries reuse the same command id, entity ids, and timestamps;
- no new timestamp/entity id is generated on retry;
- no second state-mutating command executes until the previous command produces a canonical Case response;
- the rest of the shell remains usable;
- transient network failure shows retry state;
- permanent validation failure removes the pending operation only after the user is shown the reason/fallback;
- closing or deleting a case while commands are pending requires explicit resolution of those pending commands.

This intentionally trades immediate local mutation for a single domain implementation.

A generated or fixture-validated client reducer is deferred to a future architecture gate, not hidden inside `0.2.0`.

## 9. One-tap physical check

`Проверил` must remain a one-tap default path.

The tap records a new `SearchCheck` with a neutral method value indicating that the user reported checking without specifying quality. `0.2.0` adds:

- `SearchMethod.REPORTED_CHECK`

The application must not silently upgrade this to `visual_systematic`, `empty_and_check`, or another more thorough method.

The old concept of `inaccessible` as a search **method** is not used for new Web/PWA checks. Accessibility is orthogonal and represented through `inaccessible_parts` / partial accessibility state.

If the planner later considers the same target again and method quality materially affects whether repeating the check is useful, the app asks an inline clarification such as:

> В прошлый раз вы отметили это место как проверенное. Как именно проверяли?

Options may include:

- быстро посмотрел;
- осмотрел системно;
- полностью освободил/проверил отделения;
- проверил на ощупь.

`Есть недоступная часть` is a separate checkbox/control, never a radio option competing with method quality.

## 10. Empty planner state

When no safe useful candidate is available, the app must not fabricate a next location.

The next-action card becomes a deterministic **need-more-information** state with one neutral prompt chosen from controller-owned rules, for example:

- clarify the last supported interaction;
- add an unchecked place already mentioned by the user;
- resolve a partial/inaccessible check;
- switch to practical recovery/fallback when urgency requires it.

The UI must distinguish this state from a normal physical next action.

## 11. Guard-block presentation

An AI proposal blocked by guard/safety is a visible trust event.

`0.2.0` does not silently regenerate until something passes.

When a proposal is rejected:

1. the blocked model proposal is not rendered as user-facing fact or suggestion;
2. the interaction journal receives a **system** event with reviewed copy, for example: `Не удалось использовать предложение ИИ: оно содержало неподтверждённое предположение. Показываем безопасный нейтральный шаг.`;
3. the client renders the deterministic fallback returned by the server;
4. evaluation logs record `ai_guard_blocked` with a machine reason code, not the rejected text.

Detailed machine codes may be exposed in a diagnostic/details affordance, but are not primary UX copy.

## 12. Rejecting a next action

The next-action card includes `Не подходит` / `Not suitable`.

Optional structured reasons:

- already checked;
- impossible now;
- irrelevant;
- unsafe/uncomfortable;
- other.

A rejection is domain-significant feedback, not only analytics. `case/v2` therefore records candidate-action feedback so the planner does not immediately repeat the same rejected candidate without new evidence or an explicit user reset.

The exact representation may be a small `action_feedback` collection owned by `CaseController`; it must remain categorical and must not become a numerical preference score.

## 13. Persistence, durability and export

Browser storage is private-by-default but not equivalent to durable cloud backup.

### 13.1 Local persistence

- canonical Web cases are stored in IndexedDB;
- Cache Storage/service worker caches never contain Case payloads, user text, LLM proposals/responses, or evaluation exports;
- no case is uploaded for persistence;
- the server handles the case only for the duration of an API request unless ordinary infrastructure logs are explicitly configured otherwise; application logs must not contain full case payloads.

### 13.2 Persistence request

On supported browsers the app must:

- check `navigator.storage.persisted()`;
- request `navigator.storage.persist()` after meaningful engagement such as first case creation/save;
- record only granted/denied capability state locally;
- never tell the user persistence is guaranteed when the browser denied or does not support it.

### 13.3 Install education

The app provides a contextual PWA install prompt/instruction after the first useful interaction, not before case creation.

Browser-specific installation limitations are handled as presentation logic. Installation is recommended for durability/convenience but never described as a complete backup guarantee.

### 13.4 Manual export/import

Every retained case supports explicit JSON export and validated import.

Requirements:

- export uses the canonical versioned Case schema;
- import validates schema before any local write;
- `case/v1` imports migrate deterministically to `case/v2`;
- invalid or future unsupported schemas fail closed with a user-readable message;
- export/import never starts a network upload;
- the user is clearly told that clearing site/app data can remove local cases.

### 13.5 Storage-loss copy

Privacy copy must explicitly state:

- cases are stored on this device/browser;
- the service does not provide cloud backup in `0.2.0`;
- browser/site-data clearing can delete them;
- persistent-storage requests reduce eviction risk but do not supersede explicit user deletion;
- export is the recovery mechanism for important cases.

## 14. API surface

The API is stateless with respect to persisted cases.

Minimum surface:

```text
POST /api/v1/case/create
POST /api/v1/case/command
POST /api/v1/proposal/next
POST /api/v1/case/validate
```

### 14.1 `case/create`

Creates a canonical `case/v2` through Python domain code.

### 14.2 `case/command`

Executes deterministic controller operations. Input includes current Case plus one typed command. Output is a complete canonical updated Case.

### 14.3 `proposal/next`

Input includes:

- canonical current Case;
- current interaction mode;
- locale;
- optional user input;
- experimental arm/config.

Checklist arm uses deterministic proposal generation. AI arm may call the configured LLM to produce **structured proposal objects only**. The response that reaches the client has already passed safety, guard, and controller validation.

### 14.4 `case/validate`

Validates/migrates an imported or locally restored Case without changing its evidence meaning.

## 15. Model boundary

For `0.2.0` the model is a proposal generator, not a UI copywriter or state reducer.

Model outputs may propose:

- statement classification consistent with origin rules;
- neutral clarification intent;
- search candidate;
- categorical rationale references;
- candidate action feedback interpretation when explicit user text needs mapping.

Model outputs may not directly set:

- lifecycle;
- check completion;
- `found` outcome;
- mode label;
- timestamps;
- user confirmation;
- search method quality unless user supplied it;
- probability/confidence score;
- UI safety copy.

The application validates all structured proposals before Case mutation.

## 16. Input model

Primary input is not the software keyboard.

Preferred order:

1. quick actions/chips;
2. short structured choices;
3. explicit free-text escape hatch.

No automatic focus opens the keyboard when the active-case shell loads.

Voice input remains out of scope for `0.2.0`, but the design records typing while walking/searching as a known UX cost and a candidate for later validation.

## 17. i18n and safety copy

All application-controlled strings are localization keys with RU and EN resources.

This includes, at minimum:

- reconstruction/search/system mode labels;
- guard-block copy;
- safety limitation copy;
- empty planner state;
- storage durability warnings;
- create/resume/close flows;
- check-quality labels;
- pending/retry/error states;
- export/import messages.

RU/EN parity is a CI contract. Missing keys or divergent required safety semantics are build failures.

Model-generated arbitrary prose is not required for main-shell rendering in `0.2.0`, reducing unreviewed safety-copy surface.

## 18. Evaluation log

Evaluation telemetry is local by default and excludes case text, place names, item names, and raw model output.

Required events include:

- `case_started`
- `next_action_shown`
- `next_action_started`
- `next_action_rejected`
- `check_started`
- `check_finished`
- `duplicate_check_detected`
- `check_quality_clarified`
- `ai_guard_blocked`
- `pending_command_started`
- `pending_command_retried`
- `pending_command_failed`
- `pause`
- `resume`
- `found`
- `case_closed_unresolved`
- `case_abandoned`
- `found_context_recorded`

Derived metrics include:

- time to first/next useful action;
- `shown → started` conversion;
- next-action rejection rate;
- duplicate-check count;
- repeated-check clarification rate;
- guard-block rate;
- pending/retry rate;
- found rate;
- found during current suggested action vs elsewhere/unplanned;
- unresolved and abandoned outcomes kept separate;
- user-rated task load/convenience.

No product ranking metric is converted into a location probability.

## 19. PWA/service-worker boundary

The service worker may cache only application shell assets such as:

- HTML shell;
- JS/CSS bundles;
- reviewed locale files;
- icons/fonts/static assets.

It must not cache:

- `/api/**` responses;
- Case JSON;
- user text;
- model traffic;
- evaluation export files.

No background sync of cases or queued commands is enabled in `0.2.0`. Command retry occurs only while the application is active.

`@vite-pwa/nuxt` may be used as an implementation dependency, but it is not part of the domain contract and must remain replaceable.

## 20. Backend dependency boundary

`plugins/mind-detective/scripts/` remains stdlib-only.

Web dependencies live under an application boundary such as:

```text
apps/
  web/        Nuxt 4 PWA
  api/        FastAPI adapter + model integration
```

FastAPI, ASGI server, provider SDK, and web-specific packages must not be imported from the plugin core.

The API adapter imports/reuses the released Python domain implementation rather than cloning controller logic.

## 21. Error handling

The UI must distinguish:

- offline/pending transport;
- retryable server error;
- invalid local/imported schema;
- guard-blocked AI proposal;
- safety boundary exit;
- stale/invalid command against current Case;
- storage persistence not granted;
- local storage write failure.

No error state is silently converted into a successful search/check state.

A network failure must never mark a location checked before the canonical updated Case is returned.

## 22. Security and privacy

- HTTPS is required for production PWA and Storage API use;
- no credentials or provider secrets are shipped to Nuxt;
- provider calls occur server-side;
- API logs exclude raw Case and raw user text by default;
- no cross-case server index exists;
- no analytics identifier is required for local evaluation logs;
- imported JSON is schema-validated before use;
- exported JSON is explicit user action;
- destructive delete is separated from primary search actions and requires confirmation;
- service worker and caches must not retain sensitive case data.

## 23. Candidate stable requirements

The implementation plan should assign exact tests to at least these requirements:

- `MD-WEB-REQ-SHELL-01` — checklist and AI use one shell/navigation/action card.
- `MD-WEB-REQ-MODE-01` — every journal entry persists reconstruction/search/system provenance.
- `MD-WEB-REQ-MODE-02` — mode is represented by text/icon/typography, not color alone.
- `MD-WEB-REQ-STATE-01` — no client domain reducer exists.
- `MD-WEB-REQ-QUEUE-01` — mutations use a sequential retryable pending-command queue.
- `MD-WEB-REQ-CHECK-01` — one-tap check records neutral `reported_check` quality.
- `MD-WEB-REQ-CHECK-02` — inaccessible state is orthogonal to check method.
- `MD-WEB-REQ-SUMMARY-01` — checked/remaining/inaccessible summary is persistently visible.
- `MD-WEB-REQ-CREATE-01` — first case creation is one field + one primary button.
- `MD-WEB-REQ-RESUME-01` — active/paused cases are locally listable and resumable.
- `MD-WEB-REQ-EMPTY-01` — empty planner produces a neutral deterministic information-needed state.
- `MD-WEB-REQ-GUARD-01` — blocked AI proposal produces visible system event + deterministic fallback.
- `MD-WEB-REQ-ACTION-01` — next action can be explicitly rejected with categorical feedback.
- `MD-WEB-REQ-CLOSE-01` — found context distinguishes current suggested action from elsewhere/unplanned.
- `MD-WEB-REQ-STORE-01` — IndexedDB is canonical Web persistence; server has no case DB.
- `MD-WEB-REQ-STORE-02` — persistence capability is checked/requested honestly.
- `MD-WEB-REQ-EXPORT-01` — case export/import is local, versioned, validated and migratable.
- `MD-WEB-REQ-PWA-01` — service worker never caches API/case/user/model/evaluation data.
- `MD-WEB-REQ-I18N-01` — required RU/EN safety/product strings have parity tests.
- `MD-WEB-REQ-EVAL-01` — shown/start/reject and found-context events are captured without raw case text.
- `MD-WEB-REQ-CORE-01` — Web/API reuse Python CaseController; no TS port.
- `MD-WEB-REQ-RELEASE-01` — publication retains exact-main/full-SHA immutable release governance.

## 24. Acceptance criteria for 0.2.0

`0.2.0` is acceptable only if all of the following are true:

1. A user can create a case from one field and one button.
2. Active/paused local cases can be resumed without semantic strengthening.
3. Mobile shell always exposes search-progress summary and one next-action/empty-state card.
4. Checklist and AI arms use the same shell and reviewed rendering templates.
5. Reconstruction/search provenance remains visible on every historical journal entry after reload.
6. No client-side copy of CaseController or optimistic domain reducer exists.
7. State-mutating network actions use visible pending state and sequential retry.
8. A one-tap check does not pretend a thorough method was performed.
9. Inaccessible parts are captured separately from method quality.
10. Duplicate/previous checks can be annotated inline on the current next action.
11. Planner-empty state does not invent a location.
12. Guard-blocked AI output is not silently shown or silently regenerated; a visible system event and safe fallback are produced.
13. Users can reject a next action and the planner does not immediately repeat it without new evidence/reset.
14. `found` records whether success occurred during the suggested action or elsewhere/unplanned.
15. Browser persistence capability is checked/requested and storage limits are explained honestly.
16. Users can explicitly export/import canonical versioned cases; invalid imports fail closed.
17. Clearing local browser/app data is disclosed as a data-loss risk because no cloud backup exists.
18. Service worker caches contain no case/user/model/API/evaluation payloads.
19. RU/EN reviewed product and safety copy stay in parity.
20. Evaluation logs include shown/start/reject/guard/pending/found-context signals without raw sensitive text.
21. `plugins/mind-detective/scripts/` remains transport-free and stdlib-only.
22. FastAPI/model dependencies remain outside the plugin core.
23. Existing `case/v1` exports migrate deterministically to `case/v2`.
24. Existing `0.1.0` immutable releases/tags remain untouched.
25. `0.2.0` uses the existing full-SHA CI/release governance and requires explicit human publication authorization.

## 25. Explicitly out of scope

- accounts/authentication;
- cloud case persistence or backup;
- multi-device sync;
- server-side case database;
- voice input;
- MAX/Telegram/Alice surfaces;
- push notifications;
- camera/computer vision search;
- background case sync;
- cross-case personalization/learning;
- location probabilities or Bayesian/POD models;
- generated client reducer;
- multi-provider model routing;
- admin panel;
- native mobile app.

## 26. Browser-storage evidence used by this design

Checked 2026-09-10:

- MDN Storage API: browser storage is best-effort by default; `navigator.storage.persist()` can request persistent storage, but user agents may approve or deny according to browser rules.
- MDN storage eviction guidance: Safari may proactively evict script-created storage for origins without recent user interaction; persistent storage changes eviction behavior where granted.
- WebKit storage policy: Home Screen Web Apps share the same origin/overall quota model as browser use and storage can still be evicted under defined conditions.

These facts justify `persist()` + honest capability state + export/import. They do **not** justify claiming that PWA installation alone guarantees durability.

## 27. Design conclusion

The `0.2.0` vertical slice is intentionally narrow:

```text
same state-first shell
        +
message-level mode provenance
        +
IndexedDB local Case v2
        +
no client domain reducer
        +
visible pending command queue
        +
one-tap neutral SearchCheck
        +
always-visible search summary
        +
create / resume / close / export flows
        +
structured checklist-vs-AI proposal generation
        +
existing Python CaseController
        +
stateless FastAPI/model adapter
```

The product should remain useful when the LLM is disabled. If arm C does not materially outperform arm B on useful-action, rejection, duplicate-check, task-load, and found-context metrics, the correct product outcome is to retain the checklist/controller experience and reduce AI surface rather than compensate with more conversational UI.
