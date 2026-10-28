# Clean-Room Architecture Specification: Icecream Ebook Reader Replica
**Target Application**: Modern 64-bit Desktop Ebook Reader & Library Management System  
**Language Standard**: ISO C++20 (MSVC 2022 v143+, GCC 13+, Clang 17+)  
**Framework**: Qt 6.6+ (Core, Gui, Widgets, Sql, Concurrent, Svg, TextToSpeech)  
**Database**: SQLite 3.42+ (Write-Ahead Logging / WAL mode)  
**Document Format Support**: EPUB (2.0.1 & 3.2), PDF, MOBI / AZW / PRC, FB2, CBZ / CBR, TXT  
**Author**: Teamwork Clean-Room Engineering Group (`worker_m2`, `replica-architect`)  
**Date**: 2026-10-28  
**Reference Target**: Clean-room reverse engineering of Icecream Ebook Reader (v6.56 / core binary v6.0.0.0)

---

## 1. Executive Summary & Architectural Philosophy

The objective of this project is to construct a modern, high-performance, 64-bit clean-room desktop replica of Icecream Ebook Reader. The original application is a 32-bit x86 Windows binary built upon legacy Qt 5.15.1, an obsolete QtWebKit browser engine (29.1 MB binary footprint), a commercial third-party PDF library (Foxit/Debenu Quick PDF), and an out-of-process WebSocket helper service (`icebooksvc.exe`) to perform document pagination off the GUI thread.

The replica architecture completely redesigns this system from first principles using modern C++20 and Qt 6.6+. It eliminates all commercial runtime dependencies, deprecates WebKit in favor of streamlined native text rendering and modern document abstraction, replaces inter-process socket communication with in-process C++20 cooperative multithreading, and establishes an ACID-compliant SQLite 3 persistence layer with Write-Ahead Logging (WAL).

### 1.1 Architectural Tenets

1. **Strict 60 FPS GUI Thread Independence**: The main application event loop is strictly dedicated to user interaction, scene graph painting, and lightweight model notifications. All disk I/O, archive decompression, XML/HTML stream parsing, image scaling, search indexing, and database write operations execute asynchronously on background worker threads via `std::jthread` and `QThreadPool`.
2. **Abstract Document Engine (`IDocumentEngine`)**: File format processing is cleanly decoupled from presentation widgets. Formats are divided into two fundamental paradigms: `ReflowableDocumentEngine` (EPUB, MOBI, FB2, TXT) with dynamic pagination and anchor tracking, and `FixedLayoutDocumentEngine` (PDF, CBZ, CBR) with vector/raster page scaling.
3. **Canonical Fragment Identifier (CFI) Precision**: In reflowable publications, reading progress, bookmarks, and annotations are anchored using standard EPUB Canonical Fragment Identifiers (CFI) rather than fragile pixel coordinates or unstable page numbers, ensuring absolute reading position fidelity across window resizing, typography changes, and device displays.
4. **Resilient Window Interaction**: High-frequency window resize operations trigger an interactive suppression mechanism (`setResizingMode(true)`), temporarily suspending layout calculations and presenting a hardware-accelerated bilinear-stretched bitmap preview until mouse release, completely preventing UI freezing and layout thrashing.
5. **Modern C++20 Idioms**: The codebase mandates ISO C++20 standards, adopting Concepts for compile-time interface enforcement, `std::expected<T, E>` for monadic error propagation without exceptions, `std::views` and ranges for zero-allocation collection transformation, and `std::stop_token` for instant cancellation of obsolete worker tasks.

### 1.2 Technology Stack Selection

Following the `replica-architect` methodology, every technology selection is grounded in explicit functional requirements, performance characteristics, and permissive open-source licensing:

| Architectural Layer | Selected Technology | Alternative Evaluated | Selection Rationale |
|---|---|---|---|
| **Core Language** | ISO C++20 | C++17 / C++23 | C++20 provides Concepts for engine contracts, `std::jthread` / `std::stop_token` for cancellation, ranges, and `std::span` without requiring bleeding-edge toolchains. |
| **GUI Framework** | Qt 6.6+ Widgets & QGraphicsView | Qt Quick / QML | Ebook library management and desktop text rendering require dense controls, complex multi-column text delegates, native OS window frames, and standard desktop menu bars. |
| **Vector PDF Engine** | Google PDFium (Apache 2.0) | Poppler-Qt6 (GPL v2/v3) | Permissive Apache 2.0 license, Chromium-grade battle-tested rendering engine, resilient against damaged xref tables, superior multi-threading scalability. |
| **Archive Container Extraction** | `libzip` / `QuaZip-Qt6` + `libarchive` | Minizip / zlib | Streamlined extraction of nested EPUB/CBZ archives, robust UTF-8 and ZIP64 support, in-memory stream decompression. |
| **Text Charset Detection** | `uchardet` + `QStringConverter` | ICU `ucsdet` | Lightweight Mozilla-derived statistical charset detector (~150 KB) without ICU's massive 28 MB data table overhead (`icudt.dll`). |
| **Persistence Engine** | SQLite 3.42+ (WAL mode) via `QSqlDatabase` | Flat JSON / RocksDB | Robust ACID relational store, sub-millisecond query indexing for 10,000+ books, cascading foreign keys, unified single-file library portable backups. |
| **Speech Narration (TTS)** | Qt 6 `QTextToSpeech` | Direct SAPI 5.4 COM | Native cross-platform Qt 6 speech engine seamlessly binding to Windows OneCore and SAPI voices on Windows, Speech Dispatcher on Linux, and NSSpeechSynthesizer on macOS. |
| **Build System** | Modern CMake 3.25+ | QMake / Meson | Standard cross-platform build orchestration, native target export, integrated CPM/FetchContent dependency management, CTest harness. |
| **Unit Test Framework** | Catch2 v3 + QtTest | GoogleTest | Clean BDD syntax (`SCENARIO`, `GIVEN`, `WHEN`, `THEN`), header/static library flexibility, seamless integration with Qt event loops via `QSignalSpy`. |

---

## 2. System Architecture & Layer Breakdown

The application is structured into four strictly delineated horizontal layers: Presentation, Application Core & Controllers, Document Engines, and Storage & Persistence. Information flows downward through explicit method invocations and upward through Qt signals, events, and observable callbacks.

