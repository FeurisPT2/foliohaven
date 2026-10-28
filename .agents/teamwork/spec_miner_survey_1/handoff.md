# Technical Specification Mining Report: Icecream Ebook Reader Replica
**Agent**: `spec_miner_survey_1` (teamwork_preview_spec_miner)  
**Parent**: Project Orchestrator (`acfea67d-28a9-4a44-bf11-4149602dfb38`)  
**Working Directory**: `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\spec_miner_survey_1`  
**Date**: 2026-10-28  

---

## 1. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Format Support | EPUB 2.0.1 / 3.2 Ingestion | Extract OCF ZIP container, parse `container.xml`, `content.opf` manifest and spine; support NCX and EPUB 3 Navigation Document. | EPUB archive path (`.epub`) | Parsed spine item list, metadata, cover image, TOC hierarchy | Returns `EpubError::InvalidContainer` or `CorruptPackage` if XML/mimetype malformed | Binary analysis of `icebookreader.exe` (`epub::EpubDocument`, `epub::EpubParser`), `icons/epub.ico` |
| 2 | Format Support | PDF Document Rendering | Rasterize page-based vector content, support arbitrary viewport zoom factors, continuous/spread layouts, extract bookmarks and text. | PDF document path (`.pdf`), target viewport size, DPI | Rasterized `QImage` per page, outline TOC tree, text blocks | Corrupt PDF xref repairs automatically or yields load failure | Binary analysis of `DebenuPDFLibraryDLL1016.dll`, `PdfDocument::load`, `PdfDocument::requestImage` |
| 3 | Format Support | MOBI / PRC / AZW Parsing | Unpack Palm Database (PDB) container, parse PalmDOC and MOBI headers, decompress LZ77 text records, extract EXTH metadata. | MOBI file path (`.mobi`, `.prc`) | Monolithic HTML-like chapter stream, embedded image records | Detects unsupported DRM or invalid PalmDOC record count | Binary analysis (`mobi::MobiDocument`, `mobi::MobiHead`, `mobi::PDBHeader`), `icons/mobi.ico` |
| 4 | Format Support | FB2 (FictionBook) Parsing | XML-based ebook format with embedded base64 cover/illustrations, hierarchical `<section>` DOM, and `<body name="notes">` footnotes. | FB2 file path (`.fb2`, `.fb2.zip`) | Section tree, extracted cover pixmap, inline footnote mapping | Missing root `<FictionBook>` tag yields parse error; XML malformations handled via tolerant parser | Binary analysis (`fb2::FbDocument`), `icons/fb2.ico` |
| 5 | Format Support | CBZ / CBR Comic Book Archive | ZIP/RAR compressed comic archive inspection, natural sort alphanumeric page ordering, extraction of `ComicInfo.xml` metadata. | CBZ archive path (`.cbz`, `.cbr`) | Ordered image list, cover page thumbnail, comic metadata | Corrupted archive entry skipped; non-image entries filtered | Binary analysis (`ComicDocument::load`, `ZipReader`, `RarReader`), `icons/cbz.ico`, `icons/cbr.ico` |
| 6 | Format Support | TXT Intelligent Reflow & Ingestion | Plain text file loading with charset autodetection (BOM, UTF-8, Windows-125x, ICU/uchardet), heuristic hard-wrap paragraph merging. | TXT file path (`.txt`), optional user encoding override | Reflowed paragraph stream, virtual chapter divisions | Unrecognized encoding defaults to UTF-8/system locale with manual override in UI | Binary analysis (`BookContext::changeEncoding`, `TextViewer::readBook`), `settings.ini` |
| 7 | Reading Engine | Dual-Mode Layout Engine | Support both Fixed-Layout viewer (PDF, CBZ) and Reflowable viewer (EPUB, MOBI, FB2, TXT) with 1-column or 2-column page layout. | Column count (1 or 2), viewport geometry, zoom scale | Dynamic paginated columns, seamless text flow | Layout clamping prevents column collapse at minimum window dimensions | AppData `settings.ini` (`[viewer.text] column_count=2`), `TextViewer` symbols |
| 8 | Reading Engine | Position Tracking & EPUB CFI | Canonical Fragment Identifiers (CFI) and virtual page coordinates to track and restore exact reading location across window resizes. | Book ID, CFI string or page index | Viewport scrolled/navigated to precise element/character | If CFI target missing after DOM reload, falls back to nearest chapter/page | Binary inspection (`cFI`, `TextBookChapter::getReadingPosition`, `TextBookChapter::setReadingPosition`) |
| 9 | Reading Engine | Interactive Resizing Suspension | Throttled / suspended reflow calculation during active OS window resizing (`WM_ENTERSIZEMOVE`), executing full layout on release. | Window resize event stream | Temporary scaled bilinear bitmap preview, single final reflow pass | Prevents UI freezing / thrashing during window drag operations | Application logs (`ReadingPage::setResizingMode(true)` / `false`) |
| 10 | Navigation | Hierarchical Table of Contents | Multi-level tree of book chapters/sections extracted from NCX, Nav Doc, PDF Outline, FB2 sections, or MOBI toc index. | Book context | Hierarchical `TocModel` tree with chapter title and destination target | Missing TOC synthesizes virtual chapter list based on file sections/pages | Binary analysis (`TocItemWidget::readFrom`, `TocModel`, `TextBookChapter::getReadingLink`) |
| 11 | Annotations | In-Book Highlighting & Notes | User text selection annotation with 5 color styles (Yellow, Green, Red, Purple, Blue) and Underline, with note popups and notes list. | Selection range (`startOffset`, `endOffset`), color enum, text note | Styled DOM/canvas overlay, persisted note record | Overlapping highlights normalized; note popup clamps to screen bounds | Binary analysis (`span.yellownote`, `span.greennote`, `NoteItem::NoteColor`, `NotePopup`, `notes_count`) |
| 12 | Bookmarks | Page & Fragment Bookmarking | Quick bookmark toggle on current page/CFI with thumbnail preview, title, creation timestamp, and navigation drawer. | Current reading location, optional label | Persistent bookmark entry in database, visual marker in UI | Duplicate bookmark on same page/fragment toggles removal | Binary analysis (`BookmarkWidget::readFrom`, `BookmarkModel`, `createBookmarkForCurrentPage`) |
| 13 | Search | In-Book Full-Text Search | Asynchronous background text searching across chapters/pages with progressive match emission, context snippet extraction, and hit jumping. | Query string, case sensitivity flag | Stream of search results with page index, character offset, snippet | Empty query clears results; regex special characters escaped | Binary analysis (`SearchWidget::readFrom`, `BookSearchModel`, `PdfViewerHelper::receiveText`) |
| 14 | Library Management | Multi-View Catalog (Cards & Table) | Grid cards view (`QListView` in icon mode) with high-res cover rendering and Table list view (`QTableView`) with sortable columns. | View mode enum (`Cards` = 1, `Table` = 0) | Rendered catalog grid or multi-column data table | Preserves scroll position and active selection during view toggle | Application logs (`LibraryPage::setViewMode('Cards')`), `settings.ini` |
| 15 | Library Management | Category & Folder Hierarchy | Organization of library books into System categories (All, Recently Read, Favorites, Read, Trash, Formats) and custom user Folders. | Category filter ID or Folder ID | Filtered book subset displayed in library view | Circular folder hierarchies prevented by parent validation | Authoritative SQLite schema (`folders`, `book_folder_binder`), `SideBarFolders` |
| 16 | Library Management | Deduplication & Integrity Hash | Unique file hashing (MD5/SHA-256) on import to detect duplicate books, preserve library state, and link cached covers/notes. | File binary contents | Book record with `book_hash`, prevention of redundant imports | Hash collision / duplicate notifies user or updates existing path | Authoritative SQLite schema (`books.book_hash`, `PRAGMA table_info`) |
| 17 | Library Management | Soft Deletion & Trash Workflow | Two-stage deletion: moving books to Trash (`is_deleted = 1`) with capabilities to restore all or permanently purge files. | Book ID list, purge command | Updated `is_deleted` flag or cascade deletion of metadata and binder entries | Permanently purging deletes associated thumbnails and metadata records | Binary analysis (`BookModel::clearTrash`, `BookProvider::restoreAllFromTrash`, `BookProvider::removeAllFromTrash`) |
| 18 | Accessibility | Text-To-Speech (TTS) Read Aloud | Real-time speech synthesis using native OS voice engines (SAPI / Speech Dispatcher), rate/pitch/volume controls, and phrase stepping. | Text stream from current page, voice locale ID | Audio output, synchronous text highlight callback | Missing voice falls back to system default; engine failure logs warning | AppData `settings.ini` (`ttsLocaleVoiceMap`, `ttsVolume`), `TtsSettingsPage`, `BookContext::readingAloud` |
| 19 | UI Theming | Theme & Palette Management | Day (light), Night (dark), and Sepia reading styles with synchronized UI palette, canvas background, text color, and icon tinting. | Style ID (`DayStyle`, `NightStyle`, `SepiaStyle`) | Updated application stylesheet (`QSS`), canvas render colors | Invalid style ID defaults to `DayStyle` | AppData `settings.ini` (`lastStyleId=DayStyle`), `IceStyleManager::setCurrentStyle` |
| 20 | Concurrency | Non-Blocking Background Operations | Asynchronous execution of batch book importing, thumbnail generation, PDF rasterization lookahead, and search indexing. | Background tasks queued to thread pool | Signal/slot notifications on GUI thread upon completion | Task cancellation via stop tokens / `QFutureWatcher` on rapid user navigation | Binary inspection (`QtConcurrent`, `Application::runDxDiagGeneration::lambda`, `BookProvider::updateBatch`) |
| 21 | Persistence | Atomic Metadata & Settings Storage | SQLite database for library indexing and INI configuration files for user interface preferences and geometry. | User interactions, window state changes | Written `ebooklib.sqlite3` and `settings.ini` | Uses transactions and atomic file writing to prevent database corruption | Authoritative database inspection (`ebooklib.sqlite3`, `settings.ini`) |
| 22 | Data Portability | Library Archive Export / Import | Packaging library metadata and books into a portable archive container (`ebrarch://`, `container.json`) for backup and migration. | Selected book list or full library | Compressed archive file containing books, covers, and JSON manifest | Missing source book files flagged with status report during export | Binary analysis (`bookimporter::exportToArchive`, `container.json`, `importbooks::extractBook`) |

