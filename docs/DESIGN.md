---
name: Deep Focus Protocol
colors:
  surface: '#10131a'
  surface-dim: '#10131a'
  surface-bright: '#363941'
  surface-container-lowest: '#0b0e15'
  surface-container-low: '#191b23'
  surface-container: '#1d2027'
  surface-container-high: '#272a31'
  surface-container-highest: '#32353c'
  on-surface: '#e1e2ec'
  on-surface-variant: '#c2c6d6'
  inverse-surface: '#e1e2ec'
  inverse-on-surface: '#2e3038'
  outline: '#8c909f'
  outline-variant: '#424754'
  surface-tint: '#adc6ff'
  primary: '#adc6ff'
  on-primary: '#002e6a'
  primary-container: '#4d8eff'
  on-primary-container: '#00285d'
  inverse-primary: '#005ac2'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#ffb3ad'
  on-tertiary: '#68000a'
  tertiary-container: '#ff5451'
  on-tertiary-container: '#5c0008'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#d8e2ff'
  primary-fixed-dim: '#adc6ff'
  on-primary-fixed: '#001a42'
  on-primary-fixed-variant: '#004395'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3ad'
  on-tertiary-fixed: '#410004'
  on-tertiary-fixed-variant: '#930013'
  background: '#10131a'
  on-background: '#e1e2ec'
  surface-variant: '#32353c'
typography:
  h1:
    fontFamily: Manrope
    fontSize: 40px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  h2:
    fontFamily: Manrope
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  h3:
    fontFamily: Manrope
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.4'
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  xxl: 64px
  container-padding: 32px
  gutter: 24px
---

## Brand & Style

This design system is engineered for high-performance cognitive work, prioritizing "Deep Work" states by minimizing visual noise. The personality is professional, sophisticated, and quietly authoritative. It avoids the cluttered density of traditional project management tools in favor of a premium, modern web app aesthetic that feels more like a focused IDE or a high-end creative suite.

The style is a fusion of **Minimalism** and **Modern Corporate**, utilizing tonal layering rather than harsh borders. By employing a dark neutral base, the system reduces eye strain during long sessions. Premium touches include subtle linear gradients on primary actions and deliberate micro-interactions that provide tactile feedback without distraction.

## Colors

The palette is anchored in a nearly-black background to create a "void" effect, allowing content to float. The neutral scales use cool-toned grays to maintain a professional atmosphere. 

- **Primary Blue (#3B82F6):** Reserved strictly for primary calls-to-action and active states.
- **Success Green (#10B981):** Used for completion toggles, progress bars, and "Done" statuses.
- **Urgency Red (#EF4444):** Employed sparingly for overdue deadlines, critical alerts, and destructive actions.
- **Text:** High-contrast off-white (`#F8FAFC`) ensures readability against the deep background, while secondary text is significantly de-emphasized to guide the user's focus.

## Typography

This design system uses **Manrope** for headlines to provide a refined, modern geometric touch, while **Inter** is utilized for body and UI elements due to its exceptional legibility in dark mode. 

The typographic hierarchy relies on significant scale differences and the use of "Muted" color tokens for secondary information. Uppercase labels with slight tracking (letter-spacing) are used for metadata and category headers to provide structural anchors without requiring heavy borders.

## Layout & Spacing

The layout philosophy follows a **Fluid Grid** with generous internal margins to promote a sense of calm. 

- **Ample Whitespace:** Spacing is used as a primary separator instead of lines. Components are given significant "breathing room" (minimum 24px) to prevent the UI from feeling cramped.
- **Rhythm:** A 4px baseline grid ensures vertical consistency.
- **Content Max-Width:** While the dashboard is fluid, individual task views and document editors are constrained to a centered 800px column to maintain optimal line lengths for reading.

## Elevation & Depth

Hierarchy is established through **Tonal Layers** and **Ambient Shadows**. 

- **Surface Tiers:** The background is the darkest level (`#020617`). Cards and containers sit one level higher (`#0F172A`). Hover states and active modals sit at the highest level (`#1E293B`).
- **Shadows:** Shadows are large, soft, and extremely subtle. Use a `0px 10px 30px` spread with a very low opacity (`0.4`) of the base background color.
- **Gradients:** A faint 10% opacity linear gradient (Top-Left to Bottom-Right) is applied to primary buttons and active progress bars to simulate a light source from the top-left, adding to the premium feel.

## Shapes

The shape language is defined by large, friendly radii that soften the technical nature of task management. 

- **Standard Containers:** Cards and main UI panels use a **12px** radius.
- **Large Elements:** Primary action buttons and focus-state modals use a **16px** radius.
- **Interactive States:** Soft rounded corners (8px) are applied to smaller elements like inputs and dropdown items.

## Components

- **Buttons:** Primary buttons feature the Primary Blue with a subtle top-light gradient. Ghost buttons use a low-opacity white border (`rgba(255,255,255,0.1)`) that brightens on hover.
- **Task Cards:** Use a 1px solid border (`#1E293B`) only as a fallback; primarily rely on the `surface` color to distinguish them from the background. On hover, the card should lift slightly using a shadow and an increase in surface brightness.
- **Checkboxes:** Custom-designed circular checkboxes. When checked, they fill with Success Green and trigger a subtle strike-through animation on the task title.
- **Chips/Badges:** Pill-shaped with low-opacity backgrounds (e.g., 10% opacity of the status color) and high-contrast text for a sophisticated "glass" look without full backdrop blurs.
- **Input Fields:** Deep background fills with a 2px bottom-border focus state in Primary Blue. Labels should float or remain visible in a muted color to maintain context.
- **Progress Bars:** Thin (4px-6px) tracks using a dark neutral, with the "Success Green" fill featuring a glowing micro-shimmer effect during active updates.
- **Micro-interactions:** All transitions (hover, focus, toggle) must use a 200ms `ease-out` curve to feel responsive yet smooth.