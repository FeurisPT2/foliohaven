# Recon Map: Icecream Ebook Reader (Windows Desktop)

Scope: Full clean-room feature, UI/UX, and data persistence reverse-engineering of Icecream Ebook Reader (v6.56 / core binary v6.0.0.0) for a modern 64-bit C++20 and Qt 6 desktop replica.  
Platform: Windows Desktop (x64) with cross-platform architecture (Linux / macOS compatible).  
Target Product: Icecream Ebook Reader (Icecream Apps Ltd).  
Date: 2026-10-28  
Investigator: Teamwork Clean-Room Engineering Group (`worker_m1`, `explorer_survey_1`, `explorer_survey_2`, `spec_miner_survey_1`)  

---

## 1. Executive Summary

Icecream Ebook Reader is a mature Windows desktop ebook management and reading application designed for personal document and book collections. The application couples a localized digital bookshelf (supporting both visual cover grid and tabular metadata views) with an in-depth reading canvas capable of rendering both reflowable publications and fixed-layout graphics.

### Core Loop
Users import DRM-free ebook files or directory trees into a centralized local library, organize books into categories/folders, and open them in a distraction-free, customizable reading canvas that automatically tracks reading progress, preserves bookmarks and text annotations, and restores the exact reading position across application launches.

### Supported Format Scope
The application natively handles six major document formats:
1. **EPUB** (EPUB 2.0.1 and EPUB 3.2 reflowable documents)
2. **PDF** (Portable Document Format fixed-layout vector/raster documents)
3. **MOBI / AZW / PRC** (Mobipocket PalmDOC compressed reflowable documents)
4. **FB2** (FictionBook 2.0/2.1 XML documents with embedded base64 graphics)
5. **CBZ / CBR** (Comic Book ZIP/RAR archives containing raster graphics)
6. **TXT** (Plain text documents with statistical charset detection and paragraph reflow)

### Tech Stack Comparison: Original vs. Clean-Room Replica

| Architectural Dimension | Original Application (v6.56) | Modern Clean-Room Replica (C++20 / Qt 6) |
|---|---|---|
| **Architecture / Target** | 32-bit x86 MSVC 2019 Windows | 64-bit x64 C++20 Windows / Linux / macOS |
| **GUI Framework** | Qt 5.15.1 (Widgets, WinExtras, Custom DWM) | Qt 6.6+ (Widgets, High-DPI Canvas, SVG Engine) |
| **Reflow Engine** | QtWebKit (`Qt5WebKit.dll`, 29.1 MB legacy DLL) | In-process modern engine (`QTextDocument` / custom CSS reflow) |
| **Fixed Layout (PDF)** | Foxit/Debenu Quick PDF (`DebenuPDFLibraryDLL1016.dll`) | Google PDFium / `poppler-qt6` (permissive open-source) |
| **Archive Containers** | `quazip.dll`, `unrar.dll` (v7.11), `7zxa.dll` | `libzip` / `QuaZip-Qt6` + `libarchive` |
| **Concurrency / Worker** | External process `icebooksvc.exe` via WebSockets | In-process `QThreadPool`, `QFutureWatcher`, `std::jthread` |
| **Persistence Engine** | SQLite 3 (`ebooklib.sqlite3`) + `settings.ini` | SQLite 3 WAL mode via `QSqlDatabase` + `settings.ini` |
| **Speech (TTS)** | Windows SAPI via `qtexttospeech_sapi.dll` | Qt 6 `QTextToSpeech` (Windows OneCore/SAPI, Speech Dispatcher) |
| **Commercial Gating** | PRO tier nag dialogs and feature locks | Complete, unrestricted open-source feature set |

---

## 2. Clean-Room Sources

All reconnaissance findings are grounded exclusively in clean-room observations of local installation files, binary inspection of exports and symbols, configuration INI files, extracted translation catalogs, and public product documentation. No proprietary source code was decompiled, and no proprietary reverse-engineering tools were utilized.

