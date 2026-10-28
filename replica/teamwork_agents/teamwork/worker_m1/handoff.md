# Milestone 1 Handoff Report: Reconnaissance & Feature Matrix

**Agent**: `worker_m1` (teamwork_preview_worker)  
**Parent**: Project Orchestrator (`acfea67d-28a9-4a44-bf11-4149602dfb38`)  
**Working Directory**: `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\worker_m1`  
**Milestone**: M1 (Reconnaissance & Feature Matrix)  
**Date**: 2026-10-28  

---

## 1. Observation

Direct clean-room reconnaissance and technical survey inputs were gathered from:
- `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\ORIGINAL_REQUEST.md` (Requirements R1–R4, Acceptance Criteria)
- `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\PROJECT.md` (System layers, milestones M1–M4, code layout)
- `C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-recon\SKILL.md` (Template specifications, 9-step recon method)
- Survey reports:
  - `explorer_survey_1/handoff.md`: 84 files, 111 MB installation hierarchy, 291 RTTI classes, `icebooksvc.exe` helper process, SQLite schema in binary, keyboard shortcuts.
  - `explorer_survey_2/handoff.md`: 372 UI strings across 43 QTranslator contexts, screen inventory S01–S12, user flows F01–F10, 9 UI components.
  - `spec_miner_survey_1/handoff.md`: Deep format pipelines (EPUB, PDF, MOBI, FB2, CBZ, TXT), CFI position engine, PalmDOC LZ77 decompression, C++20 concurrency, SQLite schema DDL with 10 tables/triggers.

Under exclusive write ownership, the following two authoritative deliverables were authored:
1. **`c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\recon.md`** (Size: 65,188 bytes)
   - *Executive Summary*: Platform, core loop, format scope, technical comparison between original legacy 32-bit Qt 5 stack and modern 64-bit C++20 / Qt 6 clean-room stack.
   - *Sources Table*: 8 clean-room sources examined with exact paths and yields.
   - *Screen Inventory (S01–S12)*: Deep specifications of S01A (Grid), S01B (Table), S02 (Reader Canvas), S03 (Bookmarks), S04 (TOC), S05 (Notes), S06 (NotePopup), S07 (Quick Settings), S08 (Global Settings), S09 (Properties), S10 (Search), S11 (Print), S12 (Auxiliary Modals). Every screen documents routes, purpose, components, and states (empty, loading, populated, filtered, error, multi-select).
   - *User Flows (F01–F10)*: Step-by-step maps with screen transitions, decision points, click counts, and boundary edge cases (F01 Import, F02 Search/Filter, F03 Open & Read Core Loop, F04 Pagination & Reflow, F05 Bookmarks, F06 Highlighting/Notes/HTML Export, F07 Themes & Dimming, F08 Fullscreen, F09 TTS Narration, F10 .EBR Archive Backup).
   - *UI Component Catalog*: Reusable components C01–C09 (Sidebar, Header/Action bar, BookCardWidget, Table View, Operations footer, Reader toolbar, Reader scrubber footer, NotePopup, IceWindow/IceDialog) plus complete 25-shortcut hotkeys table C10.
   - *Format Handling Pipelines*: Complete specifications for EPUB (2 & 3, container, OPF manifest/spine, NCX/Nav, CFI), PDF (rasterization, DPI scaling, viewport culling, text bounding boxes), MOBI/AZW/PRC (PDB header, PalmDOC LZ77 decompressor, EXTH tags, image mapping), FB2 (XML streaming, embedded base64 covers, body sections, footnotes), CBZ/CBR (archive extraction, natural alphanumeric sorting, ComicInfo.xml), TXT (encoding detection uchardet/ICU/QStringConverter, heuristic paragraph reflow).
   - *Inferred Data Model*: Normalized entities (`books`, `authors`, `book_authors`, `folders`, `book_folder_binder`, `reading_progress`, `bookmarks`, `annotations`, `book_metadata`, `app_settings`) with field types, foreign keys, triggers, evidence, and confidence.
   - *Sizing & Non-Cloneable Features*: Honest exclusion analysis (DRM, closed proprietary DLLs like Debenu, proprietary cloud licensing); overall project sizing rated **M (Medium — 4 to 6 weeks)**.
2. **`c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\features.csv`** (67 rows, 7 columns)
   - RFC 4180 compliant CSV header: `feature,area,priority,original,clone,complexity,notes`.
   - 67 capability entries across 9 functional areas (`Formats`, `Library`, `Reader`, `Navigation`, `Annotations`, `Customization`, `Accessibility`, `Persistence`, `Output`).
   - Categorized into priority tiers: `Must` (44 features), `Should` (17 features), `Could` (6 features).
   - Complexity estimates: `S` (27), `M` (28), `L` (9), `XL` (3).
   - `original = yes`, `clone = planned`.

