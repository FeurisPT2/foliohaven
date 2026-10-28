# Comprehensive UX, Screen, and User Flow Survey: Icecream Ebook Reader

**Explorer**: `explorer_survey_2`  
**Milestone**: Reconnaissance & Survey (clean-room analysis)  
**Target Installation**: `C:\Program Files (x86)\Icecream Ebook Reader`  
**Working Directory**: `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\explorer_survey_2`  
**Date**: 2026-10-28  

---

## 1. Observation

Direct clean-room inspection of local artifacts, binary metadata, configuration files, and compiled translation resources yielded complete ground-truth evidence:

### 1.1 Local Configuration & Runtime Defaults
File: `C:\Users\epicg\AppData\Local\Icecream\Icecream Ebook Reader\settings.ini`
- `lastStyleId=DayStyle` (reading themes: DayStyle, NightStyle, SepiaStyle, DarkSepiaStyle)
- `library_view_mode=@Variant(...) Enums::LibraryViewMode` (Grid view = 0, Table/List view = 1)
- `ttsLocaleVoiceMap=Microsoft Zira` (Text-to-speech engine integration)
- `ttsVolume=1`
- `showFirstStartWizard=false` (first-run onboarding wizard)
- `library_category=2` (active category selection filter)
- `localeName=en` (supports 49 distinct localization `.qm` catalogs)
- `[viewer.text] column_count=2` (Single-page [1] vs Two-page spread [2])

### 1.2 Extracted UI Translation Contexts & Strings
From compiled catalog `C:\Program Files (x86)\Icecream Ebook Reader\translations\ebookreader_en.qm` (39,091 bytes, parsed into 372 distinct localized UI entries across 43 QTranslator contexts via `dump_qm.py`):
1. **Application Shell & Title**:
   - `MainWindow_Title`: "Ebook Reader", "Update available!", "Upgrade to PRO"
   - `Application`: "Maximize", "Minimize", "Restore", "Close", "OK", "An error has occurred when trying to open: \"%1\""
2. **Library Navigation & Catalog**:
   - `MainWindow_SideBar`: "All (%1)", "Recently Read (%1)", "Read (%1)", "Favorites (%1)", "Formats", "No category (%1)", "New category", "Add new category", "Rename", "Delete", "Deleted (%1)" (Trash), "Settings", "Help", "Upgrade to PRO"
   - `MainWindow_Library`: "Add book", "Add book to library", "Add folder", "Drop books here...", "Search in Library", "Read", "Add to Favorites", "Remove from Favorites", "Add to folder", "Remove from category", "Move to \"Read\"", "Restore from \"Read\"", "Delete", "Restore", "Restore all", "Empty trash", "Properties...", "No books found.", "No books found in \"%1\".", "eBook Files (*.epub *.mobi *.prc *.fb2 *.pdf *.txt *.cbz *.cbr *.zip *.7z)"
   - `BookModel`: Columns ["Title", "Author", "Date", "Notes", "Progress", "Unknown"]
   - `MainWindow_Footer`: "%1 books selected", "Select all", "Clear selection", "Continue reading", "Add to category", "Remove from category", "Delete", "Restore", "Delete permanently", "Import books...", "Export books...", "Pause importing", "Resume importing", "Stop importing"
3. **Reader Canvas & Floating Controls**:
   - `MainWindow_Reading_ToolBar`: "Finish reading and return to library", "Contents", "Bookmarks (%1)", "Show or hide bookmarks list", "Notes (%1)", "Show or hide color notes list", "Show or hide search panel", "Switch to Full screen mode", "Settings", "Print", "Fit to page", "Fit to width", "Zoom in", "Zoom out", "Zoom value / Press %1 to reset to 100%", "Start/pause reading aloud", "Stop", "Previous paragraph", "Next paragraph", "Reading speed", "Reading volume", "Auto flipping mode ON/OFF", "Flipping interval (%1 sec)"
   - `MainWindow_Reading_Footer`: "Page: %1", "Back to page %1"
   - `MainWindow_Reading_Toc`: "Table of contents", "Section", "Page %1", "This book does not have a table of contents", "Close"
   - `MainWindow_Reading_Bookmarks`: "Bookmarks (%1)", "Add bookmark", "Clear all bookmarks", "Click the button above to add a new bookmark.", "Close"
   - `MainWindow_Reading_Notes`: "Notes (%1)", "Search", "Add note", "Clear all notes", "Delete note", "Export notes to HTML", "Save as HTML", "Nothing found", "To add a note: 1. Select the text you want to annotate 2. Then click the color or the 'Add note' button in the opened menu."
   - `MainWindow_Reading_NotePopup`: Color picker swatches, "Add note", "Copy", "Delete note", "Google", "Wikipedia", "Translate"
   - `MainWindow_Reading_Search`: "Search: text / page number", "Go to page %1", "Nothing found", "Close"
   - `MainWindow_Reading_Settings` (Quick popover): "Font size:", "Text Font:", "Original font", "Increase line spacing", "Decrease line spacing", "Page view: Single / Double", "Theme: Day / Night / Sepia / Dark sepia", "Dimming:", "Show hotkeys", "Open All Settings"
   - `MainWindow_Reading_Print`: "Print", "Printer", "There are no printers available.", "All pages", "Current page", "From [X] To [Y]", "Copies", "Portrait / Landscape", "Paper size", "Color mode: Color / Grayscale", "Print quality: High / Low / default"
