# Survey & Architecture Analysis: R1 Landing Page Copy & Production Web Build

**Author**: Explorer Survey Agent (`teamwork_preview_explorer`)  
**Project**: FolioHaven (Clean-Room Ebook Reader Replica)  
**Date**: October 28, 2026  
**Target Deliverables Analyzed**:
1. `replica/launch/landing.md` (Markdown Copy Specification)
2. `app/landing.html` (Production Responsive Web Build)

---

## Executive Summary

This survey synthesizes all authoritative project requirements, brand identity standards, user grievance data, design tokens, and frontend taste guidelines necessary to build:
1. A conversion-focused, anti-nag landing page copy deck in `replica/launch/landing.md` adhering strictly to **"The Anti-Nag Free Reader"** angle and FolioHaven's **Serene, Capable, Respectful** brand voice across 7 mandatory sections without fake social proof.
2. A boutique, publication-grade responsive landing page in `app/landing.html` styled with `replica/design/tokens.css`, implementing the **`colour-chapters`** editorial direction from `design-taste-frontend` (`taste-skill`), including an interactive reading theme customizer ("The Live Thing"), zero AI landing page clichés, and complete immunity to `sweep.py` linter violations.

---

## 1. Requirement & Constraint Mapping Matrix

| Touchpoint | Source Document | Exact Requirement | Enforcement & Verification Rule |
| :--- | :--- | :--- | :--- |
| **Positioning Angle** | `replica/fixes.md` §3 | "The Anti-Nag Free Reader": Attacks the #1 complaint (50% of reviews: intrusive upsells, countdown timers, artificial paywalls). | Must lead with uninterrupted reading and zero paywalls; never use generic "all-in-one reader" messaging. |
| **Brand Voice** | `replica/brand.md` §5 | Three Principles: **Serene** (literary, calm), **Capable** (powerful yet unobtrusive), **Respectful** (treats reader as owner). | Prohibits marketing jargon, FOMO, countdown timers, fake quotes, and tier shaming. |
| **Section Count & Sequence** | `replica-launch/SKILL.md` §1 | Exactly 7 mandatory sections: Hero, The Problem, How It Works, Features, Pricing, FAQ, Final CTA. | Strict order; each section must state its claim and deliver substantive content. |
| **Social Proof Policy** | `replica-launch/SKILL.md` §2 | Zero fake testimonials, zero invented review stars, zero fake press logos. | The Problem section must paraphrase verified review themes from `feedback.md` without dressing reviewer quotes as testimonials. |
| **Design Tokens** | `replica/design/tokens.css` | Warm Terracotta accent (`#c2410c`, hover `#9a3412`), Espresso sidebar (`#231f1d`), Day/Night/Sepia/Dark Sepia themes. | All colors, spacing, typography, and borders in `app/landing.html` must bind to token custom properties. |
| **Editorial Anti-Slop** | `design-taste-frontend/SKILL.md` | Anti-slop house style: No pill badges, no 01/02 numbers, no icon cards, no 1px hairlines, no CSS gradients, no static shadows. | Verified by real-browser inspection (`inspect.mjs`), max 2 lines per headline, 120–240px section spacing. |
| **The Live Thing** | `design-taste-frontend/SKILL.md` §4 | A live, interactive widget demonstrating real product utility without page reload. | Interactive Reader Theme & Typography Customizer (Day / Sepia / Night / Dark Sepia toggles + font scaling). |
| **Rebrand Sweep Gate** | `replica/brand.json` & `sweep.py` | 0 occurrences of competitor names, domains, or banned hex codes outside `replica/`. | In `app/landing.html`, zero mentions of "Icecream", "Icecream Apps", "icecreamapps.com", or competitor hexes (`#3498db`, etc.). |

---

## 2. R1 Landing Page Copy Architecture (`replica/launch/landing.md`)

### 2.1 Positioning Angle: "The Anti-Nag Free Reader"
* **Target Audience**: Desktop readers, students, and book lovers on Windows and Web who are frustrated by commercial desktop readers that interrupt reading sessions with countdown nag screens, limit free libraries to 10 books, and lock basic annotation tools behind paywalls.
* **Core Value Proposition**: The tranquil, distraction-free digital bookshelf with visual shelf curation, dual-page layout, 4-color annotations, and instant study export—completely free, open-source, and forever unrestricted.
* **Competitive Wedge**: While commercial apps impose 10-second wait delays mid-chapter and Calibre feels like a 2004 database spreadsheet, FolioHaven provides an elegant, serene reading sanctuary.

