# Clean-Room Technical Survey Report: Icecream Ebook Reader (v6.56)

**Target Installation Path**: `C:\Program Files (x86)\Icecream Ebook Reader`  
**Date of Investigation**: 2026-10-28  
**Investigator**: `explorer_survey_1` (Teamwork Explorer)  
**Target Architecture**: 32-bit x86 Windows Desktop Application  
**Primary Binary**: `icebookreader.exe` (Version 6.0.0.0 / Installer Product Version 6.56)  

---

## 1. Observation

### 1.1 Installation Directory Hierarchy & File Breakdown
The target installation directory contains **84 files** and **9 subdirectories**, occupying approximately 111 MB on disk:

```
C:\Program Files (x86)\Icecream Ebook Reader\
├── 7zxa.dll (256,200 bytes)
├── API-MS-Win-core-*.dll (17 files, Windows API forwarders)
├── api-ms-win-crt-*.dll (14 files, Universal C Runtime)
├── concrt140.dll (243,576 bytes, MSVC Concurrency Runtime)
├── CrashRpt1403.dll (116,936 bytes, CrashRpt v1.4.0.3)
├── DebenuPDFLibraryDLL1016.dll (6,084,144 bytes, Debenu Quick PDF Library v10.16.0.0)
├── icebookreader.exe (3,309,024 bytes, main executable)
├── icebooksvc.exe (80,864 bytes, pagination & helper process)
├── icudt65.dll (27,986,040 bytes, ICU data v65.1)
├── icuin65.dll (2,073,208 bytes, ICU I18N v65.1)
├── icuuc65.dll (1,369,720 bytes, ICU Common v65.1)
├── libcrypto-1_1.dll (2,533,224 bytes, OpenSSL 1.1.1p)
├── libcurl.dll (453,320 bytes, libcurl 7.87.0-DEV)
├── libssl-1_1.dll (541,544 bytes, OpenSSL 1.1.1p)
├── libxml2.dll (1,011,320 bytes, libxml2 v2.9.10)
├── libxslt.dll (167,032 bytes, libxslt)
├── msvcp140.dll (436,616 bytes, MSVC 2019 v14.29.30135.0)
├── msvcp140_1.dll (21,384 bytes, MSVC 2019)
├── Qt5Core.dll (5,377,144 bytes, Qt 5.15.1.0)
├── Qt5Gui.dll (5,929,592 bytes, Qt 5.15.1.0)
├── Qt5Network.dll (1,062,520 bytes, Qt 5.15.1.0)
├── Qt5Positioning.dll (264,824 bytes, Qt 5.15.1.0)
├── Qt5PrintSupport.dll (266,872 bytes, Qt 5.15.1.0)
├── Qt5Qml.dll (3,162,744 bytes, Qt 5.15.1.0)
├── Qt5QmlModels.dll (354,424 bytes, Qt 5.15.1.0)
├── Qt5Quick.dll (3,535,992 bytes, Qt 5.15.1.0)
├── Qt5Sensors.dll (165,496 bytes, Qt 5.15.1.0)
├── Qt5Sql.dll (161,912 bytes, Qt 5.15.1.0)
├── Qt5Svg.dll (264,312 bytes, Qt 5.15.1.0)
├── Qt5TextToSpeech.dll (41,080 bytes, Qt 5.15.1.0)
├── Qt5WebChannel.dll (110,200 bytes, Qt 5.15.1.0)
├── Qt5WebKit.dll (29,102,200 bytes, QtWebKit for Qt 5.15)
├── Qt5WebKitWidgets.dll (200,312 bytes, QtWebKitWidgets)
├── Qt5WebSockets.dll (133,752 bytes, Qt 5.15.1.0)
├── Qt5Widgets.dll (4,483,704 bytes, Qt 5.15.1.0)
├── Qt5WinExtras.dll (433,272 bytes, Qt 5.15.1.0)
├── Qt5Xml.dll (173,176 bytes, Qt 5.15.1.0)
├── quazip.dll (152,424 bytes, QuaZip ZIP wrapper)
├── ucrtbase.dll (1,170,904 bytes, Windows UCRT)
├── unins000.dat (45,158 bytes, Inno Setup 5.5.1 data)
├── unins000.exe (946,006 bytes, Inno Setup 5.5.1 uninstaller)
├── unrar.dll (327,824 bytes, UnRAR v7.11.1)
├── vccorlib140.dll (267,640 bytes, MSVC 2019)
├── vcruntime140.dll (76,152 bytes, MSVC 2019)
├── iconengines\
│   └── qsvgicon.dll (54,984 bytes, Qt SVG icon engine)
├── icons\
│   ├── cbr.ico (370,070 bytes)
│   ├── cbz.ico (370,070 bytes)
│   ├── djvu.ico (370,070 bytes)
│   ├── epub.ico (370,070 bytes)
│   ├── fb2.ico (370,070 bytes)
│   └── mobi.ico (370,070 bytes)
├── imageformats\ (9 plugins: qgif.dll, qicns.dll, qico.dll, qjpeg.dll, qsvg.dll, qtga.dll, qtiff.dll, qwbmp.dll, qwebp.dll)
├── platforms\
│   └── qwindows.dll (1,248,888 bytes, Qt Windows QPA)
├── printsupport\
│   └── windowsprintersupport.dll (43,640 bytes)
├── sqldrivers\
│   └── qsqlite.dll (1,149,048 bytes, Qt SQLite driver)
├── styles\
│   └── qwindowsvistastyle.dll (132,216 bytes)
├── texttospeech\
│   └── qtexttospeech_sapi.dll (43,592 bytes, Windows SAPI TTS)
└── translations\
    └── 49 compiled Qt translation files (.qm): ebookreader_en.qm, ebookreader_de.qm, ebookreader_fr.qm, ebookreader_es.qm, etc.
```

