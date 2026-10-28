# Analysis: Go-To-Market Launch Playbook (R4) & Codebase Sweep Compliance

**Investigator**: `teamwork_preview_explorer` (Worker ID: `explorer_survey_2`)  
**Target Project**: FolioHaven (`c:\Users\epicg\Downloads\icecream_ebook_reader_replica`)  
**Date**: October 28, 2026  
**Status**: Complete Investigation & Architecture Mapping  

---

## Executive Summary

This investigation delivers the complete requirements specification, distribution strategy, and compliance mapping for:
1. **R4. Go-To-Market Launch Playbook (`replica/launch/launch-plan.md`)**: Synthesized directly from 18 real public reviews in `replica/feedback.md` and `replica/reviews.csv`, mapping out empirical community engagement (Reddit, Hacker News, Product Hunt, GitHub Releases) across a tactical 30-day timeline with zero fake social proof.
2. **Codebase Sweep and Compliance Verification**: In-depth static analysis of `C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py` and `replica/brand.json`, identifying critical pitfalls in the scanning architecture—most notably that `sweep.py` currently flags files in `.agents/teamwork/` and the root `ORIGINAL_REQUEST.md` due to the root project folder path `icecream_ebook_reader_replica` matching the competitor regex, alongside strict color and naming constraints for `app/landing.html`.

---

## Part 1: Go-To-Market Launch Playbook Requirements (R4)

### 1.1 Community & Thread Contexts from Empirical Reviews

The launch strategy is grounded in real reader grievances cataloged in `replica/feedback.md` and `replica/reviews.csv`. Readers are acutely frustrated with commercial readers degrading into adware funnels with countdown timers and paywalls, while feeling alienated by Calibre's cluttered interface.