### 2.2 Brand Voice Guidelines (FolioHaven)
From `replica/brand.md` §5:
1. **Serene, not sterile**: Warm, tranquil, literary. Quiet confidence; no cold tech jargon.
2. **Capable, not overwhelming**: Robust multi-format parsing (EPUB, PDF, MOBI, FB2, CBZ, TXT) and HTML notes export presented cleanly without visual noise.
3. **Respectful, not apologetic**: Treats reader autonomy as sacred. Local-first storage, zero telemetry, zero unprompted modals, zero paywalls.

#### Brand Voice Do's and Don'ts for Copy:
* **DO**: Speak like a thoughtful book curator and private library steward.
* **DON'T**: Speak like an aggressive SaaS funnel, adware distributor, or growth hacker.
* **DO**: Emphasize privacy, local file ownership, and calm focus.
* **DON'T**: Use artificial urgency ("Limited time offer!", "Upgrade before reading your next chapter!").
* **DO**: State format support and DRM boundaries plainly and honestly.
* **DON'T**: Make deceptive claims about breaking proprietary DRM.

### 2.3 Detailed Content Strategy for the 7 Mandatory Sections

#### Section 1: Hero
* **Purpose**: Establish immediate clarity on what FolioHaven is, whom it is for, and why it is different within 5 seconds.
* **Headline Rule**: Maximum 2 lines at any viewport width (~32 characters per line).
  * *Draft Headline*: **Your Distraction-Free Digital Bookshelf.**
  * *Alternative*: **Read in Peace. No Nag Popups. No Paywalls.**
* **Supporting Line**: A single, clear declarative sentence answering the visitor's first question:  
  * *"A modern desktop ebook reader for Windows and Web—open-source, 100% free, and crafted for pure reading focus without countdown timers or subscription paywalls."*
* **Primary Action**: A single high-contrast action button:
  * Primary Button: `Download for Windows (64-bit)`
  * Secondary Text Link: `Launch Web Reader Demo`
* **Visual Anchor**: An authentic interface showcase (`data-ui`) depicting FolioHaven's warm dual-column book spread with active cover shelf and reading typography.

#### Section 2: The Problem (Paraphrased Grievances Without Quotes)
* **Purpose**: Validate the reader's real frustrations by directly attacking the two primary pain themes identified in `feedback.md` (50% of complaints).
* **Compliance Constraint**: **No fake testimonials or reviewer quotes dressed up as user reviews.** All points must be paraphrased as systemic industry grievances.
* **Grievance 1: The Commercial Upsell Gauntlet (Popups & Countdown Timers)**
  * *Paraphrased Problem*: Modern commercial e-readers increasingly behave like aggressive adware. Opening a chapter triggers full-screen modal upgrade prompts, and some apps even force readers to stare at artificial 10-second countdown timers before allowing them to resume reading. What was once quiet personal time becomes an obstacle course of monetization.
* **Grievance 2: Artificial Paywalls on Core Reading Tools**
  * *Paraphrased Problem*: Basic digital reading utilities—importing more than 10 books, organizing titles into custom folders, highlighting text passages, or exporting study notes—are locked behind recurring licenses or deceptive "lifetime" fees that break after minor software updates.
* **Grievance 3: The Calibre Bloat Dilemma**
  * *Paraphrased Problem*: The open-source alternative (Calibre) provides format power, but its dense, complex interface feels like managing an industrial inventory spreadsheet rather than curling up with a good book.

#### Section 3: How It Works (The 3-Step Core Flow)
* **Step 1: Drop Your Books Onto Your Shelf**
  * Simply drag and drop your EPUB, PDF, MOBI, FB2, CBZ, or TXT files directly into FolioHaven. The engine parses covers and metadata automatically while cryptographic SHA-256 deduplication ensures zero duplicates in your library.
* **Step 2: Read in Uninterrupted Comfort**
  * Choose your environment: crisp Day paper, soft Sepia parchment, or deep Night mode. Enjoy fluid dual-column spreads, smooth zoom, margin click zones, and zero ads, trackers, or countdown delays.
