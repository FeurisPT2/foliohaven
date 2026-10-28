# Bug Tracking & QA Log: Icecream Ebook Reader Replica

Conducted under the `replica-test` methodology.  
Total Bugs Identified: 2 | Total Fixed: 2 | Open S1: 0 | Open S2: 0 | Shippable: **YES**

---

### BUG-001: Two-Column Spread Fallback on Odd-Page Chapter Ends

- **Severity**: **S3** (Broken with workaround / visibly wrong layout)
- **Flow / Case**: `F04 / F04-E1` (Column Mode Reflow Toggle)
- **Screen**: `S02` (Reader Window Canvas)
- **Build**: `e511c63`
- **Browser / Device**: Chromium Headless / 1440px Desktop

**Steps to Reproduce**:
1. Open any book with an odd number of paginated columns (e.g. 3 columns total in chapter 1).
2. Advance page to the second spread (`spreadIndex = 1`).
3. Click "Two Columns" (`#btn-col-double`) in S07 quick settings popover.

**Expected**:
The canvas renders `<div class="two-column-spread">` with the third column on the left and a clean empty right page mimicking a physical book spread.

**Actual**:
`renderCurrentView()` checked `if (this.columnCount === 2 && spread.right)` and fell back to `<div class="single-column-spread">`, abruptly switching layout to single column.

**Evidence**:
`tests/e2e_suite.py` failure on `F04-E1`: `AssertionError: Two column spread not restored`.

**Root Cause**:
Condition in `engine.js` line 115 required `spread.right` to be truthy to mount `.two-column-spread`.

**Resolution & Commit**:
Modified `engine.js` to always mount `.two-column-spread` when `this.columnCount === 2`, rendering an empty right column if `spread.right` is null. Retested and passed in `tests/e2e_suite.py`.  
Status: **Fixed**.

---

### BUG-002: Missing Non-Fatal Alert on DRM-Locked Documents

- **Severity**: **S2** (Core flow error state unhandled)
- **Flow / Case**: `F01 / F01-N1` (DRM Protection Detection & Warning)
- **Screen**: `S01` / `S02` / `S12`
- **Build**: `e511c63`
- **Browser / Device**: Chromium Headless / 1440px Desktop

**Steps to Reproduce**:
1. Attempt to open a book with encrypted container or `.drm` extension.
2. Canvas mounted an empty chapter without messaging.

**Expected**:
A non-fatal modal dialog (`#modal-confirm`) appears with message: "DRM Protection Detected: The document you are attempting to open is encrypted with Digital Rights Management (DRM). Clean-room reading of DRM-locked files is prohibited." Document opening is gracefully rejected.

**Actual**:
Application entered silent failure mode with blank reader canvas.

**Evidence**:
Clean-room recon requirement R1 and `features.csv` line 9.

**Resolution & Commit**:
Added DRM encryption check in `openBook()` in `app/app.js` with non-fatal modal display. Retested and passed in `tests/e2e_suite.py` (`F01-N1`).  
Status: **Fixed**.

---

## QA Summary Table

| Bug ID | Title | Severity | Screen | Flow | Status | Resolution |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **BUG-001** | Two-column spread fallback on odd page chapter ends | S3 | S02 | F04 | **Fixed** | Updated `renderCurrentView()` in `engine.js` |
| **BUG-002** | Missing non-fatal alert on DRM-locked documents | S2 | S12 | F01 | **Fixed** | Added DRM pre-flight guard in `openBook()` in `app.js` |

*Zero open S1 blockers, zero open S2 blockers.*