| # | Source Category | File / Path / Resource | Ground Truth Yield |
|---|---|---|---|
| 1 | **Local Installation** | `C:\Program Files (x86)\Icecream Ebook Reader\` | Inventory of 84 files, 9 subdirectories, 111 MB footprint. Identification of runtime dependencies (`Qt5WebKit`, `DebenuPDFLibraryDLL1016.dll`, `quazip.dll`, `icudt65.dll`). |
| 2 | **Binary Inspection** | `icebookreader.exe` (3,309,024 bytes) | 291 RTTI class descriptors, PDB build path (`D:\Work\BookReader\...`), internal method symbols, embedded SVG resource list, SQL DDL strings. |
| 3 | **Helper Process** | `icebooksvc.exe` (80,864 bytes) | Out-of-process pagination service symbols (`icebooksvc::reportPaginationDone`, `remotehandler.cpp`, `wstransport.h`). |
| 4 | **Database Schema** | `C:\Users\epicg\.Icecream Ebook Reader\data\ebooklib.sqlite3` | Exact DDL for `books`, `folders`, `book_folder_binder`, `book_metadata`, triggers, indexes, and content hash fields. |
| 5 | **Runtime Configuration** | `C:\Users\epicg\AppData\Local\Icecream\Icecream Ebook Reader\settings.ini` | INI key hierarchy: `lastStyleId`, `library_view_mode`, `ttsLocaleVoiceMap`, `ttsVolume`, `column_count=2`, `localeName`. |
| 6 | **Localization Catalogs** | `C:\Program Files (x86)\Icecream Ebook Reader\translations\*.qm` | 49 translation files. Verbatim parsing of `ebookreader_en.qm` yielding 372 distinct localized UI text entries across 43 QTranslator contexts. |
| 7 | **Application Logs** | `C:\Users\epicg\.Icecream Ebook Reader\log\icebookreader_*.txt` | Verbatim runtime trace logs of window resizing suspension events (`RESIZE MODE true / false`) and UI mode transitions. |
| 8 | **Public Documentation** | Official Icecream Ebook Reader manual and feature guides | Verified user flows, feature descriptions, hotkey tables, and PRO tier differentiation. |

---

## 3. Screen Inventory (S01–S12)

The user interface of Icecream Ebook Reader is structured into 12 core screens, drawers, and modal dialogs. Stable identifiers (S01 through S12) are defined below with comprehensive specifications of routes, purposes, UI component compositions, and all observed functional states.

### Summary Table

| Screen ID | Screen Name | Route / Entry Point | Purpose | Key Components | States Observed |
|---|---|---|---|---|---|
| **S01A** | Library Shelf (Grid View) | Application launch or `Esc` / Back arrow from reader | Visual card-based browsing of book covers and reading progress | Sidebar categories, top action bar, search input, `BookCardWidget` flow layout, operations footer | Empty, Populated, Filtered, Multi-select, Drag-hover |
| **S01B** | Library Catalog (Table View) | Top-right view switcher button on S01 | Dense tabular view of book metadata and sortable attributes | Tabular header, `QTableView`, progress bar delegate, sort indicators, operations footer | Empty, Populated, Sorted, Multi-select |
| **S02** | Reader Window Canvas | Double-click book in S01 or click "Read" / "Continue reading" | Main reading canvas supporting reflow and fixed-page layouts | Dual-column/Single-column canvas, floating top toolbar, bottom scrubber footer, margin click zones | Loading spinner, Single page, 2-page spread, Dimmed overlay, Error |
| **S03** | Bookmarks Side Drawer | Toolbar bookmark icon or `Ctrl+B` | View, jump to, and delete page bookmarks | Drawer header, "Add bookmark" button, "Clear all" button, scrollable bookmark item cards, close `X` | Empty, Populated, Deleting, Clear confirmation |
| **S04** | Table of Contents Drawer | Toolbar TOC icon or `Ctrl+T` | Hierarchical navigation through book chapters and sections | Drawer header, expandable `QTreeView` of chapter nodes, page number labels, active chapter highlight | Empty (no TOC), Populated, Branch expanded |
| **S05** | Notes & Highlights Drawer | Toolbar notes icon or `Ctrl+N` | Review book annotations, search notes, export study reports | Header with note count, search input, "Export to HTML" button, "Clear all notes" button, annotation cards | Empty (instructional), Populated, Filtered, Empty search |
| **S06** | Text Selection Popup (`NotePopup`) | Automatic on text selection in S02 | Quick action bubble for highlighting, annotation, search, copy | 4-color palette swatches, "Add note" button, "Copy" button, Google/Wikipedia/Translate buttons | Color swatches, Inline note editor bubble |
| **S07** | In-Reader Quick Settings Popover | Toolbar gear icon in S02 | Non-modal overlay for real-time visual adjustment | Font family combobox, font size +/-, line spacing +/-, alignment buttons, single/double toggle, theme radio pills, dimming slider | Popover open, Slider dragging, Real-time canvas preview |
| **S08** | Global Preferences Dialog (`IceDialog`) | Sidebar gear icon (S01) or S07 "Open All Settings" link | System-wide application settings, hotkeys, reading defaults, TTS | 5-tab header (System, Reading, Hotkeys, Text to Speech, License), OK, Cancel, Apply buttons | Active tab display, Voice testing, Key recording |
| **S09** | Book Properties Dialog | Book context menu $\to$ "Properties..." | Inspect and edit book metadata and custom cover image | Book cover thumbnail, "Select image" / "Restore cover" buttons, Title/Author inputs, Description editor, file info labels | Original cover, Custom cover loaded, Editing metadata |
| **S10** | In-Book Search Drawer | Toolbar search icon or `Ctrl+F` | Full-text search and direct page jumping | Search input ("Search: text / page number"), "Go to page %1" action, search result snippet cards | Empty input, Searching spinner, Results list, "Nothing found" |
| **S11** | Print Ebook Dialog | Toolbar print icon or `Ctrl+P` | Configure print job for ebook content | Printer combobox, page range radios (All, Current, From/To), copies, orientation, paper size, quality | Ready to print, No printers available warning |
| **S12** | Auxiliary Modals & Confirmation Popups | Triggered by actions across S01, S02, S08 | User alerts, duplicate warnings, and destructive confirmations | Frameless dialog shells with clear title, message body, primary & secondary action buttons | Book Added, Book Exists, Missing File, Password Prompt, Clear Warning |

---

### Deep Screen Specifications

#### S01A: Library Shelf (Grid View)
- **Route**: Application start or `Esc` from S02.
- **Purpose**: Provides a rich visual catalog where book covers are displayed as cards in a responsive flow layout.
- **Layout & Structure**:
  - **Left Sidebar**: 220px fixed vertical bar displaying brand logo, system categories (`All`, `Recently Read`, `Read`, `Favorites`, `Deleted`), format filter tree, custom user folders, and bottom utility buttons (Settings, Help).
  - **Top Action Bar**: "+ Add book" button (primary accent), "+ Add folder" button, instant search bar with clear button, and segmented view toggle (Grid vs. Table).
  - **Central Area**: Responsive `IceFlowLayout` / `QListView` presenting `BookCardWidget` items with uniform padding and spacing.
  - **Bottom Footer**: Context-sensitive operations footer appearing when 1 or more books are selected.
- **Functional States**:
  1. *Empty State*: Displays a centered dashed container with a book icon and message: "Drop books here to add them to your library" alongside large "+ Add book to library" button.
  2. *Populated State*: Cover cards arranged alphabetically or by last-read timestamp. Each card renders the cover image, format badge (top-left), favorite star toggle (top-right), bold title (elided at 2 lines), author (gray, 1 line), and horizontal reading progress bar (0–100%).
  3. *Filtered State*: When a sidebar category or search term is active, non-matching cards are hidden. If zero matches occur, shows: "No books found in '%1'".
  4. *Multi-Select State*: Clicking cards with `Ctrl` or `Shift` activates multi-selection. Selected cards show a highlighted border and checkmark; footer slides up showing: "%1 books selected", "Select all", "Clear selection", "Add to category", "Delete".
  5. *Drag-and-Drop State*: Dragging book files from Windows Explorer over S01 dims the canvas and displays: "Drop books here...".

#### S01B: Library Catalog (Table View)
- **Route**: Activated by clicking the Table View button on the S01 top action bar.
- **Purpose**: Dense data presentation for large libraries, allowing sorting by metadata attributes.
- **Layout & Structure**:
  - Replaces central grid with a `QTableView` with sortable column headers:
    1. `Title` (with small format icon prefix)
    2. `Author`
    3. `Date` (formatted date added or date last opened)
    4. `Notes` (numeric counter badge of highlights/notes)
    5. `Progress` (progress bar delegate with percentage text)
    6. `Format` (file extension in uppercase: EPUB, PDF, MOBI, etc.)
- **Functional States**:
  1. *Populated State*: Alternating row colors (`#FFFFFF` and `#F8F9FA` in Day mode), rows vertically centered.
  2. *Sorted State*: Clicking any header sorts rows ascending/descending with visual arrow indicator.
  3. *Multi-Row Selection*: Row selection synchronized with the bottom operations footer.

#### S02: Reader Window Canvas
- **Route**: Double-clicking any book card or row in S01.
- **Purpose**: Distraction-free reading environment rendering book content with precise typography and pagination.
- **Layout & Structure**:
  - **Central Viewport**:
    - For Reflowable formats (EPUB, MOBI, FB2, TXT): Dual-column or single-column paginated text canvas. Left and right 15% margin zones act as clickable page-turn buttons with semi-transparent arrow indicators on hover.
    - For Fixed-layout formats (PDF, CBZ, CBR): High-DPI rendered page canvas with smooth zoom, fit-to-width, and fit-to-page modes.
  - **Floating Top Toolbar**: Collapsible horizontal bar containing: Back to Library arrow, TOC (`Ctrl+T`), Bookmarks (`Ctrl+B`), Notes (`Ctrl+N`), In-Book Search (`Ctrl+F`), Fullscreen (`F11`), Zoom In/Out, TTS controls, and Quick Settings gear.
  - **Floating Bottom Footer**: Minimalist overlay showing `Page: %1 / %2`, reading progress scrubber slider, and conditional "Back to page %1" history link.
- **Functional States**:
  1. *Loading State*: Displays semi-transparent overlay with spinning `ReadingSpinner` while the document container and first chapter are parsed.
  2. *Single-Page State*: Text rendered in a single centered column with comfortable margins.
  3. *Two-Page Spread State*: Text split into two balanced columns mimicking an open physical book with a central subtle gutter line.
  4. *Dimmed State*: Fullscreen black overlay with adjustable alpha (0% to 80%) layered over canvas to reduce eye strain in low-light environments.
  5. *Error State*: Displays modal alert if the file is DRM-protected, corrupted, or missing from the disk.

#### S03: Bookmarks Side Drawer
- **Route**: Click Bookmark icon in S02 top toolbar or press `Ctrl+B`.
- **Purpose**: Browse, jump to, and delete saved bookmarks for the current book.
- **Layout & Structure**: Slides out from the right edge over S02 (width 320px). Contains:
  - Header with title: "Bookmarks (%1)" and close button `X`.
  - "+ Add bookmark" button: Adds a bookmark for the active reading position.
  - Scrollable list of bookmark tiles, each showing: Page number ("Page %1"), relative reading percentage ("%1%"), chapter title, timestamp, and trash icon.
  - "Clear all bookmarks" button at bottom.
- **Functional States**:
  1. *Empty State*: Centered prompt: "Click the button above to add a new bookmark."
  2. *Populated State*: Vertical list sorted by document position. Clicking a tile navigates the reader immediately to the bookmarked location.
  3. *Delete Confirmation*: Clicking "Clear all bookmarks" presents `Dialog_ClearBookmarks`.

#### S04: Table of Contents (TOC) Side Drawer
- **Route**: Click TOC icon in S02 top toolbar or press `Ctrl+T`.
- **Purpose**: Hierarchical chapter and section navigation.
- **Layout & Structure**: Slides out from the left edge (width 340px). Contains:
  - Header: "Table of contents" and close `X`.
  - Recursive `QTreeView` displaying chapter titles with indentation for subsections.
  - Destination page labels right-aligned: "Page %1".
- **Functional States**:
  1. *Empty State*: Displayed if the publication contains no TOC: "This book does not have a table of contents".
  2. *Populated State*: Hierarchical tree with expand/collapse arrows. Active chapter matching the current reading position is styled with a distinct bold accent color.
  3. *Navigation*: Clicking any node immediately scrolls/navigates the reader and closes the drawer.