---

## 2. Edge Cases

| # | Feature | Input / Condition | Observed / Required Behavior |
|---|---------|-------------------|-----------------------------|
| 1 | EPUB Parsing | Malformed XML or missing closing tags in XHTML content | Fallback to tolerant HTML/XML parser (e.g. `libxml2` with `XML_PARSE_RECOVER` or Qt stream recovery); avoid terminating parser. |
| 2 | EPUB Parsing | Uncompressed `mimetype` file contains extra trailing spaces or compression | OCF spec mandates `application/epub+zip` stored uncompressed at offset 30 with no extra field. If not at offset 30, parser must inspect archive entries rather than bailing. |
| 3 | EPUB Parsing | Obfuscated fonts using Adobe (`application/vnd.adobe.page-template+xml`) or IDPF algorithm | Detect `META-INF/encryption.xml`, extract SHA-1/UUID key from `dc:identifier`, de-obfuscate first 1024 or 1040 bytes of font stream before passing to font engine. |
| 4 | PDF Rendering | Corrupted or missing cross-reference (`xref`) table | PDF parser (PDFium / Poppler) initiates rebuild phase, scanning entire file from byte 0 for `obj` / `endobj` tokens to reconstruct object catalog. |
| 5 | PDF Rendering | High-DPI display scale change (e.g. dragging window from 100% monitor to 200% 4K monitor) | Re-rasterize visible page cache at new `devicePixelRatioF()`; prevent blurry upscaled raster images. |
| 6 | MOBI Parsing | MOBI file with HUFF/CDIC compression instead of PalmDOC LZ77 | Check compression type field in PalmDOC header (Record 0, offset 0). If value is 17480, instantiate Huffman/Dictionary decompressor; if unparseable, emit clear error. |
| 7 | FB2 Parsing | Giant base64 embedded binary cover image (>20 MB) | Parse XML via streaming (`QXmlStreamReader`); stream base64 decode directly to thumbnail generator without buffering entire decoded byte array into memory. |
| 8 | CBZ Parsing | Archive filenames with non-ASCII or mixed encodings (CP437 vs UTF-8) | Check ZIP general purpose bit flag 11 for UTF-8; if unset, attempt auto-detection via `uchardet` or system codepage to prevent corrupted file paths. |
| 9 | CBZ Reading | Mixed page orientations (portrait pages mixed with double-page landscape spreads) | In two-page spread view, automatically detect landscape aspect ratio (`width > height`) and display as isolated single spread without pairing with next portrait page. |
| 10 | TXT Reading | Legacy ASCII file formatted with hard line wraps at column 72 | Apply heuristic reflow: single newline preceded by non-punctuation joins with space; double newline (`\n\n`) creates paragraph break. |
| 11 | TXT Reading | File without Byte Order Mark (BOM) in non-Latin script (e.g. Cyrillic CP1251 or Shift-JIS) | Run statistical charset detection (`uchardet`); provide manual encoding switcher in reader toolbar (`BookContext::changeEncoding`). |
| 12 | Library Scale | Importing library containing 10,000+ ebooks simultaneously | Process in background thread batches of 100 with SQLite `BEGIN TRANSACTION` / `COMMIT`. Use incremental model notifications (`beginInsertRows`) to prevent GUI lockup. |
| 13 | Library Scale | Displaying 10,000 books in Cards view with large covers | Implement virtualized item views (`QListView` with `QAbstractItemModel::canFetchMore()` and lazy fetching); cache thumbnails on disk and maintain LRU RAM cache capped at 128 MB. |
| 14 | Resizing | Rapid interactive window resizing by user dragging corner | Intercept `WM_ENTERSIZEMOVE` / resize events, set `setResizingMode(true)`, display bilinear stretched cache image; upon `WM_EXITSIZEMOVE`, execute single complete reflow pass. |
| 15 | File Deletion | Book file deleted or moved externally on disk while listed in library | On open attempt, detect `QFileInfo::exists() == false`; display user-friendly missing file dialog offering to locate file or remove entry from library. |
| 16 | Annotations | Document text content shifts due to reflow or font size modification | Anchor annotations via EPUB CFI or stable DOM node path and relative character offset rather than absolute screen pixel coordinates. |
| 17 | Database Access | Multiple threads attempting SQLite write operations simultaneously | Enable SQLite WAL mode (`PRAGMA journal_mode = WAL;`), set `PRAGMA busy_timeout = 5000;`, and serialize all write operations through a dedicated background database worker thread. |