```
+===================================================================================================+
|                                        PRESENTATION LAYER                                         |
|                                                                                                   |
|  +--------------------+   +---------------------------------------+   +------------------------+  |
|  | MainWindow (Frame) |   | LibraryView (S01A Grid / S01B Table)  |   | ReaderCanvasView (S02) |  |
|  +--------------------+   +---------------------------------------+   +------------------------+  |
|            |                                  |                                   |               |
|  +--------------------+   +-------------------+-------------------+   +------------------------+  |
|  | SideBarNav (C01)   |   | BookCard (C03)    | BookTable (C04)   |   | Toolbars / Scrubber    |  |
|  +--------------------+   +-------------------+-------------------+   +------------------------+  |
|            |                                                                      |               |
|  +--------------------------------------------------------------------------------+------------+  |
|  | Drawers & Popups: TocDrawer (S04), Bookmarks (S03), Notes (S05), Search (S10), NotePopup (S06) |  |
|  +---------------------------------------------------------------------------------------------+  |
|  | Styling & Theme Engine: StyleManager (Day, Night, Light Sepia, Dark Sepia), DimmerOverlay     |  |
+===================================================================================================+
                                                |
                                                v [Signals / Slots / Qt Models]
+===================================================================================================+
|                                APPLICATION CORE & CONTROLLER LAYER                                |
|                                                                                                   |
|  +--------------------+   +--------------------+   +--------------------+   +------------------+  |
|  | BookContext        |   | LibraryManager     |   | BookModel          |   | BookmarkManager  |  |
|  | (Session State)    |   | (Lifecycle / CRUD) |   | (QAbstractTable)   |   | (CRUD & Signals) |  |
|  +--------------------+   +--------------------+   +--------------------+   +------------------+  |
|            |                        |                        |                        |           |
|  +--------------------+   +--------------------+   +--------------------+   +------------------+  |
|  | AnnotationManager  |   | TtsController      |   | InBookSearchService|   | ExportService    |  |
|  | (DOM / CFI Ranges) |   | (Speech Synthesis) |   | (Async Worker)     |   | (.EBR / HTML)    |  |
|  +--------------------+   +--------------------+   +--------------------+   +------------------+  |
+===================================================================================================+
                                                |
                                                v [Engine Contracts & Commands]
+===================================================================================================+
|                                      DOCUMENT ENGINE LAYER                                        |
|                                                                                                   |
|                         <<concept / interface>> IDocumentEngine                                   |
|                                     ^                     ^                                       |
|                                     |                     |                                       |
|               +---------------------+                     +---------------------+                 |
|               |                                                                 |                 |
|  +-------------------------------------+                       +-------------------------------+  |
|  |      ReflowableDocumentEngine       |                       |   FixedLayoutDocumentEngine   |  |
|  +-------------------------------------+                       +-------------------------------+  |
|       |           |           |           |                         |                 |           |
|       v           v           v           v                         v                 v           |
|   +-------+   +-------+   +-------+   +-------+                 +-------+         +-------+       |
|   | EPUB  |   | MOBI  |   |  FB2  |   |  TXT  |                 |  PDF  |         |  CBZ  |       |
|   |Engine |   |Engine |   |Engine |   |Engine |                 |Engine |         |Engine |       |
|   +-------+   +-------+   +-------+   +-------+                 +-------+         +-------+       |
|   (OCF/OPF)  (PalmDOC)   (Base64)    (Reflow)                  (PDFium)          (libzip)         |
+===================================================================================================+
                                                |
                                                v [I/O & Persistence]
+===================================================================================================+
|                                     STORAGE & CACHE LAYER                                         |
|                                                                                                   |
|  +-------------------------------------+   +-----------------------+   +-----------------------+  |
|  | DatabaseManager (SQLite 3.42+ / WAL)|   | ThumbnailCache        |   | SettingsManager       |  |
|  | - books, authors, folders, binder   |   | - Two-tier: RAM LRU   |   | - settings.ini        |  |
|  | - bookmarks, annotations, progress  |   |   (128 MB) + Disk JPG |   | - Window geometry     |  |
|  +-------------------------------------+   +-----------------------+   +-----------------------+  |
+===================================================================================================+
```

---

### 2.1 Presentation Layer (Qt 6 Widgets / QGraphicsView)

The Presentation Layer manages user interface components, native window behavior, styling, and rendering viewports:

#### 1. `MainWindow` (Frameless Shell & Navigation Structure)
- **Base Class**: `QMainWindow` with custom Windows Desktop Window Manager (DWM) integration.
- **Responsibilities**:
  - Intercepts native Windows messages (`WM_NCHITTEST`, `WM_NCCALCSIZE`, `WM_ENTERSIZEMOVE`, `WM_EXITSIZEMOVE`) via `nativeEvent()` to achieve a borderless, modern user experience with native aero snap, window shadows, and resize borders.
  - Manages view transitions between `LibraryPage` (S01A/S01B) and `ReadingPage` (S02) via a smooth `QStackedWidget`.
  - Coordinates global shortcuts (`F11` fullscreen, `Esc` return to library).

#### 2. `LibraryPage` & View Implementations (S01A Grid / S01B Table)
- **`SideBarNav` (C01)**: 220px fixed navigation drawer rendering brand logo, system categories (`All`, `Recently Read`, `Read`, `Favorites`, `Deleted`), format filter sub-tree, and custom user folders. Emits category filter signals to `BookFilterProxyModel`.
- **`LibraryHeaderBar` (C02)**: Top action bar housing "+ Add book" CTA, "+ Add folder", instant search input with 150ms debounce, and segmented view toggle (Cards vs. Table).
- **`BookShelfGridView` (S01A)**:
  - Custom fluid grid implementing `IceFlowLayout` or `QListView` in `IconMode`.
  - Displays `BookCardWidget` (C03) items (160x240px) with asynchronous cover image loading, format pills, favorite star toggles, two-line title elision, author label, and smooth horizontal progress bar.
- **`BookTableView` (S01B)**:
  - High-density `QTableView` presenting sortable columns: Cover/Title, Author, Added Date, Notes Count, Reading Progress Bar, Format.
  - Custom delegates: `CoverTitleDelegate` (renders 24x32px thumbnail), `ProgressBarDelegate` (custom styled progress bar with overlaid percentage), `NotesBadgeDelegate` (pill badge).
- **`LibraryFooterBar` (C05)**:
  - Contextual animated bottom footer sliding into view upon selection of 1 or more books.
  - Provides batch actions: "Select all", "Clear selection", "Add to category", "Move to Trash", "Restore", and import/export progress indicator.

#### 3. `ReadingPage` & Dual-Mode Canvas (S02)
- **Viewport Canvas Architecture**:
  - **Reflowable Viewport**: Custom paginated text canvas or multi-column layout. Left and right 15% margin zones act as hoverable, clickable page navigation controls.
  - **Fixed-Layout Viewport**: High-performance `QGraphicsView` housing `FixedPageGraphicsItem` rendering rasterized PDF or comic pages with support for arbitrary zoom, fit-to-width, fit-to-page, and continuous or 2-page spread layouts.
- **Floating Controls**:
  - `ReadingToolBar` (C06): Autohiding top toolbar providing library back button, TOC toggle (`Ctrl+T`), bookmarks drawer (`Ctrl+B`), notes drawer (`Ctrl+N`), in-book search (`Ctrl+F`), fullscreen toggle (`F11`), zoom controls, TTS controls, and quick settings popover gear.
  - `ReadingFooterBar` (C07): Floating translucent bottom scrubber slider (`IceSlider`) with chapter ticks, hover tooltips showing target page and chapter title, page label (`Page: %1 / %2`), and dynamic "Back to page %1" history link.

#### 4. Side Drawers, Overlays & Dialogs
- **`BookmarksDrawer` (S03)**: 320px right-side drawer listing saved bookmarks with thumbnail preview, chapter name, relative percentage, creation date, and deletion action.
- **`TocDrawer` (S04)**: 340px left-side drawer presenting a hierarchical `QTreeView` of book chapters extracted from NCX, Nav Doc, PDF outlines, or MOBI/FB2 sections.
- **`NotesDrawer` (S05)**: 360px right-side drawer displaying all annotations and text commentary, search filter, and "Export notes to HTML" action.
- **`NotePopup` (S06 / C08)**: Floating context bubble appearing at text selection coordinates offering 4 color swatches (Yellow `#FFE270`, Green `#A8F29A`, Cyan `#7BE5F8`, Pink `#FFA0C5`), inline commentary editor, Copy, Google, Wikipedia, and Translate shortcuts.
- **`QuickSettingsPopover` (S07)**: Anchored non-modal overlay allowing live adjustment of font family, font size, line spacing, text alignment, column count (Single vs. Double spread), theme palette, and dimming slider.
- **`PreferencesDialog` (S08)**: 5-tab system preferences dialog (System, Reading, Hotkeys, Text-to-Speech, About).
- **`BookPropertiesDialog` (S09)**: Metadata inspector and editor with custom cover replacement support.
- **`InBookSearchDrawer` (S10)**: Right-side panel with search input, direct page jump action, search progress spinner, and streaming result list with highlighted snippet cards.

