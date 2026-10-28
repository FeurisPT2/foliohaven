"""
FolioHaven Adversarial Brand Cleanliness & Landing Page Integrity Test Suite
Author: challenger_2 (teamwork_preview_challenger)
Purpose: Stress-test brand cleanliness, HTML5 markup, interactive live reader,
         asset integrity, and launch verification suite.
"""

import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "app"
LANDING_HTML = APP_DIR / "landing.html"
BRAND_JSON = ROOT_DIR / "replica" / "brand.json"
SWEEP_SCRIPT = Path(r"C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py")
TEST_LAUNCH_ARTIFACTS = ROOT_DIR / "tests" / "test_launch_artifacts.py"

# Dynamically loaded from brand.json to prevent sweep.py self-hits
def get_brand_rules():
    with open(BRAND_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

def hex_to_rgb(hex_code):
    h = hex_code.lower().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

VOID_TAGS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
}

class StrictHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.errors = []
        self.total_tags = 0
        self.ids = set()
        self.anchors = []
        self.in_script = False
        self.in_style = False
        self.scripts = []
        self.current_script = []

    def handle_starttag(self, tag, attrs):
        self.total_tags += 1
        attr_dict = dict(attrs)
        if "id" in attr_dict:
            self.ids.add(attr_dict["id"])
        if tag.lower() == "a" and "href" in attr_dict:
            self.anchors.append((attr_dict["href"], self.getpos()))

        if tag.lower() == "script":
            self.in_script = True
            self.current_script = []
        elif tag.lower() == "style":
            self.in_style = True

        if tag.lower() not in VOID_TAGS:
            self.tag_stack.append((tag.lower(), self.getpos()))

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower == "script":
            self.in_script = False
            self.scripts.append("".join(self.current_script))
        elif tag_lower == "style":
            self.in_style = False

        if tag_lower in VOID_TAGS:
            self.errors.append(f"Void tag </{tag}> should not have end tag at line {self.getpos()[0]}")
            return

        if not self.tag_stack:
            self.errors.append(f"Unexpected closing tag </{tag}> at line {self.getpos()[0]} with empty stack")
            return

        last_tag, pos = self.tag_stack.pop()
        if last_tag != tag_lower:
            self.errors.append(
                f"Mismatched closing tag </{tag}> at line {self.getpos()[0]}, expected </{last_tag}> opened at line {pos[0]}"
            )

    def handle_data(self, data):
        if self.in_script:
            self.current_script.append(data)


def norm_hex(h):
    h = h.lower().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return "#" + h


def test_1_brand_sweep_tool():
    """Verify official sweep.py tool returns exit code 0 and 0 hits."""
    print(">>> [TEST 1] Official sweep.py Execution")
    assert SWEEP_SCRIPT.is_file(), f"sweep.py not found at {SWEEP_SCRIPT}"
    assert BRAND_JSON.is_file(), f"brand.json not found at {BRAND_JSON}"

    cmd = [sys.executable, str(SWEEP_SCRIPT), ".", "--config", str(BRAND_JSON), "--json"]
    res = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)

    assert res.returncode == 0, f"sweep.py exited with code {res.returncode}. Output:\n{res.stdout}\n{res.stderr}"
    hits = json.loads(res.stdout)
    assert len(hits) == 0, f"sweep.py reported residual competitor hits:\n{json.dumps(hits, indent=2)}"
    print(f"  [PASS] sweep.py returned exit code 0 with 0 hits.")


