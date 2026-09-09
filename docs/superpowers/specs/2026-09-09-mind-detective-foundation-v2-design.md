# MIND Detective Foundation v2 Design

**Status:** Proposed canonical replacement; human written-spec review pending  
**Date:** 2026-09-09  
**Repository:** `trafficolog/mind-detective`  
**Target first release:** repository `0.1.0`, plugin `mind-detective-v0.1.0`  
**Method:** SDD + TDD, Superpowers, DRY/KISS/YAGNI

**Supersedes for implementation:**

- `docs/superpowers/specs/2026-09-08-mind-detective-foundation-design.md`
- `docs/superpowers/plans/2026-09-09-mind-detective-foundation-implementation.md`

The superseded files remain in Git history as architecture-decision evidence. No production implementation may execute from the old plan after this v2 design is approved.

---

## 1. Product definition

MIND Detective is not a memory-restoration system, a forgetting-mechanism classifier, or an AI investigator.

Canonical positioning:

> **MIND Detective is a systematic lost-item search assistant: it helps reconstruct the sequence of actions, keep a reliable log of what has already been checked, choose one useful next step, resume after an interruption, and avoid repeating low-value checks.**

The primary product value is **reduction of cognitive load during search**. The user should not need to simultaneously remember the route, all checked places, the quality of those checks, unresolved alternatives, deadlines, and recovery contingencies.

The product must remain useful even if no memory mechanism can be identified and no probability model exists.

### 1.1 Supported product claims

The product may claim that it:

- structures user-provided recollections without turning them into verified facts;
- records physical search checks and their quality;
- distinguishes an unperformed check from a superficial or inaccessible check;
- proposes one next physical search action with an explicit rationale;
- resumes a saved case without silently inventing missing history;
- keeps urgency/safety constraints visible;
- records the outcome and lets the user retain or delete the case.

The product must not claim that it:

- restores memory;
- knows where an item is;
- diagnoses why the user forgot;
- infers a forgetting mechanism from where the item was found;
- provides calibrated location probabilities in MVP;
- medically evaluates memory or cognition;
- determines whether a person took medication or completed another high-risk forgotten action.

---

## 2. Architectural simplification

### 2.1 The case state is the product core

The central domain object is a **Case** rather than a set of memory-methodology subsystems.

```text
Skill host / future UI
          │
          ▼
┌──────────────────────────┐
│      Case Controller     │
│                          │
│ statements               │
│ timeline                 │
│ search checks            │
│ candidate checks         │
│ next action              │
│ urgency / constraints    │
│ lifecycle                │
│ outcome                  │
└───────────┬──────────────┘
            │
      ┌─────┴─────┐
      ▼           ▼
deterministic     LLM
 domain logic     dialogue / explanation
      │
      ▼
case-local persistence
```

The LLM is a dialogue and explanation component. It is not the authoritative store and does not own case-state transitions that deterministic code can represent.

### 2.2 No numerical belief model in `0.1.0`

P0 does not contain:

- Bayesian priors;
- posterior probabilities;
- probability of detection (`POD`);
- numerical location likelihood;
- hidden `belief_weight`;
- numerical ACH truth scores;
- automatic inference that repeated searches are independent.

The next action is selected using explicit categorical criteria and deterministic priority rules.

### 2.3 No forgetting-mechanism diagnosis

The product can store what the user thinks may have contributed to the loss, but that statement remains user-authored context.

Finding an item in a pocket, after a doorway transition, during stress, or after distraction does not establish a causal forgetting mechanism.

---

## 3. `0.1.0` scope

The first release contains one plugin and five production skills:

1. `mind-detective` — routing, case lifecycle, urgency and unsupported-flow boundary.
2. `mind-detective-reconstruct` — free account, neutral clarification and timeline reconstruction.
3. `mind-detective-plan` — physical search plan, search log and one-next-action selection.
4. `mind-detective-resume` — resume a saved case or hand it to another person without losing checked-state provenance.
5. `mind-detective-close` — found/unresolved outcome, optional simple prevention note, retain/delete case.

### 3.1 `0.1.0` explicitly does not contain

- Web/PWA UI;
- MAX, Telegram, Alice, voice or other channel adapters;
- long-term autobiographical recall workflow;
- prospective-memory workflow;
- cross-case personalization or learned priors;
- Bayesian search;
- mechanism-of-forgetting classification;
- full Cognitive Interview techniques such as perspective switching or imaginative reconstruction;
- external cloud/API connectors;
- model-provider abstraction;
- diagnosis, theft investigation or medical decision support.