#### 5. Unified Styling Engine (`StyleManager`)
- Manages global Qt Style Sheets (QSS) and palette tokens across four synchronized color themes:
  1. **Day Style**: Clean white canvas (`#FFFFFF`), charcoal text (`#1E1E1E`), light gray chrome (`#F4F5F7`).
  2. **Night Style**: Deep dark canvas (`#181818`), light muted text (`#C8C8C8`), dark slate chrome (`#22242A`).
  3. **Light Sepia Style**: Warm cream paper canvas (`#FBF0D9`), dark espresso text (`#433422`), warm tan chrome (`#EDE2CB`).
  4. **Dark Sepia Style**: Muted sepia brown canvas (`#2C2621`), warm off-white text (`#D0BE9C`), dark bronze chrome (`#201B17`).
- **Dimmer Overlay**: Borderless full-window `QWidget` with `Qt::WA_TransparentForMouseEvents` positioned directly above the reading viewport. The alpha channel is dynamically bound to the dimming slider (0% to 80% opacity `#000000`), allowing comfortable reading below hardware display minimum brightness.

---

### 2.2 Application Core & Controller Layer

The Application Core contains the business logic, session state machines, asynchronous worker coordination, and Qt model infrastructure:

```cpp
namespace core {

// Active reading session context
class BookContext : public QObject {
    Q_OBJECT
public:
    explicit BookContext(QObject* parent = nullptr);
    
    void loadBook(std::int64_t bookId);
    void closeCurrentBook();
    
    [[nodiscard]] std::int64_t currentBookId() const noexcept;
    [[nodiscard]] QString currentCfi() const;
    [[nodiscard]] int currentPage() const noexcept;
    [[nodiscard]] int totalPages() const noexcept;
    [[nodiscard]] double progressPercentage() const noexcept;
    [[nodiscard]] int columnCount() const noexcept;
    
public slots:
    void setReadingPosition(int page, const QString& cfi);
    void setColumnCount(int columns);
    void setFontSize(int pointSize);
    void setLineSpacing(double spacing);
    void setAlignment(Qt::Alignment alignment);
    void cycleTheme();
    
signals:
    void bookLoaded(const BookMetadata& metadata);
    void positionChanged(int page, int totalPages, double percentage, const QString& cfi);
    void layoutChanged();
    void themeChanged(ThemeId themeId);
    
private:
    std::int64_t m_currentBookId{-1};
    QString m_currentCfi;
    int m_currentPage{0};
    int m_totalPages{0};
    int m_columnCount{2};
    int m_fontSize{12};
    double m_lineSpacing{1.4};
    Qt::Alignment m_alignment{Qt::AlignJustify};
    ThemeId m_themeId{ThemeId::Day};
};

} // namespace core
```

#### Key Service Controllers:
1. **`LibraryManager`**:
   - Manages book ingestion, duplicate prevention via SHA-256 content hashing, cover thumbnail dispatch, folder association, and soft/hard deletions.
   - Coordinates batch imports via worker threads, wrapping database commits in 100-item SQLite transactions.
2. **`BookModel` (`QAbstractTableModel`)**:
   - High-performance, virtualized model representing the library collection.
   - Implements `canFetchMore()` and `fetchMore()` for incremental 50-row batch loading, ensuring instantaneous rendering of 10,000+ item libraries.
   - Synchronizes with `BookFilterProxyModel` for multi-attribute searching (title, author, format) and folder tree filtering.
3. **`BookmarkManager`**:
   - Handles creation, retrieval, and deletion of bookmarks.
   - Maps between absolute page indices and EPUB CFIs, emitting signals to synchronize the toolbar ribbon icon and `BookmarksDrawer`.
4. **`AnnotationManager`**:
   - Manages text highlights and user commentary.
   - Maintains exact DOM CFI ranges (`cfi_start`, `cfi_end`), color classifications, and coordinates database persistence with automatic update triggers on `books.notes_count`.
5. **`TtsController`**:
   - Encapsulates Qt 6 `QTextToSpeech` engine.
   - Segments chapter text into paragraph/sentence utterance queues, tracks speech synthesis events, advances reader pages when the final visible paragraph completes, and notifies the canvas to highlight currently spoken words.
6. **`InBookSearchService`**:
   - Asynchronous worker scanning chapter texts using regex or substring matchers.
   - Emits streaming hit signals containing snippet contexts, chapter names, and CFI/page locations, allowing immediate user interaction while search progresses in the background.

---

### 2.3 Document Engine Layer (`IDocumentEngine`)

The Document Engine Layer decouples publication file parsing and rendering from the user interface. It establishes a strict, type-safe C++20 contract:

```cpp
namespace engine {

enum class DocumentError {
    FileNotFound,
    AccessDenied,
    CorruptContainer,
    MissingManifest,
    InvalidSpine,
    DrmProtected,
    UnsupportedFormat,
    RasterizationFailed,
    ParseError
};

struct PageDimensions {
    double widthPoints{0.0};
    double heightPoints{0.0};
    int rotationDegrees{0};
};

struct TocItem {
    QString title;
    QString targetAnchor; // CFI string or chapter filename
    int pageIndex{0};
    std::vector<TocItem> children;
};

struct TextSearchHit {
    int pageIndex{0};
    QString cfi;
    QString contextSnippet;
    int matchStartOffset{0};
    int matchLength{0};
};

// C++20 Concept enforcing Document Engine interface
template <typename T>
concept DocumentEngineConcept = requires(T engine, const std::filesystem::path& path, 
                                         int page, double scale, std::stop_token token) {
    { engine.open(path) } -> std::same_as<std::expected<BookMetadata, DocumentError>>;
    { engine.close() } -> std::same_as<void>;
    { engine.pageCount() } -> std::same_as<int>;
    { engine.tableOfContents() } -> std::same_as<TocItem>;
    { engine.renderPage(page, scale, token) } -> std::same_as<std::expected<QImage, DocumentError>>;
    { engine.extractText(page) } -> std::same_as<QString>;
};

// Pure abstract interface for polymorphic engine storage
class IDocumentEngine {
public:
    virtual ~IDocumentEngine() = default;
    
    [[nodiscard]] virtual std::expected<BookMetadata, DocumentError> open(const std::filesystem::path& filePath) = 0;
    virtual void close() = 0;
    
    [[nodiscard]] virtual bool isReflowable() const noexcept = 0;
    [[nodiscard]] virtual int pageCount() const noexcept = 0;
    [[nodiscard]] virtual TocItem tableOfContents() = 0;
    
    [[nodiscard]] virtual std::expected<QImage, DocumentError> renderPage(
        int pageIndex, double dpiScale, std::stop_token stopToken = {}) = 0;
        
    [[nodiscard]] virtual QString extractText(int pageIndex) = 0;
    
    [[nodiscard]] virtual std::vector<TextSearchHit> search(
        const QString& query, bool caseSensitive, std::stop_token stopToken = {}) = 0;
};

} // namespace engine
```

#### Specialized Sub-Engines:

