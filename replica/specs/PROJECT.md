# Project: Icecream Ebook Reader Replica (Clean-Room C++20 / Qt 6)

## Architecture Overview
The project is a clean-room modern C++20 and Qt 6 desktop ebook reader replicating the features, UX patterns, and data persistence of Icecream Ebook Reader.
It eliminates legacy 32-bit architecture and QtWebKit dependencies in favor of modern in-process asynchronous document engines, modern Qt 6 widgets/canvas rendering, and a robust SQLite 3 persistence layer.

### System Layers
1. **Presentation Layer (Qt 6 Widgets / QGraphicsView)**:
   - Main application window, collapsible navigation drawer, dual-mode reading canvas (reflowable text vs. fixed-layout page rendering).
   - Unified styling engine (Day, Night, Light Sepia, Dark Sepia).
2. **Application Core & Controller Layer**:
   - `BookContext`, `LibraryManager`, `BookmarkManager`, `AnnotationManager`, `TtsController`.
   - Thread coordination and non-blocking asynchronous task execution via `std::jthread` and `QThreadPool`.
3. **Document Engine Abstraction (`IDocumentEngine`)**:
   - `ReflowableDocumentEngine`: EPUB (2 & 3), MOBI/AZW/PRC, FB2, TXT.
   - `FixedLayoutDocumentEngine`: PDF, CBZ/CBR.
   - Text extraction, EPUB Canonical Fragment Identifier (CFI) position tracking, table of contents extraction, full-text search.
4. **Storage & Persistence Layer**:
   - SQLite 3 database (`ebooklib.sqlite3`) with WAL journal mode.
   - INI configuration (`settings.ini`) for user preferences, window geometry, and hotkeys.
   - Disk thumbnail cache for book covers and bookmarks.

---

## Feature Inventory
Every feature identified during Phase 0 Survey mapped to its respective delivery milestone:

