# Crimson Slide System — 16:9 Presentation Design Prompt

> **How to use this file.** Paste this whole document into Claude as the design-system context when you ask for a slide deck. It defines the brand’s color, type, layout, elevation, shape, and component language. Every slide produced under this system is **16:9 only**. The system is a single-functional-accent crimson brand built on the **Pretendard** typeface — no other font is ever used.

-----

## Overview

This is a stark, engineering-grade presentation system: near-white `{colors.canvas-soft}` body, ink-near-black `{colors.ink}` text, a disciplined gray ladder, and one functional accent family — crimson red — anchored on `{colors.crimson}` (`#BF2B25`). Crimson carries every conversion target, every active indicator, every section eyebrow accent, every key-number highlight, and every structural emphasis. There is no second functional accent hue; the calm comes from restraint.

The system separates **functional color** from **atmospheric color**. Functional hierarchy is always crimson + ink + gray. However, the deck permits a separate **ambient prismatic gradient** as a large, blurred background atmosphere layer. This ambient gradient revives the bright Apple-like / Vercel-like glow: soft blue, cyan, violet, magenta, and amber light may appear behind title slides, section dividers, closing slides, and faint hero backdrops. These colors must never become buttons, KPI colors, chart series, icon fills, table states, or text emphasis.

The decorative crimson gradient is deliberately constrained: it begins in dark crimson and rises only to the main crimson as its brightest stop. **No coral, peach, salmon, apricot, or pink-tinted light stop is used inside the crimson gradient.** Lighter supportive surfaces are handled separately through near-neutral soft fills (`{colors.accent-soft}` / `{colors.accent-border}`), keeping the functional system sharp, technical, and free from warm cosmetic undertones.

Type is the second decisive voice. **Pretendard** carries everything — display, body, button, label, eyebrow, caption, and the technical/code layer. Headlines are sentence-case with aggressive negative letter-spacing (`-1.6px` at the 44 px slide-title size). The brand never letter-spaces positively except in small uppercase mono-style labels, where Pretendard Medium with `+0.6px` tracking stands in for a monospace face (Pretendard has no mono cut, and no substitute font is permitted).

Surfaces use a four-step ladder: `{colors.canvas}` (pure white for cards), `{colors.canvas-soft}` 98% (the slide body), `{colors.canvas-soft-2}` 95% (inset regions, code panels), and `{colors.ink}` (the deep ink-near-black used as the polarity-flipped dark band). Shadows are exceptionally subtle — every elevated card carries a stacked shadow built from `0px 1px 1px #00000005` + `0px 2px 2px #0000000a` + an inset hairline ring. Cards never float on a heavy drop-shadow; they sit on the slide held by hairline + soft glow.

**Key Characteristics:**

- **16:9 canvas only.** Every slide is authored on a `1280 × 720` pt grid (scales to `1920 × 1080`). No 4:3, no portrait, no square.
- **Single functional crimson accent.** `{colors.crimson}` (`#BF2B25`) and its darker crimson companions are the only colors used for CTAs, active states, eyebrow accents, key numbers, chart highlights, and structural emphasis.
- **Ambient prismatic atmosphere.** A separate blurred multi-color gradient may appear only as background atmosphere at title / divider / closing / hero scale. It creates light and depth, not hierarchy.
- **Dark-to-crimson structural gradient.** The brand crimson gradient runs from deep dark crimson to the core crimson, with **no light pink, coral, peach, salmon, or apricot stop**.
- **Neutral soft support tones.** Light highlight backgrounds, soft pills, row highlights, and subtle callout fills use near-neutral soft tints rather than pinkened crimson.
- **Fixed slide anatomy.** Chapter eyebrow, title, and subtitle land at the **same coordinates on every slide** (see Layout → Slide Anatomy). The reader’s eye never has to re-find the header.
- **Dense lower body.** The body region is filled edge-to-edge with supporting content — multi-column blocks, stat tiles, captioned cards — so the bottom of a slide is never left as trailing whitespace. Density is balanced, never crowded.
- **Text wordmark logo.** The logo is a **typeset wordmark** in Pretendard (no image logo, no third-party mark). It sits in the footer of every slide at a fixed position.
- **Pretendard everywhere.** One family, weights `100–900` available; the working set is `400 / 500 / 600 / 700`.
- **Stacked-shadow elevation.** Three small offsets layered with 4–12% black opacity, plus an inset hairline ring — never a single heavy drop.

