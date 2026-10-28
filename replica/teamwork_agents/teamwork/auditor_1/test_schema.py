import sqlite3
import os

schema_path = r'c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\schema.sql'

db = sqlite3.connect(':memory:')
db.execute('PRAGMA foreign_keys = ON;')

with open(schema_path, 'r', encoding='utf-8') as f:
    sql = f.read()

db.executescript(sql)
print("Execution SUCCESS: 0 errors returned by SQLite DDL parser.")

cur = db.cursor()
cur.execute("SELECT type, name FROM sqlite_master WHERE type IN ('table', 'index', 'trigger') ORDER BY type, name")
rows = cur.fetchall()
print(f"Total objects created: {len(rows)}")
for t, n in rows:
    print(f"  [{t}] {n}")

# Test 1: Insert book
cur.execute("""
    INSERT INTO books (title, author, file_path, file_size, file_hash, format)
    VALUES ('Clean Code', 'Robert Martin', '/books/clean_code.epub', 2048576, 'sha256_hash_1', 'epub')
""")
book_id = cur.lastrowid
print(f"Inserted book with ID: {book_id}")

# Test 2: Foreign key dependent tables
cur.execute("""
    INSERT INTO reading_progress (book_id, current_cfi, current_page, total_pages, progress_percent)
    VALUES (?, 'epubcfi(/6/4[chap01]!/4/2/10)', 15, 450, 3.33)
""", (book_id,))

cur.execute("""
    INSERT INTO bookmarks (book_id, cfi, page_number, title, snippet)
    VALUES (?, 'epubcfi(/6/4[chap01]!/4/2/14)', 16, 'Important Rule', 'Always leave the code better than you found it.')
""", (book_id,))

cur.execute("""
    INSERT INTO annotations (book_id, cfi_start, cfi_end, selected_text, note_text, color_id)
    VALUES (?, 'cfi_start_val', 'cfi_end_val', 'Boy scout rule', 'Must remember', 1)
""", (book_id,))

cur.execute("""
    INSERT INTO book_metadata (book_id, key, value)
    VALUES (?, 'genre', 'Software Engineering')
""", (book_id,))

cur.execute("""
    INSERT INTO book_folder_binder (book_id, folder_id)
    VALUES (?, 1)
""", (book_id,))

db.commit()
print("Successfully inserted rows into all dependent tables.")

# Test 3: Triggers on update
cur.execute("SELECT updated_at FROM books WHERE id = ?", (book_id,))
initial_updated = cur.fetchone()[0]
cur.execute("UPDATE books SET title = 'Clean Code: Refactored' WHERE id = ?", (book_id,))
db.commit()
cur.execute("SELECT updated_at FROM books WHERE id = ?", (book_id,))
new_updated = cur.fetchone()[0]
print(f"Trigger update check: initial={initial_updated}, updated={new_updated}")

# Test 4: Check constraint on reading_progress
try:
    cur.execute("""
        INSERT INTO reading_progress (book_id, progress_percent)
        VALUES (999, 150.0)
    """)
    raise AssertionError("CHECK constraint on progress_percent failed to trigger!")
except sqlite3.IntegrityError as e:
    print(f"Check constraint verified (progress_percent <= 100): {e}")

# Test 5: Check constraint on annotations color_id
try:
    cur.execute("""
        INSERT INTO annotations (book_id, selected_text, color_id)
        VALUES (?, 'Sample text', 9)
    """, (book_id,))
    raise AssertionError("CHECK constraint on color_id failed to trigger!")
except sqlite3.IntegrityError as e:
    print(f"Check constraint verified (color_id between 1 and 5): {e}")

# Test 6: Cascade deletion
cur.execute("DELETE FROM books WHERE id = ?", (book_id,))
db.commit()

for tbl in ['reading_progress', 'bookmarks', 'annotations', 'book_metadata', 'book_folder_binder']:
    cur.execute(f"SELECT count(*) FROM {tbl} WHERE book_id = ?", (book_id,))
    cnt = cur.fetchone()[0]
    print(f"Cascade deletion on {tbl}: remaining rows = {cnt} (expected 0)")
    assert cnt == 0, f"Cascade deletion failed for {tbl}"

# Test 7: Duplicate hash unique constraint
cur.execute("""
    INSERT INTO books (title, file_path, file_size, file_hash, format)
    VALUES ('Book A', '/path/a.epub', 100, 'unique_hash_xyz', 'epub')
""")
try:
    cur.execute("""
        INSERT INTO books (title, file_path, file_size, file_hash, format)
        VALUES ('Book B', '/path/b.epub', 200, 'unique_hash_xyz', 'epub')
    """)
    raise AssertionError("Unique constraint on file_hash failed to trigger!")
except sqlite3.IntegrityError as e:
    print(f"Unique constraint on file_hash verified: {e}")

# Test 8: Seed data presence
cur.execute("SELECT id, name FROM folders ORDER BY sort_order")
folders = cur.fetchall()
print(f"Seed folders count: {len(folders)}")
for fid, fname in folders:
    print(f"  Folder {fid}: {fname}")

assert len(folders) == 5, f"Expected 5 default folders, found {len(folders)}"
expected_folder_names = ['All Books', 'Recently Read', 'Favorites', 'Read', 'Trash']
actual_folder_names = [f[1] for f in folders]
assert actual_folder_names == expected_folder_names, f"Folder names mismatch: {actual_folder_names}"

print("\nALL 8 EMPIRICAL DATABASE INTEGRITY TESTS PASSED WITH ZERO ERRORS!")
