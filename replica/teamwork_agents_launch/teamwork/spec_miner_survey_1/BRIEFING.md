# BRIEFING — 2026-10-28T16:46:00Z

## Mission
Extract and document comprehensive technical and domain specifications for R2 (Comparative Pricing & Stripe Product Mapping) and R3 (App Store & Google Play Metadata Specification), cross-referencing user reviews/complaints and authoritative tools.

## 🔒 My Identity
- Archetype: teamwork_preview_spec_miner
- Roles: Specification Miner, Domain Expert, Technical Analyst
- Working directory: c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\spec_miner_survey_1
- Original parent: a189f661-2b98-4c19-8531-5e6ac2b8aa28
- Milestone: Launch Specifications (R2 & R3)

## 🔒 Key Constraints
- Read-only on implementation; specification extraction and documentation only
- Must read authoritative user request at ORIGINAL_REQUEST.md
- Cross-reference 12 complaint data points from replica/feedback.md and replica/reviews.csv
- Ethical pricing structure: Forever Free Core + Optional Open-Sponsor / Supporter Edition (0 recurring paywalls, 3 tiers max)
- Detail exact Stripe objects, prices, metadata, and JSON schemas
- Study listing.py and listing.example.json in replica-launch plugin
- Ensure listing draft passes listing.py with 0 errors
- Deliver analysis.md and handoff.md in working directory

## Current Parent
- Conversation ID: a189f661-2b98-4c19-8531-5e6ac2b8aa28
- Updated: 2026-10-28T16:46:00Z

## Task Summary
- **What to build**: Specification report (analysis.md, handoff.md) detailing R2 pricing architecture & Stripe mapping and R3 App Store/Google Play metadata constraints & draft.
- **Success criteria**: Complete specification mining table, edge cases, exact schemas, verbatim review cross-references, zero lint/validation errors for listing.py.
- **Interface contracts**: replica/launch/pricing.md schema, replica/launch/listing.json schema.
- **Code layout**: .agents/teamwork/spec_miner_survey_1/

## Loaded Skills
- **Source**: C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-launch\SKILL.md
- **Local copy**: C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-launch\listing.py
- **Core methodology**: App store listing linting, copycat & claim policy enforcement, and launch pricing strategy.

## Key Decisions Made
- Fully benchmarked 4 competitors with URLs and verified date (Oct 28, 2026): Icecream ($19.95/yr, $39.95 lifetime), Calibre ($0), ReadEra ($15.99 lifetime), Freda ($2.49).
- Cataloged all 12 review complaint points verbatim with sources, dates, ratings, and architectural fixes (FIX-1 through FIX-6).
- Engineered 3-tier ethical model: Reader ($0), Supporter ($12 one-time), Sustaining Patron ($24/year).
- Identified critical linter edge cases in listing.py: \bfree\b triggers on "distraction-free", [A-Z]{4,} triggers on "EPUB" in short fields.
- Verified candidate draft with listing.py: 0 errors, 0 warnings.
- Wrote full specifications to analysis.md and handoff.md.

## Artifact Index
- analysis.md — Full specification mining analysis and tables for R2 and R3 (`c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\spec_miner_survey_1\analysis.md`).
- handoff.md — 5-component handoff report for orchestrator (`c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\spec_miner_survey_1\handoff.md`).
- progress.md — Liveness heartbeat.
- DISPATCH.md — Task assignment log.