```
                      <<interface>> IDocumentEngine
                                    ▲
                                    │
            ┌───────────────────────┴───────────────────────┐
            │                                               │
<<abstract>> ReflowableDocumentEngine           <<abstract>> FixedLayoutDocumentEngine
            ▲                                               ▲
     ┌──────┴──────┬──────────┬──────────┐            ┌─────┴─────┐
     │             │          │          │            │           │
EpubEngine    MobiEngine  Fb2Engine  TxtEngine    PdfEngine   ComicEngine
(OCF/OPF)     (PalmDOC)   (Base64)   (Reflow)     (PDFium)    (libzip/CBR)
```

1. **`ReflowableDocumentEngine`**:
   - Manages linear spine items, continuous text layout, dynamic multi-column partitioning, and CFI calculation.
   - Subclasses:
     - **`EpubEngine`**: Validates OCF ZIP container; parses OPF package XML; resolves manifest item IDs; constructs spine vector; parses EPUB 2 NCX or EPUB 3 Navigation Document; renders XHTML content into column flow layouts; serializes/deserializes EPUB CFIs.
     - **`MobiEngine`**: Parses Palm Database (PDB) headers and record offset tables; decompresses PalmDOC LZ77 records; maps embedded Mobipocket image records; converts raw stream into standardized XHTML flow.
     - **`Fb2Engine`**: Streaming XML parser extracting `<title-info>`, decoding base64 embedded binary cover images; structures body `<section>` nodes into chapter streams; extracts footnote links.
     - **`TxtEngine`**: Autodetects encoding via `uchardet` / BOM; decodes text via `QStringConverter`; applies heuristic paragraph reconstruction (soft wrap removal vs. double-newline paragraph separation); divides text into virtual pages ($\approx 2,500$ chars).

2. **`FixedLayoutDocumentEngine`**:
   - Manages static, page-based publications where page boundaries are immutable.
   - Subclasses:
     - **`PdfEngine`**: Implemented via Google PDFium. Rasterizes vector pages into `QImage` buffers at calculated target DPI; supports text extraction, glyph bounding box inspection for selections, and PDF outline traversal.
     - **`ComicEngine`**: Implemented via `libzip` (CBZ) and `libarchive` / `unrar` (CBR). Natural alphanumeric sorting of image files; extracts `ComicInfo.xml` metadata; streams decompressed page pixmaps.

---

### 2.4 Storage & Cache Layer

The Storage Layer provides persistent storage, configuration retention, and thumbnail caching:

#### 1. Database Persistence (`DatabaseManager` & `ebooklib.sqlite3`)
- **Connection Management**: Configures SQLite 3 via `QSqlDatabase` with Write-Ahead Logging (`PRAGMA journal_mode = WAL;`) and non-blocking timeout handling (`PRAGMA busy_timeout = 5000;`).
- **Referential Integrity**: Enforces foreign keys (`PRAGMA foreign_keys = ON;`). All relationships implement explicit `ON DELETE CASCADE` or `ON DELETE SET NULL` constraints.
- **Query Optimization**: High-frequency queries (library search, last read sorting, format filtering, favorites, duplicate checking) are backed by dedicated B-Tree indexes.
- **Cached Counters**: Automated triggers maintain denormalized counters such as `books.notes_count` without requiring expensive runtime `COUNT(*)` aggregations.

#### 2. Two-Tier Thumbnail Cache (`ThumbnailCache`)
- **Tier 1: Memory LRU Cache**:
  - Implements an in-memory `QCache<QString, QPixmap>` capped at 128 MB.
  - Keyed by `book_hash`. Guarantees instantaneous 60 FPS scrolling through large library grids without disk I/O hits.
- **Tier 2: Disk Cache**:
  - Persistent JPEG thumbnails stored at `~/.ebookreader/covers/<book_hash>.jpg`.
  - Generated asynchronously upon book import at 300x420px (preserving 1:1.4 aspect ratio) using smooth bicubic scaling.

#### 3. Configuration Management (`SettingsManager`)
- Persists user preferences to `~/.ebookreader/settings.ini` via `QSettings`:
  - `[General]`: `localeName`, `lastStyleId`, `library_view_mode`, `library_category`, `dimming_level`.
  - `[viewer.text]`: `column_count` (1 or 2), `font_family`, `font_size`, `line_spacing`, `text_alignment`.
  - `[tts]`: `ttsLocaleVoiceMap`, `ttsVolume`, `ttsSpeed`, `ttsPitch`.
  - `[window]`: `geometry`, `maximized`, `fullscreen`.
  - `[hotkeys]`: Custom key sequence overrides for all 25 actions.

---

## 3. Third-Party Library Selection & In-Depth Technical Trade-offs

To guarantee architectural stability, legal compliance, and performance, each third-party dependency has been thoroughly evaluated against alternatives:

### 3.1 PDF Rendering Engine: Google PDFium vs. Poppler-Qt6 vs. MuPDF

```
+---------------------------------------------------------------------------------------------------+
| Metric / Criterion       | Google PDFium (Chosen)       | Poppler-Qt6                  | MuPDF    |
+---------------------------------------------------------------------------------------------------+
| License                  | Apache 2.0 (Permissive)      | GPL v2/v3 (Copyleft)         | AGPL v3  |
| Windows 64-bit ABI       | Official Google build / Vcpkg| Challenging MSVC build       | Straightforward |
| Damaged xref Resilience  | Exceptional (Chromium battle)| Moderate (Fails on corrupts) | Good     |
| Multi-threading Safety   | Page-level thread safe       | Thread-safe with locks       | Context per thread |
| Rendering Performance    | Highly optimized SIMD        | Very good                    | Excellent|
| Qt 6 Integration         | Thin C++ wrapper required    | Native QImage / Qt types     | C wrapper required |
+---------------------------------------------------------------------------------------------------+
```

- **Selection**: **Google PDFium** (via official pre-built binaries or Vcpkg).
- **Rationale**:
  1. *Licensing Freedom*: Apache 2.0 allows unrestricted commercial and open-source distribution without GPL copyleft contagiousness, unlike Poppler (GPLv2/v3) which restricts modularity.
  2. *Resilience against Corrupted PDFs*: Because PDFium powers Google Chrome, its fault tolerance against malformed xref tables, missing EOF markers, and syntax errors is superior to all competitors.
  3. *Thread Safety*: PDFium allows rendering distinct pages across worker threads simultaneously using isolated `FPDF_PAGE` handles, matching our lookahead pre-rendering requirements.

### 3.2 Archive Container Extraction: `libzip` vs. `QuaZip-Qt6` vs. `libarchive`

- **Selection**: **`libzip`** (for EPUB & CBZ) + **`libarchive`** (for CBR / RAR / 7z).
- **Rationale**:
  - `QuaZip-Qt6` is a convenient Qt wrapper over zlib, but `libzip` provides direct memory-mapped file access, seamless in-memory buffer reading, and robust ZIP64 support with zero Qt event loop dependencies.
  - For comic archives, `libarchive` provides a universal streaming extraction interface supporting RAR (CBR), 7Z, and TAR archives without requiring proprietary unrar DLLs.

### 3.3 Text Charset Detection: `uchardet` vs. ICU vs. `QStringConverter`

- **Selection**: **`uchardet`** for statistical autodetection + Qt 6 **`QStringConverter`** for decoding.
- **Rationale**:
  - The legacy application embedded ICU 65.1 binaries (`icudt65.dll` alone was 28.0 MB, `icuin65.dll` was 2.1 MB).
  - `uchardet` is a battle-tested C++ port of Mozilla's Universal Charset Detector, compiled into less than 180 KB of binary code, achieving 99%+ accuracy on Cyrillic, CJK, and Western European legacy encodings. Once the charset name is identified, Qt 6's native `QStringConverter` performs the Unicode conversion with zero third-party overhead.

