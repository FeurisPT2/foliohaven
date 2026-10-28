# Handoff Report: R1 Landing Page Copy & Production Web Build Survey

**Agent**: `explorer_survey_1` (teamwork_preview_explorer)  
**Parent**: `orchestrator_1` (`a189f661-2b98-4c19-8531-5e6ac2b8aa28`)  
**Working Directory**: `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\explorer_survey_1`  
**Date**: October 28, 2026  
**Type**: Hard Handoff (Investigation & Survey Complete)

---

## 1. Observation

1. **Original User Request Scope**:
   * File: `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\ORIGINAL_REQUEST.md` (lines 12–14):
     > "### R1. Landing Page Copy & Production Web Build
     > Author `replica/launch/landing.md` adhering strictly to the 'Anti-Nag Free Reader' angle and FolioHaven brand voice (Serene, Capable, Respectful) across 7 mandatory sections: Hero, The Problem (without quotes), How It Works (3 steps), Features (tied to FIX-1 through FIX-6), Pricing, FAQ (addressing Calibre & Icecream migrations), and Final CTA. Build a responsive, standalone `app/landing.html` styled with `replica/design/tokens.css` and art-directed with the installed `design-taste-frontend` (`taste-skill`) to ensure distinctive typography, layout substance, and zero generic AI templates."

2. **Fixes & Positioning Angle**:
   * File: `replica/fixes.md` (lines 62–74, 79–83, 96–98):
     * Six product fixes: `FIX-1` (Zero Paywalls & Zero Nag Screens), `FIX-2` (One-Click Standalone Notes & Study Export), `FIX-3` (Native 64-bit High-Performance Architecture), `FIX-4` (True Windows 11 Dark Mode & Frameless DWM), `FIX-5` (Instant Drag-and-Drop Ingestion), `FIX-6` (Open Data Portability & Backup).
     * Positioning Option A: "The Anti-Nag Free Reader" ("For desktop book lovers who are fed up with intrusive Pro upgrade popups, countdown timers, and paywalled library limits... completely free, open-source, and forever unrestricted"). Cites 12 reviews across 4 sources from `feedback.md`.

3. **Brand Voice & Naming Assets**:
   * File: `replica/brand.md` (lines 161–176, 178–191, 194–208):
     * Three voice principles: Serene, Capable, Respectful.
     * Rewritten touchpoints eliminating tier shaming and nag dialogs.
     * Brand color tokens: Warm Terracotta `#c2410c`, Deep Amber Bronze `#9a3412`, Espresso Charcoal `#231f1d`, Deep Warm Wood `#2c2724`, Parchment White `#f5f0eb`.
   * Files: `app/logo.svg` and `app/favicon.svg` provide verified vector brand marks.

4. **Design Tokens & Application UI**:
   * File: `replica/design/tokens.css` (lines 7–38, 117–168):
     * CSS custom properties for Day, Night, Sepia, Dark Sepia reading themes.
     * Typography font stacks (`--font-sans`, `--font-serif`, `--font-mono`) and spacing scales.
   * File: `app/styles.css` (lines 6–35):
     * `@import url("../replica/design/tokens.css");` confirming active stylesheet link.

