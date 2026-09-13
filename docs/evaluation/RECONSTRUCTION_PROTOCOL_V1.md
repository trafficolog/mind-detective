# Reconstruction Research Protocol v1

**Schema:** `mind-detective-reconstruction-research/v1`  
**Status:** research-only protocol freeze; not a production assistant contract  
**Base release:** `0.4.0`  
**Case contract:** `mind-detective-case/v2` remains unchanged

This document is the human-review companion to [`RECONSTRUCTION_PROTOCOL_V1.json`](RECONSTRUCTION_PROTOCOL_V1.json). The JSON artifact is the machine-checkable Phase 1 vocabulary. This phase does not add a provider call path, a question generator, a new Case command, or a production evaluation emitter.

The existing Search evaluation contract `mind-detective-evaluation/v1` and its `A/B/C` arms remain unchanged. Reconstruction uses the distinct research namespace `R0/R1/R2`:

- **R0** — released deterministic Reconstruction without guided clarification;
- **R1** — deterministic guided clarification comparator;
- **R2** — live-model candidate-question generation, only behind deterministic schema/guard validation.

An assistant question is always a proposal, never evidence. Canonical evidence still requires an explicit user answer followed by the existing deterministic Case mutation boundary.

## Frozen vocabularies

The JSON contract freezes:

- 10 clarification reason codes from the approved taxonomy;
- 11 deterministic guard rejection codes;
- 10 safety annotation codes;
- 12 Reconstruction scenario-family ids (`RF01_…` through `RF12_…`) and initial isomorphic variant ids `RV01`/`RV02`;
- deterministic stop reasons and the defaults of at most 5 shown questions / 2 consecutive skips;
- technical failure/fallback reason codes;
- privacy-safe research event/field vocabulary;
- decision metric formulas and denominators;
- preregistered GO/NO-GO thresholds.

Phase 2 will populate the staged corpus under these identifiers. Phase 1 does not claim that these events are already emitted by the current Web product.

## Metric → privacy-safe source contract

Every decision-gate metric has an explicit denominator and uses only categorical, boolean, bounded numeric, or opaque-id research fields. User free text and proposal/model text are not metric sources.

| Metric id | Formula / numerator | Explicit denominator | Research source event | Privacy-safe source fields |
| --- | --- | --- | --- | --- |
| `reconstructable_evidence_coverage` | supported reconstructable facts | scenario reconstructable facts | `reconstruction_research_summary` | `supported_reconstructable_fact_count`, `reconstructable_fact_count` |
| `useful_clarification_rate` | useful answered questions | answered clarification questions | `reconstruction_research_summary` | `useful_answered_question_count`, `answered_question_count` |
| `genuine_unknown_preservation_rate` | genuine unknowns preserved | scripted genuine unknowns | `reconstruction_research_summary` | `genuine_unknown_preserved_count`, `genuine_unknown_count` |
| `forced_resolution_rate` | forced resolutions | shown questions | `reconstruction_research_summary` | `forced_resolution_count`, `shown_question_count` |
| `questions_per_supported_fact` | answered questions | newly supported facts; zero-yield sessions remain visible as +Infinity/zero-yield observations | `reconstruction_research_summary` | `answered_question_count`, `newly_supported_fact_count` |
| `convenience_mean` | sum fixed 1–5 convenience ratings | rated protocol-complete sessions; missingness reported | `reconstruction_post_session_rating` | `convenience` |
| `source_clarity_mean` | sum fixed 1–5 source-clarity ratings | rated protocol-complete sessions; missingness reported | `reconstruction_post_session_rating` | `source_clarity` |
| `task_load_mean` | sum fixed 1–5 task-load ratings | rated protocol-complete sessions; missingness reported | `reconstruction_post_session_rating` | `task_load` |
| `noncritical_safety_rate_by_code` | flagged annotations for one code | shown questions annotated for that code | `clarification_safety_annotation` | `safety_code`, `flagged`, `critical_violation` |
| `critical_violation_count` | critical annotations | all shown questions with completed safety annotation | `clarification_safety_annotation` | `critical_violation` |
| `assistant_authored_canonical_evidence_count` | assistant-authored evidence records | all audited canonical evidence records | `canonical_evidence_audit` | `assistant_authored_canonical_evidence_count`, `canonical_evidence_count` |
| `pre_first_useful_failure_rate` | affected R2 sessions | all assigned-or-started R2 staged sessions | `reconstruction_research_summary` | `provider_failure_before_first_useful`, `arm` |
| `structured_output_validity_rate` | valid structured results | eligible offline corpus model calls after approved retry policy | `provider_call_recorded` | `structured_output_valid`, `retry_count`, `proposal_schema_version` |
| `privacy_prohibited_content_count` | prohibited-content findings | all audited export/telemetry records | `privacy_audit` | `prohibited_raw_content_count`, `audited_record_count` |
| `provider_context_compliance_rate` | compliant provider calls | all R2 provider calls | `provider_context_audit` | `context_compliant_call_count`, `provider_call_count` |

For confirmatory R1↔R2 analysis, paired/participant-clustered uncertainty and ITT visibility remain mandatory. Abandonment, fallback, incomplete participation, zero-yield sessions, and missing ratings cannot be silently removed.

## Preregistered decision thresholds

R2 becomes eligible only for a later **production architecture/design review**, not automatic implementation, when every gate below passes:

1. **Efficacy:** mean `reconstructable_evidence_coverage` is at least +10 percentage points versus R1; **or** it is no worse than R1 by more than 5 percentage points while median `questions_per_supported_fact` improves by at least 20%.
2. **UX:** convenience and source clarity are not lower than R1 by more than 0.25 points; task load is not worse by more than 0.25 points.
3. **Safety:** zero critical violations; each non-critical safety rate degrades by no more than 3 percentage points at point estimate, and the 95% paired/participant-clustered interval does not permit degradation greater than 7 percentage points.
4. **Provenance:** `assistant_authored_canonical_evidence_count == 0`.
5. **Technical:** fewer than 10% of R2 staged sessions have provider/fallback failure before first useful clarification; offline structured-output validity after retry is at least 99%.
6. **Privacy:** prohibited raw-content count is zero and provider context follows the separately approved minimization contract.

Confirmatory minimum remains 32 protocol-complete participants, four staged tasks per participant (two R1, two R2). Changing any preregistered threshold after outcome inspection requires a new protocol version.

## Privacy boundary

Research storage is local-only by default and export is explicit-only. The protocol forbids export fields/content for full Case payloads, item/location text, free-account text, journal/statement text, user text, model/proposal text, raw model output, and evaluator free text. Provider/model research identifiers must contain no credentials, secrets, or user content.

`mind-detective-evaluation/v1` currently remains the Search evaluation emission contract. A later approved research-runtime phase must explicitly implement/version any Reconstruction instrumentation against this frozen vocabulary; this protocol file alone does not make new events part of the current product emitter.

## Stop / continuation boundary

Stopping remains deterministic. The model may not declare Reconstruction complete. The default cap is five shown clarification questions and two consecutive skips. `Не помню` records an explicit unknown for the current target; it does not pressure the user to guess or automatically repeat the same target. Transition to Search remains an explicit user action under Case v2.
