---
name: FolioHaven
description: Distraction-free digital bookshelf and serene ebook reader design system
colors:
  primary: "#c2410c"
  primary-hover: "#9a3412"
  primary-on: "#ffffff"
  neutral-bg: "#ffffff"
  neutral-surface: "#f5f7fa"
  neutral-surface-hover: "#ebf0f5"
  neutral-surface-active: "#e0e6ed"
  neutral-border: "#dbe0e8"
  neutral-text: "#14181f"
  neutral-text-muted: "#525b6a"
  sidebar-bg: "#231f1d"
  sidebar-surface: "#2c2724"
  sidebar-text: "#f5f0eb"
  sidebar-text-muted: "#a89f97"
  sidebar-border: "#756b62"
  reader-day-bg: "#ffffff"
  reader-day-text: "#1a1d20"
  reader-sepia-bg: "#faf3e0"
  reader-sepia-text: "#3d2e1e"
  reader-night-bg: "#181a1f"
  reader-night-text: "#e2e4e8"
  reader-dark-sepia-bg: "#2b241e"
  reader-dark-sepia-text: "#ddd1be"
  highlight-amber: "#ffe270"
  highlight-emerald: "#a8f29a"
  highlight-azure: "#7be5f8"
  highlight-rose: "#ffa0c5"
typography:
  display:
    fontFamily: '"Crimson Pro", "Georgia", serif'
    fontSize: "2.25rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  headline:
    fontFamily: '"Plus Jakarta Sans", "Segoe UI", sans-serif'
    fontSize: "1.375rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  title:
    fontFamily: '"Plus Jakarta Sans", "Segoe UI", sans-serif'
    fontSize: "1.125rem"
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: '"Georgia", "Charter", serif'
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.7
  body-ui:
    fontFamily: '"Plus Jakarta Sans", "Segoe UI", sans-serif'
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: '"Plus Jakarta Sans", "Segoe UI", sans-serif'
    fontSize: "0.75rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.02em"
rounded:
  xs: "3px"
  sm: "5px"
  md: "8px"
  lg: "12px"
  pill: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.primary-on}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.primary-on}"
    rounded: "{rounded.md}"
  button-secondary:
    backgroundColor: "{colors.neutral-surface}"
    textColor: "{colors.neutral-text}"
    rounded: "{rounded.md}"
    padding: "8px 16px"
  card:
    backgroundColor: "{colors.neutral-bg}"
    rounded: "{rounded.md}"
    padding: "16px"
  sidebar-item:
    backgroundColor: "transparent"
    textColor: "{colors.sidebar-text}"
    rounded: "{rounded.sm}"
    padding: "8px 12px"
---

## Overview

FolioHaven's visual identity embodies the quiet dignity and focus of an archival private library. Built on clean-room, anti-slop principles, it rejects noisy AI-generated aesthetics—such as purple gradients, gratuitous glow halos, and generic emoji badges—in favor of warm terracotta tones (`#c2410c`), deep espresso wood navigation (`#231f1d`), and museum-grade public domain art accents.

The system is architected across two distinct operational environments:
1. **The Bookshelf (Library View)**: High-scanability, dense information display with Cover Grid, Detailed Shelf, and Sortable Table representations.
2. **The Sanctuary (Reading Canvas)**: Typography-led, distraction-free reading canvas optimized for prolonged study across 4 rigorously tested WCAG AAA color themes.

---

## Colors

Color in FolioHaven serves semantic clarity and eye comfort rather than ornamental spectacle.

### Primary Accents & Brand
- **Terracotta Core (`#c2410c`)**: Primary call to action, active navigation indicator, and brand accent.
- **Deep Sienna (`#9a3412`)**: Hover and active interaction states.
- **Pure White (`#ffffff`)**: High-contrast text on accent surfaces.

### Neutral System Surfaces
- **Light Workspace**: Background (`#ffffff`), Surface (`#f5f7fa`), Surface Hover (`#ebf0f5`), Borders (`#dbe0e8`).
- **Sidebar & Chrome**: Deep Espresso (`#231f1d`), Elevated Surface (`#2c2724`), Muted Text (`#a89f97`).

### Calibrated Reading Themes
1. **Day (Archival White)**: Background `#ffffff`, Text `#1a1d20` (Contrast 16.8:1, WCAG AAA).
2. **Sepia (Warm Parchment)**: Background `#faf3e0`, Text `#3d2e1e` (Contrast 11.4:1, WCAG AAA). Soothing warm tone for evening study.
3. **Night (Deep Slate)**: Background `#181a1f`, Text `#e2e4e8` (Contrast 12.1:1, WCAG AAA). OLED-friendly, reduced blue light.
4. **Dark Sepia (Roasted Walnut)**: Background `#2b241e`, Text `#ddd1be` (Contrast 9.8:1, WCAG AAA). Low-glare twilight reading.

### Annotation Swatches
- **Amber (`#ffe270`)**: Primary conceptual highlights.
- **Emerald (`#a8f29a`)**: Citations, definitions, and facts.
- **Azure (`#7be5f8`)**: Questions, references, and external notes.
- **Rose (`#ffa0c5`)**: Critical passages, counter-arguments, and key takeaways.

---

## Typography