* **Step 3: Annotate, Study, and Export Freely**
  * Highlight passages across four distinct editorial swatches, attach commentary in the notes drawer, and export comprehensive study reports to standalone HTML with a single click. Your library, annotations, and bookmarks remain entirely yours in an open local SQLite database.

#### Section 4: Features (Direct Mapping to FIX-1 through FIX-6)
Lead with the 6 strategic product fixes from `replica/fixes.md`, demonstrating how FolioHaven turns competitor flaws into core advantages:

| Fix ID | Feature Title | User-Facing Narrative | Technical Capability |
| :--- | :--- | :--- | :--- |
| **FIX-1** | **Zero Paywalls & Zero Nag Screens** | Read 10 books or 10,000. Create unlimited custom shelves, annotate every chapter, and never see a popup, banner, or countdown timer. | Unrestricted SQLite catalog; zero telemetry or upsell triggers compiled in codebase. |
| **FIX-2** | **One-Click Standalone Notes & Study Export** | Capture thoughts as you read. Highlight in 4 soft tones, record chapter notes, and export beautiful, self-contained HTML study guides to Notion, Obsidian, or print. | S05 Notes Drawer with instant DOM-to-HTML generation, preserving chapter timestamps and citations. |
| **FIX-3** | **Modern 64-Bit High-Performance Engine** | Flip pages instantly without lag. High-resolution PDF textbooks and graphic CBZ manga load smoothly with zero memory exhaustion or stutter. | 64-bit architecture replacing legacy 32-bit webkit runtimes with hardware-accelerated rendering. |
| **FIX-4** | **True Windows 11 Dark Mode & Frameless Chrome** | Read comfortably in low light. Features dark title bar integration, borderless DWM window framing, and 4 calibrated reading palettes: Day, Night, Sepia, and Dark Sepia. | Native `[data-theme="dark"]` tokens + QSS DWM frameless integration passing 100% WCAG 2.2 AA/AAA contrast. |
| **FIX-5** | **Instant Drag-and-Drop Library Ingestion** | Add single files, batches, or entire directories with a single gesture. FolioHaven indexes titles and authors immediately with instant hash deduplication. | SHA-256 fingerprinting on ingestion, preventing duplicate file storage. |
| **FIX-6** | **Open Data Portability & Local Privacy** | Your reading habits are your own business. FolioHaven operates 100% offline with zero cloud dependency. Your library, progress, and notes are stored in transparent SQLite/IndexedDB. | Open schema (`schema.sql`) with standard tables, allowing direct SQL export, backup, and sync via Syncthing/Dropbox. |

#### Section 5: Pricing Model (Synthesizing R2 Requirements)
* **Pricing Philosophy**: "Forever Free Core + Optional Open-Sponsor Edition" with zero recurring paywalls.
* **The Contrast**:
  * Legacy Commercial Reader: $19.95/year or $39.95 "lifetime" (frequently invalidated upon major version bumps).
  * ReadEra: $15.99 lifetime (mobile only; no dedicated Windows experience).
  * Freda: $2.49 (ad-supported free tier).
  * Calibre: $0 (free, but intimidating spreadsheet interface).
* **FolioHaven Tier Breakdown**:
  * **Core Reader ($0 Free Forever)**: 100% feature-complete. All formats, unlimited books, unlimited custom shelves, 4-color notes, HTML export, dark mode, offline reading. Zero ads, zero paywalls.
  * **Supporter / Open-Sponsor Edition (Optional $15 or $25 One-Time Contribution)**: For readers, students, and bibliophiles who wish to sustain ongoing open-source desktop development. Unlocks a patron badge in the About dialog, priority GitHub issue triage, and heartfelt gratitude. Zero locked reading features.

#### Section 6: FAQ (Technical Objections & Migration Paths)
1. **Can I migrate my existing library from Calibre or other readers?**  
   * *Answer*: Yes. Simply drag and drop your existing ebook collection folder into FolioHaven. Because FolioHaven uses non-destructive indexing and cryptographic hash deduplication, you can even point FolioHaven directly at your existing Calibre library folder without duplicating files or altering your folder structure.
2. **How does FolioHaven handle DRM-protected books?**  
   * *Answer*: FolioHaven is dedicated to open, privacy-first reading and supports DRM-free EPUB, PDF, MOBI, FB2, CBZ, and TXT files. It does not contain decryption keys for proprietary Adobe Adept or Amazon Kindle DRM systems. If a DRM-encrypted book is imported, FolioHaven displays a calm, respectful notice rather than crashing.