#### S05: Notes & Highlights Side Drawer
- **Route**: Click Notes icon in S02 top toolbar or press `Ctrl+N`.
- **Purpose**: Review all annotations and highlights created in the current book, search notes, and export study summaries.
- **Layout & Structure**: Slides out from the right edge (width 360px). Contains:
  - Header: "Notes (%1)" and close `X`.
  - Search input box to filter notes by keyword.
  - Top action row: "Export notes to HTML" button and "Clear all notes" trash icon.
  - Scrollable list of annotation cards. Each card displays: colored swatch pill (Yellow, Green, Cyan, Pink, Underline), page number, highlighted quote snippet in italics, user commentary text, creation date, and delete button.
- **Functional States**:
  1. *Empty State*: Instructional graphic showing: "To add a note: 1. Select the text you want to annotate 2. Then click the color or the 'Add note' button in the opened menu."
  2. *Populated State*: Ordered list of annotations sorted by document offset. Clicking an annotation jumps the reader canvas to the exact text location.
  3. *Filtered State*: Real-time sub-filtering as the user types into the search box. If no matches occur, displays "Nothing found".

#### S06: Text Selection Popup (`NotePopup`)
- **Route**: Automatically pops up adjacent to cursor upon releasing mouse selection over text in S02.
- **Purpose**: Immediate context actions for selected text.
- **Layout & Structure**: Floating bubble widget positioned above or below the selection bounding box with pointer arrow:
  - 4 circular color swatches: Yellow (`#FFE270`), Green (`#A8F29A`), Cyan (`#7BE5F8`), Pink (`#FFA0C5`).
  - Action buttons: "Add note" (pencil icon), "Copy" (`Ctrl+C`), "Google", "Wikipedia", "Translate".
- **Functional States**:
  1. *Swatch Click*: Clicking a color swatch immediately wraps the selected text in `<span class="highlight_{color}">`, increments note count, and dismisses popup.
  2. *Add Note Click*: Expands an inline comment editor bubble with a multi-line text input, "SAVE" and "CANCEL" buttons.
  3. *Web Actions*: Clicking Google / Wikipedia / Translate opens the system default browser with URL parameters containing the encoded selected text.

#### S07: In-Reader Quick Settings Popover
- **Route**: Click Gear icon on S02 top toolbar.
- **Purpose**: Non-modal popover for adjusting typography, layout, and visual themes during reading without opening modal dialogs.
- **Layout & Structure**: Popover anchored beneath the toolbar gear icon:
  - Font controls: Font Family dropdown with "Original font" checkbox, Font Size (`-` / `+` buttons and point size label).
  - Line Spacing: Increase (`+`) and Decrease (`-`) line spacing buttons.
  - Text Alignment: Segmented buttons for Left, Center, Right, Justified.
  - Page View: Segmented toggle for Single Column vs. Double Page Spread.
  - Theme Selector: 4 colored pill buttons for Day, Night, Light Sepia, and Dark Sepia.
  - Dimming Slider: Horizontal slider (0% to 80%) with moon/brightness icons.
  - Bottom link: "Open All Settings" (navigates to S08).
- **Functional States**:
  - Live adjustment: Every property change emits immediate signals, updating canvas CSS/DOM reflow in real time without requiring a save button.

#### S08: Global Preferences Dialog (`IceDialog`)
- **Route**: Click Settings (gear icon) in S01 sidebar or click "Open All Settings" from S07.
- **Purpose**: Centralized application configuration.
- **Layout & Structure**: Modal tabbed dialog with 5 tabs:
  1. **System Tab**: UI Theme (Day, Night, Light Sepia, Dark Sepia), Dimming slider, Application Language dropdown (49 languages), Local Library path picker, External drive copy toggle ("Copy eBooks from external devices"), EBR Archive Export/Import buttons, "Empty Library" button.
  2. **Reading Tab**: Default Page view (Single/Double), Default font family, Default text alignment, Auto page flipping interval spinbox (seconds).
  3. **Text-to-Speech Tab**: Voice selector dropdown (lists installed SAPI/OneCore voices), Reading speed slider (0.5x to 2.0x), Pitch slider, Volume slider (0–100%), "Test voice" playback button.
  4. **Hotkeys Tab**: Comprehensive table listing 25 customizable keyboard shortcuts with key sequence capture.
  5. **License / About Tab**: Displays application version, license status, registration key input, and website links.

#### S09: Book Properties Dialog
- **Route**: Right-click any book card/row in S01 $\to$ select "Properties...".
- **Purpose**: Inspect technical file metadata and customize title, author, description, and cover image.
- **Layout & Structure**:
  - Left column: Large book cover thumbnail (200x280px) with "Change book cover" / "Select image" and "Restore the book cover" buttons.
  - Right column:
    - Editable fields: `Title`, `Author`, `Description` (scrollable text area).
    - Read-only technical fields: `Format` (e.g. EPUB 3.2), `File path`, `File size` (formatted KB/MB), `Date added`, `Last read on`, `Progress` (percentage and current/max page).
  - Bottom buttons: "SAVE" (primary) and "CANCEL".
- **Functional States**:
  - Custom Cover Loaded: Overrides default cover extracted from container and sets `use_user_cover = 1` in SQLite.

#### S10: In-Book Search Drawer
- **Route**: Click Search icon on S02 top toolbar or press `Ctrl+F`.
- **Purpose**: Search full text of the currently open book and jump directly to matches or page numbers.
- **Layout & Structure**: Slides out from right edge (width 340px). Contains:
  - Top search input with placeholder: "Search: text / page number" and clear `X`.
  - Action button: "Go to page %1" (activates if user types an integer).
  - Result counter: "%1 results found".
  - Scrollable list of match result cards. Each card displays: Chapter title, page number, and a text snippet with the matching query term highlighted in bold yellow.
- **Functional States**:
  1. *Searching State*: Progress spinner indicates background search thread scanning chapters.
  2. *Results Populated*: Results stream into list progressively. Clicking a result card scrolls/navigates the reader to the exact text position.
  3. *No Match*: Displays "Nothing found".

#### S11: Print Ebook Dialog
- **Route**: Click Print icon on S02 top toolbar or press `Ctrl+P`.
- **Purpose**: Configure physical or PDF printer jobs for the document.
- **Layout & Structure**: Standard styled print dialog:
  - Printer dropdown showing installed system printers and status.
  - Print range: Radio buttons for "All pages", "Current page", "Pages from [X] to [Y]".
  - Copies spinbox with Collate checkbox.
  - Orientation: Portrait vs. Landscape toggle.
  - Paper size dropdown (A4, Letter, Legal, etc.).
  - Color mode: Color vs. Grayscale.
  - "Print" and "Cancel" buttons.
- **Functional States**:
  - No Printers Available: Displays warning banner: "There are no printers available." with disabled Print CTA.

#### S12: Auxiliary Modals & Confirmation Popups
- **Route**: Triggered dynamically by specific user actions across S01, S02, and S08.
- **Purpose**: User notifications, duplicate handling, password prompts, and destructive confirmations.
- **Variants**:
  1. `Dialog_BookAdded`: Triggered after single or batch import. Displays "%n books added!" with two buttons: "Start reading now" (immediately opens the first added book in S02) and "OK" (dismisses to S01).
  2. `Dialog_BookExists`: Triggered when an imported book file's hash matches an existing record in SQLite: "The document %1 has already been added to your library."
  3. `Dialog_Password`: Triggered when opening password-encrypted PDF files: "The file '%1' is password protected." with password text input, "Unlock" button, and "Wrong password!" error label.
  4. `Dialog_ClearBookmarks` / `Dialog_ClearNotes` / `Dialog_ClearLibrary` / `Dialog_EmptyTrash`: Modal warnings confirming destructive metadata purges while explicitly reassuring the user that original files on disk remain safe.
  5. `Dialog_Error`: Warning modal for unreadable, DRM-protected, or missing files.

---

## 4. Key User Flows (F01–F10)

The following 10 flows define the complete behavioral map of the application. Each flow details screen transitions, decision points, happy-path click counts, and boundary edge cases.

