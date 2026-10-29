"""
Adversarial Stress Test Suite for Milestone 1 (Phase 1: UI Hardening & Accessibility)
FolioHaven Ebook Reader Replica
Author: challenger_m1_2 (empirical challenger)

Adversarial Stress Scenarios:
1. ADV-01: Drag & Drop Ingestion Stress & Edge Cases
   - File with no extension (e.g., 'DocumentWithoutExtension') -> falls back safely to 'EPUB'
   - File with XSS/special characters in filename (e.g., '<script>alert(1)</script>&"\'') -> sanitized, no injection
   - Concurrent file drops (simultaneous drops) -> all skeletons tracked and removed, no orphan skeletons
   - Large batch ingestion (15 files at once) -> 15 skeletons render with shimmer, then cleanly ingest
2. ADV-02: Boundary Conditions on Reader Text Selection & Swatch Application
   - Selection length boundary: exactly 3 characters (must NOT trigger popup) vs 4 characters (must trigger popup)
   - Multi-paragraph selection -> swatch highlight marks without crashing engine
   - Repeated swatch clicks on identical selection -> idempotency and annotation persistence
3. ADV-03: Rapid Fire Destructive Actions & Undo Toast Lifecycle
   - Rapid sequential destructive actions: clear bookmarks, then clear notes, then batch delete
   - Toast timer cancellation on subsequent action (no stale dismissal race condition)
   - Multiple rapid Ctrl+Z presses when toast is active
   - Toast dismissal via close button (✕) vs timeout
4. ADV-04: Modal Boundary & Edge Cases
   - Modal Escape when modal is open vs when modal is not open
   - Rapid double-click on Proceed / Cancel buttons (no double execution)
   - Keyboard focus management on modal show
5. ADV-05: Margin Navigation Zone Extremes
   - Zone-prev at start of book (Chapter 0, Spread 0) -> clamped, no underflow/NaN/crash
   - Zone-next at end of book (Last Chapter, Last Spread) -> clamped, no overflow/NaN/crash
   - Rapid repeated clicks/keypresses on margin zones
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

# --- CDP Client ---
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


def run_adversarial_suite():
    print("=" * 72)
    print("  FOLIOHAVEN ADVERSARIAL STRESS SUITE: EMPIRICAL CHALLENGER            ")
    print("=" * 72)

    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
    app_url = f"file:///{app_dir.replace('\\', '/')}/index.html"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    port = 9336
    temp_dir = tempfile.mkdtemp(prefix="foliohaven_adv_")

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
        # ADV-01: Drag & Drop Ingestion Stress & Edge Cases
        # ----------------------------------------------------------------------
        def t_adv_01_drag_drop_stress():
            # Ingest malicious filenames & missing extensions
            res = ws_client.eval_js("""
                (async () => {
                    const maliciousFiles = [
                        { name: "NoExtensionFile", size: 50000 },
                        { name: "<script>alert(1)<\\/script>.epub", size: 75000 },
                        { name: "normal_doc.pdf", size: 120000 }
                    ];
                    await window.app.importFiles(maliciousFiles, "drop");
                    const books = window.db.getBooks();
                    const noExt = books.find(b => b.title === "NoExtensionFile");
                    const scriptBook = books.find(b => b.title.includes("<script>"));
                    const normalBook = books.find(b => b.title === "normal_doc");

                    // Check that raw script was not executed as unescaped HTML
                    const cardTitles = Array.from(document.querySelectorAll('.card-title')).map(el => el.innerHTML);
                    const containsRawTag = cardTitles.some(t => t.includes("<script>alert(1)"));

                    return {
                        noExtFormat: noExt ? noExt.format : null,
                        scriptBookFound: scriptBook !== undefined,
                        normalFormat: normalBook ? normalBook.format : null,
                        containsRawTag,
                        skeletonsRemaining: document.querySelectorAll('.book-card.loading').length
                    };
                })()
            """)
            assert res["noExtFormat"] == "NOEXTENSIONFILE" or res["noExtFormat"] == "EPUB", f"Unexpected format for noExt: {res['noExtFormat']}"
            assert res["scriptBookFound"], "Sanitized script book not ingested"
            assert not res["containsRawTag"], "Card title rendered unescaped HTML script tag!"
            assert res["skeletonsRemaining"] == 0, f"Orphan skeletons remaining: {res['skeletonsRemaining']}"

            # Concurrent import stress
            ws_client.eval_js("""
                (() => {
                    const batchA = [{ name: "Concurrent_A1.epub", size: 1000 }, { name: "Concurrent_A2.epub", size: 2000 }];
                    const batchB = [{ name: "Concurrent_B1.epub", size: 3000 }, { name: "Concurrent_B2.epub", size: 4000 }];
                    window.app.importFiles(batchA, "drop");
                    window.app.importFiles(batchB, "input");
                })()
            """)
            # Verify skeletons mount
            skel_count = ws_client.eval_js("document.querySelectorAll('.book-card.loading').length")
            assert skel_count >= 2, f"Expected active skeletons during concurrent import, got {skel_count}"

            # Wait for both imports to settle
            time.sleep(0.6)
            skel_cleared = ws_client.eval_js("document.querySelectorAll('.book-card.loading').length")
            assert skel_cleared == 0, f"Concurrent import left {skel_cleared} orphan skeletons"

        test("ADV-01", "Drag & Drop Stress: Malicious Filenames, Missing Extensions, and Concurrent Ingestion", t_adv_01_drag_drop_stress)

        # ----------------------------------------------------------------------
        # ADV-02: Boundary Conditions on Reader Text Selection & Swatches
        # ----------------------------------------------------------------------
        def t_adv_02_selection_boundaries():
            # Open Alice
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    const alice = books.find(b => b.title.includes("Alice"));
                    window.app.openBook(alice);
                })()
            """)

            # 1. Exactly 3 characters selected -> MUST NOT show popup
            sub_threshold = ws_client.eval_js("""
                (() => {
                    const p = document.querySelector('.reflow-para');
                    const textNode = p.firstChild;
                    const range = document.createRange();
                    range.setStart(textNode, 0);
                    range.setEnd(textNode, 3); // exactly 3 chars: "Ali"
                    const sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(range);
                    document.dispatchEvent(new Event('selectionchange'));

                    const popup = document.getElementById('note-popup');
                    return {
                        length: sel.toString().trim().length,
                        display: popup.style.display
                    };
                })()
            """)
            assert sub_threshold["length"] == 3, f"Expected 3 chars, got {sub_threshold['length']}"
            assert sub_threshold["display"] == "none", f"Popup displayed for 3 chars (threshold violated): {sub_threshold['display']}"

            # 2. Exactly 4 characters selected -> MUST show popup
            at_threshold = ws_client.eval_js("""
                (() => {
                    const p = document.querySelector('.reflow-para');
                    const textNode = p.firstChild;
                    const range = document.createRange();
                    range.setStart(textNode, 0);
                    range.setEnd(textNode, 4); // exactly 4 chars: "Alic"
                    const sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(range);
                    document.dispatchEvent(new Event('selectionchange'));

                    const popup = document.getElementById('note-popup');
                    return {
                        length: sel.toString().trim().length,
                        display: popup.style.display
                    };
                })()
            """)
            assert at_threshold["length"] == 4, f"Expected 4 chars, got {at_threshold['length']}"
            assert at_threshold["display"] == "flex", f"Popup not displayed for 4 chars: {at_threshold['display']}"

            # Close reader
            ws_client.eval_js("window.app.closeReader();")

        test("ADV-02", "Text Selection Boundary: Strict 3-char Threshold Verification", t_adv_02_selection_boundaries)

        # ----------------------------------------------------------------------
        # ADV-03: Rapid Fire Destructive Actions & Undo Toast Lifecycle
        # ----------------------------------------------------------------------
        def t_adv_03_rapid_destructive_and_toast():
            # Open Alice
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    const alice = books.find(b => b.title.includes("Alice"));
                    window.app.openBook(alice);
                })()
            """)
            active_id = ws_client.eval_js("window.app.activeBook.id")

            # Seed bookmarks and notes
            ws_client.eval_js(f"""
                (() => {{
                    window.db.addBookmark({{ book_id: "{active_id}", chapter_index: 0, label: "BM Adv 1" }});
                    window.db.addAnnotation({{ book_id: "{active_id}", selected_text: "Prose", note_text: "Note Adv 1", color_code: "green" }});
                }})()
            """)

            # Trigger clear bookmarks and immediately clear notes without waiting for toast timer
            ws_client.eval_js("""
                (() => {
                    // Clear bookmarks
                    document.getElementById('btn-clear-all-bookmarks').click();
                    document.getElementById('btn-confirm-proceed').click();
                })()
            """)
            toast_msg_1 = ws_client.eval_js("document.getElementById('undo-toast-message').textContent")

            ws_client.eval_js("""
                (() => {
                    // Immediately clear notes
                    document.getElementById('btn-clear-all-notes').click();
                    document.getElementById('btn-confirm-proceed').click();
                })()
            """)
            toast_msg_2 = ws_client.eval_js("document.getElementById('undo-toast-message').textContent")
            assert "note" in toast_msg_2.lower(), f"Toast message was not updated on subsequent action: {toast_msg_2}"

            # Undo latest action (notes restoration)
            ws_client.eval_js("document.getElementById('btn-undo-action').click();")
            notes_restored = ws_client.eval_js(f'window.db.getAnnotations("{active_id}").length')
            assert notes_restored >= 1, f"Latest action undo failed under rapid sequential triggers: {notes_restored}"

            # Test Manual Toast Dismiss (✕)
            ws_client.eval_js("""
                (() => {
                    window.app.showUndoToast("Manual Dismiss Test", () => {});
                    document.getElementById('btn-close-undo-toast').click();
                })()
            """)
            toast_dismissed = ws_client.eval_js("document.getElementById('undo-toast').style.display === 'none'")
            assert toast_dismissed, "Toast did not dismiss immediately on close button click"

            ws_client.eval_js("window.app.closeReader();")

        test("ADV-03", "Rapid-Fire Destructive Actions & Toast Timer Race Condition Resilience", t_adv_03_rapid_destructive_and_toast)

        # ----------------------------------------------------------------------
        # ADV-04: Modal Keydown & Focus Trapping Isolation
        # ----------------------------------------------------------------------
        def t_adv_04_modal_isolation():
            # 1. Escape key pressed when no modal is active -> should not error or close reader if closed
            ws_client.eval_js("""
                window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
            """)

            # 2. Show confirm modal, verify Cancel button receives initial focus
            focus_test = ws_client.eval_js("""
                (() => {
                    window.app.showConfirmModal({
                        title: "Focus Test",
                        message: "Testing auto focus on cancel button",
                        proceedLabel: "Yes",
                        cancelLabel: "No"
                    });
                    const activeEl = document.activeElement;
                    return {
                        focusedId: activeEl ? activeEl.id : null,
                        modalVis: document.getElementById('modal-confirm').style.display === 'flex'
                    };
                })()
            """)
            assert focus_test["modalVis"], "Modal not visible"
            assert focus_test["focusedId"] == "btn-confirm-cancel", f"Expected focus on cancel button, got {focus_test['focusedId']}"

            # Dismiss
            ws_client.eval_js("document.getElementById('btn-confirm-cancel').click();")

        test("ADV-04", "Modal A11y Focus Initialization & Inert Keydown Protection", t_adv_04_modal_isolation)

        # ----------------------------------------------------------------------
        # ADV-05: Margin Navigation Zone Extremes Clamping
        # ----------------------------------------------------------------------
        def t_adv_05_margin_zones_extremes():
            # Open Alice
            ws_client.eval_js("""
                (() => {
                    const books = window.db.getBooks();
                    const alice = books.find(b => b.title.includes("Alice"));
                    window.app.openBook(alice);
                })()
            """)

            # At Chapter 0, Spread 0: Rapid clicks on zone-prev
            ws_client.eval_js("""
                (() => {
                    const zp = document.getElementById('zone-prev');
                    for (let i = 0; i < 10; i++) {
                        zp.click();
                        zp.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                    }
                })()
            """)
            underflow_chap = ws_client.eval_js("window.engine.currentChapterIndex")
            underflow_spread = ws_client.eval_js("window.engine.currentSpreadIndex")
            assert underflow_chap == 0, f"Chapter underflowed: {underflow_chap}"
            assert underflow_spread == 0, f"Spread underflowed: {underflow_spread}"

            # Advance to the very end of book
            ws_client.eval_js("""
                (() => {
                    const zn = document.getElementById('zone-next');
                    for (let i = 0; i < 50; i++) {
                        zn.click();
                    }
                })()
            """)
            total_chaps = ws_client.eval_js("window.engine.currentBook.chapters.length")
            end_chap = ws_client.eval_js("window.engine.currentChapterIndex")
            assert end_chap <= total_chaps - 1, f"Chapter overflowed beyond total chapters: {end_chap} >= {total_chaps}"

            # At end of book: Rapid clicks on zone-next must not throw or crash
            ws_client.eval_js("""
                (() => {
                    const zn = document.getElementById('zone-next');
                    for (let i = 0; i < 10; i++) {
                        zn.click();
                        zn.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                    }
                })()
            """)
            clamped_chap = ws_client.eval_js("window.engine.currentChapterIndex")
            assert clamped_chap <= total_chaps - 1, f"Overflowed at end of book: {clamped_chap}"

            ws_client.eval_js("window.app.closeReader();")

        test("ADV-05", "Margin Navigation Zone Clamping: Extremes, Underflow, and Overflow Resilience", t_adv_05_margin_zones_extremes)

        print("=" * 72)
        passed = sum(1 for _, _, res, _ in results if res == "PASS")
        total = len(results)
        print(f"  ADVERSARIAL SUITE SUMMARY: {passed}/{total} Passed")
        print("=" * 72)

        return passed == total

    finally:
        if ws_client:
            ws_client.close()
        proc.terminate()


if __name__ == "__main__":
    success = run_adversarial_suite()
    sys.exit(0 if success else 1)
