import sqlite3
import os
import sys
import tempfile
import time

def run_comprehensive_tests(schema_path):
    print("=" * 70)
    print("COMPREHENSIVE SQLITE 3 SCHEMA TEST SUITE")
    print(f"Target Schema: {schema_path}")
    print("=" * 70)

    with open(schema_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # ---------------------------------------------------------
    # Test 1: File-based database test for WAL mode and Pragmas
    # ---------------------------------------------------------
    print("\n--- Test 1: WAL Mode & File Persistence ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_ebooklib.sqlite3")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(sql_content)
        
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0]
        print(f"Journal mode reported by SQLite: {journal_mode}")
        assert journal_mode.upper() == "WAL", f"Expected WAL mode, got {journal_mode}"
        
        cursor.execute("PRAGMA foreign_keys;")
        fk_status = cursor.fetchone()[0]
        print(f"Foreign keys status: {fk_status}")
        assert fk_status == 1, "Foreign keys pragma should be ON"
        conn.close()
        print("Test 1 passed successfully.")

    # ---------------------------------------------------------
    # Test 2: In-memory schema load & structural count
    # ---------------------------------------------------------
    print("\n--- Test 2: In-Memory Schema Load & Objects Inspection ---")
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(sql_content)
    cursor = conn.cursor()

    required_tables = [
        "books", "authors", "book_authors", "folders",
        "book_folder_binder", "reading_progress", "bookmarks",
        "annotations", "book_metadata", "app_settings"
    ]
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [r[0] for r in cursor.fetchall()]
    print(f"Tables present: {existing_tables}")
    for t in required_tables:
        assert t in existing_tables, f"Missing required table: {t}"
    print("All 10 required tables verified.")

    required_indexes = [
        "idx_books_file_hash",
        "idx_books_format",
        "idx_books_is_deleted",
        "idx_reading_progress_last_opened",
        "idx_bookmarks_book_id",
        "idx_annotations_book_id",
        "idx_book_folder_binder_folder",
        "idx_books_title"
    ]
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
    existing_indexes = [r[0] for r in cursor.fetchall()]
    print(f"\nIndexes present: {existing_indexes}")
    for idx in required_indexes:
        assert idx in existing_indexes, f"Missing required index: {idx}"
    print("All 8 required indexes verified.")

    required_triggers = [
        "trg_books_updated_at",
        "trg_reading_progress_updated_at",
        "trg_annotations_updated_at",
        "trg_app_settings_updated_at"
    ]
    cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
    existing_triggers = [r[0] for r in cursor.fetchall()]
    print(f"\nTriggers present: {existing_triggers}")
    for trg in required_triggers:
        assert trg in existing_triggers, f"Missing required trigger: {trg}"
    print("All required triggers verified.")

    # ---------------------------------------------------------
    # Test 3: System Folders Seed Data Verification
    # ---------------------------------------------------------
    print("\n--- Test 3: System Folders Seed Data ---")
    cursor.execute("SELECT id, name, parent_id, is_system, sort_order FROM folders ORDER BY sort_order;")
    folder_rows = cursor.fetchall()
    for row in folder_rows:
        print(f"  Row: id={row[0]}, name='{row[1]}', parent_id={row[2]}, is_system={row[3]}, sort_order={row[4]}")
    expected_names = ["All Books", "Recently Read", "Favorites", "Read", "Trash"]
    assert [r[1] for r in folder_rows] == expected_names, "System folder names mismatch"
    assert all(r[3] == 1 for r in folder_rows), "System folders must have is_system = 1"
    print("Seed system folders verified.")

    # ---------------------------------------------------------
    # Test 4: Full CRUD, Check Constraints & Unique Constraints
    # ---------------------------------------------------------
    print("\n--- Test 4: CRUD, Constraints & Error Handling ---")
    # Insert Books
    cursor.execute("""
        INSERT INTO books (title, author, description, file_path, file_size, file_hash, format, cover_path, language, publisher, publication_date)
        VALUES ('Twenty Thousand Leagues Under the Sea', 'Jules Verne', 'Classic sci-fi', '/library/20k.epub', 542000, 'hash_verne_20k', 'EPUB', 'covers/20k.jpg', 'en', 'Hetzel', '1870');
    """)
    b1_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO books (title, author, description, file_path, file_size, file_hash, format, cover_path, language, publisher, publication_date)
        VALUES ('The War of the Worlds', 'H.G. Wells', 'Invasion novel', '/library/war_worlds.pdf', 1240000, 'hash_wells_war', 'PDF', 'covers/war.jpg', 'en', 'Heinemann', '1898');
    """)
    b2_id = cursor.lastrowid
    print(f"Inserted books {b1_id} and {b2_id}.")

    # Test duplicate file_path constraint
    try:
        cursor.execute("INSERT INTO books (title, file_path, file_size, file_hash, format) VALUES ('Dup Path', '/library/20k.epub', 100, 'hash_unique_1', 'EPUB');")
        assert False, "Duplicate file_path should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] books.file_path UNIQUE constraint enforced.")

    # Test duplicate file_hash constraint
    try:
        cursor.execute("INSERT INTO books (title, file_path, file_size, file_hash, format) VALUES ('Dup Hash', '/library/other.epub', 100, 'hash_verne_20k', 'EPUB');")
        assert False, "Duplicate file_hash should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] books.file_hash UNIQUE constraint enforced.")

    # Insert Authors
    cursor.execute("INSERT INTO authors (name, sort_name) VALUES ('Jules Verne', 'Verne, Jules');")
    a1_id = cursor.lastrowid
    cursor.execute("INSERT INTO authors (name, sort_name) VALUES ('H.G. Wells', 'Wells, H.G.');")
    a2_id = cursor.lastrowid

    # Test duplicate author name
    try:
        cursor.execute("INSERT INTO authors (name) VALUES ('Jules Verne');")
        assert False, "Duplicate author name should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] authors.name UNIQUE constraint enforced.")

    # Link book_authors
    cursor.execute("INSERT INTO book_authors (book_id, author_id) VALUES (?, ?);", (b1_id, a1_id))
    cursor.execute("INSERT INTO book_authors (book_id, author_id) VALUES (?, ?);", (b2_id, a2_id))
    print("  [Pass] book_authors links created.")

    # Test duplicate book_author link
    try:
        cursor.execute("INSERT INTO book_authors (book_id, author_id) VALUES (?, ?);", (b1_id, a1_id))
        assert False, "Duplicate primary key (book_id, author_id) should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] book_authors PRIMARY KEY enforced.")

    # Insert reading_progress
    cursor.execute("""
        INSERT INTO reading_progress (book_id, current_cfi, current_page, total_pages, progress_percent, reading_time_seconds)
        VALUES (?, 'epubcfi(/6/2[ch01]!/4/2/4:0)', 10, 200, 5.0, 300);
    """, (b1_id,))
    rp1_id = cursor.lastrowid

    # Test reading_progress duplicate book_id
    try:
        cursor.execute("INSERT INTO reading_progress (book_id) VALUES (?);", (b1_id,))
        assert False, "Duplicate reading_progress book_id should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] reading_progress.book_id UNIQUE constraint enforced.")

    # Test progress_percent negative check
    try:
        cursor.execute("INSERT INTO reading_progress (book_id, progress_percent) VALUES (?, -1.0);", (b2_id,))
        assert False, "progress_percent < 0 should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] reading_progress.progress_percent >= 0.0 CHECK enforced.")

    # Test progress_percent > 100 check
    try:
        cursor.execute("INSERT INTO reading_progress (book_id, progress_percent) VALUES (?, 105.0);", (b2_id,))
        assert False, "progress_percent > 100.0 should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] reading_progress.progress_percent <= 100.0 CHECK enforced.")

    # Insert bookmarks
    cursor.execute("""
        INSERT INTO bookmarks (book_id, cfi, page_number, title, snippet)
        VALUES (?, 'epubcfi(/6/2[ch01]!/4/2/10:14)', 12, 'Giant Squid', 'A monster was sighted...');
    """, (b1_id,))

    # Insert annotations
    cursor.execute("""
        INSERT INTO annotations (book_id, cfi_start, cfi_end, selected_text, note_text, color_id)
        VALUES (?, 'cfi1', 'cfi2', 'Mobilis in mobili', 'Motto of the Nautilus', 2);
    """, (b1_id,))
    ann1_id = cursor.lastrowid

    # Test annotation color_id boundaries (1..5)
    try:
        cursor.execute("INSERT INTO annotations (book_id, selected_text, color_id) VALUES (?, 'text', 0);", (b1_id,))
        assert False, "color_id = 0 should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] annotations.color_id >= 1 CHECK enforced.")

    try:
        cursor.execute("INSERT INTO annotations (book_id, selected_text, color_id) VALUES (?, 'text', 6);", (b1_id,))
        assert False, "color_id = 6 should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] annotations.color_id <= 5 CHECK enforced.")

    # Insert book_metadata
    cursor.execute("INSERT INTO book_metadata (book_id, key, value) VALUES (?, 'genre', 'Science Fiction');", (b1_id,))
    cursor.execute("INSERT INTO book_metadata (book_id, key, value) VALUES (?, 'word_count', '104000');", (b1_id,))
    try:
        cursor.execute("INSERT INTO book_metadata (book_id, key, value) VALUES (?, 'genre', 'Adventure');", (b1_id,))
        assert False, "Duplicate book_metadata (book_id, key) should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] book_metadata UNIQUE(book_id, key) enforced.")

    # Binder
    cursor.execute("INSERT INTO book_folder_binder (book_id, folder_id) VALUES (?, 1);", (b1_id,))
    cursor.execute("INSERT INTO book_folder_binder (book_id, folder_id) VALUES (?, 3);", (b1_id,))
    try:
        cursor.execute("INSERT INTO book_folder_binder (book_id, folder_id) VALUES (?, 1);", (b1_id,))
        assert False, "Duplicate book_folder_binder primary key should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] book_folder_binder PRIMARY KEY enforced.")

    # App settings
    cursor.execute("INSERT INTO app_settings (key, value) VALUES ('theme', 'DayStyle');")
    cursor.execute("INSERT INTO app_settings (key, value) VALUES ('font_size', '16');")
    try:
        cursor.execute("INSERT INTO app_settings (key, value) VALUES ('theme', 'NightStyle');")
        assert False, "Duplicate app_settings PRIMARY KEY key should have failed!"
    except sqlite3.IntegrityError:
        print("  [Pass] app_settings PRIMARY KEY enforced.")

    # ---------------------------------------------------------
    # Test 5: Trigger Verification (updated_at)
    # ---------------------------------------------------------
    print("\n--- Test 5: Timestamp Refresh Triggers ---")
    cursor.execute("SELECT updated_at FROM books WHERE id = ?;", (b1_id,))
    b1_up1 = cursor.fetchone()[0]
    time.sleep(1.05)
    cursor.execute("UPDATE books SET title = 'Twenty Thousand Leagues (Revised)' WHERE id = ?;", (b1_id,))
    cursor.execute("SELECT updated_at FROM books WHERE id = ?;", (b1_id,))
    b1_up2 = cursor.fetchone()[0]
    assert b1_up2 > b1_up1, f"Trigger failed on books: {b1_up1} -> {b1_up2}"
    print(f"  [Pass] trg_books_updated_at: {b1_up1} -> {b1_up2}")

    cursor.execute("SELECT updated_at FROM reading_progress WHERE id = ?;", (rp1_id,))
    rp_up1 = cursor.fetchone()[0]
    time.sleep(1.05)
    cursor.execute("UPDATE reading_progress SET current_page = 25, progress_percent = 12.5 WHERE id = ?;", (rp1_id,))
    cursor.execute("SELECT updated_at FROM reading_progress WHERE id = ?;", (rp1_id,))
    rp_up2 = cursor.fetchone()[0]
    assert rp_up2 > rp_up1, f"Trigger failed on reading_progress: {rp_up1} -> {rp_up2}"
    print(f"  [Pass] trg_reading_progress_updated_at: {rp_up1} -> {rp_up2}")

    cursor.execute("SELECT updated_at FROM annotations WHERE id = ?;", (ann1_id,))
    ann_up1 = cursor.fetchone()[0]
    time.sleep(1.05)
    cursor.execute("UPDATE annotations SET note_text = 'Updated note text' WHERE id = ?;", (ann1_id,))
    cursor.execute("SELECT updated_at FROM annotations WHERE id = ?;", (ann1_id,))
    ann_up2 = cursor.fetchone()[0]
    assert ann_up2 > ann_up1, f"Trigger failed on annotations: {ann_up1} -> {ann_up2}"
    print(f"  [Pass] trg_annotations_updated_at: {ann_up1} -> {ann_up2}")

    cursor.execute("SELECT updated_at FROM app_settings WHERE key = 'theme';")
    cfg_up1 = cursor.fetchone()[0]
    time.sleep(1.05)
    cursor.execute("UPDATE app_settings SET value = 'SepiaStyle' WHERE key = 'theme';")
    cursor.execute("SELECT updated_at FROM app_settings WHERE key = 'theme';")
    cfg_up2 = cursor.fetchone()[0]
    assert cfg_up2 > cfg_up1, f"Trigger failed on app_settings: {cfg_up1} -> {cfg_up2}"
    print(f"  [Pass] trg_app_settings_updated_at: {cfg_up1} -> {cfg_up2}")

    # ---------------------------------------------------------
    # Test 6: Foreign Key Cascades & SET NULL
    # ---------------------------------------------------------
    print("\n--- Test 6: Foreign Key Cascade & SET NULL Behaviors ---")
    
    # 6a: Test folder hierarchy ON DELETE SET NULL
    cursor.execute("INSERT INTO folders (name, parent_id) VALUES ('Sci-Fi & Fantasy', NULL);")
    parent_folder_id = cursor.lastrowid
    cursor.execute("INSERT INTO folders (name, parent_id) VALUES ('Classic Sci-Fi', ?);", (parent_folder_id,))
    child_folder_id = cursor.lastrowid
    
    # Delete parent folder
    cursor.execute("DELETE FROM folders WHERE id = ?;", (parent_folder_id,))
    cursor.execute("SELECT parent_id FROM folders WHERE id = ?;", (child_folder_id,))
    res_parent = cursor.fetchone()[0]
    assert res_parent is None, f"Expected parent_id to be SET NULL, got {res_parent}"
    print("  [Pass] folders parent_id ON DELETE SET NULL verified.")

    # 6b: Test folder deletion cascade on book_folder_binder
    cursor.execute("INSERT INTO book_folder_binder (book_id, folder_id) VALUES (?, ?);", (b1_id, child_folder_id))
    cursor.execute("DELETE FROM folders WHERE id = ?;", (child_folder_id,))
    cursor.execute("SELECT COUNT(*) FROM book_folder_binder WHERE folder_id = ?;", (child_folder_id,))
    assert cursor.fetchone()[0] == 0, "book_folder_binder cascade on folder deletion failed!"
    # Ensure book still exists
    cursor.execute("SELECT COUNT(*) FROM books WHERE id = ?;", (b1_id,))
    assert cursor.fetchone()[0] == 1, "Book was deleted unexpectedly when folder was deleted!"
    print("  [Pass] folder deletion cascades to book_folder_binder without affecting books.")

    # 6c: Test author deletion cascade on book_authors
    cursor.execute("DELETE FROM authors WHERE id = ?;", (a1_id,))
    cursor.execute("SELECT COUNT(*) FROM book_authors WHERE author_id = ?;", (a1_id,))
    assert cursor.fetchone()[0] == 0, "book_authors cascade on author deletion failed!"
    cursor.execute("SELECT COUNT(*) FROM books WHERE id = ?;", (b1_id,))
    assert cursor.fetchone()[0] == 1, "Book was deleted unexpectedly when author was deleted!"
    print("  [Pass] author deletion cascades to book_authors without affecting books.")

    # 6d: Test book deletion cascade on all child entities
    cursor.execute("DELETE FROM books WHERE id = ?;", (b1_id,))
    cursor.execute("SELECT COUNT(*) FROM reading_progress WHERE book_id = ?;", (b1_id,))
    assert cursor.fetchone()[0] == 0, "reading_progress cascade failed on book deletion"
    cursor.execute("SELECT COUNT(*) FROM bookmarks WHERE book_id = ?;", (b1_id,))
    assert cursor.fetchone()[0] == 0, "bookmarks cascade failed on book deletion"
    cursor.execute("SELECT COUNT(*) FROM annotations WHERE book_id = ?;", (b1_id,))
    assert cursor.fetchone()[0] == 0, "annotations cascade failed on book deletion"
    cursor.execute("SELECT COUNT(*) FROM book_metadata WHERE book_id = ?;", (b1_id,))
    assert cursor.fetchone()[0] == 0, "book_metadata cascade failed on book deletion"
    cursor.execute("SELECT COUNT(*) FROM book_folder_binder WHERE book_id = ?;", (b1_id,))
    assert cursor.fetchone()[0] == 0, "book_folder_binder cascade failed on book deletion"
    cursor.execute("SELECT COUNT(*) FROM book_authors WHERE book_id = ?;", (b1_id,))
    assert cursor.fetchone()[0] == 0, "book_authors cascade failed on book deletion"
    print("  [Pass] book deletion successfully cascaded to all 6 child tables.")

    # ---------------------------------------------------------
    # Test 7: Index Utilization via EXPLAIN QUERY PLAN
    # ---------------------------------------------------------
    print("\n--- Test 7: Index Utilization Verification ---")
    query_checks = [
        ("SELECT * FROM books INDEXED BY idx_books_file_hash WHERE file_hash = 'hash_wells_war';", "idx_books_file_hash"),
        ("SELECT * FROM books INDEXED BY idx_books_format WHERE format = 'PDF';", "idx_books_format"),
        ("SELECT * FROM books INDEXED BY idx_books_is_deleted WHERE is_deleted = 0;", "idx_books_is_deleted"),
        ("SELECT * FROM books INDEXED BY idx_books_title WHERE title = 'The War of the Worlds';", "idx_books_title"),
        ("SELECT * FROM reading_progress INDEXED BY idx_reading_progress_last_opened ORDER BY last_opened_at DESC;", "idx_reading_progress_last_opened"),
        ("SELECT * FROM bookmarks INDEXED BY idx_bookmarks_book_id WHERE book_id = 2;", "idx_bookmarks_book_id"),
        ("SELECT * FROM annotations INDEXED BY idx_annotations_book_id WHERE book_id = 2;", "idx_annotations_book_id"),
        ("SELECT * FROM book_folder_binder INDEXED BY idx_book_folder_binder_folder WHERE folder_id = 1;", "idx_book_folder_binder_folder")
    ]
    for query, expected_idx in query_checks:
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan = cursor.fetchall()
        plan_str = " | ".join([p[3] for p in plan])
        assert expected_idx in plan_str, f"Query '{query}' did not use index '{expected_idx}'! Plan: {plan_str}"
        print(f"  [Pass] Index {expected_idx} verified: {plan_str}")

    print("\n" + "=" * 70)
    print("ALL 7 TEST SUITES PASSED FLAWLESSLY WITH 0 ERRORS!")
    print("=" * 70)

if __name__ == '__main__':
    schema_path = sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\schema.sql"
    run_comprehensive_tests(schema_path)