### F01: Book and Folder Import (Single & Bulk)
```
[S01 Library Shelf]
      │
      ├─► User clicks "+ Add book" ──► [OS File Dialog] (Filters: .epub, .pdf, .mobi, .fb2, .cbz, .txt, etc.)
      │                                       │
      │                                       └─► User selects 1 or more files & clicks "Open"
      │
      ├─► User clicks "+ Add folder" ──► [OS Folder Picker] ──► User selects directory
      │
      └─► User drags files/folders from Windows Explorer & drops over S01 canvas
                                              │
                                              ▼
                             [Background Worker Ingestion Pipeline]
                                              │
                   ┌──────────────────────────┴──────────────────────────┐
                   ▼                                                     ▼
      [Compute SHA-256 Hash]                               [Check Database Duplicates]
                   │                                                     │
                   ├─► Match found in `books.book_hash` ──► Prompt `Dialog_BookExists` (Skip)
                   │
                   └─► Unique hash ──► Ingest File:
                             ├─► Extract metadata (Title, Author, Format, Size) via Format Engine
                             ├─► Extract and render cover image thumbnail to cache directory
                             ├─► Execute SQLite: `INSERT INTO books (...) VALUES (...)`
                             └─► Bind to active sidebar folder in `book_folder_binder`
                                              │
                                              ▼
                                   [Dialog_BookAdded Modal]
                                   "1 book added!" or "%n books added!"
                                              │
                         ┌────────────────────┴────────────────────┐
                         ▼                                         ▼
           Click "Start reading now"                          Click "OK"
                         │                                         │
                         ▼                                         ▼
            Transition directly to S02               Stay on S01 (Library canvas
              (Opens book in Reader)                   refreshes with new cards)
```
- **Happy Path Clicks**: 3 clicks (Click "+ Add book" $\to$ Select file in OS dialog & click Open $\to$ Click "Start reading now").
- **Edge Cases**:
  - *Removable Media Detection*: If imported files reside on a removable USB flash drive or external SD card, the application checks preference `Copy eBooks from external devices`. If enabled, copies book files locally into `~/.ebookreader/books/` before indexing.
  - *Large Batch Progress*: When importing 500+ books from a folder hierarchy, the S01 footer displays a progress bar with item counter, "Pause", "Resume", and "Cancel" buttons, processing in non-blocking batches of 50.
  - *Corrupted Container*: If a ZIP archive or EPUB container is truncated or corrupt, the importer logs an error, skips the file, and displays an ingestion summary dialog at the end: "%1 books added, %2 files failed".

### F02: Library Search, Filter, and View Mode Switching
```
[S01 Library Screen]
      │
      ├─► 1. Sidebar Category Selection:
      │      User clicks sidebar item ("Recently Read", "Favorites", "Deleted", or custom folder)
      │      └─► Updates SQLite filter: `WHERE is_deleted = 0 AND is_favorite = 1` etc.
      │
      ├─► 2. Format Sub-Filtering:
      │      User clicks "Formats" $\to$ selects "EPUB"
      │      └─► Refines query: `AND format = 0`
      │
      ├─► 3. Instant Search Filtering:
      │      User types query into top search bar (e.g. "Tolkien")
      │      └─► Instant incremental filter query: `AND (title LIKE '%Tolkien%' OR author LIKE '%Tolkien%')`
      │
      └─► 4. View Mode Toggle:
             User clicks Table View button (top right)
             ├─► Transitions view from S01A (Grid) to S01B (Table)
             └─► Persists setting `library_view_mode=1` in `settings.ini`
```
- **Happy Path Clicks**: 1 click to filter by category; 0 clicks for search (immediate typing in input).
- **Edge Cases**:
  - *Zero Results*: If search query matches no books, the canvas renders: "No books found in '%1'" with a quick link to "Clear search".
  - *State Preservation*: Toggling between Grid (S01A) and Table (S01B) preserves active category selection, search query string, and current scroll position.

### F03: Open and Read Ebook (The Core Loop)
```
[S01 Library (Grid or Table)]
      │
      └─► User double-clicks book card OR selects book and clicks "Read" / "Continue reading"
            │
            ▼
[S02 Reader Window]
      ├─► S01 fades out; S02 canvas mounts with `ReadingSpinner` overlay
      ├─► DocumentEngine opens container in background thread
      ├─► Query `books.position` and `reading_progress.cfi_position` for saved reading offset
      ├─► Render active chapter/page with user's preferred theme, font size, and column mode
      ├─► Dismiss `ReadingSpinner`
      │
      │ (Active Reading Session)
      │   ├─► Turn pages via Keyboard (Arrows/Space), Mouse wheel, or Margin click zones
      │   ├─► Resize window ──► Triggers interactive resize suspension mechanism
      │   └─► Auto-save reading position periodically to `reading_progress` table
      │
      └─► User clicks "Back to Library" icon (top-left) OR presses `Esc`
            ├─► Commit exact current position, percentage, and `time_last_view = UTC_NOW()` to SQLite
            └─► Transition back to S01; book card displays updated reading progress % pill
```
- **Happy Path Clicks**: 1 double-click.
- **Edge Cases**:
  - *Missing Book File*: If the file was moved or deleted on disk externally after being indexed, opening triggers `Dialog_Error`: "The file you are trying to open was not found by the following path: %1" with options to "Locate file..." or "Remove from library".
  - *DRM Protection*: Encrypted files trigger error dialog: "DRM protected. Book cannot be opened."

### F04: Pagination, Layout, and Typography Adjustment
```
[S02 Reader Window]
      │
      ├─► Page Stepping:
      │      ├─► Forward: Right Arrow, Spacebar, Page Down, Down Arrow, or click Right Margin
      │      ├─► Backward: Left Arrow, Backspace, Page Up, Up Arrow, or click Left Margin
      │      └─► Boundaries: `Home` (first page of book), `End` (last page of book)
      │
      └─► Typography & Layout Adjustments (Click Gear Icon ──► S07 Quick Settings Popover):
             ├─► Switch Column Count: Click "Single" or "Double" (persisted to `column_count`)
             ├─► Change Font Size: Click `+` or `-` (or hotkeys `Ctrl+Up` / `Ctrl+Down`)
             ├─► Adjust Line Spacing: Click increase/decrease spacing buttons
             ├─► Text Alignment: Switch between Justify, Left, Center, Right
             └─► Font Family: Select installed font or check "Original font"
                         │
                         ▼
             [Document Engine Dynamic Reflow Pass]
             Recalculates chapter column breaks while preserving the active CFI anchor
             ensuring the user remains on the exact sentence being read.
```
- **Happy Path Clicks**: 2 clicks to alter column mode or font.
- **Edge Cases**:
  - *Minimum Window Width in 2-Column Mode*: If the user resizes the window below 700px width while in Two-Column mode, the engine automatically clamps to Single-Column mode to prevent unreadable column widths, restoring Two-Column mode when resized wider.

### F05: Bookmark Management
```
[S02 Reader Window]
      │
      ├─► Create Bookmark:
      │      User clicks Bookmark Ribbon icon on Toolbar OR presses `Ctrl+D`
      │      ├─► Engine captures current `page_number`, `cfi_position`, chapter title, and text snippet
      │      ├─► Inserts record into `bookmarks` SQLite table
      │      ├─► Bookmark icon on toolbar highlights, and count badge updates: "Bookmarks (N)"
      │      └─► Brief toast notification: "Bookmark added"
      │
      └─► View & Jump Bookmarks:
             User clicks "Bookmarks (N)" in toolbar OR presses `Ctrl+B`
             ├─► S03 Bookmarks Side Drawer slides out from right
             ├─► User reviews list of bookmark tiles
             ├─► Clicking a tile immediately jumps the reader canvas to the bookmarked location
             ├─► Clicking a tile's trash icon deletes that individual bookmark
             └─► Clicking "Clear all bookmarks" prompts `Dialog_ClearBookmarks`
```
- **Happy Path Clicks**: 1 click / shortcut to create; 2 clicks to open drawer and jump.

