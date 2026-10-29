"""
Adversarial Empirical Regression Verification Suite for Milestone 2
(Phase 2: Onboarding & Format Tooltips)
FolioHaven Ebook Reader Replica
Author: challenger_m2_2 (empirical challenger)

Target Scope:
1. TC-M2-01: Format Filter Activation, State Management, and Category Cleared
   - Clicking each `.nav-item[data-format]` sets `currentFormatFilter`, sets `currentCategory = null`,
     updates `.active` state, and renders filtered books.
   - Returning to a category filter clears `currentFormatFilter`.
2. TC-M2-02: Format Badge Counters Dynamic Lifecycle & Non-Interference with Title Tooltips
   - Dynamic additions and deletions update `#badge-format-*` counts accurately.
   - Tooltip `title` attributes on `.nav-item[data-format]` remain completely invariant and uncorrupted.
3. TC-M2-03: Empty State Architecture & Interaction Resilience
   - Ghost bookshelf illustration, editorial title, subtitle, and formats hint.
   - Preserved `#btn-empty-add` triggers file import.
4. TC-M2-04: Format Filtering Combined with Search Query and View Modes (Grid vs Table)
   - Conjoint filtering of format + search query.
   - Switching between Grid and Table views maintains format filter.
5. TC-M2-05: Milestone 1 Feature Non-Regression in M2 Context
   - Confirmation modals, undo toast, book import skeleton, drag feedback, and a11y labels.
"""

import os
import sys
import time
import json
import socket
import urllib.request
import subprocess
import tempfile
from pathlib import Path


class CDPClient:
    def __init__(self, host, port, path):
        self.sock = socket.create_connection((host, port), timeout=10)
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
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
            frame.extend(length.to_bytes(2, 'big'))
        else:
            frame.append(0x80 | 127)
            frame.extend(length.to_bytes(8, 'big'))

        mask = b'\x12\x34\x56\x78'
        frame.extend(mask)
        masked = bytearray(payload)
        for i in range(len(masked)):
            masked[i] ^= mask[i % 4]
        frame.extend(masked)

        self.sock.sendall(frame)

        while True:
            resp = self._read_frame()
            if not resp:
                continue
            try:
                res_json = json.loads(resp.decode('utf-8'))
                if res_json.get("id") == self._req_id:
                    return res_json.get("result", {})
            except Exception:
                pass

    def _read_frame(self):
        head = self.sock.recv(2)
        if len(head) < 2:
            return None
        b1, b2 = head[0], head[1]
        length = b2 & 0x7F
        if length == 126:
            length = int.from_bytes(self.sock.recv(2), 'big')
        elif length == 127:
            length = int.from_bytes(self.sock.recv(8), 'big')

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
        val = res.get("result", {}).get("value")
        exc = res.get("exceptionDetails")
        if exc:
            raise RuntimeError(f"JS Error: {exc}")
        return val

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