### 3.2 `0.2.0` candidate: adaptive Web/PWA vertical slice

After the `0.1.0` case contracts stabilize, a separate architecture/design gate may add a small adaptive PWA with:

- conversation pane;
- timeline;
- `checked / to check / inaccessible` view;
- one highlighted next action;
- `found`, `pause`, `resume`, `delete case` actions;
- optional voice input as input convenience, not a distinct reasoning workflow.

The PWA consumes the same Case Controller semantics; `0.1.0` does not scaffold a frontend framework or surface adapter pre-emptively.

---

## 4. Canonical naming

- Repository: `mind-detective`
- Product: **MIND Detective / Детектив памяти**
- Human-facing category: **systematic lost-item search assistant / помощник систематического поиска потерянных вещей**
- Plugin: `mind-detective`
- Skills: `mind-detective`, `mind-detective-reconstruct`, `mind-detective-plan`, `mind-detective-resume`, `mind-detective-close`
- Local case root when explicitly saved: `.mind-detective/cases/`
- Machine reason-code prefix: `MD_`

`memory-search` may appear as descriptive language but is not a second runtime namespace.

---

## 5. Statement model

The system stores source and statement type independently. It does not encode truth confidence as a hidden evidence score.

### 5.1 `Statement`

Canonical fields:

```json
{
  "id": "stmt-001",
  "source": "user",
  "statement_type": "recollection",
  "original_text": "После магазина я положил пакет на стол.",
  "recorded_at": "2026-09-09T18:00:00Z",
  "event_time": null,
  "user_confirmation": true,
  "supporting_evidence_ids": [],
  "limitations": []
}
```

### 5.2 Sources

`source` enum:

- `user`
- `file`
- `assistant`

### 5.3 Statement types

`statement_type` enum:

- `recollection`
- `habit`
- `observation`
- `hypothesis`
- `search_suggestion`

### 5.4 Origin invariants

Allowed combinations in P0:

| Source | recollection | habit | observation | hypothesis | search_suggestion |
|---|---:|---:|---:|---:|---:|
| `user` | yes | yes | yes | yes | yes |
| `file` | no | no | yes | no | no |
| `assistant` | no | no | no | yes | yes |

The assistant cannot manufacture a user's recollection, habit, or observation.

A file-derived observation records what the supplied file supports; it is not automatically proof that an event occurred exactly as interpreted.

### 5.5 No automatic confidence promotion

The system does not promote or strengthen a statement because it contains:

- sensory detail;
- vividness;
- confident wording;
- lighting/color information;
- emotional intensity.

Words such as “probably” or “maybe” are not automatically reclassified as `habit`.

---

## 6. Reconstruction model

### 6.1 Minimal retrieval method

The MVP uses only:

1. free account;
2. neutral clarification;
3. voluntary context reinstatement;
4. explicit permission to answer “I don't remember”.

P0 excludes:

- forced perspective switching;
- imagined reconstruction presented as memory retrieval;
- repeated pressure to recover remote memories;
- claims that Cognitive Interview has been validated for household lost-item recovery.

### 6.2 Reconstruction mode boundary

While collecting recollection, the assistant must not introduce a new concrete location as if asking whether the user remembers it.

Allowed:

> “Что вы помните о том, что происходило после возвращения домой?”

Not allowed in reconstruction mode when the location was not previously supplied:

> “Вы не оставили ключи в машине?”

This restriction applies to **memory elicitation**, not to physical search planning.

### 6.3 Timeline with uncertainty

The timeline records:

- last reported or externally supported interaction with the item;
- first noticed-missing event;
- supported intermediate events;
- unknown intervals;
- contradictory statements.

Canonical name: `last_supported_interaction`, not `last_confirmed_contact`.

Absence of recall is not negative evidence. “I don't remember leaving the apartment” does not establish that the item remained inside.

---

## 7. Search log: primary domain asset

The search log is the main durable product value in `0.1.0`.

### 7.1 `SearchCheck`

```json
{
  "id": "check-001",
  "target": "карманы вчерашней куртки",
  "method": "empty_and_check",
  "started_at": "2026-09-09T18:10:00Z",
  "completed_at": "2026-09-09T18:12:00Z",
  "result": "not_found",
  "inaccessible_parts": [],
  "based_on": ["stmt-004"],
  "notes": "Проверены оба внешних и внутренний карманы."
}
```