### 1.2 Executables & Processes
1. **`icebookreader.exe`** (3,309,024 bytes):
   - **Internal Build Path (PDB)**: `D:\Work\BookReader\icebookreader-Desktop_Qt_5_15_1_MSVC2019_32bit\bin\icebookreader.pdb`
   - **Compiler / Toolchain**: Microsoft Visual C++ 2019 (v14.29.30135.0), 32-bit x86 target (`IMAGE_FILE_MACHINE_I386`).
   - **File Version / Product Version**: `6.0.0.0` / Installer registered version `6.56`.
   - **Role**: Primary GUI shell, book library manager, reading window, and rendering orchestrator.
2. **`icebooksvc.exe`** (80,864 bytes):
   - **Internal Build Path (PDB)**: `D:\Work\BookReader\icebookreader-Desktop_Qt_5_15_1_MSVC2019_32bit\bin\icebooksvc.pdb`
   - **Source File**: `..\..\..\icebookreader\projects\icebooksvc\icebooksvc.cpp`
   - **Key Methods / Strings**: `icebooksvc::exec`, `icebooksvc::read`, `icebooksvc::reportPaginationDone`, `..\icedesktopcore\src\remotehandler\remotehandler.cpp`, `QPagedPaintDevice`.
   - **Role**: Out-of-process helper service spawned by the main app for document pagination and background rendering calculations, preventing UI thread blocking.
3. **`unins000.exe`** (946,006 bytes):
   - Inno Setup uninstaller version `5.5.1.ee2 (a)`.

### 1.3 Tech Stack & Dynamic Libraries
- **GUI & Application Framework**: Qt 5.15.1 (`Qt5Core`, `Qt5Gui`, `Qt5Widgets`, `Qt5WinExtras`, `Qt5Svg`).
- **HTML / EPUB / Text Rendering Engine**: QtWebKit (`Qt5WebKit.dll` 29.1 MB, `Qt5WebKitWidgets.dll`). Interacts with WebKit using a bridge via `Qt5WebSockets` and `Qt5WebChannel` (`WSTransport::textMessageReceived`).
- **PDF Rendering Engine**: Debenu Quick PDF Library (`DebenuPDFLibraryDLL1016.dll` v10.16.0.0, 6.08 MB) wrapped via `DebenuPDFLibraryDLLQt1016` / `PdfDocument` / `PdfViewerHelper`.
- **Archive & Container Extraction**:
  - `quazip.dll`: Qt wrapper around zlib for `.epub`, `.cbz`, `.zip`.
  - `unrar.dll` (v7.11.1): Decompression for `.cbr` (Comic Book RAR).
  - `7zxa.dll`: 7-Zip archive engine for `.7z` container files.
