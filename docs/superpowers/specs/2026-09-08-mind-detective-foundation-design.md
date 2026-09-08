# MIND Detective Foundation Design

**Status:** Proposed design approved in conversation; written-spec review pending  
**Date:** 2026-09-08  
**Target repository:** `trafficolog/mind-detective`  
**Target first release:** repository `0.1.0`, plugin `mind-detective-v0.1.0`  
**Development method:** SDD + TDD, Superpowers workflow, DRY/KISS/YAGNI  
**Reference architecture:** behavioral/contracts approach proven in `trafficolog/yandex-ai-plugins-skills`

---

## 1. Executive summary

MIND Detective is an evidence-safe methodology runtime for helping a user search for a misplaced item without pretending that an LLM knows where the item is.

The first release is deliberately narrow: one complete **IN_MOMENT** vertical slice for an item lost within minutes or hours. It combines a conversational skill layer with deterministic helpers for evidence classification, question safety, timeline reconstruction, search allocation, competing hypotheses, safety routing, and case debrief.

The core product claim is **not** “AI finds lost things.” The supported claim is:

> MIND Detective helps a user reconstruct what is supported by their own account, avoid memory-contaminating prompts, allocate search effort explicitly, record what has actually been checked, and choose the next bounded action while preserving uncertainty.

The central safety invariant is analogous to exact-preview write safety in `yandex-ai-plugins-skills`: a consequential action must cross a machine-enforced boundary. Here the highest-risk action is not an API mutation; it is an agent question or claim that can contaminate the user's subsequent recollection or turn an uncalibrated heuristic into a false fact.

Therefore the P0 boundary is:

```text
candidate agent question/claim
        ↓
conversation stage policy
        ↓
question_lint / claim guard
        ↓
ALLOW or BLOCK(machine code)
        ↓
user-visible output
```

The first release is plugin-first, independently installable, transport-free, and does not introduce a shared runtime package, external connectors, model SDKs, web UI, voice surface, or cross-case personalization.

---

## 2. Design principles

### 2.1 Behavioral kernel, not a premature shared library

The repository adopts the same lesson as the current Yandex plugin architecture: common architecture is primarily a **specification, stable requirement IDs, schemas, validators, conformance tests, and exact traceability**.

P0 does **not** create a root `kernel/` runtime dependency consumed by the plugin. Executable code stays inside the independently installable `plugins/mind-detective/` boundary until there is demonstrated reuse plus a defined distribution contract.

This prevents formal DRY from breaking installability.

### 2.2 LLM for dialogue; deterministic code for invariants

The LLM may:

- route to a skill;
- summarize user-provided statements without inventing new claims;
- choose among allowed neutral question forms;
- explain limitations;
- present deterministic helper output;
- formulate hypotheses explicitly as hypotheses.

The LLM must not be the source of truth for:

- evidence-class promotion;
- whether a question is safe to send;
- timeline consistency;
- search-weight update math;
- red-flag exit conditions that are mechanically detectable;
- machine reason codes;
- persistent-memory mutation in future releases.

### 2.3 Progressive disclosure

`SKILL.md` files are short discoverable workflow contracts. Longer methodology, citations, examples, and policy live in `references/`. Executable logic lives in `scripts/`; regression coverage lives in `tests/`; adversarial routing/semantic expectations live in `evals/`.

### 2.4 Truthful confidence

The system distinguishes:

- what the user recalls;
- what the user says is habitual;
- what an external source reports;
- what was actually searched;
- what deterministic code infers;
- what remains a hypothesis;
- what is merely methodology.

It never converts an uncalibrated search weight into “probability the item is there.”

### 2.5 Safety before optimization

A faster search is not a success if it is achieved by leading the user, inventing a location, making an accusation, or masking a time-critical fallback.

---

## 3. Product scope

### 3.1 P0 / `0.1.0` in scope

One complete **IN_MOMENT** flow:

```text
router
  → quickcheck
  → interview
  → timeline
  → zones/search allocation
  → first search round
  → hypotheses if unresolved
  → next bounded action or fallback
  → debrief
```

Production skills for `0.1.0`:

1. `mind-detective` — router and safety triage.
2. `mind-detective-quickcheck` — short high-value pre-interview checks.
3. `mind-detective-interview` — free account followed by neutral clarification.
4. `mind-detective-timeline` — reconstruct supported sequence and loss window.
5. `mind-detective-zones` — search allocation and round updates.
6. `mind-detective-hypotheses` — competing-hypothesis matrix after unresolved first round or fixation.
7. `mind-detective-fallback` — time-critical/high-consequence parallel recovery plan.
8. `mind-detective-debrief` — case outcome for the current session; no cross-case baseline mutation in P0.

Deterministic helpers for `0.1.0`:

- `evidence.py`
- `question_policy.py`
- `question_lint.py`
- `timeline.py`
- `zones.py`
- `ach.py`
- `redflags.py`
- `schemas.py`

Repository-level enforcement for `0.1.0`:

- stable requirement IDs;
- plugin validator;
- exact-selector contract matrix;
- eval contract v2;
- AST boundary tests;
- RU-primary + EN mirror key docs;
- secret scanning;
- pinned GitHub Actions;
- declarative release manifest;
- one hardened publisher.

### 3.2 Explicitly out of scope for `0.1.0`

The following are intentionally deferred rather than scaffolded as empty abstractions:

- `.mind-detective/` cross-case Project Memory;
- personal priors or learned household base rates;
- `mind-detective-longterm`;
- prospective-memory workflow (“did I lock/take/send?”);
- prevention/habit redesign as a separate skill;
- external evidence connectors (EXIF, calendar, messages, cloud APIs);
- MAX/VK/Telegram/voice/web adapters;
- `ModelAdapter` provider abstraction;
- model API credentials;
- live multi-model benchmark;
- calibrated location probabilities;
- floor-plan modeling;
- automated ingestion of photos or private files;
- medical diagnosis or cognitive assessment;
- law-enforcement or theft investigation workflow.

Each deferred capability requires a separate design/spec gate.

---

## 4. Canonical naming

To avoid namespace drift:

- Repository: `mind-detective`
- Product display name: **MIND Detective / Детектив памяти**
- Plugin: `mind-detective`
- Future privileged connector plugin: `mind-detective-connectors`
- Future local memory root: `.mind-detective/`
- Machine schema prefix: `mind-detective-*`
- Machine reason-code prefix: `MD_`

The earlier working label `memory-detective` is not used as a second runtime namespace.

---

## 5. Repository architecture

Target repository shape after P0 implementation:

```text
mind-detective/
├── .agents/
│   └── plugins/marketplace.json
├── .claude-plugin/
│   └── marketplace.json
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   ├── releases/
│   │   ├── release.json
│   │   └── 0.1.0.md
│   └── workflows/
│       ├── ci.yml
│       ├── methodology-freshness.yml
│       └── publish-current-release.yml
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── README.en.md
├── CHANGELOG.md
├── CHANGELOG.en.md
├── CONTRIBUTING.md
├── SECURITY.md
├── SECURITY.en.md
├── LICENSE
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ARCHITECTURE.en.md
│   ├── PLUGIN_STANDARD.md
│   ├── PLUGIN_STANDARD.en.md
│   ├── RELEASE_POLICY.md
│   ├── RELEASE_POLICY.en.md
│   ├── GETTING_STARTED.md
│   ├── GETTING_STARTED.en.md
│   ├── METHODOLOGY.md
│   ├── METHODOLOGY.en.md
│   ├── REQUIREMENTS.md
│   ├── SDD_TDD_WORKFLOW.md
│   ├── PRIVACY.md
│   ├── RISK_REGISTER.md
│   ├── GLOSSARY.md
│   ├── GLOSSARY.en.md
│   ├── CONTRACT_MATRIX.json
│   ├── EVAL_TOKEN_REGISTRY.json
│   ├── schemas/
│   ├── adr/
│   ├── reviews/
│   └── superpowers/
│       ├── specs/
│       └── plans/
├── plugins/
│   └── mind-detective/
│       ├── .agents-plugin/plugin.json
│       ├── .claude-plugin/plugin.json
│       ├── README.md
│       ├── README.en.md
│       ├── CHANGELOG.md
│       ├── CHANGELOG.en.md
│       ├── THIRD_PARTY_NOTICES.md
│       ├── skills/
│       ├── references/
│       ├── scripts/
│       ├── tests/
│       └── evals/
├── scripts/
│   ├── validate_repo.py
│   ├── contract_controls.py
│   ├── bilingual_docs.py
│   └── release_manifest.py
├── tests/
│   ├── test_boundaries.py
│   ├── test_contract_matrix.py
│   ├── test_eval_contract.py
│   └── test_release_contract.py
└── pyproject.toml
```

P0 may implement the tree incrementally under TDD; no empty directory is required merely to match the diagram.

---

## 6. Layer boundaries

### 6.1 P0 layers

```text
L3  skills / orchestration
    routing, interview stages, presentation, limitation propagation

L2  deterministic domain helpers
    evidence, question guard, timeline, zones, ACH, redflags

L1  repository contracts
    schemas, requirement IDs, validators, contract matrix, eval vocabulary
```

There is intentionally no transport layer in P0.

### 6.2 Boundary invariant

`plugins/mind-detective` P0 core must not import network SDKs, browser clients, cloud storage clients, messenger clients, or external connector implementations.

Repository AST checks will enforce a denylist of privileged/network modules appropriate to the Python codebase. The denylist is a repository policy, not a claim that AST scanning proves absence of all possible I/O.

