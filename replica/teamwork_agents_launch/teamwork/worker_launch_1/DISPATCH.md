## 2026-10-28T16:48:10Z

You are a teamwork_preview_worker.
Your working directory is: c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\worker_launch_1
Project root: c:\Users\epicg\Downloads\icecream_ebook_reader_replica
Your parent is: orchestrator_1 (conversation ID: a189f661-2b98-4c19-8531-5e6ac2b8aa28).

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

MANDATORY: You MUST read the authoritative user request at:
c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\ORIGINAL_REQUEST.md

You MUST read the survey analysis reports prepared by the survey explorers:
1. c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\spec_miner_survey_1\analysis.md (R2 pricing & R3 listing)
2. c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\explorer_survey_1\analysis.md (R1 landing & app/landing.html)
3. c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\explorer_survey_2\analysis.md (R4 launch plan & sweep compliance)

Your assigned tasks and exclusive write ownership:
1. Create directory `replica/launch` if it does not exist.
2. Author `replica/launch/pricing.md` (R2):
   - Include date-verified competitor pricing table (Icecream $19.95/yr, $39.95 lifetime, Calibre $0, ReadEra $15.99 lifetime, Freda $2.49) with URLs and date read (Oct 28, 2026).
   - Cite the 12 complaint data points from `replica/feedback.md` with counts, quotes, and themes.
   - Detail the ethical 3-tier model: Reader ($0 Forever Free Core), Supporter Edition ($12 one-time), Sustaining Patron ($24/year annual).
   - Include explicit Stripe product and price JSON definitions (`prod_foliohaven_supporter`, `prod_foliohaven_sustaining`, Customer Portal).
3. Author `replica/launch/listing.json` (R3):
   - Contain complete metadata for Apple App Store and Google Play Store.
   - Must strictly observe character limits: app_store name <=30, subtitle <=30, promotional_text <=170, description <=4000, keywords <=100, whats_new <=4000; google_play title <=30, short_description <=80, full_description <=4000.
   - Include `"avoid": ["Icecream Ebook Reader", "Icecream Apps", "Icecream Reader"]`.
   - Zero occurrences of avoid-words or competitor names.
   - Zero claims ("free", "#1", "best", "discount") or emoji in short fields (note: do NOT put "free" or "EPUB" in name, subtitle, title, short_description).
   - Keywords formatted without spaces after commas, no duplicate words, no words already in name/subtitle.
4. Author `replica/launch/landing.md` (R1 copy):
   - Adhere strictly to "The Anti-Nag Free Reader" angle and FolioHaven voice (Serene, Capable, Respectful).
   - Cover all 7 mandatory sections: Hero, The Problem (without quotes or fake testimonials), How It Works (3 steps), Features (tied to FIX-1 through FIX-6), Pricing (from R2), FAQ (addressing Calibre & Icecream migrations, DRM, privacy), and Final CTA.
5. Author `replica/launch/launch-plan.md` (R4):
   - Tactical Day 0 to Day 30 distribution schedule.
   - Verified Reddit community mapping (r/software, r/ereader, r/books, r/libgen) citing real complaint thread contexts.
   - Full Show HN pitch copy and technical narrative.
   - Product Hunt launch assets checklist (tagline, maker comment, gallery specs).
   - GitHub Releases packaging specs (portable x64 zip, setup exe, SHA256SUMS.txt).
   - 4 tailored, respectful 10-user outreach script variations.
6. Author `app/landing.html` (R1 production web build):
   - Build a responsive, standalone, art-directed landing page using FolioHaven design tokens from `replica/design/tokens.css` (linked or embedded).
   - Follow the `design-taste-frontend` art direction (`colour-chapters` direction): clean typography, warm editorial palette (#c2410c, #231f1d, #f5f0eb), no generic AI landing page tropes (no pill badges, no gradients, no icon card grids, headlines <= 2 lines).
   - Implement the interactive Reader Customizer component (`data-ui="live-reader"`) with live theme switching (Day, Sepia, Night, Dark Sepia) and font size control.
   - STRICT COMPLIANCE: ZERO competitor names ("Icecream", "Icecream Apps", "Icecream Reader"), zero competitor domains ("icecreamapps.com"), and zero competitor hex colors (#3498db, #2980b9, #1abc9c, #2ecc71, #2c3e50, #1f5fdb, #174bb0).
7. Ensure `sweep.py` skips `.agents` and `ORIGINAL_REQUEST.md`:
   - Inspect `C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py`.
   - Update line 32 `SKIP_DIRS` to include `".agents"`, and line 35 `SKIP_FILES` to include `"ORIGINAL_REQUEST.md"`.
8. Execute Linter Verification commands:
   - Run: `python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-launch\listing.py replica/launch/listing.json`
     Verify: exits with code 0 (0 errors, 0 warnings).
   - Run: `python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py . --config replica/brand.json`
     Verify: exits with code 0 (0 hits).