-----

## Colors

### Brand & Functional Accent

The entire functional accent system is a single crimson family. Ink is retained as the text/dark-band color. The decorative crimson gradient stays within darker crimson tones and rises only to the main crimson as its brightest stop. Lighter support surfaces are handled with near-neutral soft tints rather than pink, coral, peach, salmon, or apricot derivatives.

- **Gradient Start** (`{colors.gradient-start}` — `#4F100E`): The darkest decorative crimson. Used as the starting stop of the title / divider crimson gradient.
- **Gradient Mid** (`{colors.gradient-mid}` — `#7B1815`): The middle stop of the decorative crimson gradient. A dense, restrained deep crimson.
- **Crimson** (`{colors.crimson}` — `#BF2B25`): The main brand color and the brightest stop of the crimson gradient. Carries every primary CTA, active-state indicator, eyebrow accent, key-number highlight, chart highlight, and major emphasis.
- **Crimson Deep** (`{colors.crimson-deep}` — `#971E19`): Pressed / hover state of crimson and a strong in-content accent tone for emphasis.
- **Crimson Dark** (`{colors.crimson-dark}` — `#6B1411`): Darkest in-content crimson, used for dense accents, icon fills, or crimson-on-light contrast moments.
- **Accent Soft** (`{colors.accent-soft}` — `#F3F1F1`): Near-neutral soft highlight background used for pills, soft callouts, active-row fills, and subtle grouping areas.
- **Accent Border** (`{colors.accent-border}` — `#D8CFCF`): A soft neutral border / separator tone for accent-adjacent UI chrome, selected outlines, and subtle emphasized dividers.
- **Ink** (`{colors.ink}` — `#171717`): Retained. Every heading and body paragraph on light surfaces; the fill of the polarity-flipped dark band.

### Ambient Prismatic Gradient

The ambient prismatic gradient is decorative only. It may appear behind title slides, section dividers, closing slides, and very faint hero backdrops, but it must never become a functional accent color. Do not use these colors for buttons, charts, icons, badges, table states, KPI numerals, or text emphasis.

- **Ambient Blue** (`{colors.ambient-blue}` — `#007CF0`): Cool luminous blue used as one stop of the background-only prismatic mesh.
- **Ambient Cyan** (`{colors.ambient-cyan}` — `#00DFD8`): Bright cyan / teal glow used inside the ambient mesh.
- **Ambient Violet** (`{colors.ambient-violet}` — `#7928CA`): Violet glow used to add depth and richness to the ambient mesh.
- **Ambient Magenta** (`{colors.ambient-magenta}` — `#FF0080`): High-saturation magenta glow used only as a blurred background light source.
- **Ambient Amber** (`{colors.ambient-amber}` — `#F9CB28`): Warm amber glow used only as a distant background light source.

Use the ambient gradient as a large blurred mesh, never as a hard linear rainbow. The gradient should sit behind content at low opacity, usually `12–28%` on light slides, with a white or canvas-soft wash above it when text readability is needed. It should feel like light leaking through the slide, not like a color palette fighting the crimson brand.

### Surface

- **Canvas** (`{colors.canvas}` — `#ffffff`): Pure-white card / panel / mockup surface.
- **Canvas Soft** (`{colors.canvas-soft}` — `#fafafa`): The default slide background — 98% white.
- **Canvas Soft 2** (`{colors.canvas-soft-2}` — `#f5f5f5`): Slightly deeper inset surface for code panels, inset regions, hover states.
- **Hairline** (`{colors.hairline}` — `#ebebeb`): 1 px dividers — header rules, card borders, table rows, input borders.
- **Hairline Strong** (`{colors.hairline-strong}` — `#a1a1a1`): The 500-level gray, used as a slightly-stronger divider and as de-emphasized text.

### Text

