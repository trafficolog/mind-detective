# MIND Detective — Claude Design System Brief
## Glass Modern Mobile PWA

**Document purpose:** use this file as the single source of truth for generating and iterating the MIND Detective mobile PWA UI in Claude Design.

**Primary platform:** mobile-first PWA  
**Secondary platform:** tablet / desktop responsive expansion  
**Primary language:** Russian  
**Secondary language:** English  
**Visual direction:** Glass Modern / soft glassmorphism / airy blue gradients  
**Product principle:** state-first, not chatbot-first

---

# 1. Product summary

MIND Detective is a systematic lost-item search assistant.

The product reduces working-memory load by separating:

1. what the user actually reported;
2. what the user explicitly confirmed;
3. what is still unknown or contradictory;
4. hypotheses/questions used during reconstruction;
5. physical checks performed during Search.

The product does **not** guess where an item “probably is” and does not turn assistant suggestions into canonical user memories.

The core user flow is:

```text
Free account
→ user-confirmed evidence
→ reconstruction timeline
→ unknown intervals / contradictions
→ explicit transition to Search
→ physical checks
→ SearchCheck journal
→ found / paused / closed
```

---

# 2. Non-negotiable product rules

These rules are more important than visual styling.

## 2.1 Reconstruction ≠ Search

Reconstruction and Search must look and behave like different modes.

### Reconstruction
Purpose:
- rebuild a checkable timeline;
- preserve unknowns;
- expose contradictions;
- ask clarifying questions;
- confirm facts explicitly.

### Search
Purpose:
- execute physical checks;
- track what was actually checked;
- record method and result;
- resume later without repeating work.

Do not collapse both into a generic AI-chat flow.

---

## 2.2 Canonical evidence boundary

Assistant suggestions, generated hypotheses, or questions are never shown as user-confirmed facts.

Use visibly distinct visual states:

- **Confirmed**
- **Unknown**
- **Contradiction**
- **Hypothesis / question**
- **Physical check**
- **Research-only assistant proposal**

---

## 2.3 No pseudo-probabilities

Do **not** use:

- “85% likely to be here”
- “62% chance”
- “high probability location”
- calibrated-looking confidence bars
- location rankings presented as probabilities

Allowed:

- workflow completion, e.g. `5 of 12 checks`;
- number of confirmed facts;
- number of unknown intervals;
- status counts;
- progress through a finite checklist;
- explicit qualitative labels that describe workflow state rather than truth probability.

Prefer:

```text
Confirmed
Needs clarification
Unknown
Contradiction
Not checked
Checked visually
Checked by hand
Research proposal
```

---

## 2.4 Privacy clarity

The UI must make local-first storage easy to understand.

Default product message:

> Canonical Case data is stored locally on the device.

For optional online assistant flows, distinguish:

```text
Browser → API
full Case v2 may be sent to the configured API service

API → provider
server derives a narrower provider context
```

Do not claim that all data always remains on-device if an online assistant is configured.

---

## 2.5 Research-only assistant

The Reconstruction Assistant is not a normal production feature.

Always label it:

```text
Research only
```

or in Russian:

```text
Только исследование
```

Its questions/proposals cannot become canonical facts without explicit user confirmation.

---

# 3. Visual concept — Glass Modern

The UI should feel:

- calm;
- light;
- precise;
- trustworthy;
- modern;
- tactile;
- spatial;
- non-clinical;
- non-gamified.

Avoid:
- cyberpunk;
- heavy neon;
- detective clichés;
- dark “crime investigation” visuals;
- excessive gradients;
- glossy skeuomorphism;
- cartoon detective metaphors;
- red strings / conspiracy-board imagery.

---

# 4. Core visual language

## 4.1 Background

Base background:

```css
--bg-primary: #EEF7FF;
--bg-secondary: #E6F2FF;
--bg-highlight: #F7FBFF;
```

Use soft, large-scale ambient gradients:

```css
background:
  radial-gradient(circle at 75% 8%, rgba(141,194,255,.38), transparent 34%),
  radial-gradient(circle at 15% 80%, rgba(198,223,255,.32), transparent 38%),
  linear-gradient(180deg, #F7FBFF 0%, #EAF5FF 100%);
```

Do not use busy photographic backgrounds behind functional screens.

---

## 4.2 Glass surfaces

Primary glass card:

```css
background: rgba(255,255,255,.52);
backdrop-filter: blur(22px) saturate(135%);
border: 1px solid rgba(255,255,255,.75);
box-shadow:
  0 12px 36px rgba(69,118,171,.10),
  inset 0 1px 0 rgba(255,255,255,.70);
```

