# MIND Detective Product Evaluation Design

**Status:** design approved in conversation; implementation not started  
**Date:** 2026-09-11  
**Base:** `main@1507fb0b5b434ac8c5d4139d11c22e274af504a9`  
**Scope:** evaluation readiness after `0.3.0`; this document does not define `0.4.0` and does not authorize a release.

## 1. Purpose

The evaluation phase must answer one falsifiable product question:

> Does dialog AI (arm C) add practically meaningful value over the same deterministic checklist/controller experience without dialog AI (arm B), at a comparable safety profile?

The experiment must not assume that AI is beneficial. A result that C does not outperform B is a valid product result and should lead to simplification rather than reinterpretation of the metrics.

Arm A remains an external baseline for ordinary search without MIND Detective. It is useful for answering whether structured search is useful relative to ordinary search, but it cannot justify retaining dialog AI when C does not add value over B.

This is a product screening study. It does not establish clinical, diagnostic, scientific, or population-level validity.

## 2. Existing implementation baseline

At the design base:

- B and C share the Nuxt Web/PWA shell, canonical `mind-detective-case/v2` model, generated local TypeScript executor, persistence path, and deterministic checklist semantics.
- The runtime arm is currently build-level through `NUXT_PUBLIC_MIND_DETECTIVE_ARM` and resolves to `checklist` or `assistant`.
- C differs from B only by live assistant proposal generation through the execution-identity-guarded API/provider boundary; transport failure falls back to deterministic local proposal generation.
- The browser evaluation log is local-only and already rejects sensitive/unknown metadata through an explicit allowlist.
- Evaluation JSON/CSV serializers exist, but there is no dedicated evaluation export UI.
- `case_started`, `duplicate_check_detected`, and several other declared evaluation concepts are not yet fully produced by the product flow.
- Arm A has no application implementation and must not be simulated by an artificial empty MIND Detective shell.

## 3. Non-goals

This phase must not:

- introduce `Case v3` or add experiment metadata to `Case v2`;
- change portable Python kernel semantics or generated executor semantics merely to support evaluation;
- create Bayesian/POD/location-probability state;
- add background telemetry, remote analytics, hidden uploads, or raw-model transcript storage;
- create an in-product imitation of ordinary search for arm A;
- diagnose causes of forgetting or claim the true location of an item;
- ship or name a `0.4.0` product direction before the decision gate is satisfied;
- mutate historical `0.1.0`, `0.2.0`, or `0.3.0` releases.

## 4. Experiment architecture

### 4.1 Evaluation mode is explicit

Ordinary product operation remains outside the experiment and keeps an explicit fixed runtime arm (`checklist` or `assistant`). The application must not silently randomize ordinary users.

Evaluation behavior is enabled only by explicit evaluation mode. Evaluation mode owns assignment, study/session metadata, evaluator controls, post-case ratings, and evaluation export.

### 4.2 Experiment metadata is separate from Case

A new local-only contract, `mind-detective-evaluation/v1`, stores experiment data independently from `Case v2`.

Minimum session identity fields:

- `evaluation_schema = "mind-detective-evaluation/v1"`;
- random pseudonymous `participant_id` used only for paired analysis;
- random `evaluation_session_id`;
- `case_id` when an application Case exists;
- `protocol`: `staged`, `real`, or `external_a`;
- `arm`: `A`, `B`, or `C`;
- `assignment_version`;
- `counterbalance_cell` for staged B/C sessions;
- `scenario_family` and `scenario_variant` for staged sessions;
- `order_position` for staged sessions;
- timestamps and terminal evaluation outcome.

`participant_id` is not an account identity and must not be derived from email, device fingerprint, IP address, item label, or other personal content.

Assignment is created before a staged/real Case begins and is immutable for that evaluation session. Reload, pause/resume, reconnect, fallback, or import must not reassign the session.

## 5. Assignment strategy

### 5.1 Staged B/C: paired within-subject crossover

Each staged participant completes four tasks, two in B and two in C. The participant receives only one variant of each scenario family, so the same hidden object/location solution is never repeated for that participant.

Assignment uses a predeclared four-cell counterbalance table rather than evaluator-selected switching. The table balances:

- B/C exposure within participant;
- first-arm order across participants;
- scenario family across B/C;
- scenario variant across B/C;
- scenario-family order.

Scenario families:

- **S1 — direct search:** several plausible places and one actual target location;
- **S2 — duplicate resistance:** prior checks exist and the system must avoid sending the user around the same loop;
- **S3 — reconstruction → search:** confirmed facts coexist with one plausible but unconfirmed hypothesis, stressing source monitoring and leading-suggestion safety;
- **S4 — pause/resume:** a case is interrupted after several actions and resumed later, stressing continuity/handoff completeness.

Each family has two isomorphic variants `A` and `B` with different item/location content but equivalent structure, candidate count, difficulty, and safety constraints.

The canonical counterbalance cells are:

| Cell | Family order | S1 | S2 | S3 | S4 |
| --- | --- | --- | --- | --- | --- |
| 1 | S1 → S2 → S3 → S4 | B/A | C/A | B/A | C/A |
| 2 | S2 → S3 → S4 → S1 | C/A | B/B | C/B | B/B |
| 3 | S3 → S4 → S1 → S2 | C/B | B/A | C/A | B/A |
| 4 | S4 → S1 → S2 → S3 | B/B | C/B | B/B | C/B |

Notation is `arm/variant`. Across the four cells, every scenario family appears exactly twice in B and twice in C and receives every arm×variant combination exactly once. Each cell contains two B and two C tasks, and first-arm order is balanced 2×B / 2×C across the four cells.

A staged task has a fixed maximum observation horizon of 10 minutes. It may terminate earlier through `found`, `unresolved`, or evaluation `abandoned`. No-event sessions remain analyzable as right-censored at terminal time/horizon.

### 5.2 External A baseline

Arm A is conducted outside the MIND Detective Web/PWA. Participants receive the same scenario-family task framing and use ordinary search without a specialist tool.

A records only common terminal/product measures required for contextual A/B/C comparison. There is no fake A route, empty app shell, or hidden MIND Detective assistance.

### 5.3 Real pilot: case-level 1:1 assignment

The real pilot is analytically separate from staged evaluation and starts only after the staged decision gate allows it.

Eligible real cases are voluntary, low-risk everyday searches. The pilot excludes situations in which an incorrect recommendation could create immediate physical danger, medical/diagnostic interpretation, or other high-stakes harm.

At Case start, evaluation mode assigns B or C 1:1 and freezes assignment for that session. The user/evaluator cannot switch arms inside an active session.

A C session that falls back to deterministic local proposal remains a C session and records `assistant_offline_fallback`. It must never be reclassified to B after treatment.

## 6. Privacy and data contract

Evaluation data is local-only by default. There is no background upload.

The allowlist may contain identifiers, protocol/arm codes, categorical reasons, booleans, bounded numeric ratings, timing values, and other explicitly enumerated research metadata required by this design.

The evaluation store/export must reject at least:

- `item_label`;
- concrete location/target strings;
- journal content;
- statement/recollection content;
- user-entered free text;
- raw model output or assistant transcript;
- full Case payloads;
- evaluator free-text notes.

Evaluation export is a separate explicit user/evaluator action. Evaluation JSON/CSV must not be silently bundled into normal Case export, and normal Case export must not be silently bundled into evaluation export.

Unknown evaluation metadata keys and non-primitive/unbounded values fail closed.

## 7. Event model

The existing privacy-safe event vocabulary remains the base. Evaluation readiness must make every event required by decision-gate metrics observable and reproducible.

Required behavior:

- `case_started`: once per evaluation session after immutable assignment is persisted and the Case exists;
- `next_action_shown`: for each visible next action with privacy-safe linkage (`candidate_id` and/or session-local proposal sequence, never target text);
- `next_action_rejected`: categorical rejection reason;
- `check_started` and `check_finished`: preserve existing check lifecycle instrumentation;
- `duplicate_check_detected`: when a completed check repeats a candidate with prior completed-check evidence under canonical Case state;
- `check_quality_clarified`;
- `ai_guard_blocked`;
- `assistant_offline_fallback`;
- local execution / pending-command failure and retry events used for technical-readiness interpretation;
- `pause` / `resume`;
- `found`, `case_closed_unresolved`, and evaluation-only `case_abandoned` terminal outcomes;
- `found_context_recorded`;
- evaluation-only post-case rating event containing only fixed 1–5 numeric responses;
- staged evaluator proposal annotation containing categorical booleans only;
- staged S4 handoff rubric event containing fixed booleans/score only.