The future `mind-detective-connectors` plugin will be a separate independently installable boundary and will produce only structured `EXTERNAL` evidence artifacts with provenance.

---

## 7. Evidence model

### 7.1 Classes

P0 uses these canonical classes:

| Class | Meaning | Allowed origin |
|---|---|---|
| `USER_RECALLED` | User reports an episodic memory or recollection | user statement only |
| `HABITUAL` | User reports a routine, usual placement, or schema | user statement only |
| `USER_STATED` | User supplies context such as item properties, deadline, constraints | user statement only |
| `EXTERNAL` | Evidence supplied by a future external connector or explicit file parser | not produced by P0 core |
| `SEARCHED` | A zone/search method/result actually reported for a search round | user-confirmed search action |
| `INFERRED` | Deterministic conclusion derived from supported inputs by a named rule | helper only |
| `HYPOTHESIS` | Testable explanation that remains unconfirmed | agent or user, explicitly labeled |
| `METHODOLOGY` | General research/methodological principle, never a fact about this case | references/methodology |

### 7.2 Statement metadata

A normalized statement carries at least:

```json
{
  "id": "stmt-...",
  "text": "...",
  "class": "USER_RECALLED",
  "author": "user",
  "created_at": "RFC3339 timestamp",
  "elicited_by": "question-id or null",
  "detail_level": "LOW|MEDIUM|HIGH",
  "confidence_self": "LOW|MEDIUM|HIGH|UNSTATED",
  "limitations": []
}
```

`confidence_self` is the user's self-report, not an estimated probability of truth.

### 7.3 Non-promotion invariants

1. The agent cannot originate `USER_RECALLED`, `HABITUAL`, or `USER_STATED` statements on the user's behalf.
2. `HABITUAL` cannot be promoted to `USER_RECALLED` because it is repeated, plausible, or high-confidence.
3. Sensory/contextual detail may be recorded as metadata but does not mechanically certify truth.
4. Absence of recall does not become evidence that an event did not happen.
5. `METHODOLOGY` cannot directly satisfy a case-specific evidence requirement.
6. `HYPOTHESIS` remains a hypothesis until a supported rule or new evidence changes the case state.

---

## 8. Interview and memory-contamination boundary

### 8.1 Scientific posture

The project uses cognitive-interview principles as **transferred methodology**, not as proof that a forensic protocol has been validated for household lost-item recovery.

Supported design implications include:

- obtain a free account before detailed clarification;
- reinstate context in neutral terms;
- encourage retrieval without rewarding a particular answer;
- avoid misleading post-event information;
- preserve provenance of how a statement was elicited.

The repository must not claim that this adaptation has a validated effect size for finding household objects unless the project later obtains direct evidence.

### 8.2 Question stages

Canonical interview stages:

1. `FREE_ACCOUNT`
2. `CONTEXT_RECONSTRUCTION`
3. `TIMELINE_CLARIFICATION`
4. `CONTRADICTION_CLARIFICATION`
5. `SEARCH_FOLLOWUP`

The stage determines which question forms are allowed.

### 8.3 Guard architecture

`question_policy.py` defines stage-aware allowed forms and structural constraints.

`question_lint.py` inspects a concrete candidate question and returns a structured result:

```json
{
  "allowed": false,
  "codes": ["MD_Q_NEW_LOCATION"],
  "details": []
}
```

A blocked question is never sent unchanged. The orchestration layer must reformulate or choose another allowed prompt.

### 8.4 P0 question/claim rules

| Code | Invariant |
|---|---|
| `MD_Q_NEW_LOCATION` | Do not introduce a concrete location/container not already supplied by the user as case data. |
| `MD_Q_CLOSED_FREE_ACCOUNT` | During `FREE_ACCOUNT`, do not use a closed yes/no question when an open neutral prompt can collect the account. |
| `MD_Q_MULTI` | Ask one material question at a time. |
| `MD_Q_PRESUPPOSITION` | Do not presuppose an unsupported action, location, cause, or person. |
| `MD_Q_THIRD_PARTY_BLAME` | Do not formulate a named/role-based accusation as a hypothesis. |
| `MD_CLAIM_UNSUPPORTED_LOCATION` | Do not state or imply that the item is in a specific unsupported location. |
| `MD_CLAIM_UNCALIBRATED_PROBABILITY` | Do not present search weights as calibrated probabilities of location. |

The linter is intentionally conservative. Semantic edge cases not mechanically detectable remain covered by evals and review; documentation must not claim total prevention of suggestive questioning.

---

## 9. Timeline model

### 9.1 Goal

Construct the smallest supported sequence between:

- the **last supported contact** with the item; and
- the first supported observation that the item was missing.

“Supported” is used instead of “confirmed” because a user's recollection is evidence supplied by the user, not independently verified fact.

### 9.2 `timeline/v1`

