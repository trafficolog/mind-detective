# MIND Detective

<!-- release-0.1.0 -->

[Русский](README.md)

**MIND Detective is a systematic lost-item search assistant.** It reduces cognitive load during a search by preserving the user's own account without promoting it to verified fact, keeping a durable log of physical checks, selecting one useful next action, and resuming an explicitly saved case after interruption.

## What 0.1.0 does

- structures user-provided recollections while preserving uncertainty;
- keeps statement origin and type separate;
- records `SearchCheck` target, method, result, and inaccessible parts;
- chooses one next action using transparent categorical rules;
- saves only an explicitly selected case under `.mind-detective/cases/<case-id>/case.json`;
- resumes/hands off a case without erasing prior checks;
- separates physical-object search from uncertainty about whether a high-risk action happened.

## Product limits

The MVP is not a medical tool, does not diagnose a forgetting mechanism, does not provide calibrated location percentages, uses no Bayesian/POD/hidden belief-weight model, and does not convert repeated glances into independent evidence of absence. Generic Claude Code/Codex hosts also provide no repository-controlled mandatory pre-send interceptor: the guard mechanically controls only candidates submitted to it.

## Architecture

The deterministic Case Controller owns state. The LLM is limited to dialogue, explanation, neutral reconstruction, and explicitly labelled search suggestions. The plugin exposes exactly five production skills: `mind-detective`, `mind-detective-reconstruct`, `mind-detective-plan`, `mind-detective-resume`, and `mind-detective-close`. Runtime is Python-standard-library-first and transport-free.

Development follows `SPEC → RED → GREEN → REFACTOR → TRACE → EVAL → VERIFY`. See [Getting Started](docs/GETTING_STARTED.en.md), [Architecture](docs/ARCHITECTURE.en.md), [Methodology](docs/METHODOLOGY.en.md), [Privacy (RU)](docs/PRIVACY.md), and [Product Evaluation (RU)](docs/PRODUCT_EVALUATION.md).