FolioHaven pairs an authentic, classical serif for reading literature with a clean, high-legibility geometric sans-serif for library controls and data tables.

### Font Stacks
- **Literature & Editorial Prose**: `"Georgia", "Crimson Pro", "Source Serif Pro", serif` — optimal line height 1.7, column width constrained to 65–75 characters per line (`ch`).
- **Application Controls & UI**: `"Plus Jakarta Sans", "Segoe UI", system-ui, sans-serif` — clear letterforms with distinct open counters and optical kerning.
- **Numerals & Metrics**: Formatted with `font-variant-numeric: tabular-nums` to guarantee aligned columns across library tables and reading page numbers.

### Typographic Hierarchy
- **Display (`2.25rem / 36px`, Bold)**: Page headers and hero titles.
- **Headline (`1.375rem / 22px`, Bold)**: Chapter headings and modal dialog titles.
- **Title (`1.125rem / 18px`, Semibold)**: Book card titles, shelf section names.
- **Body Literature (`1.0rem / 16px`, Regular, line-height 1.7)**: Main reading text.
- **Body UI (`0.875rem / 14px`, Regular, line-height 1.5)**: General controls, metadata rows.
- **Label & Badges (`0.75rem / 12px`, Semibold)**: Format badges (EPUB, PDF, MOBI, TXT), progress counters.

---

## Layout

### Bookshelf Architecture
- **Desktop Sidebar**: Fixed `220px` width on desktop, collapsable on compact viewports. Contains navigation links and shelf tree.
- **Content Grid**: Fluid grid adjusting from 2 columns on mobile to 6 columns on wide monitors. Card size: `160px × 240px`.
- **Top Action Bar**: Height `56px` housing search input, view switcher, and import action.

### Reader Canvas Geometry
- **Single Page View**: Centered measure of max `800px` (`~70ch`) with generous horizontal padding (min `40px`).
- **Two-Page Spread**: Dual symmetrical panes (`min-width: 480px` each) separated by a subtle `30px` gutter, replicating open hardcover books.
- **Bottom Status Bar**: Height `48px` containing precision scrubbing slider, page indicator, and chapter navigation.

---

## Elevation & Depth

FolioHaven relies on **tonal layering and hairline boundaries** rather than heavy blurred drop shadows:
- **Level 0 (Base Canvas)**: Flat surface `#ffffff` (or active theme background).
- **Level 1 (Cards & Shelves)**: Tonal separation via `#f5f7fa` with a crisp `1px solid #dbe0e8` border. No drop shadow in default state.
- **Level 1 Hover**: Subtle elevation step using `box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05)` with `transform: translateY(-2px)`.
- **Level 2 (Drawers & Modals)**: Side drawers and dialogs use `box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12)` with a semi-transparent backdrop overlay (`rgba(0, 0, 0, 0.4)`).

---

## Shapes

- **Base Radius (`rounded.md: 8px`)**: Applied to book cards, input fields, buttons, and dialog boxes.
- **Compact Radius (`rounded.sm: 5px`)**: Applied to format badges, dropdown menus, and list items.
- **Pill Radius (`rounded.pill: 9999px`)**: Reserved strictly for circular icon buttons (TTS play/pause, pagination arrows).

---

## Components

### 1. Primary Action Button (`button-primary`)
- Height: `40px`
- Background: `{colors.primary}` (`#c2410c`)
- Typography: Semibold, `14px`, White
- Radius: `{rounded.md}`
- Focus Ring: `0 0 0 2px #ffffff, 0 0 0 4px #c2410c`

### 2. Book Cover Card
- Aspect ratio: `2:3` (`160px × 240px`)
- Card Frame: `1px solid #dbe0e8`, rounded `8px`
- Format Pill: Upper-left pinned badge (`#ffedd5` background, `#c2410c` text)
- Reading Progress: Bottom anchored `4px` indicator bar

### 3. Study Notes & Annotation Card
- Uniform border: `1px solid rgba(194, 65, 12, 0.25)` on all 4 sides (no asymmetric side-tab borders)
- Background: Light warm tint (`#faf7f4`)
- Padding: `16px 20px`
- Border Radius: `{rounded.md}`

---

## Do's and Don'ts

### Do:
- ✅ **Do** use hand-crafted SVG vector icons with consistent 2px stroke width.
- ✅ **Do** ensure all literature text remains in the 65–75 character measure for reading comfort.
- ✅ **Do** support all 4 calibrated reading palettes across every format (EPUB, PDF, MOBI, TXT).
- ✅ **Do** test keyboard accessibility (<kbd>Esc</kbd>, <kbd>F</kbd>, <kbd>→</kbd>, <kbd>←</kbd>).
- ✅ **Do** maintain tabular numerals (`tabular-nums`) for aligned statistics and page counts.

### Don't:
- ❌ **Don't** use emojis as interface icons or navigation controls.
- ❌ **Don't** use colored 3px–4px side-tab borders (`border-left: 4px solid ...`) on cards or callouts.
- ❌ **Don't** use gradient text or colored glow halos around text.
- ❌ **Don't** place thick accent borders on rounded elements (`border-top: 4px` on rounded card).
- ❌ **Don't** ship naked `<img>` tags without `src` and descriptive `alt` text.
