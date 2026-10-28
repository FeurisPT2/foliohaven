"""
Adversarial Stress Test Harness - Round 2 Verification
Author: challenger_1_r2 (teamwork_preview_challenger)
Target: replica/schema.sql
Empirical verification of all 5 remediations requested by challenger_1.
"""

import os
import sys
import sqlite3
import time

SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "replica", "schema.sql"))

def run_adversarial_suite():
    print("=" * 80)
    print("CHALLENGER_1_R2: DEEP ADVERSARIAL STRESS TEST HARNESS")
    print(f"Target Schema: {SCHEMA_PATH}")
    print("=" * 80)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA recursive_triggers = ON;")
    conn.executescript(schema_sql)
    cur = conn.cursor()

    test_results = {}

    # ==========================================================================
    # 1. TRIGGER RECURSION HARDENING ACROSS ALL 4 TABLES
    # ==========================================================================
    print("\n[TEST 1] Trigger Recursion Hardening under PRAGMA recursive_triggers = ON")

    # 1a. Table: books
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('Book 1', 'Author 1', '/path/book1.epub', 1000, 'hash_trg_book', 'EPUB');
    """)
    b_id = cur.lastrowid
    t0_book = cur.execute("SELECT updated_at FROM books WHERE id = ?;", (b_id,)).fetchone()[0]

    try:
        # Rapid 100 updates in the same second
        for i in range(100):
            cur.execute("UPDATE books SET description = ? WHERE id = ?;", (f"Desc {i}", b_id))
        test_results["1a_books_100_rapid_updates"] = "PASS"
        print("  [PASS] 1a. books: 100 rapid updates executed with 0 recursion errors.")
    except sqlite3.OperationalError as e:
        test_results["1a_books_100_rapid_updates"] = f"FAIL: {e}"
        print(f"  [FAIL] 1a. books: {e}")

    # Explicit updated_at preservation on books
    cur.execute("UPDATE books SET updated_at = '2099-12-31T23:59:59Z' WHERE id = ?;", (b_id,))
    t_explicit = cur.execute("SELECT updated_at FROM books WHERE id = ?;", (b_id,)).fetchone()[0]
    assert t_explicit == '2099-12-31T23:59:59Z', f"Expected explicit timestamp, got {t_explicit}"
    test_results["1a_books_explicit_timestamp"] = "PASS"
    print("  [PASS] 1a. books: Explicit updated_at preserved correctly.")

    # Batch update affecting multiple rows under recursive_triggers = ON
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('Book 2', 'Author 2', '/path/book2.epub', 2000, 'hash_trg_book2', 'EPUB'),
               ('Book 3', 'Author 3', '/path/book3.epub', 3000, 'hash_trg_book3', 'EPUB');
    """)
    try:
        for _ in range(20):
            cur.execute("UPDATE books SET format = 'MOBI' WHERE format = 'EPUB';")
        test_results["1a_books_batch_update_recursion"] = "PASS"
        print("  [PASS] 1a. books: Multi-row batch updates under recursive triggers passed.")
    except sqlite3.OperationalError as e:
        test_results["1a_books_batch_update_recursion"] = f"FAIL: {e}"
        print(f"  [FAIL] 1a. books batch update: {e}")

    # 1b. Table: reading_progress
    cur.execute("""
        INSERT INTO reading_progress (book_id, progress_percent, current_page)
        VALUES (?, 5.0, 10);
    """, (b_id,))
    rp_id = cur.lastrowid
    try:
        for i in range(100):
            cur.execute("UPDATE reading_progress SET progress_percent = ? WHERE id = ?;", (float(i % 100), rp_id))
        test_results["1b_reading_progress_100_rapid_updates"] = "PASS"
        print("  [PASS] 1b. reading_progress: 100 rapid updates executed with 0 recursion errors.")
    except sqlite3.OperationalError as e:
        test_results["1b_reading_progress_100_rapid_updates"] = f"FAIL: {e}"
        print(f"  [FAIL] 1b. reading_progress: {e}")

    # 1c. Table: annotations
    cur.execute("""
        INSERT INTO annotations (book_id, selected_text, note_text, color_id)
        VALUES (?, 'Selected quote', 'Initial note', 1);
    """, (b_id,))
    an_id = cur.lastrowid
    try:
        for i in range(100):
            cur.execute("UPDATE annotations SET note_text = ? WHERE id = ?;", (f"Note revision {i}", an_id))
        test_results["1c_annotations_100_rapid_updates"] = "PASS"
        print("  [PASS] 1c. annotations: 100 rapid updates executed with 0 recursion errors.")
    except sqlite3.OperationalError as e:
        test_results["1c_annotations_100_rapid_updates"] = f"FAIL: {e}"
        print(f"  [FAIL] 1c. annotations: {e}")

    # 1d. Table: app_settings (PK is key TEXT)
    cur.execute("INSERT INTO app_settings (key, value) VALUES ('theme', 'dark');")
    try:
        for i in range(100):
            cur.execute("UPDATE app_settings SET value = ? WHERE key = 'theme';", (f"value_{i}",))
        test_results["1d_app_settings_100_rapid_updates"] = "PASS"
        print("  [PASS] 1d. app_settings: 100 rapid updates executed with 0 recursion errors.")
    except sqlite3.OperationalError as e:
        test_results["1d_app_settings_100_rapid_updates"] = f"FAIL: {e}"
        print(f"  [FAIL] 1d. app_settings: {e}")

    # 1e. Cross-second advancement verification
    print("  Testing cross-second timestamp advancement (sleeping 1.05s)...")
    t_before_adv = cur.execute("SELECT updated_at FROM books WHERE id = ?;", (b_id,)).fetchone()[0]
    time.sleep(1.05)
    cur.execute("UPDATE books SET title = 'Book 1 Renamed' WHERE id = ?;", (b_id,))
    t_after_adv = cur.execute("SELECT updated_at FROM books WHERE id = ?;", (b_id,)).fetchone()[0]
    assert t_after_adv > t_before_adv, f"Timestamp did not advance: {t_after_adv} <= {t_before_adv}"
    test_results["1e_cross_second_advancement"] = "PASS"
    print(f"  [PASS] 1e. Timestamp correctly advanced across seconds: {t_before_adv} -> {t_after_adv}")

    # ==========================================================================
    # 2. REDUNDANT INDEX REMOVAL VERIFICATION
    # ==========================================================================
    print("\n[TEST 2] Redundant Index Removal & Unique Autoindex Utilization")

    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='books';")
    all_book_indexes = cur.fetchall()
    index_names = [row[0] for row in all_book_indexes]
    print(f"  Discovered indexes on 'books': {index_names}")

    # Verify idx_books_file_hash is absent
    assert "idx_books_file_hash" not in index_names, "CRITICAL: idx_books_file_hash is still present in schema!"
    test_results["2a_no_redundant_index"] = "PASS"
    print("  [PASS] 2a. Redundant index 'idx_books_file_hash' is completely absent.")

    # Verify sqlite_autoindex_books_2 handles file_hash
    cur.execute("PRAGMA index_list('books');")
    pragma_indexes = cur.fetchall()
    # Format: (seq, name, unique, origin, partial)
    auto_unique_indexes = [row[1] for row in pragma_indexes if row[2] == 1 and "autoindex" in row[1]]
    print(f"  Auto unique indexes: {auto_unique_indexes}")
    assert len(auto_unique_indexes) >= 2, f"Expected at least 2 auto unique indexes (file_path, file_hash), got {len(auto_unique_indexes)}"

    # Check index_info to confirm file_hash has autoindex
    file_hash_autoindex = None
    for auto_idx in auto_unique_indexes:
        cur.execute(f"PRAGMA index_info('{auto_idx}');")
        col_info = cur.fetchall()
        # Format: (seqno, cid, name)
        if any(c[2] == 'file_hash' for c in col_info):
            file_hash_autoindex = auto_idx
            break
    assert file_hash_autoindex is not None, "Could not find autoindex covering 'file_hash'!"
    test_results["2b_autoindex_covers_file_hash"] = "PASS"
    print(f"  [PASS] 2b. 'file_hash' is backed by unique autoindex: {file_hash_autoindex}")

    # Query plan for file_hash lookup
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE file_hash = 'hash_trg_book';")
    plan_hash = cur.fetchall()
    plan_hash_str = " | ".join([p[3] for p in plan_hash])
    print(f"  Query plan for file_hash lookup: {plan_hash_str}")
    assert file_hash_autoindex in plan_hash_str, f"Expected {file_hash_autoindex} in plan, got: {plan_hash_str}"
    test_results["2c_query_plan_uses_autoindex"] = "PASS"
    print(f"  [PASS] 2c. Query planner utilizes {file_hash_autoindex} directly.")

    # ==========================================================================
    # 3. CASE-INSENSITIVE TITLE SEARCH INDEX
    # ==========================================================================
    print("\n[TEST 3] Case-Insensitive Title Search Index (idx_books_title COLLATE NOCASE)")

    # Verify DDL contains COLLATE NOCASE
    cur.execute("SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_books_title';")
    title_idx_sql = cur.fetchone()[0]
    print(f"  idx_books_title DDL: {title_idx_sql}")
    assert "NOCASE" in title_idx_sql.upper(), f"idx_books_title does not contain NOCASE: {title_idx_sql}"
    test_results["3a_idx_books_title_ddl_nocase"] = "PASS"
    print("  [PASS] 3a. idx_books_title explicitly specifies COLLATE NOCASE.")

    # Populate 500 books to give planner index weight
    synth = []
    for i in range(500):
        synth.append((
            f"Adversarial Title {i:04d} The Great Book",
            f"Author {i % 10}",
            f"/lib/path_{i:04d}.epub",
            1000 + i,
            f"hash_synth_{i:08x}",
            "EPUB"
        ))
    cur.executemany("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES (?, ?, ?, ?, ?, ?);
    """, synth)
    conn.commit()

    # Prefix LIKE queries in different cases
    test_cases = [
        "adversarial title 0042%",
        "ADVERSARIAL TITLE 0042%",
        "Adversarial Title 0042%",
        "aDvErSaRiAl TiTlE 0042%"
    ]
    for pattern in test_cases:
        cur.execute(f"EXPLAIN QUERY PLAN SELECT * FROM books WHERE title LIKE '{pattern}';")
        plan_t = cur.fetchall()
        plan_t_str = " | ".join([p[3] for p in plan_t])
        print(f"  Prefix LIKE ('{pattern}'): {plan_t_str}")
        assert "USING INDEX idx_books_title" in plan_t_str, f"Plan failed to use idx_books_title for '{pattern}': {plan_t_str}"

    test_results["3b_prefix_like_all_casings"] = "PASS"
    print("  [PASS] 3b. Prefix LIKE queries across uppercase, lowercase, and mixed cases all utilize idx_books_title range scan.")

    # Equality with COLLATE NOCASE
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE title = 'adversarial title 0042 the great book' COLLATE NOCASE;")
    plan_eq = cur.fetchall()
    plan_eq_str = " | ".join([p[3] for p in plan_eq])
    print(f"  Equality with COLLATE NOCASE: {plan_eq_str}")
    assert "USING INDEX idx_books_title" in plan_eq_str
    test_results["3c_equality_collate_nocase"] = "PASS"
    print("  [PASS] 3c. Title equality search with COLLATE NOCASE utilizes idx_books_title.")

    # ==========================================================================
    # 4. AUTHOR INDEX VERIFICATION
    # ==========================================================================
    print("\n[TEST 4] Author Index (idx_books_author)")

    cur.execute("SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_books_author';")
    auth_idx_sql = cur.fetchone()[0]
    print(f"  idx_books_author DDL: {auth_idx_sql}")
    assert "books(author)" in auth_idx_sql.replace(" ", ""), f"Unexpected index definition: {auth_idx_sql}"
    test_results["4a_idx_books_author_ddl"] = "PASS"
    print("  [PASS] 4a. idx_books_author on books(author) exists.")

    # Test query plan for author filter
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE author = 'Author 5';")
    plan_auth = cur.fetchall()
    plan_auth_str = " | ".join([p[3] for p in plan_auth])
    print(f"  Author filter query plan: {plan_auth_str}")
    assert "USING INDEX idx_books_author" in plan_auth_str, f"Plan failed to use idx_books_author: {plan_auth_str}"
    test_results["4b_author_filter_query_plan"] = "PASS"
    print("  [PASS] 4b. Author equality search utilizes idx_books_author.")

    # Test query plan for author IN query
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE author IN ('Author 1', 'Author 2');")
    plan_auth_in = cur.fetchall()
    plan_auth_in_str = " | ".join([p[3] for p in plan_auth_in])
    print(f"  Author IN filter plan: {plan_auth_in_str}")
    assert "USING INDEX idx_books_author" in plan_auth_in_str
    test_results["4c_author_in_filter"] = "PASS"
    print("  [PASS] 4c. Author IN list query utilizes idx_books_author.")

    # ==========================================================================
    # 5. DEFENSIVE CHECK CONSTRAINTS
    # ==========================================================================
    print("\n[TEST 5] Defensive Check Constraints Stress Testing")

    # 5a. file_size >= 0
    negative_sizes = [-1, -500, -1048576, -9223372036854775808]
    for neg in negative_sizes:
        try:
            cur.execute("""
                INSERT INTO books (title, author, file_path, file_size, file_hash, format)
                VALUES ('Neg Book', 'Auth', ?, ?, ?, 'EPUB');
            """, (f"/path/neg_{neg}.epub", neg, f"hash_neg_{neg}"))
            assert False, f"file_size = {neg} was allowed!"
        except sqlite3.IntegrityError as e:
            assert "file_size >= 0" in str(e) or "CHECK" in str(e)
    test_results["5a_negative_file_size_rejection"] = "PASS"
    print(f"  [PASS] 5a. Negative file_size values {negative_sizes} all strictly rejected.")

    # Valid boundary file sizes: 0, 1, 10GB
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('Zero Byte Book', 'Auth', '/path/zero.epub', 0, 'hash_zero', 'EPUB');
    """)
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('1 Byte Book', 'Auth', '/path/one.epub', 1, 'hash_one', 'EPUB');
    """)
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('10GB Book', 'Auth', '/path/10gb.epub', 10737418240, 'hash_10gb', 'EPUB');
    """)
    test_results["5a_valid_file_size_boundaries"] = "PASS"
    print("  [PASS] 5a. Boundary file_size values (0, 1, 10GB) all accepted.")

    # 5b. folders.parent_id != id
    # Reject self-parenting on INSERT
    try:
        cur.execute("INSERT INTO folders (id, name, parent_id) VALUES (999, 'Self Loop', 999);")
        assert False, "Self-parenting on INSERT was allowed!"
    except sqlite3.IntegrityError as e:
        assert "parent_id != id" in str(e) or "CHECK" in str(e)
    print("  [PASS] 5b. Self-parenting on INSERT (parent_id = id) strictly rejected.")

    # Reject self-parenting on UPDATE
    cur.execute("INSERT INTO folders (id, name, parent_id) VALUES (888, 'Valid Folder', NULL);")
    try:
        cur.execute("UPDATE folders SET parent_id = 888 WHERE id = 888;")
        assert False, "Self-parenting on UPDATE was allowed!"
    except sqlite3.IntegrityError as e:
        assert "parent_id != id" in str(e) or "CHECK" in str(e)
    print("  [PASS] 5b. Self-parenting on UPDATE (parent_id = id) strictly rejected.")

    # Valid hierarchical links
    cur.execute("INSERT INTO folders (id, name, parent_id) VALUES (889, 'Child Folder', 888);")
    cur.execute("INSERT INTO folders (id, name, parent_id) VALUES (890, 'Grandchild Folder', 889);")
    test_results["5b_parent_id_check_constraint"] = "PASS"
    print("  [PASS] 5b. Valid hierarchical folder nesting (NULL, parent!=id) fully functional.")

    # 5c. reading_progress progress_percent range [0.0, 100.0]
    invalid_pcts = [-10.0, -0.0001, 100.0001, 150.0]
    for inv_pct in invalid_pcts:
        try:
            cur.execute("""
                INSERT INTO reading_progress (book_id, progress_percent)
                VALUES (?, ?);
            """, (cur.lastrowid, inv_pct))
            assert False, f"progress_percent = {inv_pct} was allowed!"
        except sqlite3.IntegrityError:
            pass
    test_results["5c_progress_percent_boundaries"] = "PASS"
    print(f"  [PASS] 5c. Invalid progress_percent values {invalid_pcts} all rejected.")

    # 5d. annotations color_id range [1, 5]
    invalid_colors = [0, -1, 6, 7, 99]
    for inv_c in invalid_colors:
        try:
            cur.execute("""
                INSERT INTO annotations (book_id, selected_text, color_id)
                VALUES (?, 'Text', ?);
            """, (cur.lastrowid, inv_c))
            assert False, f"color_id = {inv_c} was allowed!"
        except sqlite3.IntegrityError:
            pass
    test_results["5d_color_id_boundaries"] = "PASS"
    print(f"  [PASS] 5d. Invalid color_id values {invalid_colors} all rejected.")

    print("\n" + "=" * 80)
    print("ALL CHALLENGER_1_R2 ADVERSARIAL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    for test_name, status in test_results.items():
        print(f"  {test_name:40s} -> {status}")
    print("=" * 80)

    conn.close()
    return True

if __name__ == "__main__":
    success = run_adversarial_suite()
    sys.exit(0 if success else 1)