- **XML / Parsing**: `libxml2.dll` (v2.9.10) and `libxslt.dll` (used for FB2 XML parsing, OPF manifest parsing, and styling transformations).
- **Database Engine**: SQLite 3 via Qt's `qsqlite.dll` (`Qt5Sql.dll`).
- **Text-To-Speech (TTS)**: `Qt5TextToSpeech.dll` paired with `texttospeech/qtexttospeech_sapi.dll` (Windows SAPI backend).
- **Internationalization (i18n)**: ICU 65.1 (`icudt65.dll`, `icuin65.dll`, `icuuc65.dll`) + Qt Linguist `.qm` translation files.
- **Networking & SSL**: `libcurl.dll` (v7.87.0-DEV), `libcrypto-1_1.dll` (OpenSSL 1.1.1p), `libssl-1_1.dll` (OpenSSL 1.1.1p).
- **Crash Reporting**: `CrashRpt1403.dll` (CrashRpt v1.4.0.3).

### 1.4 Database Schema & Storage Hierarchy
The application stores user data under the user's home profile at:
- **Database Path**: `~/.ebookreader/data/ebooklib.sqlite3`
- **Book Storage**: `~/.ebookreader/books/`
- **Covers Cache**: `~/.ebookreader/covers/*.jpg`

The SQLite schema extracted verbatim from `icebookreader.exe`:

```sql
-- Books catalog table
CREATE TABLE IF NOT EXISTS books (
    id              INTEGER PRIMARY KEY,
    cover           TEXT,
    full_path       TEXT,
    author          TEXT,
    title           TEXT,
    format          INTEGER,
    time_added      INTEGER,
    time_last_view  INTEGER,
    position        INTEGER,
    max_position    INTEGER,
    is_favorite     INTEGER,
    is_deleted      INTEGER,
    notes_count     INTEGER,
    book_hash       TEXT,
    use_user_cover  INTEGER,
    is_read         INTEGER
);

-- User folders / collections table
CREATE TABLE IF NOT EXISTS folders (
    id          INTEGER PRIMARY KEY,
    parent_id   INTEGER,
    title       TEXT UNIQUE
);

-- Many-to-many relationship binder between books and folders
CREATE TABLE IF NOT EXISTS book_folder_binder (
    book_id     INTEGER NOT NULL,
    folder_id   INTEGER NOT NULL,
    UNIQUE(book_id, folder_id),
    FOREIGN KEY(book_id) REFERENCES books(id),
    FOREIGN KEY(folder_id) REFERENCES folders(id)
);

-- Extensible book metadata table
CREATE TABLE IF NOT EXISTS book_metadata (
    id          INTEGER PRIMARY KEY,
    book_id     INTEGER NOT NULL,
    meta_type   INTEGER NOT NULL,
    meta_value  TEXT
);

-- Cascading delete triggers
CREATE TRIGGER IF NOT EXISTS delete_book_folder_bind_books
BEFORE DELETE ON books
BEGIN
    DELETE FROM book_folder_binder WHERE book_id = old.id;
END;

CREATE TRIGGER IF NOT EXISTS delete_book_folder_bind_folders
BEFORE DELETE ON folders
BEGIN
    DELETE FROM book_folder_binder WHERE folder_id = old.id;
END;
```

### 1.5 Supported Ebook Formats & Detection
Verbatim file dialog filter string extracted from binary:
```
eBook Files (*.epub *.mobi *.prc *.fb2 *.pdf *.txt *.cbz *.cbr *.zip *.7z)
```

File association registry mappings (`HKEY_CLASSES_ROOT\IcecreamEbookReader`):
- `.epub` -> `IcecreamEbookReader\EPUB` -> DefaultIcon: `icons\epub.ico`
- `.mobi` -> `IcecreamEbookReader\MOBI` -> DefaultIcon: `icons\mobi.ico`
- `.fb2`  -> `IcecreamEbookReader\FB2`  -> DefaultIcon: `icons\fb2.ico`
- `.cbz`  -> `IcecreamEbookReader\CBZ`  -> DefaultIcon: `icons\cbz.ico`
- `.cbr`  -> `IcecreamEbookReader\CBR`  -> DefaultIcon: `icons\cbr.ico`
- `.djvu` -> `icons\djvu.ico` is present in installation directory; internal format enum references `djvu`.
- Command invocation: `"C:\Program Files (x86)\Icecream Ebook Reader\icebookreader.exe" "%1"`

