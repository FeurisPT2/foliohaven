## 2026-10-28T14:34:24Z
You are spec_miner_survey_1, a teamwork_preview_spec_miner.
Your working directory is: c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\spec_miner_survey_1
Your parent is the Project Orchestrator (conversation ID: acfea67d-28a9-4a44-bf11-4149602dfb38).

MANDATORY FIRST STEP:
Read the project requirements at: c:\Users\epicg\Downloads\icecream_ebook_reader_replica\ORIGINAL_REQUEST.md
Also read the replica-architect methodology at: C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-architect\SKILL.md

YOUR MISSION:
Mine technical specifications, format handling requirements, modern C++20 / Qt 6 architecture patterns, and SQLite database schema entities for an ebook reader clone supporting EPUB, PDF, MOBI, FB2, CBZ, and TXT.

MINE AND SPECIFY:
1. Format Handling Pipeline:
   - EPUB (2 & 3): Container XML, OPF package, manifest, spine, NCX / Nav Doc, XHTML parsing, CSS styling, EPUB Canonical Fragment Identifiers (CFI) for position tracking.
   - PDF: Page-based rendering, viewport scaling, text extraction, outline/TOC extraction. Library choice: Poppler (poppler-cpp or poppler-qt6) vs MuPDF / PDFium.
   - MOBI/AZW/PRC: PalmDOC header, Mobipocket record structure, uncompressed/LZ77 text extraction, EXTH metadata header.
   - FB2 (FictionBook 2.0): XML schema, binary base64 embedded covers, section-based DOM, genre taxonomy.
   - CBZ: ZIP container inspection (libzip / QuaZip / zlib), archive image ordering, metadata (ComicInfo.xml if present).
   - TXT: Character encoding detection (uchardet / ICU / Qt QStringConverter), heuristic paragraph reflow.
2. Architecture & Concurrency Model:
   - Modern C++20 features (concepts, ranges, coroutines/std::jthread if applicable, std::expected/optional).
   - Qt 6 architecture: Core, Gui, Widgets, Sql, Concurrent, Svg.
   - Threading model: UI thread responsiveness, worker threads for background file parsing, page pre-rendering, thumbnail generation, full-text search indexing.
   - Edge case handling: massive libraries (10k+ books), damaged/malformed files, reflow pagination under window resize, high-DPI scaling.
3. Database Entity Requirements for SQLite:
   - Entities: books, authors, categories/tags, reading_lists, reading_progress (CFI, page, percentage, timestamps), bookmarks, annotations/highlights, app_settings.
   - Constraints, foreign keys, unique indices, query patterns.

DELIVERABLE:
Write your full technical specification mining report to:
`c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\spec_miner_survey_1\handoff.md`

Send a summary message back to parent using send_message when done.