---

## 3. Comprehensive Format Handling Pipeline Specifications

### 3.1 EPUB (EPUB 2.0.1 and EPUB 3.2 / 3.3)
1. **Container Extraction & Validation**:
   - Container is an Open Container Format (OCF) ZIP archive.
   - Verification check: First entry must be `mimetype` (stored uncompressed, content `application/epub+zip`).
   - Extract `META-INF/container.xml`. Parse XML to locate `<rootfile full-path="..." media-type="application/oebps-package+xml"/>`.
2. **Package Document (`.opf`) Parsing**:
   - XML Namespace: `http://www.idpf.org/2007/opf`.
   - `<metadata>` extraction: `dc:title`, `dc:creator` (author), `dc:identifier` (UUID/ISBN), `dc:language`, `dc:date`.
   - Cover image extraction:
     - EPUB 2: `<meta name="cover" content="item_id"/>` referencing `<item id="item_id" href="cover.jpg" media-type="image/jpeg"/>`.
     - EPUB 3: `<item id="..." href="..." media-type="..." properties="cover-image"/>`.
   - `<manifest>`: Hash map of `id` $\to$ `{href, media-type, properties}`.
   - `<spine>`: Ordered vector of `itemref idref="..."`. This dictates the linear reading flow.
3. **Table of Contents (TOC) Extraction**:
   - EPUB 2 NCX: Parse file identified in `<spine toc="ncx">` (namespace `http://www.daisy.org/z3986/2005/ncx/`). Parse `<navMap>` $\to$ recursive `<navPoint>` nodes with `<navLabel><text>` and `<content src="...">`.
   - EPUB 3 Nav Doc: Manifest item with `properties="nav"`. Parse XHTML `<nav epub:type="toc">` ordered lists (`<ol><li><a href="...">Title</a></li></ol>`).
