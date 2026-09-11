# Evaluation Analysis Runbook

The analysis pipeline is stdlib-only and reads evaluation export files, never Case files.

## Commands

```bash
python -m scripts.analyze_evaluation export.json --seed 1729 --bootstrap 2000 --json-out summary.json
python -m scripts.analyze_evaluation export.json --external-a external-a.json --seed 1729 --bootstrap 2000 --json-out summary-with-a.json
```

Use the default seed and bootstrap count for prespecified reports unless a new protocol version explicitly changes them.

## Validation

The analyzer fails closed on wrong schemas, duplicate participant/session/event IDs, unknown session references, invalid staged/real/external-A assignment shapes, out-of-range ratings, inconsistent handoff score, unknown event metadata keys, and any input object containing sensitive evaluation keys such as `item_label`, `target`, `journal`, `user_text`, or `raw_model_output`.

## Primary reconstruction

For every started staged/application session:

1. sort events by `(at, event_id)`;
2. require exactly one `case_started`;
3. inspect `next_action_shown` in chronological order;
4. link by privacy-safe `proposal_id` and candidate identity when present;
5. a proposal is useful only if it later reaches matching `check_finished` without prior matching rejection;
6. endpoint time is the original `next_action_shown` timestamp;
7. otherwise right-censor at terminal time or 600 seconds, whichever comes first.

The primary staged statistic is 10-minute Kaplan–Meier restricted mean time to useful action (RMTUA), lower is better. C-vs-B percentage difference and two-sided 95% participant-clustered bootstrap interval are reported.

## ITT and secondary outputs

All assigned/started staged sessions remain visible. Abandoned sessions, fallback C sessions, incomplete participants, and missing ratings are not silently dropped or favorably imputed.

The report includes protocol-complete participant count/cell balance, task-load and convenience means/differences, duplicate-check counts, terminal outcome distributions, S4 handoff scores, safety rate differences/intervals, critical violations, pre-useful-action fallback rate, and execution-contract failure count.

`task_load_difference`, `convenience_difference`, and `duplicate_check_difference` are reported as **C minus B**. Therefore lower task-load/duplicate differences favor C; higher convenience difference favors C.

## Prespecified interpretation

Point-rule meaningful lift is satisfied when either RMTUA C is at least 15% lower than B, or C is not worse by more than 5% and mean task load improves by at least 0.5 points; convenience must not degrade. No-lift and inconclusive zones follow the approved design specification.

Safety takes priority: any C critical violation fails the safety gate. For the three staged proposal-safety rates, point degradation above 5 percentage points fails; an upper 95% clustered interval allowing degradation above 10 points is inconclusive.

Pre-useful-action fallback above 10% fails the numeric technical-readiness gate. Execution-contract failures remain visible for manual materiality review because the approved design does not invent a numeric threshold for them.

The tool deliberately returns `manual_review_required` for overall product direction. Terminal-outcome imbalance and uncertainty require product/research review; the script does not manufacture a causal conclusion from small fixtures.

## Arm A

With `--external-a`, A appears only under `contextual_external_a`. Its outcome/rating summary is contextual and never enters B-vs-C efficacy or safety calculations.

## What green tests mean

Green fixtures prove schema handling, deterministic metric reconstruction, privacy boundaries, and reproducibility of the analysis machinery. They do **not** prove dialog-AI lift, causal validity, or scientific adequacy of an actual study.
