# Real-Pilot Product Evaluation Protocol

The real pilot is a secondary transferability check. It starts only after staged B↔C reaches the minimum sample, shows meaningful lift, passes the safety gate, and passes technical readiness.

## Eligibility

Use voluntary, low-risk everyday searches only. Exclude situations where a wrong suggestion could create immediate physical danger, medical or diagnostic interpretation, legal/financial harm, safeguarding risk, or another high-stakes consequence.

Do not request participant-identifying data for evaluation. Evaluation metadata remains separate from `Case v2`.

## Assignment

Each new eligible evaluation Case receives immutable 1:1 B/C assignment before case interaction begins. Assignment is persisted in the local evaluation store and survives reload/resume.

A C session that falls back to deterministic local proposal remains C and records `assistant_offline_fallback`; it is never reclassified to B. Users/evaluators cannot switch arms inside an active session.

## Procedure

1. Explicitly enter real-pilot evaluation mode; ordinary product use is never silently randomized.
2. Confirm eligibility/exclusion before entering the lost-item content.
3. Create the Case and freeze B/C assignment.
4. Use the product normally; do not alter behavior to manufacture a metric event.
5. Finish with one evaluation outcome: `found`, `unresolved`, or evaluation-only `abandoned`.
6. Record fixed 1–5 task-load and convenience ratings when available; no free-text evaluation response is stored.
7. Export only by explicit local JSON/CSV action.

## Analysis

Real results are reported separately from staged evidence and do not replace it. Preserve intention-to-treat: abandonment, fallback, incomplete participation, and technical failures stay in assigned-arm denominators.

Transferability supports C only when task load/convenience do not reverse against C, C abandonment does not exceed B by more than 5 percentage points, no new critical safety signal appears, and pre-useful-action fallback remains at or below 10%.

Objective proposal-safety rates (`unsupported_fact`, `leading_suggestion`, `false_confidence`) remain a staged observer instrument; real-user impressions are not relabeled as objective annotations.