Secondary glass card:

```css
background: rgba(247,251,255,.40);
backdrop-filter: blur(16px);
border: 1px solid rgba(164,201,236,.32);
```

Glass should enhance hierarchy, not reduce contrast.

---

# 5. Color tokens

## 5.1 Brand / interaction

```css
--brand-50:  #EFF8FF;
--brand-100: #DCEEFF;
--brand-200: #BBDFFF;
--brand-300: #8CC9FF;
--brand-400: #58AEFF;
--brand-500: #178EF0;
--brand-600: #0674D8;
--brand-700: #075CAF;
--brand-800: #0C4C8D;
--brand-900: #103F73;
```

Primary action:

```css
--action-primary: #0B86EA;
--action-primary-hover: #0875D2;
```

---

## 5.2 Semantic states

```css
--confirmed-bg: #E8F8F1;
--confirmed-fg: #05875B;

--unknown-bg: #FFF7E6;
--unknown-fg: #B87800;

--contradiction-bg: #FFF0F1;
--contradiction-fg: #D93845;

--hypothesis-bg: #EEF2FF;
--hypothesis-fg: #4D5EEA;

--research-bg: #F4ECFF;
--research-fg: #7A35D8;

--neutral-bg: #EEF3F8;
--neutral-fg: #66788D;
```

Semantic colors must never be used decoratively without meaning.

---

# 6. Typography

Preferred stack:

```css
font-family:
  Inter,
  SF Pro Display,
  SF Pro Text,
  system-ui,
  -apple-system,
  sans-serif;
```

## Scale

```text
Display XL     40 / 44 / 700
Display L      32 / 38 / 700
Title L        28 / 34 / 700
Title M        22 / 28 / 650
Title S        18 / 24 / 650
Body L         17 / 25 / 400
Body M         15 / 22 / 400
Body S         13 / 18 / 400
Label          12 / 16 / 600
Micro          11 / 14 / 500
```

Use dark navy instead of pure black:

```css
--text-primary: #0B1733;
--text-secondary: #587196;
--text-tertiary: #8095AF;
```

---

# 7. Layout system

Target viewport baseline:

```text
390 × 844 CSS px
```

Also support:
- 360 px width;
- 393 / 402 / 430 px;
- tablet;
- desktop.

## Spacing scale

```text
4, 8, 12, 16, 20, 24, 32, 40
```

Primary page padding:

```text
16 px mobile
20 px large mobile
24–32 px tablet
```

Do not crowd information.

---

# 8. Radius system

```css
--radius-xs: 10px;
--radius-sm: 14px;
--radius-md: 18px;
--radius-lg: 24px;
--radius-xl: 30px;
--radius-pill: 999px;
```

Primary glass cards: 22–26 px  
Bottom navigation shell: 26–30 px

---

# 9. Iconography

Use:

- Lucide-style outline icons;
- consistent 1.75–2 px stroke;
- rounded joins;
- no filled cartoon icons except status dots.

Core icon categories:

```text
Case             folder
Reconstruction   nodes / timeline
Search           search
Journal          list-check
Confirmed        check-circle
Unknown          circle-help
Contradiction    triangle-alert
Hypothesis       lightbulb / sparkles
Research         flask
Export           download
Privacy          shield
Voice            microphone
Photo            image
Location         map-pin
```

---

# 10. Navigation architecture

Persistent bottom navigation for core app:

```text
Дела
Реконструкция
Поиск
Журнал
```

Rules:

- bottom nav is present only inside an active product workspace;
- onboarding / loading can omit it;
- current section uses brand blue;
- inactive icons use slate blue-gray;
- Search and Reconstruction remain visually distinct.

Optional fifth destination only if required later:

```text
Настройки
```

Prefer Settings inside Case/global menu instead of expanding to five tabs unnecessarily.

---

# 11. Core reusable components

Claude Design should build these as reusable components.

## 11.1 GlassCard

Variants:

```text
default
interactive
selected
confirmed
unknown
contradiction
research
disabled
```

---

## 11.2 StatusChip

Variants:

```text
Active search
Reconstruction
Confirmed
Unknown
Contradiction
Needs clarification
Found
Closed
Research only
Offline
```

---

## 11.3 CaseCard

Contains:

- object thumbnail/icon;
- case name;
- case ID;
- mode;
- last confirmed place;
- last updated time;
- finite workflow progress only;
- overflow menu.

Never show “likelihood of finding”.

---

## 11.4 TimelineEvent

Fields:

```text
time
place / action
evidence status
source
optional image
optional contradiction marker
```

Variants:

```text
confirmed
unknown interval
contradiction
hypothesis/question
```

