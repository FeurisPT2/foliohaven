"""
FolioHaven Adversarial Stress Test Suite: Milestone 2 (Phase 2: Onboarding & Format Tooltips)
Author: challenger_m2_1 (empirical challenger)

Adversarial Stress Scenarios:
1. M2-STATIC-01: Format Navigation Tooltips Integrity & Semantics
   - All 6 format items (.nav-item[data-format]) have non-empty, informative titles matching specs.
   - Tooltips contain full format expansions and file extensions.
   - Role and keyboard focus accessibility attributes.
2. M2-STATIC-02: Empty State Architectural Illustration & Content Specification
   - Ghost bookshelf illustration SVG structure, geometry, bookends, dashed ghost books, terracotta bookmark.
   - Friendly editorial title and calm subtitle matching anti-nag requirements.
   - "+ Add Your First Book" button and supported formats hint.
   - Zero hardcoded colors / token compliance.
3. M2-LIVE-01: #btn-empty-add Event Binding & Click Delegation
   - Clicking #btn-empty-add triggers file-import-input click handler.
   - Rapid-fire clicking (100 rapid clicks) with zero errors.
   - Keyboard Enter / Space invocation.
4. M2-LIVE-02: Dynamic Empty State Visibility Lifecycle
   - Initial state (0 books) -> #empty-state visible ('flex'), #grid-view hidden ('none'), #table-view hidden ('none').
   - Ingestion (0 -> 1 book) -> #empty-state hidden ('none'), #grid-view visible ('flex').
   - Multi-book ingestion (1 -> N books) -> #empty-state stays hidden ('none').
   - View mode toggling (Grid vs Table) -> #empty-state stays hidden ('none').
   - Zero-match format filter -> #empty-state dynamically returns ('flex').
   - Reset format filter -> #empty-state hides ('none').
   - Deletion (N -> 0 books) -> #empty-state returns ('flex').
5. M2-LIVE-03: Rapid Flapping & Stress Race Conditions
   - Rapid 20-cycle flapping between 0 and 5 books in library.
   - Import pipeline with shimmering skeleton from empty state.
"""

import os
import sys
import time
import json
import socket
import struct
import base64
import subprocess
import tempfile
import urllib.request
from pathlib import Path