The normative artifact is `mind-detective-timeline/v1` with fields conceptually equivalent to:

```json
{
  "schema": "mind-detective-timeline/v1",
  "last_supported_contact": {"statement_id": "...", "class": "USER_RECALLED"},
  "first_noticed_missing": {"statement_id": "..."},
  "loss_window": {"start": "...", "end": "...", "precision": "..."},
  "events": [],
  "gaps": [],
  "contradictions": [],
  "limitations": []
}
```

### 9.3 Timeline invariants

- A habitual statement alone cannot establish `last_supported_contact`.
- Missing timestamps remain unknown rather than fabricated.
- Contradictions are surfaced; the helper does not silently choose one version.
- Event boundaries may be annotated but do not automatically increase a location score.
- Impossible ordering/overlap detected from explicit times is a structured error/finding, not an exception traceback.

---

## 10. Event boundaries and methodology discipline

The project distinguishes **event segmentation** from a simplistic “doorway = forgetting” rule.

Evidence supports the broader proposition that event boundaries can affect memory organization and accessibility. However, the precise effects of physical doorways depend on task and experimental conditions, and the literature does not justify a universal household-search prior.

Therefore in P0:

```text
event_boundary
  → METHODOLOGY cue
  → may motivate a neutral reconstruction question
  → may contribute to a HYPOTHESIS reason
  → does NOT automatically increase a search-zone weight
```

No code path may implement `doorway => +X%` or equivalent.

---

## 11. Search allocation model

### 11.1 Goal

The search helper allocates attention among candidate zones; it does not predict the item's true location.

### 11.2 Zone artifact

Normative artifact: `mind-detective-search-plan/v1`.

A zone contains:

```json
{
  "id": "zone-...",
  "label": "user-derived categorical label",
  "belief_weight": 0.0,
  "weight_reasons": [],
  "effort": "LOW|MEDIUM|HIGH",
  "rounds": [],
  "calibration_status": "UNCALIBRATED"
}
```

The plan includes an explicit `UNKNOWN_OR_OUTSIDE` remainder when appropriate.

### 11.3 Where initial weights may come from

P0 weights may be assigned from explicit transparent rules based on:

- user-recalled interactions;
- user-stated habitual placement, capped as weaker evidence;
- physical/logical containment from supported timeline facts;
- search status;
- explicit unknown remainder.

P0 does **not** use population statistics presented as personalized probability.

Exact numeric constants, if any are needed internally, are repository policy parameters and must be labeled uncalibrated. They are not scientific claims.

### 11.4 Updating after a search round

Search theory motivates the general principle that failing to detect a target after a search reduces but does not necessarily eliminate belief that it is in the searched area.

P0 therefore implements a deterministic miss-factor update:

```text
weight_after_raw = weight_before × miss_factor(search_method)
normalize(all zone weights + UNKNOWN_OR_OUTSIDE)
```

`miss_factor` is an operational search-coverage parameter, not a validated household probability of detection.

### 11.5 Public presentation invariant

The user-facing layer may say:

- “this zone remains higher priority than that one because…”;
- “a quick glance should reduce priority less than a systematic empty-and-replace search”;
- “this is an uncalibrated search weight used to order effort.”

It may not say:

- “73% chance your keys are there”;
- “scientifically, this location is most likely”;
- “three searches prove it is not there.”

---

## 12. Competing hypotheses

### 12.1 Purpose

The hypothesis matrix exists to reduce fixation on one story, especially after an unsuccessful first round.

### 12.2 P0 hypothesis families

Candidate families are categorical and non-accusatory, for example:

- item remained within the current closed system;
- item left the current system during the loss window;
- item was moved after the user's last supported contact;
- user recalled a habitual sequence rather than the actual episode;
- item is currently in an already searched zone but was missed;
- current evidence is insufficient.

The agent may add a case-specific hypothesis only if it is explicitly labeled `HYPOTHESIS` and includes what would support or weaken it.

### 12.3 Third-party invariant

The system does not turn “someone may have moved it” into “your spouse/child/colleague moved it” unless the user independently supplies specific evidence and the wording remains non-accusatory. Even then, the tool's goal is evidence collection, not blame assignment.

---

## 13. Safety routing and fallback-first behavior

### 13.1 Red-flag categories

The router exits or limits the ordinary investigative flow for functional/safety signals rather than age alone.

P0 categories include:

- disorientation or inability to account for how the user arrived somewhere;
- sudden or progressive confusion materially affecting safety;
- a missing person;
- suspected theft with meaningful safety/financial/legal harm;
- uncertainty around critical medication use where re-dosing may be unsafe;
- time-critical identity/travel/legal documents;
- immediate physical danger.

The tool does not diagnose a medical condition or adjudicate a crime.

### 13.2 Fallback-first

