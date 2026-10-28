# Plan: FolioHaven Launch Package & Commercial Release Kit

## Architecture & Scope
FolioHaven clean-room launch deliverables per `/replica-launch`:
- `replica/launch/landing.md`
- `app/landing.html`
- `replica/launch/pricing.md`
- `replica/launch/listing.json`
- `replica/launch/launch-plan.md`

## Feature Inventory & Requirements Mapping
| # | Requirement | Deliverable | Description | Milestone |
|---|-------------|-------------|-------------|-----------|
| 1 | R1 Landing Page Copy | `replica/launch/landing.md` | 7 sections: Hero, The Problem (no quotes), How It Works (3 steps), Features (FIX-1 to FIX-6), Pricing, FAQ (Calibre/Icecream migrations), Final CTA | M2 |
| 2 | R1 Production Web Build | `app/landing.html` | Responsive standalone HTML styled with `tokens.css`, `design-taste-frontend` art direction, zero AI slop, zero avoid matches | M2 |
| 3 | R2 Comparative Pricing | `replica/launch/pricing.md` | Date-stamped table (Icecream, Calibre, ReadEra, Freda), 12 complaint citations, Forever Free + Supporter tiers, Stripe product metadata | M1 |
| 4 | R3 App Store Metadata | `replica/launch/listing.json` | iOS & Google Play fields, exact limits, zero avoid words, zero claims/emoji in short fields, passing `listing.py` | M1 |
| 5 | R4 Go-To-Market Plan | `replica/launch/launch-plan.md` | Day 0-30 distribution: Show HN copy, targeted Reddit threads, Product Hunt checklist, GitHub Releases setup, 10-user script | M2 |

## Execution Milestones
1. **Phase 0: Survey**:
   - Dispatch Explorers / Spec Miner to survey existing brand guidelines, design tokens, feedback data points, and linter constraints.
2. **Phase 1: Implementation - Foundation (R2 & R3)**:
   - Worker drafts `replica/launch/pricing.md` and `replica/launch/listing.json`.
   - Verify `listing.py` passes with 0 errors.
3. **Phase 2: Implementation - Experience & Go-To-Market (R1 & R4)**:
   - Worker drafts `replica/launch/landing.md`, `replica/launch/launch-plan.md`, and builds `app/landing.html` using `replica/design/tokens.css` and `design-taste-frontend`.
4. **Phase 3: Verification & Auditing**:
   - Run `listing.py` and `sweep.py` to confirm 0 errors and 0 brand hits.
   - Dispatch Reviewers (`teamwork_preview_reviewer`) to verify voice, completeness, and design quality.
   - Dispatch Challengers (`teamwork_preview_challenger`) to stress-test character counts, linter corner cases, responsive layout, and contrast.
   - Dispatch Forensic Auditor (`teamwork_preview_auditor`) for clean-room verification and anti-cheating check.
5. **Phase 4: Synthesis & Reporting**:
   - Synthesize results, update documentation, and report final status to Sentinel.
