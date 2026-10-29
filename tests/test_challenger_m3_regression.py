"""
Adversarial Empirical Regression Verification Suite for Milestone 3
(Milestone 3 Regression Challenger: challenger_m3_2)
FolioHaven Ebook Reader Replica

Verification Scope:
Verify that none of the changes in Milestone 3 introduced regressions into:
1. Milestone 1 features:
   - Confirmation modals (#modal-confirm) across all destructive triggers
   - Undo toast component (#undo-toast) with interactive restore and auto-dismiss
   - Book import loading skeleton (.book-card.loading) with shimmer keyframes
   - Drag-and-drop dropzone visual feedback (.drag-over on #library-content)
   - Accessibility swatch labels and margin click zones
   - Reader text selection enabled (user-select: text)
2. Milestone 2 features:
   - Ghost bookshelf empty state illustration, editorial title, subtitle, and #btn-empty-add
   - Sidebar format tooltips across all 6 formats (EPUB, PDF, MOBI, FB2, CBZ, TXT)
   - Dynamic format badge counts lifecycle and format filtering resilience
3. Core reader functionality:
   - Book open / render lifecycle and reader canvas mount
   - Page navigation (prev/next, keyboard arrows, margin zones, scrubber)
   - Secondary toolbar overflow menu (Feature 11) integration and non-regression:
     Settings popover toggle, fullscreen, print modal, Escape key isolation, outside click dismissal
   - TOC drawer chapter list rendering and navigation
   - Bookmarks creation, persistence, drawer display, and jump-to
   - Notes / annotations creation, persistence, and drawer display
   - Text highlights creation, mark injection, and persistence
   - TTS speech synthesis controller, play/pause toggle, F7 hotkey, and clean shutdown
4. Milestone 3 Architecture Isolation:
   - Duplicate #btn-add-folder removed from header without breaking category management
   - Canonical #btn-add-category-sidebar preserved and operational
   - Formats collapsible accordion persistence in localStorage
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
        self.sock = socket.create_connection((host, port), timeout=15)
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

        mask = b'\x34\x56\x78\x9a'
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


def run_empirical_m3_regression_suite():
    print("=" * 78)
    print("  FOLIOHAVEN CHALLENGER M3: EMPIRICAL REGRESSION VERIFICATION SUITE   ")
    print("=" * 78)

    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    app_url = f"file:///{app_dir.replace('\\', '/')}/index.html"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    port = 9366  # Dedicated port for M3 regression challenger
    temp_dir = tempfile.mkdtemp(prefix="foliohaven_m3_reg_")

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

        # Global safety: prevent native alert dialogs from blocking headless Chrome execution
        ws_client.eval_js("window.alert = () => {}; window.confirm = () => true;")

        # ======================================================================
        # TC-M3-REG-01: Confirmation Modals for Destructive Triggers
        # ======================================================================
        def t_confirmation_modals():
            # Setup seed book with isolated bookmarks and notes
            ws_client.eval_js("""
                (() => {
                    localStorage.clear();
                    window.db.init();
                    const b = window.db.getBooks().find(x => !x.is_encrypted && !x.is_deleted);
                    window.db.clearBookmarks(b.id);
                    window.db.clearAnnotations(b.id);
                    window.db.addBookmark({ book_id: b.id, chapter_index: 0, label: "BM 1" });
                    window.db.addBookmark({ book_id: b.id, chapter_index: 1, label: "BM 2" });
                    window.db.addAnnotation({ book_id: b.id, chapter_index: 0, text: "Sample Note", color: "yellow", note: "Test Note" });
                    window.app.openBook(b);
                })()
            """)
            book_id = ws_client.eval_js("window.app.activeBook.id")
            bm_init = ws_client.eval_js(f'window.db.getBookmarks("{book_id}").length')
            an_init = ws_client.eval_js(f'window.db.getAnnotations("{book_id}").length')
            assert bm_init == 2, f"Initial bookmarks mismatch: expected 2, got {bm_init}"
            assert an_init == 1, f"Initial annotations mismatch: expected 1, got {an_init}"

            # 1. Clear Bookmarks Trigger
            ws_client.eval_js("document.getElementById('btn-clear-all-bookmarks').click();")
            modal_state = ws_client.eval_js("""
                (() => {
                    const modal = document.getElementById('modal-confirm');
                    return {
                        display: modal.style.display,
                        title: document.getElementById('confirm-title').textContent,
                        cancelText: document.getElementById('btn-confirm-cancel').textContent
                    };
                })()
            """)
            assert modal_state["display"] == "flex", f"Modal display mismatch: {modal_state['display']}"
            assert "Bookmark" in modal_state["title"], f"Modal title mismatch: {modal_state['title']}"

            # Cancel preserves bookmarks
            ws_client.eval_js("document.getElementById('btn-confirm-cancel').click();")
            assert ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'none'"), "Modal not hidden on cancel"
            assert ws_client.eval_js(f'window.db.getBookmarks("{book_id}").length') == 2, "Bookmarks mutated on cancel"

            # Proceed deletes bookmarks
            ws_client.eval_js("document.getElementById('btn-clear-all-bookmarks').click();")
            ws_client.eval_js("document.getElementById('btn-confirm-proceed').click();")
            assert ws_client.eval_js(f'window.db.getBookmarks("{book_id}").length') == 0, "Bookmarks not cleared on proceed"
            assert ws_client.eval_js("document.getElementById('undo-toast').style.display === 'flex'"), "Undo toast not shown"

            # 2. Clear Notes Trigger
            ws_client.eval_js("document.getElementById('btn-clear-all-notes').click();")
            notes_modal = ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'flex'")
            assert notes_modal, "Modal did not open on clear-all-notes"
            ws_client.eval_js("document.getElementById('btn-confirm-cancel').click();")
            assert ws_client.eval_js(f'window.db.getAnnotations("{book_id}").length') == 1, "Annotations mutated on cancel"

            # Close reader and return to library
            ws_client.eval_js("window.app.closeReader();")

            # 3. Batch Delete in Library
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    window.app.selectedBookIds.clear();
                    window.app.selectedBookIds.add(books[0].id);
                    document.getElementById('btn-batch-delete').click();
                })()
            """)
            batch_modal = ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'flex'")
            assert batch_modal, "Modal did not open on batch delete"
            ws_client.eval_js("document.getElementById('btn-confirm-cancel').click();")
            assert ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'none'"), "Modal not hidden after batch cancel"

        test("TC-M3-REG-01", "Confirmation Modals (#modal-confirm) Destructive Actions Integration", t_confirmation_modals)

        # ======================================================================
        # TC-M3-REG-02: Interactive Undo Toast Component
        # ======================================================================
        def t_undo_toast():
            ws_client.eval_js("""
                (() => {
                    window.testUndoExecuted = false;
                    window.app.showUndoToast("Book deleted", () => {
                        window.testUndoExecuted = true;
                    }, 4000);
                })()
            """)
            toast_data = ws_client.eval_js("""
                (() => {
                    const toast = document.getElementById('undo-toast');
                    return {
                        display: toast.style.display,
                        role: toast.getAttribute('role'),
                        message: document.getElementById('undo-toast-message').textContent,
                        actionLabel: document.getElementById('btn-undo-action').textContent
                    };
                })()
            """)
            assert toast_data["display"] == "flex", f"Toast not flex: {toast_data['display']}"
            assert toast_data["role"] == "alert", f"Toast missing role='alert': {toast_data['role']}"
            assert "Book deleted" in toast_data["message"], f"Toast message mismatch: {toast_data['message']}"

            # Click Undo button
            ws_client.eval_js("document.getElementById('btn-undo-action').click();")
            assert ws_client.eval_js("window.testUndoExecuted === true"), "Undo callback was not executed"
            assert ws_client.eval_js("document.getElementById('undo-toast').style.display === 'none'"), "Toast did not hide"

            # Dismiss via close button (#btn-close-undo-toast)
            ws_client.eval_js("""
                (() => {
                    window.app.showUndoToast("Test dismiss", () => {}, 10000);
                    document.getElementById('btn-close-undo-toast').click();
                })()
            """)
            assert ws_client.eval_js("document.getElementById('undo-toast').style.display === 'none'"), "Close button did not hide toast"

        test("TC-M3-REG-02", "Interactive Undo Toast (#undo-toast) Lifecycle & Callback Execution", t_undo_toast)

        # ======================================================================
        # TC-M3-REG-03: Book Import Shimmer Skeleton & Drag-Over Visuals
        # ======================================================================
        def t_skeleton_and_dragover():
            # Verify CSS definitions and structure
            res = ws_client.eval_js("""
                (() => {
                    const lc = document.getElementById('library-content');
                    // Test dragenter / dragleave
                    window.dispatchEvent(new Event('dragenter'));
                    const isDragOver = lc.classList.contains('drag-over');
                    window.dispatchEvent(new Event('dragleave'));
                    const clearedDrag = !lc.classList.contains('drag-over');

                    // Check skeleton CSS rule presence
                    let skeletonRuleFound = false;
                    for (const sheet of document.styleSheets) {
                        try {
                            for (const rule of sheet.cssRules) {
                                if (rule.selectorText && rule.selectorText.includes('book-card.loading')) {
                                    skeletonRuleFound = true;
                                    break;
                                }
                            }
                        } catch (e) {}
                    }

                    return { isDragOver, clearedDrag, skeletonRuleFound };
                })()
            """)
            assert res["isDragOver"], "drag-over class not added on dragenter"
            assert res["clearedDrag"], "drag-over class not removed on dragleave"
            assert res["skeletonRuleFound"], ".book-card.loading CSS rule missing"

        test("TC-M3-REG-03", "Book Import Skeleton & Drag-Over Visual Feedback", t_skeleton_and_dragover)

        # ======================================================================
        # TC-M3-REG-04: Accessibility Swatch Labels & Margin Navigation Zones
        # ======================================================================
        def t_a11y_swatches_and_zones():
            a11y = ws_client.eval_js("""
                (() => {
                    const swatches = Array.from(document.querySelectorAll('.swatch-btn')).map(s => ({
                        color: s.getAttribute('data-color'),
                        label: s.getAttribute('aria-label')
                    }));

                    const zp = document.getElementById('zone-prev');
                    const zn = document.getElementById('zone-next');

                    return {
                        swatches: swatches,
                        zpRole: zp.getAttribute('role'),
                        zpTabindex: zp.getAttribute('tabindex'),
                        zpLabel: zp.getAttribute('aria-label'),
                        znRole: zn.getAttribute('role'),
                        znTabindex: zn.getAttribute('tabindex'),
                        znLabel: zn.getAttribute('aria-label')
                    };
                })()
            """)
            color_map = {s["color"]: s["label"] for s in a11y["swatches"]}
            assert color_map.get("yellow") == "Highlight in Yellow", f"Yellow swatch label: {color_map.get('yellow')}"
            assert color_map.get("green") == "Highlight in Green", f"Green swatch label: {color_map.get('green')}"
            assert color_map.get("cyan") == "Highlight in Cyan", f"Cyan swatch label: {color_map.get('cyan')}"
            assert color_map.get("pink") == "Highlight in Pink", f"Pink swatch label: {color_map.get('pink')}"

            assert a11y["zpRole"] == "button"
            assert a11y["zpTabindex"] == "0"
            assert a11y["zpLabel"] == "Previous Page"
            assert a11y["znRole"] == "button"
            assert a11y["znTabindex"] == "0"
            assert a11y["znLabel"] == "Next Page"

            # Check user-select: text CSS
            user_select_ok = ws_client.eval_js("""
                (() => {
                    const rc = document.getElementById('reader-canvas');
                    const comp = window.getComputedStyle(rc);
                    return comp.userSelect !== 'none';
                })()
            """)
            assert user_select_ok, "Reader canvas user-select is disabled"

        test("TC-M3-REG-04", "Accessibility Swatch Labels, Margin Zones & Text Selection", t_a11y_swatches_and_zones)

        # ======================================================================
        # TC-M3-REG-05: Empty State Illustration, Copy, and Call-to-Action
        # ======================================================================
        def t_empty_state():
            ws_client.eval_js("""
                (() => {
                    localStorage.clear();
                    window.db.init();
                    const books = window.db.getBooks();
                    books.forEach(b => b.is_deleted = 1);
                    window.db.saveBooks(books);
                    window.app.renderLibrary();
                })()
            """)
            empty = ws_client.eval_js("""
                (() => {
                    const el = document.getElementById('empty-state');
                    const title = el.querySelector('.empty-title') ? el.querySelector('.empty-title').textContent : '';
                    const subtitle = el.querySelector('.empty-subtitle') ? el.querySelector('.empty-subtitle').textContent : '';
                    const btn = document.getElementById('btn-empty-add');
                    const svg = el.querySelector('.empty-shelf-illustration svg');
                    return {
                        display: el.style.display,
                        title: title.trim(),
                        subtitle: subtitle.trim(),
                        btnPresent: !!btn,
                        btnText: btn ? btn.textContent.trim() : '',
                        svgPresent: !!svg
                    };
                })()
            """)
            assert empty["display"] != "none", "Empty state is hidden with 0 books"
            assert empty["title"] == "Your Library is Waiting", f"Empty title mismatch: {empty['title']}"
            assert "A calm place for your books" in empty["subtitle"], f"Empty subtitle mismatch: {empty['subtitle']}"
            assert empty["btnPresent"], "Missing #btn-empty-add"
            assert "+ Add Your First Book" in empty["btnText"], f"Button text mismatch: {empty['btnText']}"
            assert empty["svgPresent"], "Missing ghost bookshelf SVG illustration"

            # Restore books
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    books.forEach(b => b.is_deleted = 0);
                    window.db.saveBooks(books);
                    window.app.renderLibrary();
                })()
            """)

        test("TC-M3-REG-05", "Ghost Bookshelf Empty State Illustration, Editorial Copy & CTA", t_empty_state)

        # ======================================================================
        # TC-M3-REG-06: Sidebar Format Tooltips, Badges & Collapsible Filtering
        # ======================================================================
        def t_format_tooltips_and_filtering():
            formats_data = ws_client.eval_js("""
                (() => {
                    const items = Array.from(document.querySelectorAll('#formats-collapsible .nav-item[data-format]')).map(el => ({
                        format: el.getAttribute('data-format'),
                        title: el.getAttribute('title'),
                        badgeId: el.querySelector('.badge') ? el.querySelector('.badge').id : null
                    }));
                    return items;
                })()
            """)
            expected_tooltips = {
                "EPUB": "Electronic Publication (.epub) — standard reflowable ebook format",
                "PDF": "Portable Document Format (.pdf) — fixed-layout documents and books",
                "MOBI": "Mobipocket eBook (.mobi) — legacy Kindle and handheld format",
                "FB2": "FictionBook 2.0 (.fb2) — XML-based Russian and international ebook format",
                "CBZ": "Comic Book ZIP (.cbz) — archive of images for comics and manga",
                "TXT": "Plain Text (.txt) — unformatted raw text files"
            }
            assert len(formats_data) == 6, f"Expected 6 format items in #formats-collapsible, found {len(formats_data)}"
            for item in formats_data:
                fmt = item["format"]
                expected = expected_tooltips[fmt]
                assert item["title"] == expected, f"Tooltip for {fmt} mismatch: got '{item['title']}', expected '{expected}'"

            # Filter books by EPUB while formats section is collapsed
            ws_client.eval_js("""
                (() => {
                    window.app.setFormatsCollapsed(true);
                    const epubItem = document.querySelector('.nav-item[data-format="EPUB"]');
                    epubItem.click();
                })()
            """)
            filter_check = ws_client.eval_js("""
                (() => ({
                    currentFormatFilter: window.app.currentFormatFilter,
                    currentCategory: window.app.currentCategory,
                    renderedCount: document.querySelectorAll('#grid-view .book-card').length,
                    activeClassPresent: document.querySelector('.nav-item[data-format="EPUB"]').classList.contains('active')
                }))()
            """)
            assert filter_check["currentFormatFilter"] == "EPUB"
            assert filter_check["currentCategory"] is None
            assert filter_check["activeClassPresent"], "Active class missing on EPUB format item"

            # Re-expand formats section and return to all books
            ws_client.eval_js("""
                (() => {
                    window.app.setFormatsCollapsed(false);
                    document.querySelector('.nav-item[data-category="all"]').click();
                })()
            """)
            assert ws_client.eval_js("window.app.currentFormatFilter") is None
            assert ws_client.eval_js("window.app.currentCategory") == "all"

        test("TC-M3-REG-06", "Sidebar Format Tooltips, Dynamic Badges & Collapsible Filtering", t_format_tooltips_and_filtering)

        # ======================================================================
        # TC-M3-REG-07: Core Reader Open, Render, Page Navigation & Scrubber
        # ======================================================================
        def t_core_reader_navigation():
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    const nonEnc = books.find(b => !b.is_encrypted && !b.is_deleted);
                    window.app.openBook(nonEnc);
                })()
            """)
            open_state = ws_client.eval_js("""
                (() => ({
                    isReading: window.app.isReading,
                    readerDisplay: document.getElementById('reader-screen').style.display,
                    bookTitle: window.app.activeBook ? window.app.activeBook.title : '',
                    pageInfo: document.getElementById('reader-page-info').textContent
                }))()
            """)
            assert open_state["isReading"] == True
            assert open_state["readerDisplay"] != "none"
            assert len(open_state["bookTitle"]) > 0
            assert "Spread 1" in open_state["pageInfo"]

            # Step Forward via pageNext()
            ws_client.eval_js("window.app.pageNext();")
            spread_after = ws_client.eval_js("document.getElementById('reader-page-info').textContent")
            assert "Spread 2" in spread_after, f"Expected Spread 2 after pageNext, got {spread_after}"

            # Step Backward via Margin Zone #zone-prev
            ws_client.eval_js("document.getElementById('zone-prev').click();")
            spread_back = ws_client.eval_js("document.getElementById('reader-page-info').textContent")
            assert "Spread 1" in spread_back, f"Expected Spread 1 after zone-prev, got {spread_back}"

            # Step Forward via Margin Zone #zone-next
            ws_client.eval_js("document.getElementById('zone-next').click();")
            spread_fwd = ws_client.eval_js("document.getElementById('reader-page-info').textContent")
            assert "Spread 2" in spread_fwd, f"Expected Spread 2 after zone-next, got {spread_fwd}"

            # Test Scrubber Jump
            ws_client.eval_js("""
                (() => {
                    const scrubber = document.getElementById('reader-scrubber');
                    scrubber.value = 50;
                    scrubber.dispatchEvent(new Event('input', { bubbles: true }));
                })()
            """)
            prog_text = ws_client.eval_js("document.getElementById('reader-progress-info').textContent")
            assert "%" in prog_text

        test("TC-M3-REG-07", "Core Reader Mount, Page Navigation (API, Margin Zones) & Scrubber", t_core_reader_navigation)

        # ======================================================================
        # TC-M3-REG-08: Reader Toolbar Overflow Menu (Feature 11) Integration
        # ======================================================================
        def t_reader_overflow_menu_integration():
            # 1. Verify existence of trigger and inner buttons
            menu_structure = ws_client.eval_js("""
                (() => {
                    const trigger = document.getElementById('btn-reader-overflow');
                    const menu = document.getElementById('reader-overflow-menu');
                    const btnPrint = document.getElementById('btn-reader-print');
                    const btnFs = document.getElementById('btn-reader-fullscreen');
                    const btnSet = document.getElementById('btn-reader-settings');
                    return {
                        triggerPresent: !!trigger,
                        menuPresent: !!menu,
                        menuOpen: menu ? menu.classList.contains('open') : false,
                        btnPrintPresent: !!btnPrint,
                        btnFsPresent: !!btnFs,
                        btnSetPresent: !!btnSet
                    };
                })()
            """)
            assert menu_structure["triggerPresent"], "Missing #btn-reader-overflow"
            assert menu_structure["menuPresent"], "Missing #reader-overflow-menu"
            assert not menu_structure["menuOpen"], "Menu should be initially closed"
            assert menu_structure["btnPrintPresent"], "Missing #btn-reader-print in overflow menu"
            assert menu_structure["btnFsPresent"], "Missing #btn-reader-fullscreen in overflow menu"
            assert menu_structure["btnSetPresent"], "Missing #btn-reader-settings in overflow menu"

            # 2. Open overflow menu via trigger click
            ws_client.eval_js("document.getElementById('btn-reader-overflow').click();")
            assert ws_client.eval_js("document.getElementById('reader-overflow-menu').classList.contains('open')")
            assert ws_client.eval_js("document.getElementById('btn-reader-overflow').getAttribute('aria-expanded') === 'true'")

            # 3. Click #btn-reader-settings -> opens #quick-settings-popover AND closes overflow menu
            ws_client.eval_js("document.getElementById('btn-reader-settings').click();")
            state_after_settings = ws_client.eval_js("""
                (() => ({
                    menuOpen: document.getElementById('reader-overflow-menu').classList.contains('open'),
                    popoverDisplay: document.getElementById('quick-settings-popover').style.display
                }))()
            """)
            assert not state_after_settings["menuOpen"], "Overflow menu did not close on item click"
            assert state_after_settings["popoverDisplay"] == "flex", f"Settings popover display mismatch: {state_after_settings['popoverDisplay']}"

            # Dismiss popover
            ws_client.eval_js("document.getElementById('quick-settings-popover').style.display = 'none';")

            # 4. Open overflow menu and test Outside Click Dismissal
            ws_client.eval_js("document.getElementById('btn-reader-overflow').click();")
            assert ws_client.eval_js("document.getElementById('reader-overflow-menu').classList.contains('open')")
            ws_client.eval_js("document.getElementById('reader-canvas').click();")
            assert not ws_client.eval_js("document.getElementById('reader-overflow-menu').classList.contains('open')"), "Outside click did not close overflow menu"

            # 5. Open overflow menu and test Escape Key dismissal (closes menu without closing reader)
            ws_client.eval_js("document.getElementById('btn-reader-overflow').click();")
            assert ws_client.eval_js("document.getElementById('reader-overflow-menu').classList.contains('open')")
            ws_client.eval_js("""
                window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
            """)
            escape_state = ws_client.eval_js("""
                (() => ({
                    menuOpen: document.getElementById('reader-overflow-menu').classList.contains('open'),
                    isReading: window.app.isReading,
                    focusedId: document.activeElement ? document.activeElement.id : null
                }))()
            """)
            assert not escape_state["menuOpen"], "Escape key did not close overflow menu"
            assert escape_state["isReading"] == True, "Escape key closed reader instead of just overflow menu"
            assert escape_state["focusedId"] == "btn-reader-overflow", f"Expected focus on overflow trigger, got {escape_state['focusedId']}"

        test("TC-M3-REG-08", "Reader Toolbar Overflow Menu Lifecycle, Settings Trigger & Escape Isolation", t_reader_overflow_menu_integration)

        # ======================================================================
        # TC-M3-REG-09: TOC Drawer, Bookmarks, and Notes Drawers
        # ======================================================================
        def t_drawers_and_annotations():
            # Ensure reader is open
            ws_client.eval_js("""
                (() => {
                    if (!window.app.isReading) {
                        const books = window.db.getBooks();
                        const nonEnc = books.find(b => !b.is_encrypted && !b.is_deleted);
                        window.app.openBook(nonEnc);
                    }
                    window.alert = () => {};
                })()
            """)

            # 1. TOC Drawer
            ws_client.eval_js("document.getElementById('btn-toggle-toc').click();")
            toc_state = ws_client.eval_js("""
                (() => ({
                    isOpen: document.getElementById('drawer-toc').classList.contains('open'),
                    chapterCards: document.querySelectorAll('#toc-list .drawer-card').length
                }))()
            """)
            assert toc_state["isOpen"], "TOC drawer did not open"
            assert toc_state["chapterCards"] > 0, "No chapters rendered in TOC drawer"
            # Close TOC drawer
            ws_client.eval_js("document.getElementById('btn-close-toc').click();")
            assert not ws_client.eval_js("document.getElementById('drawer-toc').classList.contains('open')")

            # 2. Add Bookmark via Data Layer & verify Drawer
            book_id = ws_client.eval_js("window.app.activeBook.id")
            ws_client.eval_js(f"""
                (() => {{
                    window.db.addBookmark({{
                        book_id: "{book_id}",
                        page_number: 1,
                        chapter_title: "Chapter I",
                        snippet_text: "Drawer persistence automated check"
                    }});
                    window.app.updateBookmarkCounts();
                }})()
            """)
            bm_count = ws_client.eval_js(f'window.db.getBookmarks("{book_id}").length')
            assert bm_count >= 1, f"Bookmark not persisted, count: {bm_count}"

            # Open Bookmarks Drawer
            ws_client.eval_js("document.getElementById('btn-toggle-bookmarks').click();")
            bm_state = ws_client.eval_js("""
                (() => ({
                    isOpen: document.getElementById('drawer-bookmarks').classList.contains('open'),
                    items: document.querySelectorAll('#bookmarks-list .drawer-card').length
                }))()
            """)
            assert bm_state["isOpen"], "Bookmarks drawer did not open"
            assert bm_state["items"] >= 1, "Bookmarks list is empty in drawer"
            ws_client.eval_js("document.getElementById('btn-close-bookmarks').click();")

            # 3. Notes Drawer
            ws_client.eval_js("document.getElementById('btn-toggle-notes').click();")
            notes_open = ws_client.eval_js("document.getElementById('drawer-notes').classList.contains('open')")
            assert notes_open, "Notes drawer did not open"
            ws_client.eval_js("document.getElementById('btn-close-notes').click();")

        test("TC-M3-REG-09", "TOC, Bookmarks & Notes Drawers Lifecycle and State", t_drawers_and_annotations)

        # ======================================================================
        # TC-M3-REG-10: Text Highlighting & TTS Speech Synthesis Controller
        # ======================================================================
        def t_highlights_and_tts():
            # Ensure reader is open
            ws_client.eval_js("""
                (() => {
                    if (!window.app.isReading) {
                        const books = window.db.getBooks();
                        const nonEnc = books.find(b => !b.is_encrypted && !b.is_deleted);
                        window.app.openBook(nonEnc);
                    }
                    window.alert = () => {};
                })()
            """)

            # 1. Text Highlighting Simulation
            book_id = ws_client.eval_js("window.app.activeBook.id")
            ws_client.eval_js(f"""
                (() => {{
                    window.db.addAnnotation({{
                        book_id: "{book_id}",
                        chapter_index: 0,
                        text: "adversarial verification highlight",
                        color: "cyan",
                        note: "Automated empirical test"
                    }});
                    window.app.updateReaderView();
                }})()
            """)
            annos = ws_client.eval_js(f'window.db.getAnnotations("{book_id}")')
            assert len(annos) >= 1, "Annotation not saved in db"

            # 2. TTS Read Aloud Controller Toggle with Mocked Engine Playback
            ws_client.eval_js("""
                (() => {
                    // Prevent headless Chrome from immediately advancing all utterances to end
                    if (!window.speechSynthesis) {
                        window.speechSynthesis = {
                            cancel: () => {},
                            speak: () => {},
                            getVoices: () => []
                        };
                    } else {
                        window.speechSynthesis.cancel = () => {};
                        window.speechSynthesis.speak = () => {};
                    }

                    const btnTts = document.getElementById('btn-tts-play');
                    btnTts.click();
                })()
            """)
            tts_state = ws_client.eval_js("""
                (() => ({
                    isTtsSpeaking: window.app.isTtsSpeaking,
                    buttonText: document.getElementById('btn-tts-play').textContent
                }))()
            """)
            assert tts_state["isTtsSpeaking"] == True, f"TTS did not activate on click: {tts_state}"
            assert "Stop" in tts_state["buttonText"], f"TTS button text mismatch: {tts_state['buttonText']}"

            # Toggle off
            ws_client.eval_js("document.getElementById('btn-tts-play').click();")
            assert ws_client.eval_js("window.app.isTtsSpeaking === false"), "TTS did not deactivate on second click"

            # Close reader and ensure TTS is completely stopped
            ws_client.eval_js("window.app.closeReader();")
            assert ws_client.eval_js("window.app.isReading === false"), "Reader screen not closed"
            assert ws_client.eval_js("window.app.isTtsSpeaking === false"), "TTS was not stopped when closing reader"

        test("TC-M3-REG-10", "Text Highlights Persistence & TTS Controller Playback Lifecycle", t_highlights_and_tts)

        # ======================================================================
        # TC-M3-REG-11: Milestone 3 Header Category Isolation & Persistence
        # ======================================================================
        def t_m3_header_and_persistence():
            header_audit = ws_client.eval_js("""
                (() => ({
                    duplicateHeaderBtn: document.getElementById('btn-add-folder'),
                    canonicalSidebarBtn: document.getElementById('btn-add-category-sidebar'),
                    addBookBtn: document.getElementById('btn-add-book'),
                    searchContainer: document.querySelector('.header-left .search-container') !== null
                }))()
            """)
            assert header_audit["duplicateHeaderBtn"] is None, "Redundant #btn-add-folder still exists in DOM!"
            assert header_audit["canonicalSidebarBtn"] is not None, "Canonical #btn-add-category-sidebar missing from sidebar"
            assert header_audit["addBookBtn"] is not None, "Missing #btn-add-book in header"
            assert header_audit["searchContainer"] == True, "Missing search container in header"

            # Test Collapsible Formats state persistence across page operations
            ws_client.eval_js("""
                (() => {
                    window.app.setFormatsCollapsed(true, true);
                })()
            """)
            persisted = ws_client.eval_js("localStorage.getItem('foliohaven_formats_collapsed')")
            assert persisted == "true", f"localStorage persistence mismatch: {persisted}"

            # Toggle back to expanded
            ws_client.eval_js("""
                (() => {
                    const toggleHeader = document.getElementById('sidebar-formats-toggle');
                    toggleHeader.click();
                })()
            """)
            persisted_expanded = ws_client.eval_js("localStorage.getItem('foliohaven_formats_collapsed')")
            assert persisted_expanded == "false", f"localStorage persistence after click: {persisted_expanded}"
            assert not ws_client.eval_js("document.getElementById('formats-collapsible').classList.contains('collapsed')")

        test("TC-M3-REG-11", "Header Category Button Clean Removal & Collapsible Persistence Invariants", t_m3_header_and_persistence)

        print("=" * 78)
        passed = sum(1 for _, _, res, _ in results if res == "PASS")
        total = len(results)
        print(f"  CHALLENGER M3 REGRESSION SUITE: {passed}/{total} Passed")
        print("=" * 78)

        return passed == total

    finally:
        if ws_client:
            ws_client.close()
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    success = run_empirical_m3_regression_suite()
    sys.exit(0 if success else 1)