def run_empirical_m2_suite():
    print("=" * 76)
    print("  FOLIOHAVEN CHALLENGER M2: EMPIRICAL REGRESSION & STRESS SUITE       ")
    print("=" * 76)

    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    app_url = f"file:///{app_dir.replace('\\', '/')}/index.html"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    port = 9345  # Dedicated port for M2 challenger
    temp_dir = tempfile.mkdtemp(prefix="foliohaven_m2_chal_")

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
    results = []

    def test(test_id, description, fn):
        try:
            fn()
            print(f"  [PASS] {test_id}: {description}")
            results.append((test_id, description, "PASS", None))
        except Exception as e:
            print(f"  [FAIL] {test_id}: {description} -> {e}")
            results.append((test_id, description, "FAIL", str(e)))

    try:
        with urllib.request.urlopen(f"http://localhost:{port}/json") as resp:
            tabs = json.loads(resp.read().decode('utf-8'))
            page_tabs = [t for t in tabs if t.get("type") == "page" and "app/index.html" in t.get("url", "")]
            tab = page_tabs[0] if page_tabs else tabs[0]
            ws_url = tab["webSocketDebuggerUrl"]
            path = ws_url.split(f"localhost:{port}")[1]
            ws_client = CDPClient("localhost", port, path)

        ws_client.send_command("Runtime.enable")
        time.sleep(0.5)

        # ----------------------------------------------------------------------
        # TC-M2-01: Format Filter Activation, State Management, and Category Cleared
        # ----------------------------------------------------------------------
        def t_format_filter_state_and_rendering():
            # Reset DB with seed books
            ws_client.eval_js("""
                (() => {
                    localStorage.clear();
                    window.db.init();

                    const allEl = document.querySelector('.nav-item[data-category="all"]');
                    allEl.click();
                    window.app.updateBadges();
                    window.app.renderLibrary();
                })()
            """)

            formats = ["EPUB", "PDF", "MOBI", "FB2", "CBZ", "TXT"]

            for fmt in formats:
                # 1. First set category to 'favorites' to verify that clicking format clears it
                ws_client.eval_js("""
                    (() => {
                        const favEl = document.querySelector('.nav-item[data-category="favorites"]');
                        favEl.click();
                    })()
                """)
                cat_before = ws_client.eval_js("window.app.currentCategory")
                assert cat_before == "favorites", f"Expected category 'favorites', got {cat_before}"

                # 2. Click format nav item
                state = ws_client.eval_js(f"""
                    (() => {{
                        const fmtEl = document.querySelector('.nav-item[data-format="{fmt}"]');
                        fmtEl.click();

                        const activeNavItems = Array.from(document.querySelectorAll('.nav-item.active'));
                        const renderedCards = Array.from(document.querySelectorAll('#grid-view .book-card'));
                        const dbMatching = window.db.getBooks().filter(b => !b.is_deleted && b.format === "{fmt}");

                        return {{
                            currentFormatFilter: window.app.currentFormatFilter,
                            currentCategory: window.app.currentCategory,
                            activeItemCount: activeNavItems.length,
                            activeFormat: activeNavItems[0] ? activeNavItems[0].dataset.format : null,
                            cardCount: renderedCards.length,
                            expectedCount: dbMatching.length,
                            emptyStateVis: document.getElementById('empty-state').style.display,
                            gridVis: document.getElementById('grid-view').style.display
                        }};
                    }})()
                """)

                assert state["currentFormatFilter"] == fmt, f"currentFormatFilter was not set to {fmt}: {state['currentFormatFilter']}"
                assert state["currentCategory"] is None, f"currentCategory was not cleared to null for {fmt}: {state['currentCategory']}"
                assert state["activeItemCount"] == 1, f"Expected 1 active nav item, found {state['activeItemCount']}"
                assert state["activeFormat"] == fmt, f"Active nav item format mismatch: {state['activeFormat']} != {fmt}"
                assert state["cardCount"] == state["expectedCount"], f"Rendered cards for {fmt} expected {state['expectedCount']}, got {state['cardCount']}"
                if state["expectedCount"] > 0:
                    assert state["emptyStateVis"] == "none", f"Empty state incorrectly displayed for non-empty format {fmt}"
                    assert state["gridVis"] == "flex", f"Grid view should be flex"
                else:
                    assert state["emptyStateVis"] == "flex", f"Empty state should be displayed when format has 0 books"
                    assert state["gridVis"] == "none", f"Grid view should be hidden when format has 0 books"

            # 3. Test Empty Format Filter (Zero matching books)
            # Soft-delete all books of a specific format
            empty_state_res = ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    books.forEach(b => {
                        if (b.format === "TXT") b.is_deleted = 1;
                    });
                    window.db.saveBooks(books);

                    // Click TXT format filter
                    const txtEl = document.querySelector('.nav-item[data-format="TXT"]');
                    txtEl.click();

                    return {
                        currentFormatFilter: window.app.currentFormatFilter,
                        currentCategory: window.app.currentCategory,
                        emptyDisplay: document.getElementById('empty-state').style.display,
                        gridDisplay: document.getElementById('grid-view').style.display,
                        matchedBooksCount: window.app.getFilteredBooks().length
                    };
                })()
            """)
            assert empty_state_res["currentFormatFilter"] == "TXT", f"Expected currentFormatFilter 'TXT', got {empty_state_res['currentFormatFilter']}"
            assert empty_state_res["currentCategory"] is None, f"Expected currentCategory None, got {empty_state_res['currentCategory']}"
            assert empty_state_res["matchedBooksCount"] == 0, f"Filtered books should be 0, got {empty_state_res['matchedBooksCount']}"
            assert empty_state_res["emptyDisplay"] == "flex", f"Empty state should show for 0 books, got {empty_state_res['emptyDisplay']}"
            assert empty_state_res["gridDisplay"] == "none", f"Grid view should be hidden when empty"

            # 4. Switching from Format Filter back to Category Filter clears currentFormatFilter
            cat_restore = ws_client.eval_js("""
                (() => {
                    const allEl = document.querySelector('.nav-item[data-category="all"]');
                    allEl.click();
                    return {
                        currentCategory: window.app.currentCategory,
                        currentFormatFilter: window.app.currentFormatFilter,
                        activeCategory: document.querySelector('.nav-item.active') ? document.querySelector('.nav-item.active').dataset.category : null
                    };
                })()
            """)
            assert cat_restore["currentCategory"] == "all", f"Category not restored: {cat_restore['currentCategory']}"
            assert cat_restore["currentFormatFilter"] is None, f"currentFormatFilter not cleared when switching to category: {cat_restore['currentFormatFilter']}"
            assert cat_restore["activeCategory"] == "all", f"Active category mismatch: {cat_restore['activeCategory']}"

        test("TC-M2-01", "Format Filter Activation, State Management, and Category Cleared", t_format_filter_state_and_rendering)

        # ----------------------------------------------------------------------
        # TC-M2-02: Format Badge Counters Dynamic Lifecycle & Non-Interference with Title Tooltips
        # ----------------------------------------------------------------------
        def t_format_badge_counters_and_tooltips():
            expected_tooltips = {
                "EPUB": "Electronic Publication (.epub) — standard reflowable ebook format",
                "PDF": "Portable Document Format (.pdf) — fixed-layout documents and books",
                "MOBI": "Mobipocket eBook (.mobi) — legacy Kindle and handheld format",
                "FB2": "FictionBook 2.0 (.fb2) — XML-based Russian and international ebook format",
                "CBZ": "Comic Book ZIP (.cbz) — archive of images for comics and manga",
                "TXT": "Plain Text (.txt) — unformatted raw text files"
            }

            # 1. Audit initial tooltip titles and badge IDs
            initial_tooltips = ws_client.eval_js("""
                Array.from(document.querySelectorAll('.nav-item[data-format]')).map(el => ({
                    format: el.dataset.format,
                    title: el.getAttribute('title'),
                    badgeId: el.querySelector('.nav-badge') ? el.querySelector('.nav-badge').id : null,
                    badgeText: el.querySelector('.nav-badge') ? el.querySelector('.nav-badge').textContent : null,
                    labelSpanText: el.querySelector('.item-left span') ? el.querySelector('.item-left span').textContent : null
                }))
            """)
            assert len(initial_tooltips) == 6, f"Expected 6 format items, found {len(initial_tooltips)}"
            for it in initial_tooltips:
                f = it["format"]
                assert f in expected_tooltips, f"Unknown format {f}"
                assert it["title"] == expected_tooltips[f], f"Tooltip title mismatch for {f}: '{it['title']}' != '{expected_tooltips[f]}'"
                assert it["badgeId"] == f"badge-format-{f.lower()}", f"Badge ID mismatch for {f}: {it['badgeId']}"
                assert it["labelSpanText"] == f, f"Label text mismatch for {f}: {it['labelSpanText']}"

            # 2. Add multiple books dynamically with distinct IDs and update badges
            add_res = ws_client.eval_js("""
                (async () => {
                    const initialFb2Count = window.db.getBooks().filter(b => !b.is_deleted && b.format === "FB2").length;
                    const initialCbzCount = window.db.getBooks().filter(b => !b.is_deleted && b.format === "CBZ").length;

                    // Add 3 FB2 books, 2 CBZ books with unique IDs
                    const books = window.db.getBooks();
                    const newBooks = [
                        { id: "test_fb2_1", title: "FB2 Dyn 1", author: "Auth", format: "FB2", file_size_bytes: 1000, is_deleted: 0 },
                        { id: "test_fb2_2", title: "FB2 Dyn 2", author: "Auth", format: "FB2", file_size_bytes: 1000, is_deleted: 0 },
                        { id: "test_fb2_3", title: "FB2 Dyn 3", author: "Auth", format: "FB2", file_size_bytes: 1000, is_deleted: 0 },
                        { id: "test_cbz_1", title: "CBZ Dyn 1", author: "Auth", format: "CBZ", file_size_bytes: 1000, is_deleted: 0 },
                        { id: "test_cbz_2", title: "CBZ Dyn 2", author: "Auth", format: "CBZ", file_size_bytes: 1000, is_deleted: 0 }
                    ];
                    newBooks.forEach(nb => books.unshift(nb));
                    window.db.saveBooks(books);

                    window.app.updateBadges();

                    const fb2Badge = document.getElementById('badge-format-fb2').textContent;
                    const cbzBadge = document.getElementById('badge-format-cbz').textContent;
                    const fb2Title = document.querySelector('.nav-item[data-format="FB2"]').getAttribute('title');
                    const cbzTitle = document.querySelector('.nav-item[data-format="CBZ"]').getAttribute('title');

                    return {
                        initialFb2Count,
                        initialCbzCount,
                        fb2Badge: parseInt(fb2Badge, 10),
                        cbzBadge: parseInt(cbzBadge, 10),
                        fb2Title,
                        cbzTitle
                    };
                })()
            """)
            assert add_res["fb2Badge"] == add_res["initialFb2Count"] + 3, f"FB2 badge should be {add_res['initialFb2Count'] + 3}, got {add_res['fb2Badge']}"
            assert add_res["cbzBadge"] == add_res["initialCbzCount"] + 2, f"CBZ badge should be {add_res['initialCbzCount'] + 2}, got {add_res['cbzBadge']}"
            assert add_res["fb2Title"] == expected_tooltips["FB2"], f"FB2 title mutated after badge update: {add_res['fb2Title']}"
            assert add_res["cbzTitle"] == expected_tooltips["CBZ"], f"CBZ title mutated after badge update: {add_res['cbzTitle']}"

            # 3. Soft-delete books to verify badge decrement does not touch title
            del_res = ws_client.eval_js("""
                (() => {
                    const fb2Books = window.db.getBooks().filter(b => b.format === "FB2" && !b.is_deleted);
                    window.db.softDeleteBook(fb2Books[0].id);
                    window.db.softDeleteBook(fb2Books[1].id);

                    window.app.updateBadges();

                    return {
                        expectedFb2: fb2Books.length - 2,
                        fb2Badge: parseInt(document.getElementById('badge-format-fb2').textContent, 10),
                        fb2Title: document.querySelector('.nav-item[data-format="FB2"]').getAttribute('title')
                    };
                })()
            """)
            assert del_res["fb2Badge"] == del_res["expectedFb2"], f"FB2 badge should decrement to {del_res['expectedFb2']}, got {del_res['fb2Badge']}"
            assert del_res["fb2Title"] == expected_tooltips["FB2"], f"FB2 title mutated after delete: {del_res['fb2Title']}"

        test("TC-M2-02", "Format Badge Counters Dynamic Lifecycle & Non-Interference with Title Tooltips", t_format_badge_counters_and_tooltips)

        # ----------------------------------------------------------------------
        # TC-M2-03: Empty State Architecture & Interaction Resilience
        # ----------------------------------------------------------------------
        def t_empty_state_architecture():
            # Reset to 'all' category first so no format filters are active
            empty_check = ws_client.eval_js("""
                (() => {
                    const allEl = document.querySelector('.nav-item[data-category="all"]');
                    allEl.click();

                    // Mark all books as deleted
                    const books = window.db.getBooks();
                    books.forEach(b => {
                        b.is_deleted = 1;
                    });
                    window.db.saveBooks(books);
                    window.app.renderLibrary();

                    const emptyState = document.getElementById('empty-state');
                    const svg = emptyState.querySelector('.empty-shelf-illustration');
                    const title = emptyState.querySelector('.empty-title');
                    const subtitle = emptyState.querySelector('.empty-subtitle');
                    const addBtn = document.getElementById('btn-empty-add');
                    const hint = emptyState.querySelector('.empty-formats-hint');

                    return {
                        emptyVis: emptyState.style.display,
                        hasSvg: svg !== null,
                        svgDashedPaths: svg ? svg.querySelectorAll('[stroke-dasharray]').length : 0,
                        titleText: title ? title.textContent.trim() : null,
                        subtitleText: subtitle ? subtitle.textContent.trim() : null,
                        btnExists: addBtn !== null,
                        btnText: addBtn ? addBtn.textContent.trim() : null,
                        btnClass: addBtn ? addBtn.className : null,
                        hintText: hint ? hint.textContent.trim() : null
                    };
                })()
            """)

            assert empty_check["emptyVis"] == "flex", f"Empty state not visible: {empty_check['emptyVis']}"
            assert empty_check["hasSvg"], "Missing .empty-shelf-illustration SVG"
            assert empty_check["svgDashedPaths"] >= 4, f"Ghost bookshelf should have dashed ghost books, found {empty_check['svgDashedPaths']}"
            assert empty_check["titleText"] == "Your Library is Waiting", f"Unexpected empty-title: {empty_check['titleText']}"
            assert "A calm place for your books" in empty_check["subtitleText"], f"Subtitle text mismatch: {empty_check['subtitleText']}"
            assert empty_check["btnExists"], "btn-empty-add element missing!"
            assert empty_check["btnText"] == "+ Add Your First Book", f"Button text mismatch: {empty_check['btnText']}"
            assert "empty-btn-add" in empty_check["btnClass"], f"Button class missing empty-btn-add: {empty_check['btnClass']}"
            assert "EPUB, PDF, MOBI, FB2, CBZ, and TXT" in empty_check["hintText"], f"Formats hint mismatch: {empty_check['hintText']}"

            # Verify #btn-empty-add click handler delegates to fileInput.click()
            click_delegation = ws_client.eval_js("""
                (() => {
                    let clicked = false;
                    const fileInput = document.getElementById('file-import-input');
                    const originalClick = fileInput.click;
                    fileInput.click = () => { clicked = true; };

                    document.getElementById('btn-empty-add').click();
                    fileInput.click = originalClick; // restore

                    return clicked;
                })()
            """)
            assert click_delegation, "#btn-empty-add click failed to trigger file input click!"

            # Restore 1 book in 'all' view and verify empty state disappears
            restore_res = ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    books[0].is_deleted = 0;
                    window.db.saveBooks(books);
                    window.app.renderLibrary();

                    return {
                        emptyVis: document.getElementById('empty-state').style.display,
                        gridVis: document.getElementById('grid-view').style.display,
                        cardCount: document.querySelectorAll('#grid-view .book-card').length
                    };
                })()
            """)
            assert restore_res["emptyVis"] == "none", f"Empty state not hidden after restoring book: {restore_res['emptyVis']}"
            assert restore_res["gridVis"] == "flex", f"Grid view should be flex"
            assert restore_res["cardCount"] == 1, f"Expected 1 card rendered, got {restore_res['cardCount']}"

        test("TC-M2-03", "Empty State Architecture & Interaction Resilience", t_empty_state_architecture)

        # ----------------------------------------------------------------------
        # TC-M2-04: Format Filtering Combined with Search Query and View Modes (Grid vs Table)
        # ----------------------------------------------------------------------
        def t_format_filter_with_search_and_views():
            # Seed 3 distinct books for search & format matrix
            ws_client.eval_js("""
                (() => {
                    localStorage.clear();
                    window.db.init();

                    // Clear any previous active filter
                    const allEl = document.querySelector('.nav-item[data-category="all"]');
                    allEl.click();

                    const books = window.db.getBooks();
                    // Mark all existing deleted so only our 3 test books are active
                    books.forEach(b => b.is_deleted = 1);
                    books.unshift({ id: "q1", title: "Quantum Physics in Python", author: "Richard Feynman", format: "EPUB", is_deleted: 0 });
                    books.unshift({ id: "q2", title: "Quantum Mechanics Reference", author: "Niels Bohr", format: "PDF", is_deleted: 0 });
                    books.unshift({ id: "q3", title: "Classical Mechanics", author: "Isaac Newton", format: "EPUB", is_deleted: 0 });
                    window.db.saveBooks(books);

                    window.app.renderLibrary();
                })()
            """)

            # 1. Select EPUB format filter (q1, q3)
            ws_client.eval_js("document.querySelector('.nav-item[data-format=\"EPUB\"]').click();")
            epub_check = ws_client.eval_js("""
                (() => {
                    const expectedEpubs = window.db.getBooks().filter(b => !b.is_deleted && b.format === "EPUB").length;
                    const rendered = document.querySelectorAll('#grid-view .book-card').length;
                    return { expectedEpubs, rendered };
                })()
            """)
            assert epub_check["rendered"] == 2, f"Expected 2 EPUB cards, got {epub_check['rendered']}"

            # 2. Add search query "Quantum" -> only EPUB + Quantum matches (q1)
            ws_client.eval_js("""
                (() => {
                    const searchInput = document.getElementById('library-search');
                    searchInput.value = "Quantum";
                    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                })()
            """)
            conjoint_check = ws_client.eval_js("""
                (() => {
                    const rendered = Array.from(document.querySelectorAll('#grid-view .book-card'));
                    const titles = rendered.map(c => c.querySelector('.card-title') ? c.querySelector('.card-title').textContent : "");
                    return {
                        count: rendered.length,
                        titles: titles
                    };
                })()
            """)
            assert conjoint_check["count"] == 1, f"Expected 1 book for EPUB + Quantum, got {conjoint_check['count']}"
            assert "Quantum Physics in Python" in conjoint_check["titles"][0], f"Unexpected book title: {conjoint_check['titles']}"

            # 3. Switch to Table View mode (#btn-view-table)
            ws_client.eval_js("document.getElementById('btn-view-table').click();")
            view_state = ws_client.eval_js("""
                (() => ({
                    currentViewMode: window.app.currentViewMode,
                    gridDisplay: document.getElementById('grid-view').style.display,
                    tableDisplay: document.getElementById('table-view').style.display,
                    tableRows: document.querySelectorAll('#table-body tr').length,
                    firstRowTitle: document.querySelector('#table-body tr td') ? document.querySelector('#table-body tr td').textContent : null
                }))()
            """)
            assert view_state["currentViewMode"] == "table"
            assert view_state["gridDisplay"] == "none"
            assert view_state["tableDisplay"] == "table"
            assert view_state["tableRows"] == 1, f"Table rows mismatch: {view_state['tableRows']}"
            assert "Quantum Physics" in view_state["firstRowTitle"]

            # 4. Clear search query while in Table View -> should show both EPUBs in table
            ws_client.eval_js("""
                (() => {
                    const searchInput = document.getElementById('library-search');
                    searchInput.value = "";
                    searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                })()
            """)
            table_all_epub = ws_client.eval_js("""
                (() => {
                    const expectedEpubs = window.db.getBooks().filter(b => !b.is_deleted && b.format === "EPUB").length;
                    const rows = document.querySelectorAll('#table-body tr').length;
                    return { expectedEpubs, rows };
                })()
            """)
            assert table_all_epub["rows"] == 2, f"Table rows mismatch: {table_all_epub['rows']} != 2"

            # Restore grid view
            ws_client.eval_js("document.getElementById('btn-view-grid').click();")

        test("TC-M2-04", "Format Filtering Combined with Search Query and View Modes (Grid vs Table)", t_format_filter_with_search_and_views)

        # ----------------------------------------------------------------------
        # TC-M2-05: Milestone 1 Feature Non-Regression in M2 Context
        # ----------------------------------------------------------------------
        def t_m1_non_regression():
            # Ingest a test book and open it
            ws_client.eval_js("""
                (() => {
                    localStorage.clear();
                    window.db.init();

                    const allEl = document.querySelector('.nav-item[data-category="all"]');
                    allEl.click();

                    window.db.addBook({
                        title: "M1 Regression Test Volume",
                        author: "Author Folio",
                        format: "EPUB",
                        content: "Chapter 1: Resilience Testing.\\n\\nParagraph one for annotation testing.\\n\\nParagraph two for margin zone testing."
                    });
                    const target = window.db.getBooks()[0];
                    window.app.openBook(target);
                })()
            """)
            active_id = ws_client.eval_js("window.app.activeBook.id")

            # 1. Add Bookmark, Clear with Modal & Undo Toast
            ws_client.eval_js(f"""
                window.db.addBookmark({{ book_id: "{active_id}", chapter_index: 0, label: "BM Regression" }});
            """)
            assert ws_client.eval_js(f'window.db.getBookmarks("{active_id}").length') == 1

            # Click Clear Bookmarks -> modal opens
            ws_client.eval_js("document.getElementById('btn-clear-all-bookmarks').click();")
            modal_vis = ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'flex'")
            assert modal_vis, "Confirmation modal did not show"

            # Proceed -> cleared & toast displays
            ws_client.eval_js("document.getElementById('btn-confirm-proceed').click();")
            assert ws_client.eval_js(f'window.db.getBookmarks("{active_id}").length') == 0
            toast_vis = ws_client.eval_js("document.getElementById('undo-toast').style.display === 'flex'")
            assert toast_vis, "Undo toast did not show"

            # Click Undo -> restored
            ws_client.eval_js("document.getElementById('btn-undo-action').click();")
            assert ws_client.eval_js(f'window.db.getBookmarks("{active_id}").length') == 1
            assert ws_client.eval_js("document.getElementById('undo-toast').style.display === 'none'")

            # 2. Check Swatch Buttons Aria-labels
            swatch_labels = ws_client.eval_js("""
                Array.from(document.querySelectorAll('.swatch-btn')).map(b => b.getAttribute('aria-label'))
            """)
            assert "Highlight in Yellow" in swatch_labels
            assert "Highlight in Green" in swatch_labels
            assert "Highlight in Cyan" in swatch_labels
            assert "Highlight in Pink" in swatch_labels

            # 3. Check Margin Zones Role and Aria-label
            zp_aria = ws_client.eval_js("document.getElementById('zone-prev').getAttribute('aria-label')")
            zn_aria = ws_client.eval_js("document.getElementById('zone-next').getAttribute('aria-label')")
            assert zp_aria == "Previous Page", f"zone-prev aria-label: {zp_aria}"
            assert zn_aria == "Next Page", f"zone-next aria-label: {zn_aria}"

            # Close reader
            ws_client.eval_js("window.app.closeReader();")

            # 4. Drag feedback: .drag-over toggling on #library-content
            drag_res = ws_client.eval_js("""
                (() => {
                    const lc = document.getElementById('library-content');
                    window.dispatchEvent(new Event('dragenter'));
                    const hasDrag = lc.classList.contains('drag-over');
                    window.dispatchEvent(new Event('dragleave'));
                    const clearedDrag = !lc.classList.contains('drag-over');
                    return { hasDrag, clearedDrag };
                })()
            """)
            assert drag_res["hasDrag"], ".drag-over not added on dragenter"
            assert drag_res["clearedDrag"], ".drag-over not removed on dragleave"

        test("TC-M2-05", "Milestone 1 Feature Non-Regression in M2 Context", t_m1_non_regression)

        print("=" * 76)
        passed = sum(1 for _, _, res, _ in results if res == "PASS")
        total = len(results)
        print(f"  CHALLENGER M2 SUITE SUMMARY: {passed}/{total} Passed")
        print("=" * 76)

        return passed == total

    finally:
        if ws_client:
            ws_client.close()
        proc.terminate()


if __name__ == "__main__":
    success = run_empirical_m2_suite()
    sys.exit(0 if success else 1)
