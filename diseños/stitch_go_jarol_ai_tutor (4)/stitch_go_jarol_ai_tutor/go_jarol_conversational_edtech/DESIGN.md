---
name: Go Jarol Conversational EdTech
colors:
  surface: '#f7f9ff'
  surface-dim: '#c9dcf1'
  surface-bright: '#f7f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#edf4ff'
  surface-container: '#e2efff'
  surface-container-high: '#d8eaff'
  surface-container-highest: '#d2e5f9'
  on-surface: '#0a1d2c'
  on-surface-variant: '#3f484a'
  inverse-surface: '#203242'
  inverse-on-surface: '#e7f2ff'
  outline: '#6f797a'
  outline-variant: '#bec8ca'
  surface-tint: '#0c6870'
  primary: '#005158'
  on-primary: '#ffffff'
  primary-container: '#126b73'
  on-primary-container: '#9ee9f2'
  inverse-primary: '#88d3db'
  secondary: '#a43c28'
  on-secondary: '#ffffff'
  secondary-container: '#fd7e64'
  on-secondary-container: '#711707'
  tertiary: '#654200'
  on-tertiary: '#ffffff'
  tertiary-container: '#845800'
  on-tertiary-container: '#ffd69e'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#a4eff8'
  primary-fixed-dim: '#88d3db'
  on-primary-fixed: '#002023'
  on-primary-fixed-variant: '#004f55'
  secondary-fixed: '#ffdad3'
  secondary-fixed-dim: '#ffb4a5'
  on-secondary-fixed: '#3e0400'
  on-secondary-fixed-variant: '#842513'
  tertiary-fixed: '#ffddb1'
  tertiary-fixed-dim: '#f8bc60'
  on-tertiary-fixed: '#291800'
  on-tertiary-fixed-variant: '#624000'
  background: '#f7f9ff'
  on-background: '#0a1d2c'
  surface-variant: '#d2e5f9'
typography:
  display:
    fontFamily: Sora
    fontSize: 40px
    fontWeight: '800'
    lineHeight: 48px
  headline-lg:
    fontFamily: Sora
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
  headline-lg-mobile:
    fontFamily: Sora
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 34px
  headline-md:
    fontFamily: Sora
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
  headline-sm:
    fontFamily: Sora
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-sm:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  label-lg:
    fontFamily: Sora
    fontSize: 15px
    fontWeight: '700'
    lineHeight: 20px
  label-md:
    fontFamily: Sora
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
  label-sm:
    fontFamily: Sora
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-tablet: 1.5rem
  gutter-desktop: 2rem
  margin: 1rem
  margin-tablet: 2rem
  margin-desktop: 3rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

The design system establishes a warm, engaging, and cognitively accessible learning environment crafted specifically for secondary and high school students in Mexico (ages 12–18). Drawing inspiration from game-like micro-feedback loops and pairing them with radical editorial clarity, the system transforms academic study into an encouraging dialogue with an empathetic mentor.

### Design Archetype & Movement
- **Movement:** Tactile Modernism meets Warm Minimal Messaging.
- **Atmosphere:** Safe, approachable, and intellectually stimulating. It balances high-energy motivational accents with a calm, paper-like background that mitigates visual fatigue during prolonged study sessions.
- **Interactivity:** Buttons and actionable components feature subtle physical micro-depth (chunky 2D tactile drop-edges inspired by playful educational apps) that depress upon interaction, providing immediate physical delight without visual clutter.

## Colors

The palette balances authoritative teal depth with radiant tropical warmth, grounding educational authority while maintaining high empathy and youth appeal.

### Palette Architecture
- **Primary Teal (`#126B73`):** Anchors brand authority, system navigation, and AI identity cues.
- **Secondary Coral (`#E76D55`):** Serves as an energetic prompt accent, celebration state, and primary call-to-action color.
- **Warm Yellow Accent (`#E4AA50`):** Highlights streaks, hints, achievements, and contextual micro-tips.
- **Soft Teal Tint (`#DCEFEB`):** Provides a soothing, low-saturation backdrop for AI dialogue bubbles, focus containers, and active filters.
- **Warm Canvas (`#F7F5EF`):** A restful, paper-tinted neutral surface that eliminates pure-white eye strain.
- **Clean Surface (`#FFFFFF`):** Reserved for floating cards, user speech bubbles, modal panels, and persistent docks.
- **Deep Ink (`#0B1E2D`):** High-legibility neutral for primary reading, academic text, and prominent typography.
- **Slate Muted (`#596B72`):** Supportive tone for timestamps, metadata, inactive tab indicators, and subtle instructions.
- **Subtle Outline (`#E8E5DC`):** Organic, low-contrast boundary line for structuring containers without creating rigid grid friction.

## Typography

The type system pairs the geometric, friendly rhythm of **Sora** for brand headers and button actions with the high-legibility, humanist clarity of **Atkinson Hyperlegible Next** for conversational reading and conceptual comprehension.