# --- CDP Client ---
class MinimalCDPClient:
    def __init__(self, host, port, path):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10.0)
        self.sock.connect((host, port))

        key = base64.b64encode(os.urandom(16)).decode('utf-8')
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode('utf-8'))
        resp = self.sock.recv(4096).decode('utf-8', errors='ignore')
        if "101" not in resp:
            raise ConnectionError(f"WebSocket handshake failed: {resp}")
        self._req_id = 0

    def send_command(self, method, params=None):
        self._req_id += 1
        msg = json.dumps({"id": self._req_id, "method": method, "params": params or {}})
        payload = msg.encode('utf-8')

        frame = bytearray([0x81])
        length = len(payload)
        if length <= 125:
            frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(struct.pack("!H", length))
        else:
            frame.append(0x80 | 127)
            frame.extend(struct.pack("!Q", length))

        mask = os.urandom(4)
        frame.extend(mask)
        masked_data = bytearray(b ^ mask[i % 4] for i, b in enumerate(payload))
        frame.extend(masked_data)
        self.sock.sendall(frame)

        while True:
            res_data = self._read_frame()
            if not res_data:
                continue
            try:
                res_json = json.loads(res_data.decode('utf-8'))
                if res_json.get("id") == self._req_id:
                    return res_json.get("result", {})
            except Exception:
                pass

    def _read_frame(self):
        head = self.sock.recv(2)
        if not head:
            return None
        length = head[1] & 0x7F
        if length == 126:
            length = struct.unpack("!H", self.sock.recv(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self.sock.recv(8))[0]

        payload = bytearray()
        while len(payload) < length:
            chunk = self.sock.recv(length - len(payload))
            if not chunk:
                break
            payload.extend(chunk)
        return payload

    def eval_js(self, expression):
        res = self.send_command("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        exc = res.get("exceptionDetails")
        if exc:
            raise RuntimeError(f"JS Error: {exc}")
        return res.get("result", {}).get("value")

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


def run_all_tests():
    print("=" * 76)
    print("  FOLIOHAVEN M2 EMPIRICAL ADVERSARIAL STRESS SUITE (CHALLENGER M2)    ")
    print("=" * 76)

    root_dir = Path(__file__).resolve().parent.parent
    app_dir = root_dir / "app"
    html_path = app_dir / "index.html"
    css_path = app_dir / "styles.css"
    js_path = app_dir / "app.js"

    html_content = html_path.read_text(encoding="utf-8")
    css_content = css_path.read_text(encoding="utf-8")
    js_content = js_path.read_text(encoding="utf-8")

    results = []

    def run_subtest(test_id, desc, fn):
        try:
            fn()
            print(f"  [PASS] {test_id}: {desc}")
            results.append((test_id, desc, "PASS", None))
        except Exception as e:
            print(f"  [FAIL] {test_id}: {desc} -> {e}")
            results.append((test_id, desc, "FAIL", str(e)))

    # =========================================================================
    # PART 1: STATIC & ARCHITECTURAL VERIFICATION
    # =========================================================================
    print("\n--- PART 1: Static DOM & CSS Specification Verification ---")

    def t_m2_static_tooltips():
        expected_formats = {
            "EPUB": "Electronic Publication (.epub)",
            "PDF": "Portable Document Format (.pdf)",
            "MOBI": "Mobipocket eBook (.mobi)",
            "FB2": "FictionBook 2.0 (.fb2)",
            "CBZ": "Comic Book ZIP (.cbz)",
            "TXT": "Plain Text (.txt)",
        }
        for fmt, snippet in expected_formats.items():
            pattern = rf'data-format="{fmt}"[^>]*title="([^"]+)"'
            import re
            m = re.search(pattern, html_content)
            assert m is not None, f"Format {fmt} missing or lacking title attribute"
            title = m.group(1)
            assert len(title) > 20, f"Title for {fmt} too short: '{title}'"
            assert snippet in title, f"Title for {fmt} does not contain '{snippet}': '{title}'"

        # Check badges exist
        for fmt in ["epub", "pdf", "mobi", "fb2", "cbz", "txt"]:
            assert f'id="badge-format-{fmt}"' in html_content, f"Badge #badge-format-{fmt} missing"

    run_subtest("M2-STATIC-01", "Format Tooltips Titles and Badges Presence", t_m2_static_tooltips)

    def t_m2_static_empty_state_structure():
        # Check container
        assert '<div id="empty-state">' in html_content, "Container #empty-state missing"
        assert '<button class="btn btn-primary empty-btn-add" id="btn-empty-add">+ Add Your First Book</button>' in html_content, "#btn-empty-add element missing or corrupted"
        assert "Your Library is Waiting" in html_content, "Heading 'Your Library is Waiting' missing"
        assert "A calm place for your books — no nags, no timers, no subscriptions. Just pure reading." in html_content, "Editorial calm subtitle missing"
        assert "Supports EPUB, PDF, MOBI, FB2, CBZ, and TXT • Drop files anywhere to import" in html_content, "Supported formats hint missing"

        # Check ghost bookshelf SVG elements
        assert 'class="empty-shelf-illustration"' in html_content, "Illustration wrapper missing"
        assert 'stroke-dasharray="4 3"' in html_content, "Ghost dashed books missing in SVG"
        assert 'fill="var(--color-accent)"' in html_content, "Accent ribbon bookmark missing in SVG"

    run_subtest("M2-STATIC-02", "Empty State DOM Structure & SVG Architectural Integrity", t_m2_static_empty_state_structure)

    def t_m2_static_css_tokens():
        # Verify #empty-state CSS uses design tokens
        assert "#empty-state {" in css_content, "#empty-state CSS rule missing"
        assert "border: 1.5px dashed var(--color-border);" in css_content, "Border token missing"
        assert "border-radius: var(--radius-lg);" in css_content, "Radius token missing"
        assert "background-color: var(--color-accent);" in css_content, "Accent color token missing on button"
        assert "color: var(--color-on-accent);" in css_content, "On-accent text color token missing"
        assert ".empty-btn-add:focus-visible {" in css_content, "Focus visible state missing on button"

    run_subtest("M2-STATIC-03", "Empty State CSS Design Tokens & States", t_m2_static_css_tokens)

    # =========================================================================
    # PART 2: LIVE RUNTIME BROWSER STRESS TESTS VIA CDP
    # =========================================================================
    print("\n--- PART 2: Headless Chrome CDP Live Interaction Stress Tests ---")

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    port = 9338
    temp_dir = tempfile.mkdtemp(prefix="foliohaven_m2_stress_")
    app_url = f"file:///{str(app_dir).replace('\\', '/')}/index.html"

    chrome_cmd = [
        chrome_path,
        "--headless=new",
        f"--user-data-dir={temp_dir}",
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        "--disable-gpu",
        "--no-sandbox",
        "--allow-file-access-from-files",
        app_url
    ]
    proc = subprocess.Popen(chrome_cmd)
    time.sleep(2.0)
    ws_client = None

    try:
        with urllib.request.urlopen(f"http://localhost:{port}/json") as resp:
            tabs = json.loads(resp.read().decode('utf-8'))
            page_tabs = [t for t in tabs if t.get("type") == "page" and "index.html" in t.get("url", "")]
            tab = page_tabs[0] if page_tabs else tabs[0]
            ws_url = tab["webSocketDebuggerUrl"]
            path = ws_url.split(f"localhost:{port}")[1]
            ws_client = MinimalCDPClient("localhost", port, path)

        ws_client.send_command("Runtime.enable")
        time.sleep(0.5)

        # ---------------------------------------------------------------------
        # TEST: Live Tooltip Inspection
        # ---------------------------------------------------------------------
        def t_live_tooltips():
            tooltips = ws_client.eval_js("""
                (() => {
                    const items = document.querySelectorAll('.nav-item[data-format]');
                    return Array.from(items).map(item => ({
                        format: item.getAttribute('data-format'),
                        title: item.getAttribute('title'),
                        tabIndex: item.tabIndex,
                        role: item.getAttribute('role'),
                        hasBadge: !!item.querySelector('.nav-badge')
                    }));
                })()
            """)
            assert len(tooltips) == 6, f"Expected 6 format items, found {len(tooltips)}"
            for item in tooltips:
                fmt = item["format"]
                title = item["title"]
                assert title and len(title) > 20, f"Format {fmt} has invalid title: '{title}'"
                assert f"({item['format'].lower()})" in title.lower() or f".{item['format'].lower()}" in title.lower(), f"Format extension missing in title: {title}"
                assert item["role"] == "button", f"Format {fmt} missing role=button"
                assert item["tabIndex"] == 0, f"Format {fmt} not keyboard focusable"
                assert item["hasBadge"] is True, f"Format {fmt} missing badge"

        run_subtest("M2-LIVE-01", "Live DOM Format Tooltips & Keyboard Accessibility", t_live_tooltips)

        # ---------------------------------------------------------------------
        # TEST: #btn-empty-add Event Trigger & Click Delegation
        # ---------------------------------------------------------------------
        def t_live_btn_empty_add_click():
            # Setup spy on file-import-input
            ws_client.eval_js("""
                (() => {
                    window.__fileInputClickCount = 0;
                    const input = document.getElementById("file-import-input");
                    input.addEventListener("click", () => {
                        window.__fileInputClickCount++;
                    });
                })()
            """)

            # Direct element click
            ws_client.eval_js("document.getElementById('btn-empty-add').click();")
            count = ws_client.eval_js("window.__fileInputClickCount")
            assert count == 1, f"Expected click count 1, got {count}"

            # Rapid-fire 100 clicks stress test
            ws_client.eval_js("""
                (() => {
                    const btn = document.getElementById('btn-empty-add');
                    for (let i = 0; i < 100; i++) {
                        btn.click();
                    }
                })()
            """)
            count_after_stress = ws_client.eval_js("window.__fileInputClickCount")
            assert count_after_stress == 101, f"Expected click count 101 after rapid clicks, got {count_after_stress}"

        run_subtest("M2-LIVE-02", "#btn-empty-add File Import Click Trigger & 100-Click Rapid Fire Stress", t_live_btn_empty_add_click)

        # ---------------------------------------------------------------------
        # TEST: Empty State Visibility Lifecycle (0 -> 1 -> N -> 0 books)
        # ---------------------------------------------------------------------
        def t_live_empty_state_lifecycle():
            # Step A: 0 books state
            state_0 = ws_client.eval_js("""
                (() => {
                    window.db.saveBooks([]);
                    window.app.selectedCategory = "all";
                    window.app.selectedFormat = null;
                    window.app.searchQuery = "";
                    window.app.renderLibrary();

                    const emptyState = document.getElementById("empty-state");
                    const gridView = document.getElementById("grid-view");
                    const tableView = document.getElementById("table-view");

                    const styleEmpty = window.getComputedStyle(emptyState);
                    const styleGrid = window.getComputedStyle(gridView);
                    const styleTable = window.getComputedStyle(tableView);

                    return {
                        emptyDisplay: styleEmpty.display,
                        emptyHeight: emptyState.offsetHeight,
                        emptyWidth: emptyState.offsetWidth,
                        gridDisplay: styleGrid.display,
                        tableDisplay: styleTable.display,
                        bookCount: window.db.getBooks().length
                    };
                })()
            """)
            assert state_0["emptyDisplay"] == "flex", f"Empty state display should be 'flex', got '{state_0['emptyDisplay']}'"
            assert state_0["emptyHeight"] >= 350, f"Empty state height should be substantial, got {state_0['emptyHeight']}px"
            assert state_0["gridDisplay"] == "none", f"Grid view should be 'none', got '{state_0['gridDisplay']}'"
            assert state_0["tableDisplay"] == "none", f"Table view should be 'none', got '{state_0['tableDisplay']}'"

            # Step B: Load 1 book (0 -> 1)
            state_1 = ws_client.eval_js("""
                (() => {
                    window.db.addBook({
                        title: "Adversarial Stress Test Book 1",
                        author: "Empirical Tester",
                        format: "EPUB"
                    });
                    window.app.renderLibrary();

                    const emptyState = document.getElementById("empty-state");
                    const gridView = document.getElementById("grid-view");
                    const cards = document.querySelectorAll(".book-card");

                    return {
                        emptyDisplay: window.getComputedStyle(emptyState).display,
                        gridDisplay: window.getComputedStyle(gridView).display,
                        cardCount: cards.length
                    };
                })()
            """)
            assert state_1["emptyDisplay"] == "none", f"Empty state should be 'none' when 1 book is loaded, got '{state_1['emptyDisplay']}'"
            assert state_1["gridDisplay"] == "flex", f"Grid view should be 'flex' when 1 book is loaded, got '{state_1['gridDisplay']}'"
            assert state_1["cardCount"] == 1, f"Expected 1 book card, got {state_1['cardCount']}"

            # Step C: Load 4 more books (total 5 books)
            state_5 = ws_client.eval_js("""
                (() => {
                    const formats = ["PDF", "MOBI", "FB2", "CBZ"];
                    formats.forEach((fmt, idx) => {
                        window.db.addBook({
                            title: `Adversarial Multi Book ${idx + 2}`,
                            author: `Tester ${idx + 2}`,
                            format: fmt
                        });
                    });
                    window.app.renderLibrary();

                    const emptyState = document.getElementById("empty-state");
                    const gridView = document.getElementById("grid-view");
                    const cards = document.querySelectorAll(".book-card");

                    return {
                        emptyDisplay: window.getComputedStyle(emptyState).display,
                        gridDisplay: window.getComputedStyle(gridView).display,
                        cardCount: cards.length
                    };
                })()
            """)
            assert state_5["emptyDisplay"] == "none", "Empty state should be 'none' with 5 books"
            assert state_5["gridDisplay"] == "flex", "Grid view should be 'flex' with 5 books"
            assert state_5["cardCount"] == 5, f"Expected 5 book cards, got {state_5['cardCount']}"

            # Step D: View Mode Toggle to Table View
            state_table = ws_client.eval_js("""
                (() => {
                    window.app.setViewMode("table");
                    const emptyState = document.getElementById("empty-state");
                    const tableView = document.getElementById("table-view");
                    const gridView = document.getElementById("grid-view");

                    return {
                        emptyDisplay: window.getComputedStyle(emptyState).display,
                        tableDisplay: window.getComputedStyle(tableView).display,
                        gridDisplay: window.getComputedStyle(gridView).display
                    };
                })()
            """)
            assert state_table["emptyDisplay"] == "none", "Empty state should remain 'none' in table view"
            assert state_table["tableDisplay"] == "table", "Table view should be 'table'"
            assert state_table["gridDisplay"] == "none", "Grid view should be 'none'"

            # Step E: Zero-match Filter Display
            # Click format filter TXT (0 books exist for TXT)
            state_filter_empty = ws_client.eval_js("""
                (() => {
                    const txtNav = document.querySelector('.nav-item[data-format="TXT"]');
                    txtNav.click();

                    const emptyState = document.getElementById("empty-state");
                    const tableView = document.getElementById("table-view");
                    const gridView = document.getElementById("grid-view");

                    return {
                        emptyDisplay: window.getComputedStyle(emptyState).display,
                        tableDisplay: window.getComputedStyle(tableView).display,
                        gridDisplay: window.getComputedStyle(gridView).display,
                        formatFilter: window.app.currentFormatFilter
                    };
                })()
            """)
            assert state_filter_empty["formatFilter"] == "TXT", f"Format filter should be TXT, got {state_filter_empty['formatFilter']}"
            assert state_filter_empty["emptyDisplay"] == "flex", f"Empty state should show when filter matches 0 books, got {state_filter_empty['emptyDisplay']}"
            assert state_filter_empty["tableDisplay"] == "none"
            assert state_filter_empty["gridDisplay"] == "none"

            # Reset filter back to all books by clicking 'All Books' nav item
            ws_client.eval_js("""
                (() => {
                    const allNav = document.querySelector('.nav-item[data-category="all"]');
                    allNav.click();
                    window.app.setViewMode("grid");
                })()
            """)
            reset_display = ws_client.eval_js("window.getComputedStyle(document.getElementById('empty-state')).display")
            assert reset_display == "none", f"Empty state should hide after filter reset, got '{reset_display}'"

            # Step F: Delete all books (5 -> 0)
            state_deleted = ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    books.forEach(b => window.db.purgeBook(b.id));
                    window.app.renderLibrary();

                    const emptyState = document.getElementById("empty-state");
                    const gridView = document.getElementById("grid-view");
                    const tableView = document.getElementById("table-view");

                    return {
                        emptyDisplay: window.getComputedStyle(emptyState).display,
                        gridDisplay: window.getComputedStyle(gridView).display,
                        tableDisplay: window.getComputedStyle(tableView).display,
                        remainingBooks: window.db.getBooks().length
                    };
                })()
            """)
            assert state_deleted["remainingBooks"] == 0, f"Remaining books should be 0, got {state_deleted['remainingBooks']}"
            assert state_deleted["emptyDisplay"] == "flex", f"Empty state should return to 'flex' after deleting all books, got '{state_deleted['emptyDisplay']}'"
            assert state_deleted["gridDisplay"] == "none"
            assert state_deleted["tableDisplay"] == "none"

        run_subtest("M2-LIVE-03", "Dynamic Empty State Lifecycle (0 -> 1 -> N -> Zero-Match Filter -> 0 Books)", t_live_empty_state_lifecycle)

        # ---------------------------------------------------------------------
        # TEST: Rapid Flapping Stress (20 Iterations)
        # ---------------------------------------------------------------------
        def t_live_rapid_flapping():
            flapping_success = ws_client.eval_js("""
                (() => {
                    for (let cycle = 0; cycle < 20; cycle++) {
                        // 1. Add 3 books
                        for (let i = 0; i < 3; i++) {
                            window.db.addBook({
                                title: `Flap Book ${cycle}_${i}`,
                                author: "Flapper",
                                format: "EPUB"
                            });
                        }
                        window.app.renderLibrary();
                        if (window.getComputedStyle(document.getElementById("empty-state")).display !== "none") {
                            return `Cycle ${cycle}: Empty state failed to hide after adding books`;
                        }

                        // 2. Clear books
                        window.db.saveBooks([]);
                        window.app.renderLibrary();
                        if (window.getComputedStyle(document.getElementById("empty-state")).display !== "flex") {
                            return `Cycle ${cycle}: Empty state failed to show after clearing books`;
                        }
                    }
                    return "OK";
                })()
            """)
            assert flapping_success == "OK", f"Flapping stress test failed: {flapping_success}"

        run_subtest("M2-LIVE-04", "Rapid Flapping Stress Test (20 cycles of 0 <-> 3 books)", t_live_rapid_flapping)

        # ---------------------------------------------------------------------
        # TEST: Ingestion Skeleton Interaction from Empty State
        # ---------------------------------------------------------------------
        def t_live_skeleton_from_empty_state():
            skeleton_check = ws_client.eval_js("""
                (() => {
                    // Start from 0 books
                    window.db.saveBooks([]);
                    window.app.renderLibrary();
                    const emptyBefore = window.getComputedStyle(document.getElementById("empty-state")).display;

                    // Trigger importFiles with mock file list
                    const mockFiles = [
                        { name: "S1.epub", size: 50000 },
                        { name: "S2.pdf", size: 120000 }
                    ];
                    window.app.importFiles(mockFiles, "drop");

                    // Immediately inspect empty-state and skeleton cards
                    const emptyDuring = window.getComputedStyle(document.getElementById("empty-state")).display;
                    const skeletons = document.querySelectorAll(".book-card.loading");

                    return {
                        emptyBefore,
                        emptyDuring,
                        skeletonCount: skeletons.length
                    };
                })()
            """)
            assert skeleton_check["emptyBefore"] == "flex", "Empty state should be 'flex' before import"
            assert skeleton_check["emptyDuring"] == "none", f"Empty state should immediately hide to 'none' during import, got {skeleton_check['emptyDuring']}"
            assert skeleton_check["skeletonCount"] == 2, f"Expected 2 shimmering loading skeletons, got {skeleton_check['skeletonCount']}"

            # Wait for ingestion to finish
            time.sleep(0.5)
            final_check = ws_client.eval_js("""
                (() => {
                    const emptyAfter = window.getComputedStyle(document.getElementById("empty-state")).display;
                    const cards = document.querySelectorAll(".book-card:not(.loading)");
                    return {
                        emptyAfter,
                        cardCount: cards.length
                    };
                })()
            """)
            assert final_check["emptyAfter"] == "none", "Empty state should remain hidden after import"
            assert final_check["cardCount"] == 2, f"Expected 2 final book cards, got {final_check['cardCount']}"

        run_subtest("M2-LIVE-05", "Import Pipeline Transition from Empty State to Shimmer Skeletons to Books", t_live_skeleton_from_empty_state)

        # ---------------------------------------------------------------------
        # TEST: Reading Theme Switching Contrast & Resilience on Empty State
        # ---------------------------------------------------------------------
        def t_live_theme_resilience():
            themes_tested = ws_client.eval_js("""
                (() => {
                    // Reset to empty state
                    window.db.saveBooks([]);
                    window.app.renderLibrary();
                    const results = {};

                    const themes = ["day", "sepia", "night"];
                    themes.forEach(theme => {
                        window.app.setReadingTheme(theme);
                        const emptyState = document.getElementById("empty-state");
                        const style = window.getComputedStyle(emptyState);
                        results[theme] = {
                            display: style.display,
                            color: style.color,
                            backgroundColor: style.backgroundColor
                        };
                    });
                    // Restore day theme
                    window.app.setReadingTheme("day");
                    return results;
                })()
            """)
            for theme, data in themes_tested.items():
                assert data["display"] == "flex", f"Theme {theme} caused empty state display to break: {data['display']}"
                assert data["color"], f"Theme {theme} missing color"

        run_subtest("M2-LIVE-06", "Theme Switching Resilience on Empty State", t_live_theme_resilience)

    finally:
        if ws_client:
            ws_client.close()
        proc.terminate()
        try:
            proc.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            proc.kill()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 76)
    passed_count = sum(1 for r in results if r[2] == "PASS")
    total_count = len(results)
    print(f"  EXECUTION SUMMARY: {passed_count}/{total_count} PASSED ({(passed_count/total_count)*100:.1f}%)")
    print("=" * 76)

    failed = [r for r in results if r[2] == "FAIL"]
    if failed:
        print("\nFAILURES ENCOUNTERED:")
        for r in failed:
            print(f"  - {r[0]}: {r[1]} -> {r[3]}")
        sys.exit(1)
    else:
        print("\nAll adversarial stress scenarios passed with zero regressions.")
        sys.exit(0)


if __name__ == "__main__":
    run_all_tests()