### 7.2 Search methods

P0 canonical methods:

- `glance`
- `visual_systematic`
- `empty_and_check`
- `tactile`
- `inaccessible`

The method records **what was actually done**, not a probability of detection.

### 7.3 Search results

- `found`
- `not_found`
- `partial`
- `inaccessible`

A previous `glance + not_found` is materially different from `empty_and_check + not_found`.

### 7.4 Repeated checks

The controller must recognize duplicate or near-duplicate search targets and retain their history.

It must not treat three repeated glances as three independent statistical observations.

The user may intentionally repeat a check, but the controller should surface that it is a repeat and explain the prior method/result before recommending it again.

---

## 8. Candidate checks and concrete suggestions

The v1 design over-restricted concrete locations. V2 separates **reconstruction questions** from **search suggestions**.

### 8.1 Search suggestions are allowed

During search planning, the assistant may introduce a concrete physical location or container if it is explicitly represented as a proposal.

Allowed:

> “Предлагаю проверить карманы вчерашней куртки.”

Not allowed:

> “Ключи, вероятно, в куртке.”

Not allowed:

> “Вы вспомнили, что положили ключи в куртку.”

### 8.2 Suggestion provenance

Every assistant-generated concrete search suggestion becomes a `Statement` with:

- `source: assistant`
- `statement_type: search_suggestion`
- rationale referencing case data or an explicit generic-check rule;
- no probability field;
- no transformation into recollection/observation unless the user later supplies new evidence.

---

## 9. Choosing one next action

The controller chooses **one** next useful physical search action rather than outputting a long location list.

### 9.1 No hidden score

P0 uses categorical attributes, not numerical scoring:

- `route_relation`: `direct | indirect | none`
- `check_state`: `unchecked | partial | checked`
- `effort`: `low | medium | high`
- `safety`: `safe | caution | unsafe`
- `urgency_relevance`: `high | normal`

### 9.2 Deterministic priority rules

For ordinary safe cases, selection order is:

1. exclude `unsafe` actions from ordinary recommendation;
2. prefer unresolved checks directly tied to supported case events;
3. prefer `unchecked` or `partial` over a thorough negative check;
4. surface inaccessible portions before pretending a target was fully checked;
5. among otherwise equivalent candidates, prefer lower effort;
6. use habitual locations as weaker planning input than episode-linked locations;
7. use generic suggestions only after supported case-linked candidates are exhausted or absent;
8. if urgency changes the sensible action, fallback/recovery can outrank continued physical search.

No numeric total score is computed or exposed.

### 9.3 User-facing rationale

A next-action explanation should reference the explicit rule basis, for example:

> “Карманы вчерашней куртки связаны с вашим маршрутом и ещё не проверялись. Это короткая безопасная проверка — предлагаю сделать её следующей.”

The explanation must not imply a calibrated chance of success.

---

## 10. Case Controller

### 10.1 Responsibilities

The deterministic Case Controller owns:

- case creation and lifecycle;
- statements;
- timeline state;
- search-check history;
- candidate checks;
- next-action selection;
- urgency/safety constraints;
- pause/resume metadata;
- close outcome;
- case-local persistence and deletion.

### 10.2 Lifecycle

Canonical states:

- `active`
- `paused`
- `closed_found`
- `closed_unresolved`
- `deleted`

`deleted` is a terminal user action for the local case artifact; it is not a historical record retained by the plugin.

### 10.3 No cross-case learning

A saved case can be resumed, but P0 does not aggregate cases into:

- personal priors;
- recurring-location probabilities;
- user-specific habit models;
- automated recommendations for future cases.

Cross-case learning requires a separate design/privacy approval gate.

---

## 11. Case persistence and privacy

### 11.1 Why persistence enters `0.1.0`

`resume` and handoff require durable case state. Therefore P0 includes local case persistence while continuing to exclude cross-case personalization.

### 11.2 Persistence root

When the user explicitly chooses to save/pause a case, the default local representation is:

```text
.mind-detective/
└── cases/
    └── <case-id>/
        └── case.json
```

A single self-contained `case.json` is preferred in MVP over multiple synchronized files.

### 11.3 Persistence rules

- no automatic cloud upload;
- no credentials in case artifacts;
- no hidden chain-of-thought;
- no silent cross-case indexing;
- save/pause must be explicit when persistence is needed;
- delete removes the local case artifact;
- close may retain or delete according to explicit user choice;
- the artifact stores concise rationale and provenance, not private model reasoning.