### 1.6 UI Component Hierarchy & Architecture
291 RTTI class descriptors and source file paths reveal the internal architecture:
- **Application Core**:
  - `Application`: Manages single-instance check via `QtLocalPeer` / `QtLockedFile`, command-line opening (`Application::openFileFromCommandLine`), and TTS initialization (`Application::initTts`).
  - `BookProvider`: High-level data access service interfacing with `QSqlDatabase` (`ebooklib.sqlite3`).
  - `BookModel` (`QAbstractTableModel`), `BookSortFilterModel`, `BookSearchModel`: Library data models for views.
  - `FolderModel`: Tree / hierarchy model for folders and categories.
  - `SettingsProvider`: Reads and writes application preferences via `QSettings`.
- **Main Window & Pages**:
  - `MainWindow` (inherits `IceWindow`): Custom frameless window using native Windows DWM hits (`IceNativeWindowUtils`).
  - `LibraryPage`:
    - Shelves / View modes: `library-view-cards` (thumbnails/grid) vs `library-view-table` (list/table).
    - Sidebar categories: All Books, Recently Read, Favorites, Recently Added, Formats, Custom Folders, Books with No Folder, Trash/Deleted.
    - Drag & drop handling: `LibraryPage::onDragStarted`, `application/icecream-ebookreader-book_id-mime`.
  - `ReadingPage`:
    - `ReadingToolBar`: Back to library, full screen toggle, column layout switcher (1 column / 2 columns), theme picker (Day, Night, Sepia), font zoom in/out, line spacing inc/dec, TTS play/pause/volume controls.
    - `ReadingSideBar`: Collapsible drawer containing:
      - `TocBox` / `TocModel` / `TocItemWidget`: Table of Contents navigation.
      - `BookmarksBox` / `BookmarkModel` / `BookmarkWidget`: Bookmarks list and toggles.
      - `NotesBox` / `NotesModel` / `NotesSortFilterModel` / `NoteWidget`: Highlights and annotations list with color filters.
      - `SearchBox` / `SearchWidget` / `SearchLineEdit`: Text and page search in book.
    - `SelectionActionsPopup`: Context popup on text selection with actions:
      - Copy (`copySelection`)
      - Translate via Google (`translateSelection`)
      - Search Google / Wikipedia (`searchSelectionGoogle`, `searchSelectionWikipedia`)
      - Add Note / Highlight with 5 colors (`addNoteAtCurrentSelection`, `NotePopup`)
- **Document Viewers**:
  - `AbstractViewer`: Common viewer interface (`goPage`, `goLink`, `setZoomValue`, `handleMousePressEvent`).
  - `TextViewer`: WebKit-backed viewer (`QWebView` + `QWebPage`) for reflowable formats:
    - Injects `qrc:/jsengine.js` into chapters.
    - Communicates positions, chapter pagination, selection offsets, and DOM highlights.
    - Used for: **EPUB**, **MOBI**, **FB2**, **TXT**.
  - `ImageViewer`: `QGraphicsView` + `CustomGraphicsPixmapItem` for image-based books:
    - Used for: **CBZ**, **CBR** (uncompressed via `ZipReader` / `RarReader`).
  - `PdfViewer`: Backed by `DebenuPDFLibraryDLLQt1016` / `PdfDocument` / `PdfViewerHelper`:
    - Renders PDF pages into `QImage` at target zoom/DPI.
- **Embedded SVG Icons (94 resources)**:
  `library-view-cards.svg`, `library-view-table.svg`, `columns-single.svg`, `columns-double.svg`, `style-day.svg`, `style-night.svg`, `style-sepia.svg`, `toc.svg`, `bookmark.svg`, `notes.svg`, `tts-play.svg`, `tts-stop.svg`, `tts-speed.svg`, `tts-volume-0.svg`, `tts-volume-100.svg`, `zoom-in.svg`, `zoom-out.svg`, `linespacing-inc.svg`, `linespacing-dec.svg`, `trash.svg`, etc.

