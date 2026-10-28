"""
Adversarial Stress Test Suite for replica/schema.sql
Clean-room verification of SQLite database constraints, cascades, triggers, and query plans.
"""

import os
import sys
import sqlite3
import tempfile
import time

SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "replica", "schema.sql"))

def run_tests():
    print("=" * 80)
    print("ADVERSARIAL STRESS TEST SUITE: replica/schema.sql")
    print(f"Target Schema: {SCHEMA_PATH}")
    print("=" * 80)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    results = {}

    # --------------------------------------------------------------------------
    # GROUP 1: Syntax & DDL Integrity
    # --------------------------------------------------------------------------
    print("\n>>> GROUP 1: Syntax, DDL Integrity & WAL Mode")
    try:
        conn = sqlite3.connect(":memory:")
        conn.executescript(schema_sql)
        cursor = conn.cursor()
        
        cursor.execute("SELECT type, count(*) FROM sqlite_master GROUP BY type;")
        counts = dict(cursor.fetchall())
        print(f"  [Info] Object counts in :memory:: {counts}")
        assert counts.get("table", 0) >= 10, f"Expected at least 10 tables, found {counts.get('table', 0)}"
        assert counts.get("index", 0) >= 8, f"Expected at least 8 indexes, found {counts.get('index', 0)}"
        assert counts.get("trigger", 0) >= 4, f"Expected at least 4 triggers, found {counts.get('trigger', 0)}"
        results["g1_ddl_syntax"] = "PASS"
        print("  [PASS] 0 syntax errors executing DDL.")
    except Exception as e:
        results["g1_ddl_syntax"] = f"FAIL: {e}"
        print(f"  [FAIL] DDL execution failed: {e}")

    # Test file-backed WAL mode
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test.db")
        conn_file = sqlite3.connect(test_db)
        conn_file.executescript(schema_sql)
        cur_file = conn_file.cursor()
        cur_file.execute("PRAGMA journal_mode;")
        jmode = cur_file.fetchone()[0]
        cur_file.execute("PRAGMA foreign_keys;")
        fk_val = cur_file.fetchone()[0]
        conn_file.close()
        
        print(f"  [Info] File-backed journal_mode: {jmode}, foreign_keys: {fk_val}")
        if jmode.lower() == "wal" and fk_val == 1:
            results["g1_wal_mode"] = "PASS"
            print("  [PASS] WAL mode and foreign keys pragma active in file database.")
        else:
            results["g1_wal_mode"] = f"FAIL: jmode={jmode}, fk={fk_val}"
            print(f"  [FAIL] Unexpected pragmas: jmode={jmode}, fk={fk_val}")

    # --------------------------------------------------------------------------
    # GROUP 2: Duplicate Prevention & Uniqueness Constraints
    # --------------------------------------------------------------------------
    print("\n>>> GROUP 2: Duplicate Prevention & Constraints Stress Test")
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(schema_sql)
    cur = conn.cursor()

    # 2a: Insert initial valid book
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('Adversarial Book 1', 'Author A', 'C:/books/book1.epub', 1024, 'hash_abc_123', 'EPUB');
    """)
    b1_id = cur.lastrowid

    # 2b: Duplicate file_hash
    try:
        cur.execute("""
            INSERT INTO books (title, author, file_path, file_size, file_hash, format)
            VALUES ('Adversarial Book 2', 'Author B', 'C:/books/book2.epub', 2048, 'hash_abc_123', 'EPUB');
        """)
        results["g2_dup_hash"] = "FAIL: Duplicate hash allowed!"
        print("  [FAIL] Duplicate file_hash was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g2_dup_hash"] = "PASS"
        print(f"  [PASS] Duplicate file_hash prevented: {e}")

    # 2c: Duplicate file_path
    try:
        cur.execute("""
            INSERT INTO books (title, author, file_path, file_size, file_hash, format)
            VALUES ('Adversarial Book 3', 'Author C', 'C:/books/book1.epub', 2048, 'hash_diff_456', 'EPUB');
        """)
        results["g2_dup_path"] = "FAIL: Duplicate file_path allowed!"
        print("  [FAIL] Duplicate file_path was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g2_dup_path"] = "PASS"
        print(f"  [PASS] Duplicate file_path prevented: {e}")

    # 2d: NULL file_hash
    try:
        cur.execute("""
            INSERT INTO books (title, author, file_path, file_size, file_hash, format)
            VALUES ('Null Hash Book', 'Author D', 'C:/books/book_null.epub', 1024, NULL, 'EPUB');
        """)
        results["g2_null_hash"] = "FAIL: NULL file_hash allowed!"
        print("  [FAIL] NULL file_hash was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g2_null_hash"] = "PASS"
        print(f"  [PASS] NULL file_hash prevented: {e}")

    # 2e: NULL title
    try:
        cur.execute("""
            INSERT INTO books (title, author, file_path, file_size, file_hash, format)
            VALUES (NULL, 'Author D', 'C:/books/book_notitle.epub', 1024, 'hash_notitle', 'EPUB');
        """)
        results["g2_null_title"] = "FAIL: NULL title allowed!"
        print("  [FAIL] NULL title was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g2_null_title"] = "PASS"
        print(f"  [PASS] NULL title prevented: {e}")

    # 2f: Duplicate author name
    cur.execute("INSERT INTO authors (name) VALUES ('Adversarial Author');")
    a1_id = cur.lastrowid
    try:
        cur.execute("INSERT INTO authors (name) VALUES ('Adversarial Author');")
        results["g2_dup_author"] = "FAIL: Duplicate author allowed!"
        print("  [FAIL] Duplicate author was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g2_dup_author"] = "PASS"
        print(f"  [PASS] Duplicate author name prevented: {e}")

    # 2g: Duplicate book_authors pair
    cur.execute("INSERT INTO book_authors (book_id, author_id) VALUES (?, ?);", (b1_id, a1_id))
    try:
        cur.execute("INSERT INTO book_authors (book_id, author_id) VALUES (?, ?);", (b1_id, a1_id))
        results["g2_dup_book_authors"] = "FAIL: Duplicate book_authors link allowed!"
        print("  [FAIL] Duplicate book_authors link was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g2_dup_book_authors"] = "PASS"
        print(f"  [PASS] Duplicate book_authors composite PK enforced: {e}")

    # 2h: Duplicate reading_progress for same book
    cur.execute("INSERT INTO reading_progress (book_id, progress_percent) VALUES (?, 10.0);", (b1_id,))
    try:
        cur.execute("INSERT INTO reading_progress (book_id, progress_percent) VALUES (?, 20.0);", (b1_id,))
        results["g2_dup_reading_progress"] = "FAIL: Duplicate reading_progress allowed!"
        print("  [FAIL] Duplicate reading_progress book_id was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g2_dup_reading_progress"] = "PASS"
        print(f"  [PASS] Duplicate reading_progress book_id UNIQUE enforced: {e}")

    # 2i: Duplicate book_metadata (book_id, key)
    cur.execute("INSERT INTO book_metadata (book_id, key, value) VALUES (?, 'isbn', '978-3-16-148410-0');", (b1_id,))
    try:
        cur.execute("INSERT INTO book_metadata (book_id, key, value) VALUES (?, 'isbn', 'different_isbn');", (b1_id,))
        results["g2_dup_metadata_key"] = "FAIL: Duplicate book_metadata key allowed!"
        print("  [FAIL] Duplicate book_metadata (book_id, key) was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g2_dup_metadata_key"] = "PASS"
        print(f"  [PASS] Duplicate book_metadata (book_id, key) UNIQUE enforced: {e}")

    # --------------------------------------------------------------------------
    # GROUP 3: CHECK Constraints Boundary & Negative Testing
    # --------------------------------------------------------------------------
    print("\n>>> GROUP 3: CHECK Constraints Boundary & Negative Testing")
    
    # 3a: progress_percent < 0.0
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('Check Test Book', 'Author E', 'C:/books/check.epub', 1024, 'hash_check_1', 'EPUB');
    """)
    b_chk_id = cur.lastrowid

    try:
        cur.execute("INSERT INTO reading_progress (book_id, progress_percent) VALUES (?, -5.0);", (b_chk_id,))
        results["g3_progress_neg"] = "FAIL: progress_percent = -5.0 allowed!"
        print("  [FAIL] progress_percent = -5.0 was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g3_progress_neg"] = "PASS"
        print(f"  [PASS] progress_percent = -5.0 rejected: {e}")

    try:
        cur.execute("INSERT INTO reading_progress (book_id, progress_percent) VALUES (?, 105.0);", (b_chk_id,))
        results["g3_progress_over"] = "FAIL: progress_percent = 105.0 allowed!"
        print("  [FAIL] progress_percent = 105.0 was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g3_progress_over"] = "PASS"
        print(f"  [PASS] progress_percent = 105.0 rejected: {e}")

    # Boundary edge values
    cur.execute("INSERT INTO reading_progress (book_id, progress_percent) VALUES (?, 0.0);", (b_chk_id,))
    cur.execute("UPDATE reading_progress SET progress_percent = 100.0 WHERE book_id = ?;", (b_chk_id,))
    cur.execute("UPDATE reading_progress SET progress_percent = 0.000001 WHERE book_id = ?;", (b_chk_id,))
    cur.execute("UPDATE reading_progress SET progress_percent = 99.999999 WHERE book_id = ?;", (b_chk_id,))
    results["g3_progress_boundaries"] = "PASS"
    print("  [PASS] progress_percent exact boundaries [0.0, 100.0] accepted.")

    # 3b: annotations color_id (1..5)
    try:
        cur.execute("INSERT INTO annotations (book_id, selected_text, color_id) VALUES (?, 'text', 0);", (b_chk_id,))
        results["g3_color_zero"] = "FAIL: color_id = 0 allowed!"
        print("  [FAIL] color_id = 0 was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g3_color_zero"] = "PASS"
        print(f"  [PASS] color_id = 0 rejected: {e}")

    try:
        cur.execute("INSERT INTO annotations (book_id, selected_text, color_id) VALUES (?, 'text', 6);", (b_chk_id,))
        results["g3_color_six"] = "FAIL: color_id = 6 allowed!"
        print("  [FAIL] color_id = 6 was NOT prevented!")
    except sqlite3.IntegrityError as e:
        results["g3_color_six"] = "PASS"
        print(f"  [PASS] color_id = 6 rejected: {e}")

    for valid_color in range(1, 6):
        cur.execute("INSERT INTO annotations (book_id, selected_text, color_id) VALUES (?, ?, ?);",
                    (b_chk_id, f"Valid color {valid_color}", valid_color))
    results["g3_color_valid"] = "PASS"
    print("  [PASS] color_id values 1..5 all accepted.")

    # --------------------------------------------------------------------------
    # GROUP 4: Foreign Key Cascades & Deep Referentials
    # --------------------------------------------------------------------------
    print("\n>>> GROUP 4: Foreign Key Cascade Delete Verification")
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('Cascade Target Book', 'Author Cascade', 'C:/books/cascade.epub', 5000, 'hash_cascade_target', 'EPUB');
    """)
    cas_book_id = cur.lastrowid

    # Populate reading_progress, bookmarks, annotations, folder binder, metadata, authors
    cur.execute("INSERT INTO reading_progress (book_id, progress_percent, current_page) VALUES (?, 45.0, 120);", (cas_book_id,))
    cur.execute("INSERT INTO bookmarks (book_id, page_number, title) VALUES (?, 10, 'Bookmark 1');", (cas_book_id,))
    cur.execute("INSERT INTO bookmarks (book_id, page_number, title) VALUES (?, 20, 'Bookmark 2');", (cas_book_id,))
    cur.execute("INSERT INTO annotations (book_id, selected_text, note_text, color_id) VALUES (?, 'text1', 'note1', 1);", (cas_book_id,))
    cur.execute("INSERT INTO annotations (book_id, selected_text, note_text, color_id) VALUES (?, 'text2', 'note2', 3);", (cas_book_id,))
    cur.execute("INSERT INTO book_metadata (book_id, key, value) VALUES (?, 'subject', 'Testing');", (cas_book_id,))
    cur.execute("INSERT INTO book_folder_binder (book_id, folder_id) VALUES (?, 1);", (cas_book_id,))
    cur.execute("INSERT INTO book_folder_binder (book_id, folder_id) VALUES (?, 2);", (cas_book_id,))
    cur.execute("INSERT INTO book_authors (book_id, author_id) VALUES (?, ?);", (cas_book_id, a1_id))

    # Verify counts before delete
    assert cur.execute("SELECT count(*) FROM reading_progress WHERE book_id = ?;", (cas_book_id,)).fetchone()[0] == 1
    assert cur.execute("SELECT count(*) FROM bookmarks WHERE book_id = ?;", (cas_book_id,)).fetchone()[0] == 2
    assert cur.execute("SELECT count(*) FROM annotations WHERE book_id = ?;", (cas_book_id,)).fetchone()[0] == 2
    assert cur.execute("SELECT count(*) FROM book_metadata WHERE book_id = ?;", (cas_book_id,)).fetchone()[0] == 1
    assert cur.execute("SELECT count(*) FROM book_folder_binder WHERE book_id = ?;", (cas_book_id,)).fetchone()[0] == 2
    assert cur.execute("SELECT count(*) FROM book_authors WHERE book_id = ?;", (cas_book_id,)).fetchone()[0] == 1

    # Execute DELETE on parent book
    cur.execute("DELETE FROM books WHERE id = ?;", (cas_book_id,))

    rp_rem = cur.execute("SELECT count(*) FROM reading_progress WHERE book_id = ?;", (cas_book_id,)).fetchone()[0]
    bm_rem = cur.execute("SELECT count(*) FROM bookmarks WHERE book_id = ?;", (cas_book_id,)).fetchone()[0]
    an_rem = cur.execute("SELECT count(*) FROM annotations WHERE book_id = ?;", (cas_book_id,)).fetchone()[0]
    md_rem = cur.execute("SELECT count(*) FROM book_metadata WHERE book_id = ?;", (cas_book_id,)).fetchone()[0]
    fb_rem = cur.execute("SELECT count(*) FROM book_folder_binder WHERE book_id = ?;", (cas_book_id,)).fetchone()[0]
    ba_rem = cur.execute("SELECT count(*) FROM book_authors WHERE book_id = ?;", (cas_book_id,)).fetchone()[0]

    print(f"  Remaining rows after book deletion:")
    print(f"    reading_progress: {rp_rem}")
    print(f"    bookmarks:        {bm_rem}")
    print(f"    annotations:      {an_rem}")
    print(f"    book_metadata:    {md_rem}")
    print(f"    book_folder_binder: {fb_rem}")
    print(f"    book_authors:     {ba_rem}")

    if all(c == 0 for c in [rp_rem, bm_rem, an_rem, md_rem, fb_rem, ba_rem]):
        results["g4_cascade_delete"] = "PASS"
        print("  [PASS] All 6 dependent child tables cleanly purged by ON DELETE CASCADE.")
    else:
        results["g4_cascade_delete"] = "FAIL: Orphaned records found!"
        print("  [FAIL] Orphaned records remain!")

    # Check that parent folder ON DELETE SET NULL works
    cur.execute("INSERT INTO folders (name, parent_id) VALUES ('Grandparent Folder', NULL);")
    gp_id = cur.lastrowid
    cur.execute("INSERT INTO folders (name, parent_id) VALUES ('Parent Folder', ?);", (gp_id,))
    p_id = cur.lastrowid
    cur.execute("DELETE FROM folders WHERE id = ?;", (gp_id,))
    child_parent = cur.execute("SELECT parent_id FROM folders WHERE id = ?;", (p_id,)).fetchone()[0]
    if child_parent is None:
        results["g4_folder_set_null"] = "PASS"
        print("  [PASS] Folder parent_id successfully SET NULL upon parent deletion.")
    else:
        results["g4_folder_set_null"] = f"FAIL: parent_id = {child_parent}"
        print(f"  [FAIL] Expected NULL, got {child_parent}")

    # --------------------------------------------------------------------------
    # GROUP 5: Trigger Mechanics & Recursive Triggers Stress Test
    # --------------------------------------------------------------------------
    print("\n>>> GROUP 5: Trigger Mechanics & Recursive Triggers Stress Test")
    
    # 5a: Timestamp advancement on update
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format, updated_at)
        VALUES ('Trigger Test Book', 'Author Trg', 'C:/books/trg.epub', 1000, 'hash_trg_1', 'EPUB', '2026-01-01T00:00:00Z');
    """)
    trg_book_id = cur.lastrowid
    init_updated_at = cur.execute("SELECT updated_at FROM books WHERE id = ?;", (trg_book_id,)).fetchone()[0]
    
    cur.execute("UPDATE books SET title = 'Trigger Test Book (Updated)' WHERE id = ?;", (trg_book_id,))
    new_updated_at = cur.execute("SELECT updated_at FROM books WHERE id = ?;", (trg_book_id,)).fetchone()[0]
    
    print(f"  Initial updated_at: {init_updated_at}")
    print(f"  Updated updated_at: {new_updated_at}")
    if new_updated_at > init_updated_at:
        results["g5_trigger_advancement"] = "PASS"
        print("  [PASS] Trigger automatically updated updated_at on book UPDATE.")
    else:
        results["g5_trigger_advancement"] = f"FAIL: {new_updated_at} <= {init_updated_at}"
        print("  [FAIL] Trigger failed to advance timestamp!")

    # 5b: Stress test: PRAGMA recursive_triggers = ON
    print("\n  [Stress Test] Testing trigger behavior with PRAGMA recursive_triggers = ON...")
    cur.execute("PRAGMA recursive_triggers = ON;")
    
    # What happens when we update the book multiple times in rapid succession?
    try:
        for i in range(5):
            cur.execute("UPDATE books SET description = ? WHERE id = ?;", (f"Rapid update {i}", trg_book_id))
        results["g5_recursive_triggers"] = "PASS"
        print("  [PASS] Rapid updates under PRAGMA recursive_triggers = ON did not trigger recursion limit!")
    except sqlite3.OperationalError as e:
        results["g5_recursive_triggers"] = f"FAIL: Recursion error: {e}"
        print(f"  [FAIL] Trigger caused recursion limit error: {e}")

    # What happens when someone explicitly sets updated_at to a specific timestamp?
    cur.execute("UPDATE books SET title = 'Explicit Update', updated_at = '2030-01-01T00:00:00Z' WHERE id = ?;", (trg_book_id,))
    exp_val = cur.execute("SELECT updated_at FROM books WHERE id = ?;", (trg_book_id,)).fetchone()[0]
    if exp_val == '2030-01-01T00:00:00Z':
        results["g5_explicit_updated_at"] = "PASS"
        print("  [PASS] Explicit updated_at value was preserved (trigger skipped per WHEN OLD.updated_at IS NEW.updated_at).")
    else:
        results["g5_explicit_updated_at"] = f"FAIL: Got {exp_val}"
        print(f"  [FAIL] Explicit updated_at was overridden: {exp_val}")

    # 5c: Verification of Trigger Fix:
    print("  [Verification] Testing hardened trigger logic with recursive_triggers = ON...")
    cur.execute("DROP TRIGGER IF EXISTS trg_books_updated_at;")
    cur.execute("""
        CREATE TRIGGER trg_books_updated_at
        AFTER UPDATE ON books
        FOR EACH ROW
        WHEN OLD.updated_at IS NEW.updated_at AND strftime('%Y-%m-%dT%H:%M:%SZ', 'now') != OLD.updated_at
        BEGIN
            UPDATE books
            SET updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
            WHERE id = NEW.id;
        END;
    """)
    try:
        for i in range(20):
            cur.execute("UPDATE books SET description = ? WHERE id = ?;", (f"Hardened rapid update {i}", trg_book_id))
        results["g5_hardened_trigger_fix"] = "PASS"
        print("  [PASS] Hardened trigger safely handles rapid updates under recursive_triggers = ON with 0 recursion errors.")
    except Exception as e:
        results["g5_hardened_trigger_fix"] = f"FAIL: {e}"
        print(f"  [FAIL] Hardened trigger failed: {e}")

    # --------------------------------------------------------------------------
    # GROUP 6: Query Performance, Index Redundancy & EXPLAIN QUERY PLAN
    # --------------------------------------------------------------------------
    print("\n>>> GROUP 6: Query Optimization & Index Analysis")

    # Insert a realistic library batch (1,000 synthetic books) to evaluate query planner decisions
    print("  Inserting 1,000 synthetic books to analyze realistic query planner index selection...")
    synthetic_books = []
    formats = ['EPUB', 'PDF', 'MOBI', 'FB2', 'CBZ', 'TXT']
    authors_list = ['Isaac Asimov', 'Arthur C. Clarke', 'Philip K. Dick', 'Ursula K. Le Guin', 'Frank Herbert', 'Stanislaw Lem']
    
    for i in range(1000):
        fmt = formats[i % len(formats)]
        auth = authors_list[i % len(authors_list)]
        title = f"Book Title Volume {i:04d} - {auth}"
        path = f"C:/ebooks/library/{fmt.lower()}/book_{i:04d}.{fmt.lower()}"
        fhash = f"sha256_{i:08x}_{fmt}"
        size = 100000 + (i * 350)
        is_del = 1 if (i % 50 == 0) else 0
        synthetic_books.append((title, auth, path, size, fhash, fmt, is_del))

    cur.executemany("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format, is_deleted)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, synthetic_books)
    
    # Add reading_progress for half of the newly inserted books
    cur.execute("SELECT id FROM books WHERE file_hash LIKE 'sha256_%' LIMIT 500;")
    new_book_ids = [row[0] for row in cur.fetchall()]
    
    synthetic_rp = []
    for idx, b_id in enumerate(new_book_ids):
        pct = (idx % 100) * 1.0
        synthetic_rp.append((b_id, pct, f"2026-10-28T{10 + (idx % 12):02d}:{(idx % 60):02d}:00Z"))
    
    cur.executemany("""
        INSERT INTO reading_progress (book_id, progress_percent, last_opened_at)
        VALUES (?, ?, ?);
    """, synthetic_rp)

    conn.commit()
    print("  1,000 books and 500 reading progress entries committed.")

    # 6a: Check Natural Index Selection for duplicate hash lookup (WITHOUT INDEXED BY)
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE file_hash = 'sha256_00000005_TXT';")
    plan_hash = cur.fetchall()
    plan_hash_str = " | ".join([p[3] for p in plan_hash])
    print(f"  [Natural Plan] file_hash lookup: {plan_hash_str}")
    # Note: SQLite may use sqlite_autoindex_books_2 or idx_books_file_hash
    if "USING INDEX" in plan_hash_str or "USING COVERING INDEX" in plan_hash_str:
        print("  [Info] file_hash lookup uses an index.")

    # Check for redundant indexes
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='books';")
    indexes = cur.fetchall()
    print(f"  [Info] All indexes on 'books':")
    for idx_name, idx_sql in indexes:
        print(f"    - {idx_name}: {idx_sql}")

    # 6b: Title Search: Exact vs Prefix vs Case-Insensitive LIKE
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE title = 'Book Title Volume 0042 - Philip K. Dick';")
    plan_title_exact = cur.fetchall()
    plan_title_exact_str = " | ".join([p[3] for p in plan_title_exact])
    print(f"  [Natural Plan] Exact title match: {plan_title_exact_str}")

    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE title LIKE 'Book Title Volume 0042%';")
    plan_title_like_prefix = cur.fetchall()
    plan_title_like_prefix_str = " | ".join([p[3] for p in plan_title_like_prefix])
    print(f"  [Natural Plan] Prefix LIKE match ('Book Title...%'): {plan_title_like_prefix_str}")

    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE title LIKE '%0042%';")
    plan_title_like_sub = cur.fetchall()
    plan_title_like_sub_str = " | ".join([p[3] for p in plan_title_like_sub])
    print(f"  [Natural Plan] Substring LIKE match ('%0042%'): {plan_title_like_sub_str}")

    # 6c: Author Search (Does books.author have an index?)
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE author = 'Frank Herbert';")
    plan_author = cur.fetchall()
    plan_author_str = " | ".join([p[3] for p in plan_author])
    print(f"  [Natural Plan] Author search on books(author): {plan_author_str}")

    # 6d: Format Filter & Soft Delete
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE is_deleted = 0 AND format = 'EPUB';")
    plan_fmt = cur.fetchall()
    plan_fmt_str = " | ".join([p[3] for p in plan_fmt])
    print(f"  [Natural Plan] Format filter (is_deleted=0 AND format='EPUB'): {plan_fmt_str}")

    # 6e: Recent Books (Library Sorting by last_opened_at)
    cur.execute("""
        EXPLAIN QUERY PLAN
        SELECT b.id, b.title, b.author, b.cover_path, rp.progress_percent, rp.last_opened_at
        FROM books b
        JOIN reading_progress rp ON b.id = rp.book_id
        WHERE b.is_deleted = 0
        ORDER BY rp.last_opened_at DESC
        LIMIT 20;
    """)
    plan_recent = cur.fetchall()
    plan_recent_str = " | ".join([p[3] for p in plan_recent])
    print(f"  [Natural Plan] Recent books join and sort: {plan_recent_str}")

    # 6f: Folder Books Query
    cur.execute("""
        EXPLAIN QUERY PLAN
        SELECT b.id, b.title, b.author
        FROM books b
        JOIN book_folder_binder bfb ON b.id = bfb.book_id
        WHERE bfb.folder_id = 1 AND b.is_deleted = 0;
    """)
    plan_folder = cur.fetchall()
    plan_folder_str = " | ".join([p[3] for p in plan_folder])
    print(f"  [Natural Plan] Folder contents query: {plan_folder_str}")

    # Evaluate index observations
    # 1. Redundant index on file_hash:
    explicit_file_hash = "idx_books_file_hash" in [idx[0] for idx in indexes]
    if explicit_file_hash:
        results["g6_redundant_index_file_hash"] = "FAIL: idx_books_file_hash is still present in schema!"
        print("  [FAIL] Redundant Index: 'idx_books_file_hash' is still present in schema.")
    else:
        results["g6_redundant_index_file_hash"] = "PASS"
        print("  [PASS] Redundant Index 'idx_books_file_hash' successfully pruned; UNIQUE autoindex utilized.")
    
    # 2. Case insensitive title index:
    if "USING INDEX idx_books_title" in plan_title_like_prefix_str:
        results["g6_title_like_nocase_index"] = "PASS"
        print("  [PASS] Title prefix LIKE query utilizes 'idx_books_title' range scan (COLLATE NOCASE).")
    else:
        results["g6_title_like_nocase_index"] = f"FAIL: Expected index search, got: {plan_title_like_prefix_str}"
        print(f"  [FAIL] Title prefix LIKE did NOT use idx_books_title: {plan_title_like_prefix_str}")
    
    # 3. Missing index on books.author:
    if "USING INDEX idx_books_author" in plan_author_str:
        results["g6_author_index"] = "PASS"
        print("  [PASS] Author filter query utilizes 'idx_books_author'.")
    else:
        results["g6_author_index"] = f"FAIL: Expected index search, got: {plan_author_str}"
        print(f"  [FAIL] Author filter did NOT use idx_books_author: {plan_author_str}")

    # --------------------------------------------------------------------------
    # GROUP 7: Edge Cases & Unicode / Path Extremes
    # --------------------------------------------------------------------------
    print("\n>>> GROUP 7: Edge Cases, Unicode & Extremes")

    # 7a: Long Unicode Titles & Emoji
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('📖 War and Peace — Война и мир — 戰爭與和平 🚀', 'Лев Толстой', 'C:/books/unicode_war_peace.epub', 2500000, 'hash_unicode_1', 'EPUB');
    """)
    uni_id = cur.lastrowid
    cur.execute("SELECT title, author FROM books WHERE id = ?;", (uni_id,))
    u_title, u_author = cur.fetchone()
    assert '📖' in u_title and 'Война' in u_title and '戰爭' in u_title
    print("  [PASS] Full multi-byte UTF-8, Cyrillic, CJK, and 4-byte emoji strings handled without corruption.")

    # 7b: Path with Windows special characters / spaces
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('Spaces and Quotes', 'Author Path', 'C:/My E-Books/Sci-Fi & Fantasy (2026)/"Special" [Folder]/test.pdf', 100, 'hash_path_special', 'PDF');
    """)
    print("  [PASS] Complex file paths with spaces, brackets, ampersands, and quotes handled.")

    # 7c: Negative or Zero file_size
    try:
        cur.execute("""
            INSERT INTO books (title, author, file_path, file_size, file_hash, format)
            VALUES ('Negative Size Book', 'Author Zero', 'C:/books/neg.epub', -500, 'hash_neg_size', 'EPUB');
        """)
        results["g7_negative_file_size"] = "FAIL: Negative file_size allowed!"
        print("  [FAIL] Negative file_size allowed (-500). Schema has no CHECK(file_size >= 0).")
    except sqlite3.IntegrityError as e:
        results["g7_negative_file_size"] = "PASS"
        print(f"  [PASS] Negative file_size rejected: {e}")

    # 7d: Self-referencing folder loop
    try:
        cur.execute("INSERT INTO folders (id, name, parent_id) VALUES (100, 'Loop Folder', 100);")
        results["g7_folder_self_parent"] = "FAIL: Folder allowed to have parent_id = id!"
        print("  [FAIL] Folder allowed to have parent_id = id. Schema has no CHECK(parent_id != id).")
    except sqlite3.IntegrityError as e:
        results["g7_folder_self_parent"] = "PASS"
        print(f"  [PASS] Folder self-parenting loop rejected: {e}")

    print("\n" + "=" * 80)
    print("ALL EMPIRICAL TESTS COMPLETED.")
    print("SUMMARY OF TEST RESULTS:")
    for k, v in results.items():
        print(f"  {k:30s} -> {v}")
    print("=" * 80)

    conn.close()

if __name__ == "__main__":
    run_tests()