---

## 12. Resume and handoff

`mind-detective-resume` is a first-class MVP skill.

A resumed/handoff summary must show:

1. what is currently supported;
2. timeline unknowns or contradictions;
3. what has been checked;
4. how each material check was performed;
5. partial/inaccessible areas;
6. current next action;
7. urgency or recovery constraints.

Resume must not reinterpret old data as stronger evidence merely because it survived into a saved file.

A handoff artifact can be read by another person without giving them hidden system reasoning.

---

## 13. Close and outcome

`mind-detective-close` records:

- result: `found | unresolved | abandoned`;
- found location if user reports it;
- which search action immediately preceded the find, if known;
- what the user thinks may have contributed, stored explicitly as user-authored context;
- optional simple prevention action;
- retain/delete choice.

The close step must not infer a forgetting mechanism from the outcome.

Examples of acceptable prevention output:

- choose one consistent storage location;
- add a visible tray/hook;
- attach a tracker to a suitable object;
- create a travel/document checklist.

These are practical suggestions, not diagnoses.

---

## 14. High-risk forgotten-action boundary

The product distinguishes **finding a physical object** from **reconstructing whether a high-risk action happened**.

Supported ordinary case:

> “Где упаковка моего лекарства?”

Unsupported ordinary search reasoning:

> “Я уже принял эту таблетку?”

For medication-dose uncertainty, hazardous equipment state, security-critical actions, or similar high-risk forgotten actions, the assistant must not guess the answer or advise repeating the action solely from uncertain memory.

The router returns a limitation/safe escalation path rather than entering normal reconstruction/search planning.

---

## 15. Skill contracts

### 15.1 `mind-detective`

Default entrypoint.

Responsibilities:

- classify request as physical lost-item search vs unsupported high-risk forgotten action;
- create/open a case;
- capture urgency and constraints;
- route to reconstruct/plan/resume/close.

### 15.2 `mind-detective-reconstruct`

Responsibilities:

- obtain free account first;
- add user statements without confidence inflation;
- neutrally clarify sequence and uncertainty;
- build/update timeline;
- permit “I don't remember”.

### 15.3 `mind-detective-plan`

Responsibilities:

- register candidate checks;
- register performed SearchChecks;
- distinguish superficial/partial/thorough checks operationally through method/result;
- select one next action using categorical rules;
- allow concrete search suggestions while keeping them explicitly suggestions.

### 15.4 `mind-detective-resume`

Responsibilities:

- load explicitly saved case state;
- validate schema/version;
- summarize supported state and search history;
- continue from remaining candidate checks without erasing prior work;
- support human handoff.

### 15.5 `mind-detective-close`

Responsibilities:

- record found/unresolved/abandoned outcome;
- record user-reported find details;
- offer simple prevention if useful;
- retain or delete the saved case according to user choice.

---

## 16. Deterministic runtime modules

P0 implementation should remain focused. Expected plugin-local modules:

- `case.py` — Case model and lifecycle;
- `statements.py` — Statement origin/type validation;
- `timeline.py` — uncertainty-preserving timeline;
- `search_log.py` — SearchCheck model and duplicate history;
- `planner.py` — candidate-check categorization and one-next-action rules;
- `guard.py` — mode-aware reconstruction/search utterance checks;
- `safety.py` — unsupported high-risk forgotten-action boundary;
- `store.py` — explicit local save/load/delete of one case bundle;
- `schemas.py` — schema names and lightweight validation.

No `zones.py`, Bayesian helper, `ach.py`, ModelAdapter, connector runtime, or surface framework is required in P0.

---

## 17. Guard model v2

The primary conversational distinction is mode-aware.

### 17.1 Reconstruction mode

Block:

- assistant-originated recollection/habit/observation;
- new concrete locations embedded in memory-elicitation questions;
- presupposed unsupported events;
- false confirmation language;
- diagnosis of a forgetting mechanism.

### 17.2 Search-planning mode

Allow:

- concrete search suggestions;
- generic candidate locations when clearly proposed;
- suggestions based on item/container compatibility.

Block:

- suggestion phrased as remembered fact;
- probability language presented as location likelihood;
- blame/accusation presented as fact;
- claim that a prior superficial check proves absence.

### 17.3 Generic host limitation