### 1.7 Keyboard Shortcuts Map
Directly extracted from `Hotkeys::matches` in `hotkeys.cpp`:
- `Left` / `Up` / `PgUp` / `Backspace`: Previous Page
- `Right` / `Down` / `PgDown` / `Space`: Next Page
- `Home`: Book Start
- `End`: Book End
- `Ctrl+Up`: Zoom In / Increase Font Size
- `Ctrl+Down`: Zoom Out / Decrease Font Size
- `Ctrl+0`: Reset Zoom to 100%
- `Shift+0`: Fit to Page
- `Shift+1`: Fit to Width
- `Ctrl+1`: Single Column Mode
- `Ctrl+2`: Two Columns (Double Page Spread)
- `F11`: Toggle Fullscreen
- `Esc`: Back to Library
- `Ctrl+F` / `F3`: In-Book Search
- `Ctrl+T`: Table of Contents
- `Ctrl+B`: Toggle / Show Bookmarks List
- `Ctrl+N`: Notes / Annotations List
- `Ctrl+C` / `Ctrl+Ins`: Copy Selected Text
- `F7` / `Media Play`: Start / Pause Reading Aloud (TTS)
- `F8` / `Media Stop`: Stop Reading Aloud
- `F5` / `Media Prev`: TTS Previous Chunk
- `F6` / `Media Next`: TTS Next Chunk
- `F9`: Decrease TTS Volume
- `F10`: Increase TTS Volume
- `F1`: Switch Reading Theme

---

## 2. Logic Chain

1. **Stack Identification**:
   - Observations: Binary imports `Qt5Core.dll`, `Qt5Gui.dll`, `Qt5Widgets.dll`, `Qt5WebKit.dll`, `DebenuPDFLibraryDLL1016.dll`. PDB paths indicate MSVC 2019 32-bit compilation in Qt 5.15.1.
   - Inference: The original application is a traditional C++ Qt 5 desktop application relying heavily on legacy QtWebKit for HTML reflow and a commercial Foxit/Debenu DLL for PDF rendering.
2. **Out-of-Process Pagination Rationale**:
   - Observations: `icebooksvc.exe` imports `QPagedPaintDevice` and contains symbols `icebooksvc::reportPaginationDone`, `remotehandler.cpp`, and WebSocket IPC `wstransport.h`.
   - Inference: Rendering complex HTML/EPUB pagination in QtWebKit on the main UI thread causes freezing. The original authors offloaded pagination calculations and layout measuring to a background helper process (`icebooksvc.exe`) communicating over local WebSockets / IPC to keep the UI fluid.
3. **Storage & Data Management Architecture**:
   - Observations: Database schema contains `books`, `folders`, `book_folder_binder`, `book_metadata`. The path is `~/.ebookreader/data/ebooklib.sqlite3`, and files are indexed with `book_hash` for duplicate prevention.
   - Inference: The app maintains a centralized SQLite database. Deletion is soft (`is_deleted = 1` moving to "Trash"). Books can belong to multiple folders via a many-to-many binder table with cascading delete triggers.
4. **Three-Tier Viewer Architecture**:
   - Observations: `AbstractViewer` is subclassed into `TextViewer` (WebKit), `ImageViewer` (QGraphicsView for CBR/CBZ), and `PdfViewer` (Debenu PDF).
   - Inference: Clean architectural segregation exists between reflowable text documents (EPUB/MOBI/FB2/TXT), raster image collections (CBZ/CBR), and fixed-layout vector documents (PDF).

---

## 3. Caveats

- **DRM Handling**: The binary contains the string `"Ebook file is DRM protected. Book cannot be opened"`. No proprietary decryption keys are embedded; the application simply rejects DRM-encrypted containers.
- **DjVu Format**: `djvu.ico` is present in the installation directory and `djvu` is in the format enum, but no separate `libdjvulibre` DLL was detected (it was either compiled statically or left as an icon placeholder). For the clean-room replica, DjVu support can be marked as low priority (Could) or integrated via a lightweight open-source library.
- **Debenu PDF Licensing**: The original app uses a proprietary licensed commercial library (`DebenuPDFLibraryDLL1016.dll`). Our replica MUST NOT use Debenu, but instead an open-source library (such as Poppler, PDFium, or MuPDF).

