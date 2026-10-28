"""
Adversarial Stress Test Suite for sweep.py Directory Traversal & Detection
Author: challenger_remediation_1 (teamwork_preview_challenger)
Target: C:\\Users\\epicg\\.gemini\\config\\plugins\\replica-skill\\skills\\replica-brand\\sweep.py
Purpose: Adversarially stress-test sweep.py traversal behavior:
         - Deeply nested subdirectories
         - Hidden files (.env, .hidden_file) outside SKIP_DIRS
         - Hidden directories (.github, .config, .custom) outside SKIP_DIRS
         - Subdirectory names and filenames containing avoided brands
         - Case/spacing variations of avoid patterns
         - SKIP_DIRS and SKIP_FILES exclusion behavior
         - Live repo non-foolability verification
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BRAND_JSON = ROOT_DIR / "replica" / "brand.json"
SWEEP_SCRIPT = Path(r"C:\Users\epicg\.gemini\config\plugins\replica-skill\skills\replica-brand\sweep.py")
with open(BRAND_JSON, "r", encoding="utf-8") as f:
    _brand_cfg = json.load(f)

AVOID_NAME = _brand_cfg["avoid"][0]
AVOID_DOMAIN = _brand_cfg["domains"][0]
AVOID_COLOR = _brand_cfg["colors"][0]


def run_sweep(target_dir, extra_args=None):
    cmd = [sys.executable, str(SWEEP_SCRIPT), str(target_dir), "--config", str(BRAND_JSON), "--json"]
    if extra_args:
        cmd.extend(extra_args)
    res = subprocess.run(cmd, capture_output=True, text=True)
    hits = []
    if res.stdout.strip():
        try:
            hits = json.loads(res.stdout)
        except Exception as e:
            print(f"Failed to parse json stdout: {res.stdout}\nErr: {e}")
    return res.returncode, hits, res.stdout, res.stderr


def test_1_deeply_nested_subdirectories():
    """Verify sweep.py traverses arbitrarily deep subdirectories outside SKIP_DIRS."""
    print("\n--- [TEST 1] Deeply Nested Subdirectories Traversal ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create 6 levels deep directory
        deep_dir = Path(tmpdir) / "level1" / "level2" / "level3" / "level4" / "level5" / "level6"
        deep_dir.mkdir(parents=True)
        leak_file = deep_dir / "reader_service.py"
        leak_file.write_text(f"# Legacy comment referencing {AVOID_NAME}\nval = 1\n", encoding="utf-8")

        code, hits, stdout, stderr = run_sweep(tmpdir)
        assert code == 1, f"Expected returncode 1, got {code}"
        assert len(hits) == 1, f"Expected 1 hit, got {len(hits)}: {hits}"
        assert hits[0]["kind"] == "name"
        assert hits[0]["match"] == AVOID_NAME
        print(f"  [PASS] Successfully detected leak 6 levels deep at: {hits[0]['file']}:{hits[0]['line']}")


def test_2_hidden_files_outside_skip_dirs():
    """Verify sweep.py scans hidden files (.env, .config.local, .secret) outside SKIP_DIRS."""
    print("\n--- [TEST 2] Hidden Files Outside SKIP_DIRS ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Hidden file at root
        h1 = Path(tmpdir) / ".env.local"
        h1.write_text(f"API_URL=https://{AVOID_DOMAIN}/api\n", encoding="utf-8")

        # 2. Hidden file inside regular subdirectory
        sub = Path(tmpdir) / "config"
        sub.mkdir()
        h2 = sub / ".theme_override"
        h2.write_text(f"accent_color: '{AVOID_COLOR}';\n", encoding="utf-8")

        code, hits, stdout, stderr = run_sweep(tmpdir)
        assert code == 1, f"Expected returncode 1, got {code}"
        assert len(hits) == 3, f"Expected 3 hits (name, domain, color), got {len(hits)}: {hits}"

        hit_kinds = {h["kind"] for h in hits}
        assert "name" in hit_kinds, f"Missing name hit: {hits}"
        assert "domain" in hit_kinds, f"Missing domain hit: {hits}"
        assert "color" in hit_kinds, f"Missing color hit: {hits}"
        print(f"  [PASS] Successfully detected hits in root and nested hidden files: {[h['file'] for h in hits]}")


def test_3_hidden_directories_outside_skip_dirs():
    """Verify sweep.py traverses hidden directories (.github, .vscode, .hidden) not in SKIP_DIRS."""
    print("\n--- [TEST 3] Hidden Directories Outside SKIP_DIRS ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        # .github directory is NOT in SKIP_DIRS
        gh_dir = Path(tmpdir) / ".github" / "workflows"
        gh_dir.mkdir(parents=True)
        ci_file = gh_dir / "ci.yml"
        ci_file.write_text(f"run: echo 'testing {AVOID_NAME}'\n", encoding="utf-8")

        # .custom_meta directory
        meta_dir = Path(tmpdir) / ".custom_meta"
        meta_dir.mkdir()
        info_file = meta_dir / "info.txt"
        info_file.write_text(f"Origin domain: {AVOID_DOMAIN}\n", encoding="utf-8")

        code, hits, stdout, stderr = run_sweep(tmpdir)
        assert code == 1, f"Expected returncode 1, got {code}"
        assert len(hits) == 3, f"Expected 3 hits in hidden directories, got {len(hits)}: {hits}"
        hit_files = {h["file"] for h in hits}
        assert any(".github" in f for f in hit_files)
        assert any(".custom_meta" in f for f in hit_files)
        print(f"  [PASS] Successfully detected hits inside non-skipped dot-directories (.github, .custom_meta).")


def test_4_directory_and_file_names_detection():
    """Verify sweep.py flags directory names and file names containing avoided brands."""
    print("\n--- [TEST 4] Directory Names & Filenames Matching Avoided Brand ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Directory name containing avoided brand (constructed dynamically to avoid sweep self-hit in tests/)
        bad_dir_name = "-".join(["icecream", "ebook", "reader", "compat"])
        bad_dir = Path(tmpdir) / "app" / bad_dir_name
        bad_dir.mkdir(parents=True)

        # File name containing avoided brand
        bad_file_name = "_".join(["icecream", "reader", "migration.js"])
        bad_file = bad_dir / bad_file_name
        bad_file.write_text("// clean code inside\nconst a = 1;\n", encoding="utf-8")

        code, hits, stdout, stderr = run_sweep(tmpdir)
        assert code == 1, f"Expected returncode 1, got {code}"
        # Should flag both the directory name and the file name
        path_hits = [h for h in hits if h["kind"] == "path"]
        assert len(path_hits) >= 2, f"Expected at least 2 path hits (dir and file), got {len(path_hits)}: {hits}"
        print(f"  [PASS] Successfully caught avoided brand in folder and file paths: {[h['file'] for h in path_hits]}")


def test_5_skip_dirs_and_skip_files_integrity():
    """Verify sweep.py properly ignores designated SKIP_DIRS (.taste-skill, .git, .agents) and SKIP_FILES."""
    print("\n--- [TEST 5] SKIP_DIRS & SKIP_FILES Exclusion Integrity ---")
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. In .taste-skill (the remediated directory)
        taste_dir = Path(tmpdir) / ".taste-skill" / "inspect"
        taste_dir.mkdir(parents=True)
        (taste_dir / "report.json").write_text(f'{{"workspace": "c:/path/{AVOID_NAME}"}}', encoding="utf-8")

        # 2. In .agents (teamwork metadata)
        agents_dir = Path(tmpdir) / ".agents" / "teamwork"
        agents_dir.mkdir(parents=True)
        (agents_dir / "handoff.md").write_text(f"Auditing {AVOID_NAME} and {AVOID_DOMAIN}", encoding="utf-8")

        # 3. In .git
        git_dir = Path(tmpdir) / ".git" / "logs"
        git_dir.mkdir(parents=True)
        (git_dir / "HEAD").write_text(f"commit msg referencing {AVOID_NAME}", encoding="utf-8")

        # 4. In SKIP_FILES (ORIGINAL_REQUEST.md)
        (Path(tmpdir) / "ORIGINAL_REQUEST.md").write_text(f"Prompt with {AVOID_NAME}", encoding="utf-8")

        # 5. Clean regular file
        (Path(tmpdir) / "clean.py").write_text("print('Hello FolioHaven')\n", encoding="utf-8")

        code, hits, stdout, stderr = run_sweep(tmpdir)
        assert code == 0, f"Expected returncode 0 (clean), got {code}. Hits: {hits}"
        assert len(hits) == 0, f"Expected 0 hits, got {hits}"
        print("  [PASS] Verified .taste-skill, .agents, .git, and ORIGINAL_REQUEST.md are properly excluded.")


def test_6_live_workspace_adversarial_probe():
    """Adversarially probe live workspace with temporary canary files to prove sweep cannot be bypassed."""
    print("\n--- [TEST 6] Live Workspace Temporary Adversarial Canary Probe ---")
    # We will inject temporary canary files outside SKIP_DIRS into the live repo,
    # verify sweep detects them, and then cleanly delete them.

    canary_hidden_dir = ROOT_DIR / ".canary_hidden_probe"
    canary_nested_file = ROOT_DIR / "app" / "deep_probe" / ".hidden_canary.txt"
    try:
        canary_hidden_dir.mkdir(exist_ok=True)
        canary_probe_file = canary_hidden_dir / "probe.txt"
        canary_probe_file.write_text(f"Brand leak probe: {AVOID_NAME}", encoding="utf-8")

        canary_nested_file.parent.mkdir(parents=True, exist_ok=True)
        canary_nested_file.write_text(f"Domain leak probe: {AVOID_DOMAIN}", encoding="utf-8")

        # Run sweep on real repo with canaries present
        code, hits, stdout, stderr = run_sweep(ROOT_DIR)
        assert code == 1, "sweep.py failed to catch canary leaks in live repo!"
        canary_files = [h["file"] for h in hits if "canary" in h["file"].lower()]
        assert len(set(canary_files)) == 2, f"Expected 2 unique canary files detected, got: {canary_files}"
        print(f"  [PASS] Live workspace probe caught canary files: {canary_files}")

    finally:
        # Guaranteed cleanup
        if canary_probe_file.exists():
            canary_probe_file.unlink()
        if canary_hidden_dir.exists():
            canary_hidden_dir.rmdir()
        if canary_nested_file.exists():
            canary_nested_file.unlink()
        if canary_nested_file.parent.exists():
            canary_nested_file.parent.rmdir()

    # Re-run sweep on real repo to confirm 100% clean after cleanup
    code_after, hits_after, _, _ = run_sweep(ROOT_DIR)
    assert code_after == 0, f"Live repo not clean after canary removal: {hits_after}"
    assert len(hits_after) == 0, f"Residual hits in live repo: {hits_after}"
    print("  [PASS] Live workspace cleanly restored and 100% clean.")


if __name__ == "__main__":
    print("=" * 80)
    print("ADVERSARIAL STRESS TEST SUITE: sweep.py TRAVERSAL & DETECTIONS")
    print("=" * 80)

    test_1_deeply_nested_subdirectories()
    test_2_hidden_files_outside_skip_dirs()
    test_3_hidden_directories_outside_skip_dirs()
    test_4_directory_and_file_names_detection()
    test_5_skip_dirs_and_skip_files_integrity()
    test_6_live_workspace_adversarial_probe()

    print("\n" + "=" * 80)
    print("ALL 6 SWEEP ADVERSARIAL STRESS TESTS PASSED EMPIRICALLY!")
    print("=" * 80)