---

## 11.5 SearchCheckCard

Fields:

```text
place
method
time
result
notes
media
repeat-check flag
```

Methods:

```text
visual
by hand
with flashlight
opened compartment
moved object
asked another person
other
```

---

## 11.6 EvidenceCard

Must distinguish:

```text
user-confirmed fact
original source
assistant question
hypothesis
unknown
contradiction
```

---

## 11.7 BottomSheet

Use for:

- check details;
- event details;
- adding evidence;
- export;
- photo attachment;
- confirmation actions.

---

## 11.8 EmptyState

Should remain calm and actionable.

Never fill empty space with motivational copy that implies success.

---

# 12. Screen inventory

The design system must support the full real product, not just marketing screens.

---

# 13. Screen 01 — PWA splash / preload

Purpose:
- fast preload state;
- show product identity;
- no fake AI analysis animation.

Content:

```text
MIND Detective
Систематический поиск потерянных вещей
```

Optional:
- translucent glass sphere visual;
- simple preload bar;
- offline-ready indicator after service worker initialization.

Do not display invented percentages unless based on actual asset-loading progress.

---

# 14. Screen 02 — Cases / Дела

Primary home screen.

Sections:

```text
Header
Filters
Active Cases
Paused / Closed
Create Case CTA
Local data / export hint
```

Case statuses:

```text
Реконструкция
Активный поиск
Ожидает уточнения
Найдено
Закрыто
```

No probability rings.

Allowed case progress:

```text
5 / 12 проверок
3 неизвестных интервала
2 противоречия
```

---

# 15. Screen 03 — New Case / Свободный рассказ

Primary action:
capture a verbatim free account.

Elements:

```text
Новое дело
Свободный рассказ
large text area
voice input
optional attachment
starter prompts
privacy explanation
Continue
```

Starter prompts:

```text
Что потеряно?
Когда видели в последний раз?
Где были?
Что делали?
Кто был рядом?
Есть ли необычные детали?
```

Important:
the text entered here is preserved verbatim.

---

# 16. Screen 04 — Reconstruction overview

This is the main Reconstruction workspace.

Header:

```text
object
case ID
mode = Реконструкция
```

Sections:

```text
Timeline
Unknown intervals
Contradictions
Confirmed evidence
Clarifying questions
```

Use a vertical chronological timeline.

Unknown interval should be visually neutral/amber.

Contradiction should be red but not alarming.

---

# 17. Screen 05 — Confirm evidence

Purpose:
user explicitly confirms or rejects structured statements.

Each candidate statement:

```text
statement
source
source excerpt
status
```

Actions:

```text
Подтвердить
Не уверен
Отклонить
```

Do **not** show numeric confidence.

---

# 18. Screen 06 — Unknown intervals

List unknown timeline segments.

Example:

```text
13:20–13:50
Что происходило между кафе и дорогой домой?
```

Actions:

```text
Добавить факт
Ответить позже
Оставить неизвестным
```

Unknown is a valid final state.

---

# 19. Screen 07 — Contradictions

Show two or more conflicting statements without forcing resolution.

Example:

```text
Источник A: "Куртка была на мне"
Источник B: "Куртка осталась в машине"
```

Actions:

```text
Уточнить
Оставить противоречие
Добавить источник
```

Never auto-resolve contradictions.

---

# 20. Screen 08 — Reconstruction assistant — Research only

Strong label:

```text
Только исследование
```

Sections:

```text
Минимальный контекст
Уточняющий вопрос
Границы ответа
Why this question
```

Actions:

```text
Использовать как вопрос
Изменить
Не использовать
```

Explicit notice:

```text
Предложение ассистента не становится фактом автоматически.
```

---

# 21. Screen 09 — Transition to Search

A deliberate mode transition.

Content:

```text
Реконструкция завершена настолько, насколько возможно.
Неизвестные интервалы и противоречия сохранятся.
```

Summary:

```text
confirmed facts
unknown intervals
contradictions
candidate search zones
```

Primary CTA:

```text
Перейти к физическому поиску
```

Secondary:

```text
Вернуться к реконструкции
```

---

# 22. Screen 10 — Search overview

Search mode must feel operational.

Header:

```text
object
mode = Поиск
```

Sections:

```text
Zones to check
Already checked
Next physical check
SearchCheck log preview
```

Do not rank zones with probabilistic confidence.

Use:

```text
Проверить сейчас
Проверить позже
Не относится к делу
```

---

# 23. Screen 11 — Search zone

Example:

```text
Прихожая
```

Checklist:

```text
карманы верхней одежды
сумки
полка для обуви
консоль
под мебелью
между предметами
```

