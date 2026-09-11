# External Arm A Protocol

Arm A is an external contextual baseline: ordinary search without the MIND Detective application route, hidden checklist, or conversational assistance. Do not build a fake empty MIND UI for A, because that would contaminate the baseline with product framing.

## Procedure

1. Assign the staged family/variant externally where comparable framing is needed.
2. Start the observation before ordinary search begins.
3. Give no MIND Detective checklist, journal, candidate ranking, or assistant proposal.
4. Observe for the same bounded staged horizon where practical.
5. Record one terminal outcome: `found`, `unresolved`, or `abandoned`.
6. Record the same fixed 1–5 task-load and convenience ratings when available.
7. Do not collect item/location text, user free text, raw model output, or participant identity in the common evaluation record.

## Accepted JSON representation

`--external-a` accepts the same `mind-detective-evaluation-export/v1` container. External participants use:

```json
{
  "evaluation_schema": "mind-detective-evaluation/v1",
  "protocol": "external_a",
  "enrollment_slot": null,
  "counterbalance_cell": null
}
```

External sessions use `arm: "A"`, `assignment_version: "eval-assignment/v1"`, no `case_id`, and may carry scenario family/variant/order codes for contextual matching. Terminal timestamps/outcome and optional fixed `post_case_rating` events are allowed.

## Interpretation

The analysis tool reports A only under `contextual_external_a`. A is never used in C-vs-B efficacy, safety, clustered-bootstrap, or product-decision calculations. Without product proposal linkage, A is not forced through the B/C `time_to_next_useful_action` reconstruction.