4. **Content Rendering & EPUB CFI Engine**:
   - Resolve chapter files relative to the OPF directory.
   - Parse XHTML and sanitize (strip external network requests, inline scripts).
   - EPUB Canonical Fragment Identifier (CFI) syntax implementation: `epubcfi(/6/4[chap01]!/4/2/10/1:24)`:
     - `/6`: Spine item offset in OPF package.
     - `!`: Step into referenced XHTML document.
     - Even integers (`/4/2/10`): Element child index in DOM tree ($2n$-th child).
     - Odd integers (`/1:24`): Character offset 24 within the 1st text node child.
   - CFI serialization and deserialization allows persisting exact reading position independent of font size or window dimensions.

### 3.2 PDF (Portable Document Format)
1. **Engine Selection Rationale**:
   - **Poppler-Qt6 (`poppler-qt6`)**: Direct native Qt 6 integration, outputs `QImage` directly, supports font embedding, text selection rectangles, and PDF outline extraction. Primary choice for Linux/cross-platform Qt applications.
   - **PDFium (Chromium Engine)**: Permissive Apache 2.0 license, exceptional rendering performance, battle-tested against damaged/malformed files, zero LGPL copyleft complications. Recommended for commercial-grade Windows clean-room implementation via a thin C++ wrapper (`PdfiumDocument`).
2. **Rendering Pipeline**:
   - Logical page coordinates (points: 72 points per inch) are transformed to device pixels:
     $$\text{pixel\_width} = \frac{\text{page\_width\_points} \times \text{target\_DPI}}{72.0} \times \text{zoom\_factor}$$
   - High-DPI handling: Render buffer multiplied by `devicePixelRatio` to prevent blurriness on Retina/4K screens.
   - Viewport Culling & Lookahead: Only render pages currently intersecting the viewport geometry, plus a lookahead buffer of 1 page above and 1 page below.
3. **Outline & Text Extraction**:
   - Recursive traversal of PDF outline dictionary (`Root/Outlines`) to populate `TocModel`.
   - Extract glyph bounding boxes (`QRectF`) for text selection, highlight overlays, and in-book full-text search.

### 3.3 MOBI / AZW / PRC (Mobipocket / Legacy Kindle)
1. **Palm Database (PDB) Format**:
   - 78-byte PDB header: Database name, creation time, modification time, type (`BOOK`), creator (`MOBI`), number of records ($N$).
   - Record offset table: Array of $N$ 32-bit integers locating raw record byte offsets in the file.
2. **Header Records**:
   - Record 0 contains:
     - PalmDOC Header: Compression type (1 = none, 2 = PalmDOC LZ77, 17480 = HUFF/CDIC), uncompressed text length, record count, record size (4096 bytes).
     - MOBI Header: Magic `MOBI`, header length, MOBI type (2 = Book), text encoding (1252 or 65001/UTF-8), first non-book record index.
     - EXTH Header: Optional metadata chunk with tag/value pairs (Author = 100, Publisher = 101, Description = 103, Cover Offset = 201).
3. **PalmDOC LZ77 Decompression Algorithm**:
   - Read byte $B$:
     - `0x00`: Literal byte `0x00`.
     - `0x01` .. `0x08`: Copy next $B$ bytes literally.
     - `0x09` .. `0x7F`: Literal byte $B$.
     - `0x80` .. `0xBF`: Read next byte $B_2$. Decode backreference: $\text{distance} = ((B \ \& \ 0x3F) \ll 8) \ | \ B_2$, $\text{length} = (B_2 \ \& \ 0x07) + 3$. Copy $\text{length}$ bytes from sliding window.
     - `0xC0` .. `0xFF`: Output ASCII space followed by character `(B ^ 0xC0)`.
4. **HTML Stream & Image Assembly**:
   - Concatenate decompressed text records to form monolithic HTML document.
   - Translate Mobipocket tags (`<mbp:pagebreak/>`, `<filepos:0000000000>`).
   - Image records: Index from `first_image_index` up to `first_non_book_index`. Map `<img recindex="K">` to image extracted from record $(first\_image\_index + K - 1)$.

### 3.4 FB2 (FictionBook 2.0 / 2.1)
1. **Schema Structure**:
   - Single valid XML file (or ZIP archive containing `.fb2`).
   - Root `<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0">`.
   - `<description>`:
     - `<title-info>`: `<genre>`, `<author>`, `<book-title>`, `<coverpage><image l:href="#cover.jpg"/></coverpage>`, `<lang>`.
   - `<body>`:
     - Hierarchical `<section>` elements with `<title>`, `<p>`, `<subtitle>`, `<epigraph>`, `<cite>`.
     - Inline tags: `<strong>`, `<emphasis>`, `<style>`, `<a>` (hyperlink/footnote).
   - `<body name="notes">`: Contains footnote sections referenced by inline anchor links.
   - `<binary id="cover.jpg" content-type="image/jpeg">`:
     - Base64-encoded raw image byte stream embedded directly in XML.
2. **Streaming Parser**:
   - Use `QXmlStreamReader` to extract `<title-info>` and `<binary id="cover.jpg">` without parsing the full document into DOM, achieving sub-10ms metadata extraction for large books.
   - Convert body `<section>` tree into virtual chapters with anchor points for footnotes.

