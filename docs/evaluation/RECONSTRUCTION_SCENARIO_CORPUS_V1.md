# Reconstruction staged scenario corpus v1

**Status:** research-only synthetic instrument for the 0.4.1 Reconstruction Assistant study.  
**Machine contract:** `RECONSTRUCTION_SCENARIO_CORPUS_V1.json`  
**Protocol:** `mind-detective-reconstruction-research/v1`  
**Case schema:** unchanged `mind-detective-case/v2`

## Purpose

This corpus makes the Phase 2 research boundary reproducible before any R1 deterministic generator, R2 live-model adapter, or provider screening exists. It contains **24** fixtures: 12 canonical families with one RU and one EN isomorphic variant (`RV01` / `RV02`).

The corpus is not product memory and does not authorize production assistant behavior. It is a synthetic research instrument for later R0/R1/R2 comparison.

## Instrument boundary

Each fixture separates three semantic layers:

1. `user_visible_initial_account` — synthetic text shown to the staged participant;
2. `model_visible_context` — bounded synthetic context that intentionally contains no participant latent facts;
3. `participant_latent` — scripted facts available only to the staged participant and evaluator.

`participant_latent` is never model-visible. The `model_visible_context` shape in this corpus is a research fixture boundary, **not** the final production/provider context contract; context minimization remains a later design phase.

Genuine unknowns are first-class expected outcomes. A correct question may end in **preserve unknown** rather than forcing more detail.

## Coverage matrix

| Family | Variants | Positive clarification reason(s) | Adversarial guard class | Preserve unknown |
|---|---|---|---|---|
| `RF01_simple_chronology` | RU/EN | temporal_order, first_noticed_missing | `introduced_location` | no |
| `RF02_missing_interval` | RU/EN | timeline_gap, transition_between_places | `introduced_action` | no |
| `RF03_contradictory_recollection` | RU/EN | contradiction | `forced_contradiction_resolution` | yes |
| `RF04_habit_vs_actual_recollection` | RU/EN | source_provenance | `suggestion_disguised_as_recollection` | yes |
| `RF05_multiple_similar_locations` | RU/EN | ambiguous_location | `unsupported_entity` | yes |
| `RF06_false_friend_location` | RU/EN | ambiguous_location | `false_confidence` | yes |
| `RF07_genuine_unknown` | RU/EN | first_noticed_missing | `pressure_to_agree` | yes |
| `RF08_ambiguous_pronoun_entity` | RU/EN | ambiguous_action, source_provenance | `leading_question` | yes |
| `RF09_multiple_object_interactions` | RU/EN | object_interaction, last_supported_interaction | `assumed_chronology` | no |
| `RF10_high_risk_unsafe_context` | RU/EN | ambiguous_action | `unsafe_action` | yes |
| `RF11_prompt_injection_free_account` | RU/EN | timeline_gap | `mechanism_diagnosis` | no |
| `RF12_ru_en_isomorphism` | RU/EN | transition_between_places, last_supported_interaction | `introduced_location` | no |

## Exit-criteria coverage

- Every protocol clarification reason code has at least two positive examples because each covered family has paired RU/EN fixtures.
- Every deterministic guard rejection code has at least two adversarial examples; RU/EN pairs are structurally equivalent.
- Relevant ambiguity/uncertainty families contain at least one `preserve_unknown=true` fixture.
- Prompt injection is represented in both RU and EN under `RF11_prompt_injection_free_account`.
- Every fixture declares critical-violation triggers and deterministic readiness/stopping expectations.
- RU/EN pairs share fact ids, target ids/reason codes, guard-code multiplicity, and expected outcomes so language differences do not silently change the experimental task.

## Privacy and provenance

All scenario text is synthetic. No real user Case data belongs in this corpus.

Later evaluation export continues to store scenario/variant identifiers and categorical outcomes rather than raw participant/account text. Assistant/model proposal text remains non-canonical and may never become recollection, habit, observation, or other Case evidence without an explicit user answer followed by the existing deterministic Case mutation boundary.

## Out of scope

This Phase 2 artifact does **not** add:

- an R1 question generator;
- an R2 proposal/provider path;
- a deterministic proposal guard implementation;
- Web research controls;
- live-model calls;
- Case v3 or any Case migration;
- release/version/tag/publication changes.

Those remain separate gated phases.
