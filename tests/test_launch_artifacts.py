"""
Automated Validation Suite for FolioHaven Launch Package
Validates pricing.md, listing.json, landing.md, launch-plan.md, and app/landing.html.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
LAUNCH_DIR = ROOT_DIR / "replica" / "launch"
APP_DIR = ROOT_DIR / "app"

def test_pricing_md():
    pricing_path = LAUNCH_DIR / "pricing.md"
    assert pricing_path.is_file(), f"pricing.md not found at {pricing_path}"
    content = pricing_path.read_text(encoding="utf-8")

    # Competitor Pricing Matrix verification
    assert "Competitor Pricing Matrix" in content
    assert "Oct 28, 2026" in content
    assert "$19.95" in content and "$39.95" in content
    assert "Calibre" in content
    assert "ReadEra" in content
    assert "Freda" in content

    # 12 complaint data points
    assert "12 Complaint Data Points" in content or "12 complaint data points" in content
    assert "FIX-1" in content and "FIX-2" in content

    # 3-Tier Ethical Model
    assert "Reader" in content
    assert "Supporter Edition" in content
    assert "Sustaining Patron" in content
    assert "$12" in content
    assert "$24" in content

    # Stripe Product & Price Objects
    assert "prod_foliohaven_supporter" in content
    assert "price_foliohaven_supporter_onetime" in content
    assert "prod_foliohaven_sustaining" in content
    assert "price_foliohaven_sustaining_annual" in content
    assert "/api/portal" in content
    print("  [PASS] test_pricing_md")

def test_listing_json():
    listing_path = LAUNCH_DIR / "listing.json"
    assert listing_path.is_file(), f"listing.json not found at {listing_path}"
    with open(listing_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "avoid" in data
    assert "app_store" in data
    assert "google_play" in data

    # Check App Store limits
    app_store = data["app_store"]
    assert len(app_store["name"]) <= 30
    assert len(app_store["subtitle"]) <= 30
    assert len(app_store["promotional_text"]) <= 170
    assert len(app_store["description"]) <= 4000
    assert len(app_store["keywords"]) <= 100
    assert len(app_store["whats_new"]) <= 4000

    # Check Google Play limits
    google_play = data["google_play"]
    assert len(google_play["title"]) <= 30
    assert len(google_play["short_description"]) <= 80
    assert len(google_play["full_description"]) <= 4000

    # Verify with listing.py
    linter_path = Path(r"C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-launch\listing.py")
    res = subprocess.run([sys.executable, str(linter_path), str(listing_path)], capture_output=True, text=True)
    assert res.returncode == 0, f"listing.py failed:\n{res.stdout}\n{res.stderr}"
    assert "0 errors, 0 warnings" in res.stdout, f"listing.py reported issues:\n{res.stdout}"
    print("  [PASS] test_listing_json (0 errors, 0 warnings)")

def test_landing_md():
    landing_path = LAUNCH_DIR / "landing.md"
    assert landing_path.is_file(), f"landing.md not found at {landing_path}"
    content = landing_path.read_text(encoding="utf-8")

    # 7 mandatory sections
    assert "1. Hero Section" in content
    assert "2. The Problem" in content
    assert "3. How It Works" in content
    assert "4. Features" in content
    assert "5. Transparent & Ethical Pricing" in content
    assert "6. Frequently Asked Questions" in content
    assert "7. Final Call to Action" in content

    # FIX mapping
    for i in range(1, 7):
        assert f"FIX-{i}" in content

    print("  [PASS] test_landing_md (all 7 sections & FIX-1..6 present)")

def test_launch_plan_md():
    plan_path = LAUNCH_DIR / "launch-plan.md"
    assert plan_path.is_file(), f"launch-plan.md not found at {plan_path}"
    content = plan_path.read_text(encoding="utf-8")

    # Distribution schedule
    assert "Day 0" in content
    assert "Day 30" in content

    # Reddit mapping
    for sub in ["r/software", "r/ereader", "r/books", "r/libgen"]:
        assert sub in content

    # Show HN & Product Hunt & GitHub
    assert "Show HN" in content
    assert "Product Hunt" in content
    assert "SHA256SUMS.txt" in content

    # 4 outreach scripts
    assert "Variant 1" in content
    assert "Variant 2" in content
    assert "Variant 3" in content
    assert "Variant 4" in content
    print("  [PASS] test_launch_plan_md")

def test_app_landing_html():
    html_path = APP_DIR / "landing.html"
    assert html_path.is_file(), f"landing.html not found at {html_path}"
    content = html_path.read_text(encoding="utf-8")

    # Live Reader UI
    assert 'data-ui="live-reader"' in content
    assert 'class="reader-canvas' in content

    # Clean brand sweep checks on landing.html
    brand_path = ROOT_DIR / "replica" / "brand.json"
    with open(brand_path, "r", encoding="utf-8") as f:
        brand = json.load(f)

    for avoid_name in brand.get("avoid", []):
        assert avoid_name.lower() not in content.lower(), f"Competitor name '{avoid_name}' found in landing.html"

    for domain in brand.get("domains", []):
        assert domain.lower() not in content.lower(), f"Competitor domain '{domain}' found in landing.html"

    for color in brand.get("colors", []):
        assert color.lower() not in content.lower(), f"Competitor hex color '{color}' found in landing.html"

    print("  [PASS] test_app_landing_html (brand clean, interactive reader present)")

if __name__ == "__main__":
    print("Running FolioHaven Launch Verification Suite...")
    test_pricing_md()
    test_listing_json()
    test_landing_md()
    test_launch_plan_md()
    test_app_landing_html()
    print("All launch validation tests passed successfully!")