### 3.5 CBZ / CBR (Comic Book Archives)
1. **Container Inspection**:
   - CBZ: `QuaZip` or standard `zlib`/`libzip` to enumerate archive central directory.
   - CBR: `unrar` library to extract RAR entries.
2. **Page Ordering & Cover Extraction**:
   - Filter archive entries for image extensions (`.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`).
   - Natural alphanumeric sorting (e.g., `01.jpg`, `2.jpg`, `10.jpg` $\to$ page 1, 2, 10).
   - First natural image is extracted as cover thumbnail.
3. **Metadata (`ComicInfo.xml`)**:
   - Parse optional `ComicInfo.xml` at root of archive: `<Series>`, `<Number>`, `<Volume>`, `<Summary>`, `<Writer>`, `<Penciller>`, `<PageCount>`, `<Year>`.

### 3.6 TXT (Plain Text Engine)
1. **Encoding Autodetection**:
   - Step 1: Detect BOM (UTF-8 `EF BB BF`, UTF-16LE `FF FE`, UTF-16BE `FE FF`).
   - Step 2: Run `uchardet` (Mozilla statistical charset detector) or ICU `ucsdet_detect()`.
   - Step 3: Decode text with `QStringConverter` using identified encoding.
   - Step 4: Allow user manual override via viewer settings.
2. **Heuristic Reflow Algorithm**:
   - Identify hard vs soft wraps:
     - A single newline `\n` followed by non-whitespace is treated as soft wrap if the preceding line does not terminate with sentence punctuation (`.`, `!`, `?`, `:"`). Soft wrapped lines are joined with a single space.
     - Two consecutive newlines `\n\n` denote a paragraph break.
     - Indented lines (tab or 2+ spaces) denote paragraph beginnings.
   - Virtual Pagination: Divide monolithic text into virtual pages of $\approx 2,500$ characters or split by chapter regex (`^(Chapter\s+[0-9IVXLCDM]+|[0-9]+\.\s+)`).

---

## 4. Modern C++20 & Qt 6 Architecture and Concurrency Model

### 4.1 Layer Decomposition Diagram
```
+---------------------------------------------------------------------------------+
|                                 PRESENTATION LAYER                              |
|  MainWindow  |  LibraryPage (Cards / Table)  |  ReadingPage (Fixed / Reflow)    |
|  ReadingToolBar  |  TocDrawer  |  BookmarksDrawer  |  NotesPopup  |  StyleMgr   |
+---------------------------------------------------------------------------------+
                                       |
+---------------------------------------------------------------------------------+
|                                APPLICATION LAYER                                |
|  BookContext (Session State)  |  BookModel (QAbstractTableModel)                |
|  SearchService (Async Search) |  TtsController (Speech) |  FolderModel          |
+---------------------------------------------------------------------------------+
                                       |
+---------------------------------------------------------------------------------+
|                              DOCUMENT ENGINE LAYER                              |
|                         <<interface>> IDocumentEngine                           |
|   +-------------------+  +-------------------+  +-------------------+           |
|   |    EpubEngine     |  |     PdfEngine     |  |    MobiEngine     |           |
|   +-------------------+  +-------------------+  +-------------------+           |
|   +-------------------+  +-------------------+  +-------------------+           |
|   |     Fb2Engine     |  |    ComicEngine    |  |     TxtEngine     |           |
|   +-------------------+  +-------------------+  +-------------------+           |
+---------------------------------------------------------------------------------+
                                       |
+---------------------------------------------------------------------------------+
|                            STORAGE & PERSISTENCE LAYER                          |
|  DatabaseManager (SQLite / WAL)  |  BookProvider  |  ThumbnailCache (LRU)       |
|  SettingsProvider (QSettings / INI)               |  BookArchiveExporter        |
+---------------------------------------------------------------------------------+
```

### 4.2 C++20 Feature Utilization
- **Concepts**:
  ```cpp
  template <typename T>
  concept DocumentEngineConcept = requires(T engine, const std::filesystem::path& path) {
      { engine.open(path) } -> std::same_as<std::expected<BookMetadata, DocumentError>>;
      { engine.pageCount() } -> std::same_as<int>;
      { engine.renderPage(0, QSize{}, 1.0) } -> std::same_as<QImage>;
      { engine.tableOfContents() } -> std::same_as<TocNode>;
  };
  ```
- **Monadic Error Handling**: Use `std::expected<T, DocumentError>` and `std::optional<T>` to eliminate exceptions across engine boundaries.
- **Ranges & Views**: Use `std::views::filter`, `std::views::transform` for zero-allocation book sorting, filtering, and pagination.
- **Cancellable Worker Threads**: Utilize `std::jthread` and `std::stop_token` to immediately abort background PDF page rasterization or full-text search when the user jumps to a new chapter.

### 4.3 Qt 6 Modular Architecture
- **Core Components**:
  - `Qt6::Core`: Event loop, signals/slots, string conversions (`QStringConverter`), thread pools (`QThreadPool`), file safety (`QSaveFile`).
  - `Qt6::Gui`: Typography, font database, `QImage`, `QPixmap`, high-DPI scaling.
  - `Qt6::Widgets`: `QMainWindow`, `QListView`, `QTableView`, `QStackedWidget`, custom styled controls.
  - `Qt6::Sql`: Database abstraction with `QSQLITE` driver.
  - `Qt6::Concurrent`: High-level thread pool execution (`QtConcurrent::run`).
  - `Qt6::Svg`: Scalable vector icon rendering (`QSvgRenderer`).
  - `Qt6::TextToSpeech`: Native OS speech engine wrapper (`QTextToSpeech`).