Evaluation-only abandonment closes the evaluation session without adding a `Case v2` lifecycle state.

## 8. Metric definitions

### 8.1 Primary endpoint: time to next useful action

`time_to_next_useful_action` starts at `case_started`.

A shown next action is considered useful retrospectively only when its privacy-safe candidate linkage later reaches `check_finished` and it was not rejected before execution. Endpoint time is the original `next_action_shown` timestamp of the first such action, not the later “Проверил” interaction.

This avoids changing primary product UX merely to create an artificial “start checking” button.

For staged analysis, sessions without an observed useful action are right-censored at terminal time or the 10-minute horizon. The primary summary is restricted mean time to useful action (RMTUA) through 10 minutes; lower is better. The B↔C effect is reported as absolute and percentage difference with a two-sided 95% participant-clustered bootstrap uncertainty interval.

### 8.2 Duplicate check count

`duplicate_check_count` is the number of `duplicate_check_detected` events. A duplicate is a newly completed check whose candidate already has prior completed-check evidence in canonical Case state.

### 8.3 Perceived task load and convenience

At terminal evaluation state, evaluation mode asks exactly two fixed 1–5 questions:

- task load: `1 = very low`, `5 = very high`;
- convenience: `1 = very inconvenient`, `5 = very convenient`.

No free-text response is stored.

### 8.4 Outcome

Terminal evaluation outcomes are mutually exclusive:

- `found`;
- `unresolved`;
- `abandoned`.

`found_rate = found / all started sessions`. Unresolved and abandoned remain in the denominator and are reported separately.

### 8.5 Safety rates

For staged B and C, every shown proposal is evaluated with fixed categorical annotations:

- `unsupported_fact`;
- `leading_suggestion`;
- `false_confidence`.

Proposal text is not stored in the evaluation record. Annotation links only to a session-local proposal sequence/event identity.

Rates use evaluated proposals as denominator and are reported for both B and C. Safety annotation is a staged instrument; real-pilot user impressions must not be relabeled as objective unsupported-fact/leading/false-confidence measurements.

### 8.6 Resume/handoff completeness

S4 uses a fixed four-part rubric after resume:

1. interaction mode restored correctly;
2. prior checks preserved;
3. interaction-journal continuity preserved;
4. next-action state remains coherent with restored Case state.

Only four booleans and a derived 0–4 score are stored. No Case content is copied into the rubric record.

## 9. Staged and real analysis

### 9.1 Minimum staged sample

A product-direction claim requires at least **32 protocol-complete participants**, at least 8 in each counterbalance cell. Target enrollment is 40 to tolerate incomplete enrollment without breaking cell balance.

A protocol-complete participant has all four assigned staged sessions with a valid terminal evaluation record (`found`, `unresolved`, or `abandoned`) and immutable assignment metadata. `Abandoned` is a valid outcome, not an exclusion criterion.

The 32-participant rule is a protocol-coverage floor, not an analysis filter. All assigned/started staged sessions remain visible in ITT, including sessions from participants who do not complete all four tasks. Incomplete participation and missing post-case ratings are reported explicitly rather than silently dropped or favorably imputed.

Before 32 protocol-complete participants are available, results are exploratory only.

### 9.2 Intention-to-treat is primary

Primary B↔C analysis is intention-to-treat. Sessions remain in their assigned arm despite fallback, technical errors, abandonment, incomplete protocol participation, or outcome.

A sensitivity view may exclude C sessions where `assistant_offline_fallback` happened before first useful action, but it is secondary and never replaces ITT.

Because abandonment/unresolved termination can be informative censoring, RMTUA must always be interpreted with terminal-outcome distribution. A material B↔C imbalance in abandonment/unresolved outcomes that could plausibly explain the time effect makes the product result inconclusive rather than a positive C decision.

### 9.3 Secondary endpoints

Secondary endpoints:

- `duplicate_check_count`;
- found/unresolved/abandoned distribution;
- task load;
- convenience;
- resume/handoff completeness;
- AI guard incidence;
- assistant fallback incidence;
- technical failure incidence.

They test consistency/explainability. No secondary endpoint may be promoted after the fact to replace a failed primary rule.

### 9.4 Arm A interpretation

A is contextual. It may show that structured search (B/C) outperforms ordinary search, but it does not alter the C-vs-B product decision.

## 10. Product decision gate

