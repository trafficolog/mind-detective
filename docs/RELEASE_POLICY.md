# Политика релизов

[English](RELEASE_POLICY.en.md)

Репозиторий использует один SemVer (`0.1.0`, …) и независимый SemVer плагина с тегом `mind-detective-vX.Y.Z`. Milestone/codename не является version line.

Публикация требует: feature/design review → exact PR-head CI → human merge authorization → exact new-main CI → human-approved `.github/releases/release.json` → единственный active publisher → exact tag-SHA verification → immutable release.

Publisher обязан fail closed при stale main, conflicting tag SHA, ambiguous existing release state или mutable recovery target. Уже опубликованные tags/releases не переназначаются; исправление = новая версия.

До Task 15 этот документ описывает нормативную политику, но release control в CONTRACT_MATRIX остаётся `planned`.