- **Ink** (`{colors.ink}` — `#171717`): Every heading and body paragraph on light surfaces.
- **Body** (`{colors.body}` — `#4d4d4d`): Secondary text — sub-headings, body captions, inactive labels, footer body.
- **Mute** (`{colors.mute}` — `#888888`): Lowest-priority text — fine print, source lines, low-key labels.
- **On Accent** (`{colors.on-accent}` — `#ffffff`): All text on `{colors.crimson}` surfaces.
- **On Ink** (`{colors.on-ink}` — `#ffffff`): All text on the `{colors.ink}` dark band.

### Semantic (in-deck use, kept minimal)

The brand is mono-accent in function, so semantic colors are used sparingly and never compete with crimson for attention. On data slides, prefer crimson + grays; reach for these only when status truly must be encoded by hue.

- **Positive** (`{colors.positive}` — `#1a7f4b`): Up / pass / on-track status only.
- **Warning** (`{colors.warning}` — `#b06a00`): Caution / pending status only.
- **Negative** (`{colors.negative}` — `#971E19`): Down / fail status — reuses the deep-crimson tone so red stays in one family.

### Brand Gradient

The brand’s structural crimson gradient is a constrained dark-to-crimson tonal sweep:

- **Crimson Gradient** (`{colors.gradient-start}` `#4F100E` → `{colors.gradient-mid}` `#7B1815` → `{colors.crimson}` `#BF2B25`)

Use this gradient when the slide needs strong crimson identity: section dividers, dramatic title slides, or closing slides. Treat the crimson gradient as one unified object. Do not crop to a single stop, do not reorder stops, do not miniaturize to an icon, and never introduce a coral, peach, salmon, apricot, or pink light stop into it.

### Ambient Gradient

For a brighter Apple-like / Vercel-like atmosphere, the system permits a separate decorative prismatic mesh:

- **Prismatic Mesh**: `{colors.ambient-blue}` `#007CF0` → `{colors.ambient-cyan}` `#00DFD8` → `{colors.ambient-violet}` `#7928CA` → `{colors.ambient-magenta}` `#FF0080` → `{colors.ambient-amber}` `#F9CB28`

This prismatic mesh is not part of the functional accent system. It is a background-only atmospheric layer. It should be heavily blurred, softly masked, and placed behind white / near-white content areas. Use it sparingly at title-slide, divider, closing, or hero scale only.

-----

## Typography

### Font Family

**Pretendard is the only typeface in the system.** No substitute, no secondary face, no monospace family. Reference the uploaded Pretendard files (`.otf` / `.ttf`, or `PretendardVariable.ttf`). Available weights: Thin 100, ExtraLight 200, Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700, ExtraBold 800, Black 900. The working set for slides is **400 / 500 / 600 / 700**.

Because Pretendard has no monospace cut and no other font may be used, the “technical label” voice is simulated with **Pretendard Medium (500), uppercase, `+0.6px` tracking** — used for eyebrows, code-panel labels, and table headers. Code blocks themselves are set in Pretendard Regular with tabular figures (`font-feature-settings: "tnum"`) for column alignment.

### Hierarchy

Sizes map to the `1280 × 720` canvas (multiply ×1.5 for `1920 × 1080`).