- **Headings & Badges (Sora):** Carries wide apertures, open forms, and geometric confidence that feels dynamic and optimistic for teenage learners.
- **Reading & Chat (Atkinson Hyperlegible Next):** Features distinctive glyph distinctions (such as clear differentiations between uppercase `I`, lowercase `l`, and digit `1`), providing an effortless reading experience across science formulas, math problems, and conversational paragraphs.
- **Body Rhythm:** All body copy enforces a relaxed 1.55–1.62× line-height to maintain comfortable visual cadence during conversational tutoring sessions.

## Layout & Spacing

The layout is built around a single-stream conversational architecture prioritizing cognitive focus. The visual canvas prevents sensory overload through disciplined white space and centered reading columns.

### Spatial Logic & Breakpoints
- **Mobile (< 768px):** Single-column layout. Chat thread occupies full viewport width with a persistent floating input pill anchored above the bottom safe area. Outer padding is set to `1rem`.
- **Tablet (768px – 1024px):** Conversational feed constrained to a centered reading column (maximum 680px), flanked by contextual quick actions or milestone counters.
- **Desktop (> 1024px):** 12-column fluid grid containing a persistent, slim pedagogical sidebar (280px) and a primary tutor viewport (max 760px). Wide lateral margins frame the workspace calmly.

## Elevation & Depth

Visual hierarchy combines clean, flat layers with tactile micro-depth on active touch targets.

### Layering Principles
- **Base Layer:** `#F7F5EF` canvas sets an untextured, matte foundation.
- **Surface Elevation (Cards & Panels):** High-order chat cards and educational blocks use `#FFFFFF` bordered with a 1.5px solid boundary in `#E8E5DC`, paired with an ambient shadow: `0 4px 16px rgba(11, 30, 45, 0.04)`.
- **Interactive Depth (Tactile Edge):** Primary interactive elements (buttons, chip selectors) utilize a Duolingo-inspired physical edge created with solid directional offset shadows:
  - Default: `box-shadow: 0 4px 0 #0D4E54` (for Teal Primary) or `0 4px 0 #C4533C` (for Coral CTA).
  - Active / Pressed: Translates down 2px with `box-shadow: 0 2px 0 #...`, delivering tactile physical feedback.
- **Floating Input Dock:** The chat input bar floats over the conversation with a diffused glass-matte backdrop: `#FFFFFF` at 95% opacity, backdrop blur of 12px, bordered by `#E8E5DC`, and elevated by `0 8px 24px rgba(11, 30, 45, 0.08)`.

## Shapes

The design uses generous, organic roundedness to project warmth and reduce academic anxiety, while retaining structured boundaries for instructional diagrams and mathematical notation.

- **Containers & Surfaces:** Modals, educational panels, and quiz summaries use `rounded-xl` (1.5rem / 24px).
- **Cards & Chat Bubbles:** Content bubbles utilize `rounded-lg` (1rem / 16px) with intentional asymmetrical corner smoothing: AI messages feature a sharp bottom-left corner (`4px`), while user speech bubbles feature a sharp bottom-right corner (`4px`).
- **Interactive Controls:** Buttons, chips, and the floating chat bar utilize complete pill forms (`9999px`) to emphasize touch-friendliness and playfulness.

## Components

### Buttons
- **Primary Action (Teal / Coral):** Pill-shaped with `label-lg` uppercase typography. Height: 48px on mobile, 52px on desktop. Displays a solid 4px tactile under-lip shadow.
- **Secondary Action:** White surface `#FFFFFF`, border 2px solid `#E8E5DC`, text `#0B1E2D`, with a 3px tactile drop shadow in `#E8E5DC`.
- **Ghost Action:** Borderless, soft hover tint `#DCEFEB` with `#126B73` label.

### Chat Bubbles & Conversational Stream
- **AI Tutor Bubble:** Background `#FFFFFF` or `#DCEFEB`, border 1.5px solid `#E8E5DC`. Features an avatar anchor, comfortable line spacing, and subtle formatting tags for formulas and key vocabulary terms.
- **User Bubble:** Background `#126B73`, text `#FFFFFF`, rounded pill contour, aligned right.

### Suggestion Chips & Prompt Starters
- Compact pill-shaped modules (`height: 36px`) with 1.5px solid `#E8E5DC` on `#FFFFFF`. On hover, fills with `#DCEFEB` and active border `#126B73`. Serves as quick-reply conversational prompts.

### Floating Conversational Input
- High-visibility pill container suspended at the bottom. Houses an expandable multi-line text input, an attachment/camera button for homework photos, and a circular coral send button with a spring-press interaction.

### Form Inputs & Checkboxes
- **Input Fields:** `#FFFFFF` background, 2px border in `#E8E5DC`, transitioned to `#126B73` on focus with a smooth 3px outer glow ring in `rgba(18, 107, 115, 0.15)`.
- **Selection Checks & Radios:** 24px rounded squares and circles with a 2px border. Selected state fills with `#126B73` and displays a bold white checkmark icon.

### Concept & Flash Cards
- Contained modular cards (`#FFFFFF`) with a top color-coded badge indicating subject discipline (e.g., Mathematics in Teal, History in Coral, Biology in Warm Yellow). Uses subtle micro-borders and organized metadata labels.