---

## 2. Logic Chain

1. **Clean-Room Survey Synthesis**:
   - *Observation*: Surveys by `explorer_1`, `explorer_2`, and `spec_miner_1` established ground-truth facts on binaries, DLLs, file structures, RTTI classes, SQLite schemas, UI strings, and format pipelines.
   - *Inference*: Rather than superficial summaries, the recon map requires concrete technical blueprints (e.g. byte-level LZ77 algorithms, CFI grammar, viewport culling formulas, DDL schemas) to directly feed downstream architecture (M2) and schema (M3) work.
2. **Screen & Flow Completeness**:
   - *Observation*: Analysis of 43 QTranslator contexts revealed 12 distinct UI views and 10 core user flows.
   - *Inference*: Documenting all functional states (especially empty states, loading overlays, filtered views, and multi-select footers) prevents design omissions during implementation. Happy-path click counts establish concrete UX efficiency benchmarks.
3. **Format Engine Abstraction**:
   - *Observation*: The original application cleanly partitions reflowable text from fixed-layout graphics, but suffers from legacy 32-bit dependencies (QtWebKit, Debenu PDF).
   - *Inference*: The recon map defines `ReflowableDocumentEngine` and `FixedLayoutDocumentEngine` under `IDocumentEngine`, specifying open-source replacements (PDFium / poppler-qt6, QuaZip / libzip, uchardet, in-process Qt 6 concurrency) that preserve functional parity while modernizing the stack.
4. **RFC 4180 CSV Validation**:
   - *Observation*: Downstream tools (`replica-diff`, project tracking) parse `features.csv`.
   - *Inference*: Rigorous automated programmatic validation via Python's `csv.DictReader` guarantees zero syntax errors, valid priority tiers (`Must`/`Should`/`Could`), and correct column headers.

---

## 3. Caveats

- **DRM Decryption**: The original binary rejects DRM protected files ("Ebook file is DRM protected. Book cannot be opened."). In compliance with legal principles and clean-room requirements, proprietary DRM decryption (Adobe Adept, Apple FairPlay, Amazon KFX) is intentionally out of scope.
- **Debenu PDF Licensing**: The original application bundles Foxit/Debenu's closed-source DLL. Our clean-room clone is designed to use open-source equivalents (PDFium or Poppler-Qt6).
- **DjVu Format**: `djvu.ico` is present in the installation directory and format enum, but no dedicated DLL exists. It is classified as priority `Could` for optional plugin implementation.

---

## 4. Conclusion

Milestone M1 (Reconnaissance & Feature Matrix) is 100% complete and fully verified.
- Deliverable 1 (`replica/recon.md`) provides an exhaustive, authoritative 65 KB technical recon map meeting all `replica-recon` requirements.
- Deliverable 2 (`replica/features.csv`) provides an RFC 4180 compliant, 67-row feature matrix categorized into Must, Should, and Could with complexity estimates.
Both deliverables are in place and ready for Milestone M2 (Architecture Specification) and Milestone M3 (SQLite Schema Design).

---

## 5. Verification Method

To independently verify the deliverables, execute the following commands in the workspace root:

1. **Verify RFC 4180 CSV Parsing & Integrity**:
   ```powershell
   python -c "
   import csv
   path = r'c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\features.csv'
   with open(path, 'r', encoding='utf-8', newline='') as f:
       reader = csv.DictReader(f)
       rows = list(reader)
   assert reader.fieldnames == ['feature', 'area', 'priority', 'original', 'clone', 'complexity', 'notes']
   assert len(rows) == 67
   assert set(r['priority'] for r in rows) == {'Must', 'Should', 'Could'}
   assert set(r['complexity'] for r in rows) == {'S', 'M', 'L', 'XL'}
   print(f'features.csv verification SUCCESS: {len(rows)} valid feature rows.')
   "
   ```

2. **Verify Recon Map Sections & Structure**:
   ```powershell
   python -c "
   path = r'c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\recon.md'
   with open(path, 'r', encoding='utf-8') as f:
       content = f.read()
   for sec in ['Executive Summary', 'Clean-Room Sources', 'Screen Inventory (S01–S12)', 'Key User Flows (F01–F10)', 'UI Component Catalog', 'Format Handling Pipelines', 'Inferred Data Model', 'Out of Scope', 'Sizing']:
       assert sec in content, f'Missing section: {sec}'
   for i in range(1, 13):
       assert f'S{i:02d}' in content
   for i in range(1, 11):
       assert f'F{i:02d}' in content
   print('recon.md verification SUCCESS: all required sections, screens S01-S12, and flows F01-F10 present.')
   "
   ```