|Token                     |Size|Weight|Line Height|Letter Spacing|Use                                                              |
|--------------------------|----|------|-----------|--------------|-----------------------------------------------------------------|
|`{typography.title-hero}` |56px|700   |60px       |-2.0px        |Title-slide / section-divider headline only.                     |
|`{typography.slide-title}`|44px|700   |50px       |-1.6px        |The fixed-position title on every content slide.                 |
|`{typography.subtitle}`   |22px|500   |30px       |-0.6px        |The fixed-position subtitle directly under the title.            |
|`{typography.heading}`    |28px|600   |34px       |-0.8px        |In-body block headings, card-cluster headings.                   |
|`{typography.subheading}` |20px|600   |28px       |-0.4px        |Sub-block / column headings.                                     |
|`{typography.body-lg}`    |18px|400   |28px       |0             |Lead paragraph under a body heading.                             |
|`{typography.body}`       |16px|400   |24px       |0             |Default body paragraph.                                          |
|`{typography.body-strong}`|16px|600   |24px       |0             |Inline emphasis in body.                                         |
|`{typography.body-sm}`    |14px|400   |20px       |-0.2px        |Secondary body, card captions.                                   |
|`{typography.eyebrow}`    |13px|500   |16px       |+0.6px        |The fixed-position chapter eyebrow (UPPERCASE), crimson-accented.|
|`{typography.caption}`    |12px|400   |16px       |0             |Source lines, footnotes, badge labels.                           |
|`{typography.label-mono}` |12px|500   |16px       |+0.6px        |Technical labels, code-panel captions, table headers (UPPERCASE).|
|`{typography.code}`       |13px|400   |20px       |0             |Code panels (Pretendard + tabular figures).                      |
|`{typography.kpi}`        |48px|700   |52px       |-1.6px        |Big stat / KPI numerals in stat tiles.                           |
|`{typography.button}`     |15px|600   |20px       |0             |CTA / pill button labels.                                        |
|`{typography.footer}`     |11px|500   |14px       |+0.4px        |Footer wordmark + page number.                                   |

### Principles

- **Negative tracking is part of the voice.** Display and title sizes use `-2.0` to `-0.4px` tracking. Reverting to default tracking breaks the brand.
- **Sentence-case headlines.** Titles are sentence-case; a terminal period is welcome on hero/section titles. Never all-caps headlines.
- **Uppercase only for the mono-style label layer.** Eyebrows, code labels, table headers, and the footer — set in Pretendard Medium with positive tracking. Nothing else is uppercase.
- **Weight 700 is the display ceiling.** Pretendard never appears at 800 / 900 in the deck. Body emphasis tops out at 600.
- **One family, no exceptions.** If a layout seems to “need” a contrasting face, solve it with weight, size, color, or tracking — never a second font.

-----

## Layout

### Slide Format

- **16:9 only.** Author grid `1280 × 720` pt (1×) or `1920 × 1080` pt (1.5×). No other aspect ratio is ever produced.
- **Outer safe margin:** `64px` left/right, `56px` top, `36px` bottom on the 1280-grid.

### Spacing System

- **Base unit:** 4 px. Every spacing value is a multiple of 4.
- **Tokens:** `{spacing.xxs}` 4 · `{spacing.xs}` 8 · `{spacing.sm}` 12 · `{spacing.md}` 16 · `{spacing.lg}` 24 · `{spacing.xl}` 32 · `{spacing.2xl}` 40 · `{spacing.3xl}` 48 · `{spacing.4xl}` 64.
- **Card interior padding:** `{spacing.lg}` 24 to `{spacing.xl}` 32.
- **Inline gap:** button rows, chip rows, column gutters use `{spacing.md}` 16 to `{spacing.lg}` 24.

### Slide Anatomy (FIXED POSITIONS — apply to every content slide)

The header block is locked to the same coordinates on every content slide so chapter / title / subtitle never shift. On the 1280 × 720 grid:

|Zone                      |Position (x, y)                  |Spec                                                                                                        |
|--------------------------|---------------------------------|------------------------------------------------------------------------------------------------------------|
|**Chapter eyebrow**       |x `64`, y `56`                   |`{typography.eyebrow}`, color `{colors.crimson}`, UPPERCASE. Often prefixed with a `24px` crimson tick rule.|
|**Slide title**           |x `64`, y `84`                   |`{typography.slide-title}`, color `{colors.ink}`. Single line preferred; wraps to two at most.              |
|**Subtitle**              |x `64`, y (title baseline + `16`)|`{typography.subtitle}`, color `{colors.body}`. One line.                                                   |
|**Header rule**           |full content width, y `184`      |1 px `{colors.hairline}` divider separating header from body.                                               |
|**Body region**           |x `64`–`1216`, y `208`–`664`     |The working canvas. Filled densely (see below).                                                             |
|**Footer wordmark**       |x `64`, y `684`                  |Text logo, `{typography.footer}`, `{colors.mute}`.                                                          |
|**Footer page no.**       |x `1216` (right-aligned), y `684`|`{typography.footer}`, `{colors.mute}`.                                                                     |
|**Footer rule (optional)**|full width, y `672`              |1 px `{colors.hairline}` above footer.                                                                      |

