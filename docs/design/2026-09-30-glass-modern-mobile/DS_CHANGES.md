# DS_CHANGES — что обновить в MIND Detective Design System

Прототип опирается на дизайн-систему, но опередил её в трёх местах. Правки вносятся в проект дизайн-системы, затем пересобирается `_ds_bundle.js`.

## 1. SearchCheckCard: цифровые способы проверки
Сейчас `method` принимает только физические ключи; для цифровых дел прототип временно рисует журнал через `GlassCard + ListRow`.
Добавить в `METHODS` компонента (иконки Lucide):
| key | label | icon |
|---|---|---|
| `name-search` | Поиск по названию | `search` |
| `date-filter` | Фильтр по дате | `calendar` |
| `browsed` | Просмотрел папку или альбом | `folder-open` |
| `trash` | «Удалённые» / корзина | `trash-2` |
| `shared` | Переписка и отправленные | `message-square` |
| `asked` | Спросил человека | `users` (уже есть) |
И поле `kind?: 'physical' | 'digital'`: для digital иконка слева — `image` вместо `map-pin`. После этого прототип возвращается к единому `SearchCheckCard` (удалить ветку `k.digital`).

## 2. Логотип «Мозаика состояний» (вариант 3d)
Заменить ассеты: `logo-mark.svg/.png`, `logo-mark-white.svg`, `logo-lockup.svg`, `app-icon` + `icon-512.png`, `icon-192.png`, `apple-touch-icon.png` — готовые файлы в `assets/` этого проекта. В гайде раздел «Logo»: «brain + magnifier» → «три подтверждённых фрагмента и один пунктирный (неизвестное)», clear space ≥ ширины одного фрагмента.

## 3. Тексты и смыслы
- Подпись `AppHeader` по умолчанию: «Системный поиск потерянного».
- Гайд, Content fundamentals: пример кнопки «Перейти к физическому поиску» → зависит от типа дела (`vocab` в `domain.js`); «Вещь найдена» / «Файл найден».
- Иконка цифрового дела: `image` (CaseCard `icon`).
- См. `docs/MEANING.md`.
