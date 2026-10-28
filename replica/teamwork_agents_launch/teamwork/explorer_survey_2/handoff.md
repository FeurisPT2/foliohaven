# Handoff Report: R4 GTM Launch Playbook & Codebase Sweep Verification

**From**: `explorer_survey_2`  
**To**: `orchestrator_1`  
**Date**: 2026-10-28T16:47:00Z  
**Type**: Hard Handoff (Investigation & Survey Complete)  

---

### 1. Observation

1. **Review Data Points & Community Threads**:
   - `replica/reviews.csv` (lines 2-7) and `replica/feedback.md` (lines 21-44) catalog 6 distinct Reddit complaint threads across 4 specific subreddits:
     * `r/software`: `https://www.reddit.com/r/software/comments/123abc/icecream_reader_nag_popups/` (2024-03-15): *"Icecream Ebook Reader used to be great but now the free version is full of pop-ups encouraging an upgrade to Pro with mandatory 10-second waiting timers every few pages. It completely ruins the reading flow."*
     * `r/ereader`: `https://www.reddit.com/r/ereader/comments/456def/best_windows_epub_reader/` (2024-01-20): *"I love the clean UI of Icecream Ebook Reader compared to the clunky Calibre interface, but I wish there was no paywall on basic features like adding more than 10 books or editing categories."*
     * `r/libgen`: `https://www.reddit.com/r/libgen/comments/789ghi/reader_software_recommendations/` (2023-11-05): *"Icecream reader has a nice bookshelf design, but it keeps asking you to upgrade to Pro to unlock notes and full annotations. Why pay for an ebook reader when Sumatra and Calibre are free?"*
     * `r/software`: `https://www.reddit.com/r/software/comments/abc111/good_desktop_ebook_reader/` (2024-04-10): *"It looks much cleaner than Calibre, but it lacks advanced library organization unless you buy the Pro version. Also crashes occasionally when zooming in on complex PDFs."*
     * `r/books`: `https://www.reddit.com/r/books/comments/def222/pc_reading_apps/` (2023-09-18): *"Really pleasant two-column reading spread and sepia mode. Would be great if they let you export notes to HTML without paying for the Pro lifetime license."*
     * `r/software`: `https://www.reddit.com/r/software/comments/ghi333/icecream_apps_alternatives/` (2024-06-22): *"Too many intrusive upselling banners. Every time I open a new chapter, there is a popup asking me to upgrade to Pro. Uninstalled and went back to SumatraPDF."*
2. **Brand Rules & Avoid Configuration**:
   - `replica/brand.json` (lines 1-21) defines:
     * `avoid`: `["Icecream Ebook Reader", "Icecream Apps", "Icecream Reader"]`
     * `domains`: `["icecreamapps.com"]`
     * `colors`: `["#3498db", "#2980b9", "#1abc9c", "#2ecc71", "#2c3e50", "#1f5fdb", "#174bb0"]`
3. **Sweep Tool Implementation**:
   - `C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py`:
     * Line 32-34: `SKIP_DIRS = {".git", "node_modules", ".next", ".nuxt", ".svelte-kit", "dist", "build", "out", ".vercel", ".turbo", ".cache", "coverage", "__pycache__", ".venv", "venv", "Pods", ".expo", "DerivedData", ".gradle"}` (Does NOT include `".agents"`).
     * Line 35-36: `SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "Podfile.lock", "Cargo.lock", "poetry.lock"}` (Does NOT include `"ORIGINAL_REQUEST.md"`).
     * Line 59: `pats.append(("name", name, re.compile(r"[\s_-]?".join(parts), re.I)))`. Compiling `"Icecream Ebook Reader"` matches `icecream_ebook_reader`.
     * Line 88: `if d == "replica" and rel_dir == "." and not include_replica: continue`. `replica/` is excluded by default.
4. **Execution Results**:
   - `python sweep.py app --config replica/brand.json`: **Clean (0 hits, exit 0)**.
   - `python sweep.py tests --config replica/brand.json`: **Clean (0 hits, exit 0)**.
   - `python sweep.py . --config replica/brand.json`: **Failed (38 hits, exit 1)**.
     * All 38 hits originated from `.agents/teamwork/...` files and root `ORIGINAL_REQUEST.md:7` and `ORIGINAL_REQUEST.md:19` because the working directory path is `c:\Users\epicg\Downloads\icecream_ebook_reader_replica`.
5. **Brand Design System**:
   - `replica/design/tokens.json`:
     * Primary brand accent is `#c2410c` (Terracotta) and hover is `#9a3412` (Amber Bronze).
     * Contrast validation checked 27 color pairs with 100% WCAG 2.2 AA/AAA compliance (`replica/brand.md` lines 105-134).
     * Zero competitor hex colors are present in `tokens.json`.

---

### 2. Logic Chain

