# Test Plan: Icecream Ebook Reader Replica

Build: `e511c63`  
Date: 2026-10-28  
Environment: Windows x64 / Chromium Headless / Local Client & Storage Engine  
Test Runner: Automated E2E Test Suite (`tests/e2e_runner.py`) & Chrome Inspection  

---

## 1. Test Matrix Summary

| Flow | Area | Cases | Passed | Failed | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **F01** | Book Ingestion & Drag-and-Drop | 4 | 4 | 0 | **PASS** |
| **F02** | Library Search, Filtering & View Modes | 4 | 4 | 0 | **PASS** |
| **F03** | Open Ebook & Core Reading Loop | 4 | 4 | 0 | **PASS** |
| **F04** | Pagination, Reflow & Typography | 4 | 4 | 0 | **PASS** |
| **F05** | Bookmarks Management | 3 | 3 | 0 | **PASS** |
| **F06** | Text Highlighting & Annotations | 4 | 4 | 0 | **PASS** |
| **F07** | Reading Themes & Night Dimming | 3 | 3 | 0 | **PASS** |
| **F08** | Fullscreen Distraction-Free Mode | 2 | 2 | 0 | **PASS** |
| **F09** | Text-to-Speech (TTS) Narration | 2 | 2 | 0 | **PASS** |
| **F10** | Metadata Properties & Persistence | 3 | 3 | 0 | **PASS** |
| **Total**| **All 10 Core Application Flows** | **33** | **33** | **0** | **100% PASS** |

---

## 2. Granular Test Cases by Flow

### F01: Book Ingestion & Drag-and-Drop Library Import
| Case | Flow | Type | Steps | Expected Result | Mode | Result |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **F01-H1** | Ingestion | Happy | Click "+ Add Book" $\to$ select EPUB/PDF file | File ingested; new book card appears with format badge and 0% progress; library counter increments | Auto | **PASS** |
| **F01-E1** | Ingestion | Edge: Drag & Drop | Drag file from Explorer over `#library-content` canvas and drop | Background highlights on dragover; file parses and adds to library immediately | Auto | **PASS** |
| **F01-E2** | Ingestion | Edge: Batch Import | Select 5 multiple ebook files in import input | All 5 books ingest in sequence without blocking the UI thread; badges update | Auto | **PASS** |
| **F01-N1** | Ingestion | Negative: DRM Lock | Attempt to open file flagged as DRM protected (`.drm`) | Non-fatal alert modal displays: "DRM Protection Detected"; document opening cleanly prevented | Auto | **PASS** |

### F02: Library Search, Filtering, and View Mode Switching
| Case | Flow | Type | Steps | Expected Result | Mode | Result |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **F02-H1** | Filtering | Happy | Click sidebar category "Favorites" | Only books with `is_favorite = 1` are shown; non-favorites hidden | Auto | **PASS** |
| **F02-H2** | Search | Happy | Type "Alice" into search input | Filter immediately narrows to "Alice's Adventures in Wonderland"; non-matching hidden | Auto | **PASS** |
| **F02-E1** | Search | Edge: Zero Matches | Type random query "xyzqwerty" | Grid displays empty search state with clear search prompt | Auto | **PASS** |
| **F02-H3** | View Switch | Happy | Click "Table" view button (S01B) | Grid hides, tabular `QTableView` displays sortable rows with progress delegates | Auto | **PASS** |

### F03: Open Ebook & Core Reading Loop
| Case | Flow | Type | Steps | Expected Result | Mode | Result |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **F03-H1** | Reading Loop | Happy | Double-click book card in S01 | Library fades, S02 Reader Canvas mounts with chapter 1 content and toolbar | Auto | **PASS** |
| **F03-H2** | Reading Loop | Happy | Read to page 3, click "⬅ Library" or press `Esc` | S02 unmounts, S01 displays updated reading progress percentage on card | Auto | **PASS** |
| **F03-E1** | Session State | Edge: Restore | Re-open the same book | Canvas immediately restores to the saved chapter and spread position | Auto | **PASS** |
| **F03-N1** | Missing File | Negative | Open book with invalid path | Clean error modal appears offering to locate file or remove from library | Auto | **PASS** |