Section-divider slides break this anatomy intentionally (see `slide-section-divider`), but **all content slides obey it exactly**.

### Body Density & Vertical Balance

The body region (`y 208 → 664`, ≈ 456 px tall) must be **filled to the bottom edge** with intentional content — never left half-empty with a stack of bullets floating at the top.

- **Default to multi-column.** Split the body into 2- or 3-up columns of cards / stat tiles / captioned blocks so content reaches `y ≈ 640`.
- **Anchor the bottom band.** Reserve the lower strip (`y ≈ 520 → 656`) for a supporting row: a `stat-tile` trio, a source/methodology caption row, a mini-legend, or a key-takeaway callout bar.
- **Balanced, not crowded.** Target ~80–90% vertical fill of the body region. Keep `{spacing.lg}` gutters; density comes from *more blocks*, not from shrinking whitespace inside blocks.
- **If content is genuinely short,** scale up: promote a key number to a `{typography.kpi}` stat tile, add a captioned chart, or add a “What this means” callout — rather than leaving the lower half blank.

### Grid & Container

- **Content width:** 1152 px (1280 − 2×64 margin), centered.
- **Column patterns:** 2-up (576 / 576 minus gutter), 3-up (~362 each), 4-up stat row, or an 8/4 split (main body + side rail). Gutters `{spacing.lg}` 24.

### Responsive / Export Strategy

This is a fixed-canvas presentation system; “responsive” means clean export at the two supported scales only.

- **1× (1280 × 720)** authoring grid.
- **1.5× (1920 × 1080)** export — multiply every px value by 1.5.
- Gradient backdrops render as full-bleed flat 2-D fills, scaled to the canvas, never tiled or cropped.

-----

## Elevation & Depth

|Level                   |Treatment                                                                                           |Use                                                                          |
|------------------------|----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
|Level 0 — Flat          |No shadow, no border.                                                                               |Full-bleed title bands and the polarity-flipped dark `{colors.ink}` sections.|
|Level 1 — Inset Hairline|`0 0 0 1px #00000014` inset.                                                                        |Default card chrome — the “you can see this card” cue.                       |
|Level 2 — Subtle Drop   |`0px 1px 1px #00000005, 0px 2px 2px #0000000a` + inset hairline.                                    |Stat tiles, template cards.                                                  |
|Level 3 — Soft Stack    |`0px 2px 2px #0000000a, 0px 8px 8px -8px #0000000a` + inset hairline.                               |Feature / content cards.                                                     |
|Level 4 — Float Stack   |`0px 2px 2px #0000000a, 0px 8px 16px -4px #0000000a` + inset hairline.                              |Callout panels, KPI cards.                                                   |
|Level 5 — Modal         |`0px 1px 1px #00000005, 0px 8px 16px -4px #0000000a, 0px 24px 32px -8px #0000000f` + inset hairline.|Overlays / dropdowns (if used in interactive exports).                       |

The system uses **stacked** shadows — multiple small offsets layered to fake natural light — never a single 8 px generic drop. Inset hairline rings are always added so card edges stay crisp.

### Decorative Depth

- **Ambient prismatic gradient as atmosphere:** the multi-color prismatic mesh is the brightest decorative depth cue. It appears only as a large blurred background atmosphere, never as a functional accent.
- **Dark-to-crimson gradient as identity:** the tonal crimson sweep provides strong brand identity on title / divider / closing slides. It never fades into a pink, coral, peach, salmon, or apricot endpoint.
- **Polarity-flipped dark band:** switching a slide from `{colors.canvas-soft}` to `{colors.ink}` is the chief depth cue between sections.
- **Inset + drop combo:** an inset 1 px ring plus a multi-stop drop makes a card “sit on the slide” without feeling material-heavy.

-----

## Shapes

### Border Radius Scale