3. **Does FolioHaven require an internet connection or user account?**  
   * *Answer*: Never. FolioHaven is completely local-first. It requires no login, no email, and no cloud synchronization service. All library records, bookmarks, and study notes remain on your local machine.
4. **Is FolioHaven truly free, or will it add subscriptions later?**  
   * *Answer*: FolioHaven is licensed under open-source terms. The entire desktop application is free and will never incorporate paywalls, artificial book limits, or nag screens. Ongoing development is sustained purely through voluntary reader contributions and GitHub Sponsors.
5. **What platforms and operating systems are supported?**  
   * *Answer*: FolioHaven runs as a native 64-bit application on Windows 10 and Windows 11, and as a modern web application accessible in any standard modern desktop browser (Chrome, Edge, Firefox, Safari).

#### Section 7: Final Call to Action
* **Headline**: **Reclaim Your Quiet Reading Sanctuary.**
* **Subline**: *"Download FolioHaven today. No account needed, no credit card, no waiting timers—just your books, beautifully arranged."*
* **Primary Action**: `Download FolioHaven for Windows (64-bit)`
* **Secondary Action**: `Try the Web Reader Demo`
* **Trust Reassurance**: *100% Free & Open Source · No Ads · No Telemetry · Works Completely Offline*

---

## 3. R1 Production Web Build Architecture (`app/landing.html`)

### 3.1 Design Tokens & Asset Integration
The web build must strictly consume the design system established in `replica/design/tokens.css` and the vector assets in `app/`:

* **Color Tokens**:
  * `--color-bg: #ffffff;` (Day ground)
  * `--color-surface: #f5f7fa;` (Light warm surface)
  * `--color-text: #14181f;` (Deep legible ink)
  * `--color-text-muted: #525b6a;` (Secondary editorial notes)
  * `--color-accent: #c2410c;` (Warm Terracotta Brand Accent)
  * `--color-accent-hover: #9a3412;` (Deep Amber Bronze Hover)
  * `--color-sidebar-bg: #231f1d;` (Espresso Charcoal)
  * `--color-sidebar-surface: #2c2724;`
  * `--color-sidebar-text: #f5f0eb;` (Parchment White)
  * Reading Theme Palettes: Day (`#ffffff`), Night (`#181a1f`), Sepia (`#faf3e0` / text `#3d2e1e`), Dark Sepia (`#2b241e`).
* **Typography Tokens**:
  * Sans (Interface & Navigation): `--font-sans: "Segoe UI", -apple-system, BlinkMacSystemFont, "Inter", "Roboto", sans-serif;`
  * Serif (Editorial Headings & Book Reading Excerpts): `--font-serif: "Georgia", "Charter", "Source Serif Pro", serif;`
  * Type scale: Display (clamp 48px to 72px), Heading (32px to 44px), Subhead (20px to 24px), Body (16px to 18px, line-height 1.6).
* **Brand Assets**:
  * Logo: `app/logo.svg` (SVG terracotta book arch symbol + "FolioHaven Reader" wordmark).
  * Favicon: `app/favicon.svg` (32x32 terracotta rounded icon).

### 3.2 Art Direction via `design-taste-frontend` (`taste-skill`)

#### Selected Art Direction: `colour-chapters` (with FolioHaven Editorial Tokens)
The `draw.mjs` engine dealt `colour-chapters` for FolioHaven:
* **The Concept**: Every section is an immersive chapter with its own flat color tone from the reader's real world—alternating between paper white (`#ffffff`), warm reading parchment (`#faf3e0`), espresso charcoal (`#231f1d`), and warm terracotta accents.
* **The House Style Rules (Strictly Enforced)**:
  1. **Two-Line Headline Ceiling**: Every headline (`h1` through `h6`) must fit within two lines across desktop (1440px), tablet (768px), and phone (390px).
  2. **NO Pill Badges / Eyebrows**: Prohibit `"NEW"`, `"FEATURES"`, or tracked uppercase tags floating above headings. The heading states the topic directly.
  3. **NO 01 / 02 / 03 Index Numbering**: Sequence is communicated naturally via visual layout and clear phrasing.
  4. **NO Icon-Topped Cards**: Prohibit rows of 3 or 4 identical boxes with colored icons in tinted squares. Use varied, asymmetrical compositions (e.g., feature mosaic, live interactive preview, split comparisons).
  5. **NO Gradients or Static Drop Shadows**: Use crisp flat color fields and subtle surface tone steps (`#f5f7fa` on `#ffffff`, `#2c2724` on `#231f1d`). Shadows appear only on floating overlays/dialogs.
  6. **NO Thin Hairline Grids**: Section transitions are governed by generous vertical rhythm (120–240px gaps) and background shifts, never 1px gray border lines.
  7. **Single H1**: Exactly one clear `<h1>` on the first screen stating what the product is and does.
  8. **Equal Outer Margins**: Balanced 24–32px outer gutters; no content huddled awkwardly on one side with the opposite screen half abandoned.

