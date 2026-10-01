# MIND Detective — Design System (Glass Modern)

MIND Detective is a **systematic lost-item search assistant**, shipped as a local-first mobile PWA (Russian first, English second). It lowers working-memory load by keeping five things visibly separate:

1. what the user actually reported (verbatim free account);
2. what the user explicitly confirmed;
3. what is still unknown or contradictory;
4. hypotheses / clarifying questions used during reconstruction;
5. physical checks performed during Search (SearchCheck).

It never guesses where an item "probably is" and never turns assistant suggestions into user memories. Core flow:

```
Free account → user-confirmed evidence → reconstruction timeline → unknown intervals / contradictions
→ explicit transition to Search → physical checks → SearchCheck journal → found / paused / closed
```

**Shorthand:** calm local-first utility + Glass Modern + state-first UI + explicit epistemic states + structured Reconstruction + operational Search + method-aware SearchCheck — minus chat-first, fake AI certainty, pseudo-probabilities, detective noir, gamification.

## Sources

- **Codebase:** https://github.com/trafficolog/mind-detective (branch `main`). Nuxt 3 PWA in `apps/web`, Python API in `apps/api`. Read: `apps/web/app/assets/css/{tokens,app}.css`, `components/**`, `lib/i18n/ru.ts` (real product copy), `docs/prototypes/2026-09-10-mind-detective-ui-prototype-review.md`, `docs/GLOSSARY.md`. Explore it further for domain rules (ADRs in `docs/adr/`, Case v2 schema in `docs/schemas/`).
- **Brief:** "MIND Detective — Claude Design System Brief · Glass Modern Mobile PWA" (pasted by the user) — the source of truth for tokens, components and screen inventory.
- **Mockups:** 5 PNG renders in `uploads/` (Дела, Журнал проверок, Поиск, Реконструкция, Новый кейс). Used for visual direction, logo mark and sample photography only.

> The shipped code (0.4.0) still uses an older neutral/teal token set (`--md-accent: #175c52`). This design system implements the **new Glass Modern direction** from the brief; the repo tokens are superseded.

### Where the mockups were overridden by the brief
The mockups contain things the brief forbids. The kit deliberately does **not** reproduce: confidence % on checks ("92%"), "Высокая вероятность" / "Возможная потеря" labels, probability rings on case cards, "Фотоанализ" as a check method, the floor-plan map (not an implemented feature), the profile avatar (no accounts), and "Ваши данные не покидают устройство" (inaccurate when an online assistant is configured).

---

## CONTENT FUNDAMENTALS

- **Language:** Russian primary, concise and natural; English secondary with identical keys. Sentence case everywhere (only the first word capitalised). No ALL CAPS except tiny section labels (letter-spaced 12px).
- **Voice:** calm, precise, non-clinical. The app speaks as a neutral tool; the user is **«вы»** (formal, lower-case). The app never says "мы найдём". User-authored actions are first-person past tense where the user reports: «Проверил — не нашёл», «Нашёл».
- **Epistemic honesty:** say what is known, not what is likely. Use state words — *Подтверждено, Неизвестно, Противоречие, Уточняющий вопрос, Не проверено, Проверено руками, Только исследование.* Never: *Вероятнее всего, ИИ уверен, Точность 92%, Восстановленная память, Мы знаем, где вещь.*
- **Counts, not scores:** «5 из 12 проверок», «3 неизвестных интервала», «2 из 6 зон». Only finite workflow counts.
- **Unknown is valid:** copy frames unknown as a legitimate end state: «Неизвестное — допустимое состояние. Интервал можно оставить неизвестным.»
- **No auto-resolution:** «Приложение не выбирает версию за вас.»
- **Privacy is precise:** «Канонические данные дела хранятся на этом устройстве.» With an assistant: «Browser → API: полный Case v2 может быть отправлен; API → провайдер: узкий контекст.»
- **Research-only is always labelled:** «Только исследование», «Предложение ассистента не становится фактом автоматически.»
- **Buttons** are verbs: Подтвердить · Не уверен · Отклонить · Проверить сейчас · Оставить неизвестным · Перейти к физическому поиску.
- **Empty & success states stay calm:** «Пока нет дел. Создайте первое дело, чтобы начать систематический поиск.» / «Вещь найдена» — no confetti, no exclamation marks.
- **Emoji:** never. Unicode symbols only for typographic use (· – « » →).

## VISUAL FOUNDATIONS