|Token              |Value |Use                                           |
|-------------------|------|----------------------------------------------|
|`{rounded.none}`   |0px   |Full-bleed title / footer bands.              |
|`{rounded.xs}`     |4px   |Tightest inline pill, tag chips.              |
|`{rounded.sm}`     |6px   |Base UI radius — buttons, inputs, code panels.|
|`{rounded.md}`     |8px   |Feature cards, stat tiles, content cards.     |
|`{rounded.lg}`     |12px  |Larger callout panels, KPI cards.             |
|`{rounded.xl}`     |16px  |Cards hosting an image cap.                   |
|`{rounded.pill-sm}`|64px  |Ghost tab pills.                              |
|`{rounded.pill}`   |100px |Marketing-scale CTA pill.                     |
|`{rounded.full}`   |9999px|Circular icon containers, dot indicators.     |

### Image & Mockup Geometry

- **Ambient prismatic gradient:** full-bleed or large-scale blurred 2-D atmospheric backdrop, never cropped into a small frame, never used as an icon, and never used as a chart or UI color.
- **Dark-to-crimson gradient:** full-bleed 2-D identity backdrop, never cropped to a frame, never lightened into pink/coral.
- **Charts / diagrams:** rendered inside `{rounded.md}` chrome on `{colors.canvas}`.
- **Code panel:** dark `{colors.ink}` rectangle, `{rounded.sm}`, mono-style label in crimson.
- **Photos / thumbnails:** 16:9 inside `{rounded.md}`–`{rounded.lg}` with a Level 3 stacked shadow.

-----

## Components

### Logo (Text Wordmark)

**`logo-wordmark`** — the brand logo is **typeset text**, never an image mark.

- Brand name set in **Pretendard Bold (700)**, `{colors.ink}` (or `{colors.on-ink}` on dark bands), with a single crimson element permitted (e.g., a crimson period or a crimson dot after the name). Footer instances use `{typography.footer}` in `{colors.mute}`.
- Fixed footer position (x `64`, y `684`) on every content slide. On the title slide it may appear larger, centered or top-left, still as text.

### Buttons

**`button-primary`** — the crimson conversion pill.

- Background `{colors.crimson}`, text `{colors.on-accent}`, label `{typography.button}`, padding `0 {spacing.lg}`, height ~44px, shape `{rounded.pill}`. Hover/pressed → `{colors.crimson-deep}`.

**`button-secondary`** — the white pill paired with the crimson primary.

- Background `{colors.canvas}`, text `{colors.ink}`, 1 px `{colors.hairline}` border, same typography / shape as `button-primary`.

**`button-ghost`** — low-emphasis text action.

- Transparent bg, text `{colors.crimson}`, no border, `{typography.button}`. Underline on hover.

**`tab-ghost`** — centered tab pill row.

- Background `{colors.canvas}`, text `{colors.ink}`, active tab → `{colors.accent-soft}` fill + `{colors.crimson}` text, `{typography.body-sm}`, padding `0 {spacing.md}`, shape `{rounded.pill-sm}`.

### Cards & Containers

**`card-content`** — canonical content card (3-up / 2-up body blocks).

- Background `{colors.canvas}`, text `{colors.ink}`, padding `{spacing.lg}` 24, shape `{rounded.md}`. Level 3 soft-stack shadow. Optional crimson top-rule (`2px {colors.crimson}`) as accent.

**`card-callout`** — larger emphasis panel for a key point.

- Background `{colors.canvas}`, padding `{spacing.xl}` 32, shape `{rounded.lg}`. Level 4 float-stack. A `4px` crimson left-rule marks it as the slide’s takeaway.

**`card-soft`** — soft-tinted grouping card.

- Background `{colors.accent-soft}`, padding `{spacing.lg}`, shape `{rounded.md}`. Use for accent-adjacent grouping only; use `{colors.canvas-soft}` for neutral grouping.

**`stat-tile`** — the bottom-band KPI tile (drives density).

- Background `{colors.canvas}`, padding `{spacing.lg}`, shape `{rounded.md}`, Level 2 shadow. Inside: KPI numeral in `{typography.kpi}` `{colors.crimson}`, label below in `{typography.label-mono}` `{colors.body}`, optional delta caption in `{typography.caption}`.

**`callout-bar`** — full-width key-takeaway strip for the bottom band.

- Background `{colors.accent-soft}`, text `{colors.ink}`, `4px` crimson left-rule, optional 1 px `{colors.accent-border}` border, padding `{spacing.md} {spacing.lg}`, shape `{rounded.sm}`. Holds one line of “What this means.”