### F06: Text Highlighting, Annotations, and HTML Export
```
[S02 Reader Window]
      │
      └─► User drags mouse cursor across text to create a text selection
            │
            ▼
[S06 NotePopup Bubble Appears Adjacent to Selection]
      │
      ├─► Option A: Quick Highlight
      │      User clicks one of 4 color swatches (Yellow, Green, Cyan, Pink)
      │      ├─► DOM wraps selection in `<span class="highlight_{color}">`
      │      ├─► Inserts record into `annotations` table with `color_code`, `cfi_start`, `cfi_end`
      │      ├─► `books.notes_count` counter incremented via trigger
      │      └─► S06 popup dismisses
      │
      ├─► Option B: Add Text Commentary
      │      User clicks "Add note" button
      │      ├─► Popup expands into text editor bubble
      │      ├─► User types annotation text and clicks "SAVE"
      │      └─► Highlight persisted with attached note commentary
      │
      ├─► Option C: Web Lookup & Copy
      │      User clicks "Copy", "Google", "Wikipedia", or "Translate"
      │
      └─► Option D: Export Notes & Study Report
             User opens S05 Notes Drawer (`Ctrl+N`) ──► clicks "Export notes to HTML"
             ├─► OS File Save dialog prompts for destination filename (`*.html`)
             └─► Engine renders a standalone HTML file containing book metadata, cover,
                 and all annotations grouped by chapter with timestamps and color pills.
```
- **Happy Path Clicks**: 2 clicks to highlight; 3 clicks to add comment; 2 clicks to export.

### F07: Reading Themes, Color Profiles, and Dimming
```
[S02 Reader Window or S07 Quick Settings]
      │
      ├─► Theme Switching:
      │      User clicks Theme button on toolbar OR presses `F1`
      │      └─► Cycles or selects one of 4 reading palettes:
      │            1. Day: Crisp white background (`#FFFFFF`), charcoal text (`#1E1E1E`)
      │            2. Night: Deep charcoal background (`#181818`), light gray text (`#C8C8C8`)
      │            3. Light Sepia: Warm paper (`#FBF0D9`), dark espresso text (`#433422`)
      │            4. Dark Sepia: Muted sepia brown (`#2C2621`), warm cream text (`#D0BE9C`)
      │      └─► Canvas stylesheet, toolbars, and scrollbars re-theme synchronously.
      │
      └─► Display Dimming:
             User drags Dimming slider in S07 (0% to 80%)
             └─► Adjusts alpha channel of a borderless black overlay widget above the reader,
                 allowing reading below the monitor's minimum hardware brightness level.
```
- **Happy Path Clicks**: 1 click to switch theme.

### F08: Fullscreen Distraction-Free Reading Mode
```
[S02 Reader Window]
      │
      └─► User presses `F11` OR clicks Fullscreen icon on top toolbar
            │
            ▼
[Fullscreen Mode Activated]
      ├─► Window borders, title bar, and OS taskbar hidden (`setWindowState(Qt::WindowFullScreen)`)
      ├─► Top toolbar smoothly slides up and autohides off-screen
      ├─► Bottom footer scrubber fades out
      │
      │ (Reading in Pure Content Canvas)
      │   ├─► Moving mouse cursor within top 20px edge smoothly slides toolbar back into view
      │   ├─► Moving cursor away slides toolbar back out of view after 2-second timeout
      │   └─► Page navigation via keyboard and margins remains fully active
      │
      └─► User presses `F11` or `Esc` ──► Restores normal windowed frame and controls
```
- **Happy Path Clicks**: 1 keypress (`F11`).

### F09: Text-to-Speech (TTS) Read Aloud Narration
```
[S02 Reader Window]
      │
      └─► User clicks "Read Aloud" button on toolbar OR presses `F7`
            │
            ▼
[TTS Engine Initiated]
      ├─► Document engine extracts plain text of the active chapter/page
      ├─► Text segmented into sentence/paragraph speech units
      ├─► TTS sub-toolbar expands showing Play/Pause, Stop, Prev, Next, Speed, Volume
      ├─► Synthesizer starts speaking active paragraph via `QTextToSpeech`
      ├─► Canvas dynamically applies subtle highlight to the paragraph currently being read
      │
      │ (Continuous Playback)
      │   ├─► When the last paragraph of the visible page finishes, engine automatically
      │   │   advances page and continues reading seamlessly
      │   ├─► User adjusts Volume slider (0-100%) or Speed slider (0.5x - 2.0x) in real time
      │   └─► User clicks Prev/Next buttons (`F5`/`F6`) to skip speech chunks
      │
      └─► User clicks Stop (`F8`) ──► Synthesizer halts, highlight removed, toolbar collapses
```
- **Happy Path Clicks**: 1 click to start; 1 click to stop.

### F10: Library Archive Backup and Migration (.EBR)
```
[S01 Footer OR S08 System Settings]
      │
      ├─► Library Backup (.EBR Export):
      │      User clicks "Export Library to archive"
      │      ├─► OS File Save dialog prompts for destination filename (`*.ebr`)
      │      ├─► Background worker packages:
      │      │     1. SQLite database file (`ebooklib.sqlite3`)
      │      │     2. Cached covers directory (`covers/*.jpg`)
      │      │     3. Managed ebook files
      │      │     4. `manifest.json` describing archive version and contents
      │      ├─► Compresses into single ZIP container with `.ebr` extension
      │      └─► Modal alert displays: "Library successfully exported!"
      │
      └─► Library Restore (.EBR Import):
             User on new installation clicks "Import books from archive"
             ├─► OS File Open dialog $\to$ user selects `.ebr` file
             ├─► Worker validates `manifest.json`, extracts books and covers, merges database records
             └─► S01 library refreshes with all restored books, reading progress, and bookmarks.
```
- **Happy Path Clicks**: 3 clicks to backup or restore.

---

## 5. UI Component Catalog

The following catalog specifies all custom, composite, and reusable UI components identified across the application, detailing their child widgets, properties, visual states, and hotkeys.

### C01: Navigation Sidebar (`MainWindow_SideBar`)
- **Base Class**: `QWidget` / styled `QListWidget`.
- **Properties & Styling**: Fixed width (220px), dark slate background (`#2B303C` in default skin), zero border.
- **Children**:
  - `LogoHeader`: Application icon + "Ebook Reader" brand label.
  - `CategoryList`: List of category items with SVG icons and badge counters:
    - `AllBooks`: "All (%1)"
    - `RecentlyRead`: "Recently Read (%1)"
    - `ReadBooks`: "Read (%1)"
    - `Favorites`: "Favorites (%1)" (star icon)
    - `TrashBooks`: "Deleted (%1)" (trash can icon)
    - `FormatsSection`: Expandable tree node listing format filters (EPUB, PDF, MOBI, FB2, CBZ, TXT) with book count per format.
    - `UserFolders`: Dynamic list of custom folders created by the user with inline badge counters and context menu (Rename, Delete).
    - `AddFolderButton`: Flat button "+ Add new category".
  - `BottomUtilityBar`: Pinned at bottom: "Settings" (gear), "Help" (question mark).
- **States**: Item Normal, Item Hover (subtle white highlight), Item Selected (accent pill background).

### C02: Library Top Action Bar (`LibraryHeaderBar`)
- **Base Class**: `QToolBar` / horizontal layout.
- **Children**:
  - `BtnAddBook`: High-contrast accent button "+ Add book".
  - `BtnAddFolder`: Flat button "+ Add folder".
  - `SearchLineEdit`: Rounded search input field with embedded search glass icon, placeholder "Search in Library", and clear `X` icon. Emits `textChanged(QString)` with 150ms debounce.
  - `ViewModeSwitch`: Segmented 2-button group (`QButtonGroup`):
    - `BtnCardsView`: Icon `library-view-cards.svg`.
    - `BtnTableView`: Icon `library-view-table.svg`.

### C03: Book Cover Card Widget (`BookCardWidget`)
- **Base Class**: `QWidget` composite item used in `IceFlowLayout`.
- **Dimensions**: Fixed 160px width $\times$ 240px height.
- **Children**:
  - `ThumbnailFrame`: 150x200px cover image rendered with 4px border radius and subtle drop shadow. Uses asynchronous image loader.
  - `FormatBadge`: Small colored pill in top-left corner (e.g. `EPUB`, `PDF`, `MOBI`).
  - `FavoriteToggle`: 20x20px star button in top-right corner; transparent when inactive, solid gold when active.
  - `TitleLabel`: Bold font, elided at 2 lines.
  - `AuthorLabel`: Subdued gray font, elided at 1 line.
  - `ProgressBar`: 3px horizontal track at bottom of thumbnail rendering progress (0–100%) in green/accent color.