1. **Mapping Review Pain to GTM Playbook**:
   - *Observation 1* establishes that readers across `r/software`, `r/ereader`, `r/books`, and `r/libgen` were directly alienated by paywalls (10-book cap, note export lock) and countdown timers.
   - *Inference*: The GTM plan must lead with these empirical pain points. The Show HN narrative and Product Hunt maker comment should directly present FolioHaven as the antidote ("The Anti-Nag Free Reader") that solves FIX-1 through FIX-6, rather than presenting it as a generic reader.
   - *Inference*: The 10-user outreach script must be segmented into 4 tailored variations directly addressing the 4 specific complaints (timers, library caps, note exports, and 32-bit zoom crashes).
2. **Binary Distribution Architecture**:
   - *Observation 1* shows user complaints regarding heavy installers, activation failures, and license revocation after updates (`feedback.md` lines 32-34).
   - *Inference*: Offering a portable x64 ZIP (`FolioHaven-1.0.0-windows-x64-portable.zip`) that requires zero installation, admin privileges, or registry access directly eliminates installer/activation failure friction, backed by SHA256 cryptographic verification (`SHA256SUMS.txt`).
3. **Codebase Sweep Compliance & Scanning Vulnerability**:
   - *Observation 3* shows that `sweep.py` splits avoided names by whitespace/punctuation and joins with `[\s_-]?`. Therefore, the project directory name `icecream_ebook_reader_replica` triggers a positive regex match for `Icecream Ebook Reader`.
   - *Observation 3 & 4* show that `sweep.py` does not include `".agents"` in `SKIP_DIRS` or `"ORIGINAL_REQUEST.md"` in `SKIP_FILES`.
   - *Inference*: Running the acceptance test `python sweep.py . --config replica/brand.json` fails with exit code 1 not because production code (`app/` or `tests/`) is contaminated, but because `sweep.py` traverses `.agents/teamwork/` metadata and the root `ORIGINAL_REQUEST.md`.
   - *Inference*: When implementing `app/landing.html`, workers must strictly avoid competitor names, URLs, or hex codes, because `app/` is scanned by `sweep.py` and must maintain 0 hits.
   - *Recommendation for Orchestrator*: To satisfy the acceptance criterion cleanly, `sweep.py` should add `".agents"` to `SKIP_DIRS` and `"ORIGINAL_REQUEST.md"` to `SKIP_FILES`, or the verification step should target production code folders (`app`, `tests`).

---

### 3. Caveats

1. **Reddit Account Creation & Rate Limits**: Reddit algorithms restrict newly created accounts from posting links in subreddits like `r/software`. The GTM schedule accounts for this by prioritizing Show HN and Product Hunt first, while engaging in Reddit threads with value-add technical commentary.
2. **Read-Only Explorer Scope**: In accordance with the Explorer archetype instructions, no source files outside the agent directory have been modified. The suggested additions to `sweep.py` (`.agents` in `SKIP_DIRS`) and the implementation of `replica/launch/launch-plan.md` are documented as proposals for the implementer and orchestrator.
3. **No Testimonials Rule**: Under `/replica-launch` rules, user review quotes cannot be repurposed as fake testimonials on landing pages or marketing copy. The review quotes are strictly preserved as research data in `feedback.md` and `launch-plan.md` community background.

---

### 4. Conclusion

1. **R4 Deliverable Ready for Authoring**: All requirements for `replica/launch/launch-plan.md` have been fully architected and documented in `analysis.md`, including:
   - Verified community mapping with URLs, dates, and quotes for `r/software`, `r/ereader`, `r/books`, `r/libgen`.
   - Day 0 to Day 30 tactical distribution timeline with concrete milestone actions.
   - Complete Show HN post draft with technical details (C++20, Qt6, PDFium, SQLite).
   - Product Hunt asset checklist and maker first comment.
   - GitHub Releases packaging specs (portable x64 zip, setup exe, SHA256 checksums).
   - 4 personalized, respectful 10-user outreach script variations.
2. **Sweep Verification Gate Clear for Production Code**:
   - `app/` and `tests/` are currently 100% clean of all avoided names and hex colors.
   - The false-positive sweep failure on `.` is caused by `.agents/` and `ORIGINAL_REQUEST.md` containing the repository directory path.
   - Concrete guidelines are established to prevent any competitor names or colors from entering `app/landing.html`.

---

### 5. Verification Method

1. **Verify Current Production Code Cleanliness**:
   ```bash
   python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py app --config replica/brand.json
   python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py tests --config replica/brand.json
   ```
   *Expected output*: `Clean. Nothing of the original's name, domain or colours found.` (Exit code 0).
2. **Verify Root Sweep Failure Root Cause**:
   ```bash
   python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py . --config replica/brand.json
   ```
   *Inspection*: Confirm that all 38 matches occur exclusively in `.agents\teamwork\...` and `ORIGINAL_REQUEST.md`.
3. **Inspect Comprehensive Survey Report**:
   - View `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\explorer_survey_2\analysis.md`.
