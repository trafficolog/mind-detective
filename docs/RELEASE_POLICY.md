# Политика релизов

[English](RELEASE_POLICY.en.md)

Репозиторий использует один repository SemVer и независимый plugin SemVer с тегом `mind-detective-vX.Y.Z`. Текущий declarative intent находится в `.github/releases/release.json`: repository `0.4.0` и plugin `mind-detective-v0.4.0`. Опубликованные `0.1.0`, `0.2.0`, `0.3.0` и `0.3.1` являются immutable history; публикация текущего declarative intent выполняется только через отдельный явно авторизованный release gate.

## Единственный publication path

Публикация выполняется только `.github/workflows/publish-current-release.yml`. Параллельный publisher, ручное создание заменяющих тегов или переназначение опубликованных тегов не допускаются.

Последовательность gate:

1. design/implementation review;
2. CI на exact PR head SHA;
3. явно авторизованный merge;
4. CI на exact новом `main` SHA;
5. manual `workflow_dispatch` canonical publisher с **полным 40-hex `target_sha`** этого verified `main`;
6. publisher повторно проверяет live `origin/main`, successful CI exact target, declarative manifest и существующее release state до mutation;
7. exact tag-SHA и immutable release verification после публикации.

Publisher fail-closed при stale main, conflicting tag SHA, standalone tag без согласованного release, ambiguous existing release state, mutable recovery target или остатках rollback. Уже опубликованные tags/releases не переназначаются; исправление выпускается новой версией.

Release controls `MD-REQ-RELEASE-01`, `MD-WEB-REQ-RELEASE-01` и `MD-OFFLINE-REQ-RELEASE-01` активны и трассируются exact tests в `CONTRACT_MATRIX.json`.