---

## 4. Conclusion & Implications for Modern C++20 / Qt 6 Replica

The survey provides a complete, unambiguous blueprint for our clean-room architecture:

### Modern Architecture Mapping

| Reference Component (Legacy Qt 5) | Modern Clean-Room Replica (C++20 / Qt 6) | Rationale & Architectural Enhancement |
| :--- | :--- | :--- |
| **Architecture / Target** | 32-bit x86 MSVC 2019 Windows | **64-bit x64 Windows / Cross-platform C++20 with Qt 6.6+** |
| **Reflow Engine** | QtWebKit (29.1 MB legacy DLL) | **QtWebEngine (Chromium) OR LiteHTML / QTextDocument** | Enables modern CSS3, HTML5, EPUB3 fixed-layout & reflowable specs without legacy WebKit baggage. |
| **PDF Engine** | Debenu Quick PDF (commercial closed DLL) | **Poppler (poppler-qt6) OR Google PDFium OR MuPDF** | Clean-room, high performance, native Qt 6 integration with text selection, annotations, and search. |
| **Archive Handling** | `quazip.dll`, `unrar.dll`, `7zxa.dll` | **libzip / QuaZip-Qt6 + libarchive** | Single unified archive abstraction handling ZIP (EPUB, CBZ), RAR (CBR), and TAR/7Z. |
| **Threading Model** | Separate process `icebooksvc.exe` over WebSockets | **In-process Qt Concurrency (`QThreadPool`, `QFutureWatcher`, C++20 Coroutines / `std::jthread`)** | Eliminates inter-process overhead, socket synchronization complexity, and firewall/antivirus false positives while guaranteeing 60 FPS UI responsiveness. |
| **Database** | SQLite 3 via `qsqlite.dll` (`ebooklib.sqlite3`) | **Modern SQLite 3 with WAL (Write-Ahead Logging) via `QSqlDatabase`** | Maintain exact schema compatibility (`books`, `folders`, `book_folder_binder`, `book_metadata`) with foreign keys enabled (`PRAGMA foreign_keys = ON`). |
| **TTS Backend** | `Qt5TextToSpeech.dll` + SAPI | **Qt 6 `QTextToSpeech`** | Native support in Qt 6 with Windows SAPI / OneCore voices and Linux/macOS cross-platform voices. |
| **Custom UI** | `IceWindow`, `IceButton`, custom painter | **Qt Quick / QML OR Custom Styled Qt Widgets with SVG Icons** | Clean modern vector UI scaling smoothly on 4K/Hi-DPI displays without custom manual window hacking. |

---

## 5. Verification Method

To independently verify all findings in this report, execute the following commands on the reference environment:

1. **Verify Files and Versions**:
   ```powershell
   Get-ChildItem -Path "C:\Program Files (x86)\Icecream Ebook Reader" -Filter "*.exe" | Select-Object Name, Length, @{N='FileVersion';E={(Get-Item $_.FullName).VersionInfo.FileVersion}}
   ```
2. **Verify SQLite Database Schema in Binary**:
   ```powershell
   python -c "
   with open(r'C:\Program Files (x86)\Icecream Ebook Reader\icebookreader.exe', 'rb') as f:
       d = f.read()
   import re
   for m in re.findall(rb'create\s+table\s+[^;]+;', d, re.I):
       print(m.decode('ascii', errors='ignore'))
   "
   ```
3. **Verify File Dialog Filter & Formats**:
   ```powershell
   python -c "
   with open(r'C:\Program Files (x86)\Icecream Ebook Reader\icebookreader.exe', 'rb') as f:
       d = f.read()
   import re
   print(re.findall(rb'eBook Files \([^\)]+\)', d)[0].decode())
   "
   ```
4. **Verify Translation Count and English Strings**:
   ```powershell
   (Get-ChildItem "C:\Program Files (x86)\Icecream Ebook Reader\translations\*.qm").Count
   ```