### 3.3 "The Live Thing": Interactive Reader Experience Preview
Per `design-taste-frontend` §4, every winning site features a live, interactive element grounded in the product's actual function.
* **Component Specification**: **FolioHaven Live Reader Customizer** (marked with `data-ui="live-reader"`).
* **Location**: Integrated directly in the Hero/Showcase section.
* **Interactive Capabilities**:
  1. **Theme Switcher**: 4 clickable theme pills (Day, Sepia, Night, Dark Sepia) that dynamically re-theme the live preview canvas using FolioHaven CSS custom properties.
  2. **Type Scale Stepper**: `A-` and `A+` controls dynamically resizing the live reading passage between 14px, 16px, 18px, and 21px.
  3. **Editorial Highlight Swatches**: Clicking Yellow, Green, Cyan, or Pink highlights a selected passage in the classic excerpt (e.g., *Pride and Prejudice* or *The Time Machine*).
* **Technical Constraints**: 100% vanilla JavaScript, zero external dependencies, accessible via keyboard focus, fully functional on mobile touchscreens without layout shift.

### 3.4 Live Interface Fragments (`data-ui`)
In accordance with `references/imagery.md` §7, software products prove their capability through authentic interface fragments rather than generic illustrations or stock photos:
* **Fragment 1 (Library Shelf Preview)**: A clean visual shelf showcasing real classic book cards (e.g., *Jane Eyre*, *The Great Gatsby*, *Sherlock Holmes*), format tags (`EPUB`, `PDF`), and exact reading progress (`Page 84 of 200 · 42%`).
* **Fragment 2 (Notes & Study Drawer Preview)**: An authentic slide-out study notes card showing a yellow highlighted quote and attached user commentary with a functioning `Export HTML` button mockup.

### 3.5 Responsive Layout Structure

```
+-------------------------------------------------------------------------+
| NAVIGATION: Logo (FolioHaven) + Links (Features, Pricing, FAQ) + CTA    |
+-------------------------------------------------------------------------+
| CHAPTER 1: HERO & LIVE READER SHOWCASE                                   |
| [ Left Col: H1 (2 lines) + Value Lead + Download CTA + Web Demo Link ]  |
| [ Right Col: Live Reader Customizer (Theme pills, Type Stepper, Canvas)] |
+-------------------------------------------------------------------------+
| CHAPTER 2: THE PROBLEM (Parchment Tone Field: #faf3e0)                  |
| [ Split Grid: The Popups & Timers vs. The Paywalls & Bloat ]            |
+-------------------------------------------------------------------------+
| CHAPTER 3: HOW IT WORKS (Three Broad Stages: Ingest -> Read -> Study)   |
| [ Full-width horizontal sequence with visual stage duration & details ] |
+-------------------------------------------------------------------------+
| CHAPTER 4: FEATURES MOSAIC (FIX-1 through FIX-6)                        |
| [ Varied grid tiles: Zero Nags, Study Export, 64-Bit Speed, Dark Mode ] |
+-------------------------------------------------------------------------+
| CHAPTER 5: PRICING COMPARISON TABLE (Charcoal Ground: #231f1d)          |
| [ Clear $0 Free Core vs. Optional Sponsor + Competitor Contrast Table ] |
+-------------------------------------------------------------------------+
| CHAPTER 6: ACCORDION FAQ (Clean Details/Summary Stack)                   |
| [ Sticky Section Title (Col 1-4) + 6 Interactive Filled Tiles (Col 5-12)]|
+-------------------------------------------------------------------------+
| CHAPTER 7: FINAL CTA & LITERARY FOOTER                                  |
| [ Statement Close + Download Button + Wordmark + Privacy & Open Credits]|
+-------------------------------------------------------------------------+
```

