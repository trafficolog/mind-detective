# mind-detective plugin

[English](README.en.md)

MIND Detective `0.3.0` — transport-free Python plugin для систематического поиска потерянных физических предметов. Он остаётся source of truth для safety, provenance, search и portable deterministic semantics.

## Production skills

- `mind-detective` — safety-first router;
- `mind-detective-reconstruct` — free account + uncertainty-preserving timeline;
- `mind-detective-plan` — SearchCheck log + one next action;
- `mind-detective-resume` — explicit case resume/handoff;
- `mind-detective-close` — outcome + retain/delete.

## Portable execution 0.3.0

`portable_kernel.py` и certified intrinsics определяют restricted stdlib-only surface, из которого repository generator создаёт Web TypeScript executor. Generated artifact не является вторым вручную поддерживаемым reducer; parity проверяется committed differential conformance corpus.

Сам plugin runtime не вызывает Web/API/LiteLLM и не требует network credentials. Metadata SSOT — `.codex-plugin/plugin.json`. Локальное файловое сохранение остаётся explicit case-local в `.mind-detective/cases/<case-id>/case.json`, без cross-case learning.
