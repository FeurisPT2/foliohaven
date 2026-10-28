# BRIEFING — 2026-10-28T21:44:30Z

## Mission
Perform a deep clean-room technical survey of the reference target installation at `C:\Program Files (x86)\Icecream Ebook Reader` to determine architecture, frameworks, dependencies, assets, configs, formats, and implications for a C++20 / Qt 6 replica.

## 🔒 My Identity
- Archetype: explorer
- Roles: clean-room technical survey & architecture input
- Working directory: c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\explorer_survey_1
- Original parent: acfea67d-28a9-4a44-bf11-4149602dfb38
- Milestone: Reconnaissance & Technical Survey

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Clean-room technical survey of target installation metadata, binaries, libraries, assets, configs, formats
- Deliver comprehensive findings to handoff.md and send completion message to parent via send_message

## Current Parent
- Conversation ID: acfea67d-28a9-4a44-bf11-4149602dfb38
- Updated: 2026-10-28T14:34:23Z

## Investigation State
- **Explored paths**:
  - `C:\Program Files (x86)\Icecream Ebook Reader` (all 84 files, 9 subdirectories)
  - `icebookreader.exe`, `icebooksvc.exe`, `unins000.exe`
  - All dynamic libraries: `Qt5Core.dll`, `Qt5Gui.dll`, `Qt5Widgets.dll`, `Qt5WebKit.dll`, `DebenuPDFLibraryDLL1016.dll`, `quazip.dll`, `unrar.dll`, `7zxa.dll`, `libxml2.dll`, `libxslt.dll`, `libcurl.dll`, `libcrypto-1_1.dll`, `libssl-1_1.dll`, `CrashRpt1403.dll`
  - Embedded Qt resources (94 SVGs, `jsengine.js`, icons)
  - Compiled translations (`translations/ebookreader_*.qm`, 49 locales, 651 strings extracted from `ebookreader_en.qm`)
  - Registry keys: `HKCU\Software\Icecream\Icecream Ebook Reader New`, `HKLM\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Icecream Ebook Reader_is1`, `HKCR\IcecreamEbookReader\*`
- **Key findings**:
  - Underlying stack is 32-bit x86 Qt 5.15.1 + MSVC 2019 + QtWebKit (29.1 MB) + Debenu Quick PDF 10.16.
  - Multi-process pagination architecture: `icebooksvc.exe` helper process handles pagination and background layout via WebSocket IPC (`WSTransport` / `remotehandler`).
  - Supported formats: `.epub`, `.mobi`, `.prc`, `.fb2`, `.pdf`, `.txt`, `.cbz`, `.cbr`, `.zip`, `.7z`.
  - Database schema: Centralized SQLite database at `~/.ebookreader/data/ebooklib.sqlite3` with tables `books`, `folders`, `book_folder_binder`, `book_metadata` and cascading delete triggers.
  - Complete UI component hierarchy recovered: 291 RTTI classes, 3 viewer backends (`TextViewer`, `ImageViewer`, `PdfViewer`), reading toolbar, reading sidebar (TOC, bookmarks, notes, search), selection action popups, and hotkey mappings.
- **Unexplored areas**: None within the reference survey scope.

## Key Decisions Made
- Fully documented all technical findings, schemas, and architecture implications in `handoff.md`.
- Recommended replacement of legacy QtWebKit and commercial Debenu PDF with modern Qt 6 / QtWebEngine / Poppler / PDFium and in-process C++20 multithreading.

## Artifact Index
- `handoff.md` — Full clean-room technical survey report with verbatim observations, logic chain, caveats, conclusions, and verification commands.
- `progress.md` — Liveness heartbeat.
- `DISPATCH.md` — Parent dispatch record.
