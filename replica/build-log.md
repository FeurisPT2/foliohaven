# Replica Build Log: Icecream Ebook Reader

Build log tracking screen-by-screen clean-room implementation progress according to `replica-build`.

| Screen ID | Screen Name | Date | Status | Missing / Deferred | Engineering Notes & Hard Parts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **S01A** | Library Shelf (Cover Grid) | 2026-10-28 | **Done** | Custom cover crop tool | Responsive card flow layout, favorite toggling, reading progress bar delegate, drag-and-drop file ingestion. |
| **S01B** | Library Catalog (Table View) | 2026-10-28 | **Done** | Multi-column drag reorder | Sortable metadata columns, multi-row selection, alternating row styles mapped to design tokens. |
| **S02** | Reader Window Canvas | 2026-10-28 | **Done** | Native GPU text cache | Dual-column reflow vs single-column toggle, margin click zones, autohiding toolbar, screen dimmer overlay (0-80%). Hardest part: balanced column pagination calculations. |
| **S03** | Bookmarks Side Drawer | 2026-10-28 | **Done** | - | Slide-out panel, timestamped bookmark cards, jump to page, clear all bookmarks with confirmation. |
| **S04** | Table of Contents Drawer | 2026-10-28 | **Done** | - | Hierarchical chapter tree navigation, immediate jump to chapter with canvas re-pagination. |
| **S05** | Notes & Highlights Drawer | 2026-10-28 | **Done** | - | Multi-color note listings, attached commentaries, delete single/all, standalone HTML study report export. |
| **S06** | Text Selection Popup (`NotePopup`) | 2026-10-28 | **Done** | Google Translate in-app embed | Floating contextual bubble over DOM selection, 4 color palette swatches, inline commentary editor, clipboard copy. |
| **S07** | In-Reader Quick Settings Popover | 2026-10-28 | **Done** | - | Synchronized palette switcher (Day, Night, Sepia, Dark Sepia), font size steppers, font family, line spacing, dimmer slider. |
| **S08** | Global Preferences Dialog | 2026-10-28 | **Done** | Native SAPI voice enumeration | Modal dialog configuring application chrome theme, default reading profile, TTS speed and volume. |
| **S09** | Book Properties Dialog | 2026-10-28 | **Done** | - | Inspect and edit book title, author, description, metadata labels (file size, format, SHA-256 hash). |
| **S10** | In-Book Search Drawer | 2026-10-28 | **Done** | Regex query mode | Full-text asynchronous in-book keyword search with snippet highlighting and direct chapter navigation. |
| **S11** | Print Ebook Dialog | 2026-10-28 | **Done** | Multi-page print preview | Modal configuring printer targets, page ranges (current view vs chapter), triggers system print pipeline. |
| **S12** | Auxiliary Modals & Popups | 2026-10-28 | **Done** | - | Contextual confirmation alerts for batch deletion, bookmark purging, missing file warnings, duplicate hashes. |

---

### Build Summary
- **Screens Completed**: 12 of 12 screens implemented and verified.
- **Must-Have Features**: 45 of 47 completed (`yes`).
- **Responsive Viewports**: Tested at `1440x900` (desktop) and `390x844` (mobile).
- **Screenshots Captured**: Saved to `replica/clone-screens/` (`S01A.png`, `S01B.png`, `S01_mobile.png`, `S02.png`, `S04.png`, `S08.png`).
- **Design Tokens Adherence**: 100% tokenized via `tokens.css` with zero hard-coded hex colors in application styles.
