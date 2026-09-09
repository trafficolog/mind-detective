# Быстрый старт

[English](GETTING_STARTED.en.md)

## Установка как plugin

Репозиторий публикует metadata для Claude и Codex-compatible plugin discovery. Канонический plugin id: `mind-detective`, target version: `0.1.0`. Runtime не требует сетевых credentials.

## Первый кейс

1. Начните через `mind-detective` с названием потерянного физического предмета.
2. Router сначала применит safety boundary.
3. `mind-detective-reconstruct` попросит свободно рассказать последовательность без списка предполагаемых мест.
4. `mind-detective-plan` зафиксирует выполненные проверки и предложит одно следующее действие.
5. При паузе сохраните кейс явно; файл появится в `.mind-detective/cases/<case-id>/case.json`.
6. `mind-detective-resume` возобновит только явно указанный кейс.
7. `mind-detective-close` закроет `found`, `unresolved` или `abandoned` и выполнит явный retain/delete выбор.

## Для разработчика

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python -m unittest discover -s plugins/mind-detective/tests -v
```

Позже CI также запускает ruff, mypy, boundaries, freshness и release checks.