As in v1, repository helpers can mechanically fail closed for submitted candidate utterances, but a generic Claude Code/Codex skill host does not provide a repository-controlled pre-send interceptor. Documentation and evals must not overclaim end-to-end enforcement.

---

## 18. Artifact contracts

P0 normative artifacts should be reduced to three primary schemas:

1. `mind-detective-case/v1` — complete resumable case bundle;
2. `mind-detective-handoff/v1` — concise case transfer summary;
3. `mind-detective-outcome/v1` — close result when exported independently.

`mind-detective-case/v1` contains statements, timeline, search checks, candidates, next action, constraints, lifecycle and outcome.

This replaces the v1 proliferation of transcript/timeline/search-plan/hypothesis/fallback artifacts as independent synchronization surfaces. Internal sections remain structured, but the saved case has one canonical aggregate.

---

## 19. Candidate stable requirements

The implementation plan should formalize at least these P0 requirements:

- `MD-REQ-CASE-01` — one canonical Case Controller owns deterministic case state.
- `MD-REQ-STATEMENT-01` — source and statement type are independent fields.
- `MD-REQ-STATEMENT-02` — assistant cannot originate recollection, habit or observation.
- `MD-REQ-STATEMENT-03` — vividness/confidence/sensory detail do not mechanically promote truth status.
- `MD-REQ-RECONSTRUCT-01` — free account precedes detailed clarification.
- `MD-REQ-RECONSTRUCT-02` — reconstruction questions do not introduce unsupported concrete locations.
- `MD-REQ-RECONSTRUCT-03` — “don't remember” remains explicit uncertainty.
- `MD-REQ-TIMELINE-01` — timeline preserves unknown intervals and contradictions.
- `MD-REQ-SEARCH-01` — each physical check records target, method, result and accessibility state.
- `MD-REQ-SEARCH-02` — repeated checks are not treated as independent probability evidence.
- `MD-REQ-SEARCH-03` — search suggestions may name concrete locations only as proposals, not memories or facts.
- `MD-REQ-SEARCH-04` — one next action is selected without numerical location probability or hidden belief weight.
- `MD-REQ-SEARCH-05` — superficial and thorough checks remain distinguishable in history.
- `MD-REQ-RESUME-01` — saved case resumes without evidence strengthening or history loss.
- `MD-REQ-STORE-01` — persistence is case-local, explicit and deletable.
- `MD-REQ-STORE-02` — P0 does not perform cross-case learning or hidden aggregation.
- `MD-REQ-SAFETY-01` — high-risk forgotten actions do not enter ordinary physical-search reasoning.
- `MD-REQ-CLOSE-01` — outcome records what happened without diagnosing a forgetting mechanism.
- `MD-REQ-EVAL-01` — high-risk behavioral contracts have deterministic tests plus adversarial eval scenarios.
- `MD-REQ-DOCS-01` — key public docs are RU-primary with English mirrors.
- `MD-REQ-RELEASE-01` — one repository SemVer line, independent plugin SemVer, one manifest and one publisher govern releases.

Stable semantics freeze only when released; the v2 implementation plan must trace each high-risk requirement to exact test selectors.

---

## 20. Product evaluation strategy

The product must be testable against simpler alternatives.

### 20.1 Comparative arms

Initial safe studies compare:

- **A — ordinary search**;
- **B — structured checklist/search log**;
- **C — checklist/search log + conversational AI**.

Start with safe staged tasks; analyze voluntary real cases separately.

### 20.2 Metrics

Primary product/safety metrics:

- `time_to_next_useful_action`;
- `duplicate_check_count`;
- perceived task load / convenience;
- `found_rate`, reporting unresolved/abandoned cases separately;
- `unsupported_fact_rate`;
- `leading_suggestion_rate` during reconstruction;
- `false_confidence_rate`;
- resume/handoff completeness.

Do not report only successful-found cases; unresolved/censored cases must remain visible.

### 20.3 Falsifiable decision rule

If conversational AI does not provide practically meaningful benefit over a high-quality structured checklist/search controller, simplify the product to the checklist/controller.

That outcome is treated as valid product evidence, not as project failure.

---

## 21. Scientific/methodological posture

The project uses memory research to define **safety constraints**, not to manufacture household-location probabilities.

P0 may cite research to justify:

- avoiding suggestive/misinforming prompts;
- separating confidence from accuracy;
- using free recall and neutral clarification carefully;
- treating repeated checking as behavior that may affect confidence and cognitive load;
- avoiding unsupported causal claims about forgetting mechanisms.