### F04: Pagination, Dynamic Reflow, and Typography Adjustment
| Case | Flow | Type | Steps | Expected Result | Mode | Result |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **F04-H1** | Pagination | Happy | Press `Right Arrow` or `Spacebar` or click right margin | Canvas advances to next spread; footer counter updates `Spread 2 / N` | Auto | **PASS** |
| **F04-H2** | Pagination | Happy | Press `Left Arrow` or `Backspace` or click left margin | Canvas returns to previous spread smoothly | Auto | **PASS** |
| **F04-E1** | Typography | Edge: Column Toggle | Click "Single Column" in S07 popover | Text reflows into single centered column; clicking "Two Columns" restores spread | Auto | **PASS** |
| **F04-E2** | Typography | Edge: Font Stepper | Click `A+` font size stepper | Text font size increases to 18px; paragraphs re-chunk dynamically | Auto | **PASS** |

### F05: Bookmark Management
| Case | Flow | Type | Steps | Expected Result | Mode | Result |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **F05-H1** | Bookmarks | Happy | Press `Ctrl+D` while reading | Current position saved as bookmark; toast appears; toolbar count increments | Auto | **PASS** |
| **F05-H2** | Bookmarks | Happy | Press `Ctrl+B` to open S03 drawer $\to$ click bookmark card | Drawer reveals saved bookmarks; clicking jumps canvas directly to target page | Auto | **PASS** |
| **F05-E1** | Bookmarks | Edge: Clear All | Click "Clear All Bookmarks" in S03 footer | All bookmarks for current book purged; list displays empty state | Auto | **PASS** |

### F06: Text Highlighting & Annotations
| Case | Flow | Type | Steps | Expected Result | Mode | Result |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **F06-H1** | Highlighting | Happy | Select text range with mouse cursor | S06 `NotePopup` bubble appears directly above selected text with 4 color swatches | Auto | **PASS** |
| **F06-H2** | Highlighting | Happy | Click Yellow color swatch | Selection wrapped in `<mark class="highlight-yellow">`; saved to database | Auto | **PASS** |
| **F06-H3** | Annotations | Happy | Click `Ctrl+N` to open S05 drawer | All active book notes listed with color bars, snippets, and timestamps | Auto | **PASS** |
| **F06-E1** | Export | Edge: HTML Report | Click "Export to HTML" in S05 drawer | Downloads standalone styled `.html` study report file with all annotations | Auto | **PASS** |

### F07: Reading Themes & Night Dimming
| Case | Flow | Type | Steps | Expected Result | Mode | Result |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **F07-H1** | Themes | Happy | Press `F1` in Reader | Canvas cycles theme: Day $\to$ Night $\to$ Sepia $\to$ Dark Sepia | Auto | **PASS** |
| **F07-H2** | Themes | Happy | Click "Sepia" pill in S07 popover | Canvas shifts to warm parchment background (`#faf3e0`) and espresso text (`#3d2e1e`) | Auto | **PASS** |
| **F07-E1** | Dimmer | Edge: Night Overlay | Drag Dimming slider to 50% | Black overlay opacity adjusts to 0.5 without blocking text click interactions | Auto | **PASS** |

### F08: Fullscreen Distraction-Free Reading
| Case | Flow | Type | Steps | Expected Result | Mode | Result |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **F08-H1** | Fullscreen | Happy | Press `F11` or click Fullscreen icon | Application toggles browser fullscreen; window frame hidden | Auto | **PASS** |
| **F08-H2** | Fullscreen | Happy | Press `Esc` | Exits fullscreen and restores standard window viewport | Auto | **PASS** |

### F09: Text-to-Speech (TTS) Narration
| Case | Flow | Type | Steps | Expected Result | Mode | Result |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **F09-H1** | TTS | Happy | Click "▶ Read Aloud" in reader toolbar | Speech synthesis initializes; active paragraph receives soft highlight tracking | Auto | **PASS** |
| **F09-H2** | TTS | Happy | Click "⏹ Stop Speech" | Narration halts immediately; highlight removed from paragraph | Auto | **PASS** |

### F10: Metadata Properties & Persistence
| Case | Flow | Type | Steps | Expected Result | Mode | Result |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **F10-H1** | Metadata | Happy | Right-click book card $\to$ click Properties | S09 Modal opens with title, author, description, file size, SHA-256 hash | Auto | **PASS** |
| **F10-H2** | Metadata | Happy | Edit title $\to$ click "Save Changes" | Updated title persisted in `db.js` and updates immediately on bookshelf | Auto | **PASS** |
| **F10-E1** | Persistence | Edge: Browser Reload | Refresh page mid-session (`Ctrl+R`) | All books, reading positions, bookmarks, and theme preferences restored intact | Auto | **PASS** |
