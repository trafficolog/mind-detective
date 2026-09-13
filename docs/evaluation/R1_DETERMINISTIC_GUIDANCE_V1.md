# R1 deterministic guided clarification v1

**Status:** research-only comparator for the approved Reconstruction Assistant study.  
**Schema:** `mind-detective-reconstruction-r1/v1`  
**Base product truth:** released deterministic `0.4.0` Reconstruction.  

## Purpose

R1 is the strong non-model comparator for the future R1 ↔ R2 evaluation. It tests the value of bounded guided clarification without giving a live model credit merely for asking additional questions.

R1 is not a production assistant. It does not activate the proposed `MD-WEB-REQ-RECON-ASSIST-*` family and it does not change the released Web flow.

## Boundary

R1 accepts only a precomputed list of approved clarification opportunities. Every opportunity already has a frozen `reason_code`, an opportunity id, and canonical target ids. R1 then:

1. applies the deterministic stopping policy;
2. excludes opportunities already completed by an explicit user answer or explicit-unknown endpoint;
3. selects the next opportunity by frozen reason priority and opportunity-id tie-break;
4. emits a neutral deterministic RU/EN question with exactly `question`, `reason_code`, and `target_ids` as proposal semantics.

There is **no Case mutation** in this utility. `Case v2` remains untouched. The utility does not create Statements, timeline events, Search targets, lifecycle changes, confidence values, probabilities, or any other canonical Case state.

It has no provider/network dependency and does not read participant latent facts. The synthetic corpus may contain latent scripted answers for research, but they are outside the input surface of `scripts/reconstruction_r1.py`.

## Frozen reason priority and templates

Priority follows the protocol taxonomy exactly:

| Priority | Reason code | RU intent | EN intent |
| ---: | --- | --- | --- |
| 1 | `timeline_gap` | нейтрально спросить о промежутке | ask neutrally about the interval |
| 2 | `temporal_order` | уточнить запомнившийся порядок | clarify remembered order |
| 3 | `ambiguous_location` | уточнить уже упомянутое место | clarify an already referenced place |
| 4 | `ambiguous_action` | уточнить уже описанное действие | clarify an already referenced action |
| 5 | `source_provenance` | уточнить источник утверждения | clarify statement provenance |
| 6 | `contradiction` | предложить уточнить без выбора стороны | clarify without choosing a side |
| 7 | `object_interaction` | уточнить уже обозначенное взаимодействие | clarify an existing item interaction |
| 8 | `transition_between_places` | уточнить переход между поддержанными событиями | clarify transition between supported events |
| 9 | `last_supported_interaction` | уточнить последнее из уже описанных взаимодействий | identify the last already-described interaction |
| 10 | `first_noticed_missing` | уточнить момент первого замеченного отсутствия | identify first noticed absence |

Templates intentionally avoid inserting concrete new locations, actions, people, or latent answers. The target identity is carried separately in `target_ids`; template text does not need to restate hidden or unsupported content.

## Deterministic selection

Input ordering must not affect the output. Selection key is:

`(reason priority, opportunity_id)`.

This freezes a reproducible R1 comparator and prevents corpus fixture ordering from becoming an experimental variable.

## Stopping policy

R1 uses the same frozen study limits intended for R2:

- maximum **five** shown clarification questions;
- stop after **two consecutive skips**;
- an explicit user decision to continue without more clarification stops R1;
- Reconstruction-ready and terminal states stop R1;
- no eligible approved opportunity yields `no_eligible_clarification`;
- the generator never decides that Reconstruction is complete on its own.

An explicit unknown is a valid user endpoint for the targeted opportunity and must not trigger a re-ask of the same target.

## R1 ↔ R2 fairness

The intended downstream research shape is:

```text
shared clarification opportunity / target
        ↓
R1 deterministic template  OR  R2 model proposal
        ↓
common validation / safety boundary
        ↓
state-first research UI
        ↓
user answer / explicit unknown / skip
        ↓
existing deterministic Case mutation boundary
```

Only candidate-question generation should differ materially between R1 and R2. Later phases may refactor the opportunity selector into a shared research helper, but that refactor must preserve this deterministic behavior and remain separately reviewed.

## Non-goals

This phase does not provide:

- a production Web component;
- provider/API integration;
- a model prompt or context builder;
- the Phase 4 deterministic R2 proposal guard;
- evaluation telemetry emitters;
- a new portable command;
- a Case schema change;
- a `0.4.1` version or release action.

Green deterministic tests establish comparator contract conformance only. They do not establish that R1 is effective with real users or that a future R2 is safe or beneficial.
