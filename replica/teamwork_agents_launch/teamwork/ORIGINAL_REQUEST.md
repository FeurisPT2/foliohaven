# Original User Request

## Initial Request — 2026-10-28T16:34:10Z

Produce a complete, production-grade launch package and commercial release kit for **FolioHaven** (the clean-room, distraction-free desktop ebook reader) following the `/replica-launch` specification.

Working directory: c:\Users\epicg\Downloads\icecream_ebook_reader_replica
Integrity mode: development

## Requirements

### R1. Landing Page Copy & Production Web Build
Author `replica/launch/landing.md` adhering strictly to the "Anti-Nag Free Reader" angle and FolioHaven brand voice (Serene, Capable, Respectful) across 7 mandatory sections: Hero, The Problem (without quotes), How It Works (3 steps), Features (tied to FIX-1 through FIX-6), Pricing, FAQ (addressing Calibre & Icecream migrations), and Final CTA. Build a responsive, standalone `app/landing.html` styled with `replica/design/tokens.css` and art-directed with the installed `design-taste-frontend` (`taste-skill`) to ensure distinctive typography, layout substance, and zero generic AI templates.

### R2. Comparative Pricing Model & Stripe Product Mapping
Author `replica/launch/pricing.md` analyzing Icecream's public pricing ($19.95/yr, $39.95 lifetime) and alternatives (Calibre $0, ReadEra $15.99 lifetime, Freda $2.49), citing the 12 complaint data points from `replica/feedback.md`. Specify an ethical "Forever Free Core + Optional Open-Sponsor / Supporter Edition" tier structure with zero recurring paywalls, including explicit Stripe product and price metadata.

### R3. App Store & Google Play Metadata (Linted & Clean)
Author `replica/launch/listing.json` containing complete metadata for the Apple App Store and Google Play Store. Must strictly observe character limits (Title 30, Subtitle 30, Short Desc 80, Promo 170, Keywords 100, Descriptions 4000), omit all competitor trademarks and avoid-words (`Icecream`, `Icecream Apps`), contain zero banned claims ("best", "#1", "free" in title) or emoji in short fields, and pass `listing.py` with 0 errors.

### R4. Go-To-Market Launch Playbook
Author `replica/launch/launch-plan.md` providing a tactical Day 0 to Day 30 distribution plan: Show HN pitch copy, Reddit community engagement strategy targeting verified review complaint threads (r/software, r/ereader, r/books), Product Hunt assets checklist, GitHub Releases binary distribution setup, and initial 10-user outreach script.

## Acceptance Criteria

### Automated Linter Verification
- [ ] `python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-launch\listing.py replica/launch/listing.json` exits with code 0 (0 errors).
- [ ] `python C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py . --config replica/brand.json` exits with code 0 (0 hits).

### Completeness & File Structure
- [ ] `replica/launch/landing.md` exists and covers all 7 required sections without fake social proof or reviewer quotes used as testimonials.
- [ ] `replica/launch/pricing.md` exists with date-stamped competitor pricing tables and complaint attribution.
- [ ] `replica/launch/listing.json` exists, is valid JSON, and parses cleanly.
- [ ] `replica/launch/launch-plan.md` exists with actionable Show HN and Reddit outreach copy.
- [ ] `app/landing.html` exists, renders cleanly, and uses FolioHaven design tokens.