| # | Feature | Category | Priority | Milestone | Source |
|---|---------|----------|----------|-----------|--------|
| 1 | EPUB 2.0.1 / 3.2 Ingestion & Rendering | Format Engine | Must | M1, M2 | survey (spec_miner, explorer_1) |
| 2 | PDF Document Rendering & Viewport Scaling | Format Engine | Must | M1, M2 | survey (spec_miner, explorer_1) |
| 3 | MOBI / PRC / AZW PalmDOC Decompression | Format Engine | Must | M1, M2 | survey (spec_miner, explorer_1) |
| 4 | FB2 XML Parsing & Base64 Cover Extraction | Format Engine | Must | M1, M2 | survey (spec_miner, explorer_1) |
| 5 | CBZ / CBR Comic Book Archive Extraction | Format Engine | Must | M1, M2 | survey (spec_miner, explorer_1) |
| 6 | TXT Charset Detection & Paragraph Reflow | Format Engine | Must | M1, M2 | survey (spec_miner, explorer_1) |
| 7 | Screen Inventory (S01–S12) Specification | UX / Recon | Must | M1 | survey (explorer_2) |
| 8 | User Flows (F01–F10) Specification | UX / Recon | Must | M1 | survey (explorer_2) |
| 9 | UI Component Catalog & State Machine | UX / Recon | Must | M1 | survey (explorer_2) |
| 10 | Categorized Feature Matrix (Must/Should/Could) | UX / Recon | Must | M1 | survey (explorer_2, spec_miner) |
| 11 | Single & 2-Page Spread Reading Layouts | Reading Engine | Must | M1, M2 | survey (explorer_1, explorer_2) |
| 12 | Reading Position Tracking (Page & CFI) | Reading Engine | Must | M1, M2, M3 | survey (spec_miner, explorer_1) |
| 13 | Interactive Resizing Suspension Mechanism | Reading Engine | Must | M2 | survey (spec_miner, explorer_1) |
| 14 | Hierarchical Table of Contents (TOC) | Navigation | Must | M1, M2 | survey (explorer_2, spec_miner) |
| 15 | Page & Fragment Bookmarking | Annotations | Must | M1, M2, M3 | survey (explorer_2, spec_miner) |
| 16 | Text Highlighting & Notes (5 Colors) | Annotations | Must | M1, M2, M3 | survey (explorer_2, spec_miner) |
| 17 | In-Book Asynchronous Full-Text Search | Navigation | Must | M1, M2 | survey (explorer_2, spec_miner) |
| 18 | Multi-View Library (Cards Grid & Table List) | Library | Must | M1, M2 | survey (explorer_2, explorer_1) |
| 19 | Library Category & User Folder Hierarchy | Library | Must | M1, M2, M3 | survey (explorer_1, spec_miner) |
| 20 | Book Deduplication by Content Hash (SHA-256) | Library / Data | Must | M1, M2, M3 | survey (spec_miner, explorer_1) |
| 21 | Soft Deletion & Trash Management | Library / Data | Must | M1, M2, M3 | survey (explorer_1, spec_miner) |
| 22 | Reading Themes (Day, Night, Sepia) | Customization | Must | M1, M2 | survey (explorer_2, explorer_1) |
| 23 | Typography & Margin Customization | Customization | Must | M1, M2 | survey (explorer_2) |
| 24 | Fullscreen Distraction-Free Reading Mode | UX | Should | M1, M2 | survey (explorer_2) |
| 25 | Text-to-Speech (TTS) Narration Engine | Accessibility | Should | M1, M2 | survey (explorer_2, spec_miner) |
| 26 | Book Properties & Custom Cover Editing | Library | Should | M1, M2, M3 | survey (explorer_2, explorer_1) |
| 27 | Reading Progress Statistics & Reading Time | Analytics | Could | M1, M2, M3 | survey (spec_miner) |
| 28 | Export / Import Library Archive (.EBR) | Data Portability | Should | M1, M2 | survey (explorer_1, explorer_2) |
| 29 | Export Notes & Highlights to HTML / Text | Data Portability | Should | M1, M2 | survey (explorer_2) |
| 30 | Production SQLite Schema DDL & Constraints | Persistence | Must | M3 | survey (spec_miner, explorer_1) |
| 31 | Foreign Keys with Explicit ON DELETE Rules | Persistence | Must | M3 | survey (spec_miner, explorer_1) |
| 32 | Query Optimization & Lookup Indexes | Persistence | Must | M3 | survey (spec_miner, explorer_1) |
| 33 | Modern C++20 / Qt 6 Concurrency & Threading Model | Architecture | Must | M2 | survey (spec_miner, explorer_1) |
| 34 | Edge Case & Malformed File Handling Protocols | Architecture | Must | M2 | survey (spec_miner) |
| 35 | Phased Implementation Roadmap & Vertical Slice | Roadmap | Must | M2 | survey (spec_miner, explorer_2) |

---

## Milestones

| # | Name | Scope | Dependencies | Deliverables | Status |
|---|------|-------|-------------|--------------|--------|
| M1 | Reconnaissance & Feature Matrix | Screen inventory (S01–S12), user flows (F01–F10), component list, format pipeline, feature matrix CSV | Phase 0 Survey | `replica/recon.md`, `replica/features.csv` | DONE |
| M2 | C++20 / Qt 6 Architecture Specification | Modern layer architecture, library tradeoffs, threading model, edge case handling, phased roadmap | M1 | `replica/architecture.md` | DONE |
| M3 | SQLite Schema Design & DDL Verification | Full database DDL, tables, constraints, indexes, triggers, sqlite3 test execution | M1 | `replica/schema.sql` | DONE |
| M4 | Comprehensive Verification & Forensic Audit | Reviewers, Challengers (adversarial test cases), Forensic Auditor (clean-room integrity verification) | M1, M2, M3 | `GATE_STATUS.md`, audit handoffs | DONE |

---

## Code Layout
Deliverables directory structure:
```
c:\Users\epicg\Downloads\icecream_ebook_reader_replica\
├── ORIGINAL_REQUEST.md
├── PROJECT.md
├── replica/
│   ├── recon.md           (Screen inventory, flows, components, format pipelines)
│   ├── features.csv       (Feature matrix categorized by Must/Should/Could)
│   ├── architecture.md    (C++20 & Qt 6 architecture, threading, edge cases, roadmap)
│   └── schema.sql         (Production SQLite database schema DDL)
└── .agents/teamwork/
    ├── orchestrator_1/
    ├── explorer_survey_1/
    ├── explorer_survey_2/
    ├── spec_miner_survey_1/
    └── ...
```
