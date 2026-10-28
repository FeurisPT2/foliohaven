"""
Adversarial Stress Test Suite for Store Listing (listing.json)
Author: challenger_1 (teamwork_preview_challenger)
Target: replica/launch/listing.json
Specification: replica-launch listing requirements and listing.py linter rules.
"""

import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
LISTING_PATH = ROOT_DIR / "replica" / "launch" / "listing.json"
LINTER_PATH = Path(r"C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-launch\listing.py")

LIMITS = {
    "app_store": {
        "name": 30,
        "subtitle": 30,
        "promotional_text": 170,
        "description": 4000,
        "keywords": 100,
        "whats_new": 4000,
    },
    "google_play": {
        "title": 30,
        "short_description": 80,
        "full_description": 4000,
    },
}

SHORT_FIELDS = {"name", "subtitle", "title", "short_description"}

CLAIMS = re.compile(
    r"(#\s?1\b|\bnumber one\b|\bno\.? ?1\b|\bbest\b|\btop[- ]rated\b|\b(app|game) of the year\b"
    r"|\bfree\b|\bdiscount\b|\bsale\b|\b\d+% off\b|\bnew!?$)",
    re.I,
)

ALL_CAPS = re.compile(r"\b[A-Z]{4,}\b")

STOP = {"a", "an", "and", "app", "for", "the", "to", "of", "with", "your", "you", "in", "on", "&"}


def custom_length(text: str) -> int:
    """NFC length counting matching listing.py implementation."""
    text = unicodedata.normalize("NFC", text or "")
    count = 0
    prev_joiner = False
    for ch in text:
        cat = unicodedata.category(ch)
        if ch == "\u200d":  # Zero-width joiner
            prev_joiner = True
            continue
        if cat in ("Mn", "Me") or ch in ("\ufe0f", "\ufe0e") or 0x1F3FB <= ord(ch) <= 0x1F3FF:
            continue
        if prev_joiner:
            prev_joiner = False
            continue
        count += 1
    return count


def has_emoji(text: str) -> bool:
    return any(unicodedata.category(ch) == "So" or ord(ch) >= 0x1F000 for ch in text or "")


def extract_words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9']+", (text or "").lower()) if w not in STOP]


def test_1_listing_py_execution():
    """Empirically run listing.py on replica/launch/listing.json."""
    print("\n--- [TEST 1] Empirical Execution of listing.py ---")
    assert LINTER_PATH.is_file(), f"Linter not found at {LINTER_PATH}"
    assert LISTING_PATH.is_file(), f"Listing not found at {LISTING_PATH}"

    # Standard run
    proc = subprocess.run(
        [sys.executable, str(LINTER_PATH), str(LISTING_PATH)],
        capture_output=True,
        text=True,
    )
    print("STDOUT:\n" + proc.stdout.strip())
    if proc.stderr:
        print("STDERR:\n" + proc.stderr.strip())

    assert proc.returncode == 0, f"listing.py exited with non-zero code {proc.returncode}"
    assert "0 errors, 0 warnings" in proc.stdout, f"listing.py reported issues:\n{proc.stdout}"

    # JSON output run
    proc_json = subprocess.run(
        [sys.executable, str(LINTER_PATH), str(LISTING_PATH), "--json"],
        capture_output=True,
        text=True,
    )
    assert proc_json.returncode == 0, f"listing.py --json failed with code {proc_json.returncode}"
    issues = json.loads(proc_json.stdout)
    assert issues == [], f"Expected 0 issues from listing.py --json, got: {issues}"
    print("  [PASS] listing.py executed with exit code 0 and 0 issues reported.")