**`code-panel`** — dark code / data preview.

- Background `{colors.ink}`, text `{colors.on-ink}`, body `{typography.code}` (Pretendard + tabular figures), an UPPERCASE crimson `{typography.label-mono}` caption, padding `{spacing.lg}`, shape `{rounded.sm}`.

### Data Display

**`data-table`** — slide table.

- Header row: `{colors.canvas-soft}` background, `{typography.label-mono}` UPPERCASE `{colors.body}`. Body rows: `{typography.body-sm}`, 1 px `{colors.hairline}` row dividers. Active / highlighted row: `{colors.accent-soft}` fill with optional `{colors.accent-border}` outline. Numerals tabular-aligned, right-set.

**`chart`** — chart frame.

- Primary series `{colors.crimson}`, secondary `{colors.crimson-deep}`, tertiary / context in grays. Use line weight, opacity, dash style, or marker shape before introducing additional hue. Gridlines `{colors.hairline}`. Title in `{typography.subheading}`, axis labels `{typography.caption}` `{colors.mute}`. Single functional accent — do not introduce non-crimson series colors unless a hue must encode status, and then use the minimal semantic set.

**`legend`** — compact legend row in the bottom band.

- Dot indicators (`{rounded.full}`) + `{typography.caption}` labels, `{spacing.md}` gaps. Primary dot `{colors.crimson}`, secondary dot `{colors.crimson-deep}`, contextual dots in gray.

### Navigation / Structure

**`slide-progress`** — optional thin progress / section indicator.

- A row of `{rounded.full}` dots; current section dot `{colors.crimson}`, others `{colors.hairline-strong}`. Sits in footer band, centered.

### Signature Slide Templates

**`slide-title`** — the deck opener.

- Background `{colors.canvas}` or `{colors.canvas-soft}` with a large, blurred ambient prismatic gradient occupying the top / center atmosphere. The gradient should remain soft, luminous, and low-opacity, with readable text placed on clean white or near-white space. Eyebrow (`{typography.eyebrow}` crimson) → hero headline (`{typography.title-hero}`, sentence-case, period-terminated) → one-line subtitle (`{typography.subtitle}` `{colors.body}`) → CTA row with `button-primary` + `button-secondary` → presenter / date line in `{typography.caption}`. `logo-wordmark` larger here, text only. All functional accents remain crimson.

**`slide-title-dark`** — dramatic crimson title variant.

- Background `{colors.canvas}` with the dark-to-crimson tonal gradient occupying the top ~55% as an atmospheric identity backdrop. The gradient must terminate at `{colors.crimson}` as its brightest stop and must not fade into coral, peach, salmon, apricot, or pink. Use when the deck needs a heavier, darker, more dramatic opening.

**`slide-section-divider`** — chapter break (intentionally breaks the fixed anatomy).

- Polarity-flipped `{colors.ink}` full-bleed band, dark-to-crimson gradient band, or restrained ambient prismatic band. Large chapter number in `{typography.kpi}` crimson, chapter title in `{typography.title-hero}` `{colors.on-ink}` on dark variants or `{colors.ink}` on light variants. Minimal else.

**`slide-content`** — the workhorse.

- Obeys the fixed Slide Anatomy exactly: eyebrow / title / subtitle / header rule at locked coordinates, dense body region, footer wordmark + page number. Body filled per the Density rules (multi-column + bottom anchor band). A faint ambient prismatic glow may appear in a far corner at low opacity only if it does not compete with the content.

**`slide-stat`** — KPI-led slide.

- Standard header; body = a 3- or 4-up `stat-tile` row up top, supporting `card-content` blocks and a `callout-bar` filling the bottom band. KPI numerals use `{colors.crimson}` only.

**`slide-comparison`** — 2-up compare.

- Standard header; body split into two `card-content` columns; a `callout-bar` spans the bottom with the verdict.

**`slide-closing`** — wrap / CTA.

