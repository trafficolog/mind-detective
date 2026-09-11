# mind-detective plugin

[Русский](README.md)

MIND Detective `0.3.0` is a transport-free Python plugin for systematic lost-item search. It remains the source of truth for safety, provenance, search, and portable deterministic semantics.

## Production skills

- `mind-detective` — safety-first router;
- `mind-detective-reconstruct` — free account plus uncertainty-preserving timeline;
- `mind-detective-plan` — SearchCheck log plus one next action;
- `mind-detective-resume` — explicit case resume/handoff;
- `mind-detective-close` — outcome plus retain/delete.

## Portable execution 0.3.0

`portable_kernel.py` and certified intrinsics define the restricted stdlib-only surface used by the repository generator to emit the Web TypeScript executor. The generated artifact is not a second hand-maintained reducer; parity is checked by the committed differential conformance corpus.

The plugin runtime itself does not call Web/API/LiteLLM and needs no network credentials. Metadata SSOT is `.codex-plugin/plugin.json`. Local file persistence remains explicit and case-local at `.mind-detective/cases/<case-id>/case.json`, with no cross-case learning.