For high-consequence/time-critical items, the fallback skill runs **before** an extended search strategy.

Examples:

- passport + imminent travel → official recovery/replacement contingencies plus bounded search;
- medication uncertainty → safe escalation guidance rather than guessing whether a dose was taken;
- vehicle/house keys with security exposure → security contingency in parallel with search.

Specific jurisdictional or medical instructions are not hard-coded in P0 methodology references unless sourced and freshness-controlled.

---

## 14. Skill contracts

### 14.1 Router

`mind-detective` is the only default entrypoint.

Routing order:

1. safety/red flag;
2. high-consequence fallback requirement;
3. IN_MOMENT support;
4. unsupported/deferred workflow disclosure.

Requests for LONG_TERM or PROSPECTIVE flows in `0.1.0` receive a truthful limitation rather than silently routing through the wrong methodology.

### 14.2 Quickcheck

A bounded pre-interview step intended to prevent unnecessary cognitive load.

It may use only generic self-check categories that do not become claims about the item, such as verifying whether the item is currently on the user's person or already in active use. It must not enumerate a long list of specific household locations.

### 14.3 Interview

Free account first; neutral clarification second. Every agent-generated question passes the guard.

Output: `mind-detective-recall-transcript/v1`.

### 14.4 Timeline

Consumes transcript evidence, preserves provenance, surfaces gaps/contradictions.

Output: `mind-detective-timeline/v1`.

### 14.5 Zones

Consumes supported timeline + user evidence + prior search rounds. Creates or updates an uncalibrated search-allocation artifact.

Output: `mind-detective-search-plan/v1`.

### 14.6 Hypotheses

Required after an unresolved first structured search round or when the user is fixated on one explanation.

Output: `mind-detective-hypothesis-matrix/v1`.

### 14.7 Fallback

Produces a parallel contingency plan when consequence/time dominates continued search.

Output: `mind-detective-fallback-plan/v1`.

### 14.8 Debrief

Records current-session outcome only.

Output: `mind-detective-case-outcome/v1`.

P0 does not silently persist personal baselines across cases.

---

## 15. Artifact contracts

P0 normative schemas:

1. `mind-detective-recall-transcript/v1`
2. `mind-detective-timeline/v1`
3. `mind-detective-search-plan/v1`
4. `mind-detective-hypothesis-matrix/v1`
5. `mind-detective-fallback-plan/v1`
6. `mind-detective-case-outcome/v1`

Every artifact includes:

- `schema`;
- generated timestamp;
- case-local identifier;
- source/provenance references where applicable;
- `limitations`;
- no secrets;
- no hidden chain-of-thought.

Artifacts contain concise structured rationale/reason codes, not private model reasoning.

---

## 16. Stable P0 requirements

The canonical `docs/REQUIREMENTS.md` created during implementation will assign at least these IDs; their semantics are frozen once released.

| ID | Requirement |
|---|---|
| `MD-REQ-EVIDENCE-01` | Agent cannot originate a user recollection. |
| `MD-REQ-EVIDENCE-02` | `HABITUAL` never promotes to `USER_RECALLED`. |
| `MD-REQ-EVIDENCE-03` | Missing recall is not negative evidence by default. |
| `MD-REQ-EVIDENCE-04` | Methodology cannot be presented as case-specific observation. |
| `MD-REQ-QUESTION-01` | Every generated interview question crosses the guard boundary before user display. |
| `MD-REQ-QUESTION-02` | Unsupported concrete locations are not introduced as questions or claims. |
| `MD-REQ-QUESTION-03` | Free-account stage rejects closed leading collection patterns. |
| `MD-REQ-QUESTION-04` | Named third-party blame is not generated as an investigative hypothesis. |
| `MD-REQ-TIMELINE-01` | Last supported contact preserves its evidence class and cannot be established by habit alone. |
| `MD-REQ-TIMELINE-02` | Timeline contradictions and unknowns remain explicit. |
| `MD-REQ-SEARCH-01` | Search miss reduces rather than silently zeroes a zone weight. |
| `MD-REQ-SEARCH-02` | Uncalibrated weights are never presented as calibrated location probabilities. |
| `MD-REQ-SEARCH-03` | Unknown/outside remainder remains representable. |
| `MD-REQ-SEARCH-04` | Event boundary alone does not mechanically boost a zone weight. |
| `MD-REQ-HYPOTHESIS-01` | Hypotheses remain explicitly labeled and testable. |
| `MD-REQ-SAFETY-01` | Supported red flags exit/limit ordinary investigative flow. |
| `MD-REQ-SAFETY-02` | High-consequence/time-critical cases run fallback-first. |
| `MD-REQ-BOUNDARY-01` | P0 core remains transport/connector-free. |
| `MD-REQ-EVAL-01` | High-risk contracts have exact test traceability and adversarial eval coverage. |
| `MD-REQ-DOCS-01` | Key public docs are RU-primary with EN mirror and reciprocal navigation. |
| `MD-REQ-RELEASE-01` | One repository SemVer line and one declarative publisher govern releases. |

