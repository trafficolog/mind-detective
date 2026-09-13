# R2 deterministic proposal guard v1

**Status:** research-only guard for the approved Reconstruction Assistant study.  
**Schema:** `mind-detective-reconstruction-r2-guard/v1`  
**Base product truth:** released deterministic `0.4.0` Reconstruction plus the merged R1 comparator.

## Purpose

R2 may later use a model to propose one clarification question, but the candidate is not trusted. This Phase 4 guard is the deterministic boundary that validates the candidate before it can be shown in the research UI. It is **provider-agnostic** and does not make any external model call.

This phase does not activate a production Reconstruction assistant. `Case v2` remains unchanged and there is **no Case mutation** in the guard.

## Accepted proposal surface

A candidate must contain exactly:

```json
{
  "question": "...",
  "reason_code": "timeline_gap",
  "target_ids": ["evt_4", "evt_5"]
}
```

Unknown fields fail closed. In particular, candidates may not add probability, confidence, suggested-answer, memory, location-guess, Search-target, timeline-mutation or hidden-belief fields.

The `reason_code` must be one of the frozen Reconstruction research reason codes and must equal the current approved clarification opportunity. `target_ids` must be non-empty, unique strings, remain inside that opportunity's allowed target scope, and exist in the model-visible Reconstruction references.

## Decision surface

The guard has three deterministic decisions:

- `show`: the validated candidate may be displayed in the research surface;
- `block`: a frozen guard rejection code was detected; raw candidate text is not copied into the result;
- `abstain`: schema/scope validation failed and the stable technical failure reason is `schema_invalid`.

A guard rejection uses `technical_failure_reason = guard_rejected` plus one frozen code from `mind-detective-reconstruction-research/v1`.

## Frozen rejection vocabulary

The rejection-code vocabulary is owned by `RECONSTRUCTION_PROTOCOL_V1.json`:

- `introduced_location`
- `introduced_action`
- `leading_question`
- `suggestion_disguised_as_recollection`
- `false_confidence`
- `assumed_chronology`
- `unsupported_entity`
- `pressure_to_agree`
- `forced_contradiction_resolution`
- `mechanism_diagnosis`
- `unsafe_action`

For the staged corpus, Phase 4 uses deterministic precedence so a candidate that violates more than one rule receives one reproducible gold code. More specific semantic violations are evaluated before generic fixture deny terms; generic introduced locations/actions/entities are evaluated before the residual leading-question rule.

## Fixture context boundary

`forbidden_introductions.entities`, `.locations`, and `.actions` are **fixture deny terms** used to make the staged corpus deterministically testable. They are research-only validation aids and are **not a production provider contract**. Phase 5 is responsible for freezing the minimized model-visible context builder needed for a later live-model screen.

The guard may inspect only the candidate, current approved opportunity, the frozen model-visible context, and these synthetic fixture controls. Participant latent facts are never inputs.

## Existing safety ingress

The production product already has an existing safety ingress for high-consequence forgotten-action uncertainty. Its stable route is `limit_and_escalate`, implemented in both the authoritative Python-side safety classifier and the Web parity helper.

Phase 4 does not replace or broaden that production classifier. The research guard blocks an unsafe candidate question such as an instruction to enter a roadway so unsafe generated wording cannot reach the participant during the staged screen. This is a research guard rule aligned with the existing safety boundary; authoritative user-input safety routing remains where it already lives.

## Deterministic precedence

The corpus-facing detection precedence is:

1. `unsafe_action`
2. `mechanism_diagnosis`
3. `pressure_to_agree`
4. `forced_contradiction_resolution`
5. `suggestion_disguised_as_recollection`
6. `false_confidence`
7. `assumed_chronology`
8. `introduced_location`
9. `introduced_action`
10. `unsupported_entity`
11. `leading_question`

This precedence is an evaluation implementation detail for corpus reproducibility. It does not imply severity ordering.

## R1 ↔ R2 fairness

Safe R1 reviewed templates pass this guard when attached to the same approved target. This means R2 receives no advantage from a weaker validation path: both arms can be evaluated against the same semantic safety boundary.

Blocked and abstained decisions deliberately omit candidate question text, keeping the decision object compatible with the protocol's privacy rule that raw model text is not exported as research telemetry.

## Non-goals

This phase does not add:

- a live-model call or provider integration;
- a prompt or minimized context builder;
- Web research UI wiring;
- evaluation telemetry emitters;
- a new portable command;
- a Case schema change;
- production activation of `MD-WEB-REQ-RECON-ASSIST-*`;
- any `0.4.1` release/version action.

Passing the deterministic corpus guard is only an offline safety-screen prerequisite. It is not evidence that R2 improves Reconstruction, and it does not authorize a pilot or production rollout.
