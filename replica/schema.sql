-- ============================================================================
-- Clean-Room SQLite 3 Database Schema: Icecream Ebook Reader Replica
-- Architecture: Modern C++20 / Qt 6 (QtSql / QSQLITE Driver)
-- Target Platform: Windows / Cross-Platform Desktop
-- Target Database: ebooklib.sqlite3
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Database Configuration and Pragmas
-- ----------------------------------------------------------------------------
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- ----------------------------------------------------------------------------
-- 2. Core Publication Catalog: books
-- Tracks all indexed books, deduplicated by cryptographic file hash.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS books (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               TEXT NOT NULL,
    author              TEXT,
    description         TEXT,
    file_path           TEXT NOT NULL UNIQUE,
    file_size           INTEGER NOT NULL CHECK(file_size >= 0),
    file_hash           TEXT NOT NULL UNIQUE,
    format              TEXT NOT NULL,
    cover_path          TEXT,
    language            TEXT,
    publisher           TEXT,
    publication_date    TEXT,
    is_deleted          INTEGER NOT NULL DEFAULT 0,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- ----------------------------------------------------------------------------
-- 3. Normalized Author Index: authors
-- Normalized storage of author names and alphabetized sort keys.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS authors (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL UNIQUE,
    sort_name           TEXT
);

-- ----------------------------------------------------------------------------
-- 4. Publication-Author Association: book_authors
-- Many-to-many relationship supporting multi-author and collaborative works.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS book_authors (
    book_id             INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    author_id           INTEGER NOT NULL REFERENCES authors(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, author_id)
);

-- ----------------------------------------------------------------------------
-- 5. Collection Hierarchy: folders
-- System categories and custom user-defined hierarchical folders.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS folders (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,
    parent_id           INTEGER REFERENCES folders(id) ON DELETE SET NULL CHECK(parent_id != id),
    is_system           INTEGER NOT NULL DEFAULT 0,
    sort_order          INTEGER NOT NULL DEFAULT 0,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- ----------------------------------------------------------------------------
-- 6. Publication-Folder Mapping: book_folder_binder
-- Many-to-many relationship binder assigning books to folders/categories.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS book_folder_binder (
    book_id             INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    folder_id           INTEGER NOT NULL REFERENCES folders(id) ON DELETE CASCADE,
    added_at            TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    PRIMARY KEY (book_id, folder_id)
);

-- ----------------------------------------------------------------------------
-- 7. Active Reading State & Analytics: reading_progress
-- Tracks exact reading position (EPUB CFI / page), percentage, and elapsed time.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reading_progress (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id             INTEGER NOT NULL UNIQUE REFERENCES books(id) ON DELETE CASCADE,
    current_cfi         TEXT,
    current_page        INTEGER NOT NULL DEFAULT 1,
    total_pages         INTEGER NOT NULL DEFAULT 1,
    progress_percent    REAL NOT NULL DEFAULT 0.0 CHECK(progress_percent >= 0.0 AND progress_percent <= 100.0),
    reading_time_seconds INTEGER NOT NULL DEFAULT 0,
    last_opened_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    is_finished         INTEGER NOT NULL DEFAULT 0,
    updated_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- ----------------------------------------------------------------------------
-- 8. Bookmarks: bookmarks
-- Persistent reading markers referencing exact pages and EPUB CFIs.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookmarks (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id             INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    cfi                 TEXT,
    page_number         INTEGER NOT NULL DEFAULT 1,
    title               TEXT NOT NULL,
    snippet             TEXT,
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- ----------------------------------------------------------------------------
-- 9. Highlights and Notes: annotations
-- In-book text selections with color classification (1..5) and user commentary.
-- Color mapping: 1=Yellow, 2=Green, 3=Cyan, 4=Pink, 5=Underline
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS annotations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id             INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    cfi_start           TEXT,
    cfi_end             TEXT,
    selected_text       TEXT NOT NULL,
    note_text           TEXT,
    color_id            INTEGER NOT NULL DEFAULT 1 CHECK(color_id BETWEEN 1 AND 5),
    created_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- ----------------------------------------------------------------------------
-- 10. Extensible Metadata: book_metadata
-- Key-value pair storage for additional format-specific or extracted metadata.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS book_metadata (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id             INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    key                 TEXT NOT NULL,
    value               TEXT,
    UNIQUE(book_id, key)
);

-- ----------------------------------------------------------------------------
-- 11. Application Settings Cache: app_settings
-- Global configuration key-value store complementing settings.ini.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS app_settings (
    key                 TEXT PRIMARY KEY,
    value               TEXT NOT NULL,
    updated_at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- ----------------------------------------------------------------------------
-- 12. Performance & Query Optimization Indexes
-- Accelerates lookups for duplicate detection, format filtering, soft deletes,
-- sorting by last read date, and relationship traversals.
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_books_format ON books(format);
CREATE INDEX IF NOT EXISTS idx_books_is_deleted ON books(is_deleted);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_reading_progress_last_opened ON reading_progress(last_opened_at);
CREATE INDEX IF NOT EXISTS idx_bookmarks_book_id ON bookmarks(book_id);
CREATE INDEX IF NOT EXISTS idx_annotations_book_id ON annotations(book_id);
CREATE INDEX IF NOT EXISTS idx_book_folder_binder_folder ON book_folder_binder(folder_id);
CREATE INDEX IF NOT EXISTS idx_book_authors_author ON book_authors(author_id);
CREATE INDEX IF NOT EXISTS idx_folders_parent ON folders(parent_id);

-- ----------------------------------------------------------------------------
-- 13. Automatic updated_at Timestamp Refresh Triggers
-- Ensures modification timestamps advance automatically on row update.
-- ----------------------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_books_updated_at
AFTER UPDATE ON books
FOR EACH ROW
WHEN OLD.updated_at IS NEW.updated_at AND strftime('%Y-%m-%dT%H:%M:%SZ', 'now') != OLD.updated_at
BEGIN
    UPDATE books
    SET updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_reading_progress_updated_at
AFTER UPDATE ON reading_progress
FOR EACH ROW
WHEN OLD.updated_at IS NEW.updated_at AND strftime('%Y-%m-%dT%H:%M:%SZ', 'now') != OLD.updated_at
BEGIN
    UPDATE reading_progress
    SET updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_annotations_updated_at
AFTER UPDATE ON annotations
FOR EACH ROW
WHEN OLD.updated_at IS NEW.updated_at AND strftime('%Y-%m-%dT%H:%M:%SZ', 'now') != OLD.updated_at
BEGIN
    UPDATE annotations
    SET updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_app_settings_updated_at
AFTER UPDATE ON app_settings
FOR EACH ROW
WHEN OLD.updated_at IS NEW.updated_at AND strftime('%Y-%m-%dT%H:%M:%SZ', 'now') != OLD.updated_at
BEGIN
    UPDATE app_settings
    SET updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
    WHERE key = NEW.key;
END;

-- ----------------------------------------------------------------------------
-- 14. Initial Seed Data: Default System Folders
-- Prepopulates mandatory system categories matching the native application.
-- ----------------------------------------------------------------------------
INSERT OR IGNORE INTO folders (id, name, parent_id, is_system, sort_order) VALUES
    (1, 'All Books', NULL, 1, 1),
    (2, 'Recently Read', NULL, 1, 2),
    (3, 'Favorites', NULL, 1, 3),
    (4, 'Read', NULL, 1, 4),
    (5, 'Trash', NULL, 1, 5);