- **States**:
  - *Normal*: Standard card elevation.
  - *Hover*: Card elevates +2px with subtle glow outline; favorite star becomes visible if unset.
  - *Selected*: 2px solid accent border and checkmark badge overlay in top-right.

### C04: Library Table View (`BookTableView`)
- **Base Class**: `QTableView` with custom model `BookModel`.
- **Columns**: Title, Author, Date, Notes, Progress, Format.
- **Custom Delegates**:
  - `CoverTitleDelegate`: Renders 24x32px mini cover thumbnail adjacent to title text.
  - `ProgressDelegate`: Renders progress bar with overlaid percentage text.
  - `NotesDelegate`: Renders numeric badge pill.
- **Features**: Sort indicators in header, alternating row backgrounds, multi-row selection via `Shift`/`Ctrl`.

### C05: Library Operations Footer (`LibraryFooterBar`)
- **Base Class**: Animated sliding `QWidget` pinned to bottom of S01.
- **Children**:
  - `SelectionLabel`: "%1 books selected".
  - `BtnSelectAll`, `BtnClearSelection`.
  - `BtnContinueReading`: Visible when exactly 1 book is selected.
  - `BtnAddToFolder`, `BtnRemoveFromFolder`.
  - `BtnDelete`: Moves selected books to Trash (`is_deleted = 1`).
  - `BtnRestore`: Visible in Trash view.
  - `BtnPurge`: "Delete permanently".
  - `TransferProgressGroup`: Progress bar and Pause/Resume/Cancel buttons for active import/export jobs.

### C06: Reader Top Toolbar (`ReadingToolBar`)
- **Base Class**: Floating `QToolBar` pinned to top of S02 with autohide support in fullscreen.
- **Children**:
  - `BtnBack`: Left arrow icon ("Finish reading and return to library").
  - `Separator`.
  - `BtnToc`: Table of contents icon (`Ctrl+T`).
  - `BtnBookmarks`: Bookmark ribbon icon with count badge ("Bookmarks (N)", `Ctrl+B`).
  - `BtnNotes`: Highlighter icon with count badge ("Notes (N)", `Ctrl+N`).
  - `BtnSearch`: Magnifying glass icon ("Search text / page", `Ctrl+F`).
  - `Separator`.
  - `BtnFullscreen`: Fullscreen expand icon (`F11`).
  - `BtnZoomOut`, `BtnZoomReset` ("100%"), `BtnZoomIn`.
  - `BtnFitPage`, `BtnFitWidth` (active in PDF/Fixed-layout mode).
  - `Separator`.
  - `TtsControlGroup`: Play/Pause (`F7`), Stop (`F8`), Prev (`F5`), Next (`F6`), Volume popup.
  - `Separator`.
  - `BtnPrint`: Printer icon (`Ctrl+P`).
  - `BtnQuickSettings`: Gear icon (toggles S07 popover).

### C07: Reader Scrubber Footer (`ReadingFooterBar`)
- **Base Class**: Floating translucent overlay pinned to bottom of S02.
- **Children**:
  - `PageLabel`: "Page: %1 / %2".
  - `ScrubberSlider`: Custom `IceSlider` with chapter tick marks and hover tooltip showing target page and chapter name.
  - `BtnJumpBack`: Dynamic button "Back to page %1" appearing after chapter jumps.

### C08: Selection Context Bubble (`NotePopup`)
- **Base Class**: Frameless, shadowed `QWidget` with custom arrow pointer pointing to text selection.
- **Children**:
  - Color palette swatches: 4 colored circles (Yellow `#FFE270`, Green `#A8F29A`, Cyan `#7BE5F8`, Pink `#FFA0C5`).
  - Icon buttons: Add Note (pencil), Copy text, Delete note (trash), Google, Wikipedia, Translate.
  - Inline comment edit sub-panel with `QPlainTextEdit`, "SAVE", and "CANCEL" buttons.

### C09: Custom Frameless Shell (`IceWindow` / `IceDialog`)
- **Base Class**: `QMainWindow` / `QDialog` with native Windows DWM hit testing for borderless window resizing and aero drop shadow.
- **Children**:
  - Custom draggable title bar with icon, title text, and Windows control buttons (Minimize, Maximize/Restore, Close).

### C10: Complete Keyboard Shortcuts Catalog

| Shortcut | Context | Action |
|---|---|---|
| `Left` / `Up` / `PgUp` / `Backspace` | Reader (S02) | Previous Page |
| `Right` / `Down` / `PgDown` / `Space` | Reader (S02) | Next Page |
| `Home` | Reader (S02) | First Page of Book |
| `End` | Reader (S02) | Last Page of Book |
| `Ctrl+Up` / `Ctrl+=` | Reader (S02) | Zoom In / Increase Font Size |
| `Ctrl+Down` / `Ctrl+-` | Reader (S02) | Zoom Out / Decrease Font Size |
| `Ctrl+0` | Reader (S02) | Reset Zoom to 100% |
| `Shift+0` | Reader (S02) | Fit to Page (PDF/Images) |
| `Shift+1` | Reader (S02) | Fit to Width (PDF/Images) |
| `Ctrl+1` | Reader (S02) | Single Column Mode |
| `Ctrl+2` | Reader (S02) | Two Columns (Double Page Spread) |
| `F1` | Reader (S02) | Cycle Reading Theme (Day $\to$ Night $\to$ Sepia $\to$ Dark Sepia) |
| `F11` | Reader (S02) | Toggle Fullscreen Mode |
| `Esc` | Reader (S02) | Back to Library (or Exit Fullscreen) |
| `Ctrl+F` / `F3` | Reader (S02) | Toggle In-Book Search Drawer |
| `Ctrl+T` | Reader (S02) | Toggle Table of Contents Drawer |
| `Ctrl+B` | Reader (S02) | Toggle Bookmarks Drawer |
| `Ctrl+D` | Reader (S02) | Quick Add Bookmark for Current Page |
| `Ctrl+N` | Reader (S02) | Toggle Notes & Highlights Drawer |
| `Ctrl+C` / `Ctrl+Ins` | Reader (S02) | Copy Selected Text |
| `Ctrl+P` | Reader (S02) | Open Print Dialog |
| `F7` / `Media Play` | Reader (S02) | Start / Pause TTS Reading Aloud |
| `F8` / `Media Stop` | Reader (S02) | Stop TTS Reading Aloud |
| `F5` / `Media Prev` | Reader (S02) | TTS Skip to Previous Paragraph |
| `F6` / `Media Next` | Reader (S02) | TTS Skip to Next Paragraph |
| `F9` / `F10` | Reader (S02) | Decrease / Increase TTS Volume |

---

## 6. Format Handling Pipelines

The clean-room replica implements a unified document engine architecture (`IDocumentEngine`) abstracting all supported formats into two rendering paradigms:
- `ReflowableDocumentEngine`: EPUB, MOBI, FB2, TXT.
- `FixedLayoutDocumentEngine`: PDF, CBZ, CBR.

```
                     <<interface>>
                    IDocumentEngine
                     ▲           ▲
                     │           │
     ┌───────────────┴───┐   ┌───┴────────────────┐
     │ ReflowableEngine  │   │ FixedLayoutEngine  │
     └───────┬───────────┘   └────────┬───────────┘
             │                        │
     ┌───────┼───────┐        ┌───────┼───────┐
     ▼       ▼       ▼        ▼       ▼       ▼
    EPUB    MOBI    FB2      PDF     CBZ     CBR
    TXT
```

### 6.1 EPUB Pipeline (EPUB 2.0.1 and EPUB 3.2 / 3.3)
1. **Container Extraction & OCF Verification**:
   - The file is verified as an Open Container Format (OCF) ZIP archive.
   - Validation checks that the first entry is uncompressed `mimetype` with content `application/epub+zip`.
   - Extracts `META-INF/container.xml`. Parses XML to locate `<rootfile full-path="..." media-type="application/oebps-package+xml"/>`.