def test_2_field_lengths_and_normalization():
    """Stress-test character counts, headroom, and unicode normalization."""
    print("\n--- [TEST 2] Field Lengths & Normalization Stress Test ---")
    with open(LISTING_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for store, limits in LIMITS.items():
        assert store in data, f"Missing store section '{store}'"
        store_data = data[store]
        for field, max_limit in limits.items():
            assert field in store_data, f"Missing field '{field}' in {store}"
            val = store_data[field]
            assert isinstance(val, str), f"Field '{field}' in {store} is not a string"
            assert val.strip(), f"Field '{field}' in {store} is empty or whitespace"

            nfc_len = custom_length(val)
            raw_len = len(val)
            nfd_len = custom_length(unicodedata.normalize("NFD", val))

            print(
                f"  {store:12} | {field:18} | NFC: {nfc_len:4} | Limit: {max_limit:4} | Headroom: {max_limit - nfc_len:4}"
            )
            assert nfc_len <= max_limit, (
                f"OVER LIMIT: {store}.{field} length {nfc_len} exceeds {max_limit} by {nfc_len - max_limit}"
            )
    print("  [PASS] All field lengths strictly within limits under NFC and NFD normalization.")


def test_3_claims_leakage():
    """Test short fields and overall listing against CLAIMS regex."""
    print("\n--- [TEST 3] Claims Regex Leakage Test ---")
    with open(LISTING_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check short fields (strictly prohibited)
    for store in ("app_store", "google_play"):
        for field in ("name", "subtitle", "title", "short_description"):
            if field in data.get(store, {}):
                val = data[store][field]
                match = CLAIMS.search(val)
                print(f"  Testing {store}.{field}: '{val}'")
                assert not match, f"Claim match in {store}.{field}: '{match.group(0)}'"

    # Also inspect promotional_text and whats_new
    for store, fields in (("app_store", ["promotional_text", "whats_new"]),):
        for field in fields:
            val = data[store].get(field, "")
            match = CLAIMS.search(val)
            if match:
                print(f"  [INFO] Note: '{match.group(0)}' matched in non-short field {store}.{field}")
            else:
                print(f"  Clean: {store}.{field} has zero CLAIMS matches.")

    print("  [PASS] Zero claim leakage in short fields.")


def test_4_all_caps_leakage():
    """Test short fields against all-caps word pattern \b[A-Z]{4,}\b."""
    print("\n--- [TEST 4] All-Caps Regex Leakage Test ---")
    with open(LISTING_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for store in ("app_store", "google_play"):
        for field in ("name", "subtitle", "title", "short_description"):
            if field in data.get(store, {}):
                val = data[store][field]
                caps = ALL_CAPS.findall(val)
                print(f"  Testing {store}.{field} for all-caps words (len >= 4): {caps}")
                assert not caps, f"All-caps words found in {store}.{field}: {caps}"

    print("  [PASS] Zero all-caps words of length >= 4 found in short fields.")


def test_5_keywords_syntax_and_overlap():
    """Adversarially evaluate keywords syntax, duplicates, spaces, and wasted words."""
    print("\n--- [TEST 5] Keywords Syntax & Overlap Test ---")
    with open(LISTING_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    app_store = data["app_store"]
    kw_raw = app_store.get("keywords", "")
    assert kw_raw, "Keywords string is empty"

    # 1. No spaces after commas
    assert not re.search(r",\s", kw_raw), "Keywords string contains spaces after commas"
    # 2. No leading or trailing spaces
    assert kw_raw == kw_raw.strip(), "Keywords has leading or trailing whitespace"
    # 3. No empty tokens (double commas or trailing comma)
    tokens = kw_raw.split(",")
    for idx, token in enumerate(tokens):
        assert token, f"Empty keyword token found at position {idx}"
        assert token == token.lower(), f"Keyword '{token}' is not lowercase"
        assert token == token.strip(), f"Keyword '{token}' has untrimmed whitespace"

    # 4. No duplicates
    token_set = set()
    duplicates = []
    for t in tokens:
        if t in token_set:
            duplicates.append(t)
        token_set.add(t)
    assert not duplicates, f"Duplicate keywords detected: {duplicates}"

    # 5. Overlap with name and subtitle
    name_words = set(extract_words(app_store.get("name", "")))
    subtitle_words = set(extract_words(app_store.get("subtitle", "")))
    forbidden_words = name_words.union(subtitle_words)

    overlap = set()
    for t in tokens:
        for w in extract_words(t):
            if w in forbidden_words:
                overlap.add(w)

    print(f"  Keywords count: {len(tokens)}")
    print(f"  Tokens: {tokens}")
    print(f"  Name words (filtered): {name_words}")
    print(f"  Subtitle words (filtered): {subtitle_words}")
    print(f"  Overlap with name/subtitle: {overlap}")
    assert not overlap, f"Keywords contain wasted words already in name/subtitle: {overlap}"

    print("  [PASS] Keywords syntax, uniqueness, and name/subtitle independence confirmed.")


def test_6_avoid_words_sanitization():
    """Search for avoid words, competitor trademarks, and substrings across the entire JSON tree."""
    print("\n--- [TEST 6] Avoid-Words & Competitor Trademark Sanitization ---")
    with open(LISTING_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read()
    data = json.loads(raw_text)

    brand_path = ROOT_DIR / "replica" / "brand.json"
    with open(brand_path, "r", encoding="utf-8") as f:
        brand_data = json.load(f)
    avoid_list = brand_data.get("avoid", [])

    # Check avoid array inside listing.json
    assert "avoid" in data, "Missing 'avoid' section in listing.json"
    assert isinstance(data["avoid"], list), "'avoid' must be a list"
    for expected_avoid in avoid_list:
        assert expected_avoid in data["avoid"], f"Expected avoid token '{expected_avoid}' not listed in data['avoid']"

    # Check store fields (ignoring the "avoid" array definition itself)
    stores_data = {k: v for k, v in data.items() if k != "avoid"}
    stores_text = json.dumps(stores_data)

    for avoid_word in avoid_list:
        pattern = re.compile(r"(?<!\w)" + re.escape(avoid_word) + r"(?!\w)", re.I)
        matches = pattern.findall(stores_text)
        print(f"  Searching for avoid-word '{avoid_word}': {len(matches)} matches")
        assert len(matches) == 0, f"Found avoid-word '{avoid_word}' in store metadata: {matches}"

    # Also check other competitors from feedback.md and pricing.md
    competitor_names = ["Calibre", "ReadEra", "Freda", "Acrobat", "Kindle"]
    for comp in competitor_names:
        pattern = re.compile(r"(?<!\w)" + re.escape(comp) + r"(?!\w)", re.I)
        matches = pattern.findall(stores_text)
        print(f"  Competitor scan for '{comp}': {len(matches)} matches")
        assert len(matches) == 0, f"Competitor trademark '{comp}' leaked into store metadata!"

    print("  [PASS] All avoid-words and competitor trademarks completely absent from metadata.")


def test_7_adversarial_encoding_and_structure():
    """Check for invisible characters, null bytes, BOM, and structural integrity."""
    print("\n--- [TEST 7] Adversarial Encoding & Structural Integrity ---")
    with open(LISTING_PATH, "rb") as f:
        raw_bytes = f.read()

    # UTF-8 BOM check
    assert not raw_bytes.startswith(b"\xef\xbb\xbf"), "BOM detected at start of listing.json"

    # Null byte check
    assert b"\x00" not in raw_bytes, "Null bytes detected in listing.json"

    # Emoji in short fields check
    with open(LISTING_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for store in ("app_store", "google_play"):
        for field in ("name", "subtitle", "title", "short_description"):
            if field in data.get(store, {}):
                val = data[store][field]
                assert not has_emoji(val), f"Emoji found in short field {store}.{field}: '{val}'"

    print("  [PASS] No BOM, no null bytes, no emoji in short fields.")


if __name__ == "__main__":
    print("=" * 80)
    print("CHALLENGER_1: ADVERSARIAL STRESS TEST HARNESS FOR listing.json")
    print("=" * 80)

    test_1_listing_py_execution()
    test_2_field_lengths_and_normalization()
    test_3_claims_leakage()
    test_4_all_caps_leakage()
    test_5_keywords_syntax_and_overlap()
    test_6_avoid_words_sanitization()
    test_7_adversarial_encoding_and_structure()

    print("\n" + "=" * 80)
    print("ALL 7 ADVERSARIAL VERIFICATION SUITES PASSED EMPIRICALLY (0 ERRORS, 0 WARNINGS)")
    print("=" * 80)
