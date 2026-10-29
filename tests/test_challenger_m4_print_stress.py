"""
Adversarial Stress Test Suite for Milestone 4 (Phase 4: Interface Clarification & Token Cleanup)
FolioHaven Ebook Reader Replica
Author: challenger_m4_1 (Milestone 4 Empirical Challenger)

Adversarial Stress Test Matrix:
1. TC-M4-ADV-01: Native Print Delegation via #btn-reader-print click (window.print invoked, overflow closed, #modal-print NEVER displayed).
2. TC-M4-ADV-02: Native Print Delegation via Ctrl+P shortcut in reader (window.print invoked, #modal-print hidden).
3. TC-M4-ADV-03: Ctrl+P & Click Rapid Spam Stress Test (10x rapid Ctrl+P + 10x rapid clicks; zero uncaught errors, zero UI locking, reader fully functional).
4. TC-M4-ADV-04: Hostile Fallback & Exception Handling (window.print throws error or window.print is undefined; app never crashes).
5. TC-M4-ADV-05: Card Thumbnail (.card-thumb) Computed Background Token Resolution across Light and Dark Themes (live computedStyle vs var(--color-surface)).
6. TC-M4-ADV-06: Brand Title (.brand-title) Computed Typography, Color, and Inline Style Absence.
7. TC-M4-ADV-07: Reader Page & Progress Info Semantic Styling and Inline Style Absence.
8. TC-M4-ADV-08: Boundary & Edge Case Testing (Ctrl+P in Library mode, Defensive #modal-print button clicks).
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
import unittest

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))


class CDPClient:
    """Minimal dependency-free Chrome DevTools Protocol WebSocket client."""

    def __init__(self, host, port, path):
        self.sock = socket.create_connection((host, port), timeout=15)
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
        masked = bytearray(payload[i] ^ mask[i % 4] for i in range(len(payload)))
        frame.extend(masked)

        self.sock.sendall(frame)
        return self._read_response(self._req_id)

    def _read_response(self, target_id):
        while True:
            head = self.sock.recv(2)
            if len(head) < 2:
                raise ConnectionError("Connection closed unexpectedly")
            b1, b2 = head[0], head[1]
            length = b2 & 0x7F
            if length == 126:
                length = struct.unpack("!H", self.sock.recv(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self.sock.recv(8))[0]

            data = bytearray()
            while len(data) < length:
                chunk = self.sock.recv(min(4096, length - len(data)))
                if not chunk:
                    break
                data.extend(chunk)

            msg = json.loads(data.decode('utf-8'))
            if msg.get("id") == target_id:
                return msg

    def eval_js(self, expression):
        res = self.send_command("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True
        })
        if "error" in res:
            raise RuntimeError(f"CDP error: {res['error']}")
        result = res.get("result", {}).get("result", {})
        if result.get("subtype") == "error":
            raise RuntimeError(f"JS execution error: {result.get('description')}")
        return result.get("value")

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass


class TestChallengerM4PrintStress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        exe = None
        for p in chrome_paths:
            if os.path.exists(p):
                exe = p
                break
        if not exe:
            raise unittest.SkipTest("Google Chrome executable not found for CDP live testing")

        # Dynamic free port allocation
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            cls.port = s.getsockname()[1]

        cls.user_data_dir = tempfile.mkdtemp(prefix="chrome_challenger_m4_")
        cls.url = "file:///" + os.path.join(APP_DIR, "index.html").replace("\\", "/")

        cls.proc = subprocess.Popen([
            exe,
            "--headless=new",
            f"--remote-debugging-port={cls.port}",
            f"--user-data-dir={cls.user_data_dir}",
            "--remote-allow-origins=*",
            "--disable-gpu",
            "--no-sandbox",
            "--allow-file-access-from-files",
            cls.url
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait for debugger endpoint
        max_attempts = 30
        for _ in range(max_attempts):
            time.sleep(0.2)
            try:
                req = urllib.request.urlopen(f"http://localhost:{cls.port}/json", timeout=2)
                tabs = json.loads(req.read().decode())
                page_tabs = [t for t in tabs if t.get("type") == "page" and "index.html" in t.get("url", "")]
                tab = page_tabs[0] if page_tabs else tabs[0]
                ws_url = tab["webSocketDebuggerUrl"]
                path = ws_url.split(f"localhost:{cls.port}")[1]
                cls.client = CDPClient("localhost", cls.port, path)
                cls.client.send_command("Runtime.enable")
                break
            except Exception:
                continue
        else:
            cls.proc.terminate()
            raise unittest.SkipTest("Failed to connect to headless Chrome CDP port")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "client"):
            cls.client.close()
        if hasattr(cls, "proc"):
            cls.proc.terminate()
            try:
                cls.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                cls.proc.kill()

    def setUp(self):
        # Reset runtime state between tests
        self.client.eval_js("""
            (() => {
                if (window.app && window.app.isReading) {
                    window.app.closeReader();
                }
                document.documentElement.removeAttribute("data-theme");
                const modalPrint = document.getElementById("modal-print");
                if (modalPrint) modalPrint.style.display = "none";
                window.app._printDelegated = false;
            })()
        """)

    def test_tc_m4_adv_01_print_delegation_btn_click(self):
        """TC-M4-ADV-01: #btn-reader-print click invokes window.print(), closes overflow menu, and NEVER displays #modal-print."""
        res = self.client.eval_js("""
            (() => {
                let printInvoked = 0;
                const origPrint = window.print;
                window.print = () => { printInvoked++; };

                // 1. Open reader with first book
                const books = window.db.getBooks();
                if (!books || books.length === 0) throw new Error("No books in db");
                window.app.openBook(books[0]);

                // 2. Open reader overflow menu
                window.app.openReaderOverflowMenu();
                const menu = document.getElementById("reader-overflow-menu");
                const menuOpened = menu.classList.contains("open");

                // 3. Ensure #modal-print is not visible initially
                const modalPrint = document.getElementById("modal-print");
                const initialModalDisplay = modalPrint.style.display;
                const initialModalComputed = window.getComputedStyle(modalPrint).display;

                // 4. Trigger print click
                const printBtn = document.getElementById("btn-reader-print");
                printBtn.click();

                // 5. Check post-click states
                const menuClosed = !menu.classList.contains("open");
                const finalModalDisplay = modalPrint.style.display;
                const finalModalComputed = window.getComputedStyle(modalPrint).display;
                const printDelegatedFlag = window.app._printDelegated;

                // Cleanup
                window.print = origPrint;
                window.app.closeReader();

                return {
                    menuOpened,
                    menuClosed,
                    printInvoked,
                    printDelegatedFlag,
                    initialModalDisplay,
                    initialModalComputed,
                    finalModalDisplay,
                    finalModalComputed
                };
            })()
        """)

        self.assertTrue(res["menuOpened"], "Reader overflow menu should have opened")
        self.assertTrue(res["menuClosed"], "Reader overflow menu must be closed immediately upon clicking print")
        self.assertEqual(res["printInvoked"], 1, "window.print() must be called exactly once")
        self.assertTrue(res["printDelegatedFlag"], "window.app._printDelegated must be true")
        self.assertNotEqual(res["finalModalDisplay"], "flex", "#modal-print style.display must NEVER be set to 'flex'")
        self.assertEqual(res["finalModalComputed"], "none", "#modal-print computedStyle must remain 'none'")

    def test_tc_m4_adv_02_print_delegation_ctrl_p_shortcut(self):
        """TC-M4-ADV-02: Ctrl+P in reader invokes window.print() directly without displaying #modal-print."""
        res = self.client.eval_js("""
            (() => {
                let printCount = 0;
                const origPrint = window.print;
                window.print = () => { printCount++; };

                // Open reader
                const book = window.db.getBooks()[0];
                window.app.openBook(book);
                window.app._printDelegated = false;

                const modalPrint = document.getElementById("modal-print");

                // Dispatch Ctrl+P
                const evt = new KeyboardEvent("keydown", {
                    key: "p",
                    ctrlKey: true,
                    bubbles: true,
                    cancelable: true
                });
                const dispatched = window.dispatchEvent(evt);

                const modalDisplay = modalPrint.style.display;
                const modalComputed = window.getComputedStyle(modalPrint).display;
                const delegated = window.app._printDelegated;

                // Cleanup
                window.print = origPrint;
                window.app.closeReader();

                return {
                    dispatched,
                    printCount,
                    delegated,
                    modalDisplay,
                    modalComputed
                };
            })()
        """)

        self.assertEqual(res["printCount"], 1, "Ctrl+P shortcut must invoke window.print() once")
        self.assertTrue(res["delegated"], "window.app._printDelegated should be true after Ctrl+P")
        self.assertNotEqual(res["modalDisplay"], "flex", "#modal-print must never be set to flex")
        self.assertEqual(res["modalComputed"], "none", "#modal-print computed display must remain 'none'")

    def test_tc_m4_adv_03_ctrl_p_and_click_rapid_spam_stress(self):
        """TC-M4-ADV-03: Rapid spam of 10x Ctrl+P and 10x clicks causes zero uncaught errors and zero UI locking."""
        res = self.client.eval_js("""
            (() => {
                const capturedErrors = [];
                const errorHandler = (evt) => {
                    capturedErrors.push(evt.message || String(evt));
                };
                window.addEventListener("error", errorHandler);

                let printCallCount = 0;
                const origPrint = window.print;
                window.print = () => { printCallCount++; };

                // Open book in reader
                const book = window.db.getBooks()[0];
                window.app.openBook(book);

                const modalPrint = document.getElementById("modal-print");
                const printBtn = document.getElementById("btn-reader-print");

                // Rapid spam 10x Ctrl+P keydowns
                for (let i = 0; i < 10; i++) {
                    const evt = new KeyboardEvent("keydown", {
                        key: "p",
                        ctrlKey: true,
                        bubbles: true,
                        cancelable: true
                    });
                    window.dispatchEvent(evt);
                }

                // Rapid spam 10x print button clicks
                for (let j = 0; j < 10; j++) {
                    printBtn.click();
                }

                // Verify UI responsiveness and non-locking
                const initialSpread = window.engine.currentSpreadIndex;
                window.app.pageNext();
                const afterNextSpread = window.engine.currentSpreadIndex;

                window.app.pagePrev();
                const afterPrevSpread = window.engine.currentSpreadIndex;

                // Verify drawer toggle responsiveness
                window.app.toggleDrawer("drawer-toc");
                const tocOpen = document.getElementById("drawer-toc").classList.contains("open");
                window.app.closeAllDrawers();
                const tocClosed = !document.getElementById("drawer-toc").classList.contains("open");

                // Close reader smoothly
                window.app.closeReader();
                const isReadingAfterClose = window.app.isReading;

                // Cleanup
                window.removeEventListener("error", errorHandler);
                window.print = origPrint;

                return {
                    printCallCount,
                    capturedErrors,
                    initialSpread,
                    afterNextSpread,
                    afterPrevSpread,
                    tocOpen,
                    tocClosed,
                    isReadingAfterClose,
                    modalDisplay: modalPrint.style.display,
                    modalComputed: window.getComputedStyle(modalPrint).display
                };
            })()
        """)

        self.assertEqual(res["printCallCount"], 20, "Expected all 20 rapid print triggers to execute")
        self.assertEqual(len(res["capturedErrors"]), 0, f"Spam stress must produce zero errors: {res['capturedErrors']}")
        self.assertTrue(res["tocOpen"], "TOC drawer should be functional after print spam")
        self.assertTrue(res["tocClosed"], "TOC drawer should close normally after print spam")
        self.assertFalse(res["isReadingAfterClose"], "Reader must close cleanly without locking")
        self.assertNotEqual(res["modalDisplay"], "flex", "#modal-print must never show during rapid spam")

    def test_tc_m4_adv_04_hostile_fallback_when_print_throws_or_undefined(self):
        """TC-M4-ADV-04: Robust fallback if window.print throws an exception or is undefined (zero app crash)."""
        res = self.client.eval_js("""
            (() => {
                const uncaughtErrors = [];
                const errListener = (e) => uncaughtErrors.push(e.message || String(e));
                window.addEventListener("error", errListener);

                const origPrint = window.print;
                const book = window.db.getBooks()[0];
                window.app.openBook(book);

                // Scenario A: window.print throws a fatal Host OS error
                window.print = () => {
                    throw new Error("Simulated OS Print Spooler Deadlock / Access Denied");
                };

                let exceptionEscapedA = false;
                try {
                    document.getElementById("btn-reader-print").click();
                } catch (e) {
                    exceptionEscapedA = true;
                }

                const delegatedA = window.app._printDelegated;

                // Scenario B: window.print is undefined (e.g. sandboxed iframe)
                delete window.print;
                window.print = undefined;

                let exceptionEscapedB = false;
                try {
                    window.app.delegatePrint();
                } catch (e) {
                    exceptionEscapedB = true;
                }

                // Verify reader still operates normally after hostile failures
                window.app.pageNext();
                window.app.closeReader();
                const readerClosed = !window.app.isReading;

                // Restore
                window.print = origPrint;
                window.removeEventListener("error", errListener);

                return {
                    exceptionEscapedA,
                    exceptionEscapedB,
                    delegatedA,
                    readerClosed,
                    uncaughtCount: uncaughtErrors.length
                };
            })()
        """)

        self.assertFalse(res["exceptionEscapedA"], "delegatePrint() must catch any error thrown by window.print()")
        self.assertFalse(res["exceptionEscapedB"], "delegatePrint() must safely handle undefined window.print")
        self.assertTrue(res["delegatedA"], "_printDelegated flag should still be set")
        self.assertTrue(res["readerClosed"], "Reader must close successfully after print error")
        self.assertEqual(res["uncaughtCount"], 0, "No uncaught errors should propagate to window")

    def test_tc_m4_adv_05_card_thumb_computed_background_across_themes(self):
        """TC-M4-ADV-05: .card-thumb computed background style resolves to semantic --color-surface in light and dark mode."""
        res = self.client.eval_js("""
            (() => {
                // Ensure light mode
                document.documentElement.removeAttribute("data-theme");

                // Test pure .card-thumb element (governed by styles.css)
                const testThumb = document.createElement("div");
                testThumb.className = "card-thumb";
                document.body.appendChild(testThumb);

                const lightComputedBg = window.getComputedStyle(testThumb).backgroundColor;
                const lightRootSurface = window.getComputedStyle(document.documentElement).getPropertyValue("--color-surface").trim();

                // Test skeleton thumb
                const skeletonThumb = document.createElement("div");
                skeletonThumb.className = "card-thumb skeleton-pulse";
                document.body.appendChild(skeletonThumb);
                const lightSkeletonBg = window.getComputedStyle(skeletonThumb).backgroundColor;

                // Switch to dark theme
                document.documentElement.setAttribute("data-theme", "dark");
                const darkComputedBg = window.getComputedStyle(testThumb).backgroundColor;
                const darkRootSurface = window.getComputedStyle(document.documentElement).getPropertyValue("--color-surface").trim();
                const darkSkeletonBg = window.getComputedStyle(skeletonThumb).backgroundColor;

                // Switch back to light theme
                document.documentElement.removeAttribute("data-theme");
                const restoredLightBg = window.getComputedStyle(testThumb).backgroundColor;

                // Cleanup
                testThumb.remove();
                skeletonThumb.remove();

                return {
                    lightComputedBg,
                    lightRootSurface,
                    lightSkeletonBg,
                    darkComputedBg,
                    darkRootSurface,
                    darkSkeletonBg,
                    restoredLightBg
                };
            })()
        """)

        # Light theme: #f5f7fa -> rgb(245, 247, 250)
        self.assertEqual(res["lightComputedBg"], "rgb(245, 247, 250)",
                         f".card-thumb in light theme must resolve to rgb(245, 247, 250), got {res['lightComputedBg']}")
        self.assertNotEqual(res["lightComputedBg"], "rgb(226, 232, 240)",
                            "Hardcoded #e2e8f0 (rgb(226, 232, 240)) must NOT be used for card-thumb")

        # Dark theme: #20242c -> rgb(32, 36, 44)
        self.assertEqual(res["darkComputedBg"], "rgb(32, 36, 44)",
                         f".card-thumb in dark theme must resolve to dark --color-surface rgb(32, 36, 44), got {res['darkComputedBg']}")

        # Restored light theme
        self.assertEqual(res["restoredLightBg"], "rgb(245, 247, 250)", "Theme toggle must be fully reversible")

    def test_tc_m4_adv_06_brand_title_typography_and_inline_style_absence(self):
        """TC-M4-ADV-06: .brand-title computed font-size, color, and lack of inline styles."""
        res = self.client.eval_js("""
            (() => {
                const brand = document.querySelector(".brand-title");
                if (!brand) return null;

                const comp = window.getComputedStyle(brand);
                return {
                    hasInlineStyle: brand.hasAttribute("style"),
                    styleAttr: brand.getAttribute("style"),
                    fontSize: comp.fontSize,
                    color: comp.color,
                    fontWeight: comp.fontWeight,
                    lineHeight: comp.lineHeight,
                    tagName: brand.tagName.toLowerCase()
                };
            })()
        """)

        self.assertIsNotNone(res, "Missing .brand-title element in DOM")
        self.assertFalse(res["hasInlineStyle"], ".brand-title must have NO inline style attribute")
        self.assertIsNone(res["styleAttr"], "Inline style attribute must be null")
        # --type-lg-size is 18px
        self.assertEqual(res["fontSize"], "18px", "brand-title font-size must resolve to 18px (--type-lg-size)")
        # --color-sidebar-text is #f5f0eb -> rgb(245, 240, 235)
        self.assertEqual(res["color"], "rgb(245, 240, 235)", "brand-title color must resolve to rgb(245, 240, 235) (--color-sidebar-text)")
        self.assertEqual(res["fontWeight"], "700", "brand-title font-weight must be 700")

    def test_tc_m4_adv_07_reader_page_and_progress_info_styling(self):
        """TC-M4-ADV-07: Reader page info & progress info have semantic classes and no inline styles."""
        res = self.client.eval_js("""
            (() => {
                const pageInfo = document.getElementById("reader-page-info");
                const progInfo = document.getElementById("reader-progress-info");

                const pageComp = pageInfo ? window.getComputedStyle(pageInfo) : null;
                const progComp = progInfo ? window.getComputedStyle(progInfo) : null;

                return {
                    pageInfoHasStyle: pageInfo ? pageInfo.hasAttribute("style") : false,
                    progInfoHasStyle: progInfo ? progInfo.hasAttribute("style") : false,
                    pageInfoClass: pageInfo ? pageInfo.className : "",
                    progInfoClass: progInfo ? progInfo.className : "",
                    pageFontSize: pageComp ? pageComp.fontSize : null,
                    pageFontWeight: pageComp ? pageComp.fontWeight : null,
                    progFontSize: progComp ? progComp.fontSize : null,
                    progColor: progComp ? progComp.color : null
                };
            })()
        """)

        self.assertFalse(res["pageInfoHasStyle"], "#reader-page-info must NOT have inline styles")
        self.assertFalse(res["progInfoHasStyle"], "#reader-progress-info must NOT have inline styles")
        self.assertIn("reader-page-info", res["pageInfoClass"])
        self.assertIn("reader-progress-info", res["progInfoClass"])
        self.assertEqual(res["pageFontSize"], "13px", "reader-page-info font-size must be 13px (--type-sm-size)")
        self.assertEqual(res["pageFontWeight"], "600", "reader-page-info font-weight must be 600")
        self.assertEqual(res["progFontSize"], "13px", "reader-progress-info font-size must be 13px (--type-sm-size)")
        # --color-text-muted is #525b6a -> rgb(82, 91, 106)
        self.assertEqual(res["progColor"], "rgb(82, 91, 106)", "reader-progress-info color must be rgb(82, 91, 106)")

    def test_tc_m4_adv_08_edge_cases_and_defensive_modal(self):
        """TC-M4-ADV-08: Edge cases: Ctrl+P in library mode ignored, defensive modal buttons do not crash."""
        res = self.client.eval_js("""
            (() => {
                let libraryPrintCount = 0;
                const origPrint = window.print;
                window.print = () => { libraryPrintCount++; };

                // 1. In library mode, ensure isReading is false
                window.app.closeReader();
                const isReading = window.app.isReading;

                // Dispatch Ctrl+P in library mode
                window.app._printDelegated = false;
                window.dispatchEvent(new KeyboardEvent("keydown", {
                    key: "p",
                    ctrlKey: true,
                    bubbles: true,
                    cancelable: true
                }));

                const libraryDelegated = window.app._printDelegated;
                const modalPrint = document.getElementById("modal-print");
                const modalInLibrary = modalPrint.style.display;
                const printCountAfterLibraryKey = libraryPrintCount;

                // 2. Click defensive modal buttons (simulate stale tests or accessibility tree clicks)
                const btnClose = document.getElementById("btn-close-print");
                const btnCancel = document.getElementById("btn-cancel-print");
                const btnConfirm = document.getElementById("btn-confirm-print");

                let buttonsExist = !!(btnClose && btnCancel && btnConfirm);

                // Show modal temporarily to test close handlers
                modalPrint.style.display = "flex";
                btnClose.click();
                const closedByCloseBtn = (modalPrint.style.display === "none");

                modalPrint.style.display = "flex";
                btnCancel.click();
                const closedByCancelBtn = (modalPrint.style.display === "none");

                modalPrint.style.display = "flex";
                btnConfirm.click();
                const closedByConfirmBtn = (modalPrint.style.display === "none");
                const confirmDelegated = window.app._printDelegated;
                const printCountAfterConfirm = libraryPrintCount;

                window.print = origPrint;

                return {
                    isReading,
                    printCountAfterLibraryKey,
                    libraryDelegated,
                    modalInLibrary,
                    buttonsExist,
                    closedByCloseBtn,
                    closedByCancelBtn,
                    closedByConfirmBtn,
                    confirmDelegated,
                    printCountAfterConfirm
                };
            })()
        """)

        self.assertFalse(res["isReading"], "Should be in library mode")
        self.assertEqual(res["printCountAfterLibraryKey"], 0, "Ctrl+P in library mode must not trigger reader print")
        self.assertFalse(res["libraryDelegated"], "_printDelegated should be false in library mode")
        self.assertEqual(res["modalInLibrary"], "none", "Modal must remain hidden in library mode")
        self.assertTrue(res["buttonsExist"], "Defensive modal buttons must exist in DOM")
        self.assertTrue(res["closedByCloseBtn"], "Close button must set display: none")
        self.assertTrue(res["closedByCancelBtn"], "Cancel button must set display: none")
        self.assertTrue(res["closedByConfirmBtn"], "Confirm button must set display: none and delegate print")
        self.assertTrue(res["confirmDelegated"], "Confirm button must trigger delegation")
        self.assertEqual(res["printCountAfterConfirm"], 1, "Confirm button must invoke window.print()")


if __name__ == "__main__":
    unittest.main()