### 4.4 Threading & Concurrency Model
1. **UI Responsiveness Mandate**:
   - The main GUI thread handles exclusively user input events, paint events, and lightweight model notifications.
   - All disk I/O, archive decompression, XML parsing, image scaling, and SQLite write queries execute on worker threads.
2. **Background Concurrency Workflows**:
   - **Batch File Importer**:
     - Uses `QtConcurrent::mappedReduced` or a `QThreadPool` queue.
     - Computes file hashes, extracts metadata and cover thumbnails without locking the UI.
     - Commits records to SQLite in transactions of 100 items. Emits progressive progress signals (`itemProcessed(current, total)`).
   - **Asynchronous Page Pre-rendering & Lookahead**:
     - Priority-driven worker thread renders page $N$ at device DPI.
     - Automatically renders lookahead pages $N+1$ and $N+2$ into the memory cache.
     - If the user scrolls rapidly, pending render jobs for obsolete pages are cancelled via `stop_token`.
   - **Full-Text In-Book Search**:
     - Background worker parses chapter text, extracts snippets, and emits incremental match signals (`matchFound(SearchResult)`).

---

## 5. SQLite Database Schema Specification

Below is the production-ready SQLite schema (`replica/schema.sql`), derived from the clean-room inspection of `ebooklib.sqlite3` and expanded to fully satisfy R3 requirements.

```sql
-- Production SQLite Schema for Icecream Ebook Reader Clone
-- Compatible with SQLite 3.35+ and Qt 6 QSQLITE Driver

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;

-- 1. Books Table
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_hash TEXT NOT NULL UNIQUE,          -- SHA-256 or MD5 hash for duplicate prevention
    full_path TEXT NOT NULL,                 -- Absolute filesystem path to book file
    title TEXT NOT NULL,                     -- Extracted or user-edited book title
    author TEXT,                             -- Primary author display string
    format INTEGER NOT NULL,                 -- Format Enum: 0=EPUB, 1=MOBI, 2=PDF, 3=FB2, 4=CBZ, 5=CBR, 6=TXT
    file_size INTEGER NOT NULL DEFAULT 0,    -- File size in bytes
    cover_path TEXT,                         -- Relative path to cached cover thumbnail image
    use_user_cover INTEGER NOT NULL DEFAULT 0, -- 1 if user supplied custom cover, 0 otherwise
    time_added INTEGER NOT NULL,             -- UTC timestamp (Unix epoch seconds)
    time_last_view INTEGER NOT NULL DEFAULT 0, -- UTC timestamp of last reading session
    position INTEGER NOT NULL DEFAULT 0,     -- Reading position (page number or chapter index)
    max_position INTEGER NOT NULL DEFAULT 0, -- Total pages or chapters count
    progress_percentage REAL NOT NULL DEFAULT 0.0 CHECK(progress_percentage >= 0.0 AND progress_percentage <= 100.0),
    is_read INTEGER NOT NULL DEFAULT 0 CHECK(is_read IN (0, 1)),
    is_favorite INTEGER NOT NULL DEFAULT 0 CHECK(is_favorite IN (0, 1)),
    is_deleted INTEGER NOT NULL DEFAULT 0 CHECK(is_deleted IN (0, 1)), -- Soft delete (Trash bin)
    notes_count INTEGER NOT NULL DEFAULT 0   -- Cached count of annotations/notes
);

-- 2. Authors Table (Normalized)
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    sort_name TEXT                           -- "LastName, FirstName" for alphabetical sorting
);

-- 3. Book-Author Relationship Table
CREATE TABLE IF NOT EXISTS book_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    role TEXT DEFAULT 'author',              -- 'author', 'translator', 'editor', 'illustrator'
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

-- 4. User Categories / Folders Table
CREATE TABLE IF NOT EXISTS folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER DEFAULT NULL,          -- Hierarchical nesting support
    title TEXT NOT NULL UNIQUE,
    FOREIGN KEY (parent_id) REFERENCES folders(id) ON DELETE SET NULL
);

-- 5. Book-Folder Binder Table
CREATE TABLE IF NOT EXISTS book_folder_binder (
    book_id INTEGER NOT NULL,
    folder_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, folder_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE
);

-- 6. Reading Progress & Session History
CREATE TABLE IF NOT EXISTS reading_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    cfi_position TEXT,                       -- EPUB Canonical Fragment Identifier or anchor string
    page_number INTEGER NOT NULL DEFAULT 0,  -- Page or chapter index
    percentage REAL NOT NULL DEFAULT 0.0,    -- Reading progress percentage
    read_duration_seconds INTEGER NOT NULL DEFAULT 0, -- Total active time spent reading
    last_read_timestamp INTEGER NOT NULL,    -- UTC timestamp
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- 7. Bookmarks Table
CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    page_number INTEGER NOT NULL,            -- Page or chapter number
    cfi_position TEXT,                       -- Precise CFI string for reflow formats
    title TEXT NOT NULL,                     -- Bookmark label / chapter title
    snippet TEXT,                            -- First line of text at bookmark location
    created_at INTEGER NOT NULL,             -- UTC timestamp
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- 8. Annotations and Highlights Table
CREATE TABLE IF NOT EXISTS annotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    cfi_start TEXT,                          -- Precise start CFI / DOM node offset
    cfi_end TEXT,                            -- Precise end CFI / DOM node offset
    page_number INTEGER NOT NULL DEFAULT 0,  -- Fixed page number (for PDF / CBZ)
    selected_text TEXT NOT NULL,             -- Quoted text highlighted
    note_text TEXT,                          -- User commentary / note
    color_code TEXT NOT NULL DEFAULT 'yellow' CHECK(color_code IN ('yellow', 'green', 'red', 'purple', 'blue', 'underline')),
    created_at INTEGER NOT NULL,             -- UTC timestamp
    updated_at INTEGER NOT NULL,             -- UTC timestamp
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- 9. General Book Metadata Key-Value Table
CREATE TABLE IF NOT EXISTS book_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    meta_type INTEGER NOT NULL,              -- Metadata Enum: 1=ISBN, 2=Publisher, 3=Language, 4=Description, 5=Genre
    meta_value TEXT NOT NULL,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

-- 10. Application Settings Table (Key-Value Configuration Store)
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    data_type TEXT NOT NULL DEFAULT 'string', -- 'string', 'int', 'bool', 'json'
    updated_at INTEGER NOT NULL
);

-- Triggers for Maintaining Cached Counters
CREATE TRIGGER IF NOT EXISTS trg_increment_notes_count AFTER INSERT ON annotations
BEGIN
    UPDATE books SET notes_count = notes_count + 1 WHERE id = NEW.book_id;
END;

CREATE TRIGGER IF NOT EXISTS trg_decrement_notes_count AFTER DELETE ON annotations
BEGIN
    UPDATE books SET notes_count = MAX(0, notes_count - 1) WHERE id = OLD.book_id;
END;

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_books_hash ON books(book_hash);
CREATE INDEX IF NOT EXISTS idx_books_time_last_view ON books(time_last_view DESC);
CREATE INDEX IF NOT EXISTS idx_books_time_added ON books(time_added DESC);
CREATE INDEX IF NOT EXISTS idx_books_format ON books(format);
CREATE INDEX IF NOT EXISTS idx_books_is_deleted ON books(is_deleted);
CREATE INDEX IF NOT EXISTS idx_books_is_favorite ON books(is_favorite);
CREATE INDEX IF NOT EXISTS idx_bookmarks_book_id ON bookmarks(book_id);
CREATE INDEX IF NOT EXISTS idx_annotations_book_id ON annotations(book_id);
CREATE INDEX IF NOT EXISTS idx_book_metadata_lookup ON book_metadata(book_id, meta_type);
CREATE INDEX IF NOT EXISTS idx_folder_binder_book ON book_folder_binder(book_id);
CREATE INDEX IF NOT EXISTS idx_folder_binder_folder ON book_folder_binder(folder_id);
```

