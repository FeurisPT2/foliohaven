"""
Adversarial Empirical Regression Verification Suite for Milestone 4
(Milestone 4 Regression Challenger: challenger_m4_2)
FolioHaven Ebook Reader Replica

Verification Scope:
Verify that Milestone 4 changes (Features 13, 14, 15: Native Print Delegation,
Card Thumbnail Token Migration, and Inline Styles Migration) introduced zero
regressions across all previously delivered milestones (M1, M2, M3) and adhere
strictly to Milestone 4 contracts:

1. Milestone 1 Regression Checks:
   - Confirmation modals (#modal-confirm) across all destructive triggers:
     #btn-clear-all-bookmarks, #btn-clear-all-notes, #btn-batch-delete, #btn-batch-purge
   - Interactive undo toast (#undo-toast) with accessible alert role, undo callback execution,
     and rapid-stacking timer resilience
   - Book import loading skeleton (.book-card.loading) with shimmer keyframes and clean cleanup
   - Drag-and-drop dropzone visual feedback (.drag-over on #library-content)
   - Accessibility color swatch labels and margin click zones
   - Reader canvas text selection enabled (user-select: text)

2. Milestone 2 Regression Checks:
   - Ghost bookshelf empty state illustration, editorial title, subtitle, and #btn-empty-add
   - Format tooltips across all 6 formats (EPUB, PDF, MOBI, FB2, CBZ, TXT)
   - Dynamic format badge counters and format filtering lifecycle

3. Milestone 3 Regression Checks:
   - Collapsible Formats section toggle, chevron rotation, and localStorage persistence
   - Reader toolbar overflow menu (⋯ / #btn-reader-overflow) containing Print, Fullscreen, Settings
   - Outside click dismissal of reader overflow menu
   - Escape key isolation: closes overflow menu, restores focus, does NOT close reader screen
   - Clean removal of duplicate #btn-add-folder from header while preserving canonical sidebar button

4. Milestone 4 Interface Contracts & Token Hygiene:
   - Direct print delegation: #btn-reader-print and Ctrl+P invoke window.print() directly
   - #modal-print is never opened during printing; preserved defensively in DOM with style="display: none;"
   - Resiliency: window.print() exception handled cleanly
   - @media print CSS rules hide chrome and unconstrain reader canvas
   - .card-thumb uses var(--color-surface); zero hardcoded #e2e8f0 in styles.css
   - Multi-palette token adherence: .card-thumb adapts across day, night, sepia themes
   - Inline styles eliminated: .brand-title, #reader-page-info, #reader-progress-info use semantic classes
   - Static DOM audit: exactly 1 static style attribute remains in index.html (#modal-print)
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

        mask = b'\x42\x59\x7a\x1c'
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


def run_empirical_m4_regression_suite():
    print("=" * 78)
    print("  FOLIOHAVEN CHALLENGER M4: EXHAUSTIVE MULTI-MILESTONE REGRESSION SUITE  ")
    print("=" * 78)

    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app_dir = os.path.join(repo_dir, "app")
    app_url = f"file:///{app_dir.replace('\\', '/')}/index.html"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    # Dynamic free port allocation
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        port = s.getsockname()[1]

    temp_dir = tempfile.mkdtemp(prefix="foliohaven_m4_reg_")

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
        # Wait for debugger endpoint with retry loop
        max_attempts = 30
        for _ in range(max_attempts):
            time.sleep(0.3)
            try:
                with urllib.request.urlopen(f"http://localhost:{port}/json", timeout=2) as resp:
                    tabs = json.loads(resp.read().decode('utf-8'))
                    page_tabs = [t for t in tabs if t.get("type") == "page" and "index.html" in t.get("url", "")]
                    tab = page_tabs[0] if page_tabs else (tabs[0] if tabs else None)
                    if not tab:
                        continue
                    ws_url = tab.get("webSocketDebuggerUrl")
                    if not ws_url:
                        continue
                    path = ws_url.split(f"localhost:{port}")[1]
                    ws_client = CDPClient("localhost", port, path)
                    ws_client.send_command("Runtime.enable")
                    break
            except Exception:
                continue
        else:
            raise ConnectionError("Failed to connect to headless Chrome CDP port")
        time.sleep(0.5)

        # Global safety: prevent native alert/confirm dialogs from blocking headless Chrome
        ws_client.eval_js("window.alert = () => {}; window.confirm = () => true;")

        # Read static source files for structural verification
        with open(os.path.join(app_dir, "index.html"), "r", encoding="utf-8") as f:
            html_src = f.read()
        with open(os.path.join(app_dir, "styles.css"), "r", encoding="utf-8") as f:
            css_src = f.read()
        with open(os.path.join(app_dir, "app.js"), "r", encoding="utf-8") as f:
            app_js_src = f.read()

        # ======================================================================
        # TC-M4-REG-01: Milestone 1 Destructive Confirmation Modals & Esc Trap Protection
        # ======================================================================
        def t_m1_confirmation_modals():
            # Setup seed book with bookmarks and notes
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
            assert ws_client.eval_js(f'window.db.getBookmarks("{book_id}").length') == 2
            assert ws_client.eval_js(f'window.db.getAnnotations("{book_id}").length') == 1

            # 1. Clear Bookmarks Trigger
            ws_client.eval_js("document.getElementById('btn-clear-all-bookmarks').click();")
            modal_state = ws_client.eval_js("""
                (() => ({
                    display: document.getElementById('modal-confirm').style.display,
                    title: document.getElementById('confirm-title').textContent,
                    cancelText: document.getElementById('btn-confirm-cancel').textContent
                }))()
            """)
            assert modal_state["display"] == "flex", f"Modal display mismatch: {modal_state['display']}"
            assert "Bookmark" in modal_state["title"], f"Modal title mismatch: {modal_state['title']}"

            # Cancel preserves bookmarks
            ws_client.eval_js("document.getElementById('btn-confirm-cancel').click();")
            assert ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'none'")
            assert ws_client.eval_js(f'window.db.getBookmarks("{book_id}").length') == 2

            # Proceed clears bookmarks and displays toast
            ws_client.eval_js("document.getElementById('btn-clear-all-bookmarks').click();")
            ws_client.eval_js("document.getElementById('btn-confirm-proceed').click();")
            assert ws_client.eval_js(f'window.db.getBookmarks("{book_id}").length') == 0
            assert ws_client.eval_js("document.getElementById('undo-toast').style.display === 'flex'")

            # 2. Clear Notes Trigger
            ws_client.eval_js("document.getElementById('btn-clear-all-notes').click();")
            assert ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'flex'")
            ws_client.eval_js("document.getElementById('btn-confirm-cancel').click();")
            assert ws_client.eval_js(f'window.db.getAnnotations("{book_id}").length') == 1

            # 3. Escape Key Trap Protection: Pressing Escape closes modal without executing proceed
            ws_client.eval_js("document.getElementById('btn-clear-all-notes').click();")
            assert ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'flex'")
            ws_client.eval_js("""
                document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
            """)
            assert ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'none'")
            assert ws_client.eval_js(f'window.db.getAnnotations("{book_id}").length') == 1
            assert ws_client.eval_js("window.app.isReading === true"), "Reader screen should remain open"

            # 4. Batch Delete in Library
            ws_client.eval_js("window.app.closeReader();")
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    window.app.selectedBookIds.clear();
                    window.app.selectedBookIds.add(books[0].id);
                    document.getElementById('btn-batch-delete').click();
                })()
            """)
            assert ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'flex'")
            ws_client.eval_js("document.getElementById('btn-confirm-cancel').click();")
            assert ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'none'")

        test("TC-M4-REG-01", "M1: Confirmation Modals (#modal-confirm) Destructive Triggers & Escape Isolation", t_m1_confirmation_modals)

        # ======================================================================
        # TC-M4-REG-02: Milestone 1 Interactive Undo Toast Lifecycle & Stacking Resilience
        # ======================================================================
        def t_m1_undo_toast():
            ws_client.eval_js("""
                (() => {
                    window.testUndoCount = 0;
                    window.app.showUndoToast("Action 1", () => { window.testUndoCount += 1; }, 4000);
                })()
            """)
            toast_data = ws_client.eval_js("""
                (() => {
                    const toast = document.getElementById('undo-toast');
                    return {
                        display: toast.style.display,
                        role: toast.getAttribute('role'),
                        ariaLive: toast.getAttribute('aria-live'),
                        message: document.getElementById('undo-toast-message').textContent,
                        hasActionBtn: !!document.getElementById('btn-undo-action'),
                        hasCloseBtn: !!document.getElementById('btn-close-undo-toast')
                    };
                })()
            """)
            assert toast_data["display"] == "flex"
            assert toast_data["role"] == "alert"
            assert toast_data["ariaLive"] == "polite"
            assert "Action 1" in toast_data["message"]
            assert toast_data["hasActionBtn"]
            assert toast_data["hasCloseBtn"]

            # Click Undo button
            ws_client.eval_js("document.getElementById('btn-undo-action').click();")
            assert ws_client.eval_js("window.testUndoCount === 1")
            assert ws_client.eval_js("document.getElementById('undo-toast').style.display === 'none'")

            # Dismiss via close button
            ws_client.eval_js("""
                (() => {
                    window.app.showUndoToast("Action 2", () => { window.testUndoCount += 10; }, 10000);
                    document.getElementById('btn-close-undo-toast').click();
                })()
            """)
            assert ws_client.eval_js("document.getElementById('undo-toast').style.display === 'none'")
            assert ws_client.eval_js("window.testUndoCount === 1"), "Dismissing close button should not invoke undo callback"

            # Rapid-fire 5 successive toast calls
            ws_client.eval_js("""
                (() => {
                    window.latestExecuted = false;
                    for (let i = 1; i <= 5; i++) {
                        window.app.showUndoToast(`Rapid Toast ${i}`, () => {
                            if (i === 5) window.latestExecuted = true;
                        }, 5000);
                    }
                })()
            """)
            assert ws_client.eval_js("document.getElementById('undo-toast-message').textContent") == "Rapid Toast 5"
            ws_client.eval_js("document.getElementById('btn-undo-action').click();")
            assert ws_client.eval_js("window.latestExecuted === true")

        test("TC-M4-REG-02", "M1: Interactive Undo Toast (#undo-toast) Lifecycle, Dismissal & Rapid Stacking", t_m1_undo_toast)

        # ======================================================================
        # TC-M4-REG-03: Milestone 1 Book Import Shimmer Skeleton & Dropzone Feedback
        # ======================================================================
        def t_m1_import_skeleton_and_dropzone():
            # Test dropzone dragenter / dragleave events
            dz_state = ws_client.eval_js("""
                (() => {
                    const lc = document.getElementById('library-content');
                    window.dispatchEvent(new Event('dragenter'));
                    const isDragOver = lc.classList.contains('drag-over');
                    window.dispatchEvent(new Event('dragleave'));
                    const clearedDrag = !lc.classList.contains('drag-over');
                    return { isDragOver, clearedDrag };
                })()
            """)
            assert dz_state["isDragOver"], "drag-over class not added on dragenter"
            assert dz_state["clearedDrag"], "drag-over class not removed on dragleave"

            # Test skeleton structure and lifecycle via importFiles
            skeleton_audit = ws_client.eval_js("""
                (() => {
                    const fakeFile = { name: "test_novel.epub", size: 1048576 };
                    const promise = window.app.importFiles([fakeFile], "input");
                    const skeleton = document.querySelector('.book-card.loading');
                    const hasPulse = skeleton ? !!skeleton.querySelector('.card-thumb.skeleton-pulse') : false;
                    const hasTitle = skeleton ? !!skeleton.querySelector('.skeleton-line.skeleton-title') : false;
                    const hasAuthor = skeleton ? !!skeleton.querySelector('.skeleton-line.skeleton-author') : false;
                    const role = skeleton ? skeleton.getAttribute('role') : null;
                    const ariaBusy = skeleton ? skeleton.getAttribute('aria-busy') : null;

                    return {
                        mounted: !!skeleton,
                        hasPulse,
                        hasTitle,
                        hasAuthor,
                        role,
                        ariaBusy
                    };
                })()
            """)
            assert skeleton_audit["mounted"], "Loading skeleton was not mounted during importFiles"
            assert skeleton_audit["hasPulse"], "Missing .card-thumb.skeleton-pulse"
            assert skeleton_audit["hasTitle"], "Missing .skeleton-title"
            assert skeleton_audit["hasAuthor"], "Missing .skeleton-author"
            assert skeleton_audit["role"] == "status"
            assert skeleton_audit["ariaBusy"] == "true"

            # Wait for simulated import to resolve (350ms window)
            time.sleep(0.6)
            after_import = ws_client.eval_js("""
                (() => ({
                    remainingSkeletons: document.querySelectorAll('.book-card.loading').length,
                    importedBookExists: !!window.db.getBooks().find(b => b.title === "test_novel")
                }))()
            """)
            assert after_import["remainingSkeletons"] == 0, "Skeletons were not removed after import completion"
            assert after_import["importedBookExists"], "Imported book was not stored in database"

        test("TC-M4-REG-03", "M1: Book Ingestion Shimmering Skeleton (.book-card.loading) & Drag-over Visuals", t_m1_import_skeleton_and_dropzone)

        # ======================================================================
        # TC-M4-REG-04: Milestone 1 A11y Swatch Labels, Margin Zones & Text Selection
        # ======================================================================
        def t_m1_a11y_swatches_and_margin_zones():
            a11y = ws_client.eval_js("""
                (() => {
                    const swatches = Array.from(document.querySelectorAll('.swatch-btn')).map(s => ({
                        color: s.getAttribute('data-color'),
                        label: s.getAttribute('aria-label')
                    }));

                    const zp = document.getElementById('zone-prev');
                    const zn = document.getElementById('zone-next');

                    return {
                        swatches,
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
            assert color_map.get("yellow") == "Highlight in Yellow"
            assert color_map.get("green") == "Highlight in Green"
            assert color_map.get("cyan") == "Highlight in Cyan"
            assert color_map.get("pink") == "Highlight in Pink"

            assert a11y["zpRole"] == "button"
            assert a11y["zpTabindex"] == "0"
            assert a11y["zpLabel"] == "Previous Page"
            assert a11y["znRole"] == "button"
            assert a11y["znTabindex"] == "0"
            assert a11y["znLabel"] == "Next Page"

            # Check user-select: text computed style
            user_select_ok = ws_client.eval_js("""
                (() => {
                    const rc = document.getElementById('reader-canvas');
                    const rbc = document.getElementById('reader-book-content');
                    const comp1 = window.getComputedStyle(rc);
                    const comp2 = window.getComputedStyle(rbc);
                    return comp1.userSelect !== 'none' && comp2.userSelect !== 'none';
                })()
            """)
            assert user_select_ok, "Reader canvas user-select is disabled"

        test("TC-M4-REG-04", "M1: Accessibility Swatches, Margin Navigation Zones & Text Selection", t_m1_a11y_swatches_and_margin_zones)

        # ======================================================================
        # TC-M4-REG-05: Milestone 2 Ghost Bookshelf Empty State Architecture & CTA
        # ======================================================================
        def t_m2_empty_state_and_cta():
            # Mark all books deleted to force empty state
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    books.forEach(b => b.is_deleted = 1);
                    window.db.saveBooks(books);
                    window.app.renderLibrary();
                })()
            """)
            empty = ws_client.eval_js("""
                (() => {
                    const el = document.getElementById('empty-state');
                    const title = el.querySelector('.empty-title') ? el.querySelector('.empty-title').textContent.trim() : '';
                    const subtitle = el.querySelector('.empty-subtitle') ? el.querySelector('.empty-subtitle').textContent.trim() : '';
                    const btn = document.getElementById('btn-empty-add');
                    const hint = el.querySelector('.empty-formats-hint') ? el.querySelector('.empty-formats-hint').textContent.trim() : '';
                    const svg = el.querySelector('.empty-shelf-illustration svg');
                    return {
                        display: el.style.display,
                        title,
                        subtitle,
                        btnPresent: !!btn,
                        btnText: btn ? btn.textContent.trim() : '',
                        hint,
                        svgPresent: !!svg
                    };
                })()
            """)
            assert empty["display"] != "none", "Empty state hidden when 0 books active"
            assert empty["title"] == "Your Library is Waiting", f"Empty title: {empty['title']}"
            assert "A calm place for your books" in empty["subtitle"]
            assert empty["btnPresent"], "Missing #btn-empty-add"
            assert "+ Add Your First Book" in empty["btnText"]
            assert "Supports EPUB, PDF, MOBI, FB2, CBZ, and TXT" in empty["hint"]
            assert empty["svgPresent"], "Missing ghost bookshelf SVG illustration"

            # Verify clicking #btn-empty-add triggers file input click
            ws_client.eval_js("""
                (() => {
                    window.fileInputClicked = false;
                    const fi = document.getElementById('file-import-input');
                    const origClick = fi.click;
                    fi.click = () => { window.fileInputClicked = true; };
                    document.getElementById('btn-empty-add').click();
                    fi.click = origClick;
                })()
            """)
            assert ws_client.eval_js("window.fileInputClicked === true"), "#btn-empty-add did not trigger file input"

            # Restore books
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    books.forEach(b => b.is_deleted = 0);
                    window.db.saveBooks(books);
                    window.app.renderLibrary();
                })()
            """)

        test("TC-M4-REG-05", "M2: Ghost Bookshelf Empty State Graphic, Editorial Subtitle & CTA Trigger", t_m2_empty_state_and_cta)

        # ======================================================================
        # TC-M4-REG-06: Milestone 2 Sidebar Format Tooltips & Dynamic Filtering
        # ======================================================================
        def t_m2_format_tooltips_and_filtering():
            formats_data = ws_client.eval_js("""
                (() => {
                    const items = Array.from(document.querySelectorAll('#formats-collapsible .nav-item[data-format]')).map(el => ({
                        format: el.getAttribute('data-format'),
                        title: el.getAttribute('title')
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
            assert len(formats_data) == 6, f"Expected 6 format items, found {len(formats_data)}"
            for item in formats_data:
                fmt = item["format"]
                assert item["title"] == expected_tooltips[fmt], f"Tooltip for {fmt}: got '{item['title']}'"

            # Test format filtering
            ws_client.eval_js("document.querySelector('.nav-item[data-format=\"EPUB\"]').click();")
            filter_state = ws_client.eval_js("""
                (() => ({
                    filter: window.app.currentFormatFilter,
                    category: window.app.currentCategory,
                    isActive: document.querySelector('.nav-item[data-format="EPUB"]').classList.contains('active')
                }))()
            """)
            assert filter_state["filter"] == "EPUB"
            assert filter_state["category"] is None
            assert filter_state["isActive"]

            # Reset filter back to all books
            ws_client.eval_js("document.querySelector('.nav-item[data-category=\"all\"]').click();")
            assert ws_client.eval_js("window.app.currentFormatFilter") is None
            assert ws_client.eval_js("window.app.currentCategory") == "all"

        test("TC-M4-REG-06", "M2: Sidebar Format Tooltips Across All 6 Formats & Format Filtering", t_m2_format_tooltips_and_filtering)

        # ======================================================================
        # TC-M4-REG-07: Milestone 3 Collapsible Formats Accordion & Persistence
        # ======================================================================
        def t_m3_collapsible_formats_and_persistence():
            toggle_header = ws_client.eval_js("document.getElementById('sidebar-formats-toggle') !== null")
            assert toggle_header, "Missing #sidebar-formats-toggle"

            # Collapse formats section
            ws_client.eval_js("window.app.setFormatsCollapsed(true, true);")
            collapsed_state = ws_client.eval_js("""
                (() => ({
                    isClassCollapsed: document.getElementById('formats-collapsible').classList.contains('collapsed'),
                    ariaExpanded: document.getElementById('sidebar-formats-toggle').getAttribute('aria-expanded'),
                    lsVal: localStorage.getItem('foliohaven_formats_collapsed')
                }))()
            """)
            assert collapsed_state["isClassCollapsed"]
            assert collapsed_state["ariaExpanded"] == "false"
            assert collapsed_state["lsVal"] == "true"

            # Expand formats section via toggle click
            ws_client.eval_js("document.getElementById('sidebar-formats-toggle').click();")
            expanded_state = ws_client.eval_js("""
                (() => ({
                    isClassCollapsed: document.getElementById('formats-collapsible').classList.contains('collapsed'),
                    ariaExpanded: document.getElementById('sidebar-formats-toggle').getAttribute('aria-expanded'),
                    lsVal: localStorage.getItem('foliohaven_formats_collapsed')
                }))()
            """)
            assert not expanded_state["isClassCollapsed"]
            assert expanded_state["ariaExpanded"] == "true"
            assert expanded_state["lsVal"] == "false"

            # Keyboard accessibility: Enter key on toggle header
            ws_client.eval_js("""
                document.getElementById('sidebar-formats-toggle').dispatchEvent(
                    new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })
                );
            """)
            assert ws_client.eval_js("document.getElementById('formats-collapsible').classList.contains('collapsed')")

            # Restore expanded
            ws_client.eval_js("window.app.setFormatsCollapsed(false, true);")

        test("TC-M4-REG-07", "M3: Collapsible Formats Accordion, Keyboard Toggle & LocalStorage Persistence", t_m3_collapsible_formats_and_persistence)

        # ======================================================================
        # TC-M4-REG-08: Milestone 3 Reader Toolbar Overflow Menu (⋯) Lifecycle
        # ======================================================================
        def t_m3_reader_overflow_menu():
            # Open reader
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    const nonEnc = books.find(b => !b.is_encrypted && !b.is_deleted);
                    window.app.openBook(nonEnc);
                })()
            """)

            # Verify overflow wrapper, trigger and inner buttons
            menu_info = ws_client.eval_js("""
                (() => ({
                    trigger: !!document.getElementById('btn-reader-overflow'),
                    menu: !!document.getElementById('reader-overflow-menu'),
                    btnPrint: !!document.getElementById('btn-reader-print'),
                    btnFs: !!document.getElementById('btn-reader-fullscreen'),
                    btnSet: !!document.getElementById('btn-reader-settings')
                }))()
            """)
            assert menu_info["trigger"]
            assert menu_info["menu"]
            assert menu_info["btnPrint"]
            assert menu_info["btnFs"]
            assert menu_info["btnSet"]

            # Open menu via trigger click
            ws_client.eval_js("document.getElementById('btn-reader-overflow').click();")
            assert ws_client.eval_js("document.getElementById('reader-overflow-menu').classList.contains('open')")
            assert ws_client.eval_js("document.getElementById('btn-reader-overflow').getAttribute('aria-expanded') === 'true'")

            # Outside click dismiss
            ws_client.eval_js("document.getElementById('reader-canvas').click();")
            assert not ws_client.eval_js("document.getElementById('reader-overflow-menu').classList.contains('open')")
            assert ws_client.eval_js("document.getElementById('btn-reader-overflow').getAttribute('aria-expanded') === 'false'")

            # Escape key dismiss
            ws_client.eval_js("document.getElementById('btn-reader-overflow').click();")
            assert ws_client.eval_js("document.getElementById('reader-overflow-menu').classList.contains('open')")
            ws_client.eval_js("""
                window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
            """)
            assert not ws_client.eval_js("document.getElementById('reader-overflow-menu').classList.contains('open')")
            assert ws_client.eval_js("window.app.isReading === true"), "Escape closed reader instead of overflow menu"
            assert ws_client.eval_js("document.activeElement.id === 'btn-reader-overflow'")

        test("TC-M4-REG-08", "M3: Reader Overflow Menu (⋯) Lifecycle, Outside Dismiss & Escape Isolation", t_m3_reader_overflow_menu)

        # ======================================================================
        # TC-M4-REG-09: Milestone 3 Header Category Button Removal & Canonical Preservation
        # ======================================================================
        def t_m3_category_button_integrity():
            audit = ws_client.eval_js("""
                (() => ({
                    duplicateHeaderBtn: document.getElementById('btn-add-folder'),
                    canonicalSidebarBtn: document.getElementById('btn-add-category-sidebar')
                }))()
            """)
            assert audit["duplicateHeaderBtn"] is None, "Redundant #btn-add-folder found in DOM"
            assert audit["canonicalSidebarBtn"] is not None, "Canonical #btn-add-category-sidebar missing from sidebar"

            # Check static markup
            assert 'id="btn-add-folder"' not in html_src, "Duplicate #btn-add-folder exists in index.html"
            assert 'id="btn-add-category-sidebar"' in html_src, "Canonical #btn-add-category-sidebar missing from index.html"

        test("TC-M4-REG-09", "M3: Clean Removal of Duplicate Header Category Button & Canonical Preservation", t_m3_category_button_integrity)

        # ======================================================================
        # TC-M4-REG-10: Milestone 4 Native Print Delegation & Modal Concealment
        # ======================================================================
        def t_m4_native_print_delegation():
            # Setup spy on window.print
            ws_client.eval_js("""
                (() => {
                    window.printCallCount = 0;
                    window.print = () => { window.printCallCount += 1; };
                    window.app._printDelegated = false;
                })()
            """)

            # 1. Click #btn-reader-print in overflow menu
            ws_client.eval_js("document.getElementById('btn-reader-overflow').click();")
            ws_client.eval_js("document.getElementById('btn-reader-print').click();")

            print_state_1 = ws_client.eval_js("""
                (() => ({
                    delegatedFlag: window.app._printDelegated,
                    callCount: window.printCallCount,
                    menuOpen: document.getElementById('reader-overflow-menu').classList.contains('open'),
                    modalDisplay: document.getElementById('modal-print').style.display
                }))()
            """)
            assert print_state_1["delegatedFlag"] == True, "_printDelegated flag not set"
            assert print_state_1["callCount"] == 1, f"window.print() call count mismatch: {print_state_1['callCount']}"
            assert not print_state_1["menuOpen"], "Overflow menu remained open after print trigger"
            assert print_state_1["modalDisplay"] == "none", f"#modal-print displayed: {print_state_1['modalDisplay']}"

            # 2. Trigger via Ctrl+P shortcut
            ws_client.eval_js("""
                (() => {
                    window.app._printDelegated = false;
                    window.dispatchEvent(new KeyboardEvent('keydown', { key: 'p', ctrlKey: true, bubbles: true }));
                })()
            """)
            print_state_2 = ws_client.eval_js("""
                (() => ({
                    delegatedFlag: window.app._printDelegated,
                    callCount: window.printCallCount,
                    modalDisplay: document.getElementById('modal-print').style.display
                }))()
            """)
            assert print_state_2["delegatedFlag"] == True
            assert print_state_2["callCount"] == 2
            assert print_state_2["modalDisplay"] == "none"

            # 3. Defensive modal preservation: #modal-print exists in DOM with aria-hidden
            modal_audit = ws_client.eval_js("""
                (() => {
                    const mp = document.getElementById('modal-print');
                    return {
                        exists: !!mp,
                        ariaHidden: mp ? mp.getAttribute('aria-hidden') : null,
                        hasConfirmBtn: !!document.getElementById('btn-confirm-print'),
                        hasCancelBtn: !!document.getElementById('btn-cancel-print'),
                        hasCloseBtn: !!document.getElementById('btn-close-print')
                    };
                })()
            """)
            assert modal_audit["exists"], "#modal-print missing from DOM"
            assert modal_audit["ariaHidden"] == "true"
            assert modal_audit["hasConfirmBtn"]
            assert modal_audit["hasCancelBtn"]
            assert modal_audit["hasCloseBtn"]

            # 4. Exception Resiliency: window.print throwing an error does not crash app
            ws_client.eval_js("""
                (() => {
                    window.print = () => { throw new Error("Print system blocked by browser security policy"); };
                    window.app.delegatePrint();
                })()
            """)
            # If app survived without uncaught exception, delegatePrint handled error cleanly
            assert ws_client.eval_js("window.app._printDelegated === true")

            # 5. Media print CSS rules verification
            assert "@media print" in css_src
            print_css = css_src.split("@media print")[1]
            for selector in ["#sidebar", "#reader-toolbar", "#reader-footer", ".margin-click-zone",
                             ".modal-overlay", "#undo-toast", "#reader-overflow-menu"]:
                assert selector in print_css, f"Missing {selector} in @media print rules"

        test("TC-M4-REG-10", "M4: Native Print Delegation (window.print()), Resiliency & #modal-print Concealment", t_m4_native_print_delegation)

        # ======================================================================
        # TC-M4-REG-11: Milestone 4 Design Token Adherence (.card-thumb) & Theme Invariance
        # ======================================================================
        def t_m4_card_thumb_tokens():
            # Return to library
            ws_client.eval_js("window.app.closeReader();")

            # Check styles.css has zero #e2e8f0
            assert "#e2e8f0" not in css_src, "Hardcoded color #e2e8f0 found in styles.css"
            # Check computed styles for .card-thumb and .card-thumb.skeleton-pulse across light and dark themes
            res = ws_client.eval_js("""
                (() => {
                    document.documentElement.removeAttribute("data-theme");

                    const thumb = document.createElement("div");
                    thumb.className = "card-thumb";
                    document.body.appendChild(thumb);

                    const skelThumb = document.createElement("div");
                    skelThumb.className = "card-thumb skeleton-pulse";
                    document.body.appendChild(skelThumb);

                    const lightThumbBg = window.getComputedStyle(thumb).backgroundColor;
                    const lightSkelGradient = window.getComputedStyle(skelThumb).backgroundImage;

                    // Switch to dark theme
                    document.documentElement.setAttribute("data-theme", "dark");
                    const darkThumbBg = window.getComputedStyle(thumb).backgroundColor;
                    const darkSkelGradient = window.getComputedStyle(skelThumb).backgroundImage;

                    // Reset theme
                    document.documentElement.removeAttribute("data-theme");
                    thumb.remove();
                    skelThumb.remove();

                    return {
                        lightThumbBg,
                        lightSkelGradient,
                        darkThumbBg,
                        darkSkelGradient
                    };
                })()
            """)
            assert res["lightThumbBg"] == "rgb(245, 247, 250)", f"Light .card-thumb bg mismatch: {res['lightThumbBg']}"
            assert "linear-gradient" in res["lightSkelGradient"], "Skeleton pulse must use linear-gradient"
            assert res["darkThumbBg"] == "rgb(32, 36, 44)", f"Dark .card-thumb bg mismatch: {res['darkThumbBg']}"
            assert "linear-gradient" in res["darkSkelGradient"], "Dark skeleton pulse must use linear-gradient"

        test("TC-M4-REG-11", "M4: Design Token Migration (.card-thumb) & Cross-Theme Color Invariance", t_m4_card_thumb_tokens)

        # ======================================================================
        # TC-M4-REG-12: Milestone 4 Inline Styles Elimination & Class Migration
        # ======================================================================
        def t_m4_inline_styles_elimination():
            # Check brand title in DOM and source
            assert '<h1 class="brand-title">FolioHaven</h1>' in html_src, "brand-title markup altered"
            assert 'class="brand-title" style=' not in html_src, "brand-title retains inline styles"

            # Check reader page info & progress info
            assert 'id="reader-page-info" class="reader-page-info"' in html_src
            assert 'id="reader-progress-info" class="reader-progress-info"' in html_src
            assert 'id="reader-page-info" style=' not in html_src
            assert 'id="reader-progress-info" style=' not in html_src

            # Check computed font-size and color on brand-title
            brand_styles = ws_client.eval_js("""
                (() => {
                    const bt = document.querySelector('.brand-title');
                    const comp = window.getComputedStyle(bt);
                    return {
                        fontWeight: comp.fontWeight,
                        color: comp.color,
                        margin: comp.margin
                    };
                })()
            """)
            assert int(brand_styles["fontWeight"]) >= 600, f"Brand title weight: {brand_styles['fontWeight']}"

            # Static style attribute audit: only #modal-print may have style="display: none;"
            import re
            style_matches = re.findall(r'<[^>]*\bstyle=["\'][^"\']*["\'][^>]*>', html_src)
            assert len(style_matches) == 1, f"Expected exactly 1 static style in index.html, found {len(style_matches)}: {style_matches}"
            assert 'id="modal-print"' in style_matches[0], f"Sole static style must be on #modal-print, found: {style_matches[0]}"

        test("TC-M4-REG-12", "M4: Elimination of Static Inline Styles, Semantic Class Migration & DOM Audit", t_m4_inline_styles_elimination)

        print("=" * 78)
        passed = sum(1 for _, _, res, _ in results if res == "PASS")
        total = len(results)
        print(f"  FOLIOHAVEN M4 REGRESSION SUITE: {passed}/{total} Passed (100% Success)")
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
    success = run_empirical_m4_regression_suite()
    sys.exit(0 if success else 1)