def test_2_adversarial_brand_scan():
    """Adversarial scan of app/landing.html for avoided names, domains, and prohibited colors."""
    print(">>> [TEST 2] Adversarial Brand & Color Scan on app/landing.html")
    assert LANDING_HTML.is_file(), f"landing.html not found at {LANDING_HTML}"
    content = LANDING_HTML.read_text(encoding="utf-8")

    # 1. Competitor Names & Variations dynamically loaded
    brand_cfg = get_brand_rules()
    avoid_list = brand_cfg.get("avoid", [])
    domains_list = brand_cfg.get("domains", [])
    colors_list = brand_cfg.get("colors", [])

    for name in avoid_list:
        parts = [re.escape(p) for p in re.split(r"[\s_-]+", name) if p]
        pat = r"[\s_-]?".join(parts)
        matches = list(re.finditer(pat, content, re.IGNORECASE))
        assert not matches, (
            f"Adversarial match for avoided name '{name}' found in landing.html: "
            f"{[m.group(0) for m in matches]}"
        )

    # Stem variation check (e.g. ice + cream)
    stem_pat = r"(?i)i[c\s]*e[\s_\-]*c[r\s]*e[a\s]*m"
    stem_matches = list(re.finditer(stem_pat, content))
    assert not stem_matches, f"Adversarial stem matches found in landing.html: {[m.group(0) for m in stem_matches]}"

    # 2. Competitor Domains
    for d in domains_list:
        domain_matches = list(re.finditer(re.escape(d), content, re.IGNORECASE))
        assert not domain_matches, f"Competitor domain '{d}' found in landing.html: {domain_matches}"

    # 3. Prohibited Hex Colors (3-digit and 6-digit)
    prohibited_normalized = {norm_hex(c) for c in colors_list}
    found_hexes = re.findall(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", content)
    for h in found_hexes:
        nh = norm_hex(h)
        assert nh not in prohibited_normalized, f"Prohibited competitor color '{h}' (norm: '{nh}') found in landing.html"

    # 4. Prohibited RGB / RGBA equivalents
    prohibited_rgbs = {hex_to_rgb(c) for c in colors_list}
    rgb_matches = re.findall(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})", content, re.IGNORECASE)
    for r_s, g_s, b_s in rgb_matches:
        rgb_tuple = (int(r_s), int(g_s), int(b_s))
        assert rgb_tuple not in prohibited_rgbs, (
            f"Prohibited competitor RGB color rgb{rgb_tuple} found in landing.html"
        )

    print("  [PASS] Zero avoided names, domains, hex colors, or RGB matches in landing.html.")


def test_3_html5_markup_and_semantics():
    """Verify valid HTML5 structure, tag balance, and semantic landmarks."""
    print(">>> [TEST 3] HTML5 Markup Structure & Entity Integrity")
    content = LANDING_HTML.read_text(encoding="utf-8")

    # Document preamble & meta tags
    assert content.strip().startswith("<!DOCTYPE html>"), "Missing <!DOCTYPE html> doctype"
    assert '<html lang="en">' in content, 'Missing <html lang="en">'
    assert '<meta charset="UTF-8">' in content, "Missing UTF-8 charset declaration"
    assert '<meta name="viewport"' in content, "Missing viewport meta tag"
    assert "<title>" in content and "</title>" in content, "Missing <title> tag"

    # Semantic landmarks
    for landmark in ["<header", "<nav", "<main", "<section", "<footer"]:
        assert landmark in content, f"Semantic landmark {landmark} missing from landing.html"

    # Parse and test tag stack balance
    parser = StrictHTMLParser()
    parser.feed(content)

    assert len(parser.errors) == 0, f"HTMLParser reported errors:\n" + "\n".join(parser.errors)
    assert len(parser.tag_stack) == 0, (
        f"Unclosed HTML tags detected ({len(parser.tag_stack)}):\n" +
        "\n".join([f"<{tag}> at line {pos[0]}" for tag, pos in parser.tag_stack])
    )

    # Check internal hash links
    hash_anchors = [href[1:] for href, pos in parser.anchors if href.startswith("#") and len(href) > 1]
    for h in set(hash_anchors):
        assert h in parser.ids, f"Broken internal jump link href='#{h}'. Target id='{h}' does not exist!"

    print(f"  [PASS] HTML5 structure valid ({parser.total_tags} tags, 0 unclosed, all {len(hash_anchors)} anchor links valid).")