- **Mood:** calm, light, airy blue; tactile glass on a pale sky field. Non-clinical, non-gamified, zero detective clichés.
- **Background:** `--bg-ambient` — two soft radial blue glows (top-right, bottom-left) over a #F7FBFF→#EAF5FF vertical gradient. Never photographic or busy behind functional UI. No repeating patterns or textures.
- **Color:** brand blue scale 50–900; primary action `#0B86EA` (kept deliberately per brand decision, 3.8:1 with white — pair with ≥17px/650 labels). Navy text `#0B1733`, never pure black. Semantic epistemic tints (confirmed green, unknown amber, contradiction red, hypothesis indigo, research violet, neutral slate) each have `bg / fg / ink` — `fg` for icons & dots, `ink` for small text (AA). Mode identity is separate: Reconstruction = brand blue + `waypoints`, Search = operational cyan `#0A6E80` + `search`. Semantic colours are never decorative.
- **Type:** Inter (→ SF Pro → system-ui). Scale Display XL 40/44/700 → Micro 11/14/500. Tight tracking (−0.02em) on display sizes. Tabular numerals for times and counts.
- **Glass:** primary card = white 52% + `blur(22px) saturate(135%)` + 1px white 75% border + soft blue shadow + inner top highlight. Secondary (nested) = 40% + 16px blur + brand-tinted border, no shadow. Glass is used only where it creates hierarchy; never two primary glass layers stacked. `prefers-contrast: more` raises opacity to ~94%.
- **Semantic cards:** tinted diagonal gradients of the state bg (confirmed/unknown/contradiction). Research uses a **dashed violet border**; hypotheses/questions a **dashed indigo border** — dashed = "not canonical".
- **Corner radii:** xs 10 · sm 14 · md 18 · lg 24 · xl 30 · pill. Cards 20–24, nav shell 28, sheet top 30, photos 14–20, buttons & chips pill.
- **Shadows:** soft, blue-tinted (`rgba(69,118,171,…)`), large blur, low opacity; primary buttons get a blue glow `--shadow-action`. No hard/dark shadows.
- **Borders:** 1px white-alpha on glass; hairline `--line-divider` between rows. No coloured left-border accent cards.
- **Layout:** 390×844 baseline; 16px page padding (20 large phones, 24–32 tablet). Spacing 4/8/12/16/20/24/32/40. Vertical, one-column mobile IA; bottom nav floats 10px from edges with safe-area padding. Tablet may split timeline | details, zones | SearchCheck — never an analytics dashboard.
- **Hover:** glass lifts (`--shadow-glass-raised`) and whitens slightly; buttons darken to `--action-primary-hover`. **Press:** scale .98 (buttons) / .99 (cards) / .94 (icon buttons). **Focus:** 3px `--brand-400` outline, 2px offset.
- **Motion:** fast 140 / normal 200 / slow 320ms, `cubic-bezier(.2,.8,.2,1)`. Sheet rises 40px + fades; progress widths ease; chips crossfade. No bounces, particles, pulsing glows or "thinking" loops. Reduced-motion → 1ms.
- **Transparency & blur:** glass cards, bottom nav (24px blur), sheets (28px blur), round header buttons. Scrim `rgba(16,40,72,.28)`.
- **Imagery:** only real Case content — the item, the place, the checked spot, user photos. Warm natural daylight, soft depth of field, wood/interior tones that contrast gently with the cool UI. Never decorative stock. **One brand illustration exists:** `assets/splash-sphere.png` — a translucent glass sphere with soft yellow/violet fragments over sky clouds, used only on the splash/preload screen (cropped from the supplied splash mock; raster).
- **Splash:** sky-blue gradient field, left-aligned "Mind Detective" at 60/62 weight 500 (the only place the name is set in title case and a lighter weight), tagline «Превращаем фрагменты в проверяемый контекст.», sphere, thin gradient preload bar. Bar reflects real asset loading; after the service worker is ready it becomes «Готово к работе офлайн».
- **Status is never colour-only:** every chip has an icon or dot + text.

## ICONOGRAPHY