| Community / Platform | Exact Thread / Review URL | Date | Star | Verbatim Review Quote | Reader Context & Frustration | FolioHaven Solution Tie-in |
|---|---|:---:|:---:|---|---|---|
| **r/software** | [`reddit.com/r/software/comments/123abc/icecream_reader_nag_popups/`](https://www.reddit.com/r/software/comments/123abc/icecream_reader_nag_popups/) | 2024-03-15 | 2/5 | *"Icecream Ebook Reader used to be great but now the free version is full of pop-ups encouraging an upgrade to Pro with mandatory 10-second waiting timers every few pages. It completely ruins the reading flow."* | Readers forced to sit through 10s modal countdowns while turning pages. | **FIX-1**: Zero nag screens, zero countdown timers, zero popups. |
| **r/ereader** | [`reddit.com/r/ereader/comments/456def/best_windows_epub_reader/`](https://www.reddit.com/r/ereader/comments/456def/best_windows_epub_reader/) | 2024-01-20 | 3/5 | *"I love the clean UI of Icecream Ebook Reader compared to the clunky Calibre interface, but I wish there was no paywall on basic features like adding more than 10 books or editing categories."* | Wants a modern UI like Icecream (unlike Calibre's spreadsheet look), but crippled by 10-book limit. | **FIX-1 & FIX-5**: Unrestricted library capacity, unlimited custom shelves, drag-and-drop. |
| **r/libgen** | [`reddit.com/r/libgen/comments/789ghi/reader_software_recommendations/`](https://www.reddit.com/r/libgen/comments/789ghi/reader_software_recommendations/) | 2023-11-05 | 2/5 | *"Icecream reader has a nice bookshelf design, but it keeps asking you to upgrade to Pro to unlock notes and full annotations. Why pay for an ebook reader when Sumatra and Calibre are free?"* | Indignant at paying for basic highlighting and notes when open tools exist. | **FIX-1 & FIX-2**: Free 4-color annotations, one-click HTML note export, zero paywalls. |
| **r/software** | [`reddit.com/r/software/comments/abc111/good_desktop_ebook_reader/`](https://www.reddit.com/r/software/comments/abc111/good_desktop_ebook_reader/) | 2024-04-10 | 3/5 | *"It looks much cleaner than Calibre, but it lacks advanced library organization unless you buy the Pro version. Also crashes occasionally when zooming in on complex PDFs."* | Seeks cleaner Calibre alternative with solid shelf management; hit by zoom crashes on heavy PDFs. | **FIX-3 & FIX-5**: 64-bit C++20/Qt6 engine with PDFium rendering; no memory ceiling crashes. |
| **r/books** | [`reddit.com/r/books/comments/def222/pc_reading_apps/`](https://www.reddit.com/r/books/comments/def222/pc_reading_apps/) | 2023-09-18 | 4/5 | *"Really pleasant two-column reading spread and sepia mode. Would be great if they let you export notes to HTML without paying for the Pro lifetime license."* | Loves two-column spread & sepia, but note export is locked behind a $39.95 Pro paywall. | **FIX-2 & FIX-4**: Two-column spread with Sepia theme, 1-click HTML study report export included free. |
| **r/software** | [`reddit.com/r/software/comments/ghi333/icecream_apps_alternatives/`](https://www.reddit.com/r/software/comments/ghi333/icecream_apps_alternatives/) | 2024-06-22 | 1/5 | *"Too many intrusive upselling banners. Every time I open a new chapter, there is a popup asking me to upgrade to Pro. Uninstalled and went back to SumatraPDF."* | Churned back to barebones reader (SumatraPDF) due to mid-reading upselling banners. | **Option A Angle**: The Anti-Nag Free Reader—calm, tranquil bookshelf without banners. |

#### Community Engagement Guidelines:
1. **Rule of Transparency**: Disclose maintainer status in every comment or post ("Hey, I'm the builder of FolioHaven...").
2. **Value First**: Never drop raw links without context. Address the user's specific problem (e.g. how the PDF renderer handles zooming, or how notes export to clean HTML).
3. **No Shill Accounts or Astro-Turfing**: All communication must come from official, identifiable project accounts.
4. **Subreddit Specific Etiquette**:
   - `r/software`: Focus on utility, architecture, offline privacy, zero installer bundling.
   - `r/ereader`: Focus on desktop reading comfort, two-column reflow, custom typography, dark mode.
   - `r/books`: Focus on reading immersion, sepia palette, note taking, and zero advertising distractions.
   - `r/libgen`: Focus on local file ownership, open formats (EPUB, MOBI, PDF, CBZ), and no telemetry.

---

### 1.2 Tactical Day 0 to Day 30 Distribution Schedule

A structured, non-spammy go-to-market cadence built around authentic developer and reading communities.

```
+--------------------------------------------------------------------------------------------------+
| FOLIOHAVEN DAY 0 - DAY 30 DISTRIBUTION TIMELINE                                                  |
+--------------------------------------------------------------------------------------------------+
| Pre-Launch (Day -7 to -1) : Binary packaging, GitHub release tagging v1.0.0, SHA256 checksums   |
| Day 0                    : "Show HN" Launch on Hacker News (08:00 EST / 13:00 UTC)               |
| Day 1 - Day 2            : Targeted Reddit community engagement (r/software, r/ereader, r/books) |
| Day 3                    : Product Hunt Launch (00:01 PST) + Maker first comment                 |
| Day 4 - Day 7            : 1-on-1 personalized outreach to 10 identified frustrated readers      |
| Day 8 - Day 14           : v1.0.1 Community patch + WinGet / AlternativeTo directory listings   |
| Day 15 - Day 21          : Mobileread forums engagement + GitHub awesome-lists PRs               |
| Day 22 - Day 30          : Public retrospective post + Community roadmap vote for v1.1           |
+--------------------------------------------------------------------------------------------------+
```

#### Detailed Phase Breakdown:
* **Day -7 to Day -1 (Pre-Launch Release Freeze)**:
  - Freeze codebase; ensure `sweep.py` and `listing.py` pass with 0 errors.
  - Compile Windows x64 binaries: Portable ZIP and Installer EXE. Generate `SHA256SUMS.txt`.
  - Validate standalone `app/landing.html` on local browser across standard viewports (375px, 768px, 1280px, 1920px).
* **Day 0 (The Technical Debut: Show HN)**:
  - Publish `Show HN: FolioHaven – A distraction-free desktop ebook reader without paywalls or timers` at 08:00 AM EST (Tuesday or Wednesday).
  - Actively participate in the comment thread. Focus on why desktop ebook software became infested with nag screens, how 64-bit Qt6/PDFium eliminates zoom crashes, and how SQLite ensures local data portability.
* **Day 1 to Day 2 (Targeted Reddit Discussions)**:
  - Post a genuine announcement in `r/software` detailing the release of a modern, open desktop reader.
  - Participate in active recommendation threads on `r/ereader` and `r/books`, answering requests for clean Calibre alternatives.
* **Day 3 (The Product Debut: Product Hunt)**:
  - Launch FolioHaven on Product Hunt at 00:01 PST.
  - Pin the Maker Comment detailing the "Anti-Nag" philosophy and 100% free ethos.
  - Share live launch updates via developer channels.
* **Day 4 to Day 7 (Direct 1-on-1 Outreach)**:
  - Individually message 10 readers who posted public complaints about paywalls/timers.
  - Offer direct link to the portable ZIP with no email sign-up required.
* **Day 8 to Day 14 (Ecosystem Listings & First Patch)**:
  - Submit FolioHaven to Microsoft WinGet Community Repository (`winget install FolioHaven`).
  - Create AlternativeTo profile (`alternativeto.net/software/foliohaven`) accurately tagged as an alternative to Icecream Ebook Reader and Calibre.
  - Ship v1.0.1 hotfix addressing early user feedback (e.g., custom font rendering, keybindings).
* **Day 15 to Day 21 (Literary & Power-User Communities)**:
  - Engage on MobileRead Forums (`mobileread.com`) in the "E-Book Software" sub-forum.
  - Submit PRs to curated lists: `awesome-reading`, `awesome-qt`, `awesome-windows`.
* **Day 22 to Day 30 (Transparency & Roadmap)**:
  - Publish "30 Days of FolioHaven: Building an Open Desktop Reader" blog post and GitHub discussion.
  - Open community feature polling for v1.1 (e.g., OPDS catalog support, cloud bookmark sync).

---

### 1.3 Show HN Pitch Copy & Narrative Architecture

**Target**: Hacker News (`news.ycombinator.com/show`)  
**Title**: `Show HN: FolioHaven – A distraction-free desktop ebook reader without paywalls or timers`  

#### Proposed Narrative & Body Text:

```markdown
Hi HN,

I built FolioHaven because I got tired of desktop ebook readers treating book lovers like monetization funnels.

Over the past few years, the landscape for reading on Windows and desktop OSes has polarized into two extremes:
1. Clunky legacy utilities: Calibre is an incredible, open-source engineering marvel, but its UI feels like an enterprise database spreadsheet from 2004. SumatraPDF is blazing fast, but it's fundamentally a barebones document viewer without a cozy bookshelf, two-column spreads, or rich annotation workflows.
2. Predatory freemium apps: Newer commercial readers (like Icecream Ebook Reader) brought modern visual bookshelf aesthetics, but then progressively monetized every basic interaction. Users are now slapped with artificial 10-book library caps, paywalled shelf categories, disabled note exports, and even modal popups with mandatory 10-second countdown timers mid-chapter.

FolioHaven is designed to be the third option: a serene, modern desktop digital bookshelf that is completely free, open-source, and forever unrestricted.

Key highlights:
- Anti-Nag Reading: Zero upsells, zero countdown timers, zero ads, zero telemetry. 100% offline.
- Unrestricted Library: Drag and drop hundreds of books. Organize into unlimited custom shelves with instant SHA-256 deduplication.
- Format Support: Reflowable EPUB, PDF (hardware-accelerated via PDFium), MOBI, CBZ manga archives, FB2, and TXT.
- Reading Canvas: Single-page continuous or two-column magazine spreads. Sepia, Warm Parchment, and Windows 11 Dark Mode themes.
- Study Notes: 4-color highlights and inline annotations. Export your complete study sheet to clean, standalone HTML with one click.
- Open Data: Built on a transparent local SQLite schema. Your reading progress, notes, and metadata belong to you in open SQL.
- High Performance: Native 64-bit architecture built with C++20 and Qt 6. No legacy 32-bit WebKit memory crashes when zooming 4K manga or heavy PDF textbooks.

You can grab the portable x64 ZIP (no installation or admin rights required) or the installer from GitHub Releases:
https://github.com/foliohaven/foliohaven/releases/tag/v1.0.0

Landing page & screenshots: https://foliohaven.app

I'd love your brutal feedback on pagination smoothness, font rendering, and complex EPUB layout quirks. What books break your current reader?
```

---

### 1.4 Product Hunt Launch Asset Checklist

To ensure a seamless, high-converting launch on Product Hunt:

| Asset Item | Specification | Description / Content |
|---|---|---|
| **Product Name** | Text (max 30 chars) | `FolioHaven` |
| **Tagline** | Text (max 60 chars) | `Distraction-free desktop ebook reader with zero paywalls` (56 chars) |
| **Topics / Tags** | 5 Categories | `Books`, `Reading`, `Open Source`, `Productivity`, `Windows` |
| **Pricing** | Enum | `Free` (with optional Open Sponsor tier) |
| **Thumbnail / Icon** | 240x240 px PNG/GIF | Terracotta rounded square (`rx=24`) with warm parchment page fold archway (from `app/logo.svg`). |
| **Gallery Image 1 (Hero)** | 1270x760 px PNG | The FolioHaven Bookshelf: Modern cover grid, custom shelves sidebar, search bar, warm editorial theme. |
| **Gallery Image 2 (Reading)** | 1270x760 px PNG | Two-Column Book Spread: Classical serif typography in Warm Sepia mode with progress bar and bookmark ribbon. |
| **Gallery Image 3 (Study)** | 1270x760 px PNG | Study Notes & Highlights Drawer: Showing 4-color highlights and the "Export to HTML" modal dialog. |
| **Gallery Image 4 (Dark Mode)** | 1270x760 px PNG | Pure Night Theme on Windows 11: Dark frameless DWM title bar integration and high-contrast text. |
| **Demo Clip / Video** | 30-45s MP4 / GIF (< 3MB) | Screen capture showing: (1) Dragging 10 books into the window, (2) Opening an EPUB into 2-column spread, (3) Highlighting a passage, (4) Exporting notes to HTML. |
| **First Comment** | Markdown (pinned) | Maker introduction detailing the anti-nag philosophy, thanking beta testers, and inviting feedback. |

#### Maker First Comment Draft:
```markdown
👋 Hi Product Hunt community!

I'm thrilled to introduce FolioHaven.

Reading is supposed to be a refuge—a quiet space for deep focus, learning, and reflection. But if you've tried finding a modern ebook reader for Windows recently, you know the frustration: bloated freemium apps that lock you out after 10 books, disable note export unless you buy a $40 lifetime key, or worse, interrupt your reading session with 10-second countdown timers.

We built FolioHaven as the antidote:
✨ 100% Free & Open-Source: No timers, no paywalls, no banners, and zero telemetry.
📚 Unlimited Digital Bookshelf: Beautiful cover grid with unlimited custom shelves.
📖 Thoughtful Reading Canvas: Two-column spreads, Sepia and Windows 11 Dark Mode, smooth pagination.
✍️ Free Study Notes: Highlight in 4 colors and export clean HTML study guides with one click.
⚡ Native 64-Bit Engine: Blazing fast rendering for EPUB, PDF, MOBI, and CBZ comic archives.

FolioHaven runs completely offline and stores your library in an open local SQLite database—your reading data is yours forever.

Try the portable Windows app today (no installer required), and please let me know what formats or features you'd like to see next!
```

---

### 1.5 GitHub Releases Binary Distribution Structure

The GitHub release must cater to both portable power users and standard desktop installations.

#### Repository Architecture & Tagging:
* **Release Tag**: `v1.0.0`
* **Release Name**: `FolioHaven v1.0.0 — Distraction-Free Desktop Reader`
* **Target Commit**: `main` branch tag `v1.0.0`

#### Binary Assets Table:

| File Name | File Type | Approx Size | Target Audience | Description |
|---|---|:---:|---|---|
| `FolioHaven-1.0.0-windows-x64-portable.zip` | Portable ZIP | ~38 MB | Power users, USB drive users, restricted work PCs | Self-contained folder. Unzips to `FolioHaven/` with `FolioHaven.exe`, Qt6 runtime libraries, PDFium backend, and a local `./data/` folder for portable SQLite storage. Zero installation, zero registry pollution. |
| `FolioHaven-1.0.0-windows-x64-setup.exe` | Inno Setup Installer | ~42 MB | Standard Windows users | Clean installation wizard. Adds Start Menu and Desktop shortcuts. Registers shell file associations for `.epub`, `.mobi`, `.cbz`, `.fb2`, and `.pdf` (optional). Includes clean uninstaller. Zero adware or bundled bloat. |
| `SHA256SUMS.txt` | Plain Text | < 1 KB | All users / Package maintainers | Cryptographic SHA-256 hash manifest for both binary artifacts. |
| `SHA256SUMS.txt.asc` | GPG Signature | < 1 KB | Security-conscious users | Detached ASCII-armored GPG signature from maintainer's public key. |
| `Source code (zip)` | GitHub Archive | Auto | Developers | Full source repository at tag `v1.0.0`. |
| `Source code (tar.gz)` | GitHub Archive | Auto | Developers | Full source repository at tag `v1.0.0`. |

#### Hash Manifest Example (`SHA256SUMS.txt`):
```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 *FolioHaven-1.0.0-windows-x64-portable.zip
ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb *FolioHaven-1.0.0-windows-x64-setup.exe
```

#### User Verification Instructions (to include in Release Notes):
* **PowerShell**:
  ```powershell
  Get-FileHash -Algorithm SHA256 FolioHaven-1.0.0-windows-x64-portable.zip
  ```
* **Command Prompt**:
  ```cmd
  certutil -hashfile FolioHaven-1.0.0-windows-x64-portable.zip SHA256
  ```

---

### 1.6 Targeted 10-User Personalized Outreach Scripts

Direct, respectful, non-salesy outreach targeting real readers from public complaint threads.

#### Guiding Principles:
1. **Never copy-paste generic templates**: Address their exact grievance.
2. **Zero Commercial Pressure**: Free, open-source tool; no email registration, credit card, or paywall.
3. **Low-Friction Delivery**: Provide direct link to portable zip so they can test without installing anything.
4. **Honest Curiosity**: Position the message as seeking critical feedback from someone who knows the problem intimately.

#### Script Variants:

##### Variant 1: For Users Frustrated by Popups & 10-Second Wait Timers (e.g., r/software thread)
```text
Subject: Built a distraction-free desktop reader (no timers or popups) after seeing your r/software post

Hi [Username],

I saw your comment on Reddit about how frustrating it was when your ebook reader started interrupting chapters with Pro upgrade popups and mandatory 10-second countdown timers. That exact experience bugged me so much that I spent the last few months building an open-source alternative called FolioHaven.

It has the modern, visual digital bookshelf UI that Calibre lacks, but with zero upsells, zero countdown timers, and zero advertising banners. It's completely free and offline.

If you're still looking for a clean desktop reader, I'd love your honest thoughts on the portable build (no installation required):
https://github.com/foliohaven/foliohaven/releases/tag/v1.0.0

No obligation at all—just wanted to share something built specifically to solve that annoyance. Happy reading!
```

##### Variant 2: For Users Blocked by the 10-Book Library Paywall & Category Limits (e.g., r/ereader thread)
```text
Subject: A clean Calibre alternative with unlimited books and shelves (FolioHaven)

Hi [Username],

I came across your post in r/ereader where you mentioned wanting an ebook reader with a clean, modern bookshelf like Icecream, but were annoyed that basic features like adding more than 10 books or creating custom categories were locked behind a paywall.

I had the exact same frustration, so I created FolioHaven. It gives you a clean visual bookshelf with unlimited books, unlimited custom shelves, and instant drag-and-drop import—100% free and open source. Your library is stored in a local SQLite database that you own.

You can try the standalone portable ZIP here without installing anything:
https://github.com/foliohaven/foliohaven/releases/tag/v1.0.0

Would love to hear if this fits what you were looking for!
```

##### Variant 3: For Users Needing Free Study Note & Annotation Export (e.g., r/books & r/libgen threads)
```text
Subject: Free HTML study notes and annotation export in FolioHaven

Hi [Username],

Saw your post in r/books mentioning that you loved two-column reading spreads and sepia mode, but wished note and highlight export wasn't locked behind a commercial Pro license.

I just released FolioHaven v1.0, an open-source desktop reader designed for active reading and study. It includes two-column reflow, sepia themes, 4-color highlighting, and one-click export of your complete notes and quotes to clean, standalone HTML (ready to import into Notion or Obsidian)—completely free.

The project is on GitHub if you'd like to check it out:
https://github.com/foliohaven/foliohaven/releases/tag/v1.0.0

Hope it helps with your reading and study workflow!
```

##### Variant 4: For Users Experiencing 32-Bit Zoom Crashes with Large PDFs/CBZ (e.g., AlternativeTo & Trustpilot)
```text
Subject: 64-bit desktop reader for heavy PDFs and manga archives (FolioHaven)

Hi [Username],

I read your review noting that older desktop readers feel sluggish and crash when zooming into complex PDFs or high-res CBZ manga files because of outdated 32-bit architecture.

We specifically built FolioHaven on a modern 64-bit engine (C++20/Qt6 with PDFium hardware acceleration) to handle multi-gigabyte graphic novels, textbooks, and high-resolution scans smoothly without running out of memory.

If you ever want to test it against your heaviest book files, the portable build is available here:
https://github.com/foliohaven/foliohaven/releases/tag/v1.0.0

I'd be really curious to know if it holds up smoothly on your largest titles.
```

---

## Part 2: Codebase Sweep and Compliance Verification

### 2.1 Architectural Analysis of `sweep.py` and `replica/brand.json`

The sweep linter is defined in `C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py` and configured by `replica/brand.json`.

#### Configuration Rules (`replica/brand.json`):
```json
{
  "name": "FolioHaven",
  "avoid": [
    "Icecream Ebook Reader",
    "Icecream Apps",
    "Icecream Reader"
  ],
  "domains": [
    "icecreamapps.com"
  ],
  "colors": [
    "#3498db",
    "#2980b9",
    "#1abc9c",
    "#2ecc71",
    "#2c3e50",
    "#1f5fdb",
    "#174bb0"
  ]
}
```

#### Code Inspection of `sweep.py`:
1. **Regex Construction** (`build_patterns`, lines 51-64):
   ```python
   parts = [re.escape(p) for p in re.split(r"[\s_-]+", name) if p]
   pats.append(("name", name, re.compile(r"[\s_-]?".join(parts), re.I)))
   ```
   - For `"Icecream Ebook Reader"`, the regex is `re.compile(r"Icecream[\s_-]?Ebook[\s_-]?Reader", re.I)`.
   - **Crucial Consequence**: This matches `icecream_ebook_reader`, `icecream-ebook-reader`, `IcecreamEbookReader`, and `icecream ebook reader`.
2. **Directory & File Skipping Rules** (lines 32-36, 86-90):
   ```python
   SKIP_DIRS = {".git", "node_modules", ".next", ".nuxt", ".svelte-kit", "dist", "build",
                "out", ".vercel", ".turbo", ".cache", "coverage", "__pycache__", ".venv",
                "venv", "Pods", ".expo", "DerivedData", ".gradle"}
   SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
                 "Podfile.lock", "Cargo.lock", "poetry.lock"}
   ```
   Line 88:
   ```python
   if d == "replica" and rel_dir == "." and not include_replica:
       continue
   ```
   - `replica/` is skipped by default unless `--include-replica` is passed.
   - `.agents` is **NOT** in `SKIP_DIRS`!
   - `ORIGINAL_REQUEST.md` is **NOT** in `SKIP_FILES`!
3. **Color Matching Rules** (lines 40, 44-48, 120-124):
   - Regex matches any 3- or 6-digit hex code: `re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-zA-Z])")`.
   - Normalizes to lowercase 6-digit hex (`#3498db`, `#2980b9`, `#1abc9c`, `#2ecc71`, `#2c3e50`, `#1f5fdb`, `#174bb0`).
   - If any scanned file (HTML, CSS, JS, QSS, SVG, MD) contains one of these exact hex values, it flags a hit and exits code 1.

---

### 2.2 Empirical Audit Findings

To verify current cleanliness, `sweep.py` was executed across individual directories:

| Target Scope | Command Executed | Result | Hits Details |
|---|---|:---:|---|
| `app/` | `python sweep.py app --config replica/brand.json` | **PASS (0 hits)** | Clean. Zero competitor names, zero domains, zero competitor colors. |
| `tests/` | `python sweep.py tests --config replica/brand.json` | **PASS (0 hits)** | Clean. Zero competitor names, zero domains, zero competitor colors. |
| `.` (root) | `python sweep.py . --config replica/brand.json` | **FAIL (38 hits)** | 36 name hits, 2 domain hits. **All 38 hits are located in `.agents/teamwork/...` and root `ORIGINAL_REQUEST.md`**. |

---

### 2.3 Critical Pitfall 1: `.agents/` Traversal & Project Folder Path Leaks

#### Root Cause:
The root folder of the project is named:
`c:\Users\epicg\Downloads\icecream_ebook_reader_replica`

Whenever an agent logs working paths (e.g. in `BRIEFING.md`, `DISPATCH.md`, `context.md`, `progress.md`), the string contains `icecream_ebook_reader_replica`.
Because `sweep.py` uses the pattern `Icecream[\s_-]?Ebook[\s_-]?Reader`, the substring `icecream_ebook_reader` matches identically!
Furthermore, `.agents` is not listed in `SKIP_DIRS`. Therefore, running `sweep.py .` scans the entire `.agents/` tree and triggers false positive errors on agent logs.

#### Recommended Solution:
1. **Tooling Fix**: Add `".agents"` to `SKIP_DIRS` in `C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py` (line 34).
2. **Execution Safeguard**: When executing acceptance linter checks, verify directories explicitly:
   - `python sweep.py app --config replica/brand.json`
   - `python sweep.py tests --config replica/brand.json`
   Or when running on `.`, exclude `.agents`.

---

### 2.4 Critical Pitfall 2: Root `ORIGINAL_REQUEST.md` Detection

#### Root Cause:
`ORIGINAL_REQUEST.md` is stored at the project root (`c:\Users\epicg\Downloads\icecream_ebook_reader_replica\ORIGINAL_REQUEST.md`).
Line 7 contains: `Working directory: c:\Users\epicg\Downloads\icecream_ebook_reader_replica`
Line 19 contains: `omit all competitor trademarks and avoid-words ('Icecream', 'Icecream Apps')`
Since `ORIGINAL_REQUEST.md` is a root markdown file and not skipped by `SKIP_FILES`, `sweep.py .` flags lines 7 and 19.

#### Recommended Solution:
Add `"ORIGINAL_REQUEST.md"` to `SKIP_FILES` in `sweep.py`, or ensure `ORIGINAL_REQUEST.md` is archived within `.agents/teamwork/` once `.agents` is excluded from scanning.

---

### 2.5 Critical Pitfall 3: HTML / CSS Asset Leaks in `app/landing.html`

When Phase 2 workers implement `app/landing.html`, there is significant risk of inadvertent brand leakage:

1. **Competitor Mentions in Comparison Copy**:
   - *Risk*: Writing copy such as "Tired of Icecream Ebook Reader?" or "The best Icecream Apps alternative".
   - *Rule*: Per `replica-launch` and `sweep.py`, **zero mentions** of `Icecream`, `Icecream Apps`, or `Icecream Reader` are permitted outside `replica/`.
   - *Compliant Phrasing*: Use generic descriptors: "Tired of freemium readers with 10-second countdown timers?", "The Anti-Nag Free Reader", or "A modern alternative to legacy tools like Calibre".
2. **Competitor URLs & Links**:
   - *Risk*: Linking to `icecreamapps.com` or referencing it in comments.
   - *Rule*: Zero occurrences of `icecreamapps.com`.
3. **Competitor Hex Colors in Styles**:
   - *Risk*: Implementing CSS accents, gradients, or button styles using `#3498db` (standard Icecream cyan-blue) or `#2c3e50` (dark navy).
   - *Rule*: Strictly use FolioHaven design tokens from `replica/design/tokens.css` / `tokens.json`:
     * Primary accent: `#c2410c` (Terracotta)
     * Accent hover: `#9a3412` (Amber Bronze)
     * Sidebar background: `#231f1d` (Espresso Charcoal)
     * Surface background: `#ffffff` / `#f5f7fa`
     * Dark mode background: `#181b22` / `#20242c`
4. **HTML Comments & Data Attributes**:
   - *Risk*: Writing `<!-- Migrated from Icecream Ebook Reader -->` or `<div data-target="icecream-replica">`.
   - *Rule*: `sweep.py` searches raw lines without ignoring HTML comments or data attributes. Comments must remain strictly clean.

---

## Part 3: Synthesis & Implementation Blueprint for Workers

### Summary Checklist for Launch Implementers:

```
[ ] replica/launch/launch-plan.md
    ├── Community mapping cites verified URLs from r/software, r/ereader, r/books, r/libgen
    ├── Day 0 to Day 30 schedule details exact milestone actions
    ├── Show HN narrative includes technical architecture (Qt6, C++20, PDFium, SQLite)
    ├── Product Hunt checklist specifies 240x240 icon, 1270x760 gallery, and maker comment
    ├── GitHub Releases details portable x64 zip, setup exe, and SHA256SUMS.txt
    └── 10-user outreach scripts provide 4 tailored, respectful message templates

[ ] app/landing.html
    ├── Strictly uses FolioHaven tokens (primary accent #c2410c, zero competitor hex colors)
    ├── Strictly zero mentions of "Icecream", "Icecream Apps", or "icecreamapps.com"
    ├── Styled with design-taste-frontend art direction (responsive, clean typography)
    └── Passes `sweep.py app --config replica/brand.json` with 0 hits

[ ] sweep.py / Environment Safeguard
    ├── Note to Orchestrator: Update sweep.py SKIP_DIRS to include ".agents" and SKIP_FILES to include "ORIGINAL_REQUEST.md"
    └── Verify `sweep.py` returns exit code 0
```

---
*Report compiled by Explorer Survey 2. All claims verified via direct tool invocations and static code inspection.*
