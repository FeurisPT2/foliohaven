# Product Specification: FolioHaven

## Purpose & Positioning
FolioHaven is a serene, modern desktop and web ebook reader built for readers, researchers, and students who value typography, focus, and quiet study. It positions itself as the "Anti-Nag Reader" — a clean, private, open-source alternative to commercial desktop readers plagued by artificial book limits, countdown timers, upgrade nag popups, and intrusive telemetry.

## Platform
adaptive

## Target Audience & Scenarios
- **Literary Readers**: Deep, uninterrupted reading sessions requiring soothing archival contrast (Sepia & Dark Sepia palettes), balanced page measures, and distraction-free fullscreen (`F`).
- **Students & Researchers**: Extracting citations, highlighting across 4 color codes, organizing collections into custom shelves, in-book regex/keyword search, and one-click export of research notes to standalone printable HTML.
- **Comic & Illustrated Book Readers**: Fixed-layout CBZ and PDF rendering with dual-page spreads.

## Core Capabilities
- **Multi-Format Ingestion**: EPUB (2.0/3.2), PDF, MOBI, FB2, CBZ, and TXT via file dialogs or native drag & drop.
- **Calm Reading Canvas**: Dual-column and single-column modes, 4 WCAG AAA-compliant themes (Day, Sepia, Night, Dark Sepia), dynamic font scaling (`A-` / `A+`).
- **Research & Annotation Engine**: 4 highlight swatches (Amber, Emerald, Azure, Rose), inline notes, bookmarks drawer, HTML export.
- **Smart Bookshelf Management**: Shelf View, Grid View, and Table View with real-time title/author filtering, reading progress tracking, custom covers, and shelf password protection.
- **Speech Synthesis (TTS)**: Native text-to-speech read aloud with speed control and voice selection.
- **Privacy & Security**: 100% local persistence (SQLite with Write-Ahead Logging on native desktop, IndexedDB on web). Zero telemetry, zero external tracking.

## Durable Constraints & Design System
- Strictly adheres to the **Impeccable Craft Floor** and **Tasteskill v2**: no emojis in UI controls (authored SVGs only), no 3px side-tabs, no chunky clashing borders, authentic museum-grade artworks from the Art Institute of Chicago (CC0).
