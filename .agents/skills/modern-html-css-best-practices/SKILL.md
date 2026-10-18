---
name: modern-html-css-best-practices
description: >-
  Principal Frontend UI & Modern Web Engineering skill for semantic HTML5, modern
  CSS architectures, zero-collision padding standards, and fluid responsive design
  across Windows Desktop and Android (Samsung Galaxy S26 Ultra). Activate whenever
  writing, refactoring, or reviewing HTML markup, Tailwind/CSS styling, layout
  containment, accessibility (a11y), responsive grids, badges/pills, or canvas
  visualizers.
---

# Modern HTML5 & CSS Architecture Best Practices Skill

Apply Principal Frontend Engineering and modern Web Standards (W3C / WHATWG / MDN) across all markup, styling, and design system components.

---

## 1. Zero-Collision Layout & Border Buffer Invariants

Text glyphs, status badges, and SVG icons must **never** touch, collide with, or crowd bounding borders, outlines, or neighboring controls.

1. **The Inset Gutter Hierarchy:**
   - **Chassis & Deck Panels:** Minimum padding of `1rem` to `1.25rem` (`p-4` to `p-5`).
   - **Cards & Preset Tiles:** Minimum padding of `0.85rem` to `1.15rem` (`p-3.5` to `p-4.5`).
   - **Internal Spacers:** Sub-elements inside cards (e.g. titles, metadata rows, actions) must have dedicated horizontal padding (`px-1` or `px-1.5`) and element gaps (`gap-2` to `gap-2.5`).
2. **Pill & Badge Padding Formulas:**
   - Badges and status pills must always declare:
     - `display: inline-flex;` with `align-items: center;`
     - `line-height: 1;` (or Tailwind `leading-none`) to prevent font descender line-box distortion.
     - Minimum horizontal padding of `0.75rem` to `0.875rem` (`px-3` to `px-3.5`) and vertical padding of `0.35rem` to `0.45rem` (`py-1.5`).
     - Distinct inner icon clearance (`gap-1.5` with `shrink-0`).
3. **Box Sizing & Outline Offset:**
   - Always ensure `box-sizing: border-box` across all containers.
   - When using outer focus or status borders, prefer `outline-offset: -2px` to `-3px` or an inset box shadow (`box-shadow: inset 0 0 0 1px ...`) to eliminate layout shift and prevent content clipping.
4. **Universal SVG & Span Safe Clearance Standard:**
   - All `svg` icons must declare `box-sizing: content-box;` and have padding in front of them (`padding-inline-start: 0.25rem` / `padding-left: 0.25rem` and `padding-inline-end: 0.25rem`) so icons never touch preceding borders, cards, or adjacent elements.
   - All `span` text containers must always have right padding (`padding-inline-end: 0.35rem` / `padding-right: 0.35rem`) alongside leading padding (`padding-inline-start: 0.25rem`) with `span:empty { padding: 0; }` so that text never crowds or collides with preceding or trailing borders, outlines, or adjacent badges.
5. **Button Outline / Border Buffer & Center Alignment:**
   - All `<button>` elements must maintain dedicated internal padding (`px-3.5 py-2.5` minimum) and `outline-offset: 2px` so their text, sublabels, and focus rings never overlap outlines or borders.
   - Channel preset and memory bank tiles must be center aligned (`text-center flex flex-col items-center justify-center`) with explicit center text alignment on both primary channel titles and secondary frequency readouts.

---

## 2. Modern CSS Layout & Responsive Design Tokens

1. **CSS Logical Properties:**
   - Prefer logical properties (`padding-inline`, `padding-block`, `margin-inline`, `block-size`, `inline-size`) over legacy physical directions (`padding-left`, `margin-top`) for natural bidirectional and responsive flow.
2. **Fluid Typography & Spacing via `clamp()`:**
   - Use fluid responsive sizing: `clamp(0.75rem, 1.5vw, 0.95rem)` for scalable ergonomics across high-DPI Windows desktop and the Samsung Galaxy S26 Ultra (6.9" QHD+ 120Hz display).
3. **Container Queries & Subgrids:**
   - When designing deck modules, utilize `@container` or CSS Grid `subgrid` to allow cards to automatically adapt to single-column, 2-column, or 4-column layouts without hardcoded window breakpoints.
4. **Descriptive, Compact Class Naming (Max 20 Characters):**
   - For recurring components, extract verbose utility strings into clean, descriptive semantic classes:
     - Examples: `.fm-station-card` (15 chars), `.tactical-badge` (14 chars), `.deck-header` (11 chars), `.vfo-readout` (11 chars).

---

## 3. Semantic HTML5 & Accessibility (WCAG 2.2 AA / AAA)

1. **Semantic Landmarks & ARIA Roles:**
   - Every major deck must be wrapped in a semantic tag: `<section aria-label="...">` or `<article aria-label="...">`.
   - Never use generic unadorned `<div>` elements for clickable buttons. Always use `<button type="button">` or `<button type="submit">`.
   - Modals and dialog overlays must use native `<dialog>` or `role="dialog"` with `aria-modal="true"` and an `aria-labelledby` reference.
2. **Focus Visibility & Keyboard Navigation:**
   - Never remove outline without providing a distinct `:focus-visible` ring (`focus-visible:ring-2 focus-visible:ring-cyan-400 focus-visible:outline-none`).
   - All interactive controls (buttons, dials, frequency step toggles, channel presets) must be fully navigable via `Tab` and `Shift+Tab`.
3. **Screen Reader Live Regions:**
   - Frequency readouts, emergency SAME weather alerts, and PTT state transitions must broadcast to assistive tech via `aria-live="polite"` or `role="status"`.

---

## 4. Hardware-Accelerated Rendering & 120Hz Canvas Hygiene

1. **GPU-Safe Animation Properties:**
   - Only animate `transform` and `opacity`.
   - Never animate layout properties (`width`, `height`, `top`, `padding`, `margin`) inside 60–120Hz render loops.
2. **Canvas Display & DPI Scaling:**
   - All `<canvas>` elements (Spectrum Analyzer, KiwiSDR Waterfall, Solar Greyline Map, Audio FFT) must specify `display: block` to prevent inline vertical baseline whitespace glitches.
   - Always multiply canvas internal buffer dimensions by `window.devicePixelRatio` while keeping CSS style width/height locked at 100% to ensure pin-sharp vector rendering on Retina/AMOLED screens.
3. **CSS Containment for High-Performance Lists:**
   - For long lists (ADIF QSO logbook, scanner channels, traffic dispatches), apply `contain: content;` or `content-visibility: auto;` with `contain-intrinsic-size` to prevent costly reflows when updating telemetry.