5. **Anti-Slop Art Direction (`design-taste-frontend`)**:
   * File: `C:\Users\epicg\.gemini\config\skills\design-taste-frontend\SKILL.md` (lines 384–406):
     * Strict house rules: Headlines $\le$ 2 lines at every width; no pill badges or eyebrows; no 01/02/03 step numbering; no thin 1px rules; no CSS gradients; no static shadows; no icon-topped cards; single `h1` on the first screen.
     * Section 4 requirement: "One live thing" (an interactive component proving the subject's utility).
   * Direction dealt by `draw.mjs`: `colour-chapters` (`.taste-skill/direction.json`).

6. **Rebrand Sweep Linter Rules**:
   * File: `replica/brand.json` (lines 3–19):
     * Banned names: `Icecream Ebook Reader`, `Icecream Apps`, `Icecream Reader`.
     * Banned domain: `icecreamapps.com`.
     * Banned hex colors: `#3498db`, `#2980b9`, `#1abc9c`, `#2ecc71`, `#2c3e50`, `#1f5fdb`, `#174bb0`.
   * Execution of `python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py . --config replica/brand.json`:
     * Found that `sweep.py` compiles regex `Icecream[\s_-]?Ebook[\s_-]?Reader`.
     * The existing `app/` folder is currently 100% clean (0 hits).
     * Any occurrence of the competitor name or the project root path substring `icecream_ebook_reader` in `app/landing.html` will trigger a sweep failure.

---

## 2. Logic Chain

1. **Copy Strategy Derivation**:
   * From Observation 1, `ORIGINAL_REQUEST.md` requires 7 mandatory sections for `replica/launch/landing.md` adhering strictly to "The Anti-Nag Free Reader" angle and FolioHaven voice.
   * From Observation 2, `fixes.md` proves that 50% of complaints attack popups, timers, and paywalls, giving the primary narrative anchor.
   * From Observation 1 & 5, social proof cannot be fabricated, and reviewer quotes cannot be presented as testimonials. Therefore, Section 2 ("The Problem") must articulate the industry grievances in plain editorial prose rather than fake review cards.
   * Connecting Observations 2 & 1, Section 4 ("Features") must map directly to FIX-1 through FIX-6, while Section 5 ("Pricing") establishes the contrast between the $0 Forever Free Core / Open-Sponsor model against the competitor's $19.95/yr or $39.95 lifetime model.

2. **Web Build Art Direction Derivation**:
   * From Observation 5, `design-taste-frontend` prohibits standard AI landing page tropes (icon grids, gradient blobs, pill badges).
   * From Observation 4 & 5, the `colour-chapters` direction naturally aligns with FolioHaven's 4 reading palettes (Day, Sepia, Night, Dark Sepia).
   * To satisfy the "One live thing" requirement (Observation 5), `app/landing.html` must include an interactive Reader Customizer component (`data-ui="live-reader"`) with live theme switching and typography scaling.

3. **Linter Compliance Derivation**:
   * From Observation 6, `app/landing.html` is scanned by `sweep.py`.
   * If `app/landing.html` contains the competitor's name or domain, `sweep.py` exits with code 1.
   * Therefore, `app/landing.html` must substitute competitor names with generic terms ("legacy desktop readers", "commercial reading apps") and use relative asset paths (`logo.svg`, `styles.css`) without mentioning the directory path.

---

## 3. Caveats

1. **Competitor Mentions in Markdown vs. HTML**:
   * In `replica/launch/landing.md`, the Original Request specifies "addressing Calibre & Icecream migrations" in the FAQ. Because `sweep.py` skips the `replica/` directory by default, referencing the target by name in `replica/launch/` does not break the automated sweep. However, in `app/landing.html`, which is scanned by `sweep.py`, the competitor name MUST NOT appear.
2. **Offline Web Viewer vs. C++ Desktop App**:
   * FolioHaven has a desktop target and a web target (`app/index.html`). The landing page must clearly present FolioHaven as a desktop application (Windows 10/11 64-bit) while offering the instant web reader demo.
3. **No External Fonts/Scripts**:
   * To maintain offline robustness and privacy integrity, `app/landing.html` should use system font stacks (`Segoe UI`, `Georgia`, `Charter`) already defined in `tokens.css` without external Google Fonts or CDN dependencies.

---

## 4. Conclusion

The survey and technical architecture for R1 are complete. The requirements, design assets, and constraints are fully mapped:
1. `replica/launch/landing.md` must be authored with the 7-section copy strategy detailed in `analysis.md` §2, leading with the Anti-Nag angle and FIX-1 to FIX-6 without fake social proof.
2. `app/landing.html` must be authored as a responsive, editorial web page following the `colour-chapters` blueprint in `analysis.md` §3, featuring the interactive Reader Theme Customizer, authentic UI fragments, strict token bindings, and zero sweep violations.

---

## 5. Verification Method

To verify the findings and subsequent implementations:

1. **Rebrand Sweep Verification**:
   ```bash
   python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py . --config replica/brand.json
   ```
   *Expected for `app/landing.html`*: 0 hits on any competitor name, domain, or hex color.

2. **Design Tokens & Contrast Verification**:
   ```bash
   python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-design\contrast.py replica/design/tokens.json
   ```
   *Expected*: 100% WCAG 2.2 AA/AAA compliance.

3. **Frontend Taste & Anti-Slop Audit**:
   ```bash
   node C:\Users\epicg\.gemini\config\plugins\taste-skill\skills\design-taste-frontend\scripts\lint.mjs app/landing.html
   ```
   *Expected*: Zero lint errors on banned tropes (no pill badges, no gradients, no headline overflow).
