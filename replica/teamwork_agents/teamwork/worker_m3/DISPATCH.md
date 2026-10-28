## 2026-10-28T14:54:38Z
You are worker_m3, a teamwork_preview_worker.
Your working directory is: c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\worker_m3
Your parent is the Project Orchestrator (conversation ID: acfea67d-28a9-4a44-bf11-4149602dfb38).

MANDATORY FIRST STEPS:
1. Read the project requirements at: c:\Users\epicg\Downloads\icecream_ebook_reader_replica\ORIGINAL_REQUEST.md
2. Read the project scope document at: c:\Users\epicg\Downloads\icecream_ebook_reader_replica\PROJECT.md
3. Read the completed Milestone 1 deliverables and survey reports:
   - c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\recon.md (Inferred Data Model section)
   - c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\spec_miner_survey_1\handoff.md (Database Entity Requirements)
   - c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\explorer_survey_1\handoff.md (Authoritative SQLite schema and triggers)

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

EXCLUSIVE WRITE OWNERSHIP:
You exclusively own and must author:
`c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\schema.sql`
Do NOT modify any other files.

DELIVERABLE SPECIFICATIONS (`replica/schema.sql`):
Generate a production-ready, bulletproof SQLite 3 database schema:
1. Header configuration:
   - `PRAGMA foreign_keys = ON;`
   - `PRAGMA journal_mode = WAL;`
2. Tables required:
   - `books`: id (INTEGER PRIMARY KEY AUTOINCREMENT), title (TEXT NOT NULL), author (TEXT), description (TEXT), file_path (TEXT NOT NULL UNIQUE), file_size (INTEGER NOT NULL), file_hash (TEXT NOT NULL UNIQUE), format (TEXT NOT NULL), cover_path (TEXT), language (TEXT), publisher (TEXT), publication_date (TEXT), is_deleted (INTEGER NOT NULL DEFAULT 0), created_at (TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))), updated_at (TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))).
   - `authors`: id (INTEGER PRIMARY KEY AUTOINCREMENT), name (TEXT NOT NULL UNIQUE), sort_name (TEXT).
   - `book_authors`: book_id (INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE), author_id (INTEGER NOT NULL REFERENCES authors(id) ON DELETE CASCADE), PRIMARY KEY (book_id, author_id).
   - `folders`: id (INTEGER PRIMARY KEY AUTOINCREMENT), name (TEXT NOT NULL), parent_id (INTEGER REFERENCES folders(id) ON DELETE SET NULL), is_system (INTEGER NOT NULL DEFAULT 0), sort_order (INTEGER NOT NULL DEFAULT 0), created_at (TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))).
   - `book_folder_binder`: book_id (INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE), folder_id (INTEGER NOT NULL REFERENCES folders(id) ON DELETE CASCADE), added_at (TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))), PRIMARY KEY (book_id, folder_id).
   - `reading_progress`: id (INTEGER PRIMARY KEY AUTOINCREMENT), book_id (INTEGER NOT NULL UNIQUE REFERENCES books(id) ON DELETE CASCADE), current_cfi (TEXT), current_page (INTEGER NOT NULL DEFAULT 1), total_pages (INTEGER NOT NULL DEFAULT 1), progress_percent (REAL NOT NULL DEFAULT 0.0 CHECK(progress_percent >= 0.0 AND progress_percent <= 100.0)), reading_time_seconds (INTEGER NOT NULL DEFAULT 0), last_opened_at (TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))), is_finished (INTEGER NOT NULL DEFAULT 0), updated_at (TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))).
   - `bookmarks`: id (INTEGER PRIMARY KEY AUTOINCREMENT), book_id (INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE), cfi (TEXT), page_number (INTEGER NOT NULL DEFAULT 1), title (TEXT NOT NULL), snippet (TEXT), created_at (TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))).
   - `annotations`: id (INTEGER PRIMARY KEY AUTOINCREMENT), book_id (INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE), cfi_start (TEXT), cfi_end (TEXT), selected_text (TEXT NOT NULL), note_text (TEXT), color_id (INTEGER NOT NULL DEFAULT 1 CHECK(color_id BETWEEN 1 AND 5)), created_at (TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))), updated_at (TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))).
   - `book_metadata`: id (INTEGER PRIMARY KEY AUTOINCREMENT), book_id (INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE), key (TEXT NOT NULL), value (TEXT), UNIQUE(book_id, key).
   - `app_settings`: key (TEXT PRIMARY KEY), value (TEXT NOT NULL), updated_at (TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))).
3. Indexes for query optimization:
   - Indexes on lookup columns: `idx_books_file_hash`, `idx_books_format`, `idx_books_is_deleted`, `idx_reading_progress_last_opened`, `idx_bookmarks_book_id`, `idx_annotations_book_id`, `idx_book_folder_binder_folder`, `idx_books_title`.
4. Triggers:
   - Automatic `updated_at` refresh triggers for `books`, `reading_progress`, and `annotations`.
   - Seed data: Default system folders (All Books, Recently Read, Favorites, Read, Trash).

MANDATORY VALIDATION & TEST EXECUTION:
You MUST run sqlite3 to validate `replica/schema.sql`:
- Execute the SQL script against a test SQLite database.
- Verify 0 syntax errors.
- Test inserting sample books, folders, progress, bookmarks, and annotations.
- Test foreign key constraints (e.g. deleting a book cascades to progress, bookmarks, annotations, and folder binders).
- Test unique constraint enforcement (e.g. inserting duplicate `file_hash` fails).
- Document all test commands and execution outputs in your handoff report.

HANDOFF DELIVERABLE:
Write your report to `c:\Users\epicg\Downloads\icecream_ebook_reader_replica\.agents\teamwork\worker_m3\handoff.md`.
Report completion back to parent via send_message.
