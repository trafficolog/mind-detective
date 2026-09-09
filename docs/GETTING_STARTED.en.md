# Getting Started

[Русский](GETTING_STARTED.md)

The canonical plugin id is `mind-detective`, targeting `0.1.0`. The runtime needs no network credentials.

Start through `mind-detective` with a misplaced physical item. The router checks safety first; `mind-detective-reconstruct` obtains a free account without seeding candidate locations; `mind-detective-plan` records completed physical checks before selecting one next action. Explicit pause/retain may save `.mind-detective/cases/<case-id>/case.json`; `mind-detective-resume` loads only the explicitly requested case; `mind-detective-close` records `found`, `unresolved`, or `abandoned` and honors explicit retain/delete.

Developer baseline:

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
```