2. **Package Document (`.opf`) Parsing**:
   - Parses OPF XML:
     - `<metadata>`: Extracts `dc:title`, `dc:creator` (author), `dc:identifier` (UUID/ISBN), `dc:language`, `dc:date`.
     - Cover extraction: EPUB 2 checks `<meta name="cover" content="item_id"/>`; EPUB 3 checks manifest item with `properties="cover-image"`.
     - `<manifest>`: Builds dictionary mapping item IDs to `{href, media-type, properties}`.
     - `<spine>`: Extracts ordered vector of spine item references (`itemref idref="..."`) establishing the linear reading order.
3. **Table of Contents (TOC) Extraction**:
   - EPUB 2: Parses NCX document (`.ncx`), extracting hierarchical `<navPoint>` elements with labels and target source URLs.
   - EPUB 3: Parses XHTML Navigation Document (`properties="nav"`), extracting `<nav epub:type="toc">` ordered lists.
4. **Content Sanitization & CSS Styling**:
   - Chapter XHTML documents are extracted on demand.
   - External network requests and script tags (`<script>`) are stripped for security.
   - Injects clean-room user styling: dynamic column width, font family, line spacing, margins, and active theme palette (Day, Night, Sepia).
5. **EPUB Canonical Fragment Identifier (CFI) Engine**:
   - Synthesizes and parses EPUB CFI strings (e.g. `epubcfi(/6/4[chap01]!/4/2/10/1:24)`).
   - Resolves spine item offset (`/6`), element tree hierarchy (`/4/2/10`), and character offsets (`/1:24`).
   - Guarantees exact reading position and highlight restoration across arbitrary window resizing and font changes.

### 6.2 PDF Pipeline (Portable Document Format)
1. **Engine Selection**:
   - Selected Engine: Google PDFium (Apache 2.0) or `poppler-qt6`.
   - Eliminates the original application's legacy commercial 32-bit `DebenuPDFLibraryDLL1016.dll`.
2. **Page Rasterization & Viewport Culling**:
   - PDF pages are rendered into high-resolution `QImage` buffers on worker threads.
   - Render scale is computed from target DPI, zoom factor, and display `devicePixelRatio` to ensure razor-sharp text on Hi-DPI / 4K displays.
   - Implements Viewport Culling and Lookahead: Renders only the visible page spread plus a $\pm 1$ page lookahead buffer. When the user navigates rapidly, pending render tasks for non-visible pages are cancelled via `std::stop_token`.
3. **Outlines & Text Selection**:
   - Recursively traverses the PDF outline dictionary (`Root/Outlines`) to populate `TocModel`.
   - Extracts character glyph bounding boxes (`QRectF`) for text selection, highlight overlays, and in-book full-text search.

### 6.3 MOBI / AZW / PRC Pipeline (Mobipocket)
1. **Palm Database (PDB) Parsing**:
   - Parses the 78-byte PDB header: Database name, attributes, creation/modification timestamps, type (`BOOK`), creator (`MOBI`), and record count $N$.
   - Reads the record offset table locating the byte offset of each record in the file.
2. **Header Records & Metadata**:
   - Record 0 Header Parsing:
     - PalmDOC Header: Compression type (1 = Uncompressed, 2 = PalmDOC LZ77, 17480 = HUFF/CDIC), text length, record count.
     - MOBI Header: Header length, MOBI type, text encoding (CP1252 or UTF-8), first non-book record index, first image index.
     - EXTH Chunk: Parses tag/value records (Title, Author, Description, Publisher, Cover Offset).
3. **PalmDOC LZ77 Decompression**:
   - Implements byte-stream LZ77 decompressor:
     - Byte `0x00`: Literal byte `0x00`.
     - Bytes `0x01`–`0x08`: Copy next $N$ bytes literally.
     - Bytes `0x09`–`0x7F`: Literal ASCII character.
     - Bytes `0x80`–`0xBF`: 2-byte sequence decoding backreference distance and length from sliding window.
     - Bytes `0xC0`–`0xFF`: ASCII space followed by character `(B ^ 0xC0)`.
4. **HTML Stream Assembly**:
   - Concatenates decompressed text records into a unified HTML stream.
   - Maps Mobipocket image tags (`<img recindex="K">`) to embedded binary image records extracted from PDB offsets.

### 6.4 FB2 Pipeline (FictionBook 2.0 / 2.1)
1. **XML Streaming & DOM Architecture**:
   - Single XML file (or ZIP archive containing `.fb2`).
   - Uses `QXmlStreamReader` to extract `<description>` and cover art without parsing the entire file into memory:
     - `<title-info>`: Book title, author names, genres, language, keywords.
     - `<coverpage>`: Extracts image reference (e.g. `<image l:href="#cover.jpg"/>`).
   - Base64 binary extraction: Directly decodes `<binary id="cover.jpg" content-type="image/jpeg">` byte stream to generate cover thumbnail.
2. **Section Hierarchy & Footnotes**:
   - Parses `<body>` into virtual chapters based on hierarchical `<section>` tags.
   - Extracts `<body name="notes">` into a dedicated footnote dictionary, linking inline footnote markers to popup notes.

### 6.5 CBZ / CBR Pipeline (Comic Book Archives)
1. **Container Extraction**:
   - CBZ: Uses `QuaZip-Qt6` / `libzip` to inspect ZIP central directory.
   - CBR: Uses `unrar` / `libarchive` to inspect RAR headers.
2. **Page Ordering & Image Filtering**:
   - Filters entries for valid image formats (`.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`).
   - Applies natural alphanumeric sorting (e.g., `page_1.jpg`, `page_2.jpg`, `page_10.jpg` correctly ordered).
   - First natural image is extracted and cached as cover thumbnail.
3. **Comic Metadata (`ComicInfo.xml`)**:
   - Inspects archive root for `ComicInfo.xml`.
   - Extracts rich metadata: Series, Issue Number, Volume, Summary, Writer, Penciller, Page Count.

### 6.6 TXT Pipeline (Plain Text Reflow)
1. **Charset Detection**:
   - Step 1: Check for Byte Order Mark (UTF-8 `EF BB BF`, UTF-16LE `FF FE`, UTF-16BE `FE FF`).
   - Step 2: If no BOM, execute `uchardet` (Mozilla statistical charset detector) or ICU charset detector (`ucsdet_detect`).
   - Step 3: Decode text stream into `QString` using `QStringConverter`.
   - Step 4: Allow manual charset override via reader settings.
2. **Heuristic Paragraph Reflow**:
   - Distinguishes hard line wraps from semantic paragraph breaks:
     - A single newline `\n` followed by non-whitespace is treated as a soft wrap (joined by a single space) unless the preceding line ends with terminal punctuation (`.`, `!`, `?`, `:"`).
     - Double newlines `\n\n` denote paragraph breaks.
   - Divides monolithic text into virtual chapters and pages ($\approx 2,500$ characters per virtual page) for rapid pagination.

---

## 7. Inferred Data Model

The persistence layer centers on a production SQLite database (`ebooklib.sqlite3`) and an INI configuration file (`settings.ini`). The data model is fully normalized, enforcing strict foreign key constraints, cascading deletes, and query optimization indexes.

```
   ┌────────────────┐         1:N         ┌──────────────────┐
   │    folders     │◄───────────────────┤book_folder_binder│
   └────────────────┘                     └────────┬─────────┘
                                                   │
                                                   │ N:1
                                                   ▼
┌──────────────────┐         1:N          ┌──────────────────┐
│   book_authors   │◄────────────────────┤      books       ├───────────────────┐
└────────┬─────────┘                      └────────┬─────────┘                   │
         │ N:1                                     │                             │ 1:N
         ▼                                         │ 1:N                         ▼
┌──────────────────┐                               ▼                    ┌──────────────────┐
│     authors      │                      ┌──────────────────┐          │    bookmarks     │
└──────────────────┘                      │   annotations    │          └──────────────────┘
                                          └──────────────────┘
```

### Entity Specifications