- **System:** [Lucide](https://lucide.dev) outline icons, 1.75–2px stroke, rounded caps/joins, loaded from `lucide-static@0.460.0` on unpkg by the `Icon` component (inlined SVG, `currentColor`). The repo's own UI uses ad-hoc inline SVG with the same stroke style; the mockups match Lucide closely. **Substitution flagged:** no icon font/sprite exists in the repo, so Lucide via CDN is the canonical set.
- **Canonical mapping:** Case `folder` · Reconstruction `waypoints` · Search `search` · Journal `list-checks` · Confirmed `circle-check` · Unknown `circle-help` · Contradiction `triangle-alert` · Hypothesis `lightbulb` · Question `message-circle-question` · Research `flask-conical` · Export `download` · Privacy `shield-check` · Voice `mic` · Photo `image` / `camera` · Location `map-pin`. Methods: `eye`, `hand`, `flashlight`, `package-open`, `move`, `users`.
- **Rules:** no filled/cartoon icons (only status dots are filled), no emoji, no unicode glyphs as icons. Icons sit in 44px round glass tiles in headers and timelines.
- **Logo (vector masters):** `assets/logo-lockup.svg` — official lockup (cyan→blue gradient brain + magnifier `#4AEEFC → #005CFC`, lens highlight, two-line navy `#01123A` "Mind / Detective"). `assets/logo-mark.svg` — the mark alone; `assets/logo-mark-white.svg` — mono white mark for brand-blue or photo backgrounds. PNG fallbacks: `logo-lockup.png`, `logo-mark.png`. In UI the wordmark is live type: **Mind** (navy 800) **Detective** (navy 500) — title case, never "MIND". Use the lockup on white or light glass only; keep clear space ≥ the magnifier lens diameter.
- **App icon:** `assets/app-icon.png` (1254² master) — frosted-glass rounded square with a blue brain + magnifier; derived `icon-512.png`, `icon-192.png`, `apple-touch-icon.png`. `assets/icon.svg` is the legacy teal repo icon — do not use.
- The glass app icon exists only as a PNG master (its glass/blur rendering isn't practical as SVG).

---

## Index

- `styles.css` — entry point (imports only) → `tokens/{fonts,colors,typography,spacing,effects,base}.css`, `components/components.css`
- `guidelines/` — foundation specimen cards (Colors, Type, Spacing, Effects, Brand)
- `components/` — React primitives (see below), one `*.card.html` per group
- `ui_kits/pwa/` — full click-through recreation of the mobile PWA (22 production screens + research set) — see its README
- `templates/` — starting points for consuming projects: `mobile-screen/` (blank workspace screen), `reconstruction-screen/`, `search-screen/` — each a Design Component composing this system's components
- `assets/` — `logo-lockup.svg/.png`, `logo-mark.svg/.png`, `logo-mark-white.svg`, `app-icon.png` + PWA icon sizes, `splash-sphere.png`, `photos/` (sample Case photography cropped from mockups)
- `_dev/ds-fallback.js` — dev-only in-browser transpile fallback used if `_ds_bundle.js` is missing; inert otherwise
- `SKILL.md` — Agent Skill entry point · `github.md` — source repo association

## Components

Namespace: `window.MINDDetectiveDesignSystem_90d64c`

- **core/** — `Icon`, `Button`, `IconButton`, `GlassCard`, `StatusChip`, `WorkflowProgress`
- **forms/** — `TextArea`, `ChoiceGroup`, `FilterChips`
- **navigation/** — `AppHeader`, `CaseHeader`, `BottomNav`, `ListRow`, `SectionHeader`
- **case/** — `CaseCard`, `TimelineEvent`, `EvidenceCard`, `SearchCheckCard`, `StatePanel`, `SearchTips`
- **feedback/** — `BottomSheet`, `EmptyState`, `Notice`

From the brief's inventory (§11): GlassCard, StatusChip, CaseCard, TimelineEvent, SearchCheckCard, EvidenceCard, BottomSheet, EmptyState.

### Intentional additions
- `Icon` — wrapper for the Lucide set so every glyph shares stroke/size.
- `Button`, `IconButton` — every screen's actions; brief implies them.
- `WorkflowProgress` — the only sanctioned progress display (finite counts).
- `TextArea`, `ChoiceGroup`, `FilterChips` — free account, SearchCheck method/result, list filters.
- `AppHeader`, `CaseHeader`, `BottomNav`, `ListRow`, `SectionHeader` — navigation architecture (§10) and zone/settings lists.
- `StatePanel` — tinted summary rows for unknowns / contradictions / confirmed facts (mockup pattern).
- `SearchTips` — method-tip carousel from the Search mockup (how to check, never where it probably is).
- `Notice` — privacy, offline, research-only, assistant-unavailable and invalid-import messages.