### 3.4 Database Access: `QSqlDatabase` vs. Native SQLite3 C API

- **Selection**: **`QSqlDatabase` (`QSQLITE` driver) with native SQLite3 API fallback**.
- **Rationale**:
  - `QSqlDatabase` integrates directly with Qt's model/view architecture (`QSqlQueryModel`), simplifying UI binding.
  - Native SQLite3 C API (`sqlite3_bind_*`, `sqlite3_step`) is utilized in the background `LibraryManager` thread for batch bulk imports to achieve maximum transaction throughput (15,000+ inserts/second) bypassing Qt wrapper overhead.

### 3.5 Text-to-Speech (TTS): Qt 6 `QTextToSpeech` vs. Direct Windows SAPI COM

- **Selection**: **Qt 6 `QTextToSpeech`**.
- **Rationale**:
  - Qt 6's `QTextToSpeech` module provides a modern, asynchronous C++ interface wrapping Windows SAPI and Windows OneCore on Windows, Speech Dispatcher on Linux, and AVFoundation on macOS.
  - Eliminates manual COM initialization (`CoInitializeEx`), thread apartment marshaling, and platform-specific audio device handling.

---

## 4. Concurrency & Threading Architecture

Maintaining an uncompromising 60 FPS responsive GUI is mandatory. Any operation requiring disk I/O, compression/decompression, XML parsing, or image scaling is prohibited on the main thread.

```
+===================================================================================================+
|                                  MAIN GUI THREAD (Thread ID: 1)                                   |
|                                                                                                   |
|  - Event Loop (User Input, Mouse, Keyboard, Window Events)                                        |
|  - Widget Hierarchy & Scene Graph Painting                                                        |
|  - QAbstractItemModel Lightweight Notification Processing                                         |
|  - UI State Transitions & Popups                                                                  |
+===================================================================================================+
         │                                       ▲                                   ▲
         │ (Queued Task via QThreadPool)          │ (Signals / emit)                  │
         v                                       │                                   │
+------------------------------------------------+--+   +----------------------------+--------------+
| WORKER THREAD POOL (QThreadPool / std::jthread)   |   | DEDICATED DB WORKER (std::jthread)        |
|                                                   |   |                                           |
| Task A: Pre-render Page N+1 (stop_token checked)  |   | Serialized Write Queue:                   |
| Task B: Pre-render Page N+2 (stop_token checked)  |   | - Batch library imports (100-item chunks) |
| Task C: In-Book Text Search Scanner               |   | - Progress & reading position auto-saves  |
| Task D: EPUB Chapter XHTML Streaming & Sanitizing |   | - Bookmark & annotation CRUD operations   |
| Task E: Thumbnail Generation & Bicubic Scaling    |   |                                           |
+---------------------------------------------------+   +-------------------------------------------+
```

### 4.1 Non-Blocking GUI Thread Mandate
- The Main Thread executes the Qt event loop (`QApplication::exec()`).
- Long-running operations are encapsulated into `QRunnable` or `std::jthread` worker functions.
- Results are marshaled back to the GUI thread strictly via `Qt::QueuedConnection` signals or `QMetaObject::invokeMethod`.

### 4.2 Lookahead Pre-Rendering Buffer ($N+1, N+2$) with `std::stop_token`
- When the reader displays page $N$, the engine queues low-priority background render tasks for pages $N+1$ and $N+2$.
- Each task receives a `std::stop_token`. If the user flips pages rapidly (e.g. holding the Right Arrow key or jumping via the scrubber slider), all pending lookahead tasks for superseded pages are immediately cancelled via `std::stop_source::request_stop()`, preventing worker thread saturation:

```cpp
namespace engine {

class PageRenderTask : public QRunnable {
public:
    PageRenderTask(IDocumentEngine* engine, int pageIndex, double scale, 
                   std::stop_token stopToken,
                   std::function<void(int, QImage)> callback)
        : m_engine(engine), m_pageIndex(pageIndex), m_scale(scale), 
          m_stopToken(stopToken), m_callback(std::move(callback)) {
        setAutoDelete(true);
    }
    
    void run() override {
        if (m_stopToken.stop_requested()) return;
        
        auto result = m_engine->renderPage(m_pageIndex, m_scale, m_stopToken);
        
        if (result.has_value() && !m_stopToken.stop_requested()) {
            m_callback(m_pageIndex, std::move(result.value()));
        }
    }
    
private:
    IDocumentEngine* m_engine;
    int m_pageIndex;
    double m_scale;
    std::stop_token m_stopToken;
    std::function<void(int, QImage)> m_callback;
};

} // namespace engine
```

### 4.3 Batch Library Import with Transaction Boundaries
- Importing directories containing 1,000+ files is handled by a background worker pipeline:
  1. Directory traversal queues all candidate ebook paths.
  2. SHA-256 hash is computed in parallel across worker threads.
  3. Hashes are checked against SQLite to skip existing documents (`Dialog_BookExists`).
  4. For new documents, metadata (Title, Author, Format, Size) and cover thumbnails are extracted.
  5. The database worker writes records in atomic transactions of 100 books (`BEGIN IMMEDIATE TRANSACTION` ... `COMMIT`).
  6. The worker emits `batchInserted(int count, int total)` to allow progressive UI model updates without GUI stutter.

### 4.4 Interactive Window Resizing Suppression Protocol
Continuous HTML/CSS reflow recalculation during interactive window dragging causes catastrophic frame drops and visual stutter. Grounded in the clean-room execution logs (`ReadingPage::setResizingMode(true)` / `false`), the replica implements the following formal suppression protocol:

```
[User presses left mouse button on window edge and drags]
         │
         ▼
[Native Windows Message: WM_ENTERSIZEMOVE]
         │
         ├─► 1. Invoke: ReadingPage::setResizingMode(true)
         ├─► 2. Capture current viewport rendering as a high-res QPixmap snapshot (m_resizeSnapshot)
         ├─► 3. Suspend all active DocumentEngine reflow calculations and cancel background render tasks
         └─► 4. Switch canvas paint engine to Hardware Bilinear Stretched Bitmap mode
         │
         ▼
[Active Dragging: WM_SIZING / QResizeEvent stream]
         │
         └─► Canvas simply blits m_resizeSnapshot scaled to current viewport dimensions (60+ FPS)
         │
         ▼
[User releases mouse button]
         │
         ▼
[Native Windows Message: WM_EXITSIZEMOVE]
         │
         ├─► 1. Invoke: ReadingPage::setResizingMode(false)
         ├─► 2. Obtain final viewport geometry (width, height, DPI)
         ├─► 3. Dispatch single comprehensive reflow pass to DocumentEngine with active CFI anchor
         └─► 4. Fade smoothly from stretched snapshot to newly rendered sharp layout
```

---

## 5. Edge Case Handling Protocols

### 5.1 Indexing Massive Libraries (10,000+ Books)
- **Virtualization**: `BookTableView` and `BookShelfGridView` utilize `QAbstractItemModel` lazy fetching. The model reports the total book count (`rowCount()`) from a cached SQLite count, but instantiates internal `BookItem` data structures only for visible rows plus a 50-row buffer via `canFetchMore()` and `fetchMore()`.
- **Memory Management**: High-resolution cover thumbnails are never stored in `BookModel`. The view delegates request covers from `ThumbnailCache` by `book_hash`. If a cover is not in RAM, the delegate renders a lightweight format badge placeholder and queues an asynchronous disk read.