P0 must clearly label the household lost-item workflow as a product/methodology transfer rather than a clinically or forensically validated recovery protocol.

---

## 22. Repository and release architecture retained from v1

The following architecture remains valid:

- plugin-first independent installability;
- root `.agents/plugins/marketplace.json`;
- root `.claude-plugin/marketplace.json`;
- plugin-local `.codex-plugin/plugin.json`;
- plugin-local `.claude-plugin/plugin.json`;
- Python standard-library-first runtime;
- SDD → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY;
- exact-selector CONTRACT_MATRIX;
- eval vocabulary separating mechanical fixture validation from live semantic evidence;
- full-SHA-pinned GitHub Actions;
- RU/EN documentation parity;
- one declarative `.github/releases/release.json`;
- one active `publish-current-release.yml`;
- immutable published tags/releases;
- exact-head and exact-tag-SHA gates.

The old v1 implementation plan must not be executed because its domain decomposition is now obsolete.

---

## 23. Acceptance criteria for `0.1.0`

Release review can begin only when all are true:

1. One installed plugin exposes exactly the five approved production skills.
2. A case can be created, reconstructed, planned, paused/saved, resumed and closed without network dependencies.
3. Assistant-originated recollection/habit/observation is rejected by deterministic validation.
4. Reconstruction mode blocks unsupported concrete-location elicitation while search-planning mode permits explicit search suggestions.
5. Timeline preserves unknowns and contradictions.
6. Search log differentiates glance/systematic/empty-and-check/tactile/inaccessible checks.
7. Duplicate checks remain visible and are not converted into independent probability evidence.
8. The controller selects one next action through explicit categorical rules with no location probability or hidden belief weight.
9. The user-visible rationale states why the next action was selected without implying certainty.
10. A saved case resumes with the same statements/search history and without automatic evidence strengthening.
11. Local case deletion is supported and no cross-case profile is created.
12. High-risk forgotten-action scenarios exit ordinary search reasoning.
13. Close records outcome without mechanism diagnosis.
14. High-risk requirements have exact deterministic test selectors and adversarial eval coverage.
15. Documentation states the generic-host guard limitation truthfully.
16. RU/EN key docs pass parity checks.
17. CI passes on the exact PR head with pinned Actions and boundary/security checks.
18. Release intent is declared through the single manifest and publication remains human-authorized.

---

## 24. PWA `0.2.0` boundary

The PWA is intentionally a separate vertical slice.

The `0.1.0` core should expose stable serializable Case Controller operations so that a future UI can map naturally to:

```text
conversation
    +
timeline
    +
checked / to-check / inaccessible
    +
one next action
    +
found / pause / resume / delete
```

No frontend framework, IndexedDB adapter, service worker, responsive design system, voice layer or deployment pipeline is created in `0.1.0` merely to anticipate this future slice.

---

## 25. Design decisions final for v2 P0

- Product purpose is systematic lost-item search, not memory restoration.
- Cognitive-load reduction and search-log continuity are the core value proposition.
- One plugin, five skills.
- Case Controller is the deterministic domain center.
- Source and statement type are independent fields.
- Vividness/confidence/sensory detail never mechanically establish truth.
- Reconstruction and search planning have different concrete-location rules.
- Concrete physical search suggestions are allowed when explicitly framed as proposals.
- SearchCheck history is the primary durable domain asset.
- `0.1.0` has no numerical location model, Bayesian update, POD or hidden belief weight.
- Repeated checks are not treated as independent probability evidence.
- One next action is chosen by explicit categorical rules.
- Case-local save/resume/delete is in `0.1.0`; cross-case learning is not.
- High-risk forgotten actions are outside ordinary search reasoning.
- Close records outcome, not mechanism diagnosis.
- Adaptive Web/PWA is deferred to a separate `0.2.0` vertical slice and design gate.
- Existing repository/release hardening patterns from `yandex-ai-plugins-skills` remain the governance baseline.

---

## 26. Transition

After human review and approval of this written v2 spec:

1. the prior v1 implementation plan remains historical and is not executed;
2. a new Superpowers writing-plans pass creates `docs/superpowers/plans/2026-09-09-mind-detective-foundation-v2-implementation.md`;
3. that plan must start from the current empty/bootstrap repository state and use TDD-sized tasks for the simplified Case Controller architecture;
4. production implementation begins only after the v2 plan is complete and handed off through an execution skill.
