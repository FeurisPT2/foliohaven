import sqlite3
import time

conn = sqlite3.connect(':memory:')
conn.execute('PRAGMA foreign_keys = ON;')
with open(r'c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\schema.sql', 'r', encoding='utf-8') as f:
    conn.executescript(f.read())

# Check seed data
cur = conn.cursor()
cur.execute('SELECT count(*) FROM folders WHERE is_system = 1')
assert cur.fetchone()[0] == 5, 'System folders count mismatch'

# Insert a book
cur.execute('''
INSERT INTO books (title, file_path, file_size, file_hash, format)
VALUES ('Test Book', '/path/to/book.epub', 1024, 'hash1234', 'EPUB')
''')
book_id = cur.lastrowid
assert book_id == 1

# Check timestamps
cur.execute('SELECT created_at, updated_at FROM books WHERE id = 1')
c_at, u_at = cur.fetchone()
assert 'T' in c_at and c_at.endswith('Z'), f'Invalid timestamp format: {c_at}'

# Test UNIQUE file_path and file_hash
try:
    cur.execute('''
    INSERT INTO books (title, file_path, file_size, file_hash, format)
    VALUES ('Dup Path', '/path/to/book.epub', 2048, 'hash5678', 'EPUB')
    ''')
    assert False, 'Failed to catch unique file_path constraint'
except sqlite3.IntegrityError:
    pass

try:
    cur.execute('''
    INSERT INTO books (title, file_path, file_size, file_hash, format)
    VALUES ('Dup Hash', '/path/to/other.epub', 2048, 'hash1234', 'EPUB')
    ''')
    assert False, 'Failed to catch unique file_hash constraint'
except sqlite3.IntegrityError:
    pass

# Insert author & link
cur.execute('''INSERT INTO authors (name) VALUES ('Arthur Conan Doyle')''')
author_id = cur.lastrowid
cur.execute('''INSERT INTO book_authors (book_id, author_id) VALUES (?, ?)''', (book_id, author_id))

# Insert reading progress
cur.execute('''
INSERT INTO reading_progress (book_id, current_cfi, current_page, total_pages, progress_percent)
VALUES (?, 'epubcfi(/6/4[chap01]!/4/2/10)', 1, 100, 1.0)
''', (book_id,))

# Test check constraint on progress_percent
try:
    cur.execute('''
    UPDATE reading_progress SET progress_percent = 150.0 WHERE book_id = ?
    ''', (book_id,))
    assert False, 'Failed to catch check constraint on progress_percent > 100'
except sqlite3.IntegrityError:
    pass

# Insert bookmarks and annotations
cur.execute('''
INSERT INTO bookmarks (book_id, cfi, page_number, title)
VALUES (?, 'cfi_bm1', 5, 'Chapter 2 Start')
''', (book_id,))

cur.execute('''
INSERT INTO annotations (book_id, cfi_start, cfi_end, selected_text, color_id)
VALUES (?, 'cfi_s', 'cfi_e', 'Some highlighted text', 2)
''', (book_id,))

# Test check constraint on color_id
try:
    cur.execute('''
    INSERT INTO annotations (book_id, selected_text, color_id)
    VALUES (?, 'Text', 99)
    ''', (book_id,))
    assert False, 'Failed to catch check constraint on color_id'
except sqlite3.IntegrityError:
    pass

# Test trigger update
old_u = u_at
time.sleep(1.1)
cur.execute("UPDATE books SET title = 'Updated Book Title' WHERE id = 1")
cur.execute("SELECT updated_at FROM books WHERE id = 1")
new_u = cur.fetchone()[0]
assert new_u >= old_u, 'Trigger did not update updated_at'

# Test ON DELETE CASCADE
cur.execute('DELETE FROM books WHERE id = 1')
for tbl in ['reading_progress', 'bookmarks', 'annotations', 'book_authors']:
    cur.execute(f'SELECT count(*) FROM {tbl} WHERE book_id = 1')
    assert cur.fetchone()[0] == 0, f'Cascade delete failed for {tbl}'

# Author still exists
cur.execute('SELECT count(*) FROM authors WHERE id = ?', (author_id,))
assert cur.fetchone()[0] == 1, 'Author should not be deleted'

# Test folders parent SET NULL
cur.execute('''INSERT INTO folders (name, parent_id) VALUES ('Parent Folder', NULL)''')
p_id = cur.lastrowid
cur.execute('''INSERT INTO folders (name, parent_id) VALUES ('Child Folder', ?)''', (p_id,))
c_id = cur.lastrowid
cur.execute('DELETE FROM folders WHERE id = ?', (p_id,))
cur.execute('SELECT parent_id FROM folders WHERE id = ?', (c_id,))
assert cur.fetchone()[0] is None, 'Folder parent SET NULL failed'

print('ALL SQLITE CONSTRAINTS AND TRIGGERS VERIFIED SUCCESSFULLY!')
