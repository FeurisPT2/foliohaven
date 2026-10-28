# replica-architect skill dump

Source: `C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-architect\SKILL.md`

## Summary of Methodology
Plans the stack, database schema, API/internal interface contracts, the parts that bite, and phased build order (starting with a thin vertical slice) for an app replica from the recon map.
For this desktop C++20 / Qt 6 application, adapting web/SaaS concepts to desktop native C++:
- Stack: C++20, Qt 6.6+, SQLite3, third-party libraries (PDF, EPUB/MOBI/FB2, ZIP, uchardet, QTextToSpeech).
- Schema: Full SQLite3 schema with indexes, foreign keys, triggers, pragmas.
- API / Interface Layer: C++20 Concepts, `IDocumentEngine`, `BookContext`, controllers, signals/slots, threading boundaries.
- The parts that bite: Massive libraries (10k+), corrupted files, non-blocking UI during resize/render, reflow pagination under geometry/font changes, High-DPI scaling.
- Build order: Milestone 1 (Vertical slice), Milestone 2 (Library core), Milestone 3 (Advanced reading tools).
