#!/usr/bin/env python3
"""
Independent Victory Audit Verification Harness
Author: victory_auditor_1 (Independent Post-Victory Auditor)
Target: Icecream Ebook Reader Clean-Room Replica
"""

import sys
import os
import sqlite3
import csv
import re
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REPLICA_DIR = os.path.join(PROJECT_ROOT, "replica")

print(f"Project Root: {PROJECT_ROOT}")
print(f"Replica Directory: {REPLICA_DIR}")

failures = []

def record_pass(test_name, details=""):
    print(f"  [PASS] {test_name}: {details}")

def record_fail(test_name, details=""):
    print(f"  [FAIL] {test_name}: {details}")
    failures.append(f"{test_name}: {details}")

print("\n" + "="*70)
print("PHASE 1: INDEPENDENT SQLITE SCHEMA EXECUTION & INTEGRITY TEST")
print("="*70)

schema_path = os.path.join(REPLICA_DIR, "schema.sql")
if not os.path.exists(schema_path):
    record_fail("schema_exists", f"File not found: {schema_path}")
    sys.exit(1)

with open(schema_path, "r", encoding="utf-8") as f:
    schema_sql = f.read()

# Connect to in-memory database
conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON;")
conn.execute("PRAGMA recursive_triggers = ON;")

try:
    conn.executescript(schema_sql)
    record_pass("schema_ddl_execution", "Executed schema.sql with 0 DDL syntax errors")
except Exception as e:
    record_fail("schema_ddl_execution", str(e))

cursor = conn.cursor()

# Verify Tables
expected_tables = {
    "books", "authors", "book_authors", "folders", "book_folder_binder",
    "reading_progress", "bookmarks", "annotations", "book_metadata", "app_settings"
}
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
actual_tables = {row[0] for row in cursor.fetchall()}

if expected_tables.issubset(actual_tables):
    record_pass("tables_inventory", f"All 10 required tables present: {sorted(list(expected_tables))}")
else:
    record_fail("tables_inventory", f"Missing tables: {expected_tables - actual_tables}")

# Verify Indexes
expected_indexes = {
    "idx_books_format", "idx_books_is_deleted", "idx_books_title", "idx_books_author",
    "idx_reading_progress_last_opened", "idx_bookmarks_book_id", "idx_annotations_book_id",
    "idx_book_folder_binder_folder", "idx_book_authors_author", "idx_folders_parent"
}
cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';")
actual_indexes = {row[0] for row in cursor.fetchall()}

if expected_indexes.issubset(actual_indexes):
    record_pass("indexes_inventory", f"All 10 lookup indexes present: {sorted(list(expected_indexes))}")
else:
    record_fail("indexes_inventory", f"Missing indexes: {expected_indexes - actual_indexes}")

# Verify Triggers
expected_triggers = {
    "trg_books_updated_at", "trg_reading_progress_updated_at",
    "trg_annotations_updated_at", "trg_app_settings_updated_at"
}
cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
actual_triggers = {row[0] for row in cursor.fetchall()}

if expected_triggers.issubset(actual_triggers):
    record_pass("triggers_inventory", f"All 4 updated_at triggers present: {sorted(list(expected_triggers))}")
else:
    record_fail("triggers_inventory", f"Missing triggers: {expected_triggers - actual_triggers}")

# Verify Seed Data
cursor.execute("SELECT id, name, is_system FROM folders ORDER BY id;")
seed_folders = cursor.fetchall()
expected_seed = [
    (1, 'All Books', 1),
    (2, 'Recently Read', 1),
    (3, 'Favorites', 1),
    (4, 'Read', 1),
    (5, 'Trash', 1)
]
if seed_folders == expected_seed:
    record_pass("seed_data", f"Default 5 system folders correctly initialized: {[s[1] for s in seed_folders]}")
else:
    record_fail("seed_data", f"Seed folders mismatch: got {seed_folders}")

# Test Constraints: Unique file_hash
try:
    cursor.execute("""
        INSERT INTO books (title, file_path, file_size, file_hash, format)
        VALUES ('Book A', '/path/a.epub', 1024, 'hash_unique_1', 'EPUB');
    """)
    conn.commit()
    cursor.execute("""
        INSERT INTO books (title, file_path, file_size, file_hash, format)
        VALUES ('Book B', '/path/b.epub', 2048, 'hash_unique_1', 'EPUB');
    """)
    record_fail("unique_file_hash", "Allowed duplicate file_hash insertion")
except sqlite3.IntegrityError:
    record_pass("unique_file_hash", "Rejected duplicate file_hash as expected")

# Test Constraints: Negative file_size
try:
    cursor.execute("""
        INSERT INTO books (title, file_path, file_size, file_hash, format)
        VALUES ('Negative Book', '/path/neg.epub', -10, 'hash_unique_neg', 'EPUB');
    """)
    record_fail("negative_file_size", "Allowed negative file_size")
except sqlite3.IntegrityError:
    record_pass("negative_file_size", "Rejected negative file_size (CHECK constraint)")

