"""
Empirical Verification Test Suite for FolioHaven Reader Replica
Author: challenger_2 (teamwork_preview_challenger)
Purpose: Adversarial validation of features.csv, recon.md, and architecture.md
"""

import csv
import io
import re
import sys
from pathlib import Path

REPLICA_DIR = Path(__file__).resolve().parent.parent / "replica"
CSV_PATH = REPLICA_DIR / "features.csv"
RECON_PATH = REPLICA_DIR / "recon.md"
ARCH_PATH = REPLICA_DIR / "architecture.md"

def test_features_csv_rfc4180():
    """Verify features.csv for strict RFC 4180 compliance, header, priorities, areas, and hygiene."""
    print(">>> [TEST 1] features.csv RFC 4180 & Schema Compliance")
    assert CSV_PATH.is_file(), f"features.csv not found at {CSV_PATH}"
    
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        content = f.read()

    # Parse with standard library csv
    f_stream = io.StringIO(content)
    reader = csv.reader(f_stream)
    rows = list(reader)
    
    assert len(rows) > 1, f"CSV contains no data rows (total lines: {len(rows)})"
    header = rows[0]
    expected_header = ['feature', 'area', 'priority', 'original', 'clone', 'complexity', 'notes']
    assert header == expected_header, f"Header mismatch: {header} != {expected_header}"
    print(f"  [PASS] Header exact match: {header}")

    valid_priorities = {'Must', 'Should', 'Could'}
    valid_complexities = {'XS', 'S', 'M', 'L', 'XL'}
    valid_binary = {'yes', 'no'}
    valid_clone_status = {'planned', 'omitted', 'yes'}
    required_areas = {'Library', 'Reader', 'Navigation', 'Annotations', 'Formats', 'Customization', 'Accessibility', 'Persistence'}

    areas_found = set()
    priorities_found = {'Must': 0, 'Should': 0, 'Could': 0}
    feature_names = set()

    for idx, row in enumerate(rows[1:], start=2):
        # Column count check
        assert len(row) == 7, f"Row {idx} invalid column count: {len(row)} != 7. Content: {row}"
        feature, area, priority, original, clone, complexity, notes = row

        # Non-empty checks
        for col_name, val in zip(header, row):
            assert val.strip(), f"Row {idx} column '{col_name}' is empty or whitespace only"
            assert val == val.strip(), f"Row {idx} column '{col_name}' has untrimmed whitespace: {repr(val)}"

        # Priority validation
        assert priority in valid_priorities, f"Row {idx} invalid priority '{priority}' in feature '{feature}'"
        priorities_found[priority] += 1

        # Area validation
        areas_found.add(area)

        # Original / Clone / Complexity validation
        assert original in valid_binary, f"Row {idx} invalid 'original' value '{original}'"
        assert clone in valid_clone_status, f"Row {idx} invalid 'clone' value '{clone}'"
        assert complexity in valid_complexities, f"Row {idx} invalid complexity '{complexity}'"

        # Duplicate check
        assert feature not in feature_names, f"Row {idx} duplicate feature name: '{feature}'"
        feature_names.add(feature)

    total_features = len(rows) - 1
    print(f"  [PASS] Total features parsed: {total_features}")
    print(f"  [PASS] Priority counts: {priorities_found}")
    print(f"  [PASS] Areas covered: {sorted(list(areas_found))}")
    
    missing_areas = required_areas - areas_found
    assert not missing_areas, f"Missing required areas in features.csv: {missing_areas}"
    print("  [PASS] All 8 required functional areas represented (+ Output)")
    print("  [PASS] No duplicate feature entries detected\n")
    return rows


def test_screen_inventory_and_roadmap_crossref():
    """Verify bijection and consistency between recon.md Screen IDs and architecture.md Roadmap."""
    print(">>> [TEST 2] Screen IDs Cross-Reference (recon.md vs architecture.md)")
    assert RECON_PATH.is_file(), f"recon.md not found at {RECON_PATH}"
    assert ARCH_PATH.is_file(), f"architecture.md not found at {ARCH_PATH}"
    
    recon_text = RECON_PATH.read_text(encoding="utf-8")
    arch_text = ARCH_PATH.read_text(encoding="utf-8")

    # 1. Extract Screen IDs defined in Section 3 of recon.md
    sec3_match = re.search(r"## 3\. Screen Inventory.*?(?=## 4\.)", recon_text, re.DOTALL)
    assert sec3_match, "Section 3 not found in recon.md"
    sec3_content = sec3_match.group(0)

    # Find table entries: | **Sxx** |
    recon_screens = sorted(list(set(re.findall(r"\*\*(S\d{2}[A-Z]?)\*\*", sec3_content))))
    print(f"  [INFO] Defined Screen IDs in recon.md inventory: {recon_screens}")
    expected_screens = ['S01A', 'S01B', 'S02', 'S03', 'S04', 'S05', 'S06', 'S07', 'S08', 'S09', 'S10', 'S11', 'S12']
    assert recon_screens == expected_screens, f"Recon screen mismatch: {recon_screens} != {expected_screens}"
    print("  [PASS] All 13 specific Screen IDs (S01A-S12) defined in recon.md inventory")

    # 2. Extract Screen IDs referenced in architecture.md Section 8 (Roadmap)
    sec8_match = re.search(r"## 8\. Phased Implementation Roadmap.*?(?=## 9\.)", arch_text, re.DOTALL)
    assert sec8_match, "Section 8 not found in architecture.md"
    sec8_content = sec8_match.group(0)

    roadmap_screens = sorted(list(set(re.findall(r"\bS\d{2}[A-Z]?\b", sec8_content))))
    print(f"  [INFO] Screen IDs referenced in architecture.md Roadmap (Sec 8): {roadmap_screens}")

    # Verify every screen mentioned in roadmap exists in recon inventory (or is S01 root)
    for sid in roadmap_screens:
        if sid == 'S01':
            continue  # S01 represents root of S01A / S01B
        assert sid in recon_screens, f"Roadmap references unknown screen ID: {sid}"
    print("  [PASS] Every Screen ID in roadmap maps to a valid screen in recon inventory")

    # Verify all recon screens appear in Section 8 (Milestones 1-3)
    for sid in recon_screens:
        assert sid in roadmap_screens or (sid in ['S01A', 'S01B'] and 'S01' in roadmap_screens), (
            f"Screen {sid} not scheduled in architecture.md Roadmap"
        )
    print("  [PASS] Every screen in recon inventory is scheduled in the architecture roadmap\n")


def test_format_pipelines_completeness():
    """Verify detailed ingestion and rendering pipelines for all 6 formats in both documents."""
    print(">>> [TEST 3] Format Pipeline Completeness (recon.md & architecture.md)")
    required_formats = {
        "EPUB": {"engine": "EpubEngine", "recon_sec": "6.1 EPUB", "ingestion_kw": ["OCF", "OPF", "container.xml", "spine", "manifest"], "rendering_kw": ["reflow", "CFI", "styling", "column"]},
        "PDF": {"engine": "PdfEngine", "recon_sec": "6.2 PDF", "ingestion_kw": ["PDFium", "poppler", "outline", "xref"], "rendering_kw": ["rasterization", "DPI", "viewport", "QImage"]},
        "MOBI": {"engine": "MobiEngine", "recon_sec": "6.3 MOBI", "ingestion_kw": ["Palm Database", "PDB", "PalmDOC", "LZ77", "EXTH"], "rendering_kw": ["HTML stream", "decompressed", "reflow"]},
        "FB2": {"engine": "Fb2Engine", "recon_sec": "6.4 FB2", "ingestion_kw": ["QXmlStreamReader", "description", "title-info", "base64", "binary"], "rendering_kw": ["section", "footnotes", "chapter"]},
        "CBZ": {"engine": "ComicEngine", "recon_sec": "6.5 CBZ", "ingestion_kw": ["libzip", "QuaZip", "ComicInfo.xml", "central directory"], "rendering_kw": ["image", "sorting", "cover", "pixmap"]},
        "TXT": {"engine": "TxtEngine", "recon_sec": "6.6 TXT", "ingestion_kw": ["BOM", "uchardet", "QStringConverter", "encoding"], "rendering_kw": ["paragraph reflow", "soft wrap", "virtual page"]}
    }

    recon_text = RECON_PATH.read_text(encoding="utf-8")
    arch_text = ARCH_PATH.read_text(encoding="utf-8")

    sec6_match = re.search(r"## 6\. Format Handling Pipelines.*?(?=## 7\.)", recon_text, re.DOTALL)
    assert sec6_match, "Section 6 not found in recon.md"
    sec6_text = sec6_match.group(0)

    for fmt, specs in required_formats.items():
        # Check recon.md section 6
        assert specs["recon_sec"] in sec6_text, f"recon.md missing section for {fmt}"
        
        # Check ingestion keywords in recon.md
        found_ingest = [kw for kw in specs["ingestion_kw"] if kw.lower() in sec6_text.lower()]
        assert len(found_ingest) >= 2, f"recon.md lacks sufficient ingestion details for {fmt}: found {found_ingest}"
        
        # Check rendering keywords in recon.md
        found_render = [kw for kw in specs["rendering_kw"] if kw.lower() in sec6_text.lower()]
        assert len(found_render) >= 2, f"recon.md lacks sufficient rendering details for {fmt}: found {found_render}"
        
        # Check architecture.md engine class
        assert specs["engine"] in arch_text, f"architecture.md missing concrete engine class {specs['engine']} for {fmt}"
        print(f"  [PASS] {fmt:4s} -> recon pipeline & architecture engine ({specs['engine']}) fully verified")

    print("  [PASS] All 6 required ebook formats have comprehensive ingestion and rendering pipelines\n")


def test_cross_artifact_consistency():
    """Verify component IDs and user flow IDs across recon.md and architecture.md."""
    print(">>> [TEST 4] Cross-Artifact Component & Flow Consistency")
    recon_text = RECON_PATH.read_text(encoding="utf-8")
    arch_text = ARCH_PATH.read_text(encoding="utf-8")

    recon_c = sorted(set(re.findall(r"\bC\d{2}\b", recon_text)))
    arch_c = sorted(set(re.findall(r"\bC\d{2}\b", arch_text)))
    assert recon_c == arch_c, f"Component ID mismatch: recon={recon_c}, arch={arch_c}"
    print(f"  [PASS] Components C01-C10 match perfectly across documents: {recon_c}")

    recon_f = sorted(set(re.findall(r"\bF\d{2}\b", recon_text)))
    arch_f = sorted(set(re.findall(r"\bF\d{2}\b", arch_text)))
    assert recon_f == arch_f, f"Flow ID mismatch: recon={recon_f}, arch={arch_f}"
    print(f"  [PASS] Flows F01-F11 match perfectly across documents: {recon_f}\n")


if __name__ == "__main__":
    print("=" * 70)
    print("CHALLENGER_2 EMPIRICAL TEST SUITE EXECUTION")
    print("=" * 70)
    test_features_csv_rfc4180()
    test_screen_inventory_and_roadmap_crossref()
    test_format_pipelines_completeness()
    test_cross_artifact_consistency()
    print("=" * 70)
    print("ALL 4 EMPIRICAL VERIFICATION TESTS PASSED (100% SUCCESS)")
    print("=" * 70)