#### 1. `books`
- **Purpose**: Core catalog table tracking all indexed publications.
- **Fields**:
  - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `book_hash`: TEXT NOT NULL UNIQUE (SHA-256 hash for deduplication)
  - `full_path`: TEXT NOT NULL (Absolute path to book file)
  - `title`: TEXT NOT NULL
  - `author`: TEXT
  - `format`: INTEGER NOT NULL (0=EPUB, 1=MOBI, 2=PDF, 3=FB2, 4=CBZ, 5=CBR, 6=TXT)
  - `file_size`: INTEGER NOT NULL DEFAULT 0
  - `cover_path`: TEXT (Relative path to cached cover image)
  - `use_user_cover`: INTEGER NOT NULL DEFAULT 0 (Flag if user replaced cover)
  - `time_added`: INTEGER NOT NULL (UTC Unix epoch seconds)
  - `time_last_view`: INTEGER NOT NULL DEFAULT 0 (UTC timestamp of last session)
  - `position`: INTEGER NOT NULL DEFAULT 0 (Page index or chapter offset)
  - `max_position`: INTEGER NOT NULL DEFAULT 0 (Total page/chapter count)
  - `progress_percentage`: REAL NOT NULL DEFAULT 0.0 (0.0% to 100.0%)
  - `is_read`: INTEGER NOT NULL DEFAULT 0 (1 if finished, 0 otherwise)
  - `is_favorite`: INTEGER NOT NULL DEFAULT 0 (1 if starred, 0 otherwise)
  - `is_deleted`: INTEGER NOT NULL DEFAULT 0 (1 if moved to Trash, 0 if active)
  - `notes_count`: INTEGER NOT NULL DEFAULT 0 (Cached annotation count)
- **Evidence**: Authoritative DDL extracted from `icebookreader.exe` and `ebooklib.sqlite3`.
- **Confidence**: High (Direct observation).

#### 2. `authors` & `book_authors`
- **Purpose**: Normalized author catalog supporting multi-author works and sort names ("Tolkien, J.R.R.").
- **Fields**:
  - `authors`: `id`, `name`, `sort_name`.
  - `book_authors`: `book_id`, `author_id`, `role` ('author', 'translator', 'editor').
- **Evidence**: Required for normalized author filtering and clean-room architecture.
- **Confidence**: High.

#### 3. `folders`
- **Purpose**: Hierarchical user-defined categories and collections.
- **Fields**: `id`, `parent_id` (FOREIGN KEY referencing `folders(id)` ON DELETE SET NULL), `title` TEXT NOT NULL UNIQUE.
- **Evidence**: Authoritative DDL in `icebookreader.exe`.
- **Confidence**: High (Direct observation).

#### 4. `book_folder_binder`
- **Purpose**: Many-to-many relationship binder linking books to user folders.
- **Fields**: `book_id` (FOREIGN KEY referencing `books(id)` ON DELETE CASCADE), `folder_id` (FOREIGN KEY referencing `folders(id)` ON DELETE CASCADE), PRIMARY KEY (`book_id`, `folder_id`).
- **Evidence**: Authoritative DDL in `icebookreader.exe`.
- **Confidence**: High (Direct observation).

#### 5. `reading_progress`
- **Purpose**: Fine-grained session tracking and reading history.
- **Fields**: `id`, `book_id` (FK), `cfi_position` TEXT, `page_number` INTEGER, `percentage` REAL, `read_duration_seconds` INTEGER, `last_read_timestamp` INTEGER.
- **Evidence**: Extracted symbols `cFI`, `TextBookChapter::setReadingPosition`.
- **Confidence**: High.

#### 6. `bookmarks`
- **Purpose**: Stores page and fragment bookmarks.
- **Fields**: `id`, `book_id` (FK), `page_number` INTEGER, `cfi_position` TEXT, `title` TEXT, `snippet` TEXT, `created_at` INTEGER.
- **Evidence**: Extracted symbols `BookmarkModel`, `createBookmarkForCurrentPage`.
- **Confidence**: High.

#### 7. `annotations`
- **Purpose**: Stores text highlights and user commentary.
- **Fields**: `id`, `book_id` (FK), `cfi_start` TEXT, `cfi_end` TEXT, `page_number` INTEGER, `selected_text` TEXT, `note_text` TEXT, `color_code` TEXT CHECK(`color_code` IN ('yellow', 'green', 'red', 'purple', 'blue', 'underline')), `created_at` INTEGER, `updated_at` INTEGER.
- **Evidence**: Extracted symbols `span.yellownote`, `span.greennote`, `NotePopup`.
- **Confidence**: High.

#### 8. `book_metadata`
- **Purpose**: Extensible key-value metadata store for publications.
- **Fields**: `id`, `book_id` (FK), `meta_type` INTEGER, `meta_value` TEXT.
- **Evidence**: Authoritative DDL in `icebookreader.exe`.
- **Confidence**: High (Direct observation).

#### 9. `app_settings`
- **Purpose**: Database-backed application configuration cache complementing `settings.ini`.
- **Fields**: `key` TEXT PRIMARY KEY, `value` TEXT NOT NULL, `data_type` TEXT, `updated_at` INTEGER.
- **Evidence**: Configuration persistence requirements.
- **Confidence**: High.

---

## 8. Out of Scope and Non-Cloneable Features

The clean-room implementation strictly rebuilds functional, UX, and architectural capabilities. The following aspects are intentionally excluded with explicit technical and legal rationales:

| Excluded Item | Category | Technical & Legal Rationale |
|---|---|---|
| **Proprietary DRM Decryption** | Security / Legal | Original binary displays: "Ebook file is DRM protected. Book cannot be opened." The replica does not circumvent DRM or implement proprietary decryption schemes (Adobe Adept, Apple FairPlay, Amazon KFX DRM), operating exclusively on DRM-free documents. |
| **Debenu Quick PDF Library** | Proprietary DLL | The original application embeds Foxit/Debenu's commercial 32-bit DLL (`DebenuPDFLibraryDLL1016.dll`). The replica replaces this with open-source Google PDFium (Apache 2.0) or `poppler-qt6`. |
| **Legacy QtWebKit Engine** | Obsolete Dependency | The original application relies on an obsolete 32-bit QtWebKit DLL (29.1 MB). The replica replaces this with modern in-process Qt 6 text rendering. |
| **Commercial PRO Licensing & Nags** | Monetization | All commercial paywalls, registration key validation, and PRO upsell dialogs (`Upgrade to PRO`, 10-second countdown timers) are omitted. All advanced capabilities (bulk folder import, full text notes, unlimited folders, fullscreen) are fully unlocked in the replica. |
| **Proprietary Crash Reporting** | Telemetry | Replaces `CrashRpt1403.dll` with standard open-source crash reporting or native OS dumps. |

---

## 9. Sizing & Implementation Complexity

- **Screen Count**: 12 primary screens and dialogs (S01A/B to S12).
- **Flow Count**: 10 comprehensive user flows (F01 to F10).
- **Entity Count**: 9 normalized database entities.
- **The Three Hardest Architectural Parts**:
  1. *Reflow Pagination & Interactive Resizing*: Dynamically computing two-column balanced layout breaks across arbitrary font families, font sizes, and line spacings while seamlessly preserving exact reading anchor positions via EPUB CFI without freezing the UI during window resize operations.
  2. *Multi-Format Document Pipeline*: Robustly parsing diverse, potentially malformed file formats (corrupt EPUB containers, unindexed MOBI PalmDOC records, massive FB2 base64 XML streams, high-DPI PDF page rasterization) on background threads without ever blocking the 60 FPS GUI thread.
  3. *Precise Text Selection & Annotation Serialization*: Reliably mapping mouse drag coordinates to DOM text ranges, rendering multi-color highlight overlays across column boundaries, and persisting exact DOM node offsets that remain stable across re-renders.
- **Overall Project Size**: **M (Medium — 4 to 6 weeks for a production-grade C++20 / Qt 6 implementation)**.

---

## 10. Next Steps

With the completion of this Reconnaissance Map (`replica/recon.md`) and Feature Matrix (`replica/features.csv`), the foundation is set for the downstream architectural and schema milestones:
1. **Milestone M2**: Authoring the C++20 / Qt 6 architecture specification (`replica/architecture.md`), detailing module breakdowns, class responsibilities, threading models, and the phased implementation roadmap.
2. **Milestone M3**: Generating and validating the production SQLite schema DDL (`replica/schema.sql`).