- Ambient prismatic gradient backdrop or dark-to-crimson gradient backdrop, headline in `{typography.title-hero}`, a `button-primary` + `button-secondary` row, contact line in `{typography.caption}`, `logo-wordmark` text. CTA remains crimson even when the prismatic background is present.

-----

## Ambient Gradient Usage Rules

- Use the prismatic ambient gradient only on title slides, section dividers, closing slides, and subtle hero backdrops.
- Keep opacity low: `12–28%` on light slides, `20–40%` only on dark divider slides.
- Always blur heavily: `80–160px` visual blur equivalent.
- Keep readable text on clean `{colors.canvas}` / `{colors.canvas-soft}` / `{colors.ink}` areas.
- Crimson remains the only functional accent color.
- Do not use ambient colors for charts, buttons, icons, badges, KPI numerals, table highlights, active states, callout rules, or progress indicators.
- Do not create small rainbow decorations. The prismatic gradient lives at atmospheric scale only.
- Treat ambient colors as light, not as palette. They may glow behind content, but they must not define hierarchy.

-----

## Do’s and Don’ts

### Do

- Author **16:9 only** on the `1280 × 720` (or `1920 × 1080`) grid — no other aspect ratio, ever.
- Use **only Pretendard**, weights 400–700 for content, with negative tracking on display sizes. Solve any “needs contrast” moment with weight / size / color / tracking.
- Lock the **chapter eyebrow, title, and subtitle to their fixed coordinates** on every content slide so the header never shifts.
- Reserve `{colors.crimson}` (`#BF2B25`) for the single functional accent role: CTAs, active states, eyebrow accents, key numbers, chart highlights, and the lone structural crimson gradient.
- Use the main `{colors.crimson}` as the brightest point of the crimson brand gradient; darker tones should lead into it.
- Use the prismatic ambient gradient as a large, blurred background atmosphere when the deck needs a brighter Apple-like / Vercel-like mood.
- Keep `{colors.crimson}` as the only functional accent even when the ambient gradient is present.
- Separate atmosphere from hierarchy: ambient colors create light and depth; crimson creates emphasis and action.
- Keep brighter supportive surfaces near-neutral using `{colors.accent-soft}` and `{colors.accent-border}` rather than pinkened crimson tints.
- **Fill the body region to the bottom** with intentional density — multi-column cards plus a bottom anchor band (stat tiles, callout bar, source row). Aim for ~80–90% vertical fill.
- Render the logo as a **text wordmark** in Pretendard, fixed in the footer of every slide.
- Layer stacked shadows (small offsets + inset hairline ring) rather than a single heavy drop.
- Cycle slide surfaces through `{colors.canvas-soft}` → `{colors.canvas}` → `{colors.ink}` polarity-flipped bands; the dark band IS the depth cue.

### Don’t

- Don’t produce 4:3, portrait, or square slides. The system is 16:9 only.
- Don’t introduce any font other than Pretendard, and don’t load a separate monospace face — simulate the mono label voice with Pretendard Medium + uppercase + positive tracking.
- Don’t introduce a second functional accent hue. The system is functionally mono-accent crimson; semantic status colors are the only exception, used sparingly.
- Don’t let ambient gradient colors become UI accents.
- Don’t use cyan, magenta, violet, amber, or blue for buttons, chart series, active states, KPI numbers, table highlights, icons, or callout rules.
- Don’t make the prismatic gradient small, sharp, or icon-like. It should feel like a distant glow, not a decorative sticker.
- Don’t introduce coral, peach, salmon, apricot, or pink-tinted highlight stops into the crimson gradient.
- Don’t use light crimson washes for soft backgrounds when a neutral-soft accent fill would achieve the same hierarchy more cleanly.
- Don’t let the chapter / title / subtitle drift to different positions between slides.
- Don’t leave the lower body region as trailing whitespace — anchor it with a supporting row instead.
- Don’t use an image / icon logo or any third-party mark; the logo is typeset text.
- Don’t render headlines in all-caps; sentence-case + negative tracking is non-negotiable.
- Don’t promote Pretendard past weight 700 in the deck, and don’t drop a single heavy drop-shadow on cards.
- Don’t render the crimson gradient at icon scale, reorder its stops, or inject a non-crimson hue into it; it lives at title / divider scale only.