---

## 4. Rebrand Sweep & Anti-Trademark Safeguards

### 4.1 Root Cause Analysis of `sweep.py`
Execution of:
```bash
python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py . --config replica/brand.json
```
reveals the exact string matching rules enforced by the sweep tool:
1. **Avoided Names**:
   * `"Icecream Ebook Reader"`
   * `"Icecream Apps"`
   * `"Icecream Reader"`
   *(Note: The sweep tool splits names on whitespace/hyphens/underscores and compiles case-insensitive regular expressions: `Icecream[\s_-]?Ebook[\s_-]?Reader`).*
2. **Avoided Domains**:
   * `"icecreamapps.com"`
3. **Avoided Competitor Hex Colors**:
   * `#3498db`, `#2980b9`, `#1abc9c`, `#2ecc71`, `#2c3e50`, `#1f5fdb`, `#174bb0`
4. **Scope of Sweep**:
   * `sweep.py` skips the `replica/` directory if `--include-replica` is not passed.
   * **Crucially, `sweep.py` checks all files in `app/` and the project root!**
   * Even the directory path `icecream_ebook_reader_replica` contains the substring `icecream_ebook_reader`, which matches the regex for `"Icecream Ebook Reader"`!

### 4.2 Mandatory Code Rules for `app/landing.html`
To guarantee **0 hits (exit code 0)** on `sweep.py`:
1. **NEVER** write `"Icecream"`, `"Icecream Apps"`, `"Icecream Reader"`, or `"icecreamapps.com"` in `app/landing.html`—including in comments, metadata, data attributes, or alt text.
2. **NEVER** embed absolute Windows file paths containing `icecream_ebook_reader_replica` in `app/landing.html`. Use relative paths exclusively (e.g. `href="styles.css"`, `src="logo.svg"`).
3. **NEVER** use any of the 7 competitor hex colors. Use FolioHaven's warm editorial palette tokens (`#c2410c`, `#9a3412`, `#231f1d`, `#2c2724`, `#14181f`, `#faf3e0`).
4. **Vocabulary Substitution Table**:
   * Instead of competitor name $\to$ Use: *"legacy desktop readers"*, *"commercial reading apps"*, or *"traditional closed-source e-readers"*.
   * Instead of competitor migration $\to$ Use: *"Migrating from proprietary reader libraries"*.
   * Calibre is allowed in copy, as it is open-source and not in the `avoid` list, but must be discussed respectfully.

---

## 5. Implementation Roadmap & Quality Checklist

For the downstream authoring and frontend implementation agents:

### Checklist for `replica/launch/landing.md`:
- [ ] Incorporates all 7 sections in exact specified order.
- [ ] Hero headline strictly $\le$ 2 lines.
- [ ] No fake testimonials, fabricated user counts, or reviewer quotes used as testimonials.
- [ ] Problem section paraphrases the 3 core pain points (popups/timers, paywalled shelves/notes, bloat).
- [ ] Features section directly addresses FIX-1 through FIX-6 with clear technical benefits.
- [ ] Pricing section details the Forever Free Core ($0) and Open-Sponsor tier, citing competitor prices ($19.95/yr, $39.95 lifetime).
- [ ] FAQ covers Calibre migration, library import, DRM boundaries, offline privacy, and file formats.
- [ ] Final CTA provides clear closing with download and web reader links.

### Checklist for `app/landing.html`:
- [ ] Fully responsive standalone HTML5 document linked to `tokens.css` or with self-contained token variables matching `replica/design/tokens.css`.
- [ ] Semantic HTML (`header`, `main`, `section`, `article`, `details`, `summary`, `footer`).
- [ ] All headlines $\le$ 2 lines at 1440px, 768px, and 390px viewports.
- [ ] Zero pill badges, zero index numbers (01/02), zero icon cards, zero CSS gradients, zero static shadows.
- [ ] Includes "The Live Thing" interactive reader preview (`data-ui="live-reader"`) with functioning theme toggles and type scale stepper.
- [ ] Includes authentic UI fragments showing book covers, reading progress, and notes export.
- [ ] Passes `sweep.py` with 0 hits (no competitor names, domains, or hex colors).
- [ ] 100% WCAG 2.2 AA / AAA contrast compliant.