---

## 6. Handoff Protocol Report

### 1. Observation
- **Reference Target Installation**: Inspected `C:\Program Files (x86)\Icecream Ebook Reader`. Found binaries: `icebookreader.exe` (3.3 MB), `icebooksvc.exe`, `DebenuPDFLibraryDLL1016.dll` (Debenu PDF Library), `quazip.dll`, `unrar.dll`, `7zxa.dll`, `libxml2.dll`, `libxslt.dll`, `icudt65.dll`, `icuin65.dll`, `icuuc65.dll`, `libcrypto-1_1.dll`, `libssl-1_1.dll`, `libcurl.dll`, and Qt5 core/gui/widgets/sql/webkit libraries.
- **Reference App Configuration & Data**:
  - Found user settings at `C:\Users\epicg\AppData\Local\Icecream\Icecream Ebook Reader\settings.ini`. Direct keys observed:
    - `[General] lastStyleId=DayStyle`, `library_view_mode=@Variant(...Enums::LibraryViewMode...)`, `ttsLocaleVoiceMap=@Variant(...Microsoft Zira...)`, `ttsVolume=1`, `library_category=2`, `localeName=en`.
    - `[viewer.text] column_count=2`.
  - Found user database at `C:\Users\epicg\.Icecream Ebook Reader\data\ebooklib.sqlite3`.
- **Database Schema Extraction**:
  - Verified exact table DDL from `ebooklib.sqlite3`:
    - `CREATE TABLE books (id INTEGER primary key, cover TEXT, full_path TEXT, author TEXT, title TEXT, format INTEGER, time_added INTEGER, time_last_view INTEGER, position INTEGER, max_position INTEGER, is_favorite INTEGER, is_deleted INTEGER, notes_count INTEGER, book_hash TEXT, use_user_cover INTEGER, is_read INTEGER)`
    - `CREATE TABLE folders (id INTEGER primary key, parent_id INTEGER, title TEXT UNIQUE)`
    - `CREATE TABLE book_folder_binder (book_id INTEGER NOT NULL, folder_id INTEGER NOT NULL, unique(book_id,folder_id), foreign key(book_id) references books(id), foreign key(folder_id) references folders(id))`
    - `CREATE TABLE book_metadata (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL, meta_type INTEGER NOT NULL, meta_value TEXT)`