Method selector:

```text
визуально
руками
с фонариком
с перемещением предметов
```

---

# 24. Screen 12 — Record SearchCheck

Critical screen.

Fields:

```text
Место
Что проверяли
Метод проверки
Результат
Заметка
Фото
Время
```

Result values:

```text
Не найдено
Найдено
Нужно проверить повторно
Проверка не завершена
```

---

# 25. Screen 13 — SearchCheck Journal / Журнал

List all checks chronologically.

Filters:

```text
Все
Найдено
Не найдено
Повторить
Не завершено
```

Rows display:

```text
place
method
time
result
repeat status
```

Never use numerical confidence scores.

---

# 26. Screen 14 — SearchCheck detail

Use bottom sheet or full screen.

Content:

```text
location
method
result
time
notes
attached photos
previous checks of same place
```

Actions:

```text
Повторить проверку
Редактировать заметку
Добавить фото
```

---

# 27. Screen 15 — Found item

Calm success state.

Content:

```text
Вещь найдена
Где найдена
Когда
Какой SearchCheck помог
```

Actions:

```text
Завершить дело
Добавить итоговую заметку
Экспортировать дело
```

Avoid celebratory confetti.

---

# 28. Screen 16 — Case closed without finding

Support honest closure.

Statuses:

```text
Поиск остановлен
Вещь не найдена
Дело закрыто пользователем
```

Show:

```text
what was reconstructed
what was checked
what remains unknown
```

Actions:

```text
Возобновить
Экспортировать
Удалить
```

---

# 29. Screen 17 — Case export/import

Export:

```text
Case v2 JSON
```

Explain:

```text
portable case state
user-confirmed evidence
timeline
SearchCheck journal
```

Import should validate schema and show errors clearly.

---

# 30. Screen 18 — Offline state

The app is local-first.

Offline banner:

```text
Офлайн
Локальная работа доступна
```

Offline-safe:

```text
Case creation
Reconstruction deterministic actions
Timeline
Search
SearchCheck
Journal
Export/import
```

Provider-dependent optional actions should be visibly unavailable.

---

# 31. Screen 19 — Online assistant unavailable

No alarming error.

Message:

```text
Онлайн-ассистент сейчас недоступен.
Основной поиск продолжает работать локально.
```

CTA:

```text
Продолжить без ассистента
```

---

# 32. Screen 20 — Privacy / data boundary

Show two distinct flows:

```text
Локально на устройстве
Case v2 + журнал + реконструкция

Опционально:
Browser → configured API → minimized provider context
```

Use a simple diagram.

---

# 33. Screen 21 — Settings

Sections:

```text
Язык
Тема
Offline / PWA
Экспорт данных
Удаление локальных данных
Online assistant configuration
Privacy
About
```

Do not add social/community/account features unless implemented.

---

# 34. Screen 22 — PWA install prompt

Native-feeling bottom sheet.

Copy:

```text
Установить MIND Detective
Быстрый запуск с главного экрана.
Локальные функции доступны офлайн.
```

Actions:

```text
Установить
Не сейчас
```

---

# 35. Screen 23 — Empty cases state

Content:

```text
Пока нет дел
Создайте первое дело, чтобы начать систематический поиск.
```

Primary:

```text
Создать дело
```

Secondary:

```text
Импортировать Case
```

---

# 36. Screen 24 — Resume case

When opening an existing case:

```text
Продолжить с последнего состояния
```

Show:

```text
current mode
last confirmed action
last SearchCheck
open unknowns
```

No generic chatbot greeting.

---

# 37. Screen 25 — Error / invalid import

Explain precisely:

```text
Файл не соответствует Case v2
```

Show:
- file;
- reason;
- safe action.

Never silently mutate invalid imported state.

---

# 38. Main mobile interaction patterns

## Swipe

Allowed:

```text
back navigation
journal row actions
```

Do not hide critical destructive actions behind swipe only.

---

## Long press

Optional:

```text
quick actions
copy source text
```

---

## Bottom sheet

Preferred for:
- context details;
- SearchCheck;
- attachments;
- filters.

---

# 39. Motion system

Motion should communicate state.

Durations:

```text
fast    120–160 ms
normal  180–240 ms
slow    280–360 ms
```

Allowed:

- glass card elevation;
- sheet expansion;
- progress transition;
- route/timeline reveal;
- subtle state-chip crossfade.

Avoid:
- particles;
- pulsing AI glows;
- gamification;
- “thinking” animations suggesting certainty.

Respect `prefers-reduced-motion`.

---

# 40. Accessibility

Target:

```text
WCAG 2.2 AA
```

Requirements:

- minimum body contrast 4.5:1;
- interactive controls ≥ 44 × 44 px;
- semantic status not color-only;
- keyboard support;
- screen reader labels;
- focus visible;
- reduced motion;
- Dynamic Type friendly;
- no text baked into decorative images.

---

# 41. Responsive behavior

## Mobile
Primary design target.

## Tablet
Two-column layouts allowed:

```text
timeline | details
search zones | SearchCheck
```

## Desktop
Preserve mobile mental model.

Do not turn the product into an analytics dashboard.

---

# 42. Photography

Use photography only when it represents actual Case content:

- item;
- place;
- search evidence;
- user-attached photo.

Do not use decorative stock photos inside functional cards.

---

# 43. Design anti-patterns

Never produce:

- location “probability” scores;
- confidence percentages for memories;
- assistant-generated facts styled as confirmed;
- chat-first home screen;
- detective noir branding;
- police/crime metaphors;
- red-string evidence wall;
- leaderboard;
- gamified streaks;
- “AI found the answer” language;
- fake scientific confidence;
- diagnosis of forgetting;
- autoplay emotional animations.

---

# 44. Preferred Russian microcopy

Use:

```text
Дела
Реконструкция
Поиск
Журнал
Свободный рассказ
Подтверждённый факт
Неизвестный интервал
Противоречие
Уточняющий вопрос
Проверить место
Метод проверки
Не найдено
Найдено
Проверить повторно
Оставить неизвестным
Только исследование
Сохранено локально
Работает офлайн
```

Avoid:

```text
Мы знаем, где вещь
Вероятнее всего
ИИ уверен
Точность 92%
Восстановленная память
Настоящее воспоминание
```

---

# 45. Claude Design generation instructions

When generating screens:

1. Follow **Glass Modern** as the only visual language.
2. Generate one mobile state per frame.
3. Use realistic Russian product copy.
4. Keep all screens part of the same design system.
5. Reuse components and tokens.
6. Preserve consistent bottom navigation.
7. Treat Reconstruction and Search as separate modes.
8. Never introduce pseudo-probabilities.
9. Mark research-only functionality explicitly.
10. Prefer mobile-first vertical information architecture.
11. Use glass cards only where they improve hierarchy.
12. Keep text contrast high.
13. Use actual workflow counts rather than AI confidence scores.
14. Do not invent backend features.
15. Do not convert the product into a generic AI assistant.

---

# 46. First Claude Design task

Generate the following core production screen set in one consistent Glass Modern design system:

```text
01 Splash / preload
02 Cases
03 Empty Cases
04 New Case / free account
05 Reconstruction overview
06 Confirm evidence
07 Unknown intervals
08 Contradictions
09 Transition to Search
10 Search overview
11 Search zone
12 Record SearchCheck
13 SearchCheck Journal
14 SearchCheck detail
15 Found item
16 Closed without finding
17 Export / Import
18 Offline state
19 Privacy / data boundary
20 Settings
21 PWA install
22 Resume Case
```

Generate the separate research-only set after the production set:

```text
R1 Reconstruction Assistant — Research only
R2 Suggested clarification question
R3 Provider unavailable / deterministic fallback
```

---

# 47. Design consistency checklist

Before accepting any screen, verify:

- [ ] Glass Modern tokens are used.
- [ ] Mobile PWA first.
- [ ] Reconstruction and Search are visibly distinct.
- [ ] User-confirmed facts are distinct from hypotheses.
- [ ] Unknown states are allowed.
- [ ] Contradictions are not auto-resolved.
- [ ] No pseudo-probabilities.
- [ ] Physical check method is visible in SearchCheck flows.
- [ ] Research-only assistant is labeled.
- [ ] Local-first / offline behavior is represented accurately.
- [ ] Bottom navigation is consistent.
- [ ] No unsupported product features were invented.
- [ ] Accessibility is preserved.
- [ ] Russian copy is concise and natural.

---

# 48. Visual shorthand for Claude Design

Use this shorthand when extending the system:

```text
MIND Detective =
calm local-first utility
+ Glass Modern
+ state-first UI
+ explicit epistemic states
+ structured Reconstruction
+ operational Search
+ method-aware SearchCheck
- chat-first
- fake AI certainty
- pseudo-probabilities
- detective noir
- gamification
```

---

# 49. Final design objective

The app should feel like a **calm cognitive tool**, not like an AI demo.

The user should always understand:

```text
What do I know?
What is still unknown?
What is contradictory?
What should I physically check next?
What have I already checked?
How did I check it?
```

That clarity is the primary design metric.
