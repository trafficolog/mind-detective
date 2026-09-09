# mind-detective plugin

[English](README.en.md)

Плагин MIND Detective реализует transport-free систематический поиск потерянных физических предметов. В 0.1.0 он включает ровно пять skills и deterministic Case Controller.

## Skills

- `mind-detective` — safety-first router;
- `mind-detective-reconstruct` — free account + uncertainty-preserving timeline;
- `mind-detective-plan` — SearchCheck log + one next action;
- `mind-detective-resume` — explicit case resume/handoff;
- `mind-detective-close` — outcome + retain/delete.

Runtime: Python standard library only. Metadata SSOT: `.codex-plugin/plugin.json`. Локальное сохранение — только явно, без cross-case learning.
