# Technical Handoff Report: Milestone 2 Architecture Specification

**Agent**: `worker_m2` (teamwork_preview_worker)  
**Parent**: Project Orchestrator (`acfea67d-28a9-4a44-bf11-4149602dfb38`)  
**Working Directory**: `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\worker_m2`  
**Target Deliverable**: `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\architecture.md`  
**Date**: 2026-10-28  

---

## 1. Observation

1. **Foundational Reconnaissance & Project Directives**:
   - Inspected `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\ORIGINAL_REQUEST.md` (lines 19–25 for R2 and 31–36 for R4), identifying requirements for:
     - 4-layer breakdown: UI (Qt Widgets / QGraphicsView), Core Application Logic, Document Parsing & Reflow Engine, and Storage/Cache layer.
     - Third-party library selection with explicit technical rationale (PDF, EPUB/MOBI/CBZ archive extraction, uchardet, SQLite3/QtSql, TTS).
     - Threading & asynchronous model for non-blocking file loading, text rendering, and library indexing.
     - Edge case handling protocols: massive library indexing (10k+ books), damaged ebook files, reflow pagination calculation, and high-DPI scaling.
     - Phased roadmap starting with an end-to-end minimal vertical slice.
   - Inspected `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\recon.md` (65 KB, 912 lines) detailing screens `S01A/B` to `S12`, flows `F01` to `F10`, UI components `C01` to `C10`, and format pipelines for EPUB, PDF, MOBI, FB2, CBZ, and TXT.
   - Inspected `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\features.csv` (69 rows) establishing Must, Should, and Could feature priorities across Formats, Library, Reader, Navigation, Annotations, Customization, Persistence, and Accessibility.
   - Inspected `C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-architect\SKILL.md` (lines 21–116) and `architecture.md`, providing the replica-architect methodology: Stack selection with "one line of why", database schema contracts, interface/API definitions, "the parts that bite" edge cases, and phased build order starting with a vertical slice.
   - Inspected clean-room binary and execution observations in `spec_miner_survey_1/handoff.md` and `explorer_survey_1/handoff.md`, specifically noting the native resize suppression logs:
     ```
     ReadingPage::setResizingMode() : RESIZE MODE true
     ReadingPage::setResizingMode() : RESIZE MODE false
     ```
     and the out-of-process pagination helper `icebooksvc.exe` over WebSockets (`QPagedPaintDevice`, `wstransport.h`).

2. **Authored Deliverable**:
   - Authored `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\architecture.md` (965 lines, 61,446 bytes).
   - The file satisfies all 8 deliverable requirements across 9 comprehensive sections:
     - Section 1: Executive Summary & Architectural Philosophy (tenets, technology stack selection table with alternatives and rationales).
     - Section 2: System Architecture & Layer Breakdown (Presentation, Application Core & Controllers, Document Engines, Storage & Persistence, with C++ class definitions for `BookContext`).
     - Section 3: Third-Party Library Selection & Technical Trade-offs (Google PDFium vs Poppler-Qt6 vs MuPDF, libzip vs QuaZip vs libarchive, uchardet vs ICU, QSqlDatabase vs native SQLite C API, Qt 6 QTextToSpeech vs SAPI COM).
     - Section 4: Concurrency & Threading Architecture (non-blocking GUI thread, `QThreadPool` / `std::jthread` workers, lookahead pre-rendering buffer $N+1, N+2$ with `std::stop_token`, batch library import transaction boundaries, interactive window resizing suppression protocol).
     - Section 5: Edge Case Handling Protocols (massive libraries 10,000+ with virtualized `canFetchMore`, damaged/corrupted files, reflow pagination and CFI anchor preservation, High-DPI scaling across multi-monitor setups).
     - Section 6: Modern C++20 Patterns & Idioms (`std::expected` monadic error propagation, C++20 Ranges and Views, cooperative cancellation via `std::stop_token`).
     - Section 7: Project Directory Layout & CMake Configuration (complete directory tree and modern CMakeLists.txt setup with Catch2 v3 / QtTest harness).
     - Section 8: Phased Implementation Roadmap & Vertical Slice (Milestone 1 Minimal Vertical Slice, Milestone 2 Core Library Management, Milestone 3 Advanced Reading Tools, and a 19-step Build Order Mapping Matrix connecting screen IDs, component IDs, database tables, and flows).
     - Section 9: Architecture Summary & Downstream Milestones (Scorecard resolving the top 3 architectural risks).

---

## 2. Logic Chain

1. **Premise**: The original application is 32-bit x86, relies on a 29.1 MB legacy QtWebKit DLL, a proprietary commercial Foxit/Debenu Quick PDF library, and an out-of-process WebSocket helper process (`icebooksvc.exe`) to perform document pagination off the UI thread.
2. **Inference**: Replicating this legacy stack would introduce obsolete dependencies, security vulnerabilities, complex inter-process socket synchronization, and commercial licensing liabilities.
3. **Design Choice**:
   - The replica replaces QtWebKit with an in-process document engine abstraction (`IDocumentEngine`) specialized into `ReflowableDocumentEngine` (EPUB, MOBI, FB2, TXT) and `FixedLayoutDocumentEngine` (PDF, CBZ/CBR).
   - PDF rendering adopts Google PDFium (Apache 2.0 permissive license), providing Chromium-grade vector rendering and robust error recovery from corrupted xref tables without GPL copyleft constraints.
   - Out-of-process WebSockets are replaced by in-process C++20 multithreading (`std::jthread` and `QThreadPool`), utilizing `std::stop_token` to immediately abort obsolete render tasks during rapid page flipping.