### 5.2 Damaged, Truncated, and Malformed Files
- **EPUB OCF Violations**: Standard OCF dictates that `mimetype` must be stored uncompressed at byte offset 30. If an archive fails this check (due to re-compression by third-party utilities), `EpubEngine` does not fail immediately; it falls back to inspecting the ZIP central directory for any entry named `mimetype` or containing an `.opf` file.
- **XML Entity & Syntax Recovery**: EPUB OPF/NCX and FB2 XML documents frequently contain undeclared HTML entities (`&nbsp;`, `&mdash;`) or unclosed tags. The XML parser operates in tolerant recovery mode (using `libxml2` with `XML_PARSE_RECOVER` or Qt's token-skipping stream reader) to salvage book content.
- **PDF Corrupt Cross-Reference (`xref`) Tables**: If PDFium reports an invalid or missing `xref` table, it triggers automatic xref reconstruction, scanning the byte stream for `obj` / `endobj` tokens to restore the document hierarchy.
- **MOBI HUFF/CDIC Compression**: If Record 0 specifies compression type `17480`, `MobiEngine` inspects the dictionary records (`HUFF` and `CDIC`). If dictionary records are corrupted, the engine emits a graceful `DocumentError::CorruptContainer` alert without crashing.
- **External File Deletions**: If an indexed ebook file is deleted or moved on disk externally, opening attempts detect `std::filesystem::exists() == false` and trigger `Dialog_Error` (S12), offering the user options to "Locate file..." via file picker or "Remove from library".

### 5.3 Dynamic Reflow Pagination & Geometry Transitions
- **CFI Anchor Preservation**: When the user alters font family, font size, line spacing, margins, or window dimensions, page counts change. Before executing the reflow pass, `BookContext` queries the topmost visible text node and captures its EPUB CFI string (`epubcfi(...)`). Following the reflow calculation, the viewport scrolls to the exact element and character offset indicated by the CFI anchor, ensuring the user never loses their reading location.
- **Minimum Width Column Clamping**: If Two-Column (Double Page Spread) mode is active and the window is resized narrower than 700px, the engine automatically clamps the layout to Single-Column mode to prevent unreadable narrow columns. It seamlessly restores Two-Column mode when the window width exceeds 700px.

### 5.4 High-DPI Scaling Across Mixed-DPI Multi-Monitor Setups
- The application enables per-monitor High-DPI scaling:
  ```cpp
  QApplication::setHighDpiScaleFactorRoundingPolicy(
      Qt::HighDpiScaleFactorRoundingPolicy::PassThrough);
  ```
- All PDF page rasterization and canvas drawing operations multiply logical dimensions by `devicePixelRatioF()`:
  $$\text{RenderWidth} = \text{LogicalWidth} \times \text{devicePixelRatioF()}$$
- When a user drags the window across monitors with differing scaling factors (e.g. 100% 1080p to 200% 4K), `MainWindow` catches `QEvent::ScreenChangeInternal`, invalidates the visible page cache, and re-rasterizes at the new device pixel ratio.

---

## 6. Modern C++20 Patterns & Idioms

The architecture strictly adheres to modern C++20 idioms, enhancing safety and performance:

### 6.1 Monadic Error Propagation (`std::expected`)
No exceptions are thrown across engine or storage boundaries. All operations that can fail return `std::expected<T, E>`, enabling expressive monadic chaining:

```cpp
namespace storage {

std::expected<BookRecord, DatabaseError> getBookById(std::int64_t id);
std::expected<void, DatabaseError> updateProgress(std::int64_t id, int page, const QString& cfi);

} // namespace storage

// Usage in Controller
auto result = storage::getBookById(bookId)
    .and_then([&](const BookRecord& book) -> std::expected<QImage, DocumentError> {
        return m_documentEngine->open(book.fullPath)
            .and_then([&](const BookMetadata&) {
                return m_documentEngine->renderPage(book.position, 1.0);
            });
    });

if (!result) {
    emit errorOccurred(formatError(result.error()));
}
```

### 6.2 C++20 Ranges and Views for Zero-Allocation Filtering
Library searching and sorting operations utilize non-allocating range pipelines:

```cpp
auto matchingBooks = m_booksCache 
    | std::views::filter([&query](const BookItem& b) {
          return b.title.contains(query, Qt::CaseInsensitive) ||
                 b.author.contains(query, Qt::CaseInsensitive);
      })
    | std::views::filter([](const BookItem& b) { return !b.isDeleted; })
    | std::views::take(100);
```

### 6.3 Cooperative Cancellation via `std::jthread` and `std::stop_token`
All background workers run inside `std::jthread` instances that automatically request stop on destruction:

```cpp
class SearchWorker {
public:
    void startSearch(QString query, std::vector<QString> chapterFiles) {
        m_workerThread = std::jthread([this, q = std::move(query), files = std::move(chapterFiles)]
                                      (std::stop_token stopToken) {
            for (const auto& file : files) {
                if (stopToken.stop_requested()) return;
                searchChapter(file, q, stopToken);
            }
        });
    }
    
    void cancel() {
        m_workerThread.request_stop();
    }

private:
    std::jthread m_workerThread;
};
```

---

## 7. Project Directory Layout & CMake Configuration

### 7.1 Source Tree Layout

The project follows a clean modular CMake directory structure:

```
icecream_ebook_reader_replica/
├── CMakeLists.txt                      # Root build configuration
├── CMakePresets.json                   # Presets for MSVC, GCC, Clang
├── LICENSE                             # Open source license (MIT / Apache 2.0)
├── README.md                           # Build and usage instructions
├── cmake/                              # Custom CMake modules & CPM setup
│   ├── CPM.cmake
│   └── FindPDFium.cmake
├── assets/                             # Application assets
│   ├── icons/                          # SVG icons (94 vector icons)
│   ├── translations/                   # Qt Linguist .ts and .qm catalogs
│   └── styles/                         # Day, Night, Sepia QSS stylesheets
├── src/
│   ├── app/                            # Executable entrypoint
│   │   ├── main.cpp
│   │   └── Application.hpp / .cpp
│   ├── core/                           # Application core & controllers
│   │   ├── BookContext.hpp / .cpp
│   │   ├── LibraryManager.hpp / .cpp
│   │   ├── BookmarkManager.hpp / .cpp
│   │   ├── AnnotationManager.hpp / .cpp
│   │   ├── TtsController.hpp / .cpp
│   │   └── SearchService.hpp / .cpp
│   ├── engine/                         # Document engine layer
│   │   ├── IDocumentEngine.hpp
│   │   ├── ReflowableEngine.hpp / .cpp
│   │   ├── FixedLayoutEngine.hpp / .cpp
│   │   ├── epub/
│   │   │   ├── EpubEngine.hpp / .cpp
│   │   │   ├── OcfReader.hpp / .cpp
│   │   │   └── CfiProcessor.hpp / .cpp
│   │   ├── pdf/
│   │   │   └── PdfiumEngine.hpp / .cpp
│   │   ├── mobi/
│   │   │   └── MobiEngine.hpp / .cpp
│   │   ├── fb2/
│   │   │   └── Fb2Engine.hpp / .cpp
│   │   ├── comic/
│   │   │   └── ComicEngine.hpp / .cpp
│   │   └── txt/
│   │       ├── TxtEngine.hpp / .cpp
│   │       └── CharsetDetector.hpp / .cpp
│   ├── storage/                        # Storage & cache layer
│   │   ├── DatabaseManager.hpp / .cpp
│   │   ├── BookRepository.hpp / .cpp
│   │   ├── ThumbnailCache.hpp / .cpp
│   │   └── SettingsManager.hpp / .cpp
│   └── ui/                             # Qt 6 Presentation layer
│       ├── MainWindow.hpp / .cpp
│       ├── frameless/
│       │   ├── FramelessWindow.hpp / .cpp
│       │   └── NativeEventFilter_Win.cpp
│       ├── library/
│       │   ├── LibraryPage.hpp / .cpp
│       │   ├── BookShelfGridView.hpp / .cpp
│       │   ├── BookCardWidget.hpp / .cpp
│       │   ├── BookTableView.hpp / .cpp
│       │   ├── BookModel.hpp / .cpp
│       │   └── SideBarNav.hpp / .cpp
│       ├── reader/
│       │   ├── ReadingPage.hpp / .cpp
│       │   ├── ReflowCanvas.hpp / .cpp
│       │   ├── FixedLayoutCanvas.hpp / .cpp
│       │   ├── ReadingToolBar.hpp / .cpp
│       │   └── ReadingFooterBar.hpp / .cpp
│       ├── drawers/
│       │   ├── BookmarksDrawer.hpp / .cpp
│       │   ├── TocDrawer.hpp / .cpp
│       │   ├── NotesDrawer.hpp / .cpp
│       │   └── SearchDrawer.hpp / .cpp
│       ├── popups/
│       │   ├── NotePopup.hpp / .cpp
│       │   └── QuickSettingsPopover.hpp / .cpp
│       └── dialogs/
│           ├── PreferencesDialog.hpp / .cpp
│           ├── BookPropertiesDialog.hpp / .cpp
│           └── ConfirmationDialogs.hpp / .cpp
└── tests/                              # Unit & integration test harness
    ├── CMakeLists.txt
    ├── unit/
    │   ├── test_cfi_processor.cpp
    │   ├── test_epub_parser.cpp
    │   ├── test_pdfium_engine.cpp
    │   ├── test_mobi_decompressor.cpp
    │   ├── test_txt_reflow.cpp
    │   └── test_database_manager.cpp
    └── integration/
        ├── test_library_import_flow.cpp
        └── test_reading_session_flow.cpp
```

### 7.2 Modern CMake Configuration (`CMakeLists.txt`)

```cmake
cmake_minimum_required(VERSION 3.25)
project(IcecreamEbookReaderReplica
    VERSION 1.0.0
    LANGUAGES C CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Enable compiler warnings
if(MSVC)
    add_compile_options(/W4 /permissive- /utf-8)
else()
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find Qt 6 Modules
find_package(Qt6 6.6 REQUIRED COMPONENTS
    Core
    Gui
    Widgets
    Sql
    Concurrent
    Svg
    TextToSpeech
    Test
)

qt_standard_project_setup()

# Third-Party Dependencies via FetchContent or Vcpkg
find_package(PDFium REQUIRED)
find_package(libzip REQUIRED)
find_package(uchardet REQUIRED)
find_package(SQLite3 3.42 REQUIRED)

# Modular Library Targets
add_subdirectory(src/storage)
add_subdirectory(src/engine)
add_subdirectory(src/core)
add_subdirectory(src/ui)

# Main Executable Target
add_executable(icecream_reader src/app/main.cpp)
target_link_libraries(icecream_reader PRIVATE
    reader_ui
    reader_core
    reader_engine
    reader_storage
    Qt6::Core
    Qt6::Widgets
)

# Test Suite
enable_testing()
add_subdirectory(tests)
```

---

## 8. Phased Implementation Roadmap & Vertical Slice (R4)

Following the `replica-architect` build order methodology, implementation proceeds in three disciplined, testable milestones. Milestone 1 establishes a thin end-to-end vertical slice verifying the core reading loop, Milestone 2 expands the library management and format catalog, and Milestone 3 completes the advanced reading tools.

```
+===================================================================================================+
|                                  PHASED IMPLEMENTATION ROADMAP                                    |
|                                                                                                   |
|  [MILESTONE 1: Minimal Vertical Slice] ────────► [MILESTONE 2: Library & Catalog] ──► [MILESTONE 3]
|  - Load & render single EPUB & PDF               - Multi-view catalog (S01A/B)         - Bookmarks (S03)
|  - In-process pagination & display               - Bulk directory import (F01)         - Notes/Highlight (S05/06)
|  - Reading progress saved to SQLite              - SHA-256 deduplication (F02)         - In-Book Search (S10)
|  - Proves C++20 + Qt 6 + PDFium/EPUB loop        - Search, filter, soft delete         - Themes & TTS (S07/S08)
|  (Screens: S01/S02, Components: C01/C02/C06)     (Screens: S01A/B, S09, C01-C05)       (Screens: S03-S08, S10)
+===================================================================================================+
```

---

### Milestone 1: Minimal Vertical Slice (Core Reading Loop)
**Objective**: Build a complete, functional end-to-end slice proving the architecture: open a single EPUB or PDF document, paginate and render it inside the Qt 6 reading canvas (S02), navigate pages via keyboard, and automatically persist the exact reading position into SQLite.

- **Screens Implemented**:
  - `S01`: Minimal library container with "+ Add book" CTA and open book action.
  - `S02`: Reader Window Canvas with single-column text/page display and floating top toolbar.
- **UI Components Implemented**:
  - `C01`: Basic Sidebar.
  - `C02`: Header Bar with "+ Add book" file picker.
  - `C06`: Reader Top Toolbar with Back button and Page counter (`Page: %1 / %2`).
- **Engines Implemented**:
  - `PdfiumEngine`: Load PDF document, query page count, rasterize target page to `QImage` at device DPI.
  - `EpubEngine`: Unpack EPUB container, parse OPF spine, render first chapter XHTML.
- **Database Tables Initialized**:
  - `books` (stores file path, hash, format, current position, percentage).
  - `reading_progress` (stores fine-grained timestamp and position).
- **Core User Flow Verified**:
  - `F03` (Open and Read Ebook): Add book file $\to$ open in S02 $\to$ flip pages $\to$ close application $\to$ re-open $\to$ exact page restored.
- **Verification Criteria**:
  1. Compiles with C++20 on MSVC / Clang with zero warnings.
  2. Opening a standard EPUB 3 (e.g. *Moby Dick*) renders styled chapter text.
  3. Opening a vector PDF (e.g. complex specification) renders sharp text at 60 FPS.
  4. Closing the app at Page 42 correctly resumes at Page 42 on relaunch.

---

### Milestone 2: Core Library Management & Complete Format Ingestion
**Objective**: Transform the vertical slice into a full-featured digital bookshelf supporting thousands of books, rich metadata extraction, multi-view presentation, instant search, and all six format ingestion pipelines.

- **Screens Implemented**:
  - `S01A`: Library Shelf (Responsive cover grid with `BookCardWidget`).
  - `S01B`: Library Catalog (Sortable metadata `QTableView` with progress bar delegates).
  - `S09`: Book Properties & Custom Cover Dialog.
  - `S12`: Confirmation popups (`Dialog_BookAdded`, `Dialog_BookExists`, `Dialog_Error`).
- **UI Components Implemented**:
  - `C03`: `BookCardWidget` (cover thumbnail, format badge, favorite star, title/author elision, progress track).
  - `C04`: `BookTableView` with sortable columns and custom delegates.
  - `C05`: Animated bottom operations footer for batch operations.
- **Engines Implemented**:
  - `MobiEngine`: Palm Database parsing and PalmDOC LZ77 decompression.
  - `Fb2Engine`: Streaming XML parser and base64 cover extractor.
  - `ComicEngine`: CBZ / CBR comic archive unpacker with natural sort.
  - `TxtEngine`: `uchardet` encoding detector and heuristic paragraph reflow.
- **Database Tables & Constraints**:
  - `authors`, `book_authors`, `folders`, `book_folder_binder`, `book_metadata`.
  - All foreign keys, cascading delete triggers, and performance B-Tree indexes.
- **User Flows Verified**:
  - `F01`: Single and bulk folder import with SHA-256 deduplication.
  - `F02`: Category filtering (Recently Read, Favorites, Trash), instant text search, and Grid $\leftrightarrow$ Table view toggle.
- **Verification Criteria**:
  1. Ingesting a folder of 1,000 mixed-format books completes in background without freezing UI.
  2. Attempting to add an existing file alerts user with `Dialog_BookExists`.
  3. Grid view scrolls smoothly at 60 FPS utilizing the two-tier thumbnail cache.
  4. Moving a book to Trash updates `is_deleted = 1` and reflects in sidebar trash counter.

---

### Milestone 3: Advanced Reading Tools, Annotations & Accessibility
**Objective**: Complete the full reading suite, delivering fine-grained typography controls, side drawers, text annotation with color swatches, full-text in-book search, reading themes, and text-to-speech narration.

- **Screens Implemented**:
  - `S03`: Bookmarks Side Drawer.
  - `S04`: Hierarchical Table of Contents Drawer.
  - `S05`: Notes & Highlights Side Drawer.
  - `S06`: Text Selection Action Bubble (`NotePopup`).
  - `S07`: In-Reader Quick Settings Popover.
  - `S08`: Global Preferences Dialog (`IceDialog`).
  - `S10`: In-Book Full-Text Search Drawer.
  - `S11`: Print Ebook Dialog.
- **UI Components Implemented**:
  - `C07`: Scrubber slider footer with chapter tick marks and hover tooltips.
  - `C08`: Selection context popup with 4-color palette and inline note editor.
  - `C09`: Native Windows DWM frameless shell.
  - `C10`: Full keyboard shortcut dispatch table (25 shortcuts).
- **Core Services Implemented**:
  - `BookmarkManager` & `AnnotationManager` (CFI range serialization).
  - `InBookSearchService` (asynchronous streaming text scanner).
  - `TtsController` (Qt 6 `QTextToSpeech` with real-time paragraph highlight).
  - `StyleManager` (Day, Night, Light Sepia, Dark Sepia stylesheets and dimmer overlay).
- **User Flows Verified**:
  - `F04`: Dynamic reflow pagination, font scaling, and column toggling.
  - `F05`: Bookmark creation via `Ctrl+D` and jump via S03 drawer.
  - `F06`: Text selection highlighting (4 colors), note commentary, and HTML export.
  - `F07`: Theme cycling (`F1`) and display dimming slider.
  - `F08`: Fullscreen reading mode (`F11`) with autohiding toolbars.
  - `F09`: Text-to-speech read aloud with speed/volume controls and paragraph tracking.
  - `F10`: Library backup export and restore (`.EBR` archive packaging).
- **Verification Criteria**:
  1. Annotating text in EPUB survives font size changes and window resizing via CFI.
  2. In-book search streams matches asynchronously without interrupting reading.
  3. Window drag resizing engages `setResizingMode(true)` bitmap preview without lag.
  4. TTS engine speaks paragraphs clearly and automatically advances pages.

---

### 8.1 Complete Build Order & Milestone Mapping Matrix

| Step | Milestone | Target Deliverable | Screen IDs | Component IDs | Database Tables | Associated Flows |
|---|---|---|---|---|---|---|
| **1** | M1 | Engine Contracts & PDFium Engine | S02 | C06 | - | F03 |
| **2** | M1 | EPUB OCF/OPF Reflowable Engine | S02 | C06 | - | F03, F04 |
| **3** | M1 | Basic SQLite Connection & Session Restore | S01, S02 | C01, C02 | `books`, `reading_progress` | F03 |
| **4** | M2 | SQLite DDL, Constraints & Repository | S01 | - | All 10 tables + triggers | F01, F02 |
| **5** | M2 | Background Importer & Hash Deduplication | S01, S12 | C02, C05 | `books`, `book_authors` | F01 |
| **6** | M2 | MOBI, FB2, CBZ, TXT Format Engines | S02 | - | `books` | F01, F03 |
| **7** | M2 | Virtualized Table & Grid Shelf Models | S01A, S01B | C03, C04 | `books`, `folders`, `binder`| F02 |
| **8** | M2 | Two-Tier Thumbnail Cache (RAM LRU + Disk) | S01A | C03 | `books` | F01, F02 |
| **9** | M2 | Categories, User Folders & Soft Deletion | S01A, S01B | C01, C05 | `folders`, `binder`, `books` | F02 |
| **10**| M3 | Interactive Resizing Suppression & DWM | S02 | C09 | - | F04, F08 |
| **11**| M3 | EPUB CFI Parser & Anchor Position Engine | S02 | - | `reading_progress` | F03, F04 |
| **12**| M3 | TOC Drawer & Chapter Navigation | S04 | C06, C07 | - | F03, F04 |
| **13**| M3 | Bookmarks Drawer & Shortcut System | S03 | C06, C10 | `bookmarks` | F05 |
| **14**| M3 | Text Selection Bubble & Multi-Color Notes| S05, S06 | C08 | `annotations` | F06 |
| **15**| M3 | Asynchronous In-Book Full-Text Search | S10 | C06 | - | F03 |
| **16**| M3 | Theme Engine (Day/Night/Sepia) & Dimmer | S07, S08 | C06 | `app_settings` | F07 |
| **17**| M3 | Fullscreen Mode & Autohiding Toolbars | S02 | C06, C07 | - | F08 |
| **18**| M3 | Text-to-Speech Engine & Audio Highlighting | S02, S08 | C06 | `app_settings` | F09 |
| **19**| M3 | Study Report HTML Export & .EBR Migration | S05, S08 | C05 | All tables | F06, F10 |

---

## 9. Architecture Summary & Downstream Milestones

### 9.1 Architecture Scorecard
- **Architecture**: 64-bit Native C++20 / Qt 6.6+ Desktop Application.
- **Format Coverage**: 6 Major Formats (EPUB 2/3, PDF, MOBI, FB2, CBZ/CBR, TXT).
- **Screens Specified**: 12 Screens, Drawers, and Dialogs (S01A/B through S12).
- **Components Specified**: 10 Core Composite UI Widgets (C01 through C10).
- **Database Model**: 10 Normalized SQLite Tables with Foreign Keys, WAL Journaling, and Triggers.
- **Concurrency**: 1 GUI Thread, 1 Dedicated DB Writer Worker, Scalable Worker Thread Pool.
- **Top 3 Architectural Risks Resolved**:
  1. *Reflow Lag during Window Resizing*: Resolved via native `WM_ENTERSIZEMOVE` / `WM_EXITSIZEMOVE` suppression and bilinear stretched bitmap caching.
  2. *Reading Position Drift*: Resolved via standard EPUB Canonical Fragment Identifiers (CFI) anchoring to DOM nodes.
  3. *UI Stutter during 10,000+ Library Ingestion*: Resolved via batch SQLite transactions (100 items), virtualized item models (`canFetchMore`), and two-tier RAM/disk thumbnail caching.

### 9.2 Next Steps
This specification delivers Milestone M2. Downstream milestones proceed as follows:
1. **Milestone M3 (`replica/schema.sql`)**: Authoring the production DDL, constraints, triggers, indexes, and validating syntax execution with SQLite 3.
2. **Milestone M4 (`Verification & Audit`)**: Independent adversarial verification and forensic auditing by the QA and Challenger agents.