def test_4_asset_integrity():
    """Verify all referenced local assets exist on disk, are non-empty, and load cleanly."""
    print(">>> [TEST 4] Local Asset Resolution & Integrity")
    content = LANDING_HTML.read_text(encoding="utf-8")

    # Check favicon.svg
    assert 'href="favicon.svg"' in content, "favicon.svg not linked in landing.html"
    favicon_path = APP_DIR / "favicon.svg"
    assert favicon_path.is_file(), f"favicon.svg missing at {favicon_path}"
    assert favicon_path.stat().st_size > 0, "favicon.svg is empty"
    ET.parse(str(favicon_path)) # Validate XML

    # Check logo.svg
    logo_path = APP_DIR / "logo.svg"
    assert logo_path.is_file(), f"logo.svg missing at {logo_path}"
    assert logo_path.stat().st_size > 0, "logo.svg is empty"
    ET.parse(str(logo_path)) # Validate XML

    # Check styles.css
    assert 'href="styles.css"' in content, "styles.css not linked in landing.html"
    styles_path = APP_DIR / "styles.css"
    assert styles_path.is_file(), f"styles.css missing at {styles_path}"
    assert styles_path.stat().st_size > 0, "styles.css is empty"

    # Check tokens.css in replica/design/tokens.css
    tokens_path = ROOT_DIR / "replica" / "design" / "tokens.css"
    assert tokens_path.is_file(), f"tokens.css missing at {tokens_path}"
    assert tokens_path.stat().st_size > 0, "tokens.css is empty"

    # Verify styles.css imports tokens.css
    styles_content = styles_path.read_text(encoding="utf-8")
    assert '@import url("../replica/design/tokens.css");' in styles_content

    # Verify landing.html defines design tokens in :root
    assert "--color-accent: #c2410c;" in content
    assert "--color-sidebar-bg: #231f1d;" in content
    assert "--color-text: #14181f;" in content

    print("  [PASS] All local assets (logo.svg, favicon.svg, styles.css, tokens.css) exist and are valid.")


def test_5_interactive_live_reader():
    """Verify live reader container, theme switching, font scaling, and JavaScript logic."""
    print(">>> [TEST 5] Interactive Live Reader Functionality")
    content = LANDING_HTML.read_text(encoding="utf-8")

    # Container & Canvas existence
    assert 'data-ui="live-reader"' in content, "data-ui='live-reader' container missing"
    assert 'id="live-canvas"' in content, "id='live-canvas' reader element missing"
    assert 'class="reader-canvas theme-day"' in content, "live-canvas default theme-day class missing"

    # Theme controls verification
    themes = ["day", "sepia", "night", "dark-sepia"]
    for t in themes:
        assert f'data-theme="{t}"' in content, f"Theme button data-theme='{t}' missing"
        assert f".reader-canvas.theme-{t}" in content, f"CSS rule for .reader-canvas.theme-{t} missing"

    # Font stepper controls
    assert 'id="font-dec"' in content, "Font decrease button id='font-dec' missing"
    assert 'id="font-inc"' in content, "Font increase button id='font-inc' missing"

    # Extract script content and verify JS syntax with Node.js
    script_match = re.search(r"<script>(.*?)</script>", content, re.DOTALL)
    assert script_match, "Embedded <script> missing from landing.html"
    js_code = script_match.group(1).strip()

    # Verify core JS logic components
    assert "document.getElementById('live-canvas')" in js_code
    assert "querySelectorAll('.theme-picker .theme-btn')" in js_code
    assert "btnInc.addEventListener" in js_code
    assert "btnDec.addEventListener" in js_code
    assert "currentFontSize < 24" in js_code
    assert "currentFontSize > 12" in js_code

    # Syntax test using node --check
    node_res = subprocess.run(
        ["node", "--check", "--input-type=module"],
        input=js_code,
        text=True,
        capture_output=True
    )
    assert node_res.returncode == 0, f"Node.js syntax check failed on embedded JS:\n{node_res.stderr}"

    print("  [PASS] Interactive live reader verified (theme switching, font scaling, clean JS syntax).")


def test_6_launch_artifacts_suite():
    """Execute official test_launch_artifacts.py test suite."""
    print(">>> [TEST 6] Official test_launch_artifacts.py Pass Verification")
    assert TEST_LAUNCH_ARTIFACTS.is_file(), f"test_launch_artifacts.py not found at {TEST_LAUNCH_ARTIFACTS}"
    res = subprocess.run([sys.executable, str(TEST_LAUNCH_ARTIFACTS)], cwd=str(ROOT_DIR), capture_output=True, text=True)
    assert res.returncode == 0, f"test_launch_artifacts.py failed:\n{res.stdout}\n{res.stderr}"
    assert "All launch validation tests passed successfully!" in res.stdout
    print("  [PASS] test_launch_artifacts.py passed 100%.")


if __name__ == "__main__":
    print("=====================================================================")
    print("FolioHaven Adversarial Verification & Integrity Suite (Challenger 2)")
    print("=====================================================================")
    test_1_brand_sweep_tool()
    test_2_adversarial_brand_scan()
    test_3_html5_markup_and_semantics()
    test_4_asset_integrity()
    test_5_interactive_live_reader()
    test_6_launch_artifacts_suite()
    print("=====================================================================")
    print("ALL EMPIRICAL ADVERSARIAL STRESS TESTS PASSED (100% VERIFIED)!")
    print("=====================================================================")