# Test Constraints: Self-parenting folder
try:
    cursor.execute("""
        INSERT INTO folders (id, name, parent_id) VALUES (100, 'Self Parent', 100);
    """)
    record_fail("folder_self_parent", "Allowed self-parenting folder")
except sqlite3.IntegrityError:
    record_pass("folder_self_parent", "Rejected self-parenting folder (CHECK parent_id != id)")

# Test Foreign Key Cascading Deletions
cursor.execute("""
    INSERT INTO books (id, title, file_path, file_size, file_hash, format)
    VALUES (42, 'Parent Book', '/path/parent.epub', 5000, 'hash_parent_42', 'EPUB');
""")
cursor.execute("""
    INSERT INTO reading_progress (book_id, current_cfi, current_page, total_pages, progress_percent)
    VALUES (42, 'epubcfi(/6/4)', 12, 100, 12.0);
""")
cursor.execute("""
    INSERT INTO bookmarks (book_id, page_number, title)
    VALUES (42, 15, 'Chapter 2 Bookmark');
""")
cursor.execute("""
    INSERT INTO annotations (book_id, selected_text, note_text, color_id)
    VALUES (42, 'Important text quote', 'A comment on the quote', 2);
""")
cursor.execute("""
    INSERT INTO book_metadata (book_id, key, value)
    VALUES (42, 'drm_scheme', 'None');
""")
cursor.execute("""
    INSERT INTO book_folder_binder (book_id, folder_id)
    VALUES (42, 1);
""")
cursor.execute("INSERT INTO authors (id, name) VALUES (10, 'Independent Author');")
cursor.execute("INSERT INTO book_authors (book_id, author_id) VALUES (42, 10);")
conn.commit()

# Delete parent book
cursor.execute("DELETE FROM books WHERE id = 42;")
conn.commit()

# Check dependent records
cascaded_checks = [
    ("reading_progress", "SELECT COUNT(*) FROM reading_progress WHERE book_id = 42;"),
    ("bookmarks", "SELECT COUNT(*) FROM bookmarks WHERE book_id = 42;"),
    ("annotations", "SELECT COUNT(*) FROM annotations WHERE book_id = 42;"),
    ("book_metadata", "SELECT COUNT(*) FROM book_metadata WHERE book_id = 42;"),
    ("book_folder_binder", "SELECT COUNT(*) FROM book_folder_binder WHERE book_id = 42;"),
    ("book_authors", "SELECT COUNT(*) FROM book_authors WHERE book_id = 42;"),
]

all_cascaded = True
for tbl, query in cascaded_checks:
    cursor.execute(query)
    cnt = cursor.fetchone()[0]
    if cnt != 0:
        record_fail(f"cascade_{tbl}", f"Expected 0 rows after cascade, found {cnt}")
        all_cascaded = False
if all_cascaded:
    record_pass("cascade_delete_all", "Deleting parent book cascaded to 0 rows across all 6 dependent child tables")

# Test Trigger Non-Recursion under recursive_triggers = ON
cursor.execute("""
    INSERT INTO books (id, title, file_path, file_size, file_hash, format, updated_at)
    VALUES (99, 'Trigger Book', '/path/trig.epub', 1000, 'hash_trig_99', 'EPUB', '2020-01-01T00:00:00Z');
""")
conn.commit()

try:
    for i in range(50):
        cursor.execute("UPDATE books SET title = ? WHERE id = 99;", (f"Trigger Book Update {i}",))
    conn.commit()
    cursor.execute("SELECT updated_at FROM books WHERE id = 99;")
    new_ts = cursor.fetchone()[0]
    record_pass("trigger_recursion_hardened", f"50 rapid updates under recursive_triggers = ON passed without recursion crash (updated_at: {new_ts})")
except Exception as e:
    record_fail("trigger_recursion_hardened", f"Trigger failed under recursion: {e}")

conn.close()

print("\n" + "="*70)
print("PHASE 2: INDEPENDENT FEATURES.CSV AUDIT")
print("="*70)

features_path = os.path.join(REPLICA_DIR, "features.csv")
if not os.path.exists(features_path):
    record_fail("features_csv_exists", f"File not found: {features_path}")