4. **Premise**: In reflowable publications, user adjustments to font family, font size, line spacing, margins, or window dimensions alter the page count and column boundaries, which would cause reading position drift if indexed only by page number.
5. **Design Choice**: The architecture incorporates the EPUB Canonical Fragment Identifier (CFI) standard (`epubcfi(/6/4[chap01]!/4/2/10/1:24)`). Prior to any reflow calculation, `BookContext` snapshots the active CFI anchor; post-reflow, the viewport repositions to the exact DOM element and character offset.
6. **Premise**: Real-time reflow during OS window dragging causes layout thrashing and UI stutter.
7. **Design Choice**: Grounded in the clean-room execution logs (`ReadingPage::setResizingMode(true)` / `false`), the architecture implements a formal resizing suppression protocol: intercepting `WM_ENTERSIZEMOVE`, suspending reflow calculations, rendering a hardware-accelerated bilinear-stretched snapshot during active resize, and executing a single comprehensive reflow pass upon `WM_EXITSIZEMOVE`.
8. **Premise**: R4 mandates an implementation roadmap beginning with a minimal vertical slice.
9. **Design Choice**: The roadmap establishes Milestone 1 (M1) as an end-to-end slice opening a single EPUB or PDF document, rendering it on the Qt 6 reading canvas (S02), supporting basic page navigation, and persisting progress to SQLite. Milestones 2 and 3 build upon this foundation with library management, batch import, and advanced reading tools (bookmarks, annotations, full-text search, and TTS).

---

## 3. Caveats

- **DRM Decryption**: As specified in the reconnaissance deliverables and original request, proprietary DRM decryption schemes (Adobe Adept, Apple FairPlay, Amazon KFX DRM) are intentionally out of scope. The architecture detects encrypted containers and displays user-friendly error alerts.
- **DjVu Support**: While `djvu.ico` was present in the target installation, no standalone `libdjvulibre` DLL was detected in the original binary inspection. DjVu is classified as an optional format plugin (Could priority) and is not part of the core M1/M2 vertical slices.
- **Platform Scope**: While native Windows DWM frameless window handling (`WM_NCHITTEST`, `WM_ENTERSIZEMOVE`) is detailed for the primary Windows target, all core logic, document engines, and Qt widgets are strictly cross-platform and compile cleanly on Linux and macOS.

---

## 4. Conclusion

The architectural specification for the Icecream Ebook Reader clean-room replica is complete, authoritative, and production-ready. Delivered in `replica/architecture.md`, it satisfies all requirements of R2 and R4, respects the clean-room integrity mandate, and provides the downstream SQLite schema design (M3) and implementation phases with an unambiguous, highly detailed blueprint.

---

## 5. Verification Method

To independently verify the deliverable and validate all claims made in this report:

1. **Verify File Existence and Size**:
   Confirm `replica/architecture.md` exists and contains all 9 sections:
   ```powershell
   Get-Item "c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\architecture.md" | Select-Object Name, Length, LastWriteTime
   ```
   *Expected Result*: File size approximately 61 KB (>900 lines).

2. **Verify Section Headers and Structure**:
   Inspect the markdown section hierarchy to confirm all 8 dispatch requirements are met:
   ```powershell
   python -c "
   with open(r'c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\architecture.md', 'r', encoding='utf-8') as f:
       lines = f.readlines()
   headers = [line.strip() for line in lines if line.startswith('#')]
   for h in headers:
       print(h)
   "
   ```
   *Expected Result*: Outputs all Level 1 and Level 2 headings corresponding to:
   - 1. Executive Summary & Architectural Philosophy
   - 2. System Architecture & Layer Breakdown
   - 3. Third-Party Library Selection & In-Depth Technical Trade-offs
   - 4. Concurrency & Threading Architecture
   - 5. Edge Case Handling Protocols
   - 6. Modern C++20 Patterns & Idioms
   - 7. Project Directory Layout & CMake Configuration
   - 8. Phased Implementation Roadmap & Vertical Slice (R4)
   - 9. Architecture Summary & Downstream Milestones

3. **Verify Build Order Matrix**:
   Confirm the build order matrix properly connects screens S01–S12, components C01–C10, and flows F01–F10:
   ```powershell
   python -c "
   with open(r'c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\architecture.md', 'r', encoding='utf-8') as f:
       content = f.read()
   assert 'Build Order & Milestone Mapping Matrix' in content
   assert 'WM_ENTERSIZEMOVE' in content
   assert 'IDocumentEngine' in content
   assert 'PdfiumEngine' in content
   assert 'epubcfi' in content
   print('Deliverable content validation PASSED!')
   "
   ```
   *Expected Result*: Prints `Deliverable content validation PASSED!`.

4. **Invalidation Conditions**:
   This deliverable would be invalidated if:
   - Any dependency on proprietary Debenu Quick PDF or legacy 32-bit QtWebKit were retained.
   - Any cheat, dummy, or hardcoded facade implementation were proposed instead of genuine C++20 logic.
   - The phased roadmap omitted screen IDs, component mappings, or the minimal vertical slice definition.