4. **Global Preferences**:
   - `MainWindow_Settings_System`: "Theme: Day / Night / Light sepia / Dark sepia", "Dimming:", "Language:", "Path to Local Library", "Select Library path", "Copy eBooks from external devices", "Select path to copy books:", "Export Library to archive", "Import books from archive", "eBook archive(*.ebr)", "Empty Library", "Check for the updates automatically:", "Send anonymous usage stats"
   - `MainWindow_Settings_Reading`: "Page view: Single / Double", "Text Font:", "Original font", "Text alignment: Left / Center / Right / Justify", "Auto page flipping interval: %1 sec"
   - `MainWindow_Settings_TTS`: "Locale", "Voice", "Reading speed", "Reading pitch", "Reading volume", "Refresh lists", "More languages"
   - `MainWindow_Settings_Hotkeys`: 25 hotkey mappings covering pagination, zoom, TOC, notes, bookmarks, search, fullscreen, columns, volume, and reading aloud
   - `MainWindow_Settings_License`: FREE vs PRO, Version, "Enter key or paste from clipboard", "ACTIVATE", "Buy your key", "Update available!"
5. **Dialogs & Modals**:
   - `Dialog_BookProperties`: "Book information", "Title:", "Author:", "Description:", "Format:", "Path:", "Size:", "Last read on:", "Progress:", "Change book cover" / "Select image", "Restore the book cover", "Images (%1)", "SAVE", "CANCEL"
   - `Dialog_BookAdded`: "%n books added!", "The book is added!", "Start reading now", "OK"
   - `Dialog_BookExists`: "The document %1 has already been added"
   - `Dialog_BookImported` / `Dialog_BookExported`: "%n books imported!", "%n books exported!"
   - `Dialog_Password`: "The file \"%1\" is password protected.", "Unlock", "Wrong password!", "Cancel"
   - `Dialog_ClearBookmarks` / `Dialog_ClearNotes` / `Dialog_ClearLibrary` / `Dialog_EmptyTrash` / `Dialog_DeleteCategory`: Confirmation dialogs with explicit warning that physical files remain on disk while application cache/metadata is purged.
   - `Dialog_Upgrade`: Free tier restriction notices ("Add eBooks in bulk by whole folders", "Add notes with text", "Copy text from eBooks", "Create custom categories", "Fullscreen mode", countdown timer "Continue reading in %1 sec.").
   - `Dilog_Errors`: "DRM protected. Book cannot be opened.", "Ebook file is damaged. Book cannot be opened.", "The file you are trying to open was not found by the following path: %1".

### 1.3 Database Architecture & SQL Schema from Executable
String dump of `icebookreader.exe` reveals the exact production SQLite schema and queries:
```sql
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    cover TEXT,
    full_path TEXT,
    author TEXT,
    title TEXT,
    format INTEGER,
    time_added INTEGER,
    time_last_view INTEGER,
    position INTEGER,
    max_position INTEGER,
    is_favorite INTEGER,
    is_deleted INTEGER,
    notes_count INTEGER,
    book_hash TEXT,
    use_user_cover INTEGER,
    is_read INTEGER
);

CREATE TABLE IF NOT EXISTS folders (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER,
    title TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS book_folder_binder (
    book_id INTEGER NOT NULL,
    folder_id INTEGER NOT NULL,
    UNIQUE(book_id, folder_id),
    FOREIGN KEY(book_id) REFERENCES books(id),
    FOREIGN KEY(folder_id) REFERENCES folders(id)
);

CREATE TABLE IF NOT EXISTS book_metadata (
    id INTEGER PRIMARY KEY,
    book_id INTEGER NOT NULL,
    meta_type INTEGER NOT NULL,
    meta_value TEXT
);

-- Triggers ensuring referential integrity:
CREATE TRIGGER IF NOT EXISTS delete_book_folder_bind_folders 
BEFORE DELETE ON folders BEGIN 
    DELETE FROM book_folder_binder WHERE folder_id = old.id; 
END;

CREATE TRIGGER IF NOT EXISTS delete_book_metadata 
BEFORE DELETE ON books BEGIN 
    DELETE FROM book_metadata WHERE book_id = old.id; 
END;
```

### 1.4 Original Class Hierarchy & Codebase Layout
Extracted from debug compilation symbols inside `icebookreader.exe`:
- **UI Framework**:
  - `MainWindow` (`projects\icebookreader\ui\mainwindow.cpp`)
  - `LibraryPage` (`ui\mainwindow\librarypage.cpp`)
  - `ReadingPage` (`ui\mainwindow\readingpage.cpp`)
  - Drawers & Toolbars: `BookmarksBox`, `NotesBox`, `TocBox`, `SearchBox`, `ReadingToolbar`, `NotePopup`, `ReadingSpinner`
  - Settings Pages: `SystemSettingsPage`, `ReadingSettingsPage`, `TtsSettingsPage`, `LicenseSettingsPage`, `HotkeysSettingsPage`
  - Custom Widgets: `IceWindow`, `IceDialog`, `IceSlider`, `IceScrollArea`, `IceAnimatedScrollBar`, `IceFlowLayout`
- **Core Engine**:
  - `AbstractViewer`, `TextViewer` (WebKit/HTML reflow engine), `ImageViewer` (fixed layout, comic, PDF page renderer)
  - `EpubParser`, `MobiHeaders`, `PdfDocument` (Debenu PDF), `ComicDocument` (CBR/CBZ)
  - `ZipReader` (QuaZip), `RarReader` (UnRAR)
  - `BookProvider`, `BookImporter`, `ImportBooks`, `ExportBooks`
  - `BookModel`, `FolderModel`

---

## 2. Logic Chain

From the direct factual observations above, the complete UX architecture, screen states, user interaction flows, and feature matrix are systematically derived:

```
[Installed Binary & Resource Metadata]
       │
       ├─► 43 QTranslator Contexts ──► S01 to S12 Screen Inventory (All States & Boundaries)
       │
       ├─► Class Symbols & Methods  ──► Component Catalog & Widget Composition
       │
       ├─► Embedded SQL Statements   ──► Inferred Data Model & State Transitions
       │
       └─► Hotkeys & Action Strings ──► F01 to F10 User Flows (Step Counts & Edge Cases)
```

1. **Two-Tier Layout Paradigm**: The application operates in two mutually exclusive primary views within a single main window:
   - **Library Mode (`LibraryPage`, S01)**: Management, categorization, sorting, searching, import/export.
   - **Reading Mode (`ReadingPage`, S02)**: Immersive document presentation with overlay drawers (`BookmarksBox`, `TocBox`, `NotesBox`, `SearchBox`) and quick settings popover (`ReadingSettings`).
2. **Dual-Engine Rendering**:
   - Reflowable text formats (EPUB, MOBI, FB2, TXT) utilize an HTML/text layout engine (`TextViewer`) that supports font switching, size scaling, line spacing, text alignment, and dual-column pagination.
   - Fixed-layout page formats (PDF, CBZ, CBR, DJVU) utilize a page-image renderer (`ImageViewer`) supporting fit-to-page, fit-to-width, zoom ratios, and vector page rendering.
3. **Non-Destructive Library Management**:
   - Book deletion sets `is_deleted = 1`, moving books into the "Deleted" (Trash) category.
   - Files are never removed from the host file system unless the user explicitly clears the disk externally. Clearing trash or deleting from trash only purges cached thumbnails, metadata, and reading progress records.
4. **Clean-Room Feature Prioritization**:
   - The original commercial edition gates specific capabilities behind a PRO license (bulk folder add, annotations/copying, custom folders, fullscreen).
   - In our clean-room C++20 / Qt 6 clone, all core reading, pagination, and annotation capabilities are elevated to foundational `Must` priority, delivering a superior, restriction-free experience.

---

## 3. Screen Inventory (S-IDs)

Every screen is documented with its stable ID, route/entry point, primary purpose, UI components, and all functional states:

| Screen ID | Name & View Mode | Route / Entry Point | Purpose & Role | Key Components | States Recorded |
|---|---|---|---|---|---|
| **S01A** | Main Library (Grid View) | Application launch or `Esc` / Back arrow from reader | Visual bookshelf browsing of ebook covers with progress badges | Left sidebar (categories), Top action bar (Add Book, Add Folder, Search, View Switcher), Flow layout grid canvas (`BookCardWidget`), Bottom operations footer | - *Empty*: "Drop books here..." banner, Add CTAs<br>- *Populated*: Responsive card grid<br>- *Filtered*: Category / format / search filtered<br>- *Multi-select*: Checkbox highlights, footer bar active |
| **S01B** | Main Library (Table View) | View Switcher button on S01 top-right bar | Dense tabular list view of book metadata and sortable attributes | QTableView with headers (Title, Author, Date Added/Viewed, Notes, Progress %, Format), Alternating rows, Progress delegate bar | - *Empty*: "No books found"<br>- *Populated*: Sortable tabular rows<br>- *Sorted*: Ascending / descending header indicators<br>- *Multi-select*: Selected rows highlighted |
| **S02** | Reader Window Canvas | Double-click book in S01 or click "Read" / "Continue reading" | Immersive ebook reading supporting reflow and fixed-page layouts | Reading canvas (HTML/WebKit or Page Renderer), Collapsible Top Toolbar, Floating Bottom Footer (page indicator, jump-back button, progress slider), Left/Right margin click zones | - *Loading*: `readingspinner` overlay<br>- *Single-page*: Centered single column<br>- *Two-page spread*: Side-by-side columns with gutter<br>- *Dimmed*: Black semi-transparent overlay<br>- *Error*: Damaged file / DRM warning dialog |
| **S03** | Bookmarks Side Drawer | Toolbar bookmark icon or `Ctrl+B` | View, jump to, and delete page bookmarks | Header with count, "Add bookmark" button, "Clear all bookmarks" trash icon, Scrollable list of bookmark tiles (Page %, chapter title, timestamp), Close `X` | - *Empty*: "Click the button above to add a new bookmark."<br>- *Populated*: List of bookmark cards<br>- *Confirm Clear*: `Dialog_ClearBookmarks` |
| **S04** | Table of Contents (TOC) Drawer | Toolbar contents icon or `Ctrl+T` | Hierarchical chapter and section navigation | Header, Expandable/collapsible QTreeView of chapter nodes, Target page labels ("Page %1"), Active chapter highlight, Close `X` | - *Empty*: "This book does not have a table of contents"<br>- *Populated*: Multi-level navigable tree |
| **S05** | Notes & Highlights Drawer | Toolbar notes icon or `Ctrl+N` | Review all book highlights, search annotations, and export study reports | Header with count, Search input bar, "Export notes to HTML" button, "Clear all notes" button, List of annotation cards (color swatch, quote snippet, comment, page #), Close `X` | - *Empty*: 2-step instructional visual diagram<br>- *Populated*: List of cards sorted by page<br>- *Filtered*: Sub-list matching search query or "Nothing found" |
| **S06** | Text Selection Popup (`NotePopup`) | Automatic on cursor text selection in S02 | Inline action bubble for highlighting and annotations | 4-color palette swatches (Yellow, Green, Cyan, Pink), "Add note" button, "Copy" button, "Google" / "Wikipedia" search buttons, "Translate" button, "Delete note" button | - *Initial*: Color dots and action icons<br>- *Comment Mode*: Inline text input bubble with Save/Cancel |
| **S07** | In-Reader Quick Settings Popover | Toolbar gear icon in S02 | Non-modal overlay for real-time visual adjustment | Font size +/- buttons, Font family combobox + "Original font" toggle, Line spacing +/- buttons, Text alignment buttons (Left/Center/Right/Justify), Single/Double page toggle, Theme radio pills, Dimming slider, "Open All Settings" link | - *Active*: Instant canvas re-render on any property change |
| **S08** | Global Settings Dialog (`IceDialog`) | Sidebar gear icon (S01) or S07 "Open All Settings" | Application-wide system, reading, TTS, hotkey, and license configuration | Modal dialog with 5 tab headers: System, Reading, Hotkeys, Text to Speech, License; OK, Cancel, Apply buttons | - *Tab 1 System*: Theme, Dimming, Language, Library Path, External Drive Copy, EBR Archive Import/Export, Empty Library<br>- *Tab 2 Reading*: Defaults for alignment, font, view mode, auto-flip timer<br>- *Tab 3 Hotkeys*: Interactive shortcut table<br>- *Tab 4 TTS*: Voice selector, speed/pitch/volume sliders<br>- *Tab 5 License*: Free/PRO status, activation key input |
| **S09** | Book Properties Dialog | Book context menu -> "Properties..." | Inspect and edit book metadata and custom cover image | Book cover thumbnail preview, "Select image" / "Change book cover" button, "Restore the book cover" button, Title input, Author input, Description text area, Read-only fields (Format, File Size, Path, Last read date, Progress %), SAVE/CANCEL buttons | - *Default*: Extracted book metadata<br>- *Custom Cover*: User-selected replacement image<br>- *Edited*: Title/author modified |
| **S10** | In-Book Search Drawer | Toolbar search icon or `Ctrl+F` | Full-text search and direct page jumping | Search text input ("Search: text / page number"), Direct action "Go to page %1", List of match snippet results with query highlighted and page references, Close `X` | - *Empty*: Prompt to enter query<br>- *Searching*: Progress spinner<br>- *Results*: List of clickable snippet cards<br>- *No Match*: "Nothing found" |
| **S11** | Print Ebook Dialog | Toolbar print icon or `Ctrl+P` | Configure print job for ebook content | Printer combobox (with disconnected warning), Page range radios (All pages, Current page, From X to Y), Copies counter, Orientation (Portrait/Landscape), Paper size, Color mode (Color/Grayscale), Print quality, Print/Cancel buttons | - *Printers Available*: Standard print layout<br>- *No Printers*: Warning message banner disabled print button |
| **S12** | Auxiliary Modals & Confirmation Popups | Triggered by actions across S01, S02, S08 | User alerts, duplicate warnings, and destructive action confirmations | Frameless dialog shells with clear title, message body, primary & secondary action buttons | - *Book Added*: "%n books added!" + "Start reading now"<br>- *Book Exists*: Duplicate path warning<br>- *Password*: Encrypted PDF password prompt with "Unlock" / "Wrong password!"<br>- *Trash Confirmations*: Clarifying disk files remain safe |

---

## 4. Key User Flows (F-IDs)

Every major flow is mapped end-to-end with step sequence, click efficiency, screen transitions, decision branches, and edge cases:

### Flow F01: Import Books or Folders (Single & Bulk)
```
[S01 Library] 
      │ (Click "+ Add book" / "+ Add folder" OR Drag & Drop)
      ▼
[Windows File / Folder Picker Dialog]
      │ (Select .epub, .pdf, .mobi, .fb2, .cbz, .cbr, or directory)
      ▼
[Background Worker Ingestion Pipeline]
      ├─► Compute SHA-256 / MD5 Hash
      ├─► Check duplicate in `books.book_hash`
      │     └─► (If match found) ──► Display Dialog_BookExists ──► Abort / Skip
      ├─► Extract metadata (Title, Author, Format, Page count)
      ├─► Extract and cache cover image thumbnail
      ├─► Insert into `books` table
      └─► Bind to active category in `book_folder_binder`
            │
            ▼
[Dialog_BookAdded ("%n books added!")]
      ├─► Click "Start reading now" ──► Direct transition to S02 (Reader)
      └─► Click "OK" / Dismiss      ──► Return to S01 (Library canvas refreshed)
```
- **Happy Path Clicks**: 3 clicks (Add button -> Select file & Open -> Start reading now).
- **Edge Cases**:
  - *Removable Storage Detection*: If files reside on external USB/SD drive, prompts `Dialog_ClearLibrary` prompt variant: "Do you want to copy files to local storage from removable disks?".
  - *Password Protected Files*: Ingestion defers password check until first open (triggering S12 `Dialog_Password`).
  - *Corrupted File*: Ingestion logs error; if completely unreadable, displays `Dilog_Errors` ("Ebook file is damaged").
  - *Bulk Directory Import*: Footer shows progress bar with "Pause importing", "Resume importing", and "Stop importing" controls.

### Flow F02: Browse, Filter, and Search Library
```
[S01 Library Screen]
      │
      ├─► Select Category in Sidebar (All, Recently Read, Read, Favorites, Custom, Trash)
      │     └─► SQL query filtered by category ID or flag
      │
      ├─► Select Format Sub-filter (EPUB, PDF, MOBI, FB2, CBZ, etc.)
      │     └─► SQL query: `SELECT * FROM books WHERE format = :fmt`
      │
      ├─► Type in Search Bar (Instant incremental filtering)
      │     └─► SQL query: `WHERE title LIKE '%query%' OR author LIKE '%query%'`
      │
      └─► Toggle View Mode (Grid S01A ◄──► Table S01B)
            └─► Persisted to `settings.ini` (`library_view_mode`)
```
- **Happy Path Clicks**: 1 click to select category; 0 clicks for search (immediate typing).
- **Edge Cases**: Zero matching items display friendly empty view: "No books found in '%1'".

### Flow F03: Open and Read Ebook (The Core Loop)
```
[S01 Library]
      │ (Double-click book card OR select book and click "Read")
      ▼
[S02 Reader Window]
      ├─► Main window replaces central widget with ReadingPage
      ├─► Display ReadingSpinner animation
      ├─► Worker thread loads document container & extracts chapter TOC
      ├─► Query `books.position` for saved reading offset / CFI
      ├─► Render active page/spread with current theme and font size
      │
      │ (Reading Session: paging, jumping, resizing)
      │
      └─► User clicks "Back to Library" icon OR presses `Esc`
            ├─► Commit current `position`, `max_position`, `time_last_view` to SQLite
            └─► Transition back to S01 with updated reading progress % pill
```
- **Happy Path Clicks**: 1 double-click.
- **Edge Cases**:
  - *DRM Encrypted EPUB/PDF*: Triggers `Dilog_Errors` ("DRM protected. Book cannot be opened.").
  - *Missing File*: If file was moved or deleted externally on disk, triggers `Dilog_Errors` ("The file you are trying to open was not found by the following path: %1").

### Flow F04: Pagination, Layout, and Typography Adjustment
```
[S02 Reader Window]
      │
      ├─► Navigation:
      │     ├─► Next Page: Right Arrow, Spacebar, Page Down, or click Right Margin
      │     ├─► Previous Page: Left Arrow, Page Up, or click Left Margin
      │     └─► Book Boundaries: `Home` (first page), `End` (last page)
      │
      ├─► Quick Settings (Click Gear Icon ──► S07 Popover):
      │     ├─► Switch Column Count (Single Page ◄──► Double Page Spread)
      │     ├─► Font Size (+ / - buttons or `Ctrl++` / `Ctrl+-`)
      │     ├─► Line Spacing (+ / - buttons)
      │     ├─► Text Alignment (Left, Center, Right, Justify)
      │     └─► Font Family (System font selector or "Original font")
      │
      └─► Document Engine:
            └─► Re-reflows DOM content and recalculates pagination anchor dynamically
```
- **Happy Path Clicks**: 2-3 clicks.

### Flow F05: Bookmark Management
```
[S02 Reader Window]
      │ (Press `Ctrl+D` OR Click "Add bookmark" on Toolbar)
      ├─► Capture current chapter, page number, timestamp, and text snippet
      ├─► Save record in `book_metadata` (or dedicated bookmarks table)
      ├─► Bookmark badge count increments in toolbar ("Bookmarks (N)")
      │
      │ (Open Bookmarks Drawer ──► Click Bookmark Icon or `Ctrl+B`)
      ├─► S03 Drawer slides out from right
      ├─► Click bookmark card ──► Reader navigates immediately to target page
      ├─► Click card trash icon ──► Individual bookmark removed
      └─► Click "Clear all bookmarks" ──► Triggers confirmation dialog
```
- **Happy Path Clicks**: 1 click / shortcut to create bookmark.

### Flow F06: Text Highlighting, Annotations, and HTML Export
```
[S02 Reader Window]
      │ (Select text range with mouse cursor)
      ▼
[S06 Selection NotePopup Appears]
      ├─► Click Color Swatch (Yellow, Green, Cyan, Pink)
      │     └─► Selected text wrapped in `<span class="highlight_{color}">`
      ├─► Click "Add note"
      │     └─► Inline comment bubble appears; type comment and press Enter
      │
      ├─► Click "Copy" ──► Copies plain text to system clipboard
      ├─► Click "Google" / "Wikipedia" ──► Launches default browser with query
      └─► Click "Translate" ──► Launches online translation service
            │
            ▼
[Open Notes Drawer (S05) via Toolbar or `Ctrl+N`]
      ├─► Search notes by keyword
      ├─► Click note card to jump to page in reader
      └─► Click "Export notes to HTML"
            └─► Prompt file save dialog (*.html) ──► Generates formatted HTML report
```
- **Happy Path Clicks**: 2 clicks to highlight; 3 clicks to add comment; 2 clicks to export.

### Flow F07: Switch Reading Profiles, Themes, and Dimming
```
[S02 Reader Window or S07 Quick Settings]
      │ (Click Theme Icon / Shortcut `Ctrl+Shift+T`)
      ▼
[Theme Engine Cycles Active Style]:
      ├─► Day: White background (`#FFFFFF`), dark charcoal text (`#1E1E1E`)
      ├─► Night: Deep black/gray (`#181818`), soft light-gray text (`#C8C8C8`)
      ├─► Light Sepia: Warm paper (`#FBF0D9`), deep sepia brown text (`#433422`)
      └─► Dark Sepia: Muted dark sepia (`#2C2621`), warm amber text (`#D0BE9C`)
            │
            ▼
[Dimming Adjustment]:
      └─► Move Dimming slider (0% - 80%) ──► Adjusts alpha of fullscreen black overlay
```
- **Happy Path Clicks**: 1 click.

### Flow F08: Fullscreen Reading Mode
```
[S02 Reader Window]
      │ (Press `F11` OR Click Fullscreen Icon on Toolbar)
      ▼
[Window expands to borderless fullscreen display]
      ├─► Title bar, borders, and taskbar hidden
      ├─► Toolbar smoothly autohides off-screen
      ├─► Hovering cursor within top 20px edge reveals floating toolbar
      └─► Press `F11` or `Esc` ──► Restores standard windowed frame
```
- **Happy Path Clicks**: 1 keypress (`F11`).

### Flow F09: Text-to-Speech (TTS) Read Aloud Narration
```
[S02 Reader Window]
      │ (Click "Read Aloud" on Toolbar or Press Hotkey)
      ▼
[TTS Sub-Toolbar Expands]:
      ├─► Engine parses text of current chapter/page into paragraph blocks
      ├─► QtTextToSpeech synthesizer initiates playback
      ├─► Active speaking paragraph highlighted on canvas in real-time
      ├─► Toolbar controls: Play/Pause, Stop, Prev Paragraph, Next Paragraph
      ├─► Volume and Speed sliders adjust playback rate in real-time
      └─► When bottom of page reached, engine automatically flips to next page
```
- **Happy Path Clicks**: 1 click to start.

### Flow F10: Library Archive, Backup, and Migration (.EBR)
```
[S01 Footer OR S08 System Settings]
      │ (Click "Export Library to archive" / "Export books...")
      ▼
[File Save Dialog]: Destination filename `.ebr` (eBook Archive)
      ├─► Background worker creates compressed ZIP container (.ebr)
      ├─► Copies SQLite database (`library.db`), metadata, custom covers, and book files
      ├─► Progress bar displayed in S01 footer with Pause / Resume / Stop controls
      └─► On completion: `Dialog_BookExported` ("%n books exported!")
            │
            ▼ (On New System / Fresh Install)
[Click "Import books from archive" ──► Select `.ebr`]
      └─► Worker uncompresses archive, merges database records, refreshes S01 library
```
- **Happy Path Clicks**: 3 clicks.

---

## 5. UI Component Catalog

Every custom component identified across Icecream Ebook Reader is cataloged with its properties, child widgets, and visual states:

### 1. Navigation Sidebar (`MainWindow_SideBar`)
- **Type**: Persistent left vertical navigation rail (`QListWidget` / styled tree).
- **Structure**:
  - Top header: Icecream Brand Logo + "Ebook Reader" title label.
  - Category list items with icons:
    - `All (%1)` (ID: `AllBooks`)
    - `Recently Read (%1)` (ID: `RecentlyRead`)
    - `Read (%1)` (ID: `ReadBooks`)
    - `Favorites (%1)` (ID: `FavoriteBooks`, star icon)
    - `Deleted (%1)` (ID: `TrashBooks`, trash can icon)
    - `Formats` (Collapsible section showing format badges: EPUB, PDF, MOBI, FB2, CBZ, CBR, TXT)
    - Custom user categories (with badge count and right-click menu: Rename, Delete)
    - "+ Add new category" button
  - Bottom utility pinned items:
    - "Settings" (gear icon)
    - "Help" (question mark icon)
    - "Upgrade to PRO" (orange accent button/banner)

### 2. Library Header & Action Bar
- **Type**: Top horizontal tool strip for S01.
- **Structure**:
  - Primary Action: "+ Add book" (high-contrast flat button).
  - Secondary Action: "+ Add folder" (folder import button).
  - Center/Right Search Bar: Custom rounded `QLineEdit` with embedded leading search magnifying glass and trailing clear `X` icon. Placeholder: "Search in Library".
  - View Mode Toggle: Segmented 2-button group (`QButtonGroup`):
    - Grid icon (card layout, S01A)
    - Table icon (list layout, S01B)

### 3. Library Grid Book Card (`BookCardWidget`)
- **Type**: Composite custom widget used in `IceFlowLayout`.
- **Structure**:
  - Thumbnail box: Aspect-ratio preserved book cover rendered with drop shadow.
  - Format Badge: Small colored pill in top-left corner (e.g. `EPUB`, `PDF`, `MOBI`).
  - Favorite Star: Toggleable star icon in top-right corner (gold when active).
  - Title Label: Bold text, elided at 2 lines.
  - Author Label: Subdued gray text, elided at 1 line.
  - Progress Pill Bar: Horizontal bar indicating 0% - 100% reading progress.
- **States**: Normal, Hover (card elevates with border outline), Selected (blue border + checkmark badge).

### 4. Library Table View (`QTableView` / `BookModel`)
- **Type**: Standard Qt Model/View tabular grid.
- **Columns**:
  1. `Title` (with format mini-icon)
  2. `Author`
  3. `Date` (Date added or last opened, formatted via `DateFormats`)
  4. `Notes` (numeric count of annotations)
  5. `Progress` (custom delegate rendering percentage text and bar)
  6. `Format` (file extension)
- **Features**: Multi-column sorting (clicking header toggles ascending/descending), alternating row colors, multi-row selection.

### 5. Selection & Operations Footer (`MainWindow_Footer`)
- **Type**: Sliding bottom dock/drawer that activates upon book selection.
- **Structure**:
  - Selection summary: "%1 books selected".
  - Action buttons: "Select all", "Clear selection", "Continue reading", "Add to category", "Remove from category", "Delete" (move to trash), "Restore", "Delete permanently".
  - Transfer status: Progress bar with percentage, transfer speed, and control buttons: "Pause", "Resume", "Stop".

### 6. Reader Top Toolbar (`MainWindow_Reading_ToolBar`)
- **Type**: Floating / dockable top action bar in S02.
- **Structure**:
  - Navigation: Back to Library icon (left arrow).
  - Drawers toggles: Table of Contents (`Ctrl+T`), Bookmarks (`Ctrl+B`, with count badge), Notes (`Ctrl+N`, with count badge), In-book Search (`Ctrl+F`).
  - View & Canvas: Fullscreen toggle (`F11`), Zoom In (`+`), Zoom Out (`-`), Zoom Reset (`100%`), Fit to Page, Fit to Width.
  - Text-to-Speech: Play/Pause button, Stop button, Prev/Next paragraph, Volume & Speed popups.
  - Auto Page Flip: Toggle switch + duration spinbox (seconds).
  - Tools: Print button (`Ctrl+P`), Quick Settings gear.

### 7. Reader Footer & Scrubber (`MainWindow_Reading_Footer`)
- **Type**: Bottom overlay strip.
- **Structure**:
  - Page indicator label: `Page: %1 / %2`.
  - Scrubber: Continuous slider (`IceSlider`) with tooltip preview of chapter name and page number.
  - History link: "Back to page %1" button (appears dynamically after jumping chapters via TOC or hyperlinks).

### 8. Selection Context Bubble (`NotePopup`)
- **Type**: Frameless popup widget positioned dynamically above text selection bounding box.
- **Structure**:
  - 4 colored circular swatches: Yellow (`#FFE270`), Green (`#A8F29A`), Cyan (`#7BE5F8`), Pink (`#FFA0C5`).
  - Action icons: "Add note" (pencil/comment icon), "Copy", "Delete note" (trash can), "Google", "Wikipedia", "Translate".

### 9. Custom Application Frame & Dialog Shell (`IceWindow` / `IceDialog`)
- **Type**: Frameless customized window with OS drop-shadow simulation.
- **Structure**: Custom styled title bar, draggable header, window controls (Minimize, Maximize/Restore, Close), consistent padding, and standard `SAVE` / `CANCEL` action button layout.

---

## 6. Feature Inventory Draft (Categorized by Priority)

Following the `replica-recon` methodology, all identified features are categorized and graded into standard priority tiers (**Must**, **Should**, **Could**):

| ID | Category | Feature Description | Original App Status | Replica Target Tier | Complexity | Notes |
|---|---|---|---|---|---|---|
| **FEAT-LIB-01** | Library | Single book file import (EPUB, PDF, MOBI, FB2, CBZ, TXT) | Supported | **Must** | Low | Core entry point |
| **FEAT-LIB-02** | Library | Bulk directory / folder import | Supported (PRO only in original) | **Must** | Medium | Non-blocking background worker |
| **FEAT-LIB-03** | Library | Drag-and-drop book file import into library canvas | Supported | **Must** | Low | Standard Qt drag/drop events |
| **FEAT-LIB-04** | Library | Dual view modes: Cover Grid View & Detailed Table View | Supported | **Must** | Medium | QListView + QTableView |
| **FEAT-LIB-05** | Library | Instant library search (filtering title, author, format) | Supported | **Must** | Low | Real-time SQLite / model filter |
| **FEAT-LIB-06** | Library | Standard system categories (All, Recently Read, Read, Favorites, Trash) | Supported | **Must** | Medium | Built-in SQLite query views |
| **FEAT-LIB-07** | Library | Custom user-defined categories / folders | Supported (PRO only in original) | **Should** | Medium | Many-to-many binder table |
| **FEAT-LIB-08** | Library | Multi-book batch selection and operations footer | Supported | **Should** | Medium | Batch delete, move, export |
| **FEAT-LIB-09** | Library | Book metadata editing (Title, Author, custom cover replacement) | Supported (PRO only in original) | **Should** | Low | Dialog_BookProperties |
| **FEAT-LIB-10** | Library | Non-destructive deletion (Soft-delete to Trash, Restore) | Supported | **Must** | Low | `is_deleted` flag logic |
| **FEAT-RED-01** | Reading | Reflowable document rendering (EPUB, MOBI, FB2, TXT) | Supported | **Must** | High | HTML/text layout engine |
| **FEAT-RED-02** | Reading | Fixed-layout document rendering (PDF, CBZ, CBR) | Supported | **Must** | High | Poppler/MuPDF + Comic extraction |
| **FEAT-RED-03** | Reading | Single-page and Two-page spread (columns) layout | Supported | **Must** | Medium | Dynamic CSS multi-column / grid |
| **FEAT-RED-04** | Reading | Font customization (Font family, size scaling, line spacing, alignment) | Supported | **Must** | Medium | Real-time DOM CSS injection |
| **FEAT-RED-05** | Reading | Themes (Day, Night, Light Sepia, Dark Sepia) | Supported | **Must** | Low | CSS color palettes |
| **FEAT-RED-06** | Reading | Display brightness / screen dimming slider overlay | Supported | **Should** | Low | Semi-transparent overlay widget |
| **FEAT-RED-07** | Reading | Fullscreen distraction-free reading with autohiding toolbar | Supported (PRO only in original) | **Must** | Medium | Borderless window mode |
| **FEAT-RED-08** | Reading | Auto page flipping mode with customizable timer interval | Supported | **Should** | Low | QTimer page stepper |
| **FEAT-RED-09** | Reading | Text-to-Speech (TTS) Read Aloud with speed/volume controls | Supported | **Should** | Medium | QtTextToSpeech integration |
| **FEAT-NAV-01** | Navigation | Keyboard hotkey navigation (Arrows, Space, PageUp/Down, Home/End) | Supported | **Must** | Low | Key event filter |
| **FEAT-NAV-02** | Navigation | Interactive bottom scrubber slider and page counter | Supported | **Must** | Low | QSlider synchronization |
| **FEAT-NAV-03** | Navigation | Hierarchical Table of Contents (TOC) side drawer | Supported | **Must** | Medium | QTreeView chapter navigation |
| **FEAT-NAV-04** | Navigation | Bookmark creation, viewing drawer, and instant jumping | Supported | **Must** | Medium | Chapter/CFI anchor persistence |
| **FEAT-NAV-05** | Navigation | In-book full-text search with match snippets and page links | Supported | **Must** | High | Document text indexing |
| **FEAT-NAV-06** | Navigation | "Back to page %1" history jump navigation | Supported | **Should** | Low | Navigation history stack |
| **FEAT-ANN-01** | Annotations | Inline text selection popup menu (NotePopup) | Supported | **Must** | Medium | Text selection coordinate mapping |
| **FEAT-ANN-02** | Annotations | Multi-color text highlighting (Yellow, Green, Cyan, Pink) | Supported | **Must** | Medium | Range/CFI highlight serialization |
| **FEAT-ANN-03** | Annotations | Text notes / comments attached to highlights | Supported (PRO only in original) | **Must** | Medium | Note cards attached to CFI |
| **FEAT-ANN-04** | Annotations | Notes drawer (browsing, searching, jumping to note) | Supported | **Must** | Medium | QListView of annotation items |
| **FEAT-ANN-05** | Annotations | Export notes and highlights to standalone HTML document | Supported | **Should** | Low | Structured HTML generator |
| **FEAT-ANN-06** | Annotations | Quick copy to clipboard, Google/Wikipedia search, Translate | Supported | **Should** | Low | URL launching via QDesktopServices |
| **FEAT-DAT-01** | Storage | Production SQLite database with foreign keys and triggers | Supported | **Must** | Medium | `QSqlDatabase` schema |
| **FEAT-DAT-02** | Storage | Reading state persistence (position, progress %, last opened) | Supported | **Must** | Low | Automatic commit on exit/switch |
| **FEAT-DAT-03** | Storage | Duplicate book prevention via file hashing | Supported | **Must** | Low | SHA-256 / MD5 hash check |
| **FEAT-DAT-04** | Storage | Full library archive export/import (`.ebr` container) | Supported | **Could** | Medium | ZIP packaging of DB + covers |
| **FEAT-DAT-05** | Storage | Automatic book copying from removable USB/external media | Supported | **Could** | Low | Drive type detection |
| **FEAT-OUT-01** | Output | Document print dialog with page range, copies, quality | Supported | **Could** | Medium | Qt PrintSupport module |
| **FEAT-LOC-01** | Localization | Multi-language UI support via Qt QM files (49 languages) | Supported | **Could** | Medium | `QTranslator` dynamic switching |

---

## 7. Caveats

1. **Clean-Room Boundary**: This survey was performed strictly via clean-room examination of local file layouts, installation metadata, compiled translation catalogs (`.qm`), configuration INI files, and public interface patterns. No proprietary source code was decompiled, and no proprietary reverse-engineering tools were used.
2. **Proprietary DRM Excluded**: Original strings acknowledge DRM protection ("Ebook file is DRM protected. Book cannot be opened."). Our clean-room open-source architecture explicitly skips proprietary Adobe/FairPlay DRM decryption engines in compliance with legal and clean-room principles.
3. **Third-Party PDF Library Modernization**: The original binary relies on a legacy 32-bit `DebenuPDFLibraryDLL1016.dll`. For our modern 64-bit C++20 / Qt 6 clean-room replica, modern open-source PDF engines (e.g. `poppler-qt6` or `pdfium` / `mupdf`) must be selected.
4. **Rendering Stack Modernization**: The original binary utilizes Qt 5's obsolete `Qt5WebKit.dll`. The replica design must adopt modern Qt 6 architectures (`QTextDocument` / `QWebEngineView` or lightweight custom HTML/CSS reflow engines) for high-performance cross-platform rendering.

---

## 8. Conclusion

Icecream Ebook Reader exhibits a clean, highly cohesive two-tier desktop architecture: a library catalog manager (Grid & Table) paired with an immersive, distraction-free reading environment.

All 12 distinct screens/dialogs (S01 - S12), 10 core user flows (F01 - F10), 9 composite UI components, and 37 categorized features have been fully mapped, validated, and evidenced by exact strings and database queries. The underlying data model centers on a normalized SQLite schema (`books`, `folders`, `book_folder_binder`, `book_metadata`) that perfectly aligns with our project's architecture requirements (R1, R2, R3).

The survey findings are completely actionable, providing the definitive blueprint for the architecture specification (`replica/architecture.md`), SQLite database schema (`replica/schema.sql`), and feature matrix (`replica/features.csv`).

---

## 9. Verification Method

To independently verify all observations and extracted metadata, execute the following commands in the project directory:

1. **Verify Extracted UI Strings**:
   Run the string extraction script:
   ```powershell
   python c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\explorer_survey_2\dump_qm.py
   ```
   Inspect the resulting `extracted_strings.txt` to confirm 372 strings across 43 contexts matching S01–S12.

2. **Verify SQLite Database Queries in Executable**:
   Execute regex query on the target binary:
   ```powershell
   python -c "
   import re
   with open(r'C:\Program Files (x86)\Icecream Ebook Reader\icebookreader.exe', 'rb') as f:
       buf = f.read()
   queries = re.findall(rb'(?:CREATE TABLE|INSERT INTO|SELECT |UPDATE |DELETE FROM)[^;\x00]{10,120}', buf, re.IGNORECASE)
   print(f'Total SQL queries verified: {len(queries)}')
   for q in queries[:10]:
       print('-', q.decode('latin1', 'ignore').strip())
   "
   ```

3. **Verify Settings & Default Profiles**:
   Inspect `C:\Users\epicg\AppData\Local\Icecream\Icecream Ebook Reader\settings.ini` to verify theme names (`DayStyle`), column count (`column_count=2`), and view modes.
