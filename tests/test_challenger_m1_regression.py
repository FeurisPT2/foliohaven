"""
Adversarial Empirical Regression Verification Suite for Milestone 1
FolioHaven Ebook Reader Replica
Author: challenger_m1_2 (empirical challenger)

Empirically tests:
1. Reader canvas reflow, pagination, and text selection:
   - Text selection with user-select: text
   - #note-popup positioning and 4 swatch buttons with aria-labels & mark injection
   - Margin click zones #zone-prev and #zone-next click & keyboard (Enter/Space) activation
2. Drag-and-drop file ingestion:
   - Clean .drag-over toggling without child element flickering
   - .book-card.loading shimmering skeleton cards mounting & clean removal
   - Complete asynchronous book ingestion lifecycle
3. Destructive actions, confirmation modal (#modal-confirm) & undo toast (#undo-toast):
   - Clear bookmarks / clear notes / batch delete / batch purge confirmation
   - Undo toast restoration for bookmarks, notes, and batch deletion
   - Keyboard Ctrl+Z / Cmd+Z undo support
   - Modal Escape & backdrop click handling, reader screen isolation
   - DRM alert state isolation (no residual button corruption)
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

# --- Minimal WebSocket CDP Client ---
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
        if "101 Switching Protocols" not in resp and "101 WebSocket" not in resp:
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


def run_empirical_regression_suite():
    print("=" * 72)
    print("  FOLIOHAVEN REGRESSION SUITE: EMPIRICAL CHALLENGER VERIFICATION       ")
    print("=" * 72)

    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    app_url = f"file:///{app_dir.replace('\\', '/')}/index.html"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    port = 9333  # Isolated port to avoid collisions
    temp_dir = tempfile.mkdtemp(prefix="foliohaven_test_")

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
        # SECTION 1: DOM & ACCESSIBILITY ATTRIBUTES AUDIT
        # ----------------------------------------------------------------------
        def t_a11y_attributes():
            # 1. Swatch buttons aria-labels & data-color
            swatches = ws_client.eval_js("""
                Array.from(document.querySelectorAll('.swatch-btn')).map(b => ({
                    color: b.dataset.color,
                    ariaLabel: b.getAttribute('aria-label'),
                    title: b.getAttribute('title')
                }))
            """)
            assert len(swatches) == 4, f"Expected 4 swatches, got {len(swatches)}"
            expected_labels = {
                "yellow": "Highlight in Yellow",
                "green": "Highlight in Green",
                "cyan": "Highlight in Cyan",
                "pink": "Highlight in Pink"
            }
            for s in swatches:
                c = s["color"]
                assert c in expected_labels, f"Unexpected swatch color {c}"
                assert s["ariaLabel"] == expected_labels[c], f"Mismatch aria-label for {c}: {s['ariaLabel']}"
                assert s["title"] == expected_labels[c], f"Mismatch title for {c}: {s['title']}"

            # 2. Margin navigation zones a11y attributes
            zone_prev = ws_client.eval_js("""
                (() => {
                    const el = document.getElementById('zone-prev');
                    const arrow = el.querySelector('.zone-arrow');
                    return {
                        role: el.getAttribute('role'),
                        tabindex: el.getAttribute('tabindex'),
                        ariaLabel: el.getAttribute('aria-label'),
                        arrowHidden: arrow.getAttribute('aria-hidden')
                    };
                })()
            """)
            assert zone_prev["role"] == "button", f"zone-prev role is {zone_prev['role']}"
            assert zone_prev["tabindex"] == "0", f"zone-prev tabindex is {zone_prev['tabindex']}"
            assert zone_prev["ariaLabel"] == "Previous Page", f"zone-prev aria-label is {zone_prev['ariaLabel']}"
            assert zone_prev["arrowHidden"] == "true", f"zone-prev arrow aria-hidden is {zone_prev['arrowHidden']}"

            zone_next = ws_client.eval_js("""
                (() => {
                    const el = document.getElementById('zone-next');
                    const arrow = el.querySelector('.zone-arrow');
                    return {
                        role: el.getAttribute('role'),
                        tabindex: el.getAttribute('tabindex'),
                        ariaLabel: el.getAttribute('aria-label'),
                        arrowHidden: arrow.getAttribute('aria-hidden')
                    };
                })()
            """)
            assert zone_next["role"] == "button", f"zone-next role is {zone_next['role']}"
            assert zone_next["tabindex"] == "0", f"zone-next tabindex is {zone_next['tabindex']}"
            assert zone_next["ariaLabel"] == "Next Page", f"zone-next aria-label is {zone_next['ariaLabel']}"
            assert zone_next["arrowHidden"] == "true", f"zone-next arrow aria-hidden is {zone_next['arrowHidden']}"

            # 3. Confirmation dialog and Undo toast accessibility semantics
            modal_attrs = ws_client.eval_js("""
                (() => {
                    const m = document.getElementById('modal-confirm');
                    const t = document.getElementById('undo-toast');
                    return {
                        modalRole: m.getAttribute('role'),
                        modalAriaModal: m.getAttribute('aria-modal'),
                        modalLabelledBy: m.getAttribute('aria-labelledby'),
                        modalDescribedBy: m.getAttribute('aria-describedby'),
                        toastRole: t.getAttribute('role'),
                        toastLive: t.getAttribute('aria-live')
                    };
                })()
            """)
            assert modal_attrs["modalRole"] == "dialog", f"modal-confirm role: {modal_attrs['modalRole']}"
            assert modal_attrs["modalAriaModal"] == "true", f"modal-confirm aria-modal: {modal_attrs['modalAriaModal']}"
            assert modal_attrs["modalLabelledBy"] == "confirm-title", f"modal-confirm aria-labelledby: {modal_attrs['modalLabelledBy']}"
            assert modal_attrs["modalDescribedBy"] == "confirm-message", f"modal-confirm aria-describedby: {modal_attrs['modalDescribedBy']}"
            assert modal_attrs["toastRole"] == "alert", f"undo-toast role: {modal_attrs['toastRole']}"
            assert modal_attrs["toastLive"] == "polite", f"undo-toast aria-live: {modal_attrs['toastLive']}"

        test("CHAL-M1-01", "A11y Attributes: Swatches, Margin Zones, Dialog, and Toast", t_a11y_attributes)

        # ----------------------------------------------------------------------
        # SECTION 2: READER CANVAS TEXT SELECTION & CSS USER-SELECT
        # ----------------------------------------------------------------------
        def t_reader_selection_and_reflow():
            # Ingest rich multi-paragraph book
            ws_client.eval_js("""
                (() => {
                    window.db.addBook({
                        title: "Reflow & Selection Test Volume",
                        author: "FolioHaven Challenger",
                        format: "EPUB",
                        file_path: "test/reflow_selection.epub",
                        file_size_bytes: 409600,
                        content: `Chapter 1: The Empirical Foundation.\\n\\nParagraph alpha contains substantial text designed for selection and highlight validation across columns.\\n\\nParagraph beta demonstrates pagination stability and layout reflow under varying typographical settings.\\n\\nParagraph gamma tests mark injection fidelity inside reading spreads without breaking paragraph structures.`
                    });
                    const books = window.db.getBooks();
                    const target = books.find(b => b.title === "Reflow & Selection Test Volume");
                    window.app.openBook(target);
                })()
            """)

            # Verify computed user-select on reader content
            user_select_styles = ws_client.eval_js("""
                (() => {
                    const canvas = document.getElementById('reader-canvas');
                    const content = document.getElementById('reader-book-content');
                    const paras = Array.from(document.querySelectorAll('.reflow-para'));
                    return {
                        canvasSelect: window.getComputedStyle(canvas).userSelect,
                        contentSelect: window.getComputedStyle(content).userSelect,
                        paraSelect: paras.length > 0 ? window.getComputedStyle(paras[0]).userSelect : 'none',
                        paraCount: paras.length
                    };
                })()
            """)
            assert user_select_styles["canvasSelect"] == "text", f"canvas userSelect: {user_select_styles['canvasSelect']}"
            assert user_select_styles["contentSelect"] == "text", f"content userSelect: {user_select_styles['contentSelect']}"
            assert user_select_styles["paraSelect"] == "text", f"reflow-para userSelect: {user_select_styles['paraSelect']}"

            # Simulate text selection in first paragraph
            popup_status = ws_client.eval_js("""
                (() => {
                    const p = document.querySelector('.reflow-para');
                    const range = document.createRange();
                    range.setStart(p.firstChild, 0);
                    range.setEnd(p.firstChild, 25);
                    const sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(range);
                    document.dispatchEvent(new Event('selectionchange'));

                    const popup = document.getElementById('note-popup');
                    return {
                        selectedText: sel.toString(),
                        display: popup.style.display,
                        top: popup.style.top,
                        left: popup.style.left
                    };
                })()
            """)
            assert len(popup_status["selectedText"]) == 25, f"Selection failed: {popup_status['selectedText']}"
            assert popup_status["display"] == "flex", f"Note popup not visible: {popup_status['display']}"
            assert popup_status["top"] != "", "Note popup missing top offset"
            assert popup_status["left"] != "", "Note popup missing left offset"

            # Apply swatch annotations: Yellow, Green, Cyan, Pink across different paragraphs
            colors = ["yellow", "green", "cyan", "pink"]
            for idx, color in enumerate(colors):
                res = ws_client.eval_js(f"""
                    (() => {{
                        const paras = Array.from(document.querySelectorAll('.reflow-para'));
                        const p = paras[{idx} % paras.length];
                        const textNode = p.firstChild;
                        const range = document.createRange();
                        range.setStart(textNode, 0);
                        range.setEnd(textNode, Math.min(textNode.textContent.length, 12));
                        const sel = window.getSelection();
                        sel.removeAllRanges();
                        sel.addRange(range);
                        document.dispatchEvent(new Event('selectionchange'));

                        const btn = document.querySelector('.swatch-btn[data-color="{color}"]');
                        btn.click();

                        const activeBook = window.app.activeBook;
                        const anns = window.db.getAnnotations(activeBook.id);
                        const marks = Array.from(document.querySelectorAll('mark.highlight-{color}'));
                        return {{
                            annCount: anns.length,
                            latestAnnColor: anns[anns.length - 1].color_code,
                            markCount: marks.length
                        }};
                    }})()
                """)
                assert res["latestAnnColor"] == color, f"Expected color {color}, got {res['latestAnnColor']}"
                assert res["markCount"] > 0, f"No DOM mark injected for {color}"

            # Verify reflow toggle between 1-column and 2-column does not break layout or lose annotations
            ws_client.eval_js("""
                document.getElementById('btn-col-double').click();
            """)
            spread_type = ws_client.eval_js("""
                document.querySelector('.two-column-spread') !== null
            """)
            assert spread_type, "Two column spread not active"

            ws_client.eval_js("""
                document.getElementById('btn-col-single').click();
            """)
            single_type = ws_client.eval_js("""
                document.querySelector('.single-column-spread') !== null
            """)
            assert single_type, "Single column spread not active"

            # Return to library
            ws_client.eval_js("window.app.closeReader();")

        test("CHAL-M1-02", "Reader Canvas Text Selection, NotePopup, Swatches, and Column Reflow", t_reader_selection_and_reflow)

        # ----------------------------------------------------------------------
        # SECTION 3: MARGIN CLICK ZONES CLICK & KEYBOARD NAV (ENTER & SPACE)
        # ----------------------------------------------------------------------
        def t_margin_zones_interaction():
            ws_client.eval_js("""
                (() => {
                    const multiParaContent = Array.from({length: 12}, (_, i) =>
                        `Paragraph ${i + 1}: Multi-spread content block designed to test pagination boundaries and margin zone interaction across consecutive spreads. Continuous prose ensures that each column is filled beyond the 800-character threshold to force spread pagination.`
                    ).join('\\n\\n');

                    window.db.addBook({
                        title: "Multi-Spread Margin Zone Test Book",
                        author: "FolioHaven Challenger",
                        format: "EPUB",
                        file_path: "test/margin_test.epub",
                        file_size_bytes: 409600,
                        content: multiParaContent
                    });
                    const books = window.db.getBooks();
                    const target = books.find(b => b.title === "Multi-Spread Margin Zone Test Book");
                    window.app.openBook(target);
                })()
            """)

            # Verify initial spread & spreads count
            spread_start = ws_client.eval_js("window.engine.currentSpreadIndex")
            total_spreads = ws_client.eval_js("window.engine.pagesInChapter.length")
            assert total_spreads >= 2, f"Expected at least 2 spreads, got {total_spreads}"

            # 1. Click zone-next
            ws_client.eval_js("document.getElementById('zone-next').click();")
            spread_after_click_next = ws_client.eval_js("window.engine.currentSpreadIndex")
            assert spread_after_click_next == spread_start + 1, f"Click zone-next failed: {spread_after_click_next} != {spread_start + 1}"

            # 2. Click zone-prev
            ws_client.eval_js("document.getElementById('zone-prev').click();")
            spread_after_click_prev = ws_client.eval_js("window.engine.currentSpreadIndex")
            assert spread_after_click_prev == spread_start, f"Click zone-prev failed: {spread_after_click_prev} != {spread_start}"

            # 3. Keyboard Enter on zone-next
            ws_client.eval_js("""
                (() => {
                    const zn = document.getElementById('zone-next');
                    zn.focus();
                    zn.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                })()
            """)
            spread_enter_next = ws_client.eval_js("window.engine.currentSpreadIndex")
            assert spread_enter_next == spread_start + 1, f"Enter on zone-next failed: {spread_enter_next} != {spread_start + 1}"

            # 4. Keyboard Enter on zone-prev
            ws_client.eval_js("""
                (() => {
                    const zp = document.getElementById('zone-prev');
                    zp.focus();
                    zp.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                })()
            """)
            spread_enter_prev = ws_client.eval_js("window.engine.currentSpreadIndex")
            assert spread_enter_prev == spread_start, f"Enter on zone-prev failed: {spread_enter_prev} != {spread_start}"

            # 5. Keyboard Space on zone-prev: MUST NOT trigger pageNext via space bubbling!
            # Move to spread 1 (second spread) first
            ws_client.eval_js("window.app.pageNext();")
            spread_is_1 = ws_client.eval_js("window.engine.currentSpreadIndex")
            assert spread_is_1 == spread_start + 1, f"Expected spread {spread_start + 1}, got {spread_is_1}"

            # Press Space on zone-prev -> must navigate backwards to spread 0, NOT forward to spread 2!
            ws_client.eval_js("""
                (() => {
                    const zp = document.getElementById('zone-prev');
                    zp.focus();
                    zp.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', bubbles: true }));
                })()
            """)
            spread_space_prev = ws_client.eval_js("window.engine.currentSpreadIndex")
            assert spread_space_prev == spread_start, f"Space on zone-prev did not decrement spread! Got {spread_space_prev}, expected {spread_start}"

            ws_client.eval_js("window.app.closeReader();")

        test("CHAL-M1-03", "Margin Zones: Click, Enter, Space Activation & stopPropagation", t_margin_zones_interaction)

        # ----------------------------------------------------------------------
        # SECTION 4: DRAG-AND-DROP VISUAL FEEDBACK & SKELETON CARDS
        # ----------------------------------------------------------------------
        def t_drag_and_drop_ingestion():
            # Test drag counter & flicker prevention
            res_drag = ws_client.eval_js("""
                (() => {
                    const lc = document.getElementById('library-content');
                    const initialHasClass = lc.classList.contains('drag-over');

                    // Enter window
                    window.dispatchEvent(new Event('dragenter'));
                    const afterEnter = lc.classList.contains('drag-over');

                    // Enter child element (simulating drag over child node)
                    window.dispatchEvent(new Event('dragenter'));
                    // Leave child element
                    window.dispatchEvent(new Event('dragleave'));
                    const afterChildLeave = lc.classList.contains('drag-over');

                    // Final leave window
                    window.dispatchEvent(new Event('dragleave'));
                    const afterFinalLeave = lc.classList.contains('drag-over');

                    return {
                        initialHasClass,
                        afterEnter,
                        afterChildLeave,
                        afterFinalLeave
                    };
                })()
            """)
            assert not res_drag["initialHasClass"], "Initial drag-over should be false"
            assert res_drag["afterEnter"], "drag-over should be active after dragenter"
            assert res_drag["afterChildLeave"], "drag-over must NOT flicker off when leaving a child node!"
            assert not res_drag["afterFinalLeave"], "drag-over should be removed after exiting window"

            # Test skeleton cards during file ingestion
            ws_client.eval_js("""
                (() => {
                    // Trigger importFiles with 2 fake files
                    const fakeFiles = [
                        { name: "Adversarial_Novel_1.epub", size: 102400 },
                        { name: "Adversarial_Novel_2.mobi", size: 204800 }
                    ];
                    window._importPromise = window.app.importFiles(fakeFiles, "drop");
                })()
            """)

            # Skeletons must immediately mount
            skeleton_check = ws_client.eval_js("""
                (() => {
                    const skeletons = Array.from(document.querySelectorAll('.book-card.loading'));
                    return {
                        count: skeletons.length,
                        busy: skeletons.map(s => s.getAttribute('aria-busy')),
                        role: skeletons.map(s => s.getAttribute('role')),
                        hasPulse: skeletons.map(s => s.querySelector('.skeleton-pulse') !== null),
                        hasTitle: skeletons.map(s => s.querySelector('.skeleton-title') !== null)
                    };
                })()
            """)
            assert skeleton_check["count"] == 2, f"Expected 2 skeleton cards, found {skeleton_check['count']}"
            assert all(b == "true" for b in skeleton_check["busy"]), "Skeletons missing aria-busy='true'"
            assert all(r == "status" for r in skeleton_check["role"]), "Skeletons missing role='status'"
            assert all(skeleton_check["hasPulse"]), "Skeletons missing .skeleton-pulse"
            assert all(skeleton_check["hasTitle"]), "Skeletons missing .skeleton-title"

            # Wait for ingestion promise to complete
            time.sleep(0.5)
            completion_check = ws_client.eval_js("""
                (() => {
                    const remainingSkeletons = document.querySelectorAll('.book-card.loading').length;
                    const books = window.db.getBooks();
                    const novel1 = books.find(b => b.title === "Adversarial_Novel_1");
                    const novel2 = books.find(b => b.title === "Adversarial_Novel_2");
                    return {
                        remainingSkeletons,
                        novel1Found: novel1 !== undefined,
                        novel2Found: novel2 !== undefined
                    };
                })()
            """)
            assert completion_check["remainingSkeletons"] == 0, "Skeletons were not removed after import completed"
            assert completion_check["novel1Found"], "Novel 1 not found in library"
            assert completion_check["novel2Found"], "Novel 2 not found in library"

            # Edge case: Empty file list call
            ws_client.eval_js("""
                (() => {
                    window.app.importFiles([], "input");
                })()
            """)
            remaining_after_empty = ws_client.eval_js("document.querySelectorAll('.book-card.loading').length")
            assert remaining_after_empty == 0, "Empty import mounted spurious skeletons"

        test("CHAL-M1-04", "Drag-and-Drop: Counter-based Flicker Prevention & Skeleton Ingestion Lifecycle", t_drag_and_drop_ingestion)

        # ----------------------------------------------------------------------
        # SECTION 5: DESTRUCTIVE ACTIONS, CONFIRMATION MODAL & UNDO TOAST
        # ----------------------------------------------------------------------
        def t_destructive_actions_and_undo():
            # Open a book to test bookmarks and notes
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    window.app.openBook(books[0]);
                })()
            """)
            active_id = ws_client.eval_js("window.app.activeBook.id")

            # Seed bookmarks
            ws_client.eval_js(f"""
                (() => {{
                    window.db.addBookmark({{ book_id: "{active_id}", chapter_index: 0, label: "BM 1", excerpt: "Excerpt 1" }});
                    window.db.addBookmark({{ book_id: "{active_id}", chapter_index: 1, label: "BM 2", excerpt: "Excerpt 2" }});
                }})()
            """)
            bm_count_start = ws_client.eval_js(f'window.db.getBookmarks("{active_id}").length')
            assert bm_count_start >= 2, f"Bookmarks not seeded: {bm_count_start}"

            # 1. Test Clear Bookmarks Cancel
            ws_client.eval_js("document.getElementById('btn-clear-all-bookmarks').click();")
            modal_vis = ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'flex'")
            assert modal_vis, "Confirmation modal not visible for clear bookmarks"
            ws_client.eval_js("document.getElementById('btn-confirm-cancel').click();")
            modal_hidden = ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'none'")
            assert modal_hidden, "Confirmation modal not dismissed on cancel"
            bm_count_after_cancel = ws_client.eval_js(f'window.db.getBookmarks("{active_id}").length')
            assert bm_count_after_cancel == bm_count_start, "Bookmarks destroyed despite cancel!"

            # 2. Test Clear Bookmarks Proceed & Undo Toast
            ws_client.eval_js("document.getElementById('btn-clear-all-bookmarks').click();")
            ws_client.eval_js("document.getElementById('btn-confirm-proceed').click();")
            bm_count_cleared = ws_client.eval_js(f'window.db.getBookmarks("{active_id}").length')
            assert bm_count_cleared == 0, f"Bookmarks not cleared: {bm_count_cleared}"

            toast_vis = ws_client.eval_js("document.getElementById('undo-toast').style.display === 'flex'")
            assert toast_vis, "Undo toast not displayed after clearing bookmarks"

            # Click Undo button on toast
            ws_client.eval_js("document.getElementById('btn-undo-action').click();")
            bm_count_restored = ws_client.eval_js(f'window.db.getBookmarks("{active_id}").length')
            assert bm_count_restored == bm_count_start, f"Undo failed to restore bookmarks: {bm_count_restored} != {bm_count_start}"
            toast_hidden = ws_client.eval_js("document.getElementById('undo-toast').style.display === 'none'")
            assert toast_hidden, "Toast not hidden after undo"

            # 3. Test Clear Notes Proceed & Ctrl+Z Keyboard Undo
            ws_client.eval_js(f"""
                (() => {{
                    window.db.addAnnotation({{ book_id: "{active_id}", selected_text: "Note A", note_text: "Comment A", color_code: "yellow" }});
                    window.db.addAnnotation({{ book_id: "{active_id}", selected_text: "Note B", note_text: "Comment B", color_code: "pink" }});
                }})()
            """)
            notes_count_start = ws_client.eval_js(f'window.db.getAnnotations("{active_id}").length')
            assert notes_count_start >= 2, f"Notes not seeded: {notes_count_start}"

            ws_client.eval_js("document.getElementById('btn-clear-all-notes').click();")
            ws_client.eval_js("document.getElementById('btn-confirm-proceed').click();")
            notes_count_cleared = ws_client.eval_js(f'window.db.getAnnotations("{active_id}").length')
            assert notes_count_cleared == 0, f"Notes not cleared: {notes_count_cleared}"

            toast_vis_notes = ws_client.eval_js("document.getElementById('undo-toast').style.display === 'flex'")
            assert toast_vis_notes, "Undo toast not displayed after clearing notes"

            # Trigger Ctrl+Z keydown
            ws_client.eval_js("""
                window.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', ctrlKey: true, bubbles: true }));
            """)
            notes_count_restored = ws_client.eval_js(f'window.db.getAnnotations("{active_id}").length')
            assert notes_count_restored == notes_count_start, f"Ctrl+Z failed to restore notes: {notes_count_restored} != {notes_count_start}"

            # 4. Test Modal Escape Key Reader Screen Isolation
            # Open confirm modal in reader view
            ws_client.eval_js("document.getElementById('btn-clear-all-notes').click();")
            modal_vis_esc = ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'flex'")
            assert modal_vis_esc, "Modal not open before Escape test"

            # Press Escape
            ws_client.eval_js("""
                document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
            """)
            modal_esc_closed = ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'none'")
            assert modal_esc_closed, "Modal did not close on Escape"
            reader_still_open = ws_client.eval_js("window.app.isReading === true")
            assert reader_still_open, "Reader screen incorrectly closed when Escape was pressed inside confirm modal!"

            # 5. Test Backdrop Click Dismissal
            ws_client.eval_js("document.getElementById('btn-clear-all-notes').click();")
            ws_client.eval_js("""
                (() => {
                    const m = document.getElementById('modal-confirm');
                    m.dispatchEvent(new MouseEvent('click', { target: m, bubbles: true }));
                })()
            """)
            modal_backdrop_closed = ws_client.eval_js("document.getElementById('modal-confirm').style.display === 'none'")
            assert modal_backdrop_closed, "Modal did not close on backdrop click"

            # Return to library for batch delete testing
            ws_client.eval_js("window.app.closeReader();")

            # 6. Test Batch Delete & Undo
            debug_info = ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks().filter(b => !b.is_deleted);
                    const uniqueIds = Array.from(new Set(books.map(b => b.id)));
                    window.app.selectedBookIds.clear();
                    if (uniqueIds.length > 0) window.app.selectedBookIds.add(uniqueIds[0]);
                    if (uniqueIds.length > 1) window.app.selectedBookIds.add(uniqueIds[1]);
                    window.app.updateOperationsFooter();
                    return {
                        totalNonDeleted: books.length,
                        uniqueIdCount: uniqueIds.length,
                        selectedCount: window.app.selectedBookIds.size
                    };
                })()
            """)
            sel_count = debug_info["selectedCount"]
            assert sel_count == 2, f"Selection not set: {sel_count}"

            initial_trash_count = ws_client.eval_js("window.db.getBooks().filter(b => b.is_deleted).length")

            ws_client.eval_js("document.getElementById('btn-batch-delete').click();")
            ws_client.eval_js("document.getElementById('btn-confirm-proceed').click();")

            trash_count = ws_client.eval_js("window.db.getBooks().filter(b => b.is_deleted).length")
            assert trash_count == initial_trash_count + 2, f"Books not moved to trash: {trash_count} != {initial_trash_count + 2}"

            # Undo batch delete
            ws_client.eval_js("document.getElementById('btn-undo-action').click();")
            trash_count_restored = ws_client.eval_js("window.db.getBooks().filter(b => b.is_deleted).length")
            assert trash_count_restored == initial_trash_count, f"Undo batch delete failed, trash has {trash_count_restored} items, expected {initial_trash_count}"

            # 7. Test DRM Modal State Isolation (Does DRM warning break subsequent confirm modals?)
            ws_client.eval_js("""
                (() => {
                    window.app.openBook({ is_drm: 1, title: 'DRM Locked' });
                })()
            """)
            drm_title = ws_client.eval_js("document.getElementById('confirm-title').textContent")
            assert "DRM" in drm_title, f"DRM title mismatch: {drm_title}"
            drm_proceed_hidden = ws_client.eval_js("document.getElementById('btn-confirm-proceed').style.display === 'none'")
            assert drm_proceed_hidden, "Proceed button was not hidden during DRM warning"

            # Dismiss DRM modal
            ws_client.eval_js("document.getElementById('btn-confirm-cancel').click();")

            # Open subsequent confirm modal: MUST have proceed button restored!
            ws_client.eval_js("""
                window.app.showConfirmModal({
                    title: "Test Subsequent Dialog",
                    message: "Verifying button restoration",
                    proceedLabel: "Confirm Clean",
                    cancelLabel: "Cancel Clean"
                });
            """)
            subsequent_proceed_vis = ws_client.eval_js("document.getElementById('btn-confirm-proceed').style.display !== 'none'")
            subsequent_proceed_text = ws_client.eval_js("document.getElementById('btn-confirm-proceed').textContent")
            subsequent_cancel_text = ws_client.eval_js("document.getElementById('btn-confirm-cancel').textContent")
            assert subsequent_proceed_vis, "Proceed button remained hidden in subsequent confirm dialog!"
            assert subsequent_proceed_text == "Confirm Clean", f"Proceed text not restored: {subsequent_proceed_text}"
            assert subsequent_cancel_text == "Cancel Clean", f"Cancel text not restored: {subsequent_cancel_text}"

            ws_client.eval_js("document.getElementById('btn-confirm-cancel').click();")

        test("CHAL-M1-05", "Destructive Modals, State Restoring Undo Toast, Ctrl+Z, Escape Isolation, and DRM State Cleanliness", t_destructive_actions_and_undo)

        print("=" * 72)
        passed = sum(1 for _, _, res, _ in results if res == "PASS")
        total = len(results)
        print(f"  CHALLENGER REGRESSION SUMMARY: {passed}/{total} Passed")
        print("=" * 72)

        return passed == total

    finally:
        if ws_client:
            ws_client.close()
        proc.terminate()


if __name__ == "__main__":
    success = run_empirical_regression_suite()
    sys.exit(0 if success else 1)