Every normative MUST/never in production docs is either mechanically traced (`[enforced: ...]`) or explicitly marked review/policy (`[unenforced: ...]`).

---

## 17. Contract matrix

`docs/CONTRACT_MATRIX.json` starts at exact-function traceability, equivalent in intent to the hardened v2 contract in the reference Yandex repository.

Each high-risk entry links:

```text
stable requirement ID
  → owning SKILL.md
  → helper path
  → exact Python test selector
  → relevant reference/methodology source
```

Example intent:

```text
MD-REQ-QUESTION-02
  → skills/mind-detective-interview/SKILL.md
  → scripts/question_lint.py
  → tests/test_question_lint.py::test_rejects_new_concrete_location
  → references/question-rules.md
```

Repository validation verifies structural traceability and exact selector existence via AST. It does not claim to prove the semantic quality of the test assertion; runtime tests and review remain separate evidence.

---

## 18. Eval contract

P0 adopts `evals/scenarios.json` version 2 semantics:

- exact `must_route_to`;
- `outcome ∈ {comply, comply_with_limitations, refuse}`;
- exact registered `must_mention_tokens` only for machine vocabulary;
- natural-language `must_convey`;
- semantic `must_not_claim`.

Initial adversarial coverage includes at least:

1. “Just tell me where my keys are.”
2. User reports “I always put them there” as if it proved the episode.
3. Agent attempts a new location in a question.
4. Agent attempts a synonymous leading question.
5. User blames spouse/child/colleague.
6. Three quick searches are treated as proof of absence.
7. Request for a percentage probability by location.
8. Passport with imminent travel.
9. Medication uncertainty.
10. Disorientation/red-flag signal.
11. Event-boundary cue requested as scientific proof of location.
12. Unresolved first round requiring hypotheses.

Repository CI validates eval structure, token registry, routes, and referenced skills. Unless an executable subject/judge runner is later introduced, green CI does not claim that a model semantically passed these scenarios.

---

## 19. SDD + TDD workflow

The repository formalizes the following development loop:

```text
SPEC
  stable requirement / schema / ADR change
        ↓
RED
  exact failing regression test
        ↓
GREEN
  minimum implementation satisfying the contract
        ↓
REFACTOR
  preserve behavior and boundaries
        ↓
TRACE
  exact CONTRACT_MATRIX selector
        ↓
EVAL
  adversarial routing/semantic fixture where applicable
        ↓
VERIFY
  validator + tests + lint + typecheck + security/release checks
```

Rules:

1. No production behavior is added before a failing test where deterministic testing is applicable.
2. A high-risk guard requires at least one normal test and one bypass/adversarial negative test.
3. Machine errors carry stable codes; tests that only assert “an exception happened” are insufficient for high-risk contracts.
4. Documentation is not allowed to claim stronger enforcement than tests/CI actually provide.
5. Green CI is mechanical evidence, not proof of scientific validity or model semantic behavior.

---

## 20. CI design

Initial CI jobs should cover:

- Python syntax/compile;
- `ruff`;
- `mypy` for typed executable code;
- `pytest`;
- repository validator;
- plugin/skill metadata validation;
- JSON schema validation;
- exact contract-matrix validation;
- eval registry/vocabulary validation;
- AST boundary checks;
- bilingual-doc parity checks;
- changelog release-marker parity;
- secret scan / `gitleaks`;
- release-manifest validation;
- full-SHA pinning check for third-party GitHub Actions.

Third-party Actions are pinned to immutable full commit SHAs. Dependabot may propose action-version updates, but mutable major tags are not accepted in the active workflow set.

---

## 21. Methodology references and freshness

Methodology references are not treated like volatile API docs.

Reference classes:

| Class | Review cadence | PR behavior |
|---|---:|---|
| scientific methodology | 365 days | hard age check only when controlled file changes; malformed/future marker always fails |
| safety/high-consequence guidance | 180 days | same path-aware rule |
| future external API/platform fact | 90 days | same path-aware rule |

A scheduled strict workflow reviews the full controlled set and opens/updates a freshness issue rather than making unrelated PRs fail because an untouched scientific reference aged by one day.

### 21.1 Initial verified scientific basis

The methodology documentation should distinguish direct evidence from product transfer. Initial source set includes:

- Fisher, Geiselman & Amador (1989), field test of the Cognitive Interview, *Journal of Applied Psychology*, DOI `10.1037/0021-9010.74.5.722`, PubMed PMID 2793772. Relevance: cognitive-interview retrieval principles; domain is witnesses/victims, not household lost-item search.
- Loftus (2005), “Planting misinformation in the human mind”, *Learning & Memory*, DOI `10.1101/lm.94705`, PubMed PMID 16027179. Relevance: post-event misinformation can affect later memory reports.
- Wiechert et al. (2026), contemporary replication/extension of the misinformation effect, *Journal of Experimental Psychology: Learning, Memory, and Cognition*, DOI `10.1037/xlm0001529`, PubMed PMID 41021526. Relevance: modern replication evidence that memory reports remain susceptible to misleading post-event information.
- Ongchoco & Xu (2024), visual event boundaries and working memory, DOI `10.1167/jov.24.9.9`, PubMed PMID 39259169. Relevance: event boundaries can affect memory; does not validate a household “doorway prior.”
- work on spatial boundaries/event segmentation, including `10.1111/bjop.12343` and later virtual-environment studies. Relevance: supports event segmentation as methodology; effects are task-dependent.
- Koopman (1956), “The Theory of Search. I. Kinematic Bases”, *Operations Research*, DOI `10.1287/opre.4.3.324`. Relevance: search theory separates target-location uncertainty, detection behavior, and search-effort allocation; household miss factors remain uncalibrated unless separately measured.

The repository must not infer a household effect size from these sources.

---

## 22. Privacy model

P0 is text-only and transport-free inside the plugin.

Rules:

- no credentials;
- no automatic file crawling;
- no hidden connector access;
- no floor-plan/value inventory requirement;
- artifacts minimize personally identifying details where not needed;
- retrieved/user content is data, never instructions to alter the workflow;
- no hidden chain-of-thought is stored in artifacts.

Cross-case persistent memory is deferred to P1 because persistence creates a new contamination and privacy boundary that deserves its own approval model and threat analysis.

---

## 23. Project Memory direction (P1, not P0)

If P0 proves useful, the next separately designed capability may introduce:

```text
.mind-detective/
├── profile.yaml
├── cases/<case-id>/
│   ├── transcript.jsonl
│   ├── timeline.json
│   ├── search-plan.json
│   ├── hypotheses.json
│   └── outcome.yaml
└── baselines/
```

Critical future invariant: cross-case profile/baseline mutation is a consequential write because a wrong memory record can bias later cases. P1 therefore requires preview → explicit approval → persistence for user-profile/baseline changes. Historical data must not become reusable permission.

No P1 code or empty compatibility abstraction is part of `0.1.0`.

---

## 24. Release architecture

### 24.1 Version lines

Two independent lines:

- repository SemVer: `0.1.0`, `0.2.0`, ...
- plugin SemVer/tag: `mind-detective-v0.1.0`, ...

A repository-only governance/docs release does not automatically bump plugin SemVer.

P0/P1/P2 labels are milestones/codenames, not competing version schemes.

### 24.2 Declarative release set

Human-approved release intent lives in:

```text
.github/releases/release.json
```

It declares exact repository release metadata and an explicit plugin release list. Changed files do not silently authorize plugin publication.

### 24.3 Single publisher

The only active automatic publisher on the default branch is:

```text
.github/workflows/publish-current-release.yml
```

A new release modifies the manifest/notes/version surfaces; it does not add another release workflow.

### 24.4 Publication gates

```text
feature/design PR
  → exact-head CI
  → semantic/review evidence
  → human merge authorization
  → post-merge exact-main CI
  → human-approved release intent
  → publisher
  → exact tag-SHA validation
  → immutable GitHub Release
```

The publisher must fail closed on ambiguous/conflicting tag/release state, stale initial publication state, or inability to establish safe recovery. Published history is immutable; a correction receives a new version rather than retargeting an old tag.

---

## 25. Planned release sequence

This is a decision framework, not a commitment to implement every stage.

### `0.1.0` — P0 Core Detective

- IN_MOMENT vertical slice;
- evidence contracts;
- question/claim guards;
- timeline;
- uncalibrated search allocation;
- hypotheses;
- fallback/debrief;
- offline eval contract;
- SDD/TDD/release governance.

### `0.2.0` candidate — P1 Case Memory

Only if P0 gives evidence that resumability/personal baselines add value:

- `.mind-detective/`;
- persistent cases;
- approval-bound cross-case profile updates;
- contamination-safe personal baselines.

### `0.3.0` candidate — Long-term workflow

Only after separate methodology review:

- long-term recall workflow;
- cue rotation;
- handoff;
- prevention/debrief extensions.

### Later candidates

- executable provider-neutral eval benchmark;
- opt-in external-evidence connector plugin;
- product surfaces such as bot/web/voice.

`1.0.0` is reserved for stabilized public contracts supported by real pilot evidence, not merely completion of a feature checklist.

---

## 26. ADR set for foundation implementation

The implementation plan will create these initial ADRs:

1. **ADR-001 — Behavioral kernel and plugin-local runtime**  
   No premature shared runtime package; conformance is repository-owned.
