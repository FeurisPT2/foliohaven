# Original User Request

## Initial Request — 2026-10-28T14:31:04Z

Reverse-engineer the feature set and UX patterns of Icecream Ebook Reader from the local installation at `C:\Program Files (x86)\Icecream Ebook Reader`, and design a complete C++ and Qt clean-room architecture specification and SQLite database schema for the clone.

Working directory: c:\Users\epicg\Downloads\icecream_ebook_reader_replica
Integrity mode: development

Reference target: C:\Program Files (x86)\Icecream Ebook Reader

## Requirements

### R1. Reconnaissance and Feature Matrix
Analyze the features, user flows, supported ebook formats (EPUB, PDF, MOBI, FB2, CBZ, TXT), and UI components of Icecream Ebook Reader (via clean-room examination of the local installation metadata, UI structure, and public documentation). Produce:
- `replica/recon.md`: Screen inventory (S-IDs), user flows (F-IDs), component list, and format handling pipeline.
- `replica/features.csv`: Categorized feature matrix with priority tiers (Must, Should, Could) and complexity estimates.

### R2. C++ & Qt Architecture Specification
Author `replica/architecture.md` detailing a modern C++ (C++20) and Qt 6 architecture:
- Layer breakdown: UI layer (Qt Widgets / QML), Core Application logic, Document Parsing & Reflow Engine, and Storage/Cache layer.
- Third-party library selection with rationale (e.g., Poppler/MuPDF for PDF, libzip/QuaZip for EPUB/CBZ extraction, uchardet for encoding detection, SQLite3/QtSql).
- Threading & asynchronous model for non-blocking file loading, text rendering, and library indexing.
- Edge case handling: large library indexing, damaged ebook files, reflow pagination calculation, and high-DPI scaling.

### R3. SQLite Database Schema & Data Model
Generate `replica/schema.sql` containing a production-ready SQLite database schema:
- Tables for books (metadata, file hash, format, covers), reading state (current position/CFI, page, progress percentage, last opened timestamp), bookmarks, annotations/highlights, reading lists/tags, and user preferences.
- Foreign keys with explicit `ON DELETE` rules, unique constraints (e.g. duplicate book prevention by hash), and indexes on frequent queries (recent books, search, author/category filters).

### R4. Phased Implementation Roadmap & Vertical Slice
Define a clear, phased build order in `replica/architecture.md`:
- Milestone 1: Minimal vertical slice (load and render a single EPUB and PDF, basic pagination, save progress to SQLite).
- Milestone 2: Core library management (grid/list view, book import, metadata extraction, search & filter).
- Milestone 3: Advanced reading tools (bookmarks, annotations, text search within books, themes/night mode).

## Acceptance Criteria

### Recon Deliverables
- [ ] `replica/recon.md` exists and includes screen inventory (S01+), key user flows (library browsing, book reading, bookmarking, customization), and component catalog.
- [ ] `replica/features.csv` exists, parses as valid CSV, and covers all core capabilities of Icecream Ebook Reader categorized into Must/Should/Could.

### Architecture Deliverables
- [ ] `replica/architecture.md` exists and specifies exact Qt 6 modules, recommended C++ libraries for PDF/EPUB/MOBI parsing, project directory layout, and class/service responsibilities.
- [ ] Concurrency and threading strategy is clearly documented (background worker threads for parsing/indexing to keep the UI thread responsive).

### Schema Deliverables
- [ ] `replica/schema.sql` exists and executes successfully in SQLite (`sqlite3` test execution produces 0 errors).
- [ ] Schema includes all foreign key constraints, indexes on lookup columns, and default timestamps in UTC.

### Roadmap Deliverables
- [ ] Step-by-step build order starting with an end-to-end vertical slice is explicitly detailed with screen IDs and component mappings.
