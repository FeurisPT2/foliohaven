"""
Empirical Remediation Verification Script for Milestone 3 Remediation
Worker: worker_m3_r2
Target: replica/schema.sql
"""

import sqlite3
import os

SCHEMA_PATH = r"c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\schema.sql"

def verify_all():
    print("=" * 80)
    print("REMEDIATION VERIFICATION SUITE: replica/schema.sql")
    print("=" * 80)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(schema_sql)
    cur = conn.cursor()

    # 1. Trigger Recursion Hardening under recursive_triggers = ON
    print("\n--- 1. Testing Trigger Recursion Hardening (recursive_triggers = ON) ---")
    conn.execute("PRAGMA recursive_triggers = ON;")
    cur.execute("""
        INSERT INTO books (title, author, file_path, file_size, file_hash, format)
        VALUES ('Recursion Test Book', 'Author T', '/path/rec.epub', 1000, 'hash_rec_1', 'EPUB');
    """)
    b_id = cur.lastrowid
    
    # Rapid successive updates within the same UTC second
    for i in range(25):
        cur.execute("UPDATE books SET description = ? WHERE id = ?;", (f"Rapid update {i}", b_id))
    print("  [PASS] 25 rapid updates executed with PRAGMA recursive_triggers = ON without infinite recursion error.")

    # 2. Redundant Index Verification
    print("\n--- 2. Checking Removal of Redundant Index idx_books_file_hash ---")
    cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='books';")
    book_indexes = [r[0] for r in cur.fetchall()]
    print(f"  Indexes on 'books': {book_indexes}")
    assert "idx_books_file_hash" not in book_indexes, "idx_books_file_hash should NOT be present in schema!"
    assert any("autoindex" in idx for idx in book_indexes), "sqlite_autoindex for UNIQUE(file_hash) must be present."
    print("  [PASS] Redundant index idx_books_file_hash removed; UNIQUE constraint creates internal autoindex.")

    # 3. Case-Insensitive Title Index Search Plan
    print("\n--- 3. Checking Case-Insensitive Title Search Index (idx_books_title) ---")
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE title LIKE 'Recursion%';")
    plan_title = cur.fetchall()
    plan_title_str = " | ".join([p[3] for p in plan_title])
    print(f"  Query plan for title LIKE 'Recursion%': {plan_title_str}")
    assert "USING INDEX idx_books_title" in plan_title_str, f"Expected index search, got: {plan_title_str}"
    print("  [PASS] Prefix LIKE search successfully converted to index range scan on idx_books_title (title COLLATE NOCASE).")

    # 4. Author Index Search Plan
    print("\n--- 4. Checking Missing Author Index (idx_books_author) ---")
    cur.execute("EXPLAIN QUERY PLAN SELECT * FROM books WHERE author = 'Author T';")
    plan_author = cur.fetchall()
    plan_author_str = " | ".join([p[3] for p in plan_author])
    print(f"  Query plan for author = 'Author T': {plan_author_str}")
    assert "USING INDEX idx_books_author" in plan_author_str, f"Expected index search, got: {plan_author_str}"
    print("  [PASS] Author search successfully uses index idx_books_author.")

    # 5. Defensive Check Constraints
    print("\n--- 5. Checking Defensive CHECK Constraints ---")
    # 5a: books.file_size >= 0
    try:
        cur.execute("""
            INSERT INTO books (title, author, file_path, file_size, file_hash, format)
            VALUES ('Negative Book', 'Author N', '/path/neg.epub', -100, 'hash_neg', 'EPUB');
        """)
        raise AssertionError("Negative file_size was allowed!")
    except sqlite3.IntegrityError as e:
        print(f"  [PASS] Negative file_size successfully rejected: {e}")

    # 5b: folders.parent_id != id
    try:
        cur.execute("INSERT INTO folders (id, name, parent_id) VALUES (100, 'Self Loop Folder', 100);")
        raise AssertionError("Self-parenting loop (parent_id == id) was allowed!")
    except sqlite3.IntegrityError as e:
        print(f"  [PASS] Self-parenting loop (parent_id == id) successfully rejected: {e}")

    # Verify valid parent_id != id works normally
    cur.execute("INSERT INTO folders (id, name, parent_id) VALUES (200, 'Root Folder', NULL);")
    cur.execute("INSERT INTO folders (id, name, parent_id) VALUES (201, 'Child Folder', 200);")
    print("  [PASS] Valid hierarchical folders (parent_id IS NULL and parent_id != id) accepted.")

    conn.close()
    print("\n" + "=" * 80)
    print("ALL 5 REMEDIATIONS VERIFIED AND CONFIRMED 100% OPERATIONAL!")
    print("=" * 80)

if __name__ == "__main__":
    verify_all()
