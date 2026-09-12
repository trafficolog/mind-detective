# Semantic scenario review

`plugins/mind-detective/evals/scenarios.json` is a semantic expectation corpus for the plugin/agent surface. Repository CI validates its schema, registered routes/tokens/outcomes, and the governance declaration; it does **not** execute these prompts against an LLM and does not grade their meaning automatically.

## Current governance

Semantic execution mode is **manual**. There is no repository-native model grader, hidden score threshold, or automated semantic runner. A green repository CI run therefore means the corpus is structurally valid, not that every scenario has passed semantically.

A semantic PASS may be recorded only after a human reviewer or an explicitly approved external harness runs the scenario against the target plugin/runtime and checks all of the following:

1. the observed route matches `must_route_to`;
2. the outcome matches `outcome`;
3. all `must_mention_tokens` are present where the runtime exposes machine tokens;
4. the response conveys every `must_convey` expectation;
5. the response does not make any `must_not_claim` assertion.

## Review record

For each executed scenario record at minimum:

- scenario id;
- execution date;
- target runtime/plugin revision or exact commit SHA;
- model/provider and model version when an LLM is involved;
- observed route and outcome;
- PASS/FAIL plus a short reason for any failure.

Do not convert manual observations into calibrated percentages or scientific-validity claims. Product B↔C evaluation remains governed separately by `docs/PRODUCT_EVALUATION.md` and `docs/evaluation/STAGED_PROTOCOL.md`.

If an automated semantic runner is introduced later, it requires a separate reviewed design with explicit model/runtime pinning, reproducibility limits, failure policy, and CI/release-gate semantics before `semantic_validation.automated_runner` may become `true`.