else:
    with open(features_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        expected_header = ['feature', 'area', 'priority', 'original', 'clone', 'complexity', 'notes']
        if header == expected_header:
            record_pass("csv_header", f"Header matches exact schema: {header}")
        else:
            record_fail("csv_header", f"Header mismatch: expected {expected_header}, got {header}")

        rows = list(reader)
        if len(rows) >= 60:
            record_pass("csv_row_count", f"Total features: {len(rows)} (substantive coverage)")
        else:
            record_fail("csv_row_count", f"Insufficient features: {len(rows)}")

        priorities = set()
        invalid_rows = []
        for idx, row in enumerate(rows, 2):
            if len(row) != 7:
                invalid_rows.append((idx, f"columns={len(row)}"))
            p = row[2]
            priorities.add(p)
            if p not in ("Must", "Should", "Could"):
                invalid_rows.append((idx, f"invalid priority '{p}'"))

        if not invalid_rows:
            record_pass("csv_validation", f"All {len(rows)} rows valid with strict Must/Should/Could priorities ({sorted(list(priorities))})")
        else:
            record_fail("csv_validation", f"Row errors: {invalid_rows[:5]}")

        # Check required formats
        formats_found = set()
        for row in rows:
            feat_lower = row[0].lower() + " " + row[6].lower()
            for fmt in ["epub", "pdf", "mobi", "fb2", "cbz", "txt"]:
                if fmt in feat_lower:
                    formats_found.add(fmt.upper())
        if len(formats_found) == 6:
            record_pass("formats_in_features", f"All 6 required formats represented: {sorted(list(formats_found))}")
        else:
            record_fail("formats_in_features", f"Missing formats: {set(['EPUB', 'PDF', 'MOBI', 'FB2', 'CBZ', 'TXT']) - formats_found}")

print("\n" + "="*70)
print("PHASE 3: INDEPENDENT RECON.MD & ARCHITECTURE.MD AUDIT")
print("="*70)

recon_path = os.path.join(REPLICA_DIR, "recon.md")
arch_path = os.path.join(REPLICA_DIR, "architecture.md")

with open(recon_path, "r", encoding="utf-8") as f:
    recon_content = f.read()

with open(arch_path, "r", encoding="utf-8") as f:
    arch_content = f.read()

# Verify Screen inventory S01-S12
expected_screens = ["S01A", "S01B", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10", "S11", "S12"]
screens_in_recon = [s for s in expected_screens if s in recon_content]
screens_in_arch = [s for s in expected_screens if s in arch_content]

if len(screens_in_recon) == len(expected_screens):
    record_pass("recon_screens", f"All 13 screen identifiers present in recon.md: {screens_in_recon}")
else:
    record_fail("recon_screens", f"Missing screens in recon.md: {set(expected_screens) - set(screens_in_recon)}")

if len(screens_in_arch) == len(expected_screens):
    record_pass("arch_screens", f"All 13 screen identifiers referenced in architecture.md: {screens_in_arch}")
else:
    record_fail("arch_screens", f"Missing screens in architecture.md: {set(expected_screens) - set(screens_in_arch)}")

# Verify User Flows F01-F10
expected_flows = [f"F{i:02d}" for i in range(1, 11)]
flows_in_recon = [f for f in expected_flows if f in recon_content]
if len(flows_in_recon) == 10:
    record_pass("recon_flows", f"All 10 user flows present in recon.md: {flows_in_recon}")
else:
    record_fail("recon_flows", f"Missing flows in recon.md: {set(expected_flows) - set(flows_in_recon)}")

# Verify Format Pipelines
formats = ["EPUB", "PDF", "MOBI", "FB2", "CBZ", "TXT"]
recon_formats = [fmt for fmt in formats if fmt in recon_content]
arch_formats = [fmt for fmt in formats if fmt in arch_content]

if len(recon_formats) == 6 and len(arch_formats) == 6:
    record_pass("format_pipelines", "All 6 format pipelines detailed in both recon.md and architecture.md")
else:
    record_fail("format_pipelines", f"Format mismatch: recon={recon_formats}, arch={arch_formats}")

# Verify Modern C++20 / Qt 6 Concepts
cpp20_features = ["concept", "std::expected", "std::jthread", "std::stop_token", "views::filter"]
found_cpp20 = [feat for feat in cpp20_features if feat in arch_content]
if len(found_cpp20) >= 4:
    record_pass("cpp20_modern_idioms", f"Modern C++20 idioms actively specified: {found_cpp20}")
else:
    record_fail("cpp20_modern_idioms", f"Missing C++20 idioms: {set(cpp20_features) - set(found_cpp20)}")

# Verify Concurrency Model
concurrency_terms = ["QThreadPool", "GUI thread", "pre-rendering", "stop_token", "setResizingMode"]
found_concurrency = [term for term in concurrency_terms if term in arch_content]
if len(found_concurrency) == len(concurrency_terms):
    record_pass("concurrency_model", f"Robust threading and async architecture present: {found_concurrency}")
else:
    record_fail("concurrency_model", f"Missing concurrency terms: {set(concurrency_terms) - set(found_concurrency)}")

# Verify Phased Roadmap & Vertical Slice
roadmap_milestones = ["Milestone 1", "Milestone 2", "Milestone 3", "Vertical Slice"]
found_milestones = [m for m in roadmap_milestones if m in arch_content]
if len(found_milestones) == len(roadmap_milestones):
    record_pass("roadmap_vertical_slice", f"Phased roadmap with end-to-end vertical slice clearly specified: {found_milestones}")
else:
    record_fail("roadmap_vertical_slice", f"Missing roadmap milestones: {set(roadmap_milestones) - set(found_milestones)}")

print("\n" + "="*70)
print("INDEPENDENT AUDIT SUMMARY")
print("="*70)
if not failures:
    print(">>> FINAL VERDICT: VICTORY CONFIRMED <<<")
    print("All empirical tests, schema validations, format checks, and architectural criteria PASSED with ZERO ERRORS.")
    sys.exit(0)
else:
    print(">>> FINAL VERDICT: VICTORY REJECTED <<<")
    print(f"Encountered {len(failures)} failures:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
