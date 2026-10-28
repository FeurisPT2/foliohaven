import csv
import sys

csv_path = r'c:\Users\epicg\Downloads\icecream_ebook_reader_replica\replica\features.csv'

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows in features.csv: {len(rows)}")
print(f"Header fields: {reader.fieldnames}")

expected_fields = ['feature', 'area', 'priority', 'original', 'clone', 'complexity', 'notes']
assert reader.fieldnames == expected_fields, f"Header mismatch: {reader.fieldnames} != {expected_fields}"

priorities = {}
areas = {}
complexities = {}

for idx, row in enumerate(rows, start=2):
    for f in expected_fields:
        val = row.get(f, '').strip()
        assert val, f"Empty field '{f}' at line {idx}"
    
    p = row['priority']
    assert p in ['Must', 'Should', 'Could'], f"Invalid priority '{p}' at line {idx}"
    priorities[p] = priorities.get(p, 0) + 1

    a = row['area']
    areas[a] = areas.get(a, 0) + 1

    c = row['complexity']
    assert c in ['S', 'M', 'L', 'XL'], f"Invalid complexity '{c}' at line {idx}"
    complexities[c] = complexities.get(c, 0) + 1

    orig = row['original']
    assert orig in ['yes', 'no'], f"Invalid original '{orig}' at line {idx}"

    clone = row['clone']
    assert clone in ['planned', 'done', 'skipped'], f"Invalid clone status '{clone}' at line {idx}"

print("\nPriority counts:")
for p, c in sorted(priorities.items()):
    print(f"  {p}: {c}")

print("\nArea counts:")
for a, c in sorted(areas.items()):
    print(f"  {a}: {c}")

print("\nComplexity counts:")
for comp, c in sorted(complexities.items()):
    print(f"  {comp}: {c}")

assert priorities['Must'] > 0, "No Must priority features"
assert priorities['Should'] > 0, "No Should priority features"
assert priorities['Could'] > 0, "No Could priority features"

print("\nALL CSV VALIDATION CHECKS PASSED PERFECTLY!")