2. **ADR-002 — Evidence classes and non-promotion rules**  
   Separate user recall, habit, search observations, inference, hypothesis, methodology.
3. **ADR-003 — Question/claim guard as the primary safety boundary**  
   Stage-aware policy + machine-coded linter + adversarial evals.
4. **ADR-004 — Uncalibrated search allocation**  
   Search weights are effort-ordering devices, not household location probabilities.
5. **ADR-005 — Transport-free P0 and deferred connectors**  
   No external file/network connector inside the core plugin.
6. **ADR-006 — SDD/TDD exact traceability**  
   Stable requirement IDs + exact test selectors + truthful enforcement labels.
7. **ADR-007 — Release governance**  
   One repository SemVer line, independent plugin SemVer, one manifest, one publisher, immutable history.
8. **ADR-008 — P0 non-goals / YAGNI boundary**  
   No Project Memory, long-term, prospective, model adapters, product surfaces, or calibrated probabilities in `0.1.0`.

---

## 27. Acceptance criteria for the design implementation

The `0.1.0` implementation is ready for release review only when all of the following are true:

1. A user can traverse the IN_MOMENT flow end-to-end using the installed plugin without network dependencies.
2. Every interview question in the production workflow is passed through the guard interface.
3. Negative tests demonstrate blocking of unsupported new-location prompts and pseudo-probability claims.
4. Evidence normalization cannot promote habit to recall or create user recall from agent text.
5. Timeline artifacts preserve unknowns and contradictions.
6. Search-round updates reduce rather than erase a searched zone unless explicit case evidence establishes impossibility by a separately documented deterministic rule.
7. No user-facing artifact presents uncalibrated weights as location probability.
8. Event-boundary annotations do not directly change zone weights.
9. High-consequence/red-flag eval scenarios route to limitation/exit/fallback behavior.
10. Every high-risk contract in `CONTRACT_MATRIX.json` names an exact test selector that exists and runs in CI.
11. Eval v2 fixtures validate structurally and include bypass/adversarial cases.
12. Core AST boundary tests pass with no network/connector dependency.
13. RU/EN key docs and changelog markers pass parity validation.
14. Third-party Actions in active workflows are pinned to full immutable SHAs.
15. Release manifest/publisher tests prove a single declarative release path and fail-closed conflicting-state semantics.
16. CI is green on the exact PR head.
17. Review evidence explicitly separates mechanical CI success from semantic/scientific/product validation.
18. Human authorization is required before merge and before publication of the declared release set.

---

## 28. Risks and mitigations

| Risk | Mitigation |
|---|---|
| LLM contaminates user recollection | machine question/claim guard + free-account stage + adversarial evals |
| Linter creates false confidence | docs explicitly scope mechanical coverage; semantic eval/review remains separate |
| Household probabilities look scientific | `UNCALIBRATED` schema status; user-facing probability claim prohibited |
| “Doorway effect” becomes cargo-cult rule | event boundary cannot mechanically boost weight; methodology-only treatment |
| Habit mistaken for episode | non-promotion contract and provenance-preserving schemas |
| User fixates on blame | neutral competing hypotheses + third-party-blame guard |
| Search becomes endless | bounded next actions, fallback-first for consequential cases, unresolved-state support |
| Architecture becomes a framework before product evidence | P0 one plugin, no shared runtime package, no model/surface abstractions |
| Future memory contaminates later cases | persistence deferred to separate P1 approval design |
| CI/release process drifts | stable requirements, exact traceability, declarative manifest, single publisher |

---

## 29. Design decisions that are intentionally final for P0

To remove implementation ambiguity, P0 fixes the following decisions:

- Python is the executable helper language.
- The plugin is independently installable and transport-free.
- There is no root shared runtime dependency.
- The agent cannot create `USER_RECALLED` on behalf of the user.
- Sensory detail is metadata, not an automatic truth-certification rule.
- “Last supported contact” replaces “last confirmed contact” when evidence is only user-reported.
- Event boundaries are methodology cues, not numeric priors.
- Search weights are explicitly uncalibrated and are not exposed as location probabilities.
- Search miss uses a deterministic multiplicative reduction model; constants are operational policy, not scientific facts.
- No persistent cross-case personal baseline exists in P0.
- No connector/model/surface abstraction is scaffolded in P0.
- High-risk contracts use exact-function test traceability from the first release.
- Repository release publication uses one declarative manifest and one publisher.

---

## 30. Implementation transition

After human review of this written design, the next Superpowers step is a separate implementation plan under:

```text
docs/superpowers/plans/2026-09-08-mind-detective-foundation-implementation.md
```

That plan will decompose the work into TDD-sized commits/PR checkpoints, including exact test-first sequences, documentation surfaces, CI/bootstrap order, and release staging.

No production implementation should be committed before that implementation plan is approved for execution.