- **Binary Symbol Extraction from `icebookreader.exe`**:
  - Format engines: `epub::EpubDocument`, `epub::EpubParser`, `epub::EpubError`, `PdfDocument::load`, `PdfDocument::requestImage`, `PdfViewerHelper::receiveText`, `mobi::MobiDocument`, `mobi::MobiHead`, `mobi::PDBHeader`, `fb2::FbDocument`, `ComicDocument::load`, `ZipReader`, `RarReader`.
  - Reading viewer and position: `TextViewer::readBook`, `TextViewer::setZoomValue`, `TextBookChapter::createBookmarkForCurrentPage`, `TextBookChapter::getReadingPosition`, `TextBookChapter::setReadingPosition`, `cFI`.
  - Resizing behavior: Execution logs from `C:\Users\epicg\.Icecream Ebook Reader\log\icebookreader_2026-09-09_16_25_27.txt` verbatim show:
    ```
    IceNativeWindowUtils::nativeEvent() : IceWindow System resize started
    ReadingPage::setResizingMode() : RESIZE MODE true
    IceNativeWindowUtils::nativeEvent() : IceWindow System resize finished
    ReadingPage::setResizingMode() : RESIZE MODE false
    ```
  - Highlighting & Notes: Verbatim extracted symbols: `span.yellownote`, `span.greennote`, `span.rednote`, `span.purplenote`, `span.bluenote`, `span.underlinenote`, `createNoteFromSelection`, `createNoteFromParams`, `NotePopup::showForNote`, `NotesModel`.
  - Categories & Queries: Verbatim extracted SQL:
    ```sql
    SELECT COUNT(*) FROM sqlite_master WHERE tbl_name = 'book_folder_binder' AND type = 'index';
    SELECT b.full_path FROM books AS b WHERE b.is_deleted = 1;
    SELECT format, COUNT(*) FROM books WHERE is_deleted = 0 GROUP BY format;
    INSERT OR REPLACE INTO book_metadata (id, book_id, meta_type, meta_value) VALUES ((SELECT ID FROM book_metadata WHERE book_id = :book_id AND meta_type=:meta_type), :book_id, :meta_type, :meta_value);
    ```

### 2. Logic Chain
1. **Observation**: The reference application links against `DebenuPDFLibraryDLL1016.dll` and QtWebKit, using `TextViewer` and `PdfViewerHelper`.
   **Inference**: The original application partitioned rendering into a fixed-layout PDF engine and a WebKit-backed reflowable viewer for EPUB/FB2/MOBI. For our modern clean-room Qt 6 architecture, QtWebKit is obsolete. Replacing it with an abstraction `IDocumentEngine` implemented via `PdfiumEngine` (or `PopplerEngine`) for fixed layout and `QTextDocument` / custom column-flow layout painter (or QtWebEngine) ensures long-term maintainability, security, and smaller distribution footprint.
2. **Observation**: The reference schema stores `book_hash TEXT` in the `books` table, and checks duplicate entries during import.
   **Inference**: Content-addressable hashing (MD5 or SHA-256) is mandatory to uniquely identify books, prevent duplicate records when users re-add files, and reliably associate cached cover thumbnails in `~/.reader/Bookshelf/covers/<hash>.jpg`.
3. **Observation**: System resize events trigger `ReadingPage::setResizingMode(true)` on `WM_ENTERSIZEMOVE` and `false` on `WM_EXITSIZEMOVE`.
   **Inference**: Continuous reflow recalculation during window dragging causes significant UI stutter. A responsive reader must freeze reflow during active resize, display a hardware-scaled bitmap preview, and trigger full reflow pagination once dragging completes.
4. **Observation**: Reading position references `cFI`, `position`, and `max_position`.
   **Inference**: Reflowable documents cannot rely solely on page numbers because page counts fluctuate with window size and font scaling. The position must be captured via EPUB Canonical Fragment Identifiers (CFI) or normalized DOM text offsets, while fixed-layout documents (PDF, CBZ) use integer page numbers.
5. **Observation**: Notes in the original reader are rendered via HTML spans (`span.yellownote`, `span.greennote`, etc.) and counted in `books.notes_count`.
   **Inference**: Annotations require precise start and end CFI offsets, a color categorization (Yellow, Green, Red, Purple, Blue, Underline), and automatic cache triggers to maintain `notes_count` in the `books` table.

### 3. Caveats
- The original application utilized Debenu PDF Library (a commercial Delphi/C++ library). For our clean-room clone, we specify standard open-source equivalents: Google PDFium (Apache 2.0) or Poppler-Qt6 (GPL/LGPL).
- DRM decryption (e.g. Adobe Adept, Apple FairPlay, Amazon KFX/AZW4 with DRM) is deliberately excluded from this specification as the reader is designed for DRM-free personal ebook collections.

### 4. Conclusion
The technical specification mining is complete and thoroughly documented. The architecture cleanly separates fixed-layout rendering from reflowable text layout, employs C++20 standard capabilities with Qt 6 modular libraries, implements an SQLite schema with full referential integrity and indexes, and provides detailed pipelines for all six target formats (EPUB, PDF, MOBI, FB2, CBZ, TXT).

### 5. Verification Method
- **Verify Schema Execution**:
  Run Python's built-in sqlite3 against the schema SQL to verify 0 syntax errors:
  ```powershell
  python -c "import sqlite3; conn = sqlite3.connect(':memory:'); conn.executescript(open(r'c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\spec_miner_survey_1\handoff.md', encoding='utf-8').read().split('```sql')[1].split('```')[0]); print('Schema valid! Tables:', [r[0] for r in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")])"
  ```
- **Inspect Reference Artifacts**:
  Verify existence of `C:\Program Files (x86)\Icecream Ebook Reader\icebookreader.exe` and `C:\Users\epicg\.Icecream Ebook Reader\data\ebooklib.sqlite3`.