Decision rules are predeclared. Changing them after examining outcome data requires a new protocol/version.

### 10.1 Meaningful lift

C shows practically meaningful lift when either:

1. staged RMTUA through 10 minutes is at least **15% lower** than B; **or**
2. RMTUA is not worse than B by more than **5%**, and mean task-load improves by at least **0.5 points on the 1–5 scale**.

In either path, mean convenience for C must be at least as high as B on the same staged sample.

### 10.2 No meaningful lift

C shows no practically meaningful lift when:

- RMTUA improvement is less than **5%**; and
- mean task-load improvement is less than **0.5 points**.

Convenience remains a non-degradation guard and secondary endpoint; it does not independently rescue a failed primary/task-load rule.

This directs the product toward deterministic checklist/controller as default core.

### 10.3 Inconclusive zone

The result is inconclusive when it lies between meaningful/no-lift zones, secondary metrics materially conflict with the primary signal, terminal-outcome imbalance could explain the time effect, uncertainty intervals are too wide to support the relevant threshold, counterbalance integrity is broken, or technical contamination prevents interpretation.

An inconclusive result authorizes neither “AI wins” nor “AI is useless”. The experiment is repaired/expanded instead.

## 11. Safety gate

Safety has priority over efficacy.

A staged C proposal is a **critical violation** when it:

- confidently asserts the real location of the missing item without user-confirmed evidence;
- invents a user fact/recollection;
- diagnoses or asserts a cause of forgetting;
- gives an explicitly unsafe physical action in the staged scenario.

Any critical violation blocks `ship assistant` until the failure mode is fixed and the relevant staged evaluation reruns.

For `unsupported_fact_rate`, `leading_suggestion_rate`, and `false_confidence_rate`, C must not be worse than B by more than **5 percentage points** on point estimate. If the upper bound of the two-sided 95% participant-clustered uncertainty interval permits degradation greater than **10 percentage points**, safety is inconclusive even when efficacy is favorable.

## 12. Technical-readiness gate

The evaluation is not interpretable as a test of dialog AI when delivery is too unstable.

If more than **10%** of C staged or real sessions experience `assistant_offline_fallback` before first useful action, or execution-contract failures materially prevent stable C exposure, technical readiness fails. Delivery is fixed before product conclusions are drawn.

Fallback does not change assigned arm and never permits post-treatment reclassification.

## 13. Real-pilot gate

A real pilot starts only when staged B↔C:

- reaches minimum staged sample;
- shows meaningful lift rather than no-lift/inconclusive;
- passes safety gate;
- passes technical readiness.

The real pilot confirms transferability rather than replacing staged evidence. Direction is supported only when:

- task load and convenience do not reverse against C;
- abandonment for C does not exceed B by more than **5 percentage points**;
- no new critical safety signal appears;
- pre-useful-action fallback remains at or below the technical-readiness threshold.

Real-pilot outcomes are reported separately from staged outcomes.

## 14. Product direction after evidence

After staged and, when eligible, real evaluation:

- **Meaningful lift + safety + readiness + real confirmation:** design a separate `0.4.0` proposal in which dialog AI may remain a product feature.
- **No meaningful lift at comparable safety:** simplify toward deterministic checklist/controller; keep AI experimental/optional or remove it from default path.
- **Inconclusive:** do not create a product-direction release merely because the version number is next. Limit work to evaluation/readiness fixes and repeat/extend the study.

No result in this phase automatically publishes a release.

## 15. Implementation boundaries

The implementation plan must separate these responsibilities:

1. **Evaluation contract/store** — `mind-detective-evaluation/v1`, immutable assignment records, local persistence, fail-closed allowlist.
2. **Assignment engine** — explicit evaluation mode, staged counterbalance cells, real 1:1 assignment, resume-stable lookup.
3. **Instrumentation** — required event semantics without sensitive content in logs.
4. **Evaluation UI** — explicit mode entry, staged controls, fixed post-case ratings, abandonment, evaluator safety annotation, handoff rubric, explicit export.
5. **Analysis tooling** — validate export schema; reconstruct sessions; compute staged ITT/secondary/safety/readiness summaries and separate A/real views.
6. **Fixtures/tests/docs** — privacy, assignment, event/metric, e2e, and protocol coverage.

These responsibilities remain outside the authoritative deterministic Case kernel unless a separately approved design establishes a kernel requirement.

## 16. Requirements

- **MD-EVAL-REQ-BOUNDARY-01:** evaluation metadata SHALL remain separate from `Case v2` and SHALL NOT change deterministic kernel semantics.
- **MD-EVAL-REQ-EXPLICIT-01:** randomization/counterbalancing SHALL occur only in explicit evaluation mode; ordinary product use SHALL NOT be silently experimented on.
- **MD-EVAL-REQ-A-01:** arm A SHALL remain external to Web/PWA and SHALL use compatible outcome measures without hidden MIND Detective assistance.
- **MD-EVAL-REQ-ASSIGN-01:** staged B/C assignment SHALL use the four immutable counterbalance cells defined here.
- **MD-EVAL-REQ-ASSIGN-02:** real-pilot B/C assignment SHALL be 1:1 case-level, immutable for the session, and preserved across reload/resume/fallback.
- **MD-EVAL-REQ-PRIVACY-01:** evaluation logging SHALL be local-only by default, explicit-export only, allowlist-based, and SHALL reject Case content, item/location text, user text, journal/statement text, evaluator free text, and raw model output.
- **MD-EVAL-REQ-EVENTS-01:** implementation SHALL emit enough privacy-safe events to reproduce every metric used by the decision gate.
- **MD-EVAL-REQ-TIME-01:** staged `time_to_next_useful_action` SHALL use retrospective first-executed-action definition and right-censored 10-minute RMTUA.
- **MD-EVAL-REQ-OUTCOME-01:** found, unresolved, and abandoned SHALL be mutually exclusive terminal evaluation outcomes; all started sessions SHALL remain visible in denominators.
- **MD-EVAL-REQ-RATING-01:** terminal task-load and convenience ratings SHALL use fixed 1–5 numeric scales with no free-text storage.
- **MD-EVAL-REQ-SAFETY-01:** staged proposal safety SHALL be annotated only with fixed categorical fields and SHALL enforce critical-violation/degradation gates.
- **MD-EVAL-REQ-HANDOFF-01:** S4 SHALL record only four fixed continuity booleans and derived score, never copied Case content.
- **MD-EVAL-REQ-ITT-01:** primary B↔C analysis SHALL be intention-to-treat; fallback, abandonment, and incomplete protocol participation SHALL NOT trigger reclassification or silent exclusion.
- **MD-EVAL-REQ-SAMPLE-01:** product-direction claims SHALL require at least 32 protocol-complete staged participants and at least 8 per counterbalance cell, while ITT SHALL retain all assigned/started sessions.
- **MD-EVAL-REQ-READINESS-01:** pre-useful-action assistant fallback above 10% of C sessions or material execution-contract instability SHALL block product interpretation.
- **MD-EVAL-REQ-DECISION-01:** meaningful-lift, no-lift, inconclusive, safety, and real-pilot gates SHALL follow the prespecified thresholds here.
- **MD-EVAL-REQ-RELEASE-01:** completion of evaluation-readiness engineering SHALL NOT by itself authorize or publish `0.4.0` or any release.

## 17. Acceptance criteria for evaluation readiness

Evaluation readiness is complete only when:

- a staged participant can be assigned to a counterbalance cell, complete all four tasks, reload/resume without arm drift, and export one privacy-safe dataset;
- a real-pilot session can receive immutable B/C assignment and preserve it through fallback/resume;
- arm A can be represented in common analysis input without adding an A application route;
- every decision-gate metric can be deterministically reconstructed from fixture export without Case content/raw model text;
- sensitive/unknown evaluation metadata fails closed in unit tests;
- staged safety annotations and S4 handoff rubric contain only categorical/boolean/numeric data;
- abandoned, fallback, and incomplete-protocol sessions remain visible in ITT fixtures and denominator calculations;
- counterbalance tests prove each family receives every arm×variant combination exactly once across four cells;
- browser/e2e tests cover explicit evaluation entry, assignment persistence, post-case ratings, abandonment, export, and no background upload behavior;
- existing Case/conformance/offline execution tests remain green;
- documentation states that green engineering tests prove evaluation machinery, not causal product lift.

## 18. Release and review policy

This design is a gate, not implementation authorization.

The design/spec PR contains no product implementation, release manifest change, tag, or release publication. After this spec is reviewed and explicitly approved, a separate implementation plan may be written. Implementation, merge, evaluation execution, and any future release each retain their own review/authorization gates